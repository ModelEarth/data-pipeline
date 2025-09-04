# Data Transport Script Analysis

## File Destination Summary

When you run `python admin/transport/data_transport.py`, files are sent to:

### Local Mode (when OUTPUT_LOCAL_PATH is set)
**Destination**: `data-pipe-csv/` directory in current folder (root level)
**Mode**: Local file copying only - no GitHub operations

### GitHub Mode (when OUTPUT_LOCAL_PATH is empty/None)
**Target Repository**: `ModelEarth/data-pipe-csv` on GitHub
**Destination Path**: Repository root (no subfolder)
**Branch**: `main` (creates/uses this branch, then opens PR)

## Key Configuration (data_transport.py:34-42)

```python
OWNER         = "ModelEarth"     # GitHub organization/user
REPO          = "data-pipe-csv"  # Target repository name
BRANCH        = "main"           # Work branch for changes
SOURCE_DIR    = "."              # Current directory (data-pipeline root)
TARGET_PREFIX = ""               # Files go to root level (no subfolder)

# LOCAL OUTPUT CONFIG
OUTPUT_LOCAL_PATH = "data-pipe-csv"  # If set, outputs locally instead of GitHub
```

## What Happens When You Run It

### Local Mode (OUTPUT_LOCAL_PATH = "data-pipe-csv")
1. **Creates** `data-pipe-csv/` directory if it doesn't exist
2. **Scans** current directory for all `*.csv` files
3. **Copies** CSV files directly to `data-pipe-csv/` directory (preserving folder structure)
4. **Generates** report at `data-pipe-csv/moved-csv.md`
5. **No GitHub operations** - everything stays local

### GitHub Mode (OUTPUT_LOCAL_PATH = None/empty)
1. **Clones** `https://github.com/ModelEarth/data-pipe-csv.git` to temporary directory
2. **Scans** current directory for all `*.csv` files
3. **Copies** CSV files directly to repository root (preserving folder structure)
4. **Commits** changes with message: "chore(data): migrate CSV and update moved-csv report"
5. **Pushes** to `main` branch
6. **Opens PR** at: https://github.com/ModelEarth/data-pipe-csv/compare/main?expand=1

## File Retention Rules (data_transport.py:57-59)

Some files are kept in source and NOT moved:
- `node.csv` (anywhere in directory tree)

## Directory Exclusions

The following directories are automatically excluded from CSV scanning:
- The output directory (`data-pipe-csv/` in local mode)
- Standard ignored directories: `.git`, `.github`, `.venv`, `venv`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.idea`, `.vscode`

## Reports Generated

- **Local**: `moved-csv.md` in current directory
- **Remote**: `moved-csv.md` in target repository root
- Both contain details of moved files, retained files, and largest remaining files

## LFS (Large File Storage)

Files larger than 90MB are automatically tracked with Git LFS if available.