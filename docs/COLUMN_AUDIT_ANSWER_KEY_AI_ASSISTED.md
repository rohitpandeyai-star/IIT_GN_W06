# Column Audit Answer Key — AI-Assisted Suggestions

> **Status:** This is a separate AI-generated answer key, created at the user's request. It is a set of reasoned suggestions, not the learner's audit. Do not copy it into `COLUMNS_USER_REVIEW.md` or treat Step 2 as complete. Make your own choices in `notebooks/01_column_audit_workshop.ipynb`, then compare your reasoning with this key.

## How to read the suggested bins

- **Bin 1 — Fixed at booking:** the value is known when the booking is made and does not change.
- **Bin 2 — Amendable / timing uncertain:** the value can change, is derived later, or the paper does not prove it was fixed at booking.
- **Bin 3 — After the fact:** the field records an outcome or information written after cancellation, check-in, or stay.

The dataset article says values were extracted from the bookings table and change log as of the day before arrival. Therefore a final CSV value alone does not establish what was known when the booking was first made. The proposed bins below apply that distinction conservatively. Article facts are from Table 1, Section 2, and Tables 2–7 of Antonio, de Almeida and Nunes (2019), [*Hotel booking demand datasets*](https://doi.org/10.1016/j.dib.2018.11.126); the target and scoring interpretation also follows `docs/EVALUATION_CONTRACT.md`.

## Proposed answers for all 32 columns

| CSV column | Suggested bin | Answer to the timing / role question |
|---|---:|---|
| `hotel` | **1** | The property is known for the reservation and is not described as changing for an existing booking. Use it as a required grouping key for the hotel-night decision. It does not, by itself, prove different capacity or operating rules. |
| `is_canceled` | **3** | This is the outcome label, not a predictor. The article describes it as a binary cancellation indicator; the course contract treats a value of 1 as including no-shows. Keep proof outcomes held back until the final run. |
| `lead_time` | **2** | It is booking-entry date to arrival date. The entry date is known at creation, but an amended arrival date changes the derived lead time; the export does not establish the original value. Recompute from a dated snapshot if used. |
| `arrival_date_year` | **2** | It is part of the intended arrival date, which can be amended. It is required to identify the arrival-night grouping, but the value used must come from the current booking snapshot. |
| `arrival_date_month` | **2** | Same reasoning as arrival year: it is a date component and can change with an arrival amendment. Use the current arrival date for grouping, not an unversioned final value as proof of booking-time availability. |
| `arrival_date_week_number` | **2** | It is derived from arrival date and changes when that date changes. It is calendar information, not a separate immutable fact. |
| `arrival_date_day_of_month` | **2** | It is part of an amendable arrival date. Use it only as part of the dated hotel-night key or as a feature if the decision-time snapshot is verified. |
| `stays_in_weekend_nights` | **2** | The article says stay duration can change; this field is also calculated from the booked/stayed total nights. The final value may differ from the original request. |
| `stays_in_week_nights` | **2** | Same as weekend nights: it is a component of stay length and can change. For the contract's empty-room valuation, use the scoring contract's defined booked-stay value; for a predictor, require the as-of value. |
| `adults` | **2** | Guest counts come from booking/change records, and the paper cautions that party attributes can change. The final count is not proven to be the original booking count. |
| `children` | **2** | It sums payable and non-payable children and can change with party composition. Check the definition before interpreting zeros or extreme values. |
| `babies` | **2** | Party composition can change, and the paper gives no guarantee this is immutable at creation. The H2 maximum of 10 is a value to investigate, not automatically recode. |
| `meal` | **2** | Meal choice is taken from booking/change and meal tables; the article lists meal among attributes that may be amended. A dated snapshot is needed to know the value at the decision time. |
| `country` | **3** | The paper explicitly warns that the hotel may not know the correct country until check-in. Treat it as unavailable for an earlier booking-time recommendation unless a real source proves otherwise. |
| `market_segment` | **2** | It comes from booking/change and market-segment tables, but the paper does not prove the final classification was fixed at original booking time. Keep it in the uncertain bin pending a timestamped source. |
| `distribution_channel` | **2** | It comes from booking/change and distribution-channel tables. The channel may seem like an original booking fact, but the paper does not establish that the provided final value is immutable; use Bin 2 until verified. |
| `is_repeated_guest` | **1** | The paper defines it using whether a customer profile existed before the current booking. That is historical information available by booking creation. Check how bookings without an associated profile are represented. |
| `previous_cancellations` | **1** | The count is explicitly limited to cancellations before the current booking. It is historical. The article sets it to zero when no customer profile is linked, so zero can combine distinct cases. |
| `previous_bookings_not_canceled` | **1** | The count is explicitly for earlier bookings before the current one. It is historical, with the same caution that no linked profile is encoded as zero. |
| `reserved_room_type` | **2** | This is the requested room type, but the paper lists reserved-room type among attributes that can change. A point-in-time version is needed. |
| `assigned_room_type` | **2** | It can differ from the requested type because of operations, including overbooking, or customer request. It may reflect a later operational decision, so it is not safe as a fixed booking-time input without a timestamp. |
| `booking_changes` | **3** | It counts amendments from booking entry through check-in or cancellation. The cumulative count includes future changes relative to booking creation, so it leaks later information. |
| `deposit_type` | **2** | It is calculated from payments found before arrival or cancellation. Payments and the resulting category can occur after booking creation; the export does not establish the value available at the initial decision time. |
| `agent` | **2** | It is an anonymized agency ID from booking/change records. The paper says `NULL` means not applicable, but does not establish that the ID cannot be added or changed later. Verify the PMS event time. |
| `company` | **2** | It is an anonymized company/entity ID that made or pays for the booking. The paper does not establish that the association is fixed at booking creation. `NULL` means not applicable, not missing. |
| `days_in_waiting_list` | **2** | It is calculated from PMS entry until confirmation. The elapsed duration is not known at request entry, though it may be known once the booking is confirmed. The bin depends on the actual prediction time. |
| `customer_type` | **2** | The category includes group and transient-party relationships. Those relationships may be recognized after initial entry; the paper does not establish that the final category is available at booking creation. |
| `adr` | **2** | It is calculated from lodging transactions and total stay nights using BO/BL/TR data. Rate, transactions, or stay length may change after booking. The paper reports negative and very large values; investigate before cleaning rather than silently altering them. |
| `required_car_parking_spaces` | **2** | It is a customer request from booking/change records. The number may be added or amended after the reservation is first entered; a dated request history would settle availability. |
| `total_of_special_requests` | **2** | It is a sum of special requests, which may accumulate after booking. The final total is not proof of the count known at creation. |
| `reservation_status` | **3** | It is the last status: canceled, check-out, or no-show. It reveals the booking outcome and should be used as a label/validation field, never as a predictor. The contract's no-show interpretation comes from the contract, not from assuming the CSV status categories are identical. |
| `reservation_status_date` | **3** | It is the date the last status was set. It identifies cancellation or checkout timing, which is after the recommendation and may reveal the outcome. Do not use it as a predictor. |

## Answers to the cross-column decision questions

### Which values are strongest candidates for Bin 1?

The proposed Bin 1 fields are `hotel`, `is_repeated_guest`, `previous_cancellations`, and `previous_bookings_not_canceled`. `hotel` is mainly a grouping key. The three guest-history fields are defined using the profile and history before the current booking. Even for these, confirm that the values in the available snapshot truly preserve the pre-booking information.

### Which fields are grouping keys rather than ordinary predictors?

The action is one oversell count per hotel on each arrival night. `hotel` and the arrival date identify that unit. Arrival-date fields are Bin 2 here because an arrival date can be amended; the operational key should use the arrival date current at the time the nightly decision is produced. A key being necessary does not automatically make its final export value a safe predictor.

### Which Bin 2 fields might be usable with point-in-time data?

All Bin 2 fields could be reconsidered if the team can reconstruct their values at the exact intended prediction time. Examples include current party size, stay length, meal, deposit, room type, rate, and requests. The day-before-arrival export alone does not provide the original booking-time snapshot. For the course exercise, state clearly how its final-book scoring differs from a live morning snapshot.

### Which fields are outcomes or outcome-derived?

`is_canceled`, `booking_changes`, `country` (when only learned at check-in), `reservation_status`, and `reservation_status_date` are not safe booking-time predictors under these definitions. `assigned_room_type` is also risky because it can reflect an operational assignment made after the overbooking decision. Keep the target label separate from features.

### How should `is_canceled` and `reservation_status` be reconciled?

The article describes `is_canceled` as binary and separately lists `Canceled`, `Check-Out`, and `No-Show` statuses. The project scoring contract is authoritative for the exercise and says canceled outcomes include no-shows. Use `is_canceled` as the label per contract; use a train/choose-only cross-tab of status versus target if you need to understand how the supplied CSV encodes no-shows. Do not inspect proof outcomes during this audit.

### Do the two hotels have different operating rules?

The paper identifies H1 as a resort and H2 as a city hotel; the notebook shows different cancellation rates. That supports separate reporting, but it does not prove different capacities, cancellation policies, or walk limits. The brief supplies a shared walk ceiling. Ask the client whether a per-hotel ceiling is also required.

### What should happen to unusual values?

Do not remove or recode a row just because a published minimum or maximum looks unusual. Inspect the relevant CSV rows, count how many are affected, check the contract/source definition, and record a reason before deciding. Examples to examine include H1 ADR below zero, H2 ADR up to 5,400, adults up to 55, and babies up to 10 in the paper's profiles.

## Keep this key separate from your work

Use this file as a comparison after you have attempted the notebook prompts. If your bin differs, keep your decision if your evidence and reasoning support it; record what source or client detail would resolve the uncertainty. `docs/COLUMNS_USER_REVIEW.md` is generated only from your own completed notebook entries. Step 2 remains in progress until you finish that review.
