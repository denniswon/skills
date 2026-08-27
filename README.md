# humanizer

An agent skill that rewrites AI-sounding prose so it reads like a person wrote it, without changing what the text says.

Most humanizers treat all prose the same. This one classifies register first, because the rules that improve a blog post will damage a spec. In a protocol document, "the sequencer may reorder transactions" and "the sequencer reorders transactions" describe different systems, and a rewrite that drops the modal has introduced a bug.

## Install

```
npx skills add denniswon/skills
```

Global, for a specific agent:

```
npx skills add denniswon/skills --skill humanizer -a claude-code -g
npx skills add denniswon/skills --skill humanizer -a codex -g
```

Claude Code reads skills from `.claude/skills/`; Codex reads them from `.agents/skills/` and invokes them with `$humanizer`. Restart the agent after installing, since both scan for skills at session start.

Claude Code plugin marketplace:

```
/plugin marketplace add denniswon/skills
/plugin install humanizer@denniswon-skills
```

## What it does

Two registers, two rule sets.

Technical reference covers specs, RFCs, ADRs, READMEs, API docs, audit findings, postmortems, and runbooks. Structure is preserved: headings are link targets and diff units, and lists of requirements exist because reviewers scan them. Normative modality is treated as content rather than hedging.

Narrative covers posts, essays, announcements, and threads. Structure is fair game. Bulleted lists with bolded lead-ins are usually a model artifact in this register, and collapsing them back into prose is part of the job.

Applies to prose another person will read. Skips internal research and analysis, where precision matters and voice does not.

## What it will not touch

Code fences and inline spans, identifiers, hex strings and addresses, ABI signatures, numbers and units, version numbers, link targets, frontmatter, and quoted material. Link text can change; the URL cannot.

It also will not invent facts. Names, numbers, dates, and citations come from the source or from you. If a sentence would read better with a specific detail the source lacks, it stays general or you get asked.

## Scanner

```
python3 skills/humanizer/scripts/scan.py FILE --register technical|narrative|auto [--json]
```

Stdlib only, no network, no writes. It masks protected regions before scanning, so findings never point at anything a machine parses. Exit code 1 on findings, 0 when clean.

The scanner is a floor, not a gate. Regex catches em dashes, chatbot residue, vague attribution, filler, and title case. It cannot catch inflated significance or invented facts, so the skill runs a self-critique pass regardless.

## Evals

`evals/` holds eight cases and a checker that compares a rewrite against its source:

```
python3 evals/check.py evals/fixtures/01-spec-excerpt.md output.md --register technical
```

It verifies that identifiers survive, numbers were not invented, quotations are verbatim, modality was not weakened, and structure held. See `evals/README.md`.

## Status

0.1.0. The rules and the scanner work. The eval suite has been written but not yet run end to end against every case, so expect rough edges, particularly in short-form output.

## License

MIT. See NOTICE for attribution.
