"""
c5_headline_nf.py  --  CBO-GAP: the C5 headline counts read against the
NF 12000 null rates, beside the recorded NF 400 ones (ledger N45, C5
NULL-RATE CHECKS; Rahul's instruction 2026-11-26). Written 2026-11-26,
AFTER the C5 READINGS and after logs/c5-nfcheck-20261125.log. It re-makes
no verdict.

LAPTOP. Reads only; WRITES NOTHING. Every number it prints is a reading of
a committed log or of c5_analysis.py's own synthetic null fixture.

WHAT IT DOES, IN PLAIN LANGUAGE
-------------------------------
The C5 headline counts (how many of the 288 cells fired R1b, R1c, R1d and
D-ref) were compared with the number expected by chance, 288 x r, and a
binomial upper tail, where r is the largest of four per-level false
rejection rates measured on 400 synthetic null cells per level.
c5_nfcheck.py measured the same rates on 12000 cells per level and found
the NF 400 r sitting above the NF 12000 rates. This script prints the
expected count and the upper tail again with the NF 12000 rates, next to
the recorded NF 400 figures, and says which way each moved. The recorded
verdicts, counts, rates and comparison are not changed: c5_analysis.py
still refuses any NF but 400 for a verdict, and nothing here has a
used / NOT USED status.

INPUTS (each committed and unmodified against HEAD, checked with git;
exit 2 otherwise)
  --readings-log  default logs/c5-analysis-a0py-20261125.log, the log the
                  N45 C5 READINGS were copied from. Its HEADLINE COUNTS
                  lines give the observed counts and the recorded figures.
  --nfcheck-log   default logs/c5-nfcheck-20261125.log, the log whose
                  "NF 400" and "NF 12000" tables this run must reproduce.
  scripts/c5_analysis.py is imported: null_fixture, binom_tail, CRITS, NF
  unchanged (no retyped statistic); scripts/c5_nfcheck.py is imported for
  its log reader and fixture span.

WHAT IS COMPUTED
  n = the cell count in the readings log's HEADLINE COUNTS heading ("288
  cells"); obs_k = the "observed" figure of criterion k's headline line.
  For each k in R1b, R1c, R1d, D-ref and each of three rates:
    A  r400  = max of the four NF 400 per-level rates (the recorded r);
    B  r12   = max of the four NF 12000 per-level rates (the same rule,
               the larger fixture);
    C  m12   = mean of the four NF 12000 per-level rates;
  expected = n x rate and tail = binom_tail(n, rate, obs_k) = P(X >= obs_k)
  for X ~ Binomial(n, rate), c5_analysis.binom_tail unchanged. Expected is
  printed to 2 decimals, the tail to 4 significant figures, and line A
  also in c5_analysis.py's own format.
  B is the like-for-like replacement (the rule unchanged, NF changed); C
  is printed because the NF 12000 mean, not the max, is the figure free of
  the max-of-four selection. Neither has a status; neither decides
  anything.

CHECKS (pre-specified; all deterministic)
  H1  the readings log has one HEADLINE COUNTS heading giving n, and one
      headline line per criterion; otherwise exit 2.
  H2  line A, printed in c5_analysis.py's format, equals the log's
      headline line for that criterion, string for string (trailing
      spaces stripped). PASS: the recomputation reproduces the recorded
      figures, so B and C differ from A only in the rate. FAIL: both
      strings printed, exit 3, nothing from this run may be recorded.
  R0  the NF 400 fixture span equals the readings log's span (as
      c5_nfcheck.py's R0).
  R2  for each criterion and each NF (400 and 12000), the four per-level
      rates, max and mean, formatted to 4 decimals, equal the same row of
      the nfcheck log's table for that NF. FAIL: exit 3 (the fixture did
      not reproduce; nothing may be recorded).
  M1  binom_tail(n, p, x) is nondecreasing in p (the binomial family is
      stochastically increasing in p). So, for each k and each of B, C:
      rate below r400 implies tail at or below A's tail; rate above r400
      implies tail at or above. A violation is exit 3: a code error,
      never a finding.

DIRECTION, PRINTED PER CRITERION (rule fixed now)
  For B and for C, against A:
    expected  "falls" if n x rate < n x r400, "rises" if above, else
              "unchanged";
    tail      "falls" / "rises" / "unchanged" likewise, compared as floats;
    position  "observed above expected" if obs > expected, "observed
              below expected" if obs < expected, "observed equals
              expected" otherwise; printed for A, B and C.
  Worked example (illustrative arithmetic, not a project figure): n 288,
  obs 10, r400 0.07, rate 0.05: expected 20.16 falls to 14.40; the tail
  falls (M1); position "observed below expected" at both rates.
  WHAT "conservative" MEANS HERE (fixed now). By M1 a larger rate gives a
  larger upper tail for every criterion, so an inflated r makes an
  "observed above chance" reading harder to reach: conservative for a
  criterion whose recorded reading is an excess (observed above
  expected). The recorded reading for a criterion whose count fell below
  expected was the description "fewer than the number expected by
  chance"; there an inflated r inflates the expected count and so
  enlarges the shortfall: not conservative for that description. The
  script prints the position and the directions; which reading applied to
  which criterion is the ledger's, copied from the N45 C5 READINGS.

NULL RATE: H1, H2, R0, R2 and M1 are deterministic (string equality,
  parsing, a monotone function); none fires by chance (probability 0). No
  line of this script is a test: B and C's expected counts and tails are
  descriptions beside the recorded ones and fire nothing. No lower tail is
  printed: no test of a count below chance was pre-specified for C5, and
  none is added after the readings.

EXIT CODES  0 printed and every check PASS; 2 an input problem; 3 H2, R0,
  R2 or M1 FAIL (everything is still printed where possible).

HOW TO RUN (repository root)
    python -B scripts/c5_headline_nf.py --workers 4
Python 3.8 to 3.13, NumPy only; git is called to check the logs are
committed and unmodified. It runs the null fixture at NF 400 and at NF
12000, as c5_nfcheck.py did, so it takes about as long.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import platform                                                 # noqa: E402
import re                                                       # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import c5_analysis as A                                         # noqa: E402
import c5_nfcheck as N                                          # noqa: E402

say, hdr, Stop, JP = A.say, A.hdr, A.Stop, A.JP
NF_BIG = 12000
DEFAULT_READINGS = "logs/c5-analysis-a0py-20261125.log"
DEFAULT_NFCHECK = "logs/c5-nfcheck-20261125.log"
HEAD_RE = re.compile(r"^HEADLINE COUNTS  \((\d+) cells;")
LINE_RE = re.compile(r"^  (R1b|R1c|R1d|D-ref)\s+observed\s+(\d+)\s")


def a_line(k, obs, n, r):
    """c5_analysis.py's headline line format, verbatim (the NOT USED suffix never applies: every r400 is used)."""
    return "  {:<6} observed {:>3}   expected {:>6.1f} at null rate {:.3f}   P(X >= {}) = {:.3g}   {}".format(
        k, obs, n * r, r, obs, A.binom_tail(n, r, obs), "")


def read_headline(lines):
    """(n, {k: (obs, line)}) from the readings log; Stop(2) on anything unexpected."""
    heads = [(i, HEAD_RE.match(s)) for i, s in enumerate(lines) if s.startswith("HEADLINE COUNTS")]
    if len(heads) != 1 or heads[0][1] is None:
        raise Stop(2, "H1 FAIL: readings log has {} HEADLINE COUNTS headings, expected 1 giving the cell "
                      "count".format(len(heads)))
    i0, m = heads[0]
    n = int(m.group(1))
    got = {}
    for s in lines[i0 + 1:]:
        mm = LINE_RE.match(s)
        if mm:
            if mm.group(1) in got:
                raise Stop(2, "H1 FAIL: two headline lines for {}".format(mm.group(1)))
            got[mm.group(1)] = (int(mm.group(2)), s.rstrip())
    miss = [k for k in A.CRITS if k not in got]
    if miss:
        raise Stop(2, "H1 FAIL: no headline line for {}".format(", ".join(miss)))
    return n, got


def read_nf_tables(lines):
    """{nf: {crit: [six 4-decimal strings: four levels, max, mean]}} from the nfcheck log's PART N tables."""
    out, cur = {}, None
    for s in lines:
        m = re.match(r"^  NF (\d+)  \(\d+ pooled groups per level\)$", s)
        if m:
            cur = int(m.group(1))
            out[cur] = {}
            continue
        if s.startswith("  SIDE BY SIDE"):
            cur = None
        if cur is None:
            continue
        f = s.split()
        if len(f) >= 9 and f[0] in A.CRITS and f[5] == "|":
            out[cur][f[0]] = f[1:5] + f[6:8]
    for nf in (A.NF, NF_BIG):
        if nf not in out or any(k not in out[nf] for k in A.CRITS):
            raise Stop(2, "nfcheck log: no complete NF {} table for {}".format(nf, ", ".join(A.CRITS)))
    return out


def fmt6(v):
    return ["{:.4f}".format(x) for x in v] + ["{:.4f}".format(max(v)), "{:.4f}".format(sum(v) / 4.0)]


def cmp(a, b):
    return "falls" if a < b else ("rises" if a > b else "unchanged")


def pos(obs, e):
    return "observed above expected" if obs > e else ("observed below expected" if obs < e
                                                       else "observed equals expected")


def main():
    ap = argparse.ArgumentParser(description="C5 headline counts at the NF 12000 null rates (writes nothing)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--readings-log", default=DEFAULT_READINGS)
    ap.add_argument("--nfcheck-log", default=DEFAULT_NFCHECK)
    a = ap.parse_args()
    if a.workers < 1:
        raise Stop(2, "--workers at least 1")
    hdr("CBO-GAP c5_headline_nf  (ledger N45, after the C5 READINGS; re-makes no verdict)  --  reads only, "
        "writes nothing")
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    say("  script   sha256 {}".format(JP.sha256_of(os.path.abspath(__file__))))
    say("  c5_analysis.py sha256 {}".format(JP.sha256_of(A.__file__)))
    say("  c5_nfcheck.py  sha256 {}".format(JP.sha256_of(N.__file__)))
    say("  readings log {}   nfcheck log {}".format(a.readings_log, a.nfcheck_log))
    say("  B {}  levels {}  NF {} and {}  seeds SeedSequence({} + (level, cell, set))".format(
        A.B, A.LEVELS, A.NF, NF_BIG, A.NULL_SEED))
    rl = N.read_log(a.readings_log)
    nl = N.read_log(a.nfcheck_log)
    n, head = read_headline(rl)
    tabs = read_nf_tables(nl)
    say("  H1 PASS  n {} cells; observed {}".format(n, ", ".join("{} {}".format(k, head[k][0]) for k in A.CRITS)))

    hdr("FIXTURE AT NF {} (as c5_analysis.py prints it)".format(A.NF))
    tee = N.Tee(sys.stdout)
    sys.stdout = tee
    try:
        _u, r0, _g0 = A.null_fixture(a.workers, A.NF)
    finally:
        sys.stdout = tee.real
    mine, ref = N.span(tee.lines(), "this run"), N.span(rl, a.readings_log)
    r0ok = mine == ref
    if r0ok:
        say("  R0 PASS against {}: {} lines identical".format(a.readings_log, len(mine)))
    else:
        say("  R0 FAIL against {}: the NF {} fixture span differs".format(a.readings_log, A.NF))

    hdr("FIXTURE AT NF {} (no status: the verdicts keep the NF {} status)".format(NF_BIG, A.NF))
    _u, r1, _g1 = A.null_fixture(a.workers, NF_BIG, False)

    hdr("CHECKS")
    r2ok = True
    for nf, rr in ((A.NF, r0), (NF_BIG, r1)):
        for k in A.CRITS:
            here, there = fmt6(rr[k]), tabs[nf][k]
            if here != there:
                r2ok = False
                say("  R2 FAIL NF {} {}: here {}  nfcheck log {}".format(nf, k, " ".join(here), " ".join(there)))
    if r2ok:
        say("  R2 PASS  NF {} and NF {}: every per-level rate, max and mean of {} equals the nfcheck log".format(
            A.NF, NF_BIG, ", ".join(A.CRITS)))
    rates = {}
    for k in A.CRITS:
        rates[k] = (("A", "max NF {}".format(A.NF), max(r0[k])),
                    ("B", "max NF {}".format(NF_BIG), max(r1[k])),
                    ("C", "mean NF {}".format(NF_BIG), sum(r1[k]) / 4.0))
    h2 = True
    for k in A.CRITS:
        obs, logged = head[k]
        mine_l = a_line(k, obs, n, rates[k][0][2]).rstrip()
        if mine_l != logged:
            h2 = False
            say("  H2 FAIL {}:".format(k))
            say("    here {!r}".format(mine_l))
            say("    log  {!r}".format(logged))
    say("  H2 {}  line A reproduces the readings log's headline line for {}".format(
        "PASS" if h2 else "FAIL", ", ".join(A.CRITS)))
    ok = r0ok and r2ok and h2
    m1 = True
    for k in A.CRITS:
        obs = head[k][0]
        t0 = A.binom_tail(n, rates[k][0][2], obs)
        for _t, _lab, r in rates[k][1:]:
            t = A.binom_tail(n, r, obs)
            if (r < rates[k][0][2] and t > t0) or (r > rates[k][0][2] and t < t0):
                m1 = False
                say("  M1 FAIL {} {}: rate {!r} against {!r}, tail {!r} against {!r}".format(
                    k, _lab, r, rates[k][0][2], t, t0))
    say("  M1 {}  the upper tail moves with the rate for every criterion".format("PASS" if m1 else "FAIL"))
    ok = ok and m1

    hdr("HEADLINE COUNTS AT THREE RATES  ({} cells; A is the recorded comparison; B and C are descriptions beside "
        "it, no status, no verdict)".format(n))
    say("  {:<6} {:>4} | {:<1} {:<15} {:>9} {:>9} {:>11} | {}".format(
        "crit", "obs", "", "rate", "r", "expected", "P(X >= obs)", "position"))
    for k in A.CRITS:
        obs = head[k][0]
        for tag, lab, r in rates[k]:
            e = n * r
            say("  {:<6} {:>4} | {} {:<15} {:>9.4f} {:>9.2f} {:>11.4g} | {}".format(
                k, obs, tag, lab, r, e, A.binom_tail(n, r, obs), pos(obs, e)))
        say("")
    say("  A in c5_analysis.py's format (must equal the readings log, H2):")
    for k in A.CRITS:
        say(a_line(k, head[k][0], n, rates[k][0][2]).rstrip())

    hdr("DIRECTION AGAINST A  (rule in the docstring)")
    say("  {:<6} {:<15} {:>10} {:>10}   {}".format("crit", "rate", "expected", "tail", "position at A -> here"))
    for k in A.CRITS:
        obs = head[k][0]
        _ta, _la, ra = rates[k][0]
        ea, ta = n * ra, A.binom_tail(n, ra, obs)
        for _t, lab, r in rates[k][1:]:
            e, t = n * r, A.binom_tail(n, r, obs)
            say("  {:<6} {:<15} {:>10} {:>10}   {} -> {}".format(k, lab, cmp(e, ea), cmp(t, ta), pos(obs, ea),
                                                                  pos(obs, e)))
    code = 0 if ok else 3
    hdr("c5_headline_nf.py done, exit {}  (H1 PASS, H2 {}, R0 {}, R2 {}, M1 {}; nothing written)".format(
        code, "PASS" if h2 else "FAIL", "PASS" if r0ok else "FAIL", "PASS" if r2ok else "FAIL",
        "PASS" if m1 else "FAIL"))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
