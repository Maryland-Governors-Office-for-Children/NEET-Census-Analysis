# NEET-Census-Analysis

This repository documents a replicable methodology for estimating the percentage of youth aged 16 to 19 in Maryland who are **Not in Education, Employment, or Training (NEET)** using the U.S. Census Bureau’s American Community Survey (ACS) 5-Year Estimates. Data are generated at both the **county** and **census tract** level.

## Background and Purpose

The Maryland Governor’s Office for Children (GOC) received a request to incorporate the measure:

> "% individuals aged 16 to 24 who are neither enrolled in school nor working"

into the **ENOUGH Datahub**, which is a platform designed to visualize child and family wellbeing indicators at the state, county, and census tract level.

Upon review of publicly available data sources, it was determined that while NEET estimates for the 16–24 age range are available at the national or state level from sources like BLS or KIDS COUNT, **tract-level data is not published for that full age range**. However, the ACS Table **B14005** provides detailed data for the 16–19 age group, enabling tract-level estimation.

As a result, this project calculates:

> **"% individuals aged 16 to 19 who are neither enrolled in school nor working"**

at both the **tract** and **county** levels, using ACS Table B14005.

## What is NEET?

NEET stands for **Not in Education, Employment, or Training**. It is an internationally recognized metric for assessing youth disconnection. A high NEET rate can indicate challenges in economic opportunity, educational attainment, and future workforce participation. In this repository, "NEET" is used in filenames, column headers, and script logic to refer to this calculated percentage.

## Methodology Overview

For both tract and county levels, the NEET rate is calculated using the following formula:

```
NEET % = (Youth aged 16–19 not enrolled in school and not in labor force) / (Total youth aged 16–19) × 100
```

### Numerator
- **B14005_008E**: Male, 16–19, not enrolled in school, not in labor force
- **B14005_015E**: Female, 16–19, not enrolled in school, not in labor force

### Denominator
- **B14005_001E**: Total population aged 16–19

### Margins of Error (MOEs)
MOEs for the numerator and denominator are retrieved directly from the Census API and combined using standard error propagation formulas.

---

## Code Walkthrough

### 1. Tract-Level Script: `fetch_disconnected_youth_tract.py`

This script gathers NEET data for each Maryland census tract by looping over all valid county FIPS codes and querying tract-level data one county at a time.

**Major Steps:**
1. Load the API key from the `.env` file.
2. Define constants: year, table, state FIPS, county FIPS codes.
3. Create a list of ACS variable codes from Table B14005, including MOEs.
4. Loop through counties and send a `GET` request to the Census API using `tract:*` within each county.
5. Convert all variables to numeric for calculation.
6. Calculate:
   - `neet_count` = sum of male and female NEET
   - `total_youth` = total population 16–19
   - `neet_percent` = (neet_count / total_youth) × 100
   - `neet_count_moe` using square root of sum of squared MOEs
   - `neet_percent_moe` using error propagation formula
   - `neet_percent_cv` as a measure of estimate reliability
7. Construct full GEOIDs using state + county + tract codes.
8. Export the final columns to `output/disconnected_youth_tract.csv`.

### 2. County-Level Script: `fetch_disconnected_youth_county.py`

This script performs a single API call to retrieve NEET data for all Maryland counties at once.

**Major Steps:**
1. Load the API key from `.env`.
2. Define constants and B14005 variable codes.
3. Request all counties with `county:*` in a single API call.
4. Convert variables to numeric.
5. Calculate all NEET metrics as in the tract-level script.
6. Construct county-level GEOIDs.
7. Export the final DataFrame to `output/disconnected_youth_county.csv`.

---

## Output Files

| File | Description |
|------|-------------|
| `output/disconnected_youth_tract.csv` | NEET rates and MOEs for all Maryland census tracts |
| `output/disconnected_youth_county.csv` | NEET rates and MOEs for all Maryland counties |

Each file includes the following fields:

- `GEOID`: Full geographic identifier (state + county [+ tract])
- `neet_count`: Youth 16–19 not in school and not in labor force
- `neet_count_moe`: Margin of error for NEET count
- `total_youth`: All youth aged 16–19
- `total_youth_moe`: Margin of error for total youth
- `neet_percent`: NEET rate (percent)
- `neet_percent_moe`: MOE for NEET rate
- `neet_percent_cv`: Coefficient of variation

---

## Notes for Review

This repository is intended for internal review by:
- Maryland Department of Planning
- Governor’s Office Innovation Team

Feedback is welcome on methodology, accuracy, and potential enhancements. Alternative approaches to estimate NEET among the 16–24 age range at fine geographic scales may be considered in future versions.
