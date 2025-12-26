# Newcastle United vs Chelsea — Match Performance Summary

## Match Information
- Competition: Premier League
- Fixture: Newcastle United vs Chelsea
- Analysis Type: Post-Match Performance Summary
- Data Sources: FBref, Understat (visual reference)

---

## Analytical Context

This report represents the third iteration of a structured match analysis framework.

Compared to earlier analyses, this report places greater emphasis on contextual interpretation of shot profiles, match dynamics, and defensive contribution, while maintaining a consistent numerical foundation.

---

## Team-Level Performance Overview

### Shot Production & Expected Goals (xG)

Chelsea recorded a higher overall shot volume and total expected goals compared to Newcastle United, indicating greater attacking output over the course of the match.

This is supported by the Power BI team summary, which shows Chelsea leading in both total shots and completed passes.


::contentReference[oaicite:0]{index=0}


---

### Shot Outcome Breakdown

Shot outcome distributions show a balanced mix of blocked, saved, and off-target attempts for both teams, with goal outcomes broadly aligning with expected goals values.

This suggests that finishing performance was largely consistent with chance quality rather than driven by extreme variance.

---

## Shot Distance Profile

Shot distance analysis highlights differences in where attempts were generated:

- Chelsea produced a greater share of shots from shorter and medium-distance zones
- Newcastle United generated a higher proportion of longer-range attempts

These distributions help explain the observed difference in xG efficiency between the two sides.

---

## Match Dynamics — xG Accumulation

The xG timeline illustrates how Chelsea accumulated higher-quality chances across multiple phases of the match, rather than through isolated attacking periods.

Newcastle United’s xG accumulation was more gradual, reflecting fewer high-value chances in central areas.


::contentReference[oaicite:1]{index=1}


---

## Goalkeeper Context

Goalkeeper metrics provide additional defensive context:

- Chelsea’s goalkeeper recorded a higher number of saves
- Newcastle United’s goalkeeper faced fewer high-quality shots overall

This aligns with the shot quality and xG profiles observed.

---

## Passing Context (Qualitative)

Passing tendencies were reviewed using FBref Passing Types tables.

Due to the structure of publicly available match-level passing data, passing patterns are referenced qualitatively rather than through aggregated numeric totals. This ensures analytical accuracy while still informing interpretation of ball progression tendencies.

---

## Methodology Notes

- Numerical metrics derived from publicly available FBref tables
- Python used for data cleaning, aggregation, and validation
- Power BI used for dashboard-based visual communication
- Understat visuals included for contextual illustration only
- Tactical interpretation intentionally limited

---

## Development Summary

Relative to earlier match analyses, this project demonstrates:
- Improved integration of visual outputs
- Clearer communication of match dynamics
- Enhanced defensive context through goalkeeper metrics
- Responsible treatment of passing data

This completes the post-match analysis phase for Newcastle United and Chelsea within the current portfolio.
