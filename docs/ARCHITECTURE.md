# Architecture

## Design objective

CapacityBook is admission control for semantically described service capacity.

The design deliberately keeps semantic judgement narrow and moves every consequence that can be deterministic into ordinary contract logic.

## State objects

### CapacityBookDefinition
Owns a version-frozen set of resource pools. Sealing computes `definition_hash` over the book label, purpose and every pool's exact semantic definition, unit and capacity.

### ResourcePool
A bounded resource class such as `Dedicated P1 responders`, expressed in a deterministic integer unit.

### Reservation
Pins:

- proposer and counterparty;
- exact book hash;
- evidence URL;
- start/end interval;
- approval state;
- lifecycle state;
- final hash after admission/release/cancellation.

### DemandLine
Pairs a reservation with one pool and a caller-declared integer demand. Consensus can only confirm or reject that declaration; it cannot choose another amount.

### Allocation
Created only after every demand line is matched and the entire multi-pool reservation fits. Allocations are retained historically and toggled inactive on release.

## Atomic admission

`try_admit` performs two passes:

1. calculate every pool's overlapping used units and reject immediately if any pool would exceed capacity;
2. only after all checks pass, create all allocations.

This prevents a multi-resource reservation from partially consuming capacity.

## Overlap rule

Intervals are half-open:

```text
[start, end)
```

Two intervals overlap exactly when:

```python
a_start < b_end and b_start < a_end
```

Therefore a reservation ending at 12:00 and another starting at 12:00 do not overlap.

## Approval model

Semantic evidence alone cannot reserve capacity because anyone could grief the provider. Admission requires:

- provider approval; and
- counterparty approval when a counterparty exists.

If the provider opened the reservation, provider approval is implicit. If the counterparty opened it, counterparty approval is implicit.

## Release model

Before `end_at`, both provider and counterparty must request release. At or after `end_at`, anyone may call `expire_reservation` because the reservation's frozen time window has ended deterministically.

## Consumer boundary

`CapacityGuard` calls:

```python
CapacityBook.is_effective(reservation_id, expected_book_hash)
```

A downstream contract therefore pins both the reservation and the exact book semantics it expected.
