# Paper Frame V0 — AI-Assisted Study Draft

> **Use and status:** This draft was generated with AI at the user's request. The course materials require the paper-frame V0 to be written without AI, so this file is a study and review aid; it does not meet that requirement. The student must write a separate paper version independently if the course requires it.

## Client and problem

The brief describes a hotel group in Portugal with a city hotel in Lisbon and a resort in the Algarve. Its revenue manager currently uses a flat overbooking rule based on each hotel's cancellation rate and a small safety margin. The client wants recommendations that reduce the cost of rooms left empty after cancellations without walking too many arriving guests. The brief does not specify who pays whom under the commercial arrangement, so we should confirm rather than assume it.

## Decision and unit

For each hotel and arrival night, choose a whole-number oversell count, **k**: how many rooms beyond capacity the hotel can keep selling. The evaluation contract sets the decision unit as **one hotel on one arrival night**. A booking is an input row, not the unit of action. The requested output is a table for the next 14 arrival nights at each hotel.

## Costs and success measures

For a hotel-night with **A** cancellations, the contract defines empty rooms as `max(A − k, 0)` and walked guests as `max(k − A, 0)`. The value of an empty room is the average booked stay value for that night: average `adr` multiplied by the booking's total weekend and weekday nights. A walked guest costs **EUR 300** under the supplied scoring assumption. Night cost is:

`empty rooms × average booked stay value + walked guests × EUR 300`

The north star is lower total cost in euros over the January–August 2017 proof period compared with the client's flat rule evaluated on the same period. Report euros together with empty rooms and walks. The guardrail is **at most 10 walked guests per 1,000 arrivals**. Reject a rule that breaks the ceiling, even if it has lower euro cost. Check the ceiling while choosing settings and report it on proof.

## Evidence and evaluation periods

The supplied contract splits bookings by arrival date: train on dates before July 1, 2016; choose on July 1 through December 31, 2016; and run proof once on January 1 through August 31, 2017. Keep proof results out of tuning, and compare every candidate against the flat rule rather than against no overbooking.

The notebook checks confirm **119,390 rows**, **32 columns**, **two hotel names**, and arrival dates from **2015-07-01 to 2017-08-31**. Train has **49,157** bookings with **35.8%** cancelled; choose has **29,546** bookings with **36.9%** cancelled; proof has **40,687** bookings. Train plus choose cancellation rate is **36.2%** overall, **41.3%** for City Hotel, and **26.3%** for Resort Hotel. The proof count and dates were checked, but proof cancellation outcomes were not calculated in the early profile. These are descriptive checks, not model performance results.

## Scope and open questions

The current scope is to profile and audit the data, compare candidate rules using the fixed scoring contract, choose a buffer on the choose period, and produce a reproducible 14-night table with a one-time proof evaluation. A dashboard, automated reservation changes, and discovery of hidden guest types are not in the current MVP without a specific measurable need.

Before accepting a rule, clarify: (1) the exact safety margin in the current flat rule and whether it varies by hotel; (2) whether the walk ceiling applies to the group or each hotel separately; (3) who approves a recommendation and whether a manual override is needed; and (4) what the vendor's reported 95% accuracy measured. The brief's “about one booking in four” cancellation statement differs from the checked train-plus-choose rate, so confirm its time period and definition. Do not treat the vendor figure as verified.

## Current limitation

No method comparison, selected buffer, cost savings, proof-period walk rate, or live 14-night MVP result is established yet. The charter remains an AI-assisted working draft, and the course-required paper frame written without AI remains outstanding. See `docs/EXECUTION_TRACKER.md` for remaining work.
