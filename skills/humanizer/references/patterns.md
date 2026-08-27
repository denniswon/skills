# Pattern catalogue

35 patterns, grouped. Each entry gives the tell, a rewrite, and the register it applies to.

**Register column:** `both` — applies everywhere. `narrative` — applies to posts and essays; leave alone in reference docs. `technical` — matters most in specs and READMEs.

Contents:
- [Content patterns (1–6)](#content-patterns)
- [Language and grammar (7–13)](#language-and-grammar)
- [Style and formatting (14–19, 26–35)](#style-and-formatting)
- [Chatbot residue (20–22)](#chatbot-residue)
- [Filler and hedging (23–25)](#filler-and-hedging)
- [Safeguards](#safeguards)

---

## Content patterns

**1. Inflated importance — both.** The model reaches for historical weight it can't support.
Before: "The release marks a pivotal moment in the evolution of account abstraction."
After: "The release added paymaster support in v0.7."

**2. Name-dropping as evidence — both.** Listing institutions, publications, or well-known people to borrow credibility.
Before: "The approach has drawn interest from researchers at several leading labs."
After: Cite the specific paper, or cut it.

**3. Shallow participial analysis — both.** Trailing "-ing" clauses that assert significance the source never established.
Before: "...reducing calldata costs, highlighting the protocol's commitment to efficiency."
After: "...reducing calldata costs by about 40%." Keep the measured part, drop the editorial.

**4. Sales language — both.** Travel-brochure adjectives.
Before: "a seamless, powerful developer experience nestled in a rich ecosystem"
After: Describe what the tool does.

**5. Vague attribution — both.** "Experts believe", "many argue", "it is widely considered".
After: Name the source or delete the claim. In an audit or postmortem this is a correctness issue, not a style one.

**6. Challenges-then-outlook formula — both.** "Despite ongoing challenges around X, the project continues to grow."
After: State the challenge, state the status. Skip the arc.

---

## Language and grammar

**7. Overused vocabulary — both.** delve, testament, landscape, showcase, tapestry, realm, underscore, pivotal, crucial, robust (as filler praise), seamless, leverage (as a verb), navigate (figurative), harness, unlock, elevate, foster, myriad, plethora, vibrant, notably, moreover, furthermore, in today's ..., ever-evolving, at the forefront.
Judgment required in technical text: "robust" is legitimate in "robust against reorgs", "gate" is legitimate in "feature gate" and "CI gate". Flag the figurative uses, keep the terms of art.

**8. Avoiding "is" and "has" — both.** serves as, stands as, boasts, features, represents, functions as.
Before: "The registry serves as the canonical source of operator metadata."
After: "The registry is the canonical source of operator metadata."

**9. "Not just X, but Y" and clipped negations — both.** Also: "It's not about X. It's about Y." and trailing "No config. No setup. No surprises."
After: State the claim once, in one sentence.

**10. Forced tricolons — both.** Three parallel items because three feels complete.
Before: "faster, cheaper, and more secure"
After: Use the number of items you can support. Two is fine. One is fine.

**11. Elegant variation and repeated openings — both.** Cycling synonyms for one referent ("the sequencer... the ordering service... the node"), or three consecutive sentences opening the same way.
After: Pick one name and keep it — mandatory in technical register, where a synonym reads as a different component. For repeated openings, merge the sentences. Safeguard: deliberate anaphora is a rhetorical device; leave it if the repetition is obviously doing work.

**12. False "from X to Y" ranges — both.** "everything from mempool design to MEV"
After: List the topics. A range implies a spectrum that usually doesn't exist.

**13. Agentless passive — technical.** "No configuration file is needed." "It was determined that..."
After: Name the actor when it matters — who determined it, what needs no config. Passive is correct when the actor is genuinely irrelevant or unknown; this is not a blanket ban.

---

## Style and formatting

**14. Em and en dashes — both.** The strongest single tell. Replace with a period, comma, colon, or parentheses; often the clause just merges.
Before: "The prover is fast — much faster than the reference implementation — but memory-hungry."
After: "The prover is much faster than the reference implementation, and memory-hungry."
Safeguards: never touch dashes inside quotations, code, or a supplied writing sample's style. Ranges written with en dashes (2019–2024) are typography, not a tell.

**15. Bold scattered through prose — both.** Bolding key nouns in a paragraph so the reader "gets it."
After: Remove. Bold is for headings and genuine UI labels.

**16. Bold-lead list items — narrative.** `- **Latency:** Latency improved by 30%.`
In a blog post, convert to prose. In a README options list, config reference, or comparison table this is the correct format — leave it. This pattern is the most common false positive in technical documents.

**17. Title Case Headings — both.** "Strategic Considerations And Trade-offs" → "Strategic considerations and trade-offs". Follow the surrounding document if it already has a consistent convention.

**18. Emoji — both.** Remove, unless the target is a platform where the author clearly uses them and the sample shows it.

**19. Curly quotes and typographic ellipsis — both.** Convert to straight quotes and three periods. In technical files this also prevents copy-paste breakage.

**26. Hyphen stacking — both.** "cross-functional, data-driven, developer-first tooling"
After: Keep the hyphens grammar requires, cut the adjective pile.

**27. Manufactured depth — both.** "At its core, this is really about trust." "The deeper truth is..."
After: State the specific claim.

**28. Announced structure — narrative.** "Let's dive in." "Here's the thing." "One thing that bit me:"
After: Start with the content. In technical register, an explicit roadmap sentence ("This document covers X, then Y") is genuinely useful — keep it.

**29. Heading echoed in the first line below it — both.**
Before: `## Performance` / "When it comes to performance, performance matters."
After: Let the heading do that work; start with the substance.

**30. Describing the old version — both.** "This function was added to replace the legacy handler."
After: Describe current behavior. Migration notes belong in a changelog section, not in reference prose. Exception: an ADR or postmortem is *about* history, so the prior state is the subject.

**31. Punchline fragments — narrative.** "It had no preference. No prior. No nostalgia."
After: Natural sentence lengths and a specific claim.

**32. Aphorisms — both.** "Simplicity is the ultimate form of security."
After: State the concrete claim, or cut.

**33. Fake candor — narrative.** "Honestly? It depends." "Look, I'll be blunt:"
After: Give the answer.

**34. Answering unraised objections — both.** "This isn't primarily about block size..."
After: Cut, unless someone actually raised it — then name them and keep it.

**35. Rejecting invented alternatives — both.** "A tempting approach would be to shard the mempool, but..."
After: Cut the straw option. Keep alternatives that were genuinely considered — in an ADR, the rejected-options section is the point, and this pattern does not license deleting it.

---

## Chatbot residue

**20. Assistant framing left in the text — both.** "I hope this helps!" "Let me know if you'd like me to expand on any section." "Certainly! Here's the..." Remove.

**21. Knowledge-limit disclaimers — both.** "While specific details are limited in available sources..." "As of my last update..."
After: State what's known, or drop the claim.

**22. Sycophancy — both.** "Great question!" "You're absolutely right to focus on this."

---

## Filler and hedging

**23. Filler phrases — both.** "in order to" → "to"; "due to the fact that" → "because"; "it is important to note that" → cut; "a wide range of" → say how many; "plays a crucial role in" → say what it does.

**24. Stacked qualifiers — both.** "could potentially possibly" → "may".
Critical safeguard: stack-cutting reduces *duplicate* hedges. It never removes the last remaining modal in technical text. "may reorder" stays "may reorder".

**25. Uplift endings — both.** "The future looks bright." "Exciting times ahead."
After: End on a fact, a decision, a date, or an open question.

---

## Safeguards

These override every pattern above:

1. **No invented facts.** Names, numbers, dates, quotes, citations, benchmarks come from the source or the user. Ask rather than fabricate.
2. **Quotations are inviolable.** Every pattern stops at a quotation mark.
3. **Code and identifiers are inviolable.** Including inside link targets and inline spans.
4. **A supplied writing sample outranks the defaults**, including patterns 14, 16, 18, and 31 — some people really do write in fragments and em dashes.
5. **Normative modality is content**, not hedging.
6. **Terms of art are not overused words.** Check whether a flagged word is functioning technically before removing it.

---

Taxonomy adapted from Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup) and the `blader/humanizer` skill (MIT); register splits, safeguards, and technical examples added here.
