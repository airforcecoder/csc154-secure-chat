# CSC 154 - Secure Chat

For this project we're using my CSC 138 chat server and client as a base. The old one just sent regular messages, so now we're changing it to use JSON and encryption.

The plan is for Alice, Bob and Carol to connect to one server. The server sends messages to the right user, but it shouldn't be able to read them or change them without the client noticing.

## Who's doing what

I'm doing the first half (steps 0-7) and Tony is doing the second half (8-12). We'll both test it at the end and put the submission together.

We are doing one step per commit so it's easier to tell what changed.

## Steps

### Ian
- [x] Step 0 - Added my old CSC 138 client.py and server.py
- [x] Step 1 - Added protocol.py for sending/receiving JSON. 6 tests passed.
- [x] Step 2 - Changed server.py to register users, show LIST and handle QUIT with JSON. Tested with Alice and Bob.
- [x] Step 3 - Changed client.py to use JSON. Tested Alice and Bob with LIST, HELP, QUIT and join/leave messages.
- [x] Step 4 - Added RSA key generation and saved the private key with a password. Tested saving, loading and wrong passwords.
- [ ] Step 5 - Add AES encryption, RSA key wrapping and digital signatures
- [ ] Step 6 - Test encryption and see what happens when a message is changed
- [ ] Step 7 - Have the server keep public keys so clients can request them

### Tony
- [ ] Step 8 - Have the client load keys and check other users' public keys
- [ ] Step 9 - Server forwards encrypted messages and logs ciphertext only
- [ ] Step 10 - Encrypt and sign messages before sending them
- [ ] Step 11 - Verify, decrypt and block repeated messages
- [ ] Step 12 - Add the server attack tests (change ciphertext/header, send to wrong user, replay)

### Both
- [ ] Step 13 - Test with Alice, Bob and Carol, including the attack tests
- [ ] Step 14 - Finish README, ZIP, video, report and GitHub submission

## How we're securing the messages

Each user will have their own RSA key pair (at least 2048 bits). We keep private keys password-protected and never send them to the server.

For each message we make a new AES-256-GCM key and a new 12-byte nonce. We encrypt the AES key using the receiver's RSA public key with OAEP. We also use SHA-256 and RSA signatures to protect the sender, receiver, message number, timestamp, encrypted key, nonce and ciphertext.

The receiver checks the signature before decrypting and rejects old message numbers. We also need to check public keys so the server can't quietly swap them.

## How to run it

Use Python 3.10+.

Install the library when we get to encryption:

```powershell
python -m pip install -r requirements.txt
```

Test Step 1:

```powershell
python test_protocol.py -v
```

Run the server:

```powershell
python server.py 5000
```

We tested Step 2 with `python test_server.py` and Step 3 using the actual client in two terminals. Alice and Bob could register, use LIST and HELP, and see when someone joined or left. For Step 4, `python test_keys.py` saved Alice's RSA keys, loaded them back and rejected a wrong password. Chat messages aren't added yet.

## GitHub

We're making a branch for each step, testing it, then merging it to main.

```powershell
git switch main
git pull origin main
git switch -c feature/step-N
```

After testing, add the files for that step, commit and push the branch, then make a pull request.

Steps 0-4 are merged. Step 4 is [PR #4](https://github.com/airforcecoder/csc154-secure-chat/pull/4). Next is Step 5 (AES encryption, RSA key wrapping and signatures).

## Report / video

The professor wants a 1-2 page PDF report and a 2-minute video.

I'm writing the introduction, how the client/server works, and the encryption part in Word. Tony will write about receiving/verification, the attack tests, results and limitations. We'll put it together and save it as a PDF once everything is tested.

The demo needs to show the server, three clients, a message that decrypts correctly, the encrypted server log and at least one rejected attack.

## Notes

- Don't upload passwords or private keys to GitHub or the final ZIP.
- The server can still see who talks to who, even when messages are encrypted.
- This is for the class project, not a finished secure messaging app.
