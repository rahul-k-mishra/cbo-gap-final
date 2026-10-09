"""
cbopaths.py  --  CBO-GAP: where the archive is and where run folders go

WHY THIS EXISTS
---------------
Every round-2 script that imports dynamics from the archive needs two paths
before argparse runs: the archive, because its modules are imported at module
level, and the output root, under which the script creates its run folder.
detcheck.py carried its own function to read --archive and --outdir from
argv early. calprec.py and costprobe.py were about to get copies of the same
function, which would have meant three copies free to drift apart. This file
holds the one copy, and each script imports it.

WHAT IT DOES
------------
  early_flag(name, default, argv=None)
      Returns VALUE from "name VALUE" or "name=VALUE" in argv (default
      sys.argv), the first occurrence; otherwise default. The scripts still
      declare both flags in argparse, so --help lists them and an unknown flag
      is still an error.
  archive_path(root, argv=None, environ=None)
      --archive if given, else the environment variable CBOGAP_ARCHIVE, else
      <root>/zenodo-v1.
  output_root(root, argv=None, environ=None)
      --outdir if given, else CBOGAP_OUTDIR, else <root>/runs.
  root is the repository root, computed by the calling script from its own
  __file__, exactly as before this file existed.

Worked example. With argv ["detcheck.py", "--workers", "2", "--archive",
"/home/rahul/cbo-archive-test"], CBOGAP_ARCHIVE unset and root
"/home/rahul/Research/cbo-gap-final":
  archive_path(root) -> "/home/rahul/cbo-archive-test"
  output_root(root)  -> "/home/rahul/Research/cbo-gap-final/runs"
With argv ["calprec.py", "--outdir=/kaggle/working"] and CBOGAP_ARCHIVE set to
"/kaggle/input/cbo-gap-archive":
  archive_path(root) -> "/kaggle/input/cbo-gap-archive"
  output_root(root)  -> "/kaggle/working"

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
  It resolves paths and nothing else. It does not check that the archive or
  the output root exists, it does not create anything, it never prints, and
  it never exits. The existence check, its error message and exit code 2
  stay in each calling script, where the setup error belongs. Importing it
  has no side effects: it defines functions and nothing else.

Standard library only. Python 3.8 to 3.11 syntax.
"""

import os
import sys


def early_flag(name, default, argv=None):
    """Read --name VALUE (or --name=VALUE) from argv before argparse runs."""
    if argv is None:
        argv = sys.argv
    for i, tok in enumerate(argv):
        if tok == name and i + 1 < len(argv):
            return argv[i + 1]
        if tok.startswith(name + "="):
            return tok.split("=", 1)[1]
    return default


def archive_path(root, argv=None, environ=None):
    """--archive, else CBOGAP_ARCHIVE, else <root>/zenodo-v1. Not checked."""
    if environ is None:
        environ = os.environ
    return early_flag("--archive", environ.get("CBOGAP_ARCHIVE",
                                               os.path.join(root, "zenodo-v1")), argv)


def output_root(root, argv=None, environ=None):
    """--outdir, else CBOGAP_OUTDIR, else <root>/runs. Not checked."""
    if environ is None:
        environ = os.environ
    return early_flag("--outdir", environ.get("CBOGAP_OUTDIR",
                                              os.path.join(root, "runs")), argv)
