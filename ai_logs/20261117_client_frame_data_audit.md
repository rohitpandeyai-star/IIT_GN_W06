# AI Session Log: Client Frame and Data Timing Audit

**Date:** 2026-11-17  
**Roles:** Client Lead and Data Lead  
**Tool:** AI assistant in Codex  
**Purpose:** At the user's direction, complete the AI-assisted RFP and move to the column timing/data-decision audit. The user explicitly asked to proceed with AI assistance. The outputs are labeled AI-assisted; they are not represented as meeting the course's AI-free paper-frame requirement.

## Inputs reviewed

- Repository brief and `src/contract.py` definitions summarized in `docs/EVALUATION_CONTRACT.md`.
- Existing notebook counts and hotel-level train/choose cancellation checks.
- Dataset source notes in `data/README.md`.
- Antonio, de Almeida and Nunes (2019), [*Hotel booking demand datasets*](https://doi.org/10.1016/j.dib.2018.11.126), especially Table 1 and section 2, for source tables and time-of-capture limitations.
- User instruction to complete the RFP and continue to the next step, while labeling AI assistance.

## Work produced

- Completed the hotel-specific RFP, with explicit time periods, walk threshold, euro comparison, data constraints, deliverables, and unresolved client questions.
- Corrected the domain note so it does not assert an undocumented vendor payment arrangement.
- Classified all 32 supplied columns conservatively by timing. Uncertain or amendable fields are excluded from the selected MVP inputs unless an actual point-in-time snapshot is verified; outcomes remain labels only.
- Recorded data handling choices: no rows cleaned, filtered, recoded, or deduplicated in the current profile; proof outcomes remain held for final evaluation; hotels remain separate in reporting.
- Updated tracker to reflect that the user has chosen an AI-assisted workflow. The course's AI-free requirement is explicitly disclosed as unmet.

## Human review required

- Confirm the flat-rule safety margin and whether it differs by hotel.
- Confirm if the walk ceiling must hold for each hotel independently.
- Confirm any minimum savings target and the actual decision-time snapshot needed for a live morning table.
- Review the conservative column bins against the original PMS schema/change-log before using any ambiguous column.

## Known limits

- The public dataset article describes values extracted from booking/change-log records as of the day before arrival. This does not establish every feature's value at initial booking time.
- The existing early notebook profile did not calculate proof cancellation outcomes. No method performance or savings were computed in this session.
- The AI-free course paper-frame requirement remains unmet by these labeled AI-assisted materials.

## Follow-up: learner-led audit

The user clarified that the column audit must be completed by them, sequentially, in a Jupyter notebook, so they understand the evidence and make their own decisions. In response:

- Created `notebooks/01_column_audit_workshop.ipynb` with 45 ordered cells, grouped evidence displays, and blank bin/reason prompts for each of the 32 CSV columns.
- The notebook only shows value examples from train + choose; proof-period cancellation labels are not inspected. Its final cell saves a separate review file only after the learner has entered a valid bin and reason for every column.
- Re-labeled `docs/COLUMNS.md` and `docs/DECISIONS.md` as AI-generated preliminary suggestions/observations. They are not considered the learner's completed audit.
- Reopened Step 2 in the execution tracker. It remains in progress until the learner runs the notebook and records their choices.

The notebook structure was checked to confirm that all 32 CSV fields appear exactly once in both the evidence groups and blank decision prompts. The cells were not executed and no classifications were chosen in this follow-up.
