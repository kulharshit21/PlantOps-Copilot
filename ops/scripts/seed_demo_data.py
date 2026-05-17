from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is required. Example: postgresql://postgres:postgres@localhost:54322/postgres")
        return 2

    psql = shutil.which("psql")
    if not psql:
        print("psql was not found on PATH. Install PostgreSQL client tools or run supabase/seed.sql manually.")
        return 2

    repo_root = Path(__file__).resolve().parents[2]
    seed_file = repo_root / "supabase" / "seed.sql"
    result = subprocess.run([psql, database_url, "-v", "ON_ERROR_STOP=1", "-f", str(seed_file)], check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
