import math
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

    if type(balance) is not int or balance < 0:
        return failure_response("Balance must be a non-negative integer.", 400)

    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Could not create user.", 400)
    return success_response(user, 201)


@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a specific user by id.
    Returns the user's id, name, username, and balance.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.", 404)
    return success_response(user, 200)


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
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


@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Endpoint for sending money from one user to another.
    Updates the balances of both sender and receiver.
    """
    body = request.get_json(force=True, silent=True)
    if not isinstance(body, dict):
        return failure_response("Request body must be a JSON object.", 400)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")

    # Ensure none of the fields are missing (0 is a valid id so check `is None`)
    if sender_id is None or receiver_id is None or amount is None:
        return failure_response(
            "sender_id, receiver_id, and amount must all be provided.", 400
        )

    if type(sender_id) is not int or type(receiver_id) is not int:
        return failure_response("Sender and receiver IDs must be integers.", 400)

    # Reject negative amounts, booleans, and non-finite numbers.
    if (type(amount) not in (int, float) or amount < 0
            or (type(amount) is float and not math.isfinite(amount))):
        return failure_response("Amount must be a non-negative number.", 400)

    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)

    # Validate that both sender and receiver exist
    if sender is None or receiver is None:
        return failure_response("Sender or receiver not found.", 404)

    # Prevent sender from overdrawing balance
    if sender["balance"] < amount:
        return failure_response(
            "Sender does not have sufficient balance to send this amount.", 400
        )

    # Keep both updates together; sending to yourself leaves the balance unchanged.
    DB.transfer_money(sender_id, receiver_id, amount)

    return success_response(
        {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
        },
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
