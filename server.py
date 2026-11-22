# server.py
# Ian Wright
# CSC 138
# Programming Project
# Chat Server

import os
import sys
import socket
import threading
import time

# Only 10 users can be registered in the chat at once
MAX_USERS = 10

# This is where the log files will go
LOG_DIR = "chat_logs"

# This dictionary keeps track of users in the chat
# username is the key, and their socket is the value
clients = {}

# This lock is here because multiple threads could touch clients at the same time
clients_lock = threading.Lock()

def get_time_stamp():
    # This just makes the time look nice for the log
    return time.strftime("%Y-%m-%d %H:%M:%S")

def write_log(username, log_message):
    # This writes one line to a user's log file
    if username is None:
        return

    # Make the log folder if it does not exist yet
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Each user gets their own log file
    file_path = os.path.join(LOG_DIR, username + ".txt")

    # Append means add to the file instead of deleting old stuff
    with open(file_path, "a") as f:
        f.write(log_message + "\n")

def read_log(username):
    # This reads the log file for whoever asked for LOG
    file_path = os.path.join(LOG_DIR, username + ".txt")

    # If they have no log yet, just tell them
    if not os.path.exists(file_path):
        return "No chat history found.\n"

    # Send back everything in their log file
    with open(file_path, "r") as f:
        return f.read()

def client_handler(client_socket, client_address):
    # This function handles one client in its own thread
    print("Connected with", client_address)

    # If the client does nothing for 300 seconds, it times out
    client_socket.settimeout(300)

    # Starts as None because they have not joined yet
    username = None

    while True:
        try:
            # Wait for something from this client
            data = client_socket.recv(1024)

            # If nothing came in, the client probably left
            if not data:
                print("Client disconnected:", client_address)
                break

            # Turn bytes into text and clean it up
            message = data.decode().strip()

            # Split off the command part from the rest of the message
            command_parts = message.split(" ", 1)
            command = command_parts[0]

            # Print what the server got, just so I can see what is happening
            print("Received from", client_address, ":", message)

            # JOIN username
            if command == "JOIN":
                # If they typed JOIN with no name, tell them the right format
                if len(command_parts) < 2:
                    client_socket.sendall("Use: JOIN <username>\n".encode())
                    continue

                # This is the username they want to use
                requested_username = command_parts[1].strip()

                with clients_lock:
                    # If this socket already joined, don't let it join again
                    if username is not None:
                        client_socket.sendall("You are already registered.\n".encode())

                    # If 10 users are already in, reject this client
                    elif len(clients) >= MAX_USERS:
                        client_socket.sendall("Too Many Users\n".encode())
                        print("Too many users. Closing connection for", client_address)
                        break

                    # If someone already has this username, reject it
                    elif requested_username in clients:
                        client_socket.sendall("Username already taken.\n".encode())

                    else:
                        # Save this user into the clients dictionary
                        username = requested_username
                        clients[username] = client_socket

                        # Tell this client they joined
                        client_socket.sendall((username + " joined! Connected to server!\n").encode())
                        print(username, "Joined the Chatroom")

                        # Tell everyone else this person joined
                        for other_username, other_socket in clients.items():
                            if other_username != username:
                                try:
                                    other_socket.sendall((username + " joined!\n").encode())
                                except Exception:
                                    print("Could not notify", other_username)

            # LIST
            elif command == "LIST":
                # They need to JOIN before using LIST
                if username is None:
                    client_socket.sendall("Unregistered User. Please JOIN first using: JOIN <username>\n".encode())
                else:
                    # Join all the usernames together with commas
                    with clients_lock:
                        user_list = ",".join(clients.keys())

                    client_socket.sendall((user_list + "\n").encode())
                    print(username, "requested LIST")

            # MESG username message
            elif command == "MESG":
                # They need to JOIN before sending messages
                if username is None:
                    client_socket.sendall("Unregistered User. Please JOIN first using: JOIN <username>\n".encode())
                else:
                    # Split into MESG, receiver, and the actual message
                    parts = message.split(" ", 2)

                    # If they did not type enough parts, show the format
                    if len(parts) < 3:
                        client_socket.sendall("Use: MESG <username> <message>\n".encode())
                    else:
                        receiver = parts[1]
                        text = parts[2]

                        # Look up the receiver's socket
                        with clients_lock:
                            receiver_socket = clients.get(receiver)

                        # If that username is not in the chat, we cannot send it
                        if receiver_socket is None:
                            client_socket.sendall("Unknown Recipient\n".encode())
                            print(username, "tried to message unknown user:", receiver)
                        else:
                            # Send the message to the receiver
                            receiver_socket.sendall((username + ": " + text + "\n").encode())

                            # Tell sender it was sent
                            client_socket.sendall(("Message sent to " + receiver + "\n").encode())

                            # Save this in both users' logs
                            time_stamp = get_time_stamp()
                            write_log(username, "[" + time_stamp + "] INFO: Message sent by " + username + " to " + receiver + " - \"" + text + "\"")
                            write_log(receiver, "[" + time_stamp + "] INFO: Message received by " + receiver + " from " + username + " - \"" + text + "\"")

                            print(username, "sent message to", receiver, ":", text)

            # BCST message
            elif command == "BCST":
                # They need to JOIN before broadcasting
                if username is None:
                    client_socket.sendall("Unregistered User. Please JOIN first using: JOIN <username>\n".encode())
                else:
                    # If there is no message after BCST, show the format
                    if len(command_parts) < 2:
                        client_socket.sendall("Use: BCST <message>\n".encode())
                    else:
                        text = command_parts[1].strip()

                        # If BCST is empty, still show the format
                        if not text:
                            client_socket.sendall("Use: BCST <message>\n".encode())
                        else:
                            print(username, "is sending a broadcast")

                            # Send the broadcast to everyone except the sender
                            with clients_lock:
                                for other_username, other_socket in clients.items():
                                    if other_username != username:
                                        try:
                                            other_socket.sendall((username + ": " + text + "\n").encode())
                                        except Exception:
                                            print("Could not send broadcast to", other_username)

                            # Also show it on the sender's screen
                            client_socket.sendall((username + ": " + text + "\n").encode())

                            # Save broadcast in log files
                            time_stamp = get_time_stamp()

                            with clients_lock:
                                for other_username in clients.keys():
                                    if other_username != username:
                                        write_log(other_username, "[" + time_stamp + "] INFO: Broadcast received by " + other_username + " from " + username + " - \"" + text + "\"")

                            write_log(username, "[" + time_stamp + "] INFO: Broadcast sent by " + username + " - \"" + text + "\"")

            # LOG
            elif command == "LOG":
                # They need to JOIN before seeing their log
                if username is None:
                    client_socket.sendall("Unregistered User. Please JOIN first using: JOIN <username>\n".encode())
                else:
                    # Read this user's log and send it back
                    history = read_log(username)
                    client_socket.sendall(history.encode())
                    print(username, "requested LOG")

            # QUIT
            elif command == "QUIT":
                if username is not None:
                    print(username, "is quitting the chat server")
                    client_socket.sendall((username + " is quitting the chat server\n").encode())

                    # Tell everyone else this user left
                    with clients_lock:
                        for other_username, other_socket in clients.items():
                            if other_username != username:
                                try:
                                    other_socket.sendall((username + " left\n").encode())
                                except Exception:
                                    print("Could not notify", other_username)
                else:
                    # Even if they never joined, close them out
                    client_socket.sendall("Goodbye.\n".encode())

                break

            else:
                # If they are not joined, remind them to JOIN first
                if username is None:
                    client_socket.sendall("Unregistered User. Please JOIN first using: JOIN <username>\n".encode())
                else:
                    # If they typed something random, this is the required error
                    client_socket.sendall("Unknown Message\n".encode())
                    print(username, "sent unknown message")

        except socket.timeout:
            # This happens if they sit there too long without sending anything
            if username is not None:
                print(username + "'s session is terminated due to inactivity.")

                try:
                    client_socket.sendall("Disconnected due to inactivity.\nGoodbye.\n".encode())
                except Exception:
                    pass

                # Tell everyone else they left because of timeout
                with clients_lock:
                    for other_username, other_socket in clients.items():
                        if other_username != username:
                            try:
                                other_socket.sendall((username + " left due to inactivity\n").encode())
                            except Exception:
                                print("Could not notify", other_username)
            else:
                print("Unregistered client timed out:", client_address)

            break

        except Exception as e:
            # Catch anything else so one bad client does not crash the whole server
            print("Error with client", client_address, ":", e)
            break

    # Remove the user from the chat if they were registered
    with clients_lock:
        if username is not None and username in clients:
            del clients[username]
            print(username, "left the chatroom")

    # Close this client's socket
    client_socket.close()
    print("Connection closed for", client_address)

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

    print("The Chat Server Started")

    while True:
        # Wait for a new client to connect
        client_socket, client_address = server_socket.accept()

        # Make a thread for this client
        client_thread = threading.Thread(
            target=client_handler,
            args=(client_socket, client_address)
        )

        # Start the client thread
        client_thread.start()

if __name__ == "__main__":
    main()