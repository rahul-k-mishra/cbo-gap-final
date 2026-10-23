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
the Kaggle credentials; the workflow writes ~/.kaggle/kaggle.json and the
kaggle CLI reads it.

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
      shard; a shard's run dir ends in -s<S>of<K>; a resumed attempt
      prints "resume: read" for each of its resume folders. Any mismatch:
      HALT, even when the runner exited 0. The folder is committed.
      Worked example: "numpy 2.2.0" printed: HALT "numpy 2.2.0, expected
      2.1.3"; rule 16 then requires detcheck on the new image.

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

EXIT CODES (tick)
  0  nothing to do; one action done; an anomaly recorded (L5); the lock
     lost before any Kaggle side effect (L1)
  3  HALT: the state is HALTED, or this tick halted, or a push failed
     after a Kaggle side effect
  1  unexpected error: unreadable state, dirty checkout, an exception
  The workflow disables itself after any nonzero exit, and after DONE.

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
  tick --run-id ID   one step; run by the workflow only
  show               print the state (reads only)
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


def validate(s):
    for k in ("schema", "kaggle_user", "plan", "plan_sha256", "timing", "workers", "expect",
              "max_attempts", "max_file_mb", "queue", "status", "index", "attempt", "resume_dirs",
              "job", "args", "data_dirs", "anomaly", "halt_reason", "kernel_check", "attempts",
              "history"):
        if k not in s:
            raise ValueError("state has no key " + k)
    if s["schema"] != 1:
        raise ValueError("state schema {} is not 1".format(s["schema"]))
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
        if s["job"] != job_name(s["queue"][s["index"]], s["attempt"]):
            raise ValueError("job {!r} does not match item {} attempt {}".format(
                s["job"], s["index"], s["attempt"]))
    if s["status"] == "READY" and s["job"]:
        raise ValueError("READY with a job recorded ({})".format(s["job"]))
    if s["status"] != "HALTED" and s["kernel_check"] is not None:
        raise ValueError("a kernel check is recorded in status {} (K1: only while HALTED)".format(s["status"]))
    for k in ("python", "numpy") + tuple(k for _, k in PINNED):
        if not s["expect"].get(k):
            raise ValueError("expect has no " + k)


def history(s, run, event, note):
    s["history"].append({"at": now(), "run": run, "event": event,
                         "item": s["queue"][s["index"]]["id"] if s["index"] < len(s["queue"]) else "",
                         "attempt": s["attempt"], "job": s["job"], "note": note})


def job_name(item, attempt):
    if item["kind"] == "smoke":
        return "rerun-smoke-{}-a{}".format(item["set"], attempt)
    return "rerun-{}-s{}of{}-a{}".format(item["set"], item["shard"], item["nshards"], attempt)


def job_spec(s):
    """(job, args, data folders) for the current item and attempt."""
    item = s["queue"][s["index"]]
    if item["kind"] == "smoke":
        args = "--smoke --plan-from {} --rows {} --workers {}".format(s["plan"], item["rows"], s["workers"])
        data = [s["plan"]]
    else:
        tf = " ".join("--timing-from {}".format(t) for t in s["timing"])
        args = "--plan-from {} {} --rows {} --shard {} --nshards {} --workers {}".format(
            s["plan"], tf, item["rows"], item["shard"], item["nshards"], s["workers"])
        data = [s["plan"]] + list(s["timing"])
    return job_name(item, s["attempt"]), args, data


def holds_rows(folder):
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
    """One kgrun status call: (recognised status or None, denied for exactly this kernel, last line)."""
    rc, out = kgrun(["status", "--job", job, "--user", s["kaggle_user"]])
    kid = "{}/cbo-{}".format(s["kaggle_user"], job)
    found = None
    for ln in out.splitlines():
        m = re.match(r'^(\S+) has status "([^"]+)"$', ln.strip())
        if m and m.group(1) == kid:
            found = m.group(2).split(".")[-1].upper()
    denied = any(m.group(1) == kid for m in DENIED.finditer(out))
    lines = [ln for ln in out.splitlines() if ln.strip()]
    last = lines[-1] if lines else "(no output)"
    say("  kaggle status of {}: {}".format(kid, found if found else ("DENIED" if denied else last)))
    if rc != 0:
        raise Halt("kgrun status exit {} for {}".format(rc, job))
    return found, denied, last


def kernel_status(s, job):
    """L4: (class, detail), class one of WAIT, FINISHED, ABSENT, UNKNOWN."""
    found, denied, last = raw_status(s, job)
    if found in WAIT:
        return "WAIT", found
    if found in FINISHED:
        return "FINISHED", found
    if found:
        return "UNKNOWN", "status " + found
    if not denied:
        return "UNKNOWN", last
    say("  denied: control status of {} (L4), to tell a free name from a credential failure".format(
        CONTROL_JOB))
    cfound, _, clast = raw_status(s, CONTROL_JOB)
    if not cfound:
        return "UNKNOWN", "denied, and the control {} gave no status either ({})".format(CONTROL_JOB, clast)
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
    job, args, data = job_spec(s)
    say("LAUNCH  item {} ({}), attempt {}, job {}".format(s["index"], item["id"], s["attempt"], job))
    for name, key in PINNED:
        h = sha256_of(os.path.join(SCRIPTS, name))
        if h != s["expect"][key]:
            raise Halt("P1: scripts/{} sha256 {} differs from the pinned {}".format(name, h, s["expect"][key]))
    say("  P1 code pin: rerun.py, rerunlib.py, costprobe2.py as pinned")
    old = glob.glob(os.path.join(ROOT, "runs", job + "-kaggle-*"))
    if old:
        raise Halt("L3: {} already has a folder in runs/: {}".format(job, ", ".join(sorted(old))))
    if os.path.exists(os.path.join(ROOT, "logs", "kgrun-{}.log".format(job))):
        raise Halt("L3: logs/kgrun-{}.log already exists; was {} launched by hand?".format(job, job))
    for d in s["resume_dirs"]:
        if not holds_rows(d):
            raise Halt("resume folder {} holds no rerun-*/rerun_real.csv".format(d))
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
    argv = ["launch", "--job", job, "--user", s["kaggle_user"], "--script", "rerun.py",
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


def read_runner(text):
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


def header_problems(s, item, f):
    """R1."""
    e = s["expect"]
    p = []
    if f["python"] != e["python"]:
        p.append("python {}, expected {}".format(f["python"], e["python"]))
    if f["numpy"] != e["numpy"]:
        p.append("numpy {}, expected {}".format(f["numpy"], e["numpy"]))
    for _, k in PINNED:
        if f["hashes"].get(k) != e[k]:
            p.append("{} {}, expected {}".format(k, f["hashes"].get(k), e[k]))
    if f["plan_sha"] != s["plan_sha256"]:
        p.append("plan sha256 {}, expected {}".format(f["plan_sha"], s["plan_sha256"]))
    want = "smoke" if item["kind"] == "smoke" else "run"
    if f["mode"] != want:
        p.append("mode {}, expected {}".format(f["mode"], want))
    if item["kind"] == "shard":
        tag = "-s{}of{}".format(item["shard"], item["nshards"])
        if not (f["rundir"] or "").endswith(tag):
            p.append("run dir {}, expected a name ending {}".format(f["rundir"], tag))
    for d in s["resume_dirs"]:
        if os.path.basename(d.rstrip("/")) not in f["resume_read"]:
            p.append("no 'resume: read' line for " + d)
    return p


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

    f = read_runner(runner_text(folder, job))
    say("  runner exit {}  python {}  numpy {}  mode {}  run dir {}  D-SMOKE {}  completed {}".format(
        f["exit"], f["python"], f["numpy"], f["mode"], f["rundir"], f["smoke"], f["completed"]))
    s["attempts"].setdefault(item["id"], []).append({
        "attempt": s["attempt"], "job": job, "folder": rel, "kaggle_status": kstatus,
        "runner_exit": f["exit"], "completed": f["completed"], "d_smoke": f["smoke"],
        "resume_dirs": list(s["resume_dirs"]), "fetched_run": ctx.run, "fetched_at": now()})
    paths = [rel, fetchlog]
    code = f["exit"]
    probs = header_problems(s, item, f)
    if code is None:
        raise Halt("R2: no 'kgrun runner: exit code' line in {} (killed, cap, pre-emption or "
                   "cancelled)".format(rel), paths)
    if code not in (0, 5):
        raise Halt("R2: runner exit code {} in {}{}".format(
            code, rel, "; R1: " + "; ".join(probs) if probs else ""), paths)
    if probs:
        raise Halt("R1: header of {}: {}".format(rel, "; ".join(probs)), paths)
    if item["kind"] == "shard":
        csvs = glob.glob(os.path.join(folder, "rerun-*", "rerun_real.csv"))
        if len(csvs) != 1:
            raise Halt("F2: {} rerun-*/rerun_real.csv file(s) in {}, expected 1".format(len(csvs), rel), paths)
        with open(csvs[0], newline="") as fh:
            nok = sum(1 for r in csv.DictReader(fh) if r.get("end") == "ok")
        say("  F2: {} rows end ok; runner summary completed {}".format(nok, f["completed"]))
        if f["completed"] is None or nok != f["completed"]:
            raise Halt("F2: download incomplete or summary missing: {} rows end ok in {}, runner summary "
                       "completed {}".format(nok, rel, f["completed"]), paths)
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
        s["resume_dirs"] = [r["folder"] for r in s["attempts"][item["id"]] if holds_rows(r["folder"])]
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
    say("  plan {} (rerun_plan.csv {})".format(s["plan"], s["plan_sha256"]))
    say("  timing {}".format(", ".join(s["timing"])))
    say("  expect python {} numpy {}; {}".format(s["expect"]["python"], s["expect"]["numpy"], "; ".join(
        "{} {}".format(k, s["expect"][k][:8]) for _, k in PINNED)))
    say("  kaggle user {}  workers {}  max attempts {}  max file {} MB".format(
        s["kaggle_user"], s["workers"], s["max_attempts"], s["max_file_mb"]))
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
            s["resume_dirs"] = ([r["folder"] for r in s["attempts"].get(item["id"], []) if holds_rows(r["folder"])]
                                if item["kind"] == "shard" else [])
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
    if a.cmd in ("halt", "check", "release"):
        return manual(a)
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
