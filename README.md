# CSC 154 — Secure Chat Application

**Course:** CSC 154 — Computer System Attacks and Countermeasures (Fall 2026)  
**Project:** Secure Chat Application  
**Starting point:** My CSC 138 Python chat client/server project

> **Project status: Step 1 complete — JSON protocol and six local tests passed.**
> Step 1 is merged into `main` ([PR #1](https://github.com/airforcecoder/csc154-secure-chat/pull/1), source commit `9ddef60`). Next: **Commit 2 — JSON server** (teammate).
>
> `client.py` and `server.py` currently send and log **plaintext**. They are a
> networking foundation, **not a secure chat application yet**. Do not use them
> for private or sensitive messages until the security steps below are complete.

## Goal

Build a Python TCP chat application where Alice, Bob, and Carol communicate
through a relay server. The clients will encrypt, sign, verify, and decrypt
messages. The server should route encrypted messages without knowing their
plaintext or ever having an RSA private key or usable AES key.

## Team split — sequential milestones, separate commits

**Development rule:** Every numbered milestone is its own commit. The numbers give us an *integration order*, but some tasks may be developed in parallel on separate branches. **Don't split the tasks into 1–7 for one person and 8–14 for the other** — later tasks depend on earlier work.

**Who edits what:** Ian primarily owns `client.py` and `protocol.py`; teammate primarily owns `server.py` and `crypto_utils.py`. Ian adds the crypto tests in `tests/` after the teammate completes the crypto interface. Both handle final testing and documentation.

| Commit | Assigned | What to finish | Requires |
|---|---|---|---|
| **0 ✅** | Ian | Save original CSC 138 client/server to GitHub | Done: `89b1fed` |
| **1 ✅** | **Ian** | `protocol.py`: newline-delimited JSON send/receive; six passing protocol tests | Done: `9ddef60` ([PR #1](https://github.com/airforcecoder/csc154-secure-chat/pull/1)) |
| **2** | **Teammate** | `server.py`: JSON registration and `LIST` for multiple clients | 1 |
| **3** | **Ian** | `client.py`: JSON registration, `LIST`, `QUIT`, receiving thread | 1, 2 |
| **4** | **Teammate** | `crypto_utils.py`: RSA key generation, password-protected PEM save/load | 0 (can start alongside 1) |
| **5** | **Teammate** | `crypto_utils.py`: AES-256-GCM, RSA-OAEP, RSA-PSS/SHA-256 with signed headers; verify before decrypt | 4; agree on packet schema from 1 |
| **6** | **Ian** | `tests/test_crypto.py`: success, bad signatures, altered fields, wrong keys | 5 |
| **7** | **Teammate** | `server.py`: username/public-key directory and key lookups | 2, 4 |
| **8** | **Ian** | `client.py`: generate/load user keys, request and independently verify/pin public keys | 3, 4, 7 |
| **9** | **Teammate** | `server.py`: route encrypted payload unchanged; ciphertext-only logs | 7 |
| **10** | **Ian** | `client.py`: `MESG` encrypts/signs outgoing messages with fresh key/nonce and message number | 5, 8, 9 |
| **11** | **Ian** | `client.py`: verify before decrypt/display; reject replayed message numbers | 6, 10 |
| **12** | **Teammate** | Server `--malicious` tests: ciphertext tampering, altered headers, misrouting, replay | 9, 11 |
| **13** | **Both** | Alice/Bob/Carol integration tests and fixes; prove server sees no plaintext | 11, 12 |
| **14** | **Both** | Final README, requirements, source ZIP, two-minute demo, 1–2 page PDF report, GitHub link | 13 |

### Personal checklists

**Ian — client, protocol, and crypto tests**

- [x] Commit 0 — original CSC 138 starter
- [x] Commit 1 — JSON protocol and six tests (merged into `main`)
- [ ] Commit 3 — JSON client
- [ ] Commit 6 — crypto tests
- [ ] Commit 8 — key management in client
- [ ] Commit 10 — encrypted sending
- [ ] Commit 11 — verified receiving + replay prevention
- [ ] Commit 13 — integration testing (together)
- [ ] Commit 14 — report/docs/demo (together)

**Teammate — server and cryptography**

- [ ] Commit 2 — JSON server
- [ ] Commit 4 — RSA key creation/storage
- [ ] Commit 5 — crypto functions
- [ ] Commit 7 — public-key directory
- [ ] Commit 9 — ciphertext relay and logs
- [ ] Commit 12 — malicious-server attack demonstrations
- [ ] Commit 13 — integration testing (together)
- [ ] Commit 14 — report/docs/demo (together)

### Best order to work together

1. **Step 1 is merged:** Ian finished **1** (protocol). Teammate can now work on **2** (JSON server) and develop **4** (RSA key generation) in parallel. Agree on the JSON field names and protocol before integrating code.
2. **Connect the baseline:** Teammate works on **2**, then Ian on **3**. In parallel, teammate can complete **5**.
3. **Build security:** Ian tests the crypto module in **6**; teammate implements the key directory in **7**. Ian then integrates keys in **8**.
4. **Finish secure chat:** Teammate completes relay **9**; Ian completes send/receive **10–11**; teammate adds attack tests **12**.
5. **Finish together:** Run **13**, then complete **14**.

Only **Commits 0 and 1** are complete. All other numbered commits are planned future work, not implemented code. Create each after its code is written and tested.

### Shared protocol / security agreement

Use newline-delimited JSON over TCP, one JSON object per line, with an explicit maximum message size. Agree on names such as `register`, `users_request`, `users_response`, `key_request`, `key_response`, `secure_message`, `error`, and `quit`. Sign `sender | recipient | message_number | timestamp | encrypted_key | nonce | ciphertext` in the professor's required order. The server must authenticate the sending socket's registered username; clients must independently validate/pin peer public keys, as server-provided keys alone can be substituted.

### Git collaboration workflow

1. Ian invites the teammate via **Repository → Settings → Collaborators → Add people**. The teammate accepts and clones the repo.
2. For each task: `git switch main` and `git pull origin main`.
3. Create a task branch, for example `git switch -c feature/step-4-rsa-keys`.
4. Implement and test the task, then `git add .` and `git commit -m "Step 4: add password-protected RSA keys"`.
5. Push with `git push -u origin feature/step-4-rsa-keys`, open a pull request to `main`, review, and merge.
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

### Next task — Commit 2 (teammate)

Update `server.py` to use `send_json()` and `receive_json()`, add JSON
registration and an online-user list, and verify the server can handle multiple
registered clients. Keep encryption for later commits. The teammate should
create a separate feature branch and merge it by pull request.

## Installing the cryptography dependency (starting at Step 2)

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
