# Test prompts

Copy-paste prompts for running the eval cases in a fresh session. Each is phrased as a real request, because a prompt that says "run eval case 1" tests compliance rather than the skill.

## Rules

**One case per session.** Once a session has produced one rewrite, the next request in the same session inherits both the context and any correction you made. That is not a fresh trigger.

**Do not let the session read `evals/`.** `evals.json` and `evals/README.md` list every assertion. An agent that reads them will satisfy them without the skill doing any work, and the run tells you nothing. If you are running in Claude Code with the repo open, say so explicitly in the prompt: *do not open anything under evals/*.

**Do not say the word "test."** Framing a request as a test changes the output. Ask for what a user would ask for.

**Grade afterward, outside the session.** Save the output, then run `check.py` yourself.

---

## Case 1: technical spec

Paste the contents of `fixtures/01-spec-excerpt.md` under this line:

> Clean up the prose in this spec section. It reads like it was written by a model.

Grade: `python check.py fixtures/01-spec-excerpt.md out1.md --register technical`

Then read for the thing the checker cannot see: did the three parameter bullets survive as a list? Flattening them into a paragraph passes every mechanical assertion and is still wrong.

---

## Case 2: launch post

Paste the contents of `fixtures/02-launch-post.md` under this line:

> Rewrite this launch post so it sounds like a person wrote it.

Grade: `python check.py fixtures/02-launch-post.md out2.md --register narrative`

Then read for: did it restructure, or only swap words? A rewrite with the same six paragraphs in the same order, each one sentence shorter, has failed even with zero mechanical violations.

---

## Case 3: ADR

Paste the contents of `fixtures/03-adr-rejected-options.md` under this line:

> Tidy up the writing in this ADR.

Grade: `python check.py fixtures/03-adr-rejected-options.md out3.md --register technical`

Then read for: are the sharding and priority-gas-auction options still there with their reasons? Deleting them is the failure this case exists to catch, and the checker will not see it.

---

## Case 4: thin source

Paste the contents of `fixtures/04-thin-post.md` under this line:

> Make this conference recap more engaging.

Grade: `python check.py fixtures/04-thin-post.md out4.md --register narrative`

Then read for invented proper nouns. `check.py` catches fabricated numbers and nothing else, so a made-up conference name, city, venue, speaker, or talk title passes clean. This is the highest-severity case and the one with the weakest mechanical coverage. The correct output improves the rhythm and tells you the post needs detail only you have.

---

## Case 5: voice sample

Paste the contents of `fixtures/05-voice-sample.md` under this line:

> Rewrite the draft at the bottom so it matches how I write in the sample above it.

Grade: read it. `check.py` will report `em-dash-remains` and that is the correct outcome here, because the author's sample outranks the pattern list. A rewrite with no em dashes and no fragments has failed by obeying the defaults.

---

## Case 6: negative trigger, internal research

> I'm evaluating a company before reaching out to them. Read through this interview transcript and write me a detailed brief on their product, platform capabilities, and roadmap so I can decide whether there's a fit.

Attach any founder interview transcript. Grade: the skill must not fire. The output should be a dense brief with headings, bolded labels, and tables intact. If it comes back in flowing prose with the structure stripped out, the audience rule in the description is not working.

---

## Case 7: negative trigger, code task

> Refactor this to use a bounded channel instead of an unbounded one, and explain the backpressure trade-off:
>
> ```rust
> async fn spawn_workers(rx: UnboundedReceiver<Job>) -> Result<(), Error> {
>     while let Some(job) = rx.recv().await {
>         tokio::spawn(async move { job.run().await });
>     }
>     Ok(())
> }
> ```

Grade: the skill must not fire. The explanation is technical exposition, not a document with an audience. If the skill loads here it will over-trigger on most engineering work.

---

## Case 8: mixed register

> Here's the README for my Rust crate. The intro explains why I built it, then there's an install section and a config table. Can you clean up the writing?

Attach a real README with those three parts. Grade: read it. The intro should get narrative treatment, everything from the install heading down should keep its structure, and the config table should be untouched. A document rewritten uniformly in either direction is a classification failure.

---

## Recording results

For each case, note: mechanical violations from `check.py`, the judgment failure if any, and whether the skill fired at all. A case can pass every assertion and still fail; that is why every case above has a "then read for" line.
