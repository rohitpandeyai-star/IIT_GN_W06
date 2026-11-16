# What is the project, in one page?

**Owner:** Client Lead. **Closes:** ladder stages 0 and 1. **Length:** one page.

> **Working V0 draft:** This is an AI-assisted, deliberately rough discussion draft, written at the user's direction. It contains unverified wording and one intentionally weak decision-unit guess for the team to challenge. The course materials require the paper-frame V0 to be written without AI; this draft does not satisfy that course requirement and should be replaced or reconciled with the team's paper version before submission.

### 1. Who is the client, and who pays whom?

**Our answer:** The client seems to be the two-hotel group in Portugal: one Lisbon city hotel and one Algarve resort. It probably pays RateGain for a revenue module if the tool saves enough money. Bookings arrive from business partners and individual guests, including direct and online travel agency bookings.

### 2. Who decides, how often, and what does one wrong call cost in each direction?

**Our answer:** The revenue manager decides how far to oversell each hotel each night, probably from the bookings already on the book and a safety margin. If too few rooms are sold and cancellations leave rooms empty, the loss is roughly the booked rate times the stay length; the exact value still needs checking. If too many guests arrive, the brief says each walked guest costs EUR 300.

### 3. What is decided, from what is known when, about which outcome?

**Our answer:** We want to choose how many extra rooms to sell for each hotel over the next fourteen nights, using booking information available around the time the list is prepared. The outcome is whether each booking cancels or does not arrive. We still need to be clearer about exactly when the booking snapshot is taken.

### 4. What is the unit of decision, and why that unit?

**Our answer:** **Working guess, probably wrong:** the unit may be one booking, because cancellation is recorded for each booking row. We would then add the bookings up for each hotel and night; the actual recommendation might instead need to be one number per hotel-night.

### 5. What are the north star and the guardrail?

**Our answer:**

- **North star:** lower the total modeled cost in euros from empty rooms and walked guests.
  - Numerator: total cost in euros from those two costs.
  - Denominator: perhaps hotel-arrival nights, so the hotels can be compared; this is not settled.
  - Window: the January–August 2017 proof period, with monthly views if useful.
  - Exclusions: none decided yet; we should ask whether closed or capacity-constrained nights are included.
- **Guardrail:** no more than 10 walked guests per 1,000 arrivals.
  - Numerator: walked guests.
  - Denominator: scored bookings that did not cancel (actual arrivals), multiplied by 1,000.
  - Window: the full proof period; also check the choose period before freezing a rule.
  - Exclusions: none specified in the brief.

Metric tree (rough):

```text
Lower total cost (EUR)
├── Empty-room cost = empty rooms × average booked-stay value
└── Walk cost = walked guests × EUR 300
    Guardrail beside the tree: at most 10 walks per 1,000 arrivals
```

### 6. Which numbers in the brief did we check, and what did the data say?

Every result below is a draft status, not a completed data check. We have not yet run the data profile or computed these figures from the CSV.

| Number in the brief | What we checked | What the data said | What we do about it |
|---|---|---|---|
| About one booking in four is cancelled | Cancellation share overall and by hotel and period | Not checked yet | Treat as a rough claim until measured; report differences by hotel |
| The flat rule uses the hotel's average cancellation rate and "a few rooms" for safety | Reproduce the current rule and ask for the actual safety margin | Rate and margin not checked; the margin is not specified | Ask the revenue manager what margin is used at each hotel |
| One guest in a hundred / 10 walks per 1,000 arrivals | Compare both statements and confirm the denominator | They both look like a 1% ceiling; not tested on data | Use the explicit contract limit of 10 per 1,000 |
| EUR 300 per walked guest | Read the client's cost assumption | The brief states EUR 300; historical data cannot verify this cost | Use as the fixed scoring assumption unless the client corrects it |
| Train before 1 July 2016 | Check arrival dates and `src/contract.py` split | The period is specified; not independently checked against the downloaded file | Use the contract split |
| Choose July–December 2016 | Check arrival dates and `src/contract.py` split | The period is specified; not independently checked against the downloaded file | Tune settings and buffers here only |
| Prove January–August 2017 | Check arrival dates and `src/contract.py` split | The period is specified; not independently checked against the downloaded file | Hold it back and run proof once |
| Next fourteen nights | Check the requested nightly output | Fourteen nights are specified; no run exists yet | Make the MVP write one row per hotel and night |
| 119,390 bookings and 32 columns | Compare the downloaded file's row and column counts | Not checked yet | Confirm in the profiling notebook |
| Vendor demo claimed 95% accuracy | Look for the demo's definition and test-period details | No evidence supplied to check it | Do not use the accuracy claim as an acceptance target; report business costs instead |

### 7. What is out of scope?

**Our answer:** For now, the output is a recommendation table, not a full booking or hotel-management system. Hidden guest types, a dashboard, and automatic changes to reservations are probably out of scope, although we should confirm whether the revenue manager needs an override process.

### 8. Who owns what on this team?

| Role | Name | Owns |
|---|---|---|
| Client Lead | Rohit Pandey | Charter, RFP, client framing and metrics |
| Data Lead | Rohit Pandey | Data profile, column audit and feature inputs |
| Model Lead | Rohit Pandey | Backtest, method comparison and buffer |
| Build Lead | Rohit Pandey | PRD, build plan, architecture and nightly MVP |

### 9. What is the one question we are sending the client?

**Our answer:** What exact safety margin does the revenue manager use in the current flat rule, and does it differ between the Lisbon hotel and the Algarve resort?