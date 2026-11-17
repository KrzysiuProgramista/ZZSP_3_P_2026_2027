import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parent
python = root / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
if not python.is_file():
    raise SystemExit("Run python install.py first.")
args = sys.argv[1:]
if args and args[0] == "--inspect":
    command = [str(python), str(root / "inspect_librus_pdf.py"), *args[1:]]
elif args and args[0] == "--test":
    command = [str(python), "-m", "pytest", str(root / "test_starter.py"), *args[1:]]
else:
    command = [str(python), str(root / "starter.py"), *args]
raise SystemExit(subprocess.call(command, cwd=root))
