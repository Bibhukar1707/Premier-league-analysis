# analysis.py
# Manchester United vs Bournemouth – FBref Performance Analysis
# Match 2 in Premier League Analysis Portfolio

import pandas as pd
import matplotlib.pyplot as plt
import os

# =====================================================
# 1. SAFE PATH SETUP (DEBUG & RUN FRIENDLY)
# =====================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_RAW = os.path.join(BASE_DIR, "Data_raw")
DATA_CLEAN = os.path.join(BASE_DIR, "Data_clean")
VISUALS = os.path.join(BASE_DIR, "Visuals")
POWERBI = os.path.join(BASE_DIR, "Powerbi")

os.makedirs(DATA_CLEAN, exist_ok=True)
os.makedirs(VISUALS, exist_ok=True)

# =====================================================
# 2. LOAD RAW FBREF CSV FILES
# =====================================================
manutd_raw = pd.read_csv(
    os.path.join(DATA_RAW, "Manchester United team stats.csv"),
    encoding="latin1"
)

bournemouth_raw = pd.read_csv(
    os.path.join(DATA_RAW, "Bournemouth team stats.csv"),
    encoding="latin1"
)

shots_raw = pd.read_csv(
    os.path.join(DATA_RAW, "Shot table manchester united vs bournemouth.csv"),
    encoding="latin1"
)

# =====================================================
# 3. FBREF TABLE CLEANING FUNCTION
# =====================================================
def clean_fbref_table(df):
    """
    FBref tables store real headers in the first row.
    This function standardises them for analysis.
    """
    df.columns = df.iloc[0]
    df = df.drop(index=0)
    df = df.loc[:, df.columns.notna()]
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df.reset_index(drop=True)

manutd = clean_fbref_table(manutd_raw)
bournemouth = clean_fbref_table(bournemouth_raw)

manutd.to_csv(os.path.join(DATA_CLEAN, "manutd_players_clean.csv"), index=False)
bournemouth.to_csv(os.path.join(DATA_CLEAN, "bournemouth_players_clean.csv"), index=False)

# =====================================================
# 4. TEAM SUMMARY METRICS
# =====================================================
team_summary = pd.DataFrame({
    "team": ["Manchester United", "Bournemouth"],
    "total_shots": [
        manutd["sh"].astype(int).sum(),
        bournemouth["sh"].astype(int).sum()
    ],
    "passes_completed": [
        manutd["cmp"].astype(int).sum(),
        bournemouth["cmp"].astype(int).sum()
    ]
})

team_summary.to_csv(os.path.join(DATA_CLEAN, "team_summary.csv"), index=False)

# =====================================================
# 5. CLEAN SHOT TABLE
# =====================================================
shots = shots_raw.copy()

shots.columns = shots.iloc[0]
shots = shots.drop(index=0)

shots.columns = (
    shots.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

shots = shots.reset_index(drop=True)

# Convert numeric columns safely (FBref-safe)
shots["xg"] = pd.to_numeric(shots["xg"], errors="coerce")
shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce")
shots["distance"] = pd.to_numeric(shots["distance"], errors="coerce")

# Drop rows where xG is missing (non-shot rows / headers)
shots = shots.dropna(subset=["xg", "minute", "distance"])

shots.to_csv(os.path.join(DATA_CLEAN, "shots_clean.csv"), index=False)

# =====================================================
# 6. SHOTS & xG BY TEAM
# =====================================================
shot_summary = (
    shots
    .groupby("squad")
    .agg(
        shots=("xg", "count"),
        total_xg=("xg", "sum")
    )
    .reset_index()
)

shot_summary.to_csv(os.path.join(DATA_CLEAN, "shot_summary.csv"), index=False)

# =====================================================
# 7. SHOT TIMING ANALYSIS (MATCH DYNAMICS)
# =====================================================
shots["time_window"] = pd.cut(
    shots["minute"],
    bins=[0, 15, 30, 45, 60, 75, 90, 120],
    labels=["0-15", "16-30", "31-45+", "46-60", "61-75", "76-90+", "90+"]
)

shot_timing = (
    shots
    .groupby(["squad", "time_window"])
    .size()
    .reset_index(name="shots")
)

shot_timing.to_csv(
    os.path.join(DATA_CLEAN, "shot_timing_analysis.csv"),
    index=False
)

# =====================================================
# 8. GOAL EVENT EXTRACTION
# =====================================================
goal_events = shots[shots["outcome"] == "Goal"][
    ["minute", "squad", "player", "xg"]
]

goal_events.to_csv(
    os.path.join(DATA_CLEAN, "goal_events.csv"),
    index=False
)

# =====================================================
# 9. SHOT OUTCOME BREAKDOWN
# =====================================================
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

# =====================================================
# 10. DISTANCE-BASED SHOT ANALYSIS
# =====================================================
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

# =====================================================
# 11. OPTIONAL VISUAL QA (SHOT DISTRIBUTION)
# =====================================================
plt.figure(figsize=(7, 4))

for team in shots["squad"].unique():
    team_data = distance_analysis[distance_analysis["squad"] == team]
    plt.plot(
        team_data["distance_zone"],
        team_data["shots"],
        marker="o",
        label=team
    )

plt.title("Shot Distance Distribution – Manchester United vs Bournemouth")
plt.xlabel("Distance Zone")
plt.ylabel("Shots")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(VISUALS, "shot_distance_distribution.png"))
plt.close()

# =====================================================
# 12. UNDERSTAT IMAGE PRESENCE CHECK (SANITY)
# =====================================================
required_images = [
    "understat_shot_map.png",
    "understat_xg_timeline.png"
]

for img in required_images:
    img_path = os.path.join(VISUALS, img)
    if not os.path.exists(img_path):
        print(f"WARNING: Missing image -> {img}")
    else:
        print(f"Image found -> {img}")

print("Manchester United vs Bournemouth analysis COMPLETE.")
