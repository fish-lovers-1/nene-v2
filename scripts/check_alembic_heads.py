import subprocess
import sys

result = subprocess.run(
    ["uv", "run", "--directory", "nene-bot", "alembic", "heads"],
    capture_output=True,
    text=True,
    check=False,
)

if result.returncode != 0:
    print(result.stderr, end="")
    sys.exit(result.returncode)

heads = [line for line in result.stdout.splitlines() if line.strip()]

if len(heads) != 1:
    print(f"Alembic has {len(heads)} heads; expected exactly 1.")
    print(result.stdout, end="")
    sys.exit(1)
