"""Create the local environment and install Auto Shift. Run with Python 3.12."""
import os
import subprocess
import sys
import venv
from pathlib import Path

root = Path(__file__).resolve().parent
if sys.version_info < (3, 11):
    raise SystemExit("Install Python 3.12 or newer, then run this setup again.")
venv.EnvBuilder(with_pip=True).create(root / ".venv")
python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
subprocess.run([str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")], check=True)
subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)
print("Setup complete. Start with START_WINDOWS.cmd or: python launch.py")
print("On Linux, missing Chromium system libraries may require:")
print(str(python) + " -m playwright install-deps chromium")
