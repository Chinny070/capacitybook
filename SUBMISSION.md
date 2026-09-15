# CapacityBook — Intelligent Contract submission notes

## Category

Standalone GenLayer Intelligent Contract / reusable primitive.

There is intentionally no frontend.

## One-sentence description

CapacityBook uses GenLayer consensus to verify the semantic resource demand expressed by public service commitments, then deterministically prevents overlapping commitments from exceeding a provider's sealed capacity.

## Why GenLayer

A normal smart contract can add numbers but cannot safely decide whether arbitrary public language such as “two dedicated P1 responders reserved for the incident window” actually consumes a registered semantic resource class. CapacityBook uses Intelligent Contract consensus only for that judgement boundary and keeps capacity arithmetic and protocol consequences deterministic.

## Consensus

Validators independently re-render the public evidence and independently reproduce the bounded verdict. `MATCHED` additionally requires the leader's evidence excerpt to be present in the validator's independently fetched source.

## Reuse

`CapacityGuard` demonstrates a second Intelligent Contract gating an action on `is_effective(reservation_id, expected_book_hash)` and blocking action replay.

## Network

- Network: StudioNet
- Chain ID: `61999`
- CapacityBook address: `PENDING_OWNER_DEPLOYMENT`
- CapacityGuard address: `PENDING_OWNER_DEPLOYMENT`

Do not substitute another chain ID when completing the deployment evidence.

## Evidence to add after owner deployment

- deployment transaction/receipt for both contracts;
- sealed book hash;
- finalized MATCHED demand receipt;
- one finalized admitted reservation;
- one finalized overlapping reservation blocked for capacity;
- one disjoint reservation admitted;
- consumer failure before admission and success after admission;
- replay rejection;
- exact commit SHA submitted for review.

## Known boundaries

CapacityBook does not prove service performance and cannot see commitments that were never registered. It prevents deterministic overcommit within the sealed book based on demands that consensus has grounded in public evidence.
