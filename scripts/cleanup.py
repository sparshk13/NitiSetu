#!/usr/bin/env python3
"""NitiSetu Repository Cleanup & Audit Tool

Usage:
    python scripts/cleanup.py           # Default: dry-run
    python scripts/cleanup.py --dry-run # Explicit dry-run
    python scripts/cleanup.py --apply   # Safely remove approved generated artifacts
    python scripts/cleanup.py --report  # Audit codebase for AI leftovers, TODOs, debug logs
"""

import os
import sys
import argparse
import re
from pathlib import Path

# Explicit allowlist of safe-to-remove relative directory names and file patterns
SAFE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "coverage",
    "playwright-report",
    "test-results",
}

SAFE_FILE_NAMES = {
    ".DS_Store",
    ".coverage",
}

SAFE_FILE_EXTENSIONS = {
    ".pyc",
    ".pyo",
}

# Directories to skip when scanning / auditing
IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
}


def get_repo_root() -> Path:
    """Resolve and validate the repository root directory."""
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent

    # Safety checks
    if repo_root == Path("/") or repo_root == Path.home():
        raise RuntimeError(f"Refusing to operate on root or home directory: {repo_root}")

    # Ensure expected project indicators exist
    if not (repo_root / "data").exists() and not (repo_root / "Docs").exists():
        raise RuntimeError(f"Directory {repo_root} does not appear to be NitiSetu repository.")

    return repo_root


def scan_safe_artifacts(repo_root: Path):
    """Find all safe-to-remove artifacts matching the explicit allowlist."""
    targets = []

    for root, dirs, files in os.walk(repo_root, followlinks=False):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        current_path = Path(root)

        # Check directories
        for d in list(dirs):
            if d in SAFE_DIR_NAMES:
                target_dir = current_path / d
                if not target_dir.is_symlink():
                    targets.append(("dir", target_dir))
                    dirs.remove(d)  # Don't recurse into directory slated for removal
            elif d == "dist" and (current_path / "package.json").exists():
                # Only clean dist if it's confirmed as a frontend build artifact
                targets.append(("dir", current_path / d))
                dirs.remove(d)

        # Check files
        for f in files:
            file_path = current_path / f
            if file_path.is_symlink():
                continue

            if f in SAFE_FILE_NAMES or file_path.suffix.lower() in SAFE_FILE_EXTENSIONS:
                targets.append(("file", file_path))

    return targets


def run_cleanup(repo_root: Path, apply: bool = False):
    """Execute cleanup: dry-run by default, or delete if apply=True."""
    mode = "APPLY (DELETION)" if apply else "DRY-RUN (NO DELETION)"
    print(f"\n=======================================================")
    print(f" NitiSetu Cleanup: {mode}")
    print(f" Target Repository: {repo_root}")
    print(f"=======================================================\n")

    targets = scan_safe_artifacts(repo_root)

    if not targets:
        print("✓ No safe cleanup artifacts found. Repository is already clean.")
        return 0

    print(f"Found {len(targets)} candidate artifact(s):\n")
    bytes_freed = 0

    for kind, path in targets:
        rel_path = path.relative_to(repo_root)
        try:
            if kind == "file":
                size = path.stat().st_size
            else:
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            bytes_freed += size
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.2f} MB"
        except Exception:
            size_str = "unknown size"

        print(f"  [{kind.upper()}] {rel_path} ({size_str})")

        if apply:
            try:
                if kind == "file":
                    path.unlink()
                else:
                    import shutil
                    shutil.rmtree(path)
                print(f"    ✓ Removed {rel_path}")
            except Exception as e:
                print(f"    ✗ Error removing {rel_path}: {e}", file=sys.stderr)

    mb_freed = bytes_freed / (1024 * 1024)
    if apply:
        print(f"\n✓ Successfully removed {len(targets)} artifact(s) (approx {mb_freed:.2f} MB freed).")
    else:
        print(f"\n[DRY RUN COMPLETE] Total reclaimable space: ~{mb_freed:.2f} MB.")
        print("To execute deletion, run with: python scripts/cleanup.py --apply\n")

    return 0


def run_audit_report(repo_root: Path):
    """Audit codebase for AI leftovers, TODOs, debug statements, and placeholder text."""
    print(f"\n=======================================================")
    print(f" NitiSetu Codebase Quality Audit Report")
    print(f" Target: {repo_root}")
    print(f"=======================================================\n")

    audit_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md"}
    findings = []

    patterns = [
        (re.compile(r'\b(TODO|FIXME|HACK|XXX)\b', re.IGNORECASE), "Unresolved TODO/FIXME annotation"),
        (re.compile(r'console\.log\(|print\(f?["\'](DEBUG|test)', re.IGNORECASE), "Potential debug logging statement"),
        (re.compile(r'lorem\s+ipsum', re.IGNORECASE), "Placeholder lorem ipsum text"),
        (re.compile(r'(\bexample\.com\b|test@test\.com)', re.IGNORECASE), "Synthetic placeholder domain/email"),
    ]

    for root, dirs, files in os.walk(repo_root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and d not in SAFE_DIR_NAMES]
        current_path = Path(root)

        # Do not audit node_modules or .git
        for f in files:
            file_path = current_path / f
            if file_path.suffix.lower() not in audit_extensions:
                continue
            if file_path.is_symlink():
                continue

            rel_path = file_path.relative_to(repo_root)

            # Skip checking the cleanup tool itself or raw datasets
            if str(rel_path).startswith("scripts/cleanup.py") or str(rel_path).startswith("data/"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                    for line_num, line in enumerate(fp, 1):
                        for regex, issue_desc in patterns:
                            if regex.search(line):
                                findings.append({
                                    "file": str(rel_path),
                                    "line": line_num,
                                    "desc": issue_desc,
                                    "snippet": line.strip()[:100]
                                })
            except Exception:
                pass

    if not findings:
        print("✓ Audit passed cleanly! No suspicious placeholders, debug prints, or unresolved TODOs found.")
    else:
        print(f"Found {len(findings)} items recommended for manual review:\n")
        for item in findings:
            print(f"  • {item['file']}:{item['line']} - [{item['desc']}]")
            print(f"      Code: {item['snippet']}")
        print("\nNote: Audit findings are informational. No code was modified.")

    return 0


def main():
    parser = argparse.ArgumentParser(description="NitiSetu cleanup and code quality tool.")
    parser.add_argument("--dry-run", action="store_true", help="Print safe cleanup targets without deleting (default).")
    parser.add_argument("--apply", action="store_true", help="Delete allowlisted safe artifacts.")
    parser.add_argument("--report", action="store_true", help="Audit repository for AI leftovers, TODOs, and debug statements.")

    args = parser.parse_args()
    repo_root = get_repo_root()

    if args.report:
        return run_audit_report(repo_root)
    elif args.apply:
        return run_cleanup(repo_root, apply=True)
    else:
        return run_cleanup(repo_root, apply=False)


if __name__ == "__main__":
    sys.exit(main())

