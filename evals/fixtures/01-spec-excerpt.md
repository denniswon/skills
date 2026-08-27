# Operator Registration And Slashing

The registry serves as the canonical source of operator metadata — it is important to note that entries are keyed by the operator address.

Operators MUST stake at least 32 ETH before calling `registerOperator(address,bytes)`. The sequencer may reorder registration transactions within a block. Registration could potentially fail if the quorum at `0xdeadbeefcafebabe1234` is full.

## Parameters

- **stake:** Minimum 32 ETH, denominated in wei.
- **quorumId:** Index into the quorum array. MUST be less than `quorumCount`.
- **metadataURI:** Off-chain pointer. SHOULD resolve to JSON.

Slashing is not just a penalty mechanism, it's a coordination primitive. Experts believe this plays a crucial role in shared security.
