# Deployment handoff

## Fixed target

**StudioNet — chain ID 61999.**

This repository is intentionally prepared for that network. Do not switch to a development-chain preset.

## Contracts

Deploy in this order:

1. `contracts/capacitybook.py` — constructor takes no arguments.
2. `contracts/capacity_guard.py` — constructor argument is the finalized CapacityBook address.

## Owner-wallet steps

The final deployment transaction must be approved from Chinny's funded owner/deployer wallet. No private key belongs in this repository.

Deployed and finalized:

- CapacityBook: `0xff7D50Eb0bc99143Dcc729929B44068BC4d23281`
- CapacityGuard: `0x01bb76Abe1EC2D0eb0000BAa947602531DA5EA3B`

A first CapacityBook deployment attempt finalized as a transaction but the contract genesis itself failed (`invalid_contract`) because the source's pinned SDK hash targeted a newer GenVM generation than StudioNet's live validators currently serve. Verifying post-deployment readability (not just transaction status) caught this; see `docs/DEPLOYMENT_EVIDENCE.md` for the full account and the corrected, live-compatible redeployment.

Full evidence for the reviewer-demo lifecycle is in [`docs/DEPLOYMENT_EVIDENCE.md`](docs/DEPLOYMENT_EVIDENCE.md).

## Suggested environment

Copy `.env.example` to `.env` and fill only public addresses/URLs there. Never commit wallet secrets.

## Final preflight

```bash
python scripts/preflight.py
pytest -q tests/test_static.py
python -m py_compile contracts/capacitybook.py contracts/capacity_guard.py
```

If the Direct Mode toolchain is installed:

```bash
pytest -q tests/direct
```
