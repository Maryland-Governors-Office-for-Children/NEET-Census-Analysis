# NEET-Census-Analysis

This repository documents a replicable methodology for estimating the percentage of youth aged 16 to 19 in Maryland who are **Not in Education, Employment, or Training (NEET)** using the U.S. Census Bureau’s American Community Survey (ACS) 5-Year Estimates. Data are generated at both the **county** and **census tract** levels.

---

## Background and Purpose

The Maryland Governor’s Office for Children (GOC) received a request to incorporate the following measure into the **ENOUGH Datahub**:

> "% individuals aged 16 to 24 who are neither enrolled in school nor working"

The ENOUGH Datahub is a platform designed to visualize child and family wellbeing indicators at the state, county, and census tract level.

Upon review of publicly available data sources, it was determined that while NEET estimates for the 16–24 age range are available at the national or state level from sources like BLS or KIDS COUNT, **tract-level data is not published for that full age range**. However, the ACS Table **B14005** provides detailed data for the 16–19 age group, enabling tract-level estimation.

As a result, this project calculates:

> **"% individuals aged 16 to 19 who are neither enrolled in school nor working"**

at both the **tract** and **county** levels, using ACS Table B14005.

---

## What is NEET?

NEET stands for **Not in Education, Employment, or Training**. It is an internationally recognized metric for assessing youth disconnection. A high NEET rate can indicate challenges in economic opportunity, educational attainment, and future workforce participation.

In this repository, "NEET" is used in filenames, column headers, and script logic to refer to this calculated percentage.

---

## Methodology Overview

For both tract and county levels, the NEET rate is calculated using the following formula:

NEET % = (Youth aged 16–19 not enrolled in school and not in labor force) / (Total youth aged 16–19) × 100


### Numerator
- `B14005_008E`: Male, 16–19, not enrolled in school, not in labor force  
- `B14005_015E`: Female, 16–19, not enrolled in school, not in labor force  

### Denominator
- `B14005_001E`: Total population aged 16–19  
- `B14005_002E`: Total male, 16–19  
- `B14005_009E`: Total female, 16–19  

### Margins of Error (MOEs)
- MOEs for both counts and percentages are derived using standard error propagation formulas for ratios.
- MOEs and coefficients of variation (CVs) are only calculated when both numerator and denominator are greater than 0. This ensures statistically valid estimates and avoids division-by-zero errors.

---

## Code Walkthrough

### 1. Tract-Level Script: `fetch_disconnected_youth_tract.py`

This script gathers NEET data for each Maryland census tract by looping over all valid county FIPS codes and querying tract-level data one county at a time.

**Major Steps:**
1. Load the API key from the `.env` file.
2. Define constants: year, table, state FIPS, and Maryland county FIPS codes.
3. Query B14005 variables using the Census API.
4. Convert all variables to numeric for calculation.
5. Calculate:
   - `neet_male`, `neet_female`, and `neet_count`
   - `total_youth_male`, `total_youth_female`, and `total_youth`
   - Percent NEET and MOEs for male, female, and total population
   - Coefficients of variation (CVs)
6. Construct full GEOIDs.
7. Export final results to `output/disconnected_youth_tract.csv`

**Note:** All percent, MOE, and CV calculations are only computed if the corresponding denominator is greater than zero.

---

### 2. County-Level Script: `fetch_disconnected_youth_county.py`

This script performs a single API call to retrieve NEET data for all Maryland counties.

**Major Steps:**
1. Load the API key from `.env`.
2. Define constants and list of B14005 variables.
3. Query all counties with `county:*` in one API call.
4. Convert variables to numeric and calculate:
   - Gender-specific NEET and total counts
   - Percent NEET, MOEs, and CVs for each group
5. Construct GEOIDs and map readable county names.
6. Export final results to `output/disconnected_youth_county.csv`

**Note:** As with the tract-level script, percent and CV metrics are only calculated when valid denominators exist.

---

## Output Files

| File | Description |
|------|-------------|
| `output/disconnected_youth_tract.csv` | NEET rates and MOEs for all Maryland census tracts |
| `output/disconnected_youth_county.csv` | NEET rates and MOEs for all Maryland counties |

Each file includes the following fields:

- `GEOID`: Full geographic identifier
- `neet_male`, `neet_female`, `neet_count`
- `total_youth_male`, `total_youth_female`, `total_youth`
- `neet_percent_male`, `neet_percent_female`, `neet_percent`
- `neet_male_moe`, `neet_female_moe`, `neet_count_moe`
- `total_youth_male_moe`, `total_youth_female_moe`, `total_youth_moe`
- `neet_percent_male_moe`, `neet_percent_female_moe`, `neet_percent_moe`
- `neet_percent_male_cv`, `neet_percent_female_cv`, `neet_percent_cv`

---

## ACS Variables Used

| Variable Code | ACS Label | Description |
|---------------|-----------|-------------|
| `B14005_001E` | Total: | Total population age 16–19 |
| `B14005_002E` | Male: | Total male age 16–19 |
| `B14005_009E` | Female: | Total female age 16–19 |
| `B14005_008E` | Male: Not enrolled in school: Not in labor force | NEET male 16–19 |
| `B14005_015E` | Female: Not enrolled in school: Not in labor force | NEET female 16–19 |
| `B14005_001M` to `B14005_015M` | Margin of Error equivalents | Used for calculating MOEs and CVs |

📎 Full variable documentation: [ACS B14005 Variables](https://api.census.gov/data/2015/acs/acs5/groups/B14005.html)

---

## Notes for Review

This repository is intended for internal review by:
- Maryland Department of Planning
- Governor’s Office Innovation Team

Feedback is welcome on methodology, accuracy, and potential enhancements.
Last updated: July 23, 2025_


