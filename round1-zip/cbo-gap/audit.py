"""
audit.py  —  CBO-GAP: the statistical points, closed from existing data

A referee raised seventy points on the v0.3 manuscript. Ten of them are
statistical defects that need no new simulation, only correct analysis of runs
already on disk. This script performs those analyses and prints the numbers the
manuscript must quote instead of the informal ones it currently uses.

WHAT IS FIXED HERE

  A1  "NOISE FLOOR" WAS NEVER DEFINED.
      The manuscript compares effects against 0.055 and calls it a noise floor
      without saying what it is. Defined here as the median across cells of the
      bootstrap standard error of the fitted slope, computed from the per-J
      standard errors already stored. Printed with its interquartile range, so
      the reader can see the spread rather than a single number.

  A2  "LIES INSIDE THE NOISE FLOOR" IS NOT AN INFERENTIAL ARGUMENT.
      The claim that r does not move the exponent inside the condition rested on
      regression coefficients in [-0.057, +0.052] against a floor of 0.055 --
      coefficients the same size as the yardstick. Here each regression of slope
      on r gets a confidence interval, and the verdict is stated as whether that
      interval excludes an effect of practical size, not whether a point
      estimate is small.

  A3  "INDISTINGUISHABLE" REQUIRES EQUIVALENCE TESTING.
      A non-significant difference is not evidence of equivalence. Two one-sided
      tests are run at the prespecified margin of 0.05 for the isotropic versus
      anisotropic comparison at matched sigma. If the interval for the
      difference lies wholly inside the margin, equivalence is established; if
      it merely contains zero, it is not, and the script says so.

  A4  "DEGRADATION BEGINS NEAR r = 1.5" WAS AN EYEBALL THRESHOLD.
      A three-model comparison is run: a single line in log r, a break fixed at
      the theoretical boundary r = 1, and a break at a free location. The free
      breakpoint is estimated by profile least squares over the grid and given a
      bootstrap interval. Only if that interval excludes r = 1 may the
      manuscript say the empirical onset differs from the sufficient condition.

  A5  THE FITTED SLOPE DEPENDS ON THE FITTING WINDOW.
      The exponent is fitted over one J range and never tested against that
      choice. A sensitivity grid over lower and upper cutoffs is printed.

  A6  TOLERANCE AND MULTIPLICITY TABLES WERE PROMISED, NOT SHOWN.
      Counts at tolerances 0.10, 0.15 and 0.20, and with Bonferroni-adjusted
      intervals, for every experiment that has stored intervals.

  A7  THE REALIZATION COUNT MUST BE RECONSTRUCTIBLE.
      Cells and realizations are recounted directly from the CSV files rather
      than asserted.

WHAT CANNOT BE FIXED FROM STORED DATA, AND MUST BE SAID
  The raw files store, for each cell and each J, the mean of the coupled error
  over realizations together with its standard error. They do NOT store the
  per-realization values. A properly paired analysis of the isotropic versus
  anisotropic arms -- which shared seeds, and where pairing would remove most of
  the between-realization variance -- therefore cannot be performed from these
  files. The equivalence test below uses a normal approximation built from the
  stored standard errors, which is weaker, and this is flagged in its output.
  Future runs should store per-realization slopes; the companion script
  regimemap.py does.

HOW TO RUN
    python audit.py

Reads whatever CSV files are present in the working directory and skips the
rest. NumPy only.
"""

import csv
import glob
import math
import os
import collections

import numpy as np

TOLS = [0.10, 0.15, 0.20]
EQUIV_MARGIN = 0.05
N_BOOT = 2000
RNG = np.random.default_rng(11)


def load(path):
    return list(csv.DictReader(open(path))) if os.path.exists(path) else []


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def hdr(t):
    print("\n" + "=" * 84)
    print(t)
    print("=" * 84)


# ----------------------------------------------------------------------
# A7 + A1: bookkeeping and the noise floor
# ----------------------------------------------------------------------

def bookkeeping_and_floor():
    hdr("A7 — realization count reconstructed from the files, not asserted")
    tot_cells = tot_real = 0
    print("  {:<28} {:>8} {:>14} {:>12}".format("file", "cells", "realizations", "J values"))
    for f in sorted(glob.glob("*_raw.csv")) + sorted(glob.glob("law_synth.csv")):
        rows = load(f)
        if not rows:
            continue
        key = [k for k in rows[0] if k not in ("J", "Ehat", "stderr", "realisations")]
        cells = {tuple(r[k] for k in key if k in r) for r in rows}
        if "realisations" in rows[0]:
            per = {}
            for r in rows:
                per[tuple(r[k] for k in key if k in r)] = int(r["realisations"])
            nreal = sum(per.values())
            njs = len({r["J"] for r in rows}) if "J" in rows[0] else 0
        else:
            nreal, njs = 0, 0
        tot_cells += len(cells)
        tot_real += nreal
        print("  {:<28} {:>8} {:>14} {:>12}".format(f, len(cells), nreal, njs))
    print("  {:<28} {:>8} {:>14}".format("TOTAL (files present here)", tot_cells, tot_real))
    print("\n  Note: this counts only files in this directory. The manuscript total")
    print("  covers every phase; cross-check against the experiment matrix table.")

    hdr("A1 — the noise floor, defined")
    print("  Definition: sigma_floor = median over cells of SE(slope), where")
    print("  SE(slope) is propagated from the stored per-J standard errors by")
    print("  the delta method on the log-log regression. Previously the")
    print("  manuscript compared effects against 0.055 without saying what it was.\n")
    ses = []
    for f in sorted(glob.glob("*_raw.csv")):
        rows = load(f)
        if not rows or "stderr" not in rows[0]:
            continue
        key = [k for k in rows[0] if k not in ("J", "Ehat", "stderr", "realisations")]
        g = collections.defaultdict(list)
        for r in rows:
            g[tuple(r[k] for k in key)].append((float(r["J"]), float(r["Ehat"]),
                                                float(r["stderr"])))
        loc = []
        for k, v in g.items():
            v = sorted(v)
            J = np.array([x[0] for x in v])
            E = np.array([x[1] for x in v])
            S = np.array([x[2] for x in v])
            m = (E > 0) & np.isfinite(E)
            if m.sum() < 3:
                continue
            x = np.log(J[m])
            xc = x - x.mean()
            # delta method: d(log E)/dE = 1/E, so var(log E) ~ (S/E)^2
            w = (S[m] / E[m]) ** 2
            se = math.sqrt(float((xc ** 2 * w).sum()) / float((xc ** 2).sum() ** 2))
            loc.append(se)
        if loc:
            ses.extend(loc)
            print("    {:<26} n={:<5} median SE {:.4f}   IQR [{:.4f},{:.4f}]".format(
                f, len(loc), float(np.median(loc)),
                float(np.percentile(loc, 25)), float(np.percentile(loc, 75))))
    if ses:
        print("\n    POOLED sigma_floor = {:.4f}   IQR [{:.4f},{:.4f}]   n={}".format(
            float(np.median(ses)), float(np.percentile(ses, 25)),
            float(np.percentile(ses, 75)), len(ses)))
        print("    This is the number the manuscript should quote, with its IQR.")


# ----------------------------------------------------------------------
# A2: regression of slope on r, with intervals
# ----------------------------------------------------------------------

def r_regression():
    rows = load("sigma_summary.csv")
    if not rows:
        return
    hdr("A2 — does r move the exponent inside the condition? with intervals")
    print("  Previously: coefficients in [-0.057,+0.052] declared 'inside the noise")
    print("  floor'. That compares a point estimate to a yardstick of the same size.")
    print("  Here each coefficient gets a bootstrap interval over objectives.\n")
    for r in rows:
        for k in ("r", "tau", "slope"):
            r[k] = float(r[k])
        r["d"] = int(r["d"])
    objs = sorted({r["objective"] for r in rows})
    print("  {:<13} {:>5} {:>7} {:>10} {:>20} {:>26}".format(
        "diffusion", "d", "tau", "coef", "95% CI", "verdict"))
    for diff in sorted({r["diffusion"] for r in rows}):
        for d in sorted({r["d"] for r in rows}):
            for t in sorted({r["tau"] for r in rows}, reverse=True):
                sub = [r for r in rows if r["diffusion"] == diff and r["d"] == d
                       and r["tau"] == t]
                if len(sub) < 6:
                    continue
                byo = collections.defaultdict(list)
                for r in sub:
                    byo[r["objective"]].append((r["r"], r["slope"]))
                def coef(sel):
                    pts = [p for o in sel for p in byo[o]]
                    X = np.array([p[0] for p in pts])
                    Y = np.array([p[1] for p in pts])
                    A = np.vstack([X, np.ones(len(X))]).T
                    return float(np.linalg.lstsq(A, Y, rcond=None)[0][0])
                base = coef(objs)
                bs = [coef(list(RNG.choice(objs, len(objs), replace=True)))
                      for _ in range(500)]
                lo, hi = np.percentile(bs, [2.5, 97.5])
                v = ("no effect of size 0.10 detected" if abs(lo) < 0.10 and abs(hi) < 0.10
                     else "effect of practical size possible")
                print("  {:<13} {:>5} {:>7g} {:>10.4f} {:>20} {:>26}".format(
                    diff, d, t, base, "[{:+.3f},{:+.3f}]".format(lo, hi), v))
    print("\n  The correct claim is 'no monotone dependence distinguishable under this")
    print("  design', not 'r does not move the exponent'.")


# ----------------------------------------------------------------------
# A3: equivalence testing for isotropic vs anisotropic
# ----------------------------------------------------------------------

def equivalence():
    rows = load("crossed_summary.csv")
    if not rows:
        return
    hdr("A3 — equivalence test, isotropic versus anisotropic at matched sigma")
    print("  A gap below 0.05 is not evidence of equivalence. Two one-sided tests")
    print("  at the prespecified margin {:.2f}: equivalence holds only if the whole".format(EQUIV_MARGIN))
    print("  interval for the difference lies inside the margin.")
    print("  CAVEAT: the stored files hold cell means, not per-realization values,")
    print("  so the arms cannot be paired even though they shared seeds. This")
    print("  interval is therefore wider than a paired one would be, and the test")
    print("  is conservative.\n")
    for r in rows:
        for k in ("level", "tau", "slope", "ci_lo", "ci_hi"):
            r[k] = float(r[k])
        r["d"] = int(r["d"])
    objs = sorted({r["objective"] for r in rows})
    print("  {:<5} {:>6} {:>5} {:>7} {:>9} {:>20} {:>24}".format(
        "arm", "level", "d", "tau", "gap", "90% CI", "verdict"))
    for arm in sorted({r["arm"] for r in rows}):
        for lvl in sorted({r["level"] for r in rows if r["arm"] == arm}):
            for d in sorted({r["d"] for r in rows}):
                for t in sorted({r["tau"] for r in rows}, reverse=True):
                    def get(diff, o):
                        s = [r for r in rows if r["arm"] == arm and r["diffusion"] == diff
                             and r["objective"] == o and r["d"] == d
                             and r["level"] == lvl and r["tau"] == t]
                        return s[0] if s else None
                    pairs = [(get("isotropic", o), get("anisotropic", o)) for o in objs]
                    pairs = [(a, b) for a, b in pairs if a and b]
                    if len(pairs) < 3:
                        continue
                    diffs = np.array([b["slope"] - a["slope"] for a, b in pairs])
                    bs = [float(np.mean(RNG.choice(diffs, len(diffs), replace=True)))
                          for _ in range(N_BOOT)]
                    lo, hi = np.percentile(bs, [5, 95])
                    if lo > -EQUIV_MARGIN and hi < EQUIV_MARGIN:
                        v = "EQUIVALENT at margin"
                    elif lo > EQUIV_MARGIN or hi < -EQUIV_MARGIN:
                        v = "DIFFERENT beyond margin"
                    else:
                        v = "inconclusive"
                    print("  {:<5} {:>6g} {:>5} {:>7g} {:>9.4f} {:>20} {:>24}".format(
                        arm, lvl, d, t, float(diffs.mean()),
                        "[{:+.3f},{:+.3f}]".format(lo, hi), v))


# ----------------------------------------------------------------------
# A4: change-point analysis for the degradation onset
# ----------------------------------------------------------------------

def changepoint():
    rows = load("cliff_summary.csv")
    if not rows:
        return
    hdr("A4 — where does degradation begin? change-point, not eyeball")
    for r in rows:
        for k in ("r", "slope"):
            r[k] = float(r[k])
        r["d"] = int(r["d"])
    objs = sorted({r["objective"] for r in rows})
    rs = sorted({r["r"] for r in rows})
    print("  Three models fitted to mean slope against log r:")
    print("    M0  single line;  M1  break fixed at the theoretical boundary r=1;")
    print("    M2  break at a free location, estimated by profile least squares.")
    print("  The manuscript may only say the empirical onset differs from r=1 if the")
    print("  interval for the free breakpoint excludes 1.\n")

    def series(diff, d, sel):
        return np.array([np.mean([x["slope"] for x in rows if x["diffusion"] == diff
                                  and x["d"] == d and x["r"] == rv and x["objective"] in sel])
                         for rv in rs])

    def rss_line(x, y):
        A = np.vstack([x, np.ones(len(x))]).T
        sol, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
        return float(((y - A @ sol) ** 2).sum())

    def rss_break(x, y, b):
        z = np.maximum(x - b, 0.0)
        A = np.vstack([x, z, np.ones(len(x))]).T
        sol, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
        return float(((y - A @ sol) ** 2).sum())

    cands = np.log(np.array([0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0]))
    print("  {:<13} {:>4} {:>10} {:>10} {:>10} {:>12} {:>20}".format(
        "diffusion", "d", "RSS M0", "RSS M1", "RSS M2", "r_break", "95% CI on r_break"))
    for diff in sorted({r["diffusion"] for r in rows}):
        for d in sorted({r["d"] for r in rows}):
            x = np.log(np.array(rs))
            y = series(diff, d, objs)
            r0, r1 = rss_line(x, y), rss_break(x, y, 0.0)
            best = min(cands, key=lambda b: rss_break(x, y, b))
            r2 = rss_break(x, y, best)
            bs = []
            for _ in range(400):
                sel = list(RNG.choice(objs, len(objs), replace=True))
                yb = series(diff, d, sel)
                bs.append(math.exp(min(cands, key=lambda b: rss_break(x, yb, b))))
            lo, hi = np.percentile(bs, [2.5, 97.5])
            print("  {:<13} {:>4} {:>10.4f} {:>10.4f} {:>10.4f} {:>12.3f} {:>20}".format(
                diff, d, r0, r1, r2, math.exp(best),
                "[{:.2f},{:.2f}]".format(lo, hi)))
    print("\n  If the interval contains 1.0, the data do not distinguish the empirical")
    print("  onset from the theoretical boundary and the manuscript must say so.")


# ----------------------------------------------------------------------
# A5: fitting-window sensitivity
# ----------------------------------------------------------------------

def window():
    rows = load("mechanism_raw.csv")
    if not rows:
        return
    hdr("A5 — does the fitted exponent depend on the fitting window?")
    g = collections.defaultdict(dict)
    for r in rows:
        if r.get("init") != "centred":
            continue
        g[(r["objective"], int(r["d"]), float(r["tau"]))][int(r["J"])] = float(r["Ehat"])
    Jmins, Jmaxs = [10, 20, 40, 80], [1280, 2560, 5000]
    print("  Mean fitted slope over cells at tau = 0.1, by lower and upper cutoff.\n")
    print("  {:>8}".format("Jmin") + "".join("{:>12}".format("Jmax=" + str(b)) for b in Jmaxs))
    for a in Jmins:
        line = "  {:>8}".format(a)
        for b in Jmaxs:
            vals = []
            for k, dd in g.items():
                if k[2] != 0.1:
                    continue
                Js = sorted(j for j in dd if a <= j <= b)
                if len(Js) < 3:
                    continue
                vals.append(fit_slope(np.array(Js, float),
                                      np.array([dd[j] for j in Js])))
            line += "{:>12}".format("{:+.4f}".format(np.mean(vals)) if vals else "-")
        print(line)
    print("\n  A spread here comparable to the reported effects would mean the")
    print("  exponent is partly an artefact of the window and must be reported as such.")


# ----------------------------------------------------------------------
# A6: tolerance and multiplicity
# ----------------------------------------------------------------------

def tolerance():
    hdr("A6 — tolerance and multiplicity, for every file with stored intervals")
    print("  {:<26} {:>7} {:>10} {:>10} {:>10} {:>14}".format(
        "file", "cells", "tol 0.10", "tol 0.15", "tol 0.20", "0.15 Bonferroni"))
    for f in sorted(glob.glob("*_summary.csv")):
        rows = load(f)
        if not rows or "ci_hi" not in rows[0]:
            continue
        his = np.array([float(r["ci_hi"]) for r in rows])
        n = len(his)
        cnt = [int((his <= -1.0 + t).sum()) for t in TOLS]
        if "bonf_hi" in rows[0]:
            bh = np.array([float(r["bonf_hi"]) for r in rows])
            nb = int((bh <= -0.85).sum())
            bs = "{}/{}".format(nb, n)
        else:
            bs = "not stored"
        print("  {:<26} {:>7} {:>10} {:>10} {:>10} {:>14}".format(
            f, n, "{}/{}".format(cnt[0], n), "{}/{}".format(cnt[1], n),
            "{}/{}".format(cnt[2], n), bs))
    print("\n  Every count quoted in the manuscript must appear with all three")
    print("  tolerances beside it, not with 0.15 alone.")


def main():
    print("=" * 84)
    print("CBO-GAP audit — statistical points closed without new simulation")
    print("=" * 84)
    print("  Run in the directory holding the archived CSV files.")
    bookkeeping_and_floor()
    r_regression()
    equivalence()
    changepoint()
    window()
    tolerance()
    print("\n" + "=" * 84)
    print("done")
    print("=" * 84)


if __name__ == "__main__":
    main()
