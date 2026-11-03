"""
c5bitcmp.py  --  CBO-GAP: does a change of Kaggle's Python change the bits of
a c5run row?  (ledger N45, "C5 IMAGE SPLIT"; CLAUDE.md rules 16 and 18;
Rahul's instruction 2026-11-03)

ANALYSIS ONLY. WRITES NOTHING. Its output is its console log, which Rahul
redirects into logs/ (noclobber).

WHAT THIS DOES, IN PLAIN LANGUAGE
---------------------------------
The C5 queue halted on 2026-11-03 at shard 13 because Kaggle's image had
moved from Python 3.13.15 to 3.13.18 (NumPy 2.1.3 in both). Shards 0 to 12
ran on 3.13.15. Every c5run task's seed is keyed by the task, not by its
position, so a task re-run anywhere is the same computation on the same
seed. This script takes a committed shard folder (REF) and a fresh re-run of
the same shard (NEW, same arguments, no resume) and asks whether every
computed field of every row is the same, bit for bit.

c5run.py writes every float with repr(float(x)) (c5run.py, the row.update
block of the task function), and repr of a Python float round-trips
exactly. So two cells are bit-identical if and only if their strings are
equal. No tolerance enters anywhere.

PRE-SPECIFIED RULES (fixed 2026-11-03, before first execution)
  P0  PRECONDITIONS, each a hard stop with exit 2 and a named message:
      (a) each folder is a run folder with sha256.txt; every listed file
          hashes as listed (scripts/manifest.py sha256_of) and no file is
          present that the manifest does not list;
      (b) each folder holds exactly one c5run_params.csv and one
          c5run_real.csv, in the same subfolder;
      (c) the two params files agree on every key except "python"
          (script and five module hashes, mode run, shard, nshards,
          workers, stop_after, budget_mb, kind, timing, beta_table,
          rerun_plan, numpy, resume_from empty in NEW). A NumPy difference
          is a stop: this script answers the Python question only;
      (d) in each file every row ends "ok", no tid repeats, and the two
          tid sets are equal.
      Worked example: NEW was launched with --shard 11 by mistake: (c)
      fails on "shard 12 vs 11", exit 2. NEW's numpy prints 2.2.0: (c)
      fails on numpy, exit 2.
  B   BITWISE. COMPARED = every column of c5run_real.csv except env,
      wall_s, rss_mb and rss_flag (platform and timing: they are expected
      to differ and carry no computed value). For each tid, B holds iff
      every COMPARED field is the same string in REF and NEW.
      VERDICT IDENTICAL iff B holds for every tid; else DIFFERENT.
      Worked example: REF E_json {"10": "0.0029542882344408957", ...}, NEW
      the same string: B holds for that row. NEW E_json differs at J 40
      in the last printed digit: B fails for that row; the verdict is
      DIFFERENT whatever the other rows show.
  M   MAGNITUDE (description only, printed when DIFFERENT): for each
      differing float field, the distance in units in the last place
      (both values reinterpreted as int64 by NumPy, sign-adjusted) and
      |a - b| / max(|a|, |b|), with the row and J; then the largest of
      each over all rows. M decides nothing.
  NULL RATE: B and P0 are deterministic comparisons of committed strings
      and hashes. Under the null "the two runs computed the same bits"
      B cannot fire (probability 0, by construction: equal strings are
      equal), and under the alternative it fires on any single differing
      bit in a compared field. M is not a criterion. The null fixture
      (two copies of one folder) must print IDENTICAL; the alternative
      fixture (one E_json digit changed, manifest rewritten) must print
      DIFFERENT.

WHAT EACH OUTCOME MEANS (fixed before execution; ledger N45)
  IDENTICAL: for the keys of this shard (all four d, both rows, six
      objectives), the Python change 3.13.15 -> 3.13.18 changed no bit of
      c5run's output. The 13 shards stand; the queue continues on 3.13.18
      once the queue's pin is moved by a recorded decision and detcheck
      has passed on the new image (rule 16). The paper states the split
      and this check.
  DIFFERENT: the split matters at the bit level. Shards 0 to 12 are re-run
      on the image the remaining shards run on, so that every C5 number
      comes from one image; M is reported in the supplement. Whether the
      cause is Python or the Kaggle host is not settled by this check (see
      LIMITS) and is not needed for that decision.

LIMITS
  This compares one shard's keys. It does not prove that no key of another
  shard differs, but every key goes through the same code path
  (one_realisation and audit_one) with the same operations; only array
  sizes and objectives vary, and this shard covers every d and objective.
  If DIFFERENT, it cannot separate a Python effect from a host CPU
  effect (NumPy chooses SIMD kernels at run time by CPU), because neither
  run printed its CPU model.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/c5bitcmp.py --ref runs/<REF> --new runs/<NEW> --workers 2
EXIT CODES
  0 IDENTICAL; 1 DIFFERENT; 2 precondition failed (P0).
"""

import argparse
import csv
import json
import multiprocessing
import os
import platform
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manifest import list_files, sha256_of                     # noqa: E402

PARAMS_CSV = "c5run_params.csv"
ROWS_CSV = "c5run_real.csv"
NOT_COMPARED = ("env", "wall_s", "rss_mb", "rss_flag")
MAY_DIFFER = ("python",)
JSON_FIELDS = ("E_json", "extras_json", "audit_ratios")
FLOAT_FIELDS = ("le0", "le_redraw", "audit_ref", "beta")


class Stop(Exception):
    pass


def say(s=""):
    print(s, flush=True)


def verify_folder(folder):
    """P0 (a), (b). Return (params path, rows path)."""
    man = os.path.join(folder, "sha256.txt")
    if not os.path.isfile(man):
        raise Stop("P0(a) {}: no sha256.txt".format(folder))
    listed = {}
    with open(man, newline="") as fh:
        for ln in fh.read().splitlines():
            if not ln.strip():
                continue
            h, _, rel = ln.partition("  ")
            if len(h) != 64 or not rel:
                raise Stop("P0(a) {}: malformed manifest line {!r}".format(folder, ln))
            listed[rel] = h
    files, bad = list_files(folder)
    if bad:
        raise Stop("P0(a) {}: not a regular file: {}".format(folder, bad[0]))
    if sorted(listed) != files:
        extra = sorted(set(files) - set(listed))
        missing = sorted(set(listed) - set(files))
        raise Stop("P0(a) {}: unlisted {} / missing {}".format(folder, extra, missing))
    for rel in files:
        if sha256_of(os.path.join(folder, rel)) != listed[rel]:
            raise Stop("P0(a) {}: hash mismatch on {}".format(folder, rel))
    ps = [r for r in files if os.path.basename(r) == PARAMS_CSV]
    rs = [r for r in files if os.path.basename(r) == ROWS_CSV]
    if len(ps) != 1 or len(rs) != 1 or os.path.dirname(ps[0]) != os.path.dirname(rs[0]):
        raise Stop("P0(b) {}: expected one {} and one {} in one subfolder, found {} and {}".format(
            folder, PARAMS_CSV, ROWS_CSV, ps, rs))
    say("  manifest PASS  {}  ({} files)".format(folder, len(files)))
    return os.path.join(folder, ps[0]), os.path.join(folder, rs[0])


def read_params(path):
    out = {}
    with open(path, newline="") as fh:
        for rec in csv.reader(fh):
            if len(rec) != 2:
                raise Stop("P0(c) {}: a params line has {} fields, not 2: {!r}".format(path, len(rec), rec))
            if rec[0] in out:
                raise Stop("P0(c) {}: key {} twice".format(path, rec[0]))
            out[rec[0]] = rec[1]
    return out


def read_rows(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        header = list(rd.fieldnames or [])
        rows = list(rd)
    for need in ("tid", "end") + JSON_FIELDS + FLOAT_FIELDS:
        if need not in header:
            raise Stop("P0(d) {}: column {} missing".format(path, need))
    by = {}
    for i, r in enumerate(rows):
        if r["end"] != "ok":
            raise Stop("P0(d) {}: row {} (tid {}) ends {!r}, not ok".format(path, i + 1, r["tid"], r["end"]))
        if r["tid"] in by:
            raise Stop("P0(d) {}: tid {} twice".format(path, r["tid"]))
        by[r["tid"]] = r
    return header, by


def ulp_and_rel(a_s, b_s):
    """(ulp distance, relative difference); (-1, nan) when either is not a float string."""
    try:
        a, b = float(a_s), float(b_s)
    except ValueError:
        return -1, float("nan")
    ia = np.array([a]).view(np.int64)[0]
    ib = np.array([b]).view(np.int64)[0]
    ia = ia if ia >= 0 else np.int64(-(1 << 63)) - ia
    ib = ib if ib >= 0 else np.int64(-(1 << 63)) - ib
    ulp = abs(int(ia) - int(ib))
    den = max(abs(a), abs(b))
    rel = abs(a - b) / den if den > 0 else 0.0
    return ulp, rel


def compare_one(job):
    """One tid: return (tid, list of differing fields, list of (field, key, ulp, rel))."""
    tid, ra, rb, cols = job
    diffs, mags = [], []
    for c in cols:
        if ra[c] == rb[c]:
            continue
        diffs.append(c)
        if c in JSON_FIELDS:
            ja, jb = json.loads(ra[c]), json.loads(rb[c])
            if sorted(ja) != sorted(jb):
                mags.append((c, "keys differ", -1, float("nan")))
                continue
            for k in sorted(ja, key=lambda x: (len(x), x)):
                if ja[k] != jb[k]:
                    u, r = ulp_and_rel(ja[k], jb[k])
                    mags.append((c, k, u, r))
        elif c in FLOAT_FIELDS:
            u, r = ulp_and_rel(ra[c], rb[c])
            mags.append((c, "", u, r))
    return tid, diffs, mags


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ref", required=True, help="committed run folder (earlier image)")
    p.add_argument("--new", required=True, help="re-run folder of the same shard (later image)")
    p.add_argument("--workers", type=int, default=2)
    a = p.parse_args()

    say("=" * 100)
    say("CBO-GAP c5bitcmp  (ledger N45, C5 IMAGE SPLIT)  analysis only, writes nothing")
    say("=" * 100)
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    say("  script   sha256 {}".format(sha256_of(os.path.abspath(__file__))))
    say("  ref      {}".format(a.ref))
    say("  new      {}".format(a.new))
    say("  rule     B: every column except {} equal as strings, every tid; seeds: none drawn here".format(
        ", ".join(NOT_COMPARED)))
    say()
    try:
        say("P0  preconditions")
        pa, ra = verify_folder(a.ref)
        pb, rb = verify_folder(a.new)
        A, B = read_params(pa), read_params(pb)
        if sorted(A) != sorted(B):
            raise Stop("P0(c) params keys differ: {} vs {}".format(sorted(A), sorted(B)))
        for k in sorted(A):
            if k in MAY_DIFFER:
                continue
            if A[k] != B[k]:
                raise Stop("P0(c) params {}: {!r} (ref) vs {!r} (new)".format(k, A[k], B[k]))
        if A.get("mode") != "run":
            raise Stop("P0(c) mode {!r}, expected run".format(A.get("mode")))
        if B.get("resume_from", "") != "":
            raise Stop("P0(c) new resume_from {!r}: the re-run must compute every task".format(B["resume_from"]))
        say("  params PASS  equal on every key but python: ref python {}  new python {}  numpy {}".format(
            A.get("python"), B.get("python"), A.get("numpy")))
        if A.get("python") == B.get("python"):
            say("  NOTE  both runs used python {}: this compares two sessions, not two Pythons".format(
                A.get("python")))
        ha, A_rows = read_rows(ra)
        hb, B_rows = read_rows(rb)
        if ha != hb:
            raise Stop("P0(d) headers differ: {} vs {}".format(ha, hb))
        if sorted(A_rows) != sorted(B_rows):
            raise Stop("P0(d) tid sets differ: {} only in ref, {} only in new".format(
                len(set(A_rows) - set(B_rows)), len(set(B_rows) - set(A_rows))))
        say("  rows PASS  {} tids in each, all end ok, no repeats, same set".format(len(A_rows)))
    except Stop as e:
        say("STOP  " + str(e))
        say("VERDICT  none (exit 2)")
        return 2

    cols = [c for c in ha if c not in NOT_COMPARED]
    say("  compared columns ({}): {}".format(len(cols), ", ".join(cols)))
    say()
    jobs = [(t, A_rows[t], B_rows[t], cols) for t in sorted(A_rows)]
    with multiprocessing.Pool(a.workers) as pool:
        res = pool.map(compare_one, jobs)

    say("B  per tid")
    nbad, worst_u, worst_r, field_count = 0, None, None, {}
    for tid, diffs, mags in res:
        r = A_rows[tid]
        lab = "{} d {} {} {} tau0 {} rep {}".format(r.get("row"), r.get("d"), r.get("objective"),
                                                   r.get("law"), r.get("tau0"), r.get("rep"))
        if not diffs:
            say("  SAME  {}  {}".format(lab, tid))
            continue
        nbad += 1
        say("  DIFF  {}  {}  fields: {}".format(lab, tid, ", ".join(diffs)))
        for c in diffs:
            field_count[c] = field_count.get(c, 0) + 1
        for c, k, u, rel in mags:
            say("        M  {} {}  ulp {}  rel {!r}".format(c, k, u, rel))
            if u >= 0 and (worst_u is None or u > worst_u[0]):
                worst_u = (u, tid, c, k)
            if u >= 0 and (worst_r is None or rel > worst_r[0]):
                worst_r = (rel, tid, c, k)
    say()
    say("SUMMARY  {} tids compared, {} identical, {} differing".format(len(res), len(res) - nbad, nbad))
    if nbad:
        for c in sorted(field_count):
            say("  field {}: differs in {} rows".format(c, field_count[c]))
        if worst_u is not None:
            say("  M  largest ulp {} at {} {} {}".format(*worst_u))
            say("  M  largest rel {!r} at {} {} {}".format(*worst_r))
        say("VERDICT  DIFFERENT  (exit 1)")
        return 1
    say("VERDICT  IDENTICAL  (exit 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
