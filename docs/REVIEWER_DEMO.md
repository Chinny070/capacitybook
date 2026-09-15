# Reviewer demo plan

Use **StudioNet chain ID 61999** only.

## Goal

Show that CapacityBook is not an LLM classifier. The strongest demo is the deterministic consequence of two individually valid semantic commitments colliding on the same scarce resource.

## Demo A — first commitment is admitted

1. Deploy `CapacityBook`.
2. Create a book for `Dedicated P1 responder capacity`.
3. Add a pool with capacity `2 responder` units.
4. Seal the book and record its hash.
5. Open reservation A for a public commitment that explicitly reserves `2` responders during interval T.
6. Add a demand of `2` units.
7. Call `verify_demand`; record the finalized `MATCHED` receipt/evidence.
8. Provider and counterparty approve.
9. Call `try_admit`; show `ADMITTED` and `available_units == 0` for T.

## Demo B — second valid commitment is blocked

1. Open reservation B for a different public commitment that genuinely requires `1` responder overlapping T.
2. Consensus should also return `MATCHED`.
3. Provider/counterparty approve.
4. `try_admit` must return `false`.
5. Show `last_blocked_pool_id` and the emitted `ReservationBlocked` values.

This is the key distinction: the semantic commitment is valid, but the protocol refuses it because the registered promises would jointly exceed capacity.

## Demo C — disjoint window succeeds

Create reservation C for all `2` units after reservation A's end time. It should be admitted because half-open intervals do not overlap.

## Demo D — release then retry

1. Both parties request early release of A.
2. Show that its historical allocation remains queryable but `active == false`.
3. Retry B.
4. B should now become `ADMITTED` without changing its evidence or semantic verdict.

## Demo E — real consumer IC

Deploy `CapacityGuard` with CapacityBook's address.

- Call `execute` with B before B is admitted: must revert.
- Admit B.
- Call `execute` with the exact book hash and a 32-byte action hash: succeeds.
- Replay same action hash: must revert.

Capture finalized addresses and receipts in `SUBMISSION.md`.
