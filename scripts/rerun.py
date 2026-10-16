"""
rerun.py  --  CBO-GAP round 2: the fixed-beta rerun, trajectories

WHAT THIS DOES, IN PLAIN LANGUAGE
---------------------------------
It evolves every coupled realization of the seventeen rows of Table 2 under
the design fixed in notes/ANALYSIS_CRITERIA.md (decided by Rahul in ten
messages of 2026-10-16), with each row's own archived dynamics, and writes
every realization's per-J coupled error. It computes no slope, interval or
verdict: those are rerun_analysis.py's, whose docstring carries the
analysis criteria. Shared definitions (cells, keys, betas, the onset
estimator, the finite-J audit) are in scripts/rerunlib.py.

It runs in four modes, in this order:
  --precheck   (laptop; no trajectory) builds the PLAN: every cell of every
               row, its owner row and seed key, its beta and sigma. Runs
               V0, P1, S1, A-BETA, A-SIGMA, C2, O1, K1, K2 and K4 and
               writes a plan folder. The archive's CSVs and the manuscript
               source are read here and nowhere else, because the Kaggle
               bundle ships only two archived CSVs (kgrun.py ARCHIVE_CSVS).
  --schedule   (no trajectory) prints the shard plan for --rows and
               --nshards from the plan and costprobe2's measured walls.
  --smoke      D-SMOKE: one task per module run twice, bitwise compared.
  (default)    the trajectories of --rows from --plan-from, sharded,
               resumable, with the finite-J audit and F1.

WHAT IS IMPORTED, AND WHAT IS NOT (CLAUDE.md rule 4)
  Every realization is the archived module's one_realisation, imported and
  called unmodified with SeedSequence(key) as its seed (costprobe2's
  construction, ledger N16). The calls are rerunlib.realise. The archived
  betas are recomputed by each module's own code path; the only retyped
  lines are the 4000-point probe samplers, and A-BETA checks every result
  against the archive. The finite-J audit imports finitej.ess_frac.

THE DESIGN (notes/ANALYSIS_CRITERIA.md)
  Cells: costprobe2.py GRID, checked by V0. Betas: calprec2_beta.csv for
  CONC, TAU8, SIGMA and ANISO; the archived betas elsewhere (rerunlib
  docstring). Seeds: the approved key layout, kind 81, the owner row in
  field 3, diffusion absent (layout section; rerunlib docstring). Shared
  cells: run once, by the job whose --rows contain the owner row.

PRE-SPECIFIED CRITERIA (fixed 2026-10-16, before first execution)
------------------------------------------------------------------
  V0  PLAN IDENTITY. (a) costprobe2.p0_values: every GRID factor equals the
      constant the archived source assigns (costprobe2 P0(a)). (b) For each
      row, cells x diffusions equals Table 2's cells and that times M its
      realizations (costprobe2.TABLE2). Any failure: exit 2.
      Worked example: ONSET 3 objectives x 5 d x 6 r = 90 cells x 2
      diffusions = 180, x 12 = 2160: Table 2, pass. With 5 r values:
      150, exit 2.
  P1  ARCHIVE IDENTITY. Every module in costprobe2.MODS, and finitej, lies
      in the archive directory and hashes to its zenodo-v1.sha256 entry.
      Otherwise exit 2. Worked example: regime.py hashing to
      b671a58c...56b2: pass; one byte edited: exit 2.
  S1  SAMPLER IDENTITY (finite-J audit). In mechanism, boundary and law,
      the first line after "rng = np.random.default_rng(seed)" in
      one_realisation that mentions rng must equal rerunlib.SAMPLER_LINE.
      Otherwise exit 2. Worked example: law's line "X0 =
      rng.standard_normal((Jinf, d)) + xs": pass.
  A-BETA  ARCHIVED BETAS REPRODUCE (precheck). For every cell of a row
      that keeps archived betas, the recomputed beta is compared with every
      matching row of the archived CSV named in rerunlib.ARCH_CHECK. It
      agrees iff |recomputed - archived| <= half a unit in the archived
      string's last printed digit, plus 1e-9 relative. A cell with no
      matching archived row, or any disagreement, is a FAIL; any FAIL:
      exit 2, after the whole check is printed and written.
      Worked example: archived "1.9047" (regime_A_reference.csv); a
      recomputed 1.904731 differs by 3.1e-5 <= 5e-5 + 1.9e-9: agrees. A
      recomputed 1.90485 differs by 1.5e-4: FAIL.
  A-SIGMA  The same test for sigma, per (cell, diffusion), where the
      archived CSV has a sigma column (SIGMA, ANISO, RMAP, CLIFF, ONSET).
      Worked example: regimemap_D_real.csv sigma "0.547723" against
      sqrt(2 x 0.75 / 5) = 0.5477226: agrees.
  C2  CALPREC2 BETAS (precheck). With --calprec2 DIR (a verified finalize
      folder holding calprec2_beta.csv), every cell of CONC, TAU8, SIGMA and
      ANISO must have exactly one table row with a non-empty beta and a
      label not starting "incomplete"; otherwise exit 2. The label, its
      tau_ref and the adequacy columns are copied into the plan, unchanged,
      for rerun_analysis.py's reference-adequacy reporting. Without
      --calprec2 those four rows are written as "beta pending" and cannot
      be run from this plan.
      Worked example: CONC ackley d 40 centred tau0 0.01 with label "beta
      (not adequate)" and beta 3.1e2: copied; the run uses that beta and
      the label travels with it. A cell labelled "incomplete (phase C)":
      exit 2.
  O1  ONSET CONTROL (item 7, H3; ninth message: mandatory, before the
      estimator is used for anything). rerunlib.onset_control recomputes the
      ten archived onsets from zenodo-v1/regimemap_D_real.csv (per (diffusion,
      objective, d, r): the mean of the archived slopes over rep; then the
      mean over the three objectives; then rerunlib.onset_bp) and compares
      each with the r_onset column of the manuscript's onset table
      (zenodo-v1/sn-article.tex, tab:onset, lines 608 to 612 and 615 to
      619). Each must be equal at the table's two decimals. Any mismatch
      prints "ONSET CONTROL FAILED" and exits 2; no plan is written, so no
      trajectory can run. The per-r means are printed beside the table's,
      as a diagnostic with no stop.
      Worked example: iso d 40, table 1.25 (tex line 611). Computed 1.25:
      pass. Computed 1.00: "ONSET CONTROL FAILED", exit 2.
  K1  INJECTIVITY. No two distinct (cell group, rep) tasks share a key; a
      shared cell is one group. Otherwise exit 2.
  K2  PAIRING. In SIGMA, ANISO, RMAP, CLIFF and ONSET each cell's isotropic
      and anisotropic tasks have identical keys; elsewhere a cell has one
      diffusion. Otherwise exit 2.
  K3  The seed key and the bootstrap key are written for every realization
      (rerun_real.csv) and every cell (rerun_plan.csv).
  K4  SHARING. Cells of different rows with identical arguments (key fields
      4 to 15, beta, M, J grid, diffusions) form one group, owned by the
      first row in ROW_ORDER. The computed multi-row groups must equal
      rerunlib.expected_shared(): ackley, sphere, rosenbrock in REFSIZE,
      NAMED and HORIZON; rastrigin in NAMED and HORIZON; RMAP and ONSET at
      d 10 and 40, r 1.0 to 3.0, tau0 0.1. Any other sharing, or a missing
      one: exit 2, naming the cells and rows.
      Worked example: CONC and PROBEARM's (ackley, d 2, centred, tau0 0.5)
      have the same coordinates but different betas: two groups, as
      expected. Had their betas been equal, K4 would find a sharing not in
      the list and exit 2.
  F1  FINITE-J AUDIT IDENTITY (section 8.5). For every realization of CONC,
      PROBEARM, TAU8 and GEOM, the initial ensemble is redrawn from the
      realization's seed and the log-ESS of the full redrawn reference must
      equal the le0 that one_realisation returned, within 1e-12 x max(1,
      |le0|). The redrawn ratios ESS_0(J)/J/tau0 are written with the
      realization. A failure writes "F1 FAILED" in the row; the run
      continues, and ends with exit 3.
      Worked example: le0 8.58213012 redrawn 8.58213012 (difference 2e-15):
      pass. Difference 3e-9: F1 FAILED.
  D-SMOKE  DETERMINISM. --smoke runs, for each module of --rows, its
      smallest task twice in separate worker processes with the same key
      (kind 83). Every E_J must be identical as a %.17g string. Otherwise
      exit 3.
  G-RSS  Every task reports its worker's peak RSS (resource.getrusage,
      Linux kB / 1024), a running maximum over that worker's tasks. Above
      3072 MB (costprobe2's budget) the row is flagged OVER BUDGET and the
      run ends with exit 4. costprobe2 measured every unit of every row at
      354.2 MB or less (runs/costprobe2-finalize-20261011-101659).
  G-STOP  --stop-after SECONDS (default 36000, a margin choice under
      Kaggle's 43200 s cap, as in calprec2): no task starts after that;
      running tasks finish; the run ends with exit 5 and the remaining
      tasks are run by a resume (CLAUDE.md rule 17).
  SHARDS  Tasks of --rows are assigned to --nshards shards by longest-
      processing-time first over costprobe2's measured unit walls (--timing-
      from DIR, repeatable, one folder per flag so that kgrun rewrites each
      runs/<name> token: verified costprobe2 run folders): sorted by wall
      descending,
      then task id, each to the currently lightest shard (ties to the lower
      shard index). The assignment depends only on the plan, --rows,
      --nshards and the walls, so every shard computes the same split.
      The estimate per shard is sum(wall) / --workers, labelled "lower
      bound (perfect scaling; walls from costprobe2's timing beta)". A task
      whose unit costprobe2 never measured: exit 2, listed.
      Worked example: walls 5, 4, 3, 3 and 2 s on two shards. 5 goes to
      s0 (loads 5, 0); 4 to s1 (5, 4); 3 to s1 (5, 7); 3 to s0 (8, 7); 2 to
      s1 (8, 9). Result: s0 = {5, 3}, s1 = {4, 3, 2}.
  RESUME  (CLAUDE.md rule 17) --resume-from DIR[,DIR]: each folder is read
      only after its sha256.txt verifies; a task counts as completed only
      when its row ends "ok"; a completed task id in two folders stops the
      run; the parameters in each folder's rerun_params.csv other than the
      folder list must equal this run's, or it stops; every folder read and
      the number of tasks skipped from each are printed. Output goes to a
      new folder.

SEEDS
  Trajectory: SeedSequence(key), key as in rerunlib (kind 81), passed
  unchanged to one_realisation. Smoke: kind 83. Bootstrap keys (kind 71)
  are written for rerun_analysis.py. Entropy 20261016 is used by no other
  script; kinds 71, 81, 83 by no other script (kinds in use elsewhere: 1,
  2, 11, 12, 31 to 35, 41 to 43, 51, 61 to 67, 91).

OUTPUT (every file opened "x", every row flushed and fsynced)
  precheck: <outdir>/rerun-plan-<stamp>/
    rerun_plan_params.csv   verdicts and parameters of the plan
    rerun_plan.csv          one row per (row, cell): owner, rows sharing,
                            coordinates, keys, beta (repr), beta source,
                            sigma per diffusion (repr), calprec2 columns
    rerun_archive_check.csv A-BETA and A-SIGMA per (row, cell, diffusion)
    rerun_onset_control.csv O1
  run: <outdir>/rerun-<stamp>[-smoke][-s<i>of<k>]/
    rerun_params.csv        parameters (checked on resume)
    rerun_real.csv          one row per realization: task id, keys, cell,
                            diffusion, rep, beta, sigma, E_J for every J
                            of its grid (%.17g), the module's other outputs
                            (JSON), the audit ratios and F1, wall, peak
                            RSS, pid, environment, error, end marker

HOW TO RUN (from the repository root, venv active; Kaggle through kgrun)
    python scripts/rerun.py --precheck [--calprec2 runs/<calprec2 finalize>]
    python scripts/manifest.py runs/rerun-plan-<stamp>
    python scripts/rerun.py --schedule --plan-from runs/rerun-plan-<stamp> \
        --timing-from runs/<costprobe2 s0> --timing-from runs/<costprobe2 s1> \
        --rows ROWS --nshards K --workers 4
    python scripts/rerun.py --smoke --plan-from ... --rows ROWS --workers 4
    python scripts/rerun.py --plan-from ... --timing-from ... --rows ROWS \
        --shard i --nshards K --workers 4
  Exit codes: 0 complete; 2 setup or a precheck criterion failed; 3 F1 or
  D-SMOKE failed; 4 task errors or OVER BUDGET; 5 stopped by G-STOP.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import json                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cbopaths                                                 # noqa: E402
import rerunlib as rl                                           # noqa: E402

cp = rl.cp
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = cbopaths.output_root(ROOT)
ENV = "python {} numpy {}".format(platform.python_version(), np.__version__)
HERE = os.path.dirname(os.path.abspath(__file__))

RSS_BUDGET_MB = 3072.0
STOP_AFTER_DEFAULT = 36000.0
SCHED_LABEL = "lower bound (perfect scaling; walls from costprobe2's timing beta)"

PLAN_COLS = (["row", "owner", "rows_sharing", "group", "module", "objective", "d", "law", "tau0",
              "r", "sigma_design", "beta_design", "J_inf", "T", "K", "arm", "subarm", "diffusions",
              "M", "J_grid", "seed_key_base", "boot_key", "beta", "beta_source", "sigma_isotropic",
              "sigma_anisotropic", "sigma_none", "cal_label", "cal_tau_ref", "cal_tau_ref_n",
              "cal_range", "cal_adequacy", "cal_C5m", "cal_D1", "cal_med_64M", "cal_med_256M",
              "cal_provenance", "cal_flags"])
REAL_COLS = (["tid", "owner", "rows", "module", "objective", "d", "law", "tau0", "r",
              "sigma_design", "beta_design", "J_inf", "T", "K", "arm", "subarm", "diffusion",
              "rep", "seed_key", "boot_key", "beta", "beta_source", "sigma", "J_grid"]
             + ["E_{}".format(J) for J in rl.JCOLS]
             + ["extras", "audit_ref_ratio", "audit_ratios", "le0", "le_redraw", "F1",
                "wall_s", "peak_rss_mb", "pid", "env", "error", "end"])


def hdr(s):
    print("\n" + "-" * 96)
    print(s)
    print("-" * 96)
    sys.stdout.flush()


def fx(v):
    return "" if v is None else repr(v)


def write_rows(path, cols, rows):
    with open(path, "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow(r)
        fh.flush()
        os.fsync(fh.fileno())


def new_outdir(name):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(OUTROOT, "{}-{}".format(name, stamp))
    os.makedirs(out)
    return out


def script_hashes():
    return {"rerun_sha256": rl.file_sha(os.path.abspath(__file__)),
            "rerunlib_sha256": rl.file_sha(os.path.join(HERE, "rerunlib.py")),
            "costprobe2_sha256": rl.file_sha(os.path.join(HERE, "costprobe2.py"))}


# --------------------------------------------------------------------------
# V0, P1, S1
# --------------------------------------------------------------------------

def check_v0():
    hdr("V0  plan identity (costprobe2 P0(a); Table 2 counts)")
    ok = cp.p0_values(rl.ROWS)
    for row in rl.ROWS:
        cells = rl.cells_of(row)
        n = sum(len(c["diffs"]) for c in cells)
        m = sum(len(c["diffs"]) * c["M"] for c in cells)
        want = cp.TABLE2[row]
        good = (n, m) == tuple(want)
        ok = ok and good
        print("  V0(b) {:<9} cells {:>4} realizations {:>5}  Table 2 {}  {}".format(
            row, n, m, want, "ok" if good else "MISMATCH"))
    return ok


def check_p1():
    hdr("P1  archive identity")
    ok = True
    items = sorted(cp.MODS.items()) + [("finitej", rl.finitej)]
    for name, mod in items:
        f = os.path.abspath(mod.__file__)
        want = rl.FINITEJ_SHA256 if name == "finitej" else cp.ARCHIVE_SHA256[name]
        inside = os.path.dirname(f) == os.path.abspath(rl.ARCH) and f.endswith(".py")
        h = rl.file_sha(f)
        good = inside and h == want
        ok = ok and good
        print("  {:<12} {}...  {}".format(name, h[:16], "ok" if good else "FAIL ({})".format(f)))
    return ok


def check_s1():
    hdr("S1  sampler identity (finite-J audit modules)")
    ok = True
    for m in ("mechanism", "boundary", "law"):
        got = rl.sampler_line_of(m)
        good = got == rl.SAMPLER_LINE[m]
        ok = ok and good
        print("  {:<10} {!r}  {}".format(m, got, "ok" if good else "FAIL, expected {!r}".format(
            rl.SAMPLER_LINE[m])))
    return ok


# --------------------------------------------------------------------------
# precheck: the plan
# --------------------------------------------------------------------------

def group_ident(c, beta_s):
    return rl.coord_fields(c) + (beta_s, c["M"], c["jg"], tuple(c["diffs"]))


def build_plan(cal):
    """(plan rows as dicts, archive check rows, ok flags)."""
    entries = []
    for row in rl.ROWS:
        for c in rl.cells_of(row):
            entries.append(c)
    hdr("BETAS AND SIGMAS  (A-BETA, A-SIGMA, C2)")
    chk_rows = []
    a_ok, c2_ok = True, True
    beta_s = {}
    for i, c in enumerate(entries):
        cal_rec = None
        if c["row"] in rl.CALROWS:
            if cal is None:
                beta = None
            else:
                cal_rec = cal.get(rl.calprec2_key(c))
                if cal_rec is None or not cal_rec["beta"] or cal_rec["label"].startswith("incomplete"):
                    c2_ok = False
                    print("  C2 FAIL {}: {}".format(rl.cell_label(c),
                                                    "no table row" if cal_rec is None else
                                                    "label {!r} beta {!r}".format(cal_rec["label"],
                                                                                  cal_rec["beta"])))
                    beta = None
                else:
                    beta = float(cal_rec["beta"])
        else:
            beta = rl.recompute_beta(c)
        c["beta"] = beta
        c["cal"] = cal_rec
        beta_s[i] = "pending" if beta is None else repr(beta)
        c["sigma"] = dict((df, rl.sigma_for(c, df)) for df in c["diffs"])
        for df in c["diffs"]:
            if beta is None and c["row"] not in rl.ARCH_CHECK:
                v, det = "not applicable", "beta pending (calprec2)"
            else:
                v, det = rl.archive_check(c, df, beta if beta is not None else float("nan"),
                                          c["sigma"][df])
            if v == "FAIL":
                a_ok = False
                print("  A-BETA/A-SIGMA FAIL {} {}: {}".format(rl.cell_label(c), df, det))
            chk_rows.append([c["row"], rl.cell_label(c), df, fx(beta), fx(c["sigma"][df]), v, det])
    nfail = sum(1 for r in chk_rows if r[5] == "FAIL")
    nok = sum(1 for r in chk_rows if r[5] == "ok")
    print("  archive check: {} ok, {} FAIL, {} not applicable".format(
        nok, nfail, len(chk_rows) - nok - nfail))

    # groups and owners (K4)
    hdr("K4  shared cells")
    groups = {}
    for i, c in enumerate(entries):
        groups.setdefault(group_ident(c, beta_s[i]), []).append(c)
    k4_ok = True
    exp = rl.expected_shared()
    seen = []
    for gid, cs in groups.items():
        rows = [c["row"] for c in cs]
        owner = min(rows, key=rl.ROWS.index)
        for c in cs:
            c["owner"] = owner
            c["rows_sharing"] = sorted(set(rows), key=rl.ROWS.index)
        if len(set(rows)) != len(rows):
            k4_ok = False
            print("  K4 FAIL: a row holds one cell twice: {}".format(rl.cell_label(cs[0])))
        if len(rows) > 1:
            seen.append((rl.share_key(cs[0]), sorted(rows, key=rl.ROWS.index)))
    seen_keys = [ek for ek, _ in seen]
    for ek, rows in sorted(seen, key=lambda z: str(z[0])):
        good = ek in exp and exp[ek] == rows and seen_keys.count(ek) == 1
        k4_ok = k4_ok and good
        print("  shared {} rows {} owner {}  {}".format(ek, rows, rows[0],
                                                       "ok" if good else "NOT EXPECTED"))
    for ek, rows in sorted(exp.items(), key=lambda z: str(z[0])):
        if ek not in seen_keys:
            k4_ok = False
            print("  K4 FAIL: expected sharing {} rows {} not found".format(ek, rows))
    print("  K4 {}  ({} groups with more than one row)".format("PASS" if k4_ok else "FAIL", len(seen)))

    # K1, K2 over tasks (one per group, diffusion, rep)
    hdr("K1, K2  injectivity and pairing")
    keys = {}
    k1_ok, k2_ok = True, True
    for gid, cs in groups.items():
        c = cs[0]
        if c["row"] in rl.PAIRED:
            if c["diffs"] != ["isotropic", "anisotropic"]:
                k2_ok = False
        elif len(c["diffs"]) != 1:
            k2_ok = False
        for rep in range(c["M"]):
            k = rl.traj_key(c, c["owner"], rep)
            if k in keys:
                k1_ok = False
                print("  K1 FAIL: key {} for {} and {}".format(rl.key_str(k), rl.cell_label(c),
                                                              rl.cell_label(keys[k])))
            keys[k] = c
    print("  K1 {}  ({} distinct (group, rep) keys)".format("PASS" if k1_ok else "FAIL", len(keys)))
    print("  K2 {}  (diffusion absent from every key; paired rows carry both diffusions)".format(
        "PASS" if k2_ok else "FAIL"))
    return entries, chk_rows, {"A": a_ok, "C2": c2_ok, "K4": k4_ok, "K1": k1_ok, "K2": k2_ok}


def plan_row(c):
    cal = c.get("cal") or {}
    return [c["row"], c["owner"], ";".join(c["rows_sharing"]),
            rl.key_str(rl.coord_fields(c)), c["module"], c["obj"], c["d"], c["law"], fx(c["tau"]),
            fx(c["r"]), fx(c["sigma_design"]), fx(c["beta_design"]), c["jinf"], fx(c["T"]),
            rl.K_of(c), c["arm"], c["subarm"], ";".join(c["diffs"]), c["M"], c["jg"],
            rl.key_str(rl.traj_key(c, c["owner"], 0)[:-1]), rl.key_str(rl.boot_key(c, c["owner"])),
            "pending" if c["beta"] is None else repr(c["beta"]), rl.BETA_SOURCE[c["row"]],
            fx(c["sigma"].get("isotropic")), fx(c["sigma"].get("anisotropic")),
            fx(c["sigma"].get("none")),
            cal.get("label", ""), cal.get("tau_ref", ""), cal.get("tau_ref_n", ""), cal.get("range", ""),
            cal.get("adequacy", ""), cal.get("C5m", ""), cal.get("D1", ""), cal.get("med_64M", ""),
            cal.get("med_256M", ""), cal.get("provenance", ""), cal.get("flags", "")]


def precheck(a):
    ok = check_v0()
    ok = check_p1() and ok
    ok = check_s1() and ok
    if not ok:
        sys.stderr.write("V0, P1 or S1 failed\n")
        sys.exit(2)
    cal, cal_dir, cal_sha = None, "none", ""
    if a.calprec2:
        rels = rl.verify_folder(a.calprec2)
        path = rl.find_file(a.calprec2, rels, "calprec2_beta.csv")
        cal = rl.read_calprec2(path)
        cal_dir, cal_sha = os.path.abspath(a.calprec2), rl.file_sha(path)
        print("\n  calprec2 table {}  sha256 {}  {} cells".format(path, cal_sha, len(cal)))
    else:
        print("\n  no --calprec2: CONC, TAU8, SIGMA and ANISO are written as 'beta pending'")

    hdr("O1  onset control (before any use of the onset estimator, before any trajectory)")
    o1_ok, o1_rep, o1_rec = rl.onset_control(rl.ARCH, os.path.join(rl.ARCH, "sn-article.tex"))
    for ln in o1_rep:
        print("  " + ln)
    print("  O1 {}".format("PASS" if o1_ok else "ONSET CONTROL FAILED"))
    if not o1_ok:
        sys.stderr.write("O1 failed: no plan written\n")
        sys.exit(2)

    entries, chk_rows, flags = build_plan(cal)
    good = all(flags.values())
    outdir = new_outdir("rerun-plan")
    hs = script_hashes()
    params = [["mode", "precheck"], ["env", ENV], ["platform", platform.platform()],
              ["archive", rl.ARCH], ["calprec2_dir", cal_dir], ["calprec2_sha256", cal_sha],
              ["entropy", rl.ENTROPY], ["kind_traj", rl.KIND_TRAJ], ["kind_boot", rl.KIND_BOOT]]
    params += [[k, v] for k, v in sorted(hs.items())]
    params += [["V0", "PASS"], ["P1", "PASS"], ["S1", "PASS"], ["O1", "PASS"]]
    params += [["A-BETA/A-SIGMA", "PASS" if flags["A"] else "FAIL"],
               ["C2", "PASS" if flags["C2"] else "FAIL"],
               ["K1", "PASS" if flags["K1"] else "FAIL"], ["K2", "PASS" if flags["K2"] else "FAIL"],
               ["K4", "PASS" if flags["K4"] else "FAIL"],
               ["calprec2_rows", "present" if cal is not None else "pending"]]
    write_rows(os.path.join(outdir, "rerun_plan_params.csv"), ["name", "value"], params)
    write_rows(os.path.join(outdir, "rerun_archive_check.csv"),
               ["row", "cell", "diffusion", "beta", "sigma", "verdict", "detail"], chk_rows)
    write_rows(os.path.join(outdir, "rerun_onset_control.csv"),
               ["diffusion", "d", "computed", "archived", "tex_line", "match", "means_computed",
                "means_table"],
               [[r["diffusion"], r["d"], repr(r["computed"]), r["archived"], r["tex_line"],
                 "yes" if r["match"] else "NO", " ".join(repr(v) for v in r["means"]),
                 " ".join(r["means_tab"])] for r in o1_rec])
    write_rows(os.path.join(outdir, "rerun_plan.csv"), PLAN_COLS, [plan_row(c) for c in entries])
    hdr("PLAN WRITTEN")
    print("  {}".format(outdir))
    for k in ("A", "C2", "K1", "K2", "K4"):
        print("  {:<6} {}".format(k, "PASS" if flags[k] else "FAIL"))
    if not good:
        print("\n  A precheck criterion failed: this plan is recorded but no run accepts it.")
        sys.exit(2)
    print("\n  Next: python scripts/manifest.py {}".format(outdir))
    sys.exit(0)


# --------------------------------------------------------------------------
# reading a plan
# --------------------------------------------------------------------------

def opt_float(s):
    return None if s == "" else float(s)


def load_plan(folder):
    rels = rl.verify_folder(folder)
    ppath = rl.find_file(folder, rels, "rerun_plan_params.csv")
    params = dict((r[0], r[1]) for r in csv.reader(open(ppath, newline="")) if r and r[0] != "name")
    for k in ("V0", "P1", "S1", "O1", "A-BETA/A-SIGMA", "C2", "K1", "K2", "K4"):
        if params.get(k) != "PASS":
            sys.stderr.write("plan {}: {} is {!r}, not PASS; refused\n".format(folder, k, params.get(k)))
            sys.exit(2)
    path = rl.find_file(folder, rels, "rerun_plan.csv")
    cells = []
    for r in csv.DictReader(open(path, newline="")):
        c = rl._cell(r["row"], r["module"], r["objective"], int(r["d"]), law=r["law"],
                     tau=opt_float(r["tau0"]), r=opt_float(r["r"]),
                     sigma_design=opt_float(r["sigma_design"]),
                     beta_design=opt_float(r["beta_design"]), jinf=int(r["J_inf"]),
                     T=float(r["T"]), arm=r["arm"], subarm=int(r["subarm"]),
                     diffs=r["diffusions"].split(";"), jg=r["J_grid"])
        c["owner"] = r["owner"]
        c["rows_sharing"] = r["rows_sharing"].split(";")
        c["beta"] = None if r["beta"] == "pending" else float(r["beta"])
        c["sigma"] = dict((df, float(r["sigma_" + df])) for df in c["diffs"])
        c["plan_row"] = r
        cells.append(c)
    return params, cells, rl.file_sha(path)


def tasks_for(cells, rows, kind=rl.KIND_TRAJ):
    """One task per (group, diffusion, rep) whose owner row is in rows."""
    tasks = []
    for c in cells:
        if c["row"] != c["owner"] or c["owner"] not in rows:
            continue
        if c["beta"] is None:
            sys.stderr.write("row {} has beta pending in this plan; run --precheck with "
                             "--calprec2\n".format(c["row"]))
            sys.exit(2)
        for df in c["diffs"]:
            for rep in range(c["M"]):
                k = rl.traj_key(c, c["owner"], rep, kind)
                tasks.append({"cell": c, "diff": df, "rep": rep, "key": k,
                              "tid": "{}|{}".format(rl.key_str(k), df)})
    return tasks


def unit_of(t):
    c = t["cell"]
    diff = t["diff"] if c["module"] in ("ess_surface", "sigma", "crossed", "cliff",
                                        "regimemap") else "none"
    return (c["module"], c["obj"], c["d"], diff, c["jinf"], float(c["T"]), c["jg"], c["arm"])


def load_walls(folders):
    walls = {}
    for f in folders:
        rels = rl.verify_folder(f)
        for rel in rels:
            if os.path.basename(rel) != "costprobe2_results.csv":
                continue
            for r in csv.DictReader(open(os.path.join(f, rel), newline="")):
                if r["kind"] != "main" or r["end"] != "ok":
                    continue
                u = (r["module"], r["objective"], int(r["d"]), r["diffusion"], int(r["J_inf"]),
                     float(r["T"]), r["J_grid"], r["arm"])
                walls[u] = float(r["wall_s"])
    return walls


def assign_shards(tasks, walls, nshards):
    miss = sorted(set(unit_of(t) for t in tasks if unit_of(t) not in walls), key=str)
    if miss:
        for u in miss:
            print("  no measured wall for unit {}".format(u))
        sys.stderr.write("SHARDS: {} unit(s) without a measured wall\n".format(len(miss)))
        sys.exit(2)
    order = sorted(tasks, key=lambda t: (-walls[unit_of(t)], t["tid"]))
    load = [0.0] * nshards
    for t in order:
        s = min(range(nshards), key=lambda i: (load[i], i))
        t["shard"] = s
        t["est"] = walls[unit_of(t)]
        load[s] += t["est"]
    return load


# --------------------------------------------------------------------------
# the worker
# --------------------------------------------------------------------------

def run_one(t):
    c, df = t["cell"], t["diff"]
    out = {"tid": t["tid"], "error": "", "end": "err", "E": {}, "extras": {}, "audit": None,
           "le0": None, "le_redraw": None, "F1": "", "wall": float("nan")}
    try:
        seed = np.random.SeedSequence(list(t["key"]))
        t0 = time.time()
        E, extras, le0 = rl.realise(c, df, c["beta"], c["sigma"][df], seed)
        out["wall"] = time.time() - t0
        out["E"], out["extras"], out["le0"] = E, extras, le0
        if c["row"] in rl.AUDIT_ROWS:
            ratios, ref, f1, le_rd = rl.audit_one(c, np.random.SeedSequence(list(t["key"])),
                                                  c["beta"], le0)
            out["audit"] = (ratios, ref)
            out["le_redraw"] = le_rd
            out["F1"] = "ok" if f1 else "F1 FAILED"
        out["end"] = "ok"
    except Exception as exc:
        out["error"] = "{}: {}".format(type(exc).__name__, exc)
    out["rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out["pid"] = os.getpid()
    return out


def real_row(t, o):
    c = t["cell"]
    E = o["E"]
    row = [t["tid"], c["owner"], ";".join(c["rows_sharing"]), c["module"], c["obj"], c["d"], c["law"],
           fx(c["tau"]), fx(c["r"]), fx(c["sigma_design"]), fx(c["beta_design"]), c["jinf"],
           fx(c["T"]), rl.K_of(c), c["arm"], c["subarm"], t["diff"], t["rep"], rl.key_str(t["key"]),
           rl.key_str(rl.boot_key(c, c["owner"])), repr(c["beta"]), rl.BETA_SOURCE[c["row"]],
           repr(c["sigma"][t["diff"]]), c["jg"]]
    row += ["%.17g" % E[J] if J in E else "" for J in rl.JCOLS]
    if o["audit"] is not None:
        ratios, ref = o["audit"]
        aud = [repr(ref), json.dumps(dict((str(J), v) for J, v in sorted(ratios.items())))]
    else:
        aud = ["", ""]
    row += [rl.extras_json(o["extras"])] + aud
    row += [fx(o["le0"]), fx(o["le_redraw"]), o["F1"], "%.3f" % o["wall"], "%.1f" % o["rss"],
            o["pid"], ENV, o["error"].replace("\n", " "), o["end"]]
    return row


def run_pool(tasks, workers, outpath, stop_after, label, fresh=False):
    """Run tasks on a Pool; write each row as it completes. Returns
    (rows written as dicts, stopped flag, number not started)."""
    hdr("{}  {} task(s) on {} worker(s); stop-after {:.0f} s".format(label, len(tasks), workers,
                                                                    stop_after))
    fh = open(outpath, "x", newline="")
    w = csv.writer(fh)
    w.writerow(REAL_COLS)
    fh.flush()
    os.fsync(fh.fileno())
    done = []
    pending = list(tasks)
    inflight = {}
    t0 = time.time()
    stopped = False
    pool = multiprocessing.Pool(processes=workers, maxtasksperchild=1 if fresh else None)
    try:
        while pending or inflight:
            while pending and len(inflight) < 2 * workers and not stopped:
                if time.time() - t0 > stop_after:
                    stopped = True
                    print("  G-STOP: {:.0f} s elapsed; no further task starts".format(time.time() - t0))
                    break
                t = pending.pop(0)
                inflight[t["tid"]] = (t, pool.apply_async(run_one, (t,)))
            progressed = False
            for tid in list(inflight):
                t, ar = inflight[tid]
                if not ar.ready():
                    continue
                try:
                    o = ar.get()
                except Exception as exc:
                    o = {"tid": tid, "error": "pool: {}".format(exc), "end": "err", "E": {},
                         "extras": {}, "audit": None, "le0": None, "le_redraw": None, "F1": "",
                         "wall": float("nan"), "rss": float("nan"), "pid": ""}
                del inflight[tid]
                progressed = True
                row = real_row(t, o)
                w.writerow(row)
                fh.flush()
                os.fsync(fh.fileno())
                done.append(dict(zip(REAL_COLS, [str(x) for x in row])))
                c = t["cell"]
                flag = ""
                if o["end"] == "ok" and o["rss"] > RSS_BUDGET_MB:
                    flag = "  OVER BUDGET"
                if o["F1"] == "F1 FAILED":
                    flag += "  F1 FAILED"
                if o["end"] == "ok":
                    print("  [{:>6}/{:<6}] {:<9} {:<10} {:<17} d={:<3} {:<11} rep {:<2} wall {:>7.1f} s "
                          "RSS {:>7.1f} MB{}  elapsed {:>7.0f} s".format(
                              len(done), len(tasks), c["owner"], c["module"], c["obj"], c["d"], t["diff"],
                              t["rep"], o["wall"], o["rss"], flag, time.time() - t0))
                else:
                    print("  [{:>6}/{:<6}] ERROR {} {}".format(len(done), len(tasks), tid, o["error"]))
                sys.stdout.flush()
            if not progressed:
                time.sleep(0.2)
            if stopped and not inflight:
                break
    finally:
        pool.close()
        pool.join()
        fh.close()
    print("  finished {} task(s) in {:.1f} s; {} not started".format(len(done), time.time() - t0,
                                                                    len(pending)))
    return done, stopped, len(pending)


# --------------------------------------------------------------------------
# run modes
# --------------------------------------------------------------------------

def parse_rows(s):
    rows = [r for r in s.split(",") if r]
    bad = [r for r in rows if r not in rl.ROWS]
    if bad or not rows:
        sys.stderr.write("--rows: unknown or empty {}\n".format(bad))
        sys.exit(2)
    return sorted(set(rows), key=rl.ROWS.index)


def read_params(folder, rels):
    p = rl.find_file(folder, rels, "rerun_params.csv")
    return dict((r[0], r[1]) for r in csv.reader(open(p, newline="")) if r and r[0] != "name")


def resume_done(folders, params):
    done = {}
    for f in folders:
        rels = rl.verify_folder(f)
        old = read_params(f, rels)
        diff = [k for k in params if k not in ("resume_from",) and old.get(k) != str(params[k])]
        if diff:
            for k in diff:
                print("  RESUME param {} differs: previous {!r}, this run {!r}".format(k, old.get(k),
                                                                                    params[k]))
            sys.stderr.write("resume: parameters differ from {}\n".format(f))
            sys.exit(2)
        n = 0
        path = rl.find_file(f, rels, "rerun_real.csv")
        for r in csv.DictReader(open(path, newline="")):
            if r["end"] != "ok":
                continue
            if r["tid"] in done:
                sys.stderr.write("resume: task {} complete in {} and {}\n".format(r["tid"], done[r["tid"]], f))
                sys.exit(2)
            done[r["tid"]] = f
            n += 1
        print("  resume: read {}  completed tasks {}".format(f, n))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--precheck", action="store_true")
    ap.add_argument("--schedule", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--calprec2", default="")
    ap.add_argument("--plan-from", default="")
    ap.add_argument("--timing-from", action="append", default=[])
    ap.add_argument("--rows", default=",".join(rl.ROWS))
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--stop-after", type=float, default=STOP_AFTER_DEFAULT)
    ap.add_argument("--resume-from", default="")
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    a.timing_from = [f for x in a.timing_from for f in x.split(",") if f]

    mode = ("precheck" if a.precheck else "schedule" if a.schedule else
            "smoke" if a.smoke else "run")
    print("=" * 96)
    print("CBO-GAP rerun -- fixed-beta rerun, trajectories (mode {})".format(mode))
    print("=" * 96)
    hs = script_hashes()
    for k, v in sorted(hs.items()):
        print("  {:<18} {}".format(k, v))
    print("  python   {}   numpy {}".format(platform.python_version(), np.__version__))
    print("  platform {}".format(platform.platform()))
    print("  workers  {}".format(a.workers))
    print("  threads  " + "  ".join("{}={}".format(v, os.environ.get(v)) for v in THREAD_VARS))
    print("  archive  {}".format(rl.ARCH))
    print("  outroot  {}".format(OUTROOT))
    print("  DT {}  LAM {}  sigma (non-r rows) {}  J_inf default {}".format(rl.DT, rl.LAM,
                                                                           rl.SIGMA_ISO, rl.JINF))
    print("  seeds    SeedSequence(key), key = (ENTROPY {}, kind, owner row, module, objective, d,"
          " law, tau0e6, re6, sigma_design e6, beta_design e6, J_inf, Te6, arm, sub-arm, rep);"
          " kind {} trajectory, {} bootstrap, {} smoke".format(rl.ENTROPY, rl.KIND_TRAJ, rl.KIND_BOOT,
                                                               rl.KIND_SMOKE))
    print("  budget   {:.0f} MB peak RSS per worker".format(RSS_BUDGET_MB))

    if mode == "precheck":
        precheck(a)

    if not a.plan_from:
        sys.stderr.write("--plan-from is required outside --precheck\n")
        sys.exit(2)
    if not check_p1() or not check_s1():
        sys.stderr.write("P1 or S1 failed\n")
        sys.exit(2)
    pparams, cells, plan_sha = load_plan(a.plan_from)
    print("\n  plan     {}  rerun_plan.csv sha256 {}".format(a.plan_from, plan_sha))
    for k in ("rerunlib_sha256", "costprobe2_sha256"):
        if pparams.get(k) != hs[k]:
            sys.stderr.write("plan was built with a different {} ({} vs {})\n".format(
                k, pparams.get(k), hs[k]))
            sys.exit(2)
    rows = parse_rows(a.rows)
    print("  rows     {}".format(",".join(rows)))

    if mode == "smoke":
        by_mod = {}
        for t in tasks_for(cells, rows, rl.KIND_SMOKE):
            if t["rep"] != 0:
                continue
            m = t["cell"]["module"]
            sz = t["cell"]["d"] * (t["cell"]["jinf"] + sum(rl.jlist_of(t["cell"]))) * rl.K_of(t["cell"])
            if m not in by_mod or (sz, t["tid"]) < by_mod[m][0]:
                by_mod[m] = ((sz, t["tid"]), t)
        tasks = []
        for m in sorted(by_mod):
            t = by_mod[m][1]
            for member in ("a", "b"):
                tt = dict(t)
                tt["tid"] = t["tid"] + "|" + member
                tasks.append(tt)
        outdir = new_outdir("rerun-smoke")
        params = dict(hs)
        params.update({"mode": "smoke", "plan_sha256": plan_sha, "rows": ",".join(rows),
                       "workers": a.workers, "env": ENV})
        write_rows(os.path.join(outdir, "rerun_params.csv"), ["name", "value"],
                   [[k, v] for k, v in sorted(params.items())])
        done, _, _ = run_pool(tasks, max(2, a.workers), os.path.join(outdir, "rerun_real.csv"),
                              1e18, "D-SMOKE", fresh=True)
        hdr("D-SMOKE  bitwise comparison of the two members")
        ok = True
        by = {}
        for r in done:
            by.setdefault(r["tid"].rsplit("|", 1)[0], []).append(r)
        for base, rs in sorted(by.items()):
            ecols = ["E_{}".format(J) for J in rl.JCOLS]
            same = (len(rs) == 2 and all(r["end"] == "ok" for r in rs) and
                    [rs[0][e] for e in ecols] == [rs[1][e] for e in ecols])
            ok = ok and same
            print("  {}  {}".format(base, "identical" if same else "DIFFER or errored"))
        print("  D-SMOKE {}".format("PASS" if ok else "FAIL"))
        print("\n  files {}".format(outdir))
        sys.exit(0 if ok else 3)

    tasks = tasks_for(cells, rows)
    print("  tasks    {} (groups owned by these rows x diffusions x reps)".format(len(tasks)))
    if a.timing_from:
        walls = load_walls(a.timing_from)
        load = assign_shards(tasks, walls, a.nshards)
        hdr("SHARDS  {} shard(s), {} worker(s); {}".format(a.nshards, a.workers, SCHED_LABEL))
        for i, ld in enumerate(load):
            n = sum(1 for t in tasks if t["shard"] == i)
            print("  shard {:>2}: {:>6} tasks  summed wall {:>10.0f} s  estimate {:>8.0f} s at {} workers".format(
                i, n, ld, ld / a.workers, a.workers))
    elif a.nshards > 1 or mode == "schedule":
        sys.stderr.write("--timing-from is required with --nshards > 1 and with --schedule\n")
        sys.exit(2)
    else:
        for t in tasks:
            t["shard"] = 0
    if mode == "schedule":
        print("\n  --schedule: nothing run, nothing written.")
        sys.exit(0)
    if not (0 <= a.shard < a.nshards):
        sys.stderr.write("--shard out of range\n")
        sys.exit(2)
    mine = [t for t in tasks if t["shard"] == a.shard]

    params = dict(hs)
    params.update({"mode": "run", "plan_sha256": plan_sha, "rows": ",".join(rows),
                   "shard": a.shard, "nshards": a.nshards, "workers": a.workers,
                   "stop_after": a.stop_after, "env": ENV,
                   "timing_from": ";".join(sorted(os.path.basename(f.rstrip("/"))
                                                  for f in a.timing_from))})
    skipped = {}
    if a.resume_from:
        hdr("RESUME (CLAUDE.md rule 17)")
        skipped = resume_done([f for f in a.resume_from.split(",") if f], params)
    todo = [t for t in mine if t["tid"] not in skipped]
    print("  this shard: {} tasks, {} already complete, {} to run".format(len(mine),
                                                                       len(mine) - len(todo), len(todo)))
    tag = "-s{}of{}".format(a.shard, a.nshards) if a.nshards > 1 else ""
    outdir = new_outdir("rerun" + tag)
    write_rows(os.path.join(outdir, "rerun_params.csv"), ["name", "value"],
               [[k, v] for k, v in sorted(params.items())] +
               [["resume_from", ";".join(a.resume_from.split(","))]])
    print("  run dir  {}".format(outdir))
    done, stopped, notrun = run_pool(todo, a.workers, os.path.join(outdir, "rerun_real.csv"),
                                     a.stop_after, "TRAJECTORIES")

    hdr("SUMMARY")
    nerr = sum(1 for r in done if r["end"] != "ok")
    nover = sum(1 for r in done if r["end"] == "ok" and float(r["peak_rss_mb"]) > RSS_BUDGET_MB)
    nf1 = sum(1 for r in done if r["F1"] == "F1 FAILED")
    naud = sum(1 for r in done if r["F1"] == "ok")
    rss = [float(r["peak_rss_mb"]) for r in done if r["end"] == "ok"]
    print("  completed {}  errors {}  not started {}".format(len(done) - nerr, nerr, notrun))
    print("  peak RSS max {:.1f} MB; OVER BUDGET {}".format(max(rss) if rss else float("nan"), nover))
    print("  F1: {} ok, {} FAILED".format(naud, nf1))
    code = 0
    if nerr or nover:
        code = 4
    if nf1:
        code = 3
    if stopped:
        code = 5
        print("  G-STOP: resume with --resume-from {}".format(outdir))
    print("\n  files {}   exit {}".format(outdir, code))
    sys.exit(code)


if __name__ == "__main__":
    main()
