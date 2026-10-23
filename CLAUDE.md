# CBO-GAP — standing rules for every Claude Code session

This repository holds the revision of "Finite-ensemble observability of the
mean-field convergence rate in consensus-based optimization" (Journal of Global
Optimization, JOGO-D-26-00563, rejected 2026 with an invitation to resubmit as a
new manuscript). Sole author: Rahul Kumar Mishra, Independent Researcher,
Ranchi. Read this file in full before touching anything. Read
notes/DEFECT_LEDGER.md before touching the manuscript or proposing an
experiment. Everything in this file is non-negotiable.

## Layout

    CLAUDE.md                      this file
    README.md                      what the repository is and how to run anything
    .claude/settings.json          allow git add, commit, push; deny edits under
                                   zenodo-v1, round1-zip, runs/ and notes/rerun_queue.json
                                   (plus any Bash command naming that file;
                                   a heredoc body is not matched by the
                                   rule, so a PreToolUse hook,
                                   .claude/hooks/deny-queue-state.py,
                                   checks the full text), every rm
                                   form, chmod, force
                                   push, history rewrite, and every kaggle command;
                                   ask on mv, cp, unzip, tar
    .gitattributes                 "* -text": git never rewrites line endings; the
                                   archived CSVs are CRLF and their hashes must survive
    ENVIRONMENT.md                 Python, NumPy, platform, CPU, RAM of every machine
                                   this project runs on, pasted from console output
    requirements.lock              pip freeze of .venv on the Linux box; the
                                   determinism check is run against this environment
    zenodo-v1/                     the 68 files deposited at DOI 10.5281/zenodo.22068685,
                                   byte-identical, chmod a-w, NEVER written to
    zenodo-v1.sha256               per-file manifest computed on Rahul's machine
    zenodo-v1-manifest-claude.sha256   the same manifest computed on the zip he uploaded
    round1-zip/                    a round-1 working directory from Rahul's earlier
                                   laptop (ledger N34): a second read-only source,
                                   chmod a-w, NEVER written to, under rule 1 exactly
                                   as zenodo-v1
    round1-zip.sha256              its per-file manifest (143 files, paths relative
                                   to round1-zip/)
    referee/                       JOGO_report.pdf and the submitted PDF JOGO-D-26-00563.pdf
    notes/DEFECT_LEDGER.md         every known defect, its fix type, its status, the
                                   commit that closed it
    manuscript/                    round-2 LaTeX source; starts as zenodo-v1/sn-article.tex
                                   plus the DOI sentence, which reproduces the submitted text
    .github/workflows/rerun-queue.yml   the rerun queue's tick, dispatched every
                                   15 minutes from cron-job.org (rule 22)
    notes/rerun_queue.json         the rerun queue's state; written only by
                                   scripts/rerunq.py (rule 22)
    scripts/                       round-2 scripts only; they IMPORT dynamics from
                                   zenodo-v1 and never retype them
    runs/<run-id>/                 one folder per executed run: the output files the
                                   script wrote (CSVs) and sha256.txt, the manifest
                                   written by scripts/manifest.py (or by kgrun.py fetch
                                   for a Kaggle run); never modified after sha256.txt
                                   is written
    logs/                          console logs: of analysis-only runs, and of runs
                                   whose output folder is under runs/ (the console log
                                   names that folder in its header)
    .venv/                         local virtual environment, not tracked

## Hard rules

1. zenodo-v1 is the deposited archive. Never create, modify, delete, move or
   overwrite anything in it. It is chmod a-w and denied in .claude/settings.json;
   those are backstops, not permission. Scripts may read from it and import
   modules from it; nothing else. round1-zip/ is under this rule exactly as
   zenodo-v1 is (added 2026-10-15, Rahul's decision).

2. Never assume or compute a number independently. Every number that enters
   the manuscript, the ledger, a table, a caption or a reply must come from the
   console output of a script Rahul ran on his machine and stored under runs/
   or logs/. If a number is needed: write the script, give the command, stop,
   wait for the pasted output. Filling a gap with a plausible value is the one
   unforgivable failure in this project.

3. No output file may overwrite an existing file. Scripts open every output
   with mode "x" and write into runs/<run-id>/ where <run-id> is new (date,
   script name, short description). The Table 7 incident (a Part M result file
   destroyed by a later Part D run that opened the same filename in write mode,
   then wrongly declared fabricated) and the Part D near-miss both came from
   this. Analysis scripts that write nothing say so in their docstring.
   One exception (rule 22): scripts/rerunq.py rewrites notes/rerun_queue.json
   in place, because that file is the queue's state and its lock.

4. Never retype dynamics. Round-2 scripts import one_realisation,
   beta_on_ensemble or solve_beta, fit_slope, sigma_of, draw_initial and the
   objective functions from the archived scripts in zenodo-v1 (sys.path
   insertion), exactly as rmapj.py and perjcal.py do. The exactcal squared-norm
   bug (np.linalg.norm where every other script uses np.sum((...)**2, axis=1),
   halving every fitted exponent and costing a 3.75-hour run) came from
   reimplementing by hand. The coupled error is the SQUARED distance,
   accumulated as a running per-particle maximum over time steps.

5. Every script, without exception:
   - multiprocessing.Pool, --workers flag, parallel by default;
   - prints at the head of the run: every parameter, every seed or the seed
     table rule, Python version, NumPy version, platform, worker count;
   - states in its docstring, before first execution, every pre-specified
     criterion, threshold, sign convention and decision rule, each with a
     worked numerical example; the nine analysis-design errors of this project
     were all a threshold, sign or convention fixed by hand without one;
   - Python 3.8 to 3.11 syntax only: no backslash inside an f-string expression,
     no match statement, no X | Y unions, no parenthesised context managers,
     no removeprefix on 3.8 targets; NumPy only, no SciPy, no pandas;
   - writes per-realization, per-J errors (as exactcal_real.csv and
     rmapj_real.csv do), never only cell means or only slopes;
   - uses an injective seed table: one seed per (cell, realization) drawn from
     numpy.random.SeedSequence keyed by the cell index, written to the output
     CSV; never an arithmetic formula over name lengths (exactcal.py's formula
     gives Ackley and Sphere identical seeds in every cell, ledger N6);
   - measures and prints per-worker peak RSS (resource.getrusage) in any run
     that evolves trajectories.

6. Memory and the 12-hour limit of any shared platform are constraints;
   runtime is not. Never trim a design to save compute. Never propose a
   trajectory design whose per-worker peak RSS has not been measured by a
   script Rahul ran. Free RAM on his machines can be as low as 1.5 GB.

7. Cross-platform comparability is gated. The archive was produced on
   Windows 7, Python 3.8.10, NumPy 1.24.4, three workers. No number from a run
   on another machine is compared with an archived number until
   scripts/detcheck.py has passed its pre-registered criteria D1 to D3 on that
   machine, and the pass is recorded in ENVIRONMENT.md with the log path. If
   it fails, say so plainly; compare only within platform.

8. Manuscript edits: baseline first. Before any edit, extract the rendered PDF
   text (pdftotext) as the baseline. After the edit, recompile, extract again,
   diff against the baseline, and report the diff. Never report a fix as done
   without that diff. After every edit check that the abstract, the
   conclusions and every table caption still agree with the body; body-fixed-
   abstract-stale drift happened repeatedly in round 1. Keep compile logs
   clean: zero errors, zero undefined references, zero overfull boxes, no NaN
   in any figure.

9. Cited theorems: quote or say nothing. Any statement about a hypothesis or
   conclusion of Fornasier-Klock-Riedl 2024 (SIAM J. Optim.), the anisotropic
   Fornasier-Klock-Riedl 2022 (EvoApplications), Gerber-Hoffmann-Vaes 2025
   (ESAIM COCV) or Carrillo-Choi-Totzeck-Tse 2018 is checked against the
   primary text of the version cited, with that version's numbering.
   Paraphrased conditions were wrong twice in round 1. FKR 2024's theorem and
   equation numbers differ between the arXiv and journal versions; the
   manuscript's bibliographic note claiming they are common is a known defect
   (ledger N3).

10. Manuscript language: plain human prose; nothing AI-sounding; no
    overstatement; no "state of the art"; every mathematical step proved line
    by line; an explicit account of what is and is not possible; exploratory
    and confirmatory work labelled as such; a finite-window fitted slope is
    never called a rate; a non-significant difference is never called
    equivalence; a condition that is not a hypothesis of the theorem that owns
    the J^-1 exponent is never called that theorem's admissibility (ledger N1).

11. Deliverable zips sent to Rahul are flat: one folder, no subdirectories.
    The repository has the structure above and it changes only with his
    explicit approval.

12. Replies to Rahul: no inline code spans or backticks in prose; commands and
    URLs only inside fenced blocks; every command sequence ordered,
    copy-pasteable, with the working directory stated first; complete
    self-contained deliverables, not incremental patches; direct, unsoftened
    assessments; say "I do not know" and name what would settle it rather
    than guess.

## Known failure modes of this project (do not repeat)

- Patching introduces new defects. Every round-1 fix that was not verified in
  the rendered artefact against a baseline introduced at least one new error.
- The nine analysis-design errors (supplement S3): a two-sided criterion for a
  one-sided bound; a variance-explained criterion on a treatment that removes
  the variance; a criterion computed from an aggregate; a monotonicity
  tolerance smaller than the measured spread; rank correlation without tie
  correction; a predictive model without log transforms or support checks; an
  inverted sign in the boundary extraction; a cliff criterion that could not
  tell a cliff from a ramp; an aggregate mixing regions. Same cause each time.
- Table 7 declared fabricated when it had been overwritten; a real section,
  table and figure deleted and wrong numbers inserted as a fix.
- Severity defined as gamma(r1) - gamma(r2) in the text while the reported
  numbers were gamma(r2) - gamma(r1).
- Stale intervals from one bootstrap unit pasted next to numbers from another.
- Body text fixed, abstract left contradicting it.
- The "exact calibration" fix (beta solved on each realization's own reference
  ensemble) replaced a fixed-beta design with a random-beta design and became
  referee point 3. A fix that changes the estimand is not a fix.
- A text-extraction artefact ("35 x 10^4", a page number abutting
  "5 x 10^4") was nearly logged as a manuscript defect. Check the source
  before declaring a defect.
- Deposited archive one edit behind the submitted manuscript; claimed console
  logs and per-realization files that were never written. Archive what the
  text says is archived, then write the text.

## Workflow for any task

1. Read CLAUDE.md, notes/DEFECT_LEDGER.md and the relevant archived script in
   zenodo-v1 before writing anything.
2. State what will be computed, by which script, under which pre-specified
   criterion, and what each possible outcome will mean for the manuscript.
   Write the script into scripts/.
3. Give the ordered command sequence, working directory first. Stop. Wait for
   the pasted console output.
4. The output goes under runs/<run-id>/, and scripts/manifest.py writes
   its sha256.txt (for a Kaggle run, kgrun.py fetch writes it through the
   same function). Only run folders under runs/ get sha256.txt. Console
   logs go in logs/, are tracked in git, are never overwritten (the shell
   runs with set -o noclobber) and carry no separate manifest.
5. Only then write text, with every number copied from the log, never from
   memory, and every change verified by the baseline diff of rule 8.
6. Commit with a message naming the ledger item and the log or run folder.

## Git discipline

- Branch main. One commit per verified change. Never force-push, never
  rewrite history, never amend a pushed commit.
- Never commit .venv, scratch-*, LaTeX build artefacts or
  .claude/settings.local.json (all in .gitignore).
- runs/ and logs/ are tracked. A run folder is never modified after its
  sha256.txt is written; a corrected run is a new run folder.
- No Git LFS. Any single file above 50 MB: gzip it or stop and ask.
- After a fresh clone, run: chmod -R a-w zenodo-v1 round1-zip

## Kaggle compute

Heavy runs go to Kaggle; the repository, the manuscript and the git history
stay on the laptop. A Kaggle CPU session has 4 cores, 30 GB RAM, a hard
12-hour cap and 20 GB of output space. Treat all four as constraints.

13. scripts/kgrun.py is the only thing that talks to Kaggle. It assembles the
    bundle, versions the dataset, generates the runner and its metadata,
    pushes, polls and downloads the output into a new runs/ folder with a
    sha256.txt manifest. Never push a kernel by hand, never edit a notebook in
    the Kaggle web editor: the next push overwrites it and the repository
    stops being the source of truth.

14. Credentials never leave the laptop. ~/.kaggle/ (kaggle.json and
    access_token; the token file is what authenticates, ledger K6) is
    denied to Claude in .claude/settings.json; the kaggle CLI reads it
    itself. Never print it, copy it, put it in a notebook, or add a GitHub token to Kaggle
    Secrets. Every kaggle command is denied to Claude outright in
    .claude/settings.json: under rule 21 Claude executes nothing, and
    kgrun.py, with every kaggle command it issues, is run by Rahul.
    One exception (rule 22): the Kaggle username, key and access token are
    stored as the GitHub Actions secrets KAGGLE_USERNAME, KAGGLE_KEY and
    KAGGLE_ACCESS_TOKEN of this repository, for the rerun queue only
    (token added 2026-10-23, Rahul's decision). Claude never reads, prints or
    sets them.

15. On Kaggle the archive is mounted read-only under /kaggle/input, at a
    path the kgrun runner discovers rather than assumes (it tries
    /kaggle/input/<dataset>, then /kaggle/input/datasets/<user>/<dataset>,
    then a walk of /kaggle/input; on 2026-10-09 Kaggle used the second,
    /kaggle/input/datasets/ericsom/cbo-gap-archive; ledger K3), and
    output goes to /kaggle/working. Scripts take both as flags, --archive and
    --outdir, so one file runs unchanged on both machines. Never hard-code
    either path, and never copy the archive into /kaggle/working to work
    around the read-only mount.

16. The determinism gate is per platform. detcheck.py must pass D1 to D3 on
    Kaggle before any Kaggle number is compared with an archived one, and the
    verdict is recorded in ENVIRONMENT.md with its log path, exactly as for
    the laptop. A pass on the laptop says nothing about Kaggle.

17. A job is sized to finish inside 12 hours. Longer work is split into
    shards run as separate jobs with distinct --job names and
    --shard i --nshards k. Shards remain separate jobs with distinct names.
    Resumption is allowed (amended 2026-10-10, Rahul's decision), on these
    terms only:
    - A resumed run reads the completed task keys from one or more previous
      run folders, skips those tasks, and writes to a NEW run folder.
    - Previous output is never modified, appended to or overwritten.
    - The merge across folders is a concatenation. This is sound because
      every seed is keyed by the cell, through a SeedSequence over the task
      key, and not by position in the task list. A task therefore emits the
      same row whichever run, shard or resumption executes it.
    The following are added to make those terms checkable:
    - A previous folder is read only after its sha256.txt verifies.
    - A task key counts as completed only when its row is complete.
    - A key found in two folders stops the run.
    - The resumed run's parameters, other than the folder list, must equal
      those printed in each previous folder's header, or it stops.
    - The resumed run prints every folder it read and the number of keys it
      skipped from each.

18. Nothing that comes back from Kaggle is trusted until its header is read.
    Every script prints its parameters, seeds, Python and NumPy versions,
    platform and worker count at the head of the run; check that the Kaggle
    run used the versions and flags intended before any number from it is
    quoted. A NumPy version difference between laptop and Kaggle is exactly
    what rule 16 exists to catch.

19. Output folders from Kaggle are runs/<job>-kaggle-<timestamp>/ and are
    never modified after their sha256.txt manifest is written, same as local run
    folders. The Kaggle-side copy is not the record; the committed folder is.

20. .kaggle-bundle/ and .kaggle-push/ are scratch, rebuilt on every call, and
    are in .gitignore. Never edit them by hand and never commit them.

## Division of labour

21. Claude writes files, commits and pushes. Claude does not execute
    scripts, gates, experiments or kgrun. Every run is performed by Rahul on
    his machine, and he pastes the console output back. When a task needs a
    result Claude does not have, Claude writes the script and the exact
    command sequence for him to run, then stops and waits. Never record a
    result that was not received from him.
    One exception (rule 22): the rerun queue's jobs are launched, fetched
    and committed by the GitHub Actions workflow that Rahul enabled. Their
    results are the committed run folders and logs, read under rule 18 like
    any other.

22. The rerun queue (added 2026-10-23, Rahul's decision; ledger K6).
    .github/workflows/rerun-queue.yml runs scripts/rerunq.py tick. It is
    started by a workflow_dispatch POST that cron-job.org sends every 15
    minutes (amended 2026-10-23, Rahul's decision; ledger K6), and by
    GitHub's own schedule, which on this account fires only hours apart.
    Each tick takes at most one action (launch, poll, or fetch and
    commit) through kgrun.py, under the decision rules in rerunq.py's
    docstring, and commits as github-actions[bot].
    - While the workflow is enabled, nobody launches or fetches a Kaggle job
      by hand. Nobody edits notes/rerun_queue.json except through rerunq.py
      halt, check and release; a Claude session never edits it (denied in
      .claude/settings.json).
    - A new attempt after a halt ("release --mode next-attempt") is refused
      unless the halted job's kernel status was checked since the halt,
      by "rerunq.py check" or by Rahul with --checked-by-hand (rule K1 in
      rerunq.py's docstring), so that two kernels never run one shard.
    - A failed tick disables the workflow. Nothing continues until Rahul
      has read the halt reason, released the state and re-enabled the
      workflow.
    - The queue covers the eight jobs listed in notes/rerun_queue.json.
      Anything else goes through the runbooks by hand.
    - The dispatch token is a fine-grained personal access token of
      Rahul's, limited to this repository, with Actions read and write
      only, and an expiry date. It exists only in cron-job.org's job
      configuration. Claude never reads, prints, creates or sets it. A
      halt is enforced by the committed state, not by the dispatcher: a
      dispatch to the disabled workflow starts nothing, and a tick that
      finds the state HALTED exits 3 and disables the workflow again.
