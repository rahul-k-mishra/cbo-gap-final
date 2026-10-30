"""
adapt0.py  --  CBO-GAP: where does ADAPT's fixed arm start, and how far does
each arm's concentration move during the run?  (ledger N40, N45; ADAPT)

WHAT THIS IS
------------
ADAPT is control.py run twice per cell. The fixed arm uses beta0, bisected on
a 4000-particle probe (control.py lines 333 to 336, default_rng(999 + 131 d))
so that the PROBE's ESS fraction is tau_0, and holds it for the whole run.
The adaptive arm starts from the same beta0 but re-solves beta on the
reference ensemble before every step, the first included (control.py lines
230 to 231, goal log(tau_0 J_inf)).

control.one_realisation returns, for the run's own reference ensemble, le0
(the log ESS at the first step, under the beta used there), le_min and
le_max (over all steps). rerun.py stores them in the extras column of every
ADAPT row. So, without any redraw or audit:

    ratio0 = exp(le0) / (tau_0 J_inf)

is the reference's starting ESS fraction over its target. A value of 1 means
the run started on target. For the adaptive arm it is 1 by construction,
which makes that arm a positive control of the reading.

    drift = max(le0 - le_min, le_max - le0)

is control.py's own drift (line 377), in log units.

The fixed-against-adaptive comparison is dropped (Rahul, 2026-10-30): the
arms are not seed-paired in the rerun, no contrast was pre-registered, and
they differ at t = 0 by construction. This script compares neither arm with
the other. It describes each.

WRITES NOTHING. Every file is opened for reading only.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-30)
  R1  INPUT. Only the --runs folders, each after its sha256.txt verifies;
      every rerun_real.csv it lists; a row is used iff "rows" is exactly
      ADAPT. It must have end "ok", error empty, arm "fixed" or
      "adaptive", and extras holding finite le0, le_min, le_max and
      b_first; anything else is exit 2. A (cell, arm, rep) twice is exit 2.
      Every cell must have both arms with reps 0..n-1 and equal n.
      Cell = (objective, d, law, tau0, J_inf).
  R2  POSITIVE CONTROL, a gate. Every adaptive realization must have
      |ratio0 - 1| <= 1e-6. The bisection of solve_beta_warm (40 halvings
      of a bracket at most 1e24 wide in beta, geometric) leaves an error in
      log beta below 1e-10, far inside 1e-6. Failure is exit 3, before any
      fixed-arm statistic. Example: le0 = log(0.01 x 50000) = 6.2146080984
      gives ratio0 1.0000000; le0 6.2147 gives 1.0000919: fail.
  R3  CONSISTENCY, a gate. In the fixed arm, extras b_first must equal the
      row's beta column exactly (both are beta0; the fixed arm never
      re-solves). Failure is exit 3. Example: beta "1.5344403049780453" and
      b_first 1.5344403049780453: pass.
  R4  FIXED ARM PER CELL: n; mean and median of ratio0; two-sided 95%
      percentile bootstrap intervals of each from the same resamples, B =
      10000, indices default_rng(SeedSequence([20261030, 5, cell index]))
      .integers(0, n, (B, n)), cell index = position in the sorted cell
      list; verdicts on each interval, DIFFERENCE rule against 1 ("above
      1" iff lo > 1, "below 1" iff hi < 1, else "contains 1", which is not
      "on target"); "median within 5%" iff |median - 1| <= 0.05, a point
      value and not a test; SD (ddof 1), min, max.
      Example: 15 ratios, median 0.71 [0.64, 0.80]: median below 1, not
      within 5%.
  R5  DRIFT PER CELL AND ARM, description only: median, min and max over
      realizations of drift. No verdict, no comparison between arms.
  R6  SUMMARY, description only: per tau0 and d, and per tau0: fixed-arm
      cells; mean and median verdict counts; cells with median within 5%;
      median, min, max of the cell medians of ratio0; median of the cell
      median drifts in each arm.

EXIT CODES
  0  ran to the end; every table printed.
  2  bad argument; folder or manifest problem; an unexpected, incomplete
     or unpaired input row; a duplicate.
  3  a gate failed (R2 positive control, R3 consistency).

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python scripts/adapt0.py --workers 2 --runs <folder> --runs <folder> ...
"""

import argparse
import csv
import hashlib
import io
import json
import math
import multiprocessing
import os
import platform
import sys

import numpy as np

B = 10000
SEED0 = 20261030
ROW_CODE = 5
PC_TOL = 1e-6
ARMS = ("fixed", "adaptive")
NEED = ("rows", "objective", "d", "law", "tau0", "J_inf", "arm", "rep", "beta", "extras", "error", "end")


class Stop(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, code, msg)
        self.code = code
        self.msg = msg


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "=" * 96)
    say(s)
    say("=" * 96)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifest(folder):
    mp = os.path.join(folder, "sha256.txt")
    if not os.path.isfile(mp):
        raise Stop(2, "{}: no sha256.txt".format(folder))
    names = []
    with io.open(mp, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split(None, 1)
            if len(parts) != 2:
                raise Stop(2, "{}: sha256.txt line not 'hash  name': {!r}".format(folder, ln))
            h, n = parts[0].lower(), parts[1].lstrip("*")
            p = os.path.join(folder, n)
            if not os.path.isfile(p):
                raise Stop(2, "{}: listed file missing: {}".format(folder, n))
            if sha256_of(p) != h:
                raise Stop(2, "{}: {} differs from sha256.txt".format(folder, n))
            names.append(n)
    return names


def fnum(v, what, where):
    try:
        x = float(v)
    except (TypeError, ValueError):
        raise Stop(2, "non-numeric {}: {}".format(what, where))
    if not math.isfinite(x):
        raise Stop(2, "non-finite {}: {}".format(what, where))
    return x


def read_folder(folder):
    """R1. Returns (folder, files verified, rows used, records) or a Stop."""
    try:
        names = manifest(folder)
        csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
        recs = []
        for n in names:
            if os.path.basename(n) != "rerun_real.csv":
                continue
            path = os.path.join(folder, n)
            with io.open(path, "r", newline="", encoding="utf-8") as f:
                rd = csv.DictReader(f)
                miss = [c for c in NEED if c not in (rd.fieldnames or [])]
                if miss:
                    raise Stop(2, "{}: missing column(s) {}".format(path, ", ".join(miss)))
                for x in rd:
                    if x["rows"] != "ADAPT":
                        continue
                    where = "ADAPT {} {} d {} tau {} rep {} in {}".format(
                        x["arm"], x["objective"], x["d"], x["tau0"], x["rep"], path)
                    if x["end"] != "ok" or x["error"] != "":
                        raise Stop(2, "incomplete row: {}".format(where))
                    if x["arm"] not in ARMS:
                        raise Stop(2, "unknown arm: {}".format(where))
                    try:
                        ex = json.loads(x["extras"])
                    except ValueError:
                        raise Stop(2, "extras not JSON: {}".format(where))
                    vals = dict((k, fnum(ex.get(k), "extras " + k, where))
                                for k in ("le0", "le_min", "le_max", "b_first"))
                    try:
                        rep = int(x["rep"])
                    except ValueError:
                        raise Stop(2, "non-integer rep: {}".format(where))
                    tau = fnum(x["tau0"], "tau0", where)
                    jinf = fnum(x["J_inf"], "J_inf", where)
                    cell = (x["objective"], x["d"], x["law"], x["tau0"], x["J_inf"])
                    recs.append({"cell": cell, "arm": x["arm"], "rep": rep, "tau": tau, "jinf": jinf,
                                 "beta": x["beta"], "where": where,
                                 "ratio0": math.exp(vals["le0"]) / (tau * jinf),
                                 "drift": max(vals["le0"] - vals["le_min"], vals["le_max"] - vals["le0"]),
                                 "b_first": vals["b_first"]})
        return folder, len(names), len(recs), recs
    except Stop as e:
        return folder, 0, 0, e


def side(lo, hi):
    return "above 1" if lo > 1.0 else ("below 1" if hi < 1.0 else "contains 1")


def boot_cell(args):
    idx, vals = args
    v = np.array(vals, dtype=float)
    n = v.size
    ix = np.random.default_rng(np.random.SeedSequence([SEED0, ROW_CODE, idx])).integers(0, n, (B, n))
    rs = v[ix]
    bm, bmed = rs.mean(axis=1), np.median(rs, axis=1)
    lo, hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
    mlo, mhi = float(np.percentile(bmed, 2.5)), float(np.percentile(bmed, 97.5))
    med = float(np.median(v))
    return {"n": n, "mean": float(v.mean()), "median": med, "lo": lo, "hi": hi, "verdict": side(lo, hi),
            "mlo": mlo, "mhi": mhi, "mverdict": side(mlo, mhi), "c6": abs(med - 1.0) <= 0.05,
            "sd": float(np.std(v, ddof=1)) if n > 1 else float("nan"), "min": float(v.min()), "max": float(v.max())}


def fmt(x):
    return "{:.4f}".format(x)


def abc(sel, key):
    return "{}/{}/{}".format(sum(1 for x in sel if x[key] == "above 1"),
                             sum(1 for x in sel if x[key] == "below 1"),
                             sum(1 for x in sel if x[key] == "contains 1"))


def main():
    ap = argparse.ArgumentParser(description="ADAPT starting concentration and drift (N40)")
    ap.add_argument("--runs", action="append", default=[], help="run folder; repeat")
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    a = ap.parse_args()
    if a.workers < 1:
        raise Stop(2, "--workers must be at least 1")
    if not a.runs:
        raise Stop(2, "give at least one --runs folder")
    runs = [os.path.abspath(r) for r in a.runs]
    if len(set(runs)) != len(runs):
        raise Stop(2, "a --runs folder is given twice")
    for r in runs:
        if not os.path.isdir(r):
            raise Stop(2, "not a folder: {}".format(r))

    hdr("adapt0.py  (ledger N40, N45; ADAPT)  --  writes nothing")
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  workers         {}".format(a.workers))
    say("  ratio0          exp(le0) / (tau0 J_inf), the run's own reference at its first step")
    say("  drift           max(le0 - le_min, le_max - le0), control.py line 377")
    say("  gates           adaptive |ratio0 - 1| <= {:g} (R2); fixed b_first == beta (R3)".format(PC_TOL))
    say("  bootstrap       B {}, 95% percentile of mean and median; seed SeedSequence([{}, {}, cell index])".format(
        B, SEED0, ROW_CODE))
    for r in runs:
        say("  run             {}".format(r))

    hdr("What this measures, in plain words")
    for t in (
        "ADAPT's fixed arm takes its beta from a 4000-particle probe and keeps it. Whether its",
        "own 50000-particle reference started at the target concentration was never checked.",
        "The run recorded it: the log effective sample size of the reference at the first step.",
        "Divided by the target, 1 means the run started on target, above 1 less concentrated",
        "than intended, below 1 more. The adaptive arm re-solves beta on the reference before",
        "its first step, so it must read exactly 1; if it does not, the reading is wrong and the",
        "script stops.",
        "",
        "Drift is how far the reference's concentration moved during the run, in log units, as",
        "control.py defined it. It is printed for each arm. The two arms are not compared: they",
        "are not seed-paired, no comparison was pre-registered, and they start differently.",
    ):
        say("  " + t)

    pool = multiprocessing.Pool(processes=a.workers)
    try:
        hdr("Input  (R1)")
        res = pool.map(read_folder, runs, chunksize=1)
        for folder, nf, nr, recs in res:
            if isinstance(recs, Stop):
                raise recs
        data = {}
        for folder, nf, nr, recs in res:
            say("  {}  {} files verified; ADAPT rows read: {}".format(os.path.basename(folder), nf, nr))
            for r in recs:
                d = data.setdefault(r["cell"], {"fixed": {}, "adaptive": {}})
                if r["rep"] in d[r["arm"]]:
                    raise Stop(2, "duplicate (cell, arm, rep): {}".format(r["where"]))
                d[r["arm"]][r["rep"]] = r
        if not data:
            raise Stop(2, "no ADAPT rows in the folders given")
        for cell, d in data.items():
            nf_, na_ = sorted(d["fixed"]), sorted(d["adaptive"])
            if not nf_ or nf_ != na_ or nf_ != list(range(len(nf_))):
                raise Stop(2, "cell {}: fixed reps {} and adaptive reps {} are not both 0..n-1".format(
                    cell, nf_[:5], na_[:5]))
        say("  cells {}; realizations per arm {}".format(
            len(data), sum(len(d["fixed"]) for d in data.values())))

        hdr("Gates  (R2 positive control, R3 consistency)")
        worst = 0.0
        for cell, d in data.items():
            for rep, r in d["adaptive"].items():
                dev = abs(r["ratio0"] - 1.0)
                worst = max(worst, dev)
                if dev > PC_TOL:
                    raise Stop(3, "R2: adaptive ratio0 {!r}: {}".format(r["ratio0"], r["where"]))
            for rep, r in d["fixed"].items():
                if float(r["beta"]) != r["b_first"]:
                    raise Stop(3, "R3: fixed b_first {!r} != beta {}: {}".format(r["b_first"], r["beta"], r["where"]))
        say("  R2 PASS: every adaptive realization within {:g} of 1 (largest |ratio0 - 1| {:.3e})".format(PC_TOL, worst))
        say("  R3 PASS: every fixed realization has b_first equal to its beta")

        cells = sorted(data, key=lambda c: (c[0], int(c[1]), c[2], float(c[3]), c[4]))
        jobs = [(i, [data[c]["fixed"][k]["ratio0"] for k in sorted(data[c]["fixed"])]) for i, c in enumerate(cells)]
        stats = dict(zip(cells, pool.map(boot_cell, jobs, chunksize=8)))
    finally:
        pool.close()
        pool.join()

    drift = {}
    for c in cells:
        for arm in ARMS:
            v = np.array([data[c][arm][k]["drift"] for k in sorted(data[c][arm])])
            drift[(c, arm)] = (float(np.median(v)), float(v.min()), float(v.max()))

    hdr("Fixed arm, starting ratio0 per cell  (R4)")
    say("  {:<11} {:>3} {:>5} {:>3} {:>7} {:>17} {:<10} {:>7} {:>17} {:<10} {:>4} {:>7} {:>7} {:>7}".format(
        "objective", "d", "tau0", "n", "mean", "95% interval", "mean", "median", "95% interval", "median",
        "5%", "sd", "min", "max"))
    for c in cells:
        s = stats[c]
        say("  {:<11} {:>3} {:>5} {:>3} {:>7} {:>17} {:<10} {:>7} {:>17} {:<10} {:>4} {:>7} {:>7} {:>7}".format(
            c[0][:11], c[1], c[3], s["n"], fmt(s["mean"]), "[{}, {}]".format(fmt(s["lo"]), fmt(s["hi"])),
            s["verdict"], fmt(s["median"]), "[{}, {}]".format(fmt(s["mlo"]), fmt(s["mhi"])), s["mverdict"],
            "yes" if s["c6"] else "no", fmt(s["sd"]), fmt(s["min"]), fmt(s["max"])))

    hdr("Drift per cell and arm, log units  (R5; description, no comparison)")
    say("  {:<11} {:>3} {:>5}   {:>26}   {:>26}".format("objective", "d", "tau0", "fixed: median [min, max]",
                                                       "adaptive: median [min, max]"))
    for c in cells:
        f_, a_ = drift[(c, "fixed")], drift[(c, "adaptive")]
        say("  {:<11} {:>3} {:>5}   {:>26}   {:>26}".format(
            c[0][:11], c[1], c[3], "{} [{}, {}]".format(fmt(f_[0]), fmt(f_[1]), fmt(f_[2])),
            "{} [{}, {}]".format(fmt(a_[0]), fmt(a_[1]), fmt(a_[2]))))

    hdr("SUMMARY  (R6; description only)")
    say("  a/b/c = above 1 / below 1 / contains 1; 5% = cells whose median ratio0 is within 5% of 1;")
    say("  median, min, max are of the fixed arm's cell medians; drift columns are medians of cell medians")
    say("    {:>6} {:>4} {:>6} {:>12} {:>13} {:>4}   {:>8} {:>8} {:>8}   {:>11} {:>14}".format(
        "tau0", "d", "cells", "mean a/b/c", "median a/b/c", "5%", "median", "min", "max", "drift fixed",
        "drift adaptive"))
    taus = sorted({c[3] for c in cells}, key=float)
    dims = sorted({c[1] for c in cells}, key=int)
    for t in taus:
        for dd in dims + ["all"]:
            sel = [c for c in cells if c[3] == t and (dd == "all" or c[1] == dd)]
            if not sel:
                continue
            st = [stats[c] for c in sel]
            say("    {:>6} {:>4} {:>6} {:>12} {:>13} {:>4}   {:>8} {:>8} {:>8}   {:>11} {:>14}".format(
                t, dd, len(sel), abc(st, "verdict"), abc(st, "mverdict"), sum(1 for x in st if x["c6"]),
                fmt(float(np.median([x["median"] for x in st]))), fmt(min(x["median"] for x in st)),
                fmt(max(x["median"] for x in st)),
                fmt(float(np.median([drift[(c, "fixed")][0] for c in sel]))),
                fmt(float(np.median([drift[(c, "adaptive")][0] for c in sel])))))
    hdr("adapt0.py done, exit 0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
