# analysis.py
# Newcastle United vs Chelsea – Match Analysis with Progression
# Premier League Portfolio – Match 3

import os
import pandas as pd

# =====================================================
# 1. PATH SETUP
# =====================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_RAW = os.path.join(BASE_DIR, "Data_raw")
DATA_CLEAN = os.path.join(BASE_DIR, "Data_clean")

os.makedirs(DATA_CLEAN, exist_ok=True)

# =====================================================
# 2. GENERIC FBREF CLEANER
# =====================================================
def clean_fbref(df):
    """
    Standardise FBref tables:
    - Promote first row to header
    - Drop empty / unnamed columns
    - Normalise column names
    """
    df.columns = df.iloc[0]
    df = df.drop(index=0)

    df = df.loc[:, df.columns.notna()]
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df.reset_index(drop=True)

# =====================================================
# 3. LOAD & CLEAN DATA
# =====================================================
newcastle = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Newcastle united team stats.csv"),
        encoding="latin1"
    )
)

chelsea = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Chelsea team stats.csv"),
        encoding="latin1"
    )
)

shots = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Shot table newcastle united vs chelsea.csv"),
        encoding="latin1"
    )
)

newcastle_pass = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Newcastle united passing types.csv"),
        encoding="latin1"
    )
)

chelsea_pass = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Chelsea passing types.csv"),
        encoding="latin1"
    )
)

newcastle_gk = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Newcastle united goalkeeper stats.csv"),
        encoding="latin1"
    )
)

chelsea_gk = clean_fbref(
    pd.read_csv(
        os.path.join(DATA_RAW, "Chelsea goalkeeper stats.csv"),
        encoding="latin1"
    )
)

# =====================================================
# 4. NUMERIC SAFETY HELPERS
# =====================================================
def get_numeric_series(df, col_name):
    """
    Safely extract numeric columns from FBref tables.
    Handles duplicated column names gracefully.
    """
    if col_name not in df.columns:
        return pd.Series(dtype="float64")

    series = df[col_name]

    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]

    return pd.to_numeric(series, errors="coerce")

for col in ["sh", "cmp", "att", "fls", "ck"]:
    newcastle[col] = get_numeric_series(newcastle, col)
    chelsea[col] = get_numeric_series(chelsea, col)

shots["xg"] = pd.to_numeric(shots["xg"], errors="coerce")
shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce")
shots["distance"] = pd.to_numeric(shots["distance"], errors="coerce")

shots = shots.dropna(subset=["xg", "minute", "distance"])

# =====================================================
# 5. TEAM SUMMARY (BASELINE)
# =====================================================
team_summary = pd.DataFrame({
    "team": ["Newcastle United", "Chelsea"],
    "shots": [newcastle["sh"].sum(), chelsea["sh"].sum()],
    "passes_completed": [newcastle["cmp"].sum(), chelsea["cmp"].sum()],
    "passes_attempted": [newcastle["att"].sum(), chelsea["att"].sum()],
    "fouls": [newcastle["fls"].sum(), chelsea["fls"].sum()],
    "corners": [newcastle["ck"].sum(), chelsea["ck"].sum()]
})

team_summary.to_csv(
    os.path.join(DATA_CLEAN, "team_summary.csv"),
    index=False
)

# =====================================================
# 6. SHOT SUMMARY & xG
# =====================================================
shot_summary = (
    shots
    .groupby("squad")
    .agg(
        shots=("xg", "count"),
        total_xg=("xg", "sum"),
        xg_per_shot=("xg", "mean")
    )
    .reset_index()
)

shot_summary.to_csv(
    os.path.join(DATA_CLEAN, "shot_summary.csv"),
    index=False
)

# =====================================================
# 7. SHOT OUTCOME BREAKDOWN
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
# 8. SHOT DISTANCE ANALYSIS
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
# 9. SHOT TIMING ANALYSIS (PROGRESSION)
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
# 10. GOAL EVENTS
# =====================================================
goal_events = shots.loc[
    shots["outcome"] == "Goal",
    ["minute", "squad", "player", "xg"]
].reset_index(drop=True)

goal_events.to_csv(
    os.path.join(DATA_CLEAN, "goal_events.csv"),
    index=False
)

# =====================================================
# 11. PASSING TYPE CONTEXT
# =====================================================
def sum_passing_type(df, keyword):
    """
    Aggregate passing types (short / medium / long)
    while accounting for FBref column inconsistencies.
    """
    cols = [c for c in df.columns if keyword in c]

    if not cols:
        return 0

    values = df[cols].apply(pd.to_numeric, errors="coerce")
    return values.sum().sum()

def extract_completed_passes_by_type(df):
    """
    Extract completed passes by distance (short, medium, long)
    from FBref Passing Types tables.
    """
    result = {}

    for pass_type in ["short", "medium", "long"]:
        # find columns like short_cmp, medium_cmp, long_cmp
        cols = [c for c in df.columns if pass_type in c and "cmp" in c]

        if not cols:
            result[pass_type] = 0
        else:
            values = df[cols].apply(pd.to_numeric, errors="coerce")
            result[pass_type] = int(values.sum().sum())

    return result

# =====================================================
# 11. PASSING TENDENCY CONTEXT (QUALITATIVE – CORRECT)
# =====================================================

passing_tendencies = pd.DataFrame({
    "team": ["Newcastle United", "Chelsea"],
    "tendency_summary": [
        "Passing types reviewed from FBref Passing Types table. Distribution across short, medium and long passing used for qualitative context only.",
        "Passing types reviewed from FBref Passing Types table. Distribution across short, medium and long passing used for qualitative context only."
    ]
})

passing_tendencies.to_csv(
    os.path.join(DATA_CLEAN, "passing_tendencies.csv"),
    index=False
)



# =====================================================
# 12. GOALKEEPER CONTEXT
# =====================================================
goalkeeper_summary = pd.DataFrame({
    "team": ["Newcastle United", "Chelsea"],
    "saves": [
        pd.to_numeric(newcastle_gk["saves"].sum(), errors="coerce"),
        pd.to_numeric(chelsea_gk["saves"].sum(), errors="coerce")
    ]
})

goalkeeper_summary.to_csv(
    os.path.join(DATA_CLEAN, "goalkeeper_summary.csv"),
    index=False
)

print("Newcastle United vs Chelsea — FULL progression analysis complete.")
