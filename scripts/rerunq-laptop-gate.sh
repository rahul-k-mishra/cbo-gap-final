#!/usr/bin/env bash
# rerunq-laptop-gate.sh: decide whether the laptop timer's tick may run, and
# make sure the laptop's Kaggle access token is fresh before it does (ledger
# K11, 2026-11-12, Rahul's decision: the laptop timer returns as a FALLBACK
# driver that acts only when the Actions chain has gone quiet).
#
# Run by scripts/rerunq-tick.service as an ExecCondition, after the git
# fetch. systemd's meaning of its exit code:
#   0        the tick runs
#   1..254   the tick is SKIPPED: not a failure, the timer keeps running
#   255      the unit FAILS: OnFailure runs rerunq-stop.service, which
#            disables the timer
# This script uses 0, 1 and 255 only. It writes nothing but, through the
# kaggle CLI's own code (KaggleCredentials.refresh_access_token, which calls
# KaggleCredentials.save), ~/.kaggle/credentials.json when it refreshes. It
# never prints a token. It is a shell file, not .py, so kgrun.py does not
# ship it to Kaggle (the bundle id is unchanged).
#
# USAGE
#   bash scripts/rerunq-laptop-gate.sh            the gate (the service runs this)
#   bash scripts/rerunq-laptop-gate.sh selftest   the fixtures below; no network,
#                                                 no ~/.kaggle (a scratch HOME)
#   bash scripts/rerunq-laptop-gate.sh github     G0 to G6 only, against GitHub;
#                                                 reads only, never touches ~/.kaggle
#   bash scripts/rerunq-laptop-gate.sh token      T1 to T3 only, on the real
#                                                 ~/.kaggle; refreshes the access
#                                                 token exactly as the gate would
#
# WHY A GATE (ledger K11). While kgrun launch runs, main reads LAUNCHING:
# for c5-x-s73of116-a1 from the intent commit b91ba1b (00:48:26 IST) to the
# launched commit bf6f4c7 (00:50:01 IST). A tick of the OTHER driver that
# starts in that window reads LAUNCHING and follows L2: kgrun status, which
# is ABSENT until the push near the end of the launch, then HALT. The
# launching tick then loses its RUNNING push (L1) and exits 3. With both
# drivers ticking independently, some launches will meet this; how often
# has not been measured by a logged run. Two ticks of the workflow never
# overlap (its concurrency group), so the gate's job is to keep the laptop
# from ticking while the workflow's chain is alive.
#
# THE CHAIN, as GitHub shows it. A live chain is one run of rerun-queue.yml
# after another: each run ticks, sleeps up to 900 s (next-wake), dispatches
# its successor and only then completes, so the successor is queued before
# its predecessor finishes. The job's timeout is 90 minutes, sleep included.
#
# DECISION RULES, in order (G = GitHub; T = token). Thresholds fixed here:
#   QUIET_MIN 20, QUEUED_STALL_MIN 30, RUNNING_STALL_MIN 95,
#   REFRESH_MARGIN_MIN 35, RUNS_LISTED 20.
#   G0  "gh api" for the workflow, or for its RUNS_LISTED latest runs, fails
#       or returns something unreadable: SKIP (exit 1). GitHub may be
#       unreachable, and a tick cannot push without it anyway.
#   G1  The workflow's state is not "active": ACT. No Actions tick can start
#       (a dispatch to a disabled workflow starts nothing), so there is no
#       one to collide with. If it was disabled by a halt, the tick finds
#       HALTED, exits 3 and disables the timer, as rule 22 says.
#       Example: state "disabled_manually" -> ACT.
#   G2  A run with status in_progress started less than RUNNING_STALL_MIN
#       ago: SKIP, the chain is alive.
#       Example: in_progress, run_started_at 12 min ago -> SKIP.
#   G3  A run in any other unfinished status (queued, waiting, pending,
#       requested) created less than QUEUED_STALL_MIN ago: SKIP.
#       Example: queued, created 3 min ago -> SKIP.
#   G4  Unfinished runs exist but every one is past its limit: ACT, the
#       chain is stalled. Example: queued, created 41 min ago -> ACT;
#       in_progress, started 100 min ago (past the 90 min timeout) -> ACT.
#   G5  No run is unfinished, and the latest updated_at is less than
#       QUIET_MIN ago: SKIP, the chain may be between runs or just ended.
#       Example: last completed 6 min ago -> SKIP.
#   G6  No run is unfinished, and the latest updated_at is at least
#       QUIET_MIN ago, or there is no run: ACT, the chain is quiet.
#       Example: last completed 26 min ago -> ACT.
#   Only after an ACT:
#   T1  ~/.kaggle holds access_token, access_token.txt or kaggle.json, or
#       KAGGLE_API_TOKEN, KAGGLE_USERNAME or KAGGLE_KEY is set: FAIL (255).
#       The CLI would use any of them before credentials.json (ledger K10).
#   T2  ~/.kaggle/credentials.json is missing or has no refresh_token:
#       FAIL (255).
#   T3  access_token is empty, or access_token_expiration is empty or less
#       than REFRESH_MARGIN_MIN from now: refresh through the CLI's own
#       KaggleCredentials.refresh_access_token, which writes the file.
#       HTTP 401: FAIL (255), the refresh token is refused. Any other error
#       (network): SKIP (1), the next tick retries. Success: run.
#       Reason (ledger K10): kagglesdk 0.1.37 sends a stored access token
#       for up to 30 minutes AFTER it expires (access_token_has_expired
#       has its margin the wrong way round). A tick lasts at most 90
#       minutes, but its kaggle calls are spread over the first few, so a
#       35-minute margin covers them.
#       Example: expiration 20 min from now -> refresh; 5 h from now -> run.
#   T0  Otherwise: run (exit 0).
#   Every decision prints one line starting with its rule.
#
# WHAT THE GATE DOES NOT COVER (ledger K11). The workflow has no gate. If
# the chain resumes (GitHub's schedule backstop, a stalled run that
# starts) while a laptop tick is launching, that Actions tick can meet
# LAUNCHING and halt as above. It needs the chain to restart inside one
# launch's LAUNCHING window, so it is rarer than with two free-running
# drivers, but it is not zero. No such collision can launch a kernel twice:
# L1 lets one tick past LAUNCHING, and L3 and K1 refuse a reused name.

set -eu
exec python - "${1:-gate}" <<'EOF'
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

REPO = "rahul-k-mishra/cbo-gap-final"
WORKFLOW = "rerun-queue.yml"
QUIET_MIN = 20
QUEUED_STALL_MIN = 30
RUNNING_STALL_MIN = 95
REFRESH_MARGIN_MIN = 35
RUNS_LISTED = 20
ACT, SKIP, FAIL = 0, 1, 255


def parse(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def minutes(now, t):
    return (now - parse(t)).total_seconds() / 60.0


def decide(state, runs, now):
    """(act, line) from the workflow's state and its latest runs."""
    if state != "active":
        return True, "G1: workflow {} is {}; no Actions tick can start: act".format(WORKFLOW, state)
    live = [r for r in runs if r["status"] != "completed"]
    for r in live:
        if r["status"] == "in_progress":
            age = minutes(now, r.get("run_started_at") or r["created_at"])
            if age < RUNNING_STALL_MIN:
                return False, "G2: run {} in progress for {:.1f} min (< {}); the chain is alive: skip".format(
                    r["id"], age, RUNNING_STALL_MIN)
        else:
            age = minutes(now, r["created_at"])
            if age < QUEUED_STALL_MIN:
                return False, "G3: run {} {} for {:.1f} min (< {}); the chain is alive: skip".format(
                    r["id"], r["status"], age, QUEUED_STALL_MIN)
    if live:
        return True, "G4: {} unfinished run(s), every one past its limit ({}); the chain is stalled: act".format(
            len(live), ", ".join("{} {}".format(r["id"], r["status"]) for r in live))
    if not runs:
        return True, "G6: the workflow has no runs; the chain is quiet: act"
    last = max(runs, key=lambda r: parse(r["updated_at"]))
    age = minutes(now, last["updated_at"])
    if age < QUIET_MIN:
        return False, "G5: no run unfinished; run {} ended {:.1f} min ago (< {}): skip".format(
            last["id"], age, QUIET_MIN)
    return True, "G6: no run unfinished; run {} ended {:.1f} min ago (>= {}); the chain is quiet: act".format(
        last["id"], age, QUIET_MIN)


def gh_json(path):
    p = subprocess.run(["gh", "api", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    if p.returncode != 0:
        raise RuntimeError("gh api {} exit {}: {}".format(path, p.returncode, p.stderr.strip()[:200]))
    return json.loads(p.stdout)


def github(now):
    try:
        wf = gh_json("repos/{}/actions/workflows/{}".format(REPO, WORKFLOW))
        rl = gh_json("repos/{}/actions/workflows/{}/runs?per_page={}".format(REPO, WORKFLOW, RUNS_LISTED))
        state = wf["state"]
        runs = [{k: r.get(k) for k in ("id", "status", "created_at", "run_started_at", "updated_at")}
                for r in rl["workflow_runs"]]
        for r in runs:
            parse(r["created_at"])
            parse(r["updated_at"])
    except Exception as e:
        return None, "G0: GitHub could not be read ({}: {}): skip".format(type(e).__name__, e)
    return decide(state, runs, now)


def token(now, refresh=None):
    """(code, line). refresh: a stand-in for the CLI's refresh, for the selftest only."""
    d = os.path.expanduser("~/.kaggle")
    present = [n for n in ("access_token", "access_token.txt", "kaggle.json") if os.path.lexists(os.path.join(d, n))]
    env = [k for k in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY") if k in os.environ]
    if present or env:
        return FAIL, "T1: {} would be used before credentials.json (ledger K10): fail".format(
            ", ".join(["~/.kaggle/" + n for n in present] + env))
    from kagglesdk import KaggleClient, KaggleCredentials, KaggleEnv
    with KaggleClient(env=KaggleEnv.PROD) as client:
        creds = KaggleCredentials.load(client=client)
        if creds is None:
            return FAIL, "T2: ~/.kaggle/credentials.json missing, unreadable or without refresh_token: fail"
        exp = creds._access_token_expiration
        if creds._access_token and exp is not None and exp - now >= timedelta(minutes=REFRESH_MARGIN_MIN):
            return ACT, "T0: access token valid until {} (>= {} min): run".format(
                exp.strftime("%Y-%m-%dT%H:%M:%SZ"), REFRESH_MARGIN_MIN)
        why = "no access token" if not creds._access_token else (
            "no expiration" if exp is None else "expires {}".format(exp.strftime("%Y-%m-%dT%H:%M:%SZ")))
        try:
            (refresh or KaggleCredentials.refresh_access_token)(creds)
        except Exception as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code == 401:
                return FAIL, "T3: refresh refused with HTTP 401 ({}); the refresh token is not accepted: fail".format(why)
            return SKIP, "T3: refresh failed ({}; {}: {}): skip, the next tick retries".format(
                why, type(e).__name__, str(e)[:200])
        return ACT, "T3: refreshed ({}); valid until {}: run".format(
            why, creds._access_token_expiration.strftime("%Y-%m-%dT%H:%M:%SZ"))


def gate():
    now = datetime.now(timezone.utc)
    act, line = github(now)
    print(line)
    if act is None:
        return SKIP
    if not act:
        return SKIP
    code, line = token(now)
    print(line)
    return code


def selftest():
    import tempfile
    now = parse("2026-11-12T12:00:00Z")

    def ago(m):
        return (now - timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def run(i, status, created, started=None, updated=None):
        return {"id": i, "status": status, "created_at": ago(created),
                "run_started_at": ago(started if started is not None else created),
                "updated_at": ago(updated if updated is not None else created)}

    cases = [
        ("G1 disabled", "disabled_manually", [run(1, "in_progress", 5)], True, "G1"),
        ("G2 in progress 12 min", "active", [run(2, "in_progress", 12), run(1, "completed", 30, updated=13)], False, "G2"),
        ("G2 limit 94 min", "active", [run(2, "in_progress", 94)], False, "G2"),
        ("G3 queued 3 min behind in_progress 15", "active",
         [run(3, "queued", 3), run(2, "in_progress", 15)], False, "G3"),
        ("G3 waiting 29 min", "active", [run(3, "waiting", 29)], False, "G3"),
        ("G4 queued 41 min", "active", [run(3, "queued", 41), run(2, "completed", 60, updated=41)], True, "G4"),
        ("G4 in progress 100 min", "active", [run(3, "in_progress", 100)], True, "G4"),
        ("G5 completed 6 min ago", "active", [run(3, "completed", 22, updated=6)], False, "G5"),
        ("G5 at 19.9 min", "active", [run(3, "completed", 40, updated=19.9)], False, "G5"),
        ("G6 at 20 min", "active", [run(3, "completed", 40, updated=20)], True, "G6"),
        ("G6 completed 26 min ago", "active", [run(3, "completed", 41, updated=26)], True, "G6"),
        ("G6 no runs", "active", [], True, "G6"),
    ]
    bad = 0
    for name, state, runs, want, rule in cases:
        act, line = decide(state, runs, now)
        ok = act == want and line.startswith(rule + ":")
        bad += not ok
        print("{}  {:40s} {}".format("PASS" if ok else "FAIL", name, line))

    class Resp(object):
        status_code = 401

    class Http401(Exception):
        response = Resp()

    def fresh(creds):
        creds._access_token = "FRESH_fake"
        creds._access_token_expiration = datetime.now(timezone.utc) + timedelta(hours=12)
        creds.save()

    def refused(creds):
        raise Http401("401 Client Error")

    def offline(creds):
        raise OSError("network unreachable")

    real_now = datetime.now(timezone.utc)

    def write(h, files, cred):
        os.makedirs(os.path.join(h, ".kaggle"))
        for n in files:
            open(os.path.join(h, ".kaggle", n), "w").write("x")
        if cred is not None:
            open(os.path.join(h, ".kaggle", "credentials.json"), "w").write(json.dumps(cred))

    def cred(exp_min, at="CfDJ8fake"):
        return {"refresh_token": "KGRT_fake", "access_token": at, "username": "ericsom", "scopes": [],
                "access_token_expiration": "" if exp_min is None else
                (real_now + timedelta(minutes=exp_min)).isoformat()}

    tcases = [
        ("T1 kaggle.json", ["kaggle.json"], cred(300), {}, None, FAIL, "T1"),
        ("T1 access_token", ["access_token"], cred(300), {}, None, FAIL, "T1"),
        ("T1 KAGGLE_KEY", [], cred(300), {"KAGGLE_KEY": "k"}, None, FAIL, "T1"),
        ("T2 no file", [], None, {}, None, FAIL, "T2"),
        ("T2 no refresh token", [], {"username": "ericsom"}, {}, None, FAIL, "T2"),
        ("T0 valid 5 h", [], cred(300), {}, refused, ACT, "T0"),
        ("T3 expires in 20 min, refreshed", [], cred(20), {}, fresh, ACT, "T3"),
        ("T3 expired 10 min ago, refreshed", [], cred(-10), {}, fresh, ACT, "T3"),
        ("T3 empty access token, refreshed", [], cred(300, at=""), {}, fresh, ACT, "T3"),
        ("T3 no expiration, refreshed", [], cred(None), {}, fresh, ACT, "T3"),
        ("T3 refused 401", [], cred(20), {}, refused, FAIL, "T3"),
        ("T3 offline", [], cred(20), {}, offline, SKIP, "T3"),
    ]
    saved_home = os.environ.get("HOME")
    base = tempfile.mkdtemp(prefix="rerunq-gate-selftest-")
    for i, (name, files, c, env, refresh, want, rule) in enumerate(tcases):
        h = os.path.join(base, str(i))
        write(h, files, c)
        os.environ["HOME"] = h
        for k in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"):
            os.environ.pop(k, None)
        os.environ.update(env)
        code, line = token(real_now, refresh=refresh)
        extra = ""
        if refresh is fresh and code == ACT:
            after = json.load(open(os.path.join(h, ".kaggle", "credentials.json")))
            extra = " [file: refresh token kept {}, new token saved {}]".format(
                after["refresh_token"] == "KGRT_fake", after["access_token"] == "FRESH_fake")
            if "False" in extra:
                code = -1
        ok = code == want and line.startswith(rule + ":") and "CfDJ8fake" not in line and "KGRT_fake" not in line
        bad += not ok
        print("{}  {:40s} exit {} {}{}".format("PASS" if ok else "FAIL", name, code, line, extra))
        for k in env:
            os.environ.pop(k, None)
    if saved_home is not None:
        os.environ["HOME"] = saved_home
    print("selftest: {} case(s) failed (scratch {})".format(bad, base))
    return 0 if bad == 0 else 2


if sys.argv[1] == "selftest":
    sys.exit(selftest())
if sys.argv[1] == "github":
    act, line = github(datetime.now(timezone.utc))
    print(line)
    sys.exit(ACT if act else SKIP)
if sys.argv[1] == "token":
    code, line = token(datetime.now(timezone.utc))
    print(line)
    sys.exit(code)
if sys.argv[1] != "gate":
    print("usage: bash scripts/rerunq-laptop-gate.sh [gate|selftest|github|token]")
    sys.exit(FAIL)
try:
    sys.exit(gate())
except SystemExit:
    raise
except Exception as e:
    print("GATE ERROR: {}: {}: fail".format(type(e).__name__, e))
    sys.exit(FAIL)
EOF
