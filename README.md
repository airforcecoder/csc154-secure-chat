# CSC 154 — Secure Chat Application

**Course:** CSC 154 — Computer System Attacks and Countermeasures (Fall 2026)  
**Project:** Secure Chat Application  
**Starting point:** My CSC 138 Python chat client/server project

> **Project status: Step 0 — Original CSC 138 code preserved and pushed to GitHub.**
>
> `client.py` and `server.py` currently send and log **plaintext**. They are a
> networking foundation, **not a secure chat application yet**. Do not use them
> for private or sensitive messages until the security steps below are complete.

## Goal

Build a Python TCP chat application where Alice, Bob, and Carol communicate
through a relay server. The clients will encrypt, sign, verify, and decrypt
messages. The server should route encrypted messages without knowing their
plaintext or ever having an RSA private key or usable AES key.

## Two-person development plan — one task per commit

**GitHub team:** Owner (Ian) + Teammate (add the teammate as a repository collaborator).
**Rule:** Each row represents **one working, tested commit**. The listed commit messages are examples, not commits that already exist. Only Step 0 is complete. Each person owns their main files to reduce merge conflicts: Ian owns `client.py` and `protocol.py`; Teammate owns `server.py` and `crypto_utils.py`.

**Shared protocol contract before parallel work:** Agree on newline-delimited JSON over TCP (one JSON object per line), type names (`register`, `users_request`, `users_response`, `key_request`, `key_response`, `secure_message`, `error`, `quit`), required field names, signed-field ordering, and an explicit maximum packet size. `protocol.py` holds shared send/receive helpers. Server-side `from` must match the registered socket; client-side sender/recipient must match the verified signature. Public keys must be pinned/verified independently to resist server key substitution.

| Commit | Owner | Deliverable to implement and test | Suggested commit message |
|---|---|---|---|
| **0 — Done** | Ian | Import original CSC 138 client/server; README and ignores | `Step 0: Original CSC 138 chat application` |
| **1** | Ian | `protocol.py`: JSON framing, helpers, message format; test partial/multiple TCP packets | `Step 1: define framed JSON protocol` |
| **2** | Teammate | `server.py`: JSON registration and online user lists, thread safety | `Step 2: handle JSON registration and users on server` |
| **3** | Ian | `client.py`: use JSON registration, `LIST`, `QUIT`, receiving thread | `Step 3: add JSON client commands` |
| **4** | Teammate | `crypto_utils.py`: RSA-2048+ key creation, password-encrypted PEM save/load | `Step 4: add password-protected RSA keys` |
| **5** | Teammate | `crypto_utils.py`: fresh AES-256-GCM key/nonce per message, RSA-OAEP key wrapping, SHA-256/RSA-PSS signatures covering all required fields, verify before decrypt | `Step 5: implement encrypt sign verify decrypt` |
| **6** | Teammate | `tests/test_crypto.py`: valid message, changed header, changed ciphertext, wrong key, bad signature | `Step 6: test crypto and tamper rejection` |
| **7** | Teammate | `server.py`: username/public-key directory, requests, unknown-user errors, reject forged sender sockets | `Step 7: add server public-key directory` |
| **8** | Ian | `client.py`: prompt for key password, generate/load private key, register public key, cache and independently verify/pin peer fingerprint | `Step 8: manage and verify client keys` |
| **9** | Teammate | `server.py`: relay `secure_message` unchanged, ciphertext-only logging, no plaintext/private keys/AES keys | `Step 9: relay encrypted packets without reading them` |
| **10** | Ian | `client.py`: `MESG` generates fresh AES key and nonce, message number and timestamp; encrypt/sign and send JSON | `Step 10: encrypt and sign outgoing messages` |
| **11** | Ian | `client.py`: verify sender signature and headers, replay number check, then decrypt/display; clean errors | `Step 11: verify decrypt and reject replays` |
| **12** | Teammate | `server.py`: `--malicious` test actions for ciphertext tamper, header tamper, misroute, replay | `Step 12: add malicious relay demonstrations` |
| **13** | Both | Run Alice/Bob/Carol, assert valid delivery, server secrecy and all four rejected attacks; fix integration problems in small follow-up commits | `Step 13: test three-client secure chat` |
| **14** | Ian (report/README) + Teammate (video) | Update execution docs, `requirements.txt`, test results; 1–2 page PDF, 2-minute demo, submission ZIP excluding keys and passwords | `Step 14: finalize documentation and submission` |

### Collaboration workflow

1. Ian invites the teammate on GitHub: **Repository → Settings → Collaborators → Add people**. The teammate accepts and clones the repo.
2. Before starting a task, update `main`: `git switch main`, then `git pull origin main`.
3. Create a branch for the task, e.g. `git switch -c feature/step-4-rsa-keys`.
4. Implement **only that task** and run its tests. Commit: `git add .` then `git commit -m "Step 4: add password-protected RSA keys"`.
5. Push: `git push -u origin feature/step-4-rsa-keys`. Open a GitHub pull request into `main`, review/test, then merge.
6. Pull `main` again before the next task. **Do not both edit `main` or the same files simultaneously.** When a step needs the other person's change, merge the dependency first.
7. For Step 13, agree on tests and merge fixes one at a time; each security test should demonstrate refusal without revealing plaintext.

**Handoff points:** Finish commits 1–3 (JSON) before networking integration; commits 4–6 (crypto) can be developed in parallel. Complete commits 7–9 before secure messaging (10–11), and do commit 12 after receiving-side verification is functional. Run integration tests before recording the video.

### Project files (current)

```text
csc154-secure-chat/
├── client.py          # Original CSC 138 client (unchanged)
├── server.py          # Original CSC 138 server (unchanged)
├── README.md          # Project setup, plan, and checklist
├── requirements.txt   # Dependency for the upcoming crypto module
└── .gitignore         # Keep keys, passwords, and generated files out of Git
```

**To be added in later steps:** `crypto_utils.py`, automated tests, and any
other modules needed for the secure message protocol.

## Step 0 — Run the existing baseline

Use Python 3.10+ and open **three PowerShell terminals** in this folder.
No third-party packages are needed to run the *original* chat code.

**Terminal 1 — server:**

```powershell
python server.py 5000
```

**Terminal 2 — Alice:**

```powershell
python client.py 127.0.0.1 5000
```

When prompted, enter `Alice` (the original client automatically prefixes `JOIN`).

**Terminal 3 — Bob:**

```powershell
python client.py 127.0.0.1 5000
```

Enter `Bob`. You can also start a fourth terminal for `Carol`.

Try these original commands in a client terminal:

```text
LIST
MESG Bob Hello from Alice
HELP
QUIT
```

**Expected for baseline:** Bob sees `Alice: Hello from Alice` and the server
can read/log that same message. **This plaintext behavior must be removed
before final submission.**

## Implementation roadmap — one change at a time

Commit and test each step before moving to the next one. The checkbox list
tracks **implementation**, not merely the existence of instructions.

### Step 0 — Preserve the CSC 138 starting point

- [x] Copy original `client.py` without modifying it.
- [x] Copy original `server.py` without modifying it.
- [x] Add a README with the setup, phased plan, and requirements.
- [x] Add `.gitignore` and `requirements.txt`.
- [ ] Run and confirm the original server and two clients on my computer.
- [x] Push the baseline to a new GitHub repository.

Suggested Git commit: `Step 0: import original CSC 138 chat application`

### Step 1 — Introduce a reliable JSON protocol

- [ ] Replace plaintext command transmission with JSON objects containing a `type` field.
- [ ] Use **length-prefixed** or **newline-delimited** message framing over TCP. A single `recv()` may contain only part of a message, or several messages; do not assume one `recv()` equals one JSON object.
- [ ] Define protocol messages for registration, user list, public-key request/response, secure message, errors, and quit.
- [ ] Keep the threaded server and the client's receiving thread.
- [ ] Confirm three clients can register and list users before adding encryption.

Suggested Git commit: `Step 1: add framed JSON protocol`

### Step 2 — Build and test `crypto_utils.py` locally

- [ ] Move/adapt the instructor's `secure_message.py` demonstration into reusable functions.
- [ ] Generate **RSA 2048-bit or stronger** key pairs for each user.
- [ ] Save keys as PEM; protect each private key using a password; never transmit a private key.
- [ ] For **every message**, generate a new 256-bit AES key and new 12-byte GCM nonce.
- [ ] Encrypt plaintext using **AES-256-GCM**.
- [ ] Encrypt the AES key using the **recipient's RSA public key with OAEP**.
- [ ] Construct a deterministic signed payload with, in this order:
  `sender | recipient | message_number | timestamp | encrypted_key | nonce | ciphertext`.
- [ ] Compute SHA-256 over the complete signed payload; sign the hash with the sender's RSA private key (RSA-PSS / SHA-256).
- [ ] Encode binary fields as base64 for the JSON packet.
- [ ] On receive, **verify the signature first**, then decrypt the AES key, then decrypt the message. Show no plaintext on any failure.
- [ ] Test valid, altered ciphertext, altered header, and wrong-key messages **without networking**.

Suggested Git commit: `Step 2: add RSA and AES-GCM crypto module`

### Step 3 — Change the server into an encrypted relay

- [ ] Register each username together with its RSA **public** key.
- [ ] Maintain a thread-safe directory: username -> connection + public key.
- [ ] Return a requested user's public key, or a clear error if the user is unknown.
- [ ] Send online-user lists.
- [ ] Route based only on needed `type`, `to`, and `from` fields. Forward secure payloads unchanged.
- [ ] Verify the claimed `from` username belongs to the sender's registered socket.
- [ ] Replace the old plaintext history/logging with **ciphertext-only** relay logs.
- [ ] Never store or print usable AES keys, private keys, or plaintext.

Suggested Git commit: `Step 3: turn server into public-key directory and ciphertext relay`

### Step 4 — Update the client for key management

- [ ] Generate or load a password-protected private PEM file and corresponding public key.
- [ ] Register username and public key with the server.
- [ ] Request recipient public keys and cache them.
- [ ] **Authenticate recipient keys**: the server is potentially malicious. Compare an independently verified fingerprint or pin the expected key. A plain server-provided key alone does **not** prevent key substitution. Document the trust model.
- [ ] Make key files local only; do **not** add `.pem` files to GitHub or the ZIP submission.

Suggested Git commit: `Step 4: add client key generation and trusted key lookup`

### Step 5 — Encrypt, sign, verify, and display secure messages

- [ ] Convert `MESG <user> <message>` to the secure send operation.
- [ ] Include signed sender, recipient, message number, timestamp, encrypted key, nonce, ciphertext, and signature.
- [ ] Maintain monotonically increasing outgoing message numbers.
- [ ] Track the **highest accepted message number from each sender** and reject a repeated or lower number.
- [ ] The receiving thread verifies the signature and recipient/header, checks replay protection, decrypts, and **only then** displays plaintext.
- [ ] Display confirmation when signature verification succeeds and clear errors when it fails.
- [ ] Keep `LIST`, `HELP`, `QUIT` as useful commands; implement broadcast only if time remains, encrypting separately for each recipient.

Suggested Git commit: `Step 5: send and receive authenticated encrypted chat messages`

### Step 6 — Add malicious-server demonstrations

Implement an explicit server `--malicious` test mode. These attacks are **tests**, not normal behavior:

- [ ] Flip one ciphertext byte -> receiving client refuses it.
- [ ] Change recipient or message number in the header -> signature verification fails.
- [ ] Deliver a Bob-bound packet to Carol -> Carol rejects it (wrong recipient and/or RSA decryption failure).
- [ ] Replay an earlier valid packet -> receiving client rejects an already accepted message number.
- [ ] Show *why* each test was rejected; do not display unverified plaintext.

Suggested Git commit: `Step 6: add tampering, misrouting, and replay attack demos`

### Step 7 — Test using three clients

- [ ] Start the server and connect `Alice`, `Bob`, and `Carol`.
- [ ] Alice sends Bob a valid encrypted message; Bob sees verified plaintext.
- [ ] Confirm the server log contains ciphertext, not readable chat text or AES keys.
- [ ] Run and record the four malicious-server tests.
- [ ] Test errors (unknown user, disconnected user, invalid signature, wrong key).
- [ ] Make sure opening and closing clients does not break the server.

Suggested Git commit: `Step 7: document and verify integration/security tests`

### Step 8 — Final deliverables

- [ ] Submit **one ZIP** with `client.py`, `server.py`, crypto module, requirements, README, and related source files. **Exclude private keys and passwords.**
- [ ] Record a **two-minute video** showing the server, at least three clients, successful verified encrypted chat, ciphertext in the server log, and at least one rejected attack.
- [ ] Write a **1–2 page PDF report** explaining design, encryption/decryption, results, challenges, and limitations.
- [ ] Provide the **GitHub repository link** with the completed source code.

**Course rubric:** Code and functionality = 70 points; video = 20 points; report and GitHub = 10 points.

## Installing the cryptography dependency (starting at Step 2)

```powershell
python -m pip install -r requirements.txt
```

The baseline does not use `cryptography` yet; installing it prepares for the next steps.

## Original GitHub setup (completed — kept for reference)

1. Sign in to GitHub and visit **https://github.com/new**.
2. Repository name: `csc154-secure-chat`.
3. Choose **Private** while developing, unless your professor requires public access.
4. **Do not** check *Add a README*, *Add .gitignore*, or *Choose a license* — those files are already in this folder.
5. Create the empty repository.
6. Extract the starter ZIP to your computer. In PowerShell, go **inside** the extracted `csc154-secure-chat` folder and run:

```powershell
git init
git add .
git commit -m "Step 0: import original CSC 138 chat application"
git branch -M main
git remote add origin https://github.com/airforcecoder/csc154-secure-chat.git
git push -u origin main
```

If Git prompts you to configure your author identity, configure your own Git name and email first (`git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"` with **your actual values**), and repeat the commit/push. You may also need to authenticate to GitHub using your configured Git credential manager.

For later steps, after updating/testing files, use:

```powershell
git add .
git commit -m "Step N: brief description of the change"
git push
```

**GitHub repository (created and pushed):** https://github.com/airforcecoder/csc154-secure-chat  
**Baseline commit:** `89b1fed`.

## Security notes and limitations to explain in the report

- **Baseline is unencrypted.** Do not mistake working CSC 138 messaging for completion of CSC 154.
- The relay will still learn sender/recipient metadata and timing even though it cannot read content.
- A dishonest directory server could substitute a fake RSA public key. To claim protection against server impersonation, clients must validate trusted keys/fingerprints. Trust-on-first-use alone cannot protect the first contact against a malicious server.
- Replay protection is based on the highest accepted message number per sender; carefully document behavior when clients restart.
- The assignment is a learning-focused simulation, not an audited production secure messenger.

## Instructor materials

- `Secure Chat Application Project.pdf` (CSC 154, Fall 2026)
- `secure_message.py` (provided inside the instructor's `secure_message.zip`, used as a reference for Step 2)
- The original CSC 138 `client.py` and `server.py`

The instructor sample is not copied into this starter folder. We will adapt its cryptographic approach into the new module when implementing Step 2.
