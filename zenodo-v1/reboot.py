"""
reboot.py  —  CBO-GAP: recompute every bootstrap interval at 4000 resamples

WHY THIS EXISTS
---------------
The simulation scripts computed percentile intervals from 400 resamples. With
12 realizations in the smallest cells the tails of a 400-resample percentile
interval are coarse, and a referee asked for 2000 or more. Bootstrap resampling
costs nothing next to 30480 stochastic trajectories, so there is no reason to
report the coarse version.

This script runs NO SIMULATION. It reads the archived per-realization files and
recomputes, at 4000 resamples with a fixed seed:

  * the paired anisotropic-minus-isotropic gaps and their equivalence verdicts
    (Table 9 of the manuscript), from regimemap_D_real.csv;
  * the severity drops on both contrasts, boundary-spanning gamma(0.75)-gamma(3)
    and non-admissible gamma(1.0)-gamma(3), with their dimension trends;
  * the free-breakpoint onset estimates and intervals (Table 8);
  * the panel-wise interaction coefficients b3 (Section 7.12), from
    regimemap_M_real.csv.

It then prints, for every quantity, the 400-resample value beside the
4000-resample value and the largest endpoint shift, so that the manuscript can
state the difference as a measured number rather than assert that it is small.
A verdict flips only if an interval endpoint crosses a decision threshold; the
script counts those explicitly and names them.

WHAT IS NOT RECOMPUTED, AND WHY
-------------------------------
The tolerance table of Section 7.5 comes from boundary.py, whose archived file
stores per-J aggregates rather than per-realization slopes. Its intervals cannot
be recomputed without rerunning that phase, and this script says so rather than
silently omitting it. If that table's intervals are to be upgraded too, the fix
is to rerun boundary.py with per-realization storage, which is a separate 4.7
hour job and is not required by anything in the manuscript.

PRE-REGISTERED, unchanged from the generating scripts
-----------------------------------------------------
  Bootstrap unit: the independent coupled realization. Percentile interval.
  Two-arm comparisons resample PAIRED on the shared realization index.
  Equivalence by two one-sided tests at margin 0.05.
  Onset by free-breakpoint profile least squares in log r; it differs from the
  theoretical boundary only if the interval excludes r = 1.
  Seeds are fixed in this file. Only the resample count changes.

HOW TO RUN
    python reboot.py --workers 3

Reads regimemap_D_real.csv and regimemap_M_real.csv from the working directory.
Writes nothing. Print the console output and send it whole.
NumPy only. No SciPy. Python 3.8 compatible.
"""

import argparse
import csv
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

B_OLD = 400
B_NEW = 4000
SEED = 20260822
EQUIV = 0.05
DIMS_D = [5, 10, 20, 40, 80]
RS_D = [0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
DIMS_M = [10, 40]
RS_M = [0.5, 1.0, 1.5, 2.0, 3.0]
TAUS_M = [0.5, 0.1, 0.03, 0.01]
DIFFS = ["isotropic", "anisotropic"]


def load(path):
    if not os.path.exists(path):
        sys.stderr.write("MISSING FILE: {}\n".format(path))
        sys.exit(2)
    out = []
    for x in csv.DictReader(open(path)):
        out.append({"diffusion": x["diffusion"], "objective": x["objective"],
                    "d": int(x["d"]), "r": float(x["r"]), "tau": float(x["tau"]),
                    "rep": int(x["rep"]), "slope": float(x["slope"])})
    return out


def hdr(t):
    print("\n" + "=" * 86)
    print(t)
    print("=" * 86)


def cell(R, dif, d, r, tau=None):
    return dict(((x["objective"], x["rep"]), x["slope"]) for x in R
                if x["diffusion"] == dif and x["d"] == d
                and abs(x["r"] - r) < 1e-9
                and (tau is None or abs(x["tau"] - tau) < 1e-12))


def boot_mean(v, B, seed):
    rng = np.random.default_rng(seed)
    n = len(v)
    return np.array([v[rng.integers(0, n, n)].mean() for _ in range(B)])


# ----------------------------------------------------------------------
def paired_gaps(D):
    hdr("PAIRED anisotropic minus isotropic  —  400 vs 4000 resamples")
    print("  equivalence margin {:.2f}; DIFFERENT if the whole 90% interval is beyond it\n".format(EQUIV))
    print("  %-4s %-5s %9s %21s %21s %8s %9s" % ("d", "r", "gap", "90% @400", "90% @4000", "shift", "verdict"))
    worst = 0.0
    flips = []
    for d in DIMS_D:
        for r in RS_D:
            a, i = cell(D, "anisotropic", d, r), cell(D, "isotropic", d, r)
            k = sorted(set(a) & set(i))
            if len(k) < 3:
                continue
            v = np.array([a[x] - i[x] for x in k])
            s = SEED + d * 100 + int(r * 100)
            o = np.percentile(boot_mean(v, B_OLD, s), [5, 95])
            n = np.percentile(boot_mean(v, B_NEW, s), [5, 95])
            sh = max(abs(n[0] - o[0]), abs(n[1] - o[1]))
            worst = max(worst, sh)

            def verdict(c):
                if c[0] > -EQUIV and c[1] < EQUIV:
                    return "EQUIV"
                if c[0] > EQUIV or c[1] < -EQUIV:
                    return "DIFF"
                return "incon"
            vo, vn = verdict(o), verdict(n)
            if vo != vn:
                flips.append((d, r, vo, vn))
            print("  %-4d %-5s %+9.4f  [%+0.4f,%+0.4f]  [%+0.4f,%+0.4f] %8.4f %9s" %
                  (d, r, v.mean(), o[0], o[1], n[0], n[1], sh, vn + ("*" if vo != vn else "")))
    print("\n  largest endpoint shift: %.4f" % worst)
    print("  verdicts changed: %d" % len(flips))
    for f in flips:
        print("    d=%d r=%s  %s -> %s" % f)
    return worst, flips


# ----------------------------------------------------------------------
def severity(D):
    hdr("SEVERITY on both contrasts, with dimension trends at 4000 resamples")
    for lo, lab in ((0.75, "boundary-spanning  gamma(0.75)-gamma(3)"),
                    (1.0, "non-admissible     gamma(1.00)-gamma(3)")):
        print("\n  " + lab)
        print("  %-12s" % "" + "".join("%12s" % ("d=%d" % d) for d in DIMS_D))
        curves = {}
        for dif in DIFFS:
            A = dict((d, cell(D, dif, d, lo)) for d in DIMS_D)
            Bc = dict((d, cell(D, dif, d, 3.0)) for d in DIMS_D)
            keys = sorted(set.intersection(*[set(A[d]) & set(Bc[d]) for d in DIMS_D]))
            drops = [-np.mean([A[d][k] - Bc[d][k] for k in keys]) for d in DIMS_D]
            curves[dif] = (A, Bc, keys)
            print("  %-12s" % dif + "".join("%+12.4f" % v for v in drops))
        x = np.log2(np.array(DIMS_D, float))
        for dif in DIFFS:
            A, Bc, keys = curves[dif]
            rng = np.random.default_rng(SEED + (0 if dif == "isotropic" else 1))

            def fit(ks):
                y = np.array([-np.mean([A[d][k] - Bc[d][k] for k in ks]) for d in DIMS_D])
                return np.polyfit(x, y, 1)[0]
            b = fit(keys)
            bs = np.array([fit([keys[j] for j in rng.integers(0, len(keys), len(keys))])
                           for _ in range(B_NEW)])
            lo_, hi_ = np.percentile(bs, [2.5, 97.5])
            print("    %-12s trend %+0.4f per doubling  95%% [%+0.4f,%+0.4f]  n_pairs=%d" %
                  (dif, b, lo_, hi_, len(keys)))


# ----------------------------------------------------------------------
def breakpoint_profile(rs, ys):
    """Free-breakpoint profile least squares in log r; returns the best knot."""
    lr = np.log(np.array(rs))
    y = np.array(ys)
    best, bk = None, None
    for k in range(1, len(rs) - 1):
        c = lr[k]
        X = np.column_stack([np.ones_like(lr), np.minimum(lr - c, 0.0), np.maximum(lr - c, 0.0)])
        beta, res, _, _ = np.linalg.lstsq(X, y, rcond=None)
        r2 = float(((y - X.dot(beta)) ** 2).sum())
        if best is None or r2 < best:
            best, bk = r2, rs[k]
    return bk


def onset(D):
    hdr("ONSET: free breakpoint in log r at tau_0 = 0.1, 4000 resamples")
    print("  the onset differs from the theoretical boundary only if the interval excludes r = 1\n")
    print("  %-12s %-4s %10s %24s %10s" % ("diffusion", "d", "breakpoint", "95% interval", "excludes 1"))
    nex = 0
    for dif in DIFFS:
        for d in DIMS_D:
            cells = dict((r, cell(D, dif, d, r)) for r in RS_D)
            keys = sorted(set.intersection(*[set(cells[r]) for r in RS_D]))
            ys = [np.mean([cells[r][k] for k in keys]) for r in RS_D]
            bk = breakpoint_profile(RS_D, ys)
            rng = np.random.default_rng(SEED + d + (0 if dif == "isotropic" else 7))
            bs = []
            for _ in range(B_NEW):
                ks = [keys[j] for j in rng.integers(0, len(keys), len(keys))]
                bs.append(breakpoint_profile(RS_D, [np.mean([cells[r][k] for k in ks]) for r in RS_D]))
            lo_, hi_ = np.percentile(bs, [2.5, 97.5])
            ex = (lo_ > 1.0) or (hi_ < 1.0)
            nex += 1 if ex else 0
            print("  %-12s %-4d %10.2f       [%.2f,%.2f]        %s" %
                  (dif, d, bk, lo_, hi_, "YES" if ex else "no"))
    print("\n  intervals excluding r = 1: %d of 10" % nex)
    print("  the manuscript states nine of ten contain it; this line is the check")


# ----------------------------------------------------------------------
def _b3(args):
    P, keys, n, seed = args
    rng = np.random.default_rng(seed)
    out = np.empty(n)
    for i in range(n):
        ks = [keys[j] for j in rng.integers(0, len(keys), len(keys))]
        X, y = [], []
        for t in TAUS_M:
            for r in RS_M:
                g = math.log10(0.5 / t)
                h = math.log(r / 0.5) / math.log(2.0)
                X.append([1.0, g, h, g * h])
                y.append(float(np.mean([P[(t, r)][k] for k in ks])))
        out[i] = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)[0][3]
    return out


def interaction(M, workers):
    hdr("INTERACTION b3 per panel, 4000 resamples")
    print("  Delta = a + b1 log10(0.5/tau_0) + b2 log2(r/0.5) + b3 (product)\n")
    print("  %-12s %-4s %10s %24s %10s" % ("diffusion", "d", "b3", "95% interval", "excludes 0"))
    jobs, meta = [], []
    per = max(1, B_NEW // max(1, workers))
    for dif in DIFFS:
        for d in DIMS_M:
            P = {}
            for t in TAUS_M:
                for r in RS_M:
                    P[(t, r)] = dict(((x["objective"], x["rep"]), -1.0 - x["slope"])
                                     for x in M if x["diffusion"] == dif and x["d"] == d
                                     and abs(x["r"] - r) < 1e-9 and abs(x["tau"] - t) < 1e-12)
            keys = sorted(P[(TAUS_M[0], RS_M[0])].keys())
            X, y = [], []
            for t in TAUS_M:
                for r in RS_M:
                    g = math.log10(0.5 / t)
                    h = math.log(r / 0.5) / math.log(2.0)
                    X.append([1.0, g, h, g * h])
                    y.append(float(np.mean([P[(t, r)][k] for k in keys])))
            fit = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)[0]
            for w in range(workers):
                jobs.append((P, keys, per, SEED + 500 * len(meta) + w))
            meta.append((dif, d, workers, fit[3]))
    pool = Pool(processes=workers)
    try:
        chunks = pool.map(_b3, jobs)
    finally:
        pool.close()
        pool.join()
    at, nex, signs = 0, 0, set()
    for (dif, d, w, b3) in meta:
        bs = np.concatenate(chunks[at:at + w])
        at += w
        lo_, hi_ = np.percentile(bs, [2.5, 97.5])
        ex = (lo_ > 0) or (hi_ < 0)
        nex += 1 if ex else 0
        if ex:
            signs.add(np.sign(b3))
        print("  %-12s %-4d %+10.4f    [%+0.4f,%+0.4f]        %s" %
              (dif, d, b3, lo_, hi_, "YES" if ex else "no"))
    print("\n  intervals excluding zero: %d of 4" % nex)
    if nex >= 3 and len(signs) == 1:
        print("  RESOLVED and %s" % ("sub-additive" if signs.pop() < 0 else "super-additive"))
    else:
        print("  NOT RESOLVED under the prespecified rule; no sign is claimed")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--d", default="regimemap_D_real.csv")
    p.add_argument("--m", default="regimemap_M_real.csv")
    a = p.parse_args()
    print("=" * 86)
    print("CBO-GAP — bootstrap re-analysis at {} resamples (no simulation)".format(B_NEW))
    print("=" * 86)
    print("  numpy {}   python {}".format(np.__version__, sys.version.split()[0]))
    D, M = load(a.d), load(a.m)
    print("  loaded {} Part D rows, {} Part M rows".format(len(D), len(M)))
    paired_gaps(D)
    severity(D)
    onset(D)
    interaction(M, a.workers)
    hdr("NOT RECOMPUTED")
    print("  The tolerance table of Section 7.5 comes from boundary.py, whose archived")
    print("  file stores per-J aggregates and not per-realization slopes. Its intervals")
    print("  cannot be recomputed here. Upgrading them requires rerunning that phase")
    print("  with per-realization storage; nothing in the manuscript depends on it.")
    print("\nSend this entire console output.")


if __name__ == "__main__":
    main()
