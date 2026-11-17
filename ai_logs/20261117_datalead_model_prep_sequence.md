# AI Session Log: Reorder Step 5 Before Model Comparison

**Date:** 2026-11-17  
**Roles:** Data Lead and Build Lead (Rohit Pandey is assigned all roles)  
**Tool:** Codex AI assistant  
**Purpose:** The user clarified that cleaning, full EDA, feature selection/engineering, and model-preparation splitting have not been completed.

## Repository facts reviewed

- `src/data.py` reads the source unchanged; no `src/features.py` exists yet.
- The notebooks contain brief-number checks and use/describe the contract's arrival-date periods, but this is not a complete modeling data-preparation pipeline.
- No full EDA or cleaning decisions are recorded.

## Work produced

- Reordered the PRD and POC plan so raw schema checks come first, then the contract arrival-date split, train-focused EDA, documented cleaning/retention choices, train-only feature transformations, and only then model comparison.
- Clarified that the 32 Bin 1 classifications define a provisional candidate feature pool, not completed feature selection or engineering.
- Included the user's intended model families (Random Forest, XGBoost, CatBoost) alongside logistic regression, shallow tree, lookup, and flat-rule baseline.
- Increased the POC/data-preparation estimate from 12 to 18 hours; all hours remain planning estimates.
- Kept Step 5 not started. No data was cleaned, no features were selected or engineered, and no model was trained.

## Data separation

The contract's train/choose/proof date periods and some brief checks already exist. The modeling pipeline still needs to implement and verify those splits. Proof outcomes remain unused until all choices are frozen.
