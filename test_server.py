
# test_server.py
# CSC 154 - Commit 2
# Test two users connecting to our JSON server

import socket
from protocol import send_json, receive_json

# Connect Alice and Bob to the server
alice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

alice.connect(("127.0.0.1", 5000))
bob.connect(("127.0.0.1", 5000))

alice_reader = alice.makefile("rb")
bob_reader = bob.makefile("rb")

# Register Alice
send_json(alice, {"type": "register", "username": "Alice"})
print("Alice:", receive_json(alice_reader))

# Register Bob
send_json(bob, {"type": "register", "username": "Bob"})
print("Bob:", receive_json(bob_reader))

# Alice gets notified that Bob joined
print("Alice notification:", receive_json(alice_reader))

# Ask for the list of connected users
send_json(alice, {"type": "users_request"})
print("Connected users:", receive_json(alice_reader))

# Bob leaves the chat
send_json(bob, {"type": "quit"})
print("Bob:", receive_json(bob_reader))

# Alice gets notified that Bob left
print("Alice notification:", receive_json(alice_reader))

# Check the user list again
send_json(alice, {"type": "users_request"})
print("Remaining users:", receive_json(alice_reader))

# Alice leaves too
send_json(alice, {"type": "quit"})
print("Alice:", receive_json(alice_reader))

# Close everything when we're done
alice_reader.close()
bob_reader.close()
alice.close()
bob.close()

print("Server test finished.")
