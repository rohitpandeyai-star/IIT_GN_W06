"""Restructure Hotel_Overbooking_New_Deck_updated.pptx in the order the four leads did the work, and expand it.

Every slide and element of the source deck is kept, as native, editable PowerPoint shapes, tables and charts.
What changes:
  - three north-star slides open the deck: what we are trying to find out, the north star and its guardrail,
    and one night worked through in euros;
  - order: Client Lead -> Data Lead -> Model Lead -> Build Lead -> Client Lead (docs/ROLES.md), with a roadmap slide;
  - six new column slides explain, with graphics, which columns were chosen and which were not;
  - each slide's section label names its lead, and a small lead tracker sits top right;
  - slide numbers and cross-references follow the new order;
  - facts that changed since the source was built are corrected (the nightly command now runs; 12 tests pass).
Every figure on a new slide is computed here from the repository's data, notebook outputs or contract.

Run from the repository root:
    python presentation/build_lead_deck.py [source.pptx] [out.pptx]
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import contract  # noqa: E402

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Hotel_Overbooking_New_Deck_updated.pptx"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Hotel_Overbooking_Deck_By_Lead.pptx"

INK, PAPER, MUTED, SOFT, TINT, RULE = "14212B", "FFFFFF", "56616B", "8A949D", "F2F4F6", "D5DAE0"
ORANGE, BLUE, GOOD, CRIT, WARN, PEACH = "EB6834", "2A78D6", "0CA30C", "D03B3B", "B07A00", "FBE1D6"
YES_FILL, UNSURE_FILL, NO_FILL = "DDF2DD", "F7EACB", "F7DADA"
HEAD, BODY, MONO = "Cambria", "Calibri", "Consolas"
LEADS = ["Client", "Data", "Model", "Build"]
OWNER = "Rohit Pandey"

# The new order. int = a slide of the source deck (its old number); str = a slide built here.
ORDER = [
    (1, None, []),
    ("ns_question", "CLIENT LEAD · NORTH STAR", ["Client"]),
    ("ns_metric", "CLIENT LEAD · NORTH STAR", ["Client"]),
    ("roadmap", "HOW THIS DECK RUNS", LEADS),
    (2, "CLIENT LEAD · THE DECISION", ["Client"]),
    (3, "CLIENT + DATA LEAD · THE DATA", ["Client", "Data"]),
    ("clean_recode", "DATA LEAD · CLEANING · WHAT CHANGED", ["Data"]),
    ("clean_rows", "DATA LEAD · CLEANING · ROWS KEPT", ["Data"]),
    ("col_timeline", "DATA LEAD · COLUMNS · THE TEST", ["Data"]),
    ("col_t12", "DATA LEAD · COLUMNS · TESTS T1 AND T2", ["Data"]),
    ("col_t3", "DATA LEAD · COLUMNS · TEST T3", ["Data"]),
    ("col_t4", "DATA LEAD · COLUMNS · TEST T4 AND THE PASSES", ["Data"]),
    (4, "DATA LEAD · COLUMNS · THE CHOICE", ["Data"]),
    ("col_safe", "DATA LEAD · COLUMNS · SAFE INPUTS", ["Data"]),
    ("col_prov", "DATA LEAD · COLUMNS · PROVISIONAL INPUTS", ["Data"]),
    ("col_excl", "DATA LEAD · COLUMNS · EXCLUDED", ["Data"]),
    ("col_traps", "DATA LEAD · COLUMNS · TEMPTING TRAPS", ["Data"]),
    # Slides built on notebooks/pipeline results (source slides 7, 8, 10, 11, 12; encoding, settings, one night) are left out.
    # Model Lead in the order the notebooks ran: 11 (fit) -> 12 (validation) -> 13 (per hotel, freeze) -> 14 (test) -> 15-16, then the recap.
    ("m_trained", "MODEL LEAD · MODELS TRAINED", ["Model"]),
    ("m_val_prob", "MODEL LEAD · VALIDATION · PROBABILITIES", ["Model"]),
    ("m_shared", "MODEL LEAD · VALIDATION · ONE SHARED BUFFER", ["Model"]),
    ("m_perhotel", "MODEL LEAD · VALIDATION · BUFFER PER HOTEL", ["Model"]),
    ("m_run1", "MODEL LEAD · TEST · RUN 1", ["Model"]),
    ("m_run3", "MODEL LEAD · TEST · RUNS 2 AND 3", ["Model"]),
    (9, "MODEL LEAD · SUMMARY OF THE EXPERIMENTS", ["Model"]),
    ("b_nightly", "BUILD LEAD · NIGHTLY COMMAND AND TESTS", ["Build"]),
    (13, "CLIENT LEAD · LIMITS AND NEXT STEPS", ["Client"]),
]
POS = {key: i + 1 for i, (key, _, _) in enumerate(ORDER)}
LABEL = {key: (label, active) for key, label, active in ORDER}
OLD_SECTION = re.compile(r"^\d+ · [A-Z][A-Z ]+$")


# ============================================================ data for the new slides
D = json.loads((ROOT / "presentation" / "deck_data.json").read_text(encoding="utf-8"))
TESTS, USE = D["columns"]["tests"], D["columns"]["use"]
clean = pd.read_pickle(ROOT / "data" / "hotels_clean.pkl")
train, choose, _proof = contract.split_periods(clean)
RUN1 = json.loads((ROOT / "models" / "frozen_choice.json").read_text())  # notebooks 13-14, frozen before any test result
RATES = RUN1["flat_rule_hotel_rates_from_train"]
BUFFERS = RUN1["primary"]["flat_rule_buffers"]
assert BUFFERS == {"City Hotel": 20, "Resort Hotel": 4}
TEST1 = pd.read_csv(ROOT / "data" / "models" / "test_results_primary.csv").query("hotel == 'group'").set_index("method")
FLAT1, CAT1 = TEST1.loc["flat rule"], TEST1.loc["CatBoost"]
assert round(FLAT1["cost (EUR)"]) == 3214912 and FLAT1["walks per 1,000"] == 7.18 and round(CAT1["cost (EUR)"] - FLAT1["cost (EUR)"]) == 150459

# One night under the client's flat rule with notebook 13's per-hotel buffers: floor(hotel rate x bookings) - buffer, never below 0.
nights = contract.nightly_table(choose[contract.REQUIRED], choose["hotel"].map(RATES).to_numpy())


def night(hotel, date):
    r = nights.loc[(hotel, pd.Timestamp(date))]
    k = max(np.floor(r["expected"]) - BUFFERS[hotel], 0)
    empty, walks = max(r["cancelled"] - k, 0), max(k - r["cancelled"], 0)
    return {"hotel": hotel, "date": pd.Timestamp(date), "book": int(r["book"]), "expected": r["expected"], "k": int(k),
            "cancelled": int(r["cancelled"]), "empty": int(empty), "walks": int(walks), "value": r["stay_value"],
            "cost": empty * r["stay_value"] + walks * contract.WALK_COST}


EXAMPLES = [night("City Hotel", "2016-07-04")]

prior = {name: (part["previous_cancellations"] > 0) for name, part in [("Train", train), ("Validation", choose)]}
PRIOR_SHARE = {n: float(m.mean()) for n, m in prior.items()}
assert round(PRIOR_SHARE["Train"], 3) == 0.118 and round(PRIOR_SHARE["Validation"], 3) == 0.013
DEPOSIT = clean.groupby("deposit_type")["is_canceled"].mean()
PARKING = {"With a parking space": train.loc[train["required_car_parking_spaces"] > 0, "is_canceled"].mean(),
           "Without": train.loc[train["required_car_parking_spaces"] == 0, "is_canceled"].mean()}
PARKING_N = int((train["required_car_parking_spaces"] > 0).sum())
COUNTRY = train.groupby("country")["is_canceled"].agg(["mean", "size"]).sort_values("size", ascending=False).head(5)

# Column groups for the exclusion slide, built from notebook 06's answers (no hand-kept list can drift from them).
FLAGS = [c for c in TESTS if c.startswith("flag_")]
PASS_NOT_USED = [c for c in TESTS if USE[c] == "exclude" and TESTS[c] == ["yes"] * 4]
OUTCOME = [c for c in TESTS if USE[c] == "exclude" and TESTS[c][0] == "no" and c not in FLAGS]
LATER = [c for c in ("adr", "deposit_type", "country")]
UNKNOWN = [c for c in TESTS if USE[c] == "exclude" and "no" not in TESTS[c] and TESTS[c] != ["yes"] * 4 and c not in FLAGS]
CHANGES = [c for c in TESTS if USE[c] == "exclude" and c not in FLAGS + PASS_NOT_USED + OUTCOME + LATER + UNKNOWN]
GROUPS = [("The outcome itself", "written because of the cancellation or stay", OUTCOME, CRIT),
          ("Changes until arrival", "our data holds the last value, not the morning's", CHANGES, CRIT),
          ("Corrected or recalculated later", "at check-in, during the stay, or from payments", LATER, CRIT),
          ("Timing unknown", "the source never says when it is set", UNKNOWN, WARN),
          ("Cleaning flags", "inherit the result of the column they are built from", FLAGS, SOFT),
          ("Pass, but not in the input set", "safe on timing; left out by the team's choice", PASS_NOT_USED, BLUE)]
assert sum(len(g[2]) for g in GROUPS) == 36 and len(set(sum((g[2] for g in GROUPS), []))) == 36, [len(g[2]) for g in GROUPS]
INPUTS = [c for c in TESTS if USE[c] == "input"]
PROVISIONAL = [c for c in TESTS if USE[c] == "provisional input"]
assert len(INPUTS) == 4 and len(PROVISIONAL) == 4


def top_values(col, n=3):
    vc = train[col].value_counts(normalize=True)
    return [(str(k), float(v)) for k, v in vc.head(n).items()], int(train[col].nunique())


# ============================================================ drawing helpers
def rgb(h):
    return RGBColor.from_string(h)


def text(slide, x, y, w, h, paragraphs, size=12, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         italic=False, space_after=0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate([paragraphs] if isinstance(paragraphs, str) else paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        for chunk, opt in (para if isinstance(para, list) else [(para, {})]):
            r = p.add_run()
            r.text = chunk
            r.font.name, r.font.size = opt.get("font", font), Pt(opt.get("size", size))
            r.font.bold, r.font.italic = opt.get("bold", bold), opt.get("italic", italic)
            r.font.color.rgb = rgb(opt.get("color", color))
    return tb


def box(slide, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08, line=None, label=None, size=11,
        color=INK, bold=False, align=PP_ALIGN.CENTER):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(1.25)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if label is not None:
        tf = s.text_frame
        tf.margin_left = tf.margin_right = Inches(0.06)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = align
        r = p.add_run()
        r.text = label
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = BODY, Pt(size), bold, rgb(color)
    return s


def arrow(slide, x1, y1, x2, y2, color=SOFT, width=2, dashed=False):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = rgb(color)
    line.line.width = Pt(width)
    ln = line.line._get_or_add_ln()
    if dashed:
        ln.append(ln.makeelement(qn("a:prstDash"), {"val": "dash"}))
    else:
        ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
    return line


def table(slide, x, y, rows, col_w, row_h=0.3, size=10, fills=None, colors=None, bolds=None, align=None, header=True):
    gf = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(sum(col_w)), Inches(row_h * len(rows)))
    tbl = gf.table
    tbl.first_row = header
    for c, w in enumerate(col_w):
        tbl.columns[c].width = Inches(w)
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(row_h)
        for c, value in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            head = header and r == 0
            fill = (fills or {}).get((r, c), INK) if head else (fills or {}).get((r, c), PAPER if r % 2 else TINT)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(fill)
            p = cell.text_frame.paragraphs[0]
            cell.text_frame.word_wrap = True
            p.alignment = (align or {}).get(c, PP_ALIGN.LEFT)
            run = p.add_run()
            run.text = str(value)
            run.font.name, run.font.size = BODY, Pt(size)
            run.font.bold = True if head else (bolds or {}).get((r, c), False)
            run.font.color.rgb = rgb(PAPER if head else (colors or {}).get((r, c), INK))
    return tbl


def bar_chart(slide, x, y, w, h, categories, values, highlight=None, fmt="0.0%", horizontal=True, maximum=None, size=11,
              highlight_color=ORANGE):
    cd = CategoryChartData()
    cd.categories = categories
    cd.add_series("Cancelled", values)
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    ch = slide.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    ch.has_legend = False
    ch.has_title = False
    ch.font.name, ch.font.size = BODY, Pt(size)
    ch.font.color.rgb = rgb(MUTED)
    va, ca = ch.value_axis, ch.category_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale = 0
    if maximum:
        va.maximum_scale = maximum
    ca.format.line.color.rgb = rgb(RULE)
    ca.tick_labels.font.size = Pt(size)
    if horizontal:
        ca.reverse_order = True
    plot = ch.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size, dl.font.bold = Pt(size), True
    dl.font.color.rgb = rgb(INK)
    ser = plot.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb("B9C2CB")
    for i in highlight or []:
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(highlight_color)
    return ch


def tracker(slide, active, dark=False):
    """Client · Data · Model · Build chips, top right; the slide's lead(s) highlighted."""
    x = 9.05
    for lead in LEADS:
        on = lead in active
        chip = box(slide, x, 0.36, 0.86, 0.3, ORANGE if on else ("2B3A46" if dark else TINT), radius=0.5, label=lead, size=10,
                   color=PAPER if on else ("9AA6B1" if dark else SOFT), bold=on)
        chip.name = f"Lead tracker: {lead}"
        x += 0.92


def frame(key, title, answer, source, notes):
    """A white content slide in the source deck's layout, numbered by its place in ORDER."""
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, 13.333, 7.5, PAPER, shape=MSO_SHAPE.RECTANGLE)
    label, active = LABEL[key]
    text(s, 0.6, 0.45, 8.3, 0.28, label, size=11, color=ORANGE, bold=True)
    text(s, 0.6, 0.8, 12.1, 0.7, title, size=30, font=HEAD, bold=True)
    text(s, 0.6, 1.55, 12.1, 0.5, answer, size=17, color=MUTED)
    text(s, 0.6, 7.02, 10.8, 0.3, "Source: " + source, size=10, color=SOFT)
    text(s, 11.9, 7.02, 0.83, 0.3, str(POS[key]), size=10, color=SOFT, align=PP_ALIGN.RIGHT)
    tracker(s, active)
    s.notes_slide.notes_text_frame.text = notes
    NEW[key] = prs.slides._sldIdLst[-1]
    return s


def set_text(shape, new):
    """Replace a text box's text, keeping the first run's formatting."""
    p0 = shape.text_frame.paragraphs[0]
    runs = p0.runs
    runs[0].text = new
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for p in shape.text_frame.paragraphs[1:]:
        p._p.getparent().remove(p._p)


def replace_in_runs(slide, old, new):
    n = 0
    frames = [sh.text_frame for sh in slide.shapes if sh.has_text_frame]
    if slide.has_notes_slide:
        frames.append(slide.notes_slide.notes_text_frame)
    for tf in frames:
        for p in tf.paragraphs:
            for r in p.runs:
                if old in r.text:
                    r.text = r.text.replace(old, new)
                    n += 1
    return n


def find(slide, predicate):
    hits = [sh for sh in slide.shapes if sh.has_text_frame and predicate(sh.text_frame.text.strip())]
    assert len(hits) == 1, [h.text_frame.text for h in hits]
    return hits[0]


def eur(v):
    return f"€{v:,.0f}"


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


def slide_range(keys):
    nums = sorted(POS[k] for k in keys)
    runs, start = [], nums[0]
    for a, b in zip(nums, nums[1:] + [None]):
        if b != a + 1:
            runs.append(f"{start}" if start == a else f"{start}–{a}")
            start = b
    return ("Slide " if len(nums) == 1 else "Slides ") + ", ".join(runs)


prs = Presentation(SRC)
assert len(prs.slides) == 13, len(prs.slides)
BLANK = next(l for l in prs.slide_layouts if l.name == "Blank")
OLD = {i + 1: s for i, s in enumerate(prs.slides)}
OLD_IDS = {i + 1: el for i, el in enumerate(list(prs.slides._sldIdLst))}
NEW = {}

# ============================================================ 1. Source slides: labels, tracker, numbers, references, fixes
for key, label, active in ORDER:
    if not isinstance(key, int) or label is None:
        continue
    s = OLD[key]
    set_text(find(s, lambda t: bool(OLD_SECTION.match(t))), label)
    if key != 13:  # the dark closing slide carries no number box in the source
        set_text(find(s, lambda t: t == str(key)), str(POS[key]))
    tracker(s, active, dark=(key == 13))

assert replace_in_runs(OLD[3], "(see slide 4)", f"(see slide {POS['col_traps']})") == 1        # Non Refund -> the traps slide
assert replace_in_runs(OLD[3], "(kept, see slide 5)", f"(kept, see slide {POS['clean_rows']})") == 1      # repeats -> cleaning

# Source slide 9 becomes the recap after the detail slides: one name for the period ("Jul–Dec 2016"), and a subtitle that
# matches the detail (with a buffer per hotel only XGBoost and CatBoost were cheaper, by 1.0-1.4%).
recap = OLD[9]
set_text(find(recap, lambda t: t == "What did XGBoost and CatBoost show?"), "What did the experiments show, from validation to test?")
set_text(find(recap, lambda t: t.startswith("On Choose they looked")),
         "On Jul–Dec 2016 only XGBoost and CatBoost beat the flat rule with a buffer per hotel, by 1.0–1.4%; "
         "on the 2017 test neither was cheaper within the walk limit")
set_text(find(recap, lambda t: t.startswith("Run 3 · decided after run 1")), "Run 3 · decided after run 1, refitted on Train + Jul–Dec 2016")
assert replace_in_runs(recap, "Every row met the walk limit on Choose.", "Costs on Jul–Dec 2016; every row met the walk limit.") == 1
_heads = {"Choose AUC": "AUC, Jul–Dec 2016", "Choose cost, one buffer": "Cost, one buffer", "Choose cost, buffer per hotel": "Cost, buffer per hotel"}
_done = 0
for sh in recap.shapes:
    if sh.has_table:
        for cell in sh.table.rows[0].cells:
            if cell.text in _heads:
                runs = cell.text_frame.paragraphs[0].runs
                runs[0].text = _heads[cell.text]
                for r in runs[1:]:
                    r._r.getparent().remove(r._r)
                _done += 1
assert _done == 3, _done
recap.notes_slide.notes_text_frame.text = (
    "This recaps the Model Lead's work from notebooks 11 to 16. Four models and the flat rule were fitted on Train and scored on "
    "July to December 2016, each with its own buffer (rule: floor of expected cancellations minus the buffer). With one buffer for "
    "both hotels every model beat the flat rule, but mostly because the flat rule needed a large shared buffer. Giving every method "
    "a separate buffer per hotel, only XGBoost and CatBoost were cheaper, by 1.0 and 1.4 percent, and CatBoost was frozen. Test run "
    "1, frozen before any test result: CatBoost cost €3,365,371 against €3,214,912 for the per-hotel flat rule, €150,459 more, both "
    "within the limit. Run 3 was decided after seeing run 1: CatBoost and XGBoost refitted on Train plus July to December 2016, "
    "buffers unchanged. They cost less but walked about 13 per 1,000, breaking the limit, so the contract rejects them. All runs "
    "are reported.")

# Title slide: the headline now comes from notebooks 12-16 (run 1), not from notebooks/pipeline.
cover = OLD[1]
set_text(find(cover, lambda t: t.startswith("Keep the client's flat rule")),
         f"Keep the client's flat rule, with a margin per hotel (City {BUFFERS['City Hotel']}, Resort {BUFFERS['Resort Hotel']}). "
         "CatBoost, the model chosen on Jul–Dec 2016, cost more on the 2017 test; refitted models that cost less broke the walk limit.")
set_text(find(cover, lambda t: t == "€3.94M"), f"€{FLAT1['cost (EUR)'] / 1e6:.2f}M")
set_text(find(cover, lambda t: t.startswith("cost on the 2017 test")), "flat rule's cost on the 2017 test period (Jan–Aug)")
set_text(find(cover, lambda t: t == "6.21"), f"{FLAT1['walks per 1,000']:.2f}")
set_text(find(cover, lambda t: t == "15 + 5"), f"+€{(CAT1['cost (EUR)'] - FLAT1['cost (EUR)']) / 1e3:.0f}k")
set_text(find(cover, lambda t: t.startswith("probability models · overbooking")), "CatBoost's extra cost against the flat rule (run 1)")
set_text(find(cover, lambda t: t.startswith("Evidence: notebooks/pipeline")),
         "Evidence: notebooks 10–16 · data/models/test_results_primary.csv · scoring rule src/contract.py, unchanged")
cover.notes_slide.notes_text_frame.text = (
    f"The answer first. Keep the client's own flat rule: each hotel's cancellation rate times the night's bookings, rounded down, "
    f"minus a margin set on Jul–Dec 2016 for each hotel (City {BUFFERS['City Hotel']}, Resort {BUFFERS['Resort Hotel']}). On the 2017 "
    f"test period it cost {eur(FLAT1['cost (EUR)'])} under the client's contract and walked {FLAT1['walks per 1,000']:.2f} guests per "
    f"1,000 arrivals, inside the limit of 10. Four probability models were fitted on Train (logistic regression, random forest, XGBoost, "
    f"CatBoost); CatBoost was the cheapest on Jul–Dec 2016 and was frozen before any test result. On the 2017 test it cost "
    f"{eur(CAT1['cost (EUR)'])}, {eur(CAT1['cost (EUR)'] - FLAT1['cost (EUR)'])} more than the flat rule. Models refitted after that "
    f"result cost less but walked about 13 per 1,000, breaking the limit. Slide {POS[9]} reports every run.")

# ============================================================ 2. North star 1: what are we trying to find out?
s = frame("ns_question", "What are we trying to find out?",
          "Can a cancellation forecast set each night's oversell more cheaply than the flat rule, without walking more guests?",
          "BRIEF.md · docs/CHARTER.md · docs/EVALUATION_CONTRACT.md",
          "Start with the client's own words. Every morning the revenue manager decides, for each hotel and each of the next 14 nights, how "
          "many rooms to sell beyond capacity. Today that number comes from a flat rule: the hotel's average cancellation rate times the "
          "night's bookings, less a safety margin. So we have to find out three things: how many of tonight's bookings will cancel; how to "
          "turn that into one whole number of rooms; and whether that number is better than today's rule, in euros, without walking more "
          "guests than the brand allows. The right-hand side is one real morning, scored with the flat rule and the City Hotel's 20-room margin.")
box(s, 0.6, 2.3, 6.2, 1.55, INK, radius=0.05)
text(s, 0.85, 2.42, 5.8, 0.28, "THE CLIENT'S QUESTION", size=11, color=ORANGE, bold=True)
text(s, 0.85, 2.75, 5.75, 1.05, "“For every arrival night at each hotel, tell us how many rooms beyond capacity we can keep selling, so "
     "that cancellations stop leaving rooms empty, without walking more than one guest in a hundred.”", size=13.5, color=PAPER,
     font=HEAD, italic=True)
for i, (head, body) in enumerate([("How many of tonight's bookings will cancel?", "A forecast for each hotel and night, built from what is known that morning"),
                                  ("How many rooms should we oversell?", "Turn the forecast into one whole number the revenue manager can act on"),
                                  ("Is that better than today's flat rule?", "Compare euros on the same nights, with walks inside the brand limit")]):
    y = 4.05 + i * 0.92
    box(s, 0.6, y, 0.5, 0.5, ORANGE, shape=MSO_SHAPE.OVAL, label=str(i + 1), size=14, color=PAPER, bold=True)
    text(s, 1.3, y - 0.02, 5.5, 0.32, head, size=15, font=HEAD, bold=True)
    text(s, 1.3, y + 0.33, 5.5, 0.5, body, size=12, color=MUTED)
e = EXAMPLES[0]
assert e["walks"] == 0 and e["k"] > 0  # the 'Result' line below says no one walked
text(s, 7.35, 2.3, 5.4, 0.3, f"ONE MORNING · {e['hotel'].upper()} · ARRIVALS ON {e['date']:%a %d %b %Y}".upper(), size=11, color=ORANGE, bold=True)
steps = [("On the books", f"{e['book']} bookings due to arrive"),
         ("Expected to cancel", f"{e['book']} × {RATES[e['hotel']]:.1%} = {e['expected']:.1f}, rounded down to {int(np.floor(e['expected']))}"),
         ("Decision", f"oversell {e['k']} rooms  ({int(np.floor(e['expected']))} − {BUFFERS[e['hotel']]} safety rooms)"),
         ("What happened", f"{e['cancelled']} cancelled"),
         ("Result", f"{e['empty']} rooms empty × {eur(e['value'])} = {eur(e['cost'])}; no one walked")]
for i, (head, body) in enumerate(steps):
    y = 2.72 + i * 0.84
    last = i == len(steps) - 1
    box(s, 7.35, y, 5.4, 0.64, PEACH if last else TINT, radius=0.12)
    text(s, 7.55, y + 0.08, 1.75, 0.5, head, size=12, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 9.3, y + 0.08, 3.35, 0.5, body, size=12, color=INK if last else MUTED, anchor=MSO_ANCHOR.MIDDLE)
    if not last:
        arrow(s, 10.05, y + 0.65, 10.05, y + 0.83)

# ============================================================ 3. North star 2: the metric and its guardrail
s = frame("ns_metric", "What is our north star, and what guards it?",
          "Lowest total euros against the flat rule on the same nights, accepted only if walks stay at or below 10 per 1,000",
          "docs/CHARTER.md §3 · src/contract.py (night_cost, WALK_COST, WALK_CEILING) · BRIEF.md",
          "Our north star is one number: the total cost in euros over the period, set beside the flat rule's cost on exactly the same "
          "hotel-nights. Each night's cost has two parts: empty rooms, each priced at that night's average booked stay, and walked guests "
          "at 300 euros each. The guardrail sits beside it, not inside it: at most 10 walked guests per 1,000 arrivals, across the group. "
          "A rule over that line is rejected however cheap it is. The table gives each metric's numerator, denominator, window and "
          "exclusions, so there is no ambiguity about what we measured. We always report empty rooms and walks next to the euros, and each "
          "hotel separately, so a group total cannot hide a bad result at one property.")
box(s, 0.6, 2.35, 5.6, 1.15, INK, radius=0.06)
text(s, 0.85, 2.45, 5.2, 0.28, "NORTH STAR", size=11, color=ORANGE, bold=True)
text(s, 0.85, 2.75, 5.2, 0.4, "Total contract cost, €", size=20, font=HEAD, bold=True, color=PAPER)
text(s, 0.85, 3.15, 5.2, 0.3, "lower than the flat rule's, on the same hotel-nights", size=12, color="C9D2DA")
arrow(s, 2.0, 3.5, 2.0, 3.95)
arrow(s, 4.8, 3.5, 4.8, 3.95)
for x, head, body, sub in [(0.6, "Empty rooms × stay value", "too few oversold", "stay value = the night's average adr × nights"),
                           (3.45, "Walked guests × €300", "too many oversold", "€300 is the client's own figure")]:
    box(s, x, 3.95, 2.75, 1.25, TINT, radius=0.06)
    text(s, x + 0.18, 4.05, 2.45, 0.32, body.upper(), size=10, color=ORANGE, bold=True)
    text(s, x + 0.18, 4.33, 2.45, 0.4, head, size=14, font=HEAD, bold=True)
    text(s, x + 0.18, 4.75, 2.45, 0.42, sub, size=10.5, color=MUTED)
box(s, 0.6, 5.45, 5.6, 1.3, PAPER, radius=0.06, line=CRIT)
text(s, 0.85, 5.55, 5.2, 0.28, "GUARDRAIL", size=11, color=CRIT, bold=True)
text(s, 0.85, 5.83, 5.2, 0.4, f"≤ {contract.WALK_CEILING:.0f} walks per 1,000 arrivals", size=18, font=HEAD, bold=True)
text(s, 0.85, 6.25, 5.2, 0.45, "group-wide; a rule over it is rejected, whatever it saves", size=12, color=MUTED)
rows = [["", "North star", "Guardrail"],
        ["Numerator", "Σ night cost: empty rooms × stay value + walks × €300", "walked guests"],
        ["Denominator", "none: a total, set against the flat rule's total", "arrivals (bookings that did not cancel) ÷ 1,000"],
        ["Window", "chosen on Jul–Dec 2016; proved on Jan–Aug 2017", "checked on Jul–Dec 2016; reported on 2017"],
        ["Exclusions", "none: every hotel-night with bookings is scored", "none; per-hotel rates reported, not judged"],
        ["Shown with", "empty rooms, walks, each hotel separately", "each hotel separately"]]
table(s, 6.55, 2.35, rows, [1.35, 2.6, 2.25], row_h=0.73, size=11, bolds={(r, 0): True for r in range(1, 6)})

# ============================================================ 5. Roadmap: who did what, in which order
s = frame("roadmap", "In what order was the work done, and by which lead?",
          "Four roles in turn: frame the decision, prepare the data, choose the rule, build it, close with the client",
          "docs/ROLES.md · docs/CHARTER.md",
          "This deck follows the order in which the work was done. As Client Lead I set the north star and framed the decision: one number "
          "per hotel-night, the two costs and the walk limit. As Data Lead I profiled and cleaned the data, chose the columns by when the "
          "hotel knows them. As Model Lead I fitted four probability models on Train, chose each method's buffers on the second half of "
          "2016 within the walk limit, froze the choice, and tested it on 2017. As Build Lead I turned the frozen choice into one nightly "
          "command, with fingerprint checks and automated tests. And as "
          "Client Lead again I close with the limits and next steps. All four roles were mine.")
client1 = [k for k, _, a in ORDER if a == ["Client"] and k != 13] + [3]
data = [k for k, _, a in ORDER if "Data" in a and k != "roadmap"]
model = [k for k, _, a in ORDER if "Model" in a and k != "roadmap"]
stages = [("CLIENT LEAD", "What is decided, for whom, at what cost per wrong call?",
           ["North star and guardrail", "The decision and its two costs", "Check the brief's numbers"], slide_range(client1)),
          ("DATA LEAD", "What did the hotel know on the decision morning?",
           ["Profile and clean the data", "Choose columns by timing"], slide_range(data)),
          ("MODEL LEAD", "How many will cancel tonight, and how sure are we?",
           ["Fit four models on Train", "Score them on Jul–Dec 2016", "Choose buffers within the limit", "Freeze, then test on 2017"],
           slide_range(model)),
          ("BUILD LEAD", "What could the revenue manager use tomorrow morning?",
           ["The nightly command", "Fingerprint checks", "Automated tests"], slide_range(["b_nightly"])),
          ("CLIENT LEAD", "What is the honest range, and what comes next?", ["Limits of the evidence", "Proposed next steps"],
           slide_range([13]))]
w, gap, y0, h = 2.19, 0.3, 2.35, 4.15
for i, (lead, question, tasks, ref) in enumerate(stages):
    x = 0.6 + i * (w + gap)
    dark = i in (0, 4)
    card = box(s, x, y0, w, h, INK if dark else TINT, radius=0.05)
    card.name = f"Stage {i + 1}: {lead.title()}"
    text(s, x + 0.18, y0 + 0.18, w - 0.36, 0.3, f"{i + 1} · {lead}", size=11, color=ORANGE, bold=True)
    text(s, x + 0.18, y0 + 0.52, w - 0.36, 1.1, question, size=13, font=HEAD, bold=True, color=PAPER if dark else INK)
    text(s, x + 0.18, y0 + 1.6, w - 0.36, 1.9, [[("• " + t, {})] for t in tasks], size=11, color="C9D2DA" if dark else MUTED)
    text(s, x + 0.18, y0 + h - 0.45, w - 0.36, 0.3, ref, size=11, color=ORANGE, bold=True)
    if i < len(stages) - 1:
        arrow(s, x + w + 0.04, y0 + h / 2, x + w + gap - 0.04, y0 + h / 2)
shared = [POS[k] for k, _, a in ORDER if len(a) == 2]
text(s, 0.6, 6.68, 12.15, 0.3, f"All four roles were held by {OWNER} (docs/CHARTER.md). The questions are each role's own, from docs/ROLES.md; "
     f"slide {shared[0]} is shared by the Client and Data Leads." if len(shared) == 1 else f"slides {", ".join(map(str, shared))} are shared by two leads.", size=11, color=MUTED)

# ============================================================ 6. Columns 1: when does the hotel know each value?
s = frame("col_timeline", "When does the hotel know each value?",
          "A column is usable only if its value exists on the decision morning and does not change before arrival",
          "notebooks/06_forecast_column_selection.ipynb (four tests) · Antonio, de Almeida & Nunes (2019) column definitions",
          "Every forecast is made on a morning M, for bookings arriving up to 14 nights later. So the only fair question about a column is: "
          "did the hotel have this value that morning, and is the value in our file still the value it had then? Read the four bands from "
          "the top. Some values are fixed the moment the booking is made: the hotel, how it was sold, the agent, the lead time. Some exist "
          "that morning but keep changing until arrival: stay length, guests, meal, room type. Some are only set or corrected at check-in "
          "or afterwards: nationality, the price actually charged, the deposit, the room assigned, the final status. And for some, the "
          "source never says when they are set. Only the first band is safe; the last band is used provisionally, with its doubt on record.")
X0, XB, XM, XA, XO, X1 = 4.0, 4.25, 6.55, 9.55, 12.15, 12.6
arrow(s, X0, 2.62, X1, 2.62, color=INK, width=2.5)
for x, lab in [(XB, "Booking made"), (XM, "Decision morning M"), (XA, "Arrival · check-in"), (XO, "Outcome recorded")]:
    box(s, x - 0.09, 2.53, 0.18, 0.18, ORANGE if x == XM else INK, shape=MSO_SHAPE.OVAL)
    text(s, x - 1.0, 2.2, 2.0, 0.28, lab, size=11, bold=True, color=ORANGE if x == XM else INK, align=PP_ALIGN.CENTER)
text(s, XM - 1.2, 2.82, 2.4, 0.25, "the forecast is made here", size=10, color=ORANGE, align=PP_ALIGN.CENTER, italic=True)
arrow(s, XM, 3.1, XM, 6.85, color=ORANGE, width=1.5, dashed=True)
bands = [("Fixed when the booking is made", "→ input (4) or safe but unused (6)", GOOD, [(XB, X1, "set once, never changes")],
          "hotel · market_segment · distribution_channel · agent · lead_time · arrival date"),
         ("Known on M, but changes until arrival", "→ exclude (11)", CRIT, [(XB, XA, "can still be amended")],
          "stay length · adults, children, babies · meal · reserved room · special requests · booking changes"),
         ("Set or corrected at check-in or later", "→ exclude (6)", CRIT, [(XA, X1, "set here")],
          "country · adr (price) · deposit type · assigned room · reservation status and its date"),
         ("When it is set is not recorded", "→ provisional (4) or exclude (3)", WARN, [(XB, X1, "?")],
          "company · is_repeated_guest · previous cancellations · previous bookings · waiting list · customer type · parking")]
for i, (head, verdict, color, segs, cols) in enumerate(bands):
    y = 3.2 + i * 0.93
    text(s, 0.6, y, 3.25, 0.3, head, size=12.5, bold=True)
    text(s, 0.6, y + 0.32, 3.25, 0.3, verdict, size=11, bold=True, color=color)
    for a, b, lab in segs:
        box(s, a, y + 0.02, b - a, 0.3, color, radius=0.5, label=lab, size=10, color=PAPER, bold=True)
    tb = text(s, X0, y + 0.4, X1 - X0, 0.3, cols, size=10.5, color=MUTED, font=BODY)
    tb.fill.solid()
    tb.fill.fore_color.rgb = rgb(PAPER)

# ============================================================ 7. Columns 2: the four tests, one group of columns per slide
# Each column is placed by its deciding test: the first test it does not clearly pass ("no" or "unsure"); all-yes columns go last.
NONFLAG = [c for c in TESTS if c not in FLAGS]
assert len(NONFLAG) == 34


def deciding(c):
    for i, a in enumerate(TESTS[c]):
        if a != "yes":
            return i + 1
    return 0


BY_TEST = {t: [c for c in NONFLAG if deciding(c) == t] for t in range(5)}
assert {t: len(v) for t, v in BY_TEST.items()} == {0: 10, 1: 5, 2: 6, 3: 13, 4: 0}, {t: len(v) for t, v in BY_TEST.items()}
rank = {"input": 0, "provisional input": 1}
mark = {"yes": ("✓", YES_FILL, GOOD), "unsure": ("?", UNSURE_FILL, WARN), "no": ("✗", NO_FILL, CRIT)}
verdict = {"input": ("Input", GOOD), "provisional input": ("Provisional", WARN)}
TEST_NAMES = {1: "Not the outcome", 2: "Known on morning M", 3: "Unchanged until arrival", 4: "This booking only"}


def test_table(s, cols, focus, x=0.6, y=2.3, width_col=2.75):
    cols = sorted(cols, key=lambda c: (rank.get(USE[c], 2 if c in PASS_NOT_USED else 3), NONFLAG.index(c)))
    rows = [["Column", "T1", "T2", "T3", "T4", "Use"]]
    fills = {(0, t): ORANGE for t in focus}
    colors, bolds = {}, {}
    for r, c in enumerate(cols, 1):
        use = verdict.get(USE[c], ("Not used", BLUE) if c in PASS_NOT_USED else ("Excluded", SOFT))
        rows.append([c] + [mark[a][0] for a in TESTS[c]] + [use[0]])
        for j, a in enumerate(TESTS[c], 1):
            fills[(r, j)], colors[(r, j)], bolds[(r, j)] = mark[a][1], mark[a][2], True
        colors[(r, 5)], bolds[(r, 5)], bolds[(r, 0)] = use[1], USE[c] != "exclude", USE[c] != "exclude"
    row_h = min(0.42, 4.45 / len(rows))
    table(s, x, y, rows, [width_col, 0.5, 0.5, 0.5, 0.5, 1.3], row_h=row_h, size=11, fills=fills, colors=colors, bolds=bolds,
          align={j: PP_ALIGN.CENTER for j in range(1, 5)})
    return len(cols)


def reason_card(s, x, y, w, test, question, reason, examples, verdict_line, color):
    """A card whose height follows its text; returns its bottom edge."""
    inner = w - 0.5
    lr = -(-len(reason) // int(inner * 13))
    le = -(-len(examples) // int(inner * 15))
    yr = y + 0.8
    ye = yr + lr * 0.21 + 0.1
    yv = ye + le * 0.18 + 0.08
    h = yv + 0.34 - y
    box(s, x, y, w, h, TINT, radius=0.04)
    box(s, x, y, 0.1, h, color, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.3, y + 0.14, inner, 0.28, f"T{test} · {TEST_NAMES[test].upper()}" if test else "PASSED ALL FOUR", size=11, color=ORANGE, bold=True)
    text(s, x + 0.3, y + 0.42, inner, 0.35, question, size=15, font=HEAD, bold=True)
    text(s, x + 0.3, yr, inner, lr * 0.21, reason, size=12, color=INK)
    text(s, x + 0.3, ye, inner, le * 0.18, examples, size=10.5, color=MUTED)
    text(s, x + 0.3, yv, inner, 0.28, verdict_line, size=11, bold=True, color=color)
    return y + h


LEGEND = [("✓ yes   ", {"color": GOOD, "bold": True}), ("? unsure   ", {"color": WARN, "bold": True}), ("✗ no     ", {"color": CRIT, "bold": True}),
          ("each column sits on the slide of the first test it does not clearly pass; orange headers mark this slide's tests", {"color": MUTED})]

s = frame("col_t12", "Which columns are the outcome, or not known in time?",
          f"T1 and T2 decide {len(BY_TEST[1]) + len(BY_TEST[2])} columns: written because of the outcome, or only learned at check-in or later",
          "notebooks/06_forecast_column_selection.ipynb (test answers) · notebooks/07_forecast_columns_explained.ipynb (reasons) · Antonio, de Almeida & Nunes (2019)",
          "The first two tests catch the most dangerous columns. T1 asks whether a value is the outcome, or written because of it. The "
          "reservation status and its date are the answer itself; the room assigned is set at arrival, partly by the overbooking decision "
          "we are forecasting; price and deposit are built from transactions up to arrival or cancellation, so they are unsure at best. "
          "T2 asks whether the hotel has the value on the decision morning. Nationality is often corrected at check-in, which cancelled "
          "bookings never reach; booking changes keep counting until arrival; and for parking, the waiting list, company and customer type "
          "the source never says when the value is set. Company is the one exception kept: it passes everything else, so the team used it "
          "provisionally, with the doubt on record.")
test_table(s, BY_TEST[1] + BY_TEST[2], focus=[1, 2])
bottom = reason_card(s, 7.0, 2.3, 5.75, 1, "Is it the outcome, or written because of it?",
            "Recorded because the booking cancelled, no-showed or stayed, so it hands the model the answer.",
            "status and its date · assigned room · price and deposit (posted up to the outcome)", "→ never an input", CRIT)
bottom = reason_card(s, 7.0, bottom + 0.15, 5.75, 2, "Does the hotel have it on the decision morning?",
            "Learned at check-in or later, or its timing is not recorded; a cancelled booking never reaches check-in.",
            "country (corrected at check-in) · booking changes · parking · waiting list · company · customer type", "→ excluded; company used provisionally", WARN)
assert bottom <= 6.8, bottom
text(s, 0.6, 6.76, 12.15, 0.24, [LEGEND], size=11)

s = frame("col_t3", "Which columns change between the morning and arrival?",
          f"T3 decides {len(BY_TEST[3])} columns: our file holds each value's last version, and a cancelled booking stops changing when it cancels",
          "notebooks/06_forecast_column_selection.ipynb (test answers) · notebooks/07_forecast_columns_explained.ipynb (reasons) · Antonio, de Almeida & Nunes (2019)",
          "T3 is the test that matters most in this dataset. The paper says each value was taken from the latest entry in the booking's "
          "change log, on the day before arrival. A booking that is kept keeps changing until check-in: guests add a night, a child, a meal "
          "plan or a special request. A booking that cancels stops changing at that moment. So for every amendable field the value in our "
          "file depends on whether the booking cancelled, and a model would learn the outcome through the back door. Stay length, guests, "
          "meal, room type and special requests fail outright. The three guest-history columns are unsure rather than failing: their counts "
          "may include earlier bookings cancelled after the decision morning. The team used them provisionally, and one of them, previous "
          "cancellations, turned out to shift sharply between periods.")
test_table(s, BY_TEST[3], focus=[3])
bottom = reason_card(s, 7.0, 2.3, 5.75, 3, "Is it the value the hotel had that morning?",
            "The file keeps each booking's last value from its change log. Kept bookings keep changing until check-in; cancelled ones freeze at cancellation. The value differs because of the outcome.",
            "stay length · adults, children, babies · meal · reserved room · special requests (and nights, guests built from them)",
            "→ firm 'no': excluded", CRIT)
bottom = reason_card(s, 7.0, bottom + 0.15, 5.75, 3, "Unsure: counts of earlier bookings",
            "Earlier bookings counted here could be cancelled after the morning.",
            "is_repeated_guest · previous cancellations · previous bookings", "→ used provisionally, doubt on record", WARN)
assert bottom <= 6.8, bottom
text(s, 0.6, 6.76, 12.15, 0.24, [LEGEND], size=11)

s = frame("col_t4", "Which columns pass all four tests, and what does T4 add?",
          "T4 rules out anything built by comparing rows; the 10 columns that pass every test were all set once, at booking",
          "notebooks/06_forecast_column_selection.ipynb (test answers) · src/features.py (the 8 inputs) · notebooks/05_apply_cleaning_decisions.ipynb (flags)",
          "The last test asks whether a value describes this booking alone. A value built by comparing a row with every other row in the "
          "file would see bookings made after the decision morning, including the test period. Among the source columns none fails it "
          "outright; customer type is unsure, because Transient-party and Group depend on links to other bookings, but it already failed "
          "earlier. The one clear failure is a cleaning flag, the identical-group flag, which compares every row with every other. These "
          "ten columns pass all four tests. They all describe how and when the booking was made, set once and never changed. Four are the "
          "model's inputs. Lead time and the arrival-date parts were left out of the team's input set; they are the first candidates to "
          "add, tested on validation only.")
test_table(s, BY_TEST[0], focus=[4])
bottom = reason_card(s, 7.0, 2.3, 5.75, 4, "Is it about this booking alone?",
            "A value built by comparing rows sees bookings made after the morning, including the test period.",
            "fails: the identical-group cleaning flag · unsure: customer type (links to other bookings)", "→ every column shown here: yes", GOOD)
bottom = reason_card(s, 7.0, bottom + 0.15, 5.75, 0, "Set once, when the booking is made",
            "Which hotel, how it was sold, through which channel and agent, how far ahead and for which night: none can change later.",
            "inputs: hotel · market_segment · distribution_channel · agent", "→ 4 inputs; 6 safe but not in the input set", BLUE)
assert bottom <= 6.8, bottom
text(s, 0.6, 6.76, 12.15, 0.24, [LEGEND[:3] + [("the 10 cleaning flags inherit their source column's answers; all are excluded", {"color": MUTED})]], size=11)

# ============================================================ 8. Columns 4: the four safe inputs
s = frame("col_safe", "What do the four safe inputs tell the model?",
          "Each says how, and through whom, the booking was made — facts set once, when the booking is created",
          "notebooks/06 and 07 (reasons) · data/splits/train.csv (shares, Train) · notebooks/10_preprocessing_leakage_checked.ipynb (encoding)",
          "The four inputs that pass every test all describe the act of booking. Which hotel; which market segment sold it, such as online "
          "travel agents or groups; which distribution channel it came through; and which travel agency made it. None of them is among the "
          "attributes the source paper says guests change, and the change counter does not count them. The bars show the most common "
          "values in the training period, just so you can see what the model actually receives. All four are categories, so they are "
          "one-hot encoded, with rare agents pooled. The one open check is the hotel's change log, to confirm segments and agents are "
          "never reassigned.")
safe = [("hotel", "Which property", "Fixed at booking; a booking never moves between hotels", "one 0/1 column"),
        ("market_segment", "How it was sold", "Not among the attributes guests change", "one-hot"),
        ("distribution_channel", "Which channel it came through", "A fact of how the booking was created", "one-hot"),
        ("agent", "Which travel agency made it", "Set by the act of booking; 'none' = booked direct", "one-hot; < 30 bookings pooled")]
for i, (col, what, why, enc) in enumerate(safe):
    x = 0.6 + i * 3.08
    box(s, x, 2.3, 2.88, 4.5, TINT, radius=0.04)
    box(s, x, 2.3, 2.88, 0.1, GOOD, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.2, 2.55, 2.5, 0.32, col, size=14, font=MONO, bold=True)
    text(s, x + 0.2, 2.92, 2.5, 0.3, what, size=12.5, color=MUTED)
    vals, n_unique = top_values(col)
    text(s, x + 0.2, 3.35, 2.5, 0.25, f"MOST COMMON IN TRAIN · {n_unique} values", size=9.5, color=ORANGE, bold=True)
    for j, (v, share) in enumerate(vals):
        y = 3.65 + j * 0.42
        text(s, x + 0.2, y, 1.25, 0.3, v if col != "agent" else (f"agent {v}" if v != "none" else "none (direct)"), size=11)
        box(s, x + 1.45, y + 0.05, 0.75 * share / vals[0][1], 0.2, "B9C2CB", shape=MSO_SHAPE.RECTANGLE)
        text(s, x + 1.45, y, 1.25, 0.3, pct(share, 0), size=10.5, bold=True, align=PP_ALIGN.RIGHT)
    text(s, x + 0.2, 4.98, 2.5, 0.25, "WHY IT IS SAFE", size=9.5, color=ORANGE, bold=True)
    text(s, x + 0.2, 5.25, 2.5, 0.75, why, size=11.5)
    text(s, x + 0.2, 6.15, 2.5, 0.25, "ENCODED AS", size=9.5, color=ORANGE, bold=True)
    text(s, x + 0.2, 6.4, 2.5, 0.3, enc, size=11.5, color=MUTED)

# ============================================================ 9. Columns 5: the four provisional inputs
s = frame("col_prov", "What could go wrong with the four provisional inputs?",
          "Four pass every test except timing: the source never says when they are set — and one shifted sharply after Train",
          "notebooks/06 (test answers and reasons) · notebooks/13_validation_results_explained.ipynb · data/hotels_clean.pkl (shares)",
          "These four pass every test except one: the source does not say when their value is set. Unsure would normally mean exclude; the "
          "team chose to use them and keep the doubt on record. The company that pays could be attached at billing. The repeat-guest link "
          "could be made at check-in. And the two prior-booking counts may include earlier bookings cancelled after the decision morning. "
          "The chart shows why this matters. In Train, 11.8 percent of bookings had a prior cancellation and almost all of them cancelled "
          "again; in the validation period only 1.3 percent did. The models leaned on that signal and lost it, which is the main reason "
          "they under-predicted.")
prov = [("company", "Could be attached later, at billing or check-out", "When the company field is filled"),
        ("is_repeated_guest", "The guest profile may be linked at check-in", "When the profile is linked"),
        ("previous_cancellations", "May count bookings cancelled after morning M", "Each counted cancellation's date"),
        ("previous_bookings_not_canceled", "An open booking may cancel later and switch count", "Each earlier booking's status on M")]
text(s, 0.6, 2.3, 7.0, 0.25, "COLUMN · WHAT IS UNSURE · WHAT WOULD SETTLE IT", size=10, color=ORANGE, bold=True)
for i, (col, unsure, settle) in enumerate(prov):
    y = 2.65 + i * 1.02
    box(s, 0.6, y, 7.0, 0.9, TINT, radius=0.06)
    box(s, 0.6, y, 0.1, 0.9, WARN, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.9, y + 0.1, 6.5, 0.3, col, size=13, font=MONO, bold=True)
    text(s, 0.9, y + 0.45, 3.6, 0.42, unsure, size=11.5, color=INK)
    text(s, 4.6, y + 0.45, 2.9, 0.42, "Check: " + settle, size=11, color=MUTED)
text(s, 8.0, 2.3, 4.75, 0.25, "BOOKINGS WITH A PRIOR CANCELLATION", size=10, color=ORANGE, bold=True)
bar_chart(s, 7.9, 2.55, 4.85, 2.3, ["Train", "Validation"], [PRIOR_SHARE["Train"], PRIOR_SHARE["Validation"]], highlight=[0],
          horizontal=False, maximum=0.14, size=12)
text(s, 8.0, 5.0, 4.75, 1.75, [[("96.7% → 70.3%  ", {"bold": True, "font": HEAD, "size": 15}), ("of them cancelled", {"color": MUTED})],
                               [("27.6% → 36.4%  ", {"bold": True, "font": HEAD, "size": 15}), ("everyone else cancelled", {"color": MUTED})],
                               [("The models learnt 'prior cancellation = will cancel'; the signal nearly vanished.", {"color": MUTED, "size": 11.5})]],
     size=13, space_after=6)

# ============================================================ 10. Columns 6: why 36 are excluded
s = frame("col_excl", "Why were the other 36 columns left out?",
          "Each fails a specific test: it is the outcome, changes before arrival, is corrected later, or has unknown timing",
          "notebooks/06_forecast_column_selection.ipynb · notebooks/07_forecast_columns_explained.ipynb · src/features.py (HELD_BACK)",
          "Here are the 36 exclusions, grouped by the reason they fail. Three are the outcome itself, such as the reservation status. Eleven "
          "can still be changed until arrival, such as stay length, number of guests and meal, so our file holds the last value, not the "
          "morning's. Three are corrected or recalculated later: nationality at check-in, the price during the stay, the deposit from "
          "payments. Three have no recorded timing. Ten are flags I added during cleaning, which inherit their source column's result. And "
          "six pass every test but were left out of the team's input set: lead time and the date parts. They are the first candidates to "
          "add, tested on validation only.")
for i, (head, sub, cols, color) in enumerate(GROUPS):
    x, y = 0.6 + (i % 3) * 4.1, 2.3 + (i // 3) * 2.3
    box(s, x, y, 3.9, 2.12, TINT, radius=0.04)
    box(s, x + 3.25, y + 0.15, 0.5, 0.36, color, radius=0.5, label=str(len(cols)), size=12, color=PAPER, bold=True)
    text(s, x + 0.2, y + 0.15, 3.0, 0.3, head, size=13.5, font=HEAD, bold=True)
    text(s, x + 0.2, y + 0.5, 3.5, 0.3, sub, size=10.5, color=MUTED)
    names = [c.replace("flag_", "") if c in FLAGS else c for c in cols]
    box(s, x + 0.2, y + 0.86, 0.06, 1.1, color, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.38, y + 0.84, 3.37, 1.2, " · ".join(names), size=11, color=INK)

# ============================================================ 11. Columns 7: tempting traps
s = frame("col_traps", "Which excluded columns look useful, but are traps?",
          "Each looks like a strong signal, but its value is written or corrected after the decision morning, so it leaks the outcome",
          "data/hotels_clean.pkl (deposit: all bookings; parking and country: Train) · notebooks/06 and 07 · Antonio, de Almeida & Nunes (2019)",
          "These three would make any model look brilliant, which is exactly the warning. Read each card from the top: what the column looks like it means, what the data actually shows, why that happens, and what it would mean on the decision morning. A Non Refund booking sounds guaranteed, yet 99 percent of them cancelled; the deposit type is computed from payments up to arrival or cancellation, so the cancellation itself can create the label, and on the morning the label is not final. Not one Train guest with a parking space cancelled; parking is most likely registered on arrival, which only guests who stay reach, so on the morning almost nobody has a space. Portuguese bookings cancel about four times as often as the next countries; the paper warns that the correct nationality is often entered at check-in, which cancelled bookings never reach, so the code partly records who "
          "arrived. None of these rates was used to choose columns: notebook 06 never read an outcome. They show why timing, not "
          "score, has to decide.")
dep_order = ["No Deposit", "Non Refund", "Refundable"]
country = COUNTRY.reset_index()
nr_n = int((clean["deposit_type"] == "Non Refund").sum())
assert PARKING["With a parking space"] == 0  # not one Train booking with a parking space cancelled
others = country["mean"].iloc[1:]
charts = [("deposit_type", "Cancelled, by deposit type (all bookings)", dep_order, [float(DEPOSIT[k]) for k in dep_order], [1],
           [("Looks like", "a prepaid, guaranteed booking that should rarely cancel"),
            ("Actually", f"{pct(DEPOSIT['Non Refund'])} of {nr_n:,} Non Refund bookings cancelled, against {pct(DEPOSIT['No Deposit'])} with no deposit"),
            ("Why", "the type is computed from payments up to arrival or cancellation, so a charge posted at cancellation can create the label"),
            ("On the morning", "the label is not final yet: the model would be fed the answer")]),
          ("required_car_parking_spaces", f"Cancelled, Train ({PARKING_N:,} with parking)", list(PARKING), [float(v) for v in PARKING.values()], [0],
           [("Looks like", "a committed guest who has planned the trip"),
            ("Actually", f"0 of {PARKING_N:,} Train bookings with a space cancelled, against {pct(PARKING['Without'])} without"),
            ("Why", "parking is most likely registered on arrival, a step only guests who stay ever reach"),
            ("On the morning", "almost no booking has a space yet, so the signal is not there")]),
          ("country", "Cancelled, five largest countries (Train)", list(country["country"]), [float(v) for v in country["mean"]], [0],
           [("Looks like", "a fixed fact about the guest"),
            ("Actually", f"{pct(country['mean'].iloc[0])} of {int(country['size'].iloc[0]):,} {country['country'].iloc[0]} bookings cancelled, "
                         f"against {pct(others.min())}–{pct(others.max())} for the next four"),
            ("Why", "the correct nationality is often entered at check-in; cancelled bookings keep the original entry"),
            ("On the morning", "the code partly records who arrived, not who will cancel")])]
for i, (col, cap, cats, vals, hl, steps) in enumerate(charts):
    x = 0.6 + i * 4.1
    box(s, x, 2.3, 3.9, 4.5, TINT, radius=0.04)
    text(s, x + 0.2, 2.4, 3.5, 0.3, col, size=13, font=MONO, bold=True)
    text(s, x + 0.2, 2.72, 3.5, 0.26, cap, size=10.5, color=MUTED)
    bar_chart(s, x + 0.1, 2.95, 3.7, 1.55, cats, vals, highlight=hl, maximum=1.2, size=10)
    text(s, x + 0.2, 4.55, 3.5, 0.24, "HOW THE TRAP WORKS", size=10, color=ORANGE, bold=True)
    text(s, x + 0.2, 4.8, 3.5, 1.95, [[(f"{k}: ", {"bold": True, "color": CRIT if k == "On the morning" else INK}),
                                       (v, {"color": CRIT if k == "On the morning" else MUTED})] for k, v in steps],
         size=10.5, space_after=3)

# ============================================================ Cleaning 1: the rules, and the four values recoded (replaces source slide 5)
FLAG_ROWS = {n: p[[c for c in clean.columns if c.startswith("flag_")]].sum() for n, p in [("Train", train), ("Validation", choose), ("Test", _proof)]}
CL = D["cleaning"]
assert CL["meal_undefined"] == 1169 and CL["agent_missing"] == 16340 and CL["company_missing"] == 112593
s = frame("clean_recode", "What was wrong with the raw data, and what did we change?",
          "Four values were recoded, each backed by the source paper; no row was removed and the raw file was never edited",
          "notebooks/03_data_cleaning_review.ipynb · 04_cleaning_decisions_explained.ipynb · 05_apply_cleaning_decisions.ipynb · docs/DECISIONS.md",
          "Cleaning followed five rules, written down before any change. The raw file is evidence, so every change happens on a copy and "
          "is logged with its row count. A value is changed only when a source defines what it should be, and a row is removed only when "
          "a source proves it wrong; looking odd is a reason to flag, not delete. The scored book is fixed by the contract, so deleting a "
          "row would quietly change what the client's rule is scored on. Training data must look like the nights it is scored on. And "
          "outcomes never drive cleaning. Under those rules only four kinds of value changed. Undefined meal codes became SC, because the "
          "paper defines both as no meal package. Agent and company IDs became text, with NULL as 'none', because NULL means not applicable "
          "and IDs are labels. Missing countries became 'unknown', and CN was not merged into CHN because no source confirms they are the "
          "same. Four missing children counts became 0, with a flag. I also checked things that needed no action: the label agrees with "
          "the reservation status on every Train row.")
text(s, 0.6, 2.3, 4.3, 0.28, "THE FIVE RULES WE CLEANED BY", size=11, color=ORANGE, bold=True)
rules = [("Raw data is evidence", "Changes happen on a copy, logged with row counts"),
         ("A source must justify a change", "Odd is a reason to flag, not to delete"),
         ("The scored book is fixed", "Deleting a row changes what the contract scores"),
         ("Train must match what is scored", "Same population in training and in the book"),
         ("Outcomes never drive cleaning", "No row is kept or dropped because it cancelled")]
for i, (head, body) in enumerate(rules):
    y = 2.68 + i * 0.83
    box(s, 0.6, y + 0.04, 0.42, 0.42, INK, shape=MSO_SHAPE.OVAL, label=f"P{i + 1}", size=10.5, color=PAPER, bold=True)
    text(s, 1.17, y, 3.75, 0.3, head, size=13, bold=True)
    text(s, 1.17, y + 0.32, 3.75, 0.4, body, size=11, color=MUTED)
rows = [["Choice", "Before → after", "Rows", "Why (source)", "Rejected instead"],
        ["C1  meal", "'Undefined' → 'SC'", f"{CL['meal_undefined']:,}", "Paper: 'Undefined/SC – no meal package'", "Treat as missing"],
        ["C2  agent, company", "9.0 / NULL → '9' / 'none'", f"{CL['agent_missing']:,} / {CL['company_missing']:,}",
         "NULL means 'not applicable'; IDs are labels, not amounts", "Fill with 0 or the most common ID"],
        ["C3  country", "blank → 'unknown'", f"{CL['country_missing']:,}", "Kept visible; never a model input", "Merge CN into CHN (unconfirmed)"],
        ["C4  children", "blank → 0, flagged", f"{CL['children_missing']:,}",
         f"{CL['children_zero_share_train']:.1%} of Train have 0; one Aug 2015 cluster", "Drop the rows; fill the mean"]]
table(s, 5.2, 2.3, rows, [1.45, 1.6, 0.95, 2.0, 1.55], row_h=0.72, size=11, bolds={(r, 0): True for r in range(1, 5)},
      align={2: PP_ALIGN.RIGHT})
box(s, 5.2, 6.05, 7.55, 0.7, TINT, radius=0.1)
text(s, 5.4, 6.1, 7.15, 0.6, [[("Checked, no action needed: ", {"bold": True}),
                              ("the label matches the reservation status on every Train row (Canceled and No-Show = 1, Check-Out = 0); week "
                               "numbers use Sunday-start weeks (0 mismatches).", {"color": MUTED})]], size=11, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================ Cleaning 2: rows kept, odd rows flagged
s = frame("clean_rows", "Why was every row kept, and what was flagged instead?",
          "Odd rows can't be proved wrong without a booking ID, and deleting them would change the label and the scored nights",
          "notebooks/03_duplicate_investigation.ipynb · 04_cleaning_decisions_explained.ipynb (steps 1–5, 11) · data/hotels_clean.pkl (flag counts)",
          "The biggest cleaning question was the exact repeats: 16,291 Train rows repeat an earlier row in every column, in 3,472 groups; "
          "the largest is 150 identical cancelled City Hotel bookings for one February night. There is no booking ID, so a repeat may be "
          "a real group booking exported one row per room. Removing them would drop the Train cancellation rate from 35.8 to 22.2 percent "
          "while about a quarter of the later periods are still repeats, so the model would learn the wrong level, and it would change the "
          "booking count on 657 hotel-nights. So every row was kept and flagged. The same logic applies to the other odd rows: most "
          "zero-night and zero-guest bookings actually checked out, the 13 bookings with ten or more adults are singled out mainly by having "
          "cancelled, and the two extreme prices change nothing that is scored. Flags record each observation without changing anything, "
          "and none is a model input. Prior cancellations were left unchanged; the planned with-and-without comparison was not run before "
          "the freeze.")
box(s, 0.6, 2.3, 5.0, 2.55, INK, radius=0.05)
text(s, 0.85, 2.42, 4.6, 0.28, "EXACT REPEATS IN TRAIN", size=11, color=ORANGE, bold=True)
text(s, 0.85, 2.75, 4.6, 0.55, "16,291 rows · 3,472 groups", size=20, font=HEAD, bold=True, color=PAPER)
text(s, 0.85, 3.28, 4.6, 0.5, "largest: 150 identical cancelled City Hotel bookings for 17 Feb 2016", size=11.5, color="C9D2DA")
text(s, 0.85, 3.85, 2.3, 0.5, f"{CL['train_rate_all_rows']:.1%} → {CL['train_rate_without_repeats']:.1%}", size=20, font=HEAD, bold=True,
     color=ORANGE)
text(s, 0.85, 4.33, 2.3, 0.45, "Train cancellation rate if collapsed", size=10.5, color="C9D2DA")
text(s, 3.2, 3.85, 2.3, 0.5, "657", size=20, font=HEAD, bold=True, color=ORANGE)
text(s, 3.2, 4.33, 2.3, 0.45, "hotel-nights whose booking count would change", size=10.5, color="C9D2DA")
opts = [["Option", "Verdict"],
        ["Drop every later copy", "Rejected: no ID proves an error (P2); changes the label (P4) and the scored book (P3)"],
        ["Drop copies in Train only", "Rejected: Train no longer matches the book it is scored on (P4)"],
        ["Down-weight copies", "A modelling choice, not cleaning; could be tested on validation"],
        ["Keep and flag", "Chosen: nothing removed; flag_identical_group marks them"]]
table(s, 0.6, 5.0, opts, [1.75, 3.25], row_h=0.36, size=10, fills={(4, 0): PEACH, (4, 1): PEACH}, bolds={(4, 0): True, (4, 1): True})
why = {"flag_identical_group": "No booking ID; looks like group blocks", "flag_zero_nights": "354 of 371 in Train checked out: day-use stays",
       "flag_zero_guests": "45 of 49 in Train checked out: a missed count", "flag_children_without_adults": "A count error, not a booking error",
       "flag_room_type_p": "Probably a placeholder; too few to matter", "flag_ten_plus_adults": "Block rows; singled out mainly by cancelling (P5)",
       "flag_adr_above_1000": "€5,400 on one unscored Train night", "flag_adr_negative": "Moves one test night's stay value by under €1",
       "flag_children_missing": "The 4 rows filled with 0 in C4", "flag_repeat_status_conflict": "Repeat flag and prior counts disagree; both kept"}
frows = [["Flag (none is a model input)", "Train", "Valid.", "Test", "Why kept, not removed"]]
for f, reason in why.items():
    frows.append([f.replace("flag_", ""), f"{int(FLAG_ROWS['Train'][f]):,}", f"{int(FLAG_ROWS['Validation'][f]):,}",
                  f"{int(FLAG_ROWS['Test'][f]):,}", reason])
table(s, 5.9, 2.3, frows, [2.05, 0.72, 0.72, 0.62, 2.74], row_h=0.36, size=10, align={1: PP_ALIGN.RIGHT, 2: PP_ALIGN.RIGHT, 3: PP_ALIGN.RIGHT})
box(s, 5.9, 6.42, 6.85, 0.4, TINT, radius=0.2)
text(s, 6.1, 6.44, 6.5, 0.36, [[("C6 · previous_cancellations: ", {"bold": True}),
                               ("left unchanged (no source proves it wrong); the planned with/without test was not run before the freeze", {"color": MUTED})]],
     size=10.5, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================ Model Lead and Build Lead: results of notebooks 11-16, src/nightly.py, tests/
MD = ROOT / "data" / "models"
METHODS = ["flat-rule reference", "logistic regression", "random forest", "XGBoost", "CatBoost"]
SHORT = {"flat-rule reference": "Flat rule", "logistic regression": "Logistic regression", "random forest": "Random forest",
         "XGBoost": "XGBoost", "CatBoost": "CatBoost"}


def nb_out(name, cell):
    """The saved text output of one notebook cell (cells counted from 1, markdown included)."""
    cells = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))["cells"]
    return "\n".join("".join(o.get("text", "")) or "".join(o.get("data", {}).get("text/plain", "")) for o in cells[cell - 1].get("outputs", []))


def eur_m(v):
    return f"€{v / 1e6:.2f}M"


TR = pd.read_csv(MD / "train_scores.csv", index_col="model")
TRN = pd.read_csv(MD / "train_nightly_scores.csv").query("hotel == 'group'").set_index("model")
VS = pd.read_csv(MD / "val_scores.csv", index_col="method")
VN = pd.read_csv(MD / "val_nightly_scores.csv").set_index(["hotel", "method"])
VR = pd.read_csv(MD / "val_results.csv").set_index(["hotel", "method"])
ACC = pd.read_csv(MD / "test_accuracy.csv", index_col=[0, 1])
EARLIER = D["earlier"]["val"]
IMP = dict(zip(["random forest", "logistic regression", "XGBoost", "CatBoost"],
               map(int, re.findall(r"previous_cancellations \((\d+)%\)", nb_out("11_train_models.ipynb", 17)))))
FIT_S = dict(re.findall(r"Fitted (.+?) in ([\d.]+) s", nb_out("11_train_models.ipynb", 9)))
GAP = [float(g) for g in re.findall(r"average gap \(weighted\)\s+([\d.]+)%", nb_out("12_validate_models.ipynb", 9))]
_b = nb_out("13_validation_results_explained.ipynb", 20).split("B. A separate buffer")[1]
MONTHS13 = dict(re.findall(r"(logistic regression|random forest|XGBoost|CatBoost)\s+(\d) of 6", _b))
RESAMPLE13 = dict(re.findall(r"(logistic regression|random forest|XGBoost|CatBoost)\s+(\d+)%", _b.split("resamples cheaper")[1]))
assert IMP == {"random forest": 44, "logistic regression": 2, "XGBoost": 17, "CatBoost": 70} and len(GAP) == 5 and len(FIT_S) == 4
assert RESAMPLE13["CatBoost"] == "74" and RESAMPLE13["XGBoost"] == "69" and MONTHS13["CatBoost"] == "3"
assert EARLIER["CatBoost"]["per_hotel"]["city"] == 6 and round(EARLIER["flat-rule reference"]["per_hotel"]["cost"]) == 1950066
P1 = pd.read_csv(MD / "test_results_primary.csv").set_index(["hotel", "method"])
S1 = pd.read_csv(MD / "test_results_secondary.csv").set_index(["hotel", "method"])
R3 = pd.read_csv(MD / "test_run3_results_primary.csv").set_index(["hotel", "method"])
A3 = pd.read_csv(MD / "test_run3_accuracy.csv", index_col=0)
RUN2 = json.loads((ROOT / "models" / "frozen_choice_run2_xgboost.json").read_text())
RUN3 = json.loads((ROOT / "models" / "frozen_choice_run3_train_val.json").read_text())
MONTHS14 = re.search(r"cheaper than the flat rule in (\d) of 8", nb_out("14_test_run.ipynb", 15)).group(1)
MONTHS16 = re.search(r"CatBoost cheaper than the flat rule in (\d) of 8", nb_out("16_final_test_run.ipynb", 15)).group(1)
N_FIT3 = int(re.search(r"Fitted CatBoost on ([\d,]+)", nb_out("15_retrain_train_val.ipynb", 9)).group(1).replace(",", ""))
COLS3 = int(re.search(r"(\d+) prepared columns", nb_out("15_retrain_train_val.ipynb", 7)).group(1))
assert round(P1.loc[("group", "CatBoost"), "cost (EUR)"]) == 3365371 and R3.loc[("group", "CatBoost"), "walks per 1,000"] == 13.11
assert N_FIT3 == 78703 and COLS3 == 167 and RUN2["frozen_before_test"] is False
NIGHTLY = pd.read_csv(ROOT / "outputs" / "nightly_recommendations.csv", parse_dates=["arrival_date"])
NMAN = json.loads((ROOT / "outputs" / "nightly_recommendations.manifest.json").read_text(encoding="utf-8"))
assert NMAN["status"] == "SUCCESS" and NMAN["fingerprints_checked"] and NMAN["outcome_column_read"] is False
import subprocess  # noqa: E402

_pytest = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True).stdout
N_TESTS = int(re.search(r"(\d+) passed", _pytest).group(1))
assert "failed" not in _pytest and N_TESTS == 12, _pytest[-300:]
TEST_FILES = {f: len(re.findall(r"^\s*def test_", (ROOT / "tests" / f).read_text(encoding="utf-8"), re.M))
              for f in ("test_contract.py", "test_features.py", "test_nightly.py")}
assert sum(TEST_FILES.values()) == N_TESTS

# --- Model 1: the models trained (notebook 11)
s = frame("m_trained", "Which models were trained, and how well did they fit Train?",
          "Four models and the flat-rule reference, each fitted once on all 49,157 Train bookings with fixed settings; no folds, no tuning",
          "notebooks/11_train_models.ipynb (cells 7, 9, 11, 13, 17) · data/models/train_scores.csv, train_nightly_scores.csv",
          "Notebook 11 fits five methods on the whole training year, July 2015 to June 2016: the client's flat rule, which simply uses "
          "each hotel's training cancellation rate, and four models: logistic regression, a random forest, XGBoost and CatBoost. The "
          "settings were fixed in the code before fitting, with seed 0, and nothing was tuned: there are no folds in these notebooks. "
          "All four models use notebook 10's 143 prepared columns. On the training rows the three tree models and logistic regression "
          "all reach an AUC of about 0.81 to 0.82 and miss a night's cancellation count by about 6 rooms, against almost 10 for the flat "
          "rule. But these are the rows the models learned from, so the numbers flatter them; the fair check is the second half of 2016, "
          "on the next slide. Previous cancellations dominate the tree models: 70 percent of CatBoost's importance.")
rows = [["Method", "Settings (cell 7)", "Fit time", "Log loss", "Brier", "AUC", "Nightly miss"]]
SETTINGS = {"flat-rule reference": "each hotel's Train rate: City 41.7%, Resort 25.2%",
            "logistic regression": "C = 1, max_iter 2,000", "random forest": "300 trees, min leaf 20, seed 0",
            "XGBoost": "300 trees, depth 4, rate 0.05, subsample 0.8", "CatBoost": "300 iterations, depth 4, rate 0.05, seed 0"}
for m in METHODS:
    rows.append([SHORT[m], SETTINGS[m], f"{float(FIT_S[m]):.1f} s" if m in FIT_S else "–", f"{TR.loc[m, 'log loss']:.3f}",
                 f"{TR.loc[m, 'Brier score']:.4f}", f"{TR.loc[m, 'ROC AUC']:.3f}", f"{TRN.loc[m, 'mean absolute error (rooms)']:.2f} rooms"])
table(s, 0.6, 2.3, rows, [2.1, 4.15, 0.95, 1.1, 1.1, 1.0, 1.75], row_h=0.4, size=11, bolds={(r, 0): True for r in range(1, 6)},
      align={j: PP_ALIGN.RIGHT for j in range(2, 7)})
text(s, 0.6, 4.95, 6.0, 0.28, "PREVIOUS CANCELLATIONS: SHARE OF EACH MODEL'S IMPORTANCE", size=11, color=ORANGE, bold=True)
order = ["CatBoost", "random forest", "XGBoost", "logistic regression"]
bar_chart(s, 0.6, 5.2, 6.0, 1.65, [SHORT[m] for m in order], [IMP[m] / 100 for m in order], highlight=[0], fmt="0%", maximum=0.85)
box(s, 7.0, 4.95, 5.75, 1.9, TINT, radius=0.06)
text(s, 7.25, 5.05, 5.3, 1.75, [[("Read with care: ", {"bold": True}),
                                 ("these scores are on the rows each model learned from, so they flatter it. Validation on Jul–Dec 2016 "
                                  "(next slide) is the fair check.", {"color": MUTED})],
                                [("Importance: ", {"bold": True}),
                                 ("trees report their own importance; logistic regression's is its share of absolute coefficients "
                                  "(agent 236 ranks first, 4%).", {"color": MUTED})],
                                [("Nightly miss: ", {"bold": True}),
                                 ("average rooms between expected and actual cancellations per hotel-night.", {"color": MUTED})]],
     size=11, space_after=5)

# --- Model 2: probability quality on validation (notebook 12)
city_miss = {m: VN.loc[("City Hotel", m), "mean error (rooms)"] for m in METHODS}
s = frame("m_val_prob", "How good were the probabilities on Jul–Dec 2016?",
          f"The models ranked bookings better than the flat rule (AUC 0.70–0.71 against {VS.loc['flat-rule reference', 'ROC AUC (val)']:.2f}), "
          f"but predicted 28–29% cancellations against {VS['actual rate (val)'].iloc[0]:.1%} actual",
          "notebooks/12_validate_models.ipynb (cells 7, 9, 11) · 13 (cell 10) · data/models/val_scores.csv, val_nightly_scores.csv · "
          "test_accuracy.csv (val rows, notebook 14 cell 17)",
          "Notebook 12 scores every method on the 29,546 bookings arriving in the second half of 2016, 368 hotel-nights, which none of "
          "them saw in training. The models sort bookings far better than the flat rule: an AUC of 0.70 to 0.71 against 0.56, and a lower "
          "log loss and Brier score. But every model predicts too few cancellations: an average of 28 to 29 percent against 36.9 percent "
          "actual. On a City Hotel night that means about 10 to 11 rooms too few expected cancellations, while the flat rule is within one "
          "room. Notebook 13 found why: in training, 11.8 percent of bookings had a previous cancellation and almost all of them cancelled "
          "again, so the models leaned on that column; in the second half of 2016 only 1.3 percent did. The band check tells the same "
          "story: the models' predictions sit 8 to 9 points away from what happened, the flat rule's 1.6.")
rows = [["Method", "Log loss", "Brier", "AUC", "Predicted rate", "City night miss", "Band gap"]]
for i, m in enumerate(METHODS):
    rows.append([SHORT[m], f"{VS.loc[m, 'log loss (val)']:.3f}", f"{VS.loc[m, 'Brier (val)']:.4f}", f"{VS.loc[m, 'ROC AUC (val)']:.3f}",
                 pct(VS.loc[m, "mean predicted rate (val)"]), f"{city_miss[m]:+.1f} rooms", f"{GAP[i]:.1f} pts"])
best_auc = int(np.argmax([VS.loc[m, "ROC AUC (val)"] for m in METHODS])) + 1
table(s, 0.6, 2.3, rows, [2.0, 1.0, 1.0, 0.85, 1.3, 1.5, 1.05], row_h=0.42, size=11, bolds={(r, 0): True for r in range(1, 6)},
      align={j: PP_ALIGN.RIGHT for j in range(1, 7)}, fills={(best_auc, 3): PEACH})
cat_acc, none_acc = ACC.loc[("val", "CatBoost"), "accuracy (50% cut-off)"], ACC.loc[("val", "CatBoost"), "accuracy of 'nobody cancels'"]
text(s, 0.6, 4.95, 8.7, 0.5, [[("Actual rate: ", {"bold": True}), (f"{VS['actual rate (val)'].iloc[0]:.1%}. ", {"color": MUTED}),
                               ("City night miss: ", {"bold": True}), ("expected minus actual cancellations; negative = too few. ", {"color": MUTED}),
                               ("Band gap: ", {"bold": True}), ("average distance between predicted and actual rate across 10% bands (cell 9).",
                                                                 {"color": MUTED})]], size=10.5)
box(s, 0.6, 5.55, 8.7, 1.25, TINT, radius=0.06)
text(s, 0.85, 5.65, 8.3, 1.1, [[("Accuracy at a 50% cut-off: ", {"bold": True}),
                                (f"CatBoost classified {cat_acc:.1%} of validation bookings correctly; predicting 'nobody cancels' scores "
                                 f"{none_acc:.1%}. Ranking is better than the flat rule; the level is not.", {"color": MUTED})]], size=11.5,
     anchor=MSO_ANCHOR.MIDDLE)
box(s, 9.6, 2.3, 3.15, 4.5, INK, radius=0.05)
text(s, 9.85, 2.45, 2.7, 0.28, "WHY THE MODELS RAN LOW", size=11, color=ORANGE, bold=True)
text(s, 9.85, 2.8, 2.7, 0.3, "Bookings with a prior cancellation", size=11, color="C9D2DA")
for j, (period, share) in enumerate([("Train", PRIOR_SHARE["Train"]), ("Jul–Dec 2016", PRIOR_SHARE["Validation"])]):
    text(s, 9.85, 3.2 + j * 0.85, 2.7, 0.5, f"{share:.1%}", size=26, font=HEAD, bold=True, color=PAPER)
    text(s, 9.85, 3.68 + j * 0.85, 2.7, 0.3, period, size=10.5, color="C9D2DA")
text(s, 9.85, 5.0, 2.7, 1.7, f"{train.loc[train['previous_cancellations'] > 0, 'is_canceled'].mean():.1%} of those Train bookings cancelled, "
     f"so the models leaned on the column; by late 2016 it had almost vanished (notebook 13, cell 10; chart on slide {POS['col_prov']}).",
     size=10.5, color="C9D2DA")

# --- Model 3: one shared buffer (notebook 12)
s = frame("m_shared", "What did each method cost with one shared buffer?",
          "Every model cost 11–16% less than the flat rule, mostly because one 16-room buffer fitted the two hotels badly",
          "notebooks/12_validate_models.ipynb (cells 13, 15, 19) · 13_validation_results_explained.ipynb (cell 15) · data/models/val_results.csv",
          "Next, each method's expected cancellations become a decision: oversell the expected count, rounded down, minus a buffer, and "
          "never below zero. Notebook 12 tried buffers from 0 to 60 rooms, the same buffer for both hotels and every night, and kept the "
          "cheapest that held walks at or under 10 per 1,000 across the group. The flat rule needed 16 rooms; the models needed 5 or 6, "
          "because they already forecast too few cancellations. On cost every model looked 11 to 16 percent cheaper. But look at where the "
          "flat rule's walks fall: 167 at the City Hotel and only 2 at the Resort. One shared buffer is far too small for the City and far "
          "too big for the Resort, so the comparison handicaps the flat rule. That is what notebook 13 tested next.")
flat_cost = VR.loc[("group", "flat-rule reference"), "cost (EUR)"]
text(s, 0.6, 2.3, 5.2, 0.28, "COST ON 368 HOTEL-NIGHTS, € MILLION", size=11, color=ORANGE, bold=True)
bar_chart(s, 0.6, 2.6, 5.2, 3.3, [SHORT[m] for m in METHODS], [VR.loc[("group", m), "cost (EUR)"] / 1e6 for m in METHODS],
          highlight=[0], fmt='"€"0.00"M"', maximum=2.8)
rows = [["Method", "Buffer", "Empty", "Walked", "Per 1,000", "City walks", "Resort walks", "vs flat"]]
for m in METHODS:
    g = VR.loc[("group", m)]
    rows.append([SHORT[m], f"{int(g['buffer'])}", f"{int(g['empty rooms']):,}", f"{int(g['walked guests'])}", f"{g['walks per 1,000']:.2f}",
                 f"{int(VR.loc[('City Hotel', m), 'walked guests'])}", f"{int(VR.loc[('Resort Hotel', m), 'walked guests'])}",
                 "–" if m == METHODS[0] else f"{(g['cost (EUR)'] - flat_cost) / flat_cost:+.1%}"])
table(s, 6.1, 2.3, rows, [1.65, 0.65, 0.7, 0.7, 0.8, 0.7, 0.75, 0.7], row_h=0.45, size=11, bolds={(r, 0): True for r in range(1, 6)},
      align={j: PP_ALIGN.RIGHT for j in range(1, 8)}, fills={(1, 5): PEACH, (1, 6): PEACH})
box(s, 6.1, 5.2, 6.65, 1.6, TINT, radius=0.06)
text(s, 6.35, 5.3, 6.2, 1.4, [[("The rule: ", {"bold": True}),
                               ("oversell = max(0, floor(expected cancellations) − buffer); buffers 0–60 tried; the cheapest within 10 walks "
                                "per 1,000, group-wide, kept (cell 13).", {"color": MUTED})],
                              [("The catch: ", {"bold": True}),
                               (f"the flat rule's walks are {int(VR.loc[('City Hotel', METHODS[0]), 'walked guests'])} at the City "
                                f"({VR.loc[('City Hotel', METHODS[0]), 'walks per 1,000']:.2f} per 1,000) and "
                                f"{int(VR.loc[('Resort Hotel', METHODS[0]), 'walked guests'])} at the Resort: one buffer cannot fit both.",
                                {"color": MUTED})]], size=11, space_after=6)
text(s, 0.6, 6.1, 5.2, 0.7, "Probabilities uncalibrated; no folds. Each method scored once at its own buffer on the same hotel-nights.",
     size=10.5, color=MUTED)

# --- Model 4: a buffer per hotel, and the freeze (notebook 13)
s = frame("m_perhotel", "What changed with a separate buffer for each hotel?",
          f"The flat rule fell to {eur_m(EARLIER['flat-rule reference']['per_hotel']['cost'])}; CatBoost was only 1.4% cheaper, "
          "not a reliable difference, and was frozen before any test result",
          "notebooks/13_validation_results_explained.ipynb (cells 17, 20, 24, 30) · presentation/deck_data.py (per-hotel recomputation) · models/frozen_choice.json",
          "Notebook 13 gives every method its own buffer at each hotel. It tries every pair of buffers from 0 to 60 and keeps the cheapest "
          "pair that holds walks at or under 10 per 1,000 for the group, the only limit the client set. The flat rule improves most: "
          "City 20 and Resort 4 rooms bring it down to 1.95 million euros. Logistic regression and the random forest now cost more than "
          "the flat rule. XGBoost and CatBoost are 1.0 and 1.4 percent cheaper, but only in three of six months, and CatBoost comes out "
          "cheaper in 74 percent of resamples: not a reliable difference. If each hotel also had to stay within 10 per 1,000, which the "
          "client did not ask for, the flat rule would be cheapest. CatBoost was frozen with City 6 and Resort 3 at 01:57, before the test "
          "was opened.")
flat_ph = EARLIER["flat-rule reference"]["per_hotel"]["cost"]
rows = [["Method", "City / Resort", "Cost", "Per 1,000", "vs flat", "Months cheaper", "Resamples cheaper"]]
for m in METHODS:
    ph = EARLIER[m]["per_hotel"]
    rows.append([SHORT[m], f"{ph['city']} / {ph['resort']}", eur(ph["cost"]), f"{ph['walks_per_1000']:.2f}",
                 "–" if m == METHODS[0] else f"{(ph['cost'] - flat_ph) / flat_ph:+.1%}",
                 "–" if m == METHODS[0] else f"{MONTHS13[m]} of 6", "–" if m == METHODS[0] else f"{RESAMPLE13[m]}%"])
table(s, 0.6, 2.3, rows, [2.1, 1.35, 1.35, 1.0, 0.9, 1.45, 1.6], row_h=0.45, size=11.5, bolds={(r, 0): True for r in range(1, 6)},
      align={j: PP_ALIGN.RIGHT for j in range(1, 7)}, fills={(5, c): PEACH for c in range(7)})
text(s, 0.6, 5.1, 9.75, 0.5, [[("How chosen: ", {"bold": True}),
                               ("every (City, Resort) pair from 0–60 tried; cheapest pair within 10 walks per 1,000 group-wide (cell 17). "
                                "Months and resamples: cell 20; all figures checked by cell 30.", {"color": MUTED})]], size=10.5)
box(s, 0.6, 5.7, 9.75, 1.1, TINT, radius=0.06)
text(s, 0.85, 5.78, 9.3, 0.95, [[("If each hotel were also held to 10 per 1,000 ", {"bold": True}),
                                 ("(not a client requirement): the flat rule would be the cheapest method, and CatBoost 2.4% more expensive "
                                  "(cell 24).", {"color": MUTED})]], size=11.5, anchor=MSO_ANCHOR.MIDDLE)
box(s, 10.6, 2.3, 2.15, 4.5, INK, radius=0.05)
text(s, 10.8, 2.45, 1.8, 0.28, "FROZEN", size=11, color=ORANGE, bold=True)
text(s, 10.8, 2.8, 1.8, 0.5, RUN1["frozen_at"][11:16], size=26, font=HEAD, bold=True, color=PAPER)
text(s, 10.8, 3.35, 1.8, 0.3, RUN1["frozen_at"][:10], size=10.5, color="C9D2DA")
text(s, 10.8, 3.85, 1.8, 2.8, [[(f"{RUN1['chosen_method']} ", {"bold": True, "color": PAPER}),
                                (f"City {RUN1['primary']['chosen_buffers']['City Hotel']} / Resort {RUN1['primary']['chosen_buffers']['Resort Hotel']}",
                                 {"color": "C9D2DA"})],
                               [("Flat rule ", {"bold": True, "color": PAPER}),
                                (f"City {BUFFERS['City Hotel']} / Resort {BUFFERS['Resort Hotel']}", {"color": "C9D2DA"})],
                               [("before any test result, with SHA-256 of model and preprocessor", {"color": "C9D2DA"})]],
     size=11, space_after=8)

# --- Model 5: run 1 on the 2017 test (notebook 14)
g_flat, g_cat = P1.loc[("group", "flat rule")], P1.loc[("group", "CatBoost")]
s = frame("m_run1", "How did the frozen choice do on the 2017 test?",
          f"Run 1, frozen before any result: CatBoost cost {eur(g_cat['cost (EUR)'] - g_flat['cost (EUR)'])} more than the flat rule; "
          "both stayed within the walk limit",
          "notebooks/14_test_run.ipynb (cells 3, 5, 7, 9, 13, 15, 19) · data/models/test_results_primary.csv, test_accuracy.csv, test_results_secondary.csv",
          "Notebook 14 opens the 2017 test, January to August, 40,687 bookings on 486 hotel-nights, once. It first checks that the model "
          "and preprocessor match the fingerprints taken at the freeze, predicts every booking, saves the predictions, and only then reads "
          "the outcomes. The flat rule with City 20 and Resort 4 cost 3.21 million euros and walked 7.18 guests per 1,000. CatBoost with "
          "City 6 and Resort 3 cost 3.37 million, 150,459 euros more, and walked 8.42 per 1,000. Both met the limit. CatBoost saved a "
          "little at the City Hotel but lost 169 thousand at the Resort, and was cheaper in only three of eight months. It again "
          "predicted too few cancellations: 27 percent against 38.7. A shared-buffer view, disclosed in the notebook, would show CatBoost "
          "saving 432 thousand, but only because one buffer handicaps the flat rule.")
tiles = [(eur(g_flat["cost (EUR)"]), f"flat rule (City {BUFFERS['City Hotel']} / Resort {BUFFERS['Resort Hotel']}), {g_flat['walks per 1,000']:.2f} per 1,000", INK),
         (eur(g_cat["cost (EUR)"]), f"CatBoost (City 6 / Resort 3), {g_cat['walks per 1,000']:.2f} per 1,000", INK),
         (f"+{eur(g_cat['cost (EUR)'] - g_flat['cost (EUR)'])}", f"CatBoost's extra cost (+{(g_cat['cost (EUR)'] - g_flat['cost (EUR)']) / g_flat['cost (EUR)']:.1%}); "
          f"cheaper in {MONTHS14} of 8 months", CRIT)]
for i, (big, small, color) in enumerate(tiles):
    x = 0.6 + i * 4.1
    box(s, x, 2.3, 3.85, 1.2, TINT, radius=0.06)
    text(s, x + 0.25, 2.38, 3.4, 0.55, big, size=24, font=HEAD, bold=True, color=color)
    text(s, x + 0.25, 2.95, 3.45, 0.5, small, size=11, color=MUTED)
rows = [["Hotel · method", "Buffer", "Cost", "Empty", "Walked", "Per 1,000", "Limit (group)"]]
for hotel in ["group", "City Hotel", "Resort Hotel"]:
    for m in ["flat rule", "CatBoost"]:
        r = P1.loc[(hotel, m)]
        rows.append([f"{'Both hotels' if hotel == 'group' else hotel} · {m}",
                     f"{BUFFERS['City Hotel']} / {BUFFERS['Resort Hotel']}" if hotel == "group" and m == "flat rule" else
                     ("6 / 3" if hotel == "group" else f"{int(r['buffer'])}"),
                     eur(r["cost (EUR)"]), f"{int(r['empty rooms']):,}", f"{int(r['walked guests'])}", f"{r['walks per 1,000']:.2f}",
                     r["guardrail (<= 10, group)"].capitalize() if hotel == "group" else "not judged"])
table(s, 0.6, 3.75, rows, [2.65, 0.85, 1.3, 0.9, 0.85, 0.95, 1.3], row_h=0.4, size=11, bolds={(1, c): True for c in range(7)},
      align={j: PP_ALIGN.RIGHT for j in range(1, 6)})
acc_cat = ACC.loc[("test", "CatBoost")]
box(s, 9.6, 3.75, 3.15, 3.05, TINT, radius=0.06)
text(s, 9.85, 3.85, 2.7, 0.28, "CATBOOST'S PROBABILITIES", size=11, color=ORANGE, bold=True)
none_test = acc_cat["accuracy of 'nobody cancels'"]
text(s, 9.85, 4.2, 2.7, 2.5, [[("Correct at 50%: ", {"bold": True}), (f"{acc_cat['accuracy (50% cut-off)']:.1%} (nobody cancels: "
                                                                       f"{none_test:.1%})", {"color": MUTED})],
                              [("AUC: ", {"bold": True}), (f"{acc_cat['ROC AUC']:.3f} (flat rule {ACC.loc[('test', 'flat-rule reference'), 'ROC AUC']:.3f})", {"color": MUTED})],
                              [("Predicted rate: ", {"bold": True}), (f"{acc_cat['mean predicted rate']:.1%} against {acc_cat['actual rate']:.1%} actual", {"color": MUTED})],
                              [("Shared-buffer view (disclosed): ", {"bold": True}),
                               (f"flat 16 {eur(S1.loc[('group', 'flat rule'), 'cost (EUR)'])}, CatBoost 5 {eur(S1.loc[('group', 'CatBoost'), 'cost (EUR)'])}; "
                                "handicaps the flat rule", {"color": MUTED})]], size=10.5, space_after=5)

# --- Model 6: runs 2 and 3, decided after run 1 (notebooks 15-16)
c3, x3 = R3.loc[("group", "CatBoost")], R3.loc[("group", "XGBoost")]
fair = R3.loc[("group", "flat rule (train + val rates)")]
s = frame("m_run3", "What happened when the models were refitted after run 1?",
          f"Refitted on Train + Jul–Dec 2016, both models cost about €{c3['saving vs flat rule (EUR)'] / 1e3:.0f}k less but walked "
          f"{c3['walks per 1,000']:.0f} per 1,000, so the contract rejects them",
          "notebooks/15_retrain_train_val.ipynb (cells 7, 9, 13, 15) · 16_final_test_run.ipynb (cells 3, 13, 15, 17, 21) · data/models/test_run3_results_primary.csv, test_all_runs.csv",
          "After run 1's result, two more runs were decided, and both are disclosed. Run 2, XGBoost fitted on Train only, was frozen but "
          "never run. Run 3 refitted the preprocessor, CatBoost and XGBoost on Train plus the second half of 2016, 78,703 bookings, with "
          "the same settings and the same buffers, and froze them at 02:05 before reopening the test. The refit raised the expected "
          "cancellations by about three rooms a night. Both models then cost about 410 thousand euros less than the flat rule and were "
          "cheaper in all eight months, but they walked about 13 guests per 1,000, over the limit of 10, so the contract rejects them. A "
          "fair check refits the flat rule's rates on the same data: 3.19 million and 8.10 walks per 1,000, within the limit. Because run "
          "3 was chosen after seeing the test, it is not clean evidence of a saving.")
runs = [("Run 1", RUN1["frozen_at"][11:16], "CatBoost, fitted on Train; frozen before any test result", f"{eur(g_cat['cost (EUR)'])} · {g_cat['walks per 1,000']:.2f} · met", GOOD),
        ("Run 2", RUN2["frozen_at"][11:16], "XGBoost, fitted on Train; frozen after run 1", "never run (superseded)", SOFT),
        ("Run 3", RUN3["frozen_at"][11:16], f"CatBoost + XGBoost refitted on {N_FIT3:,} Train + Jul–Dec 2016 bookings ({COLS3} columns); "
         "decided after run 1", f"{eur(c3['cost (EUR)'])} · {c3['walks per 1,000']:.2f} · breached", CRIT)]
for i, (name, at, what, result, color) in enumerate(runs):
    y = 2.3 + i * 1.2
    box(s, 0.6, y, 4.2, 1.05, TINT, radius=0.06)
    box(s, 0.6, y, 0.1, 1.05, color, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.85, y + 0.08, 2.0, 0.3, name, size=13, bold=True)
    text(s, 3.2, y + 0.08, 1.45, 0.3, f"frozen {at}", size=10.5, color=SOFT, align=PP_ALIGN.RIGHT)
    text(s, 0.85, y + 0.38, 3.85, 0.4, what, size=10, color=MUTED)
    text(s, 0.85, y + 0.75, 3.85, 0.26, result, size=10.5, bold=True, color=color)
text(s, 0.6, 5.95, 4.2, 0.85, [[("Disclosure: ", {"bold": True}),
                                ("runs 2 and 3 were decided after run 1's test result (notebook 16, cell 21), so only run 1 is a clean test.",
                                 {"color": MUTED})]], size=10.5)
text(s, 5.1, 2.3, 7.65, 0.28, "WALKED GUESTS PER 1,000 ARRIVALS ON THE 2017 TEST · LIMIT 10", size=11, color=ORANGE, bold=True)
wl = [("Flat rule, Train rates", g_flat["walks per 1,000"]), ("Flat rule, Train + val rates", fair["walks per 1,000"]),
      ("CatBoost, run 1", g_cat["walks per 1,000"]), ("CatBoost, run 3", c3["walks per 1,000"]), ("XGBoost, run 3", x3["walks per 1,000"])]
bar_chart(s, 5.1, 2.55, 7.65, 2.2, [a for a, _ in wl], [b for _, b in wl], highlight=[i for i, (_, b) in enumerate(wl) if b > 10],
          highlight_color=CRIT,
          fmt="0.00", maximum=16, size=10.5)
rows = [["Run 3 (Train + val)", "Cost", "vs flat", "Walked", "Per 1,000", "City / Resort per 1,000", "Correct · AUC"]]
for m, r in [("CatBoost", c3), ("XGBoost", x3)]:
    rows.append([m, eur(r["cost (EUR)"]), f"−{eur(r['saving vs flat rule (EUR)'])}", f"{int(r['walked guests'])}", f"{r['walks per 1,000']:.2f}",
                 f"{R3.loc[('City Hotel', m), 'walks per 1,000']:.2f} / {R3.loc[('Resort Hotel', m), 'walks per 1,000']:.2f}",
                 f"{A3.loc[m, 'accuracy (50% cut-off)']:.1%} · {A3.loc[m, 'ROC AUC']:.3f}"])
rows.append(["Flat rule, Train + val rates", eur(fair["cost (EUR)"]), "fairness check", f"{int(fair['walked guests'])}",
             f"{fair['walks per 1,000']:.2f}", "–", "–"])
table(s, 5.1, 4.9, rows, [1.95, 1.05, 1.0, 0.7, 0.8, 1.15, 1.0], row_h=0.38, size=10, bolds={(r, 0): True for r in range(1, 4)},
      align={j: PP_ALIGN.RIGHT for j in range(1, 7)}, colors={(1, 4): CRIT, (2, 4): CRIT})
text(s, 5.1, 6.5, 7.65, 0.3, f"Refit raised expected cancellations by {RUN3['val_expected_count_shift_rooms']['CatBoost / group']:.1f} rooms a night; "
     f"models cheaper in {MONTHS16} of 8 months, but over the limit.", size=10.5, color=MUTED)

# --- Build: the nightly command and the tests (src/nightly.py, tests/)
s = frame("b_nightly", "What does the nightly command do, and is it tested?",
          f"One command reads the frozen run-1 choice, checks its fingerprints and prints each hotel's oversell for 14 nights; "
          f"{N_TESTS} automated tests pass",
          "src/nightly.py · outputs/nightly_recommendations.csv (+ .manifest.json) · tests/test_contract.py, test_features.py, test_nightly.py",
          "As Build Lead I turned the frozen choice into one command the revenue manager could run each morning. It reads "
          "models/frozen_choice.json, refuses to run if the model or preprocessor file has changed since the freeze, never retrains and "
          "never reads the cancellation outcome. For each hotel and night it prints the bookings on the books, the flat rule's expected "
          "cancellations and its oversell, with CatBoost's alongside for comparison, and saves a CSV with a manifest of fingerprints. The "
          f"replay from 18 August 2017 scored {NMAN['bookings_scored']:,} bookings. {N_TESTS} automated tests pass: five on the scoring "
          "contract, four on the input columns, three on the nightly command, including that it reproduces notebook 14's predictions and "
          "refuses a changed model file. Two limits remain: the data is the final book, not a morning snapshot, so this is a replay, not a "
          "live forecast; and there is no 'as of' booking filter yet.")
box(s, 0.6, 2.3, 5.3, 0.75, INK, radius=0.08)
text(s, 0.8, 2.3, 4.95, 0.75, "python src/nightly.py --from 2017-08-18 --nights 14", size=12.5, font=MONO, color=PAPER, anchor=MSO_ANCHOR.MIDDLE)
steps = [("Checks", f"model and preprocessor SHA-256 against {Path(NMAN['freeze_file']).name} (frozen {NMAN['frozen_at'][11:16]})"),
         ("Never", "fits, tunes or recalibrates; never reads is_canceled"),
         ("Prints", f"per hotel and night: on the books, flat-rule oversell (City {BUFFERS['City Hotel']}, Resort {BUFFERS['Resort Hotel']}), CatBoost alongside"),
         ("Saves", "outputs/nightly_recommendations.csv and a manifest of fingerprints")]
for i, (head, body) in enumerate(steps):
    y = 3.2 + i * 0.52
    text(s, 0.6, y, 0.9, 0.45, head, size=11.5, bold=True, color=ORANGE)
    text(s, 1.5, y, 4.4, 0.48, body, size=10.5, color=MUTED)
box(s, 0.6, 5.55, 5.3, 1.15, PAPER, radius=0.06, line=WARN)
text(s, 0.85, 5.63, 4.85, 1.0, [[("Limits", {"bold": True, "color": WARN})],
                                [("Historical replay on final-book data, not a live forecast; no 'as of' booking filter; serves the run-1 "
                                  "freeze from notebooks 13–14.", {"color": MUTED})]], size=11, space_after=3)
text(s, 6.2, 2.3, 6.55, 0.28, f"ITS OUTPUT, FIRST 7 OF 14 NIGHTS · {NMAN['bookings_scored']:,} BOOKINGS SCORED", size=11, color=ORANGE, bold=True)
city, resort = NIGHTLY[NIGHTLY["hotel"] == "City Hotel"].head(7), NIGHTLY[NIGHTLY["hotel"] == "Resort Hotel"].head(7)
rows = [["Arrival", "City: on books", "expected", "Oversell", "Resort: on books", "expected", "Oversell"]]
for (_, c), (_, r) in zip(city.iterrows(), resort.iterrows()):
    rows.append([f"{c['arrival_date']:%a %d %b}", f"{c['bookings']}", f"{c['flat_expected']:.1f}", f"{c['flat_oversell']}",
                 f"{r['bookings']}", f"{r['flat_expected']:.1f}", f"{r['flat_oversell']}"])
table(s, 6.2, 2.6, rows, [1.1, 1.0, 0.85, 0.9, 1.05, 0.8, 0.85], row_h=0.3, size=11, align={j: PP_ALIGN.RIGHT for j in range(1, 7)},
      bolds={(r, c): True for r in range(1, 8) for c in (3, 6)})
TEST_WHAT = {"test_contract.py": "nightly totals, too few and too many oversold, period dates, bad inputs refused",
             "test_features.py": "only the 8 approved inputs; outcome fields and country never used; no silent fills",
             "test_nightly.py": "buffer per hotel; reproduces notebook 14's predictions; refuses a changed model file"}
rows = [["Test file", "Tests", "What they check"]] + [[f, str(n), TEST_WHAT[f]] for f, n in TEST_FILES.items()]
table(s, 6.2, 5.15, rows, [1.65, 0.6, 4.3], row_h=0.41, size=10, bolds={(r, 0): True for r in range(1, 4)}, align={1: PP_ALIGN.RIGHT})

# ============================================================ 12. Reorder, then check (source slides 5 and 6 are each replaced by two slides)
ids = prs.slides._sldIdLst
for el in list(ids):
    ids.remove(el)
for _old in (5, 6, 7, 8, 10, 11, 12):  # 5 and 6 are replaced; 7, 8, 10, 11 and 12 report notebooks/pipeline results
    prs.part.drop_rel(OLD_IDS[_old].get(qn("r:id")))
for key, _, _ in ORDER:
    ids.append(OLD_IDS[key] if isinstance(key, int) else NEW[key])

assert len(prs.slides) == len(ORDER) == 26


# ============================================================ 13. One type scale for every slide (readability)
# 10 pt only for page furniture (source line, page number, lead chips); content is never below 11 pt.
def snap(pt, furniture=False):
    if furniture:
        return 10.0
    for upper, size in [(11.0, 11.0), (12.5, 12.0), (15.0, 14.0), (17.0, 17.0), (20.0, 20.0), (26.0, 24.0)]:
        if pt <= upper:
            return size
    return pt  # titles (30) and the cover's large type stay as designed


def is_furniture(sh):
    t = sh.text_frame.text.strip() if sh.has_text_frame else ""
    return (sh.name.startswith("Lead tracker") or t.startswith("Source: ") or
            (t.isdigit() and sh.left / 914400 > 11 and sh.top / 914400 > 6.9))


for s in prs.slides:
    for sh in s.shapes:
        frames = [sh.text_frame] if sh.has_text_frame else []
        if sh.has_table:
            frames += [c.text_frame for row in sh.table.rows for c in row.cells]
        furniture = is_furniture(sh)
        for tf in frames:
            for para in tf.paragraphs:
                for r in para.runs:
                    if r.font.size is not None:
                        r.font.size = Pt(snap(r.font.size.pt, furniture))
        if sh.has_chart:
            ch = sh.chart
            ch.font.size = Pt(max(11.0, snap(ch.font.size.pt if ch.font.size else 11.0)))
            plot = ch.plots[0]
            if plot.has_data_labels:
                plot.data_labels.font.size = ch.font.size
            try:
                ch.category_axis.tick_labels.font.size = ch.font.size
            except (ValueError, AttributeError):
                pass
sizes = {r.font.size.pt for s in prs.slides for sh in s.shapes if sh.has_text_frame
         for para in sh.text_frame.paragraphs for r in para.runs if r.font.size}
assert sizes <= {10.0, 11.0, 12.0, 14.0, 17.0, 20.0, 24.0, 30.0, 40.0, 44.0}, sorted(sizes)
for n, s in enumerate(prs.slides, 1):
    if n in (1, len(ORDER)):
        continue
    nums = [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip().isdigit()
            and sh.left / 914400 > 11 and sh.top / 914400 > 6.9]
    assert nums == [str(n)], (n, nums)
    alltext = " ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
    assert "Blocked" not in alltext and "11 automated tests" not in alltext
prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
