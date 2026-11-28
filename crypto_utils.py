# Ian Wright - Tony Tan
# crypto_utils.py
# CSC 154 - Commit 4 - RSA keys

from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
from cryptography.hazmat.primitives import serialization


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

