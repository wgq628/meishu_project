#!/usr/bin/env python3
"""kunlun-core bootstrap for Codex workspace."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def resolve_root() -> Path:
    env_root = os.environ.get("KUNLUN_WORKSPACE") or os.environ.get("OPENCLAW_WORKSPACE")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.cwd().resolve()


def copy_if_missing(src: Path, dst: Path) -> bool:
    if dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text("utf-8", errors="ignore"), "utf-8")
    return True


def ensure_tools_append(root: Path, template: Path) -> bool:
    marker = "# 昆仑认知系统规则（kunlun-core 自动注入）"
    dst = root / "TOOLS.md"
    addon = template.read_text("utf-8", errors="ignore")
    if dst.exists():
        cur = dst.read_text("utf-8", errors="ignore")
        if marker in cur:
            return False
        if not cur.endswith("\n"):
            cur += "\n"
        dst.write_text(cur + addon, "utf-8")
        return True
    dst.write_text(addon, "utf-8")
    return True


def main() -> None:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass
    root = resolve_root()
    skill_dir = Path(__file__).resolve().parent.parent
    tmpl = skill_dir / "scripts" / "templates"
    bridge_tmpl = skill_dir / "scripts" / "bridge-templates"

    created = []
    skipped = []

    root_files = {
        "SOUL.md": "SOUL.md",
        "IDENTITY.md": "IDENTITY.md",
        "contract.md": "contract.md",
        "VERSION.md": "VERSION.md",
    }
    for name, src_name in root_files.items():
        src = tmpl / src_name
        dst = root / name
        if copy_if_missing(src, dst):
            created.append(str(dst))
        else:
            skipped.append(str(dst))

    # Codex flavor: use knowledge-tree as primary bridge registry directory.
    bridge_dir = root / "knowledge-tree"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in [
        ("registry.md", "registry.md"),
        ("NOMENCLATURE.md", "NOMENCLATURE.md"),
        ("lifecycle-protocol.md", "lifecycle-protocol.md"),
        ("bridge-memory-protocol.md", "bridge-memory-protocol.md"),
    ]:
        src = bridge_tmpl / src_name
        dst = bridge_dir / dst_name
        if copy_if_missing(src, dst):
            created.append(str(dst))
        else:
            skipped.append(str(dst))

    memory_dir = root / "memory"
    (memory_dir / "analysis").mkdir(parents=True, exist_ok=True)
    (memory_dir / "views").mkdir(parents=True, exist_ok=True)

    memory_files = [
        "MEMORY.md",
        "memory-index.md",
        "resonance-net.md",
        "anti-fragility-pool.md",
        "failure-log.md",
        "metacognitive-protocol.md",
    ]
    for name in memory_files:
        src = tmpl / name
        dst = memory_dir / name
        if copy_if_missing(src, dst):
            created.append(str(dst))
        else:
            skipped.append(str(dst))

    # Keep root-level aliases for dashboard compatibility.
    for name in ["memory-index.md", "resonance-net.md", "anti-fragility-pool.md"]:
        src = memory_dir / name
        dst = root / name
        if dst.exists():
            skipped.append(str(dst))
            continue
        if src.exists():
            dst.write_text(src.read_text("utf-8", errors="ignore"), "utf-8")
            created.append(str(dst))

    for name in [
        "axiom-cards-index.md",
        "study-cards-index.md",
        "bridge-cards-index.md",
        "case-library-index.md",
    ]:
        src = tmpl / name
        dst = memory_dir / "views" / name
        if copy_if_missing(src, dst):
            created.append(str(dst))
        else:
            skipped.append(str(dst))

    if ensure_tools_append(root, tmpl / "TOOLS-append.md"):
        created.append(str(root / "TOOLS.md"))
    else:
        skipped.append(str(root / "TOOLS.md"))

    init_flag = root / ".kunlun-initialized"
    if not init_flag.exists():
        init_flag.write_text("initialized-by=bootstrap_codex.py\n", "utf-8")
        created.append(str(init_flag))
    else:
        skipped.append(str(init_flag))

    print("[OK] Kunlun Codex bootstrap completed")
    print(f"workspace: {root}")
    print(f"created: {len(created)}")
    print(f"skipped: {len(skipped)}")


if __name__ == "__main__":
    main()
