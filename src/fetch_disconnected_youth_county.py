# ==============================
# fetch_disconnected_youth_county.py
# ==============================
# Script to calculate the percentage of individuals aged 16–19 who are
# neither enrolled in school nor working at the county level in Maryland,
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
OUTPUT_FILENAME = "disconnected_youth_county.csv"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Variables from B14005 (age 16–19 only)
# -----------------------------
# These variables represent male and female youth aged 16–19
# who are not enrolled in school and not in the labor force,
# along with the total youth population and associated MOEs.

variables = [
    f"{TABLE_PREFIX}_008E",  # Male 16–19, not enrolled, not in labor force (Estimate)
    f"{TABLE_PREFIX}_015E",  # Female 16–19, not enrolled, not in labor force (Estimate)
    f"{TABLE_PREFIX}_001E",  # Total population 16–19 (Estimate)
    f"{TABLE_PREFIX}_008M",  # MOE for male not enrolled, not in labor force
    f"{TABLE_PREFIX}_015M",  # MOE for female not enrolled, not in labor force
    f"{TABLE_PREFIX}_001M"   # MOE for total population 16–19
]

# -----------------------------
# Make API Request for all Maryland counties
# -----------------------------
print("📡 Requesting county-level NEET data from Census API...")

params = {
    "get": ",".join(variables),
    "for": "county:*",
    "in": f"state:{STATE_FIPS}",
    "key": API_KEY
}

response = requests.get(BASE_URL, params=params)
response.raise_for_status()
data = response.json()

# -----------------------------
# Load response into DataFrame
# -----------------------------
df = pd.DataFrame(data[1:], columns=data[0])

# Convert columns to numeric
for var in variables:
    df[var] = pd.to_numeric(df[var], errors="coerce")

# -----------------------------
# Calculate NEET statistics
# -----------------------------

# NEET count = male + female not enrolled and not in labor force
df["neet_count"] = df[f"{TABLE_PREFIX}_008E"] + df[f"{TABLE_PREFIX}_015E"]

# Total youth population 16–19
df["total_youth"] = df[f"{TABLE_PREFIX}_001E"]

# NEET percentage
df["neet_percent"] = (df["neet_count"] / df["total_youth"]) * 100

# MOE for NEET count = sqrt(male_MOE^2 + female_MOE^2)
df["neet_count_moe"] = (
    df[f"{TABLE_PREFIX}_008M"] ** 2 + df[f"{TABLE_PREFIX}_015M"] ** 2
) ** 0.5

# MOE for total youth
df["total_youth_moe"] = df[f"{TABLE_PREFIX}_001M"]

# MOE for NEET percentage via error propagation
df["neet_percent_moe"] = df["neet_percent"] * (
    (df["neet_count_moe"] / df["neet_count"]) ** 2 +
    (df["total_youth_moe"] / df["total_youth"]) ** 2
) ** 0.5

# Coefficient of variation
df["neet_percent_cv"] = df["neet_percent_moe"] / df["neet_percent"]

# Create GEOID from state + county
df["GEOID"] = df["state"] + df["county"]

# -----------------------------
# Select final columns and export
# -----------------------------
final_cols = [
    "GEOID", "neet_count", "neet_count_moe",
    "total_youth", "total_youth_moe",
    "neet_percent", "neet_percent_moe", "neet_percent_cv"
]
final_df = df[final_cols].copy()

output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
final_df.to_csv(output_path, index=False)
print(f"✅ Exported county-level NEET data to {output_path}")
