# CSC 154 — Secure Chat Application

**Course:** CSC 154 — Computer System Attacks and Countermeasures (Fall 2026)  
**Project:** Secure Chat Application  
**Starting point:** My CSC 138 Python chat client/server project

> **Project status: Step 1 complete — JSON protocol and six local tests passed.**
> Step 1 is merged into `main` ([PR #1](https://github.com/airforcecoder/csc154-secure-chat/pull/1), source commit `9ddef60`). Next: **Commit 2 — JSON server** (Ian).
>
> `client.py` and `server.py` currently send and log **plaintext**. They are a
> networking foundation, **not a secure chat application yet**. Do not use them
> for private or sensitive messages until the security steps below are complete.

## Goal

Build a Python TCP chat application where Alice, Bob, and Carol communicate
through a relay server. The clients will encrypt, sign, verify, and decrypt
messages. The server should route encrypted messages without knowing their
plaintext or ever having an RSA private key or usable AES key.

## Team split — first half Ian, second half Tony

We are building this in order and making **one tested commit for each numbered task**. Ian completes **Commits 0–7**, then Tony takes over **Commits 8–12**. **Commits 13–14 are shared final testing and submission**, with Tony leading the final integration/demo and Ian contributing the first draft of the written report.

This replaces the previous split by client/server files. Both of us may need to edit `client.py` and `server.py`, but **at different stages**. This avoids one person waiting for unfinished dependencies. Don't begin integrating a later step until the required earlier code is merged into `main`.

| Commit | Owner | What to finish | Depends on |
|---|---|---|---|
| **0 ✅** | **Ian** | Preserve original CSC 138 client/server and starter files | Done: `89b1fed` |
| **1 ✅** | **Ian** | `protocol.py` JSON framing and six protocol tests | Done: `9ddef60`, [PR #1](https://github.com/airforcecoder/csc154-secure-chat/pull/1) |
| **2** | **Ian** | Update `server.py` for JSON registration and online user list | 1 |
| **3** | **Ian** | Update `client.py` for JSON registration, LIST, QUIT, receiving thread | 2 |
| **4** | **Ian** | `crypto_utils.py`: RSA key pairs and password-protected PEM storage | 0 |
| **5** | **Ian** | `crypto_utils.py`: AES-256-GCM, RSA-OAEP, RSA-PSS/SHA-256; sign required headers; verify before decrypt | 4, shared protocol |
| **6** | **Ian** | Crypto unit tests: valid messages, tampering, incorrect keys/signatures | 5 |
| **7** | **Ian** | Server public-key directory and key request/response handling | 2, 4 |
| **8** | **Tony** | Client key generation/loading, recipient key lookup and independent fingerprint verification | 3, 4, 7 |
| **9** | **Tony** | Server forwards encrypted packets unchanged; ciphertext-only logging | 7 |
| **10** | **Tony** | Client encrypts/signs outgoing messages; fresh AES key/nonce, timestamp, message number | 5, 8, 9 |
| **11** | **Tony** | Client checks recipient, replay number and signature before decrypting/displaying | 6, 10 |
| **12** | **Tony** | Malicious-server mode: alter ciphertext/header, misroute, and replay messages | 9, 11 |
| **13** | **Both; Tony leads** | Test Alice, Bob, Carol, logs, successful messages and all rejected attacks | 11, 12 |
| **14** | **Both; Tony assembles final submission** | ZIP, 2-minute demo, 1–2 page report (prepared in Word, exported to PDF), final GitHub link | 13 |

### Ian's checklist — first half

- [x] Commit 0 — CSC 138 starter
- [x] Commit 1 — JSON protocol and six passing tests, merged
- [ ] Commit 2 — JSON server
- [ ] Commit 3 — JSON client
- [ ] Commit 4 — RSA key generation and secure storage
- [ ] Commit 5 — AES encryption, key wrapping, signatures and verification
- [ ] Commit 6 — cryptography tests
- [ ] Commit 7 — public-key directory
- [ ] Write Ian's sections of the report in Word (draft while coding; update details to match implementation)

### Tony's checklist — second half

- [ ] Commit 8 — client key management and trust checking
- [ ] Commit 9 — encrypted relay and server logs
- [ ] Commit 10 — encrypted sending
- [ ] Commit 11 — verified receiving and replay rejection
- [ ] Commit 12 — malicious-server demonstrations
- [ ] Lead Commit 13 — three-client integration and security tests (both participate)
- [ ] Lead Commit 14 — demonstration video, final ZIP/PDF and submission (both participate)

### Written report division — start in Word now

The instructor requires a **1–2 page PDF report** covering design, encryption/decryption, testing results, challenges, and limitations. Draft it in Word first and **export the completed report to PDF** for submission. Do not claim tests passed until they have actually been run.

| Report part | Owner | What to document |
|---|---|---|
| Introduction and system design | **Ian** | CSC 138 starting point, TCP client/server, JSON framing, server as directory/relay, roles of Alice/Bob/Carol |
| Cryptography design and encryption process | **Ian** | RSA-2048+ keys/password protection; AES-256-GCM with new key/nonce per message; RSA-OAEP wrapped AES key; SHA-256/RSA-PSS signatures covering header + encrypted fields |
| Receiving, verification, and replay protection | **Tony** | Public-key validation/pinning, signature-first verification, decrypting only on success, message-number checks |
| Tests, attack results, challenges, and limitations | **Tony** | Three-client tests, ciphertext-only logs, tamper/misroute/replay rejection, issues encountered, threat-model limitations; use actual results |
| Final editing and submission | **Both** | Keep within 1–2 pages, confirm code matches explanations, export PDF and include with other deliverables |

**Ian can write now:** the introduction, architecture, what changed from CSC 138, and the JSON protocol test results (6 passed). Add cryptography details after Commits 4–6 are working. **Tony completes his report sections after Commits 8–13** so the report reflects actual end-to-end behavior and test results.

### Handoff between halves

1. Ian completes and merges **Commits 2–7**, one tested task at a time, into `main`.
2. Ian tells Tony when Commit 7 is merged and shares exact setup commands, working commands, test results, JSON field names, and crypto helper interfaces.
3. Tony pulls the updated `main` branch, creates a feature branch for Commit 8, and completes **8–12** in order with tests and pull requests.
4. Both run the final integration/security checks; Tony leads recording and packaging while each person finishes their report sections.
5. Preserve clear Git commit authorship and PR history for both contributors. Report who actually implemented and tested each part.

**Status as of November 25, 2026:** Only Commits **0 and 1** are confirmed merged into `main`. Later rows are planned assignments, not completed work.

### Shared protocol / security agreement

Use newline-delimited JSON over TCP, one JSON object per line, with an explicit maximum message size. Agree on names such as `register`, `users_request`, `users_response`, `key_request`, `key_response`, `secure_message`, `error`, and `quit`. Sign `sender | recipient | message_number | timestamp | encrypted_key | nonce | ciphertext` in the professor's required order. The server must authenticate the sending socket's registered username; clients must independently validate/pin peer public keys, as server-provided keys alone can be substituted.

### Git collaboration workflow

1. Ian adds Tony (GitHub username `ttan815`) via **Repository → Settings → Collaborators → Add people** if he has not already been invited. Tony accepts and clones the repo.
2. For each task: `git switch main` and `git pull origin main`.
3. Create a task branch, for example `git switch -c feature/step-2-json-server`.
4. Implement and test the task, then `git add .` and `git commit -m "Step 2: add JSON server commands"`.
5. Push with `git push -u origin feature/step-2-json-server`, open a pull request to `main`, review, and merge.
6. Pull `main` again before the next milestone. Coordinate shared files and never push unrelated, incomplete changes just to preserve numerical order.

### Project files (current)

```text
csc154-secure-chat/
├── client.py          # Original CSC 138 client (unchanged)
├── server.py          # Original CSC 138 server (unchanged)
├── protocol.py        # JSON send/receive helpers (Step 1)
├── test_protocol.py   # Six protocol tests (Step 1)
├── README.md          # Project setup, plan, and checklist
├── requirements.txt   # Dependency for the upcoming crypto module
└── .gitignore         # Keep keys, passwords, and generated files out of Git
```

**To be added in later steps:** `crypto_utils.py`, cryptography/integration tests,
and any other modules needed for secure messages.

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

## Step 1 complete — JSON protocol

**Already merged into `main`:** `protocol.py` and `test_protocol.py`.

- [x] Implement newline-delimited JSON packets with a required `type` field.
- [x] Add `send_json(socket, message)` and `receive_json(reader)` helpers.
- [x] Add a 64 KB maximum packet size and invalid/incomplete JSON checks.
- [x] Test normal messages, multiple packets, split packets, invalid JSON,
  missing `type`, and disconnections.
- [x] Run `python test_protocol.py -v` on Windows: **6 tests passed**.
- [x] Merge the Step 1 branch ([PR #1](https://github.com/airforcecoder/csc154-secure-chat/pull/1)).

**Note:** `client.py` and `server.py` still use their old plaintext protocol.
The new helpers are deliberately separate until Commits 2 and 3 integrate
them. The unit tests do **not** prove that the whole chat is secure yet.

### Test Step 1 yourself

```powershell
python test_protocol.py -v
```

Expected: six tests with `ok`, ending in `Ran 6 tests` and `OK`.

### Next task — Commit 2 (Ian)

Update `server.py` to use `send_json()` and `receive_json()`, add JSON
registration and an online-user list, and verify the server can handle multiple
registered clients. Keep encryption for later commits. Ian should
create a separate feature branch and merge it by pull request.

## Installing the cryptography dependency (needed for Commit 4 onward)

```powershell
python -m pip install -r requirements.txt
```

The baseline does not use `cryptography` yet; installing it prepares for the next steps.

## GitHub repository and working locally

Repository: https://github.com/airforcecoder/csc154-secure-chat

- **Commit 0:** `89b1fed` — original CSC 138 starting point.
- **Commit 1:** `9ddef60` — framed JSON protocol and six tests, merged via PR #1.
- The `main` branch contains all merged tasks. Develop future tasks on separate branches.

To sync local `main` **after saving or stashing any uncommitted changes**:

```powershell
git switch main
git pull origin main
python test_protocol.py -v
```

To begin a future assigned task:

```powershell
git switch main
git pull origin main
git switch -c feature/step-N-short-name
```

After the code passes its tests, commit and push that branch, then open a pull
request into `main`. Do not put private keys, passwords, or generated chat
logs in the repository.

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
