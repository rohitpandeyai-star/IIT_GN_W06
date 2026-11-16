# Defence Quick Guide: What to Know and What to Say

**Purpose:** A short study aid for explaining the current project state. Use your own words in the course defence. This guide is AI-assisted; it is not a substitute for the course-required AI-free paper frame or for work that is still unfinished.

## The case in one minute

The client wants an oversell count, **k**, for each **hotel on each arrival night**. The goal is to reduce the cost of rooms left empty after cancellations while keeping walks at or below **10 per 1,000 arrivals**. Empty rooms are valued at the night's average booked stay (average rate × stay length); each walked guest costs **EUR 300**. The supplied scoring code in `src/contract.py` defines the evaluation and must stay unchanged.

The data is divided by arrival date: fit on dates before **2016-07-01**, choose settings on **2016-07-01 through 2016-12-31**, and run proof once on **2017-01-01 through 2017-08-31**. Our early Pandas checks cover 119,390 bookings, 32 columns, and two hotels. Train plus choose cancellation rate is **36.2%**, while the brief's “about one in four” is a client observation, not what these checked rows show. This is a data check, **not a model result**: no method has yet been compared, no buffer chosen, and no savings or walk rate measured.

## Numbers worth remembering

| Item | Current checked value | How to describe it |
|---|---:|---|
| Dataset | 119,390 rows; 32 columns | Stated in brief and confirmed in the notebook checks |
| Hotels | 2: City Hotel and Resort Hotel | Confirmed distinct values |
| Arrival dates | 2015-07-01 to 2017-08-31 | Observed range |
| Train | 49,157 bookings; 2015-07-01 to 2016-06-30; 35.8% cancelled | Checked in notebook |
| Choose | 29,546 bookings; 2016-07-01 to 2016-12-31; 36.9% cancelled | Checked in notebook |
| Proof | 40,687 bookings; 2017-01-01 to 2017-08-31 | Count/date checked; cancellation outcomes not calculated in this early check |
| Train + choose | 36.2% cancelled | Checked; still not a model's performance |
| City / Resort | 41.3% / 26.3% cancelled | Train + choose checks; rates differ by hotel |
| Walk ceiling | 10 per 1,000 arrivals | Client/course scoring constraint, not measured performance |
| Walk cost | EUR 300 per walked guest | Client/course scoring assumption |
| Flat-rule safety margin | “A few rooms” | Unspecified; ask the client, don't invent a number |
| Vendor demo | 95% accuracy | Unverified client anecdote; not our result |

## Decision tree to explain

```text
What does the client need?
└─ One oversell count k for every hotel × arrival night
   ├─ What is being traded off?
   │  ├─ Too few extra bookings → cancellations can leave rooms empty
   │  └─ Too many extra bookings → guests can be walked
   ├─ What decides whether a rule is acceptable?
   │  └─ Walks ≤ 10 per 1,000 arrivals; then compare euros and rooms too
   ├─ How do we choose fairly?
   │  ├─ Train: fit candidate methods
   │  ├─ Choose: select settings and safety buffer under walk ceiling
   │  └─ Proof: one final evaluation, after choices are frozen
   └─ What can I claim today?
      └─ Data profile and split counts only; no chosen rule or performance yet
```

## Likely questions and honest answer cues

**Why is the unit a hotel-night?**  
The evaluation contract says one hotel on one arrival night, and the rule outputs one whole-number oversell count for that night. A booking is a row in the data, but it is not the decision unit.

**What is the rule deciding?**  
`k` is how many rooms beyond capacity to keep selling for that hotel-night. The contract compares actual cancellations on that night's final book with `k`: `max(cancellations − k, 0)` empty rooms and `max(k − cancellations, 0)` walked guests.

**How is a night's cost calculated?**  
Empty rooms × average booked stay value, plus walked guests × EUR 300. The walk rate is walked guests divided by arrivals, times 1,000. All reported results must show euros, rooms, and walks per 1,000 together.

**What does 36.2% tell us?**  
It is the checked cancellation rate across train and choose bookings combined. It does not prove that a model is useful, and it is not a walk rate or a cost saving. City and resort rates differ, so a single blended number hides variation.

**Why split by time?**  
The task is to predict future arrival nights. Training on earlier dates, choosing on the next period, and holding the final period for one proof run mirrors that use and keeps proof results out of tuning.

**Have we proved the approach beats the current rule?**  
No. The backtest, candidate comparison, choose-period buffer selection, and one-time proof run are not complete. We should not claim savings, chosen method, or observed walk performance.

**What about the client's current flat rule?**  
It uses each hotel's train-period cancellation rate times that night's bookings, minus a safety margin. The brief only says “a few rooms”; the margin is unknown and must be clarified or selected on choose under the same walk ceiling.

**Can the vendor's 95% accuracy be compared?**  
Not from the information we have. It is an unverified anecdote, and accuracy alone does not answer the client's euro cost and walk-ceiling question.

**What does the morning MVP show?**  
The required table is one row per hotel and each of the next 14 arrival nights, with bookings on the book, expected cancellations, buffer, and oversell count. The MVP has not been built or run yet.

**What is the biggest open issue?**  
The charter is an intentionally rough AI-assisted draft. The course requires the paper frame to be written without AI; that requirement remains outstanding. We also need to reconcile the charter with checked data, audit which columns are known at booking time, and complete model, MVP, and proof work.

## Keep these claims out of your answer for now

- “Our model saves EUR X” or “our walk rate is X”: no completed backtest/proof result exists.
- “We selected method Y” or “the 95% vendor result is verified”: neither is supported.
- “The flat rule uses N rooms of safety”: the brief leaves this unspecified.
- “We have a working 14-night MVP,” a finalized feature audit, or signed challenger checks: still pending.
- “The charter is final/course compliant”: it is a rough AI-assisted draft, and the no-AI paper frame remains to be done.

## Five-minute practice

Try answering these aloud without reading the answer cues: **(1)** What is the decision unit? **(2)** What are the two cost terms and the walk guardrail? **(3)** What is train vs choose vs proof for? **(4)** Which values are checked and which are client assumptions? **(5)** What can we not claim yet, and what is the next evidence needed?

If unsure, say what is known, what is still unverified, and where the evidence should come from. That is stronger than guessing.
