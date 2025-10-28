"""
INTEGRATED AGRI-CLIMATE DATA INTELLIGENCE SYSTEM
------------------------------------------------
Author: [Egadarshan S]
Version: 2.0

Description:
This script integrates live agricultural production data from data.gov.in
with offline rainfall data to build an intelligent query-based data analysis system.

PHASE 1:
    - Fetch crop production data from API (first run only)
    - Merge with offline rainfall data
    - Save integrated dataset locally

PHASE 2:
    - Load saved dataset
    - Enable natural-language question answering for agriculture and climate insights
"""

import os
import re
import difflib
import requests
import pandas as pd
from dotenv import load_dotenv


# -----------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------

load_dotenv()
API_KEY = os.getenv("API_KEY")  # stored securely in .env
RESOURCE_ID = "35be999b-0208-4354-b557-f6ca9a5355de"
RAIN_FILE = "data/climate.csv"
OUTPUT_FOLDER = "data"
MERGED_FILE = os.path.join(OUTPUT_FOLDER, "integrated_dataset.csv")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if not API_KEY:
    print("Error: API key missing. Please set it in the .env file.")
    exit()


# -----------------------------------------------------
# PHASE 1 : FETCH + MERGE (only first run)
# -----------------------------------------------------

if not os.path.exists(MERGED_FILE):
    print("First run detected — fetching agriculture data from data.gov.in...")

    limit = 5000
    offset = 0
    all_records = []

    while True:
        url = f"https://api.data.gov.in/resource/{RESOURCE_ID}?api-key={API_KEY}&format=json&limit={limit}&offset={offset}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching data (HTTP {response.status_code})")
            break

        batch = response.json().get("records", [])
        if not batch:
            break

        all_records.extend(batch)
        print(f"Fetched {len(batch)} records (Total: {len(all_records)})")

        if len(batch) < limit:
            break
        offset += limit

    if not all_records:
        print("Error: No records fetched. Check your API key or internet connection.")
        exit()

    agri_df = pd.DataFrame(all_records)
    print(f"Total rows downloaded: {len(agri_df)}")

    # Clean and standardize columns
    rename_map = {}
    for c in agri_df.columns:
        cl = c.lower()
        if "state" in cl:
            rename_map[c] = "state"
        elif "district" in cl:
            rename_map[c] = "district"
        elif "year" in cl:
            rename_map[c] = "year"
        elif "season" in cl:
            rename_map[c] = "season"
        elif "crop" in cl:
            rename_map[c] = "crop"
        elif "production" in cl:
            rename_map[c] = "production_tonnes"

    agri_df.rename(columns=rename_map, inplace=True)
    cols = [c for c in ["state", "district", "year", "season", "crop", "production_tonnes"] if c in agri_df.columns]
    agri_df = agri_df[cols].copy()

    # Normalize datatypes
    agri_df["state"] = agri_df["state"].astype(str).str.strip().str.title()
    agri_df["year"] = pd.to_numeric(agri_df["year"], errors="coerce").astype("Int64")
    agri_df["production_tonnes"] = pd.to_numeric(agri_df.get("production_tonnes", 0), errors="coerce").fillna(0)

    print("Agriculture data cleaned successfully.")

    # Load rainfall CSV
    print("Loading rainfall data...")
    rain_df = pd.read_csv(RAIN_FILE)
    rain_df.rename(columns={"SUBDIVISION": "state", "YEAR": "year", "ANNUAL": "rainfall_mm"}, inplace=True)
    rain_df = rain_df[["state", "year", "rainfall_mm"]]
    rain_df["state"] = rain_df["state"].astype(str).str.strip().str.title()
    rain_df["year"] = pd.to_numeric(rain_df["year"], errors="coerce").astype("Int64")
    rain_df["rainfall_mm"] = pd.to_numeric(rain_df["rainfall_mm"], errors="coerce").fillna(0)

    print("Rainfall data loaded successfully.")

    # Merge datasets
    print("Merging agriculture and rainfall datasets...")
    merged_df = pd.merge(agri_df, rain_df, on=["state", "year"], how="inner")
    merged_df.to_csv(MERGED_FILE, index=False)
    print(f"Integrated dataset saved at: {MERGED_FILE}")
    print("Please re-run the script to begin query analysis.")
    exit()


# -----------------------------------------------------
# PHASE 2 : LOAD DATA & QUERY ENGINE
# -----------------------------------------------------

print("Using saved dataset...")
merged_df = pd.read_csv(MERGED_FILE)


# -----------------------------------------------------
# ANALYTICAL FUNCTIONS
# -----------------------------------------------------

def compare_rainfall(state1, state2, years=5):
    """Compare average rainfall between two states for the past N years."""
    df = merged_df[merged_df["state"].isin([state1.title(), state2.title()])]
    if df.empty:
        return "Data not available for the given states."
    latest_years = sorted(df["year"].dropna().unique())[-years:]
    sub = df[df["year"].isin(latest_years)]
    avg_rain = sub.groupby("state")["rainfall_mm"].mean().round(2)
    return f"Average rainfall (last {years} years):\n{avg_rain.to_string()}"


def top_crops(state, n=5):
    """Display top N crops by production in a given state."""
    sub = merged_df[merged_df["state"].str.contains(state, case=False, na=False)]
    if sub.empty:
        return "No data found for this state."
    top = sub.groupby("crop")["production_tonnes"].sum().sort_values(ascending=False).head(n).round(2)
    return f"Top {n} crops in {state.title()}:\n{top.to_string()}"


def crop_trend(state, crop):
    """Show production and rainfall trends for a given crop and state."""
    sub = merged_df[
        (merged_df["state"].str.contains(state, case=False, na=False)) &
        (merged_df["crop"].str.contains(crop, case=False, na=False))
    ]
    if sub.empty:
        return "No data found for the specified crop or state."
    trend = sub.groupby("year")[["production_tonnes", "rainfall_mm"]].mean().round(2)
    return f"Crop trend for {crop.title()} in {state.title()}:\n{trend.to_string()}"


def policy_recommendation(cropA, cropB, region, years=10):
    """Compare two crops in a region and give production insights."""
    sub = merged_df[merged_df["state"].str.contains(region, case=False, na=False)]
    if sub.empty:
        return "Region not found."
    latest_years = sorted(sub["year"].dropna().unique())[-years:]
    data = sub[sub["year"].isin(latest_years)]
    a = data[data["crop"].str.contains(cropA, case=False, na=False)]
    b = data[data["crop"].str.contains(cropB, case=False, na=False)]
    if a.empty or b.empty:
        return "Not enough data for one or both crops."
    msg = (
        f"Policy Insight for {region.title()}:\n"
        f"- {cropA.title()}: Avg production = {a['production_tonnes'].mean():.2f} tonnes, "
        f"Avg rainfall = {a['rainfall_mm'].mean():.2f} mm\n"
        f"- {cropB.title()}: Avg production = {b['production_tonnes'].mean():.2f} tonnes, "
        f"Avg rainfall = {b['rainfall_mm'].mean():.2f} mm"
    )
    return msg


def rainfall_in_year(state, year):
    """Return average rainfall for a given state and year."""
    val = merged_df[(merged_df["state"].str.contains(state, case=False)) & (merged_df["year"] == year)]
    if val.empty:
        return "No data for the specified state and year."
    avg = val["rainfall_mm"].mean().round(2)
    return f"Average rainfall in {state.title()} in {year}: {avg} mm"


# -----------------------------------------------------
# NATURAL LANGUAGE QUESTION PARSER
# -----------------------------------------------------

def process_question(q):
    """
    Understands and responds to natural-language questions.
    Supports:
      - Compare rainfall between states
      - Find top crops in a state
      - Crop trend for a given state
      - Policy recommendation between two crops
      - Rainfall for a specific state and year
    """
    q = q.lower().strip()
    all_states = [s.lower() for s in merged_df["state"].dropna().unique()]
    all_crops = [c.lower() for c in merged_df["crop"].dropna().unique()]

    # Identify state (best fuzzy match)
    state_match = difflib.get_close_matches(q, all_states, n=1, cutoff=0.6)
    state = state_match[0].title() if state_match else None

    # Identify crops (handle "vs" / "versus" / "and")
    crops_found = []
    parts = re.split(r"\b(?:vs|versus|and)\b", q)
    for part in parts:
        match = difflib.get_close_matches(part.strip(), all_crops, n=1, cutoff=0.6)
        if match:
            crops_found.append(match[0].title())

    # Compare rainfall
    if "compare" in q and "rainfall" in q:
        states = [s for s in merged_df["state"].unique() if s.lower() in q]
        if len(states) >= 2:
            print(compare_rainfall(states[0], states[1]))
        else:
            print("Please mention two states to compare rainfall.")
        return

    # Top crops
    if "top" in q and "crop" in q:
        num = next((int(x) for x in q.split() if x.isdigit()), 5)
        if state:
            print(top_crops(state, num))
        else:
            print("Please mention a valid state.")
        return

    # Crop trend
    if "trend" in q or "production" in q:
        if state and crops_found:
            print(crop_trend(state, crops_found[0]))
        else:
            print("Please mention both state and crop.")
        return

    # Policy recommendation
    if any(x in q for x in ["recommend", "better", "policy", "vs", "versus", "and"]):
        if state and len(crops_found) >= 2:
            print(policy_recommendation(crops_found[0], crops_found[1], state))
        else:
            print("Please mention two crops and one state.")
        return

    # Rainfall by year
    if "rainfall" in q and re.search(r"(19|20)\d{2}", q):
        year = int(re.search(r"(19|20)\d{2}", q).group())
        if state:
            print(rainfall_in_year(state, year))
        else:
            print("Please mention a valid state.")
        return

    # Default message
    print("Unable to understand the question. Try examples like:")
    print(" - Compare rainfall in Tamil Nadu and Kerala")
    print(" - Top 3 crops in Punjab")
    print(" - Trend of rice in Maharashtra")
    print(" - Recommend paddy vs millet in Rajasthan")
    print(" - Rainfall in Tamil Nadu in 2004")


# -----------------------------------------------------
# INTERACTIVE CHAT LOOP
# -----------------------------------------------------

print("\nSystem ready for natural-language queries.")
print("Type your question (or 'exit' to quit). Examples:")
print(" - Compare rainfall in Tamil Nadu and Kerala")
print(" - Top 3 crops in Punjab")
print(" - Recommend paddy vs millet in Rajasthan")

while True:
    question = input("\nAsk: ")
    if question.lower().strip() == "exit":
        print("Exiting system.")
        break
    process_question(question)
