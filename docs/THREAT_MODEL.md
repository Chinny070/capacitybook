# Threat model

## Malicious leader

**Threat:** leader fabricates `MATCHED` with a convincing explanation.

**Control:** validator independently re-fetches and re-classifies. A `MATCHED` leader result also needs an excerpt literally present in the independently fetched source.

## Prompt injection in evidence

**Threat:** public source includes instructions such as “ignore previous instructions” or asks the model to move funds.

**Control:** the prompt explicitly treats all source and caller fields as hostile data. Model output cannot itself move funds or alter admission; deterministic contract code controls state.

## Capacity griefing

**Threat:** a stranger opens fake reservations until capacity appears full.

**Control:** opening a reservation consumes no capacity. Provider and counterparty approval plus consensus-matched demand are required before deterministic admission.

## Model invents quantity

**Threat:** model turns vague “dedicated support” into “2 responders”.

**Control:** quantity is a caller-declared integer. Consensus may only confirm that this reserved amount safely covers the publicly evidenced demand. If the source implies a larger or open-ended demand, the result must not be `MATCHED`. Ambiguous quantity fails closed.

## Partial multi-resource admission

**Threat:** first resource is allocated before a later pool fails, leaving a stranded partial commitment.

**Control:** `try_admit` checks every demand first, then writes allocations in a second pass.

## Early unilateral release

**Threat:** provider or customer frees capacity while the other party still relies on the commitment.

**Control:** early release needs both parties. Expiry after the frozen end time is permissionless.

## Stale semantics

**Threat:** consumer assumes a resource definition different from the one used during admission.

**Control:** reservation pins the sealed `book_hash`; consumer APIs require the expected hash.

## Private/off-chain commitments

**Threat:** provider made other commitments that CapacityBook never saw.

**Control/limitation:** CapacityBook does not claim global omniscience. It guarantees non-overcommit only across reservations actually admitted into the sealed book.
