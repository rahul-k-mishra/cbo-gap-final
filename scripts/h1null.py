"""
h1null.py  --  CBO-GAP: does sizetest's ELSEWHERE class say something about the
run's references, or only about H1 as a test?  EXPLORATORY, POST HOC  (ledger
N40; Rahul's instruction 2026-10-31)

WHY THIS IS POST HOC
--------------------
sizetest analyse (logs/sizetest-analyse-20261031.log) classed 14 of 56
affected cells and 19 of 53 control cells ELSEWHERE: H1 failed there. H1 was
found mis-specified only after that result was read (ledger N40, "H1 IS
MIS-SPECIFIED"). Every test below was therefore written after the outcome it
examines was seen. Nothing here is confirmatory; the output says so in its
first and last lines. sizetest's pre-specified classification stays the
reported result.

THE QUESTION
------------
Each selected cell has two sets of the same quantity, ratio = (ESS fraction
of a 50000-particle t = 0 ensemble at the run beta) / tau_0:
  RUN  the 15 run realizations' audit_ref_ratio (rerun shards, read as
       refratio2 R1 and sizetest G1 read them);
  E1   48 fresh draws at N 50000 with calprec2's sampler (sizetest E1).
If the run's references are what calprec2's sampler gives, the 63 values of
a cell are independent draws from one distribution (exchangeable). H1 asked
whether the run median lies inside the 95% bootstrap interval of the E1
median, and ignored the run median's own spread. This script measures how
often H1 fails when the two sets do come from one distribution, and replaces
it by a test whose rate under that null is known.

WHAT IS READ (committed files only; nothing is drawn; nothing is written)
  --plan-from  runs/sizetest-plan-20261031-033830 (sizetest read_plan: the
               sha256.txt verifies; 109 cells; row, why, cell, run_median,
               ratio_ref, adequate).
  --e1         the fetched E1 folders (sizetest read_run_folders: A1 exactly
               as analyse, every planned (cell, N, rep) complete once).
  --runs       the rerun shard folders the plan used (default: the plan's
               own "runs" parameter, under runs/); refratio2 read_folder.
  --analysis   the analysis folder the plan used (default: the plan's
               "analysis" parameter); refratio2 load_gate.
  --analyse-log  logs/sizetest-analyse-20261031.log, for X1.

IDENTITY CHECKS (before any test; exit 3 on failure)
  G1  per run cell, the mean of its realizations in rep order equals
      analysis_audit.csv's ref_ratio_mean within 1e-12 x max(1, |x|), and
      the cell counts per row equal the gate's (as sizetest G1).
  RM  per plan cell, np.median of its run values equals the plan's
      run_median exactly (as floats), and it has 15 realizations (sizetest
      M_RERUN). Worked example: plan 1.0101123, recomputed 1.0101123: pass;
      1.0101124: exit 3.
  X1  ANALYSE REPRODUCTION. For every plan cell, sizetest's own bootstrap
      (sizetest.boot_median, same seeds, B 10000) and analyse's class rule
      are recomputed here and must give the log's class, J_needed and
      "affected"/"control" for that cell, in plan order; the cell column is
      compared on its first 38 characters, as printed. This proves that
      the H1 examined below is the H1 that produced the 14 and the 19.
      Worked example: log "200000  SIZE (affected)", recomputed SIZE,
      200000, affected: pass; anything else: exit 3.
  NULL RATE (G1, RM, X1): null = the files are the committed ones and the
      code is sizetest's; all three are deterministic equalities, so they
      fire with probability 0 under it (no sampling enters them).

PARTS (all per cell, in parallel over cells; seeds below)
  P1  SPREAD (description). For RUN (15 values) and E1 at 50000 (48): the
      median, the interquartile range (np.percentile 25 and 75), and the
      bootstrap standard deviation of the median (B 10000 resamples with
      replacement; np.std, ddof 0). se_ratio = sd(run median) / sd(E1
      median). No threshold. Worked example: run IQR 0.20, E1 IQR 0.18,
      sd 0.040 and 0.022: se_ratio 1.82, the run median is the noisier one.
  P2  H1 NULL RATE. Pool the cell's 63 values. For p = 0 .. PERM_H1 - 1:
      permute the pool, call the first 15 "run" and the other 48 "E1",
      and apply H1 exactly as sizetest analyse: the run median inside
      [2.5th, 97.5th] percentile (np.percentile, default linear) of B 10000
      bootstrap medians of the 48, indices integers(0, 48, (B, 48)). f_c =
      failures / PERM_H1 is H1's failure rate in that cell when there is
      no difference. Its Monte Carlo standard error is at most
      sqrt(0.25 / PERM_H1).
      Per group (affected, control), with the cells independent: expected
      failures E = sum of f_c; the observed failures F (from X1: the
      ELSEWHERE count); and q = P(X >= F), X Poisson-binomial with the f_c
      (exact convolution). READING: q > 0.05: "H1 fails no more often in
      this group than it does with no difference"; q <= 0.05: "H1 fails
      more often in this group than its null rate". Neither reading says
      the references agree (CLAUDE.md rule 10). Worked example
      (illustrative values): 53 cells each with f_c 0.33, E 17.5, F 19: q
      is the upper tail at 19, read against 0.05.
      NULL RATE: null = H1's failures are draws with the cells' own rates
      f_c; then P(q <= 0.05) <= 0.05 by the definition of an upper tail,
      exactly if the f_c were known. They are estimated from PERM_H1
      shuffles, so the bound is approximate; the s.e. is printed.
  P3  TWO-SAMPLE PERMUTATION TEST (the replacement for H1). Statistic T =
      |median(RUN) - median(E1 at 50000)|. Null: the 63 values are
      exchangeable. PERM_TEST random permutations of the pool, each split
      15 / 48 as in P2; k = number with T_perm >= T_obs x (1 - 1e-12)
      (the factor keeps exact float ties counted); p = (1 + k) / (1 +
      PERM_TEST). Two-sided (the statistic is an absolute difference).
      REJECT at ALPHA = 0.05 iff p <= 0.05. Under the null its size is at
      most 0.05 by construction (the +1 makes the test valid, and
      conservative under discreteness); no simulation is needed for that.
      The smallest p it can give is 1 / (1 + PERM_TEST). Worked example:
      PERM_TEST 20000, k 150: p = 151 / 20001 = 0.00755: reject; k 1500:
      p 0.075: do not reject. Not rejecting is not agreement (rule 10).
      NULL RATE: null = the cell's 63 values are exchangeable; P(reject) <=
      0.05 by construction of the permutation p-value with the +1 (each
      cell); no simulation is needed.
  HEADLINE (decides correctness finding against test artefact). R = P3
      rejections among the CONTROL cells, n = their number. Under the
      null, every control rejects with probability at most 0.05,
      independently, so R is at most Binomial(n, 0.05) in distribution.
      p_up = P(Binomial(n, 0.05) >= R), exact (math.comb). VERDICT:
        p_up <= 0.001   WELL ABOVE THE NOMINAL LEVEL. More control cells
                        differ from fresh sampler draws than chance allows:
                        the run's references are not what calprec2's
                        sampler gives at 50000. A correctness finding about
                        CONC and TAU8.
        p_up >  0.05    NOT ABOVE THE NOMINAL LEVEL. The test finds no more
                        control differences than chance gives. This does
                        not show the references agree (rule 10).
        otherwise       UNCLEAR. Neither reading is supported.
      NULL RATE: null = P3's null in every control, cells independent;
      then R is stochastically at most Binomial(n, 0.05), so WELL ABOVE is
      reached with probability at most 0.001 and NOT ABOVE is the verdict
      with probability at least 0.95, by construction. The same rule is printed
      for the affected cells and for all cells, as secondary lines: in an
      affected cell the size effect is the same for RUN and E1 (both at
      50000), so a P3 rejection there means the same as in a control.
      Worked examples (illustrative values): n 53, R 2, p_up 0.5: NOT
      ABOVE; R 6, p_up 0.03: UNCLEAR; R 12, p_up 0.00002: WELL ABOVE.
  P4  WITHOUT THE RUN (description, sizetest's own rule minus H1). Per cell
      m(N) = np.median of E1's 48 ratios at N. OFF AT 50000 iff
      |m(50000) / ratio_ref - 1| > 0.05. J_needed = the smallest ladder N
      with |m(N') / ratio_ref - 1| <= 0.05 at N and every larger N' (J1).
      Counts per group: off at 50000; of those, J_needed by ladder size or
      none; of each, how many are "not adequate". This uses only E1 and
      calprec2's table, so H1's defect does not touch it. Worked example:
      ratio_ref 0.99, m 1.23, 1.10, 1.03, 1.01: off at 50000, J_needed
      1000000.

SEEDS (all from numpy.random.SeedSequence; cell index ci from the plan)
  X1  sizetest.boot_median: SeedSequence([20261030, 6, ci, level index]).
  P1  SeedSequence([20261031, 1, ci, 0]) (RUN), ([20261031, 1, ci, 1]) (E1).
  P2  permutations SeedSequence([20261031, 2, ci]); bootstrap of
      permutation p SeedSequence([20261031, 3, ci, p]).
  P3  SeedSequence([20261031, 4, ci]).

PRE-SPECIFIED VALUES: PERM_H1 1000, PERM_TEST 20000, ALPHA 0.05, verdict
cut-offs 0.001 and 0.05, NEAR 0.05 (sizetest's), B 10000 (sizetest's). The
flags --perm-h1 and --perm-test exist for the synthetic fixture; any other
value is printed as "NOT THE PRE-SPECIFIED VALUE" and the run is not the
registered one.

EXIT CODES
  0  ran to the end.
  2  bad argument; a folder, manifest or log problem; incomplete input.
  3  an identity check failed: G1, RM or X1.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only; writes nothing)
    python -B scripts/h1null.py --workers 2 --plan-from runs/sizetest-plan-... \\
        --e1 runs/... --e1 runs/... --analyse-log logs/sizetest-analyse-....log
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import io                                                       # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import re                                                       # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sizetest as S                                            # noqa: E402

C2 = S.C2
REPO = S.REPO
SEED = 20261031
PERM_H1 = 1000
PERM_TEST = 20000
ALPHA = 0.05
CUT_WELL = 0.001
CUT_NOT = 0.05
N_RUN = S.M_RERUN
CLASSES = ("SIZE, NOT CONVERGED", "SIZE", "NOT A MISS AT 50000", "ELSEWHERE")
ROW_RE = re.compile(r"^  (CONC|TAU8)\s+(\S+)\s+(.*)$")
TAIL_RE = re.compile(r"\s(\S+)\s+(SIZE, NOT CONVERGED|SIZE|NOT A MISS AT 50000|ELSEWHERE) "
                     r"\((affected|control)\)(  \[not adequate\])?\s*$")

Stop = S.Stop
say = S.say
hdr = S.hdr
fmt = S.fmt


# ----------------------------------------------------------------------
# reads
# ----------------------------------------------------------------------

def run_values(runs, analysis, pool):
    """G1. {(row, cell id): [values in rep order]} for every CONC and TAU8 run cell."""
    S.laptop_imports()
    R2 = S.R2
    res = pool.map(R2.read_folder, runs, chunksize=1)
    for folder, nf, cnt, recs in res:
        if isinstance(recs, R2.Stop):
            raise Stop(recs.code, recs.msg)
    cells = {}
    for folder, nf, cnt, recs in res:
        say("  run  {}  {} files verified; CONC {}, TAU8 {}".format(
            os.path.basename(folder), nf, cnt["CONC"], cnt["TAU8"]))
        for key, rep, v, path in recs:
            if key[0] not in S.ROWS:
                continue
            d = cells.setdefault(key, {})
            if rep in d:
                raise Stop(2, "duplicate (cell, rep): {} rep {}".format(key, rep))
            d[rep] = v
    gate = S.r2call(R2.load_gate, analysis)
    out = {}
    for key, d in cells.items():
        gk = (key[0], key[2], key[3], key[4], key[5])
        if gk not in gate:
            raise Stop(3, "G1: cell not in analysis_audit.csv: {}".format(gk))
        reps = sorted(d)
        if reps != list(range(len(reps))):
            raise Stop(2, "cell {}: reps not 0..n-1".format(gk))
        v = np.array([d[r] for r in reps])
        want, n = gate[gk]
        if n != len(reps) or abs(float(v.mean()) - want) > 1e-12 * max(1.0, abs(want)):
            raise Stop(3, "G1: {}: mean {!r} n {}, analysis {!r} n {}".format(gk, float(v.mean()), len(reps), want, n))
        ck = (key[0], C2.cell_id(S.cal_cell(key[0], key)))
        if ck in out:
            raise Stop(2, "two run cells map to {}".format(ck))
        out[ck] = [float(x) for x in v]
    for r in S.ROWS:
        ng = sum(1 for k in gate if k[0] == r)
        nh = sum(1 for k in out if k[0] == r)
        if nh != ng:
            raise Stop(3, "G1: {} cells here {}, in analysis_audit.csv {}".format(r, nh, ng))
        say("  G1 PASS  {:<5} {} cells, every mean equal to analysis_audit.csv".format(r, nh))
    return out


def read_log(path, cells):
    """X1 input: per plan cell, (row, cell[:38], J_needed token, class, why), in plan order."""
    if not os.path.isfile(path):
        raise Stop(2, "{}: no such log".format(path))
    with io.open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    try:
        i0 = next(i for i, s in enumerate(lines) if s.startswith("E1  per cell"))
        i1 = next(i for i, s in enumerate(lines) if i > i0 and s.startswith("SUMMARY"))
    except StopIteration:
        raise Stop(2, "{}: no E1 table or no SUMMARY (not a sizetest analyse log)".format(path))
    if not any("sizetest.py analyse done, exit 0" in s for s in lines[i1:]):
        raise Stop(2, "{}: analyse did not end with exit 0".format(path))
    out = []
    for s in lines[i0:i1]:
        m = ROW_RE.match(s)
        if not m:
            continue
        t = TAIL_RE.search(s)
        if not t:
            raise Stop(2, "{}: unreadable table row: {!r}".format(path, s[:80]))
        out.append((m.group(1), m.group(2), t.group(1), t.group(2), t.group(3)))
    if len(out) != len(cells):
        raise Stop(2, "{}: {} table rows, plan has {} cells".format(path, len(out), len(cells)))
    return out


# ----------------------------------------------------------------------
# per-cell work (in workers)
# ----------------------------------------------------------------------

def classify(meds, run_median, ratio_ref, ladder):
    """sizetest analyse's H1, J1 and class rule, for X1 and P4."""
    i50 = ladder.index(S.RUN_JINF)
    m50 = meds[i50]
    h1 = m50[1] <= run_median <= m50[2]
    off = abs(m50[0] / ratio_ref - 1.0) > S.NEAR
    near = [abs(meds[li][0] / ratio_ref - 1.0) <= S.NEAR for li in range(len(ladder))]
    jn = None
    for li in range(len(ladder)):
        if all(near[li:]):
            jn = ladder[li]
            break
    if not h1:
        cl = "ELSEWHERE"
    elif not off:
        cl = "NOT A MISS AT 50000"
    elif jn is not None:
        cl = "SIZE"
    else:
        cl = "SIZE, NOT CONVERGED"
    return h1, off, jn, cl


def h1_holds(run_part, e1_part, rng):
    """H1 exactly as sizetest analyse, with the bootstrap drawn from rng."""
    ix = rng.integers(0, e1_part.size, (S.B, e1_part.size))
    bm = np.median(e1_part[ix], axis=1)
    return float(np.percentile(bm, 2.5)) <= float(np.median(run_part)) <= float(np.percentile(bm, 97.5))


def boot_sd(v, ss):
    ix = np.random.default_rng(ss).integers(0, v.size, (S.B, v.size))
    return float(np.std(np.median(v[ix], axis=1)))


def cell_job(args):
    ci, run, e1, run_median, ratio_ref, ladder, perm_h1, perm_test = args
    run = np.array(run, dtype=float)
    lev = [np.array(e1[li], dtype=float) for li in range(len(ladder))]
    # X1: analyse's bootstrap and classes
    meds = []
    for li in range(len(ladder)):
        _c, _l, m_, lo, hi = S.boot_median((ci, li, list(lev[li])))
        meds.append((m_, lo, hi))
    h1, off, jn, cl = classify(meds, run_median, ratio_ref, ladder)
    e50 = lev[ladder.index(S.RUN_JINF)]
    nr = run.size
    # P1
    p1 = {"run_med": float(np.median(run)), "e1_med": float(np.median(e50)),
          "run_iqr": float(np.percentile(run, 75) - np.percentile(run, 25)),
          "e1_iqr": float(np.percentile(e50, 75) - np.percentile(e50, 25)),
          "run_sd": boot_sd(run, np.random.SeedSequence([SEED, 1, ci, 0])),
          "e1_sd": boot_sd(e50, np.random.SeedSequence([SEED, 1, ci, 1]))}
    pool_ = np.concatenate([run, e50])
    # P2
    rp = np.random.default_rng(np.random.SeedSequence([SEED, 2, ci]))
    fails = 0
    for p in range(perm_h1):
        x = pool_[rp.permutation(pool_.size)]
        rb = np.random.default_rng(np.random.SeedSequence([SEED, 3, ci, p]))
        if not h1_holds(x[:nr], x[nr:], rb):
            fails += 1
    # P3
    t_obs = abs(float(np.median(run)) - float(np.median(e50)))
    rt = np.random.default_rng(np.random.SeedSequence([SEED, 4, ci]))
    k = 0
    done = 0
    while done < perm_test:
        m = min(2000, perm_test - done)
        x = rt.permuted(np.tile(pool_, (m, 1)), axis=1)
        t = np.abs(np.median(x[:, :nr], axis=1) - np.median(x[:, nr:], axis=1))
        k += int(np.sum(t >= t_obs * (1.0 - 1e-12)))
        done += m
    pv = (1.0 + k) / (1.0 + perm_test)
    return {"ci": ci, "meds": meds, "h1": h1, "off": off, "jn": jn, "cl": cl, "p1": p1,
            "f_c": fails / float(perm_h1), "t_obs": t_obs, "k": k, "p": pv, "reject": pv <= ALPHA,
            "rss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0}


# ----------------------------------------------------------------------
# tails
# ----------------------------------------------------------------------

def binom_upper(n, r, a):
    """P(Binomial(n, a) >= r), exact."""
    if r <= 0:
        return 1.0
    return float(sum(math.comb(n, j) * a ** j * (1.0 - a) ** (n - j) for j in range(r, n + 1)))


def poibin_upper(ps, r):
    """P(X >= r), X a sum of independent Bernoulli(ps), by convolution."""
    dist = [1.0]
    for p in ps:
        nd = [0.0] * (len(dist) + 1)
        for j, q in enumerate(dist):
            nd[j] += q * (1.0 - p)
            nd[j + 1] += q * p
        dist = nd
    return float(sum(dist[r:])) if r < len(dist) else 0.0


def verdict(p_up):
    if p_up <= CUT_WELL:
        return "WELL ABOVE THE NOMINAL LEVEL"
    if p_up > CUT_NOT:
        return "NOT ABOVE THE NOMINAL LEVEL"
    return "UNCLEAR"


VERDICT_MEANS = {
    "WELL ABOVE THE NOMINAL LEVEL": [
        "More control cells differ from fresh calprec2-sampler draws at 50000 than chance allows.",
        "The run's references are not what calprec2's sampler gives at 50000: a correctness",
        "finding about CONC and TAU8, not a calibration note. ELSEWHERE is not only H1's artefact."],
    "NOT ABOVE THE NOMINAL LEVEL": [
        "The valid test finds no more control differences than chance gives at its level.",
        "This does not show that the references agree with the sampler (rule 10); it shows",
        "that this test, at this size, finds no excess. Read P2 for whether H1's failures are",
        "within H1's own null rate."],
    "UNCLEAR": [
        "More control rejections than expected, but not so many that chance is ruled out at",
        "the 0.001 cut-off. Neither a correctness finding nor a test artefact is supported."],
}


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="H1 null rate and a valid two-sample test (N40; exploratory)")
    ap.add_argument("--plan-from", required=True)
    ap.add_argument("--e1", action="append", default=[])
    ap.add_argument("--runs", action="append", default=[])
    ap.add_argument("--analysis", default=None)
    ap.add_argument("--analyse-log", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--perm-h1", type=int, default=PERM_H1)
    ap.add_argument("--perm-test", type=int, default=PERM_TEST)
    a = ap.parse_args()
    if a.workers < 1 or a.perm_h1 < 1 or a.perm_test < 1:
        raise Stop(2, "--workers, --perm-h1 and --perm-test must be at least 1")
    if not a.e1:
        raise Stop(2, "at least one --e1 folder is required")

    banner = "EXPLORATORY, POST HOC: written after H1's failures were seen (ledger N40). Not confirmatory."
    hdr("h1null.py  (ledger N40)  --  writes nothing\n" + banner)
    say("  script sha256   {}".format(S.sha256_of(os.path.abspath(__file__))))
    say("  sizetest sha256 {}".format(S.sha256_of(os.path.abspath(S.__file__))))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  workers         {}".format(a.workers))
    for name, val, want in (("perm-h1", a.perm_h1, PERM_H1), ("perm-test", a.perm_test, PERM_TEST)):
        say("  {:<15} {}{}".format(name, val, "" if val == want else
                                    "   NOT THE PRE-SPECIFIED VALUE ({}): not the registered run".format(want)))
    say("  alpha           {}   verdict cut-offs {} and {}   near {}   B {}".format(
        ALPHA, CUT_WELL, CUT_NOT, S.NEAR, S.B))
    say("  seeds           X1 SeedSequence([20261030, 6, ci, li]) (sizetest's); P1 ([{0}, 1, ci, 0|1]);"
        " P2 ([{0}, 2, ci]) and ([{0}, 3, ci, p]); P3 ([{0}, 4, ci])".format(SEED))

    hdr("What this does, in plain words")
    for s in (
            "Each cell has 15 run values and 48 fresh values of the same quantity: the concentration",
            "of a 50000-particle starting sample at the run's beta, over the target. If the run's",
            "samples are what calprec2's sampler gives, both sets are draws from one distribution.",
            "",
            "sizetest's H1 asked whether the run's median sits inside an interval built for the fresh",
            "median alone. It forgot that the run's median, from only 15 values, wobbles too. So H1",
            "can fail when nothing is wrong. This script does three things:",
            "  - it measures how often H1 fails when nothing is wrong, by shuffling each cell's 63",
            "    values between the two sets and applying H1 to the shuffles (P2);",
            "  - it tests each cell with a shuffle test whose false-alarm rate is at most 5% by",
            "    construction (P3);",
            "  - it counts, in the cells where the run met its target (the controls), how many such",
            "    alarms there are. If that count is far above 5% of the controls, the run's samples",
            "    differ from the sampler's: a correctness finding. If not, ELSEWHERE came from H1.",
            "That count is the HEADLINE. P4 restates the size result without using the run at all."):
        say("  " + s)

    plan = os.path.abspath(a.plan_from)
    cells, pp, psha = S.read_plan(plan)
    ladder, draws = pp["ladder"], pp["draws"]
    prm = S.read_kv(os.path.join(plan, [r for r in S.verified(plan) if os.path.basename(r) == S.PLAN_PARAMS][0]))
    runs = [os.path.abspath(x) for x in a.runs] or [os.path.join(REPO, "runs", x) for x in prm.get("runs", "").split(";")
                                                    if x]
    analysis = os.path.abspath(a.analysis) if a.analysis else os.path.join(REPO, "runs", prm.get("analysis", ""))
    if not runs or not prm.get("analysis") and not a.analysis:
        raise Stop(2, "no --runs or --analysis, and the plan names none")
    logp = os.path.abspath(a.analyse_log)

    hdr("Inputs and identity checks  (A1, G1, RM, X1)")
    say("  plan     {}   {} sha256 {}".format(a.plan_from, S.PLAN_CSV, psha))
    say("  cells {}   ladder {}   draws {}".format(len(cells), ",".join(str(n) for n in ladder), draws))
    say("  analyse log {}  sha256 {}".format(a.analyse_log, S.sha256_of(logp) if os.path.isfile(logp) else "-"))
    log = read_log(logp, cells)
    folders = [os.path.abspath(x) for x in a.e1]
    if len(set(folders)) != len(folders):
        raise Stop(2, "a folder is given twice")
    store, ref = S.read_run_folders(folders, None, None)
    if ref.get("plan_sha256") != psha or ref.get("ladder") != ",".join(str(n) for n in ladder) \
            or ref.get("draws") != str(draws) or ref.get("kind") != str(S.K_E1):
        raise Stop(2, "A1: the folders' plan sha256, ladder, draws or kind are not the plan's")
    want = set(C2.tid_of("E1", p["c"], n, rep) for p in cells for n in ladder for rep in range(draws))
    extra, miss = sorted(set(store) - want), sorted(want - set(store))
    if extra or miss:
        raise Stop(2, "A1: {} extra, {} missing complete rows".format(len(extra), len(miss)))
    say("  A1 PASS  planned {}, complete {}; platform python {} numpy {}".format(
        len(want), len(store), ref.get("python"), ref.get("numpy")))

    pool = multiprocessing.Pool(processes=a.workers)
    try:
        rv = run_values(runs, analysis, pool)
        jobs = []
        for p in cells:
            k = (p["row"], p["cell"])
            if k not in rv:
                raise Stop(3, "RM: plan cell {} {} has no run values".format(*k))
            v = rv[k]
            if len(v) != N_RUN or float(np.median(np.array(v))) != p["run_median"]:
                raise Stop(3, "RM: {} {}: {} values, median {!r}, plan {!r}".format(
                    p["row"], p["cell"], len(v), float(np.median(np.array(v))), p["run_median"]))
            e1 = [[float(store[C2.tid_of("E1", p["c"], n, rep)]["ratio"]) for rep in range(draws)] for n in ladder]
            jobs.append((p["index"], v, e1, p["run_median"], p["ratio_ref"], ladder, a.perm_h1, a.perm_test))
        say("  RM PASS  {} plan cells, {} run values each, every median equal to the plan's".format(len(cells), N_RUN))
        res = pool.map(cell_job, jobs, chunksize=1)
    finally:
        pool.close()
        pool.join()
    res.sort(key=lambda r: r["ci"])

    for p, r, lg in zip(cells, res, log):
        got = (p["row"], p["cell"][:38], str(r["jn"]) if r["jn"] else "none", r["cl"], p["why"])
        if got != lg:
            raise Stop(3, "X1: cell {} recomputed {}, log {}".format(p["cell"], got, lg))
    say("  X1 PASS  every cell's class, J_needed and group equal the analyse log's")
    say("  largest per-worker peak RSS {:.1f} MB".format(max(r["rss"] for r in res)))

    groups = [("control", [i for i, p in enumerate(cells) if p["why"] == "control"]),
              ("affected", [i for i, p in enumerate(cells) if p["why"] == "affected"]),
              ("all", list(range(len(cells))))]
    st = {}
    for g, ix in groups:
        n = len(ix)
        rj = sum(1 for i in ix if res[i]["reject"])
        f = sum(1 for i in ix if not res[i]["h1"])
        pu = binom_upper(n, rj, ALPHA)
        st[g] = {"n": n, "R": rj, "p_up": pu, "verdict": verdict(pu), "F": f,
                 "E": sum(res[i]["f_c"] for i in ix), "q": poibin_upper([res[i]["f_c"] for i in ix], f)}

    c = st["control"]
    if c["n"] == 0:
        raise Stop(2, "the plan has no control cells: the headline is undefined")
    hdr("HEADLINE  (P3 in the control cells; decides correctness finding against test artefact)\n" + banner)
    say("")
    say("  CONTROLS: {} of {} rejected by the valid test at alpha {}.".format(c["R"], c["n"], ALPHA))
    say("  P(Binomial({}, {}) >= {}) = {:.3g}".format(c["n"], ALPHA, c["R"], c["p_up"]))
    say("")
    say("  >>> {} <<<".format(c["verdict"]))
    for s in VERDICT_MEANS[c["verdict"]]:
        say("      " + s)
    say("")
    for g in ("affected", "all"):
        x = st[g]
        if x["n"] == 0:
            say("  secondary, {:<8}: no cells".format(g))
            continue
        say("  secondary, {:<8}: {} of {} rejected; P(Binomial({}, {}) >= {}) = {:.3g}: {}".format(
            g, x["R"], x["n"], x["n"], ALPHA, x["R"], x["p_up"], x["verdict"]))

    hdr("P2  how often H1 fails when there is no difference")
    say("  f_c per cell from {} shuffles (Monte Carlo s.e. at most {:.3f}); E = expected H1 failures,".format(
        a.perm_h1, math.sqrt(0.25 / a.perm_h1)))
    say("  F = observed (ELSEWHERE), q = P(X >= F) under the null rates")
    for g in ("control", "affected"):
        x = st[g]
        if x["n"] == 0:
            say("  {:<8}  no cells".format(g))
            continue
        rd = ("H1 fails no more often here than it does with no difference" if x["q"] > 0.05 else
              "H1 fails more often here than its null rate")
        say("  {:<8}  cells {:>3}   mean f_c {:.3f}   E {:.1f}   F {:>3}   q {:.3g}:  {}".format(
            g, x["n"], x["E"] / x["n"], x["E"], x["F"], x["q"], rd))

    hdr("P1, P2, P3 per cell")
    say("  {:<5} {:<38} {:>8} {:>8} {:>7} {:>7} {:>7} {:>7} {:>6} {:>6} {:>8}  {:<8} {}".format(
        "row", "cell", "run med", "E1 med", "run IQR", "E1 IQR", "run sd", "E1 sd", "se rt", "f_c", "P3 p",
        "group", "analyse class"))
    for p, r in zip(cells, res):
        q = r["p1"]
        say("  {:<5} {:<38} {:>8} {:>8} {:>7} {:>7} {:>7} {:>7} {:>6} {:>6} {:>8}  {:<8} {}{}".format(
            p["row"], p["cell"][:38], fmt(q["run_med"]), fmt(q["e1_med"]), fmt(q["run_iqr"]), fmt(q["e1_iqr"]),
            fmt(q["run_sd"]), fmt(q["e1_sd"]),
            "{:.2f}".format(q["run_sd"] / q["e1_sd"]) if q["e1_sd"] > 0 else "inf",
            "{:.3f}".format(r["f_c"]), "{:.5f}".format(r["p"]), p["why"], r["cl"],
            "  REJECT" if r["reject"] else ""))

    hdr("P4  the size result without the run (E1 against calprec2's table only)")
    for g in ("affected", "control"):
        ix = [i for i, p in enumerate(cells) if p["why"] == g]
        off = [i for i in ix if res[i]["off"]]
        say("  {:<8} cells {:>3}: off at 50000 {:>3} (not adequate {:>2}); not off {:>3}".format(
            g, len(ix), len(off), sum(1 for i in off if not cells[i]["adequate"]), len(ix) - len(off)))
        say("           of the off cells, J_needed: " + ", ".join(
            "{} {}".format(n, sum(1 for i in off if res[i]["jn"] == n)) for n in ladder) +
            ", none {}".format(sum(1 for i in off if res[i]["jn"] is None)))

    hdr("h1null.py done, exit 0\n" + banner + "\nHEADLINE: controls {} of {}, {}".format(
        c["R"], c["n"], c["verdict"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
