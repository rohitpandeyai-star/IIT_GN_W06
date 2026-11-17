# Column Source Reference for Your Audit

> **Purpose:** This is a detailed evidence sheet to use alongside `notebooks/01_column_audit_workshop.ipynb`. It extracts the definitions, source tables, engineering notes, published profile statistics, and timing cautions from the supplied Antonio, de Almeida and Nunes paper. It does **not** assign bins for you. Make your own bin and explain it in the notebook after reviewing the evidence.
>
> **Source:** Nuno Antonio, Ana de Almeida, and Luis Nunes (2019), “Hotel booking demand datasets,” *Data in Brief*, 22, 41–49. [DOI and article](https://doi.org/10.1016/j.dib.2018.11.126). The user supplied PDF `1-s2.0-S2352340918315191-main.pdf`. Column definitions and source/engineering are from Table 1 (PDF pp. 3–5); extraction timing and data cautions are from Section 2 (PDF p. 5); published profiles are from Tables 2–7 (PDF pp. 6–7).

## How to use this reference

For each field, answer these separately in your own words:

1. When would the hotel first know the value: when a booking request is entered, when it is confirmed, later before arrival, at check-in, during the stay, or after cancellation/checkout?
2. Could that value change after it first becomes known?
3. Is it an input, an identifier/grouping key, the target, or an outcome written after the event?
4. What evidence supports your timing choice? What would you still need to verify in a real booking snapshot/change log?

The project bins are: **1, fixed at booking** (known on the booking date and does not change); **2, amendable or timing uncertain**; **3, after the fact**. A published final value is not by itself proof of when it was known.

## Important reading of the paper's data timing

The article says each data point is defined as **the day before the booking's arrival**. The authors extract values from the bookings table (BO), then check the booking change log (BL) for alterations up to the day before arrival; if an alteration exists, they use the changed value. Related tables are joined for some variables. This means the paper describes a near-arrival snapshot, not a complete snapshot of what was known when each booking was first made.

The authors also warn that guest details, stay length, and room preferences can change at check-in or during the stay; the hotel may not know the correct nationality until check-in. That warning is central to your audit. The course's live decision is an oversell count by hotel-night, and its exercise scores the final book. Keep the course exercise and a real booking-time operating snapshot distinct when explaining your choices.

The paper says its underlying PMS tables had no missing data. It says `NULL` in `Agent` or `Company` is a category meaning “not applicable” (for example, no travel agent), not a missing-value error. Verify the representation in the provided CSV before changing it.

### Source-table abbreviations

| Abbreviation | Meaning in the paper |
|---|---|
| BO | Bookings table |
| BL | Bookings change-log table |
| TR | Transactions table |
| ML | Meals table |
| NT | Nationalities table |
| DC | Distribution-channels table |
| CP / C | Customer profile table |
| MS | Market-segments table |

IDs such as agency, company, and room-type codes are anonymized identifiers, not human-readable names.

## Column-by-column evidence

The article reports H1 as the resort hotel in the Algarve and H2 as the city hotel in Lisbon. In the provided CSV these correspond to `Resort Hotel` and `City Hotel`. The article says each observation is one booking, includes arrivals and cancellations, and covers arrivals from 2015-07-01 to 2017-08-31. It reports 31 shared booking variables; the provided CSV has 32 columns because it also carries the hotel category. The article is open access under CC BY 4.0. Published numeric statistics below use the article's order: mean, standard deviation, minimum, 25th percentile, median, 75th percentile, maximum. Published category counts show only the most frequent categories, not every value.

### 1. `hotel` — Hotel property (CSV category)

- **Paper context:** H1 is the resort hotel in Algarve; H2 is the city hotel in Lisbon. The article reports 40,060 H1 bookings and 79,330 H2 bookings, 119,390 in total. Property/customer identifiers were removed or anonymized.
- **Source / construction:** This is the property identifier that separates the two supplied datasets; it is not one of the 31 Table 1 booking variables.
- **Published profile:** H1 40,060 rows; H2 79,330 rows.
- **Questions for your decision:** Is `hotel` an input, an essential grouping key for one decision per hotel-night, or both? Does a property identifier change for an existing booking? Does a difference in hotel cancellation rates prove a different booking rule? What evidence would establish per-hotel capacity or policy differences?

### 2. `is_canceled` — IsCanceled (categorical / binary)

- **Paper definition:** Indicates whether a booking was canceled: 1 or 0.
- **Source / engineering:** BO.
- **Published profile:** H1: 0 = 28,938; 1 = 11,122. H2: 0 = 46,228; 1 = 33,102.
- **Questions for your decision:** This is the prediction target or label, not a usable input. The paper describes a cancellation indicator; the project scoring contract says the target's 1 includes no-shows. How will you explain the contract's interpretation alongside the paper's separate `No-Show` status? How will you keep proof-period labels out of the early audit and tuning?

### 3. `lead_time` — LeadTime (integer)

- **Paper definition:** Number of days from the date the booking was entered in the PMS to the arrival date.
- **Source / engineering:** BO and BL; calculated by subtracting the booking-entry date from the arrival date.
- **Published profile:** H1: 92.68, 97.29, 0, 10, 57, 155, 737. H2: 109.74, 110.95, 0, 23, 74, 163, 629.
- **Questions for your decision:** Is the booking-entry date known when the reservation is created? Can an arrival-date amendment change the final lead time? Does the CSV retain the original booking-entry value or only the day-before-arrival version? What point-in-time value would the rule use?

### 4. `arrival_date_year` — ArrivalDateYear (integer)

- **Paper definition:** Year of the arrival date.
- **Source / engineering:** BO and BL.
- **Published profile:** H1: 2016.12, 0.72, 2015, 2016, 2016, 2017, 2017. H2: 2016.17, 0.70, 2015, 2016, 2016, 2017, 2017.
- **Questions for your decision:** Is this a predictor or part of the hotel-night key? Could it change if the arrival date changes? If you need it for grouping, which dated snapshot provides the operative arrival date?

### 5. `arrival_date_month` — ArrivalDateMonth (categorical)

- **Paper definition:** Month of arrival, with January through December as the 12 categories.
- **Source / engineering:** BO and BL.
- **Published profile:** 12 unique values at each hotel. H1 top counts: August 4,894; July 4,573; April 3,609; May 3,559. H2: August 8,983; May 8,232; July 8,088; June 7,894.
- **Questions for your decision:** Does the month stay fixed if arrival is amended? Is it a seasonal input or only a grouping field? How should it be derived if the hotel-night date is updated?

### 6. `arrival_date_week_number` — ArrivalDateWeekNumber (integer)

- **Paper definition:** Week number of the arrival date.
- **Source / engineering:** BO and BL.
- **Published profile:** H1: 27.14, 14.01, 1, 16, 28, 38, 53. H2: 27.18, 13.40, 1, 17, 27, 38, 53.
- **Questions for your decision:** Is this only a date-derived field? Could it change with an arrival-date amendment? Do you need this separate calendar representation if you already use the full arrival date?

### 7. `arrival_date_day_of_month` — ArrivalDateDayOfMonth (integer)

- **Paper definition:** Day number within the arrival month.
- **Source / engineering:** BO and BL.
- **Published profile:** H1: 15.82, 8.88, 1, 8, 16, 24, 31. H2: 15.79, 8.73, 1, 8, 16, 23, 31.
- **Questions for your decision:** Is this a predictor or part of the decision key? Can it change if the reservation's arrival is amended? What representation will reliably identify one arrival night?

### 8. `stays_in_weekend_nights` — StaysInWeekendNights (integer)

- **Paper definition:** Number of Saturday/Sunday nights the guest stayed or booked to stay.
- **Source / engineering:** BO and BL; calculated by counting weekend nights among total nights.
- **Published profile:** H1: 1.19, 1.15, 0, 0, 1, 2, 19. H2: 0.80, 0.89, 0, 0, 1, 2, 16.
- **Questions for your decision:** Is this the original requested stay or a later amended stay? The paper says stay duration can change. If the cost contract uses the booked stay value, which timestamp's stay length should be used?

### 9. `stays_in_week_nights` — StaysInWeekNights (integer)

- **Paper definition:** Number of Monday–Friday nights the guest stayed or booked to stay.
- **Source / engineering:** BO and BL; calculated from total nights.
- **Published profile:** H1: 3.13, 2.46, 0, 1, 3, 5, 50. H2: 2.18, 1.46, 0, 1, 2, 3, 41.
- **Questions for your decision:** Could this be amended before arrival? How would a changed departure date affect the final value? Which version should be used for the project cost formula and why?

### 10. `adults` — Adults (integer)

- **Paper definition:** Number of adults.
- **Source / engineering:** BO and BL.
- **Published profile:** H1: 1.87, 0.70, 0, 2, 2, 2, 55. H2: 1.85, 0.51, 0, 2, 2, 2, 4.
- **Questions for your decision:** Can the guest party size change after the reservation is created? Does the article's caution about guest attributes changing apply? At what snapshot time is this count available?

### 11. `children` — Children (integer)

- **Paper definition:** Number of children.
- **Source / engineering:** BO and BL; sum of both payable and non-payable children.
- **Published profile:** H1: 0.13, 0.45, 0, 0, 0, 0, 10. H2: 0.091, 0.37, 0, 0, 0, 0, 3.
- **Questions for your decision:** Can this count change? Does its combined payable/non-payable definition affect how you interpret zeros and extreme values? Is it known at initial booking or only in a later snapshot?

### 12. `babies` — Babies (integer)

- **Paper definition:** Number of babies.
- **Source / engineering:** BO and BL.
- **Published profile:** H1: 0.014, 0.12, 0, 0, 0, 0, 2. H2: 0.0049, 0.084, 0, 0, 0, 0, 10.
- **Questions for your decision:** Can the party composition change after booking? What would you check about the unusually high H2 maximum of 10 before using or correcting it?

### 13. `meal` — Meal (categorical)

- **Paper definition:** Meal package. Undefined/SC means no meal package; BB means bed and breakfast; HB means half-board (breakfast plus one other meal, usually dinner); FB means full-board (breakfast, lunch, and dinner).
- **Source / engineering:** BO, BL, and ML (Meals table).
- **Published profile:** H1 has 5 unique values; top counts: BB 30,005; HB 8,046; Undefined 1,169; FB 754. H2 has 4; top counts: BB 62,305; SC 10,564; HB 6,417; FB 44.
- **Questions for your decision:** When is the meal package selected? Can it be amended? Does BO/BL establish the initial choice or the later value? What source timestamp would answer this?

### 14. `country` — Country (categorical)

- **Paper definition:** Country of origin, represented using ISO 3155-3:2013 codes.
- **Source / engineering:** BO, BL, and NT (Nationalities table).
- **Published profile:** H1 has 125 unique values; top: PRT 17,630; GBR 6,814; ESP 3,957; IRL 2,166. H2 has 166; top: PRT 30,960; FRA 8,804; DEU 6,084; GBR 5,315.
- **Paper timing caution:** The authors say hotels may not know the correct nationality until check-in.
- **Questions for your decision:** When does the hotel actually learn the correct country? Is it recorded from the guest's declared origin, a profile, or a later check-in update? Could it expose post-booking information?

### 15. `market_segment` — MarketSegment (categorical)

- **Paper definition:** Market-segment designation. TA means travel agents; TO means tour operators.
- **Source / engineering:** BO, BL, and MS (Market-segments table).
- **Published profile:** H1 has 6 unique values; top: Online 17,729; Offline 7,472; Direct 6,513; Groups 5,836. H2 has 8; top: Online 38,748; Offline 16,747; Groups 13,975; Direct 6,093.
- **Questions for your decision:** Is the category assigned at booking creation, derived later, or amendable? Does the market-segment table preserve time history? Which categories are in the CSV, and what do they mean in the client's setting?

### 16. `distribution_channel` — DistributionChannel (categorical)

- **Paper definition:** Booking distribution channel. TA means travel agents; TO means tour operators.
- **Source / engineering:** BO, BL, and DC (Distribution-channels table).
- **Published profile:** H1 has 4 unique values; top: TA/TO 28,295; Direct 7,865; Corporate 3,269; Undefined 1. H2 has 5; top: TA/TO 68,945; Direct 6,780; Corporate 3,408; GDS 193.
- **Questions for your decision:** At what moment does the channel become known? Can a reservation transferred or amended by a partner change this field? Does the final export record the original or latest channel?

### 17. `is_repeated_guest` — IsRepeatedGuest (categorical / binary)

- **Paper definition:** 1 if the booking name is from a repeat guest, 0 otherwise.
- **Source / engineering:** BO, BL, and C (Customer profile). A profile must be associated with the booking, and its creation date must be before the booking creation date to count as repeated.
- **Published profile:** H1: 0 = 38,282; 1 = 1,778. H2: 0 = 77,298; 1 = 2,032.
- **Questions for your decision:** Does the definition use only history available before the current booking? What happens when no profile is associated? Does the day-before-arrival snapshot preserve that historical test?

### 18. `previous_cancellations` — PreviousCancellations (integer)

- **Paper definition:** Number of the customer's prior bookings canceled before the current booking.
- **Source / engineering:** BO and BL. If there is no associated customer profile, the value is set to 0; otherwise count that profile's earlier canceled bookings.
- **Published profile:** H1: 0.10, 1.34, 0, 0, 0, 0, 26. H2: 0.08, 0.42, 0, 0, 0, 0, 32.
- **Questions for your decision:** Are all counted cancellations strictly before the current booking? Does 0 mean no earlier cancellations, or can it also mean no associated profile? Is that distinction important for your use?

### 19. `previous_bookings_not_canceled` — PreviousBookingsNotCanceled (integer)

- **Paper definition:** Number of the customer's prior bookings that were not canceled before the current booking.
- **Source / engineering:** BO and BL. If no customer profile is associated, value is 0; otherwise count earlier non-canceled bookings for that profile.
- **Published profile:** H1: 0.15, 1.00, 0, 0, 0, 0, 30. H2: 0.13, 1.69, 0, 0, 0, 0, 72.
- **Questions for your decision:** Is the history limited to bookings before this booking? How is a missing profile distinguished from a true zero-history guest? Do you have evidence the history count is available at the decision time?

### 20. `reserved_room_type` — ReservedRoomType (categorical)

- **Paper definition:** An anonymized code for the room type reserved.
- **Source / engineering:** BO and BL. The paper lists reserved room type among attributes that can change in the booking change log.
- **Published profile:** H1 has 10 unique values; top: A 23,399; D 7,433; E 4,892; G 1,610. H2 has 8; top: A 62,595; D 11,768; F 1,791; E 1,553.
- **Questions for your decision:** Does the value represent the original request or the latest requested room? Can guests change it? Would the room category be known at the time your decision is made?

### 21. `assigned_room_type` — AssignedRoomType (categorical)

- **Paper definition:** An anonymized code for the room type assigned to the booking. It can differ from the reserved type due to hotel operations (for example, overbooking) or customer request.
- **Source / engineering:** BO and BL.
- **Published profile:** H1 has 11 unique values; top: A 17,046; D 10,339; E 5,638; C 2,214. H2 has 9; top: A 57,007; D 14,983; E 2,168; F 2,018.
- **Questions for your decision:** When is the assignment first made and can it be changed? Might it encode an operational decision made after the oversell recommendation? Could it reveal the result of overbooking itself?

### 22. `booking_changes` — BookingChanges (integer)

- **Paper definition:** Count of changes/amendments from when a booking entered the PMS until check-in or cancellation.
- **Source / engineering:** BO and BL. The count adds unique iterations that change persons, arrival date, nights, reserved room type, or meal.
- **Published profile:** H1: 0.29, 0.73, 0, 0, 0, 0, 17. H2: 0.19, 0.61, 0, 0, 0, 0, 21.
- **Questions for your decision:** Is the full count known at initial booking? Which included changes happen later? Would this count leak future amendment or cancellation information when forecasting from the booking date?

### 23. `deposit_type` — DepositType (categorical)

- **Paper definition:** Whether a deposit was paid: No Deposit; Non Refund (deposit equals total stay cost); Refundable (deposit is less than total cost).
- **Source / engineering:** BO and TR (Transactions). Based on payments found before arrival or cancellation. If no payment is found, value is No Deposit; if payments equal/exceed total stay cost, Non Refund; otherwise Refundable.
- **Published profile:** H1: 3 unique values; No Deposit 38,199; Non-Refundable 1,719; Refundable 142. H2: 3; No Deposit 66,442; Non-Refundable 12,868; Refundable 20.
- **Questions for your decision:** Can payment occur after booking creation? Is the classification calculated using payments through a later date? Does the “before cancellation date” wording mean canceled bookings have a different information window? What would a timestamped payment snapshot show?

### 24. `agent` — Agent (categorical identifier)

- **Paper definition:** ID of the travel agency that made the booking. The ID is shown instead of the agency name for anonymity.
- **Source / engineering:** BO and BL.
- **Published profile:** H1 has 186 unique values; top: 240 13,095; NULL 8,209; 250 2,869; 241 1,721. H2 has 224; top: 9 31,955; NULL 8,131; 1 7,137; 14 3,640.
- **Paper missing-value note:** NULL means “not applicable” (such as no travel agent), not a missing-value error.
- **Questions for your decision:** Is the agent known when the booking enters the system? Can it change if the booking is transferred or amended? Does the ID encode useful information, or is it only an anonymized category?

### 25. `company` — Company (categorical identifier)

- **Paper definition:** ID of the company/entity that made the booking or is responsible for paying; the ID is anonymized.
- **Source / engineering:** BO and BL.
- **Published profile:** H1 has 236 unique values; top: NULL 36,952; 223 784; 281 138; 154 133. H2 has 208; top: NULL 75,641; 40 924; 67 267; 45 250.
- **Paper missing-value note:** NULL is a “not applicable” category, not a missing-value error.
- **Questions for your decision:** When is the payer/company link established? Could it change later? How should the large NULL category be interpreted without treating it as missing?

### 26. `days_in_waiting_list` — DaysInWaitingList (integer)

- **Paper definition:** Number of days a booking remained on the waiting list before being confirmed to the customer.
- **Source / engineering:** BO; calculated as confirmation date minus the date the booking entered the PMS.
- **Published profile:** H1: 0.53, 7.43, 0, 0, 0, 0, 185. H2: 3.23, 20.87, 0, 0, 0, 0, 391.
- **Questions for your decision:** Is this known when the request first enters the system, or only once confirmed? Is the “booking” timestamp before or after confirmation? What date would you use for a prediction made at confirmation?

### 27. `customer_type` — CustomerType (categorical)

- **Paper definition:** Contract (allotment or other contract); Group; Transient (not part of a group/contract or linked transient booking); Transient-party (transient booking associated with at least one other transient booking).
- **Source / engineering:** BO and BL.
- **Published profile:** H1 has 4 values; Transient 30,209; Transient-party 7,791; Contract 1,776; Group 284. H2: Transient 59,404; Transient-party 17,333; Contract 2,300; Group 293.
- **Questions for your decision:** When is the booking's group/contract relationship known? Could the association be added later? Is Transient-party derived from other bookings in a way that may not exist at the initial booking time?

### 28. `adr` — ADR (numeric)

- **Paper definition:** Average Daily Rate as defined by reference [5]. In this dataset it is lodging transaction amount divided by total nights stayed.
- **Source / engineering:** BO, BL, and TR; calculated from the sum of lodging transactions and total stay nights.
- **Published profile:** H1: 94.95, 61.44, -6.38, 50, 75, 125, 508. H2: 105.3, 43.6, 0, 79.2, 99.9, 126, 5,400.
- **Questions for your decision:** Is ADR fixed when first booked or can rate/transactions/stay length change? Why are negative and very large values present in the published profile? How will you investigate them without silently changing rows? The course contract uses ADR in the empty-room stay-value calculation, so distinguish that scoring use from predictor timing.

### 29. `required_car_parking_spaces` — RequiredCardParkingSpaces (integer)

- **Paper definition:** Number of car-parking spaces required by the customer.
- **Source / engineering:** BO and BL.
- **Published profile:** H1: 0.14, 0.35, 0, 0, 0, 0, 8. H2: 0.024, 0.15, 0, 0, 0, 0, 3.
- **Questions for your decision:** Is this requested at reservation time or can the request be added later? How should zero be interpreted? Does the final count match a booking-time snapshot?

### 30. `total_of_special_requests` — TotalOfSpecialRequests (integer)

- **Paper definition:** Total number of customer special requests, such as a twin bed or high floor.
- **Source / engineering:** BO and BL; sum of all special requests.
- **Published profile:** H1: 0.62, 0.81, 0, 0, 0, 1, 5. H2: 0.55, 0.78, 0, 0, 0, 1, 5.
- **Questions for your decision:** Can requests accumulate or change after the initial reservation? Does the source preserve when each request was made? At what date would the displayed total be available?

### 31. `reservation_status` — ReservationStatus (categorical outcome)

- **Paper definition:** Last reservation status, with three categories: Canceled (customer canceled); Check-Out (customer checked in and later departed); No-Show (customer did not check in and informed the hotel of the reason).
- **Source / engineering:** BO.
- **Published profile:** H1 has 3 values; Check-Out 28,938; Canceled 10,831; No-Show 291. H2: Check-Out 46,228; Canceled 32,186; No-Show 916.
- **Questions for your decision:** Is this a final outcome written after the decision? How does `No-Show` relate to the course contract's `is_canceled` target? Should this be a predictor, target-adjacent check, or validation field only?

### 32. `reservation_status_date` — ReservationStatusDate (date)

- **Paper definition:** Date the last status was set; used with status to understand when a booking was canceled or when the guest checked out.
- **Source / engineering:** BO.
- **Published profile:** H1: min 2014-11-18; max 2017-09-14; median 2016-07-31; 913 unique dates. H2: min 2014-10-17; max 2017-09-07; median 2016-08-10; 864 unique dates.
- **Questions for your decision:** Does this date record the outcome or its final update? Would it be known at original booking time? Could it disclose cancellation/check-out timing and therefore leak the target?

## Cross-column decisions to make in your notebook

- Which fields are true booking-time facts, and what evidence proves that the value is both known then and unchanged later?
- Which fields are necessary action keys (hotel and arrival night) but should not automatically be treated as predictors?
- Which fields are amendable but might be usable in a future model if an exact dated snapshot is available?
- Which fields are outcomes or outcome-derived and must not be predictors?
- Does any field have an article definition that differs from the scoring contract? In particular, explain `is_canceled` versus the separate `No-Show` category.
- Do H1/Resort and H2/City require separate reporting? Different descriptive statistics alone do not prove that different operational rules apply.
- Which unusual values (for example, ADR below zero or extreme guest counts) need investigation? Record evidence and row counts before any cleaning decision.

## Source and interpretation boundary

This guide paraphrases the article's definitions and tables; it does not reproduce the article verbatim. Article facts are separated from questions for your own decisions. The article's snapshot timing is not a substitute for the course contract or for a real hotel's timestamped point-in-time data. No bin is assigned here.
