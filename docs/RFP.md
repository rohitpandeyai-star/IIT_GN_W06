# Request for Proposal: Cancellation-Aware Hotel Overbooking

> **AI-assisted working draft.** Prepared at the user's request. The project course requires its paper-frame V0 to be written without AI; this RFP draft does not satisfy that requirement. It is a working requirements document, with unspecified client thresholds and commercial facts left open for confirmation.

**Issued by:** Revenue team for a two-hotel group in Portugal (client name withheld)
**For:** Revenue science / software vendors
**Decision owner:** Revenue manager (confirm final approver)

## 1. Background

We operate a city hotel in Lisbon and a resort in the Algarve. Our revenue manager currently applies a flat overbooking rule based on each hotel's average cancellation rate and a small safety margin. We want a reproducible recommendation for how many rooms to oversell on each arrival night, evaluated by cost and guest walks.

The brief says roughly one booking in four is cancelled. The historical data checks currently show 36.2% cancellation across train and choose bookings combined, with different rates by hotel; we need to reconcile the period and definition behind the brief's rough figure. We have not verified the vendor's reported 95% accuracy.

## 2. What the solution must do

1. Produce a whole-number oversell count `k` for each hotel on each arrival night.
2. Produce the required morning recommendation table for the next 14 arrival nights at each hotel.
3. Use the supplied `src/contract.py` scoring definitions without changing them.
4. Compare the proposed rule against the current flat rule on the same held-out proof period.
5. Show expected cancellations, buffer, and oversell count in the recommendation output; include enough explanation for the revenue manager to review the result.

## 3. Acceptance measures and periods

| Measure | Required threshold / comparison | Period and unit |
|---|---|---|
| Walk guardrail | No more than 10 walked guests per 1,000 arrivals | Check on choose before selection; report on proof across scored arrivals. The contract's denominator is bookings that did not cancel. |
| Total cost | Lower than the current flat rule, if possible, while meeting the walk guardrail; no minimum savings amount is specified in the brief | Sum of empty-room and walk costs in EUR over proof, January 1–August 31, 2017; compare on the same hotel-nights |
| Empty rooms | Report the count alongside cost | Proof period, total and by hotel where possible |
| Walked guests | Report count and walks per 1,000 arrivals alongside cost | Proof period, total and by hotel where possible |
| Candidate selection | Select settings/buffer using the choose period; do not tune on proof | Choose: July 1–December 31, 2016 |

The train period is arrival dates before July 1, 2016 and is used to fit methods and estimate hotel cancellation rates for the flat-rule baseline. Run proof once after choices are frozen. The brief gives no numeric minimum-savings threshold beyond requiring a better euro result subject to the walk ceiling; confirm whether the client wants a minimum amount or percentage. The supplied contract applies the walk ceiling to the scored period as a whole; confirm whether the client also requires a per-hotel ceiling.

## 4. Operating and technical limits

- Keep `src/contract.py` unchanged and follow its hotel-night unit, cost formulas, and arrival-date periods.
- Use only columns known at the intended decision time for the chosen recommendation. Record the timing and exclusions of each input; do not use late-arriving fields or a random train/test split for the selected rule.
- Treat each night as a separate recommendation. The required exercise scores the night's final book; a real morning-of run using only reservations present at that time is a known follow-up limitation to discuss.
- The project MVP is a reproducible table, not automated changes to reservations or a hotel-system integration.
- Provide a manual review/override approach only after confirming the revenue manager's operational needs.

## 5. Data provided

The supplied booking file contains 119,390 bookings and 32 columns, with arrival dates from July 2015 through August 2017. The initial notebook checks confirm two hotel categories, City Hotel and Resort Hotel. The data is downloaded using `python src/data.py`; the downloaded CSV should not be committed to Git. The early profiling checks report train 49,157 rows, choose 29,546, and proof 40,687. Proof outcomes were not calculated in the early profile and must remain held back until the final proof run.

## 6. Proposal evaluation

We will first reject any proposal that exceeds the walk guardrail. Among acceptable proposals, compare total proof-period euros against the flat-rule baseline, with empty-room and walk counts shown alongside. A model accuracy score alone is not sufficient evidence of business value. Record the candidate method, chosen buffer, input timing, and proof procedure so the result can be reproduced.

## 7. Timeline and deliverables

The course project sequence is: define the frame and profile the data; compare methods and select settings on the choose period; build the 14-night MVP; evaluate once on proof; prepare evidence and present the result. The course specifies the dates/train-choose-proof periods but the client brief does not provide an external delivery calendar. Confirm any client-side pilot or deployment date before committing to one.

Expected project artifacts include the reproducible backtest, selected/frozen method and buffer, 14-night output, proof comparison against the flat rule, evidence for reported figures, and a record of limitations. No deliverable should claim savings or walk performance before the proof evaluation is complete.

## 8. Questions for the client

1. What exact safety margin does the flat rule use, and does it vary by hotel or season?
2. Is the 10-per-1,000 walk ceiling group-wide only, or must each hotel also satisfy it?
3. What minimum euro or percentage saving would make a change worthwhile, if any, provided the walk guardrail is met?
4. Who approves the recommendations, who bears the walk cost, and is an override required?
5. Should the live morning table use the full final book as in the course scoring exercise, or only bookings known at run time?
6. What was the vendor's 95% accuracy measured on, over what dates, and with what definition of accuracy?
7. What period and cancellation definition support the “about one in four” observation?

## 9. Wish list

The brief's wish-list item is: “Our marketing team would love to find our hidden guest types.” No measurable acceptance criterion is provided. Treat segmentation as exploratory/out of scope for this MVP until the client states what action it would change and how its value will be measured.
