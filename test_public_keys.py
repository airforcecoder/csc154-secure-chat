
# test_public_keys.py
# Ian Wright - Tony Tan
# CSC 154 - Commit 7 - Testing public keys

import socket
from cryptography.hazmat.primitives import serialization
from crypto_utils import generate_key_pair
from protocol import send_json, receive_json


# This function turns our public key into PEM text.
# The server needs the key as text so we can send it using JSON.
def get_public_pem(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")


# This function tests registering users and requesting public keys.
# Alice should be able to get Bob's public key from the server.
def test_public_keys():
    # Make RSA keys for Alice and Bob
    alice_private, alice_public = generate_key_pair()
    bob_private, bob_public = generate_key_pair()

    alice_pem = get_public_pem(alice_public)
    bob_pem = get_public_pem(bob_public)

    # Connect both users to the server
    alice = socket.create_connection(("127.0.0.1", 5000))
    bob = socket.create_connection(("127.0.0.1", 5000))

    alice_reader = alice.makefile("rb")
    bob_reader = bob.makefile("rb")

    try:
        # Register Alice with her public key
        send_json(alice, {
            "type": "register",
            "username": "alice",
            "public_key": alice_pem
        })

        response = receive_json(alice_reader)
        assert response["type"] == "registered"
        print("Alice registered!")

        # Register Bob with his public key
        send_json(bob, {
            "type": "register",
            "username": "bob",
            "public_key": bob_pem
        })

        response = receive_json(bob_reader)
        assert response["type"] == "registered"
        print("Bob registered!")

        # Alice gets notified that Bob joined
        receive_json(alice_reader)

        # Ask the server for Bob's public key
        send_json(alice, {
            "type": "key_request",
            "username": "bob"
        })

        response = receive_json(alice_reader)

        # Make sure the server gave Alice the correct key
        assert response["type"] == "key_response"
        assert response["username"] == "bob"
        assert response["public_key"] == bob_pem

        print("Alice received Bob's correct public key!")

        
        # Now lets see what happens if Alice asks for someone who isn't online.
        # The server should send an error instead of a public key.
        send_json(alice, {
            "type": "key_request",
            "username": "carol"
        })

        # Check what the server sent back
        response = receive_json(alice_reader)

        if response["type"] == "error":
            print("Unknown user's public key rejected!")
        else:
            raise AssertionError("ERROR: Server returned a key for an unknown user!")


        # Now lets test someone trying to register with a fake public key.
        # The server should reject it because it isn't a real RSA key.
        fake = socket.create_connection(("127.0.0.1", 5000))
        fake_reader = fake.makefile("rb")

        try:
            # Try registering with random text instead of a public key
            send_json(fake, {
                "type": "register",
                "username": "fake",
                "public_key": "not a real RSA key"
            })

            # Check what the server sends back
            response = receive_json(fake_reader)

            # Make sure the server rejected the fake key
            assert response["type"] == "error"
            assert response["message"] == "Invalid public key."

            print("Invalid public key rejected!")

        finally:
            # Close the fake connection when we're done
            fake.shutdown(socket.SHUT_RDWR)
            fake_reader.close()
            fake.close()

        print("Public key test passed!")

    finally:
        # Close both connections when we're done
        for client in (alice, bob):
            try:
                send_json(client, {"type": "quit"})
            except OSError:
                pass
            client.close()

        alice_reader.close()
        bob_reader.close()


# Run the test
if __name__ == "__main__":
    test_public_keys()
