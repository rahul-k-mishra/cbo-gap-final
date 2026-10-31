"""
rerunq.py  --  CBO-GAP: the rerun queue, one step per invocation

WHAT THIS IS, IN PLAIN LANGUAGE
-------------------------------
The fixed-beta rerun is eight Kaggle jobs, run one at a time
(notes/RERUN_RUNBOOK.md). A Kaggle shard takes three to twelve hours, and a
GitHub Actions job is capped at six, so nothing here waits for a job to
finish. .github/workflows/rerun-queue.yml runs "rerunq.py tick" every 15
minutes. Each tick reads the committed state file notes/rerun_queue.json,
takes AT MOST ONE action, commits the new state together with anything it
fetched in ONE commit, pushes it, and exits:

  READY      launch the job the state names (kgrun launch: bundle, dataset
             version, kernel push; no polling)
  LAUNCHING  an earlier tick recorded the intent to launch but not the
             outcome: adopt the kernel if Kaggle has it, otherwise HALT
  RUNNING    poll (kgrun status). Still running: do nothing and commit
             nothing. Finished: fetch (kgrun fetch), verify the manifest,
             read the runner log, decide, commit and push
  HALTED     do nothing; exit 3, so the workflow run fails and disables
             the workflow, and Rahul is notified
  DONE       do nothing; the workflow disables itself

It talks to Kaggle only through scripts/kgrun.py (CLAUDE.md rule 13), with
its subcommands launch, status and fetch. It never reads, prints or writes
the Kaggle credentials; the workflow writes ~/.kaggle/kaggle.json and
~/.kaggle/access_token (the file that actually authenticates; ledger K6)
and the kaggle CLI reads them.

THE QUEUE (notes/rerun_queue.json; ledger N37, N38, K6)
  index 0     smoke-arch   rerun.py --smoke, the 13 archived-beta rows
  index 1-4   arch-s<S>of4 the archived-beta shards 0 to 3 of 4
  index 5     smoke-cal    rerun.py --smoke, CONC,TAU8,SIGMA,ANISO
  index 6-7   cal-s<S>of2  the calibrated shards 0 and 1 of 2
  Both sets use the plan runs/rerun-plan-20261023-112643. Its archived-beta
  rows are identical to those of runs/rerun-plan-20261016-193630 (ledger
  N35, second precheck), and rerun_analysis.py is run against this plan.
  Job names follow the runbook: rerun-smoke-arch-a<A>, rerun-arch-s<S>of4-
  a<A>, rerun-smoke-cal-a<A>, rerun-cal-s<S>of2-a<A>; the Kaggle kernel is
  <user>/cbo-<job>.
  Arguments, identical to the runbook's (sections 1 and 2):
    smoke: --smoke --plan-from <plan> --rows <rows> --workers 4
           data folders: the plan
    shard: --plan-from <plan> --timing-from <T0> --timing-from <T1>
           --rows <rows> --shard S --nshards K --workers 4
           data folders: the plan, T0, T1; resume folders as below

SCHEMA 2 AND THE CALPREC2 FAMILY (2026-10-25, before first execution;
ledger N42; Rahul's instruction "extend the rerun queue to drive the
calibration shards and the finalize, the way it drove the eight rerun
jobs")
  The eight-job queue above ended DONE. Its state (schema 1) is archived
  by "load" (below) and stays readable in git. From schema 2 on, the
  state names one or more PROFILES and each queue item names its
  profile. A profile is one script family with its fixed arguments and
  its pins:
    rerun     rerun.py; plan, plan_sha256, timing, workers; items smoke or
              shard, exactly as above (job names, arguments, F2, R1, R2).
    calprec2  calprec2.py; rows, throughput folder, stop_after, ceiling
              (null for the script's default), workers, cells (the plan's
              deduplicated count, for F2C); items shard or finalize.
  Every rule above (L1 to L5, F1, R2's exit handling, P1, K1) applies to
  both families unchanged, except where this section says otherwise.
  JOB NAMES (calprec2): calprec2-<set>-s<S>of<K>-a<A> for a shard,
    calprec2-<set>-finalize-a<A> for the finalize; kernel cbo-<job>.
  ARGUMENTS (calprec2), built from the profile, never typed by hand:
    shard:    --workers W --rows R --throughput T --stop-after X
              [--ceiling C] --shard S --nshards K
              data folders: T; resume folders as in R2
    finalize: --rows R --finalize F1,F2,...
              data folders: F1, F2, ... = every recorded attempt folder of
              every shard item of the same profile and set that holds a
              calprec2-full-*/calprec2_tasks.csv (FIN below)
  P1C  CODE PIN, per profile: before every launch each file the profile
      pins (calprec2.py and costprobe2.py for calprec2) must hash to the
      value "load" recorded from the committed file. Otherwise HALT.
      Worked example: costprobe2.py edited between shard 3 and shard 4:
      HALT before shard 4.
  R1C  HEADER (calprec2 shard), from cbo-<job>.log:
      (a) "python" and "numpy" equal expect (3.13.15 and 2.1.3);
      (b) "script   sha256" equals calprec2_sha256 and "costprobe2.py
          sha256" equals costprobe2_sha256;
      (c) "mode     full   rows R   shard S of K" with R, S and K the
          item's;
      (d) the "throughput" line's basename equals the profile's folder;
      (e) "files  <dir>": the basename is exactly
          calprec2-full-YYYYMMDD-HHMMSS-s<S>of<K> (calprec2.py line 1524:
          the stamp, then the tag; no tag when K = 1), the fetched folder
          holds exactly one calprec2-* folder and it has that basename,
          and its calprec2_params.csv records mode full, the rows, S, K,
          workers, stop_after and ceiling as the arguments set them, and
          the two pinned hashes;
      (f) for a resumed attempt, a line "  read <folder>: shard S of K, N
          rows, M complete" for each resume folder (calprec2's own rule-17
          line, printed by read_folders).
      Any mismatch: HALT, the folder committed.
      Worked example: files /kaggle/working/calprec2-full-20261026-
      101500-s3of15 with params shard 3, nshards 15, stop_after 30000.0:
      pass. calprec2-full-20261026-101500-s4of15: HALT on (e).
  F2C  COMPLETE DOWNLOAD (calprec2 shard): the rows of that folder's
      calprec2_tasks.csv whose end is "ok" number exactly the N of "tasks
      run by this job: N", and "errored or timed-out tasks: 0" is printed.
      Exit 0 requires "not stopped: every phase ran"; exit 5 requires
      "STOPPED by --stop-after". Otherwise HALT, the folder committed.
      Worked example: "tasks run by this job: 2007", 2007 rows end ok,
      "not stopped", exit 0: pass. 1990 rows: HALT "download incomplete".
  R2C  EXIT (calprec2): shard as R2 (0 next item; 5 next attempt resuming
      from every earlier attempt folder of the shard, with N = 0 a halt
      and max_attempts the cap; anything else HALT). Finalize: 0 next
      item; any other value, 5 included, HALT. Exit 4 from finalize means
      a cell is incomplete or "E1 not run" (calprec2.py EXIT CODES).
  FIN  FINALIZE INPUTS. A finalize launches only when every shard item of
      its profile and set has an attempt recorded with runner exit 0. Its
      folders are every recorded attempt folder of those items that holds
      calprec2 task rows, attempts that stopped at 5 included, because the
      merge is a concatenation and an exit-5 folder holds complete rows
      (rule 17). Otherwise HALT before launch.
      Worked example: shard s7of15 exited 5 at a1 and 0 at a2: both
      folders are finalize inputs.
  R1F  HEADER (finalize): (a) and (b) of R1C; "mode     finalize   rows R";
      "files  <dir>" with basename calprec2-finalize-YYYYMMDD-HHMMSS; the
      fetched folder holds exactly one calprec2-* folder, with that
      basename, holding calprec2_beta.csv; the "read" lines name exactly
      the finalize's input folders.
  F2F  COMPLETE TABLE (finalize): calprec2_beta.csv has exactly the
      profile's "cells" rows, each cell once, and no label starting
      "incomplete". Otherwise HALT.
      Worked example: 41 rows, 41 distinct cells, labels "target" or
      "beta ...": pass. 40 rows: HALT.
  LD  LOAD (subcommand "load", run by Rahul on the laptop, who commits
      and pushes). Refused unless the current state is DONE. The current
      state's bytes are copied to notes/queue-archive/<stamp>-<name>.json
      (opened "x"); the definition (a committed JSON file under
      notes/queues/) is checked: every profile and item has the keys its
      family needs, item kinds belong to their family, item ids are
      unique, data and throughput folders exist with a verified
      sha256.txt. For each profile, every pinned file's sha256 is read
      from scripts/ and recorded as expect. The new state is READY at item
      0, attempt 1, with the definition's path and sha256 and the archive
      path in its history. Worked example: "load --definition
      notes/queues/calprec2-ext.json" with the rerun queue DONE: archive
      notes/queue-archive/20261025-140000-rerun-queue-done.json written,
      state READY at calprec2-ext-s0of15.

THE SIZETEST FAMILY (2026-10-31, before first execution; ledger N40;
Rahul's instruction "E1 runs on Kaggle, in the resumable queue, CPU only.
Smoke first, shard exit 5 resumes from its own folders, same halt rules")
    sizetest  sizetest.py modes smoke and e1 (E1 of N40: fresh t = 0 draws
              weighed at the run beta; no trajectory); plan (a committed
              runs/sizetest-plan-* folder written by "sizetest.py --mode
              plan --write-plan"), plan_sha256 (of its
              sizetest_e1_plan.csv), throughput (calprec2's smoke folder),
              stop_after, workers; items smoke or shard.
  Every rule above (L1 to L5, F1, P1C, K1, R2's exit handling) applies
  unchanged, except where this section says otherwise. There is no
  finalize: "sizetest.py --mode analyse" reads the fetched folders on the
  laptop, by hand.
  JOB NAMES: sizetest-<set>-smoke-a<A> and sizetest-<set>-s<S>of<K>-a<A>;
    kernel cbo-<job>.
  ARGUMENTS, built from the profile:
    smoke: --mode smoke --plan-from P --throughput T --workers W
    shard: --mode e1 --plan-from P --throughput T --stop-after X
           --shard S --nshards K --workers W
    data folders: P and T; resume folders as in R2.
  PINS (P1C): sizetest.py, calprec2.py and costprobe2.py.
  LDZ LOAD: as LD, and P and T must pass the folder checks, and
      P/sizetest_e1_plan.csv must hash to plan_sha256. Otherwise refused.
  R1Z HEADER, from cbo-<job>.log, after the banner "CBO-GAP sizetest":
      (a) "python" and "numpy" equal expect;
      (b) "script   sha256", "calprec2.py sha256" and "costprobe2.py
          sha256" equal the three pins;
      (c) "plan     sizetest_e1_plan.csv sha256" equals plan_sha256 and
          the "throughput" line's basename is the profile's;
      (d) "mode     smoke   shard 0 of 1" for a smoke, "mode     e1
          shard S of K" for a shard, with S and K the item's;
      (e) "PC PASS" printed;
      (f) "files  <dir>": the basename is exactly
          sizetest-smoke-YYYYMMDD-HHMMSS or
          sizetest-e1-YYYYMMDD-HHMMSS-s<S>of<K> (no tag when K = 1), the
          fetched folder holds exactly one sizetest-* folder with that
          basename, and its sizetest_params.csv records the mode, S, K,
          workers, plan_sha256, the three hashes, and for a shard
          stop_after as the profile sets it;
      (g) for a resumed attempt, a line "  read <folder>: shard S of K, N
          rows, M complete" for each resume folder.
      Any mismatch: HALT, the folder committed.
      Worked example: files /kaggle/working/sizetest-e1-20261101-
      093000-s1of2, params shard 1, nshards 2, stop_after 36000.0, PC
      PASS: pass. The same with "PC FAIL" (runner exit 3): HALT on R2,
      R1Z (e) quoted.
  SMZ SMOKE: runner exit 0, "SMOKE PASS", and the smoke folder's rows
      ending ok number exactly "tasks run by this job" with "errored or
      timed-out tasks: 0". Then the next item; otherwise HALT, and no
      shard of the set launches.
      Worked example: 21 units, 21 rows ok, "SMOKE PASS", exit 0: next
      item. Exit 4 with "SMOKE FAIL": HALT.
  F2Z COMPLETE DOWNLOAD (shard): exactly one sizetest-e1-*/sizetest_e1.csv;
      its rows ending ok number exactly "tasks run by this job", with
      "errored or timed-out tasks: 0". Exit 0 requires "not stopped:
      every task ran"; exit 5 requires "STOPPED by --stop-after".
      Otherwise HALT, the folder committed.
      Worked example: "tasks run by this job: 2616", 2616 rows ok, "not
      stopped", exit 0: pass. 2600 rows: HALT "download incomplete".
  R2Z EXIT: smoke as SMZ; shard as R2 (0 next item; 5 next attempt
      resuming from every earlier attempt folder of the shard holding a
      sizetest-e1-*/sizetest_e1.csv, with N = 0 a halt and max_attempts
      the cap; anything else HALT).

THE C5 FAMILY (2026-11-01, before first execution; ledger N45; Rahul's
instruction "C5 fully automated from GitHub to Kaggle with no laptop
involvement at all")
    c5        c5run.py modes smoke, drill and run (rows CONC-X and TAU8-X:
              every CONC and TAU8 cell at J_inf 4000000); timing (the three
              jinfprobe run folders), beta_table (the calprec2 finalize
              folder), rerun_plan (the plan whose CONC and TAU8 cells the
              50000 run used), drill_stop_after, workers; items smoke,
              drill or shard.
  Every rule above (L1 to L5, F1, P1C, K1, R2's exit handling) applies
  unchanged, except where this section says otherwise. No finalize:
  c5_analysis.py reads the fetched folders.
  JOB NAMES: c5-<set>-smoke-a<A>, c5-<set>-drill-a<A>,
    c5-<set>-s<S>of<K>-a<A>; kernel cbo-<job>.
  ARGUMENTS, built from the profile (C = --timing T0,T1,T2 --beta-table B
    --rerun-plan P --workers W):
    smoke: --mode smoke C
    drill: --mode drill C --stop-after X   (X = drill_stop_after)
    shard: --mode run C --shard S --nshards K
    data folders: T0, T1, T2, B and P; resume folders as in R2.
  PINS (P1C): c5run.py, jinfprobe.py, c5price.py, calprec2.py,
    costprobe2.py and rerunlib.py.
  LDX LOAD: as LD; T0, T1, T2, B and P must pass the folder checks.
  R1X HEADER, from cbo-<job>.log, after the banner "CBO-GAP c5run":
      (a) "python" and "numpy" equal expect;
      (b) the six "sha256" lines equal the six pins;
      (c) "mode     M   shard S of K" with (M, S, K) = (smoke, 0, 1),
          (drill, 0, 1) or (run, S, K) of the item;
      (d) the "timing", "beta table" and "rerun plan" lines name the
          profile's folders (basenames); "B1 PASS" printed;
      (e) "files  <dir>": the basename is exactly
          c5run-<mode>-YYYYMMDD-HHMMSS, plus -s<S>of<K> for a run, the
          fetched folder holds exactly one c5run-* folder with that
          basename, and its c5run_params.csv records mode, shard, nshards,
          workers, kind (97 smoke, 98 drill, 95 run), the six hashes, the
          three input names, budget_mb 24000.0, and for a drill stop_after
          as the profile sets it;
      (f) for a resumed attempt, a line "  read <folder>: shard S of K, N
          rows, M complete" for each resume folder.
      Any mismatch: HALT, the folder committed.
      Worked example: files /kaggle/working/c5run-run-20261102-101500-
      s7of116 with params shard 7, nshards 116, kind 95: pass.
      c5run-run-20261102-101500-s8of116: HALT on (e).
  SMX SMOKE: runner exit 0, "SMOKE PASS", and rows ending ok number exactly
      "tasks run by this job" with "errored or timed-out tasks: 0". Then
      the next item; otherwise HALT, and nothing after it launches.
  F2X COMPLETE DOWNLOAD (drill and shard): exactly one
      c5run-*/c5run_real.csv; its rows ending ok number exactly "tasks run
      by this job", with "errored or timed-out tasks: 0" and "F1
      failures: 0". Exit 0 requires "not stopped: every task ran" and
      "complete rows, this job and resumed: N of N"; exit 5 requires
      "STOPPED by --stop-after". Otherwise HALT, the folder committed.
      Worked example: "tasks run by this job: 38", 38 rows ok, "complete
      rows, this job and resumed: 38 of 38", exit 0: pass. Exit 0 with
      "37 of 38": HALT.
  R2X EXIT: smoke as SMX; drill and shard as R2 (0 next item; 5 next
      attempt resuming from every earlier attempt folder of the item
      holding a c5run-*/c5run_real.csv, with C = 0 a halt and
      max_attempts the cap; anything else HALT). The drill exists so that
      the exit-5 path runs on Kaggle under the queue before any shard.

PRE-SPECIFIED DECISION RULES (fixed 2026-10-23, before first execution)
------------------------------------------------------------------------
  L1  THE STATE FILE IS THE LOCK. A tick changes the state only by a
      commit whose parent is the commit it read, pushed without force. If
      the push is rejected, the tick fetches main and compares main's
      notes/rerun_queue.json with the bytes it read:
      - different: the lock is lost. Before any Kaggle side effect the
        tick does nothing more and exits 0. After one, it exits 3 (HALT).
      - identical: somebody pushed another file. The tick re-applies its
        one commit on top of main (cherry-pick) and pushes again; three
        rejected pushes in all are a push failure, exit 3.
      The tick also starts only from a clean checkout whose HEAD is main's
      tip; otherwise it cannot confirm the state, does nothing and exits
      (0 if HEAD is merely behind, 1 if the tree is dirty).
      A push reported as failed whose commit is nevertheless main's tip
      (the reply was lost) counts as accepted. There is no ABA case: every
      transition appends to the state's history, so the bytes of a later
      state never equal those of an earlier one.
      Worked example: ticks A and B both read commit c1, status READY. A
      pushes c2 (READY to LAUNCHING): accepted. B's c2' is rejected; main's
      state file now reads LAUNCHING, not the READY B read: B exits 0 and
      launches nothing. Rahul pushes a ledger edit while tick C fetches:
      C's push is rejected, the state file on main is the one C read, C
      cherry-picks onto Rahul's commit and pushes: accepted.
      (The workflow's concurrency group already keeps two ticks from
      running at once; L1 is what makes that unnecessary for correctness.)

  L2  INTENT BEFORE LAUNCH. A launch is four steps: (1) kgrun status must
      report the kernel ABSENT (L3); (2) the state LAUNCHING, with the job
      name, arguments and folders, is committed and pushed; (3) kgrun
      launch; (4) the state RUNNING is committed with the kgrun log. A tick
      that finds LAUNCHING asks kgrun status: a known status means the
      push happened, and the kernel is adopted (RUNNING, "adopted"
      recorded, the dead tick's kgrun log is lost); ABSENT means it is not
      known whether a push is still to appear, so HALT. The queue never
      pushes a kernel twice under one name and never relaunches after an
      interrupted launch on its own.
      Worked example: a tick is killed after kgrun printed its push and
      before step 4; main reads LAUNCHING rerun-arch-s1of4-a1. The next
      tick's kgrun status prints 'ericsom/cbo-rerun-arch-s1of4-a1 has
      status "KernelWorkerStatus.RUNNING"': RUNNING, adopted. Had it printed
      ABSENT (L4): HALT.

  L3  KERNEL NAMES ARE NEVER REUSED. In step (1) of L2, any recognised
      status (the kernel exists) is a HALT; also a HALT: any committed
      folder runs/<job>-kaggle-* already present.
      Worked example: rerun-smoke-arch-a1 was pushed by hand from the
      laptop; kgrun status says COMPLETE: HALT "kernel already exists".

  L4  STATUS. The line '<user>/cbo-<job> has status "KernelWorkerStatus.X"'
      in kgrun status's output. X in QUEUED, RUNNING, NEW_SCRIPT,
      CANCEL_REQUESTED: wait. COMPLETE, ERROR, CANCEL_ACKNOWLEDGED:
      finished, fetch. Anything else: UNKNOWN, except this one case:
      ABSENT. kaggle 2.2.4 answers a status request for a kernel that does
      not exist with (ledger K6, measured 2026-10-23)
        Cannot access kernel 'ericsom/cbo-rerun-smoke-arch-a1' (Permission
        'kernels.get' was denied). The most likely cause is a wrong kernel
        slug. ... It can also occur if the notebook is private.
      and with no "404". The CLI's own text says the same reply covers a
      kernel that exists but cannot be read, and from this one reply
      nothing tells the two apart. What does: the account. Every kernel
      kgrun pushes is private (is_private True), and the same account's
      credentials have read the status of its own private kernels
      throughout (logs/kgrun-calprec2-long-s25of26-a1.log, "private
      True", then 'has status "KernelWorkerStatus.COMPLETE"'). So a denial
      for <user>/cbo-<job> means "no such kernel" only when the credentials
      in use are working credentials of <user>. That is tested in the same
      tick: after the denial, kgrun status of CONTROL_JOB (a private kernel
      of <user> known to exist, calprec2-long-s25of26-a1) must return a
      recognised status line. ABSENT therefore requires both:
        (a) the line "Cannot access kernel '<user>/cbo-<job>' (Permission
            'kernels.get' was denied)" for exactly this kernel; and
        (b) the control's status line, read after (a).
      A denial whose control fails is UNKNOWN, never ABSENT: an expired,
      revoked or wrong-account key is denied on the control too (it is
      private), so it cannot read as a free name. Any other reply (401,
      a network error, text not matching (a)) is UNKNOWN. The control
      runs after the target, so a key that stops working between the two
      calls fails the control; a key does not start working again.
      What this does not cover: a kernel of <user> that the owner's own
      credentials cannot read. No evidence of such a case exists, and the
      CLI gives no way to detect it.
      kgrun status itself exiting other than 0 (it exits 0 whatever the
      kaggle CLI reports, so this is a crash): HALT at once.
      Worked examples: '... has status "KernelWorkerStatus.ERROR"':
      finished; the runner log decides (a job killed at the 12-hour cap
      prints no runner exit line, and R2 halts). The denial for
      rerun-smoke-arch-a1, then the control 'has status
      "KernelWorkerStatus.COMPLETE"': ABSENT, launch. The same denial,
      then a denial or an error for the control: UNKNOWN, anomaly; a
      second one halts (L5).
      Every line kgrun status prints is copied into the tick log, and an
      UNKNOWN detail quotes the line the verdict rests on (raw_status's
      judged line), never merely the last line of the output, which is
      kgrun's closing banner.
      Worked example: both denied gives the detail 'denied, and the
      control calprec2-long-s25of26-a1 was denied too: Cannot access
      kernel 'ericsom/cbo-calprec2-long-s25of26-a1' (Permission ...'.

  L5  TWICE THE SAME WAY. A tick that cannot classify what it sees
      (UNKNOWN status; ABSENT while RUNNING) records {job, kind} as the
      anomaly, commits it and exits 0 with a warning. The next tick that
      meets the same {job, kind} HALTs. A tick that classifies cleanly
      clears the anomaly.
      Worked example: tick 1, status UNKNOWN (an HTTP 503): anomaly
      recorded. Tick 2, RUNNING: anomaly cleared. Had tick 2 also been
      UNKNOWN for the same job: HALT.

  F1  FETCH. Before the fetch: no runs/<job>-kaggle-* folder exists (L3).
      After it: kgrun fetch exited 0; exactly one new folder
      runs/<job>-kaggle-<stamp>; its files equal those its sha256.txt
      lists and every hash matches, re-read here independently of the
      write; no file above max_file_mb (50 MB; CLAUDE.md: gzip it or stop
      and ask). Any failure: HALT; the fetch log is committed, the folder
      is NOT (its manifest is not verified) and goes into the workflow
      run's rescue artifact.
      Worked example: rerun_real.csv of 63 MB: HALT "above 50 MB"; the
      folder is in the artifact rerunq-rescue-<run>.

  F2  COMPLETE DOWNLOAD (shards). The fetched folder holds exactly one
      rerun-*/rerun_real.csv, and its rows whose end column is "ok" number
      exactly the C of the runner's summary line "completed C". The
      manifest proves only that nothing changed after the download; F2 is
      what shows the download was not cut short. Checked when the runner
      printed a summary; a mismatch is a HALT, the folder committed.
      Worked example: summary "completed 2808  errors 0  not started 0",
      2808 rows ending ok: pass. 2791 rows: HALT "download incomplete".

  R1  HEADER (CLAUDE.md rule 18), from the kernel log cbo-<job>.log in the
      fetched folder: python and numpy equal expect (3.13.15 and 2.1.3,
      ENVIRONMENT.md); rerun_sha256, rerunlib_sha256 and costprobe2_sha256
      equal expect (the runbook's pinned values); rerun_plan.csv sha256
      equals plan_sha256; the mode is smoke for a smoke and run for a
      shard; a resumed attempt prints "resume: read" for each of its
      resume folders. For a shard, the output must belong to the shard
      the queue launched, which three checks establish:
      (a) the basename of the printed "run dir" is exactly
          rerun-s<S>of<K>-YYYYMMDD-HHMMSS, the name rerun.py's code gives
          a shard's output (new_outdir("rerun" + "-s<S>of<K>"): tag, then
          the stamp; its docstring's "rerun-<stamp>[-s<i>of<k>]" has the
          order wrong, ledger K6);
      (b) the fetched folder holds exactly one rerun-* folder, and it has
          that basename, so the header and the rows F2 counts come from
          one run;
      (c) that folder's rerun_params.csv records shard S and nshards K.
      Any mismatch: HALT, even when the runner exited 0. The folder is
      committed.
      Worked example: "numpy 2.2.0" printed: HALT "numpy 2.2.0, expected
      2.1.3"; rule 16 then requires detcheck on the new image.
      Worked example, arch-s0of4: run dir /kaggle/working/rerun-s0of4-
      20261023-164555, the one folder rerun-s0of4-20261023-164555 with
      shard 0 and nshards 4: pass. rerun-s1of4-20261024-031500 (another
      shard), rerun-s0of2-... (another split), rerun-s0of40-... ,
      rerun-20261023-164555 (unsharded) or rerun-smoke-...: HALT on (a).
      Header rerun-s0of4-20261023-164555 but the fetched folder holds
      rerun-s0of4-20261022-090000: HALT on (b). rerun_params.csv with
      shard 1: HALT on (c).
      (Until 2026-10-24 (a) read "the run dir ends in -s<S>of<K>", which
      no name rerun.py writes can satisfy; it halted arch-s0of4 attempt
      1, whose output passed every other check. Ledger K6.)

  R2  RUNNER EXIT, the LAST line "kgrun runner: exit code N" of that log.
      In every case below the fetched folder is committed first.
      - no such line (killed, cap, pre-emption, cancelled): HALT;
      - N = 2, 3 or 4, or any value other than 0 and 5: HALT;
      - smoke: N = 0 and "D-SMOKE PASS" printed: next item. Otherwise
        HALT. A halted queue launches nothing, so no shard of a set whose
        smoke did not pass is ever launched;
      - shard, N = 0: next item, attempt 1, no resume folders; after the
        last item, DONE;
      - shard, N = 5 (G-STOP): the same shard, attempt A + 1, with every
        earlier attempt folder of this shard as resume folders, this one
        included (each that holds a rerun-*/rerun_real.csv). Not when
        A = max_attempts (5): HALT. Not when the
        summary line "completed C" shows C = 0: a stop with no progress is
        a failure, HALT.
      Worked example: arch-s2of4 attempt 1 exits 5 with completed 2500:
      READY arch-s2of4 attempt 2, resume [a1 folder]. Attempt 2 exits 5
      with completed 300: attempt 3, resume [a1, a2]. Attempt 5 exits 5:
      HALT "5 attempts". Attempt 1 exits 4: HALT, nothing relaunched.

  P1  CODE PIN. Before every launch, scripts/rerun.py, rerunlib.py and
      costprobe2.py must hash to expect; otherwise HALT. The runbook
      forbids code edits while a shard set is in progress.
      Worked example: rerunlib.py edited on main between shards 1 and 2:
      its sha256 differs from 5d55050e...9b06: HALT before shard 2.

  K1  KERNEL CHECK BEFORE A NEW ATTEMPT. "release --mode next-attempt"
      gives the shard a new kernel name, so if a kernel under the old
      name is running, two kernels run the same shard. It is refused
      unless the state holds a kernel check made since the halt, for the
      job the halt left (the recorded job, or, when none is recorded, the
      name of the current item and attempt). A check comes from one of:
      - "check" run on the laptop: kgrun status for that job, its class
        (L4) and status recorded in the state;
      - "--checked-by-hand STATUS" on the release itself, STATUS one of
        COMPLETE, ERROR, CANCEL_ACKNOWLEDGED, ABSENT: Rahul states what he
        saw on Kaggle, and that is recorded in the history.
      Accepted: a finished status (COMPLETE, ERROR, CANCEL_ACKNOWLEDGED),
      or ABSENT seen at least CHECK_GAP_MIN (30) minutes after the halt,
      because ABSENT straight after an interrupted launch cannot tell
      "never pushed" from "pushed, not yet visible". 30 minutes is a
      design choice, not a measured Kaggle delay. Refused: a waiting status
      (the kernel is running: release with repoll instead), UNKNOWN, no
      check, or a check for another job.
      "Since the halt" is enforced by the state: kernel_check is null in
      every status but HALTED, every halt sets it null, every release sets
      it null, and only "check" or the flag sets it, while HALTED.
      Worked example: halted 10:00 "L2: rerun-arch-s1of4-a1 was left
      LAUNCHING and Kaggle does not have the kernel". At 10:05 "check"
      prints ABSENT: next-attempt refused (5 minutes). At 10:40 "check"
      prints ABSENT: next-attempt accepted, attempt 2. Had it printed
      RUNNING: refused, release with repoll.

NW  NEXT WAKE (2026-11-01; ledger N45; Rahul's instruction to drive the
    queue from GitHub alone, after horizon's loop). Subcommand "next-wake
    --min A --max B", read-only: prints "<seconds> <reason>" or "none
    <reason>", from the committed state alone. HALTED or DONE: none (no
    successor is ever started for a halted or finished queue). READY or
    LAUNCHING: A (act soon). RUNNING: B (a kernel is in flight; poll).
    The workflow (rerun-queue.yml, "Start the next tick") calls it after a
    tick that exited 0 and did not ask to be disabled, sleeps that long,
    resets to main's tip, calls it again, checks that the workflow is still
    enabled, and only then dispatches its successor. A tick that fails or
    halts starts no successor. Worked example: a fetch leaves READY:
    "60 READY"; a launch leaves RUNNING: "900 RUNNING"; a halt: "none
    HALTED".

EXIT CODES (tick)
  0  nothing to do; one action done; an anomaly recorded (L5); the lock
     lost before any Kaggle side effect (L1)
  3  HALT: the state is HALTED, or this tick halted, or a push failed
     after a Kaggle side effect
  1  unexpected error: unreadable state, dirty checkout, an exception
  The workflow disables itself after any nonzero exit, and after DONE.
  The laptop timer (scripts/rerunq-tick.service, CLAUDE.md rule 22)
  disables itself after any nonzero exit; at DONE its ticks do nothing
  and exit 0 until Rahul disables it.

FILES WRITTEN (all new files opened "x")
  notes/rerun_queue.json        the state, rewritten in place by design:
                                the one exception to CLAUDE.md rule 3
                                (ledger K6)
  logs/kgrun-<job>.log          kgrun launch's console
  logs/kgrun-<job>-fetch.log    kgrun fetch's console (-fetch2.log, ... if
                                taken)
  logs/rerunq-<job>-<event>-<stamp>.log   this script's console for every
                                tick that commits
  runs/<job>-kaggle-<stamp>/    written by kgrun fetch, with sha256.txt
  scratch-rerunq/               rescue copies for the workflow artifact;
                                ignored by git (scratch-*)

SUBCOMMANDS
  tick --run-id ID   one step; run by the workflow or by the laptop timer
                     (run id "laptop.<UTC stamp>") only
  show               print the state (reads only)
  verify             while HALTED: re-run F1, R1, R2 and F2 on the folder of
                     the current item's last fetched attempt, exactly as a
                     fetch tick would (reads only, writes nothing); exit 0
                     on PASS, 3 on FAIL. Run before "release --mode
                     next-item" after a halt that came after the fetch, so
                     that the checks the halt pre-empted are not skipped
                     (ledger K6, arch-s0of4 a1: R1 halted before F2)
  load --definition notes/queues/<name>.json --note TEXT
                     only when DONE: archive the state and start the queue
                     the definition describes (LD); Rahul commits and
                     pushes, then enables the drivers
  halt --note TEXT   set HALTED by hand; Rahul commits and pushes
  check --note TEXT  while HALTED: kgrun status for the halted job, the
                     result recorded as the kernel check (K1); run by
                     Rahul on the laptop, who commits and pushes
  release --mode M --note TEXT     leave HALTED by hand; Rahul commits and
                     pushes, then enables the workflow. M is one of:
    start         READY at the current item and attempt; only when no
                  launch intent is recorded for that attempt (job empty)
    repoll        RUNNING for the recorded job: poll and fetch it again.
                  For a halt that left a kernel unfetched (a push failure,
                  L5, a manual halt); F1 refuses if it was already fetched
    next-attempt  READY at the same item, attempt A + 1, resume folders
                  every recorded attempt folder of the item holding a
                  rerun_real.csv (shards only); for Rahul's decision after
                  exit 4, a death, or an interrupted launch. Refused
                  without an accepted kernel check (K1); the check comes
                  from "check" or from --checked-by-hand STATUS
    next-item     READY at the next item, attempt 1

Python 3.8 to 3.11 syntax. Standard library only, plus scripts/manifest.py.
No trajectory is evolved here, so the Pool, --workers and RSS items of
CLAUDE.md rule 5 do not apply (as for kgrun.py).
"""

import argparse
import csv
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import list_files, sha256_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
STATE_REL = "notes/rerun_queue.json"
STATE = os.path.join(ROOT, STATE_REL)
KGRUN = os.path.join(SCRIPTS, "kgrun.py")
RESCUE = os.path.join(ROOT, "scratch-rerunq")
STATUSES = ("READY", "LAUNCHING", "RUNNING", "HALTED", "DONE")
WAIT = ("QUEUED", "RUNNING", "NEW_SCRIPT", "CANCEL_REQUESTED")
FINISHED = ("COMPLETE", "ERROR", "CANCEL_ACKNOWLEDGED")
PINNED = (("rerun.py", "rerun_sha256"), ("rerunlib.py", "rerunlib_sha256"),
          ("costprobe2.py", "costprobe2_sha256"))
FAMILY_SCRIPT = {"rerun": "rerun.py", "calprec2": "calprec2.py", "sizetest": "sizetest.py", "c5": "c5run.py"}
FAMILY_PINS = {"rerun": PINNED,
               "calprec2": (("calprec2.py", "calprec2_sha256"), ("costprobe2.py", "costprobe2_sha256")),
               "sizetest": (("sizetest.py", "sizetest_sha256"), ("calprec2.py", "calprec2_sha256"),
                            ("costprobe2.py", "costprobe2_sha256")),
               "c5": (("c5run.py", "c5run_sha256"), ("jinfprobe.py", "jinfprobe_sha256"),
                      ("c5price.py", "c5price_sha256"), ("calprec2.py", "calprec2_sha256"),
                      ("costprobe2.py", "costprobe2_sha256"), ("rerunlib.py", "rerunlib_sha256"))}
FAMILY_KINDS = {"rerun": ("smoke", "shard"), "calprec2": ("shard", "finalize"), "sizetest": ("smoke", "shard"),
                "c5": ("smoke", "drill", "shard")}
PROFILE_KEYS = {"rerun": ("family", "workers", "plan", "plan_sha256", "timing", "expect"),
                "calprec2": ("family", "workers", "rows", "throughput", "stop_after", "ceiling", "cells",
                             "expect"),
                "sizetest": ("family", "workers", "plan", "plan_sha256", "throughput", "stop_after", "expect"),
                "c5": ("family", "workers", "timing", "beta_table", "rerun_plan", "drill_stop_after", "expect")}
C5_KIND = {"smoke": 97, "drill": 98, "shard": 95}
C5_HASH_LABELS = (("c5run_sha256", "script  "), ("jinfprobe_sha256", "jinfprobe.py"), ("c5price_sha256", "c5price.py"),
                  ("calprec2_sha256", "calprec2.py"), ("costprobe2_sha256", "costprobe2.py"),
                  ("rerunlib_sha256", "rerunlib.py"))
SIZETEST_PLAN_CSV = "sizetest_e1_plan.csv"     # sizetest.py PLAN_CSV
ARCHIVE_DIR = "notes/queue-archive"
CEILING_DEFAULT = 21600.0           # calprec2.py CEILING_DEFAULT, written to its params when --ceiling is absent
PUSH_TRIES = 3
CHECK_GAP_MIN = 30
HAND_STATUSES = FINISHED + ("ABSENT",)
CONTROL_JOB = "calprec2-long-s25of26-a1"
DENIED = re.compile(r"Cannot access kernel '([^']+)' \(Permission 'kernels\.get' was denied\)")

LOG = []


class Halt(Exception):
    def __init__(self, reason, paths=()):
        Exception.__init__(self, reason)
        self.reason = reason
        self.paths = list(paths)


class Anomaly(Exception):
    def __init__(self, kind, detail):
        Exception.__init__(self, kind)
        self.kind = kind
        self.detail = detail


def say(msg=""):
    print(msg)
    sys.stdout.flush()
    LOG.append(msg)


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

def git(args, check=True):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace").strip()
    if check and p.returncode != 0:
        raise RuntimeError("git {} failed ({}): {}".format(" ".join(args), p.returncode, out))
    return p.returncode, out


def git_bytes(args):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout


# --------------------------------------------------------------------------
# state
# --------------------------------------------------------------------------

def dump(s):
    return (json.dumps(s, indent=2) + "\n").encode("utf-8")


def write_state(s):
    tmp = STATE + ".tmp"
    with open(tmp, "xb") as fh:
        fh.write(dump(s))
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, STATE)


def profile_of(s, item):
    return s["profiles"][item["profile"]]


def family_of(s, item):
    return profile_of(s, item)["family"]


def validate_definition(s):
    """The profiles and the queue (shared by validate and load)."""
    if not isinstance(s.get("profiles"), dict) or not s["profiles"]:
        raise ValueError("no profiles")
    for name, p in s["profiles"].items():
        fam = p.get("family")
        if fam not in FAMILY_SCRIPT:
            raise ValueError("profile {}: family {!r} is not one of {}".format(name, fam, sorted(FAMILY_SCRIPT)))
        for k in PROFILE_KEYS[fam]:
            if k not in p:
                raise ValueError("profile {} ({}) has no key {}".format(name, fam, k))
        for k in ("python", "numpy"):
            if not p["expect"].get(k):
                raise ValueError("profile {}: expect has no {}".format(name, k))
    if not s.get("queue"):
        raise ValueError("empty queue")
    ids = [it.get("id") for it in s["queue"]]
    if len(set(ids)) != len(ids):
        raise ValueError("item ids are not unique: {}".format(ids))
    for it in s["queue"]:
        for k in ("id", "profile", "kind", "set", "ledger"):
            if k not in it:
                raise ValueError("item {} has no key {}".format(it.get("id"), k))
        if it["profile"] not in s["profiles"]:
            raise ValueError("item {}: unknown profile {}".format(it["id"], it["profile"]))
        fam = s["profiles"][it["profile"]]["family"]
        if it["kind"] not in FAMILY_KINDS[fam]:
            raise ValueError("item {}: kind {} is not one of {} ({})".format(it["id"], it["kind"],
                                                                         FAMILY_KINDS[fam], fam))
        if it["kind"] == "shard":
            for k in ("shard", "nshards"):
                if not isinstance(it.get(k), int):
                    raise ValueError("item {}: {} {!r}".format(it["id"], k, it.get(k)))
            if not (0 <= it["shard"] < it["nshards"]):
                raise ValueError("item {}: shard {} of {}".format(it["id"], it["shard"], it["nshards"]))
        if fam == "rerun" and not it.get("rows"):
            raise ValueError("item {}: a rerun item needs rows".format(it["id"]))


def validate(s):
    for k in ("schema", "kaggle_user", "profiles", "max_attempts", "max_file_mb", "queue", "status", "index",
              "attempt", "resume_dirs", "job", "args", "data_dirs", "anomaly", "halt_reason", "kernel_check",
              "attempts", "history", "definition"):
        if k not in s:
            raise ValueError("state has no key " + k)
    if s["schema"] != 2:
        raise ValueError("state schema {} is not 2 (a schema-1 state is loaded over with 'rerunq.py load', "
                         "LD)".format(s["schema"]))
    validate_definition(s)
    if s["status"] not in STATUSES:
        raise ValueError("status {!r} is not one of {}".format(s["status"], STATUSES))
    n = len(s["queue"])
    if s["status"] == "DONE":
        if s["index"] != n:
            raise ValueError("DONE with index {} of {}".format(s["index"], n))
    elif not (0 <= s["index"] < n):
        raise ValueError("index {} outside the queue of {}".format(s["index"], n))
    if not isinstance(s["attempt"], int) or s["attempt"] < 1:
        raise ValueError("attempt {!r}".format(s["attempt"]))
    if s["status"] in ("LAUNCHING", "RUNNING"):
        if s["job"] != job_name(s, s["queue"][s["index"]], s["attempt"]):
            raise ValueError("job {!r} does not match item {} attempt {}".format(
                s["job"], s["index"], s["attempt"]))
    if s["status"] == "READY" and s["job"]:
        raise ValueError("READY with a job recorded ({})".format(s["job"]))
    if s["status"] != "HALTED" and s["kernel_check"] is not None:
        raise ValueError("a kernel check is recorded in status {} (K1: only while HALTED)".format(s["status"]))
    for name, p in s["profiles"].items():
        for _, k in FAMILY_PINS[p["family"]]:
            if not p["expect"].get(k):
                raise ValueError("profile {}: expect has no {}".format(name, k))


def history(s, run, event, note):
    s["history"].append({"at": now(), "run": run, "event": event,
                         "item": s["queue"][s["index"]]["id"] if s["index"] < len(s["queue"]) else "",
                         "attempt": s["attempt"], "job": s["job"], "note": note})


def job_name(s, item, attempt):
    if family_of(s, item) == "c5":
        if item["kind"] in ("smoke", "drill"):
            return "c5-{}-{}-a{}".format(item["set"], item["kind"], attempt)
        return "c5-{}-s{}of{}-a{}".format(item["set"], item["shard"], item["nshards"], attempt)
    if family_of(s, item) == "sizetest":
        if item["kind"] == "smoke":
            return "sizetest-{}-smoke-a{}".format(item["set"], attempt)
        return "sizetest-{}-s{}of{}-a{}".format(item["set"], item["shard"], item["nshards"], attempt)
    if family_of(s, item) == "calprec2":
        if item["kind"] == "finalize":
            return "calprec2-{}-finalize-a{}".format(item["set"], attempt)
        return "calprec2-{}-s{}of{}-a{}".format(item["set"], item["shard"], item["nshards"], attempt)
    if item["kind"] == "smoke":
        return "rerun-smoke-{}-a{}".format(item["set"], attempt)
    return "rerun-{}-s{}of{}-a{}".format(item["set"], item["shard"], item["nshards"], attempt)


def ceiling_of(p):
    return CEILING_DEFAULT if p["ceiling"] is None else float(p["ceiling"])


def finalize_inputs(s, item):
    """FIN: (folders, problems) for a calprec2 finalize item."""
    folders, probs = [], []
    for it in s["queue"]:
        if it["profile"] != item["profile"] or it["set"] != item["set"] or it["kind"] != "shard":
            continue
        recs = s["attempts"].get(it["id"], [])
        if not any(r["runner_exit"] == 0 for r in recs):
            probs.append("{} has no attempt with runner exit 0".format(it["id"]))
        for r in recs:
            if holds_rows(r["folder"], "calprec2"):
                folders.append(r["folder"])
    if not folders:
        probs.append("no shard folder with calprec2 task rows")
    return folders, probs


def job_spec(s):
    """(job, args, data folders) for the current item and attempt."""
    item = s["queue"][s["index"]]
    p = profile_of(s, item)
    if p["family"] == "c5":
        common = "--timing {} --beta-table {} --rerun-plan {} --workers {}".format(
            ",".join(p["timing"]), p["beta_table"], p["rerun_plan"], p["workers"])
        if item["kind"] == "smoke":
            args = "--mode smoke " + common
        elif item["kind"] == "drill":
            args = "--mode drill {} --stop-after {!r}".format(common, float(p["drill_stop_after"]))
        else:
            args = "--mode run {} --shard {} --nshards {}".format(common, item["shard"], item["nshards"])
        data = list(p["timing"]) + [p["beta_table"], p["rerun_plan"]]
    elif p["family"] == "sizetest":
        if item["kind"] == "smoke":
            args = "--mode smoke --plan-from {} --throughput {} --workers {}".format(
                p["plan"], p["throughput"], p["workers"])
        else:
            args = "--mode e1 --plan-from {} --throughput {} --stop-after {!r} --shard {} --nshards {} " \
                   "--workers {}".format(p["plan"], p["throughput"], float(p["stop_after"]), item["shard"],
                                         item["nshards"], p["workers"])
        data = [p["plan"], p["throughput"]]
    elif p["family"] == "calprec2":
        if item["kind"] == "finalize":
            data, _ = finalize_inputs(s, item)
            args = "--rows {} --finalize {}".format(p["rows"], ",".join(data))
        else:
            args = "--workers {} --rows {} --throughput {} --stop-after {!r}".format(
                p["workers"], p["rows"], p["throughput"], float(p["stop_after"]))
            if p["ceiling"] is not None:
                args += " --ceiling {!r}".format(float(p["ceiling"]))
            args += " --shard {} --nshards {}".format(item["shard"], item["nshards"])
            data = [p["throughput"]]
    elif item["kind"] == "smoke":
        args = "--smoke --plan-from {} --rows {} --workers {}".format(p["plan"], item["rows"], p["workers"])
        data = [p["plan"]]
    else:
        tf = " ".join("--timing-from {}".format(t) for t in p["timing"])
        args = "--plan-from {} {} --rows {} --shard {} --nshards {} --workers {}".format(
            p["plan"], tf, item["rows"], item["shard"], item["nshards"], p["workers"])
        data = [p["plan"]] + list(p["timing"])
    return job_name(s, item, s["attempt"]), args, data


def holds_rows(folder, family="rerun"):
    if family == "c5":
        return bool(glob.glob(os.path.join(ROOT, folder, "c5run-*", "c5run_real.csv")))
    if family == "sizetest":
        return bool(glob.glob(os.path.join(ROOT, folder, "sizetest-e1-*", "sizetest_e1.csv")))
    if family == "calprec2":
        return bool(glob.glob(os.path.join(ROOT, folder, "calprec2-full-*", "calprec2_tasks.csv")))
    return bool(glob.glob(os.path.join(ROOT, folder, "rerun-*", "rerun_real.csv")))


# --------------------------------------------------------------------------
# kgrun (the only route to Kaggle)
# --------------------------------------------------------------------------

def kgrun(argv, logrel=None):
    cmd = [sys.executable, KGRUN] + argv
    say("  $ " + " ".join(cmd))
    if logrel:
        with open(os.path.join(ROOT, logrel), "x") as fh:
            rc = subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT)
        say("  kgrun exit code {}  (console: {})".format(rc, logrel))
        with open(os.path.join(ROOT, logrel), errors="replace") as fh:
            tail = fh.read().splitlines()[-25:]
        for ln in tail:
            say("    | " + ln)
        return rc, ""
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ROOT)
    out = p.stdout.decode("utf-8", "replace")
    say("  kgrun exit code {}".format(p.returncode))
    return p.returncode, out


def raw_status(s, job):
    """One kgrun status call: (recognised status or None, denied for exactly this kernel, judged line).

    Every line kgrun printed goes into the tick log. The judged line is the
    line the verdict rests on: the status line, else the denial line for
    exactly this kernel, else the kaggle CLI's reply (every line between
    kgrun's "$ kaggle kernels status" echo and its closing banner, minus the
    outdated-version warning, joined by " / "), else "(kaggle printed
    nothing)". kgrun's banner rows of "=" are never judged.
    Worked example: the reply 'Cannot access kernel
    'ericsom/cbo-calprec2-long-s25of26-a1' (Permission 'kernels.get' was
    denied). The most likely cause ...' for the control gives (None, True,
    that whole line).
    """
    rc, out = kgrun(["status", "--job", job, "--user", s["kaggle_user"]])
    for ln in out.splitlines():
        say("    | " + ln)
    kid = "{}/cbo-{}".format(s["kaggle_user"], job)
    found, judged = None, None
    for ln in out.splitlines():
        m = re.match(r'^(\S+) has status "([^"]+)"$', ln.strip())
        if m and m.group(1) == kid:
            found, judged = m.group(2).split(".")[-1].upper(), ln.strip()
    denied = False
    for ln in out.splitlines():
        if any(m.group(1) == kid for m in DENIED.finditer(ln)):
            denied = True
            if judged is None:
                judged = ln.strip()
    if judged is None:
        reply, inside = [], False
        for ln in out.splitlines():
            st = ln.strip()
            if st.startswith("$ kaggle kernels status"):
                inside = True
                continue
            if not inside or not st:
                continue
            if set(st) == {"="}:
                break
            if st.startswith("Warning: Looks like you're using an outdated `kaggle` version"):
                continue
            reply.append(st)
        judged = " / ".join(reply) if reply else "(kaggle printed nothing)"
    say("  kaggle status of {}: {}  (judged: {})".format(
        kid, found if found else ("DENIED" if denied else "no status line"), judged))
    if rc != 0:
        raise Halt("kgrun status exit {} for {}".format(rc, job))
    return found, denied, judged


def kernel_status(s, job):
    """L4: (class, detail), class one of WAIT, FINISHED, ABSENT, UNKNOWN."""
    found, denied, judged = raw_status(s, job)
    if found in WAIT:
        return "WAIT", found
    if found in FINISHED:
        return "FINISHED", found
    if found:
        return "UNKNOWN", "status " + found
    if not denied:
        return "UNKNOWN", "no status line and no denial for {}/cbo-{}; kaggle replied: {}".format(
            s["kaggle_user"], job, judged)
    say("  denied: control status of {} (L4), to tell a free name from a credential failure".format(
        CONTROL_JOB))
    cfound, cdenied, cjudged = raw_status(s, CONTROL_JOB)
    if not cfound:
        return "UNKNOWN", "denied, and the control {} {}: {}".format(
            CONTROL_JOB, "was denied too" if cdenied else "gave no status line", cjudged)
    return "ABSENT", "denied; control {} {}".format(CONTROL_JOB, cfound)


# --------------------------------------------------------------------------
# commit and push (L1)
# --------------------------------------------------------------------------

class Ctx(object):
    def __init__(self, s, base, run):
        self.s = s
        self.base = base
        self.run = run


def driver_log(job, event):
    rel = "logs/rerunq-{}-{}-{}.log".format(job or "queue", event, stamp())
    with open(os.path.join(ROOT, rel), "x") as fh:
        fh.write("\n".join(LOG) + "\n")
    return rel


def publish(ctx, paths, msg):
    """Commit the state and paths in one commit and push it. 'ok', 'lost' or 'failed'."""
    write_state(ctx.s)
    git(["add", "--", STATE_REL] + list(paths))
    git(["commit", "-q", "-m", msg])
    for i in range(PUSH_TRIES):
        rc, out = git(["push", "origin", "HEAD:refs/heads/main"], check=False)
        say("  push {} of {}: {}".format(i + 1, PUSH_TRIES, "accepted" if rc == 0 else "REJECTED: " + out))
        if rc == 0:
            git(["fetch", "-q", "origin", "main"], check=False)
            ctx.base = dump(ctx.s)
            return "ok"
        if git(["fetch", "-q", "origin", "main"], check=False)[0] != 0:
            return "failed"
        if git(["rev-parse", "origin/main"])[1] == git(["rev-parse", "HEAD"])[1]:
            say("  the push was reported failed but main's tip is this commit: accepted")
            ctx.base = dump(ctx.s)
            return "ok"
        rc, remote = git_bytes(["show", "origin/main:" + STATE_REL])
        if rc != 0 or remote != ctx.base:
            say("  the state file on main is not the one this tick read: lock lost")
            return "lost"
        sha = git(["rev-parse", "HEAD"])[1]
        git(["checkout", "-q", "-B", "main", "origin/main"])
        if git(["cherry-pick", sha], check=False)[0] != 0:
            git(["cherry-pick", "--abort"], check=False)
            return "failed"
        say("  re-applied this tick's commit on main's tip")
    return "failed"


def rescue(paths):
    if not os.path.isdir(RESCUE):
        os.makedirs(RESCUE)
    for rel in paths:
        src = os.path.join(ROOT, rel)
        dst = os.path.join(RESCUE, os.path.basename(rel.rstrip("/")))
        if os.path.isdir(src) and not os.path.exists(dst):
            shutil.copytree(src, dst)
        elif os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)


def gh_output(key, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as fh:
            fh.write("{}={}\n".format(key, value))


def gh_summary(s):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    rows = ["## rerun queue: {}".format(s["status"]), "",
            "| item | attempt | job | halt reason |", "|---|---|---|---|",
            "| {} | {} | {} | {} |".format(
                s["queue"][s["index"]]["id"] if s["index"] < len(s["queue"]) else "(end)",
                s["attempt"], s["job"] or "-", s["halt_reason"] or "-"), "",
            "| item | attempt | runner exit | completed | folder |", "|---|---|---|---|---|"]
    for item in s["queue"]:
        for r in s["attempts"].get(item["id"], []):
            rows.append("| {} | {} | {} | {} | {} |".format(item["id"], r["attempt"], r["runner_exit"],
                                                           r["completed"], r["folder"]))
    with open(path, "a") as fh:
        fh.write("\n".join(rows) + "\n")


def do_halt(ctx, reason, paths):
    s = ctx.s
    say("HALT: " + reason)
    s["status"] = "HALTED"
    s["halt_reason"] = reason
    s["kernel_check"] = None
    history(s, ctx.run, "halt", reason)
    rel = driver_log(s["job"], "halt")
    r = publish(ctx, list(paths) + [rel], "rerun queue: HALTED at {}: {} ({}, K6)".format(
        s["job"] or s["queue"][s["index"]]["id"], reason[:150], s["queue"][s["index"]]["ledger"]))
    print("::error title=rerun queue HALTED::" + reason)
    if r != "ok":
        print("::error title=rerun queue::the HALTED state could not be pushed ({}); main still holds the "
              "state this tick read. The workflow disables itself; the rescue artifact holds what was "
              "fetched. Do not commit the rescue copy: release with repoll fetches again.".format(r))
    gh_summary(s)
    return 3


def do_anomaly(ctx, kind, detail):
    s = ctx.s
    job = s["job"] or job_spec(s)[0]
    prev = s["anomaly"]
    if prev and prev.get("job") == job and prev.get("kind") == kind:
        return do_halt(ctx, "the same anomaly twice for {} ({}): first {} in run {}, now {}".format(
            job, kind, prev.get("detail"), prev.get("run"), detail), [])
    s["anomaly"] = {"job": job, "kind": kind, "detail": detail, "run": ctx.run, "at": now()}
    history(s, ctx.run, "anomaly", "{}: {}".format(kind, detail))
    rel = driver_log(job, "anomaly")
    r = publish(ctx, [rel], "rerun queue: anomaly at {} ({}), recorded (K6)".format(job, kind))
    print("::warning title=rerun queue anomaly::{} {}: {}; a second one halts".format(job, kind, detail))
    gh_summary(s)
    if r == "failed":
        return 3
    return 0


# --------------------------------------------------------------------------
# the three actions
# --------------------------------------------------------------------------

def do_launch(ctx):
    s = ctx.s
    item = s["queue"][s["index"]]
    p = profile_of(s, item)
    fam = p["family"]
    job, args, data = job_spec(s)
    say("LAUNCH  item {} ({}), attempt {}, job {}  [{} profile {}]".format(
        s["index"], item["id"], s["attempt"], job, fam, item["profile"]))
    for name, key in FAMILY_PINS[fam]:
        h = sha256_of(os.path.join(SCRIPTS, name))
        if h != p["expect"][key]:
            raise Halt("P1: scripts/{} sha256 {} differs from the pinned {}".format(name, h, p["expect"][key]))
    say("  P1 code pin: {} as pinned".format(", ".join(n for n, _ in FAMILY_PINS[fam])))
    if fam == "calprec2" and item["kind"] == "finalize":
        _f, probs = finalize_inputs(s, item)
        if probs:
            raise Halt("FIN: {}".format("; ".join(probs)))
        say("  FIN: {} input folder(s): {}".format(len(data), ", ".join(data)))
    old = glob.glob(os.path.join(ROOT, "runs", job + "-kaggle-*"))
    if old:
        raise Halt("L3: {} already has a folder in runs/: {}".format(job, ", ".join(sorted(old))))
    if os.path.exists(os.path.join(ROOT, "logs", "kgrun-{}.log".format(job))):
        raise Halt("L3: logs/kgrun-{}.log already exists; was {} launched by hand?".format(job, job))
    for d in s["resume_dirs"]:
        if not holds_rows(d, fam):
            raise Halt("resume folder {} holds no {} rows".format(d, fam))
    cls, detail = kernel_status(s, job)
    if cls == "UNKNOWN":
        raise Anomaly("preflight-status", detail)
    if cls != "ABSENT":
        raise Halt("L3: kernel {}/cbo-{} already exists on Kaggle (status {}) before this queue launched "
                   "it".format(s["kaggle_user"], job, detail))
    say("  L3: kernel absent on Kaggle, name unused")

    s["status"] = "LAUNCHING"
    s["job"], s["args"], s["data_dirs"] = job, args, data
    s["anomaly"] = None
    history(s, ctx.run, "intent", "resume " + (",".join(s["resume_dirs"]) or "none"))
    r = publish(ctx, [], "rerun queue: intent to launch {} ({}, K6)".format(job, item["ledger"]))
    if r == "lost":
        print("::warning title=rerun queue::lock lost before launch; nothing launched")
        return 0
    if r == "failed":
        print("::error title=rerun queue::the LAUNCHING state could not be pushed; nothing launched")
        return 3

    logrel = "logs/kgrun-{}.log".format(job)
    argv = ["launch", "--job", job, "--user", s["kaggle_user"], "--script", FAMILY_SCRIPT[fam],
            "--data-dirs", ",".join(data), "--args=" + args]
    if s["resume_dirs"]:
        argv += ["--resume-dirs", ",".join(s["resume_dirs"])]
    rc, _ = kgrun(argv, logrel)
    if rc != 0:
        raise Halt("kgrun launch exit {}; whether the kernel was pushed is not known: check "
                   "kgrun status by hand before any release".format(rc), [logrel])
    s["status"] = "RUNNING"
    history(s, ctx.run, "launched", logrel)
    rel = driver_log(job, "launched")
    r = publish(ctx, [logrel, rel], "rerun queue: launched {} ({}, K6)".format(job, item["ledger"]))
    gh_summary(s)
    if r != "ok":
        print("::error title=rerun queue::{} was launched but RUNNING could not be pushed ({}); main reads "
              "LAUNCHING, which the next tick adopts (L2)".format(job, r))
        return 3
    return 0


def do_recover(ctx):
    s = ctx.s
    say("RECOVER  {} was left LAUNCHING (L2)".format(s["job"]))
    cls, detail = kernel_status(s, s["job"])
    if cls == "UNKNOWN":
        raise Anomaly("recover-status", detail)
    if cls == "ABSENT":
        raise Halt("L2: {} was left LAUNCHING and Kaggle does not have the kernel; it is not known whether "
                   "the push happened. Check by hand; release with next-attempt only once it is certain "
                   "that no kernel is running under this name".format(s["job"]))
    s["status"] = "RUNNING"
    s["anomaly"] = None
    history(s, ctx.run, "adopted", "kernel {} found after an interrupted launch; that tick's kgrun log "
            "was not committed".format(detail))
    rel = driver_log(s["job"], "adopted")
    r = publish(ctx, [rel], "rerun queue: adopted {} after an interrupted launch (K6)".format(s["job"]))
    gh_summary(s)
    return 0 if r == "ok" else 3


def do_poll(ctx):
    s = ctx.s
    say("POLL  {}".format(s["job"]))
    cls, detail = kernel_status(s, s["job"])
    if cls == "UNKNOWN":
        raise Anomaly("status-unknown", detail)
    if cls == "ABSENT":
        raise Anomaly("status-absent", detail)
    if cls == "WAIT":
        if s["anomaly"]:
            s["anomaly"] = None
            history(s, ctx.run, "clear", "status " + detail)
            rel = driver_log(s["job"], "clear")
            r = publish(ctx, [rel], "rerun queue: {} {}, anomaly cleared (K6)".format(s["job"], detail))
            gh_summary(s)
            return 0 if r != "failed" else 3
        say("  {}: nothing to do".format(detail))
        gh_summary(s)
        return 0
    return do_fetch(ctx, detail)


def free_log(job):
    for i in range(1, 100):
        rel = "logs/kgrun-{}-fetch{}.log".format(job, "" if i == 1 else i)
        if not os.path.exists(os.path.join(ROOT, rel)):
            return rel
    raise RuntimeError("no free fetch log name for " + job)


def verify_manifest(folder):
    """F1: problems found, [] when the folder matches its sha256.txt exactly."""
    man = os.path.join(folder, "sha256.txt")
    if not os.path.isfile(man):
        return ["no sha256.txt"]
    listed = {}
    with open(man) as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if ln:
                h, rel = ln.split("  ", 1)
                listed[rel] = h
    files, bad = list_files(folder)
    out = ["not a regular file: " + b for b in bad]
    if sorted(listed) != files:
        out.append("files present {} differ from those listed {}".format(files, sorted(listed)))
    for rel in files:
        if rel in listed and sha256_of(os.path.join(folder, rel)) != listed[rel]:
            out.append("hash mismatch at " + rel)
    return out


def runner_text(folder, job):
    p = os.path.join(folder, "cbo-{}.log".format(job))
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    try:
        ents = json.loads(raw)
        return "".join(e.get("data", "") for e in ents if isinstance(e, dict))
    except ValueError:
        return raw


def read_runner(text, family="rerun"):
    if family == "c5":
        return read_runner_c5(text)
    if family == "sizetest":
        return read_runner_sizetest(text)
    return read_runner_calprec2(text) if family == "calprec2" else read_runner_rerun(text)


def read_runner_sizetest(text):
    """R1Z, F2Z, SMZ: the lines sizetest.py prints after its banner "CBO-GAP sizetest"."""
    f = {"exit": None, "python": None, "numpy": None, "hashes": {}, "plan_sha": None, "mode": None,
         "shard": None, "nshards": None, "throughput": None, "rundir": None, "resume_read": set(),
         "ran": None, "errors": None, "stopped": False, "notstopped": False, "completed": None, "smoke": None,
         "pc": None}
    if text is None:
        return f
    ex = re.findall(r"kgrun runner: exit code (-?\d+)", text)
    if ex:
        f["exit"] = int(ex[-1])
    i = text.find("CBO-GAP sizetest")
    body = text[i:] if i >= 0 else ""
    for key, pat in (("python", r"^  python   (\S+)\s*$"), ("numpy", r"^  numpy    (\S+)\s*$"),
                     ("throughput", r"^  throughput  (\S+)\s*$"),
                     ("plan_sha", r"^  plan     sizetest_e1_plan\.csv sha256 ([0-9a-f]{64})\s*$")):
        m = re.search(pat, body, re.M)
        if m:
            f[key] = m.group(1)
    for key, pat in (("sizetest_sha256", r"^  script   sha256 ([0-9a-f]{64})\s*$"),
                     ("calprec2_sha256", r"^  calprec2\.py sha256 ([0-9a-f]{64})\s*$"),
                     ("costprobe2_sha256", r"^  costprobe2\.py sha256 ([0-9a-f]{64})\s*$")):
        m = re.search(pat, body, re.M)
        if m:
            f["hashes"][key] = m.group(1)
    m = re.search(r"^  mode     (\w+)   shard (\d+) of (\d+)\s*$", body, re.M)
    if m:
        f["mode"], f["shard"], f["nshards"] = m.group(1), int(m.group(2)), int(m.group(3))
    m = re.findall(r"^files  (\S+)\s*$", body, re.M)
    if m:
        f["rundir"] = m[-1]
    for path in re.findall(r"^  read (\S+): shard \S+ of \S+, \d+ rows, \d+ complete\s*$", body, re.M):
        f["resume_read"].add(os.path.basename(path.rstrip("/")))
    m = re.findall(r"^tasks run by this job: (\d+)   task execution", body, re.M)
    if m:
        f["ran"] = int(m[-1])
        f["completed"] = f["ran"]
    m = re.findall(r"^errored or timed-out tasks: (\d+)\s*$", body, re.M)
    if m:
        f["errors"] = int(m[-1])
    f["stopped"] = bool(re.search(r"^STOPPED by --stop-after", body, re.M))
    f["notstopped"] = bool(re.search(r"^not stopped: every task ran\s*$", body, re.M))
    m = re.findall(r"^SMOKE (PASS|FAIL)\s*$", body, re.M)
    if m:
        f["smoke"] = m[-1]
    m = re.findall(r"^PC (PASS|FAIL)  ", body, re.M)
    if m:
        f["pc"] = m[-1]
    return f


def read_runner_c5(text):
    """R1X, F2X, SMX: the lines c5run.py prints after its banner "CBO-GAP c5run"."""
    f = {"exit": None, "python": None, "numpy": None, "hashes": {}, "mode": None, "shard": None, "nshards": None,
         "timing": None, "beta_table": None, "rerun_plan": None, "b1": False, "rundir": None, "resume_read": set(),
         "ran": None, "errors": None, "f1": None, "stopped": False, "notstopped": False, "complete": None,
         "completed": None, "smoke": None, "plan_sha": None}
    if text is None:
        return f
    ex = re.findall(r"kgrun runner: exit code (-?\d+)", text)
    if ex:
        f["exit"] = int(ex[-1])
    i = text.find("CBO-GAP c5run")
    body = text[i:] if i >= 0 else ""
    for key, pat in (("python", r"^  python   (\S+)\s*$"), ("numpy", r"^  numpy    (\S+)\s*$"),
                     ("timing", r"^  timing   (\S+)\s*$"), ("beta_table", r"^  beta table (\S+)\s*$"),
                     ("rerun_plan", r"^  rerun plan (\S+)\s*$")):
        m = re.search(pat, body, re.M)
        if m:
            f[key] = m.group(1)
    for key, label in C5_HASH_LABELS:
        m = re.search(r"^  " + re.escape(label) + r" sha256 ([0-9a-f]{64})\s*$", body, re.M)
        if m:
            f["hashes"][key] = m.group(1)
    m = re.search(r"^  mode     (\w+)   shard (\d+) of (\d+)\s*$", body, re.M)
    if m:
        f["mode"], f["shard"], f["nshards"] = m.group(1), int(m.group(2)), int(m.group(3))
    f["b1"] = bool(re.search(r"^  B1 PASS ", body, re.M))
    m = re.findall(r"^files  (\S+)\s*$", body, re.M)
    if m:
        f["rundir"] = m[-1]
    for path in re.findall(r"^  read (\S+): shard \S+ of \S+, \d+ rows, \d+ complete\s*$", body, re.M):
        f["resume_read"].add(os.path.basename(path.rstrip("/")))
    m = re.findall(r"^tasks run by this job: (\d+)   task execution", body, re.M)
    if m:
        f["ran"] = int(m[-1])
        f["completed"] = f["ran"]
    m = re.findall(r"^errored or timed-out tasks: (\d+)\s*$", body, re.M)
    if m:
        f["errors"] = int(m[-1])
    m = re.findall(r"^F1 failures: (\d+)\s*$", body, re.M)
    if m:
        f["f1"] = int(m[-1])
    m = re.findall(r"^complete rows, this job and resumed: (\d+) of (\d+)\s*$", body, re.M)
    if m:
        f["complete"] = (int(m[-1][0]), int(m[-1][1]))
    f["stopped"] = bool(re.search(r"^STOPPED by --stop-after", body, re.M))
    f["notstopped"] = bool(re.search(r"^not stopped: every task ran\s*$", body, re.M))
    m = re.findall(r"^SMOKE (PASS|FAIL)\s*$", body, re.M)
    if m:
        f["smoke"] = m[-1]
    return f


def header_problems_c5(s, item, f, folder):
    """R1X (smoke, drill and shard), with SMX's row count for a smoke."""
    p = profile_of(s, item)
    e = p["expect"]
    out = []
    if f["python"] != e["python"]:
        out.append("python {}, expected {}".format(f["python"], e["python"]))
    if f["numpy"] != e["numpy"]:
        out.append("numpy {}, expected {}".format(f["numpy"], e["numpy"]))
    for _, k in FAMILY_PINS["c5"]:
        if f["hashes"].get(k) != e[k]:
            out.append("{} {}, expected {}".format(k, f["hashes"].get(k), e[k]))
    names = {"timing": ",".join(os.path.basename(x.rstrip("/")) for x in p["timing"]),
             "beta_table": os.path.basename(p["beta_table"].rstrip("/")),
             "rerun_plan": os.path.basename(p["rerun_plan"].rstrip("/"))}
    for k, v in sorted(names.items()):
        if f[k] != v:
            out.append("{} {}, expected {}".format(k, f[k], v))
    if not f["b1"]:
        out.append("no 'B1 PASS' line")
    kind = item["kind"]
    mode = "run" if kind == "shard" else kind
    S, K = (item["shard"], item["nshards"]) if kind == "shard" else (0, 1)
    if (f["mode"], f["shard"], f["nshards"]) != (mode, S, K):
        out.append("mode {} shard {} of {}, expected {} shard {} of {}".format(
            f["mode"], f["shard"], f["nshards"], mode, S, K))
    base = os.path.basename((f["rundir"] or "").rstrip("/"))
    tag = "" if K == 1 else "-s{}of{}".format(S, K)
    if not re.fullmatch(r"c5run-" + mode + r"-\d{8}-\d{6}" + re.escape(tag), base):
        out.append("files {}, expected a basename c5run-{}-YYYYMMDD-HHMMSS{}".format(f["rundir"], mode, tag))
    subs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(folder, "c5run-*")) if os.path.isdir(d))
    if subs != [base]:
        out.append("fetched c5run-* folder(s) {}, expected exactly [{}]".format(subs, base))
    else:
        pp = os.path.join(folder, base, "c5run_params.csv")
        got = {}
        if os.path.isfile(pp):
            with open(pp, newline="") as fh:
                got = dict((r[0], r[1]) for r in csv.reader(fh) if r)
        want = {"mode": mode, "shard": str(S), "nshards": str(K), "workers": str(p["workers"]),
                "kind": str(C5_KIND[kind]), "budget_mb": "24000.0", "timing": names["timing"],
                "beta_table": names["beta_table"], "rerun_plan": names["rerun_plan"]}
        for k, _l in C5_HASH_LABELS:
            want["script_sha256" if k == "c5run_sha256" else k] = e[k]
        if kind == "drill":
            want["stop_after"] = repr(float(p["drill_stop_after"]))
        for k, v in sorted(want.items()):
            if got.get(k) != v:
                out.append("{}/c5run_params.csv {} {!r}, expected {!r}".format(base, k, got.get(k), v))
        if kind == "smoke":
            rows = os.path.join(folder, base, "c5run_real.csv")
            nok = 0
            if os.path.isfile(rows):
                with open(rows, newline="") as fh:
                    nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
            if f["ran"] is None or nok != f["ran"] or f["errors"] != 0:
                out.append("SMX: {} smoke rows end ok, tasks run {}, errored {}".format(nok, f["ran"], f["errors"]))
    for d in s["resume_dirs"]:
        if os.path.basename(d.rstrip("/")) not in f["resume_read"]:
            out.append("no 'read' line for resume folder " + d)
    return out


def f2_problem_c5(s, item, folder, rel, f):
    """F2X (drill and shard): None, or the halt reason."""
    csvs = glob.glob(os.path.join(folder, "c5run-*", "c5run_real.csv"))
    if len(csvs) != 1:
        return "F2X: {} c5run-*/c5run_real.csv file(s) in {}, expected 1".format(len(csvs), rel)
    with open(csvs[0], newline="") as fh:
        nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
    say("  F2X: {} rows end ok; runner 'tasks run by this job' {}, errored {}, F1 failures {}, complete {}".format(
        nok, f["ran"], f["errors"], f["f1"], f["complete"]))
    if f["ran"] is None or nok != f["ran"] or f["errors"] != 0 or f["f1"] != 0:
        return ("F2X: download incomplete or summary missing: {} rows end ok in {}, tasks run {}, errored {}, "
                "F1 failures {}".format(nok, rel, f["ran"], f["errors"], f["f1"]))
    if f["exit"] == 0 and (not f["notstopped"] or f["complete"] is None or f["complete"][0] != f["complete"][1]):
        return "F2X: exit 0 without 'not stopped: every task ran' and N of N complete rows in {}".format(rel)
    if f["exit"] == 5 and not f["stopped"]:
        return "F2X: exit 5 without 'STOPPED by --stop-after' in {}".format(rel)
    return None


def header_problems_sizetest(s, item, f, folder):
    """R1Z (shard and smoke), with SMZ's row count for a smoke."""
    p = profile_of(s, item)
    e = p["expect"]
    out = []
    if f["python"] != e["python"]:
        out.append("python {}, expected {}".format(f["python"], e["python"]))
    if f["numpy"] != e["numpy"]:
        out.append("numpy {}, expected {}".format(f["numpy"], e["numpy"]))
    for _, k in FAMILY_PINS["sizetest"]:
        if f["hashes"].get(k) != e[k]:
            out.append("{} {}, expected {}".format(k, f["hashes"].get(k), e[k]))
    if f["plan_sha"] != p["plan_sha256"]:
        out.append("plan sha256 {}, expected {}".format(f["plan_sha"], p["plan_sha256"]))
    if os.path.basename((f["throughput"] or "").rstrip("/")) != os.path.basename(p["throughput"].rstrip("/")):
        out.append("throughput {}, expected {}".format(f["throughput"], p["throughput"]))
    if f["pc"] != "PASS":
        out.append("PC {}, expected PASS".format(f["pc"]))
    smoke = item["kind"] == "smoke"
    S, K = (0, 1) if smoke else (item["shard"], item["nshards"])
    mode = "smoke" if smoke else "e1"
    if (f["mode"], f["shard"], f["nshards"]) != (mode, S, K):
        out.append("mode {} shard {} of {}, expected {} shard {} of {}".format(
            f["mode"], f["shard"], f["nshards"], mode, S, K))
    base = os.path.basename((f["rundir"] or "").rstrip("/"))
    tag = "" if K == 1 else "-s{}of{}".format(S, K)
    if not re.fullmatch(r"sizetest-" + mode + r"-\d{8}-\d{6}" + re.escape(tag), base):
        out.append("files {}, expected a basename sizetest-{}-YYYYMMDD-HHMMSS{}".format(f["rundir"], mode, tag))
    subs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(folder, "sizetest-*")) if os.path.isdir(d))
    if subs != [base]:
        out.append("fetched sizetest-* folder(s) {}, expected exactly [{}]".format(subs, base))
    else:
        pp = os.path.join(folder, base, "sizetest_params.csv")
        got = {}
        if os.path.isfile(pp):
            with open(pp, newline="") as fh:
                got = dict((r[0], r[1]) for r in csv.reader(fh) if r)
        want = {"mode": mode, "shard": str(S), "nshards": str(K), "workers": str(p["workers"]),
                "plan_sha256": p["plan_sha256"], "script_sha256": e["sizetest_sha256"],
                "calprec2_sha256": e["calprec2_sha256"], "costprobe2_sha256": e["costprobe2_sha256"]}
        if not smoke:
            want["stop_after"] = repr(float(p["stop_after"]))
        for k, v in sorted(want.items()):
            if got.get(k) != v:
                out.append("{}/sizetest_params.csv {} {!r}, expected {!r}".format(base, k, got.get(k), v))
        if smoke:
            rows = os.path.join(folder, base, "sizetest_e1.csv")
            nok = 0
            if os.path.isfile(rows):
                with open(rows, newline="") as fh:
                    nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
            if f["ran"] is None or nok != f["ran"] or f["errors"] != 0:
                out.append("SMZ: {} smoke rows end ok, tasks run {}, errored {}".format(nok, f["ran"], f["errors"]))
    for d in s["resume_dirs"]:
        if os.path.basename(d.rstrip("/")) not in f["resume_read"]:
            out.append("no 'read' line for resume folder " + d)
    return out


def f2_problem_sizetest(s, item, folder, rel, f):
    """F2Z (shard): None, or the halt reason."""
    csvs = glob.glob(os.path.join(folder, "sizetest-e1-*", "sizetest_e1.csv"))
    if len(csvs) != 1:
        return "F2Z: {} sizetest-e1-*/sizetest_e1.csv file(s) in {}, expected 1".format(len(csvs), rel)
    with open(csvs[0], newline="") as fh:
        nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
    say("  F2Z: {} rows end ok; runner summary 'tasks run by this job' {}, errored {}".format(
        nok, f["ran"], f["errors"]))
    if f["ran"] is None or nok != f["ran"] or f["errors"] != 0:
        return ("F2Z: download incomplete or summary missing: {} rows end ok in {}, tasks run {}, errored "
                "{}".format(nok, rel, f["ran"], f["errors"]))
    if f["exit"] == 0 and not f["notstopped"]:
        return "F2Z: exit 0 without 'not stopped: every task ran' in {}".format(rel)
    if f["exit"] == 5 and not f["stopped"]:
        return "F2Z: exit 5 without 'STOPPED by --stop-after' in {}".format(rel)
    return None


def read_runner_calprec2(text):
    """R1C, R1F, F2C: the lines calprec2.py prints (header after its banner, summary at the end)."""
    f = {"exit": None, "python": None, "numpy": None, "hashes": {}, "mode": None, "rows": None,
         "shard": None, "nshards": None, "throughput": None, "rundir": None, "resume_read": set(),
         "ran": None, "errors": None, "stopped": False, "notstopped": False, "completed": None, "smoke": None}
    if text is None:
        return f
    ex = re.findall(r"kgrun runner: exit code (-?\d+)", text)
    if ex:
        f["exit"] = int(ex[-1])
    i = text.find("CBO-GAP calprec2")
    body = text[i:] if i >= 0 else ""
    m = re.search(r"^  python   (\S+)", body, re.M)
    if m:
        f["python"] = m.group(1)
    m = re.search(r"^  numpy    (\S+)\s*$", body, re.M)
    if m:
        f["numpy"] = m.group(1)
    m = re.search(r"^  script   sha256 ([0-9a-f]{64})\s*$", body, re.M)
    if m:
        f["hashes"]["calprec2_sha256"] = m.group(1)
    m = re.search(r"^  costprobe2\.py sha256 ([0-9a-f]{64})\s*$", body, re.M)
    if m:
        f["hashes"]["costprobe2_sha256"] = m.group(1)
    m = re.search(r"^  mode     (\w+)   rows (\S+)   shard (\d+) of (\d+)", body, re.M)
    if m:
        f["mode"], f["rows"], f["shard"], f["nshards"] = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    m = re.search(r"^  throughput  (\S+)\s*$", body, re.M)
    if m:
        f["throughput"] = m.group(1)
    m = re.findall(r"^files  (\S+)\s*$", body, re.M)
    if m:
        f["rundir"] = m[-1]
    for path in re.findall(r"^  read (\S+): shard \S+ of \S+, \d+ rows, \d+ complete\s*$", body, re.M):
        f["resume_read"].add(os.path.basename(path.rstrip("/")))
    m = re.findall(r"^tasks run by this job: (\d+)   task execution", body, re.M)
    if m:
        f["ran"] = int(m[-1])
        f["completed"] = f["ran"]
    m = re.findall(r"^errored or timed-out tasks: (\d+)\s*$", body, re.M)
    if m:
        f["errors"] = int(m[-1])
    f["stopped"] = bool(re.search(r"^STOPPED by --stop-after", body, re.M))
    f["notstopped"] = bool(re.search(r"^not stopped: every phase ran\s*$", body, re.M))
    return f


def calprec2_dirs(folder):
    return sorted(os.path.basename(d) for d in glob.glob(os.path.join(folder, "calprec2-*")) if os.path.isdir(d))


def header_problems_calprec2(s, item, f, folder):
    """R1C (shard) and R1F (finalize)."""
    p = profile_of(s, item)
    e = p["expect"]
    out = []
    if f["python"] != e["python"]:
        out.append("python {}, expected {}".format(f["python"], e["python"]))
    if f["numpy"] != e["numpy"]:
        out.append("numpy {}, expected {}".format(f["numpy"], e["numpy"]))
    for _, k in FAMILY_PINS["calprec2"]:
        if f["hashes"].get(k) != e[k]:
            out.append("{} {}, expected {}".format(k, f["hashes"].get(k), e[k]))
    base = os.path.basename((f["rundir"] or "").rstrip("/"))
    subs = calprec2_dirs(folder)
    if item["kind"] == "finalize":
        if f["mode"] != "finalize" or f["rows"] != p["rows"]:
            out.append("mode {} rows {}, expected finalize rows {}".format(f["mode"], f["rows"], p["rows"]))
        if not re.fullmatch(r"calprec2-finalize-\d{8}-\d{6}", base):
            out.append("files {}, expected a basename calprec2-finalize-YYYYMMDD-HHMMSS".format(f["rundir"]))
        if subs != [base]:
            out.append("fetched calprec2-* folder(s) {}, expected exactly [{}]".format(subs, base))
        elif not os.path.isfile(os.path.join(folder, base, "calprec2_beta.csv")):
            out.append("{} has no calprec2_beta.csv".format(base))
        want = set(os.path.basename(d.rstrip("/")) for d in s["data_dirs"])
        if f["resume_read"] != want:
            out.append("folders read {}, expected the finalize inputs {}".format(sorted(f["resume_read"]),
                                                                              sorted(want)))
        return out
    S, K = item["shard"], item["nshards"]
    if (f["mode"], f["rows"], f["shard"], f["nshards"]) != ("full", p["rows"], S, K):
        out.append("mode {} rows {} shard {} of {}, expected full rows {} shard {} of {}".format(
            f["mode"], f["rows"], f["shard"], f["nshards"], p["rows"], S, K))
    want_thr = os.path.basename(p["throughput"].rstrip("/"))
    if os.path.basename((f["throughput"] or "").rstrip("/")) != want_thr:
        out.append("throughput {}, expected {}".format(f["throughput"], want_thr))
    tag = "" if K == 1 else "-s{}of{}".format(S, K)
    if not re.fullmatch(r"calprec2-full-\d{8}-\d{6}" + re.escape(tag), base):
        out.append("files {}, expected a basename calprec2-full-YYYYMMDD-HHMMSS{}".format(f["rundir"], tag))
    if subs != [base]:
        out.append("fetched calprec2-* folder(s) {}, expected exactly [{}]".format(subs, base))
    else:
        pp = os.path.join(folder, base, "calprec2_params.csv")
        got = {}
        if os.path.isfile(pp):
            with open(pp, newline="") as fh:
                got = dict((r[0], r[1]) for r in csv.reader(fh) if r)
        want = {"mode": "full", "rows": p["rows"], "shard": str(S), "nshards": str(K),
                "workers": str(p["workers"]), "stop_after": repr(float(p["stop_after"])),
                "ceiling": repr(ceiling_of(p)), "script_sha256": e["calprec2_sha256"],
                "costprobe2_sha256": e["costprobe2_sha256"]}
        for k, v in sorted(want.items()):
            if got.get(k) != v:
                out.append("{}/calprec2_params.csv {} {!r}, expected {!r}".format(base, k, got.get(k), v))
    for d in s["resume_dirs"]:
        if os.path.basename(d.rstrip("/")) not in f["resume_read"]:
            out.append("no 'read' line for resume folder " + d)
    return out


def f2_problem_calprec2(s, item, folder, rel, f):
    """F2C (shard) and F2F (finalize): None, or the halt reason."""
    p = profile_of(s, item)
    if item["kind"] == "finalize":
        hits = glob.glob(os.path.join(folder, "calprec2-finalize-*", "calprec2_beta.csv"))
        if len(hits) != 1:
            return "F2F: {} calprec2_beta.csv file(s) in {}, expected 1".format(len(hits), rel)
        with open(hits[0], newline="") as fh:
            rows = list(csv.DictReader(fh))
        cells = [(r.get("module"), r.get("objective"), r.get("d"), r.get("law"), r.get("tau0")) for r in rows]
        inc = [r for r in rows if (r.get("label") or "").startswith("incomplete")]
        say("  F2F: {} rows, {} distinct cells, {} incomplete; expected {} cells".format(
            len(rows), len(set(cells)), len(inc), p["cells"]))
        if len(rows) != p["cells"] or len(set(cells)) != len(rows) or inc:
            return "F2F: calprec2_beta.csv in {} has {} rows, {} distinct cells, {} incomplete; expected {}".format(
                rel, len(rows), len(set(cells)), len(inc), p["cells"])
        return None
    csvs = glob.glob(os.path.join(folder, "calprec2-full-*", "calprec2_tasks.csv"))
    if len(csvs) != 1:
        return "F2C: {} calprec2-full-*/calprec2_tasks.csv file(s) in {}, expected 1".format(len(csvs), rel)
    with open(csvs[0], newline="") as fh:
        nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
    say("  F2C: {} rows end ok; runner summary 'tasks run by this job' {}, errored {}".format(
        nok, f["ran"], f["errors"]))
    if f["ran"] is None or nok != f["ran"] or f["errors"] != 0:
        return ("F2C: download incomplete or summary missing: {} rows end ok in {}, tasks run {}, errored "
                "{}".format(nok, rel, f["ran"], f["errors"]))
    if f["exit"] == 0 and not f["notstopped"]:
        return "F2C: exit 0 without 'not stopped: every phase ran' in {}".format(rel)
    if f["exit"] == 5 and not f["stopped"]:
        return "F2C: exit 5 without 'STOPPED by --stop-after' in {}".format(rel)
    return None


def read_runner_rerun(text):
    f = {"exit": None, "python": None, "numpy": None, "hashes": {}, "plan_sha": None, "mode": None,
         "rundir": None, "smoke": None, "resume_read": set(), "completed": None}
    if text is None:
        return f
    ex = re.findall(r"kgrun runner: exit code (-?\d+)", text)
    if ex:
        f["exit"] = int(ex[-1])
    m = re.search(r"^  python   (\S+)   numpy (\S+)\s*$", text, re.M)
    if m:
        f["python"], f["numpy"] = m.group(1), m.group(2)
    for k, v in re.findall(r"^  (rerun_sha256|rerunlib_sha256|costprobe2_sha256)\s+([0-9a-f]{64})\s*$",
                           text, re.M):
        f["hashes"][k] = v
    m = re.search(r"rerun_plan\.csv sha256 ([0-9a-f]{64})", text)
    if m:
        f["plan_sha"] = m.group(1)
    m = re.search(r"\(mode (\w+)\)", text)
    if m:
        f["mode"] = m.group(1)
    m = re.search(r"^  run dir  (\S+)\s*$", text, re.M)
    if m:
        f["rundir"] = m.group(1)
    sm = re.findall(r"D-SMOKE (PASS|FAIL)", text)
    if sm:
        f["smoke"] = sm[-1]
    for path in re.findall(r"resume: read (\S+)  completed tasks \d+", text):
        f["resume_read"].add(os.path.basename(path.rstrip("/")))
    m = re.findall(r"completed (\d+)  errors \d+  not started \d+", text)
    if m:
        f["completed"] = int(m[-1])
    return f


def shard_problems(item, rundir, folder):
    """R1 (a) to (c): the fetched output belongs to shard S of K."""
    p = []
    base = os.path.basename((rundir or "").rstrip("/"))
    want = r"rerun-s{}of{}-\d{{8}}-\d{{6}}".format(item["shard"], item["nshards"])
    if not re.fullmatch(want, base):
        p.append("run dir {}, expected a basename rerun-s{}of{}-YYYYMMDD-HHMMSS".format(
            rundir, item["shard"], item["nshards"]))
    subs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(folder, "rerun-*")) if os.path.isdir(d))
    if subs != [base]:
        p.append("fetched rerun-* folder(s) {}, expected exactly [{}]".format(subs, base))
        return p
    pp = os.path.join(folder, base, "rerun_params.csv")
    got = {}
    if os.path.isfile(pp):
        with open(pp, newline="") as fh:
            got = {r["name"]: r["value"] for r in csv.DictReader(fh)}
    for k in ("shard", "nshards"):
        if got.get(k) != str(item[k]):
            p.append("{}/rerun_params.csv {} {}, expected {}".format(base, k, got.get(k), item[k]))
    return p


def header_problems(s, item, f, folder):
    """R1 (rerun), R1C/R1F (calprec2), R1Z (sizetest) or R1X (c5)."""
    if family_of(s, item) == "c5":
        return header_problems_c5(s, item, f, folder)
    if family_of(s, item) == "sizetest":
        return header_problems_sizetest(s, item, f, folder)
    if family_of(s, item) == "calprec2":
        return header_problems_calprec2(s, item, f, folder)
    prof = profile_of(s, item)
    e = prof["expect"]
    p = []
    if f["python"] != e["python"]:
        p.append("python {}, expected {}".format(f["python"], e["python"]))
    if f["numpy"] != e["numpy"]:
        p.append("numpy {}, expected {}".format(f["numpy"], e["numpy"]))
    for _, k in PINNED:
        if f["hashes"].get(k) != e[k]:
            p.append("{} {}, expected {}".format(k, f["hashes"].get(k), e[k]))
    if f["plan_sha"] != prof["plan_sha256"]:
        p.append("plan sha256 {}, expected {}".format(f["plan_sha"], prof["plan_sha256"]))
    want = "smoke" if item["kind"] == "smoke" else "run"
    if f["mode"] != want:
        p.append("mode {}, expected {}".format(f["mode"], want))
    if item["kind"] == "shard":
        p.extend(shard_problems(item, f["rundir"], folder))
    for d in s["resume_dirs"]:
        if os.path.basename(d.rstrip("/")) not in f["resume_read"]:
            p.append("no 'resume: read' line for " + d)
    return p


def f2_problem(s, item, folder, rel, f):
    """F2 (rerun shard), F2C/F2F (calprec2), F2Z (sizetest shard) or F2X (c5 drill, shard): None, else the halt
    reason."""
    if family_of(s, item) == "c5":
        return f2_problem_c5(s, item, folder, rel, f)
    if family_of(s, item) == "sizetest":
        return f2_problem_sizetest(s, item, folder, rel, f)
    if family_of(s, item) == "calprec2":
        return f2_problem_calprec2(s, item, folder, rel, f)
    csvs = glob.glob(os.path.join(folder, "rerun-*", "rerun_real.csv"))
    if len(csvs) != 1:
        return "F2: {} rerun-*/rerun_real.csv file(s) in {}, expected 1".format(len(csvs), rel)
    with open(csvs[0], newline="") as fh:
        nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
    say("  F2: {} rows end ok; runner summary completed {}".format(nok, f["completed"]))
    if f["completed"] is None or nok != f["completed"]:
        return ("F2: download incomplete or summary missing: {} rows end ok in {}, runner summary "
                "completed {}".format(nok, rel, f["completed"]))
    return None


def do_fetch(ctx, kstatus):
    s = ctx.s
    item = s["queue"][s["index"]]
    job = s["job"]
    say("FETCH  {} (kaggle status {})".format(job, kstatus))
    pattern = os.path.join(ROOT, "runs", job + "-kaggle-*")
    pre = set(glob.glob(pattern))
    if pre:
        raise Halt("L3: {} already has a folder in runs/ ({}); a second fetch would put its rows in two "
                   "folders".format(job, ", ".join(sorted(pre))))
    fetchlog = free_log(job)
    rc, _ = kgrun(["fetch", "--job", job, "--user", s["kaggle_user"]], fetchlog)
    new = sorted(set(glob.glob(pattern)) - pre)
    rels = [os.path.relpath(x, ROOT) for x in new]
    rescue(rels + [fetchlog])
    if rc != 0:
        raise Halt("F1: kgrun fetch exit {}; folder(s) {} not committed (rescue artifact)".format(
            rc, ", ".join(rels) or "none"), [fetchlog])
    if len(new) != 1:
        raise Halt("F1: {} new folder(s) for {}, expected 1: {}".format(len(new), job, rels), [fetchlog])
    folder, rel = new[0], rels[0]
    bad = verify_manifest(folder)
    if bad:
        raise Halt("F1: {} fails its manifest: {}".format(rel, "; ".join(bad)), [fetchlog])
    files, _ = list_files(folder)
    big = [x for x in files if os.path.getsize(os.path.join(folder, x)) > s["max_file_mb"] * 1048576]
    if big:
        raise Halt("F1: file(s) above {} MB in {}: {}".format(s["max_file_mb"], rel, big), [fetchlog])
    say("  {}: manifest verified, {} files".format(rel, len(files)))

    fam = family_of(s, item)
    f = read_runner(runner_text(folder, job), fam)
    say("  runner exit {}  python {}  numpy {}  mode {}  run dir {}  D-SMOKE {}  completed {}".format(
        f["exit"], f["python"], f["numpy"], f["mode"], f["rundir"], f["smoke"], f["completed"]))
    s["attempts"].setdefault(item["id"], []).append({
        "attempt": s["attempt"], "job": job, "folder": rel, "kaggle_status": kstatus,
        "runner_exit": f["exit"], "completed": f["completed"], "d_smoke": f["smoke"],
        "resume_dirs": list(s["resume_dirs"]), "fetched_run": ctx.run, "fetched_at": now()})
    paths = [rel, fetchlog]
    code = f["exit"]
    probs = header_problems(s, item, f, folder)
    if code is None:
        raise Halt("R2: no 'kgrun runner: exit code' line in {} (killed, cap, pre-emption or "
                   "cancelled)".format(rel), paths)
    if code not in (0, 5):
        raise Halt("R2: runner exit code {} in {}{}".format(
            code, rel, "; R1: " + "; ".join(probs) if probs else ""), paths)
    if probs:
        raise Halt("R1: header of {}: {}".format(rel, "; ".join(probs)), paths)
    if item["kind"] == "finalize" and code != 0:
        raise Halt("R2C: finalize {} exit {}; only 0 is accepted".format(rel, code), paths)
    if item["kind"] in ("shard", "finalize", "drill"):
        bad = f2_problem(s, item, folder, rel, f)
        if bad:
            raise Halt(bad, paths)
    if item["kind"] == "smoke":
        if code != 0 or f["smoke"] != "PASS":
            raise Halt("R2: smoke {} exit {}, D-SMOKE {}; no shard of set {} launches".format(
                rel, code, f["smoke"], item["set"]), paths)
    elif code == 5:
        if not f["completed"]:
            raise Halt("R2: G-STOP with completed {} in {}: no progress".format(f["completed"], rel), paths)
        if s["attempt"] >= s["max_attempts"]:
            raise Halt("R2: G-STOP at attempt {} of {}: attempt cap".format(s["attempt"], s["max_attempts"]),
                       paths)

    done_job = job
    if code == 0:
        note = "runner exit 0" + (", D-SMOKE PASS" if item["kind"] == "smoke" else "")
        s["index"] += 1
        s["attempt"] = 1
        s["resume_dirs"] = []
        s["status"] = "DONE" if s["index"] == len(s["queue"]) else "READY"
    else:
        note = "runner exit 5 (G-STOP), completed {}; next attempt resumes".format(f["completed"])
        s["attempt"] += 1
        s["resume_dirs"] = [r["folder"] for r in s["attempts"][item["id"]] if holds_rows(r["folder"], fam)]
        s["status"] = "READY"
    s["job"], s["args"], s["data_dirs"] = "", "", []
    s["anomaly"] = None
    history(s, ctx.run, "fetched", "{}: {}; now {}".format(rel, note, s["status"]))
    say("  " + note + "; state now " + s["status"])
    dlog = driver_log(done_job, "fetched")
    r = publish(ctx, paths + [dlog], "rerun queue: {} runner exit code {}, {} ({}, K6)".format(
        done_job, code, rel, item["ledger"]))
    gh_summary(s)
    if r != "ok":
        print("::error title=rerun queue::{} was fetched but could not be pushed ({}); main still reads "
              "RUNNING. The workflow disables itself. Release with repoll to fetch again; do not commit "
              "the rescue copy.".format(done_job, r))
        return 3
    if s["status"] == "DONE":
        gh_output("disable", "true")
    return 0


# --------------------------------------------------------------------------
# subcommands
# --------------------------------------------------------------------------

def tick(a):
    say("=" * 78)
    say("rerunq tick  run {}  {}".format(a.run_id, now()))
    say("  python {}".format(sys.version.split()[0]))
    say("  state file {}".format(STATE_REL))
    rc, out = git(["status", "--porcelain", "--untracked-files=all"])
    if out:
        say("  checkout not clean; cannot confirm the state:\n" + out)
        return 1
    git(["fetch", "-q", "origin", "main"])
    head = git(["rev-parse", "HEAD"])[1]
    tip = git(["rev-parse", "origin/main"])[1]
    if head != tip:
        say("  HEAD {} is not main's tip {}; cannot confirm the state; nothing done".format(head, tip))
        return 0
    git(["branch", "--set-upstream-to=origin/main", "main"], check=False)
    with open(STATE, "rb") as fh:
        base = fh.read()
    try:
        s = json.loads(base.decode("utf-8"))
        validate(s)
    except ValueError as e:
        say("  state unreadable: {}".format(e))
        return 1
    say("  state {}  item {}  attempt {}  job {}".format(s["status"], s["index"], s["attempt"], s["job"] or "-"))
    say("  definition {} (sha256 {})".format(s["definition"].get("path"), s["definition"].get("sha256")))
    for name, p in sorted(s["profiles"].items()):
        fam = p["family"]
        if fam == "rerun":
            say("  profile {} [rerun]  plan {} (rerun_plan.csv {})  timing {}  workers {}".format(
                name, p["plan"], p["plan_sha256"], ", ".join(p["timing"]), p["workers"]))
        elif fam == "c5":
            say("  profile {} [c5]  timing {}  beta table {}  rerun plan {}  drill stop-after {}  workers {}".format(
                name, ", ".join(p["timing"]), p["beta_table"], p["rerun_plan"], p["drill_stop_after"], p["workers"]))
        elif fam == "sizetest":
            say("  profile {} [sizetest]  plan {} ({} {})  throughput {}  stop-after {}  workers {}".format(
                name, p["plan"], SIZETEST_PLAN_CSV, p["plan_sha256"], p["throughput"], p["stop_after"],
                p["workers"]))
        else:
            say("  profile {} [calprec2]  rows {}  throughput {}  stop-after {}  ceiling {}  workers {}  "
                "cells {}".format(name, p["rows"], p["throughput"], p["stop_after"], ceiling_of(p),
                                  p["workers"], p["cells"]))
        say("    expect python {} numpy {}; {}".format(p["expect"]["python"], p["expect"]["numpy"], "; ".join(
            "{} {}".format(k, p["expect"][k][:8]) for _, k in FAMILY_PINS[fam])))
    say("  kaggle user {}  max attempts {}  max file {} MB".format(
        s["kaggle_user"], s["max_attempts"], s["max_file_mb"]))
    say("  L4 control kernel {}/cbo-{}  K1 ABSENT gap {} min".format(s["kaggle_user"], CONTROL_JOB, CHECK_GAP_MIN))
    say("=" * 78)
    ctx = Ctx(s, base, a.run_id)
    if s["status"] == "HALTED":
        say("HALTED: " + s["halt_reason"])
        print("::error title=rerun queue HALTED::" + s["halt_reason"])
        gh_summary(s)
        return 3
    if s["status"] == "DONE":
        say("DONE: every item complete")
        gh_summary(s)
        gh_output("disable", "true")
        return 0
    try:
        if s["status"] == "READY":
            return do_launch(ctx)
        if s["status"] == "LAUNCHING":
            return do_recover(ctx)
        return do_poll(ctx)
    except Halt as h:
        return do_halt(ctx, h.reason, h.paths)
    except Anomaly as e:
        return do_anomaly(ctx, e.kind, e.detail)


def load():
    with open(STATE, "rb") as fh:
        s = json.loads(fh.read().decode("utf-8"))
    validate(s)
    return s


def folder_ok(rel):
    """LD: a committed run folder whose sha256.txt verifies."""
    path = os.path.join(ROOT, rel)
    if not os.path.isdir(path):
        return "{} does not exist".format(rel)
    bad = verify_manifest(path)
    return "{} fails its manifest: {}".format(rel, "; ".join(bad)) if bad else None


def load_definition(a):
    """LD: archive a DONE state and start the queue a committed definition describes."""
    with open(STATE, "rb") as fh:
        old = fh.read()
    cur = json.loads(old.decode("utf-8"))
    n = len(cur.get("queue", []))
    if cur.get("status") != "DONE" or cur.get("index") != n:
        raise SystemExit("load needs a DONE state; it is {} at item {} of {}".format(
            cur.get("status"), cur.get("index"), n))
    rc, out = git(["status", "--porcelain", "--", a.definition], check=False)
    if rc != 0 or out:
        raise SystemExit("the definition {} must be committed and unmodified".format(a.definition))
    with open(os.path.join(ROOT, a.definition), "rb") as fh:
        raw = fh.read()
    d = json.loads(raw.decode("utf-8"))
    for k in ("name", "kaggle_user", "max_attempts", "max_file_mb", "profiles", "queue"):
        if k not in d:
            raise SystemExit("definition has no key " + k)
    probe = {"profiles": d["profiles"], "queue": d["queue"]}
    try:
        validate_definition(probe)
    except ValueError as e:
        raise SystemExit("definition refused: {}".format(e))
    for name, p in sorted(d["profiles"].items()):
        fam = p["family"]
        if fam == "rerun":
            dirs = [p["plan"]] + list(p["timing"])
        elif fam == "c5":
            dirs = list(p["timing"]) + [p["beta_table"], p["rerun_plan"]]
        elif fam == "sizetest":
            dirs = [p["plan"], p["throughput"]]
        else:
            dirs = [p["throughput"]]
        for rel in dirs:
            why = folder_ok(rel)
            if why:
                raise SystemExit("profile {}: {}".format(name, why))
        if fam == "sizetest":
            pf = os.path.join(ROOT, p["plan"], SIZETEST_PLAN_CSV)
            got = sha256_of(pf) if os.path.isfile(pf) else None
            if got != p["plan_sha256"]:
                raise SystemExit("profile {}: {}/{} sha256 {}, the definition says {} (LDZ)".format(
                    name, p["plan"], SIZETEST_PLAN_CSV, got, p["plan_sha256"]))
            print("  profile {}: {}/{} sha256 as defined".format(name, p["plan"], SIZETEST_PLAN_CSV))
        for fname, key in FAMILY_PINS[fam]:
            p["expect"][key] = sha256_of(os.path.join(SCRIPTS, fname))
            print("  profile {}: pinned scripts/{} {}".format(name, fname, p["expect"][key]))
    old_name = (cur.get("definition") or {}).get("name") or "rerun-queue"
    if not os.path.isdir(os.path.join(ROOT, ARCHIVE_DIR)):
        os.makedirs(os.path.join(ROOT, ARCHIVE_DIR))
    arel = "{}/{}-{}-done.json".format(ARCHIVE_DIR, stamp(), old_name)
    with open(os.path.join(ROOT, arel), "xb") as fh:
        fh.write(old)
        fh.flush()
        os.fsync(fh.fileno())
    print("  archived the DONE state ({} bytes) to {}".format(len(old), arel))
    s = {"schema": 2, "kaggle_user": d["kaggle_user"], "profiles": d["profiles"],
         "max_attempts": d["max_attempts"], "max_file_mb": d["max_file_mb"], "queue": d["queue"],
         "status": "READY", "index": 0, "attempt": 1, "resume_dirs": [], "job": "", "args": "",
         "data_dirs": [], "anomaly": None, "halt_reason": "", "kernel_check": None, "attempts": {},
         "history": [],
         "definition": {"name": d["name"], "path": a.definition,
                        "sha256": hashlib.sha256(raw).hexdigest(), "archived_previous": arel}}
    history(s, "manual", "load", "{}; previous state archived to {}; {}".format(a.definition, arel, a.note))
    validate(s)
    write_state(s)
    show(a)
    print("\nwritten: {} and {}. Commit both and push, then enable the drivers.".format(STATE_REL, arel))
    return 0


def next_wake(a):
    """NW. Reads only."""
    s = load()
    st = s["status"]
    if st in ("HALTED", "DONE"):
        print("none {}".format(st))
    elif st == "RUNNING":
        print("{} RUNNING {}".format(int(a.max), s["job"]))
    else:
        print("{} {}".format(int(a.min), st))
    return 0


def show(a):
    s = load()
    print("status   {}".format(s["status"]))
    if s["index"] < len(s["queue"]):
        print("item     {} {}  attempt {}  job {}".format(s["index"], s["queue"][s["index"]]["id"],
                                                         s["attempt"], s["job"] or "-"))
    print("resume   {}".format(",".join(s["resume_dirs"]) or "-"))
    print("anomaly  {}".format(s["anomaly"] or "-"))
    print("halt     {}".format(s["halt_reason"] or "-"))
    kc = s["kernel_check"]
    print("check    {}".format("{} {} ({}) at {}, by {}".format(kc["job"], kc["status"], kc["class"], kc["at"], kc["by"])
                               if kc else "-"))
    print("attempts")
    for item in s["queue"]:
        for r in s["attempts"].get(item["id"], []):
            print("  {:<11} a{}  exit {}  completed {}  {}".format(item["id"], r["attempt"], r["runner_exit"],
                                                                  r["completed"], r["folder"]))
    print("history (last 12)")
    for h in s["history"][-12:]:
        print("  {}  {:<9} {:<26} {}".format(h["at"], h["event"], h["job"] or h["item"], h["note"]))
    return 0


def verify(a):
    """Re-run F1 (manifest), R1, R2 and F2 on the folder of the last recorded attempt of the current
    item, as do_fetch would after a fetch. Reads only; writes nothing, changes no state."""
    s = load()
    if s["status"] != "HALTED":
        raise SystemExit("verify needs status HALTED; it is " + s["status"])
    item = s["queue"][s["index"]]
    recs = s["attempts"].get(item["id"], [])
    if not recs or recs[-1]["attempt"] != s["attempt"]:
        raise SystemExit("no fetched folder recorded for {} attempt {}".format(item["id"], s["attempt"]))
    rec = recs[-1]
    rel = rec["folder"]
    folder = os.path.join(ROOT, rel)
    say("VERIFY  {} attempt {}  job {}  folder {}".format(item["id"], s["attempt"], rec["job"], rel))
    probs = ["F1: " + x for x in verify_manifest(folder)]
    if not probs:
        say("  F1: manifest verified, {} files".format(len(list_files(folder)[0])))
    f = read_runner(runner_text(folder, rec["job"]), family_of(s, item))
    say("  runner exit {}  python {}  numpy {}  mode {}  run dir {}  D-SMOKE {}  completed {}".format(
        f["exit"], f["python"], f["numpy"], f["mode"], f["rundir"], f["smoke"], f["completed"]))
    probs += ["R1: " + x for x in header_problems(s, item, f, folder)]
    if f["exit"] != 0:
        probs.append("R2: runner exit {}, next-item needs 0".format(f["exit"]))
    if item["kind"] in ("shard", "finalize", "drill"):
        bad = f2_problem(s, item, folder, rel, f)
        if bad:
            probs.append(bad)
    elif f["smoke"] != "PASS":
        probs.append("R2: D-SMOKE {}".format(f["smoke"]))
    for x in probs:
        say("  FAIL " + x)
    say("VERIFY {}: {}".format("PASS" if not probs else "FAIL", rel))
    return 0 if not probs else 3


def halted_job(s):
    """K1: the job a halt leaves: the recorded one, else the current item and attempt's name."""
    return s["job"] or job_spec(s)[0]


def halted_at(s):
    for h in reversed(s["history"]):
        if h["event"] == "halt":
            return datetime.datetime.fromisoformat(h["at"])
    return None


def check_refusal(s):
    """K1: None when next-attempt may proceed, else the reason it may not."""
    kc = s["kernel_check"]
    job = halted_job(s)
    if kc is None:
        return ("no kernel check since the halt for {j}. Run 'python scripts/rerunq.py check --note ...' on "
                "the laptop, or pass --checked-by-hand STATUS after looking at Kaggle yourself (K1)".format(j=job))
    if kc["job"] != job:
        return "the kernel check is for {}, not {} (K1)".format(kc["job"], job)
    if kc["class"] == "WAIT":
        return ("{} is {} on Kaggle: a new attempt would run the same shard twice. Wait for it, then release "
                "with repoll (K1)".format(job, kc["status"]))
    if kc["class"] == "FINISHED":
        return None
    if kc["class"] == "ABSENT":
        t0 = halted_at(s)
        if t0 is None:
            return None
        gap = (datetime.datetime.fromisoformat(kc["at"]) - t0).total_seconds() / 60.0
        if gap < CHECK_GAP_MIN:
            return ("{} was seen ABSENT {:.0f} minutes after the halt; K1 needs at least {}. Check again "
                    "later".format(job, gap, CHECK_GAP_MIN))
        return None
    return "the kernel check for {} gave {} ({}); not accepted (K1)".format(job, kc["status"], kc["class"])


def manual(a):
    s = load()
    if a.cmd == "halt":
        if s["status"] == "DONE":
            raise SystemExit("the queue is DONE; nothing to halt")
        s["status"] = "HALTED"
        s["halt_reason"] = "manual: " + a.note
        s["kernel_check"] = None
        history(s, "manual", "halt", a.note)
    elif a.cmd == "check":
        if s["status"] != "HALTED":
            raise SystemExit("check needs status HALTED; it is " + s["status"])
        job = halted_job(s)
        try:
            cls, detail = kernel_status(s, job)
        except Halt as h:
            raise SystemExit("kernel check failed, nothing recorded: " + h.reason)
        s["kernel_check"] = {"job": job, "class": cls, "status": detail, "at": now(), "by": "kgrun status"}
        history(s, "manual", "kernel-check", "{} {} ({}): {}".format(job, detail, cls, a.note))
    else:
        if s["status"] != "HALTED":
            raise SystemExit("release needs status HALTED; it is " + s["status"])
        item = s["queue"][s["index"]]
        if a.mode == "start":
            if s["job"]:
                raise SystemExit("a launch intent is recorded for {}; use repoll or next-attempt".format(s["job"]))
            s["status"] = "READY"
        elif a.mode == "repoll":
            if not s["job"]:
                raise SystemExit("no job recorded to poll")
            s["status"] = "RUNNING"
        elif a.mode == "next-attempt":
            if a.checked_by_hand:
                s["kernel_check"] = {"job": halted_job(s), "class": "FINISHED" if a.checked_by_hand in FINISHED
                                     else "ABSENT", "status": a.checked_by_hand, "at": now(), "by": "hand"}
                history(s, "manual", "kernel-check", "{} {} by hand: {}".format(
                    halted_job(s), a.checked_by_hand, a.note))
            why = check_refusal(s)
            if why:
                raise SystemExit("next-attempt refused: " + why)
            if s["attempt"] + 1 > s["max_attempts"]:
                raise SystemExit("attempt {} would exceed max_attempts {}".format(s["attempt"] + 1, s["max_attempts"]))
            s["attempt"] += 1
            fam = family_of(s, item)
            s["resume_dirs"] = ([r["folder"] for r in s["attempts"].get(item["id"], [])
                                 if holds_rows(r["folder"], fam)]
                                if item["kind"] in ("shard", "drill") else [])
            s["job"], s["args"], s["data_dirs"] = "", "", []
            s["status"] = "READY"
        else:
            s["index"] += 1
            s["attempt"] = 1
            s["resume_dirs"] = []
            s["job"], s["args"], s["data_dirs"] = "", "", []
            s["status"] = "DONE" if s["index"] == len(s["queue"]) else "READY"
        if a.checked_by_hand and a.mode != "next-attempt":
            raise SystemExit("--checked-by-hand applies to next-attempt only")
        s["halt_reason"] = ""
        s["anomaly"] = None
        s["kernel_check"] = None
        history(s, "manual", "release-" + a.mode, a.note)
    validate(s)
    write_state(s)
    show(a)
    print("\nwritten: {}. Commit and push it{}.".format(
        STATE_REL, ", then enable the workflow" if a.cmd == "release" else ""))
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    t = sub.add_parser("tick")
    t.add_argument("--run-id", required=True)
    sub.add_parser("show")
    sub.add_parser("verify")
    nw = sub.add_parser("next-wake")
    nw.add_argument("--min", type=int, default=60)
    nw.add_argument("--max", type=int, default=900)
    ld = sub.add_parser("load")
    ld.add_argument("--definition", required=True)
    ld.add_argument("--note", required=True)
    h = sub.add_parser("halt")
    h.add_argument("--note", required=True)
    c = sub.add_parser("check")
    c.add_argument("--note", required=True)
    r = sub.add_parser("release")
    r.add_argument("--mode", required=True, choices=["start", "repoll", "next-attempt", "next-item"])
    r.add_argument("--note", required=True)
    r.add_argument("--checked-by-hand", choices=HAND_STATUSES, default=None,
                   help="next-attempt only: the status you saw on Kaggle yourself for the halted job (K1)")
    a = p.parse_args()
    if a.cmd == "tick":
        return tick(a)
    if a.cmd == "show":
        return show(a)
    if a.cmd == "next-wake":
        if a.min < 1 or a.max < a.min:
            raise SystemExit("next-wake: need 1 <= --min <= --max")
        return next_wake(a)
    if a.cmd == "verify":
        return verify(a)
    if a.cmd == "load":
        return load_definition(a)
    if a.cmd in ("halt", "check", "release"):
        return manual(a)
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
