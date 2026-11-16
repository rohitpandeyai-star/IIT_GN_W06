# Build 2, Week 6 — Role-Based Execution Tracker

This file is the working index for completing the project. Update the status and evidence for each step as the team proceeds. Commit each step as a separate Git checkpoint so the team can return to a known state. Push each checkpoint to its intended GitHub branch. Keep the AI benchmark on `ai-benchmark`; never merge it into `main`.

## Current context

- The announcement deck and the project brief, README, role guide, ladder, AI workflow and artifact templates have been reviewed.
- The project starts on `main`, which was clean and tracking `origin/main` at the time this tracker was prepared.
- `docs/CHARTER.md` now has a deliberately rough, AI-assisted draft at the user direction; it is not the course-required no-AI paper frame. Other project deliverables and implementations remain pending.
- Rohit Pandey is assigned to all four roles, as requested. Project work and challenger sign-offs remain pending until completed.
- Do not commit the downloaded bookings CSV. `src/contract.py` is supplied and must not be edited.

## File tree by role and sequence

```text
IIT_GN_W06/
├── AGENTS.md                         [Build Lead: project rules; AI guideline setup]
├── README.md                         [Build Lead: run instructions, signatures, recording links]
├── BRIEF.md                          [Reference: client question and constraints]
├── data/
│   ├── README.md                     [Reference: source, license, retrieval]
│   ├── hotels.csv                    [Generated input; do not commit]
│   └── data_explore.ipynb            [Data Lead: exploratory checks]
├── notebooks/
│   └── 00_start_here.ipynb           [Data Lead: first profile and data checks]
├── docs/
│   ├── EXECUTION_TRACKER.md           [Living sequence, status and checkpoint log]
│   ├── SOURCE_CONTEXT.md              [Reference synthesis of supplied Word files and announcement deck]
│   ├── CHARTER.md                    [Client Lead: paper frame, metrics, checked numbers]
│   ├── RFP.md                        [Client Lead: client requirements and acceptance terms]
│   ├── DOMAIN.md                     [Reference: hotel terms]
│   ├── COLUMNS.md                    [Data Lead: timing bins and leakage checks]
│   ├── DECISIONS.md                  [All owners: data choices and objections]
│   ├── grill_01_charter.md           [Client Lead: Tuesday grill and resulting changes]
│   ├── grill_02_prd.md               [Build Lead: Thursday grill and resulting changes]
│   ├── PRD.md                        [Build Lead: options, chosen method, design and limits]
│   ├── BUILD_PLAN.md                 [Build Lead: POC, MVP, final stage and production additions]
│   ├── architecture.png              [Build Lead: black-box and white-box diagrams]
│   ├── COMPARISON.md                 [Data Lead; Build Lead challenges: team vs AI build]
│   ├── ROADMAP.md                    [Build Lead: Weeks 7–9 and production additions]
│   ├── PRESENTATION.md               [Reference: ten-slide requirements and evidence]
│   ├── RECORDING.md                  [Reference: individual recording requirements]
│   ├── EVALUATION_CONTRACT.md        [Reference: scoring rules and periods]
│   └── RUBRIC.md                     [Reference: marking criteria]
├── src/
│   ├── data.py                       [Given: downloads bookings]
│   ├── contract.py                   [Given: client scoring rule; never edit]
│   ├── features.py                   [Data Lead: first-bin inputs and documented choices]
│   ├── backtest.py                   [Model Lead: methods, buffer selection, proof table]
│   └── nightly.py                    [Build Lead: next-14-night output]
├── models/                           [Model Lead: frozen chosen method and buffer]
├── tests/                            [Given checks for contract behavior]
├── evidence/                         [Data Lead: slideNN_what.png proof screenshots]
├── ai_logs/
│   ├── INDEX.md                      [Data Lead: index every AI session]
│   └── YYYYMMDD_role_tool_purpose.md [Session logs and pasted text]
└── ai_benchmark/                     [AI build artifacts on ai-benchmark branch]
    ├── PLAN_AI.md
    ├── run.py
    └── RESULT.md
```

`docs/` is the main project record. The presentation and recordings are course deliverables; their final storage location should follow the course submission process. Add links in `README.md` where instructed.

## Ordered execution steps

Statuses: `Complete`, `In progress`, `Not started`, or `Blocked`. A step is complete only when its completion check passes, its files are updated, and a checkpoint commit is recorded. For each step, add the commit hash and push result to the log below. Do not mark a step complete merely because its files exist.

| Step | Day / ladder stage | Owner(s) | Files to fill or run | Completion check | Status |
|---:|---|---|---|---|---|
| 0 | Setup / source review | Team | This tracker; assign role names in `docs/CHARTER.md` and `README.md` at Step 1 | Tracker committed; the team knows the role owners and starts from a recorded Git state | Complete |
| 1 | Tuesday / stages 0–2, paper frame | Client Lead, with all roles contributing facts | `docs/CHARTER.md`, `docs/DOMAIN.md`, `docs/RFP.md` | On paper before any AI: frame the decision and unit; define both costs, north star and guardrail; check every brief number or record a client question; finish the RFP with periods and business-unit thresholds | In progress |
| 2 | Tuesday / stages 0–2, data pass | Data Lead; Client Lead checks brief facts; Model Lead checks target; Build Lead checks usable table | `data/data_explore.ipynb`, `notebooks/00_start_here.ipynb`, `docs/COLUMNS.md`, `docs/DECISIONS.md` | Profile the bookings; log every cleaning/filtering choice and row count; bin every supplied column by when it becomes known; identify bookings governed by different rules and record evidence | Not started |
| 3 | Tuesday / after paper frame and data pass | Client Lead owns Grill 1; Build Lead writes agent rules; Data Lead maintains index | `docs/grill_01_charter.md`, `ai_logs/`, `ai_logs/INDEX.md`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Complete the 45-minute grill and record at least three document changes; log the chat; write at least five actionable project rules from decisions; follow `docs/AI_WORKFLOW.md` for coding-guideline setup | Not started |
| 4 | Wednesday / stages 3 and 5 planning | Build Lead; all roles own their decision input | `docs/PRD.md`, `docs/BUILD_PLAN.md`, `docs/DECISIONS.md` | Before seeing results, compare two approaches, name the choice and flip condition, answer the wish-list item with a number, define the client table and set owners, hours, done checks and evidence for POC/MVP/final | Not started |
| 5 | Wednesday–Thursday / stage 4 POC | Model Lead owns backtest; Data Lead owns feature audit; Client Lead checks money rule; Build Lead checks reproducibility | `src/features.py`, `src/backtest.py`, `docs/COLUMNS.md`, `docs/DECISIONS.md`, `docs/PRD.md`, `docs/BUILD_PLAN.md`, `evidence/` | One command compares flat rule, lookup table and at least two learned models on the same time split; select buffers on choose period under the ceiling; run proof once; report AUC, nightly error, rooms, euros and walks/1,000; chosen rule uses no late columns or random split | Not started |
| 6 | Thursday / stage 5 and stage 6 MVP | Build Lead owns MVP and architecture; Data Lead challenges inputs; Model Lead freezes method; Client Lead checks trust/caveat | `src/nightly.py`, `models/`, `docs/PRD.md`, `docs/BUILD_PLAN.md`, `docs/architecture.png`, `README.md`, `evidence/` | `python src/nightly.py --from 2017-08-18 --nights 14` writes the required table from the bookings file and frozen model, uses only first-bin inputs, and is signed by the challenger in the README | Not started |
| 7 | Thursday / AI benchmark | Data Lead owns benchmark; Build Lead challenges; every AI session logged | `ai_benchmark/PLAN_AI.md`, `ai_benchmark/run.py`, `ai_benchmark/RESULT.md` on `ai-benchmark`; chat log and `ai_logs/INDEX.md` on `main` | Follow `docs/AI_WORKFLOW.md`: start benchmark at the specified base commit, save plan before approval, run within the 90-minute box, commit and push the branch, then return to `main`; never merge benchmark branch | Not started |
| 8 | Friday / stage 7 evidence and next steps | Data Lead owns comparison; Build Lead challenges; Client Lead owns full-night caveat; Model Lead supplies buffer evidence | `docs/COMPARISON.md`, `docs/ROADMAP.md`, `docs/PRD.md`, `docs/CHARTER.md`, `evidence/`, `ai_logs/INDEX.md` | Compare builds row by row with file/line/log references; explain up to three gaps and AI mistakes (or state none with evidence); report full-night caveat by hotel; give Weeks 7–9 owners and hours; index all required AI logs; capture a screenshot for every slide number | Not started |
| 9 | Friday / presentation and individual recordings | Each slide owner; every member owns their own recording; Client Lead checks final story | Ten-slide presentation, `evidence/`, `README.md`, LMS recording links | Slides total ten minutes, start with the answer, show no repeated brief, include required ownership/evidence, and show three grill changes; each member submits a 15–20-minute screen-share recording and adds the LMS link to README | Not started |
| 10 | Saturday / defence | Whole team; panel selects respondent | Frozen repository, presentation, `models/`, `evidence/` | Run the MVP live from the frozen commit; give the six-minute question period; every member can explain every reported number, data bin, method, caveat and AI comparison | Not started |

## Role ownership reference

Assigned team member for Client Lead, Data Lead, Model Lead, and Build Lead: **Rohit Pandey**.

| Role | Owns | Challenges |
|---|---|---|
| Client Lead | Charter and metric tree, RFP, travel-partner view, full-night caveat, slides 1–3 and 10 | Model Lead |
| Data Lead | Profiling, data decisions, column bins, features, AI benchmark, comparison, AI log index, slides 4 and 9 | Build Lead |
| Model Lead | Backtest, method table, choose-period buffer, uncertainty buffer, slides 5 and 6 | Client Lead |
| Build Lead | PRD and architecture, build plan, nightly MVP, project rules, roadmap, slides 7 and 8 | Data Lead |

For a three-person team, use the alternate assignments in `docs/ROLES.md`; the uncertainty-buffer requirement is excused, but the full-night caveat and roadmap remain required.

## Standing rules and recurring work

- **AI boundary:** Tuesday's paper frame (ladder stages 0–2) and Saturday's defence/viva are AI-free. Log every other AI chat and explain any AI-written line you commit. Follow `docs/AI_WORKFLOW.md`.
- **Scoring:** Use `src/contract.py` unchanged. Train before 1 July 2016; choose settings on 1 July–31 December 2016; prove once on 1 January–31 August 2017. Report euros, rooms and walks per 1,000 together.
- **Data timing:** Only fixed-at-booking columns feed the MVP. Late-column and random-split runs may be diagnostic comparisons only; never use them for the chosen rule.
- **Client ceiling:** At most 10 walks per 1,000 arrivals. Any method that exceeds it is rejected regardless of savings.
- **Required commands:** `python src/backtest.py` and `python src/nightly.py --from 2017-08-18 --nights 14` must work by Friday. Commit the frozen `models/` output after the final backtest.
- **Screenshots:** Every number on a slide needs a code-and-output screenshot named `slideNN_what.png` in `evidence/`.
- **Daily card:** Each build morning, answer who pays/decides, the decision, its unit, three ranked metrics and whether it needs a rule, lookup or model.
- **Stuck process:** After 25 minutes without progress, record tried/expected/observed in three lines; use and log the clue process in `docs/LADDER.md`.
- **Checkpoint practice:** At each numbered step, first record the starting commit. When the step's completion check passes, update this tracker, commit that step's files together with the tracker update, record the new commit hash here, and push it to the corresponding GitHub branch. Keep one milestone per commit. If interrupted, make a clearly labelled checkpoint commit and leave the step `In progress`; do not claim it passed.

## Step and commit log

| Step | Status | Commit hash | GitHub push | Notes / evidence |
|---:|---|---|---|---|
| 0 | Complete | `c4e7b11` | Included in tracker update push | Source review complete; tracker creation checkpoint committed. |
| 1 | In progress | `b03e701` | Included in tracker update push | AI-assisted rough charter draft; the course-required no-AI paper frame and data checks remain to be completed. |
| 2 | Not started | | Pending | |
| 3 | Not started | | Pending | |
| 4 | Not started | | Pending | |
| 5 | Not started | | Pending | |
| 6 | Not started | | Pending | |
| 7 | Not started | | Pending | Benchmark belongs on `ai-benchmark`; its chat index row belongs on `main`. |
| 8 | Not started | | Pending | |
| 9 | Not started | | Pending | |
| 10 | Not started | | Pending | |

