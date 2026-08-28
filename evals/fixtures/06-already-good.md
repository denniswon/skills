# Why we dropped the batching layer

We built the batching layer in March because proving was expensive and we assumed amortizing across transactions would help. It did, for about six weeks.

The problem showed up in the p99. Batches waited for stragglers, and a single slow proof held up everything behind it. Median latency looked great in the dashboards. The tail was awful, and the tail is what users actually experience.

Ike noticed it first, from a support ticket where someone's withdrawal sat pending for eleven minutes. We spent two days assuming it was a serialization bug before checking the batch queue depth.

So we removed it. Proving costs went up about 15%, which we can absorb, and p99 dropped from eleven minutes to under thirty seconds. The lesson I keep relearning is that averaging a cost across a batch does not remove the cost, it just moves who pays it and when.
