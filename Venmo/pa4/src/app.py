import math
import os
from flask import Flask, jsonify, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(body, code=200):
    """
    Generalized success response format returning JSON and status code.
    """
    return jsonify(body), code


def failure_response(message, code=404):
    """
    Generalized failure response format returning an error message and status code.
    """
    return jsonify({"error": message}), code


@app.route("/")
def hello_world():
    """
    Root endpoint for sanity check.
    """
    return "Hello world!"


@app.route("/api/users/")
def get_all_users():
    """
    Endpoint for getting all users.
    Omits user balance for confidentiality.
    """
    return success_response({"users": DB.get_all_users()}, 200)


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user.
    Requires name and username, with balance defaulting to 0 if not provided.
    """
    body = request.get_json(force=True, silent=True)
    if not isinstance(body, dict):
        return failure_response("Request body must be a JSON object.", 400)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)

    if (not isinstance(name, str) or not name.strip()
            or not isinstance(username, str) or not username.strip()):
        return failure_response("Name and username must be provided.", 400)

    if type(balance) is not int or not 0 <= balance < 2**63:
        return failure_response("Balance must be a non-negative integer.", 400)

    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Could not create user.", 400)
    return success_response(user, 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a specific user by id.
    Returns the user's profile, balance, and transaction history.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.", 404)
    return success_response(user, 200)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a specific user by id.
    Returns the data of the deleted user.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.", 404)
    DB.delete_user_by_id(user_id)
    return success_response(user, 200)


@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    """Send money immediately or record a pending payment request."""
    body = request.get_json(force=True, silent=True)
    if not isinstance(body, dict):
        return failure_response("Request body must be a JSON object.", 400)
    required = ("sender_id", "receiver_id", "amount", "message", "accepted")
    if any(field not in body for field in required):
        return failure_response("All transaction fields must be provided.", 400)
    sender_id = body["sender_id"]
    receiver_id = body["receiver_id"]
    amount = body["amount"]
    accepted = body["accepted"]
    if (type(sender_id) is not int or type(receiver_id) is not int
            or not 0 < sender_id < 2**63 or not 0 < receiver_id < 2**63):
        return failure_response("User IDs must be positive integers.", 400)
    if sender_id == receiver_id:
        return failure_response("Sender and receiver must be different users.", 400)
    if (type(amount) not in (int, float) or amount <= 0
            or amount >= 2**63 or not math.isfinite(amount)):
        return failure_response("Amount must be a finite positive number.", 400)
    if not isinstance(body["message"], str):
        return failure_response("Message must be a string.", 400)
    if accepted is not None and accepted is not True:
        return failure_response("Accepted must be true or null when creating.", 400)
    try:
        transaction = DB.create_transaction(
            sender_id, receiver_id, amount, body["message"], accepted
        )
    except db.PaymentError as error:
        return failure_response(str(error), error.code)
    return success_response(transaction, 201)


@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def resolve_transaction(transaction_id):
    """Accept or deny a pending request exactly once."""
    body = request.get_json(force=True, silent=True)
    if not isinstance(body, dict) or type(body.get("accepted")) is not bool:
        return failure_response("Accepted must be true or false.", 400)
    try:
        transaction = DB.resolve_transaction(transaction_id, body["accepted"])
    except db.PaymentError as error:
        return failure_response(str(error), error.code)
    return success_response(transaction)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
