"""
manifest.py  --  CBO-GAP: write the missing sha256 manifests under runs/

WHAT IT DOES
------------
Every immediate subfolder of runs/ is a run folder. For each run folder that
has no sha256.txt, it hashes every file in that folder, subfolders included,
and writes runs/<run-id>/sha256.txt with one line per file:

    <64 hex digits><two spaces><path relative to the run folder>

Paths use "/" as the separator and the lines are sorted by path. sha256.txt
itself is never listed. The format is the one sha256sum writes, so a folder
can be checked later with

    cd runs/<run-id> && sha256sum -c sha256.txt

Worked example. runs/detcheck-20261009-082306/ contains one file,
detcheck_results.csv. The script writes
runs/detcheck-20261009-082306/sha256.txt with exactly one line, the
sha256 of detcheck_results.csv, two spaces, then "detcheck_results.csv". A
folder holding sub/b.csv and a.csv gets two lines, "a.csv" first and then
"sub/b.csv", because they are sorted by path.

All hashes in a folder are computed before sha256.txt is opened, and the
file is opened with mode "x". A read error therefore leaves no partial
manifest, and an existing manifest is never overwritten, even one created
between the check and the write.

WHAT IT REFUSES TO DO
---------------------
  - It never touches a run folder that already has a sha256.txt: it does not
    rewrite, extend, check or reformat it. That folder is reported as
    "has manifest, left alone". A run folder is never modified after its
    sha256 is written (CLAUDE.md, Git discipline).
  - It writes no manifest for a folder with no files. It reports
    "empty, skipped", because a manifest of nothing records nothing.
  - It writes no manifest for a folder containing a symbolic link or anything
    that is not a regular file or directory. It reports the offending path
    and skips the folder, because the hash would then depend on something
    outside the folder.
  - It ignores loose files directly in runs/ (it reports them), and it writes
    nowhere except runs/<run-id>/sha256.txt.
  - It never modifies, moves or deletes any existing file.

With --dry-run it hashes nothing and writes nothing. For each folder it
prints what it would do and the files that would be listed.

Exit code 0 when every folder was either written or left alone for one of
the reasons above, 1 if any write failed.

USE AS A MODULE
  kgrun.py imports write_manifest from this file, so a Kaggle run folder gets
  a manifest that is byte-identical to the one this script writes for the
  same folder. Importing this module has no side effects: it defines
  constants and functions and does nothing else. The functions are:
    list_files(folder)      -> (sorted relative paths, offending paths);
                               reads the directory tree, hashes nothing
    manifest_text(folder, files)
                            -> the exact text of sha256.txt for those files
    write_manifest(folder)  -> the list of lines written; raises
                               ManifestRefused if the folder already has
                               sha256.txt, has no files, or holds a symlink
                               or non-regular file, in which case nothing is
                               written. It raises OSError if a read or the
                               write fails.

HOW TO RUN (from the repository root)
    python scripts/manifest.py --dry-run
    python scripts/manifest.py

Standard library only. Python 3.8 to 3.11 syntax.
"""

import argparse
import hashlib
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "runs")
MANIFEST = "sha256.txt"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def list_files(folder):
    """Return (sorted relative paths, list of offending paths)."""
    files = []
    bad = []
    for base, dirs, names in os.walk(folder):
        for d in list(dirs):
            if os.path.islink(os.path.join(base, d)):
                bad.append(os.path.join(base, d))
                dirs.remove(d)
        for n in names:
            p = os.path.join(base, n)
            if os.path.islink(p) or not os.path.isfile(p):
                bad.append(p)
                continue
            rel = os.path.relpath(p, folder).replace(os.sep, "/")
            if rel == MANIFEST:
                continue
            files.append(rel)
    files.sort()
    return files, bad


class ManifestRefused(Exception):
    """The folder is one write_manifest refuses to touch; nothing was written."""


def manifest_text(folder, files):
    """Hash each relative path in files (already sorted) and return the text
    of sha256.txt: one "<sha256>  <path>" line per file, each ending in \\n."""
    return "".join("{}  {}\n".format(sha256_of(os.path.join(folder, rel)), rel)
                   for rel in files)


def write_manifest(folder):
    """Write folder/sha256.txt, opened with mode "x", and return its lines.

    Every hash is computed before the file is opened, so a read error leaves
    no partial manifest. Raises ManifestRefused, writing nothing, if the
    folder already has sha256.txt, has no files, or contains a symbolic link
    or anything that is not a regular file or directory."""
    if os.path.lexists(os.path.join(folder, MANIFEST)):
        raise ManifestRefused("has manifest, left alone")
    files, bad = list_files(folder)
    if bad:
        raise ManifestRefused("not a regular file: " + ", ".join(
            os.path.relpath(b, folder) for b in bad))
    if not files:
        raise ManifestRefused("empty, skipped")
    text = manifest_text(folder, files)
    with open(os.path.join(folder, MANIFEST), "x", newline="\n") as fh:
        fh.write(text)
    return text.splitlines()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true",
                   help="print what would be written; hash and write nothing")
    a = p.parse_args()
    dry = a.dry_run

    print("=" * 78)
    print("CBO-GAP manifest -- sha256.txt for run folders that lack one")
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  platform {}".format(platform.platform()))
    print("  runs     {}".format(RUNS))
    print("  mode     {}".format("DRY RUN: nothing is written" if dry else "WRITE"))
    print("=" * 78)

    if not os.path.isdir(RUNS):
        print("setup error: {} not found".format(RUNS))
        return 2

    counts = {"written": 0, "would write": 0, "has manifest": 0,
              "empty": 0, "unsafe": 0, "failed": 0}
    for name in sorted(os.listdir(RUNS)):
        folder = os.path.join(RUNS, name)
        if os.path.islink(folder):
            print("{:<44} symbolic link in runs/, ignored".format(name))
            continue
        if not os.path.isdir(folder):
            print("{:<44} loose file in runs/, ignored".format(name))
            continue
        if os.path.lexists(os.path.join(folder, MANIFEST)):
            print("{:<44} has manifest, left alone".format(name))
            counts["has manifest"] += 1
            continue
        files, bad = list_files(folder)
        if bad:
            print("{:<44} not a regular file, folder skipped:".format(name))
            for b in bad:
                print("    " + os.path.relpath(b, RUNS))
            counts["unsafe"] += 1
            continue
        if not files:
            print("{:<44} empty, skipped".format(name))
            counts["empty"] += 1
            continue
        if dry:
            print("{:<44} would write sha256.txt, {} file(s):".format(name, len(files)))
            for rel in files:
                print("    " + rel)
            counts["would write"] += 1
            continue
        try:
            lines = write_manifest(folder)
        except (ManifestRefused, OSError, IOError) as e:
            print("{:<44} FAILED: {}".format(name, e))
            counts["failed"] += 1
            continue
        print("{:<44} wrote sha256.txt, {} file(s):".format(name, len(files)))
        for ln in lines:
            print("    " + ln)
        counts["written"] += 1

    print("=" * 78)
    print("  " + "   ".join("{} {}".format(k, v) for k, v in counts.items()))
    print("=" * 78)
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
