# User-Completed Column Timing Audit

> Decisions entered by the learner in `notebooks/01_column_audit_workshop.ipynb`.

| Column | Bin | Reason in my words |
|---|---:|---|
| `hotel` | 1 - Fixed at booking | We always know the Hotel in which the booking has been made for |
| `is_canceled` | 3 - After the fact | As it is an event which can happen anytime before the guest actually enters the hotel |
| `lead_time` | 2 - Amendable or timing uncertain | We only know after the booking has been completed that what the actual lead time was and can be ammended later on |
| `arrival_date_year` | 2 - Amendable or timing uncertain |  It is part of the intended arrival date which can be changed later on |
| `arrival_date_month` | 2 - Amendable or timing uncertain |  It is part of the intended arrival date which can be changed later on |
| `arrival_date_week_number` | 2 - Amendable or timing uncertain |  It is part of the intended arrival date which can be changed later on |
| `arrival_date_day_of_month` | 2 - Amendable or timing uncertain | It is part of the intended arrival date which can be changed later on |
| `stays_in_weekend_nights` | 2 - Amendable or timing uncertain |  Stay duration can chnage later on |
| `stays_in_week_nights` | 2 - Amendable or timing uncertain |  Stay duration can chnage later on |
| `adults` | 2 - Amendable or timing uncertain | number of people can easily change later on |
| `children` | 2 - Amendable or timing uncertain | number of children can also easily change later on |
| `babies` | 2 - Amendable or timing uncertain |  number of babies can also change later on |
| `meal` | 2 - Amendable or timing uncertain | can change later on |
| `country` | 3 - After the fact | We may not know country until check in |
| `market_segment` | 2 - Amendable or timing uncertain | uncertain |
| `distribution_channel` | 2 - Amendable or timing uncertain |  uncertain |
| `is_repeated_guest` | 1 - Fixed at booking |  this is historical data |
| `previous_cancellations` | 1 - Fixed at booking |  this is historical data  |
| `previous_bookings_not_canceled` | 1 - Fixed at booking | this is again historical data |
| `reserved_room_type` | 2 - Amendable or timing uncertain |  it can change due to operational decisions |
| `assigned_room_type` | 2 - Amendable or timing uncertain |  it can change due to operational decisions |
| `booking_changes` | 3 - After the fact |  it can change due to operational decisions |
| `deposit_type` | 2 - Amendable or timing uncertain |  This can change accordingly later on  |
| `agent` | 2 - Amendable or timing uncertain | Uncertain |
| `company` | 2 - Amendable or timing uncertain | Uncertain |
| `days_in_waiting_list` | 2 - Amendable or timing uncertain | we need confirmation time otherwise uncertain |
| `customer_type` | 2 - Amendable or timing uncertain |  No clarity if final category is available at booking creation |
| `adr` | 2 - Amendable or timing uncertain |  Calculated from lodging transactions and stay nights which can change later on |
| `required_car_parking_spaces` | 2 - Amendable or timing uncertain | Can be ammended later on |
| `total_of_special_requests` | 2 - Amendable or timing uncertain | Can be ammended later on |
| `reservation_status` | 3 - After the fact | Can be ammended later on |
| `reservation_status_date` | 3 - After the fact | Can be ammended later on |
