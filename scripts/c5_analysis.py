"""
c5_analysis.py  --  CBO-GAP: the readings of C5 (the window extension) and of
C6's second reading (the archived window at the larger reference), on the
fetched c5run folders and the committed 50000 rerun folders  (ledger N45,
"C5 DESIGN", readings fixed 2026-11-01 before any C5 run)

LAPTOP. Reads only; WRITES NOTHING. Every number it prints is a reading of
committed run folders or of its own synthetic null fixture.

WHAT IT DOES, IN PLAIN LANGUAGE
-------------------------------
For each of the 288 cells it fits every realization's slope of log E_J on
log J over three windows of the 4000000 run and the archived window of the
50000 run, averages them (the S-slope), and resamples the realizations to
put intervals on four quantities: the slope on J 5000 to 400000, whether it
is flatter than -1, how it differs from the slope on J 10 to 5000 of the same
realizations, and how the J 10 to 5000 slope at J_inf 4000000 differs from
the J 10 to 5000 slope of the cell's 50000 run. Before any of that it runs a
null fixture: synthetic cells where nothing differs, put through the same
code, to measure how often each rule fires by chance at 15 realizations. A
rule that fires too often by chance is not used as a verdict. A fitted slope
over a finite window is a description of that window, never a rate, and a
difference not found is never an equivalence (CLAUDE.md rule 10).

INPUTS (each folder read only after its sha256.txt verifies; exit 2 otherwise)
  --c5 DIR, repeated: every fetched c5run shard folder, every attempt
      (attempts that stopped at exit 5 hold complete rows). Each holds one
      c5run-run-*/c5run_params.csv with mode run, kind 95, one common
      nshards and one common script sha256, and one c5run_real.csv. A task
      complete in two folders, or a complete task that is not one of the
      4320 c5run would run, is exit 2. Fewer than 4320 complete: exit 7,
      nothing computed (A1).
  --rerun DIR, repeated: the rerun folders holding the CONC and TAU8 cells
      at J_inf 50000 (rerun-cal-s0of2 and -s1of2). Their rows with owner
      CONC or TAU8 and end ok: exactly 15 per cell, 288 cells; each row's
      beta equals the c5run beta of its cell (B2). Otherwise exit 2.
  --sizetest-log FILE: logs/sizetest-analyse-20261031.log; its per-cell
      lines give each cell's class (affected, control; any other cell:
      neither), used for one descriptive listing only.
  c5run's inputs (--timing, --beta-table, --rerun-plan, defaults the
  committed ones) rebuild the 4320 task ids, keys and betas, with B1.

ESTIMATOR (rerun_analysis items 0 to 3, unchanged)
  Slope of a realization on a window: regimemap.fit_slope (imported), with
  every E on the window finite and > 0, otherwise the realization is
  dropped from that cell and named; more than one dropped flags the cell.
  At 4000000 a realization is kept iff it is valid on all 17 J, so all
  three windows use the same realizations. S-slope = their mean.
  B = 10000 resamples: indices default_rng(SeedSequence(boot key))
  .integers(0, n, size=(B, n)), n the kept count; the 4000000 cell's key
  is c5run's (kind 96), the 50000 cell's is the rerun row's boot_key.
  Windows: W-arch J 10 to 5000 (10 points), W-hi J 5000 to 400000 (8),
  W-ext all 17. Percentiles by numpy.percentile (linear).

INTERVALS: REVISED 2026-11-01, BEFORE ANY C5 RUN, ON THE NULL FIXTURE
  N45 fixed percentile-bootstrap intervals (rerun_analysis item 1). The
  null fixture below, run on synthetic cells while this script was being
  checked, showed the paired and two-sample percentile intervals at n = 15
  firing above 0.10 at one noise level, so by N45's own rule D-win and
  D-ref could not have been verdicts. The verdicts therefore use Student t
  intervals on the per-realization slopes, which are exact for normal
  slopes and carry the n - 1 degrees of freedom the percentile bootstrap
  ignores; the percentile bootstrap intervals are still computed and
  printed beside them (the rows' convention), with their own null rates,
  and decide nothing. Ledger N45 records the revision.
  t quantiles: the Student t CDF by Simpson integration of its density
  (math.lgamma), inverted by bisection. Worked example: t(0.975, 14) =
  2.1448, t(0.95, 14) = 1.7613.

READINGS (fixed in N45 2026-11-01, intervals as revised above; NULL RATE
nominal 0.05 for each). s_r is realization r's slope, n the kept count,
m and sd the mean and sample SD (ddof 1) of what the reading averages.
  R1a  S(W-hi) = m of s_r on W-hi; 95% t interval m +- t(0.975, n-1) sd /
       sqrt(n).
  R1b  PERSISTS iff m - t(0.95, n-1) sd / sqrt(n) > -1 (one-sided 95%
       lower bound above -1); otherwise "lower bound at or below -1".
       Worked example: m -0.90, sd 0.15, n 15: bound -0.90 - 1.7613 x
       0.0387 = -0.968: PERSISTS. m -0.95: -1.018: not.
  R1c  "upper bound <= -1: yes" iff m + t(0.95, n-1) sd / sqrt(n) <= -1.
  R1d  D-win: the paired differences s_r(W-hi) - s_r(W-arch); 95% t
       interval; DIFFERENCE iff it excludes 0, else "95% interval contains
       0". Worked example: m -0.050, sd 0.06, n 15: half-width 2.1448 x
       0.0155 = 0.0332, [-0.083, -0.017]: DIFFERENCE.
  D-ref S(W-arch, 4000000) - S(W-arch, 50000): Welch's interval, SE =
       sqrt(sd1^2/n1 + sd2^2/n2), df by Welch-Satterthwaite; DIFFERENCE
       rule as R1d.
  W-ext's S-slope is printed with its interval, no verdict.
  Beside every interval: the percentile-bootstrap interval (B resamples,
  as below), labelled "boot".
  POOLED (clarified 2026-11-01 while writing this script, before any C5
  run: N45's "per (row, tau_0)" with units (objective, law) / objective
  leaves d open): PRIMARY per (row, d, tau_0), units (objective, law) in
  CONC-X (12) and objective in TAU8-X (6), as rerun_analysis pools;
  SECONDARY per (row, tau_0), units (objective, law, d) / (objective, d).
  Pooled = the unweighted mean of the units' estimates y_i, with v_i =
  se_i^2 (the unit's t standard error squared), SE = sqrt(sum v_i) / k
  and the normal 95% interval; rerun_analysis item 6 heterogeneity (s2,
  sd_units, tau2 truncated at 0, Q, I2) from y_i and v_i; DIFFERENCE rule
  only;
  no PERSISTS and no equivalence on a pooled figure. Worked example (item
  6's): y = -1.00, -0.95, -0.90, v_i 0.0009 each: s2 0.0025, tau2 0.0016,
  Q 5.56, I2 0.64, pooled -0.95.

NULL FIXTURE AND THE RULE IT FEEDS (N40 commitment; run first, every time)
  Synthetic cells, nothing read from any run: per cell 15 realizations,
  log E_J = a_r + (-1 + delta_r) log J + eps_rJ on the 17 J of W-ext, a_r ~
  N(0, 1), delta_r ~ N(0, s), eps ~ N(0, e), at four levels (s, e) =
  (0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 0.30); NF = 400 cells
  per level; for D-ref a second independent set of 15 on W-arch. True
  S = -1 on every window, no curvature, no difference: every rejection is
  a false one. Seeds SeedSequence((20261101, 99, level, cell, set)), kind
  99 used by no other script. Printed per criterion and level: the
  rejection rate (Monte Carlo SE about 0.011 at 0.05 with NF 400).
  The t-based criteria decide; the bootstrap versions' rates are printed
  as well, for the record. Pooled DIFFERENCE is measured too: per level,
  NF / 6 pooled groups of 6 null cells.
  RULE (fixed now): r = a criterion's largest rate over the four levels.
  r > 0.10: the criterion is NOT USED as a verdict; its intervals are
  printed and its verdict column reads "not used (null rate r)". 0.05 < r
  <= 0.10: used, with "null rate r" beside every verdict. r <= 0.05: used.
  The pooled DIFFERENCE rule uses its own measured rate (P-win, P-ref).
  Worked example: R1b rates 0.048, 0.061, 0.072, 0.083: r 0.083, used
  with "null rate 0.083".

HEADLINE COUNTS
  For R1b, R1c, R1d and D-ref: the number of the 288 cells meeting the
  criterion, the number expected at rate r (288 x r), and the binomial
  upper tail P(X >= observed | 288, r), each criterion's r its own. No
  multiplicity adjustment; every cell is printed. Worked example: 31
  observed at r 0.06: expected 17.3, upper tail printed.

OUTPUT: per cell (row, module, objective, d, law, tau_0, sizetest class,
  kept n): S(W-arch), S(W-hi), S(W-ext) with intervals; R1b, R1c, R1d,
  D-ref with their verdicts; then the pooled tables, the class listing of
  D-ref, the headline counts, and the NULL RATE lines.

EXIT CODES  0 printed; 2 an input problem; 7 C5 incomplete (nothing
  computed). --null-only runs the null fixture alone (exit 0).

HOW TO RUN (repository root)
    python -B scripts/c5_analysis.py --null-only
    python -B scripts/c5_analysis.py --c5 runs/A --c5 runs/B ... \
        --rerun runs/rerun-cal-s0of2-a1-kaggle-20261025-003238 \
        --rerun runs/rerun-cal-s1of2-a1-kaggle-20261025-050238 \
        --sizetest-log logs/sizetest-analyse-20261031.log --workers 4
Python 3.8 to 3.13, NumPy only.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import io                                                       # noqa: E402
import json                                                     # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import re                                                       # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import c5run as X                                               # noqa: E402

JP, cp, rl, Stop, say, hdr = X.JP, X.cp, X.rl, X.Stop, X.say, X.hdr
fit_slope = cp.MODS["regimemap"].fit_slope

B = 10000
JL = list(X.JLIST)
W_ARCH = [J for J in JL if J <= 5000]
W_HI = [J for J in JL if J >= 5000]
W_EXT = list(JL)
J10 = list(cp.JGRIDS["J10"])
LEVELS = [(0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 0.30)]
NF = 400
NULL_SEED = (20261101, 99)
CRITS = ("R1b", "R1c", "R1d", "D-ref")
BOOTS = ("bR1b", "bR1c", "bR1d", "bD-ref")
POOLS = ("P-win", "P-ref")


def _tpdf(x, nu):
    return math.exp(math.lgamma((nu + 1) / 2.0) - math.lgamma(nu / 2.0)) / math.sqrt(nu * math.pi) * \
        (1.0 + x * x / nu) ** (-(nu + 1) / 2.0)


def tcdf(x, nu):
    if x < 0:
        return 1.0 - tcdf(-x, nu)
    m = 2000
    h = x / m
    s = _tpdf(0.0, nu) + _tpdf(x, nu)
    for i in range(1, m):
        s += (4 if i % 2 else 2) * _tpdf(i * h, nu)
    return 0.5 + s * h / 3.0


def tq(p, nu):
    """Quantile of Student t with nu (> 0, real) degrees of freedom, p in (0.5, 1)."""
    lo, hi = 0.0, 1.0
    while tcdf(hi, nu) < p:
        hi *= 2.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if tcdf(mid, nu) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


_TQ = {}


def tqc(p, nu):
    k = (p, round(nu, 6))
    if k not in _TQ:
        _TQ[k] = tq(p, nu)
    return _TQ[k]


def tstat(v):
    v = np.asarray(v, dtype=float)
    n = len(v)
    return float(v.mean()), float(v.std(ddof=1)) / math.sqrt(n), n


# ----------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------

def slopes(E, win):
    """E: array (n, len(JL)) on JL; per-realization slopes on win."""
    idx = [JL.index(J) for J in win]
    Jw = np.array(win, dtype=float)
    return np.array([fit_slope(Jw, E[i, idx]) for i in range(E.shape[0])])


def idx_of(key, n):
    return np.random.default_rng(np.random.SeedSequence(list(key))).integers(0, n, size=(B, n))


def pct(v, q):
    return float(np.percentile(v, q))


def diff_verdict(res):
    lo, hi = pct(res, 2.5), pct(res, 97.5)
    return (lo, hi), (lo > 0 or hi < 0)


def cell_stats(E4, key4, E50, key50):
    """Readings of one cell. E4: (n4, 17) at 4000000; E50: (n50, 10) on J10."""
    s_arch, s_hi, s_ext = slopes(E4, W_ARCH), slopes(E4, W_HI), slopes(E4, W_EXT)
    I = idx_of(key4, E4.shape[0])
    r_arch, r_hi, r_ext = s_arch[I].mean(axis=1), s_hi[I].mean(axis=1), s_ext[I].mean(axis=1)
    s50 = np.array([fit_slope(np.array(J10, dtype=float), E50[i]) for i in range(E50.shape[0])])
    I50 = idx_of(key50, E50.shape[0])
    r50 = s50[I50].mean(axis=1)
    dwin = r_hi - r_arch
    dref = r_arch - r50
    out = {"S_arch": float(s_arch.mean()), "S_hi": float(s_hi.mean()), "S_ext": float(s_ext.mean()),
           "S_50": float(s50.mean()), "b_arch": (pct(r_arch, 2.5), pct(r_arch, 97.5)),
           "b_hi": (pct(r_hi, 2.5), pct(r_hi, 97.5)), "b_ext": (pct(r_ext, 2.5), pct(r_ext, 97.5)),
           "D_win": float(s_hi.mean() - s_arch.mean()), "D_ref": float(s_arch.mean() - s50.mean())}
    out["bR1b"] = pct(r_hi, 5) > -1.0
    out["bR1c"] = pct(r_hi, 95) <= -1.0
    out["b_dwin"], out["bR1d"] = diff_verdict(dwin)
    out["b_dref"], out["bD-ref"] = diff_verdict(dref)
    # the verdicts: Student t
    for nm, v in (("arch", s_arch), ("hi", s_hi), ("ext", s_ext)):
        m, se, n = tstat(v)
        h = tqc(0.975, n - 1) * se
        out["ci_" + nm] = (m - h, m + h)
        out["se_" + nm] = se
    m, se, n = tstat(s_hi)
    out["R1b"] = m - tqc(0.95, n - 1) * se > -1.0
    out["R1c"] = m + tqc(0.95, n - 1) * se <= -1.0
    m, se, n = tstat(s_hi - s_arch)
    h = tqc(0.975, n - 1) * se
    out["ci_dwin"], out["se_dwin"] = (m - h, m + h), se
    out["R1d"] = (m - h > 0) or (m + h < 0)
    n1, n2 = len(s_arch), len(s50)
    v1, v2 = float(np.var(s_arch, ddof=1)) / n1, float(np.var(s50, ddof=1)) / n2
    se = math.sqrt(v1 + v2)
    df = (v1 + v2) ** 2 / (v1 ** 2 / (n1 - 1) + v2 ** 2 / (n2 - 1)) if v1 + v2 > 0 else float(n1 + n2 - 2)
    h = tqc(0.975, df) * se
    dm = out["D_ref"]
    out["ci_dref"], out["se_dref"] = (dm - h, dm + h), se
    out["D-ref"] = (dm - h > 0) or (dm + h < 0)
    out["res"] = {"hi": r_hi, "dwin": dwin, "dref": dref}
    return out


def pool(ys, ses):
    """Over units (y_i, se_i): (estimate, ci, DIFFERENCE, k, sd_units, tau2, I2 or reason). Normal interval
    on SE = sqrt(sum se_i^2) / k; item 6 heterogeneity with v_i = se_i^2."""
    y = np.array(ys, dtype=float)
    k = len(y)
    v = np.array(ses, dtype=float) ** 2
    s2 = float(np.var(y, ddof=1)) if k > 1 else float("nan")
    vbar = float(v.mean())
    tau2 = max(0.0, s2 - vbar) if k > 1 else float("nan")
    if k < 2 or np.any(v == 0):
        i2 = "undefined (k < 2 or a zero v_i)"
    else:
        yw = float(np.sum(y / v) / np.sum(1.0 / v))
        Q = float(np.sum((y - yw) ** 2 / v))
        i2 = "undefined (Q = 0)" if Q == 0 else "{:.2f}".format(max(0.0, (Q - (k - 1)) / Q))
    se = math.sqrt(float(v.sum())) / k
    m = float(y.mean())
    ci = (m - 1.959964 * se, m + 1.959964 * se)
    dif = ci[0] > 0 or ci[1] < 0
    return m, ci, dif, k, (math.sqrt(s2) if k > 1 else float("nan")), tau2, i2


def binom_tail(n, p, x):
    if x <= 0:
        return 1.0
    return float(sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(x, n + 1)))


# ----------------------------------------------------------------------
# the null fixture
# ----------------------------------------------------------------------

def null_cell(args):
    lv, c = args
    s, e = LEVELS[lv]
    g = np.random.default_rng(np.random.SeedSequence(list(NULL_SEED) + [lv, c, 0]))
    logJ = np.log(np.array(JL, dtype=float))
    a = g.normal(0, 1, 15)[:, None]
    dl = g.normal(0, s, 15)[:, None]
    E4 = np.exp(a + (-1.0 + dl) * logJ[None, :] + g.normal(0, e, (15, len(JL))))
    g2 = np.random.default_rng(np.random.SeedSequence(list(NULL_SEED) + [lv, c, 1]))
    lJ10 = np.log(np.array(J10, dtype=float))
    E50 = np.exp(g2.normal(0, 1, 15)[:, None] + (-1.0 + g2.normal(0, s, 15)[:, None]) * lJ10[None, :]
                 + g2.normal(0, e, (15, len(J10))))
    st = cell_stats(E4, list(NULL_SEED) + [lv, c, 2], E50, list(NULL_SEED) + [lv, c, 3])
    return lv, c, dict((k, bool(st[k])) for k in CRITS + BOOTS), (st["D_win"], st["se_dwin"], st["D_ref"],
                                                                    st["se_dref"])


def null_fixture(workers):
    hdr("NULL FIXTURE  synthetic cells with nothing to find (N40 commitment): rejection rate per criterion")
    say("  per cell 15 realizations, log E_J = a + (-1 + delta) log J + eps; true S = -1 everywhere, no curvature,")
    say("  no difference; {} cells per level; B {}; every rejection below is a false one".format(NF, B))
    pool_ = multiprocessing.Pool(workers)
    try:
        got = pool_.map(null_cell, [(lv, c) for lv in range(len(LEVELS)) for c in range(NF)], chunksize=8)
    finally:
        pool_.close()
        pool_.join()
    rates = dict((k, []) for k in CRITS + BOOTS + POOLS)
    say("  {:<16} {}".format("level", "  ".join("{:>7}".format(k) for k in CRITS + POOLS + BOOTS)))
    for lv, (s, e) in enumerate(LEVELS):
        row = []
        for k in CRITS + BOOTS:
            rates[k].append(sum(1 for (l2, _c, d, _p) in got if l2 == lv and d[k]) / float(NF))
        mine = sorted([(c, p) for (l2, c, _d, p) in got if l2 == lv])
        for k, j in (("P-win", 0), ("P-ref", 2)):
            groups = [mine[i:i + 6] for i in range(0, len(mine) - 5, 6)]
            hits = sum(1 for g in groups if pool([p[j] for _c, p in g], [p[j + 1] for _c, p in g])[2])
            rates[k].append(hits / float(len(groups)))
        say("  s {:.2f} e {:.2f}  {}".format(s, e, "  ".join("{:>7.3f}".format(rates[k][-1])
                                                                for k in CRITS + POOLS + BOOTS)))
    use = {}
    for k in BOOTS:
        say("  bootstrap {:<7} largest over levels {:.3f} (printed only; decides nothing)".format(k, max(rates[k])))
    for k in CRITS + POOLS:
        r = max(rates[k])
        use[k] = (r, "NOT USED" if r > 0.10 else ("used, rate printed" if r > 0.05 else "used"))
        say("  NULL RATE {:<6} largest over levels {:.3f} (nominal 0.05): {}".format(k, r, use[k][1]))
    return use


# ----------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------

def read_c5(folders, want_tids):
    store, prm = {}, []
    for f in folders:
        rels = JP.verified(f)
        pp = [r for r in rels if os.path.basename(r) == X.PARAMS_CSV]
        rr = [r for r in rels if os.path.basename(r) == X.ROWS_CSV]
        if len(pp) != 1 or len(rr) != 1:
            raise Stop(2, "A0: {}: expected one {} and one {}".format(f, X.PARAMS_CSV, X.ROWS_CSV))
        pr = JP.read_kv(os.path.join(f, pp[0]))
        if pr.get("mode") != "run" or pr.get("kind") != str(X.KIND_RUN):
            raise Stop(2, "A0: {}: mode {} kind {}, expected run 95".format(f, pr.get("mode"), pr.get("kind")))
        prm.append(pr)
        n = 0
        with io.open(os.path.join(f, rr[0]), "r", newline="", encoding="utf-8") as fh:
            for x in csv.DictReader(fh):
                if x.get("end") != "ok":
                    continue
                if x["tid"] not in want_tids:
                    raise Stop(2, "A0: {}: task {} is not a C5 task".format(f, x["tid"]))
                if x["tid"] in store:
                    raise Stop(2, "A0: task {} complete in two folders".format(x["tid"]))
                store[x["tid"]] = x
                n += 1
        say("  read {}: shard {} of {}, {} complete".format(f, pr.get("shard"), pr.get("nshards"), n))
    for k in ("nshards", "script_sha256", "python", "numpy", "timing", "beta_table", "rerun_plan"):
        if len(set(p.get(k) for p in prm)) > 1:
            raise Stop(2, "A0: the folders differ in {}".format(k))
    if prm:
        say("  platform of every folder: python {} numpy {}; script sha256 {}".format(
            prm[0].get("python"), prm[0].get("numpy"), prm[0].get("script_sha256")))
    return store


def read_rerun(folders, betas):
    cells = {}
    for f in folders:
        rels = rl.verify_folder(f)
        for rel in rels:
            if os.path.basename(rel) != "rerun_real.csv":
                continue
            with io.open(os.path.join(f, rel), "r", newline="", encoding="utf-8") as fh:
                for x in csv.DictReader(fh):
                    if x["owner"] not in ("CONC", "TAU8") or x["end"] != "ok":
                        continue
                    c = (x["owner"], x["module"], x["objective"], int(x["d"]), x["law"], float(x["tau0"]))
                    if x["J_inf"] != "50000" or x["J_grid"] != "J10":
                        raise Stop(2, "B2: {} is not J_inf 50000 J10".format(x["tid"]))
                    if x["beta"] != betas.get(c):
                        raise Stop(2, "B2: {} beta {} differs from c5run's {}".format(x["tid"], x["beta"], betas.get(c)))
                    cells.setdefault(c, {})
                    if x["rep"] in cells[c]:
                        raise Stop(2, "B2: {} rep {} twice".format(c, x["rep"]))
                    cells[c][x["rep"]] = x
        say("  read {}".format(f))
    bad = [c for c in betas if len(cells.get(c, {})) != X.M]
    if bad or len(cells) != len(betas):
        raise Stop(2, "B2: {} cell(s) without exactly {} realizations at 50000, e.g. {}".format(
            len(bad), X.M, bad[:3]))
    say("  B2 PASS  {} cells x {} realizations at 50000, every beta equal to c5run's".format(len(cells), X.M))
    return cells


def read_classes(path):
    out = {}
    if not path:
        return out
    pat = re.compile(r"^  (CONC|TAU8)  (\w+)\|(\w+)\|(\d+)\|([\w.-]+)\|([\d.]+) .*\((affected|control)\)")
    with io.open(path, "r", encoding="utf-8") as fh:
        for ln in fh:
            m = pat.match(ln)
            if m:
                out[(m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), float(m.group(6)))] = m.group(7)
    say("  sizetest classes read: {} cells ({} affected, {} control)".format(
        len(out), sum(1 for v in out.values() if v == "affected"), sum(1 for v in out.values() if v == "control")))
    return out


def E_of_c5(rows):
    E = []
    drop = []
    for x in rows:
        ej = json.loads(x["E_json"])
        v = np.array([float(ej[str(J)]) for J in JL])
        if np.all(np.isfinite(v)) and np.all(v > 0):
            E.append(v)
        else:
            drop.append(x["seed_key"])
    return np.array(E), drop


def E_of_50(rows):
    E, drop = [], []
    for x in rows:
        v = np.array([float(x["E_{}".format(J)]) if x["E_{}".format(J)] != "" else float("nan") for J in J10])
        if np.all(np.isfinite(v)) and np.all(v > 0):
            E.append(v)
        else:
            drop.append(x["seed_key"])
    return np.array(E), drop


def one(args):
    c, E4, k4, E50, k50 = args
    return c, cell_stats(E4, k4, E50, k50)


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="C5 readings (writes nothing)")
    ap.add_argument("--c5", action="append", default=[])
    ap.add_argument("--rerun", action="append", default=[])
    ap.add_argument("--sizetest-log", default="")
    ap.add_argument("--timing", default=",".join(X.DEFAULT_TIMING))
    ap.add_argument("--beta-table", default=X.DEFAULT_BETA)
    ap.add_argument("--rerun-plan", default=X.DEFAULT_PLAN)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-mb", type=float, default=X.BUDGET_MB)
    ap.add_argument("--null-only", action="store_true")
    a = ap.parse_args()
    a.timing = [x for x in a.timing.split(",") if x]
    hdr("CBO-GAP c5_analysis  (ledger N45; readings fixed 2026-11-01)  --  reads only, writes nothing")
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    say("  script   sha256 {}".format(JP.sha256_of(os.path.abspath(__file__))))
    say("  c5run.py sha256 {}".format(JP.sha256_of(X.__file__)))
    say("  windows  W-arch {}  W-hi {}  W-ext {}".format(W_ARCH, W_HI, W_EXT))
    say("  B {}  null fixture levels {}  NF {}  seeds SeedSequence({} + (level, cell, set))".format(
        B, LEVELS, NF, NULL_SEED))
    use = null_fixture(a.workers)
    if a.null_only:
        hdr("c5_analysis.py --null-only done, exit 0  (nothing written)")
        return 0
    hdr("A0, A1, B1, B2  inputs")
    probe, betas, labels, wd = X.inputs(a)
    tasks = X.make_tasks(probe, betas, labels, wd, X.KIND_RUN)
    want = dict((t["tid"], t) for t in tasks)
    store = read_c5([os.path.abspath(x) for x in a.c5], want)
    say("  A1  complete C5 tasks {} of {}".format(len(store), len(want)))
    if len(store) != len(want):
        say("  A1  INCOMPLETE: nothing computed")
        return 7
    bmap = dict((c, betas[c]) for c in betas)
    r50 = read_rerun([os.path.abspath(x) for x in a.rerun], bmap)
    cls = read_classes(a.sizetest_log)
    jobs, drops = [], {}
    for c in sorted(betas, key=lambda z: (z[0], z[1], z[2], z[3], z[4], z[5])):
        ts = [t for t in tasks if t["cell5"] == c]
        E4, d4 = E_of_c5([store[t["tid"]] for t in ts])
        E50, d50 = E_of_50([r50[c][str(r)] for r in range(X.M)])
        k50 = [int(z) for z in r50[c]["0"]["boot_key"].split("-")]
        drops[c] = (d4, d50)
        jobs.append((c, E4, list(ts[0]["boot"]), E50, k50))
    pool_ = multiprocessing.Pool(a.workers)
    try:
        res = dict(pool_.map(one, jobs, chunksize=4))
    finally:
        pool_.close()
        pool_.join()

    def tag(k, v):
        r, u = use[k]
        if u == "NOT USED":
            return "not used (null rate {:.3f})".format(r)
        s = ("yes" if v else "no")
        return s + (" (null rate {:.3f})".format(r) if u.startswith("used, rate") else "")

    hdr("PER CELL  (S-slopes; 95% intervals; a fitted slope over a finite window, never a rate)")
    say("  row  module|objective|d|law|tau0  class  n4 n50 | S(W-arch) [t 95%] | S(W-hi) [t 95%] | S(W-ext) [t 95%] "
        "| PERSISTS | ub<=-1 | D-win [t 95%] DIFF | S50(W-arch) | D-ref [Welch 95%] DIFF")
    say("      then: boot  the percentile-bootstrap intervals of S(W-hi), D-win and D-ref (printed only)")
    for c in sorted(res, key=lambda z: (z[0], z[1], z[2], z[3], z[4], z[5])):
        st = res[c]
        d4, d50 = drops[c]
        flag = " FLAG" if len(d4) > 1 or len(d50) > 1 else ""
        say("  {}-X {}|{}|{}|{}|{!r}  {}  {} {}{} | {:+.4f} [{:+.4f}, {:+.4f}] | {:+.4f} [{:+.4f}, {:+.4f}] | "
            "{:+.4f} [{:+.4f}, {:+.4f}] | {} | {} | {:+.4f} [{:+.4f}, {:+.4f}] {} | {:+.4f} | {:+.4f} [{:+.4f}, "
            "{:+.4f}] {}".format(
                c[0], c[1], c[2], c[3], c[4], c[5], cls.get(c, "neither"), X.M - len(d4), X.M - len(d50), flag,
                st["S_arch"], st["ci_arch"][0], st["ci_arch"][1], st["S_hi"], st["ci_hi"][0], st["ci_hi"][1],
                st["S_ext"], st["ci_ext"][0], st["ci_ext"][1], tag("R1b", st["R1b"]), tag("R1c", st["R1c"]),
                st["D_win"], st["ci_dwin"][0], st["ci_dwin"][1], tag("R1d", st["R1d"]), st["S_50"], st["D_ref"],
                st["ci_dref"][0], st["ci_dref"][1], tag("D-ref", st["D-ref"])))
        say("      boot  S(W-hi) [{:+.4f}, {:+.4f}]  D-win [{:+.4f}, {:+.4f}]  D-ref [{:+.4f}, {:+.4f}]".format(
            st["b_hi"][0], st["b_hi"][1], st["b_dwin"][0], st["b_dwin"][1], st["b_dref"][0], st["b_dref"][1]))
        for kk in d4:
            say("      dropped at 4000000: {}".format(kk))
        for kk in d50:
            say("      dropped at 50000: {}".format(kk))

    def pooled(title, keyf):
        hdr(title)
        groups = {}
        for c, st in res.items():
            groups.setdefault(keyf(c), []).append(st)
        say("  group | k | S(W-hi) [95%] | D-win [95%] DIFF | D-ref [95%] DIFF | sd_units, tau2, I2 (D-ref)")
        for g in sorted(groups):
            sts = groups[g]
            hi = pool([s["S_hi"] for s in sts], [s["se_hi"] for s in sts])
            dw = pool([s["D_win"] for s in sts], [s["se_dwin"] for s in sts])
            dr = pool([s["D_ref"] for s in sts], [s["se_dref"] for s in sts])
            say("  {} | {} | {:+.4f} [{:+.4f}, {:+.4f}] | {:+.4f} [{:+.4f}, {:+.4f}] {} | {:+.4f} [{:+.4f}, {:+.4f}] "
                "{} | {:.4f}, {:.5f}, {}".format(
                    g, hi[3], hi[0], hi[1][0], hi[1][1], dw[0], dw[1][0], dw[1][1], tag("P-win", dw[2]),
                    dr[0], dr[1][0], dr[1][1], tag("P-ref", dr[2]), dr[4], dr[5], dr[6]))

    pooled("POOLED, PRIMARY: per (row, d, tau_0)", lambda c: "{}-X d {} tau0 {!r}".format(c[0], c[3], c[5]))
    pooled("POOLED, SECONDARY: per (row, tau_0), over d", lambda c: "{}-X tau0 {!r}".format(c[0], c[5]))

    hdr("D-ref BY SIZETEST CLASS  (a description; the classes are not matched, N40 qualification 2)")
    for k in ("affected", "control", "neither"):
        cs = [c for c in res if cls.get(c, "neither") == k]
        say("  {:<9} cells {:>3}   D-ref DIFFERENCE {:>3}".format(k, len(cs), sum(1 for c in cs if res[c]["D-ref"])))

    hdr("HEADLINE COUNTS  (288 cells; expected at each criterion's measured null rate; binomial upper tail)")
    n = len(res)
    for k in CRITS:
        obs = sum(1 for st in res.values() if st[k])
        r, u = use[k]
        say("  {:<6} observed {:>3}   expected {:>6.1f} at null rate {:.3f}   P(X >= {}) = {:.3g}   {}".format(
            k, obs, n * r, r, obs, binom_tail(n, r, obs), "NOT USED AS A VERDICT" if u == "NOT USED" else ""))
    for k in CRITS + POOLS:
        say("  NULL RATE {:<6} {:.3f}: {}".format(k, use[k][0], use[k][1]))
    hdr("c5_analysis.py done, exit 0  (nothing written)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
