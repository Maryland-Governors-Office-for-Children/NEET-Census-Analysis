# FINALPUSH
# fetch_disconnected_youth_tract.py
# ==============================
# Script to calculate the percentage of individuals aged 16–19 who are
# neither enrolled in school nor working at the census tract level in Maryland,
# using ACS 5-Year Estimates from Table B14005, including Margins of Error (MOEs).

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# -----------------------------
# Load the Census API Key from .env file
# -----------------------------
load_dotenv()
API_KEY = os.getenv("CENSUS_API_KEY")
if not API_KEY:
    raise ValueError("❌ Missing Census API key in .env file.")

# -----------------------------
# Constants for API request
# -----------------------------
YEAR = "2023"
BASE_URL = f"https://api.census.gov/data/{YEAR}/acs/acs5"
TABLE_PREFIX = "B14005"
STATE_FIPS = "24"  # Maryland
OUTPUT_DIR = "output"
OUTPUT_FILENAME = "disconnected_youth_tract.csv"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Variables for B14005 (age 16–19 only)
# -----------------------------
# These represent counts and MOEs for youth not enrolled in school and not in labor force,
# and the total youth population (age 16–19) from ACS Table B14005.

variables = [
    f"{TABLE_PREFIX}_008E",  # Male 16–19, not enrolled, not in labor force
    f"{TABLE_PREFIX}_015E",  # Female 16–19, not enrolled, not in labor force
    f"{TABLE_PREFIX}_001E",  # Total population 16–19
    f"{TABLE_PREFIX}_008M",  # MOE for male not enrolled/not in labor force
    f"{TABLE_PREFIX}_015M",  # MOE for female not enrolled/not in labor force
    f"{TABLE_PREFIX}_001M"   # MOE for total 16–19 population
]

# -----------------------------
# Manually define valid Maryland county FIPS codes
# -----------------------------
# These are all 24 counties and Baltimore City in Maryland. This avoids making calls
# to invalid or non-existent counties.
valid_md_county_fips = [
    "001", "003", "005", "009", "011", "013", "015", "017", "019", "021",
    "023", "025", "027", "029", "031", "033", "035", "037", "039", "041",
    "043", "045", "047", "510"
]

# -----------------------------
# Loop through counties and request tract-level data
# -----------------------------
all_data = []
print("📡 Requesting tract-level NEET data from Census API...")

for county_fips in valid_md_county_fips:
    params = {
        "get": ",".join(variables),
        "for": "tract:*",
        "in": f"state:{STATE_FIPS} county:{county_fips}",
        "key": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        df["county"] = county_fips
        all_data.append(df)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed for county {county_fips}: {e}")
    except ValueError as e:
        print(f"⚠️ Could not parse response for county {county_fips}: {e}")

# -----------------------------
# Concatenate all data frames
# -----------------------------
if not all_data:
    raise ValueError("❌ No data returned from any counties.")

df_all = pd.concat(all_data, ignore_index=True)

# Convert columns to numeric
for var in variables:
    df_all[var] = pd.to_numeric(df_all[var], errors="coerce")

# -----------------------------
# Calculate NEET statistics
# -----------------------------

# NEET count = male + female not enrolled and not in labor force
df_all["neet_count"] = df_all[f"{TABLE_PREFIX}_008E"] + df_all[f"{TABLE_PREFIX}_015E"]

# Total youth population 16–19
df_all["total_youth"] = df_all[f"{TABLE_PREFIX}_001E"]

# NEET percentage
df_all["neet_percent"] = (df_all["neet_count"] / df_all["total_youth"]) * 100

# MOE for NEET count = sqrt(male_MOE^2 + female_MOE^2)
df_all["neet_count_moe"] = (
    df_all[f"{TABLE_PREFIX}_008M"] ** 2 + df_all[f"{TABLE_PREFIX}_015M"] ** 2
) ** 0.5

# MOE for total youth
df_all["total_youth_moe"] = df_all[f"{TABLE_PREFIX}_001M"]

# MOE for NEET percentage via error propagation
df_all["neet_percent_moe"] = df_all["neet_percent"] * (
    (df_all["neet_count_moe"] / df_all["neet_count"]) ** 2 +
    (df_all["total_youth_moe"] / df_all["total_youth"]) ** 2
) ** 0.5

# Coefficient of variation
df_all["neet_percent_cv"] = df_all["neet_percent_moe"] / df_all["neet_percent"]

# GEOID = state + county + tract
df_all["GEOID"] = df_all["state"] + df_all["county"] + df_all["tract"]

# -----------------------------
# Export to CSV
# -----------------------------
final_cols = [
    "GEOID", "neet_count", "neet_count_moe",
    "total_youth", "total_youth_moe",
    "neet_percent", "neet_percent_moe", "neet_percent_cv"
]
final_df = df_all[final_cols].copy()

output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
final_df.to_csv(output_path, index=False)
print(f"✅ Exported tract-level NEET data to {output_path}")
