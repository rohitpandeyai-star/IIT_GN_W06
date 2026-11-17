# AI Session Log: Duplicate Investigation Notebook

**Date:** 2026-11-17  
**Role:** Data Lead  
**Tool:** Codex AI assistant  
**Purpose:** The user asked for a separate notebook to examine the exact repeated training rows before deciding whether to retain them.

## Work produced and executed

- Created `notebooks/03_duplicate_investigation.ipynb` and executed its five code cells on the training period only.
- Counted 3,472 exact repeated row patterns, covering 19,763 rows and 16,291 later occurrences; the largest group has 150 copies.
- Inspected representative groups and the outcome/status composition within repeated groups.
- Compared keep-all with a hypothetical collapse: rows 49,157 to 32,866; cancellation rate 35.77% to 22.17%; 657 hotel-arrival nights have changed row counts.
- Left the original train data unchanged; the notebook decision cell remains pending.

## Limits

The data contains no booking ID, so these repeated values cannot be proven to be duplicate exports rather than distinct bookings. The hypothetical collapse is sensitivity analysis only. Choose and proof outcomes were not used.
