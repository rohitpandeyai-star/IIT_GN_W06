# Executive deck: where each original slide went

Source: `Hotel_Overbooking_Deck_By_Lead.pptx` (27 slides) → `Hotel_Overbooking_Executive_Deck.pptx` (49 slides).

| Original slide | Topic | Now on slides |
|---|---|---|
| 1 | Title and answer | 1, 2 |
| 2 | Client Lead · North Star | 5, 6 |
| 3 | Client Lead · North Star | 4, 18, 19 |
| 4 | Client Lead · North Star | 6, 20 |
| 5 | How This Deck Runs | 17, 18 |
| 6 | Client Lead · The Decision | 4, 19 |
| 7 | Client + Data Lead · The Data | 7 |
| 8 | Data Lead · Cleaning · What Changed | 21, 22 |
| 9 | Data Lead · Cleaning · Rows Kept | 23, 24 |
| 10 | Data Lead · Columns · The Test | 25, 26 |
| 11 | Data Lead · Columns · Tests T1 And T2 | 26, 27 |
| 12 | Data Lead · Columns · Test T3 | 27, 28 |
| 13 | Data Lead · Columns · Test T4 And The Passes | 28, 29 |
| 14 | Data Lead · Columns · The Choice | 8, 29 |
| 15 | Data Lead · Columns · Safe Inputs | 30, 31 |
| 16 | Data Lead · Columns · Provisional Inputs | 31, 32 |
| 17 | Data Lead · Columns · Excluded | 32, 33 |
| 18 | Data Lead · Columns · Tempting Traps | 33, 34, 35 |
| 19 | Data Lead · Encoding | 36, 37 |
| 20 | Model Lead · Settings Fixed In Advance | 38, 39 |
| 21 | Model Lead · Models Tried | 9, 40, 41 |
| 22 | Model Lead · Probability Quality | 10 |
| 23 | Model Lead · Rules Tried | 11, 42 |
| 24 | Model Lead · Earlier Experiments | 13, 43, 44 |
| 25 | Model Lead · The Choice | 2, 12, 45 |
| 26 | Build Lead · Engineering | 14, 46 |
| 27 | Client Lead · Limits And Next Steps | 14, 15 |

## Questions for the author

1. The formatting brief ends mid-sentence ('…and reuse a'). The process diagram (A4) is reused as a small step strip on later slides — is that what was meant?
2. Source slide 6 labels the test period 'Test · once', while slides 24–25 say the 2017 period was examined in earlier runs. Which wording should stand?
3. Source slide 15 says hotel is encoded as 'one 0/1 column' and agents '< 30 bookings pooled' (notebook 10), but slide 19 describes the final pipeline's one-hot encoding (hotel: 2 values, no pooling). Which encoding should B14 describe?
4. Source slide 22 shows '42%' and '94% · 53 rooms'; its notes say 41.6% and 94.3%. Both are kept — which precision should the chart use?
5. The repository has a second deck recommending the per-hotel flat rule (City 20 / Resort 4). This deck recommends the 17-room rule. Which is the client recommendation?
6. The nightly command serves the 20 / 4 rule, not the 17-room rule. Should it be rewired before any shadow run?
7. No owners are given for the next steps (docs/ROADMAP.md is blank). Who owns each step?
8. The evidence tags (High / Medium / Low) are this deck's reading of the source's own caveats. Please confirm or adjust them.
