
# test_encryption.py
# Ian Wright - Tony Tan
# CSC 154 - Commit 5 - Testing encryption

from datetime import datetime, timezone

from crypto_utils import (
    generate_key_pair,
    encrypt_message,
    decrypt_message,
    encrypt_aes_key,
    decrypt_aes_key,
    make_signed_data,
    sign_message,
    verify_signature
)


# This function tests sending an encrypted message from Alice to Bob.
# We want to make sure Bob can verify it and get the original message back.
def test_encryption():
    # Make RSA keys for Alice and Bob
    alice_private, alice_public = generate_key_pair()
    bob_private, bob_public = generate_key_pair()

    # This is the message Alice wants to send Bob
    message = "Hello Bob!"
    sender = "alice"
    recipient = "bob"
    message_number = 1
    timestamp = datetime.now(timezone.utc).isoformat()

    # First encrypt the message using AES
    aes_key, nonce, ciphertext = encrypt_message(message)

    # Encrypt the AES key using Bob's public key
    encrypted_key = encrypt_aes_key(aes_key, bob_public)

    # Put all the message information together for signing
    data = make_signed_data(
        sender, recipient, message_number, timestamp,
        encrypted_key, nonce, ciphertext
    )

    # Alice signs the data using her private key
    signature = sign_message(data, alice_private)

    print("Original message:", message)
    print("Encrypted message:", ciphertext.hex())

    # Bob checks the signature using Alice's public key
    valid = verify_signature(data, signature, alice_public)

    if valid:
        print("Signature verified!")

        # Bob uses his private key to unlock the AES key
        bob_aes_key = decrypt_aes_key(encrypted_key, bob_private)

        # Now Bob can decrypt the actual message
        decrypted_message = decrypt_message(bob_aes_key, nonce, ciphertext)

        print("Decrypted message:", decrypted_message)

        # Make sure Bob got the same message Alice sent
        assert decrypted_message == message
        print("Encryption test passed!")


        # Now lets test what happens if someone changes the encrypted message.
        # Bob should reject it because the signature won't match.
        changed_ciphertext = bytearray(ciphertext)

        # Change one byte of the encrypted message
        changed_ciphertext[0] ^= 1

        # Put the message information together again with the changed ciphertext
        changed_data = make_signed_data(
            sender, recipient, message_number, timestamp,
            encrypted_key, nonce, bytes(changed_ciphertext)
        )

        # Check the original signature against the changed message
        valid = verify_signature(changed_data, signature, alice_public)

        if not valid:
            print("Changed message rejected!")
        else:
            raise AssertionError("ERROR: Changed message was accepted!")

        
        # Now lets see what happens if someone uses the wrong RSA private key.
        # The AES key was encrypted for Bob, so Alice's private key shouldn't work.
        try:
            # Try unlocking Bob's AES key using Alice's private key
            wrong_key = decrypt_aes_key(encrypted_key, alice_private)

            # If this works, something went wrong
            raise AssertionError("ERROR: Wrong RSA key was accepted!")

        except ValueError:
            # The wrong private key couldn't decrypt it
            print("Wrong RSA key rejected!")

        
        # Now lets test what happens if the message has the wrong signature.
        # Bob shouldn't accept it if someone else signed the message.
        wrong_signature = sign_message(data, bob_private)

        # The message says it's from Alice, so check it using Alice's public key
        valid = verify_signature(data, wrong_signature, alice_public)

        if not valid:
            print("Wrong signature rejected!")
        else:
            raise AssertionError("ERROR: Wrong signature was accepted!")




    else:
        # This signature should work, so something is wrong if it doesn't
        raise AssertionError("ERROR: Original signature failed!")


# Run our test
if __name__ == "__main__":
    test_encryption()
