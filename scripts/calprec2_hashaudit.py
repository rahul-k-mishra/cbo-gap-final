"""
calprec2_hashaudit.py  --  CBO-GAP: did each calprec2 long shard run the code
of the commit it was launched from? (ledger K7)

WHY
  kgrun waited for "kaggle datasets status" to say ready, and that reports the
  dataset, not the version just uploaded (K7: rerun-smoke-arch-a1 mounted the
  previous version). Every calprec2-long shard shipped the same folder, so a
  stale mount would not have stopped it: it would have run the previous
  version's scripts. calprec2.py hashes its own file and costprobe2.py's at
  run time, and V1 hashes the twelve archived modules it imported, all from
  the mounted dataset. Those printed hashes are therefore what ran. This
  script compares each with the file the launch commit held.

WHAT IT READS (read-only; it writes no file)
  - runs/<prefix>-s<k>of<n>-a<A>-kaggle-*/ for k = 0 .. n-1: sha256.txt, the
    kernel log cbo-<prefix>-s<k>of<n>-a<A>.log and */calprec2_params.csv;
  - logs/kgrun-<prefix>-s<k>of<n>-a<A>.log, for the launch time;
  - git: first-parent history of HEAD, and file contents at commits
    (git rev-list, git show, git log, git merge-base, git status). Nothing is
    written to git or to disk. Its console is the record: tee it into logs/.

PRE-SPECIFIED RULES (fixed before first execution)
  A1  RECORD. Every folder matching the shard's pattern is examined. A folder
      with no sha256.txt is NOT A RECORD (for example the empty, untracked
      runs/calprec2-long-s2of26-a1-kaggle-20261013-213019 left by the aborted
      fetch): printed and skipped. A folder with sha256.txt must hold exactly
      the files it lists, each hashing as listed, and be tracked by git and
      unmodified; otherwise the shard is INCOMPLETE. A shard with no record
      folder is INCOMPLETE. With more than one record folder, every one is
      audited and all must pass.
  A2  LAUNCH TIME. The launch log's dataset version note
      "-m kgrun <job> YYYY-MM-DDTHH:MM:SS", with <job> equal to the folder's
      job, exactly one distinct such note. It is the laptop's local time
      without a zone; it is read at --launch-utc-offset (default +05:30, the
      offset of every laptop commit of that period). No note, or two
      different notes: INCOMPLETE.
      Worked example: s25 "2026-10-23T02:27:15" at +05:30 is
      2026-10-22T20:57:15 UTC.
  A3  LAUNCH COMMIT C. Walking HEAD's first-parent history from the tip
      backwards, the first commit whose committer time is at or before the
      launch time. kgrun's git guard
      refused to launch unless HEAD was pushed, so HEAD at launch was a
      commit made before it. Check: C must be an ancestor of (or equal to)
      the first commit that added the launch log; otherwise INCOMPLETE.
      Commits after C up to that log commit that changed an audited path are
      printed as WINDOW notes; they do not change the verdict.
      Limitation, stated: kgrun bundled scripts/ from the working tree, not
      from HEAD. An uncommitted edit at launch would show here as FAIL with
      "matches no committed version" (A6); this audit cannot tell it apart
      from any other uncommitted code.
  A4  HASH LINES of the kernel log (its JSON stream's "data" joined):
        "  script   sha256 <64 hex>"           -> scripts/calprec2.py
        "  costprobe2.py sha256 <64 hex>"      -> scripts/costprobe2.py
        "  <module>  <64 hex>  ok|MISMATCH"    -> zenodo-v1/<module>.py (V1)
      Any other line holding a 64-hex string is UNCLASSIFIED: the shard is
      INCOMPLETE, because a hash was printed that this audit cannot place.
      The script line and the costprobe2 line must each occur, with one
      value; otherwise INCOMPLETE. V1 must list the twelve modules of
      costprobe2.MODULES; a missing one is INCOMPLETE.
  A5  COMPARISON. For each hash line: PASS when the printed hash equals the
      sha256 of the file at C (git show C:<path>), byte for byte; FAIL
      otherwise, and FAIL when the path does not exist at C. Also, the
      record's calprec2_params.csv (exactly one) must give script_sha256 and
      costprobe2_sha256 equal to the header's; a difference is FAIL, a
      missing file or key INCOMPLETE.
      Worked example: s25 prints script sha256 c339ca9d...c14d; the file
      scripts/calprec2.py at C hashes to c339ca9d...c14d: PASS. Had it
      printed 7a44dc5c...6207 (the pre-ceiling calprec2.py, ledger N28
      third addendum) against c339ca9d...c14d at C: FAIL.
  A6  DIAGNOSIS of a FAIL (printed, not part of the verdict): the
      first-parent commits whose file at <path> hashes to the printed value.
      "matches <commit> (<date>), before the launch" is what a stale dataset
      version (K7) looks like; "matches no committed version" means code
      that was never committed ran.
  A7  SHARD VERDICT. PASS: at least one record folder, every hash line PASS,
      params consistent. FAIL: any FAIL. INCOMPLETE: no FAIL, but anything
      A1 to A5 calls INCOMPLETE.
  A8  OVERALL VERDICT, one line, exactly one of:
        VERDICT: PASS -- all <n> shards ran the code of their launch commits
        VERDICT: FAIL -- shards that did not run their launch commit's code:
                 s<i>, ...; not auditable: s<j>, ... (or "none")
        VERDICT: INCOMPLETE -- no shard failed, but not auditable: s<j>, ...
      PASS requires all <n> shards PASS. Exit code 0, 1, 2 respectively.
  A9  LEDGER PIN, one line after the verdict. The ledger (N28, result of
      2026-10-23) records calprec2.py c339ca9d...c14d and costprobe2.py
      ea5cb2e1...f64b, abbreviated. PASS when every record's printed script
      hash starts with c339ca9d and ends with c14d and every printed
      costprobe2 hash starts with ea5cb2e1 and ends with f64b; FAIL
      otherwise, naming the shards. The abbreviation is all the ledger
      holds; eight leading and four trailing hex digits are what is compared.
      Reading: VERDICT PASS with LEDGER PIN PASS means every shard ran the
      code of its launch commit and that code is the code the ledger names.
      VERDICT PASS with LEDGER PIN FAIL means the launch commits themselves
      held other code than the ledger says. A FAIL in either is a defect
      to be recorded before the calibration's 336 cells are used.

NOT APPLICABLE OF CLAUDE.md RULE 5
  No trajectory is evolved, no random number is drawn, no output file is
  written: there is no seed table and no per-realization file. The Pool,
  --workers and the per-worker peak RSS are kept.

USAGE (repository root)
  python scripts/calprec2_hashaudit.py --workers 2

Python 3.8 to 3.11 syntax. Standard library only, plus scripts/manifest.py.
"""

import argparse
import csv
import datetime
import glob
import hashlib
import json
import multiprocessing
import os
import platform
import re
import resource
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from manifest import list_files, sha256_of  # noqa: E402

ROOT = os.path.dirname(HERE)
MODULES = ["ess_surface", "visibility", "mechanism", "control", "boundary",
           "regime", "law", "sigma", "crossed", "cliff", "regimemap", "exactcal"]
PIN = {"scripts/calprec2.py": ("c339ca9d", "c14d"), "scripts/costprobe2.py": ("ea5cb2e1", "f64b")}

RE_NOTE = re.compile(r"-m kgrun (\S+) (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)")
RE_SCRIPT = re.compile(r"^  script   sha256 ([0-9a-f]{64})\s*$")
RE_CP2 = re.compile(r"^  costprobe2\.py sha256 ([0-9a-f]{64})\s*$")
RE_MOD = re.compile(r"^  (\w+)\s+([0-9a-f]{64})  (ok|MISMATCH)\s*$")
RE_HEX = re.compile(r"[0-9a-f]{64}")

G = {}


def git(args, binary=False):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout if binary else p.stdout.decode("utf-8", "replace")
    return p.returncode, out


def blob_sha(commit, path):
    rc, out = git(["show", "{}:{}".format(commit, path)], binary=True)
    if rc != 0:
        return None
    return hashlib.sha256(out).hexdigest()


def init(commits, offset):
    G["commits"] = commits
    G["offset"] = offset


def parse_offset(s):
    m = re.match(r"^([+-])(\d\d):(\d\d)$", s)
    if not m:
        raise SystemExit("--launch-utc-offset must look like +05:30")
    d = datetime.timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))
    return d if m.group(1) == "+" else -d


def to_epoch(local, offset):
    naive = datetime.datetime.strptime(local, "%Y-%m-%dT%H:%M:%S")
    return int(round((naive - offset - datetime.datetime(1970, 1, 1)).total_seconds()))


def kernel_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    try:
        ents = json.loads(raw)
        return "".join(e.get("data", "") for e in ents if isinstance(e, dict))
    except ValueError:
        return raw


def verify_record(folder):
    """A1: list of problems, [] when the folder is an intact tracked record."""
    man = os.path.join(folder, "sha256.txt")
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
        out.append("files present differ from those sha256.txt lists")
    for rel in files:
        if rel in listed and sha256_of(os.path.join(folder, rel)) != listed[rel]:
            out.append("hash mismatch at " + rel)
    relf = os.path.relpath(folder, ROOT)
    rc, _ = git(["ls-files", "--error-unmatch", os.path.join(relf, "sha256.txt")])
    if rc != 0:
        out.append("sha256.txt not tracked by git")
    rc, st = git(["status", "--porcelain", "--untracked-files=all", "--", relf])
    if rc != 0 or st.strip():
        out.append("modified or untracked under git: " + st.strip().replace("\n", "; "))
    return out


def diagnose(path, printed, launch_ct):
    """A6: where in first-parent history the printed hash occurs for this path."""
    rc, out = git(["log", "--first-parent", "--format=%H %ct %ci", "HEAD", "--", path])
    hits = []
    for ln in out.splitlines():
        sha, ct, ci = ln.split(" ", 2)
        if blob_sha(sha, path) == printed:
            hits.append((int(ct), sha[:10], ci))
    if not hits:
        return "matches no committed version of {}".format(path)
    return "; ".join("matches {} ({}), {} the launch".format(
        s, ci, "before" if ct <= launch_ct else "after") for ct, s, ci in sorted(hits))


def audit_record(prefix, k, n, folder, lines):
    """One record folder: (status, problems) and per-line output appended to lines."""
    status = "PASS"
    name = os.path.basename(folder)
    m = re.match(r"^({}-s{}of{}-a(\d+))-kaggle-".format(re.escape(prefix), k, n), name)
    job = m.group(1)
    lines.append("  record {}".format(os.path.relpath(folder, ROOT)))
    prob = verify_record(folder)
    if prob:
        lines.append("    INCOMPLETE  A1: " + "; ".join(prob))
        return "INCOMPLETE", {}
    lines.append("    A1 manifest verified, tracked and clean")

    launch = os.path.join(ROOT, "logs", "kgrun-{}.log".format(job))
    if not os.path.isfile(launch):
        lines.append("    INCOMPLETE  A2: no launch log logs/kgrun-{}.log".format(job))
        return "INCOMPLETE", {}
    with open(launch, encoding="utf-8", errors="replace") as fh:
        notes = set(t for j, t in RE_NOTE.findall(fh.read()) if j == job)
    if len(notes) != 1:
        lines.append("    INCOMPLETE  A2: {} distinct version notes for {} in the launch log: {}".format(
            len(notes), job, sorted(notes)))
        return "INCOMPLETE", {}
    local = notes.pop()
    t = to_epoch(local, G["offset"])
    before = [sha for ct, sha in G["commits"] if ct <= t]
    if not before:
        lines.append("    INCOMPLETE  A3: no commit at or before the launch time")
        return "INCOMPLETE", {}
    c = before[0]
    rc, added = git(["log", "--diff-filter=A", "--format=%H", "--", os.path.relpath(launch, ROOT)])
    added = added.split()
    if not added:
        lines.append("    INCOMPLETE  A3: the launch log was never committed")
        return "INCOMPLETE", {}
    lcommit = added[-1]
    rc, _ = git(["merge-base", "--is-ancestor", c, lcommit])
    _, cci = git(["show", "-s", "--format=%ci", c])
    lines.append("    A2 launch {} local, {} UTC   A3 launch commit {} ({})   log added in {}".format(
        local, datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%S"), c[:10], cci.strip(),
        lcommit[:10]))
    if rc != 0:
        lines.append("    INCOMPLETE  A3: launch commit {} is not an ancestor of {}".format(c[:10], lcommit[:10]))
        return "INCOMPLETE", {}

    kl = os.path.join(folder, "cbo-{}.log".format(job))
    if not os.path.isfile(kl):
        lines.append("    INCOMPLETE  A4: no kernel log cbo-{}.log".format(job))
        return "INCOMPLETE", {}
    text = kernel_text(kl)
    printed = {}
    multi = []
    unclassified = []
    for ln in text.splitlines():
        if not RE_HEX.search(ln):
            continue
        ms, mc, mm = RE_SCRIPT.match(ln), RE_CP2.match(ln), RE_MOD.match(ln)
        if ms:
            key, val = "scripts/calprec2.py", ms.group(1)
        elif mc:
            key, val = "scripts/costprobe2.py", mc.group(1)
        elif mm and mm.group(1) in MODULES:
            key, val = "zenodo-v1/{}.py".format(mm.group(1)), mm.group(2)
        else:
            unclassified.append(ln.strip())
            continue
        if key in printed and printed[key] != val:
            multi.append(key)
        printed[key] = val
    if unclassified:
        status = "INCOMPLETE"
        for u in unclassified:
            lines.append("    INCOMPLETE  A4: UNCLASSIFIED hash line: " + u)
    for key in sorted(set(multi)):
        status = "INCOMPLETE"
        lines.append("    INCOMPLETE  A4: {} printed with more than one value".format(key))
    need = ["scripts/calprec2.py", "scripts/costprobe2.py"] + ["zenodo-v1/{}.py".format(x) for x in MODULES]
    for key in need:
        if key not in printed:
            status = "INCOMPLETE"
            lines.append("    INCOMPLETE  A4: no hash line for {}".format(key))

    for key in need:
        if key not in printed or key in multi:
            continue
        ref = blob_sha(c, key)
        ok = ref == printed[key]
        lines.append("    {:<4} {:<26} printed {}".format("PASS" if ok else "FAIL", key, printed[key]))
        lines.append("         {:<26} at {} {}".format("", c[:10], ref if ref else "(path absent)"))
        if not ok:
            status = "FAIL"
            lines.append("         A6: " + diagnose(key, printed[key], t))

    rc, changed = git(["log", "--first-parent", "--format=%h %ci", "{}..{}".format(c, lcommit), "--"] + need)
    for ln in changed.splitlines():
        lines.append("    WINDOW  audited path changed between launch commit and log commit: " + ln)

    params = glob.glob(os.path.join(folder, "*", "calprec2_params.csv"))
    if len(params) != 1:
        if status == "PASS":
            status = "INCOMPLETE"
        lines.append("    INCOMPLETE  A5: {} calprec2_params.csv file(s), expected 1".format(len(params)))
    else:
        with open(params[0], newline="") as fh:
            kv = dict((r[0], r[1]) for r in csv.reader(fh) if len(r) >= 2)
        for pk, key in (("script_sha256", "scripts/calprec2.py"), ("costprobe2_sha256", "scripts/costprobe2.py")):
            if pk not in kv or key not in printed:
                if status == "PASS":
                    status = "INCOMPLETE"
                lines.append("    INCOMPLETE  A5: params {} or header line missing".format(pk))
            elif kv[pk] != printed[key]:
                status = "FAIL"
                lines.append("    FAIL  A5: params {} {} differs from the header's {}".format(pk, kv[pk], printed[key]))
            else:
                lines.append("    PASS  A5: params {} equals the header".format(pk))
    return status, printed


def audit_shard(task):
    prefix, k, n = task
    lines = ["shard s{}of{}".format(k, n)]
    folders = sorted(glob.glob(os.path.join(ROOT, "runs", "{}-s{}of{}-a*-kaggle-*".format(prefix, k, n))))
    folders = [f for f in folders if os.path.isdir(f)]
    statuses = []
    pinned = []
    for f in folders:
        if not os.path.isfile(os.path.join(f, "sha256.txt")):
            lines.append("  NOT A RECORD (no sha256.txt, {} entries): {}".format(
                len(os.listdir(f)), os.path.relpath(f, ROOT)))
            continue
        st, printed = audit_record(prefix, k, n, f, lines)
        statuses.append(st)
        pinned.append(printed)
    if not statuses:
        lines.append("  INCOMPLETE  A1: no record folder")
        verdict = "INCOMPLETE"
    elif "FAIL" in statuses:
        verdict = "FAIL"
    elif "INCOMPLETE" in statuses:
        verdict = "INCOMPLETE"
    else:
        verdict = "PASS"
    pin_ok = bool(pinned)
    for printed in pinned:
        for key, (head, tail) in PIN.items():
            v = printed.get(key, "")
            if not (v.startswith(head) and v.endswith(tail)):
                pin_ok = False
    lines.append("  shard verdict {}   ledger pin {}".format(verdict, "PASS" if pin_ok else "FAIL"))
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return k, verdict, pin_ok, lines, os.getpid(), rss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("--prefix", default="calprec2-long")
    ap.add_argument("--nshards", type=int, default=26)
    ap.add_argument("--launch-utc-offset", default="+05:30")
    a = ap.parse_args()
    offset = parse_offset(a.launch_utc_offset)
    try:
        import numpy
        npv = numpy.__version__
    except ImportError:
        npv = "not installed (not used)"
    _, head = git(["rev-parse", "HEAD"])
    _, branch = git(["rev-parse", "--abbrev-ref", "HEAD"])
    print("=" * 96)
    print("CBO-GAP calprec2_hashaudit -- printed script hashes of the {} shards against their launch "
          "commits (ledger K7)".format(a.prefix))
    print("=" * 96)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(npv))
    print("  platform {}   workers {}".format(platform.platform(), a.workers))
    print("  repository {}   HEAD {} ({})".format(ROOT, head.strip(), branch.strip()))
    print("  shards   {}-s0of{} .. s{}of{}   launch time read at UTC{}".format(
        a.prefix, a.nshards, a.nshards - 1, a.nshards, a.launch_utc_offset))
    print("  audited  scripts/calprec2.py, scripts/costprobe2.py, zenodo-v1/<m>.py for m in {}".format(
        ", ".join(MODULES)))
    print("  ledger pin  calprec2.py {}...{}   costprobe2.py {}...{}".format(
        PIN["scripts/calprec2.py"][0], PIN["scripts/calprec2.py"][1],
        PIN["scripts/costprobe2.py"][0], PIN["scripts/costprobe2.py"][1]))
    print("  rules A1 to A9 in the docstring; no seeds (nothing random); writes no file")
    print("=" * 96)
    sys.stdout.flush()

    _, out = git(["rev-list", "--first-parent", "--timestamp", "HEAD"])
    commits = []
    for ln in out.splitlines():
        ct, sha = ln.split()
        commits.append((int(ct), sha))
    tasks = [(a.prefix, k, a.nshards) for k in range(a.nshards)]
    pool = multiprocessing.Pool(a.workers, initializer=init, initargs=(commits, offset))
    try:
        res = sorted(pool.map(audit_shard, tasks))
    finally:
        pool.close()
        pool.join()

    for _, _, _, lines, _, _ in res:
        print("\n".join(lines))
        print("-" * 96)
    peak = {}
    for _, _, _, _, pid, rss in res:
        peak[pid] = max(peak.get(pid, 0), rss)
    print("  per-worker peak RSS: " + "  ".join("pid {} {:.1f} MB".format(p, r / 1024.0)
                                                for p, r in sorted(peak.items())))
    fail = ["s{}".format(k) for k, v, _, _, _, _ in res if v == "FAIL"]
    inc = ["s{}".format(k) for k, v, _, _, _, _ in res if v == "INCOMPLETE"]
    pinbad = ["s{}".format(k) for k, _, p, _, _, _ in res if not p]
    print("=" * 96)
    if fail:
        print("VERDICT: FAIL -- shards that did not run their launch commit's code: {}; not auditable: {}".format(
            ", ".join(fail), ", ".join(inc) or "none"))
        code = 1
    elif inc:
        print("VERDICT: INCOMPLETE -- no shard failed, but not auditable: {}".format(", ".join(inc)))
        code = 2
    else:
        print("VERDICT: PASS -- all {} shards ran the code of their launch commits".format(a.nshards))
        code = 0
    if pinbad:
        print("LEDGER PIN: FAIL -- printed hashes not calprec2.py {}...{} / costprobe2.py {}...{} in: {}".format(
            PIN["scripts/calprec2.py"][0], PIN["scripts/calprec2.py"][1],
            PIN["scripts/costprobe2.py"][0], PIN["scripts/costprobe2.py"][1], ", ".join(pinbad)))
    else:
        print("LEDGER PIN: PASS -- every record printed calprec2.py {}...{} and costprobe2.py {}...{}".format(
            PIN["scripts/calprec2.py"][0], PIN["scripts/calprec2.py"][1],
            PIN["scripts/costprobe2.py"][0], PIN["scripts/costprobe2.py"][1]))
    print("=" * 96)
    return code


if __name__ == "__main__":
    sys.exit(main())
