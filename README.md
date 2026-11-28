# CSC 154 - Secure Chat

This started as my CSC 138 chat project. We're keeping the TCP client/server setup but changing it so messages are encrypted and the server can't read them.

Alice, Bob and Carol will connect through one server. The server will keep track of who's online and send encrypted messages to the right person.

## Progress

We're doing this one step at a time so it's easier to test and see what changed.

### Ian (Steps 0-7)
- [x] 0 - Added the old CSC 138 client and server
- [x] 1 - Made `protocol.py` to send and receive JSON. 6 tests passed
- [x] 2 - Changed the server to handle registration, LIST and QUIT
- [x] 3 - Changed the client to use JSON. Tested with Alice and Bob
- [x] 4 - RSA key generation, saving/loading keys with a password
- [x] 5 - AES encryption, RSA-OAEP and signatures. Local tests passed
- [ ] 6 - More tests for bad messages and incorrect keys
- [ ] 7 - Server keeps public keys and lets clients request them

### Tony (Steps 8-12)
- [ ] 8 - Client loads its keys and checks other users' public keys
- [ ] 9 - Server forwards encrypted messages and logs ciphertext
- [ ] 10 - Client encrypts and signs messages before sending
- [ ] 11 - Client verifies and decrypts messages, rejects replays
- [ ] 12 - Test a malicious server changing, misrouting or replaying messages

### Both
- [ ] 13 - Test everything with Alice, Bob and Carol
- [ ] 14 - ZIP, video, report and submission

## Running it

Install Python and the required library:

```powershell
python -m pip install -r requirements.txt
```

Start the server:

```powershell
python server.py 5000
```

In another terminal, start a client:

```powershell
python client.py 127.0.0.1 5000
```

Right now the client can register, LIST, HELP and QUIT. Sending encrypted chat messages through the server isn't connected yet.

## Tests

```powershell
python test_protocol.py -v
python test_encryption.py
```

`test_encryption.py` checks a normal encrypted message, changed ciphertext, wrong keys/signatures and a changed message number. They passed locally.

`test_keys.py` was used to test saving and loading password-protected RSA keys. It creates Alice's key files, so running it again with the same username won't overwrite them.

## How the encryption works

Each user gets RSA keys (2048 bits). Their private key is saved with a password. Every message gets a new AES-256-GCM key and 12-byte nonce. The AES key is encrypted with the recipient's RSA public key. We sign the sender, recipient, message number, timestamp and encrypted fields using RSA-PSS and SHA-256.

The receiver needs to verify the signature before decrypting. We still have to connect this to the client, check public keys and block repeated messages.

## GitHub / submission

We make a branch for each step, test it, and merge it into `main`. Steps 0-5 are merged. Next is Step 6.

For the report I'm covering the introduction, client/server setup and encryption. Tony is covering receiving, attack tests, results and limitations. We'll put it together as a 1-2 page PDF.

We also need a 2-minute demo, a ZIP of the project and the GitHub link.

Don't upload private keys or passwords. The `keys/` folder is ignored by Git.
