# Skill Build Write-Up — SOP Template

Use this template every time a new skill from *Behind the Chef AI* is ready to publish. It has three parts. Don't skip the middle one — the build journey (problems hit, how they got solved, what broke next) is the actual interesting part for an audience watching a human learn to work with AI. A skill that "just worked first try" doesn't need this document; the value here is showing the real process, mistakes included.

Copy this file into the skill's folder as `WRITEUP.md` and fill in each section for real, in your own words, from what actually happened — don't invent a cleaner story than what really occurred.

---

## 1. The Need

*Why did this skill get built? What problem existed before it, and why was it worth solving?*

- What were you trying to do when you realized this was missing?
- What would you have had to do manually/repeatedly without it?
- Was there a specific moment or conversation that triggered building it? (e.g. an idea proposed, rejected, and replaced with a better one)

## 2. The Build Journey

*Chronological. Problem → attempted fix → result. If a fix caused a NEW problem, log that too — that chain is the actual story.*

Write this as a running log, roughly in the order things happened:

1. **First attempt / first assumption** — what was tried first, and why.
2. **What broke, or what was missing** — the specific failure, ideally with the actual error or symptom, not a vague summary.
3. **How it was diagnosed** — did you guess and check, look at the actual data, ask a clarifying question? Show the reasoning, not just the fix.
4. **The fix** — what changed, and why that specific fix (not just "fixed it").
5. **Repeat for every subsequent problem**, including ones that only showed up *because* of an earlier fix (e.g. "fixing the transform bug then exposed a totally separate missing-audio problem").

Good build-journey entries name the actual thing that went wrong (a specific bug, a wrong assumption, a missing dependency) rather than "we had some issues and worked through them."

## 3. Final Write-Up

*What the finished skill actually does, why it matters, and what it's ready for.*

- **Purpose** — one or two sentences, in plain language, no jargon. What does this skill do for someone who's never seen it?
- **Why it needed a human + AI working together** — what did the human catch/decide that the AI alone would have missed, and vice versa?
- **End result** — what's actually true now that wasn't true before this skill existed? Be concrete (a real example, a real number, a real before/after).
- **Known limitations** — be honest about what's still rough or untested. This isn't a marketing document; overclaiming here erodes trust with an audience that's watching for the real process.

---

## Then produce two outputs from this document:

1. **The detailed write-up** (this filled-out document) — goes in the skill's folder, linked from the main repo README, is the actual downloadable/GitHub-visible content.
2. **A short SM caption** distilled from it — 3-5 sentences max, casual tone, states the problem→fix in plain language, ends with a pointer to the full write-up/download. Save as `social/CAPTION.md` in the skill's folder.

## 4. Test Period — Don't Let "Known Limitations" Sit Forever

A skill can (and often should) get published with honest "known limitations" still open — that's better than waiting for perfect confidence before anyone gets to see the real process. But an open limitation isn't the end of the story. Once the skill actually gets used for real (not just smoke-tested), come back and add a **Field Notes** section to the bottom of `WRITEUP.md`:

```
## Field Notes (added after real use)

- Date / context of real use:
- Which "known limitations" from the original write-up held up, and which didn't:
- Anything new that broke, that the original build didn't anticipate:
```

This isn't a gate that blocks publishing — it's a commitment that open questions get closed out later instead of quietly forgotten. Same discipline already used elsewhere in this project's `[ ] untested → [x] confirmed` tracking.
