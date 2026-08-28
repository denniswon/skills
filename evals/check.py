#!/usr/bin/env python3
"""Check a humanizer rewrite against the invariants the skill promises.

Compares the original and the rewrite. Most of what the skill claims is
mechanically verifiable: identifiers survive, numbers and names are not invented
or dropped, structure holds in technical register, modality is not weakened.

Usage:
    python3 check.py ORIGINAL REWRITE [--register technical|narrative] [--json]

Exit codes: 0 = all invariants hold, 1 = violations, 2 = usage error.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]+`")
HEX = re.compile(r"\b0x[0-9a-fA-F]{4,}\b")
URL = re.compile(r"https?://\S+?(?=[)\s]|$)")
HEADING = re.compile(r"(?m)^(#{1,6}) +(.+?)\s*$")
LIST_ITEM = re.compile(r"(?m)^\s*[-*+]\s+")
# Numbers that carry meaning. Excludes bare list ordinals.
NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?\s*(?:%|ETH|wei|ms|s\b|tx/s|GB|MB)?")
MODAL = re.compile(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHALL|may|can|is not guaranteed to)\b")
QUOTED = re.compile(r"\"([^\"\n]{10,})\"")
# Capitalized word sequences: names, places, products. Line breaks do not join tokens.
PROPER = re.compile(r"\b([A-Z][a-zA-Z]{2,}(?:[ \t]+[A-Z][a-zA-Z]{2,})*)\b")
LOWER_WORD = re.compile(r"\b([a-z]{3,})\b")
COMMON_CAPS = {
    "The", "This", "That", "These", "Those", "There", "Then", "They", "Their",
    "And", "But", "For", "Not", "You", "Your", "Its", "Our", "Use", "Every",
    "Each", "When", "Where", "What", "Which", "While", "With", "Without",
    "Before", "After", "Also", "All", "Any", "One", "Two", "Three", "First",
    "MUST", "SHOULD", "MAY", "SHALL", "NOT",
    # Vague-attribution subjects. Pattern 5 tells the rewriter to delete these, so
    # flagging their removal as information loss would contradict the skill.
    "Experts", "Studies", "Research", "Many", "Some", "Most", "People", "Users",
    "Developers", "Teams", "Companies", "Others",
}


def norm_numbers(text: str) -> set:
    out = set()
    for m in NUMBER.finditer(text):
        tok = m.group(0).strip().rstrip(".,")
        if tok and not re.fullmatch(r"\d{1,2}", tok):  # skip list ordinals
            out.add(re.sub(r"\s+", "", tok))
    return out


def proper_nouns(text: str, vocabulary: set) -> set:
    """Names, places, and products.

    A capitalized token whose lowercase form appears as an ordinary word anywhere in
    either document is capitalization, not identity: 'Registration' in a Title Case
    heading is the same word as 'registration' in the body. That test does the work
    a positional heuristic cannot, since real names often open a sentence.
    """
    body = QUOTED.sub("", text)
    body = CODE_FENCE.sub("", body)
    body = INLINE_CODE.sub("", body)
    body = re.sub(r"(?m)^#{1,6} .*$", "", body)

    out = set()
    for m in PROPER.finditer(body):
        tok = m.group(1).strip()
        words = tok.split()
        if all(w in COMMON_CAPS or w.lower() in vocabulary for w in words):
            continue
        out.add(tok)
    return out


def vocabulary_of(*texts: str) -> set:
    return {w for t in texts for w in LOWER_WORD.findall(t)}


def check(original: str, rewrite: str, register: str) -> list[dict]:
    v: list[dict] = []

    def fail(rule, detail):
        v.append({"rule": rule, "detail": detail})

    # 1. Code fences must survive byte-identical.
    for block in CODE_FENCE.findall(original):
        if block not in rewrite:
            fail("code-fence-altered", block.splitlines()[0][:60])

    # 2. Inline code spans, hex literals, URLs must all still be present.
    for rx, name in ((INLINE_CODE, "inline-code"), (HEX, "hex-literal"), (URL, "url")):
        for tok in set(rx.findall(original)):
            if tok not in rewrite:
                fail(f"{name}-dropped", tok[:60])

    # 3. No invented numbers: every number in the rewrite must appear in the original.
    for num in norm_numbers(rewrite) - norm_numbers(original):
        fail("number-invented", num)

    # 3b. Proper nouns, both directions. A name in the rewrite that is absent from the
    # source is fabrication; a name in the source that is absent from the rewrite is
    # information loss. Neither is visible to a reader who lacks the original.
    vocab = vocabulary_of(original, rewrite)
    src_names, out_names = proper_nouns(original, vocab), proper_nouns(rewrite, vocab)
    for name in sorted(out_names - src_names):
        fail("proper-noun-invented", name)
    for name in sorted(src_names - out_names):
        fail("proper-noun-dropped", name)

    # 4. Quoted material must survive verbatim.
    for q in QUOTED.findall(original):
        if q not in rewrite:
            fail("quotation-altered", q[:60])

    # 5. Modality must not be strengthened (technical register only).
    if register == "technical":
        before = len(MODAL.findall(original))
        after = len(MODAL.findall(rewrite))
        if after < before:
            fail("modality-weakened", f"{before} modals before, {after} after")

    # 6. Structure preserved (technical register only).
    if register == "technical":
        h_before = [h[1] for h in HEADING.findall(original)]
        h_after = [h[1] for h in HEADING.findall(rewrite)]
        if len(h_before) != len(h_after):
            fail("heading-count-changed", f"{len(h_before)} -> {len(h_after)}")
        n_before = len(LIST_ITEM.findall(original))
        n_after = len(LIST_ITEM.findall(rewrite))
        if n_before != n_after:
            fail("list-item-count-changed", f"{n_before} -> {n_after}")

    # 7. Surface tells that should always be gone after a rewrite.
    for pat, name in (
        (r"[\u2014\u2013]", "em-dash-remains"),
        (r"I hope this helps|Let me know if you'd like", "chatbot-residue-remains"),
        (r"the future looks bright|Exciting times ahead", "uplift-ending-remains"),
        (r"[\U0001F300-\U0001FAFF]", "emoji-remains"),
    ):
        # Ignore matches inside quotations, which are inviolable.
        stripped = QUOTED.sub("", rewrite)
        if re.search(pat, stripped):
            fail(name, "")

    return v


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("original")
    ap.add_argument("rewrite")
    ap.add_argument("--register", choices=["technical", "narrative"], default="narrative")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        original = open(args.original, encoding="utf-8").read()
        rewrite = open(args.rewrite, encoding="utf-8").read()
    except OSError as exc:
        print(f"cannot read input: {exc}", file=sys.stderr)
        return 2

    violations = check(original, rewrite, args.register)

    if args.json:
        print(json.dumps({"register": args.register, "violations": violations}, indent=2))
        return 1 if violations else 0

    if not violations:
        print(f"all invariants hold ({args.register} register)")
        return 0
    print(f"{len(violations)} violation(s), {args.register} register:\n")
    for x in violations:
        print(f"  [{x['rule']}] {x['detail']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
