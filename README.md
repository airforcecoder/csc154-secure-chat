# CSC 154 - Secure Chat

Ian Wright and Tony Tan

We're using my CSC 138 chat program as the starting point. For this project we're changing it so users can send encrypted messages through a server instead of just sending regular text.

## Setup

Install the requirements:

```powershell
python -m pip install -r requirements.txt
```

Start the server:

```powershell
python server.py 5000
```

For now, open another terminal and test the public keys:

```powershell
python test_public_keys.py
```

Other tests:

```powershell
python test_protocol.py -v
python test_encryption.py
```

The tests for encryption, signatures, wrong keys and changed messages passed.

## Progress

### Ian
- [x] Steps 0-3: Original chat code, JSON protocol, server and client changes
- [x] Step 4: RSA keys and password-protected key files
- [x] Step 5: AES encryption and signatures
- [x] Step 6: Tests for changed messages and bad signatures
- [x] Step 7: Server stores public keys and responds to key requests

### Tony
- [ ] Step 8: Load keys in the client and check other users' public keys
- [ ] Steps 9-11: Send, receive and verify encrypted messages
- [ ] Step 12: Malicious server tests

### Both
- [ ] Test with Alice, Bob and Carol
- [ ] Finish the video, report and ZIP

## Notes

The encryption works in our local tests, but the actual chat messages aren't connected yet. The current `client.py` also doesn't send a public key when registering, so it won't register with the updated server until Step 8 is finished.

We'll update the client instructions once that part works.

Don't include private keys or passwords in GitHub or the ZIP. The `keys/` folder is ignored by Git.
