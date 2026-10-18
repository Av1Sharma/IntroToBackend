import json

from flask import Flask, request

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
    """Return a simple greeting."""
    return "Hello world!"


# -- Core Routes -----------------------------------------------------------


@app.route("/api/posts/", methods=["GET"])
def get_posts():
    """Get all posts in the datastore."""
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200


@app.route("/api/posts/", methods=["POST"])
def create_post():
    """Create a new post."""
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
    """Get a specific post by post id."""
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps(post), 200


@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    """Delete a specific post by post id."""
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    del posts[post_id]
    return json.dumps(post), 200


@app.route("/api/posts/<int:post_id>/comments/", methods=["GET"])
def get_comments(post_id):
    """Get all comments for a specific post."""
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps({"comments": post["comments"]}), 200


@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    """Create a new comment on a specific post."""
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
    """Edit the text of an existing comment on a post."""
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


# -- Extra Credit Routes ---------------------------------------------------


@app.route("/api/extra/posts/", methods=["GET"])
def extra_get_posts():
    """Get all posts, optionally sorted by upvotes via URL parameters."""
    sort_param = request.args.get("sort")
    posts_list = list(posts.values())
    if sort_param == "increasing":
        posts_list.sort(key=lambda x: x["upvotes"])
    elif sort_param == "decreasing":
        posts_list.sort(key=lambda x: x["upvotes"], reverse=True)
    return json.dumps({"posts": posts_list}), 200


@app.route("/api/extra/posts/", methods=["POST"])
def extra_create_post():
    """Create a post with validated body field types."""
    global post_id_counter
    try:
        body = json.loads(request.data)
    except Exception:
        return json.dumps({"error": "Invalid JSON"}), 400
    if not isinstance(body, dict):
        return json.dumps({"error": "Invalid body"}), 400
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    if not (isinstance(title, str) and isinstance(link, str) and isinstance(username, str)):
        return json.dumps({"error": "Missing or invalid fields (title, link, and username must be strings)"}), 400
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


@app.route("/api/extra/posts/<int:post_id>/", methods=["POST"])
def extra_upvote_post(post_id):
    """Increment the upvote count of a post by a given amount (default 1)."""
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404

    upvotes_to_add = 1
    if request.data:
        try:
            body = json.loads(request.data)
            if isinstance(body, dict) and "upvotes" in body:
                if isinstance(body["upvotes"], int):
                    upvotes_to_add = body["upvotes"]
                else:
                    return json.dumps({"error": "Invalid upvotes value"}), 400
        except json.JSONDecodeError:
            pass

    post["upvotes"] += upvotes_to_add
    return json.dumps(post), 200


@app.route("/api/extra/posts/<int:post_id>/comments/", methods=["POST"])
def extra_create_comment(post_id):
    """Create a comment with validated body field types."""
    global post_comment_counter
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    try:
        body = json.loads(request.data)
    except Exception:
        return json.dumps({"error": "Invalid JSON"}), 400
    if not isinstance(body, dict):
        return json.dumps({"error": "Invalid body"}), 400
    text = body.get("text")
    username = body.get("username")
    if not (isinstance(text, str) and isinstance(username, str)):
        return json.dumps({"error": "Missing or invalid fields (text and username must be strings)"}), 400
    comment = {
        "id": post_comment_counter,
        "upvotes": 1,
        "text": text,
        "username": username,
    }
    post["comments"].append(comment)
    post_comment_counter += 1
    return json.dumps(comment), 201


@app.route("/api/extra/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def extra_edit_comment(post_id, comment_id):
    """Edit comment text with validated body field types."""
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    try:
        body = json.loads(request.data)
    except Exception:
        return json.dumps({"error": "Invalid JSON"}), 400
    if not isinstance(body, dict):
        return json.dumps({"error": "Invalid body"}), 400
    text = body.get("text")
    if not isinstance(text, str):
        return json.dumps({"error": "Missing or invalid field (text must be string)"}), 400
    for comment in post["comments"]:
        if comment["id"] == comment_id:
            comment["text"] = text
            return json.dumps(comment), 200
    return json.dumps({"error": "Comment not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
