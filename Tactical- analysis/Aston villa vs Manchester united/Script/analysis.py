# analysis.py
# Aston Villa vs Manchester United — Match Analysis (Part B)

import pandas as pd
import os

# =====================================================
# 1. PATH SETUP (LOCKED & SAFE)
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
    df.columns = df.iloc[0]
    df = df.drop(index=0)
    df = df.loc[:, df.columns.notna()]
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df.reset_index(drop=True)

# =====================================================
# 3. SAFE NUMERIC EXTRACTOR (FBref DUPLICATES)
# =====================================================
def get_numeric_series(df, col):
    if col not in df.columns:
        return pd.Series(dtype="float64")

    s = df[col]
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]

    return pd.to_numeric(s, errors="coerce")

# =====================================================
# 4. LOAD RAW CSVs (EXACT FILENAMES)
# =====================================================
villa = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Aston Villa team stats.csv"),
    encoding="latin1"
))

united = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Manchester United team stats.csv"),
    encoding="latin1"
))

shots = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Shot table aston villa vs manchester united.csv"),
    encoding="latin1"
))

villa_passing_styles = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Aston villa passing styles.csv"),
    encoding="latin1"
))

united_passing_styles = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Manchester united passing styles.csv"),
    encoding="latin1"
))

villa_pass_types = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Aston Villa pass types.csv"),
    encoding="latin1"
))

united_pass_types = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Manchester United pass types.csv"),
    encoding="latin1"
))

villa_gk = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Aston Villa goalkeeper stats.csv"),
    encoding="latin1"
))

united_gk = clean_fbref(pd.read_csv(
    os.path.join(DATA_RAW, "Manchester United goalkeeper stats.csv"),
    encoding="latin1"
))

# =====================================================
# 5. TEAM SUMMARY
# =====================================================
for col in ["sh", "cmp", "att", "fls", "ck"]:
    villa[col] = get_numeric_series(villa, col)
    united[col] = get_numeric_series(united, col)

team_summary = pd.DataFrame({
    "team": ["Aston Villa", "Manchester United"],
    "shots": [villa["sh"].sum(), united["sh"].sum()],
    "passes_completed": [villa["cmp"].sum(), united["cmp"].sum()],
    "passes_attempted": [villa["att"].sum(), united["att"].sum()],
    "fouls": [villa["fls"].sum(), united["fls"].sum()],
    "corners": [villa["ck"].sum(), united["ck"].sum()]
})

team_summary.to_csv(
    os.path.join(DATA_CLEAN, "team_summary.csv"),
    index=False
)

# =====================================================
# 6. SHOT TABLE CLEANING
# =====================================================
shots["xg"] = pd.to_numeric(shots["xg"], errors="coerce")
shots["minute"] = pd.to_numeric(shots["minute"], errors="coerce")
shots["distance"] = pd.to_numeric(shots["distance"], errors="coerce")

shots = shots.dropna(subset=["xg", "minute", "distance"])

# =====================================================
# 7. SHOT SUMMARY
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
# 8. SHOT OUTCOME BREAKDOWN
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
# 9. SHOT DISTANCE ANALYSIS
# =====================================================
shots["distance_zone"] = pd.cut(
    shots["distance"],
    bins=[0, 6, 12, 18, 100],
    labels=["0–6 yards", "6–12 yards", "12–18 yards", "18+ yards"]
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
# 10. SHOT TIMING (CHRONOLOGICALLY FIXED)
# =====================================================
time_labels = ["0–15", "16–30", "31–45+", "46–60", "61–75", "76–90+", "90+"]
time_bins = [0, 15, 30, 45, 60, 75, 90, 120]

shots["time_window"] = pd.cut(
    shots["minute"],
    bins=time_bins,
    labels=time_labels,
    ordered=True
)

shot_timing = (
    shots
    .groupby(["squad", "time_window"])
    .size()
    .reset_index(name="shots")
)

shot_timing["time_window"] = pd.Categorical(
    shot_timing["time_window"],
    categories=time_labels,
    ordered=True
)

shot_timing.to_csv(
    os.path.join(DATA_CLEAN, "shot_timing_analysis.csv"),
    index=False
)

# =====================================================
# 11. GOAL EVENTS
# =====================================================
goal_events = shots[shots["outcome"] == "Goal"][
    ["minute", "squad", "player", "xg"]
].reset_index(drop=True)

goal_events.to_csv(
    os.path.join(DATA_CLEAN, "goal_events.csv"),
    index=False
)

# =====================================================
# 12. PASSING STYLES (TOTAL PASS VOLUME)
# =====================================================
def extract_passing_styles_total(df):
    """
    Extract total number of short, medium, and long passes
    from FBref passing styles tables.
    """
    output = {}

    for style in ["short", "medium", "long"]:
        cols = [c for c in df.columns if style in c and "att" in c]
        values = df[cols].apply(pd.to_numeric, errors="coerce") if cols else 0
        output[style] = int(values.sum().sum()) if cols else 0

    return output

villa_styles = extract_passing_styles_total(villa_passing_styles)
united_styles = extract_passing_styles_total(united_passing_styles)

passing_styles_summary = pd.DataFrame({
    "team": ["Aston Villa", "Manchester United"],
    "short_passes": [villa_styles["short"], united_styles["short"]],
    "medium_passes": [villa_styles["medium"], united_styles["medium"]],
    "long_passes": [villa_styles["long"], united_styles["long"]]
})

passing_styles_summary.to_csv(
    os.path.join(DATA_CLEAN, "passing_styles_summary.csv"),
    index=False
)


# =====================================================
# 13. PASS TYPES (NUMERIC SUMMARY)
# =====================================================
def extract_pass_types_numeric(df):
    """
    Extract numeric summaries from FBref pass types table.
    """
    keep_cols = [
        c for c in df.columns
        if c not in ["player", "nation", "pos", "age"]
    ]

    numeric_df = df[keep_cols].apply(pd.to_numeric, errors="coerce")
    return numeric_df.sum()

villa_pass_types_summary = extract_pass_types_numeric(villa_pass_types)
united_pass_types_summary = extract_pass_types_numeric(united_pass_types)

pass_types_summary = pd.DataFrame([
    ["Aston Villa"] + villa_pass_types_summary.tolist(),
    ["Manchester United"] + united_pass_types_summary.tolist()
], columns=["team"] + villa_pass_types_summary.index.tolist())

pass_types_summary.to_csv(
    os.path.join(DATA_CLEAN, "pass_types_summary.csv"),
    index=False
)


# =====================================================
# 14. GOALKEEPER SUMMARY
# =====================================================
goalkeeper_summary = pd.DataFrame({
    "team": ["Aston Villa", "Manchester United"],
    "saves": [
        get_numeric_series(villa_gk, "saves").sum(),
        get_numeric_series(united_gk, "saves").sum()
    ]
})

goalkeeper_summary.to_csv(
    os.path.join(DATA_CLEAN, "goalkeeper_summary.csv"),
    index=False
)

print("Aston Villa vs Manchester United — Part B analysis complete.")
