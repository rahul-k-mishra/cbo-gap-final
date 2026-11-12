#!/usr/bin/env bash
# rerunq-creds.sh: write ~/.kaggle/credentials.json for one GitHub Actions job
# of the rerun queue, from the secret KAGGLE_OAUTH_CREDENTIALS (ledger K10,
# 2026-11-12, Rahul's decision: Actions authenticates as the laptop does,
# through an OAuth refresh token from "kaggle auth login", not through a
# KGAT_ access token or a legacy kaggle.json key).
#
# It is a shell file, not a .py file, on purpose: kgrun.py ships every
# scripts/*.py except kgrun.py and rerunq.py to Kaggle, so a .py helper would
# change the bundle id of every later launch. Like rerunq-notify.sh, it is
# never shipped.
#
# USAGE (workflow step; the secret arrives in the environment only)
#   env RERUNQ_KAGGLE_OAUTH=<secret> bash scripts/rerunq-creds.sh ericsom
# The argument is the Kaggle account the queue runs as (kgrun.py --user).
#
# WHY THESE RULES (kaggle 2.2.4, kagglesdk 0.1.37, as in requirements.lock;
# read from the installed source on 2026-11-12)
#   KaggleApi.authenticate tries, in order and stopping at the first that
#   applies: (1) an access token from KAGGLE_API_TOKEN, ~/.kaggle/access_token
#   or ~/.kaggle/access_token.txt, used if Kaggle's introspection names a user;
#   (2) a legacy key, i.e. username and key from ~/.kaggle/kaggle.json or from
#   the environment variables KAGGLE_USERNAME and KAGGLE_KEY (every KAGGLE_*
#   variable is read into the CLI's configuration); (3) the OAuth file
#   ~/.kaggle/credentials.json. So credentials.json is used only if nothing of
#   (1) or (2) is present. The s73 halt was (1) winning with a token that no
#   longer had kernels.get (ledger K10).
#   KaggleCredentials.load needs a non-empty refresh_token; an empty
#   access_token, or an empty access_token_expiration, makes the CLI refresh
#   on first use (GenerateAccessToken with the refresh token, 12 h lifetime)
#   and save the new access token back to the file. The refresh response
#   carries no refresh token, so the file's refresh token never changes.
#
# DECISION RULES (each failure is a named exit 2; the secret's content, and
# every token, is never printed; only the first five characters of the
# refresh token are compared, and only "yes" or "no" is printed)
#   CRED1  the secret is missing or blank
#          example: RERUNQ_KAGGLE_OAUTH="" -> "CRED1: ... is empty"
#   CRED2  the secret is not a JSON object
#          example: '["a"]' or 'KGRT_x' -> "CRED2: ... not a JSON object"
#   CRED3  refresh_token is missing, empty or not a string
#          example: {"username": "ericsom"} -> CRED3
#   CRED4  refresh_token starts with "KGAT_": that is an API access token, the
#          kind that failed at s73, pasted in the wrong field
#          example: {"refresh_token": "KGAT_abc", ...} -> CRED4
#   CRED5  username is not the account given as the argument
#          example: argument ericsom, {"username": "someone"} -> CRED5
#   CRED6  ~/.kaggle already holds access_token, access_token.txt, kaggle.json
#          or credentials.json: the first three would be used before
#          credentials.json, the last would be overwritten
#          example: a runner image with ~/.kaggle/kaggle.json -> CRED6
#   CRED7  KAGGLE_API_TOKEN, KAGGLE_USERNAME or KAGGLE_KEY is set in this
#          job's environment: each would be used before credentials.json
#          example: KAGGLE_KEY=... at job level -> CRED7
#   CRED8  scopes is present and not a list of strings
#          example: {"scopes": "resources.admin:*"} -> CRED8
#   Otherwise it writes credentials.json with mode 600 (O_EXCL), holding
#   refresh_token, username, scopes (as given, or [] if absent), and an empty
#   access_token and access_token_expiration, so that every job starts from
#   the refresh token alone and a dead refresh token shows on the job's first
#   Kaggle call. A prefix other than KGRT_ is reported ("prefix KGRT_: no")
#   but not refused: KGRT_ has been seen once (Rahul's laptop login,
#   2026-11-12), which is not enough to call it the only format.
#   Worked example of a pass: secret {"refresh_token": "KGRT_...",
#   "access_token": "CfDJ8...", "access_token_expiration": "2026-11-12T...",
#   "username": "ericsom", "scopes": ["resources.admin:*"]}, argument ericsom,
#   empty ~/.kaggle -> prints
#     credentials.json written, mode 600; username ericsom; refresh_token
#     prefix KGRT_: yes; scopes ['resources.admin:*']; access token not
#     carried (the CLI refreshes it on first use)
#   and exits 0.
#
# The workflow's last step removes ~/.kaggle/credentials.json whatever
# happened. This script writes nothing else and contacts nothing.

set -eu
umask 077
if [ "$#" -ne 1 ] || [ -z "$1" ]; then
    echo "usage: RERUNQ_KAGGLE_OAUTH=... bash scripts/rerunq-creds.sh <kaggle user>" >&2
    exit 2
fi
exec python - "$1" <<'EOF'
import json
import os
import stat
import sys


def stop(code, text):
    print("{}: {}".format(code, text))
    sys.exit(2)


owner = sys.argv[1]
raw = os.environ.get("RERUNQ_KAGGLE_OAUTH", "")
if not raw.strip():
    stop("CRED1", "the secret KAGGLE_OAUTH_CREDENTIALS is empty or not passed to this step")
try:
    data = json.loads(raw)
except ValueError:
    data = None
if not isinstance(data, dict):
    stop("CRED2", "the secret KAGGLE_OAUTH_CREDENTIALS is not a JSON object (content not printed)")
rt = data.get("refresh_token")
if not isinstance(rt, str) or not rt.strip():
    stop("CRED3", "refresh_token is missing, empty or not a string")
if rt.startswith("KGAT_"):
    stop("CRED4", "refresh_token starts with KGAT_: that is an API access token, not a refresh token")
user = data.get("username")
if user != owner:
    stop("CRED5", "username is {!r}, the queue runs as {!r}".format(user, owner))
scopes = data.get("scopes", [])
if scopes is None:
    scopes = []
if not isinstance(scopes, list) or not all(isinstance(s, str) for s in scopes):
    stop("CRED8", "scopes is not a list of strings")

d = os.path.expanduser("~/.kaggle")
present = [n for n in ("access_token", "access_token.txt", "kaggle.json", "credentials.json")
           if os.path.lexists(os.path.join(d, n))]
if present:
    stop("CRED6", "~/.kaggle already holds {}".format(", ".join(present)))
env = [k for k in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY") if k in os.environ]
if env:
    stop("CRED7", "set in this job's environment, and used before credentials.json: {}".format(", ".join(env)))

if not os.path.isdir(d):
    os.makedirs(d, 0o700)
out = {
    "refresh_token": rt,
    "access_token": "",
    "access_token_expiration": "",
    "username": user,
    "scopes": scopes,
}
path = os.path.join(d, "credentials.json")
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as fh:
    json.dump(out, fh, indent=2)
os.chmod(path, 0o600)
print("credentials.json written, mode {:o}; username {}; refresh_token prefix KGRT_: {}; scopes {}; "
      "access token not carried (the CLI refreshes it on first use)".format(
          stat.S_IMODE(os.stat(path).st_mode), user, "yes" if rt.startswith("KGRT_") else "no", scopes))
EOF
