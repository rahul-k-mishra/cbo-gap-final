"""
costprobe2.py  --  CBO-GAP round 2: what every row of the fixed-beta rerun
                   costs, measured with each row's own archived dynamics

WHAT THIS MEASURES, IN PLAIN LANGUAGE
-------------------------------------
The fixed-beta rerun (notes/RERUN_PLAN.md) covers the whole experiment matrix
of Table 2. scripts/costprobe.py timed one design only: isotropic exactcal
dynamics at sigma 0.2, J_inf 50000, T 1, d in {2, 5, 10, 40}, the six named
objectives. This script times one coupled realization of every combination
of inputs that changes the cost of a realization anywhere in the rerun:

  * every archived module that evolves a row, called unmodified:
    ess_surface, visibility, mechanism, control, boundary, regime, law,
    sigma, crossed, cliff, regimemap;
  * d = 2, 3, 5, 10, 20, 40, 80, wherever a row uses it;
  * isotropic and anisotropic diffusion;
  * the 12 synthetic objectives of regime.py and the 14 of law.py, each
    evolved by its own module;
  * J_inf = 12500, 25000, 50000, 100000 (EXP-REFSIZE; RERUN_PLAN F6 requires
    the peak RSS at 100000 before that row runs);
  * T = 0.5, 1, 2 (EXP-HORIZON);
  * the 19-point J grid of visibility.py and the 10-point grids
    (J10, and J10b with 1250 and 2500 for regime.py and law.py);
  * both arms of control.py, including the adaptive arm, which re-solves
    beta at every step.

It writes per-probe, per-J errors, wall time and per-worker peak RSS, and
then PROJECTS each rerun row's cost from what it measured. The projection is
arithmetic on measured times, printed by the script. It decides nothing about
the science and calibrates nothing that is used later: the probe beta is for
timing only.

NOTHING IS REIMPLEMENTED
  Every realization is the archived module's own one_realisation, imported
  from the archive (CLAUDE.md rule 4) and called with a fixed beta. The
  probe beta comes from the module's own calibration code:
    ess_surface  the design value 30.0, which is on both of its beta grids;
    visibility   30 / visibility.scales_of(...)[1], the archived B rule;
    mechanism    mechanism.beta_for_target(..., tau0), the archived probe;
    the others   the module's own solve_beta on a 4000-point sample from its
                 own initial law, at the probe's tau0.
  The only lines not imported are the 4000-point samplers for the modules
  whose one_realisation draws X0 inline (boundary, law, sigma, crossed,
  cliff, regimemap): rng.standard_normal((n, d)) + x*, with x* from the
  module's own dict. They affect the probe beta only, never the dynamics.

THE COST MODEL, AND WHAT IT DOES NOT TEST
  A probe UNIT is
      (module, objective, d, diffusion, J_inf, T, J grid, arm).
  The wall time of a realization is assumed to depend on the unit only, and
  not on beta, tau0, r, sigma, the initial law or the seed. Checks A1 and A2
  give evidence on that assumption for a few chosen units only. The beta
  and r dependence of wall time stays partly untested by decision (Rahul,
  2026-10-10; notes/COSTPROBE2_REVIEW.md, items A5 and A6), because the cure
  is a combinatorial sweep that costs more than the measurement is worth.
  Every projection carries that caveat. Each Table 2 cell of a rerun row maps
  to exactly one unit.

PRE-SPECIFIED CRITERIA (fixed 2026-10-10, before first execution; revised
the same day after notes/COSTPROBE2_REVIEW.md, still before any execution)
---------------------------------------------------------------------------
  P0  PLAN IDENTITY, values and counts.
      (a) VALUES. Every factor list this script loops over for a row (the
          objectives, d, tau0, r, sigma, laws, beta values, J_inf, T, the
          diffusions, the J grid and M) is compared with the constant that
          the archived script itself assigns. That constant is read from the
          archived source with the ast module, at the line range cited in
          SOURCE below. Only the non-quick branch is used: an assignment
          under "if ...quick:" is skipped, and for "X if ...quick else Y" the
          non-quick side is taken. Names (INITS, DIMS, TAUS, NAMED) are
          resolved from the imported module, list comprehensions over SYNTH
          from the module's SYNTH, argparse defaults from the add_argument
          call, and a dict indexed by args.<flag> from that flag's default.
          Exactly one value must be found per factor. A mismatch, or no
          value, or more than one, is a FAIL. The factors that cannot be
          read as constants (literals inside a comprehension) are printed
          as "not checked against source", with their line.
          Worked example: TAU8's d list is [5, 10, 40]; boundary.py line 253
          assigns dims = [5, 10, 40] in the else branch of "if args.quick:":
          ok. Had this script typed [5, 10, 20], P0 would print "MISMATCH
          archive [5, 10, 40], here [5, 10, 20]" and exit 2.
      (b) COUNTS. For every row the cell and realization counts must equal
          the Table 2 counts embedded below (TABLE2).
          Worked example: EXP-SIGMA is 2 diffusions x 4 objectives x 3 d x
          6 r x 2 tau0 = 288 cells, at 12 realizations = 3456: equal to
          Table 2, pass.
      Any failure of (a) or (b) exits 2 before any computation.
  P1  ARCHIVE IDENTITY. After import, each archive module's __file__ must lie
      in the archive directory and end in .py, and its sha256 must equal its
      entry in zenodo-v1.sha256, embedded below (ARCHIVE_SHA256). Otherwise
      exit 2. Worked example: regimemap.__file__ =
      <archive>/regimemap.py, hashing to eb1d704f...14c8: pass. A module
      found elsewhere on sys.path, or edited by one byte: exit 2.
  P2  SEED PASS-THROUGH AND DETERMINISM, one pair per module. Every probe
      passes numpy.random.SeedSequence(key) unchanged as the seed argument
      of the archived one_realisation, which calls default_rng(seed) on it.
      For EVERY module in the plan, check A3-<module> runs that module's
      smallest unit twice with the same key, in two separate processes.
      Every E_J must be bitwise identical, compared as its %.17g string,
      which identifies a double uniquely. P2 PASSES only if every planned A3
      pair is complete and identical. A pair with a member that errored,
      timed out or is missing is a FAIL, with its error text. A P2 FAIL
      gives exit code 3, after every row has been written. Worked example:
      E_10 = 0.056786325012345678 in both members: that pair passes. Either
      member ending "err": P2 FAIL.
      What P2 tests is repeatability per module. It does not show that
      distinct keys give distinct streams.
  P3  OBJECTIVE IDENTITY (reported; no decision rests on it). For every
      module and named objective, f is evaluated on a fixed array of 1000
      points (seed kind 43) at d = 2 and d = 40 and compared bitwise with
      exactcal.OBJECTIVES. The regime.py and law.py synthetic objectives
      with the same name are compared with each other. Worked example:
      boundary's ackley equal to exactcal's in every element: "same".
  P4  MEMORY BUDGET. Each probe runs in its own fresh process. Its peak RSS
      (resource.getrusage, Linux kilobytes / 1024) must be at most 3072 MB
      (Rahul, 2026-10-10). A row passes P4 when every unit it uses passes.
      Worked example: units at 180, 330 and 2950 MB: pass; one at 3100 MB:
      "EXCEEDS BUDGET".
  A1  BETA, TAU0, R AND SIGMA (evidence, not a measurement). Each check in
      CHECKS runs one unit twice, differing only in a calibration or
      diffusion-strength input. The two members are queued adjacently.
      NEIGHBOUR LOAD IS UNCONTROLLED: other probes run alongside each
      member, and they can differ between the two members. ratio = max(wall)
      / min(wall). PASS when ratio <= 1.25. On FAIL, every row of that
      module is projected with its walls multiplied by the largest failing
      ratio of that module. That projection is labelled SCALED (P5), never a
      lower bound. Every ratio is printed with the caveat "neighbour load
      uncontrolled; evidence, not a measurement". Worked example: 30.0 s and
      36.0 s give 1.20: pass. 30.0 s and 40.0 s give 1.333: fail, and that
      module's rows become SCALED by 1.333.
  A2  INITIAL LAW. As A1, with the initial law varied; same ratio, threshold,
      caveat and consequence.
  A3  TIMING NOISE. The P2 pair of each module is also that module's
      timing-noise yardstick. If its ratio exceeds 1.25, that module's A1 and
      A2 verdicts are labelled "noise-limited".
  A-ERR  Any A1 or A2 check with a member that errored, timed out or is
      missing is a FAIL, reported with the error text. It is never dropped.
      It sets exit code 4 (unless P2 has set 3). The module's scaling is not
      changed by an errored check, and the row's projection is labelled
      "check errored".
  P5  PROJECTION. For each rerun row, with W the --workers of the run that
      measured the walls:
          core_s = sum over its cells of M_row x wall(unit of the cell)
                   x scale(module)
          wall_s = core_s / W
          shards = ceil(wall_s / 21600)
      21600 s is the 6-hour ceiling per shard (Rahul, 2026-10-10). Walls are
      measured with up to W probes running at once, so they include the
      load of a saturated pool. Division by W assumes perfect scaling.
      Scheduling gaps, the run's tail, beta and r effects outside A1 and the
      seed-to-seed variation of cost are ignored.
      Labels:
        - an unscaled row is labelled "lower bound (perfect scaling;
          beta and r dependence partly untested)";
        - a row with scale > 1 is labelled "SCALED, not a bound".
      Worked example: 144 cells, M = 15, every unit 40.0 s, W = 4, scale 1:
      core_s = 86400, wall_s = 21600, shards = 1, "lower bound". With W = 2
      the same walls give wall_s = 43200, shards = 2.
  A row is NOT PROJECTED when any of its units has no completed probe; the
  missing units are listed.
  T1  PER-TASK TIMEOUT. Every probe runs in its own process. A probe still
      running after TIMEOUT_S seconds is terminated and written as an error
      row ("timeout"). A process that exits without a result (for example,
      killed for memory) is written as an error row ("worker exited").
      Nothing waits forever.
          TIMEOUT_S = 5 x (projected wall of the largest unit in the queue)
          projected wall of a unit = rate x proxy(unit)
          proxy(unit) = d x (J_inf + sum of its J) x K x (4 if adaptive
                        else 1)
          rate = the largest wall/proxy over a reference set of measured
                 probes
      The reference set:
        - with --timing-from DIR[,DIR], every completed probe in those
          verified folders;
        - otherwise, the 24 probes of logs/costprobe.log (laptop, 2 workers,
          exactcal dynamics, J10, J_inf 50000, K 100), embedded below as
          COSTPROBE_LOG.
      The proxy is a crude cost model, used only for the timeout and for
      ordering, never for P5. Its factor 4 for the adaptive arm is a
      deliberately generous guess. The rate, its source, the largest unit,
      its projection and TIMEOUT_S are printed at the head of the run.
      Worked example: rate 5.0e-7 s, largest proxy 9.6e8, projected 480 s,
      TIMEOUT_S = 2400 s.

SEEDS
  Every stream is numpy.random.default_rng(SeedSequence(key)) at full width,
  never reduced to 32 bits (ledger N16). For a probe realization, the key is
      (ENTROPY 20261010, kind 41, module code, objective code, d, diffusion
       code, law code, J_inf, K, arm code, variant, tau0 x 1e6, r x 1e6,
       design beta x 1e6, design sigma x 1e6)
  For the 4000-point beta sample it is
      (ENTROPY, kind 42, module code, objective code, d, law code,
       tau0 x 1e6)
  For P3's test array it is
      (ENTROPY, kind 43, d).
  The codes are the indices in MODULES, OBJ_NAMES, DIFFS, LAWS and ARMS
  below. The plan refuses duplicate keys, except within an A3 pair, whose
  duplication is the test (variant 99, used by no other task). calprec v2
  uses the same ENTROPY with kinds 31 to 34, so no stream here coincides
  with one there. Every key is written out in full in the results CSV.

MODES
  --plan      Print P1, P0, the probe list and its size, and the timeout.
              No dynamics, nothing written.
  --smoke     Only the A3 pair of every module, each module's smallest unit
              run twice. This tests imports, P1, P2, P3, the timeout and the
              plumbing. It projects nothing.
  (default)   Every unit needed by the rows selected with --rows (default:
              all), plus every check whose module is among them.
  --shard i --nshards k   Main probes, sorted by task id, go to shard
              (index mod k). All checks go to shard 0. Each shard is a
              separate job with a distinct name (CLAUDE.md rule 17).
  --resume-from DIR[,DIR]  CLAUDE.md rule 17 as amended 2026-10-10:
              - each DIR is read only after its sha256.txt verifies;
              - a task counts as completed only when its row ends in "ok";
              - a completed task id found twice stops the run;
              - the parameters in each DIR's costprobe2_params.csv, other
                than the folder list, must equal this run's, or it stops;
              - output goes to a new folder, and the script prints every
                folder read and the number of tasks skipped from each.
              On Kaggle no previous folder is available (ledger K5).
  --finalize DIR[,DIR]  No dynamics. Reads the verified folders in the order
              given and applies P2, P4, A1 to A3, A-ERR and P5. Every
              folder's parameters except the shard index must agree (script
              hash, mode, rows, nshards, workers, Python, NumPy), or it
              stops with exit 2.
              The rows finalized are those stored in the folders' params
              file, not this invocation's --rows. If --rows is given and
              differs from the folders' rows, finalize stops with exit 2.
              A REPEATED TASK ID is accepted only when every earlier
              occurrence is an error row ("err"); the later row replaces it.
              A repeated id whose earlier occurrence is complete ("ok")
              stops the run with exit 2. This lets a resumed run that
              recovered an errored task be finalized together with the
              folder that holds the error.
              A complete, unsharded, unresumed run finalizes itself.

OUTPUT (new folder <outdir>/costprobe2-<timestamp>[-smoke][-s<i>of<k>]/,
        every file opened "x", every row flushed and fsynced)
  costprobe2_params.csv      the parameters that resumption and finalize must
                             match
  costprobe2_results.csv     one row per probe: task id, check, unit fields,
                             beta (repr) and sigma (repr), seed key, wall,
                             peak RSS, slope (a diagnostic of one realization
                             at a timing beta, not a result), E_J for every J
                             in the unit's grid (%.17g), error, end marker
  costprobe2_checks.csv      (finalize) A1, A2, A3, A-ERR and P2 verdicts,
                             with the caveat
  costprobe2_projection.csv  (finalize) P4 and P5 per row, with the label
  costprobe2_objcheck.csv    P3

HOW TO RUN (from the repository root, venv active)
    python scripts/costprobe2.py --plan
    python scripts/costprobe2.py --workers 2 --smoke
    python scripts/costprobe2.py --workers 4
  --archive PATH and --outdir PATH are resolved by scripts/cbopaths.py, as
  in every round-2 script. On Kaggle the kgrun runner passes both.
  Exit codes:
    0  completed, whatever the verdicts;
    2  setup error (P0, P1, an import, a resume or finalize check);
    3  P2 failed;
    4  an A1 or A2 check errored, timed out or is missing (A-ERR).

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

# The archived modules pin BLAS to one thread before importing numpy. Here
# numpy is imported first, so their setdefault calls would come too late. The
# same variables are set here, unconditionally and before numpy, so that a
# platform default cannot leave several BLAS threads per worker. They are
# printed in the header.
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import ast                                                      # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import hashlib                                                  # noqa: E402
import importlib                                                # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True

import cbopaths                                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = cbopaths.archive_path(ROOT)
OUTROOT = cbopaths.output_root(ROOT)
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: archive not found at {}\n".format(ARCH))
    sys.stderr.write("pass --archive <path> or set CBOGAP_ARCHIVE\n")
    sys.exit(2)
sys.path.insert(0, ARCH)

MODULES = ["ess_surface", "visibility", "mechanism", "control", "boundary",
           "regime", "law", "sigma", "crossed", "cliff", "regimemap", "exactcal"]
DYN_MODULES = MODULES[:-1]

# Copied from zenodo-v1.sha256 (commit 423a4d4). P1.
ARCHIVE_SHA256 = {
    "boundary": "93d2eb0452fc0e422dc8db15e83f770fa6d1f1595010842d1d7f1c14c18eb3e4",
    "cliff": "017082fac66327d6276c3b23402c9b05cb701047ac0e88a41ff2e7d1719d1c51",
    "control": "4f50bbe5e94cfcf210d6aba5e6a6cf24ac5e3c95ea7a88a32f795a8995a46268",
    "crossed": "21ff6d389ec89147ff9ab0ab34370dd4eb492350ac9fa34cc2d44972bd53c840",
    "ess_surface": "e02f5287834bd100ac0f688a15ce0f5646ecf2a8e02347f347c57cebd427d436",
    "exactcal": "b17e1be3c024ec4de0d88a6a50dfde557ea6552d50bd0cb5ed9521ab4012a813",
    "law": "2003d65b72abb86c587a644b410559f587e3838bcc6e7bab8aa8d9888fdd1513",
    "mechanism": "74fee417de088b6d206535348d05450910ca3b9ffdd1d2eb7ad002a008e20c71",
    "regime": "b671a58c63f0ba7d2b583c338b76072e8e48d588baed0ab72ca8b7fb26cc56b2",
    "regimemap": "eb1d704f5cf150a06b82d8eefc672fd62fb3f05aacdc3704a092118da92f14c8",
    "sigma": "414c61c3f8dfa3abc4bf52115b788241fd12bb294493bfba797452d30004e779",
    "visibility": "7971bbcc93b7be82d6580b7dc833edda4afe126a1ec964fc39274439638db7aa",
}

MODS = {}
for _m in MODULES:
    try:
        MODS[_m] = importlib.import_module(_m)
    except Exception as exc:                                    # pragma: no cover
        sys.stderr.write("setup error: cannot import {}: {}\n".format(_m, exc))
        sys.exit(2)

# --------------------------------------------------------------------------
# constants; every grid below is checked against the archived source by P0
# --------------------------------------------------------------------------
DT, LAM, SIGMA_ISO, JINF = 0.01, 1.0, 0.2, 50000
J10 = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
J10B = [10, 20, 40, 80, 160, 320, 640, 1250, 2500, 5000]
J19 = [10, 14, 20, 28, 40, 57, 80, 113, 160, 226, 320, 452, 640,
       905, 1280, 1810, 2560, 3620, 5000]
JGRIDS = {"J10": J10, "J10b": J10B, "J19": J19}
JCOLS = sorted(set(J10) | set(J10B) | set(J19))

OBJ6 = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
OBJ4 = ["ackley", "rastrigin", "sphere", "rosenbrock"]
OBJ3 = ["ackley", "rastrigin", "sphere"]
REG_SYNTH = [n for n, _, _, _ in MODS["regime"].SYNTH]
LAW_SYNTH = [n for n, _, _, _ in MODS["law"].SYNTH]
OBJ_NAMES = list(OBJ6)
for _n in REG_SYNTH + LAW_SYNTH:
    if _n not in OBJ_NAMES:
        OBJ_NAMES.append(_n)
DIFFS = ["isotropic", "anisotropic", "none"]
LAWS = ["centred", "offset", "mix-0.1", "mix-0.01"]
ARMS = ["", "fixed", "adaptive"]
TAU8 = [0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01]
DIFF2 = ["isotropic", "anisotropic"]

ENTROPY = 20261010
KIND_PROBE, KIND_BETA, KIND_OBJ = 41, 42, 43
PROBE_TAU, PROBE_R, PROBE_N = 0.1, 0.5, 4000
RSS_BUDGET_MB = 3072.0
RATIO_MAX = 1.25
SHARD_CEIL_S = 21600.0
TIMEOUT_FACTOR = 5.0
ADAPTIVE_PROXY_FACTOR = 4
CAVEAT = "neighbour load uncontrolled; evidence, not a measurement"
LB_LABEL = "lower bound (perfect scaling; beta and r dependence partly untested)"
SCALED_LABEL = "SCALED, not a bound"

# logs/costprobe.log (laptop, 2 workers, 2026-10-09): exactcal.one_realisation,
# isotropic, sigma 0.2, J10, J_inf 50000, K 100, tau0 0.1. (objective, d, wall s)
COSTPROBE_LOG = [
    ("ackley", 2, 4.8), ("ackley", 5, 7.2), ("ackley", 10, 13.2), ("ackley", 40, 37.2),
    ("rastrigin", 2, 4.5), ("rastrigin", 5, 7.6), ("rastrigin", 10, 12.4), ("rastrigin", 40, 44.2),
    ("sphere", 2, 3.7), ("sphere", 5, 5.1), ("sphere", 10, 7.8), ("sphere", 40, 22.9),
    ("griewank", 2, 4.5), ("griewank", 5, 6.5), ("griewank", 10, 10.6), ("griewank", 40, 34.2),
    ("levy", 2, 6.1), ("levy", 5, 8.9), ("levy", 10, 16.6), ("levy", 40, 52.8),
    ("rosenbrock", 2, 4.2), ("rosenbrock", 5, 7.3), ("rosenbrock", 10, 11.3), ("rosenbrock", 40, 32.3),
]

# Table 2 of the submitted manuscript, printed page 12: (cells, realizations).
# CONC is EXP-MECH and EXP-CAL run once (ledger N17). PROBEARM is the
# seed-paired probe arm on the same grid; its counts are EXP-MECH's, by
# Rahul's instruction of 2026-10-10, and are not in Table 2.
TABLE2 = {
    "BETA-ISO": (42, 840), "BETA-ANI": (12, 240), "LAWPANEL": (144, 2880),
    "CONC": (144, 2160), "PROBEARM": (144, 2160), "ADAPT": (72, 1080),
    "TAU8": (144, 2160), "REFSIZE": (12, 144), "SYNTH": (72, 864),
    "NAMED": (36, 432), "HORIZON": (24, 288), "GEOM": (336, 4032),
    "SIGMA": (288, 3456), "ANISO": (288, 3456), "RMAP": (240, 2880),
    "CLIFF": (144, 1728), "ONSET": (180, 2160),
}
ROW_ORDER = ["BETA-ISO", "BETA-ANI", "LAWPANEL", "CONC", "PROBEARM", "ADAPT",
             "TAU8", "REFSIZE", "SYNTH", "NAMED", "HORIZON", "GEOM", "SIGMA",
             "ANISO", "RMAP", "CLIFF", "ONSET"]

# The factor lists every row loops over. P0(a) compares each with SOURCE.
GRID = {
    "BETA-ISO": {"objs": ["ackley", "rastrigin"],
                 "betas": [1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0],
                 "dims": [2, 5, 10], "M": 20, "jgrid": J10},
    "BETA-ANI": {"objs": ["ackley", "rastrigin"], "betas": [3.0, 30.0, 300.0],
                 "dims": [2, 10], "M": 20, "jgrid": J10},
    "LAWPANEL": {"objs": OBJ6, "dims": [2, 3, 5, 10, 20, 40],
                 "laws": ["centred", "offset", "mix-0.1", "mix-0.01"], "M": 20, "jgrid": J19},
    "CONC": {"objs": OBJ6, "dims": [2, 5, 10, 40], "laws": ["centred", "mix-0.1"],
             "taus": [0.5, 0.1, 0.01], "M": 15, "jgrid": J10},
    "ADAPT": {"objs": OBJ6, "dims": [5, 10, 40], "taus": [0.1, 0.01],
              "arms": ["fixed", "adaptive"], "M": 15, "jgrid": J10},
    "TAU8": {"objs": OBJ6, "dims": [5, 10, 40], "taus": TAU8, "M": 15, "jgrid": J10},
    "REFSIZE": {"objs": ["ackley", "sphere", "rosenbrock"],
                "jinfs": [12500, 25000, 50000, 100000], "d": 10, "M": 12, "jgrid": J10B},
    "SYNTH": {"objs": REG_SYNTH, "dims": [5, 10, 40], "taus": [0.1, 0.01], "M": 12, "jgrid": J10B},
    "NAMED": {"objs": OBJ6, "dims": [5, 10, 40], "taus": [0.1, 0.01], "M": 12, "jgrid": J10B},
    "HORIZON": {"objs": OBJ4, "laws": ["centred", "mix-0.1"], "Ts": [0.5, 1.0, 2.0],
                "M": 12, "jgrid": J10B},
    "GEOM": {"objs": LAW_SYNTH, "dims": [5, 10, 40], "taus": TAU8, "M": 12, "jgrid": J10B},
    "SIGMA": {"diffs": DIFF2, "objs": OBJ4, "dims": [5, 10, 40],
              "rs": [0.1, 0.25, 0.5, 0.75, 0.9, 0.99], "taus": [0.1, 0.01], "M": 12, "jgrid": J10},
    "ANISO": {"diffs": DIFF2, "objs": OBJ4, "dims": [5, 10, 40], "sigmas": [0.1, 0.2, 0.4],
              "rs": [0.1, 0.5, 0.9], "taus": [0.1, 0.01], "M": 12, "jgrid": J10},
    "RMAP": {"diffs": DIFF2, "objs": OBJ3, "dims": [10, 40], "rs": [0.5, 1.0, 1.5, 2.0, 3.0],
             "taus": [0.5, 0.1, 0.03, 0.01], "M": 12, "jgrid": J10},
    "CLIFF": {"diffs": DIFF2, "objs": OBJ4, "dims": [10, 40],
              "rs": [0.5, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0], "taus": [0.1], "M": 12,
              "jgrid": J10},
    "ONSET": {"diffs": DIFF2, "objs": OBJ3, "dims": [5, 10, 20, 40, 80],
              "rs": [0.75, 1.0, 1.25, 1.5, 2.0, 3.0], "tau": 0.1, "M": 12, "jgrid": J10},
}
GRID["PROBEARM"] = GRID["CONC"]

# Where each factor is assigned in the archived source:
# factor -> (module, first line, last line, variable or flag, how)
# how: "assign" | "for" (the iterable of a for loop over that name) |
#      "arg" (argparse default of that flag)
SOURCE = {
    "BETA-ISO": {"objs": ("ess_surface", 273, 273, "obj", "for"),
                 "betas": ("ess_surface", 241, 246, "betas", "assign"),
                 "dims": ("ess_surface", 241, 246, "dims", "assign"),
                 "M": ("ess_surface", 241, 246, "M", "assign"),
                 "jgrid": ("ess_surface", 241, 246, "J_list", "assign")},
    "BETA-ANI": {"objs": ("ess_surface", 280, 280, "obj", "for"),
                 "betas": ("ess_surface", 241, 246, "aniso_betas", "assign"),
                 "dims": ("ess_surface", 241, 246, "aniso_dims", "assign"),
                 "M": ("ess_surface", 241, 246, "M", "assign"),
                 "jgrid": ("ess_surface", 241, 246, "J_list", "assign")},
    "LAWPANEL": {"objs": ("visibility", 321, 326, "objs", "assign"),
                 "dims": ("visibility", 321, 326, "dims", "assign"),
                 "laws": ("visibility", 321, 326, "inits", "assign"),
                 "M": ("visibility", 321, 326, "M", "assign"),
                 "jgrid": ("visibility", 321, 326, "J_list", "assign")},
    "CONC": {"objs": ("mechanism", 294, 297, "objs", "assign"),
             "dims": ("mechanism", 294, 297, "dims", "assign"),
             "laws": ("mechanism", 294, 297, "inits", "assign"),
             "taus": ("mechanism", 294, 297, "taus", "assign"),
             "M": ("mechanism", 294, 297, "M", "assign"),
             "jgrid": ("mechanism", 294, 297, "J_list", "assign")},
    "ADAPT": {"objs": ("control", 297, 300, "objs", "assign"),
              "dims": ("control", 297, 300, "dims", "assign"),
              "taus": ("control", 297, 300, "taus", "assign"),
              "arms": ("control", 305, 305, "arms", "assign"),
              "M": ("control", 297, 300, "M", "assign"),
              "jgrid": ("control", 297, 300, "J_list", "assign")},
    "TAU8": {"objs": ("boundary", 252, 256, "objs", "assign"),
             "dims": ("boundary", 252, 256, "dims", "assign"),
             "taus": ("boundary", 252, 256, "taus", "assign"),
             "M": ("boundary", 252, 256, "M", "assign"),
             "jgrid": ("boundary", 252, 256, "J_list", "assign")},
    "REFSIZE": {"objs": ("regime", 511, 511, "objsA", "assign"),
                "jinfs": ("regime", 508, 508, "Jinfs", "assign"),
                "d": ("regime", 512, 512, "dA", "assign"),
                "M": ("regime", 483, 483, "M", "assign"),
                "jgrid": ("regime", 484, 484, "Jgrid", "assign")},
    "SYNTH": {"objs": ("regime", 548, 548, "names", "assign"),
              "dims": ("regime", 549, 549, "dims", "assign"),
              "taus": ("regime", 550, 550, "taus", "assign"),
              "M": ("regime", 483, 483, "M", "assign"),
              "jgrid": ("regime", 484, 484, "Jgrid", "assign")},
    "NAMED": {"objs": ("regime", 575, 575, "names", "assign"),
              "dims": ("regime", 576, 576, "dims", "assign"),
              "taus": ("regime", 577, 577, "taus", "assign"),
              "M": ("regime", 483, 483, "M", "assign"),
              "jgrid": ("regime", 484, 484, "Jgrid", "assign")},
    "HORIZON": {"objs": ("regime", 596, 596, "names", "assign"),
                "Ts": ("regime", 599, 599, "Ts", "assign"),
                "laws": ("regime", 600, 600, "inits", "assign"),
                "M": ("regime", 483, 483, "M", "assign"),
                "jgrid": ("regime", 484, 484, "Jgrid", "assign")},
    "GEOM": {"objs": ("law", 521, 521, "names", "assign"),
             "dims": ("law", 522, 522, "dims", "assign"),
             "taus": ("law", 522, 522, "taus", "assign"),
             "M": ("law", 770, 770, "--realisations", "arg"),
             "jgrid": ("law", 523, 523, "Jgrid", "assign")},
    "SIGMA": {"diffs": ("sigma", 259, 260, "diffs", "assign"),
              "objs": ("sigma", 253, 257, "objs", "assign"),
              "dims": ("sigma", 253, 257, "dims", "assign"),
              "rs": ("sigma", 253, 257, "rs", "assign"),
              "taus": ("sigma", 253, 257, "taus", "assign"),
              "M": ("sigma", 238, 238, "--realisations", "arg"),
              "jgrid": ("sigma", 253, 257, "Jgrid", "assign")},
    "ANISO": {"diffs": ("crossed", 248, 248, "diffs", "assign"),
              "objs": ("crossed", 255, 258, "objs", "assign"),
              "dims": ("crossed", 255, 258, "dims", "assign"),
              "sigmas": ("crossed", 255, 258, "sigmas", "assign"),
              "rs": ("crossed", 255, 258, "rs", "assign"),
              "taus": ("crossed", 255, 258, "taus", "assign"),
              "M": ("crossed", 239, 239, "--realisations", "arg"),
              "jgrid": ("crossed", 255, 258, "Jgrid", "assign")},
    "RMAP": {"diffs": ("regimemap", 288, 288, "diffs", "assign"),
             "objs": ("regimemap", 289, 289, "objs", "assign"),
             "dims": ("regimemap", 300, 302, "dimsM", "assign"),
             "rs": ("regimemap", 300, 302, "rsM", "assign"),
             "taus": ("regimemap", 300, 302, "tausM", "assign"),
             "M": ("regimemap", 279, 279, "--realisations", "arg"),
             "jgrid": ("regimemap", 300, 302, "Jgrid", "assign")},
    "CLIFF": {"diffs": ("cliff", 253, 253, "diffs", "assign"),
              "objs": ("cliff", 260, 264, "objs", "assign"),
              "dims": ("cliff", 260, 264, "dims", "assign"),
              "rs": ("cliff", 260, 264, "rs", "assign"),
              "taus": ("cliff", 260, 264, "taus", "assign"),
              "M": ("cliff", 244, 244, "--realisations", "arg"),
              "jgrid": ("cliff", 260, 264, "Jgrid", "assign")},
    "ONSET": {"diffs": ("regimemap", 288, 288, "diffs", "assign"),
              "objs": ("regimemap", 289, 289, "objs", "assign"),
              "dims": ("regimemap", 300, 302, "dimsD", "assign"),
              "rs": ("regimemap", 300, 302, "rsD", "assign"),
              "tau": ("regimemap", 304, 304, "tauD", "assign"),
              "M": ("regimemap", 279, 279, "--realisations", "arg"),
              "jgrid": ("regimemap", 300, 302, "Jgrid", "assign")},
}
SOURCE["PROBEARM"] = SOURCE["CONC"]

# Factors that are literals inside a comprehension or a dict lookup that P0
# cannot read as one constant. They are printed, not checked.
NOT_CHECKED = {
    "REFSIZE": ["tau0 0.1, law centred, T 1.0 inside the cells comprehension, regime.py 513"],
    "HORIZON": ["d 10 and tau0 0.1 inside the cells comprehension, regime.py 601"],
    "SYNTH": ["law centred inside the cells comprehension, regime.py 553"],
    "NAMED": ["law centred inside the cells comprehension, regime.py 578"],
    "ANISO": ["the two arms A and B: an expression over args.arm, crossed.py 260-262"],
    "TAU8": ["law centred: X0 drawn inline as standard normal + MINIMIZER, boundary.py 181"],
}


# --------------------------------------------------------------------------
# P0(a): constants read from the archived source
# --------------------------------------------------------------------------

def _is_quick(node):
    return "quick" in ast.dump(node)


def _negated(test):
    return isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not)


def _parents(tree):
    par = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            par[c] = n
    return par


def _in_quick_branch(node, par):
    """True if node sits in the branch of an 'if ...quick...' taken in quick mode."""
    child, p = node, par.get(node)
    while p is not None:
        if isinstance(p, ast.If) and _is_quick(p.test):
            in_body = any(child is s for s in p.body)
            neg = _negated(p.test)
            if (in_body and not neg) or ((not in_body) and neg):
                return True
        child, p = p, par.get(p)
    return False


def _argdefault(tree, flag):
    found = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument" and n.args
                and isinstance(n.args[0], ast.Constant) and n.args[0].value == flag):
            for kw in n.keywords:
                if kw.arg == "default":
                    found.append(ast.literal_eval(kw.value))
    if len(found) != 1:
        raise ValueError("argparse default of {}: {} found".format(flag, len(found)))
    return found[0]


def _resolve(expr, mod, tree):
    if isinstance(expr, ast.IfExp) and _is_quick(expr.test):
        expr = expr.body if _negated(expr.test) else expr.orelse
    if isinstance(expr, ast.Name):
        return list(getattr(mod, expr.id)) if isinstance(getattr(mod, expr.id), (list, tuple, dict)) \
            else getattr(mod, expr.id)
    if (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "list"
            and len(expr.args) == 1 and isinstance(expr.args[0], ast.Name)):
        return list(getattr(mod, expr.args[0].id))
    if (isinstance(expr, ast.ListComp) and len(expr.generators) == 1
            and isinstance(expr.generators[0].iter, ast.Name)
            and expr.generators[0].iter.id == "SYNTH"):
        return [t[0] for t in mod.SYNTH]
    if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Dict):
        sl = expr.slice
        if hasattr(ast, "Index") and isinstance(sl, getattr(ast, "Index")):
            sl = sl.value
        if isinstance(sl, ast.Attribute):
            return ast.literal_eval(expr.value)[_argdefault(tree, "--" + sl.attr)]
        raise ValueError("unsupported dict index")
    return ast.literal_eval(expr)


def _target_value(tgt, val, var):
    """The expression assigned to var by 'tgt = val', or None."""
    if isinstance(tgt, ast.Name) and tgt.id == var:
        return val
    if isinstance(tgt, ast.Attribute) and tgt.attr == var:
        return val
    if isinstance(tgt, ast.Tuple) and isinstance(val, ast.Tuple) and len(tgt.elts) == len(val.elts):
        for t, v in zip(tgt.elts, val.elts):
            r = _target_value(t, v, var)
            if r is not None:
                return r
    return None


_TREES = {}


def archived_value(module, lo, hi, var, how):
    mod = MODS[module]
    if module not in _TREES:
        with open(mod.__file__) as fh:
            tree = ast.parse(fh.read())
        _TREES[module] = (tree, _parents(tree))
    tree, par = _TREES[module]
    if how == "arg":
        return _argdefault(tree, var)
    found = []
    for n in ast.walk(tree):
        ln = getattr(n, "lineno", None)
        if ln is None or not (lo <= ln <= hi) or _in_quick_branch(n, par):
            continue
        if how == "assign" and isinstance(n, ast.Assign):
            for tgt in n.targets:
                e = _target_value(tgt, n.value, var)
                if e is not None:
                    found.append(_resolve(e, mod, tree))
        elif how == "for" and isinstance(n, ast.For):
            if isinstance(n.target, ast.Name) and n.target.id == var:
                found.append(list(ast.literal_eval(n.iter)))
    if len(found) != 1:
        raise ValueError("{} values found for {} in {}.py {}-{}".format(len(found), var, module, lo, hi))
    v = found[0]
    return list(v) if isinstance(v, tuple) else v


def p0_values(sel):
    ok = True
    for name in sel:
        for fac, spec in sorted(SOURCE[name].items()):
            mine = GRID[name][fac]
            try:
                arch = archived_value(*spec)
                good = (arch == mine)
                msg = "ok" if good else "MISMATCH archive {}, here {}".format(arch, mine)
            except Exception as exc:
                good, msg = False, "NOT READ: {}".format(exc)
            ok &= good
            print("  {:<9} {:<7} {}.py {}-{} {:<15} {}".format(
                name, fac, spec[0], spec[1], spec[2], spec[3], msg))
        for txt in NOT_CHECKED.get(name, []):
            print("  {:<9} not checked against source: {}".format(name, txt))
    return ok


# --------------------------------------------------------------------------
# rows, units, checks
# --------------------------------------------------------------------------

def unit(module, obj, d, diff="none", jinf=JINF, T=1.0, jg="J10", arm=""):
    return (module, obj, int(d), diff, int(jinf), float(T), jg, arm)


def row_cells(name):
    """(list of units, one per Table 2 cell; realizations per cell), built from
    GRID, which P0(a) checks against the archived source."""
    g = GRID[name]
    c = []
    if name == "BETA-ISO":
        for o in g["objs"]:
            for _b in g["betas"]:
                for d in g["dims"]:
                    c.append(unit("ess_surface", o, d, "isotropic"))
    elif name == "BETA-ANI":
        for o in g["objs"]:
            for _b in g["betas"]:
                for d in g["dims"]:
                    c.append(unit("ess_surface", o, d, "anisotropic"))
    elif name == "LAWPANEL":
        for o in g["objs"]:
            for d in g["dims"]:
                for _law in g["laws"]:
                    c.append(unit("visibility", o, d, jg="J19"))
    elif name in ("CONC", "PROBEARM"):
        for o in g["objs"]:
            for d in g["dims"]:
                for _law in g["laws"]:
                    for _t in g["taus"]:
                        c.append(unit("mechanism", o, d))
    elif name == "ADAPT":
        for o in g["objs"]:
            for d in g["dims"]:
                for _t in g["taus"]:
                    for arm in g["arms"]:
                        c.append(unit("control", o, d, arm=arm))
    elif name == "TAU8":
        for o in g["objs"]:
            for d in g["dims"]:
                for _t in g["taus"]:
                    c.append(unit("boundary", o, d))
    elif name == "REFSIZE":
        for o in g["objs"]:
            for ji in g["jinfs"]:
                c.append(unit("regime", o, g["d"], jinf=ji, jg="J10b"))
    elif name in ("SYNTH", "NAMED"):
        for o in g["objs"]:
            for d in g["dims"]:
                for _t in g["taus"]:
                    c.append(unit("regime", o, d, jg="J10b"))
    elif name == "HORIZON":
        for o in g["objs"]:
            for _law in g["laws"]:
                for T in g["Ts"]:
                    c.append(unit("regime", o, 10, T=T, jg="J10b"))
    elif name == "GEOM":
        for o in g["objs"]:
            for d in g["dims"]:
                for _t in g["taus"]:
                    c.append(unit("law", o, d, jg="J10b"))
    elif name == "SIGMA":
        for df in g["diffs"]:
            for o in g["objs"]:
                for d in g["dims"]:
                    for _r in g["rs"]:
                        for _t in g["taus"]:
                            c.append(unit("sigma", o, d, df))
    elif name == "ANISO":
        for levels in (g["sigmas"], g["rs"]):          # arm A, arm B
            for df in g["diffs"]:
                for o in g["objs"]:
                    for d in g["dims"]:
                        for _lvl in levels:
                            for _t in g["taus"]:
                                c.append(unit("crossed", o, d, df))
    elif name == "RMAP":
        for df in g["diffs"]:
            for o in g["objs"]:
                for d in g["dims"]:
                    for _r in g["rs"]:
                        for _t in g["taus"]:
                            c.append(unit("regimemap", o, d, df))
    elif name == "CLIFF":
        for df in g["diffs"]:
            for o in g["objs"]:
                for d in g["dims"]:
                    for _r in g["rs"]:
                        for _t in g["taus"]:
                            c.append(unit("cliff", o, d, df))
    elif name == "ONSET":
        for df in g["diffs"]:
            for o in g["objs"]:
                for d in g["dims"]:
                    for _r in g["rs"]:
                        c.append(unit("regimemap", o, d, df))
    else:
        raise ValueError(name)
    if g["jgrid"] != JGRIDS[c[0][6]]:
        raise ValueError("row {} uses grid {} but GRID says otherwise".format(name, c[0][6]))
    return c, g["M"]


# A1, A2: (name, base unit, base fields, [variant fields 0, variant fields 1]).
# A3 pairs, one per module, are added by build_plan.
CHECKS = [
    ("A1-ess_surface-beta", unit("ess_surface", "ackley", 10, "isotropic"), {},
     [{"beta_design": 1.0}, {"beta_design": 1000.0}]),
    ("A1-mechanism-tau", unit("mechanism", "ackley", 40), {},
     [{"tau": 0.1}, {"tau": 0.01}]),
    ("A1-boundary-tau", unit("boundary", "levy", 40), {},
     [{"tau": 0.3}, {"tau": 0.01}]),
    ("A1-control-fixed-tau", unit("control", "ackley", 40, arm="fixed"), {},
     [{"tau": 0.1}, {"tau": 0.01}]),
    ("A1-control-adaptive-tau", unit("control", "ackley", 40, arm="adaptive"), {},
     [{"tau": 0.1}, {"tau": 0.01}]),
    ("A1-regime-tau", unit("regime", "syn_k100_r20_w3", 40, jg="J10b"), {},
     [{"tau": 0.1}, {"tau": 0.01}]),
    ("A1-law-tau", unit("law", "syn_k100_r20_w7", 40, jg="J10b"), {},
     [{"tau": 0.3}, {"tau": 0.01}]),
    ("A1-sigma-r", unit("sigma", "sphere", 40, "isotropic"), {},
     [{"r": 0.1}, {"r": 0.99}]),
    ("A1-crossed-sigma", unit("crossed", "ackley", 40, "anisotropic"), {},
     [{"sigma_design": 0.1}, {"sigma_design": 0.4}]),
    ("A1-cliff-r-aniso", unit("cliff", "rosenbrock", 40, "anisotropic"), {},
     [{"r": 0.5}, {"r": 5.0}]),
    ("A1-cliff-r-iso", unit("cliff", "ackley", 40, "isotropic"), {},
     [{"r": 0.5}, {"r": 5.0}]),
    ("A1-regimemap-r", unit("regimemap", "ackley", 80, "isotropic"), {},
     [{"r": 0.75}, {"r": 3.0}]),
    ("A2-visibility-law", unit("visibility", "ackley", 40, jg="J19"), {},
     [{"law": "centred"}, {"law": "mix-0.01"}]),
    ("A2-regime-law", unit("regime", "ackley", 10, jg="J10b"), {},
     [{"law": "centred"}, {"law": "mix-0.1"}]),
    ("A2-mechanism-law", unit("mechanism", "ackley", 40), {},
     [{"law": "centred"}, {"law": "mix-0.1"}]),
]


def micro(x):
    return 0 if x is None else int(round(float(x) * 1000000))


def seed_key(t):
    return (ENTROPY, KIND_PROBE, MODULES.index(t["module"]), OBJ_NAMES.index(t["obj"]),
            t["d"], DIFFS.index(t["diff"]), LAWS.index(t["law"]), t["jinf"], t["K"],
            ARMS.index(t["arm"]), t["variant"], micro(t["tau"]), micro(t["r"]),
            micro(t["beta_design"]), micro(t["sigma_design"]))


def make_task(u, kind, check="", member=0, variant=0, extra=None, rows=None):
    module, obj, d, diff, jinf, T, jg, arm = u
    t = {"module": module, "obj": obj, "d": d, "diff": diff, "jinf": jinf,
         "T": T, "jg": jg, "arm": arm, "law": "centred", "tau": PROBE_TAU,
         "r": PROBE_R, "beta_design": None, "sigma_design": None,
         "kind": kind, "check": check, "member": member, "variant": variant,
         "rows": list(rows or [])}
    if module == "ess_surface":
        t["beta_design"] = 30.0
    for k, v in (extra or {}).items():
        t[k] = v
    t["K"] = int(round(T / DT))
    t["key"] = seed_key(t)
    ks = "-".join(str(x) for x in t["key"])
    t["tid"] = ks if kind == "main" else "{}|{}|m{}".format(check, ks, member)
    return t


def proxy_u(module, d, jinf, K, jg, arm):
    jl = [J for J in JGRIDS[jg] if J <= jinf // 10]
    return d * (jinf + sum(jl)) * K * (ADAPTIVE_PROXY_FACTOR if arm == "adaptive" else 1)


def proxy(t):
    return proxy_u(t["module"], t["d"], t["jinf"], t["K"], t["jg"], t["arm"])


def build_plan(rows, smoke):
    """(main tasks, check tasks). In smoke mode: the A3 pairs only."""
    use = {}
    for name in rows:
        cells, _ = row_cells(name)
        for u in cells:
            use.setdefault(u, set()).add(name)
    mods = sorted(set(u[0] for u in use), key=MODULES.index)
    smallest = {}
    for u in use:
        p = proxy(make_task(u, "main"))
        if u[0] not in smallest or (p, u) < smallest[u[0]]:
            smallest[u[0]] = (p, u)
    chk = []
    for m in mods:                                   # A3: one pair per module
        u = smallest[m][1]
        for mi in (0, 1):
            chk.append(make_task(u, "check", "A3-" + m, mi, 99))
    main = []
    if not smoke:
        main = [make_task(u, "main", rows=sorted(use[u])) for u in sorted(use)]
        for ci, (cname, cu, base, variants) in enumerate(CHECKS):
            if cu[0] not in mods:
                continue
            for mi, vf in enumerate(variants):
                ex = dict(base)
                ex.update(vf)
                chk.append(make_task(cu, "check", cname, mi, 100 + 10 * ci + mi, ex))
    return main, chk


# --------------------------------------------------------------------------
# the worker: one probe, the archived one_realisation, a fixed beta
# --------------------------------------------------------------------------

def objective_of(module, mod, obj):
    if module in ("regime", "law"):
        return mod.objective(obj)[0]
    if module in ("sigma", "crossed", "cliff", "regimemap"):
        return mod.OBJ[obj]
    return mod.OBJECTIVES[obj]


def probe_sample(module, mod, obj, d, law, rng, n):
    """The 4000-point sample for the probe beta: the module's own sampler where
    it has one, else the line its one_realisation uses for X0."""
    if module in ("control", "mechanism", "visibility"):
        return mod.draw_initial(rng, n, d, obj, law)
    if module == "regime":
        return mod.draw_initial(rng, n, d, mod.objective(obj)[1], law)
    if module == "boundary":
        return rng.standard_normal((n, d)) + mod.MINIMIZER[obj]
    if module == "law":
        return rng.standard_normal((n, d)) + mod.objective(obj)[1]
    if module in ("sigma", "crossed", "cliff"):
        return rng.standard_normal((n, d)) + mod.XSTAR[obj]
    if module == "regimemap":
        return rng.standard_normal((n, d))
    raise ValueError(module)


def probe_beta(t, mod):
    m = t["module"]
    if m == "ess_surface":
        return float(t["beta_design"])
    if m == "visibility":
        return 30.0 / mod.scales_of(t["obj"], t["d"], t["law"])[1]
    if m == "mechanism":
        return float(mod.beta_for_target(t["obj"], t["d"], t["law"], t["tau"])[0])
    key = (ENTROPY, KIND_BETA, MODULES.index(m), OBJ_NAMES.index(t["obj"]), t["d"],
           LAWS.index(t["law"]), micro(t["tau"]))
    rng = np.random.default_rng(np.random.SeedSequence(list(key)))
    X = probe_sample(m, mod, t["obj"], t["d"], t["law"], rng, PROBE_N)
    fv = objective_of(m, mod, t["obj"])(X)
    return float(mod.solve_beta(fv - fv.min(), math.log(t["tau"] * PROBE_N)))


def probe_sigma(t, mod):
    if t["sigma_design"] is not None:
        return float(t["sigma_design"])
    if t["module"] in ("sigma", "crossed", "cliff", "regimemap"):
        return float(mod.sigma_of(t["diff"], t["d"], t["r"]))
    return SIGMA_ISO


def run_task(t):
    out = dict(t)
    try:
        m = t["module"]
        mod = MODS[m]
        t0 = time.time()
        beta = probe_beta(t, mod)
        sg = probe_sigma(t, mod)
        out["beta_wall"] = time.time() - t0
        jl = [J for J in JGRIDS[t["jg"]] if J <= t["jinf"] // 10]
        seed = np.random.SeedSequence(list(t["key"]))
        K, ji, d, o = t["K"], t["jinf"], t["d"], t["obj"]
        t1 = time.time()
        if m == "ess_surface":
            res, _ = mod.one_realisation(o, t["diff"], beta, d, sg, DT, K, ji, jl, seed)
            E = dict((J, res[J][0]) for J in jl)
        elif m == "visibility":
            E, _ = mod.one_realisation(o, beta, d, t["law"], sg, DT, K, ji, jl, seed)
        elif m == "mechanism":
            E, _, _ = mod.one_realisation(o, beta, d, t["law"], sg, DT, K, ji, jl, seed)
        elif m == "control":
            E = mod.one_realisation(o, d, t["law"], t["tau"], t["arm"], beta, sg, DT, K,
                                    ji, jl, seed)[0]
        elif m == "boundary":
            E = mod.one_realisation(o, d, t["tau"], beta, sg, DT, K, ji, jl, seed)[0]
        elif m == "regime":
            E, _ = mod.one_realisation(o, d, t["law"], beta, sg, DT, K, ji, jl, seed)
        elif m == "law":
            E = mod.one_realisation(o, d, beta, sg, DT, K, ji, jl, seed)[0]
        elif m in ("sigma", "crossed", "cliff"):
            E = mod.one_realisation(o, d, t["diff"], beta, sg, LAM, DT, K, ji, jl, seed)[0]
        elif m == "regimemap":
            r = mod.one_realisation(o, d, t["diff"], beta, sg, LAM, DT, K, ji, jl, seed)
            E = dict((J, float(v)) for J, v in zip(jl, r["E"]))
        else:
            raise ValueError(m)
        out["wall"] = time.time() - t1
        out["E"] = dict((J, float(E[J])) for J in jl)
        out["beta"] = beta
        out["sigma"] = sg
        try:
            out["slope"] = float(MODS["exactcal"].fit_slope(jl, [E[J] for J in jl]))
        except Exception:
            out["slope"] = float("nan")
        out["end"] = "ok"
    except Exception as exc:
        out["error"] = "{}: {}".format(type(exc).__name__, exc)
        out["end"] = "err"
    out["rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out["pid"] = os.getpid()
    return out


def child_main(t, conn):
    """Entry point of the fresh process that runs one probe."""
    try:
        conn.send(run_task(t))
    finally:
        conn.close()


def error_row(t, msg, pid):
    o = dict(t)
    o["error"] = msg
    o["end"] = "err"
    o["rss"] = float("nan")
    o["pid"] = pid
    return o


# --------------------------------------------------------------------------
# results files
# --------------------------------------------------------------------------

RES_COLS = (["tid", "kind", "check", "member", "rows", "module", "objective", "d",
             "diffusion", "law", "J_inf", "T", "K", "J_grid", "arm", "tau0", "r",
             "beta_design", "sigma_design", "beta", "sigma", "beta_wall_s", "wall_s",
             "peak_rss_mb", "pid", "seed_key", "slope"]
            + ["E_{}".format(J) for J in JCOLS] + ["error", "end"])


def res_row(o):
    def fx(x):
        return "" if x is None else repr(float(x))
    E = o.get("E", {})
    return ([o["tid"], o["kind"], o["check"], o["member"], ";".join(o["rows"]),
             o["module"], o["obj"], o["d"], o["diff"], o["law"], o["jinf"], o["T"],
             o["K"], o["jg"], o["arm"], fx(o["tau"]), fx(o["r"]), fx(o["beta_design"]),
             fx(o["sigma_design"]), fx(o.get("beta")), fx(o.get("sigma")),
             "{:.3f}".format(o.get("beta_wall", float("nan"))),
             "{:.3f}".format(o.get("wall", float("nan"))), "{:.1f}".format(o["rss"]),
             o["pid"], "-".join(str(x) for x in o["key"]),
             "" if "slope" not in o else "{:.6f}".format(o["slope"])]
            + [("%.17g" % E[J]) if J in E else "" for J in JCOLS]
            + [o.get("error", ""), o["end"]])


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verify_folder(folder):
    """Every file listed in folder/sha256.txt must hash as listed. Returns the
    listed relative paths; exits 2 otherwise."""
    man = os.path.join(folder, "sha256.txt")
    if not os.path.isfile(man):
        sys.stderr.write("{} has no sha256.txt\n".format(folder))
        sys.exit(2)
    rels = []
    with open(man) as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln:
                continue
            h, rel = ln.split("  ", 1)
            if sha256_file(os.path.join(folder, rel)) != h:
                sys.stderr.write("{} fails its manifest at {}\n".format(folder, rel))
                sys.exit(2)
            rels.append(rel)
    return rels


def read_folder(folder):
    """(params dict or None, list of result rows as dicts) from a verified folder."""
    rels = verify_folder(folder)
    params, rows = None, []
    for rel in rels:
        base = os.path.basename(rel)
        p = os.path.join(folder, rel)
        if base == "costprobe2_params.csv":
            if params is not None:
                sys.stderr.write("two params files in {}\n".format(folder))
                sys.exit(2)
            params = dict((r[0], r[1]) for r in csv.reader(open(p, newline="")) if r)
        elif base == "costprobe2_results.csv":
            rows.extend(csv.DictReader(open(p, newline="")))
    return params, rows


def row_unit(r):
    return unit(r["module"], r["objective"], int(r["d"]), r["diffusion"], int(r["J_inf"]),
                float(r["T"]), r["J_grid"], r["arm"])


# --------------------------------------------------------------------------
# T1: the timeout
# --------------------------------------------------------------------------

def timeout_for(queue, timing_rows):
    if timing_rows:
        rates = []
        for r in timing_rows:
            if r["end"] != "ok":
                continue
            u = row_unit(r)
            p = proxy_u(u[0], u[2], u[4], int(r["K"]), u[6], u[7])
            rates.append(float(r["wall_s"]) / p)
        if not rates:
            sys.stderr.write("setup error: --timing-from holds no completed probe\n")
            sys.exit(2)
        src = "--timing-from, {} completed probes".format(len(rates))
    else:
        rates = [w / proxy_u("exactcal", d, JINF, 100, "J10", "") for _o, d, w in COSTPROBE_LOG]
        src = "logs/costprobe.log, 24 laptop probes (embedded)"
    rate = max(rates)
    if not queue:
        return rate, src, None, 0.0, 0.0
    big = max(queue, key=proxy)
    proj = rate * proxy(big)
    return rate, src, big, proj, TIMEOUT_FACTOR * proj


# --------------------------------------------------------------------------
# P3
# --------------------------------------------------------------------------

def objcheck(outdir):
    hdr("P3 -- OBJECTIVE IDENTITY (reported; no decision rests on it)")
    ec = MODS["exactcal"]
    lines = []
    for d in (2, 40):
        rng = np.random.default_rng(np.random.SeedSequence([ENTROPY, KIND_OBJ, d]))
        X = 3.0 * rng.standard_normal((1000, d)) + 0.5
        for m in DYN_MODULES:
            mod = MODS[m]
            for o in OBJ6:
                try:
                    f = objective_of(m, mod, o)
                except Exception:
                    continue
                a, b = f(X), ec.OBJECTIVES[o](X)
                lines.append([m, "exactcal", o, d,
                              "same" if np.array_equal(a, b) else "differs",
                              "{:.3e}".format(float(np.max(np.abs(a - b))))])
        for o in REG_SYNTH:
            if o in LAW_SYNTH:
                a = MODS["regime"].objective(o)[0](X)
                b = MODS["law"].objective(o)[0](X)
                lines.append(["regime", "law", o, d,
                              "same" if np.array_equal(a, b) else "differs",
                              "{:.3e}".format(float(np.max(np.abs(a - b))))])
    nd = [ln for ln in lines if ln[4] != "same"]
    print("  {} comparisons, {} differ".format(len(lines), len(nd)))
    for ln in nd:
        print("    DIFFERS  {} vs {}  {}  d={}  max |diff| {}".format(ln[0], ln[1], ln[2], ln[3], ln[5]))
    if outdir:
        with open(os.path.join(outdir, "costprobe2_objcheck.csv"), "x", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["module", "against", "objective", "d", "verdict", "max_abs_diff"])
            w.writerows(lines)


# --------------------------------------------------------------------------
# finalize: P2, A1-A3, A-ERR, P4, P5
# --------------------------------------------------------------------------

def finalize(rows, outdir, sel_rows, workers, smoke):
    """Returns the exit code: 3 if P2 failed, else 4 if any check errored, else 0."""
    hdr("FINALIZE -- P2, A1 to A3, A-ERR, P4, P5 from {} result rows (W = {})".format(
        len(rows), workers))
    for r in rows:
        if r["end"] != "ok":
            print("  ERROR row {}: {}".format(r["tid"], r["error"]))
    wall, rssu = {}, {}
    for r in rows:
        if r["kind"] == "main" and r["end"] == "ok":
            wall[row_unit(r)] = float(r["wall_s"])
            rssu[row_unit(r)] = float(r["peak_rss_mb"])

    _, planned = build_plan(sel_rows, smoke)
    expected = {}
    for t in planned:
        expected.setdefault(t["check"], (t["module"], set()))[1].add(t["member"])
    got = {}
    for r in rows:
        if r["kind"] == "check":
            got.setdefault(r["check"], {})[int(r["member"])] = r

    scale = dict((m, 1.0) for m in MODULES)
    errored_mod = set()
    a3 = {}
    p2_fail, any_err = False, False
    lines = []
    for cname in sorted(expected, key=lambda c: (not c.startswith("A3"), c)):
        module, members = expected[cname]
        pair = got.get(cname, {})
        bad = []
        for mi in sorted(members):
            if mi not in pair:
                bad.append("member {} missing".format(mi))
            elif pair[mi]["end"] != "ok":
                bad.append("member {}: {}".format(mi, pair[mi]["error"]))
        if bad:
            verdict = "FAIL (errored: {})".format("; ".join(bad))
            if cname.startswith("A3"):
                p2_fail = True
            else:
                any_err = True
                errored_mod.add(module)
            lines.append([cname, module, "", "", "", verdict, CAVEAT])
            continue
        w0, w1 = float(pair[0]["wall_s"]), float(pair[1]["wall_s"])
        ratio = max(w0, w1) / min(w0, w1) if min(w0, w1) > 0 else float("inf")
        if cname.startswith("A3"):
            same = all(pair[0]["E_{}".format(J)] == pair[1]["E_{}".format(J)] for J in JCOLS)
            a3[module] = ratio
            if not same:
                p2_fail = True
            verdict = "P2 {}; noise ratio {}".format(
                "PASS" if same else "FAIL (E_J differ)",
                "above 1.25" if ratio > RATIO_MAX else "within 1.25")
        else:
            verdict = "PASS" if ratio <= RATIO_MAX else "FAIL"
            if verdict == "FAIL":
                scale[module] = max(scale[module], ratio)
        lines.append([cname, module, "{:.3f}".format(w0), "{:.3f}".format(w1),
                      "{:.4f}".format(ratio), verdict, CAVEAT])
    print("\n  {:<26} {:<12} {:>10} {:>10} {:>8}  verdict".format("check", "module", "wall 0", "wall 1", "ratio"))
    for ln in lines:
        noisy = (not ln[0].startswith("A3")) and a3.get(ln[1], 0.0) > RATIO_MAX
        print("  {:<26} {:<12} {:>10} {:>10} {:>8}  {}{}   [{}]".format(
            ln[0], ln[1], ln[2], ln[3], ln[4], ln[5], "  (noise-limited)" if noisy else "", ln[6]))
    p2 = "FAIL" if p2_fail else "PASS"
    print("\n  P2 (one A3 pair per module, bitwise E_J): {}".format(p2))
    if any_err:
        print("  A-ERR: at least one A1/A2 check errored; exit code 4 unless P2 failed")

    proj = []
    proj_rows = [] if smoke else sel_rows
    if proj_rows:
        print("\n  P4 budget {:.0f} MB per worker; P5 at W = {} workers, ceiling {:.0f} s per shard".format(
            RSS_BUDGET_MB, workers, SHARD_CEIL_S))
        print("  {:<10} {:>6} {:>7} {:>6} {:>10} {:>10} {:>7} {:>7} {:>9} {:>15}  label".format(
            "row", "cells", "real.", "units", "core h", "wall h", "shards", "scale", "max RSS", "P4"))
    for name in proj_rows:
        cells, M = row_cells(name)
        units = sorted(set(cells))
        miss = [u for u in units if u not in wall]
        mod = units[0][0]
        if miss:
            proj.append([name, len(cells), len(cells) * M, len(units), "", "", "", "", "", "",
                         "NOT PROJECTED: missing " + ";".join("/".join(str(x) for x in u) for u in miss)])
            print("  {:<10} {:>6} {:>7} {:>6}  NOT PROJECTED: {} unit(s) missing".format(
                name, len(cells), len(cells) * M, len(units), len(miss)))
            continue
        core = sum(M * wall[u] * scale[mod] for u in cells)
        wW = core / float(workers)
        sh = int(math.ceil(wW / SHARD_CEIL_S))
        mx = max(rssu[u] for u in units)
        p4 = "pass" if mx <= RSS_BUDGET_MB else "EXCEEDS BUDGET"
        label = SCALED_LABEL if scale[mod] > 1.0 else LB_LABEL
        if mod in errored_mod:
            label += "; check errored"
        proj.append([name, len(cells), len(cells) * M, len(units), "{:.1f}".format(core),
                     "{:.1f}".format(wW), sh, "{:.4f}".format(scale[mod]), "{:.1f}".format(mx),
                     p4, label])
        print("  {:<10} {:>6} {:>7} {:>6} {:>10.2f} {:>10.2f} {:>7} {:>7.3f} {:>9.1f} {:>15}  {}".format(
            name, len(cells), len(cells) * M, len(units), core / 3600.0, wW / 3600.0, sh,
            scale[mod], mx, p4, label))
    if outdir:
        with open(os.path.join(outdir, "costprobe2_checks.csv"), "x", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["check", "module", "wall0_s", "wall1_s", "ratio", "verdict", "caveat"])
            w.writerows(lines)
            w.writerow(["P2", "", "", "", "", p2, ""])
        with open(os.path.join(outdir, "costprobe2_projection.csv"), "x", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["row", "cells", "realizations", "units", "core_s", "wall_s",
                        "shards_at_6h", "scale", "max_rss_mb", "P4", "label"])
            w.writerows(proj)
    return 3 if p2_fail else (4 if any_err else 0)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def hdr(s):
    print("\n" + "-" * 96)
    print(s)
    print("-" * 96)


def merge_folders(folders):
    """D1 rule: a repeated task id is accepted only when every earlier
    occurrence is an error row; a repeated completed row stops the run."""
    merged, order, ref = {}, [], None
    for f in folders:
        pr, rr = read_folder(f)
        if pr is None:
            sys.stderr.write("{} has no params file\n".format(f))
            sys.exit(2)
        cmp_ = dict((k, v) for k, v in pr.items() if k != "shard")
        if ref is None:
            ref = cmp_
        elif cmp_ != ref:
            sys.stderr.write("{} was run with other parameters: {} vs {}\n".format(f, cmp_, ref))
            sys.exit(2)
        rep = 0
        for r in rr:
            tid = r["tid"]
            if tid in merged:
                if merged[tid]["end"] == "ok":
                    sys.stderr.write("task {} is complete in an earlier folder and repeated in {}\n".format(tid, f))
                    sys.exit(2)
                rep += 1
            else:
                order.append(tid)
            merged[tid] = r
        print("  read {}: {} rows, {} replacing earlier error rows".format(f, len(rr), rep))
    return [merged[t] for t in order], ref


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--rows", default=None,
                   help="comma-separated rows; default all. With --finalize the rows come "
                        "from the folders, and a --rows that disagrees is an error")
    p.add_argument("--plan", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--nshards", type=int, default=1)
    p.add_argument("--resume-from", default="")
    p.add_argument("--finalize", default="")
    p.add_argument("--timing-from", default="")
    p.add_argument("--archive", default=None,
                   help="deposited archive; default <repo>/zenodo-v1 or CBOGAP_ARCHIVE")
    p.add_argument("--outdir", default=None,
                   help="output root; default <repo>/runs or CBOGAP_OUTDIR")
    a = p.parse_args()
    rows_given = a.rows is not None
    sel = [r for r in (a.rows if rows_given else ",".join(ROW_ORDER)).split(",") if r]
    for r in sel:
        if r not in TABLE2:
            sys.stderr.write("setup error: unknown row {}\n".format(r))
            sys.exit(2)
    if not (0 <= a.shard < a.nshards) or a.workers < 1:
        sys.stderr.write("setup error: need 0 <= shard < nshards and workers >= 1\n")
        sys.exit(2)
    mode = "finalize" if a.finalize else ("plan" if a.plan else ("smoke" if a.smoke else "full"))
    me = sha256_file(os.path.abspath(__file__))

    print("=" * 96)
    print("CBO-GAP costprobe2 -- cost of every rerun row, measured with each row's own dynamics")
    print("=" * 96)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers))
    print("  start    {}".format(multiprocessing.get_start_method()))
    print("  threads  " + "  ".join("{}={}".format(v, os.environ.get(v)) for v in THREAD_VARS))
    print("  archive  {}".format(ARCH))
    print("  script   sha256 {}".format(me))
    print("  mode     {}   shard {} of {}   rows {}".format(mode, a.shard, a.nshards, ",".join(sel)))
    print("  fixed    dt {}  lambda {}  iso sigma {}  probe tau0 {}  probe r {}  probe sample {}".format(
        DT, LAM, SIGMA_ISO, PROBE_TAU, PROBE_R, PROBE_N))
    print("  seeds    default_rng(SeedSequence(key)), full width; key = (ENTROPY {}, kind {}, module, "
          "objective, d, diffusion, law, J_inf, K, arm, variant, tau0e6, re6, beta_design e6, "
          "sigma_design e6); probe-beta kind {}; P3 kind {}".format(ENTROPY, KIND_PROBE, KIND_BETA, KIND_OBJ))
    print("  P4       peak RSS <= {:.0f} MB per worker;  A1-A3 ratio <= {};  P5 ceiling {:.0f} s per shard".format(
        RSS_BUDGET_MB, RATIO_MAX, SHARD_CEIL_S))

    hdr("P1 -- ARCHIVE IDENTITY (the imported modules' own files)")
    p1 = True
    arch_real = os.path.realpath(ARCH)
    for m in MODULES:
        f = os.path.realpath(MODS[m].__file__)
        where = os.path.dirname(f) == arch_real and f.endswith(".py")
        h = sha256_file(f)
        okm = where and (h == ARCHIVE_SHA256[m])
        p1 &= okm
        print("  {:<12} {}  {}  {}".format(m, h, f, "ok" if okm else "MISMATCH"))
    if not p1:
        print("\nP1 FAILED: an imported module is not the deposited file. Nothing runs.")
        sys.exit(2)
    print("  P1 PASS")

    hdr("P0 -- PLAN IDENTITY: (a) grid values against the archived source, (b) counts against Table 2")
    p0 = p0_values(sel)
    for name in sel:
        try:
            cells, M = row_cells(name)
        except Exception as exc:
            print("  {:<10} cannot build cells: {}".format(name, exc))
            p0 = False
            continue
        want = TABLE2[name]
        got = (len(cells), len(cells) * M)
        okr = (got == want)
        p0 &= okr
        print("  {:<10} cells {:>4} (Table 2 {:>4})   realizations {:>5} (Table 2 {:>5})   units {:>3}   {}".format(
            name, got[0], want[0], got[1], want[1], len(set(cells)), "ok" if okr else "MISMATCH"))
    if not p0:
        print("\nP0 FAILED: a grid does not reproduce the archive or Table 2. Nothing runs.")
        sys.exit(2)
    print("  P0 PASS")

    if mode == "finalize":
        hdr("FINALIZE FOLDERS (repeated task ids: only error rows may be replaced)")
        rows, ref = merge_folders([x for x in a.finalize.split(",") if x])
        # R4: the rows come from the folders' params, never from this invocation
        fsel = [r for r in ref["rows"].split(",") if r]
        for r in fsel:
            if r not in TABLE2:
                sys.stderr.write("finalize: the folders name an unknown row {}\n".format(r))
                sys.exit(2)
        if rows_given and sel != fsel:
            sys.stderr.write("finalize: --rows {} disagrees with the folders' rows {}; "
                             "omit --rows or pass the folders' rows\n".format(",".join(sel), ",".join(fsel)))
            sys.exit(2)
        print("  rows from the folders' params: {}".format(",".join(fsel)))
        sel = fsel
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = os.path.join(OUTROOT, "costprobe2-finalize-{}".format(stamp))
        os.makedirs(outdir)
        code = finalize(rows, outdir, sel, int(ref["workers"]), ref["mode"] == "smoke")
        print("\nfiles  {}".format(outdir))
        sys.exit(code)

    main_t, chk_t = build_plan(sel, a.smoke)
    keys = {}
    for t in main_t + chk_t:
        if t["check"].startswith("A3") and t["member"] == 1:
            continue
        if t["key"] in keys:
            sys.stderr.write("setup error: duplicate seed key {}\n".format(t["key"]))
            sys.exit(2)
        keys[t["key"]] = t["tid"]
    main_t = [t for i, t in enumerate(sorted(main_t, key=lambda x: x["tid"])) if i % a.nshards == a.shard]
    if a.shard != 0:
        chk_t = []
    hdr("PLAN")
    bym = {}
    for t in main_t:
        bym[(t["module"], t["d"])] = bym.get((t["module"], t["d"]), 0) + 1
    for (m, d) in sorted(bym):
        print("  {:<12} d={:<3} {:>4} main probe(s)".format(m, d, bym[(m, d)]))
    print("  main probes {}   check probes {}   total {}".format(len(main_t), len(chk_t), len(main_t) + len(chk_t)))

    timing_rows = []
    if a.timing_from:
        for f in [x for x in a.timing_from.split(",") if x]:
            timing_rows.extend(read_folder(f)[1])
    rate, src, big, projb, timeout_s = timeout_for(main_t + chk_t, timing_rows)
    hdr("T1 -- PER-TASK TIMEOUT")
    print("  rate {:.3e} s per proxy unit, from {}".format(rate, src))
    if big is not None:
        print("  largest unit {} {} d={} {} J_inf={} T={} {} {}  proxy {:.3e}".format(
            big["module"], big["obj"], big["d"], big["diff"], big["jinf"], big["T"], big["jg"],
            big["arm"] or "-", proxy(big)))
        print("  projected wall of the largest unit {:.1f} s;  TIMEOUT_S = {} x {:.1f} = {:.1f} s".format(
            projb, TIMEOUT_FACTOR, projb, timeout_s))

    if mode == "plan":
        print("\nPLAN MODE: no dynamics run, nothing written.")
        sys.exit(0)

    params = [["script_sha256", me], ["mode", mode], ["rows", ",".join(sel)],
              ["shard", a.shard], ["nshards", a.nshards], ["workers", a.workers],
              ["python", platform.python_version()], ["numpy", np.__version__]]
    done = set()
    if a.resume_from:
        hdr("RESUME (CLAUDE.md rule 17)")
        mine = dict((k, str(v)) for k, v in params)
        for f in [x for x in a.resume_from.split(",") if x]:
            pr, rr = read_folder(f)
            if pr is None:
                sys.stderr.write("resume: {} has no params file\n".format(f))
                sys.exit(2)
            for k, v in mine.items():
                if pr.get(k) != v:
                    sys.stderr.write("resume: {} has {}={}, this run {}\n".format(f, k, pr.get(k), v))
                    sys.exit(2)
            n = 0
            for r in rr:
                if r["end"] != "ok":
                    continue
                if r["tid"] in done:
                    sys.stderr.write("resume: task {} found twice\n".format(r["tid"]))
                    sys.exit(2)
                done.add(r["tid"])
                n += 1
            print("  read {}: {} completed task(s) skipped".format(f, n))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = "-smoke" if mode == "smoke" else ""
    if a.nshards > 1:
        tag += "-s{}of{}".format(a.shard, a.nshards)
    outdir = os.path.join(OUTROOT, "costprobe2-{}{}".format(stamp, tag))
    os.makedirs(outdir)
    with open(os.path.join(outdir, "costprobe2_params.csv"), "x", newline="") as fh:
        csv.writer(fh).writerows(params)
    print("\n  run dir  {}".format(outdir))

    objcheck(outdir)

    # checks first, pairs adjacent (neighbour load uncontrolled); then main
    # probes, largest proxy first
    queue = [t for t in chk_t if t["tid"] not in done]
    queue += sorted([t for t in main_t if t["tid"] not in done], key=lambda x: -proxy(x))
    hdr("PROBES  {} task(s), at most {} at once, one fresh process each, timeout {:.0f} s".format(
        len(queue), a.workers, timeout_s))
    rows_written = []
    t0 = time.time()
    fh = open(os.path.join(outdir, "costprobe2_results.csv"), "x", newline="")
    w = csv.writer(fh)
    w.writerow(RES_COLS)
    fh.flush()
    os.fsync(fh.fileno())
    pending = list(queue)
    running = []
    nout = 0
    try:
        while pending or running:
            while pending and len(running) < a.workers:
                t = pending.pop(0)
                rc, sc = multiprocessing.Pipe(duplex=False)
                pr_ = multiprocessing.Process(target=child_main, args=(t, sc))
                pr_.start()
                sc.close()
                running.append([pr_, rc, t, time.monotonic()])
            progressed = False
            for item in list(running):
                pr_, rc, t, ts = item
                o = None
                if rc.poll():
                    try:
                        o = rc.recv()
                    except EOFError:
                        pr_.join()
                        o = error_row(t, "worker exited with code {} without a result".format(pr_.exitcode), pr_.pid)
                    pr_.join()
                elif not pr_.is_alive():
                    pr_.join()
                    o = error_row(t, "worker exited with code {} without a result".format(pr_.exitcode), pr_.pid)
                elif time.monotonic() - ts > timeout_s:
                    pr_.terminate()
                    pr_.join()
                    o = error_row(t, "timeout after {:.0f} s (TIMEOUT_S {:.0f} s)".format(
                        time.monotonic() - ts, timeout_s), pr_.pid)
                if o is None:
                    continue
                rc.close()
                running.remove(item)
                progressed = True
                nout += 1
                row = res_row(o)
                w.writerow(row)
                fh.flush()
                os.fsync(fh.fileno())
                rows_written.append(dict(zip(RES_COLS, [str(x) for x in row])))
                el = time.time() - t0
                if o["end"] == "ok":
                    print("  [{:>4}/{:<4}] {:<11} {:<17} d={:<3} {:<11} Jinf={:<6} T={:<3} {:<5} {:<8} "
                          "wall {:>8.1f} s  RSS {:>7.1f} MB{}  elapsed {:>8.0f} s".format(
                              nout, len(queue), o["module"], o["obj"], o["d"], o["diff"], o["jinf"],
                              o["T"], o["jg"], o["arm"] or "-", o["wall"], o["rss"],
                              "  OVER BUDGET" if o["rss"] > RSS_BUDGET_MB else "", el))
                else:
                    print("  [{:>4}/{:<4}] ERROR {} {} d={}: {}".format(
                        nout, len(queue), o["module"], o["obj"], o["d"], o["error"]))
                sys.stdout.flush()
            if not progressed:
                time.sleep(0.2)
    finally:
        for pr_, rc, _t, _ts in running:
            pr_.terminate()
            pr_.join()
        fh.close()
    print("  probes finished in {:.1f} s".format(time.time() - t0))

    code = 0
    if a.nshards == 1 and not a.resume_from:
        if mode == "smoke":
            hdr("SMOKE: the A3 pair of each module; no projection")
            for r in rows_written:
                print("  {:<12} {:<17} d={:<3} member {} wall {} s  RSS {} MB  end {}".format(
                    r["module"], r["objective"], r["d"], r["member"], r["wall_s"], r["peak_rss_mb"], r["end"]))
            code = finalize(rows_written, None, sel, a.workers, True)
        else:
            code = finalize(rows_written, outdir, sel, a.workers, False)
    else:
        print("\n  Sharded or resumed run: finalize after every shard is fetched, with")
        print("  --finalize <folder>,<folder>,... (no dynamics).")
    print("\n" + "=" * 96)
    print("files  {}".format(outdir))
    print("=" * 96)
    sys.exit(code)


if __name__ == "__main__":
    main()
