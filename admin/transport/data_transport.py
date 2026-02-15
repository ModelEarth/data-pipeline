#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git-based CSV transporter with dual reports and requested features:

1) Add an HTML comment before each moved file entry in the report containing src/dst path
2) Append Top-10 largest remaining files (in source repo) at the end of moved-csv.md
3) Allow omitting some CSVs (glob / exact / size-based) e.g. keep node.csv at root
4) Provide delete-after-copy step, but KEEP IT OFF for deployment review

Flow:
- Clone target repo, checkout/create work branch (avoid pushing main directly)
- Copy ALL .csv from SOURCE_DIR -> TARGET_PREFIX in target repo (preserving structure)
- Optionally retain some CSVs in source repo (won't be copied)
- Optionally LFS-track large CSVs (or all CSVs)
- Generate moved-csv.md locally & remotely, with comment lines before each move
- Commit & push data + report to remote branch; then open PR on GitHub

Run in the root of your local data-pipeline repo:
  python admin/transport/data_transport.py
"""

import os
import sys
import csv
import shutil
import tempfile
import subprocess
from pathlib import Path
from fnmatch import fnmatch

# ========== BASIC CONFIG ==========
OWNER         = "ModelEarth"   # e.g. "sltan0331"
REPO          = "data-pipe-csv"
BRANCH        = "main"                     # work branch; open PR to main later
SOURCE_DIR    = "."                              # scan CSVs from here (your data-pipeline root)
TARGET_PREFIX = ""                               # destination root in target repo (empty = repo root)

# ========== LOCAL OUTPUT CONFIG ==========
OUTPUT_LOCAL_PATH = "data-pipe-csv"              # If set, outputs locally instead of GitHub

# ========== REPORT CONFIG ==========
#Report setup
#Group datasets by first N path levels relative to SOURCE_DIR(1 = top-level folder; 2 = two-levels)
#e.g. Suppose I have states/commodities/2020/CA.csv and international/comtrade/export.csv exported.
#If REPORT_GROUPS_LEVELS=1, then I'll have groups states, international in the report.
#If REPORT_GROUPS_LEVELS=2, then I'll have groups states/commodities, international/comtrade in the report.
REPORT_GROUP_LEVELS     = 1     
#Report location. A moved-csv is created as md (md file type for better looking) to report what csv files are exported.
REPORT_LOCAL_PATH       = "moved-csv.md"         # written into SOURCE_DIR root
REPORT_REMOTE_PATH      = "moved-csv.md"         # path inside target repo; or f"{TARGET_PREFIX}/moved-csv.md"
ENABLE_LARGEST_SECTION  = True                   # add "largest remaining files" tail section
REPORT_TOP_N_LARGEST    = 10

# ========== RETAIN / OMIT RULES ==========
#omit/retain rules (files that will NOT be relocated)
ENABLE_RETAIN_RULES = True
# What files are omitted
OMIT_CSV_GLOBS = [
    "node.csv",        
]
# Exact relative paths (relative to LOCAL_DIR)
OMIT_CSV_REL_PATHS = { }

def should_omit_by_size(rel_path: str, abs_path: str) -> bool:
    # return os.path.getsize(abs_path) < 5 * 1024
    return False

# ========== LFS CONFIG ==========
TRACK_ALL_CSV_WITH_LFS = False                   # If True, then all filkes are transported through LFS.If False, then only csvs larger than threshold will be transported through LFS.
LFS_THRESHOLD_MB       = 90                      # Threshold for transport through LFS.

# ========== DELETE AFTER COPY (KEEP OFF) ==========
DELETE_LOCAL_AFTER_COPY = False  # If True, files will be deleted after moving.

# ========== AUTH FOR REMOTE (optional) ==========
USE_TOKEN_REMOTE = False  # False is used for the case that git is already logged in on the computer. 
# If git is not logged in on the computer, then export/set GITHUB_TOKEN=ghp_xxx need to be used.

# ================== UTILITIES ==================
def run(cmd, cwd=None, check=True):
    print(f"$ {' '.join(cmd)}" + (f"  (cwd={cwd})" if cwd else ""))
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.stdout: print(p.stdout.rstrip())
    if p.stderr: print(p.stderr.rstrip())
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return p

def ensure_tool_exists(tool):
    try:
        run([tool, "--version"], check=True)
    except Exception:
        raise SystemExit(f"Required tool '{tool}' not found. Please install it and try again.")

def build_remote_url(owner, repo):
    base = f"https://github.com/{owner}/{repo}.git"
    if not USE_TOKEN_REMOTE:
        return base
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("USE_TOKEN_REMOTE=True but GITHUB_TOKEN is not set.")
    # WARNING: token will be saved in .git/config; remove it after push if you use this.
    return f"https://{token}@github.com/{owner}/{repo}.git"

def human_size(nbytes: int) -> str:
    """
    Convert file size from bytes to human reable size. The maximum unit is TB.
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(nbytes)
    for u in units:
        if size < 1024 or u == "TB":
            return f"{size:.1f} {u}"
        size /= 1024.0

def posix_rel(p: Path) -> str:
    """
    Convert "\" in pathes into "/" for safety.
    """
    return p.as_posix()

def group_key_for(rel_path: str) -> str:
    """
    Convert the first N path segments (without filename) into names of the dataset group in the report.
    """
    parts = rel_path.split("/")
    if len(parts) <= REPORT_GROUP_LEVELS:
        return "/".join(parts[:-1]) or "."
    return "/".join(parts[:REPORT_GROUP_LEVELS])

def collect_csvs(src_root: Path, exclude_dirs=None):
    """Collect CSV files from src_root, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    csvs = []
    for p in src_root.rglob("*.csv"):
        if not p.is_file():
            continue
        
        # Check if the file is in any excluded directory
        excluded = False
        for exclude_dir in exclude_dirs:
            try:
                # Check if the CSV file path is relative to any excluded directory
                p.relative_to(src_root / exclude_dir)
                excluded = True
                break
            except ValueError:
                # File is not in this excluded directory, continue checking
                continue
        
        if not excluded:
            csvs.append(p)
    
    return csvs

def should_retain(rel_path: str, abs_path: Path) -> bool:
    if not ENABLE_RETAIN_RULES:
        return False
    if rel_path in OMIT_CSV_REL_PATHS:
        return True
    if any(fnmatch(rel_path, pat) for pat in OMIT_CSV_GLOBS):
        return True
    if should_omit_by_size(rel_path, str(abs_path)):
        return True
    return False

def copy_preserve_structure(csv_files, source_root: Path, dest_root: Path,
                            retained_out: list, moved_out: list):
    """
    retained_out: [(rel, size)]
    moved_out:    [(src_rel, dst_rel, size)]
    """
    for f in csv_files:
        rel = posix_rel(f.relative_to(source_root))
        if should_retain(rel, f):
            retained_out.append((rel, f.stat().st_size))
            print(f"[SKIP] retained (not moved): {rel}")
            continue

        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        size = dest.stat().st_size
        dst_rel = posix_rel((Path(TARGET_PREFIX) / rel)) if TARGET_PREFIX else rel
        moved_out.append((rel, dst_rel, size))
        print(f"[COPY] {rel} -> {dest}")

        if DELETE_LOCAL_AFTER_COPY:
            try:
                os.remove(f)
                print(f"[DEL] local removed: {rel}")
            except Exception as e:
                print(f"[WARN] failed to delete local file {rel}: {e}")

def is_lfs_installed():
    try:
        run(["git", "lfs", "version"], check=True)
        return True
    except Exception:
        return False

def lfs_track(repo_dir: Path, patterns):
    if not patterns:
        return
    run(["git", "lfs", "install"], cwd=repo_dir, check=True)
    for pat in patterns:
        run(["git", "lfs", "track", pat], cwd=repo_dir, check=True)
    gitattributes = repo_dir / ".gitattributes"
    if gitattributes.exists():
        run(["git", "add", ".gitattributes"], cwd=repo_dir, check=True)

def largest_remaining(source_root: Path, moved_rel_set: set, top_n: int, exclude_dirs=None):
    """Scan SOURCE_DIR for remaining files (exclude moved CSVs), return top N by size."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    ignore_names = {".git", ".github", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"}
    all_files = []
    for p in source_root.rglob("*"):
        name = p.name
        if p.is_dir():
            if name in ignore_names or name.startswith("."):
                continue
            continue
        
        # Check if file is in any excluded directory
        excluded = False
        for exclude_dir in exclude_dirs:
            try:
                p.relative_to(source_root / exclude_dir)
                excluded = True
                break
            except ValueError:
                continue
        
        if excluded:
            continue
            
        rel = posix_rel(p.relative_to(source_root))
        if rel in moved_rel_set:
            continue
        try:
            sz = p.stat().st_size
        except OSError:
            continue
        all_files.append((rel, sz))
    all_files.sort(key=lambda x: x[1], reverse=True)
    return all_files[:top_n] if top_n and top_n > 0 else all_files

def build_report_text(moved, retained, largest, title="# Moved CSV Report"):
    """
    moved:    list of (src_rel, dst_rel, size)
    retained: list of (rel, size)
    largest:  list of (rel, size)
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [title, "_This file is auto-generated by git transport script._", ""]

    # group moved by group key
    grouped = {}
    for src_rel, dst_rel, size in moved:
        g = group_key_for(src_rel)
        grouped.setdefault(g, []).append((src_rel, dst_rel, size))

    # groups with HTML comment line BEFORE each move (for auto-update)
    for g in sorted(grouped.keys()):
        lines.append(f"## {g} — moved on {now}")
        for src_rel, dst_rel, size in sorted(grouped[g], key=lambda x: x[0]):
            # A line is added for each file moved.
            lines.append(f"<!-- MOVE: {src_rel} -> {dst_rel} -->")
            lines.append(f"- `{src_rel}` → `{dst_rel}`  ({human_size(size)})")
        lines.append(f"\n**Files moved**: {len(grouped[g])}\n")

    # retained
    if retained:
        lines.append("### Retained CSVs (not relocated)")
        for rel, sz in sorted(retained, key=lambda x: x[0]):
            lines.append(f"- `{rel}`  ({human_size(sz)})")
        lines.append("")

    # largest remaining
    if largest is not None:
        if largest:
            lines.append(f"### Largest remaining files (top {len(largest)})")
            for rel, sz in largest:
                lines.append(f"- `{rel}`  ({human_size(sz)})")
            lines.append("")
        else:
            lines.append("### Largest remaining files\n_(No remaining files found)_\n")

    return "\n".join(lines).strip() + "\n"

# ================== MAIN ==================
def main():
    src_root = Path(SOURCE_DIR).resolve()
    if not src_root.exists():
        raise SystemExit(f"SOURCE_DIR not found: {src_root}")

    # Determine directories to exclude
    exclude_dirs = []
    if OUTPUT_LOCAL_PATH:
        exclude_dirs.append(OUTPUT_LOCAL_PATH)
    
    # Collect CSVs first (excluding output directory)
    csvs = collect_csvs(src_root, exclude_dirs)
    if not csvs:
        print("No CSV files found under:", src_root)
        return

    moved = []      # (src_rel, dst_rel, size)
    retained = []   # (rel, size)

    # Check if using local output mode
    if OUTPUT_LOCAL_PATH:
        print(f"[LOCAL MODE] Outputting to local directory: {OUTPUT_LOCAL_PATH}")
        
        # Create local output directory
        local_output_dir = src_root / OUTPUT_LOCAL_PATH
        local_output_dir.mkdir(parents=True, exist_ok=True)
        
        dest_root = local_output_dir / TARGET_PREFIX if TARGET_PREFIX else local_output_dir
        dest_root.mkdir(parents=True, exist_ok=True)

        # Copy files (respect retain rules)
        copy_preserve_structure(csvs, src_root, dest_root, retained_out=retained, moved_out=moved)

        # Build report text
        moved_rel_set = set(src for src, _, _ in moved)
        largest = largest_remaining(src_root, moved_rel_set, REPORT_TOP_N_LARGEST, exclude_dirs) if ENABLE_LARGEST_SECTION else None
        report_text = build_report_text(moved, retained, largest, title="# Local CSV Transport Report")

        # Write report to local output directory
        report_path = local_output_dir / REPORT_REMOTE_PATH
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
        print(f"[REPORT] written to: {report_path}")

        print(f"\n[LOCAL MODE] Files copied to: {dest_root}")
        print(f"[LOCAL MODE] Report written to: {report_path}")
        
    else:
        # Original GitHub mode
        ensure_tool_exists("git")
        remote = build_remote_url(OWNER, REPO)

        with tempfile.TemporaryDirectory(prefix="data-sync-") as tmp:
            repo_dir = Path(tmp) / "repo"
            # clone + checkout/create work branch
            run(["git", "clone", "--depth", "1", remote, str(repo_dir)], check=True)
            run(["git", "fetch", "origin"], cwd=repo_dir, check=True)
            rc = run(["git", "checkout", BRANCH], cwd=repo_dir, check=False)
            if rc.returncode != 0:
                run(["git", "checkout", "-b", BRANCH], cwd=repo_dir, check=True)
                run(["git", "push", "-u", "origin", BRANCH], cwd=repo_dir, check=True)

            run(["git","pull","--rebase","origin",BRANCH],cwd=repo_dir, check=True)
            
            dest_root = repo_dir / TARGET_PREFIX if TARGET_PREFIX else repo_dir
            dest_root.mkdir(parents=True, exist_ok=True)

            # Copy files (respect retain rules)
            copy_preserve_structure(csvs, src_root, dest_root, retained_out=retained, moved_out=moved)

            # Decide LFS tracking
            lfs_patterns = []
            if TRACK_ALL_CSV_WITH_LFS:
                if TARGET_PREFIX:
                    lfs_patterns.append(f"{TARGET_PREFIX}/**/*.csv")
                else:
                    lfs_patterns.append("**/*.csv")
            else:
                threshold = LFS_THRESHOLD_MB * 1024 * 1024
                for _, dst_rel, size in moved:
                    if size >= threshold:
                        lfs_patterns.append(dst_rel)  # track specific large files

            if lfs_patterns:
                if is_lfs_installed():
                    print("[LFS] tracking patterns:")
                    for p in lfs_patterns: print("  -", p)
                    lfs_track(repo_dir, lfs_patterns)
                else:
                    print("[WARN] Git LFS not installed; large files won't be pointered (repo may bloat).")

            # Build report text
            moved_rel_set = set(src for src, _, _ in moved)
            largest = largest_remaining(src_root, moved_rel_set, REPORT_TOP_N_LARGEST, exclude_dirs) if ENABLE_LARGEST_SECTION else None
            report_text = build_report_text(moved, retained, largest)

            # Write remote report
            report_remote_path = repo_dir / REPORT_REMOTE_PATH
            report_remote_path.parent.mkdir(parents=True, exist_ok=True)
            report_remote_path.write_text(report_text, encoding="utf-8")
            print(f"[REPORT] remote written: {report_remote_path}")

            # Stage + commit + push (data + report)
            if TARGET_PREFIX:
                run(["git", "add", TARGET_PREFIX], cwd=repo_dir, check=True)
            else:
                run(["git", "add", "."], cwd=repo_dir, check=True)
            run(["git", "add", REPORT_REMOTE_PATH], cwd=repo_dir, check=True)

            status = run(["git", "status", "--porcelain"], cwd=repo_dir, check=True)
            if not status.stdout.strip():
                print("Nothing to commit. Done.")
                return

            run(["git", "commit", "-m", "chore(data): migrate CSV and update moved-csv report"], cwd=repo_dir, check=True)
            run(["git","pull","--rebase","origin",BRANCH],cwd=repo_dir, check=True)
            run(["git", "push", "origin", BRANCH], cwd=repo_dir, check=True)

            print("\n Data and remote report pushed.")
            print(f"   Open PR: https://github.com/{OWNER}/{REPO}/compare/{BRANCH}?expand=1")

    # Write local report (in both modes)
    local_report = src_root / REPORT_LOCAL_PATH
    local_report.write_text(report_text, encoding="utf-8")
    print(f"[REPORT] local written: {local_report}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)
