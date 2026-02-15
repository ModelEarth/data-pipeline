# Integration Plan: County and State Data using CBP API

**Created:** 2026-01-25
**Status:** Planning Phase

## Overview

Integrate support for county and state-level business data using the Census Bureau's **CBP (County Business Patterns)** API. This complements our existing ZBP (Zip Business Patterns) implementation.

## Key Differences: ZBP vs CBP

| Aspect | ZBP (Zip Codes) | CBP (Counties/States) |
|--------|-----------------|----------------------|
| **Last Available Year** | 2018 (discontinued) | 2021+ (ongoing) |
| **API Endpoint** | `/data/{year}/zbp` | `/data/{year}/cbp` |
| **Geographic Levels** | Zipcode only | County, State, National |
| **Status** | ✅ Implemented | 🔄 To be integrated |

## File Structure from naics-annual.ipynb

The notebook generates three geographic levels:

### 1. County Level
- **Path:** `community-data/industries/naics/US/county-update/{STATE}/`
- **Naming:** `US-{STATE}-census-naics{2,4,6}-county-{YEAR}.csv`
- **Columns:** Fips, Naics, Establishments, Employees, Payroll
- **Example:** `US-GA-census-naics6-county-2021.csv`

### 2. State Level
- **Path:** `community-data/industries/naics/US/states-update/{STATE}/`
- **Naming:** `US-{STATE}-census-naics{2,4,6}-{YEAR}.csv`
- **Columns:** Naics, Establishments, Employees, Payroll (no Fips)
- **Example:** `US-GA-census-naics6-2021.csv`

### 3. Country Level
- **Path:** `community-data/industries/naics/US/country-update/`
- **Naming:** `US-census-naics{2,4,6}-{YEAR}.csv`
- **Columns:** Fips, Naics, Establishments, Employees, Payroll
- **Example:** `US-census-naics6-2021.csv`

## Proposed Implementation

### Phase 1: Create counties.py Script
- [x] Extract county processing logic from naics-annual.ipynb
- [x] Convert to standalone Python script similar to zipcodes.py
- [x] Add command-line arguments:
  - `year` (positional, default: 2021)
  - `--naics-level` (default: "all" for levels 2,4,6)
  - `--state` (optional, to process single state)
  - `--output-path` (default: ../../../community-data/industries/naics/US/county-update)
  - `--api-key` (optional, for Census API authentication)
- [x] Generate results-county.md with timing and file stats
- [x] Handle years 2017-2021+ (CBP continues past 2018)
- [x] Filter out NAICS code "00" (totals)
- [x] Handle year-based column variations (NAICS2017, NAICS2012, etc.)
- [ ] Test with single state sample
- [ ] Test with full 50 states

### Phase 2: Create states.py Script
- [ ] Extract state processing logic from naics-annual.ipynb
- [ ] Similar structure to counties.py
- [ ] Add command-line arguments
- [ ] Generate results-states.md

### Phase 3: Create country.py Script
- [ ] Aggregate state data to country level
- [ ] Simpler than counties/states (single output per level)
- [ ] Generate results-country.md

### Phase 4: Integration and Documentation
- [ ] Update CLAUDE.md with CBP integration details
- [ ] Update README.md with new scripts
- [ ] Document API differences between ZBP and CBP
- [ ] Add examples of running all scripts together

## API Details

### CBP API Format (from naics-annual.ipynb)

**County Level:**
```
https://api.census.gov/data/{year}/cbp?get=GEO_ID,NAME,COUNTY,YEAR,NAICS2017,NAICS2017_LABEL,ESTAB,EMP,PAYANN&for=county:*&in=state:{fips:02d}
```

**State Level:**
```
https://api.census.gov/data/{year}/cbp?get=GEO_ID,NAME,COUNTY,YEAR,NAICS2017,NAICS2017_LABEL,ESTAB,EMP,PAYANN&for=state:{fips:02d}
```

### Year-Based Column Variations
- **2017-2021:** NAICS2017, NAICS2017_LABEL, NAME
- **2012-2016:** NAICS2012, NAICS2012_TTL, GEO_TTL
- **2008-2011:** NAICS2007, NAICS2007_TTL, GEO_TTL

## Technical Notes from Jupyter Notebook

1. **API Key:** Notebook uses `api_headers['x-api-key']` - we should make this optional
2. **State FIPS:** Uses `community-data/us/id_lists/state_fips.csv`
3. **NAICS Crosswalk:** Uses `community-data/us/Crosswalk_MasterCrosswalk.csv`
4. **Processing:**
   - Filters out NAICS code "00" (totals)
   - Drops territorial data (limits to 50 states)
   - Groups by state/county/naics for aggregation

## Naming Conventions

Following existing zipcodes.py pattern:

| Script | Output Files | Results File |
|--------|--------------|--------------|
| zipcodes.py | `zipcodes-naics{2,3,4,5,6}-{year}.csv` | results.md |
| zipcodes-naics.py | `zipcode-{XXXXX}-census-naics{level}-{year}.csv` | results-naics.md |
| **counties.py** | `US-{ST}-census-naics{2,4,6}-county-{year}.csv` | results-county.md |
| **states.py** | `US-{ST}-census-naics{2,4,6}-{year}.csv` | results-states.md |
| **country.py** | `US-census-naics{2,4,6}-{year}.csv` | results-country.md |

## Next Steps

1. ✅ Analyze naics-annual.ipynb structure
2. ✅ Document CBP API endpoints and format
3. ✅ Create plan.md to track progress
4. [ ] Decide: Single unified script or separate counties.py/states.py/country.py?
5. [ ] Extract and refactor county processing code
6. [ ] Test with small state sample
7. [ ] Full implementation and documentation

## Questions to Resolve

1. Should we create one unified script (cbp.py) or separate scripts for counties/states/country?
2. Should we process only levels 2,4,6 (as notebook does) or all levels 2-6 like zipcodes.py?
3. Default year should be 2021 (last complete year in notebook) or dynamic?
4. Should we require API key or make it optional?

## Resources

- Census CBP API: https://www.census.gov/data/developers/data-sets/cbp-nonemp-zbp.html
- naics-annual.ipynb: Local reference implementation
- README-CBP.md: Documentation and context
