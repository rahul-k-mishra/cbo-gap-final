"""onsetr_rehearsal.py -- SYNTHETIC ONSET-R data for a rehearsal of
rerun_analysis.py before the ONSET-R queue is loaded (ledger N44).

WHAT THIS IS FOR
  rerun_analysis.py's main(), from the twenty-row reproduction check
  (O-R10) through the ONSET-R stage to the final write, cannot run until
  ONSET-R is complete: A1 refuses (exit 7). This script writes a run folder
  of SYNTHETIC ONSET-R realizations, keyed exactly as the plan's tasks, so
  that the analysis can be run once on the real twenty-row shard folders
  plus this folder. That rehearsal yields two things:
  - the twenty-row reproduction check under the new code, on real data:
    real evidence;
  - confirmation that the wiring from that check through the ONSET-R stage
    to the final write executes.
  Every ONSET-R number it produces is SYNTHETIC and must never be quoted.

WHAT IT WRITES, AND WHERE
  One folder, <out>/REHEARSAL-SYNTHETIC-onsetr-<stamp>/, containing
  rerun_real.csv (rerun.py's REAL_COLS, one row per ONSET-R task of the
  plan), README.txt (what the folder is and is not) and sha256.txt (the
  manifest rerun_analysis's A0 verifies). Every file is opened "x".
  - <out> must lie outside the repository. The script refuses (exit 2) if
    the resolved path is inside the repository root, so nothing synthetic
    can land in runs/ or be committed. Worked example: --out
    ~/cbo-rehearsal: accepted. --out runs: refused, exit 2.
  - Every row carries env "REHEARSAL-SYNTHETIC" and error "".
  It never writes into the repository, never reads or writes the queue
  state, and runs no dynamics.

  The subcommand "banner" prints the warning block that the rehearsal
  command puts at the head and the foot of the analysis log.

HOW THE ROWS ARE MADE
  The plan (rerun.load_plan, its manifest verified) gives every ONSET-R
  task: cell, diffusion, rep, seed key, boot key, beta and sigma. These are
  written exactly as rerun.py writes them (repr of beta and sigma, the key
  strings), so A0's checks pass. Only E_J is synthetic: for a realization
  with synthetic slope s, E_J = 0.5 x J^s at each J of the cell's grid
  (J <= J_inf / 10), so fit_slope recovers s. Then s = gamma(unit, r) +
  noise, with noise ~ N(0, sd_unit) drawn from
  default_rng(SeedSequence([20261028, 4, cell index, diffusion index,
  rep])): one seed per (cell, diffusion, rep), injective.

  The curves gamma, per unit (diffusion, objective, d), chosen so the
  ONSET-R stage reaches every path (delta 0.10 primary; noise sd 0.03
  unless stated):
  - isotropic ackley, d 5, 10, 20, 80: -1 + 0.4 max(0, ln(r / 1.2)), a
    steady rise from 1.2. Crossing inside the rise, near 1.54 (0.4 ln(r /
    1.2) = 0.10), "above 1".
  - isotropic ackley, d 40: -1.00 up to 1.0, a ramp to -0.70 at 2.0
    (-0.92, -0.85, -0.78 at 1.2, 1.4, 1.7), -0.70 after: a rise then a
    plateau. The crossing lies inside the rise (1.2 to 1.4), not at its
    end.
  - isotropic rastrigin, d 5: -1.00 everywhere: no crossing,
    right-censored, "no verdict (point beyond 4.8)".
  - isotropic rastrigin, d 10: baseline -1.00, -1.00, -1.00, -0.80, then
    -0.75 from 0.6: g(0.5) >= 0.10, left-censored, "no verdict (point at
    or below 0.5)". A left-censored unit is necessarily also not flat:
    g(0.5) >= delta means the 0.5 point sits delta above the mean of the
    four, so the range is at least 4 delta / 3 (the derived bound in
    O-R3).
  - isotropic rastrigin, d 20: baseline -1.00, -1.12, -1.00, -0.98 (range
    0.14), -1.00 from 0.6 to 1.7, -0.70 from 2.0: finite crossing,
    "baseline not flat", no verdict.
  - isotropic rastrigin, d 40: as d 80 below, except that every
    realization of the cell at r 1.0 has E_J = nan. cw_task drops all 48
    from both arms (the arms are paired), so the r 1.0 cell keeps no
    realization in BOTH diffusions. Its slope and every resampled slope
    are non-finite: point non-finite, every resample non-finite, FLAG
    (non-finite above 1% of B), no verdict. This also reaches the
    anisotropic rastrigin d 40 unit.
  - isotropic rastrigin, d 80: -1.00 up to 2.0, -0.60 from 2.4: a late
    rise, "above 1".
  - isotropic sphere, all d: -1.00 up to 0.6, -0.70 from 0.7: crossing
    between 0.6 and 0.7, "below 1".
  - anisotropic ackley, all d: -1.00 up to 0.85, -0.90 at 1.0, -0.80 from
    1.2; noise sd 0.15. g(1.0) is 0.10 before noise, so the resampled
    crossings fall on either side of 1.0: intended "not distinguishable
    from 1" (not guaranteed; it depends on the draw).
  - anisotropic rastrigin and sphere, all d (rastrigin d 40 apart, above):
    as isotropic ackley d 5, "above 1".
  Pooled lines (O-R7): computed where every objective's point is finite,
  "not computed" where one is censored or non-finite (isotropic d 5, 10,
  40; anisotropic d 40).

  One path cannot be reached by construction: FLAG with a FINITE point. A
  resampled slope is non-finite only if its cell kept no realization
  (rerun_analysis's ctx.S), and then the point slope is non-finite too.
  So a unit with more than 1% non-finite resamples always has a
  non-finite point, and its verdict reads "no verdict (point non-finite)",
  which is checked before FLAG. The FLAG itself is still raised and
  printed (ctx_flags), and the rehearsal shows it.

PRINTS
  The parameters, the seed rule, Python, NumPy, platform, workers, the
  plan and its sha256, the folder written, the row count per unit kind,
  and the README text.

EXIT CODES
  0 written; 2 refused (--out inside the repository, the plan unreadable,
  or the folder already exists).

HOW TO RUN
  python scripts/onsetr_rehearsal.py generate \
      --plan-from runs/rerun-plan-20261028-212945 --out ~/cbo-rehearsal --workers 2
  python scripts/onsetr_rehearsal.py banner

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import rerun                                                    # noqa: E402
import rerunlib as rl                                           # noqa: E402

SEED0, SEED_KIND = 20261028, 4
LABEL = "REHEARSAL-SYNTHETIC"
BANNER = [
    "#" * 100,
    "# REHEARSAL WITH SYNTHETIC ONSET-R DATA (ledger N44). THE ONSET-R NUMBERS IN THIS LOG ARE",
    "# SYNTHETIC: generated by scripts/onsetr_rehearsal.py, not by any trajectory. NEVER QUOTE THEM.",
    "# What this log is evidence of: the twenty-row reproduction check (O-R10) on the real shard",
    "# folders, and that the analysis runs from that check through the ONSET-R stage to the write.",
    "#" * 100,
]


def say(s=""):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()


def gamma(df, obj, d, r):
    """The synthetic slope curve of a unit (see the docstring)."""
    if df == "isotropic":
        if obj == "ackley":
            if d == 40:
                return {1.2: -0.92, 1.4: -0.85, 1.7: -0.78}.get(r, -1.0 if r <= 1.0 else -0.70)
            return -1.0 + 0.4 * max(0.0, math.log(r / 1.2))
        if obj == "rastrigin":
            if d == 5:
                return -1.0
            if d == 10:
                return {0.3: -1.0, 0.35: -1.0, 0.42: -1.0, 0.5: -0.80}.get(r, -0.75)
            if d == 20:
                base = {0.3: -1.0, 0.35: -1.12, 0.42: -1.0, 0.5: -0.98}
                if r in base:
                    return base[r]
                return -1.0 if r <= 1.7 else -0.70
            return -1.0 if r <= 2.0 else -0.60
        return -1.0 if r <= 0.6 else -0.70
    if obj == "ackley":
        return -1.0 if r <= 0.85 else (-0.90 if r == 1.0 else -0.80)
    if obj == "rastrigin" and d == 40:
        return -1.0 if r <= 2.0 else -0.60
    return -1.0 + 0.4 * max(0.0, math.log(r / 1.2))


def noise_sd(df, obj):
    return 0.15 if (df == "anisotropic" and obj == "ackley") else 0.03


def nan_cell(c, df):
    """The cell whose realizations are all invalid (isotropic rastrigin d 40,
    r 1.0); paired dropping carries it into the anisotropic arm."""
    return c["obj"] == "rastrigin" and c["d"] == 40 and c["r"] == 1.0 and df == "isotropic"


def unit_kind(df, obj, d):
    if df == "isotropic" and obj == "rastrigin":
        return {5: "right-censored", 10: "left-censored", 20: "baseline not flat",
                40: "non-finite cell (FLAG)", 80: "late rise"}[d]
    if df == "anisotropic" and obj == "rastrigin" and d == 40:
        return "non-finite cell (FLAG, paired)"
    if df == "isotropic" and obj == "sphere":
        return "crossing below 1"
    if df == "anisotropic" and obj == "ackley":
        return "crossing near 1"
    if df == "isotropic" and obj == "ackley" and d == 40:
        return "rise then plateau"
    return "rise from 1.2"


def rows_for(job):
    """One worker job: (cell index, cell, list of (diffusion, rep, task id,
    seed key, boot key)). Returns the CSV rows."""
    ci, c, tasks = job
    out = []
    Js = rl.jlist_of(c)
    for df, rep, tid, skey, bkey in tasks:
        di = c["diffs"].index(df)
        rng = np.random.default_rng(np.random.SeedSequence([SEED0, SEED_KIND, ci, di, rep]))
        s = gamma(df, c["obj"], c["d"], c["r"]) + rng.normal(0.0, noise_sd(df, c["obj"]))
        E = {}
        for J in Js:
            E[J] = "nan" if nan_cell(c, df) else repr(0.5 * float(J) ** s)
        rec = {"tid": tid, "owner": c["owner"], "rows": ";".join(c["rows_sharing"]),
               "module": c["module"], "objective": c["obj"], "d": c["d"], "law": c["law"],
               "tau0": c["plan_row"]["tau0"], "r": c["plan_row"]["r"],
               "sigma_design": c["plan_row"]["sigma_design"], "beta_design": c["plan_row"]["beta_design"],
               "J_inf": c["jinf"], "T": c["plan_row"]["T"], "K": rl.K_of(c), "arm": c["arm"],
               "subarm": c["subarm"], "diffusion": df, "rep": rep, "seed_key": skey, "boot_key": bkey,
               "beta": repr(c["beta"]), "beta_source": rl.BETA_SOURCE[c["row"]],
               "sigma": repr(c["sigma"][df]), "J_grid": c["jg"], "extras": "", "audit_ref_ratio": "",
               "audit_ratios": "", "le0": "", "le_redraw": "", "F1": "", "wall_s": "0", "peak_rss_mb": "0",
               "pid": "0", "env": LABEL, "error": "", "end": "ok"}
        for J in Js:
            rec["E_{}".format(J)] = E[J]
        out.append([rec.get(k, "") for k in rerun.REAL_COLS])
    return out


def inside_repo(path):
    p = os.path.realpath(path)
    r = os.path.realpath(ROOT)
    return p == r or p.startswith(r + os.sep)


def generate(a):
    out = os.path.expanduser(a.out)
    if inside_repo(out):
        say("REFUSED: --out {} resolves inside the repository {}; nothing synthetic may land there.".format(
            out, ROOT))
        sys.exit(2)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = os.path.join(out, "{}-onsetr-{}".format(LABEL, stamp))
    for ln in BANNER:
        say(ln)
    say("CBO-GAP onsetr_rehearsal -- SYNTHETIC ONSET-R realizations for an analysis rehearsal (N44)")
    say("  onsetr_rehearsal sha256 {}".format(rl.file_sha(os.path.abspath(__file__))))
    say("  python {}   numpy {}   platform {}   workers {}".format(
        platform.python_version(), np.__version__, platform.platform(), a.workers))
    say("  seeds: default_rng(SeedSequence([{}, {}, cell index, diffusion index, rep])), one per"
        " (cell, diffusion, rep)".format(SEED0, SEED_KIND))
    say("  E_J = 0.5 x J^s, s = gamma(unit, r) + N(0, sd); sd 0.15 for anisotropic ackley, else 0.03")
    say("  plan {}".format(a.plan_from))
    params, cells, plan_sha = rerun.load_plan(a.plan_from)
    say("  plan rerun_plan.csv sha256 {}".format(plan_sha))
    tasks = rerun.tasks_for(cells, ["ONSET-R"])
    by_cell = {}
    order = []
    for t in tasks:
        k = id(t["cell"])
        if k not in by_cell:
            by_cell[k] = (t["cell"], [])
            order.append(k)
        by_cell[k][1].append((t["diff"], t["rep"], t["tid"], rl.key_str(t["key"]),
                              rl.key_str(rl.boot_key(t["cell"], t["cell"]["owner"]))))
    jobs = [(i, by_cell[k][0], by_cell[k][1]) for i, k in enumerate(order)]
    say("  ONSET-R tasks in the plan: {} over {} cells".format(len(tasks), len(jobs)))
    os.makedirs(folder)
    pool = multiprocessing.Pool(a.workers)
    try:
        parts = pool.map(rows_for, jobs)
    finally:
        pool.close()
        pool.join()
    rows = [r for p in parts for r in p]
    with open(os.path.join(folder, "rerun_real.csv"), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(rerun.REAL_COLS)
        w.writerows(rows)
    readme = [
        "THIS FOLDER IS REHEARSAL DATA. IT IS SYNTHETIC. IT IS NOT A RESULT.",
        "",
        "Written by scripts/onsetr_rehearsal.py (ledger N44) on {}.".format(stamp),
        "rerun_real.csv holds {} ONSET-R rows keyed as the tasks of plan {}".format(len(rows), a.plan_from),
        "(rerun_plan.csv sha256 {}). Keys, betas and sigmas are the plan's;".format(plan_sha),
        "every coupled error E_J is made up (E_J = 0.5 x J^s, s from a chosen curve plus noise).",
        "No trajectory was evolved. Every row has env REHEARSAL-SYNTHETIC.",
        "",
        "Its only use: one rerun_analysis.py rehearsal, to check the twenty-row reproduction (O-R10)",
        "and that the ONSET-R stage runs. No ONSET-R number from that rehearsal may be quoted.",
        "This folder must never be copied into runs/ or committed.",
    ]
    with open(os.path.join(folder, "README.txt"), "x") as fh:
        fh.write("\n".join(readme) + "\n")
    with open(os.path.join(folder, "sha256.txt"), "x") as fh:
        for f in ("README.txt", "rerun_real.csv"):
            fh.write("{}  {}\n".format(rl.file_sha(os.path.join(folder, f)), f))
    kinds = {}
    for i, c, ts in jobs:
        for df in c["diffs"]:
            k = unit_kind(df, c["obj"], c["d"])
            kinds[k] = kinds.get(k, 0) + sum(1 for x in ts if x[0] == df)
    say("  rows written {} to {}".format(len(rows), folder))
    for k in sorted(kinds):
        say("    {:<34} {:>6} rows".format(k, kinds[k]))
    say("")
    for ln in readme:
        say("  README: " + ln)
    say("  folder {}".format(folder))


def main():
    ap = argparse.ArgumentParser(description="SYNTHETIC ONSET-R rehearsal data (N44)")
    sub = ap.add_subparsers(dest="cmd")
    g = sub.add_parser("generate")
    g.add_argument("--plan-from", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--workers", type=int, default=2)
    sub.add_parser("banner")
    a = ap.parse_args()
    if a.cmd == "banner":
        for ln in BANNER:
            say(ln)
        return
    if a.cmd != "generate":
        ap.print_help()
        sys.exit(2)
    generate(a)


if __name__ == "__main__":
    main()
