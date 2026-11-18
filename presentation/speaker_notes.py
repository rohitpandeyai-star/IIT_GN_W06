# Spoken speaker notes, one per slide. Executed by build_deck.py after every slide is built; replaces the
# written-style notes. Key figures are asserted against deck_data.json so the script cannot drift from the slides.
_R1 = {(r["hotel"], r["method"]): r for r in D["nb"]["run1"]["rows"]}
_R3 = {(r["hotel"], r["method"]): r for r in D["nb"]["run3"]["rows"]}
assert round(_R1[("group", "flat rule")]["cost (EUR)"]) == 3214912 and _R1[("group", "flat rule")]["walks per 1,000"] == 7.18
assert round(_R1[("group", "CatBoost")]["cost (EUR)"] - _R1[("group", "flat rule")]["cost (EUR)"]) == 150459
assert (_R3[("group", "CatBoost")]["walks per 1,000"], _R3[("group", "XGBoost")]["walks per 1,000"]) == (13.11, 13.07)
assert round(D["earlier"]["val"]["flat-rule reference"]["per_hotel"]["cost"]) == 1950066
assert round(100 * D["nb"]["resample_cheaper_than_flat"]["CatBoost"]) == 74
assert D["nb"]["nb10"]["columns"] == 143 and D["nb"]["nb10"]["checks"] == 16

NOTES = {
    1: ("~40 s",
        "How many rooms can each hotel safely oversell each night? I'll give you the answer first. I trained four models: logistic "
        "regression, random forest, XGBoost and CatBoost. CatBoost won on the validation period, and I froze it before touching the 2017 "
        "test. On the test it did not beat the client's own flat rule: it cost about 150 thousand euros more. When I refitted the models on "
        "more data they got cheaper, but walked 13 guests per thousand, over the limit of 10, so the contract rejects them. My "
        "recommendation: keep the flat rule, with a separate safety margin for each hotel. It cost 3.21 million euros and walked 7.18 per thousand.",
        "The three numbers, left to right.",
        "First, what exactly is being decided.",
        ["So the project failed? — No model beat the rule on this data. That is a valid result: it tells the client not to buy a model yet, and why."]),
    2: ("~35 s",
        "The decision is one whole number per hotel per night: how many extra rooms to sell. There are two ways to be wrong. Too few, and "
        "cancelled rooms stay empty; each costs that night's average stay value. Too many, and a guest arrives to a full hotel and is walked, "
        "at 300 euros. And there is a hard limit: no more than 10 walks per 1,000 arrivals across the group. A rule that breaks it is out, "
        "however cheap. The contract fixes three periods by arrival date: train before July 2016, choose on the second half of 2016, test on "
        "January to August 2017.",
        "The three cards, then the period bar.",
        "So what does the data look like?",
        ["Why not just minimise cost? — Without the limit, every method's cheapest choice walks 22 to 82 guests per thousand.",
         "Are these real euros? — No. They are simulated contract costs: booking rows, not rooms, and no record of real walks."]),
    3: ("~30 s",
        "119,390 bookings over two years. 37 percent cancel: not one in four, as the brief said, but more than one in three. The City Hotel "
        "cancels far more than the Resort, 42 against 28 percent, and both move with the season. Two oddities shaped later decisions: about "
        "32 thousand rows are exact repeats, and Non Refund bookings cancel 99 percent of the time, which tells me the deposit field can't be "
        "trusted as an input.",
        "The gap between the two lines on the chart.",
        "That raises the question of which columns I may use.",
        ["Why would Non Refund cancel 99 percent? — Most likely the field is set or corrected after the outcome. Either way its timing can't be trusted."]),
    4: ("~35 s",
        "I chose columns by when the hotel knows them, not by how well they predict, because a leaking column predicts well everywhere, so no "
        "score can catch it. Each column faced four tests: not the outcome, known on the decision morning, unchanged until arrival, and about "
        "this booking only. Four pass all four. Four more are provisional: they pass, except that the source doesn't say when they are set. "
        "36 are excluded: things that change before arrival, get recalculated later, or are the outcome itself.",
        "Green 'Input' against amber 'Provisional'.",
        "Next, how the data was cleaned.",
        ["Which column would you drop if it were set at check-in? — Company first. But the riskiest is previous cancellations, which the models lean on most.",
         "Why not lead time? — It passes the tests but wasn't in the team's input set. It is the first thing I'd add, tested on validation."]),
    5: ("~30 s",
        "Six cleaning choices, each approved and logged with the rows it touched. Most are small recodes: an 'Undefined' meal means no meal, "
        "and a blank agent means no agent. The big one is the repeats: I kept all of them. There is no booking ID to prove a repeat is an "
        "error, and removing them would drop the training cancellation rate from 36 to 22 percent and change the nights the contract scores. "
        "I flagged odd rows instead.",
        "The dark box: 35.8 to 22.2 percent.",
        "Then the data has to become numbers a model can use.",
        ["Aren't duplicates obviously errors? — A tour operator can book a whole block. The largest group is 150 identical cancelled bookings on one night, which looks like a released block."]),
    6: ("~30 s",
        "Notebook 10 turns the eight inputs into 143 numeric columns. Categories are one-hot encoded, rare agents are pooled, and the two "
        "counts are log-scaled. Everything is learnt from the training period only, and 16 leakage checks pass, including a shuffled-label "
        "test that proves the label plays no part. On the right are the model settings, all fixed before I saw any result. Nothing was tuned, "
        "and I didn't rebalance the classes, because the contract adds the probabilities up, so they must stay on the real scale.",
        "The settings table.",
        "Here's how they fit the training data.",
        ["Why not tune? — Every choice made on validation inflates validation, and the later failure came from a data shift that tuning can't fix."]),
    7: ("~25 s",
        "On the training data all four models beat the flat rate by a similar margin: AUC around 0.81 against 0.58, and about 6 rooms of "
        "nightly error against 10. But these are scored on the same bookings they learnt from, so I chose nothing here.",
        "The 'Read with care' box.",
        "The real test is the validation period.",
        ["What's the Brier score? — The average squared gap between the probability and what happened. 0 is perfect; always saying 50 percent scores 0.25.",
         "What's the nightly error? — The average gap, in rooms, between expected and actual cancellations per hotel-night."]),
    8: ("~40 s",
        "On the second half of 2016, data the models never saw, they lost much of their skill. AUC fell to about 0.70, and every model "
        "predicted around 28 percent cancellations when 37 percent actually cancelled. That's about 11 rooms too few per City Hotel night. "
        "Why? In training, 12 percent of bookings had a prior cancellation, and almost all of them cancelled again. In validation that group "
        "shrank to about 1 percent, while everyone else started cancelling more. The models had learnt the wrong lesson.",
        "The City nightly bias column, then the WHY box.",
        "So how does that translate into euros?",
        ["What is City nightly bias? — Expected minus actual cancellations, averaged over the 184 City nights. Minus 11 means 11 too few expected."]),
    9: ("~45 s",
        "Each method's oversell is its expected cancellations, rounded down, minus a safety buffer. I chose each buffer as the cheapest that "
        "keeps the group within the walk limit. With one buffer for both hotels, the models look 16 percent cheaper. But that's mostly the "
        "buffer: the flat rule needs 16 rooms to protect the City Hotel, which is far too many at the Resort. Give every method its own buffer "
        "per hotel, and the flat rule drops to 1.95 million. CatBoost is then only 1.4 percent cheaper, and only in three quarters of "
        "resampled weeks. That's not a reliable difference.",
        "The two 'vs flat' columns, then 74 percent.",
        "Still, the rule I'd set in advance picks CatBoost.",
        ["Is a per-hotel buffer allowed? — The contract doesn't forbid it. It's chosen on validation like the shared one, and the flat rule gets the same freedom."]),
    10: ("~30 s",
         "My selection rule, written before any result, was the lowest validation cost within the walk limit. CatBoost won under both "
         "setups, so I froze it with buffers of 6 and 3, together with the benchmark, the flat rule with 20 and 4, before opening a single "
         "test file. I recorded the risks at the time: the edge wasn't reliable, XGBoost was nearly tied, and the models were under-predicting.",
         "The risks box.",
         "Here's what happened on the test.",
         ["Why not XGBoost, which had the best AUC? — The contract scores euros under the limit, not AUC. XGBoost would have been equally defensible."]),
    11: ("~40 s",
         "On January to August 2017, the frozen CatBoost cost 3.37 million euros against 3.21 million for the flat rule: 150 thousand more. "
         "Both stayed within the walk limit. It was slightly cheaper at the City Hotel and much dearer at the Resort, and cheaper in only 3 "
         "of 8 months. The reason is visible: it predicted 27 percent cancellations when 39 percent happened. The gap grew, and buffers set "
         "on validation couldn't follow it.",
         "The +150,459 figure and the two highlighted rows.",
         "I then tried one more thing, and I need to disclose it.",
         ["The Resort walked 11.29 under the flat rule. Isn't that a breach? — The limit is group-wide, 7.18 here. No per-hotel threshold was given, so I report it rather than judge it."]),
    12: ("~40 s",
         "After seeing run 1, I refitted CatBoost and XGBoost on training plus validation, and I'm reporting it beside run 1, not instead of "
         "it. I kept the same buffers, because there was no unseen data left to choose new ones. The refitted models expected about 5 more "
         "cancellations per City night, so they oversold more. They were cheaper, at 2.8 million, but walked 13 guests per thousand. That's "
         "over the limit, so they're rejected. Shrinking the buffer now would mean tuning on the test, which I won't do.",
         "The two red 'Breached' cells.",
         "Now the reasoning behind each role's decisions.",
         ["Isn't run 3 test-informed? — Yes, which is why it's labelled that way. It failed anyway and doesn't change the recommendation."]),
    13: ("~30 s",
         "As Client Lead, I framed the problem so every method is judged by what the revenue manager actually does: one number per "
         "hotel-night, with both errors in euros. Walks are a hard limit, not a price, because without it every method would oversell flat out "
         "and walk 22 to 82 guests per thousand. And the benchmark gets the same freedom as the model, so only the forecast differs.",
         "Rows 3 and 4.",
         "As Data Lead, the question is what the hotel knew that morning.",
         ["Who is the decision for? — The revenue manager, each night, for each hotel."]),
    14: ("~30 s",
         "As Data Lead, my rule was timing over score. Leakage can't be caught by a score, only by asking when a value is set. I flagged four "
         "uncertain columns instead of hiding the doubt, and that doubt turned out to explain the failure. I kept every row, split strictly by "
         "time, and fitted every statistic on training data only.",
         "Row 2: the risk that came true.",
         "As Model Lead, two pieces of theory drove my choices.",
         ["How would you catch leakage you didn't think of? — The timing tests first; notebook 10 also lists any near-perfect predictor for review, such as agent 236."]),
    15: ("~30 s",
         "First: the expected number of cancellations is just the sum of the booking probabilities. That means the probabilities have to be "
         "right in level, not just in order, which is why I judged the models by Brier score and log loss, and why I didn't rebalance the "
         "classes. Second: every choice made on validation inflates validation, so I fixed the settings in advance.",
         "The formula strip.",
         "Then: how many rooms to oversell.",
         ["Isn't the sum wrong if groups cancel together? — The expected value is still right; only the spread is understated, and the buffer is chosen from data, not from the spread."]),
    16: ("~40 s",
         "Here's the economics. An empty room costs about 330 to 380 euros, and a walk costs 300. So pure cost says: oversell about as many "
         "rooms as you expect to cancel, with no safety margin. The data agrees: without the limit, every method's cheapest buffer is zero, "
         "but that walks 22 to 82 per thousand. So the walk limit is what forces the buffer; the buffer is the price of keeping the brand "
         "promise. I picked the cheapest buffer inside the limit, resampled whole weeks to judge how sure I could be, and froze everything "
         "before the test.",
         "The theory box, then the evidence box.",
         "Finally, can someone actually run this?",
         ["If a walk cost 1,000 euros? — The ratio falls to about 0.25, so the cost-optimal rule already holds rooms back. I'd re-run the buffer search on validation, never on the test."]),
    17: ("~45 s, including the live run",
         "As Build Lead: one command replays the frozen choice for any nights. [Run: python src/nightly.py --from 2017-08-18 --nights 14] "
         "It checks the model's fingerprints, refuses to run if anything has changed, never reads the outcome, and prints the flat rule's "
         "recommendation first, with CatBoost alongside. A test checks that it reproduces the test-run predictions exactly. What I don't "
         "claim is a live forecast. This data is the final booking export; a real morning run needs timestamped snapshots.",
         "In the terminal, the first City row: 121 bookings, 50.4 expected, oversell 30.",
         "So, what should the hotels do?",
         ["Was anything trained just now? — No. It loads frozen files, and it would refuse to run if their hashes changed."]),
    18: ("~30 s",
         "Keep the flat rule, with a separate margin per hotel: 3.21 million euros and 7.18 walks per thousand on the test. The frozen model "
         "cost 150 thousand more, and the refitted ones broke the limit. The models failed mainly because one input shifted between periods. "
         "Next steps: get timestamped booking snapshots, confirm or drop the uncertain inputs, run the flat rule beside the revenue manager, "
         "and only then try models again, on nights nobody has looked at. Thank you.",
         "The two columns: the evidence, then the next steps.",
         "Questions.",
         ["What did the project deliver? — A fair, reproducible test showing that a per-hotel margin on the existing rule captures most of the available gain without a model, and the specific risk any future model must handle."]),
}

assert len(NOTES) == len(prs.slides), (len(NOTES), len(prs.slides))
for _n, (_time, _say, _point, _next, _asked) in NOTES.items():
    _lines = [f"[{_time}]", "", "SAY: " + _say, "", "POINT TO: " + _point, "", "NEXT: " + _next]
    if _asked:
        _lines += ["", "IF ASKED:"] + ["• " + q for q in _asked]
    prs.slides[_n - 1].notes_slide.notes_text_frame.text = "\n".join(_lines)
