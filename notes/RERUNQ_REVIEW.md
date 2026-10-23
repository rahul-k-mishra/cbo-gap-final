# Review of the rerun queue before its first execution

## 2026-10-23, first pass

- Reviewed: scripts/rerunq.py (997 lines, md5
  46a5de46ca85c82b53d26aeda03c47bf), .github/workflows/rerun-queue.yml,
  notes/rerun_queue.json, and the launch subcommand added to
  scripts/kgrun.py (md5 7a92e52f485b6fbd21d3da184f611b91). Ledger K6.
- Written by the author of the code (Claude), reading it as someone else's
  code.
- Nothing has been executed in any mode. The only checks made:
  - a parse of rerunq.py and kgrun.py under the Python 3.8 grammar
    (ast.parse, feature_version (3, 8));
  - a walk of rerunq.py's syntax tree for names read but never defined.
    It reported only __file__;
  - a YAML parse of the workflow and a JSON parse of the state file;
  - every regular expression in read_runner was compared by eye with the
    print statement in rerun.py or in kgrun's runner that it is meant to
    match. They were not run against a real log.
- The pass is against the instruction of 2026-10-23, item by item, then
  two failure walks: the double-launch guard, and an invocation that dies
  mid-fetch.

### The instruction, item by item

| Item | Where | Result |
|---|---|---|
| Scheduled every 15 minutes, no polling loop | workflow on.schedule; tick returns after one action | ok |
| Queue order and plan | notes/rerun_queue.json queue; job_spec | ok; the arguments are the runbook's, character for character, with the new plan |
| State in a committed file; the state file is the lock | publish, rule L1 | ok (walk 1) |
| Cannot confirm the state: do nothing | tick: dirty tree exit 1; HEAD not main's tip exit 0; unreadable state exit 1 | ok |
| One action per invocation | tick dispatch; every branch returns after one publish of a transition | ok. A launch makes two commits (intent, then RUNNING): one action, two state writes, by design (L2) |
| Exit 0: next job | do_fetch | ok |
| Exit 5: commit, relaunch A + 1 with every earlier attempt folder | do_fetch; the relaunch is the NEXT tick's action | ok; cap 5 then HALT |
| 2, 3, 4 or no exit line: HALT, commit, reason in state, visible failure | do_fetch, do_halt, exit 3, workflow step "Disable" | ok |
| Smoke without D-SMOKE PASS halts before the set's shards | do_fetch smoke branch | ok; a HALT stops the whole queue |
| Halt on push failure | publish "failed"; exit 3 | ok after a Kaggle side effect. Before one (lock acquisition) a rejection with the state changed is "lock lost", exit 0, by the instruction's own "does nothing and exits" |
| Halt on manifest mismatch | verify_manifest, F1 | ok |
| Halt on kgrun exit other than 0 | launch, fetch: HALT. status: HALT (fixed in this pass, Q3) | ok |
| Same shard failing twice the same way | L5 | see "Interpretation" below |
| Secrets as KAGGLE_USERNAME, KAGGLE_KEY; written to ~/.kaggle/kaggle.json; never logged | workflow step 4 | ok: written by Python from the environment with umask 077, mode "x"; nothing echoes them; GitHub also masks secret values in logs |
| Commits with the built-in GITHUB_TOKEN | actions/checkout persists it; permissions contents: write | ok |

### Walk 1: can two invocations launch the same job?

A launch needs, in order: L3's check that Kaggle has no kernel of that
name; the LAUNCHING state pushed as a fast-forward of the commit the tick
read; then kgrun launch. Cases:

1. Two ticks at once. The workflow's concurrency group already serialises
   them. Without it, both read commit c1, at most one fast-forward from c1
   is accepted, and the loser finds main's state file different from the
   bytes it read and exits before kgrun runs. There is no ABA case: every
   transition appends to the history, so a later state's bytes never
   equal an earlier one's.
2. A tick dies after the LAUNCHING push and before kgrun pushed the
   kernel. Main reads LAUNCHING. The next tick asks Kaggle: absent, so it
   halts. It does not relaunch, because "absent" cannot tell "never
   pushed" from "pushed and not yet visible".
3. A tick dies after kgrun pushed the kernel and before RUNNING was
   pushed. The next tick finds LAUNCHING, Kaggle reports a status, and the
   kernel is adopted. No second push. The kgrun launch log of the dead
   tick is lost, and the adoption is recorded in the history.
4. A re-run of an old failed workflow run from the GitHub UI. The checkout
   is ref main, not the old run's commit, so it reads the current state.
5. A hand launch of a queue job name from the laptop. If it comes before
   the queue's launch, L3 halts the queue. If it comes after, it pushes a
   second version of the same kernel, and nothing in the queue can
   prevent that. CLAUDE.md rule 22 forbids hand launches while the
   workflow is enabled.
6. kgrun launch exits nonzero. HALT, with the reason "whether the kernel
   was pushed is not known". The state keeps the job name. Release
   "start" is refused for it, so a relaunch must take a new attempt
   number, after a hand check.

Residual risk, as first reviewed: case 2 or 6, if Rahul releases
next-attempt without checking and a push of the earlier name did land, two
kernels run the same shard. Closed in the second pass (Q8): next-attempt is
refused without a kernel check recorded since the halt.

### Walk 2: an invocation dies mid-fetch

The fetched folder, the fetch log, the driver log and the next state go
into one commit and one push. Before that push lands, nothing of the fetch
exists on main, and main still reads RUNNING.

1. Death before the push (killed, the 90-minute timeout, a runner
   failure). The next tick polls, sees the kernel finished, and fetches
   again into a new runs/<job>-kaggle-<stamp>. The first copy died with
   the runner. One folder reaches the repository. This relies on Kaggle
   keeping a finished kernel's output downloadable. A separate later
   fetch has worked before (the calprec2 -fetch logs). How long Kaggle
   keeps the output is not recorded in this repository.
2. The push lands, but the client reports failure (reply lost). This was
   classified as "lock lost" before this pass, with a false error message.
   It is now recognised: main's tip is this commit, so the push counts as
   accepted (Q1).
3. The push is rejected because Rahul pushed some other file. The state
   file on main is unchanged, so the commit is cherry-picked onto main's
   tip and pushed again. This happens at most three times.
4. The push fails for good. Exit 3 and the workflow disables itself. The
   rescue artifact holds the folder. Main still reads RUNNING, so after
   "release repoll" (or re-enabling, if the state was never HALTED) the
   next tick fetches again. The rescue copy must never be committed by
   hand. Doing so would put the same rows in two folders, which
   rerun_analysis.py refuses (exit 2), and L3 would then halt the
   re-fetch. The rule is written in the runbook, section 8, and in the
   error message.
5. The download is cut short but kgrun exits 0. The manifest is written
   over whatever arrived, so it verifies; it proves nothing about
   completeness. Before this pass that case was not caught. Now F2
   compares the rows ending "ok" in rerun_real.csv with the runner's
   "completed C" (Q4). A truncated runner log loses its exit line, and R2
   halts.

### Fixed in this pass

- Q1. A push reported as failed whose commit is nevertheless main's tip
  was treated as a lost lock. It is now accepted (walk 2, case 2).
- Q2. The fetch after an accepted push was fatal. A network error there
  would have left main at LAUNCHING with nothing launched. It is no longer
  fatal. kgrun's own git guard is still the check that HEAD is pushed.
- Q3. A nonzero exit of kgrun status was an anomaly (one free retry). The
  instruction says a kgrun exit other than 0 halts, so it now halts at
  once. kgrun status exits 0 whatever the kaggle CLI reports, so this is a
  crash and not a network error.
- Q4. F2, the completeness check (walk 2, case 5).
- Q5. An existing logs/kgrun-<job>.log made kgrun's console log fail to
  open (mode "x"). That happened AFTER the LAUNCHING push, so it left an
  interrupted launch with nothing pushed. It is now checked before the
  intent, with L3.
- Q6. Resume folders after exit 5 now include only attempt folders that
  hold a rerun_real.csv, as in the runbook. A folder without one would
  make rerun.py refuse the resume.
- Q7. The tick now prints its parameters at the head: plan and hash,
  timing folders, pinned versions and hashes, user, workers, caps.

### Interpretation the instruction leaves open

- "The same shard failing twice the same way." Exits 2, 3 and 4 and a
  death already halt the first time, so "twice" can only apply to what
  does not halt at once. Two cases:
  - an observation the tick cannot classify (status UNKNOWN, or ABSENT
    for a job the state says is RUNNING): recorded the first time, halted
    the second time for the same job and kind (L5);
  - a G-STOP with zero completed tasks halts the first time, because a
    second identical attempt would repeat it.
- Exit 4 and a death with rows halt, as instructed. Runbook section 5
  resumes them. Release next-attempt does exactly that, after Rahul has
  read the folder.

### Left, noted, not fixed

- L4's "absent" test assumes the kaggle CLI's reply for an unknown kernel
  contains "404". I do not know the exact text: no log in the repository
  holds one. If it does not contain "404", the first launch records an
  anomaly and the second tick halts. That fails safe, but it stops at the
  first job. Setup step 5 shows the text by hand before anything is
  enabled.
- If the account's GITHUB_TOKEN may not disable workflows, a halted queue
  keeps ticking, and every tick fails visibly (exit 3) and does nothing.
  The first tick after setup tests this, because the state starts HALTED.
- Any transient failure of a setup step (checkout, pip, credentials)
  fails the run and disables the workflow. The state is untouched; re-enable.
- GitHub's schedule is best effort; ticks can be late or skipped. That
  affects timing, not correctness.
- Actions minutes: this is a private repository, and every tick is billed
  at least one minute. I do not know this account's allowance; it is shown
  under Settings, Billing.
- The history in the state file grows without bound, by one entry per
  transition.
- Scheduled-workflow failure emails go to the user who last changed the
  cron line, that is, whoever pushes the workflow file.

### Decided by Rahul (2026-10-23)

- The CLAUDE.md amendments (rules 3, 14 and 21 each gain one exception;
  rule 22 is new): approved.
- Edit(/notes/rerun_queue.json) added to the deny list in
  .claude/settings.json at his request. It stops Claude's file-editing
  tools only; a shell command that writes the file is not covered by
  that entry. Rule 22 forbids it.

## 2026-10-23, second pass: Q8, the kernel check (rule K1)

- Asked by Rahul: the walk 1 residual risk must not depend on memory.
- Reviewed after the change: scripts/rerunq.py (1103 lines, md5
  0e65649efa6c60a33be80d307f5ba933).
- Q8. "release --mode next-attempt" now refuses unless the state holds a
  kernel check for the halted job made since the halt. The check comes
  from "rerunq.py check" (kgrun status, run by Rahul on the laptop, result
  recorded) or from --checked-by-hand STATUS on the release (recorded in
  the history with his note).
- "Since the halt" holds by an invariant that validate() enforces on every
  write: kernel_check is null in every status but HALTED. Every halt,
  automatic or by hand, sets it null, and so does every release. Only
  check and the flag set it, and only while HALTED. A check made before
  one halt therefore cannot survive into the next.
- Accepted: COMPLETE, ERROR or CANCEL_ACKNOWLEDGED; ABSENT only when seen
  30 minutes or more after the halt. That keeps an ABSENT read straight
  after an interrupted launch from passing. The 30 minutes is a design
  choice; I do not know Kaggle's actual delay between a push and the
  kernel becoming visible. Refused: QUEUED, RUNNING, NEW_SCRIPT,
  CANCEL_REQUESTED (the message says to use repoll), UNKNOWN, no check,
  or a check for another job name.
- The job checked is the recorded one; when none is recorded (a halt
  before the intent, such as L3's "kernel already exists"), it is the
  current item and attempt's name, which is the kernel that halt found.
- Not covered: next-item. It moves to a different shard, so a kernel left
  running under the old item cannot write rows of the new one. The check
  rests on what Rahul states with --checked-by-hand; a false statement is
  recorded, not prevented.
- Static checks only, as before: Python 3.8 grammar parse and JSON parse.
  Nothing executed.
