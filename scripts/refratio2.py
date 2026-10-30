"""
refratio2.py  --  CBO-GAP: probe and calibrated betas against their target on
the reference ensemble, with per-cell MEDIANS, and TAU8 added
(ledger N40; second script; refratio.py and its log stay as they are)

WHAT THIS IS
------------
refratio.py (v1, logs/refratio-20261030.log) tested the MEAN of

    audit_ref_ratio = ESS_0(J_inf) / J_inf / tau_0

over each cell's realizations (rerunlib.audit_one: the full reference
ensemble, redrawn from the realization's seed, under the row's own beta).
calprec2 does not calibrate a mean: its criterion C6 (calprec2.py line 213)
is |tau_ref(beta)/tau_0 - 1| <= 0.05 with tau_ref the MEDIAN over six
reference draws. A right-skewed fraction can have its median on target and
its mean above it. v2 prints the median beside the mean, and adds TAU8.

WHICH ROWS WERE AUDITED. rerunlib.AUDIT_ROWS (line 183) is CONC, PROBEARM,
TAU8 and GEOM; rerun.py writes audit_ref_ratio only for those. SIGMA and
ANISO are calprec2 rows but were not audited (their audit_ref_ratio is
empty in every shard row), so they cannot be read here.

Rows read:
  PROBEARM  mechanism probe beta
  GEOM      law probe beta
  CONC      calprec2 fixed beta
  TAU8      calprec2 fixed beta (the operating-level row)

Each row is measured against 1 on its own; no row-against-row contrast.

WRITES NOTHING. Every file is opened for reading only.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-30)
  R1  INPUT, as v1: only the --runs folders, each after its sha256.txt
      verifies; every rerun_real.csv it lists; a row is used iff "rows" is
      exactly PROBEARM, GEOM, CONC or TAU8; it must have end "ok", error
      empty, F1 "ok", a finite audit_ref_ratio; a (cell, rep) twice is exit
      2. Cell = (row, module, objective, d, law, tau0, r, J_inf, arm,
      subarm, diffusion, beta).
  R2  REPRODUCTION GATE, as v1: the --analysis folder (default the
      twenty-one-row analysis) verifies; for every cell the mean in rep
      order equals analysis_audit.csv's ref_ratio_mean for (row, objective,
      d, law, tau0) within 1e-12 x max(1, |x|), same n, same cell sets.
      Failure is exit 3 before any statistic.
  R3  PER CELL: n, mean, median (np.median), SD (ddof 1), min, max; and
      two-sided 95% percentile bootstrap intervals of the mean AND of the
      median from the same resamples, B = 10000, indices
      default_rng(SeedSequence([20261030, row code, cell index]))
      .integers(0, n, (B, n)); row codes PROBEARM 1, GEOM 2, CONC 3, TAU8
      4; cell index = position in the sorted cell list of its row. These are
      v1's codes and seed rule, so for PROBEARM, GEOM and CONC the mean and
      its interval are v1's, by construction.
  R4  VERDICTS PER CELL, each the DIFFERENCE rule against 1: on the mean
      interval and on the median interval separately; "above 1" iff lo >
      1, "below 1" iff hi < 1, else "contains 1". "Contains 1" is not
      "reached the target" (no equivalence claim).
      Example: 15 ratios, mean 1.62 [1.23, 1.99], median 1.04 [0.88,
      1.47]: mean above 1, median contains 1.
  R5  C6 READING, a point value and not a test: "median within 5%" iff
      |median - 1| <= 0.05. It mirrors calprec2's C6 in form only: C6 is
      over six reference draws of calprec2's own, this is over the rerun's
      realizations. Example: median 1.031: yes; 0.948: no.
  R6  SUMMARY, description only: per row and (tau0, d), and per row and
      tau0 ("all"): cells; mean verdicts; median verdicts; cells with
      median within 5%; median, minimum and maximum of the cell medians.

EXIT CODES
  0  ran to the end; every table printed.
  2  bad argument; a folder or manifest problem; an unexpected or
     incomplete input row; a duplicate (cell, rep); a row with no cells.
  3  the reproduction gate R2 failed.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python scripts/refratio2.py --workers 2 --runs <folder> --runs <folder> ...
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
ROWS = ("PROBEARM", "GEOM", "CONC", "TAU8")
ROW_CODE = {"PROBEARM": 1, "GEOM": 2, "CONC": 3, "TAU8": 4}
ROW_BETA = {"PROBEARM": "mechanism probe", "GEOM": "law probe", "CONC": "calprec2 fixed beta",
            "TAU8": "calprec2 fixed beta"}
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
    """R3 to R5 for one cell."""
    row, idx, vals = args
    v = np.array(vals, dtype=float)
    n = v.size
    ss = np.random.SeedSequence([SEED0, ROW_CODE[row], idx])
    ix = np.random.default_rng(ss).integers(0, n, (B, n))
    rs = v[ix]
    bm = rs.mean(axis=1)
    bmed = np.median(rs, axis=1)
    lo, hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
    mlo, mhi = float(np.percentile(bmed, 2.5)), float(np.percentile(bmed, 97.5))
    med = float(np.median(v))
    return {"n": n, "mean": float(v.mean()), "median": med,
            "sd": float(np.std(v, ddof=1)) if n > 1 else float("nan"),
            "min": float(v.min()), "max": float(v.max()), "lo": lo, "hi": hi, "verdict": side(lo, hi),
            "mlo": mlo, "mhi": mhi, "mverdict": side(mlo, mhi), "c6": abs(med - 1.0) <= 0.05}


def side(lo, hi):
    return "above 1" if lo > 1.0 else ("below 1" if hi < 1.0 else "contains 1")


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


def abc(sel, key):
    return "{}/{}/{}".format(sum(1 for x in sel if x[key] == "above 1"),
                             sum(1 for x in sel if x[key] == "below 1"),
                             sum(1 for x in sel if x[key] == "contains 1"))


def main():
    ap = argparse.ArgumentParser(description="reference ratios with medians, v2 (N40)")
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

    hdr("refratio2.py  (ledger N40; second script, v1 kept)  --  writes nothing")
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  workers         {}".format(a.workers))
    say("  rows            {}".format(", ".join("{} ({})".format(r, ROW_BETA[r]) for r in ROWS)))
    say("  bootstrap       B {}, two-sided 95% percentile of the mean and of the median, same resamples".format(B))
    say("  C6 reading      |median - 1| <= 0.05, a point value, not a test (R5)")
    say("  seed rule       default_rng(SeedSequence([{}, row code, cell index])); row codes {}".format(
        SEED0, ", ".join("{} {}".format(r, ROW_CODE[r]) for r in ROWS)))
    say("  gate            analysis_audit.csv ref_ratio_mean, tolerance {} x max(1,|x|)".format(GATE_TOL))
    say("  analysis        {}".format(os.path.abspath(a.analysis)))
    for r in runs:
        say("  run             {}".format(r))

    hdr("What this measures, in plain words")
    for t in (
        "Each row's beta was chosen to give the reference ensemble a target concentration",
        "tau_0. The rerun recorded, for every realization, the reference ensemble's ESS",
        "fraction divided by tau_0. A value of 1 means the target was reached; above 1 means",
        "the reference is less concentrated than intended; below 1, more concentrated.",
        "",
        "The first version of this check tested the average over realizations. The calibrated",
        "rows (CONC, TAU8) were tuned so that the MEDIAN reference fraction is within 5% of the",
        "target, not the average. When a few realizations are far less concentrated than the",
        "rest, the average can sit above 1 while the median is on target. So this version",
        "prints both, each with its own 95% interval, and says whether the median lies within",
        "5% of 1. That last line is a point value, not a test that the target was reached.",
        "",
        "PROBEARM and GEOM use probe betas; CONC and TAU8 use calibrated betas. SIGMA and ANISO",
        "also use calibrated betas but were not audited, so they cannot be shown. Each row is",
        "compared with 1 on its own; no difference between rows is computed.",
    ):
        say("  " + t)

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
            raise Stop(2, "no PROBEARM, GEOM, CONC or TAU8 rows in the folders given")

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
        hdr("{}  ({})  per cell  (R3 to R5)".format(r, ROW_BETA[r]))
        say("  {:<14} {:>3} {:<8} {:>5} {:>3} {:>7} {:>17} {:<10} {:>7} {:>17} {:<10} {:>4} {:>7} {:>7} {:>7}".format(
            "objective", "d", "law", "tau0", "n", "mean", "95% interval", "mean", "median", "95% interval",
            "median", "5%", "sd", "min", "max"))
        for k in ks:
            s_ = stats[k]
            say("  {:<14} {:>3} {:<8} {:>5} {:>3} {:>7} {:>17} {:<10} {:>7} {:>17} {:<10} {:>4} {:>7} {:>7} {:>7}".format(
                k[2][:14], k[3], k[4][:8], k[5], s_["n"], fmt(s_["mean"]),
                "[{}, {}]".format(fmt(s_["lo"]), fmt(s_["hi"])), s_["verdict"], fmt(s_["median"]),
                "[{}, {}]".format(fmt(s_["mlo"]), fmt(s_["mhi"])), s_["mverdict"],
                "yes" if s_["c6"] else "no", fmt(s_["sd"]), fmt(s_["min"]), fmt(s_["max"])))

    hdr("SUMMARY  (R6; description only)")
    say("  a/b/c = above 1 / below 1 / contains 1; 5% = cells whose median is within 5% of 1;")
    say("  median, min, max are of the cell medians")
    for r in ROWS:
        ks = [k for k in stats if k[0] == r]
        taus = sorted({k[5] for k in ks}, key=float)
        dims = sorted({k[3] for k in ks}, key=int)
        say("\n  {}  ({})".format(r, ROW_BETA[r]))
        say("    {:>6} {:>4} {:>6} {:>14} {:>14} {:>6}   {:>8} {:>8} {:>8}".format(
            "tau0", "d", "cells", "mean a/b/c", "median a/b/c", "5%", "median", "min", "max"))
        for t in taus:
            for d in dims + ["all"]:
                sel = [stats[k] for k in ks if k[5] == t and (d == "all" or k[3] == d)]
                if not sel:
                    continue
                say("    {:>6} {:>4} {:>6} {:>14} {:>14} {:>6}   {:>8} {:>8} {:>8}".format(
                    t, d, len(sel), abc(sel, "verdict"), abc(sel, "mverdict"),
                    sum(1 for x in sel if x["c6"]), fmt(float(np.median([x["median"] for x in sel]))),
                    fmt(min(x["median"] for x in sel)), fmt(max(x["median"] for x in sel))))
        tot = [stats[k] for k in ks]
        say("    all cells: {}; mean {}; median {}; median within 5%: {}".format(
            len(tot), abc(tot, "verdict"), abc(tot, "mverdict"), sum(1 for x in tot if x["c6"])))
    hdr("refratio2.py done, exit 0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
