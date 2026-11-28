
# test_keys.py
# CSC 154 - Commit 4 - Test our RSA keys

from getpass import getpass
from crypto_utils import generate_key_pair, save_keys, load_keys


# This function tests if we can save and load our RSA keys.
# We also want to make sure the wrong password doesn't work.
def test_keys():
    username = "alice"

    # Ask for a password so we don't put it directly in our code.
    password = getpass("Enter a password for Alice: ")

    if not password:
        print("Password cannot be empty.")
        return

    # First make a new pair of RSA keys.
    private_key, public_key = generate_key_pair()

    # Save both keys to their files.
    save_keys(username, password, private_key, public_key)

    # Try loading the keys back with the correct password.
    loaded_private, loaded_public = load_keys(username, password)

    # Check that the keys we loaded are the same ones we saved.
    if (private_key.private_numbers() == loaded_private.private_numbers()
            and public_key.public_numbers() == loaded_public.public_numbers()):
        print("Keys loaded correctly!")
    else:
        print("ERROR: Keys don't match!")

    # Now try loading the private key with the wrong password.
    try:
        load_keys(username, password + "_wrong")
        print("ERROR: Wrong password was accepted!")

    except ValueError:
        print("Wrong password rejected!")


# Run the test when we start this file.
if __name__ == "__main__":
    test_keys()
