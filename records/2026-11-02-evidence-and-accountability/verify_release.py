"""Entry point for the NEW 2026-11-02 edition; earlier verifier remains preserved."""
from pathlib import Path
import runpy
import sys

root = Path(__file__).resolve().parent
if len(sys.argv) == 1:
    sys.argv += ['--root', str(root)]
runpy.run_path(str(root / 'helpers' / 'verify_release.py'), run_name='__main__')
