# Quick Start Guide - Enhanced Data Transport

## TL;DR

The enhanced transport script now:
1. ✅ Updates [nodes.csv](../../nodes.csv) with actual file sizes and counts
2. ✅ Automatically retains lookup/crosswalk files
3. ✅ Generates mapping reports showing which files belong to which nodes

## Run It

```bash
# From the root of data-pipeline repo
python admin/transport/data_transport_enhanced.py
```

This will:
- Copy CSV files to `data-pipe-csv/` folder locally
- Update `nodes.csv` with new columns
- Generate reports

## Check Results

```bash
# View updated nodes.csv (check last 3 columns)
head -2 nodes.csv && tail -1 nodes.csv

# See which files matched to which nodes
cat data-pipe-csv/node-mapping.md

# Review transport report
cat data-pipe-csv/moved-csv.md | less
```

## New Columns in nodes.csv

| Column | Description | Example |
|--------|-------------|---------|
| `actual_size_mb` | Total size of CSV files in MB | `0.66` |
| `csv_file_count` | Number of CSV files | `51` |
| `last_transport_date` | Date of transport | `2025-11-19` |

## Mystery Solved

**Where is data being sent to community-data?**

Answer: The [naics-annual.ipynb](../../industries/naics/naics-annual.ipynb) Jupyter notebook writes directly to `../../../community-data/industries/naics/US/`

This notebook is **not tracked** in nodes.csv yet because it's a Jupyter notebook, not a Python script.

## Files Automatically Retained

These files stay in data-pipeline (not moved):
- `nodes.csv` - The registry itself
- `*crosswalk*.csv` - Crosswalk files
- `*_to_*.csv` - Mapping files
- `*fips*.csv` - FIPS lookup files
- `*id_list*.csv` - ID lists
- All files in `timelines/prep/all/input/` - Input data for ML

Total: 39 files retained

## Test Results

**Current Run (2025-11-19)**:
- 83 files moved
- 39 files retained
- 2 nodes matched:
  - `eco_001`: 51 files, 0.66 MB
  - `reg_001`: 14 files, 78.48 MB

## Switch to GitHub Mode

To push to remote `ModelEarth/data-pipe-csv` repository:

1. Edit [data_transport_enhanced.py](data_transport_enhanced.py):
   ```python
   OUTPUT_LOCAL_PATH = None  # Change from "data-pipe-csv"
   ```

2. Run:
   ```bash
   python admin/transport/data_transport_enhanced.py
   ```

## Customize Retention Rules

Edit these sections in [data_transport_enhanced.py](data_transport_enhanced.py):

```python
# Add more file patterns to keep
OMIT_CSV_GLOBS = [
    "node.csv",
    "nodes.csv",
    "*crosswalk*.csv",
    # Add your patterns here
]

# Add more directories to skip
OMIT_DIRECTORIES = [
    "timelines/prep/all/input",
    # Add your directories here
]
```

## Common Issues

### No files matched to nodes

**Cause**: Output paths in nodes.csv don't match actual file locations

**Fix**: The script uses flexible matching (3 strategies), but if still not matching:
1. Check the `output_path` column in nodes.csv
2. Check actual file paths in `moved-csv.md`
3. Update `output_path` in nodes.csv to match actual paths

### Files being transported that should stay

**Cause**: File pattern not in retention rules

**Fix**: Add the pattern to `OMIT_CSV_GLOBS` or directory to `OMIT_DIRECTORIES`

### nodes.csv not updating

**Cause**: `UPDATE_NODES_CSV` is False

**Fix**: Set `UPDATE_NODES_CSV = True` in the script

## Documentation

- **[SUMMARY.md](SUMMARY.md)** - Complete summary of everything
- **[ENHANCED_README.md](ENHANCED_README.md)** - Detailed usage guide
- **[FINDINGS.md](FINDINGS.md)** - Investigation findings
- **[README.md](README.md)** - Original transport script docs

## Example: View eco_001 Updates

```bash
# Before (original nodes.csv)
grep "eco_001" nodes.csv
# eco_001,Economic Data Fetcher,...,207M,...,no,,,

# After (enhanced script run)
grep "eco_001" nodes.csv
# eco_001,Economic Data Fetcher,...,207M,...,no,0.66,51,2025-11-19
#                                            ^^^^  ^^  ^^^^^^^^^^
#                                            size  cnt    date
```

## Next Steps

1. Review [SUMMARY.md](SUMMARY.md) for complete details
2. Check [data-pipe-csv/node-mapping.md](../../data-pipe-csv/node-mapping.md) to see matches
3. Verify retention rules worked: `cat data-pipe-csv/moved-csv.md | grep "Retained CSVs"`
4. Consider adding naics-annual.ipynb to nodes.csv manually

## Questions?

- Read [ENHANCED_README.md](ENHANCED_README.md) for detailed explanations
- Check [FINDINGS.md](FINDINGS.md) for investigation details
- Review generated reports in `data-pipe-csv/` folder
