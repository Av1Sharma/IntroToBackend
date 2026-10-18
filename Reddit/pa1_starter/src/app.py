import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
    1: {"id": 1, "upvotes": 1, "title": "Post 1", "title": "My cat is the cutest", 
    "link": "https://i.imgur.com/jseZqNK.jpg", "username": "alicia98"},
    2: {"id": 2, "upvotes": 3, "title": "Post 2", "title": "Cat loaf", 
    "link": "https://i.imgur.com/TJ46wX4.jpg", "username": "alicia98"},
}

@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
