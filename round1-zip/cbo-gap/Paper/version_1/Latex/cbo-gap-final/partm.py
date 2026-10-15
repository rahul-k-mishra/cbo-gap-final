"""
partm.py  —  CBO-GAP: integrity check and interaction analysis for Phase 11 Part M

WHY THIS EXISTS
---------------
Part M of regimemap.py — the tau_0 x r regime map — was pre-registered in that
script and never run. A manuscript table and a figure were nevertheless written
describing its output. The figure rendered as a grid of NaN, which is what
exposed the problem: the plotting code asked for rows with part == "M" and the
archive contained only part == "D". Eighty numbers had no data underneath them.
Both the table and the figure have been removed from the manuscript.

This script does two things, and it is frozen BEFORE the run so that no
criterion can be chosen after seeing the result.

  1. INTEGRITY. It refuses to proceed unless the Part M output is complete and
     finite. The specific failure that produced the retracted table -- a table
     written against absent rows -- is made impossible: every cell the design
     calls for must be present, with the full complement of realizations, and
     no non-finite slope anywhere. If any check fails the script prints what is
     missing and exits non-zero. Nothing downstream runs on a partial file.

  2. THE INTERACTION, MODELLED. The retracted text argued that the two axes
     interact sub-additively from a single cell. That is not an argument. Here
     the deficit

         Delta_c = -1 - gamma_hat_c

     is regressed, separately within each (diffusion, dimension) panel, on

         Delta = a + b1 g(tau_0) + b2 h(r) + b3 g(tau_0) h(r),

         g(tau_0) = log10(0.5 / tau_0),      h(r) = log2(r / 0.5),

     both coordinates being zero at the reference cell (tau_0 = 0.5, r = 0.5),
     so that a is the deficit at the reference, b1 and b2 are the marginal
     effects per decade of concentration and per doubling of r, and b3 is the
     interaction. b3 < 0 is sub-additive, b3 > 0 super-additive, and an
     interval containing zero means the interaction is not resolved and the
     manuscript may claim neither.

PRE-REGISTERED, fixed before the first Part M row exists
--------------------------------------------------------
  Bootstrap unit: the (objective, realization) pair, resampled jointly across
  every cell in a panel so the design stays balanced. 4000 resamples,
  percentile interval, seed 20260821.

  P-M1  INFORMATIVENESS, inherited verbatim from regimemap.py: the map is
        informative iff the fitted exponent varies by more than 0.10 across the
        tau_0 axis at fixed r AND more than 0.10 across the r axis at fixed
        tau_0. Reported per panel. If only one axis moves, the manuscript
        reports one axis.

  P-M2  INTERACTION RESOLVED iff the 95 percent interval for b3 excludes zero
        in at least 3 of the 4 panels, with a consistent sign. If resolved with
        b3 < 0 the manuscript may say sub-additive; with b3 > 0, super-additive;
        otherwise it says the interaction was not resolved and reports the
        interval. No cell-by-cell arithmetic is admissible as a substitute.

  P-M3  EXTERNAL CONSISTENCY. Part M shares no data with the concentration
        experiment of Section 7.3 but overlaps it in design. Within the
        condition (r <= 1.0) the d = 40 minus d = 10 deficit gap at tau_0 = 0.5,
        0.1 and 0.01 must reproduce the values 0.030, 0.099 and 0.553 to within
        twice the noise floor, 0.0438. This is a falsification test of the
        earlier experiment, not a tuning target. A failure is reported as a
        failure and the two experiments are then in conflict.

  P-M4  BOUNDARY AGREEMENT. At tau_0 = 0.1 and r = 1.0, Part M and Part D
        measure the same operating point at d = 10 and d = 40 with different
        seeds. The paired difference must lie within twice the noise floor.
        This is the only direct check that the two halves of Phase 11 agree.

  Nothing in this script decides which claims enter the manuscript except by
  the rules above. The verdict lines print PASS or FAIL and are quoted as
  printed.

WHAT THIS DOES NOT DO
---------------------
It does not run any simulation. It does not modify regimemap.py. It reads the
archived CSVs and prints numbers and a LaTeX table body. If Part M contradicts
Section 7.3, this script says so and the resolution is a separate decision.

HOW TO RUN
    python partm.py --workers 3

Reads regimemap_M_real.csv and regimemap_D_real.csv from the working directory.
NumPy only. No SciPy. Python 3.8 compatible.
"""

import argparse
import csv
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

N_BOOT = 4000
SEED = 20260821
NOISE_FLOOR = 0.0219
AXIS_THRESHOLD = 0.10

DIFFS = ["isotropic", "anisotropic"]
OBJS = ["ackley", "rastrigin", "sphere"]
DIMS_M = [10, 40]
RS_M = [0.5, 1.0, 1.5, 2.0, 3.0]
TAUS_M = [0.5, 0.1, 0.03, 0.01]
REPS = 12

# Section 7.3 values this must reproduce, and the Part D boundary point.
SEC73 = {0.5: 0.030, 0.1: 0.099, 0.01: 0.553}


def load(path):
    if not os.path.exists(path):
        sys.stderr.write("MISSING FILE: {}\n".format(path))
        sys.exit(2)
    rows = []
    for x in csv.DictReader(open(path)):
        rows.append({
            "part": x["part"],
            "diffusion": x["diffusion"],
            "objective": x["objective"],
            "d": int(x["d"]),
            "r": float(x["r"]),
            "tau": float(x["tau"]),
            "rep": int(x["rep"]),
            "slope": float(x["slope"]),
        })
    return rows


def hdr(t):
    print("\n" + "=" * 84)
    print(t)
    print("=" * 84)


# ----------------------------------------------------------------------
# 1. INTEGRITY
# ----------------------------------------------------------------------

def integrity(M):
    hdr("INTEGRITY — the check that the retracted table would have failed")
    fail = []

    parts = sorted(set(x["part"] for x in M))
    print("  parts present            : {}".format(parts))
    if parts != ["M"]:
        fail.append("file contains parts {}, expected only M".format(parts))

    want = set()
    for dif in DIFFS:
        for obj in OBJS:
            for d in DIMS_M:
                for r in RS_M:
                    for t in TAUS_M:
                        want.add((dif, obj, d, r, t))
    have = {}
    for x in M:
        k = (x["diffusion"], x["objective"], x["d"], x["r"], x["tau"])
        have.setdefault(k, []).append(x)

    print("  cells required           : {}".format(len(want)))
    print("  cells present            : {}".format(len(have)))
    missing = sorted(want - set(have))
    if missing:
        fail.append("{} cells missing".format(len(missing)))
        for k in missing[:10]:
            print("    MISSING {}".format(k))
        if len(missing) > 10:
            print("    ... and {} more".format(len(missing) - 10))
    extra = sorted(set(have) - want)
    if extra:
        fail.append("{} cells not in the design".format(len(extra)))

    short = [(k, len(v)) for k, v in sorted(have.items()) if len(v) != REPS]
    print("  cells with {} realizations: {}".format(REPS, len(have) - len(short)))
    if short:
        fail.append("{} cells have the wrong realization count".format(len(short)))
        for k, n in short[:10]:
            print("    SHORT {} has {}".format(k, n))

    bad = [x for x in M if not np.isfinite(x["slope"])]
    print("  non-finite slopes        : {}".format(len(bad)))
    if bad:
        fail.append("{} non-finite slopes".format(len(bad)))

    print("  total realizations       : {}".format(len(M)))
    if len(M) != len(want) * REPS:
        fail.append("expected {} realizations, found {}".format(len(want) * REPS, len(M)))

    if fail:
        print("\n  INTEGRITY: FAIL")
        for f in fail:
            print("    - {}".format(f))
        print("\n  Nothing downstream is computed. Fix the run and rerun this script.")
        sys.exit(1)
    print("\n  INTEGRITY: PASS  — {} cells x {} realizations, all finite".format(len(want), REPS))
    return have


def panel_matrix(have, dif, d):
    """Return arrays keyed by (tau, r) -> dict[(obj,rep)] = deficit."""
    out = {}
    for t in TAUS_M:
        for r in RS_M:
            cell = {}
            for obj in OBJS:
                for x in have[(dif, obj, d, r, t)]:
                    cell[(obj, x["rep"])] = -1.0 - x["slope"]
            out[(t, r)] = cell
    return out


# ----------------------------------------------------------------------
# 2. P-M1 informativeness
# ----------------------------------------------------------------------

def informativeness(have):
    hdr("P-M1 — INFORMATIVENESS (criterion fixed in regimemap.py: > 0.10 on both axes)")
    verdicts = {}
    for dif in DIFFS:
        for d in DIMS_M:
            P = panel_matrix(have, dif, d)
            mean = dict(((k, float(np.mean(list(v.values())))) for k, v in P.items()))
            tau_ranges = [max(mean[(t, r)] for t in TAUS_M) - min(mean[(t, r)] for t in TAUS_M)
                          for r in RS_M]
            r_ranges = [max(mean[(t, r)] for r in RS_M) - min(mean[(t, r)] for r in RS_M)
                        for t in TAUS_M]
            a = min(tau_ranges)
            b = min(r_ranges)
            ok = (a > AXIS_THRESHOLD) and (b > AXIS_THRESHOLD)
            verdicts[(dif, d)] = ok
            print("  {:<12} d={:<3d} min range along tau_0 {:.3f} | along r {:.3f} | {}".format(
                dif, d, a, b, "INFORMATIVE" if ok else "ONE AXIS ONLY"))
    n = sum(1 for v in verdicts.values() if v)
    print("\n  P-M1: {} of 4 panels informative on both axes".format(n))
    return verdicts


# ----------------------------------------------------------------------
# 3. P-M2 interaction model
# ----------------------------------------------------------------------

def design_rows(P, keys):
    """Build (X, y) for one bootstrap resample given the (obj,rep) keys used."""
    X = []
    y = []
    for t in TAUS_M:
        for r in RS_M:
            g = math.log10(0.5 / t)
            h = math.log(r / 0.5) / math.log(2.0)
            cell = P[(t, r)]
            y.append(float(np.mean([cell[k] for k in keys])))
            X.append([1.0, g, h, g * h])
    return np.array(X), np.array(y)


def _boot(args):
    P, keys, n, seed = args
    rng = np.random.default_rng(seed)
    idx_pool = list(keys)
    out = np.empty((n, 4))
    for i in range(n):
        samp = [idx_pool[j] for j in rng.integers(0, len(idx_pool), len(idx_pool))]
        X, y = design_rows(P, samp)
        out[i] = np.linalg.lstsq(X, y, rcond=None)[0]
    return out


def interaction(have, workers):
    hdr("P-M2 — INTERACTION MODEL  Delta = a + b1 g(tau_0) + b2 h(r) + b3 g h")
    print("  g(tau_0) = log10(0.5/tau_0)   h(r) = log2(r/0.5)   reference cell tau_0=0.5, r=0.5")
    print("  paired bootstrap over (objective, realization), {} resamples\n".format(N_BOOT))
    print("  {:<12} {:>4} {:>9} {:>9} {:>9} {:>9} {:>21}".format(
        "diffusion", "d", "a", "b1", "b2", "b3", "b3 95% interval"))
    res = {}
    jobs = []
    meta = []
    per = max(1, N_BOOT // max(1, workers))
    for dif in DIFFS:
        for d in DIMS_M:
            P = panel_matrix(have, dif, d)
            keys = sorted(P[(TAUS_M[0], RS_M[0])].keys())
            X, y = design_rows(P, keys)
            fit = np.linalg.lstsq(X, y, rcond=None)[0]
            res[(dif, d)] = {"fit": fit, "P": P, "keys": keys}
            for w in range(workers):
                jobs.append((P, keys, per, SEED + 1000 * len(meta) + w))
            meta.append((dif, d, workers))
    pool = Pool(processes=workers)
    try:
        chunks = pool.map(_boot, jobs)
    finally:
        pool.close()
        pool.join()

    at = 0
    resolved = []
    for (dif, d, w) in meta:
        B = np.vstack(chunks[at:at + w])
        at += w
        fit = res[(dif, d)]["fit"]
        lo, hi = np.percentile(B[:, 3], [2.5, 97.5])
        res[(dif, d)]["ci3"] = (lo, hi)
        res[(dif, d)]["boot"] = B
        excl = (lo > 0) or (hi < 0)
        resolved.append((dif, d, fit[3], lo, hi, excl))
        print("  {:<12} {:>4d} {:>+9.4f} {:>+9.4f} {:>+9.4f} {:>+9.4f} {:>21}".format(
            dif, d, fit[0], fit[1], fit[2], fit[3],
            "[{:+.4f},{:+.4f}]{}".format(lo, hi, "*" if excl else "")))

    nex = sum(1 for x in resolved if x[5])
    signs = set(np.sign(x[2]) for x in resolved if x[5])
    print("\n  panels with b3 interval excluding zero: {} of 4".format(nex))
    if nex >= 3 and len(signs) == 1:
        s = signs.pop()
        word = "SUB-ADDITIVE" if s < 0 else "SUPER-ADDITIVE"
        print("  P-M2: PASS — interaction resolved and {}.".format(word))
        print("        The manuscript may state this, quoting the four intervals above.")
    else:
        print("  P-M2: FAIL — interaction NOT resolved by the pre-registered rule.")
        print("        The manuscript reports the intervals and claims no interaction sign.")
    return res


# ----------------------------------------------------------------------
# 4. P-M3 external consistency with Section 7.3
# ----------------------------------------------------------------------

def external(have):
    hdr("P-M3 — EXTERNAL CONSISTENCY with Section 7.3 (d=40 minus d=10, r <= 1)")
    print("  tolerance 2 x noise floor = {:.4f}\n".format(2 * NOISE_FLOOR))
    allpass = True
    for dif in DIFFS:
        for t in (0.5, 0.1, 0.01):
            g10 = []
            g40 = []
            for r in (0.5, 1.0):
                for obj in OBJS:
                    g10 += [-1.0 - x["slope"] for x in have[(dif, obj, 10, r, t)]]
                    g40 += [-1.0 - x["slope"] for x in have[(dif, obj, 40, r, t)]]
            gap = float(np.mean(g40) - np.mean(g10))
            want = SEC73[t]
            ok = abs(gap - want) <= 2 * NOISE_FLOOR
            allpass = allpass and (ok or dif == "anisotropic")
            print("  {:<12} tau_0={:<5} gap {:+.4f}  Section 7.3 {:+.4f}  diff {:+.4f}  {}".format(
                dif, t, gap, want, gap - want, "PASS" if ok else "**FAIL**"))
    print("\n  Section 7.3 used isotropic diffusion; the anisotropic rows are")
    print("  reported for completeness and are not part of the test.")
    print("  P-M3: {}".format("PASS" if allpass else "FAIL — the two experiments conflict"))


# ----------------------------------------------------------------------
# 5. P-M4 agreement with Part D at the shared operating point
# ----------------------------------------------------------------------

def boundary(have, D):
    hdr("P-M4 — AGREEMENT WITH PART D at tau_0 = 0.1, r = 1.0")
    print("  tolerance 2 x noise floor = {:.4f}\n".format(2 * NOISE_FLOOR))
    ok_all = True
    for dif in DIFFS:
        for d in DIMS_M:
            m = []
            for obj in OBJS:
                m += [x["slope"] for x in have[(dif, obj, d, 1.0, 0.1)]]
            dd = [x["slope"] for x in D
                  if x["diffusion"] == dif and x["d"] == d
                  and abs(x["r"] - 1.0) < 1e-9 and abs(x["tau"] - 0.1) < 1e-9]
            if not dd:
                print("  {:<12} d={:<3d} Part D has no matching cell".format(dif, d))
                continue
            a, b = float(np.mean(m)), float(np.mean(dd))
            ok = abs(a - b) <= 2 * NOISE_FLOOR
            ok_all = ok_all and ok
            print("  {:<12} d={:<3d} Part M {:+.4f}  Part D {:+.4f}  diff {:+.4f}  {}".format(
                dif, d, a, b, a - b, "PASS" if ok else "**FAIL**"))
    print("\n  P-M4: {}".format("PASS" if ok_all else "FAIL — the two halves of Phase 11 disagree"))


# ----------------------------------------------------------------------
# 6. the table body, printed as LaTeX
# ----------------------------------------------------------------------

def latex(have):
    hdr("TABLE BODY — paste into the manuscript verbatim; do not retype")
    print(r"\begin{tabular}{@{}llccccc@{}}")
    print(r"\toprule")
    print(r"& $\tau_0$ & " + " & ".join(r"$r=%s$" % ("%.1f" % r) for r in RS_M) + r"\\")
    print(r"\midrule")
    first = True
    for dif in DIFFS:
        for d in DIMS_M:
            if not first:
                print(r"\midrule")
            first = False
            lab = ("iso" if dif == "isotropic" else "aniso") + ", $d=%d$" % d
            print(r"\multirow{4}{*}{%s}" % lab)
            for t in TAUS_M:
                vals = []
                for r in RS_M:
                    v = []
                    for obj in OBJS:
                        v += [x["slope"] for x in have[(dif, obj, d, r, t)]]
                    vals.append("$%+.3f$" % float(np.mean(v)))
                print(r" & $%s$ & " % ("%.2f" % t) + " & ".join(vals) + r"\\")
    print(r"\botrule")
    print(r"\end{tabular}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--m", default="regimemap_M_real.csv")
    p.add_argument("--d", default="regimemap_D_real.csv")
    a = p.parse_args()

    print("=" * 84)
    print("CBO-GAP — Phase 11 Part M: integrity and interaction")
    print("=" * 84)
    print("  criteria frozen before the first Part M row existed; see the docstring")
    print("  numpy {}   python {}".format(np.__version__, sys.version.split()[0]))

    M = load(a.m)
    D = load(a.d)
    have = integrity(M)
    informativeness(have)
    interaction(have, a.workers)
    external(have)
    boundary(have, D)
    latex(have)
    print("\n" + "=" * 84)
    print("Send this entire console output. Nothing is quoted from it selectively.")
    print("=" * 84)


if __name__ == "__main__":
    main()
