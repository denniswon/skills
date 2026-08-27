---
name: humanizer
description: Rewrites AI-sounding prose so it reads like a person wrote it, without changing what it says or touching code, identifiers, addresses, or normative spec language. Detects register first (technical reference vs narrative) and applies different rules to each. Use whenever the user pastes text and asks to humanize, de-slop, de-AI, tighten, or make it sound less like ChatGPT; whenever they point at a Markdown file, README, ADR, spec, RFC, audit note, launch post, blog draft, or thread and ask for a prose cleanup; whenever they say writing sounds robotic, generic, corporate, LLM-generated, or full of em dashes; AND whenever the user asks you to draft prose another person will read as prose (posts, quote-tweets, announcements, partnership or strategy docs, protocol writeups, release notes, outreach) so the draft comes out clean the first time. Do NOT use it for internal research, analysis, summaries, or briefs the requester reads to inform their own decision, where precision matters and voice does not.
metadata:
  version: 0.1.0
---

# Humanizer

Rewrite text so a reader cannot tell a model produced it, while keeping every factual claim, every technical constraint, and every literal token that a machine will parse.

The failure this skill exists to prevent is not ugly prose. It is a rewrite that reads beautifully and quietly changes what the document asserts — a hedge dropped from a spec, a function name "cleaned up," a number rounded because it looked awkward. In a protocol spec, an audit note, or a postmortem, that is a defect, not a style regression. Every rule below is subordinate to that.

## When this applies

The trigger is audience, not the act of writing. Apply this skill when the text will be read as prose by someone other than the person asking for it: a published post, a quote-tweet, a partnership document, a spec other engineers implement against, outreach to a counterparty. Skip it when the output is an input to the requester's own thinking — research notes, a competitive teardown, a summary of an interview, options analysis. That material is read for precision, not voice, and rewriting it for rhythm costs time and risks blunting exactly the specifics the reader wanted.

Two cases sit on the boundary and are worth a moment's thought rather than a reflex. A strategy document written to think with is internal; the same document sent to the counterparty is not — ask which one it is if the framing doesn't say. And notes that will later be pasted into something public should stay in research form now and get humanized at the point they become the draft, not before.

## Two things to establish before rewriting

### 1. Register

Read the text and classify it. The rule set changes completely, so getting this wrong is worse than any individual pattern miss.

**Technical reference** — specs, RFCs, ADRs, READMEs, API docs, audit findings, postmortems, release notes, runbooks. Signals: normative keywords (MUST/SHOULD/MAY), code blocks, version numbers, threat models, precise units, numbered requirements, cross-references.

**Narrative** — blog posts, launch announcements, essays, threads, conference recaps, personal writeups. Signals: first person, opinion, chronology, an argument the author is making rather than a system they are describing.

**Mixed** is common: an engineering blog post with a code sample, a README with a story in the intro. Classify per section, not per document. The intro of a README is often narrative; the configuration section beneath it is not.

If the classification is genuinely ambiguous, say which way you're leaning in one line and proceed. Don't stall.

### 2. Voice

If the user supplied a writing sample, that sample outranks every default in this skill, including the dash and hedging rules. Copy its rhythm, sentence length distribution, vocabulary level, punctuation habits, and its quirks — quirks are the strongest human signal there is. Do not sand them off in the name of the pattern list.

With no sample, default to the register: technical prose stays plain, neutral, and specific; narrative prose gets a real point of view and uneven sentence rhythm.

## Structural freedom

**Technical register: preserve structure.** Headings, heading order, list items and their count, table rows and columns, numbering, and anchors stay as they are. Someone links to `#gas-accounting`; someone else diffs this file in review. Rewrite inside the structure. If the structure itself is bad, say so at the end as a recommendation rather than acting on it.

**Narrative register: structure is yours.** Collapse a bulleted list back into prose, merge sections, reorder for argument, cut a heading that exists only because the model felt a document needed headings. Bullet lists in a personal post are usually a model artifact — a person writing about a conference doesn't emit six parallel bullets with bolded lead-ins.

## What must survive byte-identical

Never rewrite, reflow, spell-correct, or "improve" any of these, in either register:

- Fenced code blocks and inline code spans, including comments inside them
- Identifiers of any kind: function and type names, config keys, env vars, CLI flags, file paths, package names
- Hex strings, addresses, hashes, selectors, ABI signatures, chain IDs, block numbers
- Numbers, units, tolerances, version numbers, dates, durations, gas figures, percentages
- Link targets and anchors (link *text* may be rewritten; the URL may not)
- YAML/TOML frontmatter, license headers, badges
- Quoted material and citations — a quote is a claim about what someone said

Before the first pass, mentally mask these regions. `scripts/scan.py` does the same masking, which is why its findings can be trusted not to point at code.

## What must survive semantically

**Normative modality.** In technical register, `MUST`, `SHOULD`, `MAY`, `may`, `can`, `is not guaranteed to`, `is expected to` carry meaning that a reader will implement against. "The sequencer may reorder transactions" and "the sequencer reorders transactions" describe different systems. Never strengthen or weaken modality to make a sentence read more confidently.

This creates a real tension with the anti-hedging rules below, so use this test: is the hedge about the *world* or about the *author*? "May reorder" is about the world — keep it. "It's worth noting that this may possibly reorder" hedges the author's own act of telling you — cut the wrapper, keep the modal.

**Claims.** Every name, number, date, quote, benchmark, and citation must come from the source text or from the user. If a rewrite would read better with a specific detail the source doesn't have — the month, the neighborhood, the p99 latency — ask for it or leave the sentence general. Inventing a plausible number is the worst thing this skill can do.

Before rewriting anything longer than a few paragraphs, list the load-bearing claims to yourself. After rewriting, walk that list against the new text. Anything dropped, added, or altered gets fixed or flagged.

## Workflow

**Rewrite mode** (user supplies text or a file path):

1. Classify register; note it in one line.
2. Build the claim list and mask the protected regions.
3. Rewrite. Don't treat the original sentence and paragraph boundaries as fixed within whatever structural freedom the register allows — a real edit merges, splits, and cuts. A pass that only swaps words leaves the underlying model cadence intact and reads exactly as artificial as the input.
4. Run `python scripts/scan.py <file>` (or pipe the draft in on stdin) with `--register technical|narrative`. It flags what regex can catch reliably; it does not catch cadence, so it is a floor, not a ceiling.
5. Critique your own draft against `references/patterns.md` and the claim list. Name what still sounds machine-made.
6. Rewrite the parts the critique identified.
7. Show the user the critique and the final text. For file input, apply the edit and show a diff of prose changes only.

The visible critique matters: it lets the user see which changes were judgment calls, and it catches the case where pass 1 fixed surface tics and left the shape untouched.

**Draft mode** (user asks you to write something new):

Apply the pattern set as you compose rather than generating and then cleaning. Then run the scanner on your own draft before showing it, and fix what it finds. Don't narrate this — the user asked for a launch post, not a process report. Mention the check only if it surfaced something you deliberately kept, like an em dash inside a quotation.

## The patterns

`references/patterns.md` holds the catalogue: 35 patterns grouped as content, language, style, chatbot residue, and hedging, each with a before/after and a note on which register it applies to. Read it before the critique pass in rewrite mode. In draft mode, read it if you haven't already this session.

The ones that carry the most weight, worth holding in mind without opening the file:

- **Inflated significance.** "marks a pivotal moment in the evolution of rollup design" → say what it does and when it shipped.
- **Avoiding "is."** "serves as", "stands as", "boasts", "features" → "is", "has".
- **Not X but Y.** "This isn't just an optimization, it's a rethinking of..." → state the claim once.
- **Forced tricolons.** Three parallel items when the meaning has two or four.
- **Em dashes.** The single loudest tell. Periods, commas, colons, parentheses. In technical register keep them where they set off a genuine aside inside a long clause, but the default is cut.
- **Bold mini-headings in lists.** `- **Latency:** Latency improved.` In narrative, convert to prose. In technical reference this is often the correct format — a config table or an options list is *supposed* to look like that — so leave it.
- **Chatbot residue.** "I hope this helps", "Great question", "Let me know if you'd like me to expand".
- **Generic uplift endings.** "The future of the protocol looks bright." End on a fact, a decision, or an open question.
- **Fake candor and announced structure.** "Honestly? It depends." "Let's dive in." "One thing that bit me:".
- **Answering objections nobody raised** and **rejecting alternatives nobody proposed.** "This isn't really about block size..." — if no one said it was, cut it. If the objection is real and the doc needs to address it, keep it and name who raised it.

## Register-specific cautions

In **technical** register, do not:
- flatten a list of requirements into flowing prose because prose reads more human — reviewers scan these
- remove a qualifier that scopes a claim to a version, a chain, or a configuration
- change terminology to a synonym for variety; consistent naming beats varied naming in a spec, and pattern 11 (name-switching) does not license renaming a component mid-document
- delete a "note that" when the note carries a caveat a reader would otherwise miss — cut the phrase, keep the caveat

In **narrative** register, do not:
- add color, scene, or emotion the author didn't supply; if the post feels thin, that's a content gap for the author to fill, not for you to paper over with invented detail
- replace vagueness with specificity you made up
- flatten a deliberate stylistic choice you can tell is the author's — repeated openings can be rhetoric rather than a tic

## Output

Default to showing the critique and then the final text, since the user usually wants to see the reasoning. Two variations worth offering when the context suggests them: final text only, when they're pasting it straight somewhere; or an annotated version marking each change, when they're evaluating whether to trust the rewrite.

For files, edit in place and report what changed as a prose diff. State explicitly that code, identifiers, and link targets were untouched — that assurance is the thing a reviewer most needs to hear.

## Sources

The pattern taxonomy derives from Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup), by way of the `blader/humanizer` skill (MIT), with register-splitting, invariant protection, and normative-modality handling added for technical documentation.
