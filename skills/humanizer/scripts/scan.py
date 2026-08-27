#!/usr/bin/env python3
"""Flag mechanically detectable signs of AI writing in Markdown or plain text.

Masks code fences, inline code, URLs, link targets, and frontmatter before
scanning, so findings never point at anything a machine parses.

Usage:
    python scan.py FILE [--register technical|narrative|auto] [--json]
    cat draft.md | python scan.py - --register narrative

Exit codes: 0 = no findings, 1 = findings, 2 = usage error.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass, asdict

# --------------------------------------------------------------------------
# Masking: replace protected regions with same-length filler so offsets hold.
# --------------------------------------------------------------------------

MASK_PATTERNS = [
    (re.compile(r"\A---\n.*?\n---\n", re.DOTALL), "frontmatter"),
    (re.compile(r"```.*?```", re.DOTALL), "fenced code"),
    (re.compile(r"~~~.*?~~~", re.DOTALL), "fenced code"),
    (re.compile(r"(?m)^(?: {4}|\t).*$"), "indented code"),
    (re.compile(r"`[^`\n]+`"), "inline code"),
    (re.compile(r"\]\([^)\s]+\)"), "link target"),
    (re.compile(r"<https?://[^>\s]+>"), "url"),
    (re.compile(r"https?://\S+"), "url"),
    (re.compile(r"\b0x[0-9a-fA-F]{6,}\b"), "hex literal"),
]


def mask(text: str) -> str:
    """Blank out protected regions, preserving length and newlines."""
    masked = text
    for pattern, _kind in MASK_PATTERNS:
        def blank(m: re.Match) -> str:
            return "".join("\n" if ch == "\n" else "\x00" for ch in m.group(0))
        masked = pattern.sub(blank, masked)
    return masked


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

@dataclass
class Rule:
    id: str
    pattern: str
    message: str
    registers: tuple  # which registers this applies to
    confidence: str = "high"
    flags: int = re.IGNORECASE


FIGURATIVE_WORDS = [
    "delve", "delves", "delving", "testament", "tapestry", "realm",
    "showcas(?:e|es|ing|ed)", "underscor(?:e|es|ing|ed)", "pivotal",
    "seamless(?:ly)?", "leverag(?:e|es|ing|ed)", "harness(?:es|ing|ed)?",
    "unlock(?:s|ing)? the", "elevat(?:e|es|ing|ed) the", "foster(?:s|ing)?",
    "myriad", "plethora", "vibrant", "ever-evolving", "at the forefront",
    "in today's", "navigat(?:e|es|ing) the", "the landscape of",
    "in the (?:world|realm|landscape) of", "game[- ]chang(?:er|ing)",
    "cutting[- ]edge", "state[- ]of[- ]the[- ]art", "revolutioniz(?:e|es|ing|ed)",
]

RULES = [
    Rule("em-dash", r"\s?[\u2014\u2013]\s?", "em/en dash: use a period, comma, colon, or parentheses",
         ("technical", "narrative")),
    Rule("curly-quote", r"[\u2018\u2019\u201c\u201d]", "curly quote: use straight quotes",
         ("technical", "narrative")),
    Rule("ellipsis-char", r"\u2026", "typographic ellipsis: use three periods",
         ("technical", "narrative")),
    Rule("emoji", "[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]", "emoji",
         ("technical", "narrative")),

    Rule("figurative-vocab", r"\b(?:" + "|".join(FIGURATIVE_WORDS) + r")\b",
         "overused AI vocabulary (check for terms of art before cutting)",
         ("technical", "narrative"), confidence="medium"),
    Rule("transition-adverb", r"(?m)^\s*(?:Moreover|Furthermore|Additionally|Notably|Importantly)\b",
         "formulaic transition opener", ("technical", "narrative")),

    Rule("not-just", r"\b(?:isn't|is not|it's not|not) just [^.,;]{2,40}(?:,| but| it's)",
         "\"not just X, but Y\" construction", ("technical", "narrative")),
    Rule("avoid-is", r"\b(?:serves as|stands as|boasts|represents a|functions as)\b",
         "avoiding 'is'/'has'", ("technical", "narrative")),
    Rule("false-range", r"\bfrom [^.]{3,40} to [^.]{3,40}\b(?=[,.])",
         "possible false 'from X to Y' range", ("technical", "narrative"),
         confidence="low"),

    Rule("filler", r"\b(?:in order to|due to the fact that|it is important to note that|"
                   r"it's worth noting that|when it comes to|a wide range of|"
                   r"plays? a (?:crucial|key|vital|pivotal) role|"
                   r"at the end of the day|needless to say)\b",
         "filler phrase", ("technical", "narrative")),
    Rule("stacked-qualifier",
         r"\b(?:could potentially|may possibly|might potentially|possibly could|"
         r"generally tends to|often times)\b",
         "stacked qualifiers: keep one modal", ("technical", "narrative")),

    Rule("chatbot-residue",
         r"(?:I hope this helps|Let me know if|Feel free to (?:ask|reach)|"
         r"Great question|You're absolutely right|Certainly[!,]|"
         r"As an AI|As of my last (?:update|knowledge)|"
         r"While (?:specific )?details are limited)",
         "chatbot residue", ("technical", "narrative")),

    Rule("manufactured-depth",
         r"\b(?:at its core|the deeper truth|what (?:this )?really means is|"
         r"fundamentally, this is about)\b",
         "manufactured depth", ("technical", "narrative")),
    Rule("announced-structure",
         r"\b(?:let's dive in|let's (?:get|jump) (?:started|into it)|here's the thing|"
         r"buckle up|without further ado)\b",
         "announced structure", ("narrative",)),
    Rule("fake-candor", r"(?:^|[.!?]\s)(?:Honestly[?,]|Look,|Truth be told,|I'll be blunt)",
         "fake candor opener", ("narrative",), flags=re.MULTILINE),
    Rule("uplift-ending",
         r"\b(?:the future (?:looks|is) bright|exciting times ahead|"
         r"only time will tell|the possibilities are endless|"
         r"one thing is (?:clear|certain))\b",
         "generic uplift ending", ("technical", "narrative")),
    Rule("unraised-objection",
         r"\b(?:this (?:isn't|is not) (?:really |primarily |mainly )?about|"
         r"a tempting (?:option|approach) would be)\b",
         "objection or alternative that may not have been raised",
         ("technical", "narrative"), confidence="medium"),

    Rule("vague-attribution",
         r"\b(?:experts (?:believe|say|agree)|many (?:believe|argue|consider)|"
         r"it is (?:widely|generally) (?:believed|considered|regarded)|"
         r"studies (?:show|suggest)|research (?:shows|suggests)|"
         r"some (?:argue|say)|is (?:widely|often) (?:seen|viewed) as)\b",
         "vague attribution: name the source or drop the claim",
         ("technical", "narrative")),

    Rule("bold-lead-list", r"(?m)^\s*[-*+]\s+\*\*[^*]{1,40}:?\*\*:?\s",
         "bold-lead list item (correct in reference docs, a tell in prose)",
         ("narrative",)),
    Rule("bold-inline", r"(?m)^(?!\s*(?:[-+#>]|\* ))(?=.*\S).*?\*\*[^*\n]{1,60}\*\*",
         "bold inside a prose paragraph", ("narrative",), confidence="medium"),
    Rule("title-case-heading", r"(?m)^#{1,6} (?:[A-Z][a-z']+ ){2,}[A-Z][a-z']+\s*$",
         "Title Case heading: use sentence case", ("technical", "narrative"),
         flags=re.MULTILINE),
]


@dataclass
class Finding:
    rule: str
    message: str
    confidence: str
    section: str
    excerpt: str
    count_in_doc: int = 1


def section_for(text: str, pos: int) -> str:
    """Nearest enclosing Markdown heading, so findings are located by area, not line number."""
    line_start = text.rfind("\n", 0, pos) + 1
    here = re.match(r"#{1,6} +(.+)$", text[line_start:text.find("\n", pos) if text.find("\n", pos) != -1 else len(text)])
    if here:
        return here.group(1).strip() + " (the heading itself)"
    matches = re.findall(r"(?m)^#{1,6} +(.+)$", text[:pos])
    return matches[-1].strip() if matches else "(document preamble)"


def excerpt_for(original: str, start: int, end: int, width: int = 46) -> str:
    lo = max(0, start - width)
    hi = min(len(original), end + width)
    snippet = original[lo:hi].replace("\n", " ")
    snippet = re.sub(r"\s{2,}", " ", snippet).strip()
    marked = (original[start:end]).replace("\n", " ").strip()
    return f"...{snippet}..." if marked not in snippet else f"...{snippet}..."


def scan(original: str, register: str) -> list[Finding]:
    masked = mask(original)
    findings: list[Finding] = []
    for rule in RULES:
        if register != "auto" and register not in rule.registers:
            continue
        rx = re.compile(rule.pattern, rule.flags)
        hits = list(rx.finditer(masked))
        hits = [h for h in hits if "\x00" not in masked[h.start():h.end()]]
        for h in hits[:6]:  # cap noise per rule
            findings.append(Finding(
                rule=rule.id,
                message=rule.message,
                confidence=rule.confidence,
                section=section_for(original, h.start()),
                excerpt=excerpt_for(original, h.start(), h.end()),
                count_in_doc=len(hits),
            ))
    return findings


def cadence(original: str) -> dict:
    """Sentence-length variance. Model prose clusters tightly around 15-22 words."""
    prose = mask(original)
    prose = re.sub(r"(?m)^#{1,6} .*$", "", prose)
    prose = prose.replace("\x00", "")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if len(s.strip()) > 1]
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 2]
    if len(lengths) < 8:
        return {"sentences": len(lengths), "note": "too short to assess cadence"}
    mean = statistics.mean(lengths)
    sd = statistics.pstdev(lengths)
    return {
        "sentences": len(lengths),
        "mean_words": round(mean, 1),
        "stdev_words": round(sd, 1),
        "burstiness": round(sd / mean, 2) if mean else 0.0,
        "note": ("low variance: sentence lengths are uniform, a strong model tell"
                 if mean and sd / mean < 0.35 else "variance acceptable"),
    }


def detect_register(text: str) -> str:
    technical = 0
    technical += 3 * len(re.findall(r"\b(?:MUST|SHOULD|MAY|SHALL)\b", text))
    technical += 2 * text.count("```")
    technical += len(re.findall(r"\b0x[0-9a-fA-F]{6,}\b", text))
    technical += len(re.findall(r"\bv?\d+\.\d+\.\d+\b", text))
    narrative = len(re.findall(r"(?i)\b(?:I|my|we|our) \w+", text))
    return "technical" if technical >= narrative else "narrative"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="file to scan, or - for stdin")
    ap.add_argument("--register", choices=["technical", "narrative", "auto"], default="auto")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    try:
        text = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    except OSError as exc:
        print(f"cannot read input: {exc}", file=sys.stderr)
        return 2

    register = detect_register(text) if args.register == "auto" else args.register
    findings = scan(text, register)
    rhythm = cadence(text)

    if args.json:
        print(json.dumps({
            "register": register,
            "findings": [asdict(f) for f in findings],
            "cadence": rhythm,
        }, indent=2))
        return 1 if findings else 0

    print(f"register: {register}")
    print(f"cadence: {rhythm}")
    if not findings:
        print("no mechanical findings")
        return 0
    print(f"\n{len(findings)} finding(s):\n")
    by_rule: dict[str, list[Finding]] = {}
    for f in findings:
        by_rule.setdefault(f.rule, []).append(f)
    for rule, group in by_rule.items():
        print(f"[{rule}] {group[0].message} ({group[0].count_in_doc} in document, {group[0].confidence} confidence)")
        for f in group:
            print(f"    under \"{f.section}\": {f.excerpt}")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
