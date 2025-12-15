# analysis.py
# Chelsea vs Everton – FBref data cleaning & basic analysis

import pandas as pd
import matplotlib.pyplot as plt
import os

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_RAW = os.path.join(BASE_DIR, "Data- Raw")
DATA_CLEAN = os.path.join(BASE_DIR, "Data- Clean")
VISUALS = os.path.join(BASE_DIR, "Visuals")

os.makedirs(DATA_CLEAN, exist_ok=True)
os.makedirs(VISUALS, exist_ok=True)
# -----------------------------
# 2. LOAD RAW CSV FILES
# -----------------------------
chelsea_raw = pd.read_csv(
    os.path.join(DATA_RAW, "Chelsea team stats.csv"),
    encoding="latin1"
)

everton_raw = pd.read_csv(
    os.path.join(DATA_RAW, "Everton team stats.csv"),
    encoding="latin1"
)

shots_raw = pd.read_csv(
    os.path.join(DATA_RAW, "Shot table chelsea vs everton.csv"),
    encoding="latin1"
)

# -----------------------------
# 3. CLEAN FBREF PLAYER TABLES
# -----------------------------
def clean_fbref_player_table(df):
    """
    Cleans FBref player tables by:
    - Using the first row as column names
    - Removing grouped header rows
    - Normalising column names
    """

    # Use first row as header
    df.columns = df.iloc[0]
    df = df.drop(index=0)

    # Drop empty columns
    df = df.loc[:, df.columns.notna()]

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df.reset_index(drop=True)

chelsea = clean_fbref_player_table(chelsea_raw)
everton = clean_fbref_player_table(everton_raw)

# Save clean player tables
chelsea.to_csv(
    os.path.join(DATA_CLEAN, "chelsea_players_clean.csv"),
    index=False
)

everton.to_csv(
    os.path.join(DATA_CLEAN, "everton_players_clean.csv"),
    index=False
)

# -----------------------------
# 4. TEAM SUMMARY METRICS
# -----------------------------
chelsea_shots = chelsea["sh"].astype(int).sum()
everton_shots = everton["sh"].astype(int).sum()

chelsea_passes = chelsea["cmp"].astype(int).sum()
everton_passes = everton["cmp"].astype(int).sum()

team_summary = pd.DataFrame({
    "team": ["Chelsea", "Everton"],
    "total_shots": [chelsea_shots, everton_shots],
    "passes_completed": [chelsea_passes, everton_passes]
})

team_summary.to_csv(
    os.path.join(DATA_CLEAN, "team_summary.csv"),
    index=False
)

# -----------------------------
# 5. CLEAN FBREF SHOT TABLE
# -----------------------------
shots = shots_raw.copy()

# Use first row as column names
shots.columns = shots.iloc[0]
shots = shots.drop(index=0)

# Clean column names
shots.columns = (
    shots.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

shots = shots.reset_index(drop=True)

# Save clean shot table
shots.to_csv(os.path.join(DATA_CLEAN, "shots_clean.csv"), index=False)

# -----------------------------
# 6. SHOTS & xG SUMMARY BY TEAM
# -----------------------------
shots["xg"] = shots["xg"].astype(float)

shot_summary = (
    shots
    .groupby("squad")
    .agg(
        shots=("xg", "count"),
        total_xg=("xg", "sum")
    )
    .reset_index()
)

shot_summary.to_csv(
    os.path.join(DATA_CLEAN, "shot_summary.csv"),
    index=False
)

# -----------------------------
# 7. VISUALS – SHOTS & xG
# -----------------------------
plt.figure(figsize=(6, 4))
plt.bar(shot_summary["squad"], shot_summary["shots"], color=["blue", "red"])
plt.title("Shots by Team")
plt.ylabel("Shots")
plt.savefig(os.path.join(VISUALS, "shots_by_team.png"))
plt.close()

plt.figure(figsize=(6, 4))
plt.bar(shot_summary["squad"], shot_summary["total_xg"], color=["blue", "red"])
plt.title("Total xG by Team")
plt.ylabel("xG")
plt.savefig(os.path.join(VISUALS, "xg_by_team.png"))
plt.close()
# -----------------------------
# 8. SHOT VOLUME BY TEAM (FORMAL)
# -----------------------------
shot_volume = (
    shots
    .groupby("squad")
    .size()
    .reset_index(name="shots")
)

shot_volume.to_csv(
    os.path.join(DATA_CLEAN, "shot_volume_by_team.csv"),
    index=False
)

# -----------------------------
# 9. SHOT OUTCOME BREAKDOWN
# -----------------------------
shot_outcomes = (
    shots
    .groupby(["squad", "outcome"])
    .size()
    .reset_index(name="count")
)

shot_outcomes.to_csv(
    os.path.join(DATA_CLEAN, "shot_outcome_breakdown.csv"),
    index=False
)

# -----------------------------
# 10. DISTANCE-BASED ANALYSIS
# -----------------------------
# Ensure distance is numeric
shots["distance"] = shots["distance"].astype(float)

# Create football-relevant distance zones
shots["distance_zone"] = pd.cut(
    shots["distance"],
    bins=[0, 6, 12, 18, 100],
    labels=["0-6 yards", "6-12 yards", "12-18 yards", "18+ yards"]
)

distance_analysis = (
    shots
    .groupby(["squad", "distance_zone"])
    .size()
    .reset_index(name="shots")
)

distance_analysis.to_csv(
    os.path.join(DATA_CLEAN, "distance_based_analysis.csv"),
    index=False
)

# -----------------------------
# 11. OPTIONAL VISUAL: SHOT DISTANCE DISTRIBUTION
# -----------------------------
plt.figure(figsize=(7, 4))

for team in shots["squad"].unique():
    team_data = distance_analysis[distance_analysis["squad"] == team]
    plt.plot(
        team_data["distance_zone"],
        team_data["shots"],
        marker="o",
        label=team
    )

plt.title("Shot Distance Distribution by Team")
plt.xlabel("Distance Zone")
plt.ylabel("Shots")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(VISUALS, "shot_distance_distribution.png"))
plt.close()

print("Extended FBref analysis complete – all outputs saved.")