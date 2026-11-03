"""SQLite storage for the Venmo payment application."""

from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from threading import RLock


class PaymentError(Exception):
    """An operation that cannot be completed, with an HTTP status code."""

    def __init__(self, message, code):
        """Store the error message and status code."""
        super().__init__(message)
        self.code = code


class DatabaseDriver:
    """Read and write users and transactions using SQL."""

    def __init__(self, database_path=None):
        """Connect to SQLite, enable foreign keys, and create all tables."""
        default_path = Path(__file__).resolve().parent / "venmo.db"
        self.conn = sqlite3.connect(
            database_path or os.environ.get("VENMO_DB_PATH", default_path),
            check_same_thread=False,
        )
        self.conn.row_factory = sqlite3.Row
        self.lock = RLock()
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0)
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                amount NUMERIC NOT NULL CHECK (amount > 0),
                message TEXT NOT NULL,
                accepted BOOLEAN CHECK (accepted IN (0, 1)),
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
                CHECK (sender_id != receiver_id)
            );
        """)

    def get_all_users(self):
        """Return public profiles without balances or transaction histories."""
        with self.lock:
            return [dict(row) for row in self.conn.execute(
                "SELECT id, name, username FROM users ORDER BY id;"
            )]

    def insert_user_table(self, name, username, balance=0):
        """Insert a user and return the generated ID."""
        with self.lock, self.conn:
            cursor = self.conn.execute(
                "INSERT INTO users (name, username, balance) VALUES (?, ?, ?);",
                (name, username, balance),
            )
            return cursor.lastrowid

    def get_user_by_id(self, user_id):
        """Return a user with every incoming and outgoing transaction."""
        if user_id >= 2**63:
            return None
        with self.lock:
            row = self.conn.execute(
                "SELECT * FROM users WHERE id = ?;", (user_id,)
            ).fetchone()
            if row is None:
                return None
            user = dict(row)
            user["transactions"] = [self.serialize_transaction(row)
                                    for row in self.conn.execute(
                "SELECT * FROM transactions WHERE sender_id = ? "
                "OR receiver_id = ? ORDER BY id;", (user_id, user_id)
            )]
            return user

    def delete_user_by_id(self, user_id):
        """Delete a user, cascading their transactions."""
        with self.lock, self.conn:
            self.conn.execute("DELETE FROM users WHERE id = ?;", (user_id,))

    @staticmethod
    def serialize_transaction(row):
        """Convert SQLite's nullable integer into a JSON boolean or null."""
        transaction = dict(row)
        if transaction["accepted"] is not None:
            transaction["accepted"] = bool(transaction["accepted"])
        return transaction

    @staticmethod
    def timestamp():
        """Return the current UTC time with microsecond precision."""
        return datetime.now(timezone.utc).isoformat(sep=" ")

    def transfer_money(self, sender_id, receiver_id, amount):
        """Move money within the caller's SQL transaction without overdrawing."""
        cursor = self.conn.execute(
            "UPDATE users SET balance = balance - ? "
            "WHERE id = ? AND balance >= ?;", (amount, sender_id, amount)
        )
        if cursor.rowcount != 1:
            raise PaymentError("Sender has insufficient funds.", 403)
        self.conn.execute(
            "UPDATE users SET balance = balance + ? WHERE id = ?;",
            (amount, receiver_id),
        )

    def create_transaction(self, sender_id, receiver_id, amount, message, accepted):
        """Atomically save a request/payment and any immediate balance changes."""
        with self.lock, self.conn:
            self.conn.execute("BEGIN IMMEDIATE;")
            for user_id in (sender_id, receiver_id):
                if self.conn.execute(
                    "SELECT id FROM users WHERE id = ?;", (user_id,)
                ).fetchone() is None:
                    raise PaymentError("Sender or receiver not found.", 404)
            if accepted is True:
                self.transfer_money(sender_id, receiver_id, amount)
            cursor = self.conn.execute(
                "INSERT INTO transactions "
                "(timestamp, sender_id, receiver_id, amount, message, accepted) "
                "VALUES (?, ?, ?, ?, ?, ?);",
                (self.timestamp(), sender_id, receiver_id, amount, message, accepted),
            )
            return self.get_transaction_by_id(cursor.lastrowid)

    def get_transaction_by_id(self, transaction_id):
        """Return a transaction, or None when the ID does not exist."""
        if transaction_id >= 2**63:
            return None
        with self.lock:
            row = self.conn.execute(
                "SELECT * FROM transactions WHERE id = ?;", (transaction_id,)
            ).fetchone()
            return None if row is None else self.serialize_transaction(row)

    def resolve_transaction(self, transaction_id, accepted):
        """Resolve a request once; roll back all changes if funds are lacking."""
        with self.lock, self.conn:
            self.conn.execute("BEGIN IMMEDIATE;")
            transaction = self.get_transaction_by_id(transaction_id)
            if transaction is None:
                raise PaymentError("Transaction not found.", 404)
            if transaction["accepted"] is not None:
                raise PaymentError(
                    "Cannot change an accepted or denied transaction.", 403
                )
            if accepted:
                self.transfer_money(transaction["sender_id"],
                                    transaction["receiver_id"], transaction["amount"])
            self.conn.execute(
                "UPDATE transactions SET accepted = ?, timestamp = ? WHERE id = ?;",
                (accepted, self.timestamp(), transaction_id),
            )
            return self.get_transaction_by_id(transaction_id)

