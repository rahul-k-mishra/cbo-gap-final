"""
kgrun.py  --  CBO-GAP: drive Kaggle compute from this laptop

WHAT THIS IS, IN PLAIN LANGUAGE
-------------------------------
The laptop has 2 cores and about 7 GB of usable memory. A Kaggle CPU session
has 4 cores and 30 GB, with a hard 12-hour cap per session and 20 GB of output
space. The heavy runs therefore go to Kaggle while the repository, the
manuscript and the git history stay here.

This script is the only thing that talks to Kaggle. It:
  1. assembles the upload bundle: the archived scripts from zenodo-v1, the two
     per-realization CSVs the determinism gate needs, and the round-2 scripts
     from scripts/;
  2. creates the dataset the first time, versions it afterwards, and waits
     until "kaggle datasets status" reports ready and then until Kaggle
     lists this bundle's identity file (BUNDLE IDENTITY below; --ready-poll,
     default 30 s; --ready-timeout, default 1800 s; on timeout nothing is
     pushed);
  3. generates the Kaggle runner (a short script that calls one of our scripts
     with the flags you name) and its kernel-metadata.json;
  4. pushes the kernel, which starts a batch run;
  5. polls until it finishes;
  6. downloads its output into a NEW runs/<job>-kaggle-<timestamp>/ folder and
     writes sha256.txt for what came back, through write_manifest from
     scripts/manifest.py, so it is byte-identical to the manifest
     manifest.py would write for the same folder.

The notebook on Kaggle is generated from the script in this repository on
every push, so there is never a second copy of the code to drift. Never edit
the notebook in the Kaggle web editor: the next push overwrites it.

WHAT IT DOES NOT DO
  It does not read, print or transmit your Kaggle credentials; the kaggle CLI
  reads ~/.kaggle/credentials.json itself, the OAuth file written by "kaggle
  auth login", and refreshes its access token on its own (ledger K10,
  2026-11-12; until then ~/.kaggle/access_token, ledger K6). access_token and
  kaggle.json must be absent: the CLI uses either before credentials.json,
  and a dead KGAT_ token in access_token is what halted c5-x-s73of116-a1.
  It does not write to zenodo-v1. It does
  not overwrite an existing run folder.

RESUMPTION ON KAGGLE (ledger K5, closed 2026-10-11)
  --resume-dirs runs/A[,runs/B]   earlier fetched run folders, passed to the
                                  script as --resume-from (CLAUDE.md rule 17)
  --data-dirs runs/C[,runs/D]     earlier run folders the script reads as
                                  input, for example calprec2's --throughput.
                                  Every token of --args equal to "runs/<name>"
                                  is replaced on Kaggle by the folder's path.
                                  Since 2026-10-25 (ledger N42) so is every
                                  member of a comma-joined token, for
                                  calprec2's --finalize runs/A,runs/B: each
                                  member equal to "runs/<name>" is replaced
                                  and the token is rejoined. A token without
                                  a comma is handled exactly as before.
                                  Worked example: "--finalize
                                  runs/A,runs/B" with A and B shipped gives
                                  "--finalize /tmp/kgrun-ship/A,/tmp/kgrun-
                                  ship/B", one occurrence each.
                                  Since 2026-10-26 (ledger K8) the check
                                  made before anything else, that every
                                  --data-dirs folder is named in --args,
                                  uses the same rule (arg_members). Until
                                  then it matched whole tokens only and
                                  refused the finalize above before any
                                  Kaggle command.
  Before the bundle is built, every such folder must:
    - be a direct subfolder of runs/;
    - hold a sha256.txt listing exactly the files present, each with a
      matching hash;
    - be tracked by git and unmodified.
  Its files are copied into the bundle FLAT, under the names
  kgrun-ship-<i>-<j>-<basename>, with an index file kgrun-ship-index.json
  that maps each name back to its folder and relative path. The reason is
  that kgrun versions the dataset with "--dir-mode skip", which drops
  subdirectories, and how Kaggle treats uploaded archives is not recorded
  here.
  The runner rebuilds each folder under /tmp/kgrun-ship/<name>/ and
  verifies it against its sha256.txt. On any mismatch it exits 2 before the
  script starts. It then prints each folder with its file count, rows and
  complete rows, and passes the rebuilt paths. The rebuilt folders are under
  /tmp, not /kaggle/working, so they are not fetched back as output; a
  fetched run folder never contains a copy of its resume inputs. Nothing of
  the archive is copied (rule 15).
  The new run writes a NEW folder of new rows only; the merge is a
  concatenation (rule 17).
  The bundle grows with every shipped folder. Its size and file count are
  printed, with a warning above --warn-mb (default 1000 MB). That threshold
  is a local choice, not a Kaggle figure: Kaggle's dataset limits are not
  recorded in this repository.

BUNDLE IDENTITY (ledger K7, 2026-10-23)
  "kaggle datasets status" reports ready for the dataset, not for the
  version just uploaded: on 2026-10-23 it said ready 0 s after the upload
  of the rerun-smoke-arch-a1 bundle, the kernel was pushed, and the runner
  read the previous version's kgrun-ship-index.json, which did not list the
  folder just shipped (logs/kgrun-rerun-smoke-arch-a1.log). So every
  bundle now carries its own identity:
    - build_bundle writes kgrun-bundle-<id>.sha256 into the bundle: one
      line "<sha256>  <name>" for every other bundle file except
      dataset-metadata.json (which is not uploaded), sorted by name; <id>
      is the first 16 hex digits of the sha256 of that text. Identical
      bytes give the same <id>, so the id names the content, not the
      upload.
    - before the push, wait_version polls "kaggle datasets files <dataset>
      --page-size 200" until the name kgrun-bundle-<id>.sha256 appears in
      its output. Any line containing "error" or "usage" stops at once;
      on timeout the kernel is NOT pushed.
    - the runner, before anything else, requires
      kgrun-bundle-<id>.sha256 in the mounted dataset and every file it
      lists to hash as listed; otherwise SETUP ERROR, exit 2, before any
      shipped folder is rebuilt and before the script starts.
  Worked example: the bundle's id is 3f0c9a12d4e6b871. Kaggle still lists
  kgrun-bundle-77ab01c4e5f62d90.sha256 (the previous version): not
  pushed yet, polled again. Had the kernel been pushed anyway and mounted
  that version, the runner prints "mounted dataset is not this launch's
  bundle 3f0c9a12d4e6b871; it holds kgrun-bundle-77ab01c4e5f62d90.sha256"
  and exits 2 within seconds, instead of running a 12-hour shard on the
  previous version's code.
  What this does not establish: which version a kernel attaches when two
  are listed. The runner check is what makes that question harmless.
  "push" alone does not rebuild the bundle; it takes the id from the one
  kgrun-bundle-*.sha256 in .kaggle-bundle/ and refuses if there is not
  exactly one.

LAUNCH STOPPED BEFORE THE PUSH: EXIT 10 (ledger K9, 2026-11-08)
  "launch" runs its steps in a fixed order: git guard, bundle, dataset
  version, ready wait, bundle wait, runner generation, and only then
  "kaggle kernels push". push() records that it has started immediately
  before it runs that command. If "launch" stops for any reason (a failed
  kaggle command, a timeout, a refusal, an uncaught exception) while that
  record is still unset, this process never ran "kaggle kernels push".
  kgrun then prints the cause, the line
    NOT PUSHED: kgrun launch stopped before it ran "kaggle kernels push"
  and exits 10 (NOT_PUSHED_EXIT). A stop after the record is set keeps the
  exit code it had, because a push that returned an error may still have
  created the kernel; since K12 that code is 11 or 12 for any reply the
  push returned (PUSH VERDICT below), and 1 only for a crash.
  Exit 10 states what this process did. It does not say what Kaggle holds:
  a kernel of that name created by anything else is outside its view.
  rerunq.py's L3 check before every launch and its K1 check before every
  new attempt are what cover that, and neither is changed by this.
  A parse error of the arguments (argparse, exit 2) happens before the
  action is known and keeps its exit 2; it also precedes any push.
  Worked example: on 2026-11-08 the launch of c5-x-s50of116-a1 uploaded
  all 88 files and then "kaggle datasets version" exited 1 with "400
  Client Error: Bad Request for url: .../CreateDatasetVersion"
  (logs/kgrun-c5-x-s50of116-a1.log). run_cmd raised SystemExit("command
  failed with code 1") in dataset_version, before push() was reached, and
  kgrun exited 1. Under this rule it prints that message, the NOT PUSHED
  line, and exits 10. Had the same 400 come from "kaggle kernels push"
  instead, the exit would be 12 (PUSH VERDICT).

PUSH VERDICT: EXIT 0, 11 OR 12 (ledger K12, 2026-11-14; before first
execution)
  The exit code of "kaggle kernels push" is not evidence of a push.
  kaggle 2.2.4 exits 0 when Kaggle refuses one. On 2026-11-14 the launch
  of c5-x-s91of116-a1 printed "Kernel push error: Maximum batch CPU
  session count of 5 reached."; run_cmd raised nothing, which it does for
  every non-zero exit, so the CLI's exit code was 0; kgrun printed
  LAUNCHED and exited 0 (logs/kgrun-c5-x-s91of116-a1.log). Exit 10 (above)
  did not apply, by design: the push had started.
  The verdict is therefore read from what Kaggle returned. The REPLY is
  the CLI's output with blank lines and the outdated-version warning line
  removed, each line stripped.
  PUSHED       the REPLY holds exactly one line starting "Kernel version N
               successfully pushed." (N a positive integer), no line
               containing "error" in any case, and the CLI exited 0.
               kgrun prints "PUSH VERDICT: PUSHED version N of <kernel>",
               and launch then prints LAUNCHED. Exit 0.
  CAPACITY     the REPLY is exactly ONE line, "Kernel push error: Maximum
               batch CPU session count of M reached." (M a positive
               integer; the final full stop optional), whatever the CLI's
               exit code. kgrun prints "PUSH VERDICT: CAPACITY (...)" and
               the CAPACITY_LINE below, and exits 11 (CAPACITY_EXIT).
  UNCONFIRMED  every other REPLY: no success line, two of them, a success
               line beside an error line, a success line with a non-zero
               exit, any other error text, the capacity line with any
               other line beside it, nothing at all. kgrun prints "PUSH
               VERDICT: UNCONFIRMED (<reason>; Kaggle replied: <REPLY>)"
               and the UNCONFIRMED_LINE, and exits 12 (UNCONFIRMED_EXIT).
               Whether a kernel was created is not known.
  Why this rule. Recording RUNNING is the one consequence that must be
  proved, so PUSHED needs Kaggle's own positive statement with a version
  number, not the absence of a crash. Everything else is UNCONFIRMED and
  halts the queue, except ONE refusal whose text is pinned exactly and
  whose meaning is measured. An error text not seen before lands in
  UNCONFIRMED, never in PUSHED and never in CAPACITY. Rate limits (HTTP
  429) and the GPU variant are not CAPACITY: their text has not been seen
  here, so they halt until it has.
  Why CAPACITY means "no session was started": (a) the text says the
  account's limit was reached, so the push was refused, not queued; (b)
  measured for s91: kgrun status of ericsom/cbo-c5-x-s91of116-a1 gave a
  404 from GetKernelSessionStatus at 18:17 and 18:33 IST, 15 and 31
  minutes after the refusal (logs/rerunq-c5-x-s91of116-a1-anomaly-
  20261114-181745.log and -halt-20261114-183309.log), and Rahul read
  GetKernel 403 and GetKernelSessionStatus 404 for it at 22:39 IST while
  s90 answered COMPLETE on the same credential. A session, queued or
  running, has a status.
  What it does not establish: what Kaggle keeps under the name after the
  refusal. Before the refused push, kgrun status of that name gave the
  kernels.get denial (logs/rerunq-c5-x-s91of116-a1-launched-20261114-
  180219.log); after it, the 404 above. The reply changed; why is not
  known. rerunq.py's capacity wait (CW) handles that reply.
  "run" and "push" use the same verdict: after CAPACITY or UNCONFIRMED
  nothing is polled or fetched.
  Worked examples: logs/kgrun-c5-x-s90of116-a1.log, "Kernel version 1
  successfully pushed.  Please check progress at https://www.kaggle.com/
  code/ericsom/cbo-c5-x-s90of116-a1", exit 0: PUSHED version 1.
  logs/kgrun-c5-x-s91of116-a1.log, the one line "Kernel push error:
  Maximum batch CPU session count of 5 reached.", exit 0: CAPACITY, exit
  11. "Kernel push error: Notebook not found": UNCONFIRMED, exit 12.
  "429 Client Error: Too Many Requests for url: ...": UNCONFIRMED. The
  success line, exit 1: UNCONFIRMED. The success line and a line "Kernel
  push error: ...": UNCONFIRMED. Nothing printed: UNCONFIRMED.
  NULL RATE: deterministic string tests on one reply; none fires by
  chance. A false PUSHED needs Kaggle to print its success line for a
  refused push; a false CAPACITY needs the exact refusal line, alone, for
  a push that started a session. Neither has been seen; rerunq's L4 at the
  next poll (no status) and its preflight before a retry (a status means
  the name is in use: L3 HALT) would show either.

DATASET REUSE (ledger K9, 2026-11-08; Rahul's decision)
  Applies to "launch" without --first only. "dataset-version", "run" and
  "--first" always upload. Before uploading, launch asks whether the
  dataset's CURRENT version already holds exactly this bundle:
    C1  "kaggle datasets status <dataset> --format json" prints one JSON
        object; its "status" is "ready" and its "current_version_number"
        is a positive integer N.
    C2  "kaggle datasets files <dataset>/N --page-size 200" (the listing of
        version N by number, not the unpinned listing that K7 found can lag
        a new version) prints a table with no "Next Page Token" line, no
        line containing "error" or "usage", and at least one row.
    C3  Of the listed names, exactly one has the form kgrun-bundle-*.sha256,
        and it is kgrun-bundle-<id>.sha256 for this launch's id.
    C4  The listed names equal the names this launch would upload (every
        file in .kaggle-bundle/ but dataset-metadata.json), none missing,
        none extra.
    C5  C1 asked again after C2 gives "ready" and the same N.
  Any command that fails, any output these rules do not recognise, and any
  exception in the check is a refusal. A refusal uploads a new version,
  exactly as before this rule. Pass: no upload, no ready wait, no bundle
  wait (an unpinned wait would prove nothing here).
  The launch log always prints one of
    DATASET PATH: SKIPPED UPLOAD  bundle <id> already in current version N ...
    DATASET PATH: UPLOADED NEW VERSION  bundle <id>  because: <reason>
  with the check's lines above it. The reason names the rule that refused,
  or says the check passed in shadow mode.
  REUSE_MODE: "shadow" runs C1 to C5 and prints the verdict, then always
  uploads. "on" skips on a pass. The mode is "shadow" until Rahul has
  measured, and the ledger (K9) records, what kaggle 2.2.4 prints for C1,
  and that "files <dataset>/N" lists version N rather than the latest. The
  K9 entry describes that measurement. Changing the mode is a commit
  naming the log.
  The mode is "on" since 2026-11-14 (Rahul's decision; ledger K9, MODE ON),
  naming logs/kgrun-c5-x-s91of116-a1.log: C1 to C5 PASS on version 182,
  bundle 40f9ec17f6037595. Shadow record before the switch: 41 launches,
  s51 to s91 of c5-x, all PASS, every one with version N equal to the
  previous launch's N + 1 and the previous launch's bundle id equal to its
  own, so no skip it would have made was wrong; and no launch in it had a
  changed bundle, so the refusing path (C3 with another id) has run on
  fixtures only. "on" applies to every "launch" without --first: a first
  try and a capacity retry (rerunq.py CW) alike. "run", "dataset-version",
  "dataset-create" and "launch --first" always upload.
  What the check establishes: version N, as numbered by Kaggle's
  GetDataset, holds files with exactly this bundle's names, including
  this id's identity file. The id is a hash of every file's hash, so the
  bytes are this launch's.
  What it does not establish: (a) that N includes a version still being
  processed (K7 found "status" says ready while one is); (b) that a kernel
  pushed now mounts N. Under the queue nobody creates versions by hand
  (rule 22), so (a) needs a second writer that does not exist. Either way
  the runner's own check (BUNDLE IDENTITY) holds: a mounted version without
  this id stops the kernel with exit 2 before the script starts. The skip
  can waste an attempt but cannot run other code.
  Sizes are not compared: whether Kaggle's listed size equals the local
  byte count for every file type is not measured.
  Worked examples (bundle id 40f9ec17f6037595, 88 upload names):
    status {"status": "ready", "current_version_number": 61}; files of
    version 61 list the 88 names with kgrun-bundle-40f9ec17f6037595.sha256;
    status again 61, ready: pass. "on": SKIPPED UPLOAD. "shadow":
    UPLOADED NEW VERSION because the check passed but the mode is shadow.
    Stale: files of version 61 list kgrun-bundle-681ac0f4987f6998.sha256:
    C3 refuses, UPLOADED NEW VERSION because version 61 holds
    kgrun-bundle-681ac0f4987f6998.sha256, not this bundle's.
    Status again gives 62: C5 refuses. Status prints "ready" with no JSON
    (an older CLI): C1 refuses.

GIT GUARD (Rahul, 2026-10-11: after each job its output is committed and
pushed before the next job starts)
  run and push refuse to start when runs/ has untracked or modified paths,
  or when HEAD is ahead of its upstream. Nothing is pushed to Kaggle then.

EVERY command it is about to execute is printed first. --dry-run prints
without executing.

SUBCOMMANDS
    bundle            assemble the upload folder and list it
    dataset-create    first-time dataset creation (private)
    dataset-version   push a new version of the dataset
    push              generate the runner, push the kernel, start the run
    status            print the kernel's current status
    fetch             download the kernel's output into a new run folder
    run               bundle, dataset-version (or create), push, poll, fetch
    launch            run without the poll and the fetch: bundle,
                      dataset-version (or create), push, then exit. Used by
                      scripts/rerunq.py, which polls and fetches on later
                      invocations (ledger K6)

TYPICAL USE (from the repository root, venv active)
    python scripts/kgrun.py run --job detcheck --script detcheck.py \
        --args "--workers 4" --dry-run
    python scripts/kgrun.py run --job detcheck --script detcheck.py \
        --args "--workers 4"

SHARDING
  A job must finish inside Kaggle's 12-hour cap. Run shards as separate jobs
  with distinct --job names, for example:
    --job calprec-s0 --args "--workers 4 --shard 0 --nshards 4"
  Each shard writes its own output folder; the merge is a concatenation,
  because every seed is derived from a SeedSequence keyed by the cell rather
  than by position in the task list.

Python 3.8 to 3.11 syntax. Standard library only, plus scripts/manifest.py
(itself standard library only), imported from this script's directory.
"""

import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import ManifestRefused, list_files, sha256_of, write_manifest  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "zenodo-v1")
SCRIPTS = os.path.join(ROOT, "scripts")
BUNDLE = os.path.join(ROOT, ".kaggle-bundle")
PUSHDIR = os.path.join(ROOT, ".kaggle-push")

ARCHIVE_CSVS = ["exactcal_real.csv", "rmapj_real.csv"]
RUNS = os.path.join(ROOT, "runs")
SHIP_INDEX = "kgrun-ship-index.json"
DEFAULT_USER = "ericsom"
DEFAULT_DATASET = "cbo-gap-archive"

# LAUNCH STOPPED BEFORE THE PUSH (docstring; ledger K9)
NOT_PUSHED_EXIT = 10
NOT_PUSHED_LINE = 'NOT PUSHED: kgrun launch stopped before it ran "kaggle kernels push"'
STATE = {"action": None, "push_started": False}

# PUSH VERDICT (docstring; ledger K12). rerunq.py keeps copies of the two
# lines and of the two patterns (CW); a change here must be made there too.
CAPACITY_EXIT = 11
UNCONFIRMED_EXIT = 12
CAPACITY_LINE = "NOT LAUNCHED: Kaggle refused the push at the account's batch CPU session limit"
UNCONFIRMED_LINE = "PUSH UNCONFIRMED: whether a kernel was created is not known; check kgrun status first"
PUSH_OK_RE = re.compile(r"^Kernel version ([1-9][0-9]*) successfully pushed\.")
PUSH_CAPACITY_RE = re.compile(r"^Kernel push error: Maximum batch CPU session count of ([1-9][0-9]*) reached\.?$")
CLI_OUTDATED = "Warning: Looks like you're using an outdated `kaggle` version"

# DATASET REUSE (docstring; ledger K9). "shadow" or "on".
REUSE_MODE = "on"

RUNNER_TEMPLATE = '''"""Generated by kgrun.py. Do not edit here; edit the repository script."""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys

USER = "{user}"
DATASET = "{dataset}"
BASE = "/kaggle/input"
WORK = "/kaggle/working"
STAGE = "/tmp/kgrun-ship"
SHIP = {ship!r}
BUNDLE_ID = "{bundle}"


def find_archive():
    """Return (path, how) for the mounted dataset, or (None, None).

    Kaggle has been assumed to mount datasets at /kaggle/input/<dataset>; on
    2026-10-09 it mounted this one at /kaggle/input/datasets/<user>/<dataset>
    (ledger K3). Neither is assumed: both are tried in that order, then
    /kaggle/input is walked in sorted order to depth 3 and the first
    directory named exactly <dataset> is taken."""
    c1 = os.path.join(BASE, DATASET)
    if os.path.isdir(c1):
        return c1, "candidate 1, /kaggle/input/<dataset>"
    c2 = os.path.join(BASE, "datasets", USER, DATASET)
    if os.path.isdir(c2):
        return c2, "candidate 2, /kaggle/input/datasets/<user>/<dataset>"
    if os.path.isdir(BASE):
        for base, dirs, files in os.walk(BASE):
            dirs.sort()
            for d in dirs:
                if d == DATASET:
                    return (os.path.join(base, d),
                            "candidate 3, first directory named <dataset> in a sorted "
                            "walk of /kaggle/input to depth 3")
            if base[len(BASE):].count(os.sep) >= 2:
                dirs[:] = []
    return None, None


print("kgrun runner: job {job}")
print("  python  ", sys.version.replace(chr(10), " "))
print("  dataset ", USER + "/" + DATASET)
sys.stdout.flush()
ARCHIVE, HOW = find_archive()
if ARCHIVE is None:
    print("kgrun runner: SETUP ERROR, archive not found. Tried "
          + os.path.join(BASE, DATASET) + ", then "
          + os.path.join(BASE, "datasets", USER, DATASET) + ", then a walk of "
          + BASE + " to depth 3 for a directory named " + DATASET)
    print("  /kaggle/input holds:")
    if not os.path.isdir(BASE):
        print("    (/kaggle/input does not exist)")
    else:
        shown = 0
        for base, dirs, files in os.walk(BASE):
            dirs.sort()
            if base[len(BASE):].count(os.sep) >= 3:
                dirs[:] = []
            print("    " + base + "/   " + str(len(files)) + " file(s): "
                  + ", ".join(sorted(files)[:10]) + (" ..." if len(files) > 10 else ""))
            shown += 1
            if shown >= 50:
                print("    (listing stopped after 50 directories)")
                break
    print("kgrun runner: exit code 2")
    sys.stdout.flush()
    sys.exit(2)
SCRIPT = os.path.join(ARCHIVE, "{script}")
print("  archive ", ARCHIVE)
print("  found by", HOW)
print("  listing ", len(os.listdir(ARCHIVE)), "files in the mounted dataset")
print("  script  ", SCRIPT)
print("  args    ", {args!r})
sys.stdout.flush()

ARGS = {args!r}.split()


def fail(msg):
    print("kgrun runner: SETUP ERROR, " + msg)
    print("kgrun runner: exit code 2")
    sys.stdout.flush()
    sys.exit(2)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


bmf = os.path.join(ARCHIVE, "kgrun-bundle-" + BUNDLE_ID + ".sha256")
if not os.path.isfile(bmf):
    held = sorted(f for f in os.listdir(ARCHIVE) if f.startswith("kgrun-bundle-"))
    fail("mounted dataset is not this launch's bundle " + BUNDLE_ID + "; it holds "
         + (", ".join(held) if held else "no kgrun-bundle-*.sha256 file"))
nb = 0
with open(bmf) as fh:
    for ln in fh:
        ln = ln.rstrip(chr(10))
        if not ln:
            continue
        h, rel = ln.split("  ", 1)
        if not os.path.isfile(os.path.join(ARCHIVE, rel)):
            fail("bundle " + BUNDLE_ID + ": " + rel + " is not in the mounted dataset")
        if sha256_of(os.path.join(ARCHIVE, rel)) != h:
            fail("bundle " + BUNDLE_ID + ": " + rel + " does not hash as listed")
        nb += 1
print("  bundle   " + BUNDLE_ID + ": " + str(nb) + " files verified against kgrun-bundle-" + BUNDLE_ID + ".sha256")
sys.stdout.flush()

if SHIP:
    idxp = os.path.join(ARCHIVE, "{index}")
    if not os.path.isfile(idxp):
        fail("folders were requested but " + idxp + " is not in the mounted dataset")
    with open(idxp) as fh:
        index = json.load(fh)
    byname = dict((f["name"], f) for f in index["folders"])
    resume = []
    print("  shipped folders (rebuilt under " + STAGE + ", verified against sha256.txt):")
    for name, role in SHIP:
        if name not in byname:
            fail("folder " + name + " is not in " + idxp)
        dst = os.path.join(STAGE, name)
        if os.path.exists(dst):
            fail(dst + " already exists")
        for flat, rel in byname[name]["files"]:
            tgt = os.path.join(dst, *rel.split("/"))
            if not os.path.isdir(os.path.dirname(tgt)):
                os.makedirs(os.path.dirname(tgt))
            shutil.copyfile(os.path.join(ARCHIVE, flat), tgt)
        listed = []
        with open(os.path.join(dst, "sha256.txt")) as fh:
            for ln in fh:
                ln = ln.rstrip(chr(10))
                if not ln:
                    continue
                h, rel = ln.split("  ", 1)
                if sha256_of(os.path.join(dst, rel)) != h:
                    fail(name + " fails its manifest at " + rel)
                listed.append(rel)
        print("    " + role + "  " + name + "  ->  " + dst + "   " + str(len(listed)) + " files, manifest PASS")
        for rel in listed:
            if rel.endswith(".csv"):
                with open(os.path.join(dst, rel), newline="") as fh:
                    rows = list(csv.DictReader(fh))
                done = sum(1 for r in rows if r.get("end") == "ok")
                print("        " + rel + ": " + str(len(rows)) + " rows, " + str(done) + " with end ok")
        if role == "resume":
            resume.append(dst)
        else:
            token = "runs/" + name
            hits = 0
            NEWARGS = []
            for x in ARGS:
                parts = x.split(",")
                hits += sum(1 for q in parts if q == token)
                NEWARGS.append(",".join(dst if q == token else q for q in parts))
            if hits == 0:
                fail("data folder " + name + " is not named in the args as " + token)
            ARGS = NEWARGS
            print("        args: " + token + " -> " + dst + " (" + str(hits) + " occurrence(s))")
    if resume:
        ARGS = ARGS + ["--resume-from", ",".join(resume)]
    sys.stdout.flush()

cmd = [sys.executable, SCRIPT, "--archive", ARCHIVE, "--outdir", WORK] + ARGS
print("  command ", " ".join(cmd))
sys.stdout.flush()
rc = subprocess.call(cmd)
print("kgrun runner: exit code", rc)
sys.exit(rc)
'''


def say(msg):
    print(msg)
    sys.stdout.flush()


def run_cmd(cmd, dry, check=True, capture=False):
    say("  $ " + " ".join(cmd))
    if dry:
        return ""
    if capture:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode("utf-8", "replace")
        say(out.rstrip())
        if check and p.returncode != 0:
            raise SystemExit("command failed with code {}".format(p.returncode))
        return out
    rc = subprocess.call(cmd)
    if check and rc != 0:
        raise SystemExit("command failed with code {}".format(rc))
    return ""


def git_out(args):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip()


def git_guard():
    """Refuse to start a Kaggle job unless runs/ is committed and HEAD is pushed."""
    say("GIT GUARD  runs/ committed, HEAD pushed")
    rc, out = git_out(["status", "--porcelain", "--untracked-files=all", "--", "runs"])
    if rc != 0:
        raise SystemExit("git guard: git status failed: " + out)
    if out:
        say(out)
        raise SystemExit("git guard: runs/ has untracked or modified paths (above). Commit and push "
                         "the previous job's output before the next job starts. Nothing was pushed to Kaggle.")
    rc, out = git_out(["rev-list", "--count", "@{u}..HEAD"])
    if rc != 0:
        raise SystemExit("git guard: cannot compare HEAD with its upstream: " + out)
    if out != "0":
        raise SystemExit("git guard: HEAD is {} commit(s) ahead of its upstream. Push before the next job "
                         "starts. Nothing was pushed to Kaggle.".format(out))
    say("  runs/ clean, HEAD pushed")


def verify_run_dir(path):
    """A shipped folder: (name, relative paths) once it passes every check, or SystemExit."""
    full = os.path.realpath(os.path.join(ROOT, path))
    name = os.path.basename(full)
    if os.path.dirname(full) != os.path.realpath(RUNS) or not os.path.isdir(full):
        raise SystemExit("shipped folder {}: not a direct subfolder of runs/".format(path))
    man = os.path.join(full, "sha256.txt")
    if not os.path.isfile(man):
        raise SystemExit("shipped folder {}: no sha256.txt".format(path))
    listed = {}
    with open(man) as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if ln:
                h, rel = ln.split("  ", 1)
                listed[rel] = h
    files, bad = list_files(full)
    if bad or sorted(listed) != files:
        raise SystemExit("shipped folder {}: the files present do not equal those its sha256.txt lists".format(path))
    for rel in files:
        if sha256_of(os.path.join(full, rel)) != listed[rel]:
            raise SystemExit("shipped folder {}: fails its manifest at {}".format(path, rel))
    rc, out = git_out(["ls-files", "--error-unmatch", os.path.join("runs", name, "sha256.txt")])
    if rc != 0:
        raise SystemExit("shipped folder {}: not tracked by git; commit it first".format(path))
    rc, out = git_out(["status", "--porcelain", "--untracked-files=all", "--", os.path.join("runs", name)])
    if rc != 0 or out:
        raise SystemExit("shipped folder {}: modified or untracked files under git: {}".format(path, out))
    return name, ["sha256.txt"] + files


def arg_members(args):
    """The strings a --data-dirs folder may be named by in --args: every
    whitespace token, split on commas. This is the rule the runner applies
    when it rewrites runs/<name> (RUNNER_TEMPLATE, "x.split(',')"); the
    pre-launch check must use the same rule, or it refuses what the runner
    would ship (ledger K8).
    Worked example: "--rows RMAP,CLIFF --finalize runs/A,runs/B" gives
    ["--rows", "RMAP", "CLIFF", "--finalize", "runs/A", "runs/B"], so
    runs/A and runs/B are both named; "runs/AB" names neither."""
    return [q for x in args.split() for q in x.split(",")]


def ship_list(resume_dirs, data_dirs):
    """[(path, role)] from the two flags; a folder may appear once."""
    out, seen = [], set()
    for role, val in (("resume", resume_dirs), ("data", data_dirs)):
        for x in [y for y in (val or "").split(",") if y]:
            key = os.path.realpath(os.path.join(ROOT, x))
            if key in seen:
                raise SystemExit("shipped folder {} is named twice".format(x))
            seen.add(key)
            out.append((x, role))
    return out


def build_bundle(user, dataset, dry, ship=(), warn_mb=1000.0):
    say("ASSEMBLE BUNDLE  {}".format(BUNDLE))
    if not os.path.isdir(ARCHIVE):
        raise SystemExit("setup error: {} not found".format(ARCHIVE))
    if not dry:
        if os.path.isdir(BUNDLE):
            shutil.rmtree(BUNDLE)
        os.makedirs(BUNDLE)
    n = 0
    for f in sorted(os.listdir(ARCHIVE)):
        if f.endswith(".py") or f in ARCHIVE_CSVS:
            if not dry:
                shutil.copy2(os.path.join(ARCHIVE, f), os.path.join(BUNDLE, f))
            n += 1
    m = 0
    for f in sorted(os.listdir(SCRIPTS)):
        if f.endswith(".py") and f not in ("kgrun.py", "rerunq.py"):
            if not dry:
                shutil.copy2(os.path.join(SCRIPTS, f), os.path.join(BUNDLE, f))
            m += 1
    index = {"folders": []}
    shipped = []
    for i, (path, role) in enumerate(ship):
        name, rels = verify_run_dir(path)
        files = []
        for j, rel in enumerate(rels):
            flat = "kgrun-ship-{:03d}-{:04d}-{}".format(i, j, rel.split("/")[-1])
            if not dry:
                shutil.copy2(os.path.join(RUNS, name, *rel.split("/")), os.path.join(BUNDLE, flat))
            files.append([flat, rel])
        index["folders"].append({"name": name, "role": role, "files": files})
        shipped.append([name, role])
        say("  ship {:<6} {}   {} files, manifest verified, tracked and clean in git".format(role, name, len(rels)))
    meta = {"title": dataset, "id": "{}/{}".format(user, dataset),
            "licenses": [{"name": "unknown"}]}
    bid = "dry-run"
    if not dry:
        if shipped:
            with open(os.path.join(BUNDLE, SHIP_INDEX), "w") as fh:
                json.dump(index, fh, indent=2)
        lines = ["{}  {}".format(sha256_of(os.path.join(BUNDLE, f)), f) for f in sorted(os.listdir(BUNDLE))]
        text = "\n".join(lines) + "\n"
        bid = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        with open(os.path.join(BUNDLE, "kgrun-bundle-{}.sha256".format(bid)), "x") as fh:
            fh.write(text)
        say("  bundle id {}  (kgrun-bundle-{}.sha256, {} files listed)".format(bid, bid, len(lines)))
        with open(os.path.join(BUNDLE, "dataset-metadata.json"), "w") as fh:
            json.dump(meta, fh, indent=2)
        names = os.listdir(BUNDLE)
        total = sum(os.path.getsize(os.path.join(BUNDLE, f)) for f in names)
        say("  {} archive files + {} round-2 scripts + {} shipped folder(s); bundle {} files, {:.1f} MB".format(
            n, m, len(shipped), len(names), total / 1048576.0))
        if total / 1048576.0 > warn_mb:
            say("  WARNING: bundle {:.1f} MB is above --warn-mb {:.0f} MB. Kaggle's dataset limits are not recorded "
                "in this repository; check them before pushing more.".format(total / 1048576.0, warn_mb))
        say("  dataset id {}/{}".format(user, dataset))
    else:
        say("  would copy {} archive files, {} round-2 scripts and {} shipped folder(s)".format(n, m, len(shipped)))
    return shipped, bid


def bundle_id_on_disk():
    """For "push" alone: the id of the one kgrun-bundle-*.sha256 in .kaggle-bundle/, or SystemExit."""
    found = [f for f in (os.listdir(BUNDLE) if os.path.isdir(BUNDLE) else [])
             if f.startswith("kgrun-bundle-") and f.endswith(".sha256")]
    if len(found) != 1:
        raise SystemExit("push: expected one kgrun-bundle-*.sha256 in {}, found {}; rebuild with "
                         "dataset-version first".format(BUNDLE, found))
    return found[0][len("kgrun-bundle-"):-len(".sha256")]


def dataset_create(user, dataset, dry):
    say("CREATE DATASET (private)")
    run_cmd(["kaggle", "datasets", "create", "-p", BUNDLE, "-r", "skip"], dry)


def dataset_version(user, dataset, note, dry):
    say("VERSION DATASET")
    run_cmd(["kaggle", "datasets", "version", "-p", BUNDLE, "-m", note,
             "-r", "skip"], dry)


def wait_ready(user, dataset, every, timeout, dry):
    """Poll "kaggle datasets status" until the dataset reports ready.

    This wait was added for K1 on a wrong diagnosis (processing delay); the
    real cause of both failed launches was the mount path (ledger K3). It is
    kept only as a guard against pushing a kernel against a version that is
    genuinely still being processed. Ready means the last
    non-empty line of the status output is exactly "ready"; a last line
    containing "error" stops at once; anything else is polled again. On
    timeout the script stops and the kernel is NOT pushed."""
    did = "{}/{}".format(user, dataset)
    say("WAIT FOR DATASET READY  {}  (every {} s, timeout {} s)".format(did, every, timeout))
    if dry:
        say("  $ kaggle datasets status {}".format(did))
        say("  (dry run: would poll until it reports ready; not polling)")
        return
    t0 = time.time()
    while True:
        out = run_cmd(["kaggle", "datasets", "status", did], False, check=False,
                      capture=True)
        lines = [ln.strip().lower() for ln in out.splitlines() if ln.strip()]
        last = lines[-1] if lines else ""
        elapsed = time.time() - t0
        say("  {:.0f} s: status {!r}".format(elapsed, last))
        if last == "ready":
            return
        if "error" in last:
            raise SystemExit("dataset {} reports {!r}; kernel NOT pushed".format(did, last))
        if elapsed >= timeout:
            raise SystemExit("dataset {} not ready after {:.0f} s; kernel NOT pushed. "
                             "Check it with: kaggle datasets status {} ; when it reports "
                             "ready, run: python scripts/kgrun.py push --job <job> ..."
                             .format(did, elapsed, did))
        time.sleep(every)


def wait_version(user, dataset, bid, every, timeout, dry):
    """Poll "kaggle datasets files" until this bundle's identity file is listed.

    Listed means the exact name kgrun-bundle-<bid>.sha256 occurs in the
    output. A line containing "error" or "usage" stops at once; on timeout
    the script stops and the kernel is NOT pushed (BUNDLE IDENTITY in the
    docstring; ledger K7)."""
    did = "{}/{}".format(user, dataset)
    want = "kgrun-bundle-{}.sha256".format(bid)
    say("WAIT FOR THIS BUNDLE  {} lists {}  (every {} s, timeout {} s)".format(did, want, every, timeout))
    cmd = ["kaggle", "datasets", "files", did, "--page-size", "200"]
    if dry:
        say("  $ " + " ".join(cmd))
        say("  (dry run: would poll until the name is listed; not polling)")
        return
    t0 = time.time()
    while True:
        out = run_cmd(cmd, False, check=False, capture=True)
        elapsed = time.time() - t0
        held = sorted(set(w for w in out.split() if w.startswith("kgrun-bundle-")))
        if want in out.split():
            say("  {:.0f} s: {} listed".format(elapsed, want))
            return
        say("  {:.0f} s: not listed; kgrun-bundle files listed: {}".format(elapsed, ", ".join(held) or "none"))
        bad = [ln for ln in out.splitlines() if "error" in ln.lower() or "usage" in ln.lower()]
        if bad:
            raise SystemExit("kaggle datasets files reports {!r}; kernel NOT pushed".format(bad[0].strip()))
        if elapsed >= timeout:
            raise SystemExit("{} not listed for {} after {:.0f} s; kernel NOT pushed".format(want, did, elapsed))
        time.sleep(every)


def upload_names():
    """The names "kaggle datasets version" uploads: every file in the bundle but dataset-metadata.json."""
    return sorted(f for f in os.listdir(BUNDLE) if f != "dataset-metadata.json")


def parse_status_json(out):
    """C1: ("ready", N) or (None, reason). The one line of the output that starts with "{" is the JSON."""
    objs = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("{")]
    if len(objs) != 1:
        return None, "status printed {} JSON line(s), expected 1".format(len(objs))
    try:
        d = json.loads(objs[0])
    except ValueError:
        return None, "status line is not JSON: {!r}".format(objs[0][:120])
    if not isinstance(d, dict):
        return None, "status JSON is not an object"
    st, v = d.get("status"), d.get("current_version_number")
    if st != "ready":
        return None, "dataset status {!r}, not 'ready'".format(st)
    if not isinstance(v, int) or isinstance(v, bool) or v < 1:
        return None, "current_version_number {!r} is not a positive integer".format(v)
    return "ready", v


def parse_files_table(out):
    """C2: (names, None) or (None, reason), from the table "kaggle datasets files" prints."""
    lines = out.splitlines()
    for ln in lines:
        low = ln.lower()
        if ln.strip().startswith("Next Page Token"):
            return None, "listing is paged (Next Page Token): not every file was listed"
        if "error" in low or "usage" in low:
            return None, "listing reports {!r}".format(ln.strip()[:160])
    dash = [i for i, ln in enumerate(lines) if ln.strip() and set(ln.strip()) <= set("- ")]
    if len(dash) != 1 or dash[0] == 0 or not lines[dash[0] - 1].split()[:1] == ["name"]:
        return None, "no single 'name ... ----' table header in the listing"
    names = []
    for ln in lines[dash[0] + 1:]:
        if not ln.strip():
            continue
        if ln.startswith("Warning: Looks like you're using an outdated"):
            continue
        names.append(ln.split()[0])
    if not names:
        return None, "listing has no rows"
    if len(set(names)) != len(names):
        return None, "listing repeats a name"
    return names, None


def reuse_check(user, dataset, bid):
    """C1 to C5 of DATASET REUSE: (True, detail) on a pass, else (False, the refusing rule and why)."""
    did = "{}/{}".format(user, dataset)
    status_cmd = ["kaggle", "datasets", "status", did, "--format", "json"]
    out = run_cmd(status_cmd, False, check=False, capture=True)
    st, v = parse_status_json(out)
    if st is None:
        return False, "C1: " + v
    say("  C1: status ready, current version {}".format(v))
    out = run_cmd(["kaggle", "datasets", "files", "{}/{}".format(did, v), "--page-size", "200"], False,
                  check=False, capture=True)
    names, why = parse_files_table(out)
    if names is None:
        return False, "C2: version {}: {}".format(v, why)
    say("  C2: version {} lists {} file(s)".format(v, len(names)))
    want = "kgrun-bundle-{}.sha256".format(bid)
    ids = sorted(n for n in names if n.startswith("kgrun-bundle-") and n.endswith(".sha256"))
    if ids != [want]:
        return False, "C3: version {} holds {}, not this bundle's {} alone".format(v, ", ".join(ids) or "no identity file", want)
    say("  C3: version {} holds {} and no other identity file".format(v, want))
    local = upload_names()
    missing = sorted(set(local) - set(names))
    extra = sorted(set(names) - set(local))
    if missing or extra:
        return False, "C4: version {} differs from this bundle by name: {} missing ({}), {} extra ({})".format(
            v, len(missing), ", ".join(missing[:5]), len(extra), ", ".join(extra[:5]))
    say("  C4: version {} lists exactly the {} names this launch would upload".format(v, len(local)))
    out = run_cmd(status_cmd, False, check=False, capture=True)
    st2, v2 = parse_status_json(out)
    if st2 is None:
        return False, "C5: second status: " + v2
    if v2 != v:
        return False, "C5: current version moved from {} to {} during the check".format(v, v2)
    say("  C5: status again ready, current version still {}".format(v))
    return True, "version {} holds exactly this bundle's {} files".format(v, len(local))


def dataset_step(user, dataset, note, bid, dry, every, timeout):
    """DATASET REUSE: skip the upload on a pass in mode "on"; otherwise version, then both waits."""
    say("DATASET REUSE CHECK  bundle {}  (mode {}; ledger K9)".format(bid, REUSE_MODE))
    if dry:
        say("  (dry run: would run C1 to C5; not checking)")
        ok, why = False, "dry run"
    else:
        try:
            ok, why = reuse_check(user, dataset, bid)
        except Exception as e:
            ok, why = False, "the check raised {}: {}".format(type(e).__name__, e)
    say("  verdict: {}".format("PASS, " + why if ok else "REFUSED, " + why))
    if ok and REUSE_MODE == "on":
        say("DATASET PATH: SKIPPED UPLOAD  bundle {} already in the current dataset version ({}); no new "
            "version created, no wait; the runner verifies bundle {} before the script starts".format(bid, why, bid))
        return
    if ok:
        because = "the reuse check passed ({}) but REUSE_MODE is {!r}, so the upload runs as before".format(
            why, REUSE_MODE)
    else:
        because = "the reuse check refused: " + why
    say("DATASET PATH: UPLOADED NEW VERSION  bundle {}  because: {}".format(bid, because))
    dataset_version(user, dataset, note, dry)
    wait_ready(user, dataset, every, timeout, dry)
    wait_version(user, dataset, bid, every, timeout, dry)


def write_kernel(user, dataset, job, script, args, dry, shipped=(), bid="dry-run"):
    kid = "{}/cbo-{}".format(user, job)
    say("GENERATE KERNEL  {}".format(kid))
    runner = RUNNER_TEMPLATE.format(user=user, dataset=dataset, script=script, job=job,
                                    args=args, ship=[list(x) for x in shipped], index=SHIP_INDEX,
                                    bundle=bid)
    meta = {
        "id": kid,
        "title": "cbo-{}".format(job),
        "code_file": "run.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": False,
        "dataset_sources": ["{}/{}".format(user, dataset)],
        "competition_sources": [],
        "kernel_sources": [],
    }
    if not dry:
        if os.path.isdir(PUSHDIR):
            shutil.rmtree(PUSHDIR)
        os.makedirs(PUSHDIR)
        with open(os.path.join(PUSHDIR, "run.py"), "w") as fh:
            fh.write(runner)
        with open(os.path.join(PUSHDIR, "kernel-metadata.json"), "w") as fh:
            json.dump(meta, fh, indent=2)
        say("  wrote {}/run.py and kernel-metadata.json".format(PUSHDIR))
    say("  runner requires bundle {} in the mounted dataset, every file hashing as listed".format(bid))
    say("  private {}  internet {}  gpu {}".format(
        meta["is_private"], meta["enable_internet"], meta["enable_gpu"]))
    say("  runner will search /kaggle/input/{0}, then /kaggle/input/datasets/{1}/{0}, "
        "then a walk of /kaggle/input to depth 3".format(dataset, user))
    say("  runner will call: {} --archive <found path> --outdir /kaggle/working {}".format(
        script, args))
    for name, role in shipped:
        if role == "resume":
            say("  runner will rebuild {} under /tmp/kgrun-ship and append it to --resume-from".format(name))
        else:
            say("  runner will rebuild {} under /tmp/kgrun-ship and replace runs/{} in the args".format(name, name))
    return kid


def push_reply(out):
    """The REPLY of PUSH VERDICT: stripped lines, blank and outdated-version warning lines removed."""
    return [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.strip().startswith(CLI_OUTDATED)]


def classify_push(rc, out):
    """PUSH VERDICT (docstring; ledger K12): ("PUSHED", N), ("CAPACITY", M) or ("UNCONFIRMED", reason)."""
    reply = push_reply(out)
    ok = [m.group(1) for m in (PUSH_OK_RE.match(ln) for ln in reply) if m]
    err = [ln for ln in reply if "error" in ln.lower()]
    if len(ok) == 1 and not err and rc == 0:
        return "PUSHED", ok[0]
    if not ok and len(reply) == 1:
        m = PUSH_CAPACITY_RE.match(reply[0])
        if m:
            return "CAPACITY", m.group(1)
    if not reply:
        reason = "kaggle printed nothing (exit {})".format(rc)
    elif len(ok) > 1:
        reason = "{} success lines".format(len(ok))
    elif ok and err:
        reason = "a success line beside an error line"
    elif ok:
        reason = "a success line, but the CLI exited {}".format(rc)
    else:
        reason = "no success line (CLI exit {})".format(rc)
    return "UNCONFIRMED", reason


def push(kid, dry):
    """Run "kaggle kernels push" and judge it (PUSH VERDICT). Returns only on PUSHED;
    SystemExit(CAPACITY_EXIT or UNCONFIRMED_EXIT) otherwise."""
    say("PUSH KERNEL (this starts a batch run; 12 hour cap)")
    STATE["push_started"] = True
    cmd = ["kaggle", "kernels", "push", "-p", PUSHDIR]
    if dry:
        run_cmd(cmd, dry)
        say("  (dry run: no push, no verdict)")
        return
    say("  $ " + " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    say(out.rstrip())
    say("  kaggle kernels push exit code {} (printed; the reply decides, PUSH VERDICT)".format(p.returncode))
    verdict, detail = classify_push(p.returncode, out)
    reply = " / ".join(push_reply(out)) or "(nothing)"
    if verdict == "PUSHED":
        say("PUSH VERDICT: PUSHED version {} of {}".format(detail, kid))
        return
    if verdict == "CAPACITY":
        say("PUSH VERDICT: CAPACITY (all {} batch CPU sessions of the account in use; Kaggle replied: {})".format(
            detail, reply))
        say(CAPACITY_LINE)
        say("  exit {}".format(CAPACITY_EXIT))
        raise SystemExit(CAPACITY_EXIT)
    say("PUSH VERDICT: UNCONFIRMED ({}; Kaggle replied: {})".format(detail, reply))
    say(UNCONFIRMED_LINE)
    say("  exit {}".format(UNCONFIRMED_EXIT))
    raise SystemExit(UNCONFIRMED_EXIT)


def status(kid, dry):
    out = run_cmd(["kaggle", "kernels", "status", kid], dry, check=False,
                  capture=True)
    return out.lower()


def poll(kid, every, dry):
    say("POLL until the run finishes (every {} s)".format(every))
    if dry:
        say("  (dry run: not polling)")
        return "dry"
    t0 = time.time()
    while True:
        out = status(kid, False)
        if "complete" in out:
            say("  finished after {:.0f} s".format(time.time() - t0))
            return "complete"
        if "error" in out or "cancel" in out:
            say("  run did not complete after {:.0f} s".format(time.time() - t0))
            return "error"
        time.sleep(every)


def fetch(kid, job, dry):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(ROOT, "runs", "{}-kaggle-{}".format(job, stamp))
    say("FETCH OUTPUT into {}".format(outdir))
    if not dry:
        os.makedirs(outdir)
    run_cmd(["kaggle", "kernels", "output", kid, "-p", outdir], dry)
    if dry:
        return outdir
    try:
        lines = write_manifest(outdir)
    except ManifestRefused as e:
        raise SystemExit("no manifest written in {}: {}".format(outdir, e))
    say("  {} files, manifest written to sha256.txt".format(len(lines)))
    for ln in lines:
        say("    " + ln)
    return outdir


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["bundle", "dataset-create",
                                      "dataset-version", "push", "status",
                                      "fetch", "run", "launch"])
    p.add_argument("--job", default="job", help="short name; kernel is cbo-<job>")
    p.add_argument("--script", default="detcheck.py",
                   help="script in the bundle for the runner to call")
    p.add_argument("--args", default="--workers 4",
                   help="flags passed to that script, in one quoted string")
    p.add_argument("--user", default=DEFAULT_USER)
    p.add_argument("--dataset", default=DEFAULT_DATASET)
    p.add_argument("--note", default=None, help="dataset version message")
    p.add_argument("--poll", type=int, default=60, help="seconds between polls")
    p.add_argument("--ready-poll", type=int, default=30,
                   help="seconds between dataset status polls after create/version")
    p.add_argument("--ready-timeout", type=int, default=1800,
                   help="seconds to wait for the dataset to report ready before giving up")
    p.add_argument("--first", action="store_true",
                   help="create the dataset instead of versioning it")
    p.add_argument("--resume-dirs", default="",
                   help="fetched run folders under runs/, passed to the script as --resume-from")
    p.add_argument("--data-dirs", default="",
                   help="run folders under runs/ the script reads; runs/<name> in --args is replaced")
    p.add_argument("--warn-mb", type=float, default=1000.0,
                   help="warn when the bundle exceeds this many MB (a local choice, not a Kaggle limit)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    STATE["action"] = a.action
    if "--resume-from" in a.args.split():
        raise SystemExit("--args must not contain --resume-from; name the folders with --resume-dirs")
    ship = ship_list(a.resume_dirs, a.data_dirs)
    members = arg_members(a.args)
    for path, role in ship:
        if role == "data" and "runs/" + os.path.basename(os.path.normpath(path)) not in members:
            raise SystemExit("data folder {} is not named in --args as runs/{}".format(
                path, os.path.basename(os.path.normpath(path))))

    dry = a.dry_run
    note = a.note or "kgrun {} {}".format(a.job, datetime.datetime.now().isoformat(timespec="seconds"))
    kid = "{}/cbo-{}".format(a.user, a.job)

    say("=" * 78)
    say("kgrun  action {}  job {}  dataset {}/{}".format(a.action, a.job,
                                                         a.user, a.dataset))
    say("  repository {}".format(ROOT))
    if dry:
        say("  DRY RUN: commands are printed, nothing is executed")
    say("=" * 78)

    if a.action == "bundle":
        build_bundle(a.user, a.dataset, dry, ship, a.warn_mb)
    elif a.action == "dataset-create":
        _, bid = build_bundle(a.user, a.dataset, dry)
        dataset_create(a.user, a.dataset, dry)
        wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
        wait_version(a.user, a.dataset, bid, a.ready_poll, a.ready_timeout, dry)
    elif a.action == "dataset-version":
        _, bid = build_bundle(a.user, a.dataset, dry, ship, a.warn_mb)
        dataset_version(a.user, a.dataset, note, dry)
        wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
        wait_version(a.user, a.dataset, bid, a.ready_poll, a.ready_timeout, dry)
    elif a.action == "push":
        git_guard()
        shipped = [[os.path.basename(os.path.normpath(x)), r] for x, r in ship]
        bid = "dry-run" if dry else bundle_id_on_disk()
        if shipped:
            say("  push alone does not rebuild the bundle: the dataset's current version must already hold "
                "these folders (the runner checks and exits 2 otherwise)")
        wait_version(a.user, a.dataset, bid, a.ready_poll, a.ready_timeout, dry)
        write_kernel(a.user, a.dataset, a.job, a.script, a.args, dry, shipped, bid)
        push(kid, dry)
    elif a.action == "status":
        status(kid, dry)
    elif a.action == "fetch":
        fetch(kid, a.job, dry)
    elif a.action == "launch":
        git_guard()
        shipped, bid = build_bundle(a.user, a.dataset, dry, ship, a.warn_mb)
        if a.first:
            say("DATASET PATH: UPLOADED NEW VERSION  bundle {}  because: --first creates the dataset".format(bid))
            dataset_create(a.user, a.dataset, dry)
            wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
            wait_version(a.user, a.dataset, bid, a.ready_poll, a.ready_timeout, dry)
        else:
            dataset_step(a.user, a.dataset, note, bid, dry, a.ready_poll, a.ready_timeout)
        write_kernel(a.user, a.dataset, a.job, a.script, a.args, dry, shipped, bid)
        push(kid, dry)
        say("LAUNCHED {}; not polled, not fetched. Check it with:".format(kid))
        say("  python scripts/kgrun.py status --job {}".format(a.job))
    else:
        git_guard()
        shipped, bid = build_bundle(a.user, a.dataset, dry, ship, a.warn_mb)
        if a.first:
            dataset_create(a.user, a.dataset, dry)
        else:
            dataset_version(a.user, a.dataset, note, dry)
        wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
        wait_version(a.user, a.dataset, bid, a.ready_poll, a.ready_timeout, dry)
        write_kernel(a.user, a.dataset, a.job, a.script, a.args, dry, shipped, bid)
        push(kid, dry)
        verdict = poll(kid, a.poll, dry)
        if verdict in ("complete", "dry"):
            fetch(kid, a.job, dry)
        else:
            say("Run did not complete. Fetch the log yourself with:")
            say("  python scripts/kgrun.py fetch --job {}".format(a.job))
    say("=" * 78)


def entry():
    """main(), with exit 10 for a launch that stopped before the push (docstring; ledger K9)."""
    try:
        main()
    except BaseException as e:
        if STATE["action"] != "launch" or STATE["push_started"]:
            raise
        if isinstance(e, SystemExit):
            if e.code is None or e.code == 0:
                raise
            cause = e.code if isinstance(e.code, str) else "exit code {}".format(e.code)
        else:
            cause = traceback.format_exc().rstrip()
        say(str(cause))
        say(NOT_PUSHED_LINE)
        say("  no kernel push was attempted by this process; exit {}".format(NOT_PUSHED_EXIT))
        sys.exit(NOT_PUSHED_EXIT)


if __name__ == "__main__":
    entry()
