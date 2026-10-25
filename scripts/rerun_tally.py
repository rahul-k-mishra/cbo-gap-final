"""
rerun_tally.py  --  CBO-GAP round 2: verdict counts from a rerun_analysis folder

WHAT THIS DOES, IN PLAIN LANGUAGE
---------------------------------
rerun_analysis.py prints one verdict per cell and per statistic but no count
of them (the audit counts and the J4 counts are the only exceptions). This
script reads the CSV files of one rerun-analysis folder and prints how many
rows carry each verdict, grouped as stated below. It computes no statistic,
refits nothing, resamples nothing and changes no verdict. It WRITES NOTHING:
every output is printed, and the console log is the record (CLAUDE.md
rule 3, analysis-only script).

INPUT CHECK, BEFORE ANY COUNT
  V1  Every file listed in <folder>/sha256.txt must hash as listed, and the
      five files read below must all be listed. Otherwise exit 2 and no
      count is printed.
      Worked example: analysis_cells.csv hashes to a value other than its
      line in sha256.txt: "V1 FAILED analysis_cells.csv", exit 2.

PARSING A CELL LABEL (analysis_cells.csv, column "cell")
  The label is "|"-separated: row, module, objective, then fields. A field
  "dN" is the dimension N; "key=value" is that key (tau, r, sigma_design,
  beta_design); "JinfN" is J_inf; "TN" is the horizon; a last field fixed,
  adaptive, armA or armB is the arm. Nothing else is inferred.
  Worked example: "ONSET|regimemap|ackley|d40|centred|tau=0.1|r=0.75|
  Jinf50000|T1.0" gives objective ackley, d 40, law centred, tau 0.1,
  r 0.75, J_inf 50000, T 1.0, no arm.

REGION (rows whose cells carry r): the string after "r=" is read as an exact
  fraction. r < 1: "admissible"; r = 1: "boundary"; r > 1: "outside". Cells
  without r (ANISO arm A carries sigma_design instead) get "no r".
  Worked example: r=0.99 admissible; r=1.0 boundary; r=1.1 outside;
  ANISO ...|sigma_design=0.4|...|armA: no r.

COUNTS PRINTED (no threshold, no criterion beyond the verdict strings
rerun_analysis.py wrote; every count is printed with its denominator)
  C1  Rate verdict, analysis_cells.csv, window W-full only: the number of
      cell-arm rows whose upper_bound_le_minus1 is "yes", "no" or anything
      else, per row and diffusion, and per row, diffusion and the row's
      stratum (STRATUM below). The verdict reads "the one-sided 95% upper
      bound of the S-slope is at most -1". A cell whose true slope is
      exactly -1 gets "no" about 95% of the time, so a count of "no" is not
      a count of cells without the rate.
      Worked example: TAU8, none, tau 0.1: yes 4 no 14 of 18 (illustrative).
  C2  Region, rows SIGMA, ANISO, RMAP, CLIFF, ONSET: C1's counts per row,
      diffusion and region.
  C3  Cell quality, analysis_cells.csv, every window: rows whose M is not
      "n of n", whose nonfinite is not "0 of B", or whose flag is not empty.
      Worked example: M "11 of 12" counts once under "M below full".
  C4  Statistic verdicts, analysis_stats.csv: for each (row, quantity,
      level, window), the number of rows with each verdict string
      ("DIFFERENCE", "95% interval contains 0", "sensitivity, no verdict",
      "no finite interval"). Quantity is the column as written.
      Worked example: CONC, "c1 dimension d40-d2", unit, W-full:
      DIFFERENCE 20  95% interval contains 0 16  of 36 (illustrative).
  C5  Equivalence, analysis_stats.csv, quantity starting "c3", level unit,
      window W-full: counts of each equivalence string per row, and per row
      and dimension for SIGMA and ANISO (dimension read from the group
      column's "d=N").
      Worked example: ANISO d=5: EQUIVALENT 10, not established 2, not
      attainable 0 of 12 (illustrative).
  C6  Reference adequacy, analysis_adequacy.csv: counts per (module,
      label, adequacy) with adequacy cut at its first "(" and stripped.
      Worked example: "beta, not adequate (C5m 0.057 > 0.05)" is counted
      as "not adequate" under label beta.
  C7  Audit floor, analysis_audit.csv: per row, rows with floor_flag not
      empty, of all rows.

STRATUM per row for C1 (the coordinate the round-1 text counted over):
  BETA-ISO, BETA-ANI: beta_design; LAWPANEL: law; CONC, PROBEARM, TAU8,
  GEOM, SYNTH, NAMED: tau; ADAPT: (arm, tau); REFSIZE: Jinf; HORIZON: T;
  SIGMA: (d, tau); ANISO: (arm, d, tau); RMAP: (d, tau); CLIFF: (d, r);
  ONSET: (d, r).

HOW TO RUN (repository root, venv active)
    python scripts/rerun_tally.py --analysis runs/rerun-analysis-<stamp> --workers 2
  Exit codes: 0 counts printed; 2 V1 failed or a file is missing.

NumPy only (imported for its version line). Python 3.8 to 3.11 syntax.
"""

import argparse
import csv
import hashlib
import multiprocessing
import os
import platform
import sys
from fractions import Fraction

import numpy as np

FILES = ["analysis_cells.csv", "analysis_stats.csv", "analysis_adequacy.csv",
         "analysis_audit.csv", "analysis_params.csv"]
REGION_ROWS = ["SIGMA", "ANISO", "RMAP", "CLIFF", "ONSET"]
STRATUM = {
    "BETA-ISO": ("beta_design",), "BETA-ANI": ("beta_design",), "LAWPANEL": ("law",),
    "CONC": ("tau",), "PROBEARM": ("tau",), "TAU8": ("tau",), "GEOM": ("tau",),
    "SYNTH": ("tau",), "NAMED": ("tau",), "ADAPT": ("arm", "tau"), "REFSIZE": ("jinf",),
    "HORIZON": ("T",), "SIGMA": ("d", "tau"), "ANISO": ("arm", "d", "tau"),
    "RMAP": ("d", "tau"), "CLIFF": ("d", "r"), "ONSET": ("d", "r"),
}
ARMS = ("fixed", "adaptive", "armA", "armB")


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "-" * 100)
    say(s)
    say("-" * 100)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def verify(folder):
    listed = {}
    for line in open(os.path.join(folder, "sha256.txt")):
        line = line.strip()
        if not line:
            continue
        h, name = line.split(None, 1)
        listed[name.strip()] = h
    bad = []
    for name, h in sorted(listed.items()):
        p = os.path.join(folder, name)
        if not os.path.exists(p) or sha(p) != h:
            bad.append(name)
    missing = [f for f in FILES if f not in listed]
    return listed, bad, missing


def parse_cell(label):
    parts = label.split("|")
    out = {"objective": parts[2] if len(parts) > 2 else "", "arm": "", "law": ""}
    for f in parts[3:]:
        if "=" in f:
            k, v = f.split("=", 1)
            out[k] = v
        elif f in ARMS:
            out["arm"] = f
        elif f.startswith("Jinf") and f[4:].isdigit():
            out["jinf"] = f[4:]
        elif f.startswith("T") and f[1:].replace(".", "", 1).isdigit():
            out["T"] = f[1:]
        elif f.startswith("d") and f[1:].isdigit():
            out["d"] = f[1:]
        elif f in ("centred", "offset", "mix-0.1", "mix-0.01"):
            out["law"] = f
    return out


def region(p):
    if "r" not in p:
        return "no r"
    r = Fraction(p["r"])
    if r < 1:
        return "admissible"
    if r == 1:
        return "boundary"
    return "outside"


def add(dct, key, val):
    dct.setdefault(key, {})
    dct[key][val] = dct[key].get(val, 0) + 1


def task(a):
    name, path = a
    res = {"name": name}
    rows = list(csv.DictReader(open(path, newline="")))
    res["n"] = len(rows)
    if name == "analysis_cells.csv":
        c1, c1s, c2, c3 = {}, {}, {}, {}
        for r in rows:
            p = parse_cell(r["cell"])
            if r["window"] == "W-full":
                v = r["upper_bound_le_minus1"]
                v = v if v in ("yes", "no") else "other: " + v
                add(c1, (r["row"], r["diffusion"]), v)
                st = tuple("{}={}".format(k, p.get(k, "")) for k in STRATUM.get(r["row"], ()))
                add(c1s, (r["row"], r["diffusion"]) + st, v)
                if r["row"] in REGION_ROWS:
                    add(c2, (r["row"], r["diffusion"], region(p)), v)
            m = r["M"].split(" of ")
            q = []
            if len(m) != 2 or m[0] != m[1]:
                q.append("M below full")
            if not r["nonfinite"].startswith("0 of "):
                q.append("nonfinite above 0")
            if r["flag"]:
                q.append("flag not empty")
            for x in q:
                add(c3, (r["row"], r["window"]), x)
            add(c3, (r["row"], r["window"]), "rows")
        res.update({"c1": c1, "c1s": c1s, "c2": c2, "c3": c3})
    elif name == "analysis_stats.csv":
        c4, c5 = {}, {}
        for r in rows:
            add(c4, (r["row"], r["quantity"], r["level"], r["window"]), r["verdict"])
            if r["quantity"].startswith("c3") and r["level"] == "unit" and r["window"] == "W-full":
                e = r["equivalence"] or "(none)"
                add(c5, (r["row"], "all d"), e)
                if r["row"] in ("SIGMA", "ANISO"):
                    dd = [t for t in r["group"].split() if t.startswith("d=")]
                    add(c5, (r["row"], dd[0] if dd else "d?"), e)
        res.update({"c4": c4, "c5": c5})
    elif name == "analysis_adequacy.csv":
        c6 = {}
        for r in rows:
            ad = r["adequacy"].split("(")[0].strip().rstrip(",").strip()
            add(c6, (r["module"], r["label"]), ad)
        res["c6"] = c6
    elif name == "analysis_audit.csv":
        c7 = {}
        for r in rows:
            add(c7, (r["row"],), "floor" if r["floor_flag"] else "no floor flag")
            add(c7, (r["row"],), "rows")
        res["c7"] = c7
    return res


def show(dct, width=60):
    for k in sorted(dct):
        tot = sum(v for kk, v in dct[k].items() if kk != "rows")
        if "rows" in dct[k]:
            tot = dct[k]["rows"]
        parts = ["{} {}".format(kk, dct[k][kk]) for kk in sorted(dct[k]) if kk != "rows"]
        say("  {:<{w}} {}   of {}".format("  ".join(str(x) for x in k), "  ".join(parts), tot,
                                          w=width))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()

    say("=" * 100)
    say("CBO-GAP rerun_tally -- verdict counts from one rerun_analysis folder (writes nothing)")
    say("=" * 100)
    say("  rerun_tally sha256 {}".format(sha(os.path.abspath(__file__))))
    say("  python {}   numpy {}   platform {}   workers {}".format(
        platform.python_version(), np.__version__, platform.platform(), a.workers))
    say("  analysis folder {}".format(a.analysis))
    say("  no seeds, no resampling, no trajectories; counts only")

    hdr("V1  manifest")
    listed, bad, missing = verify(a.analysis)
    for name in sorted(listed):
        say("  {:<28} {}".format(name, "FAILED" if name in bad else "ok"))
    if bad or missing:
        for f in missing:
            say("  {} not listed in sha256.txt".format(f))
        say("  V1 FAILED. No count printed. Exit 2.")
        sys.exit(2)
    for row in csv.reader(open(os.path.join(a.analysis, "analysis_params.csv"), newline="")):
        say("  params  {}".format("  ".join(row)))

    jobs = [(f, os.path.join(a.analysis, f)) for f in FILES if f != "analysis_params.csv"]
    pool = multiprocessing.Pool(processes=a.workers)
    try:
        out = dict((r["name"], r) for r in pool.map(task, jobs, chunksize=1))
    finally:
        pool.close()
        pool.join()
    for f in sorted(out):
        say("  read {:<26} rows {}".format(f, out[f]["n"]))

    cells, stats = out["analysis_cells.csv"], out["analysis_stats.csv"]
    hdr("C1  rate verdict 'upper bound <= -1', W-full, per row and diffusion")
    say("  ('no' is expected about 95% of the time for a cell whose slope is exactly -1)")
    show(cells["c1"], 30)
    hdr("C1  rate verdict, W-full, per row, diffusion and stratum")
    show(cells["c1s"], 60)
    hdr("C2  rate verdict, W-full, per row, diffusion and region (r<1 admissible, r=1 boundary, r>1 outside)")
    show(cells["c2"], 40)
    hdr("C3  cell quality, every window")
    show(cells["c3"], 30)
    hdr("C4  statistic verdicts per (row, quantity, level, window)")
    show(stats["c4"], 72)
    hdr("C5  equivalence, c3 per unit, W-full")
    show(stats["c5"], 24)
    hdr("C6  reference adequacy per (module, label)")
    show(out["analysis_adequacy.csv"]["c6"], 30)
    hdr("C7  audit floor flags per row")
    show(out["analysis_audit.csv"]["c7"], 12)
    say("\n  done; nothing written")
    sys.exit(0)


if __name__ == "__main__":
    main()
