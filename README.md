# humanizer

An agent skill that rewrites AI-sounding prose so it reads like a person wrote it, without changing what the text says.

Most humanizers treat all prose the same. This one classifies register first, because the rules that improve a blog post will damage a spec. In a protocol document, "the sequencer may reorder transactions" and "the sequencer reorders transactions" describe different systems, and a rewrite that drops the modal has introduced a bug.

Works with any agent that supports the SKILL.md format: Claude Code, Codex, Cursor, and others.

---

## Install

### Claude Code

User-global, available in every project:

```
npx skills add denniswon/skills --skill humanizer -a claude-code -g
```

Project-scoped instead, committed and shared with your team, drop the `-g`:

```
npx skills add denniswon/skills --skill humanizer -a claude-code
```

Or install as a plugin, which gives you version tracking and `/plugin update`:

```
/plugin marketplace add denniswon/skills
/plugin install humanizer@denniswon-skills
```

### Codex

```
npx skills add denniswon/skills --skill humanizer -a codex -g
```

### Both at once

```
npx skills add denniswon/skills --skill humanizer -a claude-code -a codex -g
```

### From a clone, if you plan to edit it

```
git clone https://github.com/denniswon/skills.git ~/src/skills
ln -s ~/src/skills/skills/humanizer ~/.claude/skills/humanizer
```

Edits then take effect on the next session with no reinstall step.

### Where it lands

| Agent | Global | Project | Invoke |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | automatic |
| Codex | `~/.agents/skills/` | `.agents/skills/` | automatic, or `$humanizer` |

Restart the agent after installing. Both scan for skills at session start.

### Verify

```
ls ~/.claude/skills/humanizer/
python3 ~/.claude/skills/humanizer/scripts/scan.py --help
```

You should see `SKILL.md`, `references/`, and `scripts/`. If `references/` or `scripts/` is missing, the skill will load and then fail when it reaches for the pattern catalogue or the scanner.

---

## Usage

The skill loads on its own when a request matches. You do not need to name it.

### Rewriting text you already have

```
Clean up the prose in this README, it reads like a model wrote it.

[paste text, or give a file path]
```

Other phrasings that trigger it: humanize this, de-slop this draft, make this sound less like ChatGPT, this reads robotic, too many em dashes.

You get a critique naming what still sounded machine-made, then the final text. Ask for a different shape if you want one:

- **Final text only**, when you are pasting it straight somewhere.
- **Annotated**, marking each change, when you are deciding whether to trust the rewrite.

Point it at a file and it edits in place and reports a prose diff.

### Drafting something new

The skill also applies while composing, so the first draft comes out clean:

```
Draft a launch post for the v0.7 release.
Write the announcement for our partnership with X.
```

### Matching your voice

Paste a sample of your own writing and say so. The sample outranks every default in the skill, including the em dash and fragment rules:

```
Rewrite this to match how I write in the sample above.
```

This matters if you write in fragments or use dashes deliberately. Without a sample, the skill applies its defaults and will strip both.

### When it deliberately does nothing

It skips internal research, competitive teardowns, interview summaries, and options analysis. That material is read for precision, not voice. If you want a research brief humanized anyway, say so explicitly.

---

## What it will not touch

Code fences and inline spans, identifiers, hex strings and addresses, ABI signatures, numbers and units, version numbers, link targets, frontmatter, and quoted material. Link text can change; the URL cannot.

In technical register it also preserves normative modality. `MUST`, `SHOULD`, and `may` carry meaning a reader implements against, so they are treated as content rather than hedging, and headings and list counts stay put because they are link targets and diff units.

It will not invent facts. Names, numbers, dates, and citations come from the source or from you. If a sentence would read better with a specific detail the source lacks, it stays general or you get asked.

---

## Scanner

A deterministic regex pass you can run yourself:

```
python3 skills/humanizer/scripts/scan.py FILE --register technical|narrative|auto [--json]
```

Stdlib only, no network, no writes. It masks code fences, inline spans, link targets, URLs, hex literals, and frontmatter before scanning, so findings never point at anything a machine parses. Findings are reported by enclosing heading rather than line number. Exit code 1 on findings, 0 when clean.

It is a floor, not a gate. Regex catches em dashes, chatbot residue, vague attribution, filler, stacked qualifiers, and title case. It cannot catch inflated significance, forced tricolons, or invented facts, so the skill runs a self-critique pass regardless of what the scanner says.

---

## Evals

Eight cases in `evals/`, five with fixtures and a checker that compares a rewrite against its source:

```
python3 evals/check.py evals/fixtures/01-spec-excerpt.md output.md --register technical
```

It verifies that identifiers survive, numbers were not invented, quotations are verbatim, modality was not weakened, and structure held. `evals/PROMPTS.md` has copy-paste prompts for running each case in a fresh session, and explains why grading has to happen outside the session being tested.

---

## Troubleshooting

**It never fires.** Skills load by description match. Say what you want done to the text rather than naming the skill, and check the install actually landed in the directory your agent reads.

**It fires on everything.** If it triggers on code explanations or research notes, the audience rule is not doing its job. Open an issue with the prompt that triggered it.

**It flattened a list I wanted.** It classified the document as narrative. Say "this is reference documentation" and it will preserve structure.

**It stripped my em dashes.** Give it a writing sample. Without one it applies the defaults.

**Scanner not found.** The skill runs it from its own directory. If your agent's working directory is elsewhere, give the absolute path.

---

## Status

0.1.0. The rules and the scanner work and are tested. The eval suite has been written but not yet run end to end against every case, so expect rough edges, particularly in short-form output.

## License

MIT. See NOTICE for attribution. The pattern taxonomy derives from Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup) and the `blader/humanizer` skill.
