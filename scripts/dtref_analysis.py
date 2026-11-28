"""
dtref_analysis.py  --  CBO-GAP: the pre-registered analysis of DTREF, the
time-step refinement check (ledger N46; criterion fixed 2026-11-03 in N46 and
in scripts/dtref.py, PRE-REGISTERED ANALYSIS; the details below that N46 left
open were fixed 2026-11-28, before any DTREF shard ran, and are recorded in
N46, DTREF ANALYSIS)

LAPTOP. Reads only; WRITES NOTHING. Every number it prints is a reading of
committed run folders or of its own synthetic fixtures.

WHAT IT DOES, IN PLAIN LANGUAGE
-------------------------------
Every slope in the paper is fitted to the explicit Euler-Maruyama scheme at
dt = 0.01. DTREF ran the same realizations of the scope rows (CONC, PROBEARM,
ONSET) at dt = 0.005 (level L1) and 0.0025 (L2) on the same Brownian path and
the same initial ensemble. For every realization this script fits the slope
at each level exactly as rerun_analysis.py fits it, takes the difference from
the dt 0.01 slope of the same realization (the committed rerun row), and asks,
for every cell arm and every contrast rerun_analysis.py computes for these
rows, whether the mean difference is inside +-0.01 (STABLE), outside it
(SHIFTED), or neither can be said (UNRESOLVED). Before any of that it runs a
null fixture that measures how often STABLE and SHIFTED fire when they should
not, and a criterion that fires too often is not used as a verdict. A finite-
window slope is never called a rate, and a difference not found is never
called an equivalence unless STABLE, which is itself an equivalence test with
a stated margin and a measured false rate, says so (CLAUDE.md rule 10). No dt
measurement is a continuous-time statement (N46).

INPUTS (each folder read only after its sha256.txt verifies; exit 2 otherwise)
  --dtref DIR, repeated: every fetched DTREF shard folder of the queue, every
      accepted attempt, attempts that stopped at exit 5 included (they hold
      complete rows, rule 17). NOT the drill's folders (they repeat tasks of
      shard D) and NOT the folders IMG marked superseded (rerunq.py; made on
      an image the run then left). Each holds one dtref-run-*/
      dtref_params.csv with mode run and one dtref_real.csv.
  --rerun DIR, repeated: the committed rerun folders holding the dt 0.01
      rows (L0) of every scope trajectory (CONC: rerun-cal-s0of2, -s1of2;
      PROBEARM, ONSET and the RMAP-owned ONSET cells: rerun-arch-s0of4 to
      -s3of4).
  --gate DIR, repeated: every gate folder the --dtref folders name (their
      params "gate"); each must record GATE PASS.
  --py-detcheck LOG, repeated: A0-PY rule D evidence (below).
  --plan, --timing: dtref.py's (defaults the committed ones); they rebuild
      the trajectory list through dtref.traj_tasks (K2: shared cells under
      their owner's key), the cells and their bootstrap keys.

A0  ADMISSION (exit 2 on any failure, naming it)
  - The --dtref folders agree on rows (= --rows, default CONC,PROBEARM,
    ONSET), nshards, plan, plan_sha256, timing, numpy and the five script
    hashes (script_sha256, rerun_sha256, rerunlib_sha256, costprobe2_sha256,
    calprec2_sha256), and on python unless A0-PY admits the difference.
    plan_sha256 equals the plan's rerun_plan.csv sha256.
  - Every --dtref folder's gate is one of the --gate folders, and that
    gate's python, numpy and script_sha256 equal the folder's (dtref.py
    refuses otherwise; checked again here). Every --gate folder records
    GATE PASS, rows = --rows and every module PASS.
  - Every complete dtref row (end "ok"): tid = traj_tid + "|L" + level,
    phase "L<level>", level 1 or 2, dt = repr(0.01 / 2^level), K_level =
    round(T / dt), bridge "ok", bridge_err <= 1e-12, n_coarse = round(T /
    0.01), n_fine = round(T / dt); traj_tid one of the scope trajectories;
    beta, sigma, boot_key and seed_key equal to the plan's (rerun_analysis
    A0's four checks). A tid complete in two folders, or not one of the
    12960 the scope needs, is exit 2.
  - Every committed L0 row used (end "ok", tid one of the scope
    trajectories): the same four plan checks; a tid complete in two --rerun
    folders is exit 2.
  L0 ADMISSION. The L0 rows were written on Kaggle's Python 3.13.15 image;
  the DTREF rows on whatever image each gate passed on. They are compared
  because every gate the --dtref folders used recorded A2 PASS: on that
  image, the wrapped dt 0.01 call reproduced the committed row string for
  string in every computed column, for one trajectory of every gate group.
  The python versions of the L0 rows (their env column) are printed.

A0-PY  A SECOND INTERPRETER AMONG THE --dtref FOLDERS (written with the
  script, 2026-11-28, on the A0-PY pattern of c5_analysis.py, Rahul's
  binding of 2026-11-28: "accepts a second interpreter only on committed
  bitcmp and detcheck evidence, ... whether or not regate is ever used").
  Let V be the set of python versions in the --dtref folders' params.
  |V| = 1: nothing more is needed.
  |V| > 1: admitted iff ALL hold, else exit 2 naming what is missing:
  PY-G every version in V is the python of at least one --gate folder, and
       each --dtref folder's own gate has its python (A0);
  PY-B the versions in V are connected by edges (v1, v2) given by pairs of
       --gate folders with pythons v1 != v2, equal numpy and script_sha256,
       whose dtref_real.csv rows are IDENTICAL: the same tid set (at least
       one), and every column string-equal except env, wall_s,
       peak_rss_mb, pid and rss_mb (machine readings). The two gates run
       the same task list (P0, W0, W1 and W2 of every group, and the RSS
       tasks), so this is a bitwise comparison of the dynamics at all
       three levels across the two images;
  PY-D every version in V has a --py-detcheck log that passes c5_analysis
       rule D (c5_analysis.py_detcheck, imported, not retyped): a committed,
       unmodified kernel log in a run folder whose sha256.txt is committed
       and verifies, one python version, numpy the folders', "VERDICT
       D1+D2: PASS   D3: PASS   OVERALL: PASS", and an ENVIRONMENT.md line
       ending "OVERALL: PASS -- see <log>".
  Every supplied --py-detcheck log is checked whether or not needed; one
  that fails, or names a version no folder reports, is exit 2.
  ONE DIFFERENCE FROM c5_analysis, AND WHY. c5_analysis takes its bitwise
  evidence from a c5bitcmp log. Here it is the pair of committed gate
  folders, compared inside this script (PY-B). c5bitcmp.py reads c5run
  folders only, and rerunq.py's IMG makes every image change produce a
  second gate over the identical task list, so the evidence exists, is
  committed, and is checked every time this script runs instead of in a
  separate step that could be skipped.
  Worked example: shards 0 to 3 on 3.13.18 (gate1), 4 to 8 on 3.13.19
  (gate2 after IMG); --gate gate1 --gate gate2; the 34 gate rows of the
  two folders identical in every computed column; --py-detcheck for 3.13.18
  and for 3.13.19: PY PASS. A W2 row of gate2 differing in one E_J string:
  PY-B FAIL, exit 2. No detcheck log for 3.13.19: PY-D FAIL, exit 2.
  NULL RATE: deterministic string, hash and git checks; none fires by
  chance. A0-PY decides which folders may be read together, never what is
  read from them.

A1  COMPLETE (as rerun_analysis A1, D3): all 12960 DTREF tasks (6480
  trajectories x L1, L2) and all 6480 L0 rows present and complete.
  Otherwise every row's count is printed, "INCOMPLETE: analysis refused",
  nothing is computed, exit 7.

B-RUN  SAME START, SAME PATH (dtref.py docstring, before any Delta is used):
  for every trajectory its L1 and L2 rows have equal, non-empty x0_sha,
  coarse_sha and n_init, equal le0 strings, and where the committed L0 row
  has a le0 it equals theirs. A trajectory that fails is excluded: its
  realization is dropped from its cell at every level, and in a paired
  (ONSET) cell from both arms, as rerun_analysis item 3 drops a
  realization. Every exclusion is listed; the count per row is printed.
  Worked example: an ONSET trajectory whose L2 coarse_sha differs from its
  L1: B-RUN FAIL, rep dropped from both arms of its cell, "M 11 of 12".
  NULL RATE: deterministic; none fires by chance.

ESTIMATOR (rerun_analysis items 0, 2, 3, unchanged and imported)
  Slope of realization r of cell arm a at level l on window w: s_r(a, l, w)
  = regimemap.fit_slope (rerun_analysis.fit_slope) over the J of
  rerun_analysis.window(c, w), every E finite and > 0, else the realization
  is dropped from the cell (at every level, from both arms). Windows: W-full
  for every cell, W-ge where it drops a point (tau_0 < 0.1), exactly the
  instances rerun_analysis computes.
  Delta_r(a, l, w) = s_r(a, l, w) - s_r(a, 0, w), l = 1, 2.
  Resamples: B = 10000, the cell's own index matrix
  rerun_analysis.boot_idx(rerunlib.boot_key(cell, owner), n), n the kept
  count, applied to the same kept realizations at every level and in both
  arms (paired across levels and arms). A statistic's DTREF difference is
  computed by running rerun_analysis's own code for that statistic
  (conc_like, paired_gaps) on S-slopes replaced by mean Deltas: every such
  statistic is linear in the cell S-slopes (contrasts, CON, TMM, REGF
  coefficients, pooled means), so this is exactly stat(l) - stat(0),
  resample by resample. Severity S(r 3) - S(r 1) and S(r 3) - S(r 0.75)
  and their trends on log2 d are computed by severity_block, the severity
  loop of rerun_analysis.onset_block retyped here (onset_block also
  computes onsets, which are not linear); the pre-handover check ran both
  on the same S-slopes and found every severity row equal.
  Cell arms: every (cell, diffusion, window) of the scope rows, the 24
  RMAP-owned ONSET cells included (counted under ONSET).
  Contrasts: CONC and PROBEARM, everything conc_like computes (c1
  dimension, c2 target, c4 law, CON pairs, TMM, REGF b_d, b_tau, b_dtau,
  per unit and pooled); ONSET, c3 aniso - iso (paired_gaps) and severity.
  Not under DTREF: onsets (below); the finite-J audit (an ESS ratio, not a
  slope); P3.4 R^2 (a point value with no interval).

THE CRITERION (N46, approved 2026-11-03; dtref.py docstring)
  delta = 0.01 (a third of +0.0305, the smallest resolved effect the
  abstract reports, N46). On the 95% percentile interval [lo, hi] (2.5th
  and 97.5th percentiles of the B finite resamples, rerun_analysis.pct) of
  the mean Delta:
    STABLE      -delta < lo and hi < +delta
    SHIFTED     lo > +delta or hi < -delta
    UNRESOLVED  otherwise.
  Worked example: [-0.004, +0.007] STABLE; [+0.013, +0.021] SHIFTED;
  [-0.002, +0.015] UNRESOLVED.
  The verdict is given on every window, W-ge included (fixed 2026-11-28:
  the abstract quotes the W-ge "J >= 1/tau_0" changes of CONC, so DTREF
  must judge that window too; rerun_analysis's own verdicts stay on
  W-full). Each line says which window role it is.
  No verdict, and the reason printed, when more than 1% of B resamples are
  non-finite (rerun_analysis FLAG) or the interval is not finite.
  Counts per (level, row, kind: cell arm, unit, pooled; window role) of
  STABLE, SHIFTED, UNRESOLVED and no verdict. No multiplicity adjustment,
  no family-wise claim: every line is printed.
  NULL RATE (by construction, as N46 states it): under any true |Delta| >=
  delta, STABLE fires with probability at most 0.025 per quantity, and
  under any true |Delta| <= delta SHIFTED fires with probability at most
  0.025 (one-sided coverage of a 95% interval at the nearer bound),
  asymptotically in M. At M 15 and 12 the percentile bootstrap can fall
  short of that (C5's null fixture found percentile intervals at n 15
  firing above nominal, N45), so the rates are MEASURED, every run, before
  any verdict:

NULL FIXTURE AND THE RULE IT FEEDS (run first, every time; N40 commitment)
  Synthetic quantities, nothing read from any run. A cell holds n
  per-realization Deltas, Delta_r = m + s e_r, e_r of unit variance from
  one of three laws: normal; Student t with 3 degrees of freedom scaled
  to unit variance; centred lognormal (sigma 0.75) scaled to unit
  variance (skewed; a stress law, not fitted to anything: no committed
  run measures the distribution of a Delta). A unit is a weighted sum
  sum_j w_j (cell j's resampled mean) of independent cells, each cell
  resampled with its own index matrix of B = 10000 (the B the verdicts
  use); the cell a with the largest |w_j| carries m = mu / w_a and every
  other cell m = 0, so the unit's true value is mu. A pooled figure is
  the mean of k independent such units. The criterion is applied to the
  resulting interval.
  Shapes (CORRECTED 2026-11-28, ledger N46, NULL FIXTURE FAMILIES). Each
  family holds only shapes its statistics have; the weight vectors are
  the statistics' own:
    cell    C1     w (1): a cell arm.
    unit    D2     (+1, -1): every two-cell contrast in scope (c1
                   dimension, c2 target, c4 law, c3 aniso - iso, change,
                   severity).
            CON4   (+1, -1, -1, +1): CON(t1, t2).
            TMM6   (+1, -1, -1/2, +1/2, -1/2, +1/2): change(0.01) -
                   (change(0.5) + change(0.1)) / 2.
            RGd, RGt, RGdt  the rows b_d, b_tau, b_dtau of pinv(X), X
                   rerun_analysis's REGF design [1, log2 d, log10(1/tau_0),
                   log2 d log10(1/tau_0)] on rerunlib.GRID["CONC"]'s 4 d x 3
                   tau_0 (PROBEARM's grid is the same; checked at start),
                   computed here from the grid, scaled to max |w| = 1 (a
                   scale change leaves a BOUNDARY rate unchanged).
    pooled  D2 at k 3 (ONSET's c3 and severity), 6 (c4 law), 12 (c1, c2,
            change); CON4, TMM6, RGd, RGt, RGdt at k 12. These are the
            pooled sizes rerun_analysis prints for the scope rows.
  Each unit and pooled shape is run in two law modes: "all", every cell
  on the row's law (a contrast of identically distributed cells, where
  equal weights cancel skew), and "one", the cell a on the row's law and
  every other cell normal (unequal laws: skew does not cancel; with
  unequal weights it cancels only partly even in "all"). Mode "one" is
  run for t3 and lognormal only (for normal it is "all"). Unequal cell
  scales are unequal weights in this model; their extreme, one cell
  dominating, is C1.
  The first version (2026-11-28, logs/dtref-analysis-selftest-20261128.log)
  put the single-cell shapes (1, 1) into family unit and (1, 3) into
  family pooled; no unit or pooled statistic in scope is a single cell, so
  those families' NF 400 rates came from shapes they never contain. C1
  keeps shape index 0 and the same draws, so its rows reproduce that
  log's (1, 1) rows exactly.
  n = 12 (ONSET) and 15 (CONC, PROBEARM). NF = 400 replicates per row
  (Monte Carlo SE about 0.008 at a rate of 0.025).
  Blocks:
    BOUNDARY   mu = delta, s = 0.005, every shape, its laws, both n.
               The null of STABLE (true Delta exactly at the margin) and of
               SHIFTED (|true Delta| <= delta). For a location-scale law
               the rates do not depend on s; s only has to be fixed.
    NO EFFECT  mu = 0 (N46's "no dt effect" fixture), s 0.005 and 0.02,
               normal, shapes C1, D2 and D2 k 12 (one per family), both
               n: STABLE's rate (power, reported) and SHIFTED's (a null,
               used in its r).
    PLANTED    mu = 2 delta = 0.02 (N46's "planted shift"), same grid:
               SHIFTED's rate (power, reported) and STABLE's (a null,
               used in its r).
  Seeds SeedSequence((20261128, 102, block, shape, n, law, s, mu, rep)),
  kind 102 used by no other script (in use: 1, 2, 4, 11, 12, 31 to 35, 41
  to 43, 51, 61 to 67, 71, 81, 83, 91, 92, 95 to 99, 101; 103 is
  --selftest's).
  RULE (fixed now). For each criterion (STABLE, SHIFTED) and family
  (cell, unit, pooled): r = the largest rate over the rows that are a null
  for that criterion in that family. r <= 0.025: used. 0.025 < r <= 0.05:
  used, with "null rate r" beside every verdict. r > 0.05: NOT USED; its
  verdict column reads "not used (null rate r)" and the interval is still
  printed. (C5's rule, nominal 0.05 and flag 0.10, scaled to this
  criterion's nominal 0.025.) A cell arm reads family cell, every unit
  (contrast, CON, TMM, REGF coefficient, c3, severity) family unit, a
  pooled figure family pooled. More rows in a family raise its maximum
  by Monte Carlo noise alone; NF 12000 measures that (as for C5).
  Worked example: BOUNDARY STABLE rates for family cell 0.021, 0.024,
  0.034, ... and PLANTED STABLE rates 0.000: r 0.034, STABLE used for cell
  arms with "null rate 0.034".
  --null-only runs the fixture alone (exit 0). --nf N changes NF for
  --null-only and --selftest only; a real run always reads the NF 400
  rates (exit 2 otherwise).

ONSETS (description only; fixed 2026-11-28). rerun_analysis.onset_block
  (imported) is run at each level, L0 included, on the S-slopes of the
  realizations kept at every level: onsets (H3), the J4 counts "k of n
  intervals contain 1" per level, contrast 6 and severity, each printed
  with its interval and NO verdict. Why no DTREF verdict: delta is a
  margin for slopes and slope contrasts; an onset is a location on the r
  grid, and N46 fixed no margin for it. What it lets the paper say: the
  onset counts the abstract quotes ("nine of ten" intervals contain 1),
  stated at each dt. The L0 line here can differ from rerun_analysis's
  published one only if a realization is dropped (B-RUN, a bad point at
  L1 or L2); the kept counts are printed.

--selftest  (N46's "through the whole analysis script" fixture). Reads the
  plan only. Synthetic E for every scope trajectory: log E_J(L0) = a_r +
  (-1 + g_r) log J + e_J, a_r ~ N(0, 1), g_r ~ N(0, 0.05), e_J ~ N(0,
  0.02); log E_J(Ll) = log E_J(L0) + (mu + 0.003 z_rl) log J, z ~ N(0, 1);
  seeds SeedSequence((20261128, 103, trajectory key, level)). Run twice,
  mu = 0 and mu = 0.02, through the same code as a real run from the
  slopes onwards (B-RUN, A0 and A1 are file checks and are not exercised).
  Expected, as a check of the plumbing, not of rates: at mu = 0 the cell
  arms STABLE, at mu = 0.02 SHIFTED; contrasts STABLE in both (a uniform
  shift cancels in a difference of cells). Exit 0. It prints counts only.

OUTPUT (printed; nothing written)
  The header (every parameter, versions, workers); the null fixture table
  and the RULE's status per criterion and family; A0, A0-PY, L0 admission,
  A1 counts; B-RUN exclusions; per level L1 and L2: every cell arm, then
  every contrast, unit and pooled, with estimate, interval, verdict and
  window role; the counts; the per-level onset description; the summary.

EXIT CODES  0 printed (also --null-only, --selftest); 2 an input problem;
  7 DTREF incomplete (nothing computed).

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/dtref_analysis.py --null-only --workers 2
    python -B scripts/dtref_analysis.py --selftest --workers 2
    python -B scripts/dtref_analysis.py --workers 2 \\
        --dtref runs/<shard folder> --dtref runs/<shard folder> ... \\
        --gate runs/<gate folder> \\
        --rerun runs/rerun-arch-s0of4-a1-kaggle-20261024-020220 \\
        --rerun runs/rerun-arch-s1of4-a1-kaggle-20261024-133226 \\
        --rerun runs/rerun-arch-s2of4-a1-kaggle-20261024-160215 \\
        --rerun runs/rerun-arch-s3of4-a1-kaggle-20261024-200233 \\
        --rerun runs/rerun-cal-s0of2-a1-kaggle-20261025-003238 \\
        --rerun runs/rerun-cal-s1of2-a1-kaggle-20261025-050238
  with --py-detcheck LOG per python version when the shards span two.
Git is called (A0-PY) from the repository root to check that evidence
files are committed and unmodified.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import io                                                       # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dtref as D                                               # noqa: E402
import rerun_analysis as RA                                     # noqa: E402
import c5_analysis as C5A                                       # noqa: E402

rl, RR = D.rl, D.RR
Stop = D.Stop
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DELTA = 0.01
B = RA.B
FLAG_FRAC = RA.FLAG_FRAC
LEVELS = (1, 2)
SCOPE = "CONC,PROBEARM,ONSET"
MACHINE_COLS = ("env", "wall_s", "peak_rss_mb", "pid", "rss_mb")
NOMINAL = 0.025
FLAG_RATE = 0.05
NF = 400
NULL_SEED = (20261128, 102)
SELF_SEED = (20261128, 103)
NULL_NS = (12, 15)
NULL_LAWS = ("normal", "t3", "lognormal")
LAW_MODES = ("all", "one")
PARAM_COMMON = ("rows", "nshards", "plan", "plan_sha256", "timing", "numpy", "script_sha256", "rerun_sha256",
                "rerunlib_sha256", "costprobe2_sha256", "calprec2_sha256")

LOG = []


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "=" * 100)
    say(s)
    say("=" * 100)


def fmt(x, n=4):
    return RA.fmt(x, n)


# ----------------------------------------------------------------------
# the criterion
# ----------------------------------------------------------------------

def criterion(q):
    """STABLE / SHIFTED / UNRESOLVED on q = rerun_analysis.pct(vec); None and a reason when no verdict."""
    if q["nf"] > FLAG_FRAC * B:
        return None, "FLAG non-finite above 1% ({} of {}), no verdict".format(q["nf"], B)
    lo, hi = q["lo"], q["hi"]
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return None, "no finite interval"
    if -DELTA < lo and hi < DELTA:
        return "STABLE", ""
    if lo > DELTA or hi < -DELTA:
        return "SHIFTED", ""
    return "UNRESOLVED", ""


# ----------------------------------------------------------------------
# null fixture
# ----------------------------------------------------------------------

def noise(rng, law, n):
    if law == "normal":
        return rng.standard_normal(n)
    if law == "t3":
        return rng.standard_t(3, n) / math.sqrt(3.0)
    s2 = 0.75 ** 2
    x = np.exp(0.75 * rng.standard_normal(n))
    return (x - math.exp(s2 / 2.0)) / math.sqrt((math.exp(s2) - 1.0) * math.exp(s2))


def regf_weights():
    """Rows b_d, b_tau, b_dtau of pinv(X) for rerun_analysis's REGF design on GRID["CONC"], max |w| = 1."""
    gs = [rl.GRID[r] for r in ("CONC", "PROBEARM")]
    if [(g["dims"], g["taus"]) for g in gs][0] != [(g["dims"], g["taus"]) for g in gs][1]:
        raise Stop(2, "null fixture: CONC and PROBEARM REGF grids differ; RG shapes need both")
    g = gs[0]
    X = np.array([[1.0, math.log2(d), math.log10(1.0 / t), math.log2(d) * math.log10(1.0 / t)]
                  for d in g["dims"] for t in g["taus"]])
    P = np.linalg.pinv(X)
    return [tuple(float(x) for x in P[j] / np.abs(P[j]).max()) for j in (1, 2, 3)]


def make_shapes():
    """(name, family, weights, mode, k); index 0 is C1 (same draws as the first version's (1, 1))."""
    rgd, rgt, rgdt = regf_weights()
    units = (("D2", (1.0, -1.0)), ("CON4", (1.0, -1.0, -1.0, 1.0)),
             ("TMM6", (1.0, -1.0, -0.5, 0.5, -0.5, 0.5)), ("RGd", rgd), ("RGt", rgt), ("RGdt", rgdt))
    out = [("C1", "cell", (1.0,), "all", 1)]
    for nm, w in units:
        for md in LAW_MODES:
            out.append((nm, "unit", w, md, 1))
    for nm, w in units:
        for k in ((3, 6, 12) if nm == "D2" else (12,)):
            for md in LAW_MODES:
                out.append((nm, "pooled", w, md, k))
    return tuple(out)


SHAPES = make_shapes()


def shape_label(si):
    nm, _f, _w, md, k = SHAPES[si]
    return nm if k == 1 and nm == "C1" else "{}/{}{}".format(nm, md, "" if k == 1 else " k{}".format(k))


def shape_index(name, fam, md, k):
    for i, x in enumerate(SHAPES):
        if (x[0], x[1], x[3], x[4]) == (name, fam, md, k):
            return i
    raise KeyError(name)


def null_rep(rng, si, n, law, s, mu):
    _nm, _fam, w, md, k = SHAPES[si]
    a = int(np.argmax(np.abs(np.array(w))))
    vecs, pts = [], []
    for _u in range(k):
        v = np.zeros(B)
        p = 0.0
        for j, wj in enumerate(w):
            lj = law if (md == "all" or j == a) else "normal"
            x = (mu / w[a] if j == a else 0.0) + s * noise(rng, lj, n)
            idx = rng.integers(0, n, size=(B, n))
            v += wj * x[idx].mean(axis=1)
            p += wj * float(x.mean())
        vecs.append(v)
        pts.append(p)
    return float(np.mean(pts)), np.mean(np.vstack(vecs), axis=0)


def null_task(a):
    blk, si, n, li, sidx, s, midx, mu, nf = a
    cnt = {"STABLE": 0, "SHIFTED": 0, "UNRESOLVED": 0, None: 0}
    for rep in range(nf):
        rng = np.random.default_rng(np.random.SeedSequence(list(NULL_SEED) + [blk, si, n, li, sidx, midx, rep]))
        _p, vec = null_rep(rng, si, n, NULL_LAWS[li], s, mu)
        v, _why = criterion(RA.pct(vec))
        cnt[v] += 1
    return a, cnt


def family_of_shape(si, fam):
    return SHAPES[si][1] == fam


def null_fixture(workers, nf=NF):
    hdr("NULL FIXTURE  (synthetic; run first, every time)  B {}  NF {} per row  delta {}".format(B, nf, DELTA))
    jobs = []
    for si in range(len(SHAPES)):
        for n in NULL_NS:
            for li in range(len(NULL_LAWS)):
                if SHAPES[si][3] == "one" and NULL_LAWS[li] == "normal":
                    continue
                jobs.append((0, si, n, li, 0, 0.005, 0, DELTA, nf))
    pw_shapes = (0, shape_index("D2", "unit", "all", 1), shape_index("D2", "pooled", "all", 12))
    for blk, mu, midx in ((1, 0.0, 1), (2, 2 * DELTA, 2)):
        for si in pw_shapes:
            for n in NULL_NS:
                for sidx, s in ((0, 0.005), (1, 0.02)):
                    jobs.append((blk, si, n, 0, sidx, s, midx, mu, nf))
    pool = multiprocessing.Pool(processes=workers)
    try:
        res = dict(pool.map(null_task, jobs, chunksize=1))
    finally:
        pool.close()
        pool.join()
    names = {0: "BOUNDARY", 1: "NO EFFECT", 2: "PLANTED"}
    say("  {:<10} {:<7} {:<16} {:>3} {:<9} {:>6} {:>6}   {:>8} {:>8} {:>10} {:>9}".format(
        "block", "family", "shape", "n", "law", "s", "mu", "STABLE", "SHIFTED", "UNRESOLVED", "no verdict"))
    rows = []
    for a in jobs:
        cnt = res[a]
        blk, si, n, li, _sidx, s, _midx, mu, _nf = a
        rs = cnt["STABLE"] / float(nf)
        rh = cnt["SHIFTED"] / float(nf)
        rows.append((blk, si, rs, rh))
        say("  {:<10} {:<7} {:<16} {:>3} {:<9} {:>6} {:>6}   {:>8.4f} {:>8.4f} {:>10.4f} {:>9.4f}".format(
            names[blk], SHAPES[si][1], shape_label(si), n, NULL_LAWS[li], s, mu, rs, rh,
            cnt["UNRESOLVED"] / float(nf), cnt[None] / float(nf)))
    status = {}
    say("\n  RULE: r = largest rate over the rows that are a null for the criterion in the family;")
    say("  r <= {} used; {} < r <= {} used with 'null rate r'; r > {} NOT USED".format(
        NOMINAL, NOMINAL, FLAG_RATE, FLAG_RATE))
    for crit in ("STABLE", "SHIFTED"):
        for fam in ("cell", "unit", "pooled"):
            if crit == "STABLE":
                rr = [x[2] for x in rows if x[0] in (0, 2) and family_of_shape(x[1], fam)]
            else:
                rr = [x[3] for x in rows if x[0] in (0, 1) and family_of_shape(x[1], fam)]
            r = max(rr)
            st = "used" if r <= NOMINAL else ("flagged" if r <= FLAG_RATE else "not used")
            status[(crit, fam)] = (st, r)
            say("  NULL RATE {:<8} family {:<7} r {:.4f} over {:>2} null rows: {}".format(
                crit, fam, r, len(rr), {"used": "used", "flagged": "used, with 'null rate {:.4f}'".format(r),
                                        "not used": "NOT USED as a verdict"}[st]))
    pw = [(names[x[0]], SHAPES[x[1]], x[2], x[3]) for x in rows if x[0] in (1, 2)]
    say("\n  power (reported, decides nothing): NO EFFECT rows' STABLE rate and PLANTED rows' SHIFTED rate are")
    say("  in the table above; {} rows".format(len(pw)))
    return status


# ----------------------------------------------------------------------
# statistics objects (rerun_analysis's family() calls our one())
# ----------------------------------------------------------------------

class DStats(RA.Stats):
    """Records DTREF verdicts; rerun_analysis.Stats.family pools units and calls one()."""

    def __init__(self, lev, status):
        RA.Stats.__init__(self)
        self.lev = lev
        self.status = status
        self.recs = []

    def one(self, row, quantity, group, level, unit, wlabel, point, vec, primary, equiv=False, orient=False,
            note="", het=None, cells=None):
        q = RA.pct(vec)
        v, why = criterion(q)
        fam = {"cell": "cell", "unit": "unit"}.get(level, "pooled")
        shown = v or why
        if v in ("STABLE", "SHIFTED"):
            st, r = self.status[(v, fam)]
            if st == "flagged":
                shown = "{} (null rate {:.4f})".format(v, r)
            elif st == "not used":
                shown = "not used (null rate {:.4f}; criterion {})".format(r, v)
                v = None
        role = "primary" if primary else "sensitivity"
        rec = {"lev": self.lev, "row": row, "quantity": quantity, "group": group, "level": level, "unit": unit,
               "window": wlabel, "role": role, "point": point, "lo": q["lo"], "hi": q["hi"], "verdict": v,
               "shown": shown, "not_used": shown.startswith("not used")}
        self.recs.append(rec)
        extra = ""
        if het is not None:
            extra = "  k {} sd_units {} I2 {}".format(het["k"], fmt(het["sd_units"]), het["I2"])
        say("  L{} {:<9} {:<26} {:<34} {:<7} {:<22} {:<6} {:<11} {} [{}, {}] {}{}".format(
            self.lev, row, quantity, group, level, unit, wlabel, role, fmt(point, 5),
            fmt(q["lo"], 5), fmt(q["hi"], 5), shown, extra))
        return rec


class PlainStats(RA.Stats):
    """Per-level description: estimate and interval, no verdict (onsets, ONSETS above)."""

    def __init__(self, lev):
        RA.Stats.__init__(self)
        self.lev = lev

    def one(self, row, quantity, group, level, unit, wlabel, point, vec, primary, equiv=False, orient=False,
            note="", het=None, cells=None):
        q = RA.pct(vec)
        say("  L{} {:<9} {:<26} {:<34} {:<7} {:<22} {:<6} {} [{}, {}] description, no verdict".format(
            self.lev, row, quantity[:26], group[:34], level, unit[:22], wlabel, fmt(point), fmt(q["lo"]),
            fmt(q["hi"])))
        return {}


# ----------------------------------------------------------------------
# per-level slope contexts (rerun_analysis.Ctx with S replaced)
# ----------------------------------------------------------------------

class LevelCtx(RA.Ctx):
    """S(c, df, w) on the realizations kept at every level: level l's S-slope (delta=False) or the mean
    Delta s(l) - s(0) (delta=True), with the cell's own index matrix."""

    def __init__(self, cells_by_row, res, lev, delta):
        RA.Ctx.__init__(self, cells_by_row, res, {})
        self.lev = lev
        self.delta = delta

    def S(self, c, df, w):
        Js = tuple(RA.window(c, w))
        bk = rl.key_str(rl.boot_key(c, c["owner"]))
        r = self.res[(bk, Js)]
        n = len(r["kept"])
        if n == 0:
            return float("nan"), np.full(B, np.nan)
        x = r["sl"][self.lev][df] - (r["sl"][0][df] if self.delta else 0.0)
        ck = (bk, n)
        if ck not in self.idx_cache:
            if len(self.idx_cache) > 64:
                self.idx_cache.clear()
            self.idx_cache[ck] = RA.boot_idx(rl.boot_key(c, c["owner"]), n)
        return float(x.mean()), x[self.idx_cache[ck]].mean(axis=1)


def severity_block(ctx, st, row):
    """rerun_analysis.onset_block's severity part (8.2), retyped: S(1,3) and S(0.75,3) per (diffusion, d),
    units the objectives, pooled; their OLS trend on log2 d (five d, intercept)."""
    g = rl.GRID[row]
    objs, dims, t = g["objs"], g["dims"], g["tau"]
    hdr("{}  severity S(1,3), sensitivity S(0.75,3), and their trend on log2 d (J2)".format(row))
    Xd = np.array([[math.log2(d), 1.0] for d in dims])
    for nm, rlo in (("severity S(1,3)", 1.0), ("severity S(0.75,3) boundary-spanning", 0.75)):
        sev = {}
        for df in g["diffs"]:
            for d in dims:
                us = []
                for o in objs:
                    c3_ = ctx.cell(row, obj=o, d=d, tau=t, r=3.0)
                    c1_ = ctx.cell(row, obj=o, d=d, tau=t, r=rlo)
                    p3, v3 = ctx.S(c3_, df, "full")
                    p1, v1 = ctx.S(c1_, df, "full")
                    sev[(df, o, d)] = (p3 - p1, v3 - v1)
                    us.append((o, p3 - p1, v3 - v1, [c3_, c1_]))
                st.family(row, nm, "{} d={}".format(df, d), us, "W-full", True)
            us = []
            for o in objs:
                pts = np.array([sev[(df, o, d)][0] for d in dims])
                Y = np.vstack([sev[(df, o, d)][1] for d in dims])
                us.append((o, float(RA.ols_coef(Xd, pts)[0]), RA.ols_coef(Xd, Y)[0],
                           [ctx.cell(row, obj=o, d=d, tau=t, r=rr) for d in dims for rr in (3.0, rlo)]))
            st.family(row, nm + " trend per doubling of d", df, us, "W-full", True,
                      note="coefficient only; no shape is claimed")


# ----------------------------------------------------------------------
# slopes per (cell, window), all levels, paired
# ----------------------------------------------------------------------

def slope_task(a):
    Js = a["Js"]
    Jarr = np.array(Js, dtype=float)
    per = {}
    for lev in (0,) + LEVELS:
        for df in a["diffs"]:
            for rep in a["reps"]:
                e = a["E"][lev][df][rep]
                vals = [e.get(J, float("nan")) for J in Js]
                bad = sum(1 for v in vals if not (np.isfinite(v) and v > 0))
                if bad:
                    per[(lev, df, rep)] = (float("nan"), "L{} {} {} bad point(s)".format(lev, df, bad))
                    continue
                s = RA.fit_slope(Jarr, np.array(vals))
                per[(lev, df, rep)] = (s, "") if np.isfinite(s) else (float("nan"), "L{} {} non-finite slope".format(
                    lev, df))
    kept, dropped = [], []
    for rep in a["reps"]:
        why = [per[(lev, df, rep)][1] for lev in (0,) + LEVELS for df in a["diffs"]
               if not np.isfinite(per[(lev, df, rep)][0])]
        why += ["B-RUN {}".format(df) for df in a["diffs"] if (df, rep) in a["bad"]]
        if why:
            dropped.append((rep, a["keys"][rep], "; ".join(why)))
        else:
            kept.append(rep)
    sl = dict((lev, dict((df, np.array([per[(lev, df, rep)][0] for rep in kept])) for df in a["diffs"]))
              for lev in (0,) + LEVELS)
    return {"id": a["id"], "kept": kept, "dropped": dropped, "sl": sl, "M": len(a["reps"])}


def phase_slopes(by_row, E, bad, workers):
    """res[(boot key, Js)] for every cell-window instance of the scope rows. E[lev][tid] = {J: E}."""
    jobs = {}
    inst = []
    for row in by_row:
        for c in by_row[row]:
            wins = [("full", "W-full")] + ([("ge", "W-ge")] if RA.has_ge(c) else [])
            bk = rl.key_str(rl.boot_key(c, c["owner"]))
            for w, wl in wins:
                Js = tuple(RA.window(c, w))
                jid = (bk, Js)
                inst.append((row, c, w, wl, jid))
                if jid in jobs:
                    continue
                tids = dict(((df, rep), RA.task_tid(c, df, rep)) for df in c["diffs"] for rep in range(c["M"]))
                jobs[jid] = {"id": jid, "Js": list(Js), "diffs": list(c["diffs"]), "reps": list(range(c["M"])),
                             "E": dict((lev, dict((df, dict((rep, E[lev][tids[(df, rep)]]) for rep in range(c["M"])))
                                                  for df in c["diffs"])) for lev in (0,) + LEVELS),
                             "bad": set(k for k, tid in tids.items() if tid in bad),
                             "keys": dict((rep, rl.key_str(rl.traj_key(c, c["owner"], rep))) for rep in range(c["M"]))}
    say("  {} cell-window instances, {} distinct computations, {} workers".format(len(inst), len(jobs), workers))
    pool = multiprocessing.Pool(processes=workers)
    try:
        res = dict((o["id"], o) for o in pool.imap_unordered(slope_task, list(jobs.values()), chunksize=4))
    finally:
        pool.close()
        pool.join()
    return res, inst


# ----------------------------------------------------------------------
# the DTREF statistics for one level
# ----------------------------------------------------------------------

def dtref_level(by_row, res, inst, lev, status):
    ctx = LevelCtx(by_row, res, lev, True)
    st = DStats(lev, status)
    hdr("L{} (dt {!r}) minus L0: CELL ARMS (every cell, diffusion and window of the scope rows)".format(
        lev, D.dt_of(lev)))
    for row, c, w, wl, jid in inst:
        r = res[jid]
        for df in c["diffs"]:
            p, v = ctx.S(c, df, w)
            st.one(row, "cell Delta", rl.cell_label(c), "cell", "{} M {} of {}".format(df, len(r["kept"]), r["M"]),
                   wl, p, v, w == "full")
    for row in ("CONC", "PROBEARM"):
        if row in by_row:
            hdr("L{} minus L0: {} contrasts (rerun_analysis.conc_like on mean Deltas)".format(lev, row))
            RA.conc_like(ctx, st, row)
    if "ONSET" in by_row:
        hdr("L{} minus L0: ONSET contrast 3 (rerun_analysis.paired_gaps on mean Deltas)".format(lev))
        RA.paired_gaps(ctx, st, "ONSET")
        severity_block(ctx, st, "ONSET")
    return st.recs


def tally(recs, title):
    hdr(title)
    keys = {}
    for r in recs:
        kind = r["level"] if r["level"] in ("cell", "unit") else "pooled"
        k = (r["lev"], r["row"], kind, r["role"])
        keys.setdefault(k, {"STABLE": 0, "SHIFTED": 0, "UNRESOLVED": 0, "not used": 0, None: 0})
        keys[k]["not used" if r["not_used"] else r["verdict"]] += 1
    say("  {:<4} {:<9} {:<7} {:<11} {:>7} {:>8} {:>11} {:>9} {:>11} {:>6}".format(
        "lev", "row", "kind", "window", "STABLE", "SHIFTED", "UNRESOLVED", "not used", "no verdict", "total"))
    for k in sorted(keys, key=lambda z: (z[0], rl.ROWS.index(z[1]), z[2], z[3])):
        v = keys[k]
        say("  L{:<3} {:<9} {:<7} {:<11} {:>7} {:>8} {:>11} {:>9} {:>11} {:>6}".format(
            k[0], k[1], k[2], k[3], v["STABLE"], v["SHIFTED"], v["UNRESOLVED"], v["not used"], v[None],
            sum(v.values())))
    say("  'not used': the criterion that fired has a null rate above {} (RULE); 'no verdict': FLAG or no "
        "finite interval".format(FLAG_RATE))


def onsets_by_level(by_row, res):
    if "ONSET" not in by_row:
        return
    for lev in (0,) + LEVELS:
        hdr("ONSET at L{} (dt {!r}): per-level description (rerun_analysis.onset_block on the level's S-slopes, "
            "realizations kept at every level); no DTREF verdict".format(lev, D.dt_of(lev)))
        ctx = LevelCtx(by_row, res, lev, False)
        RA.onset_block(ctx, PlainStats(lev), [], "ONSET")


def analyse(by_row, E, bad, workers, status):
    hdr("SLOPES  every cell-window instance, levels L0, L1, L2, paired")
    res, inst = phase_slopes(by_row, E, bad, workers)
    for row, c, w, wl, jid in inst:
        for d_ in res[jid]["dropped"]:
            say("  {} {} {} rep {} key {}: dropped at every level{}: {}".format(
                row, rl.cell_label(c), wl, d_[0], d_[1], " and from both arms" if len(c["diffs"]) > 1 else "",
                d_[2]))
    recs = []
    for lev in LEVELS:
        recs.extend(dtref_level(by_row, res, inst, lev, status))
    tally(recs, "COUNTS per level, row, kind and window role (no multiplicity adjustment, no family-wise claim)")
    onsets_by_level(by_row, res)
    return recs, res


# ----------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------

def verified(f):
    return D.verified(f)


def params_of(folder, rels, name):
    return D.read_kv(D.one_file(folder, rels, name))


def plan_check(r, c, df, traj):
    bad = []
    if r["beta"] != repr(c["beta"]):
        bad.append("beta {} vs plan {!r}".format(r["beta"], c["beta"]))
    if r["sigma"] != repr(c["sigma"][df]):
        bad.append("sigma {} vs plan {!r}".format(r["sigma"], c["sigma"][df]))
    if r["boot_key"] != rl.key_str(rl.boot_key(c, c["owner"])):
        bad.append("boot key")
    if r["seed_key"] != traj.rsplit("|", 1)[0]:
        bad.append("seed_key {} differs from the trajectory id's key".format(r["seed_key"]))
    return bad


def e_of(r):
    out = {}
    for J in rl.JCOLS:
        v = r.get("E_{}".format(J), "")
        if v != "":
            out[J] = float(v)
    return out


def read_gates(folders, rows):
    hdr("GATE folders")
    out = {}
    for f in folders:
        rels = verified(f)
        vt = {}
        with io.open(D.one_file(f, rels, D.VERDICT_CSV), "r", newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if r and r[0] != "module":
                    vt[r[0]] = r[1]
        mods = dict((k, v) for k, v in vt.items() if k not in ("GATE", "rows", "python", "numpy", "script_sha256"))
        prob = []
        if vt.get("GATE") != "PASS":
            prob.append("GATE {!r}".format(vt.get("GATE")))
        if vt.get("rows") != rows:
            prob.append("rows {!r}".format(vt.get("rows")))
        if not mods or any(v != "PASS" for v in mods.values()):
            prob.append("modules {}".format(mods))
        if prob:
            raise Stop(2, "A0: gate folder {}: {}".format(f, "; ".join(prob)))
        with io.open(D.one_file(f, rels, D.ROWS_CSV), "r", newline="", encoding="utf-8") as fh:
            grow = dict((r["tid"], r) for r in csv.DictReader(fh))
        out[D.base(f)] = {"folder": f, "python": vt["python"], "numpy": vt["numpy"], "sha": vt["script_sha256"],
                          "rows": grow}
        say("  {}: GATE PASS, python {}, numpy {}, {} gate rows, modules {}".format(
            D.base(f), vt["python"], vt["numpy"], len(grow), ",".join(sorted(mods))))
    return out


def read_dtref(folders, want, rts_by_tid, rows):
    """{tid: row} for the dtref folders; A0 checks. want: the 12960 dtref tids."""
    hdr("DTREF folders (A0)")
    store, where, prms = {}, {}, {}
    for f in folders:
        rels = verified(f)
        pr = params_of(f, rels, D.PARAMS_CSV)
        if pr.get("mode") != "run" or pr.get("rows") != rows:
            raise Stop(2, "A0: {}: mode {} rows {}, expected run {}".format(f, pr.get("mode"), pr.get("rows"), rows))
        prms[f] = pr
        n = 0
        with io.open(D.one_file(f, rels, D.ROWS_CSV), "r", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("end") != "ok":
                    continue
                tid = r["tid"]
                if tid not in want:
                    raise Stop(2, "A0: {}: task {} is not one of the scope's DTREF tasks".format(f, tid))
                if tid in where:
                    raise Stop(2, "A0: task {} complete in {} and {} (a drill or superseded folder?)".format(
                        tid, where[tid], f))
                lev = int(r["level"])
                rt = rts_by_tid[r["traj_tid"]]
                c, T = rt["cell"], rt["cell"]["T"]
                bad = plan_check(r, c, rt["diff"], r["traj_tid"])
                if (tid != "{}|L{}".format(r["traj_tid"], lev) or r["phase"] != "L{}".format(lev)
                        or r["dt"] != repr(D.dt_of(lev)) or r["K_level"] != str(D.k_of(T, lev))):
                    bad.append("tid, phase, dt or K_level")
                if (r["bridge"] != "ok" or not float(r["bridge_err"]) <= D.BRIDGE_TOL
                        or r["n_coarse"] != str(D.k_of(T, 0)) or r["n_fine"] != str(D.k_of(T, lev))):
                    bad.append("bridge {} bridge_err {} n_coarse {} n_fine {}".format(
                        r["bridge"], r["bridge_err"], r["n_coarse"], r["n_fine"]))
                if bad:
                    raise Stop(2, "A0: {}: task {}: {}".format(f, tid, "; ".join(bad)))
                store[tid] = r
                where[tid] = f
                n += 1
        say("  {}: shard {} of {}, python {}, numpy {}, gate {}, {} complete rows".format(
            D.base(f), pr.get("shard"), pr.get("nshards"), pr.get("python"), pr.get("numpy"), pr.get("gate"), n))
    for k in PARAM_COMMON:
        vals = sorted(set(p.get(k) for p in prms.values()))
        if len(vals) != 1:
            raise Stop(2, "A0: the --dtref folders differ in {}: {}".format(k, vals))
    return store, prms


def read_l0(folders, rts_by_tid):
    hdr("COMMITTED L0 rows (dt 0.01, the rerun)")
    out, where, envs = {}, {}, {}
    for f in folders:
        rels = verified(f)
        n = 0
        with io.open(D.one_file(f, rels, "rerun_real.csv"), "r", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("end") != "ok" or r["tid"] not in rts_by_tid:
                    continue
                if r["tid"] in where:
                    raise Stop(2, "A0: L0 task {} complete in {} and {}".format(r["tid"], where[r["tid"]], f))
                rt = rts_by_tid[r["tid"]]
                bad = plan_check(r, rt["cell"], rt["diff"], r["tid"])
                if bad:
                    raise Stop(2, "A0: {}: L0 task {}: {}".format(f, r["tid"], "; ".join(bad)))
                out[r["tid"]] = r
                where[r["tid"]] = f
                envs[r.get("env", "")] = envs.get(r.get("env", ""), 0) + 1
                n += 1
        say("  {}: {} scope rows".format(D.base(f), n))
    say("  L0 environments (env column): {}".format("; ".join("{} ({} rows)".format(k, v)
                                                              for k, v in sorted(envs.items()))))
    return out


def gate_rows_identical(g1, g2):
    """PY-B: None when the two gate folders' rows are identical in every computed column, else the reason."""
    a, b = g1["rows"], g2["rows"]
    if not a or set(a) != set(b):
        return "tid sets differ ({} vs {} rows)".format(len(a), len(b))
    for tid in sorted(a):
        ks = sorted((set(a[tid]) | set(b[tid])) - set(MACHINE_COLS))
        diff = [k for k in ks if a[tid].get(k) != b[tid].get(k)]
        if diff:
            return "tid {} differs in {}".format(tid, ",".join(diff[:6]))
    return None


def check_python(prms, gates, detchecks):
    """A0-PY (docstring)."""
    hdr("A0-PY  python versions of the --dtref folders")
    by_v = {}
    for f, p in sorted(prms.items()):
        g = gates.get(p.get("gate"))
        if g is None:
            raise Stop(2, "A0: {} names gate {}, which is not one of the --gate folders".format(f, p.get("gate")))
        for k, gk in (("python", "python"), ("numpy", "numpy"), ("script_sha256", "sha")):
            if p.get(k) != g[gk]:
                raise Stop(2, "A0: {}: {} {} but its gate {} has {}".format(f, k, p.get(k), p.get("gate"), g[gk]))
        by_v.setdefault(p["python"], []).append(p.get("shard"))
    for v in sorted(by_v):
        say("  python {}: {} folder(s), shards {}".format(v, len(by_v[v]), ",".join(sorted(set(by_v[v]), key=int))))
    npy = sorted(set(p["numpy"] for p in prms.values()))[0]
    probs, dvers, lines = [], set(), []
    for rel in detchecks:
        res, pr = C5A.py_detcheck(rel, npy)
        if pr:
            probs.extend(pr)
        else:
            if res[0] not in by_v:
                probs.append("D: {} is for python {}, which no --dtref folder reports".format(rel, res[0]))
            dvers.add(res[0])
            lines.append(res[1])
    if len(by_v) > 1:
        for v in sorted(by_v):
            if v not in dvers:
                probs.append("PY-D: no passing --py-detcheck log for python {}".format(v))
            if not any(g["python"] == v for g in gates.values()):
                probs.append("PY-G: no --gate folder on python {}".format(v))
        edges = []
        gl = sorted(gates.items())
        for i in range(len(gl)):
            for j in range(i + 1, len(gl)):
                (n1, g1), (n2, g2) = gl[i], gl[j]
                if g1["python"] == g2["python"] or g1["numpy"] != g2["numpy"] or g1["sha"] != g2["sha"]:
                    continue
                why = gate_rows_identical(g1, g2)
                if why:
                    probs.append("PY-B: gates {} and {} ({} and {}): {}".format(n1, n2, g1["python"], g2["python"],
                                                                             why))
                else:
                    edges.append((g1["python"], g2["python"]))
                    say("  PY-B  gates {} ({}) and {} ({}): {} rows identical in every computed column".format(
                        n1, g1["python"], n2, g2["python"], len(g1["rows"])))
        seen, todo = set(), [sorted(by_v)[0]]
        while todo:
            v = todo.pop()
            if v in seen:
                continue
            seen.add(v)
            todo.extend(b for a, b in edges if a == v)
            todo.extend(a for a, b in edges if b == v)
        if not set(by_v) <= seen:
            probs.append("PY-B: versions {} are not connected by identical gate pairs".format(sorted(set(by_v) - seen)))
    for x in probs:
        say("  A0-PY FAIL " + x)
    if probs:
        raise Stop(2, "A0-PY: the folders differ in python and A0-PY does not admit it" if len(by_v) > 1
                   else "A0-PY: a supplied evidence log fails")
    for ln in lines:
        say("  A0-PY  detcheck {}".format(ln))
    if len(by_v) == 1:
        say("  A0-PY PASS  one interpreter, python {}".format(sorted(by_v)[0]))
    else:
        say("  A0-PY PASS  {} interpreters ({}) admitted on the evidence above".format(
            len(by_v), ", ".join(sorted(by_v))))


def b_run(rts, L0, DT):
    hdr("B-RUN  same start, same path: L1 and L2 x0_sha, coarse_sha, n_init, le0 (and le0 = L0's)")
    bad, per_row = {}, {}
    for rt in rts:
        tid = rt["tid"]
        a, b, z = DT[tid + "|L1"], DT[tid + "|L2"], L0[tid]
        why = []
        for k in ("x0_sha", "coarse_sha", "n_init"):
            if not a.get(k) or a.get(k) != b.get(k):
                why.append(k)
        if a.get("le0") != b.get("le0"):
            why.append("le0 L1 != L2")
        if z.get("le0") and z.get("le0") != a.get("le0"):
            why.append("le0 != L0")
        if why:
            bad[tid] = "; ".join(why)
            per_row[rt["scope_row"]] = per_row.get(rt["scope_row"], 0) + 1
    for tid in sorted(bad):
        say("  B-RUN FAIL {}: {}  (excluded)".format(tid, bad[tid]))
    for row in sorted(set(rt["scope_row"] for rt in rts), key=rl.ROWS.index):
        say("  {:<9} trajectories excluded by B-RUN: {}".format(row, per_row.get(row, 0)))
    return set(bad)


# ----------------------------------------------------------------------
# selftest
# ----------------------------------------------------------------------

def synth_E(rts, mu):
    E = dict((lev, {}) for lev in (0,) + LEVELS)
    for rt in rts:
        rng = np.random.default_rng(np.random.SeedSequence(list(SELF_SEED) + [int(x) for x in rt["key"]]
                                                           + [0 if rt["diff"] in ("none", "isotropic") else 1]))
        Js = [J for J in rl.JCOLS]
        lj = np.log(np.array(Js, dtype=float))
        a = rng.standard_normal()
        g = 0.05 * rng.standard_normal()
        base_ = a + (-1.0 + g) * lj + 0.02 * rng.standard_normal(len(Js))
        E[0][rt["tid"]] = dict(zip(Js, np.exp(base_)))
        for lev in LEVELS:
            dl = mu + 0.003 * rng.standard_normal()
            E[lev][rt["tid"]] = dict(zip(Js, np.exp(base_ + dl * lj)))
    return E


def selftest(a, rows, status):
    hdr("SELFTEST  (synthetic E on the plan's scope trajectories; plumbing check, not a result)")
    cells, _walls, _psha = D.inputs(a)
    rts = D.traj_tasks(cells, rows)
    by_row = dict((row, [c for c in cells if c["row"] == row]) for row in rows)
    for mu in (0.0, 2 * DELTA):
        hdr("SELFTEST mu = {}".format(mu))
        recs, _res = analyse(by_row, synth_E(rts, mu), set(), a.workers, status)
        n = {}
        for r in recs:
            kind = r["level"] if r["level"] in ("cell", "unit") else "pooled"
            vv = "not used" if r["not_used"] else r["verdict"]
            n.setdefault(kind, {}).setdefault(vv, 0)
            n[kind][vv] += 1
        say("\n  SELFTEST mu {} counts: {}".format(mu, "; ".join("{} {}".format(k, dict(sorted(
            ((str(x), y) for x, y in v.items())))) for k, v in sorted(n.items()))))
    return 0


# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="DTREF analysis (ledger N46); writes nothing")
    ap.add_argument("--dtref", action="append", default=[])
    ap.add_argument("--rerun", action="append", default=[])
    ap.add_argument("--gate", action="append", default=[])
    ap.add_argument("--py-detcheck", action="append", default=[])
    ap.add_argument("--rows", default=SCOPE)
    ap.add_argument("--plan", default=D.DEFAULT_PLAN)
    ap.add_argument("--timing", default=",".join(D.DEFAULT_TIMING))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--null-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--nf", type=int, default=NF)
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    a.timing = [x for x in a.timing.split(",") if x]
    rows = D.parse_rows(a.rows)
    hdr("CBO-GAP dtref_analysis  (ledger N46: DTREF, the pre-registered analysis)  writes nothing")
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    for label, path in (("dtref_analysis.py", os.path.abspath(__file__)), ("dtref.py", D.__file__),
                        ("rerun_analysis.py", RA.__file__), ("c5_analysis.py", C5A.__file__),
                        ("rerunlib.py", rl.__file__), ("rerun.py", RR.__file__)):
        say("  {:<17} sha256 {}".format(label, D.sha256_of(path)))
    say("  rows     {}".format(",".join(rows)))
    say("  plan     {}".format(D.base(a.plan)))
    say("  timing   {}".format(",".join(D.base(x) for x in a.timing)))
    say("  delta {}  B {}  intervals: 95% percentile (2.5, 97.5); FLAG above {:.0%} non-finite".format(
        DELTA, B, FLAG_FRAC))
    say("  bootstrap indices: rerun_analysis.boot_idx(rerunlib.boot_key(cell, owner), n kept), kind {}".format(
        rl.KIND_BOOT))
    say("  null fixture: NF {}  seeds SeedSequence(({}, {}, ...))  laws {}  n {}  {} shapes (corrected "
        "families, N46)".format(a.nf, NULL_SEED[0], NULL_SEED[1], ",".join(NULL_LAWS),
                                ",".join(str(x) for x in NULL_NS), len(SHAPES)))
    for si, (nm, fam, w, md, k) in enumerate(SHAPES):
        say("    shape {:>2} {:<7} {:<16} k {:>2}  w ({})".format(
            si, fam, shape_label(si), k, ", ".join("{:+.4f}".format(x) for x in w)))
    for f in a.dtref:
        say("  dtref    {}".format(f))
    for f in a.gate:
        say("  gate     {}".format(f))
    for f in a.rerun:
        say("  rerun    {}".format(f))
    for f in a.py_detcheck:
        say("  py-detcheck {}".format(f))
    if a.nf != NF and not (a.null_only or a.selftest):
        raise Stop(2, "--nf other than {} is for --null-only or --selftest (a real run's verdicts read the NF {} "
                      "rates)".format(NF, NF))
    status = null_fixture(a.workers, a.nf)
    if a.null_only:
        hdr("dtref_analysis --null-only done, exit 0")
        return 0
    if a.selftest:
        return selftest(a, rows, status)
    if not (a.dtref and a.rerun and a.gate):
        raise Stop(2, "--dtref, --rerun and --gate are required (or --null-only / --selftest)")
    cells, _walls, psha = D.inputs(a)
    rts = D.traj_tasks(cells, rows)
    rts_by_tid = dict((rt["tid"], rt) for rt in rts)
    want = set("{}|L{}".format(rt["tid"], lev) for rt in rts for lev in LEVELS)
    gates = read_gates([os.path.abspath(x) for x in a.gate], ",".join(rows))
    DT, prms = read_dtref([os.path.abspath(x) for x in a.dtref], want, rts_by_tid, ",".join(rows))
    p0 = list(prms.values())[0]
    if p0.get("plan_sha256") != psha:
        raise Stop(2, "A0: the --dtref folders' plan_sha256 {} is not the plan's {}".format(p0.get("plan_sha256"),
                                                                                           psha))
    check_python(prms, gates, a.py_detcheck)
    L0 = read_l0([os.path.abspath(x) for x in a.rerun], rts_by_tid)
    say("\n  L0 ADMISSION: every gate used recorded A2 PASS (W0 = the committed row, string for string, on its image)")
    hdr("A1  completeness")
    ok = True
    for row in rows:
        mine = [rt for rt in rts if rt["scope_row"] == row]
        have0 = sum(1 for rt in mine if rt["tid"] in L0)
        have = sum(1 for rt in mine for lev in LEVELS if "{}|L{}".format(rt["tid"], lev) in DT)
        good = have0 == len(mine) and have == 2 * len(mine)
        ok = ok and good
        say("  {:<9} trajectories {:>5}  L0 present {:>5}  DTREF tasks {:>5} of {:>5}  {}".format(
            row, len(mine), have0, have, 2 * len(mine), "complete" if good else "INCOMPLETE"))
    if not ok:
        say("\n  INCOMPLETE: analysis refused (A1). Nothing computed. Exit 7.")
        return 7
    bad = b_run(rts, L0, DT)
    E = {0: dict((t, e_of(r)) for t, r in L0.items())}
    for lev in LEVELS:
        E[lev] = dict((rt["tid"], e_of(DT["{}|L{}".format(rt["tid"], lev)])) for rt in rts)
    by_row = dict((row, [c for c in cells if c["row"] == row]) for row in rows)
    analyse(by_row, E, bad, a.workers, status)
    hdr("dtref_analysis done, exit 0  (nothing written)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
