# Decide

Turn a question into a `decision` issue the people involved vote on. Formats are in
`references/board.md`.

## 1. Frame it

Grill the person who raised it until you have:
- one question;
- the options, each with its cost (time, risk, what it rules out);
- the people involved: everyone whose task, files or promise it touches. For a goal change, everyone in **People:**;
- a deadline: the profile's default unless they set one;
- a recommendation with its reason.

Facts go in before the question reaches people: search the repo, the closed decisions and the commit history yourself, and put numbers and file references in the options.

Done when every field has an answer the person agreed to.

## 2. Look for an existing decision

`gh issue list --label decision --state all --search "<key words>"`. If one already covers it, the new issue supersedes it (**Supersedes:** D-n) or the question is already answered: show the person and stop.

Done when you have searched and named the related decisions, or found none.

## 3. Post it

Create the issue with labels `decision` and `proposed`, mention the people, and add it to the Project. If an agent asked the question for its own task, it marks the task `/stuck D-n` until the vote.

Done when the issue exists and the people are mentioned in it.

## Variants

- **Verbal agreement.** Someone says "we agreed X" in a call. Write it as a decision with **Source:** verbal (names), the agreement as the only option, and the named people as **People:**. It counts as decided only once each named person posts `/vote yes`. Until then agents treat it as proposed.
- **Goal change** (the goal was misunderstood). **Goal change:** yes, everyone votes. Once decided, the referee marks every open task `recheck`; each owner answers `/keep` or `/release`, the manager answers for unowned ones. Update the pinned Goal and Done when to match.
- **Replacing a decision.** **Supersedes:** D-n. When the new one is decided, the referee marks the old one superseded.
