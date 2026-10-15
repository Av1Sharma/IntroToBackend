# Create an application that manages all your todos to do

import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

tasks = {
    1: {"id": 1, "description": "do your homework", "done": False},
    2: {"id": 2, "description": "go running", "done": False},
}

task_id_counter = 3


@app.route("/")
def hello_world():
    return "Fuck you Richard!"


# your routes here

# Get all tasks
@app.route("/tasks/")
def get_tasks():
    res = {"tasks": list(tasks.values())}
    return json.dumps(res), 200

# Create a task
@app.route("/tasks/", methods = ["POST"])
def create_task():
   global task_id_counter
   body = json.loads(request.data)
   description = body["description"]
   task = {"id": task_id_counter, "description": description, "done": False}
   tasks[task_id_counter] = task
   task_id_counter+=1
   return json.dumps(task), 201

# Get a task by ID
@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"Error": "task not found"}), 404
    return json.dumps(task), 200
    
# Update a task
@app.route("/tasks/<int:task_id>/", methods = ["PUT"])
def update_task():
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"Error": "task not found"}), 404
    body = json.loads(request.data)
    task["description"] = body["description"]
    task["done"] = body["done"]
    return json.dumps(task), 200

# Delete a task
@app.route("/tasks/<int:task_id>/", methods = ["DELETE"])
def delete_task():
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"Error": "task not found"}), 404
    del tasks[task_id]
    return json.dumps({"message": "task deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
