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
     until "kaggle datasets status" reports ready (--ready-poll, default 30 s;
     --ready-timeout, default 1800 s; on timeout nothing is pushed);
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
  reads ~/.kaggle/kaggle.json itself. It does not write to zenodo-v1. It does
  not overwrite an existing run folder.

RESUMPTION ON KAGGLE (ledger K5, closed 2026-10-11)
  --resume-dirs runs/A[,runs/B]   earlier fetched run folders, passed to the
                                  script as --resume-from (CLAUDE.md rule 17)
  --data-dirs runs/C[,runs/D]     earlier run folders the script reads as
                                  input, for example calprec2's --throughput.
                                  Every token of --args equal to "runs/<name>"
                                  is replaced on Kaggle by the folder's path
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
import json
import os
import shutil
import subprocess
import sys
import time

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
            hits = sum(1 for x in ARGS if x == token)
            if hits == 0:
                fail("data folder " + name + " is not named in the args as " + token)
            ARGS = [dst if x == token else x for x in ARGS]
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
        if f.endswith(".py") and f != "kgrun.py":
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
    if not dry:
        if shipped:
            with open(os.path.join(BUNDLE, SHIP_INDEX), "w") as fh:
                json.dump(index, fh, indent=2)
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
    return shipped


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


def write_kernel(user, dataset, job, script, args, dry, shipped=()):
    kid = "{}/cbo-{}".format(user, job)
    say("GENERATE KERNEL  {}".format(kid))
    runner = RUNNER_TEMPLATE.format(user=user, dataset=dataset, script=script, job=job,
                                    args=args, ship=[list(x) for x in shipped], index=SHIP_INDEX)
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


def push(kid, dry):
    say("PUSH KERNEL (this starts a batch run; 12 hour cap)")
    run_cmd(["kaggle", "kernels", "push", "-p", PUSHDIR], dry, capture=True)


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
                                      "fetch", "run"])
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
    if "--resume-from" in a.args.split():
        raise SystemExit("--args must not contain --resume-from; name the folders with --resume-dirs")
    ship = ship_list(a.resume_dirs, a.data_dirs)
    for path, role in ship:
        if role == "data" and "runs/" + os.path.basename(os.path.normpath(path)) not in a.args.split():
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
        build_bundle(a.user, a.dataset, dry)
        dataset_create(a.user, a.dataset, dry)
        wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
    elif a.action == "dataset-version":
        build_bundle(a.user, a.dataset, dry, ship, a.warn_mb)
        dataset_version(a.user, a.dataset, note, dry)
        wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
    elif a.action == "push":
        git_guard()
        shipped = [[os.path.basename(os.path.normpath(x)), r] for x, r in ship]
        if shipped:
            say("  push alone does not rebuild the bundle: the dataset's current version must already hold "
                "these folders (the runner checks and exits 2 otherwise)")
        write_kernel(a.user, a.dataset, a.job, a.script, a.args, dry, shipped)
        push(kid, dry)
    elif a.action == "status":
        status(kid, dry)
    elif a.action == "fetch":
        fetch(kid, a.job, dry)
    else:
        git_guard()
        shipped = build_bundle(a.user, a.dataset, dry, ship, a.warn_mb)
        if a.first:
            dataset_create(a.user, a.dataset, dry)
        else:
            dataset_version(a.user, a.dataset, note, dry)
        wait_ready(a.user, a.dataset, a.ready_poll, a.ready_timeout, dry)
        write_kernel(a.user, a.dataset, a.job, a.script, a.args, dry, shipped)
        push(kid, dry)
        verdict = poll(kid, a.poll, dry)
        if verdict in ("complete", "dry"):
            fetch(kid, a.job, dry)
        else:
            say("Run did not complete. Fetch the log yourself with:")
            say("  python scripts/kgrun.py fetch --job {}".format(a.job))
    say("=" * 78)


if __name__ == "__main__":
    main()
