
# protocol.py
# CSC 154
# Secure Chat Application
# Handles JSON messages between the client and server

import json

# Maximum size of one message (64 KB)
MAX_MESSAGE_SIZE = 65536


def send_json(client_socket, message):
    # Make sure the message is a dictionary with a type
    if not isinstance(message, dict) or not isinstance(message.get("type"), str):
        raise ValueError("Invalid message format.")

    # Convert the dictionary into JSON text
    json_message = json.dumps(message)

    # Add a newline so the receiver knows where the message ends
    data = (json_message + "\n").encode()

    # Make sure the message is not too large
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large.")

    # Send the entire message over TCP
    client_socket.sendall(data)


def receive_json(reader):
    # Read one complete message from the connection
    # The newline tells us where the message ends
    data = reader.readline(MAX_MESSAGE_SIZE + 1)

    # If nothing comes through, the connection was closed
    if not data:
        return None

    # Reject messages that are too large
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large.")

    # If there is no newline, the message was incomplete
    if not data.endswith(b"\n"):
        raise ValueError("Incomplete message received.")

    try:
        # Convert JSON text back into a Python dictionary
        message = json.loads(data.decode())

    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid JSON message received.")

    # Make sure the message has a valid type field
    if not isinstance(message, dict) or not isinstance(message.get("type"), str):
        raise ValueError("Invalid message format.")

    return message
