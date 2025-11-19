# Data Pipeline Transport - Documentation Index

## 🚀 Quick Start

**New here?** Start with [QUICK_START.md](QUICK_START.md) for a quick overview and getting started guide.

**Want the full story?** Read [SUMMARY.md](SUMMARY.md) for complete details on the mystery solved and enhancements made.

---

## 📚 Documentation Files

### 1. [QUICK_START.md](QUICK_START.md) - Start Here!
Quick reference guide with TL;DR, common commands, and troubleshooting.

**Best for**: Getting started quickly, checking test results, quick reference

### 2. [SUMMARY.md](SUMMARY.md) - Complete Overview
Full summary including:
- Mystery solved: Where data goes to community-data
- What we built (enhanced transport script)
- Test results and matched nodes
- Files retained and why
- Next steps and Q&A

**Best for**: Understanding the complete picture, investigation results, decision making

### 3. [ENHANCED_README.md](ENHANCED_README.md) - User Guide
Detailed guide to using the enhanced transport script:
- New features explained
- Configuration options
- Usage instructions (local vs GitHub mode)
- Verification steps
- Troubleshooting guide

**Best for**: Learning how to use the enhanced script, configuration, troubleshooting

### 4. [FINDINGS.md](FINDINGS.md) - Investigation Report
Investigation results answering:
- Which scripts output to community-data?
- What files should be retained as lookups/crosswalks?
- Where does model.earth/localsite/info/ get its data?
- Recommendations for nodes.csv updates

**Best for**: Understanding the investigation, technical details, data pipeline architecture

### 5. [README.md](README.md) - Original Transport Script
Documentation for the original transport script by Shulin.

**Best for**: Understanding the original script, baseline functionality

### 6. [CLAUDE.md](CLAUDE.md) - Original Analysis
Original analysis of the transport script and how it works.

**Best for**: Understanding file destinations and configuration

---

## 🔧 Script Files

### [data_transport_enhanced.py](data_transport_enhanced.py) - Enhanced Script (NEW)
Enhanced version with:
- Automatic nodes.csv updates
- Enhanced retention rules for lookup files
- Node-to-file mapping reports
- Three new columns in nodes.csv

**Use this** for production runs with nodes.csv integration.

### [data_transport.py](data_transport.py) - Original Script
Original transport script without nodes.csv integration.

**Use this** if you just want to move files without updating nodes.csv.

---

## 🎯 Choose Your Path

### Path 1: Quick Test Run
```bash
# 1. Read quick start
cat admin/transport/QUICK_START.md

# 2. Run the enhanced script
python admin/transport/data_transport_enhanced.py

# 3. Check results
cat data-pipe-csv/node-mapping.md
```

### Path 2: Deep Dive
```bash
# 1. Read the investigation findings
cat admin/transport/FINDINGS.md

# 2. Read the complete summary
cat admin/transport/SUMMARY.md

# 3. Read the detailed guide
cat admin/transport/ENHANCED_README.md

# 4. Run with understanding
python admin/transport/data_transport_enhanced.py
```

### Path 3: Just Move Files (Original)
```bash
# 1. Read original README
cat admin/transport/README.md

# 2. Run original script
python admin/transport/data_transport.py
```

---

## 🎁 What You Get

After running the enhanced script:

### Updated Files in data-pipeline/
- [nodes.csv](../../nodes.csv) - Now with `actual_size_mb`, `csv_file_count`, `last_transport_date`
- [moved-csv.md](../../moved-csv.md) - Local copy of transport report

### New Files in data-pipe-csv/
- All transported CSV files (preserving structure)
- `moved-csv.md` - Transport report with file listings
- `node-mapping.md` - Shows which files belong to which nodes

---

## 🧩 Key Concepts

### Mystery Solved
**Q**: Where is data being sent to community-data?

**A**: The [naics-annual.ipynb](../../industries/naics/naics-annual.ipynb) Jupyter notebook writes directly to `../../../community-data/industries/naics/US/`

See [FINDINGS.md](FINDINGS.md) for full details.

### Enhanced Features

1. **Nodes.csv Integration**: Script now updates nodes.csv with actual file sizes and counts
2. **Smart Retention**: Automatically keeps lookup/crosswalk files (39 files retained in test)
3. **Mapping Reports**: Shows which files matched to which nodes
4. **Flexible Matching**: 3-strategy approach to match files to nodes

### Files Retained (Not Moved)

The script automatically keeps:
- `nodes.csv` - Registry itself
- `*crosswalk*.csv`, `*_to_*.csv`, `*fips*.csv`, `*id_list*.csv`, `*lookup*.csv` - Lookup files
- `timelines/prep/all/input/` - Input data directory (39 files)

---

## 📊 Test Results Summary

**Latest Run (2025-11-19)**:
- ✅ 83 files transported
- ✅ 39 files retained
- ✅ 2 nodes matched with actual data
  - eco_001: 51 files, 0.66 MB
  - reg_001: 14 files, 78.48 MB

---

## 🔗 Quick Links

- [nodes.csv](../../nodes.csv) - Node registry with new columns
- [data-pipe-csv/node-mapping.md](../../data-pipe-csv/node-mapping.md) - Node-to-file mapping
- [data-pipe-csv/moved-csv.md](../../data-pipe-csv/moved-csv.md) - Transport report
- [industries/naics/naics-annual.ipynb](../../industries/naics/naics-annual.ipynb) - Main community-data generator

---

## 💡 Tips

- **First time?** → [QUICK_START.md](QUICK_START.md)
- **Want details?** → [SUMMARY.md](SUMMARY.md)
- **Need help?** → [ENHANCED_README.md](ENHANCED_README.md) (see Troubleshooting)
- **Just move files?** → Use [data_transport.py](data_transport.py)
- **Customize retention?** → Edit `OMIT_CSV_GLOBS` in [data_transport_enhanced.py](data_transport_enhanced.py)

---

## 📝 Documentation Authors

- **Investigation & Enhanced Script**: Claude Code (Anthropic)
- **Original Transport Script**: Shulin
- **Project**: ModelEarth data-pipeline

Last Updated: 2025-11-19
