# client.py
# Ian Wright - Tony Tan
# CSC 154
# Programming Project

import sys
import socket
import threading

# CSC 154 - Commit 3 - Use our JSON functions instead of sending regular text
from protocol import send_json, receive_json


def receive_messages(reader):
    # This still runs in its own thread so I can keep typing while messages come in
    while True:
        try:
            # Get the next JSON message from the server
            message = receive_json(reader)

            # If nothing comes through, the server probably disconnected
            if message is None:
                print("Disconnected from server.")
                break

            # Find out what kind of message the server sent
            message_type = message["type"]

            # For now just print what came back
            # We'll make these look nicer after we get everything connected
            print(message)

            # If the server says goodbye, stop receiving
            if message_type == "goodbye":
                break

        except Exception as e:
            # If something breaks, stop this receiving thread
            print("Error receiving message:", e)
            break



def show_menu():
    print("\n========== CHAT COMMANDS ==========")
    print("LIST    Show connected users")
    print("HELP    Show this menu again")
    print("QUIT    Leave the chatroom")
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

    # CSC 154 - Commit 3 - Make a reader for JSON messages
    # rb means read binary, so we can read the bytes coming from the server
    reader = client_socket.makefile("rb")

    
    # CSC 154 - Commit 3 - Use our JSON reader for incoming messages
    # This thread still lets me receive messages while I'm typing
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(reader,)
    )


    # Daemon means this thread dies too when the program closes.
    receive_thread.daemon = True

    # Start the thread.
    receive_thread.start()

    
    # CSC 154 - Commit 3 - Register the user with JSON instead of JOIN
    # Just type the username now, we don't need to type JOIN anymore
    username = input("Enter your username: ").strip()

    # Make sure they actually typed something
    while not username:
        print("Please enter a username.")
        username = input("Enter your username: ").strip()

    # Send the username to the server using JSON
    send_json(client_socket, {
        "type": "register",
        "username": username
    })

    # Show the commands after registering
    show_menu()


    # Keep letting the user type commands.
    while True:
        try:
            # Read whatever the user types.
            user_input = input().strip()

            # Ignore empty enter presses.
            if not user_input:
                continue

            
            # CSC 154 - Commit 3 - Send commands using JSON now
            # Make the command uppercase so list and LIST both work
            command = user_input.upper()

            if command == "LIST":
                # Ask the server who is connected
                send_json(client_socket, {
                    "type": "users_request"
                })

            elif command == "QUIT":
                # Tell the server we're leaving
                send_json(client_socket, {
                    "type": "quit"
                })
                break

            elif command == "HELP":
                # Just show the commands again
                show_menu()

            else:
                # We haven't added encrypted messages yet
                print("Unknown command. Try LIST, HELP, or QUIT.")


        except KeyboardInterrupt:
            # If Ctrl+C happens try to quit normally first.
            try:
                # Send quit using JSON instead of regular text
                send_json(client_socket, {"type": "quit"})
            except Exception:
                pass

            break

        except Exception:
            # If something random breaks just leave the loop.
            break

    
    # Give the receiving thread a chance to get the goodbye message
    # Wait up to 2 seconds before closing the client
    receive_thread.join(timeout=2)

    # Close the reader if the thread is finished
    if not receive_thread.is_alive():
        reader.close()

    # Close the socket before ending thepython client.py 127.0.0.1 5000 program
    client_socket.close()
    print("Client closed.")


if __name__ == "__main__":
    main()