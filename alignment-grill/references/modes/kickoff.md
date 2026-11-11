# Kickoff

Two roles. The **manager** sets up GitHub, runs the compare and writes the Vision. Every
**member** (the manager too) answers the blind questions on their own machine. If the pinned
issue already exists, this person is joining: go to step 3.

Every step ends on something you can see on GitHub or on disk.

## 1. Settle the frame (manager)

Grill the manager on:
- the context: one of the profiles in `references/profiles/`. Read the chosen file now;
- the people: GitHub logins, and who is manager;
- the grouping field and its values, with the profile's default as your recommendation;
- the lease length, the profile's default recommended;
- stack defaults: Python unless the team says otherwise (with uv and pytest as the suggestion);
- the referee action to use: look for an `alignment-referee` repo with `gh repo list <owner> --json name`; if none is found, ask for its `owner/repo`.

Done when each of these has an answer.

## 2. Set up GitHub (manager)

Show the manager the full list of what will be created, then do it:

1. Labels, each with `gh label create <name> --force --color <hex> --description <text>`: `alignment`, `task`, `decision`, `review`, `proposed`, `decided`, `superseded`, `dropped`, `working`, `stuck`, `recheck`, `logged-after`.
2. The pinned issue from the template in `references/board.md`, with Goal, Done when, Risks, Vision and Glossary marked `pending kickoff` and every field filled. Create it with `gh issue create`, then `gh issue pin`.
3. The Project. Needs the `project` scope: if `gh auth status` lacks it, have the person run `! gh auth refresh -s project`. Then:
   - `gh project create --owner <owner> --title "<repo> board" --format json`
   - `gh project link <number> --owner <owner> --repo <owner>/<repo>`
   - fields with `gh project field-create <number> --owner <owner> --name <name> --data-type <type>`:
     `Task status` (SINGLE_SELECT, options `To do,Working on it,Stuck,Done`), `Owner`, `Stage`, `Lease`, `Waits on`, `Last updated`, `Criterion`, `Scope`, `Agent / model` (TEXT), `Start` and `Target` (DATE), the grouping field (SINGLE_SELECT with its values), and the profile's extra fields.
   - Put the Project URL in the pinned issue's **Project:** field.
   - The CLI cannot make views. Ask the manager to add two in the browser: a Board grouped by `Task status`, and a Roadmap using `Start` and `Target`. The default Table view stays.
4. The referee token. The workflow's own token can't edit a Project owned by a user. The manager creates a token in GitHub settings that can read and write this repo's issues and edit the Project (a fine-grained token if it offers Projects for their account, otherwise a classic token with `repo` and `project`), then runs `! gh secret set ALIGNMENT_TOKEN`. Skipping it is allowed: the referee then assigns and labels but leaves Project fields alone, and says so on the pinned issue.
5. In the code repo, on a branch the manager approves, with a commit they approve:
   - `.github/workflows/alignment.yml`:
     ```yaml
     name: alignment referee
     on:
       issue_comment: {types: [created]}
       push:
       schedule: [{cron: "17 * * * *"}]
       workflow_dispatch:
     concurrency: {group: alignment-referee, cancel-in-progress: false}
     permissions: {issues: write, contents: read}
     jobs:
       referee:
         runs-on: ubuntu-latest
         steps:
           - uses: <owner>/alignment-referee@v1
             with:
               project-token: ${{ secrets.ALIGNMENT_TOKEN }}
     ```
   - one line in `AGENTS.md` (create it if missing), and the same line in `CLAUDE.md` unless it already imports `AGENTS.md`:
     `Alignment for this repo lives in GitHub issue #<pinned>. Read its "For agents" section before you claim work and before you mark it done, and follow it.`

   Nothing else goes in the repo.

Done when the pinned issue is pinned with every field filled, the Project has its fields, and the workflow file and the AGENTS.md line are pushed. Check that the workflow ran: `gh run list --workflow alignment.yml --limit 1`.

## 3. Blind answers (every member)

Grill this person alone, without showing anyone else's answers:
- the goal, in one paragraph;
- what "done" means, as checkable criteria;
- the top 3 risks;
- the profile's extra kickoff questions;
- terms they expect the team to use, with their meaning.

Save the answers to `~/.alignment-grill/<owner>__<repo>/kickoff.md`, outside the repo. Then post `/ready [Person / Agent]` on the pinned issue.

Done when the file exists and the referee gave `/ready` a thumbs up.

## 4. Reveal (every member)

The referee comments "Reveal" on the pinned issue once every person in **People:** is ready. Check with `gh issue view <pinned> --comments`. Before the reveal, tell the person who is still missing and stop; they rerun this step later.

After the reveal, post the saved answers as one comment on the pinned issue, headed `Kickoff answers: <Person>`, then delete the local file.

Done when the comment is posted and the local file is gone.

## 5. Compare (manager)

Once every person posted answers, read them side by side and sort each point:
- **Agreed**: the same meaning in every answer. It goes into Goal, Done when, Risks or Glossary.
- **Different**: open a `decision` issue for each, with the people involved and your recommended option (see `decide.md`).
- **Terms**: a word used with two meanings becomes a glossary entry and, if the meaning matters, a decision.

Show the manager the draft pinned sections and the list of new decisions before writing them.

Done when no point is unsorted, the pinned sections are written, and every difference has a decision issue.

## 6. Vision (manager)

Grill the manager on a ranked list: what matters most when two good things conflict (for example: a working demo over coverage, correctness over speed). Five lines at most, each a choice with a loser. Write it into the pinned issue.

Done when the Vision has at least three ranked lines, each naming what it wins over.

## Next phase

When the goal was met and the team wants to go further:
1. Create a milestone for the finished phase: `gh api repos/<owner>/<repo>/milestones -f title="<phase name>"`, and put the closed tasks of that phase in it with `gh issue edit N --milestone`.
2. Rerun steps 3 to 6 for goal, done criteria, risks and Vision only. People, glossary and decisions carry over.

When the goal was misunderstood instead, use `decide.md` with **Goal change:** yes.
