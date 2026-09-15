# CapacityBook

**Consensus-backed capacity admission for autonomous services.**

CapacityBook prevents a provider from accepting a set of commitments that cannot all be fulfilled at the same time. It is a standalone GenLayer Intelligent Contract primitive, deliberately **without a frontend**.

The primitive separates the problem into two layers:

1. **Semantic consensus** verifies that a public commitment really consumes a declared resource class and that the caller-reserved unit amount is a safe upper bound for the commitment during the declared interval.
2. **Deterministic admission control** sums overlapping admitted allocations and refuses any new reservation that would exceed the sealed capacity of a resource pool.

The model never decides capacity, performs arithmetic, invents resources, changes demand quantities, or admits a reservation.

## Network

CapacityBook is prepared for **StudioNet, chain ID `61999`**.

This repository intentionally does not target the Studio development network. Do not change the deployment target while preparing the submission.

## Why this primitive exists

An autonomous service can satisfy every contract individually and still make promises that are jointly impossible.

Example:

```text
provider capacity: 2 dedicated P1 responders

commitment A: 2 responders, 10:00-12:00  -> fits
commitment B: 1 responder, 10:30-11:30  -> would overcommit
commitment C: 2 responders, 13:00-15:00  -> fits because the window is disjoint
```

Ordinary smart contracts can enforce the arithmetic only if every demand has already been reduced to deterministic structured data. CapacityBook addresses the missing semantic boundary: whether a real public service commitment actually consumes the registered resource class and declared amount/window.

## Protocol flow

```text
create book
   ↓
add bounded resource pools
   ↓
seal immutable book definition
   ↓
open reservation + public evidence URL
   ↓
add one or more declared demand lines
   ↓
GenLayer validators independently re-read evidence
   ↓
MATCHED / NOT_MATCHED / AMBIGUOUS / UNAVAILABLE
   ↓
provider + counterparty approval
   ↓
deterministic overlap/capacity check
   ↓
ADMITTED or blocked for overcommit
   ↓
early release by both parties OR expire at end time
```

A blocked reservation remains pending and can be retried if earlier capacity is released.

## Core invariants

- A book is mutable only until sealed.
- A pool's capacity, unit and semantic definition are frozen into the book hash.
- A reservation pins the exact sealed book hash.
- Every demand line must be consensus `MATCHED` before admission.
- `AMBIGUOUS`, `NOT_MATCHED`, and `UNAVAILABLE` fail closed.
- Consensus never computes availability.
- Overlap arithmetic is deterministic.
- Admission of a multi-pool reservation is atomic: either every demand fits or no allocation is written.
- A third party cannot grief capacity merely by opening a reservation; provider and counterparty approval are required.
- Early release requires both parties. End-of-window expiry is permissionless.
- Released allocations remain in history but stop consuming capacity.

## Contracts

### `contracts/capacitybook.py`

The reusable primitive. Main interfaces:

```python
create_book(...)
add_pool(...)
seal_book(...)
open_reservation(...)
add_demand(...)
verify_demand(...)
approve_reservation(...)
accept_reservation(...)
try_admit(...)
request_release(...)
expire_reservation(...)
available_units(...)
is_admitted(...)
```

### `contracts/capacity_guard.py`

A deliberately tiny consumer contract proving that another Intelligent Contract can gate an action on a CapacityBook reservation. It also blocks replay of an action hash.

This consumer is not the product. It exists to demonstrate reuse.

## Consensus design

For each demand line, the leader fetches the public evidence URL and asks whether it establishes all three bounded claims:

1. the commitment consumes the registered resource class;
2. the caller-declared units are a safe upper bound for the commitment's resource demand (under-reservation is never accepted);
3. it applies throughout the caller-declared interval, or a broader interval containing it.

The validator independently fetches the same public source and repeats the classification. A leader's `MATCHED` result is accepted only when the validator independently obtains `MATCHED` and the leader's supporting excerpt is literally present in the validator's fetched source.

This avoids a thin format-only validator.

See [`docs/CONSENSUS.md`](docs/CONSENSUS.md).

## What CapacityBook does not claim

CapacityBook does **not** prove that a provider will ultimately perform the service. It does not discover private contracts, infer undeclared commitments, or guarantee that every relevant reservation was registered.

It proves a narrower and useful statement:

> Given the sealed resource book and the set of reservations admitted through this contract, this new publicly evidenced commitment does not make those registered capacity obligations overlap beyond the declared deterministic capacity.

This boundary is intentional.

## Testing

Static/syntax checks:

```bash
python -m py_compile contracts/capacitybook.py contracts/capacity_guard.py
pytest -q tests/test_static.py
```

Direct Mode environment:

```bash
python -m pip install -r requirements-direct.txt
pytest -q tests/direct
```

The direct suite covers sealing, validator-grounded evidence, ambiguous evidence, overlapping rejection, disjoint reuse, bilateral early release, retry after capacity release, and hash-pinned consumption.

## Deployment status

The package does **not** pretend to contain deployment evidence before the owner's wallet executes deployment. See [`DEPLOYMENT.md`](DEPLOYMENT.md) and [`docs/REVIEWER_DEMO.md`](docs/REVIEWER_DEMO.md).

After deployment, replace the `PENDING_OWNER_DEPLOYMENT` placeholders in `SUBMISSION.md` with finalized StudioNet `61999` addresses and transaction/receipt evidence.

## Repository scope

No frontend, database, indexer or off-chain decision server is required. CapacityBook is intended for the **Intelligent Contracts** category rather than Projects.
