# Instructions for Chinny's coding agent

Unzip this package into the already-created repository `Chinny070/capacitybook` and work **in that repository**.

## Non-negotiable scope

- This is a **standalone GenLayer Intelligent Contract submission**.
- **Do not add a frontend.** No React, Next.js, dashboard, landing page, Supabase, database or indexer is needed.
- Target **StudioNet chain ID 61999 only**.
- Do not switch to a development network or another chain ID.
- Preserve the core CapacityBook design: semantic demand verification + deterministic interval/capacity admission control.
- Do not turn LLM output into arithmetic, capacity selection or admission authority.

## What is already implemented

The package already contains:

- `contracts/capacitybook.py` — main reusable primitive;
- `contracts/capacity_guard.py` — minimal IC-to-IC consumer;
- custom leader/validator consensus with independent source re-fetching;
- grounded evidence excerpt enforcement;
- immutable sealed book hashes;
- multi-pool demand lines;
- atomic admission checks;
- overlapping-capacity rejection;
- disjoint-window reuse;
- bilateral early release;
- permissionless end-of-window expiry;
- Direct Mode scenario tests;
- static invariants and CI;
- architecture, consensus, threat-model and reviewer-demo docs;
- submission/deployment handoff files.

Do not rewrite this into a different product unless a real runtime incompatibility forces a narrowly scoped change.

## Your job

1. Inspect every file before editing.
2. Install the pinned Direct Mode toolchain from `requirements-direct.txt`.
3. Run:

   ```bash
   python scripts/preflight.py
   pytest -q tests/test_static.py
   pytest -q tests/direct
   ```

4. Fix **actual** GenVM/SDK/runtime incompatibilities while preserving protocol invariants.
5. Run the GenVM linter if supported by the installed toolchain.
6. Do not weaken the custom validator into format-only validation.
7. Do not change the network target from StudioNet chain ID `61999`.
8. Do not add secrets to the repo.
9. Deploy `CapacityBook` from Chinny's funded owner wallet on **61999** only after Chinny approves the deployment transaction.
10. Wait for an accepted/finalized receipt and record the deployed address.
11. Deploy `CapacityGuard`, passing the finalized CapacityBook address.
12. Execute the full lifecycle in `docs/REVIEWER_DEMO.md` on 61999:
    - one matched reservation admitted;
    - one separately matched overlapping reservation blocked for overcommit;
    - one disjoint reservation admitted;
    - bilateral release frees capacity;
    - blocked reservation succeeds when retried after release;
    - consumer IC rejects before admission, succeeds after admission, and rejects replay.
13. Update `SUBMISSION.md` only with **real finalized evidence**. Never invent deployment addresses, transaction hashes or test results.
14. Add/update an integration test with the real deployed addresses if the current network tooling supports it.
15. Re-run every check.
16. Ensure a repository-wide search returns **zero occurrences of the other Studio development chain ID** and that `61999` is consistently documented.
17. Commit the completed work to `main` and push to `Chinny070/capacitybook`.

## Review standard

Before finishing, verify all of these:

- a reviewer can explain why GenLayer consensus is necessary;
- a reviewer can see exactly what the LLM may and may not decide;
- `AMBIGUOUS` and unavailable evidence fail closed;
- source evidence is independently re-observed by validators;
- arithmetic is deterministic;
- multi-resource admission cannot partially allocate;
- outsiders cannot grief capacity without provider/counterparty approvals;
- early unilateral release cannot free a live reservation;
- the book hash pins semantics for downstream consumers;
- `CapacityGuard` demonstrates real composability and replay protection;
- deployment evidence is real and finalized;
- no frontend has been introduced.

If a test cannot run because of a toolchain/network issue, document the exact blocker and command/output. Do not replace failed verification with a claim that it passed.
