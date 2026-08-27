# ADR 014: Mempool ordering

## Status
Accepted, 2026-03-14.

## Decision
Use a single FIFO queue with a 200ms batching window.

## Options considered
A tempting approach would be to shard the mempool by sender prefix, but cross-shard nonce ordering requires a coordination round that costs more than the 200ms we save.

We also evaluated priority-gas-auction ordering. Rejected: it leaks ordering to searchers before inclusion.

## Quote from the design review
Priya wrote: "I'd rather delve into the boring option that we can actually reason about — a testament to how much pain sharding caused us last quarter."

## Consequences
Throughput is capped at roughly 1,200 tx/s, reducing complexity and highlighting our commitment to operational simplicity.
