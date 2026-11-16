# Which columns are available at the decision time?

**Owner:** Data Lead. **Use:** feature audit, PRD, and slide 4.

> **AI-generated preliminary suggestions, not the learner's audit.** Do not treat these bins as your decisions. The learner is reviewing every field sequentially in `notebooks/01_column_audit_workshop.ipynb`; replace or reconcile this file only after recording their choices. The source CSV is a snapshot reconstructed from the property-management system; the article says values were taken from booking/change records as of the day before arrival. A column's presence in this export does not prove its value was known at the original booking time.

Bins:

1. **Fixed at booking:** known when the booking is made and does not change.
2. **Amendable / timing uncertain:** can change, accumulates, or the source does not establish it was fixed at booking. Exclude from the MVP unless point-in-time availability is verified.
3. **After the fact:** outcome or information recorded after cancellation, check-in, or stay. Never use as a predictor.

The dataset reference is Antonio, de Almeida and Nunes (2019), especially Table 1 and section 2, [*Hotel booking demand datasets*](https://doi.org/10.1016/j.dib.2018.11.126). The article describes the day-before-arrival extraction, the booking change log, possible changes to guest attributes, and country sometimes being unknown until check-in. “Source” abbreviations in the article include BO (bookings), BL (booking change log), TR (transactions), and related property-management tables.

| Column | Preliminary AI bin | AI's rationale to review | Evidence to consider |
|---|---:|---|---|
| `hotel` | 1 | Property for which the booking is made; no evidence that a booking changes hotels. | BO; property identity. Keep as grouping/input. |
| `is_canceled` | 3 | Outcome label (includes the course's no-show treatment). | BO; target only, never predictor. |
| `lead_time` | 2 | Derived from booking entry and arrival date; arrival dates may be amended. | BO/BL; do not assume the final value equals the booking-time value. |
| `arrival_date_year` | 2 | Part of arrival date; arrival date may change. | BO/BL; may be used only if frozen as known at decision time. |
| `arrival_date_month` | 2 | Part of arrival date; arrival date may change. | BO/BL; same caveat as arrival year. |
| `arrival_date_week_number` | 2 | Derived from arrival date; arrival date may change. | BO/BL; same caveat as arrival year. |
| `arrival_date_day_of_month` | 2 | Part of arrival date; arrival date may change. | BO/BL; same caveat as arrival year. |
| `stays_in_weekend_nights` | 2 | Length of stay can be amended before arrival. | BO/BL; source article notes nights among attributes that can change. |
| `stays_in_week_nights` | 2 | Length of stay can be amended before arrival. | BO/BL; source article notes nights among attributes that can change. |
| `adults` | 2 | Guest count can be amended. | BO/BL; article cautions guest attributes can change. |
| `children` | 2 | Guest count can be amended; source sums payable and non-payable children. | BO/BL; do not assume booking-time value. |
| `babies` | 2 | Guest count can be amended. | BO/BL; conservative timing classification. |
| `meal` | 2 | Meal choice may be amended. | BO/BL/ML; article lists meal among booking changes. |
| `country` | 3 | The hotel may not know the guest's country until check-in. | BO/BL/NT; explicitly cautioned in section 2. Exclude. |
| `market_segment` | 2 | Source does not establish that the final category is immutable at original booking time. | BO/BL/MS; verify point-in-time snapshot before use. |
| `distribution_channel` | 2 | Source includes booking and channel tables but does not establish original-time immutability in this export. | BO/BL/DC; conservative pending source-system validation. |
| `is_repeated_guest` | 1 | Defined by whether the guest profile existed before this booking. | BO/BL/customer profile; historical relationship fixed at booking creation. |
| `previous_cancellations` | 1 | Counts cancellations before the current booking. | BO/BL; historical count prior to current booking. |
| `previous_bookings_not_canceled` | 1 | Counts non-canceled bookings before the current booking. | BO/BL; historical count prior to current booking. |
| `reserved_room_type` | 2 | Requested room type can change. | BO/BL; article lists reserved room type among booking changes. |
| `assigned_room_type` | 2 | Assignment can differ from requested type and may reflect hotel operations or a customer request. | BO/BL; assignment is not proven fixed at booking. Exclude pending timing validation. |
| `booking_changes` | 3 | Cumulative changes from booking creation through check-in or cancellation; future changes are included in the export. | BO/BL; definition explicitly spans later events. Exclude. |
| `deposit_type` | 2 | Derived from payments up to arrival or cancellation, so it can reflect transactions after booking creation. | BO/TR; not guaranteed available at booking. |
| `agent` | 2 | Agency ID is recorded from booking/change-log tables, but the source does not prove it is immutable in this snapshot. | BO/BL; treat conservatively until booking-time value is validated. |
| `company` | 2 | Company/entity association may not be fixed in the initial booking record. | BO/BL; source does not establish immutability. |
| `days_in_waiting_list` | 2 | Calculated from booking entry until confirmation; the value is not known when the request first enters the list. | BO; derived from elapsed time to confirmation. |
| `customer_type` | 2 | Includes relationship/grouping categories; source does not establish that the final classification is available and stable at creation. | BO/BL; verify time of classification. |
| `adr` | 2 | Built from booking/change-log and transaction data and can change with rate or stay amendments. | BO/BL/TR; not established as fixed at original booking time. |
| `required_car_parking_spaces` | 2 | A guest request can be added or changed. | BO/BL; conservative timing classification. |
| `total_of_special_requests` | 2 | Requests may accumulate after the booking is created. | BO/BL; cumulative count not guaranteed at original booking time. |
| `reservation_status` | 3 | Final status is cancellation, no-show, or checkout and reveals the outcome. | BO; target-related outcome field. Exclude. |
| `reservation_status_date` | 3 | Date when the last status was set. | BO; reveals outcome timing. Exclude. |

## MVP input rule

The only columns currently judged safe as fixed at booking are `hotel`, `is_repeated_guest`, `previous_cancellations`, and `previous_bookings_not_canceled`. The arrival-night grouping fields are needed to define the decision unit, but their booking-time values must be taken from a booking snapshot and updated if an amendment changes the arrival date. Do not use any bin 2/3 field as a predictor for the chosen MVP until a genuine point-in-time snapshot and availability time are established. Keep the target `is_canceled` only for fitting/evaluation labels.

The article's data point is the day before arrival, not a versioned row at initial booking creation. Thus the bins above are an audit of feature timing, not proof that this export supports a live booking-time model. The course's full-final-book scoring exercise is a separate, simplified decision setting.

## Leakage comparison

The proof AUC comparisons below belong to the POC stage and have not been run. Do not calculate or tune on proof outcomes until the method and settings are frozen.

| Run | Columns | Split | AUC on proof |
|---|---|---|---|
| A | Verified booking-time inputs only | Time | Not run |
| B | Includes amendable and after-the-fact columns (diagnostic only) | Time | Not run |
| C | Verified booking-time inputs only | Random (diagnostic only) | Not run |
