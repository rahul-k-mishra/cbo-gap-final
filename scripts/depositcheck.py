"""
depositcheck.py  --  CBO-GAP: do the published counts of Tables 4 and 5 and
Sections 7.10 and 7.11 follow from the deposited files?

WHAT THIS IS
------------
Ledger N8. The deposited text (zenodo-v1/sn-article.tex, line 309) says every
reported interval is a 4000-resample value from one archived re-analysis
script. The deposited code sets other resample counts. This script asks a
narrower question, one per table or section: do the published numbers follow
from the deposited files, at the resample counts the deposited code sets?

  Table 4 (tab:control)    tallied from control_summary.csv
  Table 5 (tab:boundary)   tallied from boundary_summary.csv
  Section 7.10 (sec:sigma) counts tallied from sigma_summary.csv;
                           coefficients from audit.py, block A2
  Section 7.11 (sec:aniso) equivalence counts from audit.py, block A3

It does not recompute any bootstrap of the generating scripts. The deposit has
no per-realization data for these experiments (ledger ARC2): the summary files
hold each cell's interval as the generating script computed it. A tally can
show that the published counts follow from those stored intervals; it cannot
show the intervals themselves are right.

audit.py is run as deposited, unchanged, in a child process whose working
directory is the archive, because it reads its inputs from its working
directory by relative name. It writes nothing (checked before it runs, P3).

WRITES NOTHING. Every file is opened for reading only. No output folder.

RULES FIXED BEFORE THE FIRST EXECUTION (2026-10-30; Rahul's instruction)
  R0  No setting is searched. Every quantity is computed one way, the way
      stated here. A count that does not reproduce is reported with both
      numbers. That is the finding, not a problem to fix.
  R1  PUBLISHED VALUES are parsed from the deposited tex by the patterns in
      PUBLISHED_PATTERNS, never typed into this script. A pattern that does
      not match exactly once is exit 2.
  R2  MATCH RULE for a decimal (the n30_reconstruct.py R3 rule). A value x
      reproduces a published value p printed with k decimals iff
      |x - p| <= 0.5 x 10^-k + 1e-12. Worked example: p "-1.0017" allows
      [-1.00175, -1.00165]; x -1.00172 reproduces, -1.00176 does not.
      Where the comparison value is itself audit.py's printed output with
      more decimals than p (A2 coefficient, A3 gap, 4 against 3), the rule
      is applied to the printed value. Example: audit prints -0.0473, p
      "-0.047": |diff| 0.0003 <= 0.0005, reproduces. An interval endpoint
      that audit.py prints with 3 decimals, like p, must be equal as a
      3-decimal string.
      Integer counts must be equal.
  R3  TABLE 4. For each published row (arm, tau0): the 18 rows of
      control_summary.csv with that arm and tau. Mean of slope (np.mean),
      by R2. Counts of the verdict column, which control.py line 378
      writes: "recovered" is the table's rate-consistent, "UNDECIDED" its
      undecided, "NOT observed" its not. Any other verdict string, or a
      row count other than 18, is exit 2. The row reproduces iff all five
      numbers do; the table iff all four rows do.
      Example: 18 cells, slopes averaging -1.00168, verdicts 17 recovered, 1
      UNDECIDED, 0 NOT observed, against "-1.0017, 17, 1, 0": reproduces.
  R4  TABLE 5. For each published tau0 row: the 18 rows of
      boundary_summary.csv with that tau. Mean of slope, and SD with ddof 1,
      the convention boundary.py's own P5.4 printout uses (line 454),
      each by R2. Rate-consistent at 0.15: count of verdict "recovered"
      (boundary.py line 334, THRESH -0.85). The "all" row: 0.15 as the sum
      of verdict "recovered" over 144 cells; 0.10 and 0.20 as the count of
      ci_hi <= -1.0 + tol, the expression of sigma.py P8.3 and audit.py
      A6, on the stored ci_hi. The caption's point-estimate count: slope
      <= -1.0 + 0.15. Also printed, for information and without a verdict:
      the ci_hi rule at 0.15, beside the verdict column (the stored ci_hi
      is rounded to 6 decimals; the verdict used the unrounded value).
      Example: tau0 0.07, 18 cells, mean -0.99128, SD 0.07322, 16 recovered,
      against "-0.9913, 0.0732, 16": reproduces.
  R5  SECTION 7.10 COUNTS. Per diffusion, the 144 rows of
      sigma_summary.csv: counts of ci_hi <= -1.0 + tol for tol 0.10, 0.15,
      0.20, and of bonf_hi <= -1.0 + 0.15 (sigma.py P8.3, lines 434 to 441).
      "Bonferroni costs c cells" is read as c = count(0.15) - count(bonf).
      Example: isotropic 71, 93, 115, Bonferroni 82: cost 11.
  R6  SECTION 7.10 COEFFICIENTS (audit.py A2). The text gives two
      coefficients with intervals, isotropic d 10, at the two tau0 it names;
      each against audit's line for (isotropic, 10, tau0) by R2. And three
      verdict claims: all six anisotropic lines and both isotropic d 5
      lines say "no effect of size 0.10 detected"; both isotropic d 10
      lines say "effect of practical size possible". The isotropic d 40
      lines are printed; the text says nothing about them, so no verdict.
      The section's coefficient part reproduces iff all five items do.
  R7  SECTION 7.11 (audit.py A3, arm A). The text's "18 cells" are the
      matched-sigma arm A of crossed.py (docstring: ARM A, matched sigma;
      3 levels x 3 d x 2 tau0 = 18 lines). Counts of A3's verdicts:
      "EQUIVALENT at margin" is equivalent, "inconclusive" inconclusive,
      "DIFFERENT beyond margin" outside. The section reproduces iff the
      three counts equal the text's.
      The six gaps the text quotes per (d, tau0) name no sigma level. They
      are printed against A3's arm-A gap at each of the three levels, with
      the levels at which R2 holds, and are NOT part of the verdict: a
      number that does not say which of three cells it is cannot be
      reproduced, only located.
  R8  PLATFORM. The tallies of R3 to R5 involve no random draw. A2 and A3
      resample with numpy.random.default_rng(11) in a fixed order; their
      intervals depend on that Generator's stream on the NumPy that runs
      them. The original audit run's NumPy is not recorded anywhere. A
      difference in an A2 or A3 interval therefore says: not reproduced on
      this NumPy. It is printed that way.

CHECKS BEFORE ANYTHING IS READ (each failure is exit 2)
  P1  Every file of zenodo-v1.sha256 (68) hashes to its manifest value.
  P2  Each published pattern matches the deposited tex exactly once.
  P3  audit.py writes nothing: no open() call in it has a mode argument,
      and no write, savefig or to_csv call appears in it.
  P4  The resample counts are read from the deposited source, not typed:
      N_BOOT of control.py, boundary.py, sigma.py, crossed.py and audit.py,
      and the range() literal of audit.r_regression (A2).

EXIT CODES
  0  The check ran to the end; every verdict is printed, whether the
     numbers reproduce or not.
  2  Bad argument, manifest mismatch, a published pattern not found once,
     an unexpected input row or column, or audit.py could write.
  3  audit.py exited non-zero, or did not finish within --audit-timeout.
  4  audit.py ran but its A2 or A3 block did not have the expected lines
     (12 and 36).

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python scripts/depositcheck.py --workers 2
"""

import argparse
import ast
import csv
import hashlib
import io
import multiprocessing
import os
import platform
import re
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TOLS = (0.10, 0.15, 0.20)

T4_VERDICTS = {"recovered": "rate-consistent", "UNDECIDED": "undecided", "NOT observed": "not"}
T5_VERDICTS = ("recovered", "UNDECIDED", "NOT observed")
A3_VERDICTS = {"EQUIVALENT at margin": "equivalent", "inconclusive": "inconclusive",
               "DIFFERENT beyond margin": "outside"}

# R1: published values come from these patterns over the deposited tex.
# Each is searched inside the span that starts at the label named.
PUBLISHED_PATTERNS = {
    "t4_rows": ("\\label{tab:control}",
                r"^(fixed|adaptive) & \$(0\.\d+)\$ & \$(-?\d\.\d{4})\$ & \$(\d+)\$ & \$(\d+)\$ & \$(\d+)\$\\\\$",
                4),
    "t5_rows": ("\\label{tab:boundary}",
                r"^\$(0\.\d\d)\$ & \$(-?\d\.\d{4})\$ & \$(\d\.\d{4})\$ & \$(\d+)\$ & --- \\\\$",
                8),
    "t5_all": ("\\label{tab:boundary}",
               r"^all & --- & --- & \$(\d+)/(\d+)\$ & \$(\d+)/(\d+)\$ / \$(\d+)/(\d+)\$\\\\$",
               1),
    "t5_point": ("\\caption{Eight concentration targets",
                 r"the point-estimate rule would give \$(\d+)/(\d+)\$ at \$\\delta=0\.15\$",
                 1),
    "s710_coef": ("\\label{sec:sigma}",
                  r"where the coefficients are \$(-?\d\.\d{3})\\;\[(-?\d\.\d{3}),(-?\d\.\d{3})\]\$ at "
                  r"\$\\tau_0=(0\.\d+)\$ and \$(-?\d\.\d{3})\\;\[(-?\d\.\d{3}),(-?\d\.\d{3})\]\$ at "
                  r"\$\\tau_0=(0\.\d+)\$",
                  1),
    "s710_claim": ("\\label{sec:sigma}",
                   r"exclude an effect of size \$0\.10\$ in all six anisotropic cells and in the two "
                   r"isotropic cells at \$d=5\$, but not at \$d=10\$",
                   1),
    "s710_counts": ("\\label{sec:sigma}",
                    r"isotropic \$(\d+)/(\d+)/(\d+)\$ of \$(\d+)\$ at tolerances \$0\.10/0\.15/0\.20\$, "
                    r"anisotropic \$(\d+)/(\d+)/(\d+)\$; Bonferroni at \$0\.15\$ costs \$(\d+)\$ and "
                    r"\$(\d+)\$ cells",
                    1),
    "s711_gaps": ("\\label{sec:aniso}",
                  r"gap is \$([+-]\d\.\d{3})\$, \$([+-]\d\.\d{3})\$, \$([+-]\d\.\d{3})\$ at \$d=5,10,40\$ "
                  r"for \$\\tau_0=0\.1\$ and \$([+-]\d\.\d{3})\$, \$([+-]\d\.\d{3})\$, \$([+-]\d\.\d{3})\$ "
                  r"for \$\\tau_0=0\.01\$",
                  1),
    "s711_counts": ("\\label{sec:aniso}",
                    r"declares \$(\d+)\$ of the \$(\d+)\$ cells equivalent, leaves \$(\d+)\$ inconclusive, "
                    r"and classifies \$(\d+)\$ as lying outside",
                    1),
}
SPAN_END = {"\\label{tab:control}": "\\end{tabular}", "\\label{tab:boundary}": "\\end{tabular}",
            "\\caption{Eight concentration targets": "\\end{tabular}",
            "\\label{sec:sigma}": "\\subsection", "\\label{sec:aniso}": "\\subsection"}

A2_LINE = re.compile(r"^\s+(isotropic|anisotropic)\s+(\d+)\s+(\S+)\s+(-?\d+\.\d{4})\s+"
                     r"\[([+-]\d+\.\d{3}),([+-]\d+\.\d{3})\]\s+"
                     r"(no effect of size 0\.10 detected|effect of practical size possible)\s*$")
A3_LINE = re.compile(r"^\s+([AB])\s+(\S+)\s+(\d+)\s+(\S+)\s+(-?\d+\.\d{4})\s+"
                     r"\[([+-]\d+\.\d{3}),([+-]\d+\.\d{3})\]\s+"
                     r"(EQUIVALENT at margin|DIFFERENT beyond margin|inconclusive)\s*$")


class Stop(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, code, msg)
        self.code = code
        self.msg = msg


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "=" * 92)
    say(s)
    say("=" * 92)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return path, h.hexdigest()


def ndec(s):
    return len(s.split(".")[1]) if "." in s else 0


def r2_match(x, p):
    """R2: x reproduces the published string p."""
    return abs(float(x) - float(p)) <= 0.5 * 10 ** (-ndec(p)) + 1e-12


def yn(b):
    return "reproduces" if b else "DOES NOT REPRODUCE"


# ----------------------------------------------------------------------
# readers (each classifies every row; anything unexpected is a Stop(2))
# ----------------------------------------------------------------------

def read_csv(archive, name, need):
    path = os.path.join(archive, name)
    with io.open(path, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise Stop(2, "{}: no rows".format(name))
    miss = [c for c in need if c not in rows[0]]
    if miss:
        raise Stop(2, "{}: missing column(s) {}".format(name, ", ".join(miss)))
    return rows


def fnum(name, r, k):
    try:
        return float(r[k])
    except (TypeError, ValueError):
        raise Stop(2, "{}: non-numeric {} {!r}".format(name, k, r.get(k)))


def tally_t4(archive, published):
    name = "control_summary.csv"
    rows = read_csv(archive, name, ("arm", "tau", "slope", "verdict"))
    for r in rows:
        if r["verdict"] not in T4_VERDICTS:
            raise Stop(2, "{}: unknown verdict {!r}".format(name, r["verdict"]))
        if r["arm"] not in ("fixed", "adaptive"):
            raise Stop(2, "{}: unknown arm {!r}".format(name, r["arm"]))
    out = []
    for arm, tau, mean_p, rc_p, und_p, not_p in published:
        sub = [r for r in rows if r["arm"] == arm and float(r["tau"]) == float(tau)]
        if len(sub) != 18:
            raise Stop(2, "{}: {} rows for arm {} tau {}, expected 18".format(name, len(sub), arm, tau))
        mean = float(np.mean([fnum(name, r, "slope") for r in sub]))
        cnt = dict((v, sum(1 for r in sub if T4_VERDICTS[r["verdict"]] == v))
                   for v in ("rate-consistent", "undecided", "not"))
        out.append({"arm": arm, "tau": tau, "n": len(sub), "mean": mean, "mean_p": mean_p,
                    "cnt": cnt, "cnt_p": {"rate-consistent": int(rc_p), "undecided": int(und_p),
                                          "not": int(not_p)}})
    return out


def tally_t5(archive, published_rows):
    name = "boundary_summary.csv"
    rows = read_csv(archive, name, ("tau", "slope", "ci_hi", "verdict"))
    for r in rows:
        if r["verdict"] not in T5_VERDICTS:
            raise Stop(2, "{}: unknown verdict {!r}".format(name, r["verdict"]))
    if len(rows) != 144:
        raise Stop(2, "{}: {} rows, expected 144".format(name, len(rows)))
    per = []
    for tau, mean_p, sd_p, rc_p in published_rows:
        sub = [r for r in rows if float(r["tau"]) == float(tau)]
        if len(sub) != 18:
            raise Stop(2, "{}: {} rows for tau {}, expected 18".format(name, len(sub), tau))
        s = np.array([fnum(name, r, "slope") for r in sub])
        per.append({"tau": tau, "n": len(sub), "mean": float(np.mean(s)),
                    "sd": float(np.std(s, ddof=1)), "rc": sum(1 for r in sub if r["verdict"] == "recovered"),
                    "mean_p": mean_p, "sd_p": sd_p, "rc_p": int(rc_p)})
    his = np.array([fnum(name, r, "ci_hi") for r in rows])
    slopes = np.array([fnum(name, r, "slope") for r in rows])
    allrow = {"n": len(rows),
              "rc015_verdict": sum(1 for r in rows if r["verdict"] == "recovered"),
              "ci": dict((t, int((his <= -1.0 + t).sum())) for t in TOLS),
              "point015": int((slopes <= -1.0 + 0.15).sum())}
    return {"per": per, "all": allrow}


def tally_s710(archive):
    name = "sigma_summary.csv"
    rows = read_csv(archive, name, ("diffusion", "ci_hi", "bonf_hi"))
    out = {}
    for r in rows:
        if r["diffusion"] not in ("isotropic", "anisotropic"):
            raise Stop(2, "{}: unknown diffusion {!r}".format(name, r["diffusion"]))
    for diff in ("isotropic", "anisotropic"):
        sub = [r for r in rows if r["diffusion"] == diff]
        his = np.array([fnum(name, r, "ci_hi") for r in sub])
        bhs = np.array([fnum(name, r, "bonf_hi") for r in sub])
        cnt = dict((t, int((his <= -1.0 + t).sum())) for t in TOLS)
        nb = int((bhs <= -1.0 + 0.15).sum())
        out[diff] = {"n": len(sub), "cnt": cnt, "bonf": nb, "cost": cnt[0.15] - nb}
    return out


def run_audit(archive, timeout):
    cmd = [sys.executable, "-I", "-B", "-X", "utf8", "audit.py"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=archive, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"rc": None, "out": "", "err": "timeout after {} s".format(timeout), "wall": time.time() - t0,
                "cmd": " ".join(cmd)}
    return {"rc": p.returncode, "out": p.stdout.decode("utf-8", "replace"),
            "err": p.stderr.decode("utf-8", "replace"), "wall": time.time() - t0, "cmd": " ".join(cmd)}


def job(args):
    kind = args[0]
    try:
        if kind == "t4":
            return kind, tally_t4(args[1], args[2])
        if kind == "t5":
            return kind, tally_t5(args[1], args[2])
        if kind == "s710":
            return kind, tally_s710(args[1])
        if kind == "audit":
            return kind, run_audit(args[1], args[2])
    except Stop as e:
        return kind, e
    raise ValueError(kind)


# ----------------------------------------------------------------------
# P1 to P4
# ----------------------------------------------------------------------

def check_manifest(pool, archive, manifest):
    want = {}
    with io.open(manifest, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split(None, 1)
            if len(parts) != 2:
                raise Stop(2, "P1: manifest line not 'hash  name': {!r}".format(ln))
            want[parts[1].lstrip("*")] = parts[0].lower()
    paths = [os.path.join(archive, n) for n in sorted(want)]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise Stop(2, "P1: {} manifest file(s) missing, e.g. {}".format(len(missing), missing[0]))
    bad = [p for p, h in pool.map(sha256_of, paths) if h != want[os.path.relpath(p, archive)]]
    if bad:
        raise Stop(2, "P1: {} file(s) differ from the manifest, e.g. {}".format(len(bad), bad[0]))
    return len(paths)


def published(tex):
    got = {}
    for key, (start, pat, nwant) in PUBLISHED_PATTERNS.items():
        i = tex.find(start)
        if i < 0 or tex.find(start, i + 1) >= 0:
            raise Stop(2, "P2 {}: anchor {!r} not found exactly once".format(key, start))
        j = tex.find(SPAN_END[start], i + len(start))
        span = tex[i:j if j > 0 else len(tex)]
        ms = list(re.finditer(pat, span, re.M))
        if len(ms) != nwant:
            raise Stop(2, "P2 {}: pattern matched {} time(s), expected {}".format(key, len(ms), nwant))
        got[key] = [m.groups() for m in ms]
    return got


def audit_source_checks(archive):
    path = os.path.join(archive, "audit.py")
    with io.open(path, "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else "")
            if nm == "open" and (len(node.args) > 1 or node.keywords):
                raise Stop(2, "P3: audit.py line {}: open() with a mode".format(node.lineno))
            if nm in ("write", "writelines", "savefig", "to_csv", "writerow", "writerows"):
                raise Stop(2, "P3: audit.py line {}: {}() call".format(node.lineno, nm))
    funcs = dict((n.name, n) for n in tree.body if isinstance(n, ast.FunctionDef))
    for fname in ("r_regression", "equivalence"):
        if fname not in funcs:
            raise Stop(2, "P4: audit.py has no function {}".format(fname))

    def range_arg(fn):
        vals = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range" \
                    and len(node.args) == 1:
                a = node.args[0]
                if isinstance(a, ast.Constant) and isinstance(a.value, int):
                    vals.append(str(a.value))
                elif isinstance(a, ast.Name):
                    vals.append(a.id)
        return vals
    return src, range_arg(funcs["r_regression"]), range_arg(funcs["equivalence"])


def nboot_of(archive, name):
    with io.open(os.path.join(archive, name), "r", encoding="utf-8") as f:
        m = re.findall(r"^N_BOOT\s*=\s*(\d+)\s*$", f.read(), re.M)
    if len(m) != 1:
        raise Stop(2, "P4: {}: N_BOOT assignment found {} time(s)".format(name, len(m)))
    return int(m[0])


# ----------------------------------------------------------------------
# audit output parsing
# ----------------------------------------------------------------------

def parse_audit(out):
    blk, a2, a3 = None, [], []
    for ln in out.splitlines():
        m = re.match(r"^(A\d) ", ln)
        if m:
            blk = m.group(1)
            continue
        if blk == "A2":
            m = A2_LINE.match(ln)
            if m:
                g = m.groups()
                a2.append({"diff": g[0], "d": int(g[1]), "tau": float(g[2]), "coef": g[3],
                           "lo": g[4], "hi": g[5], "verdict": g[6], "line": ln.strip()})
        elif blk == "A3":
            m = A3_LINE.match(ln)
            if m:
                g = m.groups()
                a3.append({"arm": g[0], "level": float(g[1]), "d": int(g[2]), "tau": float(g[3]),
                           "gap": g[4], "lo": g[5], "hi": g[6], "verdict": g[7], "line": ln.strip()})
    if len(a2) != 12 or len(a3) != 36 or sum(1 for x in a3 if x["arm"] == "A") != 18:
        raise Stop(4, "audit.py output: {} A2 line(s) (expected 12), {} A3 line(s) (expected 36, "
                      "18 of arm A)".format(len(a2), len(a3)))
    return a2, a3


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="deposit check for Tables 4, 5 and Sections 7.10, 7.11 (N8)")
    ap.add_argument("--archive", default=os.path.join(REPO, "zenodo-v1"))
    ap.add_argument("--manifest", default=os.path.join(REPO, "zenodo-v1.sha256"))
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--audit-timeout", type=int, default=3600)
    a = ap.parse_args()
    if a.workers < 1:
        raise Stop(2, "--workers must be at least 1")
    archive = os.path.abspath(a.archive)
    if not os.path.isfile(os.path.join(archive, "audit.py")):
        raise Stop(2, "--archive {}: no audit.py there".format(archive))
    if not os.path.isfile(a.manifest):
        raise Stop(2, "--manifest {}: not found".format(a.manifest))

    hdr("depositcheck.py  (ledger N8)  --  writes nothing")
    say("  script sha256   {}".format(sha256_of(os.path.abspath(__file__))[1]))
    say("  archive         {}".format(archive))
    say("  manifest        {}".format(os.path.abspath(a.manifest)))
    say("  workers         {}".format(a.workers))
    say("  audit timeout   {} s".format(a.audit_timeout))
    say("  python          {}".format(sys.version.split()[0]))
    say("  numpy           {}".format(np.__version__))
    say("  platform        {}".format(platform.platform()))
    say("  seeds           none drawn by this script; audit.py draws from its own"
        " numpy.random.default_rng(11)")
    say("  tolerances      {}".format(", ".join("{:.2f}".format(t) for t in TOLS)))
    say("  match rule      |x - p| <= 0.5 x 10^-k + 1e-12, k = decimals printed in p (R2)")

    hdr("What this checks, in plain words")
    for s in (
        "The deposited paper reports cell means and verdict counts in Tables 4 and 5, and",
        "counts, coefficients and equivalence verdicts in Sections 7.10 and 7.11. Line 309",
        "says every interval behind them is a 4000-resample value from one re-analysis",
        "script. The deposited code says otherwise: the generating scripts store each cell's",
        "interval in a summary file at their own resample count, and audit.py computes the",
        "regression and equivalence intervals at its own counts. Those counts are printed",
        "below, read from the code.",
        "",
        "For each table and section, this asks: if you take the deposited files and the",
        "deposited code exactly as they are, do you get the numbers printed in the paper?",
        "",
        "For Tables 4 and 5 and the Section 7.10 counts, the answer needs no random draw: it",
        "is a count of the stored per-cell verdicts or interval ends. A match shows the",
        "published counts follow from the stored intervals. It does not show the stored",
        "intervals are right; the deposit has no per-realization data to redo them.",
        "",
        "For the Section 7.10 coefficients and the Section 7.11 equivalence counts, audit.py is",
        "run unchanged. Its intervals depend on how this NumPy draws random numbers; a mismatch",
        "means 'not reproduced on this NumPy', not more than that.",
        "",
        "Where a number does not reproduce, both numbers are printed. Nothing is tuned to match.",
    ):
        say("  " + s)

    pool = multiprocessing.Pool(processes=a.workers)
    try:
        hdr("P1 to P4  checks before anything is read")
        n = check_manifest(pool, archive, a.manifest)
        say("  P1  {} files hash to {}: PASS".format(n, os.path.basename(a.manifest)))
        with io.open(os.path.join(archive, "sn-article.tex"), "r", encoding="utf-8") as f:
            tex = f.read()
        pub = published(tex)
        say("  P2  {} published patterns each found in the deposited tex as expected: PASS".format(len(pub)))
        _, a2_range, a3_range = audit_source_checks(archive)
        say("  P3  audit.py has no write call and no open() with a mode: PASS")
        nb = dict((m, nboot_of(archive, m + ".py")) for m in ("control", "boundary", "sigma", "crossed", "audit"))
        a3_n = [str(nb["audit"]) if v == "N_BOOT" else v for v in a3_range]
        say("  P4  resample counts set by the deposited code:")
        say("      Table 4         control.py   N_BOOT = {} (per-cell intervals in control_summary.csv)".format(nb["control"]))
        say("      Table 5         boundary.py  N_BOOT = {} (per-cell intervals in boundary_summary.csv)".format(nb["boundary"]))
        say("      7.10 counts     sigma.py     N_BOOT = {} (per-cell intervals in sigma_summary.csv)".format(nb["sigma"]))
        say("      7.10 coeffs     audit.py A2  range({}) in r_regression".format(", ".join(a2_range) or "none found"))
        say("      7.11 counts     audit.py A3  range({}) in equivalence, N_BOOT = {}".format(
            ", ".join(a3_range) or "none found", nb["audit"]))
        say("      (crossed.py N_BOOT = {} sets crossed_summary.csv's intervals; A3 uses only its slopes)".format(nb["crossed"]))

        t4_pub = [(g[0], g[1], g[2], g[3], g[4], g[5]) for g in pub["t4_rows"]]
        t5_pub = [(g[0], g[1], g[2], g[3]) for g in pub["t5_rows"]]
        jobs = [("audit", archive, a.audit_timeout), ("t4", archive, t4_pub), ("t5", archive, t5_pub),
                ("s710", archive)]
        res = dict(pool.map(job, jobs, chunksize=1))
    finally:
        pool.close()
        pool.join()
    for k in ("t4", "t5", "s710"):
        if isinstance(res[k], Stop):
            raise res[k]
    aud = res["audit"]
    if aud["rc"] != 0:
        say("\n  audit.py stderr:\n" + aud["err"])
        raise Stop(3, "audit.py: {}".format("exit {}".format(aud["rc"]) if aud["rc"] is not None else aud["err"]))
    a2, a3 = parse_audit(aud["out"])

    final = []

    # ---------------- Table 4
    hdr("Table 4 (tab:control, tex 403 to 413)  against control_summary.csv  [R3]")
    ok4 = True
    for r in res["t4"]:
        okm = r2_match(r["mean"], r["mean_p"])
        okc = all(r["cnt"][k] == r["cnt_p"][k] for k in r["cnt"])
        ok4 = ok4 and okm and okc
        say("  {:<8} tau0 {:<5} n {}  mean published {}  deposited {:+.5f}  {}".format(
            r["arm"], r["tau"], r["n"], r["mean_p"], r["mean"], yn(okm)))
        for k in ("rate-consistent", "undecided", "not"):
            say("      {:<16} published {:>3}  deposited {:>3}  {}".format(
                k, r["cnt_p"][k], r["cnt"][k], yn(r["cnt"][k] == r["cnt_p"][k])))
    final.append(("Table 4", ok4, "control.py, {} resamples".format(nb["control"])))

    # ---------------- Table 5
    hdr("Table 5 (tab:boundary, tex 420 to 438)  against boundary_summary.csv  [R4]")
    ok5 = True
    for r in res["t5"]["per"]:
        okm, oks, okr = r2_match(r["mean"], r["mean_p"]), r2_match(r["sd"], r["sd_p"]), r["rc"] == r["rc_p"]
        ok5 = ok5 and okm and oks and okr
        say("  tau0 {:<5} n {}  mean {} / {:+.5f} {}   sd {} / {:.5f} {}   rate-consistent at 0.15 {} / {} {}".format(
            r["tau"], r["n"], r["mean_p"], r["mean"], yn(okm), r["sd_p"], r["sd"], yn(oks),
            r["rc_p"], r["rc"], yn(okr)))
    say("  (each pair is published / deposited)")
    al = res["t5"]["all"]
    g = pub["t5_all"][0]
    pa = [(int(g[0]), int(g[1])), (int(g[2]), int(g[3])), (int(g[4]), int(g[5]))]
    gp = pub["t5_point"][0]
    rows_all = [("all, rate-consistent at 0.15 (verdict column)", pa[0], al["rc015_verdict"]),
                ("all, at 0.10 (ci_hi <= -0.90)", pa[1], al["ci"][0.10]),
                ("all, at 0.20 (ci_hi <= -0.80)", pa[2], al["ci"][0.20]),
                ("caption, point-estimate rule at 0.15", (int(gp[0]), int(gp[1])), al["point015"])]
    for lab, (pn, pd), dv in rows_all:
        okx = pn == dv and pd == al["n"]
        ok5 = ok5 and okx
        say("  {:<46} published {}/{}  deposited {}/{}  {}".format(lab, pn, pd, dv, al["n"], yn(okx)))
    say("  information only: ci_hi <= -0.85 gives {}/{}, beside the verdict column's {}/{}".format(
        al["ci"][0.15], al["n"], al["rc015_verdict"], al["n"]))
    final.append(("Table 5", ok5, "boundary.py, {} resamples".format(nb["boundary"])))

    # ---------------- 7.10 counts
    hdr("Section 7.10 counts (sec:sigma, tex 491)  against sigma_summary.csv  [R5]")
    g = [int(x) for x in pub["s710_counts"][0]]
    pubc = {"isotropic": (g[0], g[1], g[2], g[3], g[7]), "anisotropic": (g[4], g[5], g[6], g[3], g[8])}
    okc = True
    for diff in ("isotropic", "anisotropic"):
        s = res["s710"][diff]
        p = pubc[diff]
        dep = (s["cnt"][0.10], s["cnt"][0.15], s["cnt"][0.20])
        okd = dep == p[:3] and s["n"] == p[3] and s["cost"] == p[4]
        okc = okc and okd
        say("  {:<12} n {}  at 0.10/0.15/0.20 published {}/{}/{}  deposited {}/{}/{}   "
            "Bonferroni cost published {}  deposited {} ({} - {})   {}".format(
                diff, s["n"], p[0], p[1], p[2], dep[0], dep[1], dep[2], p[4], s["cost"],
                s["cnt"][0.15], s["bonf"], yn(okd)))
    final.append(("Section 7.10 counts", okc, "sigma.py, {} resamples".format(nb["sigma"])))

    # ---------------- 7.10 coefficients
    hdr("Section 7.10 coefficients (sec:sigma, tex 487)  against audit.py A2  [R6]")
    say("  audit.py A2 lines, verbatim:")
    for x in a2:
        say("    " + x["line"])
    g = pub["s710_coef"][0]
    okk = True
    for coef_p, lo_p, hi_p, tau_p in ((g[0], g[1], g[2], g[3]), (g[4], g[5], g[6], g[7])):
        x = [y for y in a2 if y["diff"] == "isotropic" and y["d"] == 10 and y["tau"] == float(tau_p)]
        if len(x) != 1:
            raise Stop(4, "audit.py A2: no single line for isotropic d 10 tau {}".format(tau_p))
        x = x[0]
        okx = r2_match(x["coef"], coef_p)
        oki = x["lo"] == "{:+.3f}".format(float(lo_p)) and x["hi"] == "{:+.3f}".format(float(hi_p))
        okk = okk and okx and oki
        say("  isotropic d 10 tau0 {:<5} coefficient published {} audit {} {};  interval published [{}, {}] "
            "audit [{}, {}] {}".format(tau_p, coef_p, x["coef"], yn(okx), lo_p, hi_p, x["lo"], x["hi"], yn(oki)))
    claims = [("all six anisotropic", lambda y: y["diff"] == "anisotropic", "no effect of size 0.10 detected", 6),
              ("both isotropic d 5", lambda y: y["diff"] == "isotropic" and y["d"] == 5,
               "no effect of size 0.10 detected", 2),
              ("both isotropic d 10", lambda y: y["diff"] == "isotropic" and y["d"] == 10,
               "effect of practical size possible", 2)]
    for lab, sel, want, nwant in claims:
        xs = [y for y in a2 if sel(y)]
        hit = sum(1 for y in xs if y["verdict"] == want)
        okx = len(xs) == nwant and hit == nwant
        okk = okk and okx
        say("  claim: {} say '{}': {} of {} lines do  {}".format(lab, want, hit, len(xs), yn(okx)))
    for y in a2:
        if y["diff"] == "isotropic" and y["d"] == 40:
            say("  isotropic d 40 tau0 {:g}: '{}' (the text says nothing about this cell; no verdict)".format(
                y["tau"], y["verdict"]))
    final.append(("Section 7.10 coefficients", okk, "audit.py A2, {} resamples, NumPy {}".format(
        ", ".join(a2_range), np.__version__)))

    # ---------------- 7.11
    hdr("Section 7.11 (sec:aniso, tex 497)  against audit.py A3, arm A  [R7]")
    say("  audit.py A3 lines, verbatim (arm A is matched sigma; arm B is matched r):")
    for x in a3:
        say("    " + x["line"])
    g = [int(v) for v in pub["s711_counts"][0]]
    armA = [x for x in a3 if x["arm"] == "A"]
    dep = dict((v, sum(1 for x in armA if A3_VERDICTS[x["verdict"]] == v))
               for v in ("equivalent", "inconclusive", "outside"))
    ok11 = g[1] == len(armA) and dep["equivalent"] == g[0] and dep["inconclusive"] == g[2] \
        and dep["outside"] == g[3]
    say("  arm A cells published {}  audit {}".format(g[1], len(armA)))
    for k, pv in (("equivalent", g[0]), ("inconclusive", g[2]), ("outside", g[3])):
        say("  {:<13} published {:>3}  audit {:>3}  {}".format(k, pv, dep[k], yn(dep[k] == pv)))
    gp = pub["s711_gaps"][0]
    say("  The six gaps quoted per (d, tau0) name no sigma level. Located only, no verdict (R7):")
    for (d, tau), p in zip(((5, 0.1), (10, 0.1), (40, 0.1), (5, 0.01), (10, 0.01), (40, 0.01)), gp):
        xs = sorted([x for x in armA if x["d"] == d and x["tau"] == tau], key=lambda x: x["level"])
        at = [x for x in xs if r2_match(x["gap"], p)]
        say("    d {:<3} tau0 {:<5} published {}  audit by level: {}  ->  {}".format(
            d, tau, p, ", ".join("{:g}: {}".format(x["level"], x["gap"]) for x in xs),
            ("within R2 at level " + ", ".join("{:g}".format(x["level"]) for x in at)) if at
            else "within R2 at no level"))
    final.append(("Section 7.11 counts", ok11, "audit.py A3, {} resamples, NumPy {}".format(
        ", ".join(a3_n), np.__version__)))

    # ---------------- summary
    hdr("SUMMARY  (per table and section; published counts against the deposited files)")
    for lab, ok, how in final:
        say("  {:<28} {:<20} at the deposited code's setting: {}".format(lab, yn(ok), how))
    say("\n  Platform note (R8): Tables 4, 5 and the 7.10 counts involve no random draw. The 7.10")
    say("  coefficients and the 7.11 counts come from audit.py's resampling on NumPy {};".format(np.__version__))
    say("  the NumPy of the original audit run is not recorded.")

    hdr("Appendix: audit.py stdout, verbatim ({}; wall {:.1f} s; exit 0)".format(aud["cmd"], aud["wall"]))
    say(aud["out"].rstrip("\n"))
    if aud["err"].strip():
        say("\n  audit.py stderr (exit 0):\n" + aud["err"].rstrip("\n"))
    hdr("depositcheck.py done, exit 0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
