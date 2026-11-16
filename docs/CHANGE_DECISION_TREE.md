# Change and Decision Tree

This file is the structured history of the project changes recorded during this collaboration. The JSON below is ordered by phase and then by commit. Every event includes its trigger, decision, reason, files, and verification notes. Git commit history remains the authoritative source for exact diffs.

The log begins from the clean `main` baseline below. It distinguishes user requests from course requirements contained in the project documents. Those course requirements are recorded as context, not silently treated as completed work.

## Structured record

```json
{
  "schema_version": "1.0",
  "repository": {
    "name": "IIT_GN_W06",
    "remote": "https://github.com/rohitpandeyai-star/IIT_GN_W06.git",
    "branch": "main",
    "baseline": {
      "commit": "1a4a978e7b5c8d7359569c5c2ff90e0923aa6b2d",
      "message": "updates",
      "observed_state": "Clean working tree, synchronized with origin/main before this collaboration's first repository change."
    }
  },
  "reading_guide": {
    "ordering": "Phases and events are in chronological order. Each commit is a separate event, including tracker-only commits.",
    "meaning": "A reason explains why the change was made. A decision records the chosen treatment. Verification describes what was actually checked, not what remains to be done.",
    "course_instructions": "Requirements in the supplied course documents are context. They are not recorded as completed merely because they appear here.",
    "self_reference": "The ledger records its initial creation commit after that commit is made. Its later hash-recording commit is visible in Git history and is not recursively recorded inside itself."
  },
  "change_tree": [
    {
      "phase_sequence": 1,
      "phase_id": "execution_tracker",
      "purpose": "Turn the announcement and repository instructions into an ordered, role-based work plan with reversible checkpoints.",
      "events": [
        {
          "sequence": 1,
          "commit": "c4e7b118b4a1a087de3db7e471eb257fc7d56aff",
          "parent": "1a4a978e7b5c8d7359569c5c2ff90e0923aa6b2d",
          "timestamp_local": "2026-11-16T22:57:13+05:30",
          "message": "docs: add role-based execution tracker",
          "kind": "artifact_creation",
          "trigger": "User asked for a tree of files to fill and tasks to execute by role, with progress context and commits at each step.",
          "decision": "Create docs/EXECUTION_TRACKER.md as the ordered project index, with owners, files, completion checks, statuses, and a commit log.",
          "reason": "A single tracker makes the required sequence and remaining work reviewable before implementation starts.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "Confirmed the repository was clean before the tracker change. No project deliverables were filled by this commit.",
          "pushed_to": "origin/main"
        },
        {
          "sequence": 2,
          "commit": "c085f90be8c6e23b3867cc570837ae98ef28ad8d",
          "parent": "c4e7b118b4a1a087de3db7e471eb257fc7d56aff",
          "timestamp_local": "2026-11-16T22:57:54+05:30",
          "message": "docs: record tracker checkpoint",
          "kind": "tracker_update",
          "trigger": "The tracker creation checkpoint had been committed.",
          "decision": "Mark setup/source review complete and record the tracker creation hash.",
          "reason": "Keep the tracker aligned with Git history and make the setup checkpoint traceable.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "Tracker update committed; branch later confirmed synchronized with origin/main.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 2,
      "phase_id": "source_context",
      "purpose": "Summarize supplied reference materials without confusing their course instructions with the user's immediate request.",
      "events": [
        {
          "sequence": 3,
          "commit": "cd07292ef209ed05104c2e16e2c3b4dbffc79d24",
          "parent": "c085f90be8c6e23b3867cc570837ae98ef28ad8d",
          "timestamp_local": "2026-11-16T23:20:03+05:30",
          "message": "docs: summarize supplied course references",
          "kind": "reference_summary",
          "trigger": "User asked to read all supplied Word files and the announcement PowerPoint and gather their context in Markdown.",
          "decision": "Create docs/SOURCE_CONTEXT.md and add it to the tracker file tree.",
          "reason": "Centralize the client brief, playbook, templates, and 12-slide announcement context for later work.",
          "files_changed": ["docs/SOURCE_CONTEXT.md", "docs/EXECUTION_TRACKER.md"],
          "verification": "Read all three DOCX files and the 12-slide PPTX. Marked home-health worked examples as examples, not hotel facts. Flagged the playbook path typo aibenchmark versus the repository's ai_benchmark.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 3,
      "phase_id": "role_assignment",
      "purpose": "Record the user's explicit assignment of the four project roles.",
      "events": [
        {
          "sequence": 4,
          "commit": "c6ac670be6f3cf294f31eef48cfaebd7a1494c00",
          "parent": "cd07292ef209ed05104c2e16e2c3b4dbffc79d24",
          "timestamp_local": "2026-11-16T23:44:04+05:30",
          "message": "docs: assign all roles to Rohit Pandey",
          "kind": "role_assignment",
          "trigger": "User instructed that all roles be assigned to Rohit Pandey.",
          "decision": "Set Rohit Pandey as Client Lead, Data Lead, Model Lead, and Build Lead in the charter and README roster; update the tracker.",
          "reason": "Record the user's direct assignment in the project artifacts.",
          "files_changed": ["docs/CHARTER.md", "README.md", "docs/EXECUTION_TRACKER.md"],
          "verification": "Confirmed all four role rows contain Rohit Pandey. Recording links and challenger signatures remain blank because they were not completed.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 4,
      "phase_id": "charter_rough_draft",
      "purpose": "Fill the charter questions with the roughness and deliberate weakness explicitly requested by the user.",
      "events": [
        {
          "sequence": 5,
          "commit": "b03e701ae552c57e6de6f11544c4cfdd98fd3b4f",
          "parent": "c6ac670be6f3cf294f31eef48cfaebd7a1494c00",
          "timestamp_local": "2026-11-16T23:50:48+05:30",
          "message": "docs: draft charter with review prompts",
          "kind": "rough_draft",
          "trigger": "User asked to fill the charter with some vagueness or incorrectness.",
          "decision": "Fill all nine questions as an intentionally rough discussion draft; flag unverified claims and mark the booking-level unit guess as probably wrong.",
          "reason": "Provide the requested reviewable draft without presenting invented data checks as findings.",
          "files_changed": ["docs/CHARTER.md", "docs/EXECUTION_TRACKER.md"],
          "verification": "The charter labels itself AI-assisted and not compliant with the course's AI-free paper-frame V0 instruction. Step 1 was marked In progress. No data checks were claimed.",
          "pushed_to": "origin/main"
        },
        {
          "sequence": 6,
          "commit": "00e3c319f4584fb8b3017ddfa099cb6b97336d24",
          "parent": "b03e701ae552c57e6de6f11544c4cfdd98fd3b4f",
          "timestamp_local": "2026-11-16T23:51:19+05:30",
          "message": "docs: record charter draft checkpoint",
          "kind": "tracker_update",
          "trigger": "The rough charter checkpoint had been committed.",
          "decision": "Record the charter draft commit hash in the tracker.",
          "reason": "Make the intentionally incomplete draft and its review state traceable.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "Step 1 remains In progress; the paper-frame and data checks are still outstanding.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 5,
      "phase_id": "initial_notebook_context",
      "purpose": "Mirror the charter's draft number-check status into the two supplied notebooks after the user requested it.",
      "events": [
        {
          "sequence": 7,
          "commit": "21b0369e92fed38493af451223b4fe20cf64c6f7",
          "parent": "00e3c319f4584fb8b3017ddfa099cb6b97336d24",
          "timestamp_local": "2026-11-17T00:06:05+05:30",
          "message": "docs: mirror charter checks in notebooks",
          "kind": "draft_notebook_context",
          "trigger": "User asked to populate both notebooks with the charter content.",
          "decision": "Add a draft status table to notebooks/00_start_here.ipynb and data/data_explore.ipynb, keeping unchecked items marked as unchecked.",
          "reason": "Carry the charter's current state into the notebooks without inventing computed results.",
          "files_changed": ["notebooks/00_start_here.ipynb", "data/data_explore.ipynb", "docs/EXECUTION_TRACKER.md"],
          "verification": "Both notebook JSON files parsed successfully. Existing cached outputs were preserved. This draft-only table was later replaced by calculated Pandas checks.",
          "pushed_to": "origin/main"
        },
        {
          "sequence": 8,
          "commit": "6327e2a3449b4249c9e4a4654f43408533341e72",
          "parent": "21b0369e92fed38493af451223b4fe20cf64c6f7",
          "timestamp_local": "2026-11-17T00:06:36+05:30",
          "message": "docs: record notebook checkpoint",
          "kind": "tracker_update",
          "trigger": "The draft notebook-context checkpoint had been committed.",
          "decision": "Record the notebook checkpoint hash and keep Step 2 In progress.",
          "reason": "Notebook presence did not mean the data pass was complete.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "No notebook calculations were run in this checkpoint.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 6,
      "phase_id": "calculated_brief_checks",
      "purpose": "Replace draft-only rows with Pandas calculations and visible results while protecting the proof period.",
      "events": [
        {
          "sequence": 9,
          "commit": "3d11379ad0e1eacc2a4142720333a494936988e6",
          "parent": "6327e2a3449b4249c9e4a4654f43408533341e72",
          "timestamp_local": "2026-11-17T00:16:19+05:30",
          "message": "notebooks: calculate brief number checks",
          "kind": "data_check_notebook",
          "trigger": "User clarified that the notebooks should contain simple Pandas code showing the numbers, not only copied draft statuses.",
          "decision": "Add Pandas checks and saved table outputs for raw dimensions, arrival dates, train/choose/proof counts, cancellation rates on train+choose, client thresholds, and unverified claims.",
          "reason": "Show measured values where the CSV can answer, and clearly label client assumptions that cannot be verified from booking rows.",
          "files_changed": ["notebooks/00_start_here.ipynb", "data/data_explore.ipynb", "docs/EXECUTION_TRACKER.md"],
          "data_results": {
            "raw_rows": 119390,
            "raw_columns": 32,
            "arrival_date_range": ["2015-07-01", "2017-08-31"],
            "train": {"bookings": 49157, "arrival_dates": ["2015-07-01", "2016-06-30"], "cancellation_rate": "35.8%"},
            "choose": {"bookings": 29546, "arrival_dates": ["2016-07-01", "2016-12-31"], "cancellation_rate": "36.9%"},
            "proof": {"bookings": 40687, "arrival_dates": ["2017-01-01", "2017-08-31"], "cancellation_rate": "not calculated in this early check"},
            "train_plus_choose_cancellation_rate": "36.2%",
            "hotel_cancellation_rates_train_plus_choose": {"City Hotel": "41.3%", "Resort Hotel": "26.3%"}
          },
          "reasoned_constraints": ["Proof-period cancellation outcomes were not used in the summary.", "EUR 300 and 10 walks per 1,000 are client scoring assumptions, not observed data values.", "The current flat-rule safety margin and the vendor's 95% accuracy claim require client/source evidence."],
          "verification": "Executed the calculation cells against data/hotels.csv and confirmed notebook JSON validity. No pytest run was requested.",
          "pushed_to": "origin/main"
        },
        {
          "sequence": 10,
          "commit": "b363035cf79c7304cbab002aeb63add1e94edf2b",
          "parent": "3d11379ad0e1eacc2a4142720333a494936988e6",
          "timestamp_local": "2026-11-17T00:16:50+05:30",
          "message": "docs: record brief check notebook results",
          "kind": "tracker_update",
          "trigger": "The calculated notebook-check checkpoint had been committed.",
          "decision": "Update Step 2 notes and record the calculation checkpoint hash.",
          "reason": "Keep the tracker aligned with the actual computed outputs and the untouched proof labels.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "Step 2 remains In progress; charter reconciliation is pending.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 7,
      "phase_id": "notebook_readability_refactor",
      "purpose": "Make notebook structure easier to follow, with comments and grouped cells.",
      "events": [
        {
          "sequence": 11,
          "commit": "c3da90a7afa4aa9c15ac149a9355f6dd8a5af23f",
          "parent": "b363035cf79c7304cbab002aeb63add1e94edf2b",
          "timestamp_local": "2026-11-17T00:24:50+05:30",
          "message": "notebooks: group brief checks into clear sections",
          "kind": "notebook_refactor",
          "trigger": "User asked for clean code, ease of understanding, proper comments, simple syntax, and information grouped by notebook cells.",
          "decision": "Split each notebook into labeled sections for loading data, checking periods, comparing cancellation rates, and listing remaining client numbers; save outputs below relevant calculation cells.",
          "reason": "Reduce cognitive load and make each calculation and its purpose visible in order.",
          "files_changed": ["notebooks/00_start_here.ipynb", "data/data_explore.ipynb", "docs/EXECUTION_TRACKER.md"],
          "verification": "Executed the table cells to refresh visible outputs. Proof-period cancellation labels remain unused.",
          "pushed_to": "origin/main"
        },
        {
          "sequence": 12,
          "commit": "9fae4561cbdb58eedc9f4a71ae7c5ea212841273",
          "parent": "c3da90a7afa4aa9c15ac149a9355f6dd8a5af23f",
          "timestamp_local": "2026-11-17T00:25:19+05:30",
          "message": "docs: record notebook layout checkpoint",
          "kind": "tracker_update",
          "trigger": "The notebook readability checkpoint had been committed.",
          "decision": "Record the refactor hash in the tracker.",
          "reason": "Preserve one separately reversible checkpoint per requested step.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "Notebook sections and output tables remain present; Step 2 remains In progress.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 8,
      "phase_id": "hotel_count_check",
      "purpose": "Close a missing numeric check in the brief-number table.",
      "events": [
        {
          "sequence": 13,
          "commit": "3ae076ef14aed745040b9e506b2036ed7e6ba5c6",
          "parent": "9fae4561cbdb58eedc9f4a71ae7c5ea212841273",
          "timestamp_local": "2026-11-17T00:35:59+05:30",
          "message": "notebooks: verify hotel count in brief checks",
          "kind": "data_check_completion",
          "trigger": "A completeness review found the explicit two-hotel count was missing from the number table.",
          "decision": "Add a Pandas distinct-hotel count and save the updated output in both notebooks.",
          "reason": "Make the two-hotel claim directly checkable against the dataset rather than infer it from other rows.",
          "files_changed": ["notebooks/00_start_here.ipynb", "data/data_explore.ipynb", "docs/EXECUTION_TRACKER.md"],
          "data_result": {"distinct_hotels": 2, "hotel_names": ["City Hotel", "Resort Hotel"]},
          "verification": "The distinct-hotel check returned 2 in both notebooks; proof cancellation labels remained unused.",
          "pushed_to": "origin/main"
        },
        {
          "sequence": 14,
          "commit": "d12068b79a0df6b9747c73a16a8f62a81afd3583",
          "parent": "3ae076ef14aed745040b9e506b2036ed7e6ba5c6",
          "timestamp_local": "2026-11-17T00:36:29+05:30",
          "message": "docs: record hotel count check",
          "kind": "tracker_update",
          "trigger": "The two-hotel check checkpoint had been committed.",
          "decision": "Record the hotel-count checkpoint hash in the tracker.",
          "reason": "Keep the notebook finding and tracker history synchronized.",
          "files_changed": ["docs/EXECUTION_TRACKER.md"],
          "verification": "Branch confirmed clean and synchronized with origin/main.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 9,
      "phase_id": "change_decision_ledger",
      "purpose": "Create this structured, sequential tree of changes and decisions.",
      "events": [
        {
          "sequence": 15,
          "commit": "562de9a2b428b949bc771f9dc399c693315c83f8",
          "parent": "d12068b79a0df6b9747c73a16a8f62a81afd3583",
          "timestamp_local": "2026-11-17",
          "message": "docs: add structured change and decision tree",
          "kind": "ledger_creation",
          "trigger": "User asked for another Markdown file in structured JSON format that records important details, every change and decision sequentially, with reasons.",
          "decision": "Create docs/CHANGE_DECISION_TREE.md and add it to the execution tracker's docs tree.",
          "reason": "Provide a navigable, machine-readable history of why each artifact changed, what files changed, what was verified, and which commit contains the change.",
          "files_changed": ["docs/CHANGE_DECISION_TREE.md", "docs/EXECUTION_TRACKER.md"],
          "verification": "The JSON block parses successfully; the creation commit is 562de9a2b428b949bc771f9dc399c693315c83f8 and will be pushed with this finalization update.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 10,
      "phase_id": "defence_preparation",
      "purpose": "Prepare a concise, evidence-based guide for explaining the project and its current limits.",
      "events": [
        {
          "sequence": 16,
          "commit": "13e90fc6775ed1cbd4507836dd5b67d240019d20",
          "parent": "97b3e0bdafa62628609c784e6a1db6bcc8dbd679",
          "timestamp_local": "2026-11-17",
          "message": "docs: add defence preparation guide",
          "kind": "study_guide",
          "trigger": "User asked for a concise decision tree and relevant project facts to prepare for questions the next day.",
          "decision": "Create docs/DEFENCE_QUICK_GUIDE.md with the decision flow, checked numbers, likely questions, and explicit limits on current claims; add it to the execution tracker tree.",
          "reason": "A short, evidence-linked study aid helps the user explain what is known and distinguish it from assumptions and unfinished project work.",
          "files_changed": ["docs/DEFENCE_QUICK_GUIDE.md", "docs/EXECUTION_TRACKER.md"],
          "verification": "Guide content reflects the tracker, evaluation contract, brief, and notebook checks. No model or proof performance is claimed.",
          "pushed_to": "origin/main"
        }
      ]
    },
    {
      "phase_sequence": 11,
      "phase_id": "charter_working_draft",
      "purpose": "Complete the charter's project framing and checked-number context while preserving the required distinction between AI-assisted support and the AI-free paper frame.",
      "events": [
        {
          "sequence": 17,
          "commit": "47a1c8f6fda8ef087ac77511742262a0627cc892",
          "parent": "6558df289c7bb9d729db5336335b449d67c780c6",
          "timestamp_local": "2026-11-17",
          "message": "docs: complete charter working draft",
          "kind": "charter_update",
          "trigger": "User asked to complete the paper frame in the assistant's words.",
          "decision": "Complete docs/CHARTER.md as an explicitly AI-assisted reference draft, correct the decision unit and metric definitions against the evaluation contract, add notebook-checked figures, and state open client questions and project limits.",
          "reason": "Provide the requested complete framing without misrepresenting it as the course-required AI-free paper frame; avoid inventing unspecified client values.",
          "files_changed": ["docs/CHARTER.md"],
          "verification": "Checked wording against BRIEF.md, docs/EVALUATION_CONTRACT.md, existing notebook-check results, and tracker status. The course-required student-written no-AI paper frame remains outstanding.",
          "pushed_to": "origin/main"
        }
      ]
    }
  ],
  "current_snapshot": {
    "as_of": "2026-11-17",
    "latest_recorded_commit": "13e90fc6775ed1cbd4507836dd5b67d240019d20",
    "defence_guide": "docs/DEFENCE_QUICK_GUIDE.md; study aid only, and explicitly distinguishes measured checks, client assumptions, and pending work.",
    "charter_status": "Completed AI-assisted reference draft; does not satisfy the course-required AI-free paper frame.",
    "last_known_commit_before_this_ledger": "d12068b79a0df6b9747c73a16a8f62a81afd3583",
    "working_tree_before_this_ledger": "clean",
    "role_assignment": {"Client Lead": "Rohit Pandey", "Data Lead": "Rohit Pandey", "Model Lead": "Rohit Pandey", "Build Lead": "Rohit Pandey"},
    "tracker_status": {"step_0": "Complete", "step_1": "In progress", "step_2": "In progress", "steps_3_to_10": "Not started"},
    "notebook_status": "Both notebooks contain grouped Pandas cells and saved tables for brief checks. Proof-period cancellation outcomes are held back.",
    "data_results": {"rows": 119390, "columns": 32, "hotels": 2, "train_choose_cancellation_rate": "36.2%", "proof_cancellation_rate": "not calculated in early checks"},
    "unresolved_items": ["Reconcile the charter with the notebook findings.", "Ask for the current flat-rule safety margin.", "Verify the vendor 95% accuracy claim if evidence exists.", "Do not claim an observed walk rate until a rule is evaluated.", "The no-AI paper-frame requirement remains outstanding."],
    "implementation_scope": {"files_not_changed": ["src/contract.py", "src/features.py", "src/backtest.py", "src/nightly.py"], "test_suite_run": false}
  }
}
```
