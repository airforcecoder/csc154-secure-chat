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
import json
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
# Both the sender and receiver need to use the same order or the signature won't match.
def make_signed_data(sender, recipient, message_number, timestamp, encrypted_key, nonce, ciphertext):
    # Turn the encrypted bytes into text so JSON can handle them.
    # Keep everything in the order our project requires.
    data = [
        sender,
        recipient,
        message_number,
        timestamp,
        base64.b64encode(encrypted_key).decode("ascii"),
        base64.b64encode(nonce).decode("ascii"),
        base64.b64encode(ciphertext).decode("ascii")
    ]

    # Turn the data into JSON and then bytes so we can sign it.
    signed_data = json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    # Give the data back so it can be signed or verified.
    return signed_data
