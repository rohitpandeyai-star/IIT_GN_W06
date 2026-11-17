# What did the AI build get wrong, and what did it expose in ours?

**Owner:** Data Lead. **Challenger:** Build Lead. **When:** started on Thursday, finished on Friday.

Compare your build on `main` with the AI build on the `ai-benchmark` branch, row by row. Every cell points to a file and a line, or to a log excerpt. "Same" is an acceptable verdict when it is true.

> **Status (2026-11-18):** the AI build is **not available**. The repository has no `ai-benchmark` branch, and `ai_benchmark/PLAN_AI.md`, `ai_benchmark/run.py` and `ai_benchmark/RESULT.md` do not exist (`evidence/ai_benchmark_review/ai_branch_artifact_status.csv`). The "Our build" column is filled from the executed pipeline in `notebooks/pipeline/`; the AI column and every AI finding stay empty until the branch exists. No AI mistake is inferred from its absence.

| Row | Our build | AI build | Verdict |
|---|---|---|---|
| What counts as a cancellation, and which bookings are scored | `is_canceled` = 1 (cancellations and no-shows); every booking whose arrival falls in the period is scored (`src/contract.py`, `nightly_table`; `notebooks/pipeline/11_choose_policy_selection.ipynb` §6) | Not available | Cannot compare |
| Unit of decision (night or booking) | Hotel × arrival night: booking probabilities summed per night (`src/contract.py`, `nightly_table`) | Not available | Cannot compare |
| Columns used, and the bin each sits in | 8 inputs, `country` held back (`src/features.py`, `HELD_BACK`; `notebooks/pipeline/05_feature_engineering.ipynb` §2); four are provisional on timing (`docs/DECISIONS.md` P3) | Not available | Cannot compare |
| Split (time or random), and where the buffer was chosen | Contract arrival-date periods; hyperparameters by expanding folds inside Train (`08_hyperparameter_experiments.ipynb` §3); margin chosen on Choose (`11_choose_policy_selection.ipynb` §8b, §10) | Not available | Cannot compare |
| Baselines run before any model | Global, hotel and pooled rates (`06_baselines_and_pooling_lab.ipynb`); dummy (`07`); contract flat rule with margin (`11` §8b) | Not available | Cannot compare |
| Walk ceiling respected on the choose period and reported on proof | Enforced on Choose: flat rule margin 17, 9.06 per 1,000 (`evidence/choose_policy_selection/choose_policy_scores.csv`); reported on Proof: 6.21 (`evidence/proof_evaluation/proof_group_score.csv`) | Not available | Cannot compare |
| Euros, rooms and walks per 1,000 on the proof period | EUR 3,935,876; 8,186 empty rooms; 155 walks; 6.21 per 1,000 — retrospective, Proof previously exposed (`evidence/proof_evaluation/proof_group_score.csv`) | Not available | Cannot compare |
| Runs end to end with one command | No: ten notebooks run in order (`docs/PIPELINE_VALIDATION.md`); the nightly command rejects its stale model (`evidence/nightly_pipeline_validation/smoke_test.json`) | Not available | Cannot compare |
| Lines of code a team member can explain | scikit-learn pipelines plus the contract's functions (`notebooks/pipeline/08`–`12`); not assessed by the team yet | Not available | Cannot compare |

## Which gaps in our build did the AI build expose?

_Up to three, each naming a file and line in our build, or an excerpt from a log. If you found none, say so and name the file that shows it._

<!-- answer:4 -->

None can be stated: the AI build is not available (`evidence/ai_benchmark_review/ai_branch_artifact_status.csv`). The gaps below were found by the team's own audit on 2026-11-18, **not** by an AI build:

1. No as-of booking snapshot: `src/nightly.py` (`load_bookings`) scores every row in the input, including bookings made after, or cancelled before, the decision time.
2. The saved nightly model uses the held-back `country`: `models/xgboost.joblib` is rejected by `src/nightly.py` (`validate_model_schema`), so the nightly command does not currently run.
3. Booking rows stand in for rooms: the contract counts bookings, not physical rooms, and no actual walk records exist (`docs/EVALUATION_CONTRACT.md`).

## Which mistakes did the AI build make that ours did not?

_Up to three, each naming a file and line on the `ai-benchmark` branch. If you found none, say so and name the file that shows it._

<!-- answer:4 -->

None can be stated: there is no `ai-benchmark` branch to inspect (`evidence/ai_benchmark_review/ai_branch_findings.csv` is empty by design).

## What would we take from the AI build, and what would we never ship?

_Two sentences, each pointing to a file and line._

<!-- answer:2 -->

Not answerable until the AI build exists. Run the benchmark as `docs/AI_WORKFLOW.md` describes (separate branch from the first commit, four input files, plan first, 90 minutes), then fill this section.
