import json

from db import db, Task, Subtask, Category
from flask import Flask, request

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
    tasks = []

    for task in Task.query.all():
        tasks.append(task.serialize())

    return success_response({"tasks": tasks})
    
@app.route("/tasks/", methods=["POST"])
def create_task():
    """
    Endpoint for creating a new task
    """
    body = json.loads(request.data)
    new_task = Task(description=body.get("description"), done = body.get("done"))
    db.session.add(new_task)
    db.session.commit()
    return success_response(new_task.serialize(), 201)


@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    """
    Endpoint for getting a task by id
    """
    task = task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response("Task not found!", 404)
    return success_response(task.serialize())
    
@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    """
    Endpoint for updating a task by id
    """
    body = json.loads(request.data)
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response("Task not found!", 404)
    task.description = body.get("description", task.description)
    task.done = body.get("done", task.done)
    db.session.commit()
    return success_response(task.serialize())

@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    """
    Endpoint for deleting a task by id
    """
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response("Task not found!", 404)
    db.session.delete(task)
    db.session.commit()
    return success_response(task.serialize())

# -- SUBTASK ROUTES ---------------------------------------------------


@app.route("/tasks/<int:task_id>/subtasks/", methods=["POST"])
def create_subtask(task_id):
    """
    Endpoint for creating a subtask
    for a task by id
    """
    
    
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response("Task not found!", 404)
    body = json.loads(request.data)
    subtask = Subtask(
        description = body.get("description"),
        done = body.get("done"),
        task_id = task_id
    )
    db.session.add(subtask)
    db.session.commit()
    return success_response(subtask.serialize(), 201)


# -- CATEGORY ROUTES --------------------------------------------------


@app.route("/tasks/<int:task_id>/category/", methods=["POST"])
def assign_category(task_id):
    """
    Endpoint for assigning a category
    to a task by id
    """
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response("Task not found!")

    body = json.loads(request.data)
    description = body.get("description")
    color = body.get("color")

    category = Category.query.filter_by(color=color).first()
    if category is None:
        category = Category(description=description, color=color)

    task.categories.append(category)
    db.session.commit()
    return success_response(task.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
