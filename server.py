
# server.py
# Ian Wright - Tony Tan
# CSC 154
# Programming Project
# Chat Server
# CSC 154 - Commit 2 - Change the server to use JSON

import sys
import socket
import threading

# Use the JSON functions we made in Commit 1
from protocol import send_json, receive_json

# Only 10 users can be registered in the chat at once
MAX_USERS = 10

# This dictionary keeps track of users in the chat
# Each username has a socket and a lock for sending messages
clients = {}

# This lock is here because multiple threads could touch clients at the same time
clients_lock = threading.Lock()


def send_message(client_socket, send_lock, message):
    # Only let one thread send to this client at a time
    # This way two JSON messages don't get mixed together
    with send_lock:
        send_json(client_socket, message)


def client_handler(client_socket, client_address):
    # This function handles one client in its own thread
    print("Connected with", client_address)

    # If the client does nothing for 300 seconds, it times out
    client_socket.settimeout(300)

    # Starts as None because they have not registered yet
    username = None

    # Read one complete JSON message at a time
    # rb means read binary, since the socket gives us bytes
    reader = client_socket.makefile("rb")

    # Every client gets its own lock so sends don't overlap
    send_lock = threading.Lock()

    try:
        while True:
            try:
                # Wait for the next JSON message from this client
                message = receive_json(reader)

                # If nothing comes through, the client probably left
                if message is None:
                    print("Client disconnected:", client_address)
                    break

                # Get the command from the type in the JSON message
                command = message["type"]
                print("Received command from", client_address, ":", command)

                # REGISTER username (this replaces JOIN from CSC 138)
                if command == "register":
                    # Grab the username from the JSON message
                    requested_username = message.get("username")

                    # Make sure they actually gave us a username
                    if not isinstance(requested_username, str) or not requested_username.strip():
                        send_message(client_socket, send_lock, {
                            "type": "error",
                            "message": "Please enter a valid username."
                        })
                        continue

                    requested_username = requested_username.strip()

                    # Check everything before letting them register
                    with clients_lock:
                        if username is not None:
                            error = "You are already registered."

                        elif len(clients) >= MAX_USERS:
                            error = "Too many users."

                        elif requested_username in clients:
                            error = "Username already taken."

                        else:
                            # Save this username with their socket and send lock
                            username = requested_username
                            clients[username] = (client_socket, send_lock)
                            error = None

                            # Get the other users so we can tell them who joined
                            other_clients = [
                                info for name, info in clients.items()
                                if name != username
                            ]

                    if error is not None:
                        send_message(client_socket, send_lock, {
                            "type": "error",
                            "message": error
                        })
                        continue

                    # Tell this client they joined
                    send_message(client_socket, send_lock, {
                        "type": "registered",
                        "username": username,
                        "message": username + " joined! Connected to server!"
                    })
                    print(username, "Joined the Chatroom")

                    # Tell everyone else this user joined
                    for other_socket, other_lock in other_clients:
                        try:
                            send_message(other_socket, other_lock, {
                                "type": "user_joined",
                                "username": username
                            })
                        except Exception:
                            print("Could not notify another user")

                # LIST (now sent as users_request through JSON)
                elif command == "users_request":
                    # They need to register before using LIST
                    if username is None:
                        send_message(client_socket, send_lock, {
                            "type": "error",
                            "message": "Unregistered User. Please register first."
                        })
                    else:
                        # Get everyone who is connected
                        with clients_lock:
                            user_list = list(clients.keys())

                        # Send the user list back as JSON
                        send_message(client_socket, send_lock, {
                            "type": "users_response",
                            "users": user_list
                        })
                        print(username, "requested LIST")

                # QUIT (now sent as quit through JSON)
                elif command == "quit":
                    # Tell the user goodbye and then leave the loop
                    send_message(client_socket, send_lock, {
                        "type": "goodbye",
                        "message": "Goodbye."
                    })
                    print(username or "Unregistered client", "is quitting")
                    break

                else:
                    # We haven't added encrypted messaging yet
                    # Don't use the old plaintext MESG, BCST or LOG commands
                    send_message(client_socket, send_lock, {
                        "type": "error",
                        "message": "Unknown Message"
                    })

            except socket.timeout:
                # This happens if they sit there too long
                print("Client timed out:", client_address)
                break

            except ValueError as e:
                # The JSON message was missing something or was not valid
                print("Invalid JSON from", client_address, ":", e)
                try:
                    send_message(client_socket, send_lock, {
                        "type": "error",
                        "message": str(e)
                    })
                except Exception:
                    pass
                break

            except Exception as e:
                # If something breaks with this client, don't crash the server
                print("Error with client", client_address, ":", e)
                break

    finally:
        # Remove this user when they leave or lose the connection
        with clients_lock:
            if username is not None and username in clients:
                del clients[username]
                print(username, "left the chatroom")

                # Grab everyone who's still online
                other_clients = list(clients.values())
            else:
                other_clients = []

        # Close our reader and socket when we're done
        reader.close()
        client_socket.close()
        print("Connection closed for", client_address)

        # Tell everyone else that this user left
        if username is not None:
            for other_socket, other_lock in other_clients:
                try:
                    send_message(other_socket, other_lock, {
                        "type": "user_left",
                        "username": username
                    })
                except Exception:
                    print("Could not notify another user")


def main():
    # Server needs the port number from the command line
    if len(sys.argv) != 2:
        print("usage: python3 server.py <svr_port>")
        sys.exit(1)

    # Convert the port into an int
    port = int(sys.argv[1])

    # Make TCP server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Lets me reuse the port if I restart the server fast
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to all interfaces on this port
    server_socket.bind(("0.0.0.0", port))

    # Start listening for clients
    server_socket.listen(10)

    
    # Start listening for clients
    server_socket.listen(10)

    # Check every second instead of waiting forever
    # This way Ctrl+C can stop the server
    server_socket.settimeout(1.0)

    print("The Chat Server Started")
    print("Press Ctrl+C to stop the server")

    try:
        while True:
            try:
                # Wait for a new client to connect
                client_socket, client_address = server_socket.accept()

            except socket.timeout:
                # Nobody connected yet, just keep waiting
                continue

            # Make a thread for this client
            client_thread = threading.Thread(
                target=client_handler,
                args=(client_socket, client_address)
            )

            # This way client threads won't stop the server from closing
            client_thread.daemon = True

            client_thread.start()

    except KeyboardInterrupt:
        # If I press Ctrl+C, stop the server
        print("\nStopping the chat server...")

    finally:
        # Close the server socket before ending
        server_socket.close()
        print("Chat Server Closed")


if __name__ == "__main__":
    main()
