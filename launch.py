import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.exists():
    raise SystemExit("Run python setup.py first.")
raise SystemExit(subprocess.call([str(python), "-m", "autoshift"], cwd=root))
