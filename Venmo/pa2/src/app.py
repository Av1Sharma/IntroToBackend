import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"


@app.route("/api/users/", methods=["POST"])
def get_user():
    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")
    user_id = DB.insert_user_table(username, password)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Could not create user.", 400)
    return success_response(user, 201)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
