"""
c5_nfcheck.py  --  CBO-GAP: two checks on the C5 readings' null rates
(ledger N45, C5 READINGS; Rahul's instruction 2026-11-25). Written
2026-11-25, AFTER the readings were recorded. It re-makes no verdict.

LAPTOP. Reads only; WRITES NOTHING. Every number it prints is a reading of
a committed log or of c5_analysis.py's own synthetic null fixture.

WHAT IT DOES, IN PLAIN LANGUAGE
-------------------------------
Part T counts, from the committed C5 readings log, how the 288 cells fall
on the two one-sided criteria R1b and R1c, so that R1b's count is read
against the cells that were free to fire it. Part N runs c5_analysis.py's
null fixture twice, at the 400 cells per level the verdicts were read
against and at a larger number, and prints how far the largest of the four
per-level rates (the rule's r) sits above their mean at each size. That
gap is the inflation the max-of-four rule adds to r. Nothing here changes
r, a verdict, or any recorded reading: the verdicts keep the NF 400 rates
of 2026-11-01 (c5_analysis.py refuses any other NF outside --null-only).

INPUTS (each committed and unmodified against HEAD, checked with git;
exit 2 otherwise)
  --readings-log  default logs/c5-analysis-a0py-20261125.log, the log the
                  N45 C5 READINGS were copied from.
  --null-log      default logs/c5-analysis-null-20261101.log, the
                  2026-11-01 null-only run whose rates the readings use.
  scripts/c5_analysis.py is imported; its null_cell, null_fixture, LEVELS,
  B, NF and seeds are used unchanged (no retyped statistic).

PART T  R1b AGAINST R1c, FROM THE READINGS LOG
  Lines read: those between the "PER CELL" heading and the next "POOLED"
  heading that start "  CONC-X " or "  TAU8-X " and contain " | ". Fields
  by " | ": 4 is the PERSISTS (R1b) verdict, 5 the "ub<=-1" (R1c) verdict.
  Each must read "yes" or "no", optionally followed by " (null rate x)";
  anything else (e.g. "not used") is exit 2. The cell is field 0 up to
  the class word.
  T1  exactly 288 such lines, 288 distinct cells; otherwise exit 2.
  T2  the yes counts equal the log's own HEADLINE COUNTS lines ("R1b
      observed N", "R1c observed N"); otherwise exit 3.
  T3  no cell fires both. By construction: R1b fires iff m - t se > -1
      and R1c iff m + t se <= -1, with t > 0 and se >= 0, so m - t se <=
      m + t se and both cannot hold. A cell firing both is exit 3 (a
      parsing or code error, never a finding).
  Printed: the 2 x 2 table (R1b yes/no by R1c yes/no), the number firing
  neither, and the number not firing R1c (the cells that could have fired
  R1b). Worked example: 288 cells, R1b 5, R1c 47, none both: neither 236,
  not R1c 241. (Illustrative arithmetic on the recorded totals; the
  printed figures are what counts.)
  NULL RATE (T1 to T3): deterministic parsing and counting; none fires by
  chance (probability 0).

PART N  THE MAX-OF-FOUR INFLATION, AT TWO FIXTURE SIZES
  N0  c5_analysis.null_fixture at NF 400, printed as c5_analysis.py
      prints it. R0 (pre-specified): its lines from the "NULL FIXTURE"
      heading to the "NULL RATE P-ref" line equal, string for string, the
      same span of BOTH committed logs. PASS: the NF 400 rates below are
      the recorded ones. FAIL: every line that differs is printed, Part N
      is still printed, and the run ends exit 3; no NF 400 figure from it
      may be recorded.
  N1  the same fixture at --nf-big cells per level (default 12000).
      Why 12000: the per-level rate's Monte Carlo SE is sqrt(p (1 - p) /
      NF), 0.0109 at p 0.05 and NF 400, so the max of four such rates
      sits above their mean by about one SE from noise alone, the same
      size as the excesses over 0.05 that put R1b to D-ref in the "rate
      printed" band. At NF 12000 the per-cell SE is 0.0020 (a 5.5-fold
      cut), and the pooled rules, measured on NF / 6 groups (2000 groups,
      SE 0.0049 at 0.05, against 0.027 on 66 groups at NF 400), drop
      below 0.005 as well; 12000 is a multiple of 6, so no cell is left
      out of a pooled group. The seeds are keyed by (level, cell), so
      cells 0 to 399 of N1 are the cells of N0: N1 contains N0 and the
      two are not independent.
  For each criterion k (R1b, R1c, R1d, D-ref, P-win, P-ref, and the four
  bootstrap versions, printed only) and each NF:
      the four per-level rates (unrounded; the logs print 3 decimals),
      max  = the largest of the four (the rule's r at that NF),
      mean = their arithmetic mean,
      excess = max - mean  (the inflation, as Rahul defined it),
      SE   = sqrt(mean (1 - mean) / n), n = NF, or the pooled group count.
  Worked example: rates 0.0675, 0.0600, 0.0575, 0.0375: max 0.0675, mean
  0.0556, excess 0.0119, SE at n 400 0.0115.
  READING (fixed now): excess is the inflation at that NF. It holds two
  parts that this script does not separate: the selection of the largest
  of four noisy rates (shrinks as 1 / sqrt(NF)) and any real difference
  between the four noise levels (does not shrink). The NF 12000 excess is
  mostly the second. No "used / NOT USED" status is printed for NF 12000:
  the rule's status is the NF 400 one, recorded in N45, and stays.
  NULL RATE (N): R0 is deterministic (string equality); excess and the
  rates are descriptions, not tests, and decide nothing.

EXIT CODES  0 printed, R0 PASS and T1 to T3 PASS; 2 an input problem;
  3 R0 FAIL or T2 or T3 FAIL (everything is still printed where possible).

HOW TO RUN (repository root)
    python -B scripts/c5_nfcheck.py --workers 4
Python 3.8 to 3.13, NumPy only; git is called to check the logs are
committed and unmodified.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import re                                                       # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import c5_analysis as A                                         # noqa: E402

say, hdr, Stop, JP = A.say, A.hdr, A.Stop, A.JP
ROOT = A.ROOT
NF_BIG = 12000
DEFAULT_READINGS = "logs/c5-analysis-a0py-20261125.log"
DEFAULT_NULL = "logs/c5-analysis-null-20261101.log"
VERD = re.compile(r"^(yes|no)( \(null rate [0-9.]+\))?$")
SPAN_START = "NULL FIXTURE  synthetic cells"
SPAN_END = "  NULL RATE P-ref"


class Tee(object):
    def __init__(self, real):
        self.real, self.buf = real, []

    def write(self, s):
        self.real.write(s)
        self.buf.append(s)

    def flush(self):
        self.real.flush()

    def lines(self):
        return "".join(self.buf).split("\n")


def read_log(rel):
    why = A._committed_unmodified(rel)
    if why:
        raise Stop(2, why)
    with open(os.path.join(ROOT, rel)) as f:
        return f.read().split("\n")


def span(lines, where):
    i = [k for k, s in enumerate(lines) if s.startswith(SPAN_START)]
    if len(i) != 1:
        raise Stop(2, "{}: {} '{}' headings, expected 1".format(where, len(i), SPAN_START))
    j = [k for k in range(i[0], len(lines)) if lines[k].startswith(SPAN_END)]
    if not j:
        raise Stop(2, "{}: no '{}' line after the fixture heading".format(where, SPAN_END.strip()))
    return lines[i[0]:j[0] + 1]


def parse_cell(line):
    """(cell, R1b, R1c) or (None, reason)."""
    f = line.split(" | ")
    if len(f) < 9:
        return None, "fewer than 9 fields: " + line[:80]
    head = f[0].split()
    if len(head) < 3:
        return None, "cell field unreadable: " + line[:80]
    out = []
    for k in (4, 5):
        m = VERD.match(f[k].strip())
        if not m:
            return None, "verdict field {} reads {!r}".format(k, f[k].strip())
        out.append(m.group(1) == "yes")
    return (head[0] + " " + head[1], out[0], out[1]), None


def part_t(lines, workers):
    hdr("PART T  R1b against R1c, per cell, from the readings log")
    a = [k for k, s in enumerate(lines) if s.startswith("PER CELL")]
    if len(a) != 1:
        raise Stop(2, "readings log: {} PER CELL headings, expected 1".format(len(a)))
    b = [k for k in range(a[0], len(lines)) if lines[k].startswith("POOLED")]
    if not b:
        raise Stop(2, "readings log: no POOLED heading after PER CELL")
    cl = [s for s in lines[a[0]:b[0]] if (s.startswith("  CONC-X ") or s.startswith("  TAU8-X ")) and " | " in s]
    pool_ = multiprocessing.Pool(workers)
    try:
        got = pool_.map(parse_cell, cl, chunksize=16)
    finally:
        pool_.close()
        pool_.join()
    bad = [w for (c, w) in got if c is None]
    if bad:
        raise Stop(2, "readings log: {} unreadable cell lines; first: {}".format(len(bad), bad[0]))
    cells = [c for (c, _w) in got]
    names = set(c[0] for c in cells)
    say("  cell lines read {}   distinct cells {}".format(len(cells), len(names)))
    if len(cells) != 288 or len(names) != 288:
        raise Stop(2, "T1 FAIL: expected 288 lines and 288 distinct cells")
    say("  T1 PASS")
    tab = {}
    for _n, b1, c1 in cells:
        tab[(b1, c1)] = tab.get((b1, c1), 0) + 1
    nb = sum(1 for c in cells if c[1])
    nc = sum(1 for c in cells if c[2])
    head = {}
    for s in lines:
        m = re.match(r"^  (R1b|R1c)\s+observed\s+(\d+)\s", s)
        if m:
            head.setdefault(m.group(1), []).append(int(m.group(2)))
    ok = True
    for k, n in (("R1b", nb), ("R1c", nc)):
        h = head.get(k, [])
        if len(h) != 1 or h[0] != n:
            say("  T2 FAIL {}: per-cell yes count {}, HEADLINE COUNTS line(s) {}".format(k, n, h))
            ok = False
    if ok:
        say("  T2 PASS  per-cell yes counts equal the HEADLINE COUNTS lines: R1b {}, R1c {}".format(nb, nc))
    both = tab.get((True, True), 0)
    if both:
        say("  T3 FAIL  {} cells fire both R1b and R1c (impossible by construction: a parsing or code "
            "error)".format(both))
        ok = False
    else:
        say("  T3 PASS  no cell fires both")
    say("")
    say("                   R1c yes   R1c no    total")
    say("  R1b yes (PERSISTS) {:>6}   {:>6}   {:>6}".format(tab.get((True, True), 0), tab.get((True, False), 0), nb))
    say("  R1b no             {:>6}   {:>6}   {:>6}".format(tab.get((False, True), 0), tab.get((False, False), 0),
                                                            len(cells) - nb))
    say("  total              {:>6}   {:>6}   {:>6}".format(nc, len(cells) - nc, len(cells)))
    say("")
    say("  fired neither R1b nor R1c: {} of {}".format(tab.get((False, False), 0), len(cells)))
    say("  did not fire R1c (the cells that could have fired R1b): {} of {}".format(len(cells) - nc, len(cells)))
    return ok


def summary(res):
    hdr("PART N  max-of-four inflation: per-level rates, max (the rule's r), mean, excess = max - mean")
    say("  rates unrounded (the logs print 3 decimals); SE = sqrt(mean (1 - mean) / n), n = cells per level, or")
    say("  pooled groups per level for P-win and P-ref; no status is given for any NF but 400 (the verdicts')")
    for nf, (rates, groups) in res:
        say("")
        say("  NF {}  ({} pooled groups per level)".format(nf, groups))
        say("  {:<7} {:>8} {:>8} {:>8} {:>8} | {:>8} {:>8} {:>8} | {:>7}".format(
            "crit", "level 1", "level 2", "level 3", "level 4", "max", "mean", "excess", "SE"))
        for k in A.CRITS + A.POOLS + A.BOOTS:
            v = rates[k]
            mx, mn = max(v), sum(v) / 4.0
            n = groups if k in A.POOLS else nf
            say("  {:<7} {} | {:>8.4f} {:>8.4f} {:>8.4f} | {:>7.4f}{}".format(
                k, " ".join("{:>8.4f}".format(x) for x in v), mx, mn, mx - mn, math.sqrt(mn * (1 - mn) / n),
                "   (bootstrap: printed only)" if k in A.BOOTS else ""))
    say("")
    say("  SIDE BY SIDE  excess = max - mean")
    (n0, (r0, _g0)), (n1, (r1, _g1)) = res
    say("  {:<7} {:>12} {:>12} {:>12} | {:>12} {:>12} {:>12}".format(
        "crit", "max NF " + str(n0), "mean", "excess", "max NF " + str(n1), "mean", "excess"))
    for k in A.CRITS + A.POOLS:
        a0, a1 = r0[k], r1[k]
        say("  {:<7} {:>12.4f} {:>12.4f} {:>12.4f} | {:>12.4f} {:>12.4f} {:>12.4f}".format(
            k, max(a0), sum(a0) / 4.0, max(a0) - sum(a0) / 4.0, max(a1), sum(a1) / 4.0, max(a1) - sum(a1) / 4.0))


def main():
    ap = argparse.ArgumentParser(description="C5 null-rate checks (writes nothing)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--nf-big", type=int, default=NF_BIG)
    ap.add_argument("--readings-log", default=DEFAULT_READINGS)
    ap.add_argument("--null-log", default=DEFAULT_NULL)
    a = ap.parse_args()
    if a.workers < 1 or a.nf_big <= A.NF or a.nf_big % 6:
        raise Stop(2, "--workers at least 1; --nf-big above {} and a multiple of 6".format(A.NF))
    hdr("CBO-GAP c5_nfcheck  (ledger N45, after the C5 READINGS; re-makes no verdict)  --  reads only, writes nothing")
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    say("  script   sha256 {}".format(JP.sha256_of(os.path.abspath(__file__))))
    say("  c5_analysis.py sha256 {}".format(JP.sha256_of(A.__file__)))
    say("  readings log {}   null log {}".format(a.readings_log, a.null_log))
    say("  B {}  levels {}  NF {} and {}  seeds SeedSequence({} + (level, cell, set))".format(
        A.B, A.LEVELS, A.NF, a.nf_big, A.NULL_SEED))
    rl_lines = read_log(a.readings_log)
    nl_lines = read_log(a.null_log)
    ref = {a.readings_log: span(rl_lines, a.readings_log), a.null_log: span(nl_lines, a.null_log)}
    ok_t = part_t(rl_lines, a.workers)

    hdr("PART N, N0  the fixture at NF {} (as c5_analysis.py prints it)".format(A.NF))
    tee = Tee(sys.stdout)
    sys.stdout = tee
    try:
        _u, r0, g0 = A.null_fixture(a.workers, A.NF)
    finally:
        sys.stdout = tee.real
    mine = span(tee.lines(), "this run")
    ok_r = True
    for where, lines in sorted(ref.items()):
        diff = [(i, x, y) for i, (x, y) in enumerate(zip(mine, lines)) if x != y]
        if len(mine) != len(lines) or diff:
            ok_r = False
            say("  R0 FAIL against {}: {} lines here, {} there, {} differing".format(where, len(mine), len(lines),
                                                                                      len(diff)))
            for i, x, y in diff:
                say("    line {}: here  {!r}".format(i, x))
                say("    line {}: there {!r}".format(i, y))
        else:
            say("  R0 PASS against {}: {} lines identical".format(where, len(mine)))

    hdr("PART N, N1  the fixture at NF {} (no status: the verdicts keep the NF {} status)".format(a.nf_big, A.NF))
    _u, r1, g1 = A.null_fixture(a.workers, a.nf_big, False)
    summary([(A.NF, (r0, g0)), (a.nf_big, (r1, g1))])
    code = 0 if (ok_t and ok_r) else 3
    hdr("c5_nfcheck.py done, exit {}  (T {}, R0 {}; nothing written)".format(
        code, "PASS" if ok_t else "FAIL", "PASS" if ok_r else "FAIL"))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
