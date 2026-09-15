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

After deployment:

1. verify the network reports chain ID `61999`;
2. wait for finalized/accepted receipts;
3. record both addresses in `.env` locally;
4. execute the lifecycle in `docs/REVIEWER_DEMO.md`;
5. replace `PENDING_OWNER_DEPLOYMENT` in `SUBMISSION.md` with finalized evidence;
6. run the repository preflight;
7. commit and push only after all checks pass.

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
