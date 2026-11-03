"""rerunqwatch.py -- the rerun queue's watchdog (ledger K6, WATCHDOG;
2026-11-03, Rahul's instruction after the C5 restart at shard 14).

WHAT IT IS FOR
  rerunq-notify.sh reports a tick that FAILS. Two ways for the queue to
  stop are not failures and so report nothing (ledger K6, NOTIFY, "Not
  covered"):
  - a tick cancelled by its 90-minute timeout (timeout-minutes: 90 in
    rerun-queue.yml): GitHub marks the job cancelled, failure() is false,
    so neither the disable step nor the alert step runs, and the
    successor step (success()) does not run either;
  - a chain that simply stops: no successor dispatched, no halt, the
    schedule backstop late or absent.
  This script looks for both, plus a third silence it can see for free
  (ticks running but the state never changing), and reports them through
  the same issue mechanism. It is run by
  .github/workflows/rerun-queue-watchdog.yml on GitHub's schedule.

IT ONLY REPORTS
  It reads the checked-out state through rerunq.load() (the same reader
  "rerunq.py show" uses) and the GitHub API (gh api, GET only). It writes
  nothing to the repository: no commit, no push, no state change, no
  workflow enable or disable, no dispatch. The workflow that runs it has
  contents: read, actions: read and issues: write, so the token could not
  push even if this script tried. Its only outputs are its console log, a
  scratch file scratch-rerunqwatch/alert.md and two GITHUB_OUTPUT keys
  (alert, title), which the workflow passes to rerunq-notify.sh watchdog.

DECISION RULES (all times UTC; "now" is the time of this run)
  Q  QUIET. If the state's status is HALTED or DONE, report nothing and
     look at nothing else. A deliberate halt (rerunq.py halt) and a
     finished queue are therefore always silent. A halt made by a tick
     has already been reported by the tick (rerunq-notify.sh failure).
     Worked example: status HALTED, halt_reason "R1: ...", workflow
     disabled, last tick 30 h ago -> QUIET, exit 0, no alert.
  Otherwise (status READY, LAUNCHING or RUNNING) each of W1 to W3 is
  checked and every one that fires is reported:
  W1 TIMED-OUT TICK. A run of rerun-queue.yml created in the last
     LOOKBACK_H = 72 h whose conclusion is "cancelled" or "timed_out" and
     whose tick job ran for at least TIMEOUT_MIN = 85 min (job
     completed_at - started_at). The job limit is 90 min; nothing else in
     the tick runs that long (the successor's sleep is at most 900 s), so
     85 min separates a timeout from the short cancellations GitHub makes
     in the concurrency group (a waiting run cancelled when a newer one is
     queued never starts its job, or starts it for seconds). The job's own
     start and end are used, not the run's, because a run can wait in the
     concurrency group before its job starts.
     Worked example: run 123, conclusion cancelled, job tick started
     10:00:05Z, completed 11:30:07Z (90.0 min) -> W1 fires, key
     "W1 run 123". Run 124, conclusion cancelled, job tick started
     10:15:00Z, completed 10:15:02Z -> nothing.
  W2 STOPPED CHAIN. Either
     (a) the workflow rerun-queue.yml is not "active" while the status is
         not HALTED or DONE (disabled by hand without a halt, or by a tick
         that failed without halting; GitHub's own inactivity disable), or
     (b) the newest LIVE run started more than STALL_MIN = 120 min ago, or
         there is no live run in the last LOOKBACK_H. A run is live if it
         is in progress, or completed with conclusion success, failure or
         timed_out, or is a W1 run. Queued, waiting and short-cancelled
         runs are not live: they never ran a tick.
     A healthy chain starts a tick every tick-duration + at most 900 s
     (next-wake --max 900), so 120 min is several missed ticks, not one
     slow one.
     Worked example: status RUNNING, workflow active, newest live run 456
     started 08:00Z, now 10:30Z (150 min) -> W2 fires, key
     "W2 after run 456". Same with now 09:30Z (90 min) -> nothing.
  W3 NO PROGRESS. The newest history entry of the state is more than
     PROGRESS_H = 14 h old. Every launch, fetch, anomaly, clear and
     release writes a history entry; a Kaggle session is capped at 12 h,
     so a RUNNING job has finished, one way or another, within 12 h of its
     launch entry and the next poll writes a fetch or anomaly entry. 14 h
     is that cap plus 2 h for Kaggle's queue and the fetch.
     Worked example: last history entry at 2026-11-03T21:00:00+05:30
     (15:30Z), now 2026-11-04T06:00Z (14.5 h) -> W3 fires, key
     "W3 since 2026-11-03T21:00:00+05:30". With now 05:00Z (13.5 h) ->
     nothing.
  ONCE PER EVENT. Each finding has a key (above). Every alert body carries
  the line "[rerunq-watchdog KEY]". Before reporting, the bodies and
  comments of every issue labelled rerunq-alert (open or closed) are read,
  and a key already present is not reported again. So one timed-out run is
  reported once; one stall is reported once (its key names the last live
  run, so a later stall after a recovery has a new key); one stuck state
  is reported once. If the notify step fails, the key never appears and
  the next run reports it again.
  ERROR. Any exception (state unreadable, gh failing) exits 1; the
  workflow then runs rerunq-notify.sh watchdog-error. A watchdog that
  cannot look is reported, not silent.

NULL RATE (false alarms)
  Q, W1 and W3 are deterministic comparisons of recorded times; none fires
  by chance. W1 could fire on a run cancelled by hand after 85 min (a real
  event worth seeing). W2(b) fires falsely only if GitHub delays a
  dispatched successor's job by more than about 100 min while the chain
  is healthy; I do not know how often GitHub does that, and the alert
  then says "look", not "act". W3 fires falsely only if Kaggle holds a
  kernel QUEUED for more than about 2 h. W2(a) fires if Rahul disables the
  workflow by hand without "rerunq.py halt": that is by design; pause the
  queue with halt, not by disabling.

WHAT IT CANNOT CATCH
  - Anything while GitHub Actions itself does not run (outage, account
    suspension): the watchdog runs there too.
  - Late detection: the watchdog runs only when GitHub's schedule fires
    it, which on this account has been hours apart for the queue's own
    schedule (rule 22). Latency is that gap plus the thresholds above.
  - An email that does not arrive: the issue is opened; delivery depends
    on Rahul's GitHub notification settings (ledger K6, NOTIFY).
  - The watchdog's own workflow being disabled.
  - The laptop timer: it reads only main's state and the workflow's runs.
  - Wrong results from a tick that looks healthy: that is what rerunq's
    header and manifest checks are for.

Usage (by the workflow; works on the laptop too with gh logged in):
  python scripts/rerunqwatch.py --repo OWNER/REPO [--now ISO]
--now is for testing only.

Python 3.8 to 3.11 syntax. Standard library only, plus scripts/rerunq.py
(for load) and the gh CLI. No trajectory is evolved here, so the Pool,
--workers and RSS items of CLAUDE.md rule 5 do not apply (as for
rerunq.py).
"""

import argparse
import datetime
import json
import os
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = "rerun-queue.yml"
LABEL = "rerunq-alert"
LOOKBACK_H = 72
TIMEOUT_MIN = 85
STALL_MIN = 120
PROGRESS_H = 14
TERMINAL = ("HALTED", "DONE")
LIVE_CONCLUSIONS = ("success", "failure", "timed_out")
OUT_DIR = os.path.join(ROOT, "scratch-rerunqwatch")
MARK = "[rerunq-watchdog {}]"


def ts(text):
    """ISO 8601 with Z or an offset -> aware UTC datetime; None stays None."""
    if not text:
        return None
    t = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timestamp without a zone: " + text)
    return t.astimezone(datetime.timezone.utc)


def minutes(a, b):
    return (b - a).total_seconds() / 60.0


def job_minutes(jobs):
    """Longest started-to-completed span of the run's jobs, in minutes."""
    best = None
    for j in jobs:
        a, b = ts(j.get("started_at")), ts(j.get("completed_at"))
        if a is not None and b is not None:
            m = minutes(a, b)
            best = m if best is None else max(best, m)
    return best


def decide(s, wf_state, runs, jobs_of, now):
    """Pure decision. s: the state dict; wf_state: the workflow's state
    string; runs: rerun-queue runs (GitHub API objects) created in the
    last LOOKBACK_H; jobs_of(run_id) -> that run's jobs; now: aware UTC.
    Returns (verdict, findings), findings a list of (key, title, detail)."""
    status = s["status"]
    if status in TERMINAL:
        return "QUIET: queue {}".format(status), []
    found = []
    timed_out = set()
    for r in runs:
        if r.get("status") != "completed" or r.get("conclusion") not in ("cancelled", "timed_out"):
            continue
        m = job_minutes(jobs_of(r["id"]))
        if m is not None and m >= TIMEOUT_MIN:
            timed_out.add(r["id"])
            found.append(("W1 run {}".format(r["id"]),
                          "rerun queue watchdog: a tick ran {:.0f} min and was cancelled (timeout?)".format(m),
                          "Run {} ({}), conclusion {}, job ran {:.1f} min (W1 threshold {} min). A tick cancelled "
                          "on timeout runs neither the disable step nor the alert step nor the successor step. "
                          "Read the run's log; the state may hold an intent the tick did not finish.".format(
                              r["id"], r.get("html_url", "-"), r["conclusion"], m, TIMEOUT_MIN)))
    if wf_state != "active":
        last = latest_live(runs, timed_out)
        found.append(("W2 workflow {} after run {}".format(wf_state, last["id"] if last else "none"),
                      "rerun queue watchdog: workflow {} while the queue is {}".format(wf_state, status),
                      "rerun-queue.yml is {} but the state is {} (not HALTED or DONE), so no tick will run. "
                      "If this was a deliberate pause, use rerunq.py halt instead.".format(wf_state, status)))
    else:
        last = latest_live(runs, timed_out)
        if last is None:
            found.append(("W2 after run none",
                          "rerun queue watchdog: no tick ran in {} h while the queue is {}".format(LOOKBACK_H, status),
                          "No live run of rerun-queue.yml in the last {} h; the chain is not running.".format(
                              LOOKBACK_H)))
        else:
            age = minutes(ts(last["run_started_at"]), now)
            if age > STALL_MIN:
                found.append(("W2 after run {}".format(last["id"]),
                              "rerun queue watchdog: no tick for {:.0f} min while the queue is {}".format(age, status),
                              "Newest live run {} ({}) started {} ({:.0f} min ago; W2 threshold {} min). The "
                              "self-schedule chain has stopped without a halt.".format(
                                  last["id"], last.get("html_url", "-"), last["run_started_at"], age, STALL_MIN)))
    hist = s.get("history") or []
    if hist:
        at = hist[-1]["at"]
        age_h = minutes(ts(at), now) / 60.0
        if age_h > PROGRESS_H:
            found.append(("W3 since {}".format(at),
                          "rerun queue watchdog: state unchanged for {:.1f} h ({})".format(age_h, status),
                          "Last history entry {} ({}, job {}), {:.1f} h ago (W3 threshold {} h). Ticks may be "
                          "running but nothing advances.".format(at, hist[-1].get("event"), hist[-1].get("job"),
                                                                age_h, PROGRESS_H)))
    return ("ALERT" if found else "OK: queue {}".format(status)), found


def latest_live(runs, timed_out):
    live = [r for r in runs if r.get("run_started_at") and (
        r.get("status") == "in_progress" or r["id"] in timed_out
        or (r.get("status") == "completed" and r.get("conclusion") in LIVE_CONCLUSIONS))]
    if not live:
        return None
    return max(live, key=lambda r: ts(r["run_started_at"]))


# --------------------------------------------------------------------------
def gh_json(path, paginate=False):
    cmd = ["gh", "api", "-H", "Accept: application/vnd.github+json"]
    if paginate:
        cmd.append("--paginate")
    cmd.append(path)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        raise RuntimeError("gh api {} failed ({}): {}".format(path, p.returncode, p.stderr.strip()))
    out = p.stdout.strip()
    if not paginate:
        return json.loads(out)
    # --paginate concatenates one JSON document per page
    docs, dec, i = [], json.JSONDecoder(), 0
    while i < len(out):
        while i < len(out) and out[i].isspace():
            i += 1
        if i >= len(out):
            break
        d, i = dec.raw_decode(out, i)
        docs.append(d)
    return docs


def gather(repo, now):
    wf = gh_json("repos/{}/actions/workflows/{}".format(repo, WORKFLOW))
    since = (now - datetime.timedelta(hours=LOOKBACK_H)).strftime("%Y-%m-%dT%H:%M:%SZ")
    pages = gh_json("repos/{}/actions/workflows/{}/runs?per_page=100&created=%3E%3D{}".format(
        repo, WORKFLOW, since), paginate=True)
    runs = [r for pg in pages for r in pg.get("workflow_runs", [])]
    cache = {}

    def jobs_of(run_id):
        if run_id not in cache:
            cache[run_id] = gh_json("repos/{}/actions/runs/{}/jobs".format(repo, run_id)).get("jobs", [])
        return cache[run_id]
    return wf.get("state"), runs, jobs_of


def seen_texts(repo):
    texts = []
    for pg in gh_json("repos/{}/issues?labels={}&state=all&per_page=100".format(repo, LABEL), paginate=True):
        for iss in pg:
            texts.append(iss.get("body") or "")
            if iss.get("comments", 0):
                for cp in gh_json("repos/{}/issues/{}/comments?per_page=100".format(repo, iss["number"]),
                                  paginate=True):
                    texts.extend(c.get("body") or "" for c in cp)
    return texts


def gh_output(key, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as fh:
            fh.write("{}={}\n".format(key, value.replace("\n", " ")))


def main():
    ap = argparse.ArgumentParser(description="rerun queue watchdog; reports only")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--now", default=None, help="testing only: ISO time to use as now")
    a = ap.parse_args()
    now = ts(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
    print("=" * 78)
    print("rerunqwatch  repo {}  now {}".format(a.repo, now.isoformat(timespec="seconds")))
    print("  python {}  platform {}".format(sys.version.split()[0], platform.platform()))
    print("  workflow {}  lookback {} h  W1 >= {} min  W2 > {} min  W3 > {} h  label {}".format(
        WORKFLOW, LOOKBACK_H, TIMEOUT_MIN, STALL_MIN, PROGRESS_H, LABEL))
    print("=" * 78)
    import rerunq
    s = rerunq.load()
    print("state {}  item {}  attempt {}  job {}".format(s["status"], s["index"], s["attempt"], s["job"] or "-"))
    if s["status"] in TERMINAL:
        verdict, found = decide(s, None, [], lambda i: [], now)
        print("VERDICT " + verdict)
        gh_output("alert", "false")
        return 0
    wf_state, runs, jobs_of = gather(a.repo, now)
    print("workflow state {}  runs in lookback {}".format(wf_state, len(runs)))
    verdict, found = decide(s, wf_state, runs, jobs_of, now)
    texts = seen_texts(a.repo) if found else []
    new = []
    for key, title, detail in found:
        dup = any(MARK.format(key) in t for t in texts)
        print("  {} {}: {}".format("SEEN" if dup else "NEW ", key, title))
        if not dup:
            new.append((key, title, detail))
    if not new:
        print("VERDICT " + (verdict if not found else "ALERT, all already reported"))
        gh_output("alert", "false")
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    body = os.path.join(OUT_DIR, "alert.md")
    with open(body, "w") as fh:
        for key, title, detail in new:
            fh.write("**{}**\n\n{}\n\n{}\n\n".format(title, detail, MARK.format(key)))
    title = new[0][1] if len(new) == 1 else "rerun queue watchdog: {} findings ({})".format(
        len(new), ", ".join(k.split()[0] for k, _, _ in new))
    print("VERDICT ALERT  {} new  title: {}".format(len(new), title))
    gh_output("alert", "true")
    gh_output("title", title[:240])
    return 0


if __name__ == "__main__":
    sys.exit(main())
