"""Run offline tests with optional project-local dependencies, without network.

Install first if needed:
  python -m pip install --target .testdeps pytest==8.4.2
"""
from pathlib import Path
import os
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
if (root / ".testdeps").is_dir():
    sys.path.insert(0, str(root / ".testdeps"))
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
os.chdir(root)
import pytest

if __name__ == "__main__":
    raise SystemExit(pytest.main(sys.argv[1:] or ["-q"]))
