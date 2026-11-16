# Build 2, Week 6 — Source Document Context

## Purpose and scope

This note consolidates context from the three supplied student Word documents and the Build 2 announcement deck. It is a reading aid for the project repository, not a replacement for the source documents and not a completed client deliverable.

The course documents contain project requirements for the student team. This note records those requirements so the team can use them; it does not mean that the corresponding project steps have been performed. The user request for this file was to read the supplied Word documents and presentation and gather their context here. No charter, model, code, slides, AI log, or team decision has been filled by this summary.

**Important template distinction:** The worked examples in the templates describe a fictional home-collection diagnostics business with rupee costs. They are examples of answer format only. Their numbers, roles, operating assumptions, and answers are not facts about the hotel project.

## 1. The client problem

The fictional client is a two-hotel group in Portugal: a city hotel in Lisbon and a resort in the Algarve. The revenue manager currently uses a flat overbooking rule based on the hotel's average cancellation rate, the night's bookings, and a safety margin. The client wants a better nightly oversell count, justified in euros.

The decision is **one whole-number oversell count, k, per hotel per arrival night**. The desired operating output is a table for the next fourteen nights at both hotels. It should show the hotel, date, bookings on the book, expected cancellations, buffer, and oversell count. A revenue manager should be able to read it each morning.

### Client scoring contract

- `is_canceled = 1` is the cancellation outcome; it includes no-shows.
- If A bookings cancel and the rule sets oversell count k, empty rooms are `max(A − k, 0)` and walked guests are `max(k − A, 0)`.
- The value of an empty room is the night's mean booked stay value: `adr × nights`, with `nights = stays_in_weekend_nights + stays_in_week_nights`.
- Each walked guest costs EUR 300.
- Night cost is empty rooms times stay value plus walked guests times EUR 300.
- The walk ceiling is at most 10 walks per 1,000 arrivals. A rule above the ceiling is rejected even if its euro cost is lower.
- Every result must report euros, rooms, and walks per 1,000 together.
- Use the scoring implementation in `src/contract.py` unchanged.

### Time periods and baselines

| Period | Arrival dates | Use |
|---|---|---|
| Train | Before 1 July 2016 | Fit methods and estimate the flat-rule cancellation rate |
| Choose | 1 July–31 December 2016 | Choose settings and buffers; check the walk ceiling |
| Proof | 1 January–31 August 2017 | Run once at the end and report outcomes, including walks |

The client's flat rule is a required baseline: each hotel's train-period cancellation rate times the night's bookings, less a safety margin selected on the choose period under the ceiling. Savings must be measured against this rule, never against selling nothing extra. Settings and buffers are frozen before proof. If a team changes anything after seeing proof results, it must disclose the change and report both runs.

The proof table scores each night's final book. The fourteen-day live example therefore treats the final book as already available. The brief notes that only about half of a night's eventual bookings are usually on the books fourteen days before arrival; a live system using only the bookings known on the run date belongs in the roadmap as future work.

### Data and business observations

The data is the open Hotel Booking Demand dataset: 119,390 booking rows, 32 columns, arrivals from July 2015 through August 2017. The cited source is Antonio, de Almeida and Nunes (2019), *Hotel booking demand datasets*, *Data in Brief* 22, 41–49, CC BY 4.0. The course materials say `src/data.py` downloads the TidyTuesday copy into `data/`; do not commit the downloaded CSV.

The client offers three unverified observations for the team to investigate with evidence:

1. Finance believes prepaid, non-refundable bookings mostly do not become stays, despite the assumption that prepayment guarantees a stay.
2. The front desk stopped using a vendor's daily cancellation-risk list within a month.
3. A vendor demo claimed 95% accuracy, but that performance did not hold in the lobby.

The wish-list item is to find hidden guest types. The PRD must answer it with a number, name the method it would require, and explain whether it changes a number the client acts on.

Business context: tour operators, travel agents, groups, corporates, and airlines are B2B partners; individual guests book directly or through online travel agencies. The hotel group pays RateGain for software, so the case must show value in the hotel's euros. `market_segment` identifies the customer segment; `distribution_channel` identifies how the booking arrived. An OTA is a business partner to the hotel and a shop to the guest.

## 2. The team playbook and course workflow

The team playbook frames the week as one client question, one decision, four roles, and four core documents: charter, RFP, PRD, and build plan. Work proceeds through eight ladder stages. If later evidence changes an earlier answer, revise the earlier document and record the change in `docs/DECISIONS.md`.

| Stage | Question | Completion evidence |
|---:|---|---|
| 0 | What is the business as a black box? | Charter has client/decision/cost context, every brief number is checked or queried, and one client question is written |
| 1 | What exactly is decided, from what information and at what unit? | Charter frame sentence; all columns in three timing bins; special booking groups named with evidence |
| 2 | How good must the answer be, and within what limits? | One- or two-page RFP with business-unit thresholds and all three periods |
| 3 | Which decision approaches are possible, and which is chosen? | PRD has two options, a choice, a condition that would change the choice, and a quantified wish-list answer |
| 4 | Does the idea survive a first test? | One command prints all methods' proof results with AUC, nightly room error, euros, and the ceiling check |
| 5 | What does the system look like inside? | PRD has black-box and white-box architecture plus production additions |
| 6 | Could the revenue manager use it tomorrow? | Fourteen-night MVP command writes its table from first-bin inputs; challenger signs in README |
| 7 | Can every member defend every number? | All members can explain the evidence; slide 1 states the answer |

### Week timing

- **Tuesday:** First hour: brief, roles, ladder stages 0–2, evaluation contract. Write the paper frame with no AI. Profile the data and begin the column audit. After the paper frame and data pass, run Grill 1 on the charter/RFP skeleton and complete project rules.
- **Wednesday:** Fill PRD options before the method table exists; prepare the POC plan and method table.
- **Thursday:** Build the MVP, conduct Grill 2 after the POC, and run the AI benchmark in its separate branch within a 90-minute box.
- **Friday:** Finish the team-vs-AI comparison, roadmap, slide evidence, and each member's recording. The last commit before Friday's deadline is graded.
- **Saturday:** Defend the result. The presentation is ten slides in ten minutes, followed by six minutes of questions. Slide 7 runs the frozen MVP live; no retraining occurs on stage.

The two commands the project expects by Friday are:

```text
python src/backtest.py
python src/nightly.py --from 2017-08-18 --nights 14
```

The backtest prints every method on proof and saves the selected method/buffer under `models/`; the saved model is committed so the nightly run works from a fresh checkout. `pytest -q` is the supplied contract check; run it as part of project work when appropriate.

### Roles, artifact ownership, and checks

| Role | Main ownership | Challenged by | Primary question |
|---|---|---|---|
| Client Lead | Charter and metric tree, checked-number table, RFP, travel-partner view, full-night caveat, slides 1–3 and 10 | Model Lead | What is decided, for whom, and what does each wrong call cost? |
| Data Lead | Profiling notebook, data decisions, column audit, `src/features.py`, AI benchmark, comparison, `ai_logs/INDEX.md`, slides 4 and 9 | Build Lead | What did the hotel know on the booking date? |
| Model Lead | `src/backtest.py`, method table, choose-period buffer, uncertainty buffer, slides 5 and 6 | Client Lead | How many will cancel, and how certain are we? |
| Build Lead | PRD and architecture, build plan, `src/nightly.py`, project rules, roadmap, slides 7 and 8 | Data Lead | What can the revenue manager use tomorrow? |

The owner decides on their artifact. A challenger can submit a three-line objection in `docs/DECISIONS.md` (objection, reason, proposal); the owner responds within 15 minutes. If still open, frame/money questions go to the Client Lead and scope/time questions to the Build Lead; a TA breaks a true tie. A challenger signs the artifact in the README with the commit hash checked. An artifact is not complete until signed. Each member must be able to explain the decision, unit, costs/ceiling, column bins, method rankings, MVP inputs/outputs, and AI comparison.

For a team of three, use the alternate owners in `docs/ROLES.md`: there is no Build Lead, uncertainty-buffer work is excused, but the full-night caveat and roadmap remain; the team makes three recordings.

### Data timing and evidence rules

Every column is assigned exactly one bin in `docs/COLUMNS.md`:

1. Fixed at booking: known on booking day and does not change.
2. Amendable: known at booking but may change, or only partly known then.
3. After the fact: recorded at check-in, during the stay, or after the outcome.

Only first-bin columns may feed the MVP. Second-bin features need caveats; third-bin features never feed a method. The template asks for three diagnostic AUC runs: first-bin/time split; all columns/time split; first-bin/random split. These diagnose leakage and split effects; neither late features nor a random split may enter the chosen rule.

The slide deck needs a code-and-output screenshot for every number, saved as `evidence/slideNN_what.png`. A clue that changes a decision is named on the slide where that decision appears. The client values discipline of comparison, not which method wins.

### AI rules from the course materials

The paper frame (ladder stages 0–2) and Saturday defence/viva are AI-free. Other AI use is allowed by the course instructions, but every chat must be logged and every committed AI-written line must be explainable. The Build Lead is instructed to write at least five repo rules derived from logged decisions, append the named coding guidelines, and copy the rules file to the supported tool locations. The course asks the team to capture an AI assumption/pushback screenshot in `ai_logs/karpathy_effect.md`.

Two grills are required: Tuesday's charter/RFP grill (45 minutes, Client Lead owns the log) and Thursday's PRD/build-plan grill (45 minutes, Build Lead owns the log). Each log needs at least three rows showing a document change; write the team's answer before reading the AI recommendation.

The AI benchmark is a separate `ai-benchmark` branch rooted at the repository's first commit. Save a plan before approval, provide the specified execution prompt, alter AI logic only to fix environment errors, stop at 90 minutes, commit/push that branch, and return to `main`; never merge it. Keep the chat log and index row on `main`. **Path note:** the Team Playbook's execution prompt has a typo that renders the path as `aibenchmark/run.py`; the AI workflow document and repository use `ai_benchmark/run.py`. Verify with the team and use the actual repository folder name.

## 3. Required template content

The student templates are blank forms with examples, not filled hotel answers. The local `docs/` versions of these forms are intended to hold the team's final work.

- **Charter (`docs/CHARTER.md`, Client Lead):** client/payer, nightly decision maker and two error costs, frame/outcome/unit, north star and guardrail with numerator/denominator/window/exclusions, checked brief numbers, out-of-scope items, role names/ownership, one client question.
- **RFP (`docs/RFP.md`, Client Lead):** client background; up to five checkable solution requirements; acceptance thresholds and periods; limits/rules; provided data; evaluation; timeline; client questions; exact wish-list item.
- **PRD (`docs/PRD.md`, Build Lead):** user/timing; two approaches and costs/choice/flip condition; quantified wish-list answer; output-table columns; input bins; probability/buffer method and freeze point; proof-period error bill; black- and white-box diagrams plus production additions; limits, risks, and scope.
- **Build plan (`docs/BUILD_PLAN.md`, Build Lead):** POC/MVP/final stages with owners, planned/used hours, done condition and evidence; production additions with client value, owner and estimate; cuts and reasons.
- **Column audit (`docs/COLUMNS.md`, Data Lead):** all 32 named columns assigned to the three bins with reason and evidence, then the three diagnostic AUCs and explanation of which estimate the client should trust.
- **Decisions (`docs/DECISIONS.md`):** append-only data cleaning/filter decisions with row counts, plus team decisions/objections and resolution.
- **Grill logs:** question, AI recommendation, team answer, accepted/changed/rejected, document change, and reflection; link each to the full chat log.
- **Comparison (`docs/COMPARISON.md`, Data Lead; Build Lead challenger):** same rows of evidence for team and AI builds; cite file/line or log excerpt; name up to three gaps and mistakes, or say none with evidence; state what to keep and never ship.
- **Roadmap (`docs/ROADMAP.md`):** Weeks 7–9, one line each with measurable client reason, owner and hours; include production additions.
- **README:** commands, owners/challenger signatures with checked commit hashes, and each recording's LMS link.

The Templates Word file includes the charter, RFP, PRD, build plan, column audit, decisions log, both grill logs, comparison, and roadmap forms. The Client Brief Word file adds the channel/B2B context. The Team Playbook compiles the workflow, scoring contract, domain vocabulary, AI workflow, presentation, recording, and rubric that also appear as separate Markdown files in `docs/`.

## 4. Announcement deck, slide-by-slide context

The 12-slide announcement presents the work from the student point of view:

1. The team has five days to answer how many rooms each hotel can oversell tonight, in euros.
2. For a 20-room example with k=4, six cancellations leave two rooms empty; four cancellations fill the hotel; two cancellations create two walked guests. It illustrates why k trades empty rooms against walks.
3. Scoring uses the average booked-stay value for an empty room, EUR 300 per walked guest, and a ceiling of 10 walks per 1,000. Train to June 2016, choose H2 2016, prove on 2017.
4. The context is RateGain, a Lisbon city hotel and Algarve resort, with B2B tour operators/groups/corporates and B2C direct/OTA guests. The same overselling decision appears in other capacity businesses.
5. Timeline: Tuesday paper frame/charter/RFP/grill; Wednesday POC and PRD/pooling lab; Thursday MVP, AI benchmark and second grill; Friday evidence/comparison/recording; Saturday defence and live run.
6. Four owners—Client, Model, Data, Build Lead—with an owner and challenger check for each artifact.
7. AI is used on its own branch after the no-AI frame; compare plans/builds and explain gaps/mistakes. Chats are logged and each AI line must be explainable.
8. Prioritize a one-sentence decision, checking brief numbers, binning columns, comparing four methods, a one-command MVP, and screenshots. Skip repeating the brief or arguing over the winner; drop dashboards, apps, deep learning and AUC tuning.
9. Avoid false progress: business euros under the ceiling rather than accuracy; time split rather than random split; booking-time inputs rather than columns written later; buffer chosen on 2016 rather than tuned on proof; savings versus the flat rule rather than selling nothing; checked values rather than unchecked brief numbers.
10. The 40 marks split into 24 team marks and 16 individual marks. Team criteria cover frame/metrics, honest evidence, client observations, MVP and evidence/AI story. Individual criteria cover the recording, question defence and contribution trail.
11. Saturday: ten slides in ten minutes plus six minutes of questions. Each member submits a 15–20 minute recording by Friday covering artifacts, their number in code, stuck-to-unstuck, research proof and what they would redo.
12. Daily 60-second card: who pays/decides, the decision, unit, three ranked metrics, and rule/table/model. When stuck after 25 minutes, record three lines and use staged clues.

## 5. Current project state observed while preparing this note

- `docs/EXECUTION_TRACKER.md` exists. Step 0 (source review/setup) is complete; execution steps 1–10 remain not started.
- `docs/CHARTER.md` contains a partial student draft; several required fields remain blank. The initial paper-frame requirement still belongs to the team.
- The repository inventory had `src/data.py` and the supplied `src/contract.py`, but not `src/features.py`, `src/backtest.py`, or `src/nightly.py`; no saved `models/` output or slide screenshots were present yet.
- Team names, measured data checks, chosen methods, proof results, challenger sign-offs, recordings, and AI benchmark results have not been supplied or produced in this context note. Do not infer or fabricate them.

## Source files read

- `C2_W06_D02_Client_Brief_STUDENT.docx`
- `C2_W06_D02_Team_Playbook_STUDENT.docx`
- `C2_W06_D02_Templates_STUDENT.docx`
- `C2_W06_D02_Build2_Announcement.pptx` (12 slides)
- Cross-checked against `BRIEF.md`, `README.md`, `AGENTS.md`, and the relevant files under `docs/`.
