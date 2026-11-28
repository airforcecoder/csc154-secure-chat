# CSC 154 - Secure Chat

We're using my old CSC 138 chat project for this. The original client and server sent regular text, so we're changing it to send encrypted messages instead. Alice, Bob and Carol will all connect through the same server.

## What we've done

We split the work into steps so we can test each part before moving on.

### Ian
- [x] 0 - Added the CSC 138 client and server
- [x] 1 - Added `protocol.py` for JSON messages. 6 tests passed
- [x] 2 - Updated the server for registration, LIST and QUIT
- [x] 3 - Updated the client to use JSON. Tested with Alice and Bob
- [x] 4 - Made RSA keys and saved the private keys with a password
- [x] 5 - Added AES encryption, RSA-OAEP and signatures
- [x] 6 - Tested changed messages, recipient, message number, AES key and signatures
- [ ] 7 - Store public keys on the server so clients can request them

### Tony
- [ ] 8 - Load client keys and check other users' public keys
- [ ] 9 - Have the server forward encrypted messages and log ciphertext
- [ ] 10 - Send encrypted and signed messages from the client
- [ ] 11 - Verify and decrypt incoming messages, and reject repeats
- [ ] 12 - Add tests where the server changes or replays messages

### Both
- [ ] 13 - Test everything with Alice, Bob and Carol
- [ ] 14 - Finish the ZIP, video and report

## Running the project

Install the requirements:

```powershell
python -m pip install -r requirements.txt
```

Start the server:

```powershell
python server.py 5000
```

Start a client in another terminal:

```powershell
python client.py 127.0.0.1 5000
```

The client can register, LIST, HELP and QUIT right now. We haven't connected the encrypted chat messages to the server yet.

## Tests

```powershell
python test_protocol.py -v
python test_encryption.py
```

The encryption tests passed locally. We checked that Bob could read a message from Alice, and that changed message data, wrong keys and bad signatures were rejected. Step 6 added more tests for changed recipients, message numbers and encrypted keys.

We also tested `test_keys.py` for saving and loading the RSA keys. It makes key files for Alice, so it won't overwrite them if they're already there.

## Encryption

Each user has an RSA key pair. The private key is password-protected. We use a new AES-256-GCM key and nonce for every message, encrypt the AES key with the receiver's public key, and sign the message information with RSA-PSS and SHA-256.

The receiver checks the signature before decrypting. We still need to finish the public-key lookup, replay checks and actual client-to-client messaging.

## GitHub and submission

We're making a branch for each step and merging it after testing. Steps 0-6 are merged. Next is Step 7.

I'm writing the introduction, how the client/server works and the encryption part of the report. Tony is doing the receiving side, attack tests, results and limitations.

We need to turn in the code ZIP, a 2-minute video, a 1-2 page PDF report and the GitHub link. No private keys or passwords should be included. The `keys/` folder is in `.gitignore`.
