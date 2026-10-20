# Cornell AppDev — Databases Notes

## 1. SQLite3 Basics

SQLite is a database system that stores information in tables consisting of rows and columns.

### Starting SQLite

In the terminal:

```bash
sqlite3
```

To open or create a database file:

```bash
sqlite3 database.db
```

**Important:** If you don't save your database to a file, your changes may be lost when you exit SQLite.

Useful commands:

| Command | Purpose |
|---|---|
| `.tables` | Show all tables |
| `.schema` | Show table definitions |
| `.schema user` | Show the structure of the `user` table |
| `.open database.db` | Open/create a database file |
| `.shell clear` | Clear terminal on Mac/Linux |
| `.quit` | Exit SQLite |
| `PRAGMA table_info(user);` | Show column information |

**Note:** SQLite shell commands starting with `.` don't need semicolons. SQL statements generally end with `;`.

---

## 2. Creating Tables

Use `CREATE TABLE` to make a table in the database.

### Example 1: User Table

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INT NOT NULL,
    email CHAR(50)
);
```

### Understanding the Syntax

| Keyword | Meaning |
|---|---|
| `CREATE TABLE` | Creates a new table |
| `INTEGER` | Stores integers |
| `TEXT` | Stores strings |
| `CHAR(50)` | Declares a character field with length 50; SQLite does not enforce this limit |
| `PRIMARY KEY` | Uniquely identifies each row |
| `AUTOINCREMENT` | Automatically generates increasing IDs |
| `NOT NULL` | Requires a value; cannot be `NULL` |

**Important:**
- Every SQL statement should end with a semicolon.
- Do not put a comma after the last column definition.
- SQL keywords are usually capitalized for readability.
- The `email` column is optional because it does not have `NOT NULL`.

### Example 2: Fruit Table

```sql
CREATE TABLE fruit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    is_healthy INTEGER NOT NULL
);
```

For booleans in SQLite, we typically use integers:

- `0` = False
- `1` = True

Example data:

| id | name | is_healthy |
|---|---|---|
| 1 | Apple | 1 |
| 2 | Candy | 0 |
| 3 | Banana | 1 |

---

## 3. Viewing and Deleting Tables

### View All Tables

```sql
.tables
```

### View Table Columns

```sql
PRAGMA table_info(fruit);
```

This shows the columns, their types, and constraints.

### Delete an Entire Table

```sql
DROP TABLE fruit;
```

**Warning:** `DROP TABLE` permanently removes the table and its data.

---

## 4. Inserting Data (CREATE)

Use `INSERT INTO` to add rows.

```sql
INSERT INTO user (name, age, email)
VALUES ('Alanna', 20, 'alanna@gmail.com');
```

Insert another user:

```sql
INSERT INTO user (name, age, email)
VALUES ('Conner', 21, 'conner@gmail.com');
```

Insert a user without an email:

```sql
INSERT INTO user (name, age)
VALUES ('Alicia', 21);
```

This works because `email` is optional.

**Important:**
- Column order must match the values.
- You cannot omit a required (`NOT NULL`) column without a default.
- You don't need to manually insert `id` because it is automatically generated.

---

## 5. Retrieving Data (READ)

Use `SELECT` to read rows from a table.

### Retrieve Everything

```sql
SELECT * FROM user;
```

The `*` means all columns.

### Retrieve Specific Columns

```sql
SELECT name, email FROM user;
```

### Filter Using WHERE

```sql
SELECT name, age
FROM user
WHERE age >= 18;
```

### Multiple Conditions

Use `AND` when both conditions must be true:

```sql
SELECT id, name, age
FROM user
WHERE name = 'Alicia' AND age > 20;
```

Use `OR` when either condition can be true:

```sql
SELECT *
FROM user
WHERE age < 18 OR age > 60;
```

### Common SQL Operators

| Operator | Meaning |
|---|---|
| `=` | Equal to |
| `!=` | Not equal to |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater than or equal to |
| `<=` | Less than or equal to |
| `AND` | Both conditions must be true |
| `OR` | At least one condition must be true |

---

## 6. Updating Data (UPDATE)

Use `UPDATE` to modify existing rows.

```sql
UPDATE user
SET email = 'asz33@cornell.edu'
WHERE id = 1;
```

This changes the email for the user whose ID is 1.

**Important:** Without `WHERE`, every row would be updated.

---

## 7. Deleting Data (DELETE)

Use `DELETE FROM` to remove rows.

```sql
DELETE FROM user
WHERE age = 21;
```

This deletes all users whose age is 21.

**Important:**

- `DELETE FROM user WHERE id = 1;` removes one matching user.
- `DELETE FROM user;` removes all rows but keeps the table.
- `DROP TABLE user;` removes the entire table.

---

## 8. CRUD Summary

CRUD represents the four main database operations.

| Operation | SQL Keyword | Purpose |
|---|---|---|
| Create | `INSERT INTO` | Add a row |
| Read | `SELECT` | Retrieve data |
| Update | `UPDATE` | Modify data |
| Delete | `DELETE FROM` | Remove data |

Table creation (`CREATE TABLE`) is separate from creating records using `INSERT INTO`.

---

# Part 2 — Using SQLite with Python and Flask

## 9. Connecting Python to SQLite

Python has a built-in library called `sqlite3`.

Create a file called `db.py`.

```python
import sqlite3

class DatabaseDriver:
    def __init__(self):
        self.conn = sqlite3.connect("todo.db")
        self.create_task_table()
```

### Explanation

- `sqlite3.connect("todo.db")` opens the database or creates it if it does not exist.
- `self.conn` stores the connection.
- `self.create_task_table()` initializes the table.

We use a `DatabaseDriver` class so that our Flask routes do not need to directly manage SQL queries.

---

## 10. Creating Tables Through Python

Inside `DatabaseDriver`:

```python
def create_task_table(self):
    self.conn.execute("""
        CREATE TABLE IF NOT EXISTS task (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DESCRIPTION TEXT NOT NULL,
            DONE BOOLEAN NOT NULL
        );
    """)
    self.conn.commit()
```

### Explanation

- `self.conn.execute()` executes SQL from Python.
- Triple quotes `"""` allow multiline SQL.
- `IF NOT EXISTS` prevents an error if the table already exists.
- `commit()` saves the transaction.

SQLite stores `BOOLEAN` values using integer values, usually `0` and `1`.

---

## 11. Getting All Tasks

```python
def get_all_tasks(self):
    cursor = self.conn.execute("SELECT * FROM task;")
    tasks = []

    for row in cursor:
        tasks.append({
            "id": row[0],
            "description": row[1],
            "done": row[2]
        })

    return tasks
```

### Explanation

A cursor lets us access the results of a SQL query.

Each row contains values corresponding to the columns:

```python
row[0]  # ID
row[1]  # DESCRIPTION
row[2]  # DONE
```

We transform each row into a Python dictionary.

Example result:

```python
[
    {"id": 1, "description": "Finish homework", "done": 0},
    {"id": 2, "description": "Study SQL", "done": 1}
]
```

---

## 12. Adding a Task

```python
def insert_task_table(self, description, done):
    cursor = self.conn.cursor()

    cursor.execute(
        "INSERT INTO task (DESCRIPTION, DONE) VALUES (?, ?);",
        (description, done)
    )

    self.conn.commit()
    return cursor.lastrowid
```

### Explanation

- `cursor()` creates a cursor object.
- `?` represents a placeholder.
- `(description, done)` provides the actual values.
- `commit()` saves the inserted row.
- `lastrowid` returns the ID of the newly inserted task.

**Why use `?` instead of directly inserting variables into SQL strings?**

It keeps values separate from the SQL statement and helps prevent SQL injection attacks.

---

## 13. Getting One Task by ID

```python
def get_task_by_id(self, id):
    cursor = self.conn.execute(
        "SELECT * FROM task WHERE ID = ?;",
        (id,)
    )

    for row in cursor:
        return {
            "id": row[0],
            "description": row[1],
            "done": row[2]
        }

    return None
```

### Explanation

- Retrieves the row with the matching ID.
- Returns a dictionary if the task exists.
- Returns `None` if no matching task exists.

**Python detail:** `(id,)` is a tuple containing one value. The comma is necessary.

---

## 14. Updating a Task

```python
def update_task_by_id(self, id, description, done):
    self.conn.execute("""
        UPDATE task
        SET DESCRIPTION = ?, DONE = ?
        WHERE ID = ?;
    """, (description, done, id))

    self.conn.commit()
```

The `?` placeholders are filled in order:

1. `description`
2. `done`
3. `id`

---

## 15. Deleting a Task

```python
def delete_task_by_id(self, id):
    self.conn.execute(
        "DELETE FROM task WHERE ID = ?;",
        (id,)
    )

    self.conn.commit()
```

This removes the task with the provided ID.

---

# Part 3 — Connecting the Database to Flask

## 16. Setting Up Flask

In `app.py`:

```python
import json
from flask import Flask, request
import db

app = Flask(__name__)
DB = db.DatabaseDriver()
```

`DB` is an instance of our database driver, allowing Flask routes to interact with the database.

### Response Helpers

```python
def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({"error":