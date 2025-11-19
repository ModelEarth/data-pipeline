# Enhanced Data Transport Script

## Overview

The enhanced transport script (`data_transport_enhanced.py`) extends the original `data_transport.py` with the following key features:

1. **Updates nodes.csv** with actual file sizes and transport metadata
2. **Enhanced retention rules** to automatically keep lookup/crosswalk files
3. **Node-to-file mapping report** showing which CSVs belong to which data pipeline nodes
4. **New columns in nodes.csv**: `actual_size_mb`, `csv_file_count`, `last_transport_date`

## New Features

### 1. Automatic nodes.csv Updates

The script now:
- Reads the existing [nodes.csv](../../nodes.csv)
- Matches transported CSV files to nodes based on their `output_path`
- Calculates total file sizes and file counts per node
- Adds/updates three new columns:
  - `actual_size_mb`: Total size of all CSV files for this node (in MB)
  - `csv_file_count`: Number of CSV files transported
  - `last_transport_date`: Date of last transport (YYYY-MM-DD)

### 2. Enhanced File Retention Rules

The script automatically retains (does not transport) the following files:

**File Patterns** (automatically kept in source repo):
- `node.csv` / `nodes.csv` - Node registry
- `*crosswalk*.csv` - Crosswalk/mapping files
- `*_to_*.csv` - Mapping files (e.g., zip_to_zcta)
- `*fips*.csv` - FIPS code lookup files
- `*id_list*.csv` - ID list files
- `*lookup*.csv` - Lookup tables

**Directories** (completely skipped):
- `timelines/prep/all/input/` - Input files for ML/regression scripts

These files are dependencies for other scripts and should remain in the data-pipeline repo.

### 3. Node Mapping Report

A new report file `node-mapping.md` is generated showing:
- Which CSV files were matched to which nodes
- File counts and total sizes per node
- Helps verify that the matching logic is working correctly

## Configuration

Edit these settings in `data_transport_enhanced.py`:

```python
# Enable/disable nodes.csv updates
UPDATE_NODES_CSV = True

# Path to nodes.csv
NODES_CSV_PATH = "nodes.csv"

# Add additional file patterns to retain
OMIT_CSV_GLOBS = [
    "node.csv",
    "nodes.csv",
    "*crosswalk*.csv",
    # Add more patterns here
]

# Add directories to skip entirely
OMIT_DIRECTORIES = [
    "timelines/prep/all/input",
    # Add more directories here
]
```

## Usage

### Test in Local Mode (Recommended First Step)

```bash
# Run from the root of data-pipeline repo
python admin/transport/data_transport_enhanced.py
```

This will:
1. Create a `data-pipe-csv/` folder locally
2. Copy CSV files there (respecting retention rules)
3. Update `nodes.csv` with actual sizes and counts
4. Generate reports:
   - `data-pipe-csv/moved-csv.md` - Transport report
   - `data-pipe-csv/node-mapping.md` - Node mapping report
5. Create `moved-csv.md` in the root

### Switch to GitHub Mode

To push to the remote repository:

1. Edit `data_transport_enhanced.py`:
   ```python
   OUTPUT_LOCAL_PATH = None  # Change from "data-pipe-csv" to None
   ```

2. Run:
   ```bash
   python admin/transport/data_transport_enhanced.py
   ```

This will push to the `ModelEarth/data-pipe-csv` repository.

## Output Files

After running the script:

### In data-pipeline repo (updated):
- `nodes.csv` - Updated with actual sizes and transport dates
- `moved-csv.md` - Local copy of transport report

### In data-pipe-csv/ (or remote repo):
- All transported CSV files (preserving folder structure)
- `moved-csv.md` - Transport report with file listings
- `node-mapping.md` - Node-to-file mapping report (local mode only)

## Node Matching Logic

The script matches files to nodes using this algorithm:

1. For each node in nodes.csv, get its `output_path`
2. For each CSV file being transported, check if its relative path starts with the node's `output_path`
3. If matched, accumulate file size and count for that node
4. Update node's new columns with aggregated data

### Example Matching

Node entry:
```csv
node_id,name,output_path
eco_001,Economic Data Fetcher,states/commodities/2020/
```

Files that match:
- `states/commodities/2020/CA.csv` ✓
- `states/commodities/2020/NY.csv` ✓
- `states/other/data.csv` ✗

## Files That Are Retained (Not Transported)

Based on the enhanced retention rules, these files will stay in the data-pipeline repo:

1. **Registry Files**:
   - `nodes.csv` - The node registry itself

2. **Lookup/Reference Files**:
   - Any files matching `*crosswalk*.csv`
   - Any files matching `*fips*.csv`
   - Any files matching `*id_list*.csv`
   - Any files matching `*_to_*.csv` (e.g., zip-to-ZCTA mappings)

3. **Input Data**:
   - Files in `timelines/prep/all/input/` directory

4. **Size-based retention**:
   - Can be customized in `should_omit_by_size()` function

## Verification Steps

After running the script:

1. **Check nodes.csv**:
   ```bash
   # View the updated nodes.csv
   cat nodes.csv | head -5
   ```

   Look for the new columns: `actual_size_mb`, `csv_file_count`, `last_transport_date`

2. **Review Node Mapping Report**:
   ```bash
   cat data-pipe-csv/node-mapping.md
   ```

   Verify that files are matched to the correct nodes.

3. **Check Retained Files**:
   ```bash
   cat data-pipe-csv/moved-csv.md
   ```

   Look for the "Retained CSVs" section to see which files were kept.

4. **Verify File Sizes**:
   Compare the `actual_size_mb` in nodes.csv with the `folder_size` column to see if they align.

## Troubleshooting

### Files Not Matching to Nodes

If files aren't being matched to nodes:

1. Check that `output_path` in nodes.csv uses forward slashes (`/`)
2. Ensure `output_path` doesn't have leading or trailing slashes
3. Paths are case-sensitive
4. Run in local mode and check `node-mapping.md` to see what was matched

### Files Being Transported That Shouldn't Be

If lookup/crosswalk files are being transported:

1. Add the filename pattern to `OMIT_CSV_GLOBS`
2. Or add the directory to `OMIT_DIRECTORIES`

### nodes.csv Not Being Updated

1. Ensure `UPDATE_NODES_CSV = True`
2. Check that `nodes.csv` exists at the root
3. Look for error messages about CSV parsing

## Differences from Original Script

| Feature | Original | Enhanced |
|---------|----------|----------|
| Updates nodes.csv | No | Yes |
| Retention rules | Basic | Enhanced (auto-detects lookups) |
| Node mapping report | No | Yes |
| Directory exclusions | By name | By path pattern |
| File size tracking | In report only | In nodes.csv |

## Future Enhancements

Potential additions:

1. Add validation to detect files that don't match any node
2. Auto-detect Jupyter notebooks and add them to nodes.csv
3. Track destination repository (community-data vs community-timelines)
4. Add file hash tracking to detect changes
5. Support for updating remote nodes.csv in GitHub mode

## See Also

- [FINDINGS.md](FINDINGS.md) - Investigation results on community-data paths
- [README.md](README.md) - Original transport script documentation
- [../../nodes.csv](../../nodes.csv) - The node registry
- [../../admin/README.md](../../admin/README.md) - Admin dashboard documentation
