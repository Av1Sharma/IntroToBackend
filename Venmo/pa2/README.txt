Name: Avi Sharma
NetID: as4632

Challenges Attempted: None

Run from the pa2 folder:
1. Install dependencies: python3 -m pip install -r src/requirements.txt
2. Start the API: python3 src/app.py
3. Import Assignment2Tests.postman_collection.json into Postman.
   Run requests in order on a fresh database. CreateReceiver is setup for
   sending money between two different users. No request scripts are used.
   Expected statuses: 200, 201, 201, 200, 200, 200.
   The transfer returns sender_id 1, receiver_id 2, and amount 10.
   After the transfer, user 1 has balance 90 and user 2 has balance 10.

Run the course tests:
Stop the API first (Ctrl+C) because pa2_test.py starts its own server on
port 5000. With the downloaded pa2_test.py in src, run:
    python3 src/pa2_test.py
Extra credit routes are not implemented; do not use --extra.

Fresh database:
Stop any running server, then delete src/venmo.db before running the
Postman collection. SQLite creates this file automatically on startup.
The database path is always src/venmo.db regardless of working directory.

Submission:
The submission zip contains README.txt, the Postman JSON, app.py, db.py,
and requirements.txt. Database files, virtual environments, caches, and
the downloaded course test script are excluded. Complete the course
feedback form separately.
