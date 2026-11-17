# Which rules must a coding agent follow in this repository?

## Which rules has our team set?

1. Keep `src/contract.py` unchanged; use its scoring formulas, hotel-night unit, and arrival-date periods as supplied.
2. Do not use proof-period outcomes to choose features, methods, or buffers; freeze choices on the choose period and run proof once.
3. Do not use `is_canceled`, reservation outcomes, or other post-outcome fields as predictors.
4. Use a time-based arrival-date split; do not replace the contract periods with a random split.
5. Compare every candidate with the flat-rule baseline on the same hotel-nights and report euros alongside empty rooms and walked guests.
6. Enforce the group-wide walk ceiling on choose and report it on proof; report hotel-level results separately without claiming unprovided per-hotel thresholds.
7. Do not claim a live morning forecast from final-book data; identify the need for timestamped reservation snapshots.
8. Do not claim savings, proof performance, or vendor-accuracy validation until the relevant evidence exists.

## Which general coding guidelines apply?

Behavioral guidelines to reduce common coding mistakes. Merge these with the project-specific rules above.

### 1. Think before coding

State assumptions explicitly. If multiple interpretations exist, surface them instead of choosing silently. Call out simpler approaches and push back when warranted. If something is unclear, stop and name what needs clarification.

### 2. Simplicity first

Write the minimum code that solves the requested problem. Avoid unrequested features, one-use abstractions, and speculative flexibility. Simplify code that has become more complicated than necessary.

### 3. Make surgical changes

Change only what the request requires. Do not refactor unrelated code or remove pre-existing code just because it appears unused. Match the existing style. Every changed line should connect to the task.

### 4. Work toward a verifiable goal

Define concrete success criteria and check them. For multi-step work, state the brief plan and how each step will be verified. Keep working until the stated criteria are satisfied or report the blocker clearly.
