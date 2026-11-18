# Presentation QA — `Hotel_Overbooking_New_Deck.pptx` (18 slides)

**Built:** 18 November 2026 with python-pptx from `presentation/deck_data.json`.
**Basis:** notebooks 10–16, with outputs in `data/models/` and `models/`.
**Rendering:** every slide was rendered by Microsoft PowerPoint 16 (COM export to 1600 × 900 PNG) and inspected.

## What changed from the previous version

**Model story.** Slides 1 and 6–12 now follow notebooks 11–16. They replace the `notebooks/pipeline` story (calibrated logistic regression, shared margin 17).

| Slide | Section | Notebook |
|---|---|---|
| 6 | Encoding and settings | 10–11 |
| 7 | Training | 11 |
| 8 | Validation | 12 |
| 9 | Buffers and costs | 12–13 |
| 10 | The choice: CatBoost, buffers 6 / 3 | 13 |
| 11 | Test run 1 | 14 |
| 12 | Retraining: runs 1–3 | 15–16 |
| 13–17 | Decisions by lead: theory and logic | 03–16 |
| 18 | Conclusion | — |

**Kept:** slides 2–5 (decision, data, columns, cleaning).

**Decisions by lead (slides 13–17):** five slides added, one each for the Client, Data and Build Leads and two for the Model Lead. Each gives Decision | Theory behind it | How it played out here. The conclusion is now slide 18. The layout follows the role-per-slide idea of the earlier panel deck; every figure comes from the current notebooks through `deck_data.json` (new block `nb.leads`).

**Title answer:**
- The flat rule (City 20, Resort 4) costs €3.21M at 7.18 walks per 1,000.
- CatBoost costs +€150,459.
- Refitted models walk 13.1 per 1,000.

**Recommendation:** keep the flat rule, with a margin per hotel.

**The previous version** is still saved as `Hotel_Overbooking_New_Deck_updated.pptx`.

## Checks

| Check | Result |
|---|---|
| Format | 16:9 (13.333 × 7.5 in), 18 slides |
| `validate.py` | All validations passed |
| Speaker notes | All content slides |
| Data checks in `deck_data.py` | Per-hotel validation costs equal notebook 13 (flat €1,950,066, CatBoost €1,922,977); resample shares CatBoost 74%, XGBoost 69%; cleaning counts equal the notebook 05 log |

## Contract checks

| Rule | How the deck handles it |
|---|---|
| Choice made before the test | CatBoost and its buffers were frozen at 01:57:07, before any test file was opened (slide 10) |
| Every test run reported | Run 1, run 2 (never run) and run 3 are all on slide 12. Run 3 is labelled "after run 1" |
| No tuning on the test | Slide 12 states that choosing a bigger buffer now would be tuning on the test |
| Same nights as the flat rule | Every comparison is against the flat rule on the same hotel-nights, with euros, empty rooms and walks |
| Walk limit | Enforced group-wide on validation and reported on the test. Hotel figures are not called breaches |
| No claimed savings | No saving is claimed. CatBoost cost more on the test |

## Issues found on render, and fixes

| Slide | Issue | Fix |
|---|---|---|
| 2 | The period bar said "Test · once", but the test was scored twice | Now reads "Test · Jan–Aug 2017" |
| 9 | The answer line wrapped onto the table | Shorter wording |
| 11 | The title wrapped into the answer line | Shorter title: "What happened on the 2017 test?" |
| 15 | The formula strip wrapped to two lines | Shorter example text |
| 16 | The answer wrapped; the theory box overflowed; "61 × 61 pairs per hotel" was wrong | Shorter text; now "every City / Resort pair (61 × 61)" |

## Open points

- **No screenshots beside numbers.** `docs/PRESENTATION.md` asks for a screenshot of the producing code and output beside every number.
- **Test scored twice.** Run 3 was decided after run 1's result. The deck discloses this, so its numbers are retrospective.
- **Morning forecast not shown.** The data is final-book data, so the deck shows no live morning forecast. Timestamped booking snapshots are listed as a next step.
