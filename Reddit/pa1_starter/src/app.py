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

post_id_counter = 3
post_comment_counter = 3

@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here

@app.route("/posts/", methods = ["GET"])
def get_posts():
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200

@app.route("/posts/", methods = ["POST"])
def create_post():
    global post_id_counter
    body = json.loads(request.data)
    title = body["title"]
    link = body["link"]
    username = body["username"]
    post = {"id": post_id_counter, "upvotes": 0, "title": title, "link": link, "username": username}
    posts[post_id_counter] = post
    post_id_counter += 1
    return json.dumps(post), 201

@app.route("/posts/<int:post_id>", methods = ["GET"])
def get_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"Error": "post not found"}), 404
    return json.dumps(post), 200

@app.route("/posts/<int:post_id>", methods = ["DEL"])
def delete_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"Error": "post not found"}), 404
    del posts[post_id]
    return json.dumps(post), 200

@app.route("/posts/<int:post_id>", methods = ["GET"])
def get_comments(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"Error": "post not found"}), 404
    return json.dumps(post["comments"])

@app.route("/posts/<int:post_id>/comments/", methods = ["POST"])
def create_comment(post_id):
    global post_comment_counter
    body = json.loads(request.data)
    comment = {"id": post_comment_counter, "comment": body["comment"], "username": body["username"]}
    posts[post_id]["comments"].append(comment)
    post_comment_counter += 1
    return json.dumps(comment), 201

@app.route("/posts/<int:post_id>/<int:comment_id>", methods = ["POST"])
def edit_comment(post_id, comment_id):
    

    

    
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
