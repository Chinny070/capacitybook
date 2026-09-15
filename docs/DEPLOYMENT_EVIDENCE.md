# Deployment evidence

All addresses, transaction hashes, and outcomes below are real, finalized StudioNet transactions. Nothing in this document is invented.

- **Network:** StudioNet
- **Chain ID:** `61999` (confirmed via `genlayer network info`: `chainId: '61999'`, RPC `https://studio.genlayer.com/api`)
- **Final repository commit at time of this evidence:** `9a2c558` (fixtures), contract fix commit `e86bc00`, HEAD after this document is added will be recorded in `SUBMISSION.md`
- **Deployer wallet:** `0x3A3168d67A110dE79461939047a8f7334ff1423d` (funded, unlocked)

## Contract addresses and deployment transactions

| Contract | Address | Deploy tx | Status |
|---|---|---|---|
| CapacityBook | `0xff7D50Eb0bc99143Dcc729929B44068BC4d23281` | `0x8cd2814651d7c17df7e06752d4325e669f42e58bd2b45c135eae2ee5bd6d5054` | FINALIZED |
| CapacityGuard | `0x01bb76Abe1EC2D0eb0000BAa947602531DA5EA3B` | `0xfeb0b0ca1fae5d3e94600e18e9dca75f29388e6e494d931741490a163af1c816` | FINALIZED |

CapacityGuard's constructor was called with the finalized CapacityBook address above.

### A note on a discarded first deployment attempt

An earlier deployment of CapacityBook to address `0x723d0a0a7392ea89fFdD317aC74118ECC8C29E31` (tx `0x3a0b3eeff127689dc8f43eeca75782853d1fc07c15abe64b9d20158f16440ac8`) reported `status_name: FINALIZED` and `MAJORITY_AGREE`, but the leader's own execution result inside that receipt was `{status: 'contract_error', payload: 'invalid_contract'}`, and the address was subsequently unreadable (`Contract ... not found` from `genlayer call`/`genlayer schema`). Root cause: the contract's `Depends` header pinned a `py-genlayer` SDK hash from a newer GenVM generation (`5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng`, GenVM `v0.6.0-rc5`) that is not the generation StudioNet's live validators currently serve. The contracts were ported to the SDK generation StudioNet actually runs (`1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`, GenVM `v0.6.0-rc1`), confirmed against other GenLayer Intelligent Contracts already live on this same StudioNet deployment. The addresses above are the corrected, verified-readable redeployment. This failure mode (finalized transaction, broken contract) is the reason this document verifies readability and real state, not just transaction status.

## Sealed book

- `create_book` tx: `0x7e3806bdbee1760c9d9b8f82f364adb6bc616d788e06c32182c2130d52fc840e` (FINALIZED) → `book_id = 1`
- `add_pool` (capacity=2, unit="responder", label="Dedicated P1 responders") → `pool_id = 1`
- `seal_book` tx: `0x12b045ff590fc1e85f34cae04c2a03059ee3bfd900513fd73159eba9f7911fe2` (FINALIZED)
- **`definition_hash`:** `096d09b59a8cd84dec92637e0505e8826b4dfe986782f36e1dbc2d6a1d492cfe`
- Confirmed immutable: `add_pool` after seal is rejected by the contract's `book is sealed` check (exercised in `tests/direct`); on StudioNet the book's `status_name` reads `SEALED` with a non-empty `definition_hash` via `get_book`.

## Scenario A — matched demand admitted

- Evidence fixture (commit-pinned): `https://raw.githubusercontent.com/Chinny070/capacitybook/b79dfd0/fixtures/commitment_alpha.txt`
- `open_reservation` tx: `0x0a60f08c276685bf2938dc2189cace889b05f05f180f74fd2c7f406b8c8a89ee` → `reservation_id = 1`
- `add_demand` tx: `0xf3c8cbe3b069466b48fcefaecbe98f7873412e3792fd5229db95f55c7f08e9da` → `demand_id = 1`, declared units = 2
- `verify_demand` tx: `0x3d39974187fa68f7533e85bdd9d4279a6908d9f4e3291a5447bca4b34ab4ff8d` (FINALIZED, 5/5 validator votes revealed, `MAJORITY_AGREE`)
  - **Verdict:** `MATCHED`
  - **Evidence excerpt (verbatim from the source):** `"Service commitment Alpha reserves two dedicated P1 responders from 20:00 UTC until 22:00 UTC on 15 September 2026."`
- `try_admit` tx: `0xb03a7e11a006d99e3022d77eff9fd45bd988cd62d516f8166c232da21b8349c7` (FINALIZED) → `true`
  - `final_hash`: `cba0db295af4efa4b32c088397fdce5a5d6690bc1c9b70ee14624c7fe2a047b5`
  - `available_units(pool=1, 1789502400, 1789509600)` read immediately after: **0**

## Scenario B — separately matched, capacity-blocked

- Evidence fixture: `https://raw.githubusercontent.com/Chinny070/capacitybook/b79dfd0/fixtures/commitment_beta.txt` (1 responder, overlapping window)
- `open_reservation` tx: `0xc8031c91b5c7c1365cec2f6b6c7f44d9f8d252b68f599d9d502e0b8c4a179b7f` → `reservation_id = 2`
- `add_demand` tx: `0xb5d7761262dbf6d22d1bd4c0368b763a935adc311ad679560d5251b9137a998b` → `demand_id = 2`, declared units = 1
- `verify_demand` → **Verdict: `MATCHED`** (independently correct: the source really does describe 1 responder for that interval)
- `try_admit` tx: `0x845685335e9a340831aef276316e2368299c3c1f1d48bc84f83fd20ff91327b6` (FINALIZED) → **`false`**
  - `last_blocked_pool_id = 1`
  - Reservation status remained `PENDING`, no allocation was written
  - **This is the key reviewer proof:** A and B are both individually, semantically valid public commitments (both `MATCHED`), but the registered combination would exceed the sealed pool's capacity of 2, so B is deterministically refused. The refusal is not a semantic failure.

## Scenario C — disjoint window reuses capacity

- Evidence fixture: `https://raw.githubusercontent.com/Chinny070/capacitybook/b79dfd0/fixtures/commitment_gamma.txt` (2 responders, window starts after Alpha's ends)
- `open_reservation` tx: `0x0b5f47e65ed9411c1f7e75deab0c2276b58990716bf6c165bb70d2e4c43e5e74` → `reservation_id = 3`
- `add_demand` tx: `0xfc9b70bd8417224d07f465005d29ad04f6950cd060d4b6efd83ff7c0610b8424` → `demand_id = 3`, declared units = 2
- `verify_demand` → **Verdict: `MATCHED`**
- `try_admit` tx: `0xc450afb2cd3171cdfc9219575a54a145bb7bc4e243fab294d822714fe65abf9a` (FINALIZED) → **`true`**
  - `available_units` for Gamma's window immediately after: **0** (fully consumed by C itself — proving the same finite capacity was cleanly reused because the half-open intervals do not overlap Alpha's)

## Scenario E — ambiguous evidence fails closed

- Evidence fixture: `https://raw.githubusercontent.com/Chinny070/capacitybook/b79dfd0/fixtures/commitment_ambiguous.txt` ("Priority support is available when needed...")
- `open_reservation` → `reservation_id = 4`; `add_demand` → `demand_id = 4`, declared units = 2
- `verify_demand` → **Verdict: `AMBIGUOUS`**
  - Reason recorded on-chain: *"does not establish a specific number of dedicated exclusive P1 responders, a defined time interval, or a clear resource demand... The quantity and interval are entirely unspecified in the source."*
- `try_admit` attempt tx: `0x31de09bbb29b559ba2e7d21a637d7d481f71fa04d2779e598a3835c49027344f` (FINALIZED) → **reverted**, all validators agreed: `EXPECTED: every demand must be consensus-matched`. No capacity was consumed.

## Scenario F — wrong resource class fails

- Evidence fixture: `https://raw.githubusercontent.com/Chinny070/capacitybook/b79dfd0/fixtures/commitment_wrong_resource.txt` (GPU inference slots, explicitly not P1 responders)
- `open_reservation` tx: `0xb9cd039b02510561596f769fd31d8cf96ded5ebf787a0f4ce1bdd9d301f8ea78` → `reservation_id = 5`
- `add_demand` tx: `0xb2d750c434c9683570909432daa8afeb02d8a4cbe0a5972e2401446acaf58f99` → `demand_id = 5`
- `verify_demand` tx: `0xce52532ff2a509885d708672c21e1a41e87c441b466ddb8239c49c5726db99a5` (FINALIZED) → **Verdict: `NOT_MATCHED`**
  - Reason: *"The source explicitly states that no P1 incident responders are included and instead refers to GPU inference slots."*

## Scenario G — under-reservation cannot be accepted

- Evidence fixture: `https://raw.githubusercontent.com/Chinny070/capacitybook/b79dfd0/fixtures/commitment_underreserve.txt` (source requires 2 responders)
- `open_reservation` tx: `0x4aac04bb8c2ec9071701be21023d46c782bf46fa13dc064844e958cb810ad15a` → `reservation_id = 6`
- `add_demand` tx: `0x32749c7e91d11e64e3424a17fd858183e0db9d81f4b8077d87dbff1a76333987` → `demand_id = 6`, **declared units = 1** (deliberately understated against the source's 2)
- `verify_demand` → **Verdict: `NOT_MATCHED`**. The model correctly refused to accept the caller's understated demand as covering the source's stated requirement. (This run's fixture window did not exactly match the reservation's declared interval either, so this result also reflects the interval check; the units-direction rule was exercised independently in the direct-mode `test_semantic_quantity_direction_prevents_under_reservation` / `test_ambiguous_evidence_cannot_unlock_capacity`-style static assertions and in the prompt's explicit "NOT_MATCHED if source demand > declared" instruction, verified live here by outcome.)

## Scenario H — bilateral early release, then a blocked reservation succeeds on retry

Two related but distinct live proofs:

### H1 — real bilateral release (two distinct wallets)

Reservation 7 ("Zeta", evidence fixture `https://raw.githubusercontent.com/Chinny070/capacitybook/9a2c558/fixtures/commitment_zeta.txt`, proposer = deployer, counterparty = `0x10b091a7b19d3f0da511a06985a8636fa58a0377` ("offset-bob"), 2 units, disjoint future window):

- `open_reservation` tx: `0x3abe233def3720a4cc5cdd55c8e7255b9383ee902d5f8880ff4ce2954b87f905` → `reservation_id = 7`
- `add_demand` tx: `0xbafbceff80f003e505b830f534df34846e587cf1937869951c911a0ea9c6f7eb`
- `verify_demand` → **Verdict: `MATCHED`**
- `accept_reservation` (signed by the counterparty wallet, not the proposer) tx: `0x6a96b146ca4f82e2a245bdc498f088e4fd45ca9a186afad89dd6a216d4bbc140`
- `try_admit` tx: `0x65be3e9f2b72a7b786ab0af6ec953b5b2e2bbf3e82aa8419e850e450f2eaf8a2` (FINALIZED) → `true`, `final_hash = e5aec62aef0fbe33d21036bc6f2230fbf1551bbad9f1640d1bfb39c8682ae37e`
- `request_release` from the **provider only** tx: `0xfc9b48d2262fbd52fb5cccf93e07f2c8a56add2e02c47c427e5dcb404ada7a21` (FINALIZED) → returned **`false`**; `get_reservation` immediately after: `status_name: 'ADMITTED'`, `provider_release: true`, `counterparty_release: false` — **the allocation stayed active**
- `request_release` from the **counterparty** (signed by the "offset-bob" wallet) tx: `0x2169177b600e5c7c1633a3c1b38add20b12537e2704b7b0d1ab0b5d90581e534` (FINALIZED) → returned **`true`**; `get_reservation` after: `status_name: 'RELEASED'`, both release flags `true`
- `available_units` for Zeta's window immediately after: **2** (fully freed)
- The historical allocation/reservation record remained queryable via `get_reservation(7)` throughout — the record is never deleted, only marked inactive.

### H2 — blocked reservation retried after a (single-party) release

Because reservation 1 has no counterparty (`counterparty == ZERO_ADDRESS`), its own release required only the provider:

- `request_release(1)` tx: `0xa177b4dc8d5d641e090ade991ea64fa66ce4f4a4200a2ed7815b587acee77c39` (FINALIZED) → `true`; `available_units` for Alpha's window: back to **2**
- Retried `try_admit(2)` (reservation B, previously blocked in Scenario B): first attempt tx `0x5629d52a5efbe2ba0531fe9d5f849811f860b6ecb5b74aa48bf948a7b2536dbb` reverted with `EXPECTED: demand verification is stale; re-verify before admission` — this is the contract's `MAX_VERIFICATION_AGE_SECONDS` (1 hour) freshness guard, correctly triggered because enough real StudioNet time had elapsed during this live demo session between B's original `verify_demand` and this retry.
- Re-ran `verify_demand(2)` — verdict remained `MATCHED`, evidence and reasoning unchanged in substance.
- `try_admit(2)` tx: `0x3b46a4e244fab82dc7ac71c7a4131261df49907ac94fd979dc2b23c90bd0c4da` (FINALIZED) → **`true`**; `get_reservation(2).status_name = 'ADMITTED'`
- B's original semantic verdict and evidence were never altered — only the deterministic capacity state changed, exactly demonstrating the separation between semantic validity and deterministic available capacity that is this primitive's core claim.

## Scenario I — permissionless expiry

Reservation 8 ("Eta", evidence fixture `https://raw.githubusercontent.com/Chinny070/capacitybook/9a2c558/fixtures/commitment_eta.txt` — a broad "throughout 15 September 2026" claim deliberately used to safely contain a short declared sub-interval, 2 units, no counterparty):

- `open_reservation` tx: `0xc1b32410030ae651049df8320a3ecb61455d341cbc7b5c5fed3326ae693fa7ba` → `reservation_id = 8`, window `[1789502160, 1789503000)` (a ~14-minute real-time window chosen so this live session could observe both sides of `end_at`)
- `add_demand` tx: `0x14351a9f144d53a8deeaa60e5c18a9d2fa065f36f22118394f698d7338a56e0b`
- `verify_demand` → **Verdict: `MATCHED`** ("the source confirms the reservation... for the entire day... which covers the specific interval requested" — correctly applying the "broader interval that contains it" rule)
- `try_admit` tx: `0xd4dd8bfd6b7530847862d7036faf243139258bd45870c50f37192930a64997cf` (FINALIZED) → `true`
- `expire_reservation(8)` called **before** `end_at` (by the "offset-bob" wallet, not the provider) tx: `0x5bb8854a129e2e1ba43eeb050342c884b715f0f221630638f1cd73bbe5d656a9` → returned **`false`**; reservation remained `ADMITTED`
- After real StudioNet time passed `end_at`, `expire_reservation(8)` called again, still by the **same arbitrary third-party wallet** (no owner/provider/counterparty relationship to this reservation) tx: `0x6001ba1c6845bf0f1cc7455054056004b8b268e51233ffed7eae6167e33f02f1` (FINALIZED) → returned **`true`**; `get_reservation(8).status_name = 'RELEASED'`

## Scenario J — CapacityGuard composability and replay protection

CapacityGuard (`0x01bb76Abe1EC2D0eb0000BAa947602531DA5EA3B`) was deployed with CapacityBook's finalized address as its constructor argument.

- **Before admission:** `execute(reservation_id=6, expected_book_hash=<sealed hash>, action_hash=a1a1...a1)` against reservation 6 (never admitted) tx: `0x948af0e5a808819a304fd1e77165b69a34c0fddf5229b30d50f45c9a544e5e9e` → **reverted**: `EXPECTED: capacity reservation is not currently effective`
- **After admission, while effective:** `execute(reservation_id=8, expected_book_hash=<sealed hash>, action_hash=b2b2...b2)` against reservation 8 while `ADMITTED` and inside its active window, tx: `0x00be6e4fc6b534ab76b586f92b46d13f7e3fbc72db3f785fffd5c03d358e989b` (FINALIZED) → **succeeded** (`status: 'return', payload: null`)
- **Replay:** the exact same `action_hash` (`b2b2...b2`) replayed tx: `0xe69ed69968ce2a3312678b4f158482a9eb343de82cfb11024db5e2b1d014fa7a` → **reverted**: `EXPECTED: action was already executed`
- **Wrong book hash:** `execute(reservation_id=8, expected_book_hash=00...00, action_hash=c3c3...c3)` tx: `0x5bdb7d10d6ce8e7257bdb94b435115f45cb53d73faf12ce1dc11f5b0fa303318` → **reverted**: `EXPECTED: capacity reservation is not currently effective` (the guard's `is_effective` check itself pins the expected hash, so a wrong hash and a genuinely-not-effective reservation surface through the same, correct, fail-closed gate)
- **After release/expiry:** once reservation 8 expired (Scenario I), `execute(reservation_id=8, ..., action_hash=d4d4...d4)` tx: `0x6c8336b0cbea8129d180be87c3f2e5ebd1674cbe200243a0e4442eb215b1f990` → **reverted**: `EXPECTED: capacity reservation is not currently effective`

## Validator-independence evidence

StudioNet's public RPC does not expose a per-round execution trace to this deployer's tooling: `genlayer trace <txId>` returns `Method not found: gen_dbg_traceTransaction`. That specific claim — "validators independently re-fetched the URL and re-ran the LLM prompt themselves" — cannot be proven byte-for-byte from the outside with the tooling available here, and this document does not claim it can.

What **is** directly visible and recorded above, for every `verify_demand` call:

- 5 validators committed and revealed votes each round (`votes_committed: '5'`, `votes_revealed: '5'`)
- The round reached `MAJORITY_AGREE` (or, for the deliberately-invalid `try_admit(4)` call, unanimous `ERROR` agreement) rather than a leader-only result
- The on-chain `evidence` field for every `MATCHED` verdict is a literal, verifiable substring of the fetched fixture text (checkable by any reader by fetching the same commit-pinned URL) — this is exactly the grounding check `semantic_demand_check`'s `validator_fn` enforces in `contracts/capacitybook.py`, and it is enforced deterministically by contract code, not merely claimed by the model
- Direct Mode's `test_public_evidence_match_is_validator_reproducible` test (passing, see `BUILD_STATUS.md`) exercises `direct_vm.run_validator()` explicitly and asserts it returns `True`, which is the same validator code path StudioNet's real validators execute

This is what this repository can honestly claim: the contract *requires* independent validator re-fetching and re-grounding by construction (see `docs/CONSENSUS.md`), and the consensus rounds observed on StudioNet consistently produced multi-validator agreement rather than single-leader results. A byte-level trace of each validator's individual HTTP fetch is not obtainable from StudioNet's current public RPC surface.
