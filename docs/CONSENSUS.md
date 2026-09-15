# Consensus and equivalence design

## Why consensus is needed

The deterministic part of CapacityBook is straightforward: integer capacity, interval overlap and state transitions.

The non-deterministic question is whether a public real-world commitment actually consumes a registered semantic resource class in the declared amount/window.

Example pool definition:

> A human or autonomous responder reserved for exclusive P1 incident handling during the declared interval.

Example source:

> Service commitment Alpha reserves two dedicated P1 responders from 10:00 UTC until 12:00 UTC.

A deterministic parser cannot safely generalize this boundary across arbitrary public service language.

## Bounded verdicts

Only four results exist:

- `MATCHED`
- `NOT_MATCHED`
- `AMBIGUOUS`
- `UNAVAILABLE`

Only `MATCHED` can participate in admission.

## Leader

The leader independently:

1. renders the public HTTPS source;
2. treats all source text and caller text as hostile data;
3. evaluates the frozen pool definition, declared units and interval;
4. returns a bounded verdict, short reason and, for `MATCHED`, one verbatim supporting excerpt.

## Validator

The validator does not validate JSON formatting alone. It independently:

1. renders the source again;
2. performs the same bounded classification;
3. requires the verdict class to match;
4. if `MATCHED`, checks that the leader's evidence excerpt literally occurs in the validator's independently fetched source.

This makes unsupported leader claims rejectable even when the output schema is valid.

## What validators cannot decide

Validators do not decide:

- pool capacity;
- number of units to reserve;
- whether to admit despite an overcommit;
- arithmetic;
- release conditions;
- approval requirements;
- which new resource class should exist.

Those are frozen inputs or deterministic state rules.

## Inconclusive is first-class

Vague evidence is not normalized into a match. `AMBIGUOUS` remains stored and blocks admission until the demand is re-verified against evidence that actually establishes the bounded claim.
