#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Git-based CSV transporter with nodes.csv integration

NEW FEATURES:
1) Updates nodes.csv with actual file sizes and output paths
2) Enhanced retention rules for lookup/crosswalk files
3) Generates a mapping report showing which files belong to which nodes
4) Adds new columns to nodes.csv: actual_size_mb, csv_file_count, last_transport_date

Flow:
- Clone target repo, checkout/create work branch (avoid pushing main directly)
- Copy ALL .csv from SOURCE_DIR -> TARGET_PREFIX in target repo (preserving structure)
- Match CSV files to nodes in nodes.csv by folder path
- Update nodes.csv with actual sizes and transport destinations
- Optionally retain lookup/crosswalk CSVs in source repo (won't be copied)
- Generate moved-csv.md locally & remotely, with comment lines before each move
- Commit & push data + report + updated nodes.csv to remote branch

Run in the root of your local data-pipeline repo:
  python admin/transport/data_transport_enhanced.py
"""

import os
import sys
import csv
import shutil
import tempfile
import subprocess
from pathlib import Path
from fnmatch import fnmatch
from datetime import datetime, timezone
from collections import defaultdict

# ========== BASIC CONFIG ==========
OWNER         = "ModelEarth"
REPO          = "data-pipe-csv"
BRANCH        = "main"
SOURCE_DIR    = "."
TARGET_PREFIX = ""

# ========== LOCAL OUTPUT CONFIG ==========
OUTPUT_LOCAL_PATH = "data-pipe-csv"

# ========== NODES.CSV INTEGRATION ==========
NODES_CSV_PATH = "nodes.csv"
UPDATE_NODES_CSV = True

# ========== REPORT CONFIG ==========
REPORT_GROUP_LEVELS     = 1
REPORT_LOCAL_PATH       = "moved-csv.md"
REPORT_REMOTE_PATH      = "moved-csv.md"
ENABLE_LARGEST_SECTION  = True
REPORT_TOP_N_LARGEST    = 10

# ========== RETAIN / OMIT RULES ==========
ENABLE_RETAIN_RULES = True

# Enhanced omit rules to include lookup/crosswalk files
OMIT_CSV_GLOBS = [
    "node.csv",
    "nodes.csv",
    "*crosswalk*.csv",
    "*_to_*.csv",
    "*fips*.csv",
    "*id_list*.csv",
    "*lookup*.csv",
]

# Directories to completely skip (don't transport anything from these)
OMIT_DIRECTORIES = [
    "timelines/prep/all/input",  # Input files for ML/regression
]

OMIT_CSV_REL_PATHS = {}

def should_omit_by_size(rel_path: str, abs_path: str) -> bool:
    return False

# ========== LFS CONFIG ==========
TRACK_ALL_CSV_WITH_LFS = False
LFS_THRESHOLD_MB       = 90

# ========== DELETE AFTER COPY (KEEP OFF) ==========
DELETE_LOCAL_AFTER_COPY = False

# ========== AUTH FOR REMOTE (optional) ==========
USE_TOKEN_REMOTE = False

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
    return f"https://{token}@github.com/{owner}/{repo}.git"

def human_size(nbytes: int) -> str:
    """Convert file size from bytes to human readable size."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(nbytes)
    for u in units:
        if size < 1024 or u == "TB":
            return f"{size:.1f} {u}"
        size /= 1024.0

def bytes_to_mb(nbytes: int) -> float:
    """Convert bytes to megabytes."""
    return round(nbytes / (1024 * 1024), 2)

def posix_rel(p: Path) -> str:
    """Convert path separators to forward slashes."""
    return p.as_posix()

def group_key_for(rel_path: str) -> str:
    """Get group key based on first N path segments."""
    parts = rel_path.split("/")
    if len(parts) <= REPORT_GROUP_LEVELS:
        return "/".join(parts[:-1]) or "."
    return "/".join(parts[:REPORT_GROUP_LEVELS])

def is_in_omit_directory(rel_path: str) -> bool:
    """Check if file is in any omitted directory."""
    for omit_dir in OMIT_DIRECTORIES:
        if rel_path.startswith(omit_dir + "/") or rel_path.startswith(omit_dir):
            return True
    return False

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
                p.relative_to(src_root / exclude_dir)
                excluded = True
                break
            except ValueError:
                continue

        if not excluded:
            csvs.append(p)

    return csvs

def should_retain(rel_path: str, abs_path: Path) -> bool:
    """Determine if a file should be retained (not moved)."""
    if not ENABLE_RETAIN_RULES:
        return False

    # Check if in omitted directory
    if is_in_omit_directory(rel_path):
        return True

    # Check exact paths
    if rel_path in OMIT_CSV_REL_PATHS:
        return True

    # Check glob patterns
    filename = Path(rel_path).name
    if any(fnmatch(filename, pat) for pat in OMIT_CSV_GLOBS):
        return True

    # Check size-based rules
    if should_omit_by_size(rel_path, str(abs_path)):
        return True

    return False

def load_nodes_csv(nodes_path: Path):
    """Load nodes.csv and return as list of dicts."""
    if not nodes_path.exists():
        print(f"[WARN] nodes.csv not found at {nodes_path}")
        return []

    nodes = []
    with open(nodes_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodes.append(row)

    return nodes

def save_nodes_csv(nodes_path: Path, nodes, fieldnames):
    """Save updated nodes.csv."""
    with open(nodes_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(nodes)

    print(f"[NODES] Updated {nodes_path}")

def match_files_to_nodes(nodes, moved_files):
    """
    Match moved CSV files to nodes based on output_path.

    Uses flexible matching:
    1. Exact prefix match (src_rel starts with output_path)
    2. Suffix match (src_rel ends with output_path + filename)
    3. Contains match (output_path is contained in src_rel)

    Returns:
        dict: node_id -> {files: [(rel, size)], total_size: int, count: int}
    """
    node_map = defaultdict(lambda: {"files": [], "total_size": 0, "count": 0})

    for node in nodes:
        node_id = node.get("node_id", "")
        output_path = node.get("output_path", "").strip()
        link = node.get("link", "").strip()

        if not output_path or not node_id:
            continue

        # Normalize output_path (remove leading/trailing slashes)
        output_path = output_path.strip("/")

        # Find matching files
        for src_rel, dst_rel, size in moved_files:
            matched = False

            # Strategy 1: Direct prefix match (most reliable)
            if src_rel.startswith(output_path):
                matched = True

            # Strategy 2: Check if file is in the link directory and output_path subdirectory
            elif link and output_path:
                # e.g., link="research/economy", output_path="states/commodities/2020/"
                # should match "research/economy/states/commodities/2020/CA.csv"
                combined_path = f"{link}/{output_path}".strip("/")
                if src_rel.startswith(combined_path):
                    matched = True

            # Strategy 3: Partial path match (contains the output path segment)
            elif f"/{output_path}/" in f"/{src_rel}/":
                matched = True

            if matched:
                node_map[node_id]["files"].append((src_rel, size))
                node_map[node_id]["total_size"] += size
                node_map[node_id]["count"] += 1

    return dict(node_map)

def update_nodes_with_transport_data(nodes, node_file_map, transport_date):
    """Update nodes list with actual file sizes and counts."""
    # Add new columns if they don't exist
    new_columns = ["actual_size_mb", "csv_file_count", "last_transport_date"]

    for node in nodes:
        node_id = node.get("node_id", "")

        # Initialize new columns if not present
        for col in new_columns:
            if col not in node:
                node[col] = ""

        # Update if we have data for this node
        if node_id in node_file_map:
            data = node_file_map[node_id]
            node["actual_size_mb"] = bytes_to_mb(data["total_size"])
            node["csv_file_count"] = data["count"]
            node["last_transport_date"] = transport_date

    return nodes

def copy_preserve_structure(csv_files, source_root: Path, dest_root: Path,
                            retained_out: list, moved_out: list):
    """
    Copy CSV files preserving structure.

    Args:
        retained_out: [(rel, size)]
        moved_out: [(src_rel, dst_rel, size)]
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
    """Build markdown report text."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [title, "_This file is auto-generated by git transport script._", ""]

    # Group moved by group key
    grouped = {}
    for src_rel, dst_rel, size in moved:
        g = group_key_for(src_rel)
        grouped.setdefault(g, []).append((src_rel, dst_rel, size))

    # Groups with HTML comment line BEFORE each move
    for g in sorted(grouped.keys()):
        lines.append(f"## {g} — moved on {now}")
        for src_rel, dst_rel, size in sorted(grouped[g], key=lambda x: x[0]):
            lines.append(f"<!-- MOVE: {src_rel} -> {dst_rel} -->")
            lines.append(f"- `{src_rel}` → `{dst_rel}`  ({human_size(size)})")
        lines.append(f"\n**Files moved**: {len(grouped[g])}\n")

    # Retained
    if retained:
        lines.append("### Retained CSVs (not relocated)")
        for rel, sz in sorted(retained, key=lambda x: x[0]):
            lines.append(f"- `{rel}`  ({human_size(sz)})")
        lines.append("")

    # Largest remaining
    if largest is not None:
        if largest:
            lines.append(f"### Largest remaining files (top {len(largest)})")
            for rel, sz in largest:
                lines.append(f"- `{rel}`  ({human_size(sz)})")
            lines.append("")
        else:
            lines.append("### Largest remaining files\n_(No remaining files found)_\n")

    return "\n".join(lines).strip() + "\n"

def build_node_mapping_report(node_file_map, nodes):
    """Build a report showing which files belong to which nodes."""
    lines = ["# Node-to-File Mapping Report", ""]
    lines.append("_This report shows which CSV files were mapped to which nodes in nodes.csv._\n")

    # Create a lookup dict for node info
    node_info = {n.get("node_id"): n for n in nodes}

    for node_id in sorted(node_file_map.keys()):
        data = node_file_map[node_id]
        node = node_info.get(node_id, {})
        node_name = node.get("name", "Unknown")

        lines.append(f"## {node_id}: {node_name}")
        lines.append(f"**Files**: {data['count']} | **Total Size**: {human_size(data['total_size'])}")
        lines.append("")

        for rel, size in sorted(data["files"], key=lambda x: x[0]):
            lines.append(f"- `{rel}` ({human_size(size)})")
        lines.append("")

    return "\n".join(lines)

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

        # Update nodes.csv if enabled
        if UPDATE_NODES_CSV:
            nodes_path = src_root / NODES_CSV_PATH
            nodes = load_nodes_csv(nodes_path)

            if nodes:
                # Match files to nodes
                transport_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                node_file_map = match_files_to_nodes(nodes, moved)

                # Update nodes with actual data
                original_fieldnames = list(nodes[0].keys()) if nodes else []
                updated_nodes = update_nodes_with_transport_data(nodes, node_file_map, transport_date)

                # Ensure new columns are in fieldnames
                new_fieldnames = list(updated_nodes[0].keys()) if updated_nodes else original_fieldnames

                # Save updated nodes.csv
                save_nodes_csv(nodes_path, updated_nodes, new_fieldnames)

                # Generate node mapping report
                mapping_report = build_node_mapping_report(node_file_map, updated_nodes)
                mapping_report_path = local_output_dir / "node-mapping.md"
                mapping_report_path.write_text(mapping_report, encoding="utf-8")
                print(f"[MAPPING] written to: {mapping_report_path}")

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
                        lfs_patterns.append(dst_rel)

            if lfs_patterns:
                if is_lfs_installed():
                    print("[LFS] tracking patterns:")
                    for p in lfs_patterns: print("  -", p)
                    lfs_track(repo_dir, lfs_patterns)
                else:
                    print("[WARN] Git LFS not installed; large files won't be pointered.")

            # Update nodes.csv if enabled
            if UPDATE_NODES_CSV:
                nodes_path = src_root / NODES_CSV_PATH
                nodes = load_nodes_csv(nodes_path)

                if nodes:
                    transport_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    node_file_map = match_files_to_nodes(nodes, moved)

                    original_fieldnames = list(nodes[0].keys()) if nodes else []
                    updated_nodes = update_nodes_with_transport_data(nodes, node_file_map, transport_date)
                    new_fieldnames = list(updated_nodes[0].keys()) if updated_nodes else original_fieldnames

                    save_nodes_csv(nodes_path, updated_nodes, new_fieldnames)

                    # Also copy updated nodes.csv to remote
                    # (This will be committed separately in the data-pipeline repo)

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

    # Summary
    print(f"\n[SUMMARY]")
    print(f"  Files moved: {len(moved)}")
    print(f"  Files retained: {len(retained)}")
    if UPDATE_NODES_CSV:
        print(f"  nodes.csv updated: Yes")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()
        sys.exit(1)
