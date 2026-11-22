# client.py
# Ian Wright
# CSC 138
# Programming Project

import sys
import socket
import threading

def receive_messages(client_socket):
    # This function runs in a separate thread and just keeps waiting for messages from the server.
    while True:
        try:
            # Grab whatever the server sends over.
            message = client_socket.recv(4096)

            # If nothing comes through anymore the server probably closed.
            if not message:
                print("Disconnected from server.")
                break

            # Decode turns the bytes back into normal text.
            print(message.decode().strip())

        except Exception:
            # If something breaks with the socket just stop the loop.
            break

def show_menu():
    print("\n========== CHAT COMMANDS ==========")
    print("LIST              Show connected users")
    print("MESG <user> <msg> Send a private message")
    print("BCST <message>    Message everyone")
    print("LOG               View your chat history")
    print("HELP              Show this menu again")
    print("QUIT              Leave the chatroom")
    print("===================================\n")

def main():
    # Need hostname and port or else the client will not know where to connect.
    if len(sys.argv) != 3:
        print("usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    # Grab the hostname and port from command line.
    host = sys.argv[1]
    port = int(sys.argv[2])

    # Make the TCP socket.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Try connecting to the server.
    try:
        client_socket.connect((host, port))

    except Exception as e:
        # If it cannot connect just print the error and quit.
        print("Could not connect to server:", e)
        sys.exit(1)

    # Make another thread that only handles receiving messages.
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,)
    )

    # Daemon means this thread dies too when the program closes.
    receive_thread.daemon = True

    # Start the thread.
    receive_thread.start()

    # First thing user should do is JOIN.
    user_input = input("Enter JOIN followed by your username: ").strip()

    if user_input:

        # If I only type my username this automatically adds JOIN.
        # Example: bob becomes JOIN bob.
        if not user_input.startswith("JOIN "):
            user_input = "JOIN " + user_input

        # Send JOIN message to server.
        client_socket.sendall(user_input.encode())
        show_menu()

    # Keep letting the user type commands.
    while True:
        try:
            # Read whatever the user types.
            user_input = input().strip()

            # Ignore empty enter presses.
            if not user_input:
                continue

            # Send the message/command to the server.
            client_socket.sendall(user_input.encode())

            # If user types QUIT end the client.
            if user_input == "QUIT":
                break

        except KeyboardInterrupt:
            # If Ctrl+C happens try to quit normally first.
            try:
                client_socket.sendall("QUIT".encode())
            except Exception:
                pass

            break

        except Exception:
            # If something random breaks just leave the loop.
            break

    # Close the socket before ending the program.
    client_socket.close()
    print("Client closed.")

if __name__ == "__main__":
    main()