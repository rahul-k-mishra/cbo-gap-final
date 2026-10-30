"""
refratio.py  --  CBO-GAP: how far does a probe beta miss its target on the
reference ensemble?  (ledger N40, C1; N45 nominal tau_0)

WHAT THIS IS
------------
Round 1 calibrated beta on a probe: mechanism.beta_for_target bisects beta
until a probe sample of 4000 particles, drawn with a fixed seed, has ESS
fraction tau_0, and that beta is then used unchanged for the reference
ensemble. law.py's GEOM probe works the same way on its own sample. Neither
protocol checks the concentration the reference ensemble actually reaches.

The rerun already measured it. For every realization of CONC, PROBEARM,
TAU8 and GEOM, rerun.py's finite-J audit (F1, section 8.5) redrew the
initial ensemble from the realization's seed and wrote

    audit_ref_ratio = ESS_0(J_inf) / J_inf / tau_0

for the full reference ensemble under the row's own beta (rerunlib.audit_one).
A ratio of 1 means the reference reached its target. This script reads those
values from the committed shard folders and reports, per cell, how far they
lie from 1. It runs no trajectory and no simulation.

Rows read:
  PROBEARM  mechanism probe beta (the probe protocol of round 1's Section 7.3)
  GEOM      law probe beta
  CONC      calprec2 fixed beta, printed alongside as the calibrated row

Each row is measured against 1 on its own. No CONC-minus-PROBEARM contrast is
computed: that comparison was dropped (N40, C1), and printing the two side by
side is description, not a contrast.

WRITES NOTHING. Every file is opened for reading only.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-30)
  R1  INPUT. Only the folders given with --runs are read, each after its
      sha256.txt verifies (every file it lists). In each, every
      rerun_real.csv listed in sha256.txt is read; a row is used iff its
      "rows" field is exactly PROBEARM, GEOM or CONC. Such a row must have
      end "ok", error empty, F1 "ok" and a finite audit_ref_ratio; anything
      else is exit 2. A (cell, rep) found twice is exit 2.
      Cell = (row, module, objective, d, law, tau0, r, J_inf, arm, subarm,
      diffusion, beta).
  R2  REPRODUCTION GATE. The --analysis folder (default the twenty-one-row
      analysis) is verified against its sha256.txt. For every cell, the
      mean of audit_ref_ratio over its realizations, in rep order, must
      equal analysis_audit.csv's ref_ratio_mean for (row, objective, d,
      law, tau0) within 1e-12 x max(1, |x|), with the same n; the two cell
      sets must be equal. Any failure is exit 3, before any statistic is
      printed. Example: analysis 1.0019991516954845, here
      1.0019991516954845: pass. 1.00199915169 against that: fail.
  R3  PER CELL. n, mean, SD (ddof 1), min, max, and a two-sided 95%
      percentile bootstrap interval of the mean over the cell's
      realizations, B = 10000, indices
      default_rng(SeedSequence([20261030, row code, cell index]))
      .integers(0, n, (B, n)); row codes PROBEARM 1, GEOM 2, CONC 3; cell
      index = position of the cell in the sorted cell list of its row
      (injective within a row).
  R4  VERDICT PER CELL (DIFFERENCE rule against 1, two-sided 95%):
      "above 1" iff lo > 1 (the reference is less concentrated than the
      target: its ESS fraction is above tau_0); "below 1" iff hi < 1;
      otherwise "contains 1". Example: 15 ratios with mean 1.31 and
      interval [1.22, 1.40]: above 1. Mean 0.99, [0.97, 1.01]: contains 1.
      "Contains 1" is not "reached the target" (no equivalence claim).
  R5  SUMMARY, description only, no verdict: per row and (tau0, d), and per
      row and tau0: the number of cells, counts of the three verdicts, and
      the median, minimum and maximum of the cell means.

EXIT CODES
  0  ran to the end; every table printed.
  2  bad argument; a folder or manifest problem; an unexpected or
     incomplete input row; a duplicate (cell, rep).
  3  the reproduction gate R2 failed.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python scripts/refratio.py --workers 2 --runs <folder> --runs <folder> ...
"""

import argparse
import csv
import hashlib
import io
import math
import multiprocessing
import os
import platform
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ROWS = ("PROBEARM", "GEOM", "CONC")
ROW_CODE = {"PROBEARM": 1, "GEOM": 2, "CONC": 3}
ROW_BETA = {"PROBEARM": "mechanism probe", "GEOM": "law probe", "CONC": "calprec2 fixed beta"}
CELL_COLS = ("rows", "module", "objective", "d", "law", "tau0", "r", "J_inf", "arm", "subarm",
             "diffusion", "beta")
NEED = CELL_COLS + ("rep", "audit_ref_ratio", "F1", "error", "end")
B = 10000
SEED0 = 20261030
GATE_TOL = 1e-12
DEFAULT_ANALYSIS = os.path.join(REPO, "runs", "rerun-analysis-20261030-144722")


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
    """Verify folder/sha256.txt; return the relative paths it lists."""
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


def read_folder(folder):
    """R1. Returns (folder, files verified, {row: count}, records) or a Stop."""
    try:
        names = manifest(folder)
        csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
        recs = []
        cnt = dict((r, 0) for r in ROWS)
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
                    if x["rows"] not in ROWS:
                        continue
                    where = "{} rep {} {}".format(x["rows"], x["rep"], path)
                    if x["end"] != "ok" or x["error"] != "":
                        raise Stop(2, "incomplete row: {}".format(where))
                    if x["F1"] != "ok":
                        raise Stop(2, "F1 not ok ({!r}): {}".format(x["F1"], where))
                    try:
                        v = float(x["audit_ref_ratio"])
                        rep = int(x["rep"])
                    except ValueError:
                        raise Stop(2, "non-numeric audit_ref_ratio or rep: {}".format(where))
                    if not math.isfinite(v):
                        raise Stop(2, "non-finite audit_ref_ratio: {}".format(where))
                    recs.append((tuple(x[c] for c in CELL_COLS), rep, v, path))
                    cnt[x["rows"]] += 1
        return folder, len(names), cnt, recs
    except Stop as e:
        return folder, 0, None, e


def boot_cell(args):
    """R3 and R4 for one cell."""
    row, idx, vals = args
    v = np.array(vals, dtype=float)
    n = v.size
    ss = np.random.SeedSequence([SEED0, ROW_CODE[row], idx])
    ix = np.random.default_rng(ss).integers(0, n, (B, n))
    bm = v[ix].mean(axis=1)
    lo, hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
    verdict = "above 1" if lo > 1.0 else ("below 1" if hi < 1.0 else "contains 1")
    return {"n": n, "mean": float(v.mean()), "sd": float(np.std(v, ddof=1)) if n > 1 else float("nan"),
            "min": float(v.min()), "max": float(v.max()), "lo": lo, "hi": hi, "verdict": verdict}


def load_gate(folder):
    manifest(folder)
    path = os.path.join(folder, "analysis_audit.csv")
    if not os.path.isfile(path):
        raise Stop(2, "{}: no analysis_audit.csv".format(folder))
    out = {}
    with io.open(path, "r", newline="", encoding="utf-8") as f:
        for x in csv.DictReader(f):
            if x["row"] not in ROWS:
                continue
            k = (x["row"], x["objective"], x["d"], x["law"], x["tau0"])
            val = (float(x["ref_ratio_mean"]), int(x["n"]))
            if k in out and out[k] != val:
                raise Stop(2, "analysis_audit.csv: two different ref_ratio_mean for {}".format(k))
            out[k] = val
    return out


def fmt(x):
    return "{:.4f}".format(x)


def main():
    ap = argparse.ArgumentParser(description="probe-beta reference ratios (N40)")
    ap.add_argument("--runs", action="append", default=[], help="run folder; repeat")
    ap.add_argument("--analysis", default=DEFAULT_ANALYSIS)
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    a = ap.parse_args()
    if a.workers < 1:
        raise Stop(2, "--workers must be at least 1")
    if not a.runs:
        raise Stop(2, "give at least one --runs folder")
    runs = [os.path.abspath(r) for r in a.runs]
    if len(set(runs)) != len(runs):
        raise Stop(2, "a --runs folder is given twice")
    for r in runs + [os.path.abspath(a.analysis)]:
        if not os.path.isdir(r):
            raise Stop(2, "not a folder: {}".format(r))

    hdr("refratio.py  (ledger N40, C1; N45)  --  writes nothing")
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  workers         {}".format(a.workers))
    say("  rows            {}".format(", ".join("{} ({})".format(r, ROW_BETA[r]) for r in ROWS)))
    say("  bootstrap       B {}, two-sided 95% percentile of the mean over realizations".format(B))
    say("  seed rule       default_rng(SeedSequence([{}, row code, cell index])); row codes {}".format(
        SEED0, ", ".join("{} {}".format(r, ROW_CODE[r]) for r in ROWS)))
    say("  gate            analysis_audit.csv ref_ratio_mean, tolerance {} x max(1,|x|)".format(GATE_TOL))
    say("  analysis        {}".format(os.path.abspath(a.analysis)))
    for r in runs:
        say("  run             {}".format(r))

    hdr("What this measures, in plain words")
    for s in (
        "A probe beta is chosen so that a 4000-particle probe sample has the target",
        "concentration tau_0. It is then used on a much larger reference ensemble without",
        "checking that ensemble. The rerun did check it: for every realization it recorded",
        "the reference ensemble's ESS fraction divided by tau_0. A value of 1 means the",
        "target was reached; above 1 means the reference is less concentrated than intended;",
        "below 1, more concentrated.",
        "",
        "Below, each cell's realizations give a mean ratio with a 95% interval. A cell is",
        "'above 1' or 'below 1' only if its whole interval is on that side. 'contains 1' means",
        "the miss is not resolved in that cell; it does not mean the target was reached.",
        "PROBEARM and GEOM use probe betas. CONC uses the calibrated fixed beta and is printed",
        "alongside for reference only; no difference between rows is computed.",
    ):
        say("  " + s)

    pool = multiprocessing.Pool(processes=a.workers)
    try:
        hdr("Input  (R1)")
        res = pool.map(read_folder, runs, chunksize=1)
        for folder, nfiles, cnt, recs in res:
            if isinstance(recs, Stop):
                raise recs
        cells = {}
        for folder, nfiles, cnt, recs in res:
            say("  {}  {} files verified; rows read: {}".format(
                os.path.basename(folder), nfiles, ", ".join("{} {}".format(r, cnt[r]) for r in ROWS)))
            for key, rep, v, path in recs:
                d = cells.setdefault(key, {})
                if rep in d:
                    raise Stop(2, "duplicate (cell, rep): {} rep {} (second in {})".format(key, rep, path))
                d[rep] = v
        if not cells:
            raise Stop(2, "no PROBEARM, GEOM or CONC rows in the folders given")

        absent = [r for r in ROWS if not any(k[0] == r for k in cells)]
        if absent:
            raise Stop(2, "no cells for row(s) {} in the folders given".format(", ".join(absent)))

        hdr("Reproduction gate  (R2)")
        gate = load_gate(os.path.abspath(a.analysis))
        seen = set()
        for key, d in cells.items():
            row = key[0]
            gk = (row, key[2], key[3], key[4], key[5])
            if gk in seen:
                raise Stop(2, "two cells share (row, objective, d, law, tau0): {}".format(gk))
            seen.add(gk)
            if gk not in gate:
                raise Stop(3, "R2: cell not in analysis_audit.csv: {}".format(gk))
            reps = sorted(d)
            if reps != list(range(len(reps))):
                raise Stop(2, "cell {}: reps {} are not 0..n-1".format(gk, reps[:5]))
            m = float(np.array([d[r] for r in reps]).mean())
            want, n = gate[gk]
            if n != len(reps) or abs(m - want) > GATE_TOL * max(1.0, abs(want)):
                raise Stop(3, "R2: {}: here mean {!r} n {}, analysis {!r} n {}".format(gk, m, len(reps), want, n))
        missing = [k for k in gate if k not in seen and k[0] in set(k2[0] for k2 in cells)]
        if missing:
            raise Stop(3, "R2: {} cell(s) of analysis_audit.csv not found in the runs, e.g. {}".format(
                len(missing), missing[0]))
        for r in ROWS:
            n_here = sum(1 for k in cells if k[0] == r)
            n_gate = sum(1 for k in gate if k[0] == r)
            say("  {:<9} cells here {:>4}  in analysis_audit.csv {:>4}  every mean equal: PASS".format(r, n_here, n_gate))

        jobs, keys = [], []
        for r in ROWS:
            ks = sorted(k for k in cells if k[0] == r)
            for i, k in enumerate(ks):
                jobs.append((r, i, [cells[k][j] for j in sorted(cells[k])]))
                keys.append(k)
        stats = dict(zip(keys, pool.map(boot_cell, jobs, chunksize=16)))
    finally:
        pool.close()
        pool.join()

    for r in ROWS:
        ks = sorted(k for k in stats if k[0] == r)
        hdr("{}  ({})  per cell  (R3, R4)".format(r, ROW_BETA[r]))
        say("  {:<14} {:>3} {:<8} {:>5} {:>3} {:>8} {:>8} {:>18} {:>8} {:>8}  {}".format(
            "objective", "d", "law", "tau0", "n", "mean", "sd", "95% interval", "min", "max", "verdict"))
        for k in ks:
            s = stats[k]
            say("  {:<14} {:>3} {:<8} {:>5} {:>3} {:>8} {:>8} {:>18} {:>8} {:>8}  {}".format(
                k[2][:14], k[3], k[4][:8], k[5], s["n"], fmt(s["mean"]), fmt(s["sd"]),
                "[{}, {}]".format(fmt(s["lo"]), fmt(s["hi"])), fmt(s["min"]), fmt(s["max"]), s["verdict"]))

    hdr("SUMMARY  (R5; description only)")
    for r in ROWS:
        ks = [k for k in stats if k[0] == r]
        taus = sorted({k[5] for k in ks}, key=float)
        dims = sorted({k[3] for k in ks}, key=int)
        say("\n  {}  ({})".format(r, ROW_BETA[r]))
        say("    {:>6} {:>4} {:>6} {:>8} {:>8} {:>11}   {:>8} {:>8} {:>8}".format(
            "tau0", "d", "cells", "above 1", "below 1", "contains 1", "median", "min", "max"))
        for t in taus:
            for d in dims + ["all"]:
                sel = [stats[k] for k in ks if k[5] == t and (d == "all" or k[3] == d)]
                if not sel:
                    continue
                ms = np.array([s["mean"] for s in sel])
                say("    {:>6} {:>4} {:>6} {:>8} {:>8} {:>11}   {:>8} {:>8} {:>8}".format(
                    t, d, len(sel), sum(1 for s in sel if s["verdict"] == "above 1"),
                    sum(1 for s in sel if s["verdict"] == "below 1"),
                    sum(1 for s in sel if s["verdict"] == "contains 1"),
                    fmt(float(np.median(ms))), fmt(float(ms.min())), fmt(float(ms.max()))))
        tot = [stats[k] for k in ks]
        say("    all cells: {}; above 1 {}, below 1 {}, contains 1 {}".format(
            len(tot), sum(1 for s in tot if s["verdict"] == "above 1"),
            sum(1 for s in tot if s["verdict"] == "below 1"),
            sum(1 for s in tot if s["verdict"] == "contains 1")))
    hdr("refratio.py done, exit 0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
