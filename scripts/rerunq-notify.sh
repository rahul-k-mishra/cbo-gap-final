#!/usr/bin/env bash
# rerunq-notify.sh -- report a halted, failed or finished rerun queue by a
# GitHub issue (ledger K6, "NOTIFY", 2026-11-03; Rahul's instruction after
# the c5-x-s13of116-a1 halt went unseen for eight hours).
#
# It REPORTS ONLY. It reads the checked-out tree (git log, "rerunq.py show",
# which reads only) and writes nothing to the repository: no commit, no
# push, no state change. The workflow step that calls it runs after the
# halt, the disable and the credential removal, with continue-on-error, so
# a failure here changes neither the tick's outcome nor the workflow's state.
#
# Why an issue: the ticks are started by the job's own successor, so
# GitHub records github-actions[bot] as the triggering actor and sends the
# Actions failure email to nobody (run 41554516690, the s13 halt: event
# workflow_dispatch, actor and triggering_actor github-actions[bot],
# conclusion failure). An issue that assigns and @-mentions the repository
# owner is a "participating" notification, which GitHub emails by default.
#
# Usage: rerunq-notify.sh KIND RUN_URL
#   KIND  failure  a tick exited nonzero (halt 3, error 1, or found HALTED)
#         done     the tick asked to disable because the queue is DONE
#         test     a hand-run test (rerun-queue-notify-test.yml)
# Environment: GH_TOKEN (issues: write), GITHUB_REPOSITORY, OWNER.
#
# One open alert at a time: if an open issue labelled rerunq-alert exists,
# the report is added to it as a comment (which mentions OWNER again);
# otherwise a new issue is opened, labelled, assigned to OWNER.
# Worked example: the s13 halt. HEAD's subject is "rerun queue: HALTED at
# c5-x-s13of116-a1: R1: header of runs/...: python 3.13.18, expected
# 3.13.15 (N45, K6)", so that subject is the title; no alert is open, so
# issue opened and assigned. A second failed tick before Rahul closes it:
# one comment on that issue, no second issue.

set -u
kind="${1:?KIND}"
run_url="${2:?RUN_URL}"
: "${GITHUB_REPOSITORY:?}" "${OWNER:?}" "${GH_TOKEN:?}"
label="rerunq-alert"

head_line=$(git log -1 --format='%h %s' 2>/dev/null || echo "(git log failed)")
head_subj=$(git log -1 --format='%s' 2>/dev/null || echo "")
case "$kind" in
  failure)
    case "$head_subj" in
      "rerun queue: HALTED"*) title="$head_subj" ;;
      *) title="rerun queue: a tick failed (no halt commit on HEAD); read the run" ;;
    esac ;;
  done) title="rerun queue: DONE" ;;
  test) title="rerun queue: notification test (nothing is wrong)" ;;
  *) echo "unknown KIND $kind"; exit 2 ;;
esac
title="${title:0:240}"

body=$(mktemp)
{
  echo "@${OWNER}"
  echo
  echo "Kind: ${kind}"
  echo "Run: ${run_url}"
  echo "HEAD of the run's tree: ${head_line}"
  echo
  echo "This is a report only. Nothing was changed by it. For a failure the"
  echo "workflow has already disabled itself (rule 22). Read the halt reason,"
  echo "release by hand, check the laptop clone for unpushed commits, re-enable."
  echo "Close this issue when it is dealt with; while it is open, later alerts"
  echo "are added to it as comments."
  echo
  echo "rerunq.py show:"
  echo '```'
  timeout 60 python scripts/rerunq.py show 2>&1 | head -60 || true
  echo '```'
} > "$body"

gh label create "$label" --repo "$GITHUB_REPOSITORY" --color B60205 \
  --description "rerun queue alert (rerunq-notify.sh)" >/dev/null 2>&1 || true

open=$(gh issue list --repo "$GITHUB_REPOSITORY" --label "$label" --state open \
  --json number --jq '.[0].number' 2>/dev/null || echo "")
if [ -n "$open" ]; then
  { echo "**${title}**"; echo; cat "$body"; } > "${body}.c"
  gh issue comment "$open" --repo "$GITHUB_REPOSITORY" --body-file "${body}.c"
  echo "commented on open alert #${open}: ${title}"
else
  gh issue create --repo "$GITHUB_REPOSITORY" --title "$title" --body-file "$body" \
    --label "$label" --assignee "$OWNER"
  echo "opened alert: ${title}"
fi
