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
  * J_inf = 12500, 25000, 50000, 100000 (EXP-REFSIZE; ledger F6 requires the
    peak RSS at 100000 before that row runs);
  * T = 0.5, 1, 2 (EXP-HORIZON);
  * the 19-point J grid of visibility.py and the 10-point grids
    (J10, and J10b with 1250 and 2500 for regime.py and law.py);
  * both arms of control.py, including the adaptive arm, which re-solves
    beta at every step.

It writes per-probe, per-J errors, wall time and per-worker peak RSS. It then
PROJECTS each rerun row's cost from what it measured. The projection is
arithmetic on measured times, printed by the script, and labelled a lower
bound. It decides nothing about the science and calibrates nothing that is
used later: the probe beta is for timing only.

NOTHING IS REIMPLEMENTED
  Every realization is the archived module's own one_realisation, imported
  from the archive (CLAUDE.md rule 4) and called with a fixed beta. The
  probe beta is computed by the module's own calibration code, as follows:
    ess_surface  the design value 30.0, which is on both of its beta grids;
    visibility   30 / visibility.scales_of(...)[1], the archived B rule;
    mechanism    mechanism.beta_for_target(..., tau0), the archived probe;
    the others   the module's own solve_beta on a 4000-point sample from its
                 own initial law, at the probe's tau0.
  The only lines not imported are the 4000-point samplers for modules whose
  one_realisation draws X0 inline (boundary, law, sigma, crossed, cliff,
  regimemap): rng.standard_normal((n, d)) + x*, with x* from the module's own
  dict. They affect the probe beta only, never the dynamics.

THE COST MODEL, AND THE ASSUMPTION IT RESTS ON
  A probe UNIT is
      (module, objective, d, diffusion, J_inf, T, J grid, arm).
  The wall time of a realization is assumed to depend on the unit only: not
  on beta, tau0, r, sigma, the initial law or the seed. The assumption is
  tested, not asserted, by criteria A1 to A3 below. Each Table 2 cell of a
  rerun row maps to exactly one unit.

PRE-SPECIFIED CRITERIA (fixed 2026-10-10, before first execution)
------------------------------------------------------------------
  P0  PLAN IDENTITY. For every rerun row the script builds its cell list
      from the grid read from the archived script (notes/RERUN_PLAN.md). The
      cell and realization counts must equal the Table 2 counts embedded
      below (TABLE2), or the script exits 2 before any computation.
      Worked example: EXP-SIGMA is 2 diffusions x 4 objectives x 3 d x 6 r x
      2 tau0 = 288 cells, at 12 realizations = 3456: equal to Table 2, pass.
      An r list with five values would give 240 cells: exit 2.
  P1  ARCHIVE IDENTITY. The sha256 of every imported archive module must
      equal its entry in zenodo-v1.sha256, embedded below (ARCHIVE_SHA256),
      or the script exits 2. Worked example: regimemap.py must hash to
      eb1d704f...14c8. A file edited by one byte hashes differently: exit 2.
  P2  SEED PASS-THROUGH AND DETERMINISM. Every probe passes
      numpy.random.SeedSequence(key) unchanged as the seed argument of the
      archived one_realisation, which calls default_rng(seed) on it. Check
      A3 runs one task twice with the same key in two worker processes.
      Every E_J must be bitwise identical, compared as its %.17g string,
      which identifies a double uniquely. If not, P2 FAILS, all rows are
      still written, and the exit code is 3. Worked example: E_10 =
      0.056786325012345678 in both runs: pass. A difference in the last bit
      of any E_J changes its %.17g string: fail.
  P3  OBJECTIVE IDENTITY (reported; no decision rests on it). For every
      module and named objective, f is evaluated on a fixed array of 1000
      points (seed kind 43) at d = 2 and d = 40 and compared bitwise with
      exactcal.OBJECTIVES. The regime.py and law.py synthetic objectives
      with the same name are compared with each other. This informs
      notes/CALPREC_V2_SPEC.md; calibration is through each row's own module
      whatever P3 shows (RERUN_PLAN F5). Worked example: boundary's ackley
      equal to exactcal's in every element: "same".
  P4  MEMORY BUDGET. Each probe runs in a fresh worker (maxtasksperchild=1).
      Its peak RSS (resource.getrusage, Linux kilobytes / 1024) must be at
      most 3072 MB (Rahul, 2026-10-10: 3 GB per worker, so four workers stay
      under half of Kaggle's 30 GB). A row passes P4 when every unit it uses
      passes. Worked example: units at 180, 330 and 2950 MB: pass. One unit
      at 3100 MB: that row fails P4 and is flagged "exceeds budget".
  A1  COST INDEPENDENCE OF BETA, TAU0, R AND SIGMA. Each check in CHECKS
      below runs one unit twice, differing only in a calibration or
      diffusion-strength input. The two runs are queued next to each other,
      so they run at the same load. ratio = max(wall) / min(wall). PASS when
      ratio <= 1.25. On FAIL, every row of that module is projected with its
      walls multiplied by the largest failing ratio of that module, and is
      flagged. Worked example: 30.0 s and 36.0 s give 1.20: pass. 30.0 s and
      40.0 s give 1.333: fail, and that module's rows are scaled by 1.333.
  A2  COST INDEPENDENCE OF THE INITIAL LAW. As A1, with the initial law
      varied; same ratio, threshold and consequence.
  A3  TIMING NOISE. The P2 pair, the same task twice. Its ratio is the
      timing-noise yardstick. If it exceeds 1.25, every A1 and A2 verdict is
      labelled "noise-limited". The scaling rule above still applies.
  P5  PROJECTION (lower bound, labelled). For each rerun row:
          core_s  = sum over its cells of M_row x wall(unit of the cell)
                    x scale(module)
          wall4_s = core_s / 4
          shards  = ceil(wall4_s / 21600)
      21600 s is the 6-hour ceiling per shard (Rahul, 2026-10-10). Walls are
      measured with up to --workers probes running at once on the same
      machine, so they include the load of a saturated pool. The division by
      4 assumes perfect scaling. Scheduling gaps and the tail of a run are
      ignored, so this is a lower bound. Worked example: 144 cells, M = 15,
      every unit 40.0 s, scale 1: core_s = 86400, wall4_s = 21600,
      shards = 1. At 40.1 s: wall4_s = 21654, shards = 2.
  A row is NOT PROJECTED when any of its units has no completed probe; the
  missing units are listed.

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
  below. The plan refuses duplicate keys, except the A3 pair, whose
  duplication is the test (variant 99, used by no other task). calprec v2 uses the same ENTROPY with kinds 31 to
  34 (notes/CALPREC_V2_SPEC.md), so no stream here coincides with one there.
  Every key is written out in full in the results CSV.

MODES
  --plan      Print the rows, P0, P1, the probe list and its size. Run no
              dynamics and write nothing.
  --smoke     The smallest unit of every module, plus the A3 pair. This
              tests imports, P1, P2, P3 and the plumbing on a new platform.
              It projects nothing: walls at the smallest d say nothing
              about d = 80.
  (default)   Every unit needed by the rows selected with --rows (default:
              all), plus every check whose module is among them.
  --shard i --nshards k   Main probes, sorted by task id, go to shard
              (index mod k). All checks go to shard 0. Each shard is a
              separate job with a distinct name (CLAUDE.md rule 17).
  --resume-from DIR[,DIR]  CLAUDE.md rule 17 as amended 2026-10-10:
              - each DIR is read only after its sha256.txt verifies;
              - a task counts as completed only when its row ends in "ok";
              - a task id found twice stops the run;
              - the parameters in each DIR's costprobe2_params.csv, other
                than the folder list, must equal this run's, or it stops;
              - output goes to a new folder, and the script prints every
                folder read and the number of tasks skipped from each.
  --finalize DIR[,DIR]  No dynamics. Reads verified folders, concatenates
              their results, applies P2, P4, A1 to A3 and P5, and writes the
              projection into a new folder. A complete unsharded run
              finalizes itself.

OUTPUT (new folder <outdir>/costprobe2-<timestamp>[-smoke][-s<i>of<k>]/,
        every file opened "x", every row flushed and fsynced)
  costprobe2_params.csv      the parameters that resumption must match
  costprobe2_results.csv     one row per probe: task id, check, unit fields,
                             beta (repr) and sigma (repr), seed key, wall,
                             peak RSS, slope, E_J for every J in the unit's
                             grid (%.17g), and an end marker
  costprobe2_checks.csv      (finalize) A1, A2, A3 and P2 verdicts
  costprobe2_projection.csv  (finalize) P4 and P5 per row
  costprobe2_objcheck.csv    P3

HOW TO RUN (from the repository root, venv active)
    python scripts/costprobe2.py --plan
    python scripts/costprobe2.py --workers 2 --smoke
    python scripts/costprobe2.py --workers 4
  --archive PATH and --outdir PATH are resolved by scripts/cbopaths.py, as
  in every round-2 script. On Kaggle the kgrun runner passes both.
  Exit codes: 0 completed (whatever the verdicts); 2 setup error (P0, P1, an
  import, a resume check); 3 P2 failed.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

# The archived modules pin BLAS to one thread before importing numpy. Here
# numpy is imported first, so their setdefault calls would come too late; the
# same variables are set here, before numpy, and printed in the header.
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for _v in THREAD_VARS:
    os.environ.setdefault(_v, "1")

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import hashlib                                                  # noqa: E402
import importlib                                                # noqa: E402
import math                                                     # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402
from multiprocessing import Pool                                # noqa: E402

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
# constants read from the archived scripts (notes/RERUN_PLAN.md)
# --------------------------------------------------------------------------
DT, LAM, SIGMA_ISO, JINF = 0.01, 1.0, 0.2, 50000
J10 = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
J10B = [10, 20, 40, 80, 160, 320, 640, 1250, 2500, 5000]          # regime.py 484, law.py 523
J19 = [10, 14, 20, 28, 40, 57, 80, 113, 160, 226, 320, 452, 640,
       905, 1280, 1810, 2560, 3620, 5000]                        # visibility.py 322-323
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
PROJ_WORKERS = 4

# Table 2 of the submitted manuscript, printed page 12: (cells, realizations).
# CONC is EXP-MECH and EXP-CAL run once (ledger N17); PROBEARM is the
# seed-paired probe arm on the same grid, so it carries EXP-MECH's counts.
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


def unit(module, obj, d, diff="none", jinf=JINF, T=1.0, jg="J10", arm=""):
    return (module, obj, int(d), diff, int(jinf), float(T), jg, arm)


def row_cells(name):
    """(list of units, one per Table 2 cell; realizations per cell).

    Grids from the archived scripts at the lines cited in RERUN_PLAN.md. Only
    the factors that enter the unit appear as fields; the others are looped
    so that the cell count is the Table 2 count."""
    c = []
    if name == "BETA-ISO":            # ess_surface.py 241-246, 273-279
        for o in ["ackley", "rastrigin"]:
            for _b in [1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]:
                for d in [2, 5, 10]:
                    c.append(unit("ess_surface", o, d, "isotropic"))
        return c, 20
    if name == "BETA-ANI":            # ess_surface.py 246, 280-286
        for o in ["ackley", "rastrigin"]:
            for _b in [3.0, 30.0, 300.0]:
                for d in [2, 10]:
                    c.append(unit("ess_surface", o, d, "anisotropic"))
        return c, 20
    if name == "LAWPANEL":            # visibility.py 164, 321-326
        for o in OBJ6:
            for d in [2, 3, 5, 10, 20, 40]:
                for _law in ["centred", "offset", "mix-0.1", "mix-0.01"]:
                    c.append(unit("visibility", o, d, jg="J19"))
        return c, 20
    if name in ("CONC", "PROBEARM"):  # mechanism.py 294-297
        for o in OBJ6:
            for d in [2, 5, 10, 40]:
                for _law in ["centred", "mix-0.1"]:
                    for _t in [0.5, 0.1, 0.01]:
                        c.append(unit("mechanism", o, d))
        return c, 15
    if name == "ADAPT":               # control.py 297-305
        for o in OBJ6:
            for d in [5, 10, 40]:
                for _t in [0.1, 0.01]:
                    for arm in ["fixed", "adaptive"]:
                        c.append(unit("control", o, d, arm=arm))
        return c, 15
    if name == "TAU8":                # boundary.py 252-256
        for o in OBJ6:
            for d in [5, 10, 40]:
                for _t in TAU8:
                    c.append(unit("boundary", o, d))
        return c, 15
    if name == "REFSIZE":             # regime.py 508-516
        for o in ["ackley", "sphere", "rosenbrock"]:
            for ji in [12500, 25000, 50000, 100000]:
                c.append(unit("regime", o, 10, jinf=ji, jg="J10b"))
        return c, 12
    if name == "SYNTH":               # regime.py 167-172, 548-554
        for o in REG_SYNTH:
            for d in [5, 10, 40]:
                for _t in [0.1, 0.01]:
                    c.append(unit("regime", o, d, jg="J10b"))
        return c, 12
    if name == "NAMED":               # regime.py 575-579
        for o in OBJ6:
            for d in [5, 10, 40]:
                for _t in [0.1, 0.01]:
                    c.append(unit("regime", o, d, jg="J10b"))
        return c, 12
    if name == "HORIZON":             # regime.py 596-602
        for o in OBJ4:
            for _law in ["centred", "mix-0.1"]:
                for T in [0.5, 1.0, 2.0]:
                    c.append(unit("regime", o, 10, T=T, jg="J10b"))
        return c, 12
    if name == "GEOM":                # law.py 125-126, 191-196, 521-547
        for o in LAW_SYNTH:
            for d in [5, 10, 40]:
                for _t in TAU8:
                    c.append(unit("law", o, d, jg="J10b"))
        return c, 12
    if name == "SIGMA":               # sigma.py 253-258
        for df in DIFF2:
            for o in OBJ4:
                for d in [5, 10, 40]:
                    for _r in [0.1, 0.25, 0.5, 0.75, 0.9, 0.99]:
                        for _t in [0.1, 0.01]:
                            c.append(unit("sigma", o, d, df))
        return c, 12
    if name == "ANISO":               # crossed.py 255-258, 282-297
        for _arm in ["A", "B"]:
            for df in DIFF2:
                for o in OBJ4:
                    for d in [5, 10, 40]:
                        for _lvl in range(3):
                            for _t in [0.1, 0.01]:
                                c.append(unit("crossed", o, d, df))
        return c, 12
    if name == "RMAP":                # regimemap.py 300-301
        for df in DIFF2:
            for o in OBJ3:
                for d in [10, 40]:
                    for _r in [0.5, 1.0, 1.5, 2.0, 3.0]:
                        for _t in [0.5, 0.1, 0.03, 0.01]:
                            c.append(unit("regimemap", o, d, df))
        return c, 12
    if name == "CLIFF":               # cliff.py 260-264
        for df in DIFF2:
            for o in OBJ4:
                for d in [10, 40]:
                    for _r in [0.5, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0]:
                        c.append(unit("cliff", o, d, df))
        return c, 12
    if name == "ONSET":               # regimemap.py 302-304
        for df in DIFF2:
            for o in OBJ3:
                for d in [5, 10, 20, 40, 80]:
                    for _r in [0.75, 1.0, 1.25, 1.5, 2.0, 3.0]:
                        c.append(unit("regimemap", o, d, df))
        return c, 12
    raise ValueError(name)


# A1, A2, A3: (name, base unit, base fields, [variant fields 0, variant fields 1])
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
    ("A3-repeat", unit("mechanism", "ackley", 10), {},
     [{}, {}]),
]


# --------------------------------------------------------------------------
# tasks
# --------------------------------------------------------------------------

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


def micro(x):
    return 0 if x is None else int(round(float(x) * 1000000))


def seed_key(t):
    return (ENTROPY, KIND_PROBE, MODULES.index(t["module"]), OBJ_NAMES.index(t["obj"]),
            t["d"], DIFFS.index(t["diff"]), LAWS.index(t["law"]), t["jinf"], t["K"],
            ARMS.index(t["arm"]), t["variant"], micro(t["tau"]), micro(t["r"]),
            micro(t["beta_design"]), micro(t["sigma_design"]))


def proxy(t):
    jl = [J for J in JGRIDS[t["jg"]] if J <= t["jinf"] // 10]
    return t["d"] * (t["jinf"] + sum(jl)) * t["K"] * (2 if t["arm"] == "adaptive" else 1)


def build_plan(rows, smoke):
    """Returns (main tasks, check tasks, unit -> rows map, row -> (cells, M))."""
    use = {}
    rowinfo = {}
    for name in rows:
        cells, M = row_cells(name)
        rowinfo[name] = (cells, M)
        for u in cells:
            use.setdefault(u, set()).add(name)
    mods = set(u[0] for u in use)
    if smoke:
        best = {}
        for u in use:
            t = make_task(u, "main")
            if u[0] not in best or proxy(t) < best[u[0]][0]:
                best[u[0]] = (proxy(t), u)
        units = [best[m][1] for m in sorted(best)]
        checks = [c for c in CHECKS if c[0] == "A3-repeat"]
    else:
        units = sorted(use)
        checks = [c for c in CHECKS if c[1][0] in mods]
    main = [make_task(u, "main", rows=sorted(use[u])) for u in units]
    chk = []
    for ci, (cname, cu, base, variants) in enumerate(CHECKS):
        if (cname, cu, base, variants) not in checks:
            continue
        for mi, vf in enumerate(variants):
            ex = dict(base)
            ex.update(vf)
            # A3's two members share one key on purpose (variant 99, never used
            # by a main probe); every other check member has its own variant.
            var = 99 if cname == "A3-repeat" else 100 + 10 * ci + mi
            chk.append(make_task(cu, "check", cname, mi, var, ex))
    return main, chk, use, rowinfo


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
        out["jl"] = jl
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
    listed relative paths; raises SystemExit(2) otherwise."""
    man = os.path.join(folder, "sha256.txt")
    if not os.path.isfile(man):
        sys.stderr.write("resume/finalize: {} has no sha256.txt\n".format(folder))
        sys.exit(2)
    rels = []
    with open(man) as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln:
                continue
            h, rel = ln.split("  ", 1)
            if sha256_file(os.path.join(folder, rel)) != h:
                sys.stderr.write("resume/finalize: {} fails its manifest at {}\n".format(folder, rel))
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
                sys.stderr.write("resume/finalize: two params files in {}\n".format(folder))
                sys.exit(2)
            params = dict((r[0], r[1]) for r in csv.reader(open(p, newline="")) if r)
        elif base == "costprobe2_results.csv":
            rows.extend(csv.DictReader(open(p, newline="")))
    return params, rows


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
        for m in ["ess_surface", "visibility", "mechanism", "control", "boundary",
                  "regime", "law", "sigma", "crossed", "cliff", "regimemap"]:
            mod = MODS[m]
            for o in OBJ6:
                try:
                    f = objective_of(m, mod, o)
                except Exception:
                    continue
                a, b = f(X), ec.OBJECTIVES[o](X)
                same = bool(np.array_equal(a, b))
                md = float(np.max(np.abs(a - b)))
                lines.append([m, "exactcal", o, d, "same" if same else "differs",
                              "{:.3e}".format(md)])
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
# finalize: P2, P4, A1-A3, P5
# --------------------------------------------------------------------------

def finalize(rows, outdir, sel_rows):
    hdr("FINALIZE -- P2, P4, A1 to A3, P5 from {} result rows".format(len(rows)))
    ok = [r for r in rows if r["end"] == "ok"]
    bad = [r for r in rows if r["end"] != "ok"]
    for r in bad:
        print("  ERROR row {}: {}".format(r["tid"], r["error"]))
    wall = {}
    rssu = {}
    for r in ok:
        if r["kind"] != "main":
            continue
        u = unit(r["module"], r["objective"], int(r["d"]), r["diffusion"], int(r["J_inf"]),
                 float(r["T"]), r["J_grid"], r["arm"])
        wall[u] = float(r["wall_s"])
        rssu[u] = float(r["peak_rss_mb"])

    # checks
    p2 = "not run"
    scale = dict((m, 1.0) for m in MODULES)
    a3_ratio = None
    chk_lines = []
    by = {}
    for r in ok:
        if r["kind"] == "check":
            by.setdefault(r["check"], {})[int(r["member"])] = r
    for cname, cu, _b, _v in CHECKS:
        pair = by.get(cname, {})
        if 0 not in pair or 1 not in pair:
            if cname in by:
                chk_lines.append([cname, cu[0], "", "", "", "INCOMPLETE"])
            continue
        w0, w1 = float(pair[0]["wall_s"]), float(pair[1]["wall_s"])
        ratio = max(w0, w1) / min(w0, w1) if min(w0, w1) > 0 else float("inf")
        if cname == "A3-repeat":
            a3_ratio = ratio
            same = all(pair[0]["E_{}".format(J)] == pair[1]["E_{}".format(J)] for J in JCOLS)
            p2 = "PASS" if same else "FAIL"
            chk_lines.append([cname, cu[0], "{:.3f}".format(w0), "{:.3f}".format(w1),
                              "{:.4f}".format(ratio), "P2 " + p2])
            continue
        v = "PASS" if ratio <= RATIO_MAX else "FAIL"
        if v == "FAIL":
            scale[cu[0]] = max(scale[cu[0]], ratio)
        chk_lines.append([cname, cu[0], "{:.3f}".format(w0), "{:.3f}".format(w1),
                          "{:.4f}".format(ratio), v])
    noise = a3_ratio is not None and a3_ratio > RATIO_MAX
    print("\n  {:<26} {:<12} {:>10} {:>10} {:>8}  verdict".format("check", "module", "wall 0", "wall 1", "ratio"))
    for ln in chk_lines:
        tag = ln[5] + ("  (noise-limited)" if noise and ln[0].startswith(("A1", "A2")) else "")
        print("  {:<26} {:<12} {:>10} {:>10} {:>8}  {}".format(ln[0], ln[1], ln[2], ln[3], ln[4], tag))
    print("\n  P2 (seed pass-through, bitwise E_J on the A3 pair): {}".format(p2))
    if a3_ratio is not None:
        print("  A3 timing-noise ratio {:.4f}{}".format(a3_ratio, "  -> A1/A2 noise-limited" if noise else ""))

    # projection
    proj = []
    print("\n  P4 budget {:.0f} MB per worker; P5 lower bound at {} workers, {:.0f} s per shard".format(
        RSS_BUDGET_MB, PROJ_WORKERS, SHARD_CEIL_S))
    print("  {:<10} {:>6} {:>7} {:>6} {:>12} {:>12} {:>7} {:>7} {:>9} {:>6}".format(
        "row", "cells", "real.", "units", "core h", "wall4 h", "shards", "scale", "max RSS", "P4"))
    for name in sel_rows:
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
        w4 = core / PROJ_WORKERS
        sh = int(math.ceil(w4 / SHARD_CEIL_S))
        mx = max(rssu[u] for u in units)
        p4 = "pass" if mx <= RSS_BUDGET_MB else "EXCEEDS BUDGET"
        proj.append([name, len(cells), len(cells) * M, len(units), "{:.1f}".format(core),
                     "{:.1f}".format(w4), sh, "{:.4f}".format(scale[mod]), "{:.1f}".format(mx), p4,
                     "flagged: A1/A2 scaling" if scale[mod] > 1.0 else ""])
        print("  {:<10} {:>6} {:>7} {:>6} {:>12.2f} {:>12.2f} {:>7} {:>7.3f} {:>9.1f} {:>6}".format(
            name, len(cells), len(cells) * M, len(units), core / 3600.0, w4 / 3600.0, sh,
            scale[mod], mx, p4))
    print("  (lower bounds: perfect scaling across {} workers; scheduling gaps and run tails ignored)".format(PROJ_WORKERS))
    if outdir:
        with open(os.path.join(outdir, "costprobe2_checks.csv"), "x", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["check", "module", "wall0_s", "wall1_s", "ratio", "verdict"])
            w.writerows(chk_lines)
            w.writerow(["P2", "", "", "", "", p2])
            w.writerow(["A3_noise_limited", "", "", "", "", "yes" if noise else "no"])
        with open(os.path.join(outdir, "costprobe2_projection.csv"), "x", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["row", "cells", "realizations", "units", "core_s", "wall4_s",
                        "shards_at_6h", "scale", "max_rss_mb", "P4", "note"])
            w.writerows(proj)
    return p2


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def hdr(s):
    print("\n" + "-" * 96)
    print(s)
    print("-" * 96)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--rows", default=",".join(ROW_ORDER))
    p.add_argument("--plan", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--nshards", type=int, default=1)
    p.add_argument("--resume-from", default="")
    p.add_argument("--finalize", default="")
    p.add_argument("--archive", default=None,
                   help="deposited archive; default <repo>/zenodo-v1 or CBOGAP_ARCHIVE")
    p.add_argument("--outdir", default=None,
                   help="output root; default <repo>/runs or CBOGAP_OUTDIR")
    a = p.parse_args()
    sel = [r for r in a.rows.split(",") if r]
    for r in sel:
        if r not in TABLE2:
            sys.stderr.write("setup error: unknown row {}\n".format(r))
            sys.exit(2)
    if not (0 <= a.shard < a.nshards):
        sys.stderr.write("setup error: need 0 <= shard < nshards\n")
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

    hdr("P1 -- ARCHIVE IDENTITY")
    p1 = True
    for m in MODULES:
        h = sha256_file(os.path.join(ARCH, m + ".py"))
        okm = (h == ARCHIVE_SHA256[m])
        p1 &= okm
        print("  {:<12} {}  {}".format(m, h, "ok" if okm else "MISMATCH"))
    if not p1:
        print("\nP1 FAILED: the archive is not the deposited one. Nothing runs.")
        sys.exit(2)
    print("  P1 PASS")

    hdr("P0 -- PLAN IDENTITY against Table 2 (printed page 12)")
    p0 = True
    for name in sel:
        cells, M = row_cells(name)
        want = TABLE2[name]
        got = (len(cells), len(cells) * M)
        okr = (got == want)
        p0 &= okr
        print("  {:<10} cells {:>4} (Table 2 {:>4})   realizations {:>5} (Table 2 {:>5})   units {:>3}   {}".format(
            name, got[0], want[0], got[1], want[1], len(set(cells)), "ok" if okr else "MISMATCH"))
    if not p0:
        print("\nP0 FAILED: a grid does not reproduce Table 2. Nothing runs.")
        sys.exit(2)
    print("  P0 PASS")

    if mode == "finalize":
        rows = []
        seen = set()
        for f in [x for x in a.finalize.split(",") if x]:
            _, rr = read_folder(f)
            for r in rr:
                if r["tid"] in seen:
                    sys.stderr.write("finalize: task {} found twice\n".format(r["tid"]))
                    sys.exit(2)
                seen.add(r["tid"])
            print("  read {}: {} rows".format(f, len(rr)))
            rows.extend(rr)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = os.path.join(OUTROOT, "costprobe2-finalize-{}".format(stamp))
        os.makedirs(outdir)
        p2 = finalize(rows, outdir, sel)
        print("\nfiles  {}".format(outdir))
        sys.exit(3 if p2 == "FAIL" else 0)

    main_t, chk_t, use, _ = build_plan(sel, a.smoke)
    keys = {}
    for t in main_t + chk_t:
        if t["check"] == "A3-repeat":
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
        bym.setdefault((t["module"], t["d"]), 0)
        bym[(t["module"], t["d"])] += 1
    for (m, d) in sorted(bym):
        print("  {:<12} d={:<3} {:>4} main probe(s)".format(m, d, bym[(m, d)]))
    print("  main probes {}   check probes {}   total {}".format(len(main_t), len(chk_t), len(main_t) + len(chk_t)))

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

    # checks first, pairs adjacent; then main probes, most expensive first
    queue = [t for t in chk_t if t["tid"] not in done]
    queue += sorted([t for t in main_t if t["tid"] not in done], key=lambda x: -proxy(x))
    hdr("PROBES  {} task(s) on {} worker(s), one fresh process each".format(len(queue), a.workers))
    rows_written = []
    t0 = time.time()
    fh = open(os.path.join(outdir, "costprobe2_results.csv"), "x", newline="")
    w = csv.writer(fh)
    w.writerow(RES_COLS)
    fh.flush()
    os.fsync(fh.fileno())
    pool = Pool(processes=a.workers, maxtasksperchild=1)
    try:
        for i, o in enumerate(pool.imap_unordered(run_task, queue, chunksize=1)):
            w.writerow(res_row(o))
            fh.flush()
            os.fsync(fh.fileno())
            rows_written.append(dict(zip(RES_COLS, [str(x) for x in res_row(o)])))
            el = time.time() - t0
            if o["end"] == "ok":
                print("  [{:>4}/{:<4}] {:<11} {:<17} d={:<3} {:<11} Jinf={:<6} T={:<3} {:<5} {:<8} "
                      "wall {:>8.1f} s  RSS {:>7.1f} MB{}  elapsed {:>8.0f} s".format(
                          i + 1, len(queue), o["module"], o["obj"], o["d"], o["diff"], o["jinf"],
                          o["T"], o["jg"], o["arm"] or "-", o["wall"], o["rss"],
                          "  OVER BUDGET" if o["rss"] > RSS_BUDGET_MB else "", el))
            else:
                print("  [{:>4}/{:<4}] ERROR {} {} d={}: {}".format(
                    i + 1, len(queue), o["module"], o["obj"], o["d"], o["error"]))
            sys.stdout.flush()
    finally:
        pool.close()
        pool.join()
        fh.close()
    print("  probes finished in {:.1f} s".format(time.time() - t0))

    p2 = "not run"
    if a.nshards == 1 and not a.resume_from:
        if mode == "smoke":
            hdr("SMOKE: walls at the smallest unit of each module; no projection")
            for r in rows_written:
                print("  {:<12} {:<17} d={:<3} wall {} s  RSS {} MB  end {}".format(
                    r["module"], r["objective"], r["d"], r["wall_s"], r["peak_rss_mb"], r["end"]))
            p2 = finalize(rows_written, None, [])
        else:
            p2 = finalize(rows_written, outdir, sel)
    else:
        print("\n  Sharded or resumed run: finalize after every shard is fetched, with")
        print("  --finalize <folder>,<folder>,... (no dynamics).")
    print("\n" + "=" * 96)
    print("files  {}".format(outdir))
    print("=" * 96)
    sys.exit(3 if p2 == "FAIL" else 0)


if __name__ == "__main__":
    main()
