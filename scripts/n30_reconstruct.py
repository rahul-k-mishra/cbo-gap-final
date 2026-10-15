"""
n30_reconstruct.py  --  CBO-GAP: forensic reconstruction of the N30 numbers

WHAT THIS IS
------------
Ledger N30. The submitted manuscript reports numbers that no archived script
computes, and no round-1 log prints either (N30, searched in round1-zip,
N34). This script asks one question of each such number: does any
plausible specification, ENUMERATED BELOW BEFORE ANY RUN, reproduce it from
the archived data? It does not ask which specification is right.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-15; Rahul's instruction)
  R1  The enumeration below is complete and final. No specification is
      added, removed or changed after any output exists. A later idea is a
      new script with its own pre-registration, never an edit of this one.
  R2  No specification is tuned to match. Every specification in the
      enumeration is computed for every target it applies to, and every
      result is written to the output files.
  R3  MATCH RULE. A computed value x REPRODUCES a published value p, printed
      with k decimals, iff |x - p| <= 0.5 x 10^-k (half a unit in the last
      printed digit; the detcheck rule, half_ulp_of_string), plus 1e-12 for
      floating-point noise. For an interval, both endpoints must reproduce
      under the SAME specification. Worked examples: p "+0.054" allows
      [0.0535, 0.0545], so x 0.0542 reproduces and 0.0546 does not. p
      "-0.0091" allows [-0.00915, -0.00905].
  R4  OUTPUT. One line per published quantity: "REPRODUCED by <specs>" or
      "NOT REPRODUCED". If no specification reproduces a number, that is
      the finding, and it is reported as such.
  R5  SECONDARY, REPORTED BELOW THE R4 LINE AND NEVER REPLACING IT. A
      bootstrap interval can be reproduced exactly only with the original
      seed and draw order, which are unknown. So for each interval, a
      "family" is a specification with its seed and RNG scope left free.
      The family is CONSISTENT with the published interval iff each
      published endpoint lies within the [min, max] of that endpoint over
      the family's 7 seeds x its scopes. This says "this construction,
      under some seed, could give this"; it is not a reproduction. Also
      printed: the NEAREST specification, the one minimising the larger
      endpoint error.
  R6  POSITIVE CONTROL, a gate. Before anything is judged, the machinery
      must reproduce exactcal.py's own P-E2 output in
      round1-zip/cbo-gap/logs_exact_full.log (sha256 checked against
      round1-zip.sha256). The specification: URp-a, S-slope, W-full,
      unit order X, B 4000, seed 20260822, shared scope over tau_0 0.5,
      0.1, 0.01, absolute value, 2.5/97.5. All fifteen printed values must
      reproduce under R3 (4 decimals):
          tau 0.5   d=2 -1.0655  d=40 -1.0113  change 0.0542  [0.0132,0.0965]
          tau 0.1   d=2 -1.0629  d=40 -1.0037  change 0.0592  [0.0155,0.1031]
          tau 0.01  d=2 -1.1299  d=40 -0.8766  change 0.2533  [0.1985,0.3101]
      If any fails, the script prints PC FAIL and exits 3 without judging
      any target, because its reading of the data or its bootstrap
      mechanics would not be the archive's.

DATA (read-only; hashes checked against zenodo-v1.sha256)
  exactcal_real.csv     2160 realizations, 144 cells, E_J per J (Table 3,
                        7.3 regression, contrasts, separation).
  regimemap_D_real.csv  180 cells x 12 per-realization slopes; and
  regimemap_M_real.csv  240 cells x 12 (the 420 cells of tex 78).
  regimemap_summary.csv and regimemap_M_summary.csv (stored ci_lo, ci_hi).
  rmapj_real.csv        180 cells x 12, E_J per J (the D cells, refittable).
  Slopes of exactcal data are fitted with exactcal.fit_slope, the function
  that wrote them; rmapj data with regimemap.fit_slope, which rmapj
  imports (CLAUDE.md rule 4).

TARGETS (copied from manuscript/sn-article.tex; "label" is the window the
text attaches to each)
  T3U  Table 3 upper block (tex 368-371), label J >= 1/tau_0:
       tau 0.5 : d2 -1.066  d5 -1.001  d10 -1.041  d40 -1.011  change +0.054  [0.021,0.083]
       tau 0.1 : d2 -1.063  d5 -1.036  d10 -0.999  d40 -1.004  change +0.059  [0.005,0.126]
       tau 0.01: d2 -1.071  d5 -1.091  d10 -1.006  d40 -0.994  change +0.078  [0.003,0.199]
  T3M  Table 3 middle block (tex 373-375), label full grid:
       tau 0.5 : as T3U                                        change +0.054  [0.022,0.083]
       tau 0.1 : as T3U                                        change +0.059  [0.006,0.124]
       tau 0.01: d2 -1.130  d5 -1.048  d10 -0.968  d40 -0.877  change +0.253  [0.117,0.381]
  REGR 7.3 regression on J >= 1/tau_0 (tex 392): b_dtau +0.0073
       [-0.0091,+0.0227]; b_tau -0.0288 [-0.0754,+0.0208]; b_d +0.0069
       [-0.0025,+0.0160].
  REGF the same on the full grid: b_dtau +0.0305 [+0.0123,+0.0479].
  CON  pairwise contrasts on J >= 1/tau_0, "paired on the same twelve
       objective-law cells" (tex 394): 0.5 minus 0.1 -0.0050
       [-0.0701,+0.0545]; 0.5 minus 0.01 -0.0233 [-0.1482,+0.0567]; 0.1
       minus 0.01 -0.0182 [-0.1096,+0.0480].
  SEP  full grid: "the tightest target appeared to differ from the moderate
       ones by +0.1940 with [+0.0682,+0.3105]" (tex 394).
  SE   tex 78: bootstrap slope-SE over 420 cells, median 0.0260, IQR
       [0.0191, 0.0341].

THE ENUMERATION (complete; written before any execution)
  Definitions. A unit is an (objective, init) pair; there are 12. For a
  cell (unit, d, tau_0) under window W:
    S-curve  = exactcal.fit_slope on the 15-realization mean curve;
    S-slope  = mean of the 15 per-realization exactcal.fit_slope values.
  Table 3's per-d entry = the mean over the 12 units at (d, tau_0).
  c(tau)   = entry(d = 40) - entry(d = 2), the "change 2 -> 40" (sign as
             Table 3 prints it: positive = flatter at d = 40).

  E   estimand            S-curve, S-slope                                2
  W   fit window          W-full   all J in 10 ... 5000
                          W-ge     J >= 1/tau_0 (exact fraction arithmetic)
                          W-gt     J >  1/tau_0
                          W-20     J >= 20 (rmapj.py's refit window)
                          W-1250   J <= 1250 (regime.py Part A's cap)     5
  O   unit order          X  exactcal's loop order: ackley, rastrigin,
                             sphere, griewank, levy, rosenbrock; centred,
                             mix-0.1
                          A  alphabetical by (objective, init)            2
  U   bootstrap unit and pairing (a "group" is the set of values one cell
      group contributes: for a change, d = 40 then d = 2 at that tau_0):
      U12p   the 12 units resampled with replacement, ONE index vector per
             resample shared by every group (paired across d and tau_0).
             This is the Table 3 caption's unit.
      U12u-a the 12 units resampled independently per group, drawn within
             each resample in the canonical group order.
      U12u-b as U12u-a, groups drawn in reverse order.
      URp-a  pooled realizations: each group is the 180 per-realization
             slopes of its 12 cells, concatenated in unit order O, rows in
             file order, resampled independently per group, drawn in
             canonical order within each resample. This is exactcal P-E2's
             construction. Defined for S-slope only.
      URp-b  as URp-a, reverse group order.                               5
  B   resamples           400, 1000, 2000, 4000                           4
  S   seed                7, 11, 20260821, 20260822, 20260824, 20260827,
                          20260828: every bootstrap seed in the archived
                          analysis code (scripts' BOOT_SEED, audit, partm,
                          exactcal and reboot, finitej, rmapj, perjcal)   7
  G   RNG scope           fresh   numpy.random.default_rng(S) anew for
                                  each published quantity;
                          shared  one default_rng(S) consumed in printed
                                  order across a section: the three taus of
                                  a Table 3 block (0.5, 0.1, 0.01), or the
                                  three contrasts. For SEP and REG there is
                                  one draw sequence, so "single".        <=2
  Draw primitive: rng.integers(0, n, n) per group per resample, the call
  used by exactcal, perjcal, finitej, reboot and the per-cell boot_ci
  functions.
  L   interval level      L95 two-sided (2.5th, 97.5th percentiles)
                          L90 two-sided (5th, 95th), which also gives the
                              one-sided 95% bound                         2
  V   variant             change, contrast, separation: signed, or abs
                          (absolute value of the point and of every
                          resample, as exactcal P-E2)                     2
                          regression: response gamma-hat (tex 392) or
                          Delta = -1 - gamma-hat                          2
                          separation definition: S1 c(0.01) - c(0.1);
                          S2 c(0.01) - c(0.5); S3 c(0.01) - (c(0.5) +
                          c(0.1))/2. The text does not define it.         3
  Canonical group orders:
    change(tau)       [d40, d2] at tau
    contrast(t1, t2)  [(t1,d40), (t1,d2), (t2,d40), (t2,d2)]
    separation        [(0.5,d40), (0.5,d2), (0.1,d40), (0.1,d2),
                       (0.01,d40), (0.01,d2)]
    regression        the 12 (d, tau) cells, tau outer (0.5, 0.1, 0.01),
                      d inner (2, 5, 10, 40)
  Regression fit (tex 392): OLS of the 12 cell means on [1, log2 d,
  log10(1/tau_0), log2 d x log10(1/tau_0)]. With 12 units in every cell
  this gives the same coefficients as OLS on the 144 unit-level values.
  Point estimates depend only on E, W and V. Intervals depend on all of
  them. Per interval target: 80 (E, W, O, U) combinations (S-curve has no
  URp) x 4 B x 7 S x scopes x 2 L x the V variants.

  SE construction for 0.0260 (cells: the 180 Part D cells and the 240
  Part M cells; per-realization slopes as stored):
      SE-a  regimemap.boot_ci's own draw: for each cell, rng =
            default_rng(S); B resampled means, each np.mean(rng.choice(s,
            s.size, replace=True)); SE = np.std over the B means, ddof 0
            or 1.
      SE-b  sample SD of the 12 slopes / sqrt(12), ddof 0 or 1.
      SE-c  (ci_hi - ci_lo) / (2 z) from the stored summary files (400
            resamples, seed 7), z = 1.96 or 1.959963984540054.
      SE-d  D cells: realizations of rmapj_real.csv resampled, slope
            REFITTED on the resampled mean curve (regimemap.fit_slope;
            rng = default_rng(S) per cell, rng.integers per resample), SD
            ddof 0 or 1; M cells as SE-a. This is the construction tex 78
            describes, as far as the M files allow.
      B in {400, 1000, 2000, 4000}, S as above for SE-a and SE-d.
      Statistics: median, 25th and 75th percentiles (numpy default rule).

WHAT THE RESULT CAN INFORM
  - Whether each N30 number follows from the archived data under some
    enumerated specification, and which one: the window, the estimand and
    the unit the text should have stated.
  - Whether Table 3's labels (J >= 1/tau_0, full grid) match the window
    that reproduces its numbers.
WHAT IT CANNOT INFORM
  - What code was actually run in round 1. A match shows a specification
    that gives the number, not that it was the one used.
  - Anything about calprec v2 betas or the rerun.
  - NOT REPRODUCED does not show a number to be wrong. It shows that no
    enumerated specification gives it.

OUTPUT (new folder <outdir>/n30-<timestamp>/, every file opened "x")
  n30_points.csv     every point target x every point specification.
  n30_intervals.csv  every interval target x every specification x scope:
                     the endpoints of every L and V, and the matches.
  n30_se.csv         every SE specification: median, q25, q75, matches.
  n30_verdicts.csv   one row per published quantity: verdict, reproducing
                     specifications, consistent families, nearest.

HOW TO RUN (from the repository root, venv active)
    python scripts/n30_reconstruct.py --workers 2
  --round1 defaults to <repo>/round1-zip. Exit 0 when the verdicts are
  printed (whatever they are), 2 on a setup error, 3 on PC FAIL.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import csv
import math
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

import measlib as ml                                            # noqa: E402

ec = ml.ec
rm = ml.rm

FILES = ["exactcal.py", "regimemap.py", "reboot.py", "rmapj.py", "exactcal_real.csv",
         "regimemap_D_real.csv", "regimemap_M_real.csv", "regimemap_summary.csv",
         "regimemap_M_summary.csv", "rmapj_real.csv"]
EXO = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
INITS = ["centred", "mix-0.1"]
DIMS = [2, 5, 10, 40]
TAUS = ["0.5", "0.1", "0.01"]
WINDOWS = ["W-full", "W-ge", "W-gt", "W-20", "W-1250"]
ESTS = ["curve", "slope"]
ORDERS = ["X", "A"]
UTYPES = ["U12p", "U12u-a", "U12u-b", "URp-a", "URp-b"]
BLIST = [400, 1000, 2000, 4000]
SEEDS = [7, 11, 20260821, 20260822, 20260824, 20260827, 20260828]
CONTRASTS = [("0.5", "0.1"), ("0.5", "0.01"), ("0.1", "0.01")]
Z = [1.96, 1.959963984540054]

PUB_T3 = {
    "T3U": {"0.5": ["-1.066", "-1.001", "-1.041", "-1.011", "+0.054", "0.021", "0.083"],
            "0.1": ["-1.063", "-1.036", "-0.999", "-1.004", "+0.059", "0.005", "0.126"],
            "0.01": ["-1.071", "-1.091", "-1.006", "-0.994", "+0.078", "0.003", "0.199"]},
    "T3M": {"0.5": ["-1.066", "-1.001", "-1.041", "-1.011", "+0.054", "0.022", "0.083"],
            "0.1": ["-1.063", "-1.036", "-0.999", "-1.004", "+0.059", "0.006", "0.124"],
            "0.01": ["-1.130", "-1.048", "-0.968", "-0.877", "+0.253", "0.117", "0.381"]}}
LABEL = {"T3U": "W-ge", "T3M": "W-full", "REGR": "W-ge", "REGF": "W-full",
         "CON": "W-ge", "SEP": "W-full"}
PUB_REG = {"REGR": {"b_dtau": ("+0.0073", "-0.0091", "+0.0227"),
                    "b_tau": ("-0.0288", "-0.0754", "+0.0208"),
                    "b_d": ("+0.0069", "-0.0025", "+0.0160")},
           "REGF": {"b_dtau": ("+0.0305", "+0.0123", "+0.0479")}}
PUB_CON = {("0.5", "0.1"): ("-0.0050", "-0.0701", "+0.0545"),
           ("0.5", "0.01"): ("-0.0233", "-0.1482", "+0.0567"),
           ("0.1", "0.01"): ("-0.0182", "-0.1096", "+0.0480")}
PUB_SEP = ("+0.1940", "+0.0682", "+0.3105")
PUB_SE = {"median": "0.0260", "q25": "0.0191", "q75": "0.0341"}
PC_LOG = "cbo-gap/logs_exact_full.log"
PC = {"0.5": ("-1.0655", "-1.0113", "0.0542", "0.0132", "0.0965"),
      "0.1": ("-1.0629", "-1.0037", "0.0592", "0.0155", "0.1031"),
      "0.01": ("-1.1299", "-0.8766", "0.2533", "0.1985", "0.3101")}
COEF = ["a", "b_d", "b_tau", "b_dtau"]

G = {}


def matches(pub, x):
    return bool(np.isfinite(x)) and abs(x - float(pub)) <= ml.half_ulp_of_string(pub) + 1e-12


def window_J(w, tau):
    inv = 1 / Fraction(tau)
    if w == "W-full":
        return list(ml.J_LIST)
    if w == "W-ge":
        return [J for J in ml.J_LIST if J >= inv]
    if w == "W-gt":
        return [J for J in ml.J_LIST if J > inv]
    if w == "W-20":
        return [J for J in ml.J_LIST if J >= 20]
    if w == "W-1250":
        return [J for J in ml.J_LIST if J <= 1250]
    raise ValueError(w)


def unit_order(o):
    x = [(ob, it) for ob in EXO for it in INITS]
    return x if o == "X" else sorted(x)


def prepare(cells):
    """Per window: per-realization slopes and S-curve of every cell."""
    data = {}
    for w in WINDOWS:
        real, curve = {}, {}
        for (ob, d, it, t), c in cells.items():
            Js = window_J(w, t)
            cols = [ml.J_LIST.index(J) for J in Js]
            Ew = c["E"][:, cols]
            real[(ob, d, it, t)] = np.array([ec.fit_slope(Js, row) for row in Ew])
            curve[(ob, d, it, t)] = ec.fit_slope(Js, Ew.mean(axis=0))
        data[w] = {"real": real, "curve": curve}
    return data


def group_values(data, est, w, o, utype, groups):
    """For each (d, tau) group, the vector the bootstrap resamples."""
    units = unit_order(o)
    out = []
    for (d, t) in groups:
        if utype.startswith("URp"):
            out.append(np.concatenate([data[w]["real"][(ob, d, it, t)] for ob, it in units]))
        elif est == "curve":
            out.append(np.array([data[w]["curve"][(ob, d, it, t)] for ob, it in units]))
        else:
            out.append(np.array([float(np.mean(data[w]["real"][(ob, d, it, t)])) for ob, it in units]))
    return out


def design():
    X = []
    for t in TAUS:
        for d in DIMS:
            g = math.log10(1.0 / float(t))
            h = math.log2(d)
            X.append([1.0, h, g, h * g])
    return np.array(X)


XREG = design()


def stat_change(g):
    return g[0] - g[1]


def stat_contrast(g):
    return (g[0] - g[1]) - (g[2] - g[3])


def stat_sep(g):
    c5, c1, c01 = g[0] - g[1], g[2] - g[3], g[4] - g[5]
    return np.array([c01 - c1, c01 - c5, c01 - 0.5 * (c5 + c1)])


def stat_reg(g):
    return np.linalg.lstsq(XREG, np.asarray(g, dtype=np.float64), rcond=None)[0]


def run_boot(rng, vals, utype, B, stat):
    k = len(vals)
    order = list(range(k)) if not utype.endswith("-b") else list(range(k))[::-1]
    res = []
    for _ in range(B):
        if utype == "U12p":
            idx = rng.integers(0, 12, 12)
            g = [v[idx].mean() for v in vals]
        else:
            g = [0.0] * k
            for j in order:
                n = vals[j].size
                g[j] = vals[j][rng.integers(0, n, n)].mean()
        res.append(stat(g))
    return np.array(res)


def ends(v):
    return [ml.pct(v, q) for q in (2.5, 97.5, 5.0, 95.0)]


def init_worker(data):
    G["data"] = data


def fam_task(a):
    fam, est, w, o, utype, B, seed = a
    data = G["data"]
    rows = []
    if fam in ("T3", "CON"):
        items = ([(t, [(40, t), (2, t)], stat_change) for t in TAUS] if fam == "T3" else
                 [(c, [(40, c[0]), (2, c[0]), (40, c[1]), (2, c[1])], stat_contrast) for c in CONTRASTS])
        for scope in ("fresh", "shared"):
            shared = np.random.default_rng(seed)
            for key, groups, st in items:
                rng = shared if scope == "shared" else np.random.default_rng(seed)
                vals = group_values(data, est, w, o, utype, groups)
                v = run_boot(rng, vals, utype, B, st)
                pt = st([x.mean() for x in vals])
                rows.append({"key": key, "scope": scope, "signed": ends(v), "abs": ends(np.abs(v)),
                             "pt": pt})
    elif fam == "SEP":
        groups = [(40, "0.5"), (2, "0.5"), (40, "0.1"), (2, "0.1"), (40, "0.01"), (2, "0.01")]
        vals = group_values(data, est, w, o, utype, groups)
        v = run_boot(np.random.default_rng(seed), vals, utype, B, stat_sep)
        pt = stat_sep([x.mean() for x in vals])
        for j, nm in enumerate(("S1", "S2", "S3")):
            rows.append({"key": nm, "scope": "single", "signed": ends(v[:, j]),
                         "abs": ends(np.abs(v[:, j])), "pt": pt[j]})
    else:
        groups = [(d, t) for t in TAUS for d in DIMS]
        vals = group_values(data, est, w, o, utype, groups)
        v = run_boot(np.random.default_rng(seed), vals, utype, B, stat_reg)
        pt = stat_reg([x.mean() for x in vals])
        for j, nm in enumerate(COEF):
            rows.append({"key": nm, "scope": "single", "gamma": ends(v[:, j]),
                         "delta": ends((-1.0 - v[:, j]) if j == 0 else -v[:, j]), "pt": pt[j]})
    return {"spec": a, "rows": rows, "rss": ml.rss_mb()}


def se_task(a):
    kind, B, seed = a
    out = {}
    for ddof in (0, 1):
        out[ddof] = []
    for src in ("D", "M"):
        for key, s in G["slopes"][src]:
            if kind == "SE-d" and src == "D":
                E = G["rmapj"][key]
                R = E.shape[0]
                Jv = np.array(ml.J_LIST, dtype=np.float64)
                rng = np.random.default_rng(seed)
                bs = [rm.fit_slope(Jv, E[rng.integers(0, R, R)].mean(axis=0)) for _ in range(B)]
            else:
                ss = s[np.isfinite(s)]
                rng = np.random.default_rng(seed)
                bs = [float(np.mean(rng.choice(ss, ss.size, replace=True))) for _ in range(B)]
            bs = np.array(bs)
            bs = bs[np.isfinite(bs)]
            for ddof in (0, 1):
                out[ddof].append(float(np.std(bs, ddof=ddof)))
    return {"spec": a, "se": out, "rss": ml.rss_mb()}


def stats3(v):
    v = np.asarray(v, dtype=np.float64)
    return {"median": float(np.median(v)), "q25": float(np.percentile(v, 25)),
            "q75": float(np.percentile(v, 75))}


def sid(*parts):
    return "|".join(str(p) for p in parts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--round1", default=os.path.join(ml.ROOT, "round1-zip"))
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    if a.workers < 1:
        sys.stderr.write("setup error: --workers >= 1 required\n")
        return 2

    outdir = ml.new_outdir("n30")
    n_int = len(WINDOWS) * len(ORDERS) * 3 + len(WINDOWS) * len(ORDERS) * 5   # S-curve: no URp
    ok = ml.print_header(
        "CBO-GAP N30 -- forensic reconstruction of numbers with no archived code",
        0, a.workers,
        {"rules": "R1-R6 in the docstring, fixed before execution",
         "E": ESTS, "W": WINDOWS, "O": ORDERS, "U": UTYPES, "B": BLIST, "S": SEEDS,
         "G": "fresh / shared (T3, CON); single (SEP, REG)",
         "L": "L95 (2.5, 97.5), L90 (5, 95)",
         "V": "signed/abs (change, contrast, separation); gamma/delta (regression); S1/S2/S3",
         "(E,W,O,U) combos per interval target": n_int,
         "SE": "SE-a, SE-b, SE-c, SE-d over 180 D + 240 M cells; ddof 0/1; z 1.96/1.959963984540054",
         "match": "|x - p| <= half a unit in p's last printed digit (+1e-12)",
         "seeds note": "bootstrap seeds here are the archive's integer seeds, "
                       "numpy.random.default_rng(S); no SeedSequence keys"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing computed")
        return 2
    man = os.path.join(ml.ROOT, "round1-zip.sha256")
    want = None
    with open(man, newline="") as fh:
        for line in fh:
            h, n = line.strip().split(None, 1)
            if n.strip() == PC_LOG:
                want = h
    logp = os.path.join(a.round1, PC_LOG)
    if want is None or not os.path.isfile(logp) or ml.sha256_of(logp) != want:
        print("SETUP ERROR: {} missing or not equal to round1-zip.sha256".format(logp))
        return 2
    print("  positive-control source {}  sha256 ok".format(logp))

    cells = ml.load_exactcal()
    t0 = time.time()
    data = prepare(cells)
    print("  slopes prepared for {} windows in {:.1f} s".format(len(WINDOWS), time.time() - t0))

    # ------------------------------------------------------------ R6 positive control
    print("\n  R6 POSITIVE CONTROL: exactcal.py P-E2 as printed in {}".format(PC_LOG))
    rng = np.random.default_rng(20260822)
    pc_bad = 0
    for t in TAUS:
        vals = group_values(data, "slope", "W-full", "X", "URp-a", [(40, t), (2, t)])
        v = np.abs(run_boot(rng, vals, "URp-a", 4000, stat_change))
        lo, hi = np.percentile(v, [2.5, 97.5])
        got = (vals[1].mean(), vals[0].mean(), abs(vals[0].mean() - vals[1].mean()), lo, hi)
        okt = [matches(pv, gv) for pv, gv in zip(PC[t], got)]
        pc_bad += okt.count(False)
        print("    tau {:<5} d2 {:+.4f}  d40 {:+.4f}  change {:.4f}  [{:.4f},{:.4f}]   {}".format(
            t, got[0], got[1], got[2], got[3], got[4],
            "ok" if all(okt) else "FAIL vs log {}".format(PC[t])))
    if pc_bad:
        print("  PC FAIL: {} of 15 values not reproduced; nothing judged".format(pc_bad))
        return 3
    print("  PC PASS")
    sys.stdout.flush()

    # ------------------------------------------------------------ point estimates
    prow, verdict = [], {}

    def note(q, pub, spec, x, label_w=None, w=None):
        m = matches(pub, x)
        prow.append([q, pub, spec, ml.fmt(x), "yes" if m else "no",
                     "" if label_w is None else ("label" if w == label_w else "differs from label")])
        v = verdict.setdefault(q, {"pub": pub, "kind": "point", "rep": [], "near": None})
        if m:
            v["rep"].append(spec)
        err = abs(x - float(pub))
        if v["near"] is None or err < v["near"][1]:
            v["near"] = (spec, err, x)

    for est in ESTS:
        for w in WINDOWS:
            means = {}
            for t in TAUS:
                for d in DIMS:
                    means[(d, t)] = float(np.mean(group_values(data, est, w, "X", "U12p", [(d, t)])[0]))
            for blk in ("T3U", "T3M"):
                for t in TAUS:
                    for j, d in enumerate(DIMS):
                        note("{} tau={} d={}".format(blk, t, d), PUB_T3[blk][t][j], sid("E=" + est, "W=" + w),
                             means[(d, t)], LABEL[blk], w)
                    ch = means[(40, t)] - means[(2, t)]
                    for sg, x in (("signed", ch), ("abs", abs(ch))):
                        note("{} tau={} change".format(blk, t), PUB_T3[blk][t][4],
                             sid("E=" + est, "W=" + w, "V=" + sg), x, LABEL[blk], w)
            c = {t: means[(40, t)] - means[(2, t)] for t in TAUS}
            for (t1, t2), pub in PUB_CON.items():
                x = c[t1] - c[t2]
                for sg, xx in (("signed", x), ("abs", abs(x))):
                    note("CON {}-{}".format(t1, t2), pub[0], sid("E=" + est, "W=" + w, "V=" + sg), xx,
                         LABEL["CON"], w)
            seps = {"S1": c["0.01"] - c["0.1"], "S2": c["0.01"] - c["0.5"],
                    "S3": c["0.01"] - 0.5 * (c["0.5"] + c["0.1"])}
            for nm, x in seps.items():
                for sg, xx in (("signed", x), ("abs", abs(x))):
                    note("SEP", PUB_SEP[0], sid("E=" + est, "W=" + w, "def=" + nm, "V=" + sg), xx,
                         LABEL["SEP"], w)
            coefs = stat_reg([means[(d, t)] for t in TAUS for d in DIMS])
            for blk in ("REGR", "REGF"):
                for nm, pub in PUB_REG[blk].items():
                    j = COEF.index(nm)
                    for resp, x in (("gamma", coefs[j]), ("delta", -coefs[j])):
                        note("{} {}".format(blk, nm), pub[0], sid("E=" + est, "W=" + w, "resp=" + resp), x,
                             LABEL[blk], w)
    ml.write_csv(os.path.join(outdir, "n30_points.csv"),
                 ["quantity", "published", "spec", "computed", "reproduces", "window_vs_label"], prow)

    # ------------------------------------------------------------ intervals
    tasks = []
    for fam in ("T3", "CON", "SEP", "REG"):
        for est in ESTS:
            for w in WINDOWS:
                for o in ORDERS:
                    for u in UTYPES:
                        if est == "curve" and u.startswith("URp"):
                            continue
                        for B in BLIST:
                            for s in SEEDS:
                                tasks.append((fam, est, w, o, u, B, s))
    print("\n  interval tasks: {} (each a full bootstrap per quantity and scope)".format(len(tasks)))
    sys.stdout.flush()
    t1 = time.time()
    with Pool(processes=a.workers, initializer=init_worker, initargs=(data,)) as pool:
        res = pool.map(fam_task, tasks, chunksize=4)
    print("  interval bootstraps done in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        time.time() - t1, max(r["rss"] for r in res)))

    irow = []
    fams = {}

    def judge(q, pub_lo, pub_hi, specbase, s_, sc, w, label_w, variants):
        """variants: list of (vname, lo, hi). One CSV row per (q, spec, seed,
        scope) with every variant's endpoints and match flags."""
        v = verdict.setdefault(q, {"pub": "[{},{}]".format(pub_lo, pub_hi), "kind": "interval",
                                   "rep": [], "near": None})
        cells = []
        for vname, lo, hi in variants:
            fk = sid(specbase, vname)
            spec = sid(fk, "S={}".format(s_), "G=" + sc)
            m = matches(pub_lo, lo) and matches(pub_hi, hi)
            if m:
                v["rep"].append(spec)
            err = max(abs(lo - float(pub_lo)), abs(hi - float(pub_hi)))
            if np.isfinite(err) and (v["near"] is None or err < v["near"][1]):
                v["near"] = (spec, err, (lo, hi))
            fams.setdefault((q, fk), []).append((lo, hi))
            cells += [vname, ml.fmt(lo), ml.fmt(hi), "yes" if m else "no"]
        irow.append([q, "[{},{}]".format(pub_lo, pub_hi), specbase, s_, sc,
                     "label" if w == label_w else "differs from label"] + cells)

    LV = (("L95", 0, 1), ("L90", 2, 3))
    for r in res:
        fam, est, w, o, u, B, s_ = r["spec"]
        base = sid("E=" + est, "W=" + w, "O=" + o, "U=" + u, "B={}".format(B))
        for row in r["rows"]:
            sc = row["scope"]
            if fam in ("T3", "CON", "SEP"):
                variants = [("L={}|V={}".format(ln, sg), row[sg][i0], row[sg][i1])
                            for sg in ("signed", "abs") for ln, i0, i1 in LV]
            else:
                variants = [("L={}|resp={}".format(ln, rp), row[rp][i0], row[rp][i1])
                            for rp in ("gamma", "delta") for ln, i0, i1 in LV]
            if fam == "T3":
                t = row["key"]
                for blk in ("T3U", "T3M"):
                    pub = PUB_T3[blk][t]
                    judge("{} tau={} CI".format(blk, t), pub[5], pub[6], base, s_, sc, w,
                          LABEL[blk], variants)
            elif fam == "CON":
                pub = PUB_CON[row["key"]]
                judge("CON {}-{} CI".format(*row["key"]), pub[1], pub[2], base, s_, sc, w,
                      LABEL["CON"], variants)
            elif fam == "SEP":
                judge("SEP CI", PUB_SEP[1], PUB_SEP[2], sid(base, "def=" + row["key"]), s_, sc, w,
                      LABEL["SEP"], variants)
            else:
                for blk in ("REGR", "REGF"):
                    if row["key"] not in PUB_REG[blk]:
                        continue
                    pub = PUB_REG[blk][row["key"]]
                    judge("{} {} CI".format(blk, row["key"]), pub[1], pub[2], base, s_, sc, w,
                          LABEL[blk], variants)
    vcols = []
    for j in range(4):
        vcols += ["variant{}".format(j + 1), "lo{}".format(j + 1), "hi{}".format(j + 1),
                  "reproduces{}".format(j + 1)]
    ml.write_csv(os.path.join(outdir, "n30_intervals.csv"),
                 ["quantity", "published", "spec", "seed", "scope", "window_vs_label"] + vcols, irow)

    # ------------------------------------------------------------ SE (0.0260)
    rd = ml.load_regimemap("regimemap_D_real.csv")
    rmm = ml.load_regimemap("regimemap_M_real.csv")
    rj = ml.load_rmapj()
    slopes = {"D": [(k, c["slope"]) for k, c in rd.items()],
              "M": [(k, c["slope"]) for k, c in rmm.items()]}
    rjE = {}
    for (dif, ob, d, r), c in rj.items():
        rjE[(dif, ob, d, r, "0.1")] = c["E"]
    missing = [k for k, _ in slopes["D"] if k not in rjE]
    if missing:
        print("SETUP ERROR: {} Part D cells have no rmapj counterpart, e.g. {}".format(len(missing), missing[0]))
        return 2
    G["slopes"] = slopes
    G["rmapj"] = rjE
    se_rows = []

    def se_note(spec, vals):
        st = stats3(vals)
        ms = {k: matches(PUB_SE[k], st[k]) for k in PUB_SE}
        se_rows.append([spec, len(vals), ml.fmt(st["median"]), ml.fmt(st["q25"]), ml.fmt(st["q75"]),
                        "yes" if ms["median"] else "no", "yes" if ms["q25"] else "no",
                        "yes" if ms["q75"] else "no"])
        for k in PUB_SE:
            q = "SE {}".format(k)
            v = verdict.setdefault(q, {"pub": PUB_SE[k], "kind": "se", "rep": [], "near": None})
            if ms[k]:
                v["rep"].append(spec)
            err = abs(st[k] - float(PUB_SE[k]))
            if v["near"] is None or err < v["near"][1]:
                v["near"] = (spec, err, st[k])
        q = "SE IQR"
        v = verdict.setdefault(q, {"pub": "[{},{}]".format(PUB_SE["q25"], PUB_SE["q75"]), "kind": "se",
                                   "rep": [], "near": None})
        if ms["q25"] and ms["q75"]:
            v["rep"].append(spec)
        return st

    for ddof in (0, 1):
        vals = [float(np.std(s[np.isfinite(s)], ddof=ddof) / math.sqrt(np.isfinite(s).sum()))
                for src in ("D", "M") for _, s in slopes[src]]
        se_note(sid("SE-b", "ddof={}".format(ddof)), vals)
    for z in Z:
        vals = []
        for fn in ("regimemap_summary.csv", "regimemap_M_summary.csv"):
            with open(os.path.join(ml.ARCH, fn), newline="") as fh:
                for x in csv.DictReader(fh):
                    vals.append((float(x["ci_hi"]) - float(x["ci_lo"])) / (2.0 * z))
        se_note(sid("SE-c", "z={}".format(z), "n={}".format(len(vals))), vals)
    se_tasks = [(k, B, s) for k in ("SE-a", "SE-d") for B in BLIST for s in SEEDS]
    t2 = time.time()
    with Pool(processes=a.workers, initializer=init_worker, initargs=(data,)) as pool:
        G_pass = {"slopes": slopes, "rmapj": rjE}
        se_res = pool.map(se_task_wrap, [(t, G_pass) for t in se_tasks], chunksize=1)
    print("  SE bootstraps done in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        time.time() - t2, max(r["rss"] for r in se_res)))
    se_fams = {}
    for r in se_res:
        k, B, s = r["spec"]
        for ddof in (0, 1):
            fk = sid(k, "B={}".format(B), "ddof={}".format(ddof))
            st = se_note(sid(fk, "S={}".format(s)), r["se"][ddof])
            se_fams.setdefault(fk, []).append(st)
    ml.write_csv(os.path.join(outdir, "n30_se.csv"),
                 ["spec", "cells", "median", "q25", "q75", "median_reproduces", "q25_reproduces",
                  "q75_reproduces"], se_rows)

    # ------------------------------------------------------------ verdicts
    print("\n" + "=" * 88)
    print("VERDICTS  (R4: REPRODUCED or NOT REPRODUCED; R5 lines are secondary)")
    print("=" * 88)
    vrows = []
    order = sorted(verdict)
    for q in order:
        v = verdict[q]
        cons = []
        if v["kind"] == "interval":
            pl, ph = v["pub"].strip("[]").split(",")
            for (qq, fk), lst in fams.items():
                if qq != q:
                    continue
                los = [x[0] for x in lst]
                his = [x[1] for x in lst]
                if min(los) <= float(pl) <= max(los) and min(his) <= float(ph) <= max(his):
                    cons.append(fk)
        elif v["kind"] == "se" and q != "SE IQR":
            key = q.split()[1]
            for fk, lst in se_fams.items():
                vals = [x[key] for x in lst]
                if min(vals) <= float(v["pub"]) <= max(vals):
                    cons.append(fk)
        head = "REPRODUCED by {} spec(s)".format(len(v["rep"])) if v["rep"] else "NOT REPRODUCED"
        print("\n  {:<26} published {:<20} {}".format(q, v["pub"], head))
        for spec in v["rep"]:
            print("      reproduced by  {}".format(spec))
        if v["kind"] != "point" and q != "SE IQR":
            print("      R5 consistent families: {}".format(len(cons)))
            for fk in cons:
                print("        {}".format(fk))
        if v["near"] is not None:
            nv = v["near"][2]
            nvs = ("[{:+.4f},{:+.4f}]".format(nv[0], nv[1]) if isinstance(nv, tuple) else "{:+.5f}".format(nv))
            print("      nearest: {}  value {}  max error {:.5f}".format(v["near"][0], nvs, v["near"][1]))
        vrows.append([q, v["pub"], "REPRODUCED" if v["rep"] else "NOT REPRODUCED", len(v["rep"]),
                      " ; ".join(v["rep"]), len(cons), " ; ".join(cons),
                      v["near"][0] if v["near"] else "", ml.fmt(v["near"][1]) if v["near"] else ""])
    ml.write_csv(os.path.join(outdir, "n30_verdicts.csv"),
                 ["quantity", "published", "verdict", "n_reproducing", "reproducing_specs",
                  "n_consistent_families", "consistent_families", "nearest_spec", "nearest_max_error"],
                 vrows)

    print("\n" + "=" * 88)
    print("ONE LINE PER PUBLISHED QUANTITY")
    print("=" * 88)
    for q in order:
        v = verdict[q]
        if v["rep"]:
            print("  {:<26} {:<20} REPRODUCED by {}".format(q, v["pub"], v["rep"][0] +
                  ("" if len(v["rep"]) == 1 else "  (+{} more, see above)".format(len(v["rep"]) - 1))))
        else:
            print("  {:<26} {:<20} NOT REPRODUCED".format(q, v["pub"]))
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


def se_task_wrap(arg):
    t, gp = arg
    G["slopes"] = gp["slopes"]
    G["rmapj"] = gp["rmapj"]
    return se_task(t)


if __name__ == "__main__":
    sys.exit(main())
