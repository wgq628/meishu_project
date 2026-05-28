#!/usr/bin/env python3
"""kunlun-ecosystem bootstrap for Codex workspace."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REQUIRED_SKILLS = [
    "kunlun-core",
    "kunlun-academy",
    "kunlun-dashboard",
    "kunlun-governance",
    "kunlun-knowledge-structure",
    "kunlun-metacognition",
    "kunlun-onboarding",
    "kunlun-output-packaging",
    "kunlun-session-recovery",
]


def main() -> None:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass
    root = Path.cwd().resolve()
    skills_root = root / "skills"
    missing = [s for s in REQUIRED_SKILLS if not (skills_root / s).is_dir()]
    if missing:
        print("[WARN] Missing skill directories:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("[OK] All required Kunlun skills directories exist")

    core_bootstrap = skills_root / "kunlun-core" / "scripts" / "bootstrap_codex.py"
    if not core_bootstrap.is_file():
        print(f"[ERROR] core bootstrap not found: {core_bootstrap}")
        sys.exit(1)

    print("[RUN] Running kunlun-core Codex bootstrap...")
    result = subprocess.run([sys.executable, str(core_bootstrap)], cwd=str(root))
    if result.returncode != 0:
        print("[ERROR] core bootstrap failed")
        sys.exit(result.returncode)

    print("[OK] Kunlun ecosystem Codex bootstrap completed")


if __name__ == "__main__":
    main()
