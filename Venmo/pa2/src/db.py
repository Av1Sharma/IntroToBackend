import os
import sqlite3


# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Venmo app.
    Handles reading and writing data with the SQLite database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the
        instance variable `conn`, then ensures the user table is created.
        """
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()

    def create_user_table(self):
        """
        Using SQL, creates the users table if it does not already exist.
        Stores id, name, username, and balance.
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0
                );
                """
            )
        except Exception as e:
            print(e)

    def delete_user_table(self):
        """
        Using SQL, drops the users table if it exists.
        """
        self.conn.execute("DROP TABLE IF EXISTS users;")
        self.conn.commit()

    def get_all_users(self):
        """
        Using SQL, retrieves all users in the users table.
        Does NOT return user balance for confidentiality.
        """
        cursor = self.conn.execute("SELECT id, name, username FROM users;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def insert_user_table(self, name, username, balance=0):
        """
        Using SQL, adds a new user into the users table and returns their id.
        """
        cursor = self.conn.execute(
            "INSERT INTO users (name, username, balance) VALUES (?, ?, ?);",
            (name, username, balance),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, user_id):
        """
        Using SQL, gets a user by id including their balance.
        Returns None if user with given id is not found.
        """
        cursor = self.conn.execute(
            "SELECT id, name, username, balance FROM users WHERE id = ?;",
            (user_id,),
        )
        for row in cursor:
            return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "balance": row[3],
            }
        return None

    def delete_user_by_id(self, user_id):
        """
        Using SQL, deletes a user from the users table by id.
        """
        self.conn.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        self.conn.commit()

    def update_user_balance(self, user_id, balance):
        """
        Using SQL, updates a user's balance by id.
        """
        self.conn.execute(
            "UPDATE users SET balance = ? WHERE id = ?;",
            (balance, user_id),
        )
        self.conn.commit()


# Only <=1 instance of the database driver exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
