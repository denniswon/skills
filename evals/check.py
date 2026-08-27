#!/usr/bin/env python3
"""Check a humanizer rewrite against the invariants the skill promises.

Compares the original and the rewrite. Most of what the skill claims is
mechanically verifiable: identifiers survive, numbers are not invented,
structure holds in technical register, modality is not strengthened.

Usage:
    python check.py ORIGINAL REWRITE [--register technical|narrative] [--json]

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


def norm_numbers(text: str) -> set:
    out = set()
    for m in NUMBER.finditer(text):
        tok = m.group(0).strip().rstrip(".,")
        if tok and not re.fullmatch(r"\d{1,2}", tok):  # skip list ordinals
            out.add(re.sub(r"\s+", "", tok))
    return out


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
