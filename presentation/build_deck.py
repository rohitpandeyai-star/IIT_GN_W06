"""Build the simplified 10-slide Hotel_Overbooking_New_Deck.pptx from presentation/deck_data.json.

Run from the repository root, after `python presentation/deck_data.py`:

    python presentation/build_deck.py
"""
import datetime as dt
import json
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((Path(__file__).parent / "deck_data.json").read_text(encoding="utf-8"))

INK, PAPER, MUTED, SOFT, TINT, RULE = "14212B", "FFFFFF", "56616B", "8A949D", "F2F4F6", "D5DAE0"
BLUE, ORANGE, AQUA = "2A78D6", "EB6834", "1BAF7A"
GOOD, CRIT, WARN, PEACH = "0CA30C", "D03B3B", "B07A00", "FBE1D6"
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def rgb(h):
    return RGBColor.from_string(h)


def text(slide, x, y, w, h, paragraphs, size=14, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, italic=False, space_after=0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(paragraphs, str):
        paragraphs = [paragraphs]
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        for chunk, opt in (para if isinstance(para, list) else [(para, {})]):
            r = p.add_run()
            r.text = chunk
            f = r.font
            f.name, f.size = opt.get("font", font), Pt(opt.get("size", size))
            f.bold, f.italic = opt.get("bold", bold), opt.get("italic", italic)
            f.color.rgb = rgb(opt.get("color", color))
    return tb


def rect(slide, x, y, w, h, fill, line=None, radius=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        s.adjustments[0] = radius
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def oval(slide, x, y, d, fill):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def frame(section, title, answer, source, notes):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 13.333, 7.5, PAPER)
    text(s, 0.6, 0.45, 8, 0.28, section.upper(), size=11, color=ORANGE, bold=True)
    text(s, 0.6, 0.8, 12.1, 0.7, title, size=30, font=HEAD, bold=True)
    text(s, 0.6, 1.55, 12.1, 0.5, answer, size=17, color=MUTED)
    text(s, 0.6, 7.02, 10.8, 0.3, "Source: " + source, size=10, color=SOFT)
    text(s, 11.9, 7.02, 0.83, 0.3, str(len(prs.slides._sldIdLst)), size=10, color=SOFT, align=PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = notes
    return s


def table(slide, x, y, w, rows, col_w, row_h=0.36, size=12, highlight=None, align=None, header_fill=INK):
    gf = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
    tbl = gf.table
    for c, cw in enumerate(col_w):
        tbl.columns[c].width = Inches(cw)
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(row_h)
        for c, value in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill, color, bold = (header_fill, PAPER, True) if r == 0 else ((TINT if r % 2 == 0 else PAPER), INK, False)
            if highlight and (r, c) in highlight:
                fill, color, bold = highlight[(r, c)]
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(fill)
            p = cell.text_frame.paragraphs[0]
            cell.text_frame.word_wrap = True
            p.alignment = align[c] if align else (PP_ALIGN.LEFT if c == 0 else PP_ALIGN.RIGHT)
            run = p.add_run()
            run.text = str(value)
            run.font.name, run.font.size, run.font.bold = BODY, Pt(size), bold
            run.font.color.rgb = rgb(color)
    return tbl


def row_highlight(r, ncols, fill=PEACH, color=INK):
    return {(r, c): (fill, color, True) for c in range(ncols)}


def m(v):
    return f"€{v / 1e6:.2f}M"


def eur(v):
    return f"€{v:,.0f}"


def big(slide, x, y, w, value, label, color=INK, size=40):
    text(slide, x, y, w, 0.75, value, size=size, font=HEAD, bold=True, color=color)
    text(slide, x, y + 0.8, w, 0.7, label, size=14, color=MUTED)


L, R, C_ = PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.CENTER
DATA, CAL, PB = D["data"], D["calibration"]["decision"], D["proof"]["benchmarks"]
SEL = next(b for b in PB if b["role"] == "frozen selected policy" and b["period"] == "Proof")
SELC = next(b for b in PB if b["role"] == "frozen selected policy" and b["period"] == "Choose")
MB = next(b for b in PB if b["role"].startswith("best model"))
PH = {h["hotel"]: h for h in D["proof"]["hotels"]}
POL = {p["policy"]: p for p in D["policies"]["all"]}
CV = {r["label"]: r for r in D["cv"]}
MM = {r["method"]: r for r in D["model_matrix"]}
EV, R1, R3 = D["earlier"]["val"], D["earlier"]["proof_run1"], D["earlier"]["proof_run3"]

# ============================================================ 1. Title and answer (notebooks 11-16)
NB = D["nb"]
_R1 = {(r["hotel"], r["method"]): r for r in NB["run1"]["rows"]}
_FLAT1, _CAT1 = _R1[("group", "flat rule")], _R1[("group", "CatBoost")]
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.333, 7.5, INK)
text(s, 0.8, 0.75, 11.5, 0.3, "BUILD 2 · WEEK 6 · CANCELLATION-AWARE OVERBOOKING FOR A LISBON CITY HOTEL AND AN ALGARVE RESORT", size=12, color=ORANGE, bold=True)
text(s, 0.8, 1.35, 11.5, 1.6, "How many rooms can each hotel safely oversell tonight?", size=44, font=HEAD, bold=True, color=PAPER)
text(s, 0.8, 3.05, 11.6, 0.9, "We trained logistic regression, random forest, XGBoost and CatBoost. CatBoost won on the validation period, but on the "
     "2017 test it did not beat the client's flat rule — so keep the flat rule, with a margin per hotel.", size=19, color="C9D2DA")
for i, (value, label, color) in enumerate([(m(_FLAT1["cost (EUR)"]), f"flat rule on the 2017 test, {_FLAT1['walks per 1,000']:.2f} walks per 1,000", PAPER),
                                           (f"+{eur(_CAT1['cost (EUR)'] - _FLAT1['cost (EUR)'])}", "what CatBoost cost on top, within the walk limit", ORANGE),
                                           ("13.1", "walks per 1,000 after refitting: over the limit of 10", PAPER)]):
    x = 0.8 + i * 4.05
    text(s, x, 4.45, 3.8, 0.8, value, size=40, font=HEAD, bold=True, color=color)
    text(s, x, 5.25, 3.6, 0.6, label, size=14, color="C9D2DA")
text(s, 0.8, 6.5, 8, 0.35, "Rohit Pandey · Client, Data, Model and Build Lead", size=14, color=PAPER, bold=True)
text(s, 0.8, 6.85, 11.5, 0.3, "Evidence: notebooks 05–16 · models trained, validated and tested in notebooks 11–16 · scoring rule src/contract.py, unchanged",
     size=11, color="9AA6B1")
s.notes_slide.notes_text_frame.text = (
    "The answer first. Four models were trained on 2015-16 bookings: logistic regression, random forest, XGBoost and CatBoost. CatBoost had the lowest "
    "cost within the walk limit on the validation period (Jul-Dec 2016) and was frozen before the test. On January-August 2017 it cost "
    f"{eur(_CAT1['cost (EUR)'] - _FLAT1['cost (EUR)'])} more than the client's flat rule with a separate margin per hotel (City 20, Resort 4), "
    f"which cost {eur(_FLAT1['cost (EUR)'])} at {_FLAT1['walks per 1,000']:.2f} walks per 1,000. Refitting the models on more data made them cheaper but "
    "walked 13 guests per 1,000, over the limit, so the contract rejects them. Recommendation: keep the flat rule, with a margin per hotel.")

# ============================================================ 2. The decision
s = frame("1 · The decision", "What is decided, and what does a wrong call cost?",
          "One whole number per hotel per night: how many rooms to sell beyond capacity", "BRIEF.md · docs/EVALUATION_CONTRACT.md · src/contract.py",
          "The revenue manager sets one number per hotel-night. Too few oversold: rooms stay empty and each costs that night's average booked stay "
          "(rate × nights). Too many: guests are walked at €300 each. The brand limit is at most 10 walked guests per 1,000 arrivals over the period, "
          "group-wide; a rule that breaks it is rejected however cheap. Periods are fixed by the contract: train on arrivals before July 2016, choose "
          "settings on July–December 2016, test once on January–August 2017. The data has booking rows, not rooms, so all euros are simulated contract costs.")
cards = [("Too few oversold", "Cancelled rooms stay empty", "Cost = empty rooms × the night's average booked stay", BLUE),
         ("Too many oversold", "Guests arrive to a full hotel", "Cost = walked guests × €300", ORANGE),
         ("The hard limit", "Max 10 walks per 1,000 arrivals", "A rule that breaks it is rejected, whatever it saves", CRIT)]
for i, (head, sub, body, color) in enumerate(cards):
    x = 0.6 + i * 4.1
    rect(s, x, 2.45, 3.85, 2.5, TINT, radius=0.05)
    oval(s, x + 0.3, 2.75, 0.32, color)
    text(s, x + 0.3, 3.25, 3.3, 0.4, head, size=20, font=HEAD, bold=True)
    text(s, x + 0.3, 3.75, 3.3, 0.4, sub, size=15)
    text(s, x + 0.3, 4.2, 3.3, 0.7, body, size=14, color=MUTED)
periods = DATA["periods"]
total = sum(periods.values())
x = 0.6
for name, label, fill, fg in [("Train", "Train · fit models · before Jul 2016", "D6E6F8", INK),
                              ("Choose", "Choose · settings · Jul–Dec 2016", PEACH, INK),
                              ("Proof", "Test · Jan–Aug 2017", INK, PAPER)]:
    w = 12.15 * periods[name] / total
    rect(s, x, 5.35, w - 0.05, 0.75, fill, radius=0.12)
    text(s, x + 0.15, 5.35, w - 0.3, 0.75, [[(label, {"bold": True}), (f"\n{periods[name]:,} bookings", {})]], size=13, color=fg, anchor=MSO_ANCHOR.MIDDLE)
    x += w
text(s, 0.6, 6.3, 12.1, 0.4, "The data has booking rows, not rooms, and no record of real walks: every euro in this deck is a simulated contract cost.",
     size=13, color=MUTED, italic=True)

# ============================================================ 3. Data and inputs
s = frame("2 · The data", "What does the data say about cancellations?",
          f"{DATA['cancel_rate']:.0%} of {DATA['rows']:,} bookings cancel, far more at the City Hotel, and the rate moves with the season",
          "data/hotels.csv (Antonio, de Almeida & Nunes 2019) via src/data.py · presentation/deck_data.py",
          f"119,390 bookings for two hotels, arrivals July 2015 to August 2017, 32 columns. {DATA['cancel_rate']:.1%} cancel (including no-shows): "
          f"City Hotel {DATA['hotels']['City Hotel']['rate']:.1%} of {DATA['hotels']['City Hotel']['bookings']:,}, Resort {DATA['hotels']['Resort Hotel']['rate']:.1%} "
          f"of {DATA['hotels']['Resort Hotel']['bookings']:,}. The brief's 'one in four' is a client impression; the data says more than one in three. "
          f"Two oddities shaped later decisions: {DATA['exact_duplicate_rows']:,} exact repeated rows (kept — next slides) and Non Refund bookings that cancel "
          f"{DATA['non_refund']['rate']:.1%} of the time (so the deposit field cannot be an input).")
mr = DATA["monthly_rate"]
cd = CategoryChartData()
cd.categories = [dt.date(int(x[:4]), int(x[5:7]), 1).strftime("%b %y") if i % 3 == 0 else " " * (i + 1)
                 for i, x in enumerate(mr["months"])]
cd.add_series("City Hotel", mr["City Hotel"])
cd.add_series("Resort Hotel", mr["Resort Hotel"])
ch = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(0.5), Inches(2.3), Inches(7.4), Inches(4.5), cd).chart
ch.font.name, ch.font.size = BODY, Pt(12)
ch.font.color.rgb = rgb(MUTED)
ch.has_legend = True
ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.BOTTOM, False
va, ca = ch.value_axis, ch.category_axis
va.minimum_scale, va.maximum_scale, va.major_unit = 0, 0.8, 0.2
va.tick_labels.number_format, va.tick_labels.number_format_is_linked = "0%", False
ca.tick_labels.font.size = Pt(11)
va.major_gridlines.format.line.color.rgb = rgb("E6E9ED")
from pptx.oxml.ns import qn  # noqa: E402
_body = ca._element.txPr.find(qn("a:bodyPr"))  # keep quarterly labels horizontal
_body.set("rot", "0")
_body.set("vert", "horz")
for ax in (va, ca):
    ax.format.line.color.rgb = rgb(RULE)
ch.has_title = True
ch.chart_title.text_frame.text = "Share of bookings cancelled, by arrival month"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.color.rgb = rgb(INK)
for ser, color in zip(ch.plots[0].series, [BLUE, ORANGE]):
    ser.format.line.color.rgb = rgb(color)
    ser.format.line.width = Pt(2.5)
    ser.smooth = False
    ser.marker.style = XL_MARKER_STYLE.NONE
for i, (value, label) in enumerate([
        (f"{DATA['rows']:,}", "bookings, two hotels, Jul 2015 – Aug 2017"),
        (f"{DATA['hotels']['City Hotel']['rate']:.1%} · {DATA['hotels']['Resort Hotel']['rate']:.1%}", "cancelled at the City Hotel · at the Resort"),
        (f"{DATA['exact_duplicate_rows']:,}", "exact repeated rows (kept, see slide 5)"),
        (f"{DATA['non_refund']['rate']:.1%}", "of Non Refund bookings cancelled (see slide 4)")]):
    text(s, 8.4, 2.4 + i * 1.12, 4.35, 0.55, value, size=30, font=HEAD, bold=True, color=ORANGE if i == 3 else INK)
    text(s, 8.4, 2.95 + i * 1.12, 4.35, 0.4, label, size=13, color=MUTED)

# ============================================================ NEW A. Which columns were chosen, and why
COLS = D["columns"]
s = frame("3 · Columns", "Which columns were chosen, and why?",
          f"{COLS['counts']['input'] + COLS['counts']['provisional input']} of 44 columns: only values the hotel knows on the decision morning and that cannot change afterwards",
          "notebooks/06_forecast_column_selection.ipynb (decisions) · 07_forecast_columns_explained.ipynb (reasons) · src/features.py · tests/test_features.py",
          "Every column was judged by when the hotel knows its value, not by how well it predicts — a column that leaks the outcome predicts well on every "
          "period, so a score cannot reveal it. Four tests: is it something other than the outcome; is it known on the decision morning; will it stay the same "
          "until arrival; is it about this booking alone. Four columns pass all four. Four more are provisional: they pass except that the source does not say "
          "when they are set — company could be attached at billing, the repeat-guest link could be made at check-in, and the two prior-booking counts might "
          "include bookings cancelled later; their share with a prior cancellation fell from 11.8% in Train to 1.3% in Choose. "
          f"{COLS['counts']['exclude']} columns are excluded. lead_time and the arrival-date parts pass the tests but are not in the team's feature set. "
          "src/features.py implements exactly these 8 and a test fails if a held-back column returns.")
rows = [["Column", "Timing tests", "Status", "Why it is allowed"],
        ["hotel", "4 of 4 pass", "Input", "Fixed when booked; a booking never moves between hotels"],
        ["market_segment", "4 of 4 pass", "Input", "How the booking was sold; not a field the source says is amended"],
        ["distribution_channel", "4 of 4 pass", "Input", "The channel the booking came through; not amended"],
        ["agent", "4 of 4 pass", "Input", "The travel agency that made the booking (none = direct)"],
        ["company", "2 pass, 2 unsure", "Provisional", "A paying company might be attached later, at billing"],
        ["is_repeated_guest", "3 pass, 1 unsure", "Provisional", "When the guest profile is linked is not recorded"],
        ["previous_cancellations", "3 pass, 1 unsure", "Provisional", "May count earlier bookings cancelled after the decision morning"],
        ["previous_bookings_not_canceled", "3 pass, 1 unsure", "Provisional", "Same question as previous cancellations"]]
for c in ["hotel", "market_segment", "distribution_channel", "agent", "company", "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled"]:
    assert "no" not in COLS["tests"][c]  # every chosen column passes or is unsure; none fails
hl = {(r, 2): ((TINT if r % 2 == 0 else PAPER), WARN, True) for r in range(5, 9)}
hl.update({(r, 2): ((TINT if r % 2 == 0 else PAPER), GOOD, True) for r in range(1, 5)})
table(s, 0.6, 2.3, 8.3, rows, [2.45, 1.45, 1.05, 3.35], row_h=0.42, size=12, highlight=hl, align=[L, L, L, L])
rect(s, 9.2, 2.3, 3.55, 4.5, TINT, radius=0.04)
text(s, 9.45, 2.45, 3.1, 0.35, f"{COLS['counts']['exclude']} columns excluded", size=17, font=HEAD, bold=True)
text(s, 9.45, 2.9, 3.1, 3.8, [
    [("Change before arrival: ", {"bold": True}), ("stay length, adults/children/babies, meal, room type, special requests, booking changes", {})],
    [("Recalculated or corrected later: ", {"bold": True}), ("deposit type, price (adr), country", {})],
    [("Written by the outcome: ", {"bold": True}), ("reservation status and its date, assigned room", {})],
    [("Pass, not used: ", {"bold": True}), ("lead time, arrival year/month/week/day", {})]], size=12, color=MUTED, space_after=7)
text(s, 0.6, 6.15, 8.3, 0.7, "Tests: not the outcome · known on the decision morning · won't change before arrival · about this booking only. "
     "“Unsure” normally means exclude; these four are used provisionally and their timing must be verified.", size=11, color=MUTED)

# ============================================================ NEW B. Data cleaning choices
CL = D["cleaning"]
s = frame("4 · Cleaning", "What cleaning was done to the data?",
          "Six recorded choices; no row was removed and the source file was never changed",
          "notebooks/03_duplicate_investigation, 04_cleaning_decisions_explained, 05_apply_cleaning_decisions · docs/DECISIONS.md · presentation/deck_data.py",
          "Every cleaning choice was proposed with its evidence, approved one by one, and logged with the rows it touched (docs/DECISIONS.md). C1: 1,169 meal "
          "codes 'Undefined' became 'SC' — the source paper says both mean no meal package. C2: agent and company IDs are labels, not numbers, so they are "
          "stored as text and a blank becomes 'none' (no agent / no company). C3: 488 missing countries labelled 'unknown' (country is not an input anyway). "
          "C4: 4 missing children set to 0 with a flag. C5: all rows kept, including 31,994 exact repeats — there is no booking ID to prove a repeat is an "
          f"error, and removing them would cut the Train cancellation rate from {CL['train_rate_all_rows']:.1%} to {CL['train_rate_without_repeats']:.1%} and "
          "change the nights the contract scores; ten flag columns mark odd rows instead, and none is a model input. C6: previous_cancellations left as is "
          "and treated as provisional. The final pipeline reads the raw file and applies the same missing-value labels inside its feature step.")
rows = [["Choice", "What was done", "Rows", "Why"],
        ["C1  Meal code", "'Undefined' recoded to 'SC'", f"{CL['meal_undefined']:,}", "The source paper: both mean no meal package"],
        ["C2  Agent, company", "IDs kept as text; blank → 'none'", f"{CL['agent_missing']:,} / {CL['company_missing']:,}", "IDs are labels, not quantities; blank means none"],
        ["C3  Country", "Blank → 'unknown'", f"{CL['country_missing']:,}", "Kept visible; country is not an input"],
        ["C4  Children", "Blank → 0, with a flag", f"{CL['children_missing']:,}", f"{CL['children_zero_share_train']:.1%} of Train bookings have 0"],
        ["C5  Repeated rows", "All kept; 10 flag columns added", "0 removed", "No booking ID proves an error (see right)"],
        ["C6  Prior cancellations", "Left unchanged", "0", "Handled as a provisional input instead"]]
table(s, 0.6, 2.3, 8.3, rows, [2.1, 2.55, 1.25, 2.4], row_h=0.5, size=12, align=[L, L, R, L])
rect(s, 9.2, 2.3, 3.55, 3.5, INK, radius=0.04)
text(s, 9.45, 2.45, 3.1, 0.3, "WHY ROWS WERE KEPT", size=11, color=ORANGE, bold=True)
text(s, 9.45, 2.85, 3.1, 0.6, f"{CL['train_rate_all_rows']:.1%} → {CL['train_rate_without_repeats']:.1%}", size=28, font=HEAD, bold=True, color=PAPER)
text(s, 9.45, 3.5, 3.1, 2.2, f"Train cancellation rate if the 31,994 exact repeats were removed ({CL['train_rows_without_repeats']:,} of 49,157 Train rows "
     "left). Without a booking ID we cannot tell a true repeat from separate identical bookings, and removing them would change every night the contract scores.",
     size=12, color="C9D2DA")
text(s, 9.2, 6.0, 3.55, 0.85, "Source data never edited: cleaning happens on a copy, with every step logged and checked.", size=12, color=MUTED, italic=True)

exec((Path(__file__).parent / "deck_nb11_16.py").read_text(encoding="utf-8"))

import sys  # noqa: E402
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Hotel_Overbooking_New_Deck.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides))
