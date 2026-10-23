"""PreToolUse hook (Bash): refuse any command whose full text names the
rerun queue's state file (CLAUDE.md rule 22; ledger K6).

The deny rule Bash(*rerun_queue.json*) in .claude/settings.json matches
the command text without a heredoc body, so a heredoc script naming the
file passed it (notes/RERUNQ_REVIEW.md, fourth pass). This hook reads the
whole command as Claude Code hands it over, heredoc included.

DECISION RULE
  Block (exit 2, reason on stderr) when the string "rerun_queue" occurs
  anywhere in tool_input.command. "rerun_queue" rather than the full file
  name, so that rerun_queue.json.tmp and a name split as
  "rerun_queue" + ".json" are caught as well.
  If stdin is not the expected JSON, the raw stdin text is searched
  instead: a hook that cannot read its input still blocks a match.
  Anything else: exit 0, no output; the normal permission flow decides.
  A crash of this script blocks the call ("onFailure": "block" in
  settings.json).
  Worked examples:
    wc -c notes/rerun_queue.json                    block
    python3 - <<'EOF' / open("notes/rerun_queue.json") / EOF   block
    python3 -c 'open("notes/" + "rerun_" + "queue.json")'      NOT blocked:
        the name is assembled from pieces that do not contain
        "rerun_queue"; nothing that matches command text can see that
    git status                                      allow (exit 0)

LIMITS
  It sees the command text, not what a program does. A script file that
  opens the state file itself (scripts/rerunq.py, run by Rahul, by
  design), a glob such as notes/rerun_q*.json, or a name assembled at run
  time from pieces is not caught. Rule 22 still forbids those.
  It also blocks harmless commands that merely mention the name (a git
  commit message, a grep); Claude uses the Read and Edit tools for those
  files instead.

Writes nothing. Standard library only; Python 3.8 syntax.
"""

import json
import sys

NEEDLE = "rerun_queue"


def main():
    raw = sys.stdin.read()
    try:
        command = json.loads(raw)["tool_input"]["command"]
        if not isinstance(command, str):
            raise TypeError("command is not a string")
    except (ValueError, KeyError, TypeError):
        command = raw
    if NEEDLE in command:
        sys.stderr.write("Blocked by .claude/hooks/deny-queue-state.py: the command names the rerun "
                         "queue's state file (notes/rerun_queue.json). No Claude session reads or "
                         "writes it through Bash (CLAUDE.md rule 22).\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
