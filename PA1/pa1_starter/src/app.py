import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Fuck you Richard!"


# your routes here


# Create an application that manages all your todos to do

# Get all tasks
# Create a task
# Get a task by ID
# Update a task
# Delete a task


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
