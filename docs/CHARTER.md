# Project Charter: Cancellation-Aware Overbooking

> **Status: AI-assisted working draft.** Prepared at the user's request. The course requires the paper-frame V0 to be written without AI, so this document is not that deliverable. Use it as a reference when writing the paper version in your own words. Any unknown client facts remain explicit questions.

**Client Lead:** Rohit Pandey (team member assigned to all four roles)
**Decision owner at client:** Revenue manager (as described in the brief)
**Project outcome:** A defensible rule and a 14-night recommendation table for two hotels.

## 1. Client and value exchange

The brief describes a Portugal hotel group with a city hotel in Lisbon and a resort in the Algarve. The client wants a better way to decide how many rooms to oversell on each arrival night. RateGain is the named supplier in the course setting, but the brief does not state the commercial payment arrangement; confirm that rather than assuming a contract or pricing model.

The client says its current rule is a hotel's average cancellation rate multiplied by that night's bookings, less a small safety margin. The margin is not quantified. The decision user is the revenue manager; confirm who approves a rule for use and who bears the cost of a walked guest.

## 2. Decision, timing, and outcomes

**Decision:** choose a whole-number oversell count, `k`, for each hotel on each arrival night. The evaluation contract defines this as the unit. A booking row is an input observation, not the unit at which the final action is scored.

**When:** the requested product is a morning table for each of the next 14 arrival nights. The course scoring contract evaluates each night's final book, meaning all bookings eventually made for that night. A real morning-of-arrival operating rule would need a dated booking snapshot; that is a separate extension and should be named as a limitation if the MVP uses the full-book exercise.

**Outcome:** cancellations/no-shows on each hotel's arrival-night book, aggregated to the hotel-night for scoring. The data target is `is_canceled`; confirm how the production client distinguishes cancellations from no-shows if those require different actions.

## 3. Costs, north star, and guardrail

For one hotel-night, let `A` be the number of cancellations and `k` the oversell count:

- **Empty rooms:** `max(A - k, 0)`.
- **Walked guests:** `max(k - A, 0)`.
- **Stay value:** average of `adr × (weekend nights + week nights)` over bookings on that night's book.
- **Night cost:** `empty rooms × stay value + walked guests × EUR 300`.

These are the supplied contract definitions. Keep `src/contract.py` unchanged.

**North star:** minimize total cost in euros over the proof period, January 1 through August 31, 2017, compared with the client's flat rule evaluated on the same period. Report euros alongside empty rooms and walks; do not present a euro saving without the operational counts. Also show hotel-level results where possible so a group total does not conceal a poor outcome at one property.

**Guardrail:** no more than 10 walked guests per 1,000 arrivals over the scored period. The contract defines arrivals as scored bookings that did not cancel. Check this on the choose period before freezing settings, then report it on proof. A rule that breaches the ceiling is unacceptable even if its euro cost is lower.

The brief does not provide separate per-hotel cost or walk thresholds, so this charter does not invent any. Ask the client whether the group-wide ceiling is sufficient or whether each hotel needs its own ceiling.

## 4. Evaluation plan

| Period | Arrival dates | Use |
|---|---|---|
| Train | Before 2016-07-01 | Fit candidate methods and estimate the flat-rule cancellation rates |
| Choose | 2016-07-01 through 2016-12-31 | Compare candidates and choose settings/buffer while enforcing the walk ceiling |
| Proof | 2017-01-01 through 2017-08-31 | Run the frozen choice once and report cost, empty rooms, and walks per 1,000 |

Use arrival-date splits from `src/contract.py`. Do not tune after examining proof outcomes. If a change is made after seeing proof, disclose it and report both runs as required by the contract. Compare every candidate against the flat rule, not against doing no overbooking.

## 5. Numbers checked against the brief and data

| Brief item | Evidence/status | Current interpretation and action |
|---|---|---|
| About one booking in four is cancelled | Notebook check: train + choose is 36.2%; City Hotel 41.3%, Resort Hotel 26.3% | The brief's figure is a rough client observation and differs from this historical sample. Reconcile the period/definition with the client; do not overwrite either figure. |
| Two hotels in Portugal | Data has 2 distinct hotel names: City Hotel and Resort Hotel | Supports two hotel categories; the dataset names are anonymized and do not establish Lisbon/Algarve identity by themselves. |
| 119,390 bookings, 32 columns | Confirmed in the notebook profile | Raw file dimensions match the brief. |
| Arrival coverage | Checked: 2015-07-01 to 2017-08-31 | Matches the requested train/choose/proof coverage. |
| Train | 49,157 bookings, 2015-07-01 to 2016-06-30; 35.8% cancelled | Checked. Use only for fitting and baseline rate estimation. |
| Choose | 29,546 bookings, 2016-07-01 to 2016-12-31; 36.9% cancelled | Checked. Use for model/buffer selection under the guardrail. |
| Proof | 40,687 bookings, 2017-01-01 to 2017-08-31 | Count and date range checked. Cancellation outcomes were not calculated in the early profile; reserve proof evaluation until the method is frozen. |
| 10 walks per 1,000 arrivals | Contract ceiling; not a measured model result | Enforce on choose and report on proof. |
| EUR 300 per walk | Stated scoring assumption | Use in the contract; historical booking data cannot verify this client cost. |
| “A few rooms” safety margin | Not specified | Ask for the current margin and whether it varies by hotel. Select any benchmark margin on choose under the same ceiling. |
| Vendor's 95% accuracy | Client anecdote; no demo evidence or definition supplied | Do not treat as verified or as an acceptance target. Ask what data, horizon, and metric were used if comparison is needed. |
| Next 14 nights | Required output specification | No completed MVP run yet. Produce one row per hotel-arrival night with the fields defined by the project contract/PRD. |

**Important:** These notebook checks are descriptive data facts, not evidence that a predictive method beats the flat rule. No chosen method, buffer, savings, proof-period walk rate, or live MVP result is established yet.

## 6. Scope and exclusions

**In scope:** profile the supplied booking data; audit when each column becomes available; compare the required rule/model candidates with the fixed contract; select a buffer on choose; produce a reproducible 14-night table; report proof results against the flat rule.

**Out of scope for the current MVP:** automated reservation changes, a hotel-management-system integration, and discovery of hidden guest types unless a later quantified requirement is approved. The marketing wish for guest types needs a specific decision or measurable value before it becomes build scope. Confirm the revenue manager's manual override and escalation needs before deployment.

## 7. Roles and review

Rohit Pandey is assigned to Client Lead, Data Lead, Model Lead, and Build Lead, as requested. The charter's role assignment does not itself complete each role's checks. Course materials expect cross-role challenge/sign-off; record how that is handled with a single assigned member and obtain any required challenger review/signatures rather than implying they already exist.

## 8. Open questions for the client

1. What exact safety margin does the current flat rule use, and does it differ by hotel or season?
2. Is the walk ceiling evaluated only across the group, or must each hotel also stay at 10 or fewer walks per 1,000 arrivals?
3. Who approves the recommendation and bears the walk cost? Does the revenue manager need a manual override or escalation step?
4. Is the morning table a course full-final-book exercise, or must a production version use only reservations present at the time it runs?
5. What did the vendor's 95% accuracy measure, on which dates, and against what baseline?
6. Are cancellations and no-shows treated identically for operational decisions, as they are in the supplied target/scoring setup?

**Priority client question to send first:** What exact safety margin does the revenue manager use in the current flat rule, and does it differ between the Lisbon hotel and the Algarve resort?

## 9. Current completion status

This is a completed **AI-assisted reference draft**, not a completed course paper frame. The data profile is partly checked; the column timing audit, reconciliation of the no-AI paper frame, finalized client requirements, candidate comparison, choose-period buffer, proof run, MVP, and required sign-offs remain to be completed. See `docs/EXECUTION_TRACKER.md` for the ordered work and checkpoint record.


## Grill 1 update — confirmation gates (2026-11-17)

The compressed AI-assisted grill did not establish new client facts. Before treating the flat rule as a reproducible baseline, obtain its actual safety margin and any hotel or seasonal variation; do not substitute a guessed value. The contract's walk ceiling is group-wide: show hotel-level diagnostics, and treat any per-hotel ceiling as unconfirmed until the client supplies it. The course exercise uses each night's final book; a live morning recommendation requires timestamped reservation snapshots and must be described as a separate operating design. Keep the client questions about final approval, walk-cost ownership, override, and no-show handling open. These are confirmation gates, not assumptions resolved by this document.
