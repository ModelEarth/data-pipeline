# Agent Guidance

This file provides guidance when working in `data-pipeline/industries/naics`.

## Overview

Use `annual.py` for all NAICS pulls. It supports:
- Scopes: `zip`, `county`, `state`, `country`, or `all`
- Multiple scopes: comma-separated in `config.yaml` or `--scope`
- NAICS level filtering: `--naics-level <level>` or `all`

ZIP scope uses ZBP for years ≤ 2018 and CBP for 2019+.

## Common Commands

```bash
python annual.py
python annual.py 2023 --scope county
python annual.py 2023 --scope state,country
python annual.py 2018 --scope zip --naics-level all
```

## Config

`annual.py` reads defaults from `config.yaml` when CLI params are not provided. CLI args always override config values.

Key fields:
- `YEAR`
- `NAICS_LEVEL` (use `all` for multiple levels)
- `STATE` (optional)
- `OUTPUT_PATH`
- `API_KEY` (optional; for rate limits)
- `SCOPE.selected` (single or comma-separated)

Local state FIPS file: `state-fips.csv`

## Environment

```bash
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install "numpy<2" pandas pyarrow requests pyyaml
```
