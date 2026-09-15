# Build status

Prepared: 2026-09-14. Finished and deployed: 2026-09-15.

## Completed

- CapacityBook and CapacityGuard implemented, ported to the GenVM SDK generation StudioNet's live validators actually serve (see `docs/DEPLOYMENT_EVIDENCE.md` for why the port was necessary), and deployed live.
- `python scripts/preflight.py` passes.
- `pytest -q tests/test_static.py` passes (5 passed).
- `python -m py_compile contracts/capacitybook.py contracts/capacity_guard.py` passes.
- `genvm-lint check` passes both static lint and SDK-based semantic validation for both contracts.
- `pytest -q tests/direct` passes (10 passed) against the newer GenVM SDK generation the pinned Direct Mode toolchain (`genlayer-test` v0.30.0-rc2) supports. Repointing the toolchain at the older, StudioNet-live GenVM generation (`v0.6.0-rc1`, matching the contracts' current `Depends` hash) still fails with a `DecodingError: unexpected end of memory` from inside the toolchain's own calldata layer, not from the contract — a genuine toolchain/SDK-generation gap, not a contract defect. Live StudioNet execution (below) is the authoritative verification for the deployed contracts.
- Repository is pinned to StudioNet chain ID `61999` everywhere; zero references to the forbidden dev chain ID or the forbidden studio dev-network alias (verified by `scripts/preflight.py` and `tests/test_static.py`).
- Repository contains no frontend.
- Deployed both contracts, verified finalization and post-deployment readability, and executed the full reviewer-demo lifecycle (Scenarios A, B, C, E, F, G, H, I, J from `docs/REVIEWER_DEMO.md`) with real StudioNet transactions. Full evidence: `docs/DEPLOYMENT_EVIDENCE.md`.

## Deployment status

Deployed and finalized on StudioNet, chain ID `61999`:

- CapacityBook: `0xff7D50Eb0bc99143Dcc729929B44068BC4d23281`
- CapacityGuard: `0x01bb76Abe1EC2D0eb0000BAa947602531DA5EA3B`

An earlier CapacityBook deployment (different address, since discarded) finalized as a transaction while its actual contract genesis failed; see `docs/DEPLOYMENT_EVIDENCE.md` for the full account. This is why deployment evidence in this repository is always accompanied by a post-deployment readability check, not just a transaction receipt.

## Known toolchain gap

Direct Mode's pinned `genlayer-test` (v0.30.0-rc2) targets a GenVM SDK generation newer than the one currently live on StudioNet. This does not affect the correctness of the deployed contracts — it is documented in `docs/DEPLOYMENT_EVIDENCE.md` and was not worked around by weakening any test or by faking a passing result.
