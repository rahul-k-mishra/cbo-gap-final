"""
rerunlib.py  --  CBO-GAP round 2: the definitions shared by the fixed-beta
                 rerun's trajectory script (rerun.py) and its analysis
                 script (rerun_analysis.py)

WHY THIS EXISTS
---------------
The rerun's cells, seed keys, shared cells, betas, the onset estimator and
the finite-J audit are used by two scripts. Each lives here once, so the
two cannot drift apart (the reason scripts/cbopaths.py exists). Importing
this file defines constants and functions; it runs no dynamics, writes
nothing and prints nothing. It imports scripts/costprobe2.py, which
imports the archive (CLAUDE.md rule 4) and holds GRID, which costprobe2's
P0 checks against the archived source.

Everything stated here is specified in notes/ANALYSIS_CRITERIA.md; the
section is named at each definition. The criteria and worked examples are
in rerun.py's and rerun_analysis.py's docstrings, which cite this file.

CELLS (costprobe2.py GRID; counts checked against Table 2 by V0 in
rerun.py). A cell is a dict with: row, module, obj, d, law, tau, r,
sigma_design, beta_design, jinf, T, arm, subarm, diffs, M, jg. Absent
factors are None. diffs is ["isotropic", "anisotropic"] in the five paired
rows (SIGMA, ANISO, RMAP, CLIFF, ONSET), ["isotropic"] in BETA-ISO,
["anisotropic"] in BETA-ANI and ["none"] elsewhere.

SEED KEY (layout section, approved in the ninth message). Sixteen integers:
  (ENTROPY 20261016, kind, owner row, module, objective, d, law,
   tau0 x 1e6, r x 1e6, design sigma x 1e6, design beta x 1e6, J_inf,
   T x 1e6, arm, ANISO sub-arm, rep)
kind 81 for trajectories, 71 for the bootstrap (rep removed), 83 for the
determinism smoke pair (rerun.py D-SMOKE). Indices are those of
costprobe2's ROW_ORDER, MODULES, OBJ_NAMES, LAWS and ARMS. Diffusion is
absent, so the two arms of a paired cell share every key (5a). 0 means
"none" in fields 8 to 11. The owner row is the first row in ROW_ORDER
that holds an identical cell (shared cells); for every other cell it is
the cell's own row.

SHARED CELLS (layout section, ninth message). Two cells of different rows
are the same experiment iff they call the same module with identical
arguments other than the seed: the key fields 4 to 15, the beta used, M,
the J grid and the diffusions. EXPECTED_SHARED lists the sharing the
criteria file derived from the code; rerun.py's K4 stops the run if the
computed sharing differs from it.

BETAS (notes/ANALYSIS_CRITERIA.md, measurements note; calprec2.py lines 68
to 75). CONC, TAU8, SIGMA and ANISO use calprec2_beta.csv. Every other row
keeps its archived beta, recomputed here by the archived module's own code
path:
  BETA-ISO, BETA-ANI  the design value (ess_surface.py lines 241 to 246)
  LAWPANEL  B / visibility.scales_of(o, d, law)[1], B = 30.0
            (visibility.py lines 314, 359 to 367)
  PROBEARM  mechanism.beta_for_target(o, d, law, tau)[0] (mechanism.py
            lines 326 and 200 to 216), imported
  ADAPT     control.py lines 333 to 336: default_rng(999 + 131 d),
            draw_initial(rng, 4000, d, o, "centred"), solve_beta on f - min
            f at log(tau x 4000); both arms start from it
  REFSIZE, SYNTH, NAMED, HORIZON  regime.py lines 320 to 326:
            default_rng(4242 + 131 d + 17 len(name)), draw_initial(rng,
            4000, d, xstar, law), solve_beta(f - min f, log(tau x 4000))
  GEOM      law.py lines 530 to 539: default_rng(4242 + 131 d),
            standard_normal((4000, d)) + xs, solve_beta
  CLIFF     cliff.py lines 304 to 312: default_rng(4242 + 131 d + 7
            len(name)), standard_normal((4000, d)) + XSTAR, solve_beta
  RMAP, ONSET  regimemap.py lines 337 to 344 (getbeta, nested in main):
            default_rng(4242 + 131 d + 7 len(name)), standard_normal((4000,
            d)), solve_beta
Only these sampling lines are retyped; every function they call is
imported. They are not trusted: rerun.py's A-BETA compares every
recomputed beta with the archived CSV's beta column and stops on any
mismatch.

CALIBRATED r ROWS (2026-10-25; ledger N41, N42). Three rows are appended
after costprobe2's seventeen:
    RMAP-CAL   the cells of RMAP;
    CLIFF-CAL  the cells of CLIFF;
    ONSET-CAL  the cells of ONSET;
each with the base row's GRID entry, module, diffusions, M and J grid, and
with its beta from calprec2_beta.csv (the N41 calibration of the regimemap
and cliff cells) instead of the archived probe.
  - ROWS = costprobe2.ROW_ORDER + the three, so the seventeen rows keep
    their indices and every key of the run of 2026-10-24 and 25 is
    unchanged; the new rows' owner field is 17, 18 or 19.
  - costprobe2.py is NOT edited: it is pinned by calprec2 (header, params,
    resume and finalize compare it) and by the plan. GRID here is
    costprobe2.GRID plus the three aliases; V0 checks the base rows'
    factors against the source and counts the new rows against their base
    row's Table 2 entry (rerun.py).
  - The calibrated rows are paired (5a) and calprec2-calibrated (C2). The
    archived betas are not recomputed for them (recompute_beta raises);
    A-SIGMA still checks their sigma against the base row's archived file.
  - Sharing: RMAP-CAL and ONSET-CAL share, cell for cell, what RMAP and
    ONSET share (d 10 and 40, r 1.0 to 3.0, tau0 0.1), owner RMAP-CAL.
    The probe cells and the calibrated cells have the same share key and
    different betas, so they are different groups. expected_shared
    therefore maps a share key to a LIST of row lists, one per group.
    Worked example: (regimemap, ackley, 10, centred, 0.1, 1.5, 50000, 1.0)
    -> [[RMAP, ONSET], [RMAP-CAL, ONSET-CAL]].

ONSET ESTIMATOR (item 7, H3). regimemap.py lines 496 to 505, retyped
because bp is nested inside main and cannot be imported (rule 4 does not
cover it). onset_bp(rs, y): x = log r; for each candidate c in x without
its last value, fit y = a + b1 x + b2 max(x - c, 0) by least squares and
take the c with the smallest residual sum of squares, ties to the first
(Python's min); return exp(c). Its use is gated by the onset control O1
(rerun.py), which must reproduce the ten archived onsets first.

FINITE-J AUDIT (section 8.5). The initial ensemble of a realization is
redrawn from its seed with the module's own first draw, whose source line
is checked (S1 in rerun.py), and finitej.ess_frac is imported from the
archive.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import csv
import hashlib
import inspect
import json
import math
import os
import re
import sys
from decimal import Decimal

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import costprobe2 as cp                                         # noqa: E402

ARCH = cp.ARCH

try:
    import finitej                                              # noqa: E402
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import finitej from the archive: {}\n".format(exc))
    sys.exit(2)

# zenodo-v1.sha256 line 29. The other modules are costprobe2.ARCHIVE_SHA256.
FINITEJ_SHA256 = "5b7a81ef54433369cae6e9d9e416a51078f207a34c329d7ca7023ce448f9c4b1"

ENTROPY = 20261016
KIND_TRAJ, KIND_BOOT, KIND_SMOKE = 81, 71, 83

EXT_ROWS = ["RMAP-CAL", "CLIFF-CAL", "ONSET-CAL"]
EXT_BASE = {"RMAP-CAL": "RMAP", "CLIFF-CAL": "CLIFF", "ONSET-CAL": "ONSET"}
ROWS = list(cp.ROW_ORDER) + EXT_ROWS
MODULES, OBJ_NAMES, LAWS, ARMS = cp.MODULES, cp.OBJ_NAMES, cp.LAWS, cp.ARMS
GRID = dict(cp.GRID)
for _r in EXT_ROWS:
    GRID[_r] = cp.GRID[EXT_BASE[_r]]
JGRIDS, JCOLS = cp.JGRIDS, cp.JCOLS
PAIRED = ["SIGMA", "ANISO", "RMAP", "CLIFF", "ONSET"] + EXT_ROWS
CALROWS = ["CONC", "TAU8", "SIGMA", "ANISO"] + EXT_ROWS
AUDIT_ROWS = ["CONC", "PROBEARM", "TAU8", "GEOM"]
DT, LAM, SIGMA_ISO, JINF = 0.01, 1.0, 0.2, 50000
B_VIS = 30.0

BETA_SOURCE = {
    "BETA-ISO": "design (ess_surface.py 241-246)",
    "BETA-ANI": "design (ess_surface.py 241-246)",
    "LAWPANEL": "B / robust spread (visibility.py 314, 359-367)",
    "CONC": "calprec2_beta.csv",
    "PROBEARM": "mechanism.beta_for_target (mechanism.py 200-216, 326)",
    "ADAPT": "control probe (control.py 333-336)",
    "TAU8": "calprec2_beta.csv",
    "REFSIZE": "regime probe (regime.py 320-326)",
    "SYNTH": "regime probe (regime.py 320-326)",
    "NAMED": "regime probe (regime.py 320-326)",
    "HORIZON": "regime probe (regime.py 320-326)",
    "GEOM": "law probe (law.py 530-539)",
    "SIGMA": "calprec2_beta.csv",
    "ANISO": "calprec2_beta.csv",
    "RMAP": "regimemap probe (regimemap.py 337-344)",
    "CLIFF": "cliff probe (cliff.py 304-312)",
    "ONSET": "regimemap probe (regimemap.py 337-344)",
    "RMAP-CAL": "calprec2_beta.csv",
    "CLIFF-CAL": "calprec2_beta.csv",
    "ONSET-CAL": "calprec2_beta.csv",
}


def micro(x):
    return 0 if x is None else int(round(float(x) * 1000000))


# --------------------------------------------------------------------------
# cells
# --------------------------------------------------------------------------

def _cell(row, module, obj, d, law="centred", tau=None, r=None, sigma_design=None,
          beta_design=None, jinf=JINF, T=1.0, arm="", subarm=0, diffs=None, jg="J10"):
    return {"row": row, "module": module, "obj": obj, "d": int(d), "law": law,
            "tau": None if tau is None else float(tau), "r": None if r is None else float(r),
            "sigma_design": None if sigma_design is None else float(sigma_design),
            "beta_design": None if beta_design is None else float(beta_design),
            "jinf": int(jinf), "T": float(T), "arm": arm, "subarm": int(subarm),
            "diffs": list(diffs or ["none"]), "M": int(GRID[row]["M"]), "jg": jg}


def cells_of(row):
    """Every cell of a row, in a fixed order, from GRID (checked by P0)."""
    if row in EXT_BASE:
        out = cells_of(EXT_BASE[row])
        for c in out:
            c["row"] = row
        return out
    g = GRID[row]
    out = []
    if row in ("BETA-ISO", "BETA-ANI"):
        df = "isotropic" if row == "BETA-ISO" else "anisotropic"
        for o in g["objs"]:
            for b in g["betas"]:
                for d in g["dims"]:
                    out.append(_cell(row, "ess_surface", o, d, beta_design=b, diffs=[df]))
    elif row == "LAWPANEL":
        for o in g["objs"]:
            for d in g["dims"]:
                for law in g["laws"]:
                    out.append(_cell(row, "visibility", o, d, law=law, jg="J19"))
    elif row in ("CONC", "PROBEARM"):
        for o in g["objs"]:
            for d in g["dims"]:
                for law in g["laws"]:
                    for t in g["taus"]:
                        out.append(_cell(row, "mechanism", o, d, law=law, tau=t))
    elif row == "ADAPT":
        for o in g["objs"]:
            for d in g["dims"]:
                for t in g["taus"]:
                    for arm in g["arms"]:
                        out.append(_cell(row, "control", o, d, tau=t, arm=arm))
    elif row == "TAU8":
        for o in g["objs"]:
            for d in g["dims"]:
                for t in g["taus"]:
                    out.append(_cell(row, "boundary", o, d, tau=t))
    elif row == "REFSIZE":
        for o in g["objs"]:
            for ji in g["jinfs"]:
                out.append(_cell(row, "regime", o, g["d"], tau=0.1, jinf=ji, jg="J10b"))
    elif row in ("SYNTH", "NAMED"):
        for o in g["objs"]:
            for d in g["dims"]:
                for t in g["taus"]:
                    out.append(_cell(row, "regime", o, d, tau=t, jg="J10b"))
    elif row == "HORIZON":
        for o in g["objs"]:
            for law in g["laws"]:
                for T in g["Ts"]:
                    out.append(_cell(row, "regime", o, 10, law=law, tau=0.1, T=T, jg="J10b"))
    elif row == "GEOM":
        for o in g["objs"]:
            for d in g["dims"]:
                for t in g["taus"]:
                    out.append(_cell(row, "law", o, d, tau=t, jg="J10b"))
    elif row in ("SIGMA", "CLIFF", "RMAP"):
        mod = {"SIGMA": "sigma", "CLIFF": "cliff", "RMAP": "regimemap"}[row]
        for o in g["objs"]:
            for d in g["dims"]:
                for r in g["rs"]:
                    for t in g["taus"]:
                        out.append(_cell(row, mod, o, d, tau=t, r=r, diffs=g["diffs"]))
    elif row == "ANISO":
        for o in g["objs"]:
            for d in g["dims"]:
                for s in g["sigmas"]:
                    for t in g["taus"]:
                        out.append(_cell(row, "crossed", o, d, tau=t, sigma_design=s,
                                         subarm=1, diffs=g["diffs"]))
        for o in g["objs"]:
            for d in g["dims"]:
                for r in g["rs"]:
                    for t in g["taus"]:
                        out.append(_cell(row, "crossed", o, d, tau=t, r=r, subarm=2,
                                         diffs=g["diffs"]))
    elif row == "ONSET":
        for o in g["objs"]:
            for d in g["dims"]:
                for r in g["rs"]:
                    out.append(_cell(row, "regimemap", o, d, tau=g["tau"], r=r, diffs=g["diffs"]))
    else:
        raise ValueError(row)
    if g["jgrid"] != JGRIDS[out[0]["jg"]]:
        raise ValueError("row {}: J grid mismatch".format(row))
    return out


def jlist_of(c):
    return [J for J in JGRIDS[c["jg"]] if J <= c["jinf"] // 10]


def K_of(c):
    return int(round(c["T"] / DT))


def coord_fields(c):
    """Key fields 4 to 15 (module .. ANISO sub-arm)."""
    return (MODULES.index(c["module"]), OBJ_NAMES.index(c["obj"]), c["d"], LAWS.index(c["law"]),
            micro(c["tau"]), micro(c["r"]), micro(c["sigma_design"]), micro(c["beta_design"]),
            c["jinf"], micro(c["T"]), ARMS.index(c["arm"]), c["subarm"])


def traj_key(c, owner, rep, kind=KIND_TRAJ):
    return (ENTROPY, kind, ROWS.index(owner)) + coord_fields(c) + (int(rep),)


def boot_key(c, owner):
    return (ENTROPY, KIND_BOOT, ROWS.index(owner)) + coord_fields(c)


def key_str(k):
    return "-".join(str(x) for x in k)


def cell_label(c):
    parts = [c["row"], c["module"], c["obj"], "d{}".format(c["d"]), c["law"]]
    for f in ("tau", "r", "sigma_design", "beta_design"):
        if c[f] is not None:
            parts.append("{}={!r}".format(f, c[f]))
    parts += ["Jinf{}".format(c["jinf"]), "T{!r}".format(c["T"])]
    if c["arm"]:
        parts.append(c["arm"])
    if c["subarm"]:
        parts.append("armA" if c["subarm"] == 1 else "armB")
    return "|".join(parts)


def share_key(c):
    return (c["module"], c["obj"], c["d"], c["law"], c["tau"], c["r"], c["jinf"], c["T"])


# The sharing derived from the code in the criteria file (layout section,
# "Shared cells"). Each entry: share_key -> a list of row lists, one per
# multi-row group with that key, each in ROWS order (N42: the probe and the
# calibrated r rows have the same share keys and different betas).
def expected_shared():
    exp = {}
    for o in ["ackley", "sphere", "rosenbrock"]:
        exp[("regime", o, 10, "centred", 0.1, None, 50000, 1.0)] = [["REFSIZE", "NAMED", "HORIZON"]]
    exp[("regime", "rastrigin", 10, "centred", 0.1, None, 50000, 1.0)] = [["NAMED", "HORIZON"]]
    for o in ["ackley", "rastrigin", "sphere"]:
        for d in [10, 40]:
            for r in [1.0, 1.5, 2.0, 3.0]:
                exp[("regimemap", o, d, "centred", 0.1, r, 50000, 1.0)] = [["RMAP", "ONSET"],
                                                                         ["RMAP-CAL", "ONSET-CAL"]]
    return exp


# --------------------------------------------------------------------------
# betas and sigmas
# --------------------------------------------------------------------------

def recompute_beta(c):
    """The archived beta of a non-calprec2 cell, by the module's own code path
    (see the module docstring). Raises for a calprec2 row."""
    row, m, o, d = c["row"], c["module"], c["obj"], c["d"]
    mod = cp.MODS[m]
    if row in CALROWS:
        raise ValueError("calprec2 row {}".format(row))
    if m == "ess_surface":
        return float(c["beta_design"])
    if m == "visibility":
        return B_VIS / mod.scales_of(o, d, c["law"])[1]
    if m == "mechanism":
        return float(mod.beta_for_target(o, d, c["law"], c["tau"])[0])
    if m == "control":
        rng = np.random.default_rng(999 + 131 * d)
        Xp = mod.draw_initial(rng, 4000, d, o, "centred")
        fv = mod.OBJECTIVES[o](Xp)
        return float(mod.solve_beta(fv - fv.min(), math.log(c["tau"] * 4000)))
    if m == "regime":
        f, xstar = mod.objective(o)
        rng = np.random.default_rng(4242 + 131 * d + 17 * len(o))
        Xp = mod.draw_initial(rng, 4000, d, xstar, c["law"])
        fv = f(Xp)
        return float(mod.solve_beta(fv - fv.min(), math.log(c["tau"] * 4000)))
    if m == "law":
        f, xs = mod.objective(o)
        rng = np.random.default_rng(4242 + 131 * d)
        Xp = rng.standard_normal((4000, d)) + xs
        fv = f(Xp)
        return float(mod.solve_beta(fv - fv.min(), math.log(c["tau"] * 4000)))
    if m == "cliff":
        rng = np.random.default_rng(4242 + 131 * d + 7 * len(o))
        Xp = rng.standard_normal((4000, d)) + mod.XSTAR[o]
        fv = mod.OBJ[o](Xp)
        return float(mod.solve_beta(fv - fv.min(), math.log(c["tau"] * 4000)))
    if m == "regimemap":
        rng = np.random.default_rng(4242 + 131 * d + 7 * len(o))
        Xp = rng.standard_normal((4000, d))
        fv = mod.OBJ[o](Xp)
        return float(mod.solve_beta(fv - fv.min(), math.log(c["tau"] * 4000)))
    raise ValueError(m)


def sigma_for(c, diff):
    if c["sigma_design"] is not None:
        return float(c["sigma_design"])
    if c["module"] in ("sigma", "crossed", "cliff", "regimemap") and c["r"] is not None:
        return float(cp.MODS[c["module"]].sigma_of(diff, c["d"], c["r"], LAM))
    return SIGMA_ISO


def calprec2_key(c):
    return (c["module"], c["obj"], c["d"], c["law"], float(c["tau"]))


def read_calprec2(path):
    """calprec2_beta.csv -> {(module, objective, d, law, tau0): row dict}."""
    out = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            k = (r["module"], r["objective"], int(r["d"]), r["law"], float(r["tau0"]))
            if k in out:
                raise ValueError("duplicate calprec2 cell {}".format(k))
            out[k] = r
    return out


# --------------------------------------------------------------------------
# archive check of betas and sigmas (rerun.py A-BETA, A-SIGMA)
# --------------------------------------------------------------------------

# row -> (file, [(csv column, cell field or ("=", constant) or "diff")],
#         beta column or None, sigma column or None, print format)
# Print format: "g6" where the archive wrote the column with "{:.6g}"
# (visibility.py 416, mechanism.py 378, control.py 381-383, regime.py 383,
# law.py 582, sigma.py 356-357, crossed.py 373-375, cliff.py 360-361,
# regimemap.py 395-396); "str" for ess_surface's design beta, written as the
# float itself (ess_surface.py 321).
# ADAPT matches the FIXED arm's row for both arms: control.py 347 passes the
# same beta0 to both arms, but control_summary.csv's beta_first is the mean
# of b_first, and in the adaptive arm b_first is the beta after the first
# re-solve (control.py 223 to 250), not beta0.
ARCH_CHECK = {
    "BETA-ISO": ("ess_surface_summary.csv", [("objective", "obj"), ("diffusion", "diff"),
                                             ("beta", "beta_design"), ("d", "d")], "beta", None, "str"),
    "BETA-ANI": ("ess_surface_summary.csv", [("objective", "obj"), ("diffusion", "diff"),
                                             ("beta", "beta_design"), ("d", "d")], "beta", None, "str"),
    "LAWPANEL": ("visibility_summary.csv", [("objective", "obj"), ("d", "d"), ("init", "law")],
                 "beta", None, "g6"),
    "PROBEARM": ("mechanism_summary.csv", [("objective", "obj"), ("d", "d"), ("init", "law"),
                                           ("tau", "tau")], "beta", None, "g6"),
    "ADAPT": ("control_summary.csv", [("objective", "obj"), ("d", "d"), ("tau", "tau"),
                                      ("arm", ("=", "fixed"))], "beta_first", None, "g6"),
    "REFSIZE": ("regime_A_reference.csv", [("name", "obj"), ("d", "d"), ("init", "law"),
                                           ("tau", "tau"), ("Jinf", "jinf"), ("T", "T")], "beta", None, "g6"),
    "SYNTH": ("regime_B_synth.csv", [("name", "obj"), ("d", "d"), ("init", "law"), ("tau", "tau"),
                                     ("Jinf", "jinf"), ("T", "T")], "beta", None, "g6"),
    "NAMED": ("regime_C_named.csv", [("name", "obj"), ("d", "d"), ("init", "law"), ("tau", "tau"),
                                     ("Jinf", "jinf"), ("T", "T")], "beta", None, "g6"),
    "HORIZON": ("regime_D_horizon.csv", [("name", "obj"), ("d", "d"), ("init", "law"),
                                         ("tau", "tau"), ("Jinf", "jinf"), ("T", "T")], "beta", None, "g6"),
    "GEOM": ("law_synth.csv", [("name", "obj"), ("d", "d"), ("tau", "tau")], "beta", None, "g6"),
    "RMAP": ("regimemap_M_real.csv", [("part", ("=", "M")), ("diffusion", "diff"),
                                      ("objective", "obj"), ("d", "d"), ("r", "r"), ("tau", "tau")],
             "beta", "sigma", "g6"),
    "ONSET": ("regimemap_D_real.csv", [("part", ("=", "D")), ("diffusion", "diff"),
                                       ("objective", "obj"), ("d", "d"), ("r", "r"), ("tau", "tau")],
              "beta", "sigma", "g6"),
    "CLIFF": ("cliff_summary.csv", [("diffusion", "diff"), ("objective", "obj"), ("d", "d"),
                                    ("r", "r"), ("tau", "tau")], "beta", "sigma", "g6"),
    "SIGMA": ("sigma_summary.csv", [("diffusion", "diff"), ("objective", "obj"), ("d", "d"),
                                    ("r", "r"), ("tau", "tau")], None, "sigma", "g6"),
    "ANISO": ("crossed_summary.csv", [("arm", "armAB"), ("diffusion", "diff"), ("objective", "obj"),
                                      ("d", "d"), ("level", "level"), ("tau", "tau")], None, "sigma",
              "g6"),
}


# N42: the calibrated r rows check sigma against the base row's archived file
# (sigma depends on the diffusion, d and r only); their beta is calprec2's, so
# no archived beta column applies.
for _r in EXT_ROWS:
    _f, _m, _bcol, _scol, _fmt = ARCH_CHECK[EXT_BASE[_r]]
    ARCH_CHECK[_r] = (_f, _m, None, _scol, _fmt)


def printed_tol(s, fmt):
    """Half a unit in the last digit the archive printed, plus a relative
    slack of 1e-9 for a value on a rounding boundary.
    fmt "g6": the column was written with "{:.6g}", which keeps six
    significant digits but drops trailing zeros, so the last printed digit is
    the sixth significant one: 0.5 x 10^(floor(log10|v|) - 5).
    fmt "str": the last digit of the string itself."""
    v = float(s)
    if fmt == "g6":
        if v == 0.0:
            return 1e-12
        return 0.5 * 10.0 ** (math.floor(math.log10(abs(v))) - 5) + 1e-9 * abs(v)
    dv = Decimal(s.strip())
    q = float(Decimal(1).scaleb(dv.as_tuple().exponent))
    return 0.5 * q + 1e-9 * abs(v)


def agrees(x, s, fmt):
    return abs(float(x) - float(s)) <= printed_tol(s, fmt)


_CSV_CACHE = {}


def archived_rows(fname):
    if fname not in _CSV_CACHE:
        with open(os.path.join(ARCH, fname), newline="") as fh:
            _CSV_CACHE[fname] = list(csv.DictReader(fh))
    return _CSV_CACHE[fname]


def _field_value(c, field, diff):
    if isinstance(field, tuple):
        return field[1]
    if field == "diff":
        return diff
    if field == "armAB":
        return "A" if c["subarm"] == 1 else "B"
    if field == "level":
        return c["sigma_design"] if c["subarm"] == 1 else c["r"]
    return c[field]


def _matches(rowv, want):
    if isinstance(want, str):
        return rowv.strip() == want
    try:
        return float(rowv) == float(want)
    except ValueError:
        return False


def archive_check(c, diff, beta, sigma):
    """(verdict, detail) for one (cell, diffusion): 'ok', 'FAIL' or
    'not applicable'. Every matching archived row must agree."""
    spec = ARCH_CHECK.get(c["row"])
    if spec is None:
        return "not applicable", "no archived beta or sigma for this row"
    fname, match, bcol, scol, pfmt = spec
    want = [(col, _field_value(c, f, diff)) for col, f in match]
    hits = [r for r in archived_rows(fname) if all(_matches(r[col], v) for col, v in want)]
    if not hits:
        return "FAIL", "no row of {} matches {}".format(fname, want)
    bad = []
    for r in hits:
        if bcol is not None and not agrees(beta, r[bcol], pfmt):
            bad.append("beta {!r} vs archived {}".format(beta, r[bcol]))
        if scol is not None and not agrees(sigma, r[scol], pfmt):
            bad.append("sigma {!r} vs archived {}".format(sigma, r[scol]))
    if bad:
        return "FAIL", "{} ({} archived rows): {}".format(fname, len(hits), "; ".join(sorted(set(bad))))
    return "ok", "{}: {} archived row(s) agree".format(fname, len(hits))


# --------------------------------------------------------------------------
# onset (item 7, H3) and its control O1
# --------------------------------------------------------------------------

def onset_bp(rs, y):
    """regimemap.py lines 496 to 505, retyped (bp is nested in main)."""
    x = np.log(np.array(rs, dtype=float))
    yy = np.asarray(y, dtype=float)

    def rss(b):
        z = np.maximum(x - b, 0.0)
        A = np.vstack([x, z, np.ones(len(x))]).T
        sol, _, _, _ = np.linalg.lstsq(A, yy, rcond=None)
        return float(((yy - A @ sol) ** 2).sum())
    return math.exp(min(x[:-1], key=rss))


def tex_onset_table(path):
    """{(diffusion, d): (six per-r means as strings, onset string)} and the r
    header, read from the manuscript's tab:onset."""
    lines = open(path, encoding="utf-8").read().splitlines()
    start = [i for i, ln in enumerate(lines) if "\\label{tab:onset}" in ln]
    if len(start) != 1:
        raise ValueError("tab:onset found {} times".format(len(start)))
    out, rs, diff = {}, None, None
    for i in range(start[0], len(lines)):
        ln = lines[i]
        if "\\end{tabular}" in ln:
            break
        if "r_{\\rm onset}" in ln:
            rs = [float(v) for v in re.findall(r"\$([0-9.]+)\$", ln.split("r_{\\rm onset}")[0])]
            continue
        if "\\multirow{5}{*}{iso}" in ln:
            diff = "isotropic"
        elif "\\multirow{5}{*}{aniso}" in ln:
            diff = "anisotropic"
        m = re.match(r"\s*&\s*\$(\d+)\$\s*&(.*)\\\\", ln)
        if m and diff is not None:
            vals = re.findall(r"\$([^$]*)\$", m.group(2))
            out[(diff, int(m.group(1)))] = ([v for v in vals[:6]], vals[6], i + 1)
    return out, rs


def onset_control(arch_dir, tex_path):
    """O1. Returns (passed, report lines, records)."""
    table, rs = tex_onset_table(tex_path)
    g = GRID["ONSET"]
    rep = []
    ok = True
    if rs != list(g["rs"]):
        rep.append("O1 FAIL: table r header {} differs from GRID {}".format(rs, g["rs"]))
        return False, rep, []
    rec = {}
    with open(os.path.join(arch_dir, "regimemap_D_real.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            if r["part"] != "D":
                continue
            k = (r["diffusion"], r["objective"], int(r["d"]), float(r["r"]))
            rec.setdefault(k, []).append(float(r["slope"]))
    out = []
    for diff in g["diffs"]:
        for d in g["dims"]:
            ms = []
            for r in g["rs"]:
                v = [float(np.nanmean(rec[(diff, o, d, float(r))])) for o in g["objs"]
                     if (diff, o, d, float(r)) in rec]
                ms.append(float(np.mean(v)) if v else float("nan"))
            got = onset_bp(g["rs"], ms)
            means_tab, onset_tab, line = table[(diff, d)]
            good = ("{:.2f}".format(got) == onset_tab)
            ok = ok and good
            out.append({"diffusion": diff, "d": d, "computed": got, "archived": onset_tab,
                        "tex_line": line, "match": good, "means": ms, "means_tab": means_tab})
            rep.append("O1 {:<11} d {:<3} computed {:.2f}  archived {} (tex line {})  {}".format(
                diff, d, got, onset_tab, line, "ok" if good else "ONSET CONTROL FAILED"))
            rep.append("     per-r means (diagnostic): computed " +
                       " ".join("{:+.3f}".format(v) for v in ms) +
                       "  table " + " ".join(means_tab))
    return ok, rep, out


# --------------------------------------------------------------------------
# finite-J audit (section 8.5)
# --------------------------------------------------------------------------

SAMPLER_LINE = {
    "mechanism": "X0 = draw_initial(rng, Jinf, d, objective, init)",
    "boundary": "X0 = rng.standard_normal((Jinf, d)) + MINIMIZER[objective]",
    "law": "X0 = rng.standard_normal((Jinf, d)) + xs",
}


def sampler_line_of(module):
    """The first line after 'rng = np.random.default_rng(seed)' in
    one_realisation that mentions rng (calprec2.py V2's rule)."""
    src = inspect.getsource(cp.MODS[module].one_realisation).splitlines()
    for i, ln in enumerate(src):
        if ln.strip() == "rng = np.random.default_rng(seed)":
            for nx in src[i + 1:]:
                if "rng" in nx:
                    return nx.strip()
    return None


def audit_objective(c):
    mod = cp.MODS[c["module"]]
    if c["module"] == "law":
        return mod.objective(c["obj"])
    return mod.OBJECTIVES[c["obj"]], None


def redraw_X0(c, seed):
    mod = cp.MODS[c["module"]]
    rng = np.random.default_rng(seed)
    if c["module"] == "mechanism":
        return mod.draw_initial(rng, c["jinf"], c["d"], c["obj"], c["law"])
    if c["module"] == "boundary":
        return rng.standard_normal((c["jinf"], c["d"])) + mod.MINIMIZER[c["obj"]]
    if c["module"] == "law":
        return rng.standard_normal((c["jinf"], c["d"])) + mod.objective(c["obj"])[1]
    raise ValueError(c["module"])


def audit_one(c, seed, beta, le0):
    """(ratio per J of the row's list, reference ratio, F1 verdict, redrawn
    log-ESS). ratio = finitej.ess_frac(fv[:J], beta) / tau0."""
    X0 = redraw_X0(c, seed)
    f = audit_objective(c)[0]
    fv = f(X0)
    ref = finitej.ess_frac(fv, beta)
    ratios = dict((J, finitej.ess_frac(fv[:J], beta) / c["tau"]) for J in jlist_of(c))
    le_redraw = math.log(ref * len(fv))
    f1 = abs(le_redraw - le0) <= 1e-12 * max(1.0, abs(le0))
    return ratios, ref / c["tau"], f1, le_redraw


# --------------------------------------------------------------------------
# one realization: the archived one_realisation, called unmodified
# --------------------------------------------------------------------------

def _flat(x, name, out):
    if isinstance(x, dict):
        for k in sorted(x, key=lambda z: str(z)):
            _flat(x[k], "{}.{}".format(name, k) if name else str(k), out)
    elif isinstance(x, (tuple, list)):
        for i, v in enumerate(x):
            _flat(v, "{}[{}]".format(name, i), out)
    elif isinstance(x, np.ndarray):
        if x.size <= 64:
            _flat(x.tolist(), name, out)
    else:
        try:
            out[name] = float(x)
        except (TypeError, ValueError):
            out[name] = str(x)


def realise(c, diff, beta, sigma, seed):
    """(E dict, extras dict, le0 or None) from the module's one_realisation."""
    m = c["module"]
    mod = cp.MODS[m]
    o, d, ji, jl, K = c["obj"], c["d"], c["jinf"], jlist_of(c), K_of(c)
    le0 = None
    extras = {}
    if m == "ess_surface":
        res, emin = mod.one_realisation(o, diff, beta, d, sigma, DT, K, ji, jl, seed)
        E = dict((J, res[J][0]) for J in jl)
        _flat({"ess_min_sub": dict((J, res[J][1]) for J in jl), "ess_min_ref": emin}, "", extras)
    elif m == "visibility":
        E, lem = mod.one_realisation(o, beta, d, c["law"], sigma, DT, K, ji, jl, seed)
        _flat({"log_ess_min": lem}, "", extras)
    elif m == "mechanism":
        E, le0, lem = mod.one_realisation(o, beta, d, c["law"], sigma, DT, K, ji, jl, seed)
        _flat({"le0": le0, "le_min": lem}, "", extras)
    elif m == "control":
        out = mod.one_realisation(o, d, c["law"], c["tau"], c["arm"], beta, sigma, DT, K, ji, jl, seed)
        E = out[0]
        _flat({"le0": out[1], "le_min": out[2], "le_max": out[3], "b_first": out[4],
               "b_last": out[5]}, "", extras)
    elif m == "boundary":
        out = mod.one_realisation(o, d, c["tau"], beta, sigma, DT, K, ji, jl, seed)
        E, le0 = out[0], out[1]
        _flat({"le0": out[1], "le_mean": out[2], "le_min": out[3]}, "", extras)
    elif m == "regime":
        E, feats = mod.one_realisation(o, d, c["law"], beta, sigma, DT, K, ji, jl, seed)
        _flat({"feats": feats}, "", extras)
    elif m == "law":
        out = mod.one_realisation(o, d, beta, sigma, DT, K, ji, jl, seed)
        E, le0 = out[0], out[1]
        _flat({"le0": out[1], "le_mean": out[2], "le_decay": out[3]}, "", extras)
    elif m in ("sigma", "crossed", "cliff"):
        out = mod.one_realisation(o, d, diff, beta, sigma, LAM, DT, K, ji, jl, seed)
        E = out[0]
        _flat({"rest": list(out[1:])}, "", extras)
    elif m == "regimemap":
        out = mod.one_realisation(o, d, diff, beta, sigma, LAM, DT, K, ji, jl, seed)
        E = dict((J, float(v)) for J, v in zip(jl, out["E"]))
        _flat(dict((k, v) for k, v in out.items() if k != "E"), "", extras)
    else:
        raise ValueError(m)
    return dict((J, float(E[J])) for J in jl), extras, (None if le0 is None else float(le0))


def extras_json(extras):
    return json.dumps(extras, sort_keys=True)


# --------------------------------------------------------------------------
# folders
# --------------------------------------------------------------------------

def sha256_file(path):
    return cp.sha256_file(path)


def verify_folder(folder):
    """Every file in folder/sha256.txt hashes as listed (costprobe2's check);
    returns the listed relative paths, or exits 2."""
    return cp.verify_folder(folder)


def find_file(folder, rels, base):
    hits = [r for r in rels if os.path.basename(r) == base]
    if len(hits) != 1:
        sys.stderr.write("{}: expected one {}, found {}\n".format(folder, base, len(hits)))
        sys.exit(2)
    return os.path.join(folder, hits[0])


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()
