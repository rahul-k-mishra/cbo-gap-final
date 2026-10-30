"""
sizetest.py  --  CBO-GAP: is the calibrated rows' miss at tight targets a
reference-size effect?  E0 (a read), E1 (a measurement, sharded and resumable
on Kaggle), and the plan for a larger-reference rerun  (ledger N40; Rahul's
instructions 2026-10-30 and 2026-10-31)

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
  READ (committed files only; nothing drawn; laptop):
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
  MEASUREMENT (E1, Kaggle): fresh initial ensembles of size N are drawn with
    calprec2's sampler (calprec2.f_chunk -> costprobe2.probe_sample, the
    archived samplers, verified line by line by calprec2 V2 and again here,
    V2S) and the ESS fraction is evaluated at the cell's run beta with
    calprec2's streamed evaluation (chunks of 250000, log-sum-exp
    combination). NO TRAJECTORY IS EVOLVED: there are no time steps, no
    dynamics, no coupled error. Only t = 0 draws and one weight evaluation.
    Seeds: each draw (cell, N, rep) has the key calprec2.key_of(41, cell,
    N, rep); chunk ci of it uses default_rng(SeedSequence(key + [ci])),
    exactly as calprec2 seeds its own draws. Kind 41 is used by no other
    script (calprec2 uses 31, 32, 33, 35), so no E1 draw coincides with a
    calprec2 or rerun draw, and every E1 draw is reproducible from its key.
    The smoke uses kind 42, so no smoke draw is an E1 draw.

MODES (rewritten 2026-10-31, before any E1 draw; the earlier single-process
"--mode run" was never executed and is removed)
  --mode plan     LAPTOP. Reads, runs the gates G3, G1, G2, SEL, E0, and
                  prints: E1's cost per ladder size, the measured peak RSS
                  for the streamed evaluation, the SHARD SCHEDULE (S1, S2)
                  and the larger-reference plan. Draws nothing. With
                  --write-plan it also writes the E1 plan folder (PF), the
                  only input the Kaggle modes read besides the throughput
                  folder; without it, it writes nothing.
  --mode smoke    KAGGLE. Gates G-FORK, G3, V2S, PF, then PC, then one
                  kind-42 draw per (module, objective, d, law) unit of the
                  plan at the largest ladder size, measuring wall and peak
                  RSS against the throughput estimate (SM1). Writes a new
                  folder sizetest-smoke-<stamp>/.
  --mode e1       KAGGLE. One shard of E1: gates G-FORK, G3, V2S, PF, G-STOP;
                  resume (RS); PC; then the shard's draws through
                  calprec2's scheduler (one process per task, a timeout,
                  --stop-after). Writes a new folder
                  sizetest-e1-<stamp>[-s<S>of<K>]/ with one row per draw.
  --mode analyse  LAPTOP. Reads the plan folder and every fetched E1 folder,
                  checks completeness (A1), then H1, J1 and the classes.
                  Writes nothing.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-30; sharding, resume,
smoke and the RSS figure added 2026-10-31, before any E1 draw)
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
  RSS PEAK RSS FIGURE (plan; corrected 2026-10-31, ledger N40). E1 streams
      every draw in chunks of 250000 and never holds a sample. The plan
      prints, per (module, d) of the selected cells, the largest RSS of
      calprec2's phase C rows at N = 256,000,000, which are streamed only
      (calprec2 holds replicate 0 of the 64M rung for its own check E1, so
      the 64M rows are not a streamed figure; they are printed beside it,
      labelled "held"). Worked example: a 256M row of 350.2 MB and a 64M
      row of 2537.5 MB: the streamed figure is 350.2 MB.
  PF  PLAN FOLDER (--write-plan; read by smoke, e1 and analyse). A new
      folder runs/sizetest-plan-<stamp>/ (opened "x") holding
      sizetest_e1_plan.csv (one row per selected cell: index, row, why,
      cell, beta as the run's string, tau_0, run median, ratio_ref, label,
      adequate) and sizetest_plan_params.csv (ladder, draws, kind, the PC
      row: tid, cell, key, betas, log_ess). Rahul writes its sha256.txt
      with scripts/manifest.py and commits it. The Kaggle modes read it
      only after its sha256.txt verifies, and print the sha256 of
      sizetest_e1_plan.csv; exit 2 if the folder fails or a column is
      missing.
  S1  SHARD ASSIGNMENT. The E1 tasks are every (cell, N, rep) of the plan:
      cells x ladder x draws. Each has the estimate est = N x (t_draw +
      t_beta) from the throughput table for its (module, objective, d,
      law). Tasks are sorted by (-est, tid) and task i goes to shard i
      modulo K. The assignment is a function of the plan, the throughput
      folder and K only, so every shard, resume and the analysis compute
      the same one. Worked example (illustrative values): estimates 20,
      20, 5, 5, 1, 1 s and K 2: shard 0 gets 20, 5, 1 and shard 1 gets 20,
      5, 1; each 26 s.
  S2  SHARD COUNT (plan). A shard's estimate is the sum of its tasks'
      estimates divided by --workers (perfect scaling: a lower bound) plus
      the PC estimate. The plan prints the smallest K whose largest shard
      estimate is at most --shard-target x --ceiling (defaults 0.5 and
      21600 s, calprec2's margin choices, not Kaggle limits), and the
      smallest K at the ceiling itself; it recommends the first. Worked
      example (illustrative values): total 40000 core s at 4 workers is
      10000 s in one shard: at target 10800 s, K = 1.
  T1  PER-TASK TIMEOUT = max(600 s, 5 x the largest est among the job's
      tasks) (calprec2's TIMEOUT_FACTOR; the 600 s floor is calprec2's
      smoke floor). A task over it is terminated and written as an error
      row. Worked example: largest est 20.1 s: timeout 600 s.
  STOP --stop-after SECONDS (default 36000, calprec2's): once task execution
      has run that long, no new task starts; running tasks finish and are
      written; the job prints "STOPPED by --stop-after" and exits 5. G-STOP:
      the job refuses (exit 2) if --stop-after + timeout exceeds the
      12-hour cap, 43200 s. Worked example: 36000 + 600 = 36600 <= 43200:
      pass.
  RS  RESUME (CLAUDE.md rule 17), --resume-from DIR[,DIR], e1 mode only.
      Each folder is read only after its sha256.txt verifies; it must hold
      exactly one sizetest_params.csv and one sizetest_e1.csv. Its
      parameters (mode, plan sha256, throughput, shard, nshards, workers,
      stop_after, ladder, draws, kind, the three script hashes, python,
      numpy) must equal this job's; a row counts as complete only with end
      "ok"; a complete tid found twice, or a tid not of this shard, stops
      the job (exit 2). Every folder read is printed with its counts as
      "  read <folder>: shard S of K, N rows, M complete". Complete rows
      are skipped; error rows are run again. The new folder holds new rows
      only; the merge is a concatenation.
      Worked example: a1 stopped at 5 with 900 rows complete; a2 resumes
      from a1, skips those 900 and runs the rest.
  G-FORK The scheduler's child processes find the E1 task in calprec2's
      task table only under the "fork" start method; any other method is
      exit 2 before anything runs.
  V2S SAMPLER IDENTITY, as calprec2 V2, for mechanism and boundary; exit 2
      otherwise.
  PC  POSITIVE CONTROL (smoke and every e1 job, before any draw). The plan's
      PC row (the lowest-sorted calprec2 phase C row at N 64,000,000 among
      the selected cells) is recomputed with calprec2's own key, sampler
      and streamed evaluation at its own betas; every log-ESS must equal
      the committed one within 1e-12 relative (calprec2's E1_TOL). Exit 3
      otherwise: the E1 machinery would not be calprec2's on this machine.
  SM1 SMOKE. PC, then one kind-42 draw per (module, objective, d, law)
      unit of the plan at the largest ladder size, each printed with its
      wall, its est and their ratio, and its peak RSS. The ratio is
      reported, not a threshold: an overrun is absorbed by --stop-after
      and RS. "SMOKE PASS" iff PC passed, no task errored or timed out,
      and no task exceeds calprec2's 3072 MB RSS budget; exit 0. Otherwise
      "SMOKE FAIL", exit 4.
  A1  COMPLETENESS (analyse). Every fetched folder verifies and holds
      sizetest_e1.csv rows of the plan's sha256, ladder, draws and kind;
      python and numpy are the same in every folder (one platform, rule
      16); every planned (cell, N, rep) has exactly one row ending "ok";
      a second "ok" row for a tid is exit 2; a missing one is exit 4
      ("incomplete"), and nothing is classified.
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
  PLAN (printed before anything is drawn):
      E1 cost per ladder size = sum over selected cells of draws x N x
      (t_draw + t_beta), from calprec2's throughput table (Kaggle, python
      3.13.15, numpy 2.1.3: a laptop is slower and the figure is labelled
      so); the PC cost likewise at 64M with its number of betas.
      LARGER-REFERENCE PLAN: the affected d 40 cells, grouped by (module,
      objective, law); costprobe2's measured trajectory wall and peak RSS
      at J_inf 50000 for each group's unit; what is not measured; the probe
      needed (one realization per group at each candidate J_inf); the
      rerun's size (cells x 15 realizations at J_needed). J_needed comes
      from E1 (J1); in plan mode it is not yet known.

EXIT CODES
  0  ran to the end (plan, smoke with SMOKE PASS, e1 not stopped, analyse).
  2  bad argument; folder, manifest or archive problem; unexpected or
     incomplete input; a missing throughput entry; 50000 not in the ladder;
     G-FORK, V2S, G-STOP; a resume problem; a duplicate complete row.
  3  a gate failed: G1, G2 or PC.
  4  errored or timed-out tasks (smoke, e1); SMOKE FAIL; analyse found a
     planned draw without a complete row.
  5  e1 stopped by --stop-after: complete as far as it goes, NOT a failure;
     resume the same shard from this folder.
  Precedence in e1: 3 over 4, 4 over 5.

OUTPUT
  plan --write-plan  runs/sizetest-plan-<stamp>/sizetest_e1_plan.csv,
                     sizetest_plan_params.csv
  smoke              <outdir>/sizetest-smoke-<stamp>/sizetest_params.csv,
                     sizetest_e1.csv (kind 42 rows)
  e1                 <outdir>/sizetest-e1-<stamp>[-s<S>of<K>]/
                     sizetest_params.csv, sizetest_e1.csv (one row per draw:
                     tid, phase, cell, key, n, rep, beta, tau0, log_ess,
                     ratio, env, wall_s, rss_mb, rss_flag, error, end)
  Every file is opened "x". --archive and --outdir are resolved by
  scripts/cbopaths.py.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/sizetest.py --mode plan --workers 2 --runs ... --cal ... [--write-plan]
    python -B scripts/sizetest.py --mode analyse --plan-from runs/sizetest-plan-... --e1 runs/... --e1 ...
  smoke and e1 are launched by rerunq.py (family sizetest) through kgrun.py:
    --mode smoke --plan-from P --throughput T --workers 4
    --mode e1 --plan-from P --throughput T --stop-after X --shard S --nshards K --workers 4
              [--resume-from DIR,DIR]
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import hashlib                                                  # noqa: E402
import inspect                                                  # noqa: E402
import io                                                       # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import calprec2 as C2                                           # noqa: E402

R2 = None                    # refratio2, imported by the laptop modes only (laptop_imports)
cp = C2.cp
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = C2.OUTROOT
ROWS = ("CONC", "TAU8")
MODULE = {"CONC": "mechanism", "TAU8": "boundary"}
K_E1 = 41
K_SMOKE = 42
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
PLAN_CSV = "sizetest_e1_plan.csv"
PLAN_PARAMS = "sizetest_plan_params.csv"
ROWS_CSV = "sizetest_e1.csv"
PARAMS_CSV = "sizetest_params.csv"
PLAN_COLS = ["index", "row", "why", "cell", "beta", "tau0", "run_median", "ratio_ref", "label", "adequate"]
E1_COLS = ["tid", "phase", "cell", "key", "n", "rep", "beta", "tau0", "log_ess", "ratio", "env", "wall_s",
           "rss_mb", "rss_flag", "error", "end"]
SHARD_TARGET = 0.5
TIMEOUT_FLOOR = 600.0
RESUME_KEYS = ("mode", "plan_sha256", "throughput", "shard", "nshards", "workers", "stop_after", "ladder",
               "draws", "kind", "script_sha256", "calprec2_sha256", "costprobe2_sha256", "python", "numpy")
TASK_FN = "sizetest_e1"


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


def laptop_imports():
    global R2
    if R2 is None:
        import refratio2
        R2 = refratio2


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


def verified(folder):
    """cp.verify_folder, with its exit turned into Stop(2)."""
    try:
        return cp.verify_folder(folder)
    except SystemExit:
        raise Stop(2, "{} fails or lacks its sha256.txt".format(folder))


# ----------------------------------------------------------------------
# laptop reads (plan)
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
# tasks, estimates, shards (S1, S2, T1)
# ----------------------------------------------------------------------

def unit_of(c):
    return (c[0], c[1], c[2], c[3])


def est_of(c, n, thr):
    td, tb, _ts = thr[unit_of(c)]
    return n * (td + tb)


def pc_est(pc, thr):
    td, tb, _ts = thr[unit_of(pc["c"])]
    return C2.N_LO * (td + len(pc["betas"]) * tb)


def e1_tasks(plan, ladder, draws, thr):
    """Every (cell, N, rep) of the plan, as scheduler task dicts, sorted by (-est, tid) (S1)."""
    out = []
    for p in plan:
        for n in ladder:
            for rep in range(draws):
                out.append({"tid": C2.tid_of("E1", p["c"], n, rep), "phase": "E1", "c": p["c"], "n": n,
                            "rep": rep, "kind": K_E1, "beta": float(p["beta"]), "beta_s": p["beta"],
                            "tau0": p["tau0"], "est": est_of(p["c"], n, thr)})
    out.sort(key=lambda t: (-t["est"], t["tid"]))
    return out


def shard_of(tasks, shard, nshards):
    return [t for i, t in enumerate(tasks) if i % nshards == shard]


def shard_loads(tasks, k, workers, pce):
    return [sum(t["est"] for t in shard_of(tasks, i, k)) / workers + pce for i in range(k)]


def shards_needed(tasks, workers, pce, limit):
    for k in range(1, len(tasks) + 1):
        top = max(shard_loads(tasks, k, workers, pce))
        if top <= limit:
            return k, top
    return None, None


def timeout_of(tasks):
    return max(TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR * max([t["est"] for t in tasks] or [0.0]))


# ----------------------------------------------------------------------
# the draw (no trajectory) and the positive control
# ----------------------------------------------------------------------

def task_e1(t):
    """One draw: the ESS fraction of a fresh size-n sample at the run beta, over tau_0."""
    row = C2.base_row(t)
    t0 = time.time()
    try:
        key = C2.key_of(t["kind"], t["c"], t["n"], t["rep"])
        row["key"] = C2.key_str(key)
        per = [C2.chunk_terms(C2.f_chunk(t["c"], key, ci, m), [t["beta"]]) for ci, m in C2.chunks_of(t["n"])]
        le = C2.log_ess_from(C2.combine_terms(per, 1)[0])
        row.update({"beta": t["beta_s"], "tau0": repr(float(t["tau0"])), "log_ess": repr(le),
                    "ratio": repr(C2.tau_of(le, t["n"]) / t["tau0"]), "end": "ok", "error": ""})
    except Exception as e:                                       # noqa: BLE001 (written as an error row)
        row.update({"error": "{}: {}".format(type(e).__name__, e), "end": "err"})
    row["wall_s"] = "{:.3f}".format(time.time() - t0)
    row["rss_mb"] = "{:.1f}".format(C2.rss_mb())
    return row


C2.TASKS[TASK_FN] = task_e1          # found by calprec2.child_main in forked children (G-FORK)


def pc_task(t):
    c, n, key, betas = t
    t0 = time.time()
    per = []
    for ci, m in C2.chunks_of(n):
        per.append(C2.chunk_terms(C2.f_chunk(c, key, ci, m), betas))
    les = [C2.log_ess_from(r) for r in C2.combine_terms(per, len(betas))]
    return les, time.time() - t0, C2.rss_mb()


def run_pc(pc):
    hdr("PC  positive control: recompute the plan's calprec2 phase C row")
    pool = multiprocessing.Pool(processes=1)
    try:
        les, wall, rss = pool.apply(pc_task, ((pc["c"], C2.N_LO, pc["key"], pc["betas"]),))
    finally:
        pool.close()
        pool.join()
    worst = max(abs(x - y) / abs(y) if y != 0.0 else abs(x) for x, y in zip(les, pc["want"]))
    if worst > C2.E1_TOL or len(les) != len(pc["want"]):
        say("PC FAIL  {}: largest log-ESS relative difference {:.3e} > {}".format(pc["tid"], worst, C2.E1_TOL))
        raise Stop(3, "PC: {} log-ESS relative difference {:.3e} > {}".format(pc["tid"], worst, C2.E1_TOL))
    say("PC PASS  {}: {} log-ESS values within {:.3e} (wall {:.1f} s, RSS {:.1f} MB)".format(
        pc["tid"], len(les), worst, wall, rss))


def boot_median(args):
    ci, li, vals = args
    v = np.array(vals, dtype=float)
    ix = np.random.default_rng(np.random.SeedSequence([SEED0, 6, ci, li])).integers(0, v.size, (B, v.size))
    bm = np.median(v[ix], axis=1)
    return ci, li, float(np.median(v)), float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))


# ----------------------------------------------------------------------
# plan folder (PF) and run folders (RS, A1)
# ----------------------------------------------------------------------

def read_kv(path):
    with io.open(path, "r", newline="", encoding="utf-8") as fh:
        return dict((r[0], r[1]) for r in csv.reader(fh) if r)


def read_plan(folder):
    """PF: (cells as dicts, params dict, plan csv sha256)."""
    rels = verified(folder)
    names = dict((os.path.basename(r), r) for r in rels)
    for n in (PLAN_CSV, PLAN_PARAMS):
        if n not in names:
            raise Stop(2, "{}: no {}".format(folder, n))
    path = os.path.join(folder, names[PLAN_CSV])
    cells = []
    with io.open(path, "r", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames != PLAN_COLS:
            raise Stop(2, "{}: columns {}, expected {}".format(PLAN_CSV, rd.fieldnames, PLAN_COLS))
        for x in rd:
            try:
                cells.append({"index": int(x["index"]), "row": x["row"], "why": x["why"], "cell": x["cell"],
                              "c": C2.cell_from_id(x["cell"]), "beta": x["beta"], "tau0": float(x["tau0"]),
                              "run_median": float(x["run_median"]), "ratio_ref": float(x["ratio_ref"]),
                              "label": x["label"], "adequate": x["adequate"] == "1"})
                float(x["beta"])
            except (KeyError, ValueError):
                raise Stop(2, "{}: unreadable row {}".format(PLAN_CSV, x))
    if [p["index"] for p in cells] != list(range(len(cells))) or not cells:
        raise Stop(2, "{}: indices are not 0..n-1".format(PLAN_CSV))
    pr = read_kv(os.path.join(folder, names[PLAN_PARAMS]))
    try:
        ladder = [int(x) for x in pr["ladder"].split(",")]
        draws = int(pr["draws"])
        pc = {"tid": pr["pc_tid"], "c": C2.cell_from_id(pr["pc_cell"]),
              "key": tuple(int(x) for x in pr["pc_key"].split("-")),
              "betas": C2.floats(pr["pc_betas"]), "want": C2.floats(pr["pc_log_ess"])}
        if int(pr["kind"]) != K_E1:
            raise ValueError("kind")
    except (KeyError, ValueError):
        raise Stop(2, "{}: unreadable or missing parameter".format(PLAN_PARAMS))
    if RUN_JINF not in ladder or ladder != sorted(set(ladder)) or draws < 2:
        raise Stop(2, "{}: ladder {} or draws {} not usable".format(PLAN_PARAMS, ladder, draws))
    return cells, {"ladder": ladder, "draws": draws, "pc": pc}, sha256_of(path)


def read_run_folders(folders, want, mine):
    """RS (e1) and A1 (analyse): complete rows by tid from verified folders.
    want: parameters every folder must carry (None: compare with the first);
    mine: the set of tids allowed (None: any planned E1 tid)."""
    store, ref = {}, None
    for f in folders:
        rels = verified(f)
        pp = [r for r in rels if os.path.basename(r) == PARAMS_CSV]
        rr = [r for r in rels if os.path.basename(r) == ROWS_CSV]
        if len(pp) != 1 or len(rr) != 1:
            raise Stop(2, "{}: {} {} and {} {}, expected one of each".format(f, len(pp), PARAMS_CSV, len(rr),
                                                                           ROWS_CSV))
        pr = read_kv(os.path.join(f, pp[0]))
        cmp_ = dict((k, pr.get(k)) for k in (want.keys() if want is not None else RESUME_KEYS))
        if want is not None and cmp_ != want:
            bad = sorted(k for k in want if cmp_.get(k) != want[k])
            raise Stop(2, "{}: parameters differ from this job's in {} (CLAUDE.md rule 17)".format(f, bad))
        if want is None:
            if ref is None:
                ref = cmp_
            else:
                same = ("plan_sha256", "ladder", "draws", "kind", "python", "numpy")
                bad = sorted(k for k in same if cmp_.get(k) != ref.get(k))
                if bad:
                    raise Stop(2, "{}: {} differ from the first folder's (A1)".format(f, bad))
        rows, nok = 0, 0
        with io.open(os.path.join(f, rr[0]), "r", newline="", encoding="utf-8") as fh:
            for x in csv.DictReader(fh):
                rows += 1
                if mine is not None and x["tid"] not in mine:
                    raise Stop(2, "{}: task {} is not one of this job's".format(f, x["tid"]))
                if x.get("end") != "ok":
                    continue
                nok += 1
                if x["tid"] in store:
                    raise Stop(2, "task {} is complete in two folders (second: {})".format(x["tid"], f))
                store[x["tid"]] = x
        say("  read {}: shard {} of {}, {} rows, {} complete".format(
            f, pr.get("shard"), pr.get("nshards"), rows, nok))
    return store, ref


# ----------------------------------------------------------------------
# Kaggle gates: G-FORK, G3, V2S
# ----------------------------------------------------------------------

def kaggle_gates():
    hdr("G-FORK, G3, V2S")
    sm = multiprocessing.get_start_method(allow_none=False)
    if sm != "fork":
        raise Stop(2, "G-FORK: start method {}, the scheduler needs fork".format(sm))
    say("  G-FORK PASS  start method fork")
    g3()
    for m in ("mechanism", "boundary"):
        lines = [s.strip() for s in inspect.getsource(cp.MODS[m].one_realisation).splitlines()]
        try:
            i = lines.index("rng = np.random.default_rng(seed)")
            nxt = next(s for s in lines[i + 1:] if "rng" in s)
        except (ValueError, StopIteration):
            nxt = "(not found)"
        if nxt != C2.SAMPLER_LINE[m]:
            raise Stop(2, "V2S: {} sampler line {!r}, expected {!r}".format(m, nxt, C2.SAMPLER_LINE[m]))
        say("  V2S PASS  {:<10} {}".format(m, nxt))


def g3():
    for m in ("mechanism", "boundary", "exactcal"):
        want = cp.ARCHIVE_SHA256.get(m)
        got = sha256_of(cp.MODS[m].__file__)
        if want is None or got != want:
            raise Stop(2, "G3: archived {} hash {} does not match costprobe2's pin".format(m, got[:16]))
    say("  G3 PASS  mechanism, boundary, exactcal match costprobe2.ARCHIVE_SHA256")


# ----------------------------------------------------------------------
# modes
# ----------------------------------------------------------------------

def header(a, mode):
    say("=" * 100)
    say("CBO-GAP sizetest  (ledger N40)  mode {}".format(mode))
    say("=" * 100)
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    say("  script   sha256 {}".format(sha256_of(os.path.abspath(__file__))))
    say("  calprec2.py sha256 {}".format(sha256_of(C2.__file__)))
    say("  costprobe2.py sha256 {}".format(sha256_of(cp.__file__)))
    say("  archive  {}".format(cp.ARCH))
    say("  E1 seeds calprec2.key_of({}, cell, N, rep); smoke kind {}; chunk ci: default_rng(SeedSequence(key + "
        "[ci]))".format(K_E1, K_SMOKE))


def mode_plan(a):
    laptop_imports()
    try:
        ladder = sorted(set(int(x) for x in a.ladder.split(",") if x.strip()))
    except ValueError:
        raise Stop(2, "--ladder must be integers separated by commas")
    if RUN_JINF not in ladder:
        raise Stop(2, "--ladder must contain {} (the run's J_inf)".format(RUN_JINF))
    if a.draws < 2:
        raise Stop(2, "--draws must be at least 2")
    if not a.runs or not a.cal:
        raise Stop(2, "give the rerun folders (--runs) and the calprec2 record folders (--cal)")
    analysis = os.path.abspath(a.analysis or R2.DEFAULT_ANALYSIS)
    runs = [os.path.abspath(x) for x in a.runs]
    cals = [os.path.abspath(x) for x in a.cal]
    cps = [os.path.abspath(x) for x in (a.costprobe or DEFAULT_COSTPROBE)]
    for x in runs + cals + cps + [analysis, a.beta_table, a.throughput]:
        if not os.path.isdir(x):
            raise Stop(2, "not a folder: {}".format(x))
    if len(set(runs)) != len(runs) or len(set(cals)) != len(cals):
        raise Stop(2, "a folder is given twice")

    hdr("sizetest.py  (ledger N40)  mode plan  --  {}".format(
        "writes the E1 plan folder (PF)" if a.write_plan else "writes nothing"))
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))))
    say("  imports         refratio2 {}  calprec2 {}  costprobe2 {}".format(
        sha256_of(R2.__file__)[:16], sha256_of(C2.__file__)[:16], sha256_of(cp.__file__)[:16]))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  workers         {} (this laptop process); --kaggle-workers {} for the schedule".format(
        a.workers, a.kaggle_workers))
    say("  rows            CONC (mechanism), TAU8 (boundary)")
    say("  ladder          {}   draws per (cell, N) {}".format(", ".join(str(x) for x in ladder), a.draws))
    say("  near            |x - 1| <= {} (5%)".format(NEAR))
    say("  E1 seeds        calprec2.key_of({}, cell, N, rep); chunk ci: default_rng(SeedSequence(key + [ci]))".format(K_E1))
    say("  bootstrap       B {}, SeedSequence([{}, 6, cell index, level index])".format(B, SEED0))
    say("  controls        {}".format("off" if a.no_controls else "d 40 cells within 5%"))
    say("  schedule        --shard-target {} x --ceiling {:.0f} s; --stop-after {:.0f} s".format(
        a.shard_target, a.ceiling, a.stop_after))

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
        "E1 measures, on Kaggle. It draws fresh starting samples of 50000 particles, and of",
        "larger sizes, from the same sampler, and computes their concentration at the run's",
        "beta. No algorithm is run: nothing moves, only the starting cloud is drawn and",
        "weighed. If the 50000-particle draws reproduce the run's miss and the miss disappears",
        "as the sample grows, the cause is the reference size. If fresh 50000-particle draws",
        "do not reproduce the run's miss, the cause is somewhere else.",
        "",
        "This plan draws nothing. It prints what E1 would cost, how it would be split into",
        "Kaggle jobs, and what a rerun with larger references would need measured first.",
    ):
        say("  " + t)

    pool = multiprocessing.Pool(processes=a.workers)
    try:
        hdr("Gates and reads  (G3, G1, G2)")
        g3()
        rm = run_medians(runs, analysis, pool)
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
    finally:
        pool.close()
        pool.join()

    hdr("PLAN  E1 cost from measured walls  (draws nothing)")
    thr = C2.load_throughput(os.path.abspath(a.throughput))
    for row, c, why in sel:
        if unit_of(c) not in thr:
            raise Stop(2, "no throughput entry for {}".format(unit_of(c)))
    say("  throughput: {} (Kaggle; python 3.13.15, numpy 2.1.3). Seconds per point:".format(
        os.path.basename(a.throughput)))
    say("  t_draw to draw and evaluate f, t_beta to weigh one beta. A laptop is slower;")
    say("  these are Kaggle figures and a lower bound (perfect scaling).")
    say("  {:>10} {:>8} {:>14} {:>22} {:>18}".format("N", "tasks", "core s", "wall s at Kaggle W", "largest task s"))
    tot = 0.0
    for n in ladder:
        cs = sum(a.draws * est_of(c, n, thr) for _r, c, _w in sel)
        big = max(est_of(c, n, thr) for _r, c, _w in sel)
        tot += cs
        say("  {:>10} {:>8} {:>14} {:>22} {:>18}".format(
            n, a.draws * len(sel), "{:.1f}".format(cs), "{:.1f}".format(cs / a.kaggle_workers), "{:.2f}".format(big)))
    selids = set(C2.cell_id(c) for _r, c, _w in sel)
    cand = sorted([x for x in Crows if x[1] in selids and x[2] == C2.N_LO], key=lambda x: x[0])
    if not cand:
        raise Stop(2, "PC: no phase C row at N {} among the selected cells".format(C2.N_LO))
    pcrow = cand[0]
    pc = {"tid": pcrow[0], "c": C2.cell_from_id(pcrow[1]), "key": tuple(int(x) for x in pcrow[3].split("-")),
          "betas": C2.floats(pcrow[4]), "want": C2.floats(pcrow[5])}
    pce = pc_est(pc, thr)
    tot += pce
    say("  PC: {} at N {} with {} beta(s): {:.1f} s per job (committed wall {:.1f} s, RSS {:.1f} MB); it runs in the".format(
        pcrow[1], C2.N_LO, len(pc["betas"]), pce, pcrow[6], pcrow[7]))
    say("      smoke and at the start of every e1 job")
    say("  total core s {:.1f} (E1 and one PC)".format(tot))

    hdr("PLAN  measured peak RSS for this evaluation  (RSS; corrected 2026-10-31)")
    say("  E1 streams each draw in chunks of {} and holds no sample. calprec2's phase C rows at".format(C2.CHUNK))
    say("  N {} are streamed only; its 64M rows hold replicate 0 for calprec2's own E1".format(C2.N_HI))
    say("  check and are printed only beside it, labelled held.")
    say("  {:<10} {:>4} {:>30} {:>30}".format("module", "d", "streamed (256M rows)", "held (64M rows)"))
    for m in sorted(set(c[0] for _r, c, _w in sel)):
        for d in sorted(set(c[2] for _r, c, _w in sel if c[0] == m)):
            def peak(nn):
                rs = [x[7] for x in Crows if x[1].startswith(m + "|") and x[1].split("|")[2] == str(d) and x[2] == nn]
                return "{:.1f} MB over {} tasks".format(max(rs), len(rs)) if rs else "not measured"
            say("  {:<10} {:>4} {:>30} {:>30}".format(m, d, peak(C2.N_HI), peak(C2.N_LO)))
    say("  calprec2's per-task budget G-RSS is {:.0f} MB; the scheduler flags a row above it.".format(C2.RSS_BUDGET_MB))

    hdr("PLAN  shard schedule for Kaggle  (S1, S2, T1, G-STOP)")
    plan = [{"c": c, "beta": rm[(row, c)]["beta_s"], "tau0": rm[(row, c)]["tau0"]} for row, c, _w in sel]
    tasks = e1_tasks(plan, ladder, a.draws, thr)
    W = a.kaggle_workers
    tgt = a.shard_target * a.ceiling
    say("  {} E1 tasks ({} cells x {} sizes x {} draws), {} Kaggle workers, PC {:.1f} s per job".format(
        len(tasks), len(sel), len(ladder), a.draws, W, pce))
    say("  shard estimate = its tasks' est / workers + PC (perfect scaling: a lower bound)")
    kt, tt = shards_needed(tasks, W, pce, tgt)
    kc, tc = shards_needed(tasks, W, pce, a.ceiling)
    say("  at the target {:.0f} s ({} x {:.0f} s): smallest --nshards {}, largest shard {:.1f} s".format(
        tgt, a.shard_target, a.ceiling, kt, tt))
    say("  at the ceiling {:.0f} s: smallest --nshards {}, largest shard {:.1f} s".format(a.ceiling, kc, tc))
    if kt is not None:
        say("  RECOMMENDED: --nshards {}, the count at the target".format(kt))
        say("  {:>6} {:>8} {:>14} {:>16} {:>12} {:>34}".format("shard", "tasks", "est core s", "est wall s",
                                                                 "timeout s", "G-STOP (stop-after + timeout)"))
        for i in range(kt):
            mine = shard_of(tasks, i, kt)
            to = timeout_of(mine)
            say("  {:>6} {:>8} {:>14} {:>16} {:>12} {:>34}".format(
                i, len(mine), "{:.1f}".format(sum(t["est"] for t in mine)),
                "{:.1f}".format(sum(t["est"] for t in mine) / W + pce), "{:.0f}".format(to),
                "{:.0f} + {:.0f} = {:.0f} {}".format(a.stop_after, to, a.stop_after + to,
                                                   "PASS" if a.stop_after + to <= C2.KAGGLE_CAP_S else "REFUSE")))
        say("  schedule: smoke first, then shards 0 to {} one at a time, by rerunq.py (family sizetest)".format(kt - 1))
    sm_units = sorted(set(unit_of(c) for _r, c, _w in sel))
    say("  The smoke draws one kind-{} sample per unit at N {}: {} units, est {:.1f} core s, plus PC.".format(
        K_SMOKE, ladder[-1], len(sm_units), sum(est_of(u, ladder[-1], thr) for u in sm_units)))

    hdr("PLAN  larger-reference rerun of the affected d 40 cells  (draws nothing)")
    aff40 = [(row, c) for row, c, why in sel if why == "affected" and c[2] == 40]
    groups = {}
    for row, c in aff40:
        groups.setdefault(unit_of(c), []).append((row, c))
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

    if a.write_plan:
        hdr("PF  writing the E1 plan folder")
        out = os.path.join(OUTROOT, "sizetest-plan-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(out)
        with io.open(os.path.join(out, PLAN_CSV), "x", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(PLAN_COLS)
            for i, (row, c, why) in enumerate(sel):
                r = rm[(row, c)]
                w.writerow([i, row, why, C2.cell_id(c), r["beta_s"], repr(r["tau0"]), repr(r["median"]),
                            repr(r["ratio_ref"]), r["label"], "1" if r["adequate"] else "0"])
        with io.open(os.path.join(out, PLAN_PARAMS), "x", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows([
                ["ladder", ",".join(str(n) for n in ladder)], ["draws", a.draws], ["kind", K_E1],
                ["near", repr(NEAR)], ["controls", "off" if a.no_controls else "d40"],
                ["pc_tid", pcrow[0]], ["pc_cell", pcrow[1]], ["pc_key", pcrow[3]], ["pc_betas", pcrow[4]],
                ["pc_log_ess", pcrow[5]], ["writer_sha256", sha256_of(os.path.abspath(__file__))],
                ["beta_table", os.path.basename(a.beta_table.rstrip("/"))],
                ["analysis", os.path.basename(analysis.rstrip("/"))],
                ["runs", ";".join(os.path.basename(x.rstrip("/")) for x in runs)]])
        say("  wrote {}".format(out))
        say("  {} sha256 {}".format(PLAN_CSV, sha256_of(os.path.join(out, PLAN_CSV))))
        say("  next: python scripts/manifest.py (writes its sha256.txt), then commit the folder")
    hdr("sizetest.py plan done, exit 0  (nothing drawn)")
    return 0


def kaggle_setup(a, mode):
    """Shared by smoke and e1: header, gates, plan, throughput."""
    header(a, mode)
    if not a.plan_from or not a.throughput:
        raise Stop(2, "--plan-from and --throughput are required in mode {}".format(mode))
    kaggle_gates()
    hdr("PF  the E1 plan folder")
    cells, pp, psha = read_plan(os.path.abspath(a.plan_from))
    say("  plan     {}".format(a.plan_from))
    say("  plan     {} sha256 {}".format(PLAN_CSV, psha))
    say("  cells {}   ladder {}   draws {}   PC row {}".format(len(cells), ",".join(str(n) for n in pp["ladder"]),
                                                              pp["draws"], pp["pc"]["tid"]))
    try:
        thr = C2.load_throughput(os.path.abspath(a.throughput))
    except SystemExit:
        raise Stop(2, "{} fails or lacks its sha256.txt".format(a.throughput))
    say("  throughput  {}".format(a.throughput))
    for p in cells:
        if unit_of(p["c"]) not in thr:
            raise Stop(2, "no throughput entry for {}".format(unit_of(p["c"])))
    return cells, pp, psha, thr


def params_rows(a, mode, psha, pp, shard, nshards):
    return [["mode", mode], ["plan_sha256", psha], ["throughput", os.path.basename(a.throughput.rstrip("/"))],
            ["shard", str(shard)], ["nshards", str(nshards)], ["workers", str(a.workers)],
            ["stop_after", repr(float(a.stop_after))], ["ladder", ",".join(str(n) for n in pp["ladder"])],
            ["draws", str(pp["draws"])], ["kind", str(K_SMOKE if mode == "smoke" else K_E1)],
            ["script_sha256", sha256_of(os.path.abspath(__file__))], ["calprec2_sha256", sha256_of(C2.__file__)],
            ["costprobe2_sha256", sha256_of(cp.__file__)], ["python", platform.python_version()],
            ["numpy", np.__version__], ["resume_from", a.resume_from or ""]]


def new_outdir(mode, shard, nshards):
    tag = "" if nshards == 1 else "-s{}of{}".format(shard, nshards)
    out = os.path.join(OUTROOT, "sizetest-{}-{}{}".format(mode, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
                                                         tag))
    os.makedirs(out)
    return out


def mode_smoke(a):
    cells, pp, psha, thr = kaggle_setup(a, "smoke")
    say("  mode     smoke   shard 0 of 1")
    units, seen = [], set()
    for p in cells:
        u = unit_of(p["c"])
        if u not in seen:
            seen.add(u)
            units.append(p)
    n = pp["ladder"][-1]
    tasks = [{"tid": C2.tid_of("SMOKE", p["c"], n, 0), "phase": "SMOKE", "c": p["c"], "n": n, "rep": 0,
              "kind": K_SMOKE, "beta": float(p["beta"]), "beta_s": p["beta"], "tau0": p["tau0"],
              "est": est_of(p["c"], n, thr)} for p in units]
    to = timeout_of(tasks)
    hdr("T1  per-task timeout")
    say("  TIMEOUT_S = {:.0f} s  (max({:.0f}, {:.0f} x largest est {:.2f} s))".format(
        to, TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR, max(t["est"] for t in tasks)))
    run_pc(pp["pc"])
    out = new_outdir("smoke", 0, 1)
    with io.open(os.path.join(out, PARAMS_CSV), "x", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(params_rows(a, "smoke", psha, pp, 0, 1))
    hdr("SM1  one kind-{} draw per unit at N {}: {} units".format(K_SMOKE, n, len(tasks)))
    o = C2.Out(os.path.join(out, ROWS_CSV), E1_COLS)
    runner = C2.Runner(a.workers, to, o, {})
    try:
        runner.run([(TASK_FN, t) for t in tasks], "smoke")
    finally:
        o.close()
    hdr("SM1  measured wall against the throughput estimate (reported, not a threshold)")
    say("  {:<44} {:>10} {:>10} {:>8} {:>10}".format("unit (cell used)", "wall s", "est s", "ratio", "RSS MB"))
    flagged = 0
    for t in tasks:
        r = runner.store.get(t["tid"])
        if r is None or r.get("end") != "ok":
            say("  {:<44} {:>10}".format(C2.cell_id(t["c"])[:44], "error"))
            continue
        if r.get("rss_flag"):
            flagged += 1
        w = float(r["wall_s"])
        say("  {:<44} {:>10} {:>10} {:>8} {:>10}".format(C2.cell_id(t["c"])[:44], "{:.2f}".format(w),
                                                        "{:.2f}".format(t["est"]), "{:.2f}".format(w / t["est"]),
                                                        r["rss_mb"]))
    say("\n" + "=" * 96)
    say("tasks run by this job: {}   task execution {:.0f} s".format(runner.ran, runner.elapsed()))
    say("not stopped: every task ran")
    say("errored or timed-out tasks: {}".format(runner.errors))
    ok = runner.errors == 0 and flagged == 0
    say("SMOKE {}".format("PASS" if ok else "FAIL"))
    say("files  {}".format(out))
    say("=" * 96)
    return 0 if ok else 4


def mode_e1(a):
    cells, pp, psha, thr = kaggle_setup(a, "e1")
    if not (0 <= a.shard < a.nshards):
        raise Stop(2, "shard {} of {}".format(a.shard, a.nshards))
    say("  mode     e1   shard {} of {}".format(a.shard, a.nshards))
    say("  stop     --stop-after {:.0f} s from the start of task execution".format(a.stop_after))
    tasks = e1_tasks(cells, pp["ladder"], pp["draws"], thr)
    mine = shard_of(tasks, a.shard, a.nshards)
    say("  E1 tasks {} in all; this shard {} (S1: sorted by (-est, tid), i modulo {})".format(
        len(tasks), len(mine), a.nshards))
    to = timeout_of(mine)
    hdr("T1, G-STOP")
    say("  TIMEOUT_S = {:.0f} s  (max({:.0f}, {:.0f} x largest est {:.2f} s))".format(
        to, TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR, max(t["est"] for t in mine)))
    say("  --stop-after {:.0f} s + TIMEOUT_S {:.0f} s = {:.0f} s   cap {:.0f} s".format(
        a.stop_after, to, a.stop_after + to, C2.KAGGLE_CAP_S))
    if a.stop_after + to > C2.KAGGLE_CAP_S:
        raise Stop(2, "G-STOP: --stop-after + TIMEOUT_S exceeds the 12-hour cap; lower --stop-after")
    say("  G-STOP PASS")
    prm = params_rows(a, "e1", psha, pp, a.shard, a.nshards)
    store = {}
    if a.resume_from:
        hdr("RS  resume (CLAUDE.md rule 17)")
        want = dict((k, v) for k, v in prm if k in RESUME_KEYS)
        store, _ = read_run_folders([x for x in a.resume_from.split(",") if x], want,
                                    set(t["tid"] for t in mine))
        say("  {} complete task(s) read; they are skipped".format(len(store)))
    run_pc(pp["pc"])
    out = new_outdir("e1", a.shard, a.nshards)
    with io.open(os.path.join(out, PARAMS_CSV), "x", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(prm)
    say("\n  run dir  {}".format(out))
    hdr("E1  fresh draws, no trajectory  (a measurement)")
    o = C2.Out(os.path.join(out, ROWS_CSV), E1_COLS)
    runner = C2.Runner(a.workers, to, o, store, stop_after=a.stop_after)
    try:
        runner.run([(TASK_FN, t) for t in mine], "e1")
    finally:
        o.close()
    peak = max([float(r["rss_mb"]) for r in runner.store.values()
                if r.get("end") == "ok" and r.get("rss_mb") not in (None, "", "nan")] or [float("nan")])
    say("\n" + "=" * 96)
    say("tasks run by this job: {}   task execution {:.0f} s".format(runner.ran, runner.elapsed()))
    if runner.stopped:
        say("STOPPED by --stop-after {:.0f} s: {} task(s) not started. Resume this shard from this folder.".format(
            a.stop_after, runner.stopped[1]))
    else:
        say("not stopped: every task ran")
    say("errored or timed-out tasks: {}".format(runner.errors))
    say("largest per-task peak RSS {:.1f} MB (resumed rows included)".format(peak))
    say("files  {}".format(out))
    say("=" * 96)
    if runner.errors:
        return 4
    return 5 if runner.stopped else 0


def mode_analyse(a):
    hdr("sizetest.py  (ledger N40)  mode analyse  --  writes nothing")
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))))
    say("  python          {}   numpy {}   workers {}".format(sys.version.split()[0], np.__version__, a.workers))
    if not a.plan_from or not a.e1:
        raise Stop(2, "--plan-from and at least one --e1 folder are required")
    cells, pp, psha = read_plan(os.path.abspath(a.plan_from))
    ladder, draws = pp["ladder"], pp["draws"]
    say("  plan     {}   {} sha256 {}".format(a.plan_from, PLAN_CSV, psha))
    hdr("A1  completeness")
    folders = [os.path.abspath(x) for x in a.e1]
    if len(set(folders)) != len(folders):
        raise Stop(2, "a folder is given twice")
    store, ref = read_run_folders(folders, None, None)
    if ref.get("plan_sha256") != psha or ref.get("ladder") != ",".join(str(n) for n in ladder) \
            or ref.get("draws") != str(draws) or ref.get("kind") != str(K_E1):
        raise Stop(2, "A1: the folders' plan sha256, ladder, draws or kind are not the plan's")
    say("  platform of every folder: python {} numpy {}".format(ref.get("python"), ref.get("numpy")))
    want = set(C2.tid_of("E1", p["c"], n, rep) for p in cells for n in ladder for rep in range(draws))
    extra = sorted(set(store) - want)
    if extra:
        raise Stop(2, "A1: {} complete row(s) not in the plan, first {}".format(len(extra), extra[0]))
    miss = sorted(want - set(store))
    say("  planned draws {}; complete {}; missing {}".format(len(want), len(want) - len(miss), len(miss)))
    if miss:
        raise Stop(4, "A1: incomplete; first missing {}".format(miss[0]))
    jobs = []
    for p in cells:
        for li, n in enumerate(ladder):
            v = [float(store[C2.tid_of("E1", p["c"], n, rep)]["ratio"]) for rep in range(draws)]
            jobs.append((p["index"], li, v))
    pool = multiprocessing.Pool(processes=a.workers)
    try:
        med = {}
        for ci, li, m_, lo, hi in pool.map(boot_median, jobs, chunksize=4):
            med[(ci, li)] = (m_, lo, hi)
    finally:
        pool.close()
        pool.join()
    peak = max(float(r["rss_mb"]) for r in store.values())
    say("  largest per-task peak RSS over the complete rows {:.1f} MB".format(peak))

    hdr("E1  per cell: median ratio [95% interval] at each N; classification  (H1, J1)")
    say("  {:<5} {:<38} {:>8} {:>9} ".format("row", "cell", "run med", "ratio_ref") + "".join(
        "{:>26}".format("N " + str(n)) for n in ladder) + "  J_needed   class")
    classes = []
    i50 = ladder.index(RUN_JINF)
    for p in cells:
        i = p["index"]
        m50 = med[(i, i50)]
        h1 = m50[1] <= p["run_median"] <= m50[2]
        off = abs(m50[0] / p["ratio_ref"] - 1.0) > NEAR
        near = [abs(med[(i, li)][0] / p["ratio_ref"] - 1.0) <= NEAR for li in range(len(ladder))]
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
        flag = "" if p["adequate"] else "  [not adequate]"
        classes.append((p["row"], p["c"], p["why"], cl, jn, p["adequate"]))
        say("  {:<5} {:<38} {:>8} {:>9} ".format(p["row"], p["cell"][:38], fmt(p["run_median"]), fmt(p["ratio_ref"])) +
            "".join("{:>26}".format("{} [{}, {}]".format(fmt(med[(i, li)][0]), fmt(med[(i, li)][1]),
                                                        fmt(med[(i, li)][2]))) for li in range(len(ladder))) +
            "  {:<9}  {} ({}){}".format(str(jn) if jn else "none", cl, p["why"], flag))

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
    hdr("sizetest.py analyse done, exit 0")
    return 0


def main():
    ap = argparse.ArgumentParser(description="E0, E1 (sharded on Kaggle) and the larger-reference plan (N40)")
    ap.add_argument("--mode", choices=("plan", "smoke", "e1", "analyse"), required=True)
    ap.add_argument("--runs", action="append", default=[], help="plan: rerun shard folder; repeat")
    ap.add_argument("--cal", action="append", default=[], help="plan: calprec2 record folder; repeat")
    ap.add_argument("--analysis", default=None, help="plan: default refratio2's")
    ap.add_argument("--beta-table", default=DEFAULT_BETA_TABLE)
    ap.add_argument("--throughput", default=None, help="default (plan only) " + DEFAULT_THROUGHPUT)
    ap.add_argument("--costprobe", action="append", default=[])
    ap.add_argument("--ladder", default=DEFAULT_LADDER)
    ap.add_argument("--draws", type=int, default=DEFAULT_DRAWS)
    ap.add_argument("--no-controls", action="store_true")
    ap.add_argument("--write-plan", action="store_true")
    ap.add_argument("--kaggle-workers", type=int, default=4, help="plan: workers the schedule assumes")
    ap.add_argument("--shard-target", type=float, default=SHARD_TARGET)
    ap.add_argument("--ceiling", type=float, default=C2.CEILING_DEFAULT)
    ap.add_argument("--stop-after", type=float, default=C2.STOP_AFTER_DEFAULT)
    ap.add_argument("--plan-from", default=None)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--resume-from", default="")
    ap.add_argument("--e1", action="append", default=[], help="analyse: fetched E1 folder; repeat")
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    if a.workers < 1 or a.kaggle_workers < 1 or not (0.0 < a.shard_target <= 1.0) or a.ceiling <= 0 \
            or a.stop_after <= 0 or a.nshards < 1:
        raise Stop(2, "workers, shard-target, ceiling, stop-after or nshards out of range")
    if a.resume_from and a.mode != "e1":
        raise Stop(2, "--resume-from is for mode e1 only")
    if a.mode == "plan":
        if a.throughput is None:
            a.throughput = DEFAULT_THROUGHPUT
        return mode_plan(a)
    if a.mode == "smoke":
        return mode_smoke(a)
    if a.mode == "e1":
        return mode_e1(a)
    return mode_analyse(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
