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
   task[task_id_counter] = task
   task_id_counter+=1
   return json.dumps(task), 201
# Get a task by ID
# Update a task
# Delete a task


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
