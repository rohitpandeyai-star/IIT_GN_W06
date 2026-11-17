# Build Plan: From POC to Reproducible Nightly Table

> **Status: AI-assisted planning draft, prepared at the user's request.** Hour values are planning estimates, not recorded effort. Adjust “Hours used” as work is performed. All four roles are assigned to Rohit Pandey; the role named for each stage is accountable and the other roles review the listed evidence.

| Stage | What is built | Owner | Hours planned | Hours used | Done when | Evidence file |
|---|---|---|---:|---:|---|---|
| POC | Compare the flat-rule baseline, hotel-by-history lookup, logistic regression, and depth-limited decision tree (max depth 3) on the contract's arrival-date split. Select method and buffers on choose; run proof once after freeze. Report AUC as a diagnostic plus nightly error, euros, empty rooms, and walks per 1,000. | Model Lead (Rohit); Data Lead verifies inputs; Client Lead checks the cost rule; Build Lead checks reproducibility | 12 | Not started | `python src/backtest.py` runs end to end; every candidate is scored on the same hotel-nights; choose-period candidate and flat-rule margins meet the walk ceiling; settings are frozen before proof; output includes proof-period comparison and hotel-level diagnostics; no late fields or random split are used. | `src/backtest.py`, `src/features.py`, `docs/DECISIONS.md`, `evidence/poc_results.png` |
| MVP | Produce the requested 14-night historical replay using the frozen method and first-bin predictors. Make the output readable for human review; do not modify reservations. | Build Lead (Rohit); Model Lead freezes method; Data Lead checks timing; Client Lead checks caveats | 8 | Not started | `python src/nightly.py --from 2017-08-18 --nights 14` writes one row per hotel-arrival night, uses only approved first-bin predictors, shows method/expected cancellations/buffer/`k`, and states that it is a historical full-book replay; the independent challenger review is recorded in README. | `src/nightly.py`, `models/`, `README.md`, `evidence/mvp_14_night_table.png` |
| Final | Compare the rooms buffer with the uncertainty buffer; quantify the full-final-book caveat; document architecture, comparison, and production roadmap. Prepare traceable evidence for reported numbers. | Build Lead (Rohit); Data Lead supplies checks; Model Lead supplies frozen settings; Client Lead checks the operating story | 4 | Not started | Both buffer choices are evaluated under the same choose-period ceiling; the selected one is justified before proof; the full-night caveat is quantified from the supplied data and labeled as a limitation; comparison and roadmap have owners/hours; every presentation number points to its source/output. | `docs/COMPARISON.md`, `docs/ROADMAP.md`, `docs/PRD.md`, `docs/architecture.png`, `evidence/` |

**Total initial planning estimate: 24 hours.** This is a proposed effort budget; update it with actual hours as work proceeds. It excludes client discovery, deployment, and the course presentation/defence.

## What would production add that the MVP leaves out?

These rough estimates require technical and client discovery before commitment.

| Addition | Why it matters | Owner | Hours (estimate) |
|---|---|---|---:|
| Timestamped reservation snapshots and point-in-time feature reconstruction | A morning run must use only information available at that time. | Data Lead | 16 |
| PMS data connection, scheduled run, and output delivery | Moves the replay from a local file to an operational feed. | Build Lead | 32 |
| Revenue-manager approval, override, and audit history | Makes the recommendation reviewable and records the final decision. | Client Lead | 16 |
| Monitoring for data shifts, calibration, and walk outcomes | Detects when the historical rule no longer behaves as expected. | Model Lead | 20 |
| Access controls and operational support procedures | Limits access to booking information and clarifies who handles failed runs. | Build Lead | 16 |

## What did we cut, and why?

- **Guest segmentation:** zero segment outputs in the MVP because no client action or value case is defined. Revisit only under the proposed PRD gate: client names an action and segmentation cuts choose-period cost by at least 5% while meeting the walk ceiling.
- **Live morning forecast:** cut because no timestamped reservation snapshots are supplied. The current CLI produces a historical full-book replay.
- **Automatic reservation changes:** cut because the brief asks for recommendations, and approval/override authority is not confirmed.
- **Vendor 95% accuracy replication:** cut until its metric definition, test dates, population, and baseline are provided.
