# Evals

Eight cases. Five have fixtures and a mechanical checker; three are judgment cases a human reads.

## Running one

Point the agent at a fixture, save its output, then diff the two:

```
python check.py fixtures/01-spec-excerpt.md output.md --register technical
```

Exit code 1 on violations, 0 when every invariant holds.

## What check.py verifies

It compares original against rewrite rather than grading prose, because the skill's important promises are all comparisons:

| Invariant | How it is checked |
|---|---|
| Code fences survive | Byte-identical substring match |
| Identifiers, hex literals, URLs survive | Every token in the original appears in the rewrite |
| No invented numbers | Every number in the rewrite must appear in the original |
| Quotations survive | Verbatim match on anything in double quotes |
| Modality not weakened | Count of MUST/SHOULD/MAY/may does not drop (technical register) |
| Structure preserved | Heading count and list item count unchanged (technical register) |
| Surface tells gone | Em dashes, chatbot residue, uplift endings, emoji, outside quotations |

The number check is the one that matters most. A rewrite that reads well and quietly changes 32 ETH to 64 ETH is the failure this skill exists to prevent, and no amount of reading catches it reliably.

## What it cannot check

Inflated significance, forced tricolons, manufactured depth, cadence, and whether the result actually sounds human. Case 5 is expected to fail the em-dash assertion, because the author's writing sample outranks the pattern list. A green run means nothing was broken, not that the rewrite is good.

## Cases

1. Technical spec. Surface tells go, modality and structure and identifiers stay.
2. Narrative launch post with the full slop signature. Tests restructuring and fabrication resistance.
3. ADR. Rejected options must survive pattern 35; a quotation containing flagged words must survive verbatim.
4. Thin conference recap with an instruction to make it engaging. Nothing may be invented.
5. Writing sample with fragments and em dashes. The sample outranks the defaults.
6. Internal research brief. The skill must not fire.
7. Rust refactor with an explanation. The skill must not fire.
8. Mixed-register README. Narrative rules on the intro, technical rules below it.
