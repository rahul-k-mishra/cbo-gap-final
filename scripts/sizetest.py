"""
sizetest.py  --  CBO-GAP: is the calibrated rows' miss at tight targets a
reference-size effect?  E0 (a read), E1 (a measurement), and the plan for a
larger-reference rerun  (ledger N40; Rahul's instruction 2026-10-30)

THE QUESTION
------------
refratio2 (logs/refratio2-20261030.log) found that CONC and TAU8, whose beta
calprec2 calibrated, miss their target concentration on the run's own
reference ensemble in some cells, mostly at tight tau_0 and d 40. Claude's
reading: calprec2 calibrates the median ESS fraction on references of
64,000,000 particles, while every CONC and TAU8 run uses J_inf = 50000; at
tight targets the fraction of a 50000-particle sample differs from the
large-sample value. That is a reading, not a test. This script tests it.

WHAT IS A READ AND WHAT IS A MEASUREMENT
----------------------------------------
  READ (committed files only; nothing drawn):
    - the run's reference ratios, from the rerun shards (as refratio2, with
      its gate against the twenty-one-row analysis);
    - calprec2's table (runs/calprec2-finalize-20261023-112503): each cell's
      beta, label and tau_ref (its large-sample median fraction);
    - E0: calprec2's phase A, which solved beta on 24 independent draws at
      each of N = 4000, 16000, 64000, 256000, 1000000, 4000000 for every
      cell (the 26 calprec2-long record folders);
    - measured costs: calprec2's throughput table (seconds per point to
      draw and to evaluate one beta), calprec2's own task walls and peak
      RSS, and costprobe2's trajectory walls and peak RSS at J_inf 50000.
  MEASUREMENT (E1, --mode run only): fresh initial ensembles of size N are
    drawn with calprec2's sampler (calprec2.f_chunk -> costprobe2.
    probe_sample, the archived samplers, verified line by line by calprec2
    V2) and the ESS fraction is evaluated at the cell's run beta with
    calprec2's streamed evaluation (chunks of 250000, log-sum-exp
    combination). NO TRAJECTORY IS EVOLVED: there are no time steps, no
    dynamics, no coupled error. Only t = 0 draws and one weight evaluation.
    Seeds: each draw (cell, N, rep) has the key calprec2.key_of(41, cell,
    N, rep); chunk ci of it uses default_rng(SeedSequence(key + [ci])),
    exactly as calprec2 seeds its own draws. Kind 41 is used by no other
    script (calprec2 uses 31, 32, 33, 35), so no E1 draw coincides with a
    calprec2 or rerun draw, and every E1 draw is reproducible from its key.

WRITES NOTHING. No file is written anywhere; the console is the record.

MODES
  --mode plan   reads, runs the gates, E0, and prints the cost of E1 at each
                ladder size and the plan for the larger-reference probe.
                Draws nothing. Run this first; Rahul approves the ladder and
                the draw count.
  --mode run    repeats everything in plan, then the positive control PC,
                then E1, with exactly the --ladder and --draws given.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-30)
  G1  RUN RATIOS, as refratio2 R1 and R2: the --runs folders verify; CONC and
      TAU8 rows only; per cell the mean in rep order equals
      analysis_audit.csv's ref_ratio_mean within 1e-12 x max(1,|x|); exit 3
      otherwise. The run median of a cell is np.median of its 15 ratios.
  G2  BETA IDENTITY: for every CONC and TAU8 cell, calprec2_beta.csv's beta
      for (module, objective, d, law, tau_0) equals the beta in the run's
      shards exactly (as floats); exit 3 otherwise. Module: CONC
      mechanism, TAU8 boundary.
  G3  ARCHIVE IDENTITY: the archived modules used (mechanism, boundary,
      exactcal) hash to costprobe2.ARCHIVE_SHA256; exit 2 otherwise.
  SEL SELECTION. ratio_ref = tau_ref / tau_0 from calprec2_beta.csv (the
      large-sample median fraction over target; 64M for "target" cells,
      the reported size for the others). A cell is AFFECTED iff its run
      median is not within 5% of 1 (|median - 1| > 0.05, refratio2's
      reading). CONTROLS (--controls, on by default) are the d 40 cells
      within 5%. Every selected cell is printed with its reason.
      Example: TAU8 levy d 40 tau_0 0.01, run median 1.2534: affected.
  E0  READ TEST of the direction, per selected cell. bmed(N) = median of
      phase A's 24 beta_solved at size N; q(N) = bmed(N) / beta_run. ESS
      fraction falls as beta rises, so if the run's 50000-particle fraction
      is above the large-sample one (s = run median / ratio_ref > 1), a
      50000 sample needs a larger beta to reach tau_0: the size reading
      predicts q > 1 at the two levels that bracket 50000 (16000, 64000);
      if s < 1 it predicts q < 1. Verdict for affected cells: "agrees" iff
      both levels are on the predicted side; "disagrees" iff both are on the
      other; else "mixed". Controls: q printed, no verdict. Phase A must
      have exactly 24 completed draws per (cell, N); exit 2 otherwise.
      Example: s 1.25, q(16000) 1.04, q(64000) 1.02: agrees.
  PC  POSITIVE CONTROL (--mode run, before E1). The lowest-sorted phase C
      row at N 64,000,000 among the selected cells is recomputed with
      calprec2's own key, sampler and streamed evaluation at its own betas;
      every log-ESS must equal the committed one within 1e-12 relative
      (calprec2's E1_TOL). Exit 3 otherwise: the E1 machinery would not be
      calprec2's on this machine.
  E1  MEASUREMENT, per selected cell and ladder size N: --draws fresh draws
      (default 48), ratio = (ESS fraction at beta_run) / tau_0; median, and
      its two-sided 95% percentile bootstrap interval (B 10000, indices
      default_rng(SeedSequence([20261030, 6, cell index, level index]))).
      The ladder must contain 50000, the run's J_inf; exit 2 otherwise.
      H1 (run consistency): the run median lies inside E1's interval at
      50000. "Off at 50000": |E1 median(50000) / ratio_ref - 1| > 0.05.
      J1: J_needed = the smallest ladder N such that |E1 median(N') /
      ratio_ref - 1| <= 0.05 at N and at every larger ladder N'; none if no
      such N. CLASS per cell:
        SIZE                      H1 holds, off at 50000, J_needed found;
        SIZE, NOT CONVERGED       H1 holds, off at 50000, no J_needed;
        NOT A MISS AT 50000       H1 holds, not off at 50000;
        ELSEWHERE                 H1 fails: fresh 50000-particle draws do
                                  not reproduce the run's reference.
      Cells whose calprec2 label says "not adequate" carry that flag: their
      ratio_ref is not a converged value (C5m or D1 failed at 64M/256M).
      Example: run median 1.25; E1 at 50000 median 1.23 [1.15, 1.31]; at
      200000 1.10; at 1M 1.03; at 4M 1.01; ratio_ref 0.99: H1 holds, off at
      50000, J_needed 1M: SIZE.
  PLAN (both modes, printed before anything is drawn):
      E1 cost per ladder size = sum over selected cells of draws x N x
      (t_draw + t_beta), from calprec2's throughput table (Kaggle, python
      3.13.15, numpy 2.1.3: a laptop is slower and the figure is labelled
      so); the PC cost likewise at 64M with its number of betas; the peak
      RSS bound is calprec2's own measured peak for the same streamed
      evaluation (phase C rows at 64M, d 40, same module).
      LARGER-REFERENCE PLAN: the affected d 40 cells, grouped by (module,
      objective, law); costprobe2's measured trajectory wall and peak RSS
      at J_inf 50000 for each group's unit; what is not measured; the probe
      needed (one realization per group at each candidate J_inf); the
      rerun's size (cells x 15 realizations at J_needed). J_needed comes
      from E1 (J1); in plan mode it is not yet known.

EXIT CODES
  0  ran to the end (plan or run).
  2  bad argument; folder, manifest or archive problem; unexpected or
     incomplete input; a missing throughput entry; 50000 not in the ladder.
  3  a gate failed: G1, G2 or PC.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/sizetest.py --mode plan --workers 2 --runs ... --cal ...
    python -B scripts/sizetest.py --mode run  --workers 2 --runs ... --cal ...
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import hashlib                                                  # noqa: E402
import io                                                       # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import refratio2 as R2                                          # noqa: E402
import calprec2 as C2                                           # noqa: E402

cp = C2.cp
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROWS = ("CONC", "TAU8")
MODULE = {"CONC": "mechanism", "TAU8": "boundary"}
K_E1 = 41
RUN_JINF = 50000
NEAR = 0.05
B = 10000
SEED0 = 20261030
M_RERUN = 15
DEFAULT_LADDER = "50000,200000,1000000,4000000"
DEFAULT_DRAWS = 48
DEFAULT_BETA_TABLE = os.path.join(REPO, "runs", "calprec2-finalize-20261023-112503")
DEFAULT_THROUGHPUT = os.path.join(REPO, "runs", "calprec2-smoke-kaggle-20261011-121225")
DEFAULT_COSTPROBE = [os.path.join(REPO, "runs", "costprobe2-s0-kaggle-20261010-103952"),
                     os.path.join(REPO, "runs", "costprobe2-s1-kaggle-20261011-101343")]


class Stop(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, code, msg)
        self.code = code
        self.msg = msg


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "=" * 100)
    say(s)
    say("=" * 100)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def r2call(fn, *a):
    try:
        return fn(*a)
    except R2.Stop as e:
        raise Stop(e.code, e.msg)


def fmt(x, k=4):
    return ("{:." + str(k) + "f}").format(x)


def cal_cell(row, key):
    """calprec2 cell tuple for a run cell key (refratio2 CELL_COLS)."""
    return (MODULE[row], key[2], int(key[3]), key[4], float(key[5]))


# ----------------------------------------------------------------------
# reads
# ----------------------------------------------------------------------

def run_medians(runs, analysis, pool):
    """G1. {(row, cal cell): {"beta", "tau0", "median", "n", "key"}}."""
    res = pool.map(R2.read_folder, runs, chunksize=1)
    for folder, nf, cnt, recs in res:
        if isinstance(recs, R2.Stop):
            raise Stop(recs.code, recs.msg)
    cells = {}
    for folder, nf, cnt, recs in res:
        say("  run  {}  {} files verified; CONC {}, TAU8 {}".format(
            os.path.basename(folder), nf, cnt["CONC"], cnt["TAU8"]))
        for key, rep, v, path in recs:
            if key[0] not in ROWS:
                continue
            d = cells.setdefault(key, {})
            if rep in d:
                raise Stop(2, "duplicate (cell, rep): {} rep {}".format(key, rep))
            d[rep] = v
    gate = r2call(R2.load_gate, analysis)
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
        c = cal_cell(key[0], key)
        out[(key[0], c)] = {"beta": float(key[11]), "beta_s": key[11], "tau0": float(key[5]),
                            "median": float(np.median(v)), "n": len(reps), "key": key}
    for r in ROWS:
        ng = sum(1 for k in gate if k[0] == r)
        nh = sum(1 for k in out if k[0] == r)
        if nh != ng:
            raise Stop(3, "G1: {} cells here {}, in analysis_audit.csv {}".format(r, nh, ng))
        say("  G1 PASS  {:<5} {} cells, every mean equal to analysis_audit.csv".format(r, nh))
    return out


def beta_table(folder):
    r2call(R2.manifest, folder)
    path = os.path.join(folder, "calprec2_beta.csv")
    if not os.path.isfile(path):
        raise Stop(2, "{}: no calprec2_beta.csv".format(folder))
    out = {}
    with io.open(path, "r", newline="", encoding="utf-8") as f:
        for x in csv.DictReader(f):
            try:
                out[x["cell"]] = {"beta": float(x["beta"]), "label": x["label"],
                                  "tau_ref": float(x["tau_ref"]), "tau_ref_n": x["tau_ref_n"]}
            except (KeyError, ValueError):
                raise Stop(2, "calprec2_beta.csv: unreadable row {}".format(x.get("cell")))
    return out


def read_cal_folder(folder):
    """Phase A beta_solved and phase C rows of one calprec2 record folder."""
    try:
        names = r2call(R2.manifest, folder)
        a, c = [], []
        for n in names:
            if os.path.basename(n) != "calprec2_tasks.csv":
                continue
            with io.open(os.path.join(folder, n), "r", newline="", encoding="utf-8") as f:
                for x in csv.DictReader(f):
                    if x["end"] != "ok":
                        continue
                    if x["phase"] == "A":
                        a.append((x["tid"], x["cell"], int(x["n"]), float(x["beta_solved"]),
                                  float(x["wall_s"]), float(x["rss_mb"])))
                    elif x["phase"] == "C":
                        c.append((x["tid"], x["cell"], int(x["n"]), x["key"], x["betas"], x["log_ess"],
                                  float(x["wall_s"]), float(x["rss_mb"])))
        return folder, a, c
    except Stop as e:
        return folder, None, e


def costprobe_units(folders):
    out = {}
    for folder in folders:
        names = r2call(R2.manifest, folder)
        for n in names:
            if os.path.basename(n) != "costprobe2_results.csv":
                continue
            with io.open(os.path.join(folder, n), "r", newline="", encoding="utf-8") as f:
                for x in csv.DictReader(f):
                    if x["kind"] != "main" or x["end"] != "ok":
                        continue
                    rows = set(x["rows"].split(";"))
                    if not rows & set(ROWS):
                        continue
                    k = (x["module"], x["objective"], int(x["d"]), x["law"])
                    out[k] = (float(x["wall_s"]), float(x["peak_rss_mb"]), x["J_inf"])
    return out


# ----------------------------------------------------------------------
# E1 work
# ----------------------------------------------------------------------

def e1_task(t):
    c, n, rep, beta, tau0 = t
    t0 = time.time()
    key = C2.key_of(K_E1, c, n, rep)
    per = []
    for ci, m in C2.chunks_of(n):
        per.append(C2.chunk_terms(C2.f_chunk(c, key, ci, m), [beta]))
    le = C2.log_ess_from(C2.combine_terms(per, 1)[0])
    return (c, n, rep, C2.tau_of(le, n) / tau0, time.time() - t0, C2.rss_mb())


def pc_task(t):
    c, n, key, betas = t
    t0 = time.time()
    per = []
    for ci, m in C2.chunks_of(n):
        per.append(C2.chunk_terms(C2.f_chunk(c, key, ci, m), betas))
    les = [C2.log_ess_from(r) for r in C2.combine_terms(per, len(betas))]
    return les, time.time() - t0, C2.rss_mb()


def boot_median(args):
    ci, li, vals = args
    v = np.array(vals, dtype=float)
    ix = np.random.default_rng(np.random.SeedSequence([SEED0, 6, ci, li])).integers(0, v.size, (B, v.size))
    bm = np.median(v[ix], axis=1)
    return ci, li, float(np.median(v)), float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="E0, E1 and the larger-reference plan (N40)")
    ap.add_argument("--mode", choices=("plan", "run"), required=True)
    ap.add_argument("--runs", action="append", default=[], help="rerun shard folder; repeat")
    ap.add_argument("--cal", action="append", default=[], help="calprec2 record folder; repeat")
    ap.add_argument("--analysis", default=R2.DEFAULT_ANALYSIS)
    ap.add_argument("--beta-table", default=DEFAULT_BETA_TABLE)
    ap.add_argument("--throughput", default=DEFAULT_THROUGHPUT)
    ap.add_argument("--costprobe", action="append", default=[])
    ap.add_argument("--ladder", default=DEFAULT_LADDER)
    ap.add_argument("--draws", type=int, default=DEFAULT_DRAWS)
    ap.add_argument("--no-controls", action="store_true")
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    a = ap.parse_args()
    try:
        ladder = sorted(set(int(x) for x in a.ladder.split(",") if x.strip()))
    except ValueError:
        raise Stop(2, "--ladder must be integers separated by commas")
    if RUN_JINF not in ladder:
        raise Stop(2, "--ladder must contain {} (the run's J_inf)".format(RUN_JINF))
    if a.draws < 2 or a.workers < 1:
        raise Stop(2, "--draws must be at least 2 and --workers at least 1")
    if not a.runs or not a.cal:
        raise Stop(2, "give the rerun folders (--runs) and the calprec2 record folders (--cal)")
    runs = [os.path.abspath(x) for x in a.runs]
    cals = [os.path.abspath(x) for x in a.cal]
    cps = [os.path.abspath(x) for x in (a.costprobe or DEFAULT_COSTPROBE)]
    for x in runs + cals + cps + [a.analysis, a.beta_table, a.throughput]:
        if not os.path.isdir(x):
            raise Stop(2, "not a folder: {}".format(x))
    if len(set(runs)) != len(runs) or len(set(cals)) != len(cals):
        raise Stop(2, "a folder is given twice")

    hdr("sizetest.py  (ledger N40)  mode {}  --  writes nothing".format(a.mode))
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))))
    say("  imports         refratio2 {}  calprec2 {}  costprobe2 {}".format(
        sha256_of(R2.__file__)[:16], sha256_of(C2.__file__)[:16], sha256_of(cp.__file__)[:16]))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  workers         {}".format(a.workers))
    say("  rows            CONC (mechanism), TAU8 (boundary)")
    say("  ladder          {}   draws per (cell, N) {}".format(", ".join(str(x) for x in ladder), a.draws))
    say("  near            |x - 1| <= {} (5%)".format(NEAR))
    say("  E1 seeds        calprec2.key_of({}, cell, N, rep); chunk ci: default_rng(SeedSequence(key + [ci]))".format(K_E1))
    say("  bootstrap       B {}, SeedSequence([{}, 6, cell index, level index])".format(B, SEED0))
    say("  controls        {}".format("off" if a.no_controls else "d 40 cells within 5%"))

    hdr("What this does, in plain words")
    for t in (
        "CONC and TAU8 were calibrated so that a very large sample (64 million particles) has",
        "the target concentration. The runs use 50000-particle references, and in some cells",
        "those references miss the target. The suspicion is that the miss is simply what a",
        "50000-particle sample does at that beta. This script checks that in two ways.",
        "",
        "E0 only reads. calprec2 already solved beta on samples of 16000 and 64000 particles.",
        "If the suspicion is right, those betas sit on a predictable side of the run's beta.",
        "",
        "E1 measures. It draws fresh starting samples of 50000 particles, and of larger sizes,",
        "from the same sampler, and computes their concentration at the run's beta. No",
        "algorithm is run: nothing moves, only the starting cloud is drawn and weighed. If the",
        "50000-particle draws reproduce the run's miss and the miss disappears as the sample",
        "grows, the cause is the reference size, and the size at which it disappears is the",
        "reference the affected cells would need. If fresh 50000-particle draws do not",
        "reproduce the run's miss, the cause is somewhere else.",
        "",
        "In plan mode nothing is drawn: the script prints what E1 would cost, and what a",
        "rerun with larger references would need measured first.",
    ):
        say("  " + t)

    pool = multiprocessing.Pool(processes=a.workers)
    try:
        hdr("Gates and reads  (G3, G1, G2)")
        for m in ("mechanism", "boundary", "exactcal"):
            want = cp.ARCHIVE_SHA256.get(m)
            got = sha256_of(cp.MODS[m].__file__)
            if want is None or got != want:
                raise Stop(2, "G3: archived {} hash {} does not match costprobe2's pin".format(m, got[:16]))
        say("  G3 PASS  mechanism, boundary, exactcal match costprobe2.ARCHIVE_SHA256")
        rm = run_medians(runs, os.path.abspath(a.analysis), pool)
        bt = beta_table(os.path.abspath(a.beta_table))
        for (row, c), r in rm.items():
            cid = C2.cell_id(c)
            if cid not in bt:
                raise Stop(2, "calprec2_beta.csv has no cell {}".format(cid))
            if bt[cid]["beta"] != r["beta"]:
                raise Stop(3, "G2: {} {}: table beta {!r}, run beta {}".format(row, cid, bt[cid]["beta"], r["beta_s"]))
            r["ratio_ref"] = bt[cid]["tau_ref"] / r["tau0"]
            r["label"] = bt[cid]["label"]
            r["adequate"] = "not adequate" not in bt[cid]["label"]
        say("  G2 PASS  every CONC and TAU8 run beta equals calprec2_beta.csv's")

        sel = []
        for (row, c), r in sorted(rm.items(), key=lambda z: (z[0][0], C2.cell_id(z[0][1]))):
            off = abs(r["median"] - 1.0) > NEAR
            if off:
                sel.append((row, c, "affected"))
            elif not a.no_controls and c[2] == 40:
                sel.append((row, c, "control"))
        hdr("Selection  (SEL)")
        say("  affected = run median not within 5% of 1; control = d 40 and within 5%")
        say("  {:<5} {:<38} {:>8} {:>9} {:>9}  {:<9} {}".format("row", "cell", "beta", "run med", "ratio_ref",
                                                                "why", "calprec2 label"))
        for row, c, why in sel:
            r = rm[(row, c)]
            say("  {:<5} {:<38} {:>8} {:>9} {:>9}  {:<9} {}".format(
                row, C2.cell_id(c)[:38], "{:.4g}".format(r["beta"]), fmt(r["median"]), fmt(r["ratio_ref"]), why,
                r["label"]))
        naff = sum(1 for s in sel if s[2] == "affected")
        say("  selected {}: affected {}, controls {}".format(len(sel), naff, len(sel) - naff))
        if not sel:
            raise Stop(2, "no cell selected")

        hdr("E0  calprec2 phase A betas against the run beta  (a read)")
        res = pool.map(read_cal_folder, cals, chunksize=1)
        A, Crows, seen = {}, [], set()
        for folder, aa, cc in res:
            if aa is None:
                raise cc
            for row_ in aa:
                if row_[0] in seen:
                    raise Stop(2, "phase A task {} found twice".format(row_[0]))
                seen.add(row_[0])
                A.setdefault((row_[1], row_[2]), []).append(row_)
            for row_ in cc:
                if row_[0] in seen:
                    raise Stop(2, "phase C task {} found twice".format(row_[0]))
                seen.add(row_[0])
                Crows.append(row_)
        say("  calprec2 folders read: {}; phase A tasks {}; phase C tasks {}".format(
            len(cals), sum(len(v) for v in A.values()), len(Crows)))
        say("  q(N) = median of 24 beta_solved at N / run beta;  s = run median / ratio_ref")
        say("  {:<5} {:<38} {:>7} ".format("row", "cell", "s") + "".join(
            "{:>10}".format("q " + str(n)) for n in C2.L_CAL) + "  verdict")
        e0 = {}
        for row, c, why in sel:
            r = rm[(row, c)]
            cid = C2.cell_id(c)
            q = {}
            for n in C2.L_CAL:
                v = A.get((cid, n), [])
                if len(v) != C2.R_CAL:
                    raise Stop(2, "phase A {} N {}: {} completed draws, expected {}".format(cid, n, len(v), C2.R_CAL))
                q[n] = float(np.median([x[3] for x in v])) / r["beta"]
            s = r["median"] / r["ratio_ref"]
            if why == "affected":
                pred_up = s > 1.0
                sides = [(q[n] > 1.0) == pred_up for n in (16000, 64000)]
                verdict = "agrees" if all(sides) else ("disagrees" if not any(sides) else "mixed")
            else:
                verdict = "(control)"
            e0[(row, c)] = verdict
            say("  {:<5} {:<38} {:>7} ".format(row, cid[:38], fmt(s)) + "".join(
                "{:>10}".format(fmt(q[n])) for n in C2.L_CAL) + "  " + verdict)
        say("  affected: agrees {}, mixed {}, disagrees {}".format(
            sum(1 for v in e0.values() if v == "agrees"), sum(1 for v in e0.values() if v == "mixed"),
            sum(1 for v in e0.values() if v == "disagrees")))

        hdr("PLAN  E1 cost from measured walls  (draws nothing)")
        thr = C2.load_throughput(os.path.abspath(a.throughput))
        say("  throughput: {} (Kaggle; python 3.13.15, numpy 2.1.3). Seconds per point:".format(
            os.path.basename(a.throughput)))
        say("  t_draw to draw and evaluate f, t_beta to weigh one beta. A laptop is slower;")
        say("  these are Kaggle figures and a lower bound (perfect scaling).")
        say("  {:>10} {:>8} {:>14} {:>16} {:>18}".format("N", "tasks", "core s", "wall s at W", "largest task s"))
        tot = 0.0
        for n in ladder:
            cs, big = 0.0, 0.0
            for row, c, why in sel:
                k = (c[0], c[1], c[2], c[3])
                if k not in thr:
                    raise Stop(2, "no throughput entry for {}".format(k))
                td, tb, _ts = thr[k]
                one = n * (td + tb)
                cs += a.draws * one
                big = max(big, one)
            tot += cs
            say("  {:>10} {:>8} {:>14} {:>16} {:>18}".format(
                n, a.draws * len(sel), "{:.1f}".format(cs), "{:.1f}".format(cs / a.workers), "{:.2f}".format(big)))
        pcrow = None
        selids = set(C2.cell_id(c) for _r, c, _w in sel)
        cand = sorted([x for x in Crows if x[1] in selids and x[2] == C2.N_LO], key=lambda x: x[0])
        if cand:
            pcrow = cand[0]
            pc_c = C2.cell_from_id(pcrow[1])
            td, tb, _ts = thr[(pc_c[0], pc_c[1], pc_c[2], pc_c[3])]
            nb = len(C2.floats(pcrow[4]))
            pc_cost = C2.N_LO * (td + nb * tb)
            tot += pc_cost
            say("  PC: {} at N {} with {} beta(s): {:.1f} s, one task (committed wall {:.1f} s, RSS {:.1f} MB)".format(
                pcrow[1], C2.N_LO, nb, pc_cost, pcrow[6], pcrow[7]))
        else:
            say("  PC: no phase C row at N {} among the selected cells; run mode will stop (exit 2)".format(C2.N_LO))
        say("  total core s {:.1f}; at {} workers {:.1f} s".format(tot, a.workers, tot / a.workers))
        say("  peak RSS bound, calprec2's measured peak for the same streamed evaluation (phase C, N 64M):")
        for m in sorted(set(c[0] for _r, c, _w in sel)):
            for d in sorted(set(c[2] for _r, c, _w in sel if c[0] == m)):
                rs = [x[7] for x in Crows if x[1].startswith(m + "|") and x[1].split("|")[2] == str(d)]
                say("    {:<10} d {:>3}: {}".format(m, d, "{:.1f} MB over {} tasks".format(max(rs), len(rs))
                                                     if rs else "not measured"))

        hdr("PLAN  larger-reference rerun of the affected d 40 cells  (draws nothing)")
        aff40 = [(row, c) for row, c, why in sel if why == "affected" and c[2] == 40]
        groups = {}
        for row, c in aff40:
            groups.setdefault((c[0], c[1], c[2], c[3]), []).append((row, c))
        cu = costprobe_units(cps)
        say("  affected d 40 cells: {} in {} (module, objective, law) groups".format(len(aff40), len(groups)))
        say("  measured trajectory cost per realization at J_inf 50000 (costprobe2 main units):")
        say("  {:<36} {:>6} {:>10} {:>12}".format("group", "cells", "wall s", "peak RSS MB"))
        for g in sorted(groups):
            u = cu.get(g)
            say("  {:<36} {:>6} {:>10} {:>12}".format(
                "|".join(str(x) for x in g), len(groups[g]),
                "{:.1f}".format(u[0]) if u else "not measured", "{:.1f}".format(u[1]) if u else "not measured"))
        say("  NOT MEASURED: any trajectory at d 40 with J_inf above 50000; any trajectory at any d")
        say("  above J_inf 100000 (REFSIZE, d 10, J <= 1250, is the largest measured).")
        say("  Arithmetic, not a measurement: one J_inf x d float64 array is J_inf x d x 8 bytes:")
        for n in ladder:
            if n > RUN_JINF:
                say("    J_inf {:>9}: {:.1f} MB per array at d 40".format(n, n * 40 * 8 / 1e6))
        cand_sizes = [n for n in ladder if n > RUN_JINF]
        say("  PROBE REQUIRED FIRST (rule 6): one realization of each group above at each candidate")
        say("  J_inf in {}, measuring wall and per-worker peak RSS: {} units.".format(
            ", ".join(str(n) for n in cand_sizes), len(groups) * len(cand_sizes)))
        say("  E1 decides J_needed per cell (J1); only the sizes it names need probing.")
        say("  RERUN AFTER THE PROBE: the affected d 40 cells at J_needed, the run's beta, {} realizations".format(M_RERUN))
        say("  each, as new rows with new seed keys: {} realizations; its cost is the probe's measured".format(
            len(aff40) * M_RERUN))
        say("  wall at J_needed times that count, printed by the probe's projection, not here.")
        say("  Cells labelled 'not adequate' have no converged ratio_ref; a larger J_inf cannot be")
        say("  judged against it.")

        if a.mode == "plan":
            hdr("sizetest.py plan done, exit 0  (nothing drawn)")
            return 0

        hdr("PC  positive control: recompute a committed calprec2 phase C row")
        if pcrow is None:
            raise Stop(2, "PC: no phase C row at N {} among the selected cells".format(C2.N_LO))
        key = tuple(int(x) for x in pcrow[3].split("-"))
        betas = C2.floats(pcrow[4])
        want = C2.floats(pcrow[5])
        les, wall, rss = pool.apply(pc_task, ((pc_c, C2.N_LO, key, betas),))
        worst = max(abs(x - y) / abs(y) if y != 0.0 else abs(x) for x, y in zip(les, want))
        if worst > C2.E1_TOL:
            raise Stop(3, "PC: {} log-ESS relative difference {:.3e} > {}".format(pcrow[0], worst, C2.E1_TOL))
        say("  PC PASS  {}: {} log-ESS values within {:.3e} (wall {:.1f} s, RSS {:.1f} MB)".format(
            pcrow[0], len(les), worst, wall, rss))

        hdr("E1  fresh draws, no trajectory  (a measurement)")
        tasks = [(c, n, rep, rm[(row, c)]["beta"], rm[(row, c)]["tau0"])
                 for row, c, _w in sel for n in ladder for rep in range(a.draws)]
        tasks.sort(key=lambda t: -t[1])
        t0 = time.time()
        out = pool.map(e1_task, tasks, chunksize=1)
        vals, peak = {}, 0.0
        for c, n, rep, ratio, w, rss in out:
            vals.setdefault((C2.cell_id(c), n), []).append((rep, ratio))
            peak = max(peak, rss)
        say("  {} draws, wall {:.1f} s, largest per-worker peak RSS {:.1f} MB".format(len(out), time.time() - t0, peak))
        index = dict((C2.cell_id(c), i) for i, (_r, c, _w) in enumerate(sel))
        jobs = []
        for (cid, n), v in vals.items():
            v.sort()
            jobs.append((index[cid], ladder.index(n), [x[1] for x in v]))
        med = {}
        for ci, li, m_, lo, hi in pool.map(boot_median, jobs, chunksize=4):
            med[(ci, li)] = (m_, lo, hi)
    finally:
        pool.close()
        pool.join()

    hdr("E1  per cell: median ratio [95% interval] at each N; classification  (H1, J1)")
    say("  {:<5} {:<38} {:>8} {:>9} ".format("row", "cell", "run med", "ratio_ref") + "".join(
        "{:>26}".format("N " + str(n)) for n in ladder) + "  J_needed   class")
    classes = []
    for i, (row, c, why) in enumerate(sel):
        r = rm[(row, c)]
        m50 = med[(i, ladder.index(RUN_JINF))]
        h1 = m50[1] <= r["median"] <= m50[2]
        off = abs(m50[0] / r["ratio_ref"] - 1.0) > NEAR
        near = [abs(med[(i, li)][0] / r["ratio_ref"] - 1.0) <= NEAR for li in range(len(ladder))]
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
        flag = "" if r["adequate"] else "  [not adequate]"
        classes.append((row, c, why, cl, jn, r["adequate"]))
        say("  {:<5} {:<38} {:>8} {:>9} ".format(row, C2.cell_id(c)[:38], fmt(r["median"]), fmt(r["ratio_ref"])) +
            "".join("{:>26}".format("{} [{}, {}]".format(fmt(med[(i, li)][0]), fmt(med[(i, li)][1]),
                                                        fmt(med[(i, li)][2]))) for li in range(len(ladder))) +
            "  {:<9}  {} ({}){}".format(str(jn) if jn else "none", cl, why, flag))

    hdr("SUMMARY  (description; classes by rule)")
    for why in ("affected", "control"):
        sub = [x for x in classes if x[2] == why]
        if not sub:
            continue
        say("  {} cells: {}".format(why, len(sub)))
        for cl in ("SIZE", "SIZE, NOT CONVERGED", "NOT A MISS AT 50000", "ELSEWHERE"):
            say("    {:<22} {:>4}   of which not adequate {:>3}".format(
                cl, sum(1 for x in sub if x[3] == cl), sum(1 for x in sub if x[3] == cl and not x[5])))
    say("  J_needed, affected d 40 cells classed SIZE: " + ", ".join(
        "{} {}".format(n, sum(1 for x in classes if x[2] == "affected" and x[1][2] == 40 and x[4] == n
                              and x[3] == "SIZE")) for n in ladder))
    hdr("sizetest.py run done, exit 0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
