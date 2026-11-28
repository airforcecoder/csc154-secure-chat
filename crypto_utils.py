# Ian Wright - Tony Tan
# crypto_utils.py
# CSC 154 - RSA keys and encryption

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from pathlib import Path
from cryptography.hazmat.primitives import serialization
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature
import base64

# This function makes a new RSA private and public key for the user.
# We're using 2048 bits because that's what the project requires.
def generate_key_pair():
    # Make a new RSA private key
    # Using 2048 bits like the project requires
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Get the public key from the private key
    public_key = private_key.public_key()

    # Return both keys so we can use them later
    return private_key, public_key




# This function saves the user's keys in their own files.
# The private key is protected with a password so nobody can just open it.
def save_keys(username, password, private_key, public_key):
    # Make sure they entered a username and password
    if not username or not username.replace("_", "").isalnum():
        raise ValueError("Invalid username.")

    if not password:
        raise ValueError("Password cannot be empty.")

    # Make a folder to keep the keys in
    key_folder = Path("keys")
    key_folder.mkdir(exist_ok=True)

    # Each user gets their own private and public key files
    private_path = key_folder / (username + "_private.pem")
    public_path = key_folder / (username + "_public.pem")

    # Don't replace someone's keys if they already exist
    if private_path.exists() or public_path.exists():
        raise FileExistsError("Keys already exist for this user.")

    # Save the private key with password protection
    private_data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            password.encode()
        )
    )

    # Public keys don't need password protection
    public_data = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write both keys to their own files
    with open(private_path, "xb") as file:
        file.write(private_data)

    with open(public_path, "xb") as file:
        file.write(public_data)

    print(username, "keys saved!")





# This function loads the user's private and public keys from their files.
# The private key needs the password we used when saving it.
def load_keys(username, password):
    # Make sure the username and password are valid.
    if not username or not username.replace("_", "").isalnum():
        raise ValueError("Invalid username.")

    if not password:
        raise ValueError("Password cannot be empty.")

    # Find where we saved this user's keys.
    key_folder = Path("keys")
    private_path = key_folder / (username + "_private.pem")
    public_path = key_folder / (username + "_public.pem")

    # Open the private key file and read it.
    with open(private_path, "rb") as file:
        private_data = file.read()

    # Open the public key file and read it.
    with open(public_path, "rb") as file:
        public_data = file.read()

    # Use the password to unlock the private key.
    private_key = serialization.load_pem_private_key(
        private_data,
        password=password.encode()
    )

    # The public key doesn't need a password.
    public_key = serialization.load_pem_public_key(public_data)

    # Give both keys back so we can use them.
    return private_key, public_key




# This function encrypts a message using AES-256-GCM.
# Each message gets a new AES key and nonce so we're not reusing them.
def encrypt_message(message):
    # Make sure we're encrypting a string
    if not isinstance(message, str):
        raise ValueError("Message must be text.")

    # Generate a new 256 bit AES key for this message
    aes_key = AESGCM.generate_key(bit_length=256)

    # Generate a random 12 byte nonce for this message
    nonce = os.urandom(12)

    # Turn our message into bytes so AES can encrypt it
    message_bytes = message.encode("utf-8")

    # Encrypt the message using our AES key and nonce
    aes = AESGCM(aes_key)
    ciphertext = aes.encrypt(nonce, message_bytes, None)

    # Return everything we need for the next encryption steps
    return aes_key, nonce, ciphertext




# This function decrypts a message using the AES key and nonce.
# If someone changed the encrypted message, it should fail.
def decrypt_message(aes_key, nonce, ciphertext):
    # Use the same AES key that encrypted the message
    aes = AESGCM(aes_key)

    # Decrypt the message using the key and nonce
    message_bytes = aes.decrypt(nonce, ciphertext, None)

    # Turn the bytes back into normal text
    message = message_bytes.decode("utf-8")

    # Give the original message back
    return message




# This function encrypts our AES key using the receiver's RSA public key.
# That way we don't have to send the AES key as regular text.
def encrypt_aes_key(aes_key, public_key):
    # Encrypt the AES key using RSA-OAEP
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Give back the encrypted AES key
    return encrypted_key




# This function decrypts the AES key using the receiver's private key.
# Only the person with the matching RSA private key should be able to unlock it.
def decrypt_aes_key(encrypted_key, private_key):
    # Decrypt the AES key using RSA-OAEP
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Give back the original AES key
    return aes_key




# This function signs our message data using the sender's private key.
# This lets the receiver check who sent it and if anything was changed.
def sign_message(data, private_key):
    # Sign the data using RSA-PSS and SHA-256
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Give back the signature so we can send it with the message
    return signature





# This function checks the signature using the sender's public key.
# If the signature doesn't match, we shouldn't decrypt the message.
def verify_signature(data, signature, public_key):
    try:
        # Check the signature using RSA-PSS and SHA-256
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # The signature matched
        return True

    except InvalidSignature:
        # Something didn't match, so reject it
        return False




# This function puts all the message information together before we sign it.
# We're using | to separate everything like the project instructions say.
def make_signed_data(sender, recipient, message_number, timestamp, encrypted_key, nonce, ciphertext):
    # Turn the encrypted bytes into base64 text
    # Keep the fields in the order the professor wants
    data = [
        sender,
        recipient,
        str(message_number),
        timestamp,
        base64.b64encode(encrypted_key).decode("ascii"),
        base64.b64encode(nonce).decode("ascii"),
        base64.b64encode(ciphertext).decode("ascii")
    ]

    # Don't allow the separator inside the header fields
    if "|" in sender or "|" in recipient or "|" in timestamp:
        raise ValueError("Invalid message header.")

    # Join everything with | and turn it into bytes
    signed_data = "|".join(data).encode("utf-8")

    # Return the data so we can sign or verify it
    return signed_data



# This function encrypts and signs a message before sending it.
# We use AES for the message, RSA for the AES key, and the sender's private key to sign it.
def encrypt_and_sign(message, sender, recipient, message_number, timestamp, sender_private_key, recipient_public_key):
    # First encrypt the message using AES
    aes_key, nonce, ciphertext = encrypt_message(message)

    # Encrypt the AES key using the receiver's public key
    encrypted_key = encrypt_aes_key(aes_key, recipient_public_key)

    # Put all the message information together so we can sign it
    data = make_signed_data(
        sender, recipient, message_number, timestamp,
        encrypted_key, nonce, ciphertext
    )

    # Sign everything using the sender's private key
    signature = sign_message(data, sender_private_key)

    # Make our JSON message so it can be sent to the server
    # Convert the encrypted bytes to base64 since JSON can't use regular bytes
    secure_message = {
        "type": "secure_message",
        "from": sender,
        "to": recipient,
        "message_number": message_number,
        "timestamp": timestamp,
        "encrypted_key": base64.b64encode(encrypted_key).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii")
    }

    # Give the encrypted message back so the client can send it
    return secure_message



# This function checks and decrypts a message someone sent us.
# We check the signature first so we don't decrypt something that was changed.
def decrypt_and_verify(secure_message, recipient_private_key, sender_public_key, username):
    # Make sure this is actually an encrypted message
    if secure_message["type"] != "secure_message":
        raise ValueError("Not a secure message.")

    # Make sure the message was meant for this user
    if secure_message["to"] != username:
        raise ValueError("This message was not meant for you.")

    # Get the message information we need to check the signature
    sender = secure_message["from"]
    recipient = secure_message["to"]
    message_number = secure_message["message_number"]
    timestamp = secure_message["timestamp"]

    # Turn the base64 text back into bytes
    encrypted_key = base64.b64decode(secure_message["encrypted_key"], validate=True)
    nonce = base64.b64decode(secure_message["nonce"], validate=True)
    ciphertext = base64.b64decode(secure_message["ciphertext"], validate=True)
    signature = base64.b64decode(secure_message["signature"], validate=True)

    # Put the message information back together in the same order
    data = make_signed_data(
        sender, recipient, message_number, timestamp,
        encrypted_key, nonce, ciphertext
    )

    # Check the signature using the sender's public key
    if not verify_signature(data, signature, sender_public_key):
        raise ValueError("Signature verification failed.")

    # The signature worked, so now unlock the AES key
    aes_key = decrypt_aes_key(encrypted_key, recipient_private_key)

    # Decrypt the actual message
    message = decrypt_message(aes_key, nonce, ciphertext)

    # Give back the original message
    return message
