import json

from db import db
from flask import Flask

# define db filename
db_filename = "todo.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

@app.route("/")
@app.route("/tasks/")
def get_tasks():
    """
    Endpoint for getting all tasks
    """
    # return success_response({"tasks": DB.get_all_tasks()})

    return json.dumps({"tasks": DB.get_all_tasks()})

@app.route("/tasks/", methods=["POST"])
def create_task():
    """
    Endpoint for creating a new task
    """
    body = json.loads(request.data)
    description = body.get("description")
    task_id = DB.insert_task_table(description, False)
    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Could not create task.", 400)
    return success_response(task, 201)

@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    """
    Endpoint for getting a task by id
    """
    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found!"}), 404
        # return failure_response("Task not found!")
    task["subtasks"] = DB.get_subtasks_of_task(task_id)
    return json.dumps(task), 200
    # return success_response(task)
    
@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    """
    Endpoint for updating a task by id
    """
    body = json.loads(request.data)
    description = body.get("description")
    done = body.get("done")
    DB.update_task_by_id(task_id, description, done)

    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found!"}), 404
        # return failure_response("Task not found!")

    return json.dumps(task), 200
    # return success_response(task)

@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    """
    Endpoint for deleting a task by id
    """
    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found!"}), 404
        # return failure_response("Task not found!")
    DB.delete_task_by_id(task_id)
    # return success_response(task)
    return json.dumps(task), 200

# -- SUBTASK ROUTES ---------------------------------------------------


@app.route("/tasks/<int:task_id>/subtasks/", methods=["POST"])
def create_subtask(task_id):
    """
    Endpoint for creating a subtask
    for a task by id
    """
    
    
    self.conn.execute(
        """
            CREATE TABLE IF NOT EXISTS subtask (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            done BOOLEAN NOT NULL,
            task_id INTEGER NOT NULL,
            FOREIGN KEY (task_id) REFERENCES task(id)
            )
        """
    )


# -- CATEGORY ROUTES --------------------------------------------------


@app.route("/tasks/<int:task_id>/category/", methods=["POST"])
def assign_category(task_id):
    """
    Endpoint for assigning a category
    to a task by id
    """
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
