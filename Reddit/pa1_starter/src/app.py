import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
    1: {
        "id": 1,
        "upvotes": 1,
        "title": "My cat is the cutest",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "alicia98",
        "comments": [],
    },
    2: {
        "id": 2,
        "upvotes": 3,
        "title": "Cat loaf",
        "link": "https://i.imgur.com/TJ46wX4.jpg",
        "username": "alicia98",
        "comments": [],
    },
}

post_id_counter = 3
post_comment_counter = 1


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here


@app.route("/api/posts/", methods=["GET"])
def get_posts():
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200


@app.route("/api/posts/", methods=["POST"])
def create_post():
    global post_id_counter
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    if title is None or link is None or username is None:
        return json.dumps({"error": "Missing required field (title, link, or username)"}), 400
    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": title,
        "link": link,
        "username": username,
        "comments": [],
    }
    posts[post_id_counter] = post
    post_id_counter += 1
    return json.dumps(post), 201


@app.route("/api/posts/<int:post_id>/", methods=["GET"])
def get_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps(post), 200


@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    del posts[post_id]
    return json.dumps(post), 200


@app.route("/api/posts/<int:post_id>/comments/", methods=["GET"])
def get_comments(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps({"comments": post["comments"]}), 200


@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    global post_comment_counter
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    if text is None or username is None:
        return json.dumps({"error": "Missing required field (text or username)"}), 400
    comment = {
        "id": post_comment_counter,
        "upvotes": 1,
        "text": text,
        "username": username,
    }
    post["comments"].append(comment)
    post_comment_counter += 1
    return json.dumps(comment), 201


@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def edit_comment(post_id, comment_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    body = json.loads(request.data)
    text = body.get("text")
    if text is None:
        return json.dumps({"error": "Missing required field (text)"}), 400
    for comment in post["comments"]:
        if comment["id"] == comment_id:
            comment["text"] = text
            return json.dumps(comment), 200
    return json.dumps({"error": "Comment not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
