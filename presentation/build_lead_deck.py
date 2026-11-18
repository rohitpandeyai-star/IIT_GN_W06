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
    ("ns_night", "CLIENT LEAD · NORTH STAR", ["Client"]),
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
    (6, "DATA + MODEL LEAD · ENCODING AND SETTINGS", ["Data", "Model"]),
    (7, "MODEL LEAD · MODELS TRIED", ["Model"]),
    (11, "MODEL LEAD · PROBABILITY QUALITY", ["Model"]),
    (8, "MODEL LEAD · RULES TRIED", ["Model"]),
    (9, "MODEL LEAD · EARLIER EXPERIMENTS", ["Model"]),
    (10, "MODEL LEAD · THE CHOICE", ["Model"]),
    (12, "BUILD LEAD · ENGINEERING", ["Build"]),
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
RATES = json.loads((ROOT / "models" / "frozen_choice.json").read_text())["flat_rule_hotel_rates_from_train"]
FROZEN = json.loads((ROOT / "evidence" / "choose_policy_selection" / "frozen_configuration.json").read_text())
MARGIN = 17
assert "17" in json.dumps(FROZEN), "the pipeline's frozen rule should be the flat rule with margin 17"

# One night under the deck's selected rule: ceil(hotel rate x bookings) - 17, never below 0 (validation nights).
nights = contract.nightly_table(choose[contract.REQUIRED], choose["hotel"].map(RATES).to_numpy())
k_all = np.maximum(np.ceil(nights["expected"].to_numpy()) - MARGIN, 0)
choose_score = contract.night_cost(nights, k_all)
assert round(choose_score["cost_eur"]) == 2414409 and choose_score["walks_per_1000"] == 9.06  # as notebook pipeline/11
none_score = contract.night_cost(nights, np.zeros(len(nights)))


def night(hotel, date):
    r = nights.loc[(hotel, pd.Timestamp(date))]
    k = max(np.ceil(r["expected"]) - MARGIN, 0)
    empty, walks = max(r["cancelled"] - k, 0), max(k - r["cancelled"], 0)
    return {"hotel": hotel, "date": pd.Timestamp(date), "book": int(r["book"]), "expected": r["expected"], "k": int(k),
            "cancelled": int(r["cancelled"]), "empty": int(empty), "walks": int(walks), "value": r["stay_value"],
            "cost": empty * r["stay_value"] + walks * contract.WALK_COST}


EXAMPLES = [night("City Hotel", "2016-07-04"), night("City Hotel", "2016-07-30"), night("Resort Hotel", "2016-07-05")]

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


def bar_chart(slide, x, y, w, h, categories, values, highlight=None, fmt="0.0%", horizontal=True, maximum=None, size=11):
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
        pt.format.fill.fore_color.rgb = rgb(ORANGE)
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
assert replace_in_runs(OLD[10], "earlier runs (slide 9)", f"earlier runs (slide {POS[9]})") == 1
assert replace_in_runs(OLD[1], "which slide 9 reports in full", f"which slide {POS[9]} reports in full") == 1

eng = OLD[12]  # src/nightly.py was rewired and tests/test_nightly.py added after the source deck was built
set_text(find(eng, lambda t: t.startswith("The analysis reproduces end to end")),
         "The analysis reproduces end to end; the nightly command now runs, but serves the earlier per-hotel rule")
set_text(find(eng, lambda t: t == "11 automated tests pass"), "12 automated tests pass")
set_text(find(eng, lambda t: t.startswith("scoring rule, nightly aggregation")), "scoring rule, nightly command, feature schema")
set_text(find(eng, lambda t: t == "Nightly command stops"), "Nightly command runs")
set_text(find(eng, lambda t: t.startswith("its model file uses the excluded")),
         "but it serves the earlier per-hotel rule (20 / 4), not this 17-room rule")
status = find(eng, lambda t: t == "Blocked")
set_text(status, "Partly")
status.text_frame.paragraphs[0].runs[0].font.color.rgb = rgb(WARN)
for sh in eng.shapes:
    if sh.shape_type == 1 and abs(sh.left / 914400 - 7.05) < 0.01 and abs(sh.top / 914400 - 4.27) < 0.01:
        sh.fill.fore_color.rgb = rgb(WARN)
set_text(find(eng, lambda t: t.startswith("Source: evidence/pipeline_run")),
         "Source: evidence/pipeline_run/run_manifest.json · tests/ · src/nightly.py · tests/test_nightly.py · docs/COMPARISON.md")
eng.notes_slide.notes_text_frame.text = (
    "All ten pipeline notebooks run in order with no errors; each later notebook reads the earlier one's saved choice, so nothing is "
    "copied by hand. 12 automated tests pass (contract, nightly command, feature schema). Data, code and 49 evidence files are "
    "fingerprinted. The nightly command, python src/nightly.py --from 2017-08-18 --nights 14, now runs: it checks the frozen files' "
    "fingerprints, never retrains, never reads outcomes, and prints a table per hotel and night. But it serves the run-1 freeze from "
    "notebooks 11-16 (the flat rule with City 20 / Resort 4, CatBoost alongside), not this deck's 17-room rule, so wiring the selected "
    "rule into it is still to do. It also has no 'as of' filter, so it would score bookings not yet made on the decision morning. The "
    "independent AI benchmark branch was never created, so no AI comparison is claimed.")

# ============================================================ 2. North star 1: what are we trying to find out?
s = frame("ns_question", "What are we trying to find out?",
          "Can a cancellation forecast set each night's oversell more cheaply than the flat rule, without walking more guests?",
          "BRIEF.md · docs/CHARTER.md · docs/EVALUATION_CONTRACT.md",
          "Start with the client's own words. Every morning the revenue manager decides, for each hotel and each of the next 14 nights, how "
          "many rooms to sell beyond capacity. Today that number comes from a flat rule: the hotel's average cancellation rate times the "
          "night's bookings, less a safety margin. So we have to find out three things: how many of tonight's bookings will cancel; how to "
          "turn that into one whole number of rooms; and whether that number is better than today's rule, in euros, without walking more "
          "guests than the brand allows. The right-hand side is one real morning, worked through on the next slides.")
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
text(s, 7.35, 2.3, 5.4, 0.3, f"ONE MORNING · {e['hotel'].upper()} · ARRIVALS ON {e['date']:%a %d %b %Y}".upper(), size=11, color=ORANGE, bold=True)
steps = [("On the books", f"{e['book']} bookings due to arrive"),
         ("Expected to cancel", f"{e['book']} × {RATES[e['hotel']]:.1%} = {e['expected']:.1f}, rounded up to {int(np.ceil(e['expected']))}"),
         ("Decision", f"oversell {e['k']} rooms  ({int(np.ceil(e['expected']))} − {MARGIN} safety rooms)"),
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

# ============================================================ 4. North star 3: one night in euros
s = frame("ns_night", "What does one night look like in euros?",
          "Each night the rule can miss in one of two directions; the north star adds those misses over every night",
          "src/contract.py (nightly_table, night_cost) · data/hotels_clean.pkl (validation nights) · notebooks/pipeline/11_choose_policy_selection.ipynb",
          "Three real nights from the validation period, scored with the rule this deck selects: the hotel's rate times the night's "
          "bookings, rounded up, minus 17 rooms. On the first night 30 guests cancelled but we only oversold 22, so 8 rooms stood empty at "
          "about 440 euros each. On the second, only 27 cancelled but we had oversold 43, so 16 guests were walked at 300 euros. On the "
          "third, a small Resort night, the 17-room margin swallowed the whole forecast, so we oversold nothing and 3 rooms stood empty at "
          "869 euros each: one shared margin is too big for a small hotel. Add up all 368 nights and this rule cost 2.41 million euros "
          "with 9.06 walks per 1,000; selling nothing extra would have cost 4.16 million.")
tags = [("Too few oversold", BLUE), ("Too many oversold", ORANGE), ("Margin too big for a small night", CRIT)]
for i, (e, (tag, color)) in enumerate(zip(EXAMPLES, tags)):
    x = 0.6 + i * 4.1
    box(s, x, 2.3, 3.85, 3.65, TINT, radius=0.04)
    box(s, x + 0.25, 2.5, 3.35, 0.36, color, radius=0.5, label=tag, size=11, color=PAPER, bold=True)
    text(s, x + 0.25, 3.0, 3.4, 0.3, f"{e['hotel']} · {e['date']:%a %d %b %Y}", size=14, font=HEAD, bold=True)
    lines = [("On the books", f"{e['book']} bookings"),
             ("Expected", f"{e['book']} × {RATES[e['hotel']]:.1%} = {e['expected']:.1f} → {int(np.ceil(e['expected']))}"),
             ("Oversold", f"{int(np.ceil(e['expected']))} − {MARGIN} = {e['k']}" if e["k"] > 0 else f"{int(np.ceil(e['expected']))} − {MARGIN} → 0"),
             ("Cancelled", f"{e['cancelled']}"),
             ("Empty rooms", f"{e['empty']}" + (f" × {eur(e['value'])}" if e["empty"] else "")),
             ("Walked", f"{e['walks']}" + (" × €300" if e["walks"] else ""))]
    for j, (a, b) in enumerate(lines):
        y = 3.45 + j * 0.34
        text(s, x + 0.25, y, 1.4, 0.3, a, size=12, color=MUTED)
        text(s, x + 1.6, y, 2.05, 0.3, b, size=12, bold=a in ("Oversold",), align=PP_ALIGN.RIGHT)
    text(s, x + 0.25, 5.53, 1.4, 0.32, "Night cost", size=13, bold=True)
    text(s, x + 1.6, 5.53, 2.05, 0.32, eur(e["cost"]), size=15, font=HEAD, bold=True, color=color, align=PP_ALIGN.RIGHT)
box(s, 0.6, 6.15, 12.15, 0.65, PEACH, radius=0.1)
text(s, 0.85, 6.2, 11.7, 0.55, [[("Over all 368 validation nights: ", {"bold": True}),
                                 (f"this rule cost {eur(choose_score['cost_eur'])} with {choose_score['walks_per_1000']:.2f} walks per 1,000; "
                                  f"selling nothing extra would have cost {eur(none_score['cost_eur'])}. That gap is what the north star chases.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================ 5. Roadmap: who did what, in which order
s = frame("roadmap", "In what order was the work done, and by which lead?",
          "Four roles in turn: frame the decision, prepare the data, choose the rule, build it, close with the client",
          "docs/ROLES.md · docs/CHARTER.md",
          "This deck follows the order in which the work was done. As Client Lead I set the north star and framed the decision: one number "
          "per hotel-night, the two costs and the walk limit. As Data Lead I profiled and cleaned the data, chose the columns by when the "
          "hotel knows them, and encoded them on Train only. As Model Lead I tried probability models, checked their calibration and the "
          "uncertainty of a night's count, chose an overbooking rule within the walk limit, froze it, and tested it on 2017. As Build Lead "
          "I made it reproducible and testable, with one nightly command. And as Client Lead again I close with the limits and next steps. "
          "All four roles were mine.")
client1 = [k for k, _, a in ORDER if a == ["Client"] and k != 13] + [3]
data = [k for k, _, a in ORDER if "Data" in a and k != "roadmap"]
model = [k for k, _, a in ORDER if "Model" in a and k != "roadmap"]
stages = [("CLIENT LEAD", "What is decided, for whom, at what cost per wrong call?",
           ["North star and guardrail", "The decision and its two costs", "Check the brief's numbers"], slide_range(client1)),
          ("DATA LEAD", "What did the hotel know on the decision morning?",
           ["Profile and clean the data", "Choose columns by timing", "Encode them on Train only"], slide_range(data)),
          ("MODEL LEAD", "How many will cancel tonight, and how sure are we?",
           ["Try models, calibrate", "Measure nightly uncertainty", "Choose a rule within the limit", "Freeze, then test once"],
           slide_range(model)),
          ("BUILD LEAD", "What could the revenue manager use tomorrow morning?",
           ["Reproduce end to end", "Automated tests", "The nightly command"], slide_range([12])),
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
     f"slides {shared[0]} and {shared[1]} are hand-overs between two leads.", size=11, color=MUTED)

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


def reason_card(s, x, y, w, h, test, question, reason, examples, verdict_line, color):
    box(s, x, y, w, h, TINT, radius=0.04)
    box(s, x, y, 0.1, h, color, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.3, y + 0.15, w - 0.5, 0.28, f"T{test} · {TEST_NAMES[test].upper()}" if test else "PASSED ALL FOUR", size=11, color=ORANGE, bold=True)
    text(s, x + 0.3, y + 0.45, w - 0.5, 0.4, question, size=15, font=HEAD, bold=True)
    text(s, x + 0.3, y + 0.9, w - 0.5, h - 1.6, reason, size=12, color=INK)
    text(s, x + 0.3, y + h - 0.72, w - 0.5, 0.3, examples, size=10.5, color=MUTED)
    text(s, x + 0.3, y + h - 0.38, w - 0.5, 0.28, verdict_line, size=11, bold=True, color=color)


LEGEND = [("✓ yes   ", {"color": GOOD, "bold": True}), ("? unsure   ", {"color": WARN, "bold": True}), ("✗ no     ", {"color": CRIT, "bold": True}),
          ("each column sits on the slide of the first test it does not clearly pass; orange headers mark this slide's tests", {"color": MUTED})]

s = frame("col_t12", "Which columns are the outcome, or not yet known that morning?",
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
reason_card(s, 7.35, 2.3, 5.4, 2.1, 1, "Is it the outcome, or written because of it?",
            "A value recorded because a booking cancelled, no-showed or stayed hands the model the answer; it predicts brilliantly and is useless on the morning.",
            "status and its date · assigned room · price and deposit (posted up to the outcome)", "→ never an input", CRIT)
reason_card(s, 7.35, 4.55, 5.4, 2.2, 2, "Does the hotel have it on the decision morning?",
            "Some values only arrive at check-in or later, or their timing is not recorded. A cancelled booking never reaches check-in, so a late value differs because of the outcome.",
            "country (corrected at check-in) · booking changes · parking · waiting list · company · customer type", "→ excluded; company used provisionally", WARN)
text(s, 0.6, 6.85, 12.15, 0.22, [LEGEND], size=10)

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
reason_card(s, 7.35, 2.3, 5.4, 2.6, 3, "Is the value still the one the hotel had that morning?",
            "The file keeps each booking's last value from its change log. Kept bookings keep changing until check-in; cancelled ones freeze at cancellation. The value differs because of the outcome.",
            "stay length · adults, children, babies · meal · reserved room · special requests (and nights, guests built from them)",
            "→ firm 'no': excluded", CRIT)
reason_card(s, 7.35, 5.05, 5.4, 1.7, 3, "Unsure: counts of earlier bookings",
            "Earlier bookings counted here could be cancelled after the morning.",
            "is_repeated_guest · previous cancellations · previous bookings", "→ used provisionally, doubt on record", WARN)
text(s, 0.6, 6.85, 12.15, 0.22, [LEGEND], size=10)

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
reason_card(s, 7.35, 2.3, 5.4, 2.1, 4, "Is it about this booking alone?",
            "A value built by comparing rows sees bookings made after the morning, including the test period.",
            "fails: the identical-group cleaning flag · unsure: customer type (links to other bookings)", "→ every column shown here: yes", GOOD)
reason_card(s, 7.35, 4.55, 5.4, 2.2, 0, "Set once, when the booking is made",
            "Which hotel, how it was sold, through which channel and agent, how far ahead and for which night: none can change later.",
            "inputs: hotel · market_segment · distribution_channel · agent", "→ 4 inputs; 6 safe but not in the input set", BLUE)
text(s, 0.6, 6.85, 12.15, 0.22, [LEGEND[:3] + [("the 10 cleaning flags inherit their source column's answers; all are excluded", {"color": MUTED})]], size=10)

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
    cx, cy = x + 0.2, y + 0.88
    for c in cols:
        label = c.replace("flag_", "") if c in FLAGS else c
        cw = max(0.45, 0.2 + 0.062 * len(label))
        if cx + cw > x + 3.75:
            cx, cy = x + 0.2, cy + 0.3
        box(s, cx, cy, cw, 0.24, PAPER, radius=0.5, line=color, label=label, size=8.5, color=INK)
        cx += cw + 0.06

# ============================================================ 11. Columns 7: tempting traps
s = frame("col_traps", "Which excluded columns look useful, but are traps?",
          "Their patterns are too clean to be true: each is shaped by what happened after the decision morning",
          "data/hotels_clean.pkl (deposit: all bookings; parking and country: Train) · notebooks/06 and 07 · Antonio, de Almeida & Nunes (2019)",
          "These three would make any model look brilliant, which is exactly the warning. Non Refund bookings cancel 99 percent of the "
          "time, the opposite of what the label promises; the deposit type is computed from payments up to arrival or cancellation, so the "
          "cancellation itself can create the label. Not one guest with a parking space cancelled; parking is most likely registered on "
          "arrival, which only guests who stay reach. And Portuguese bookings cancel far more than others; the paper warns that "
          "nationality is often corrected at check-in, which cancelled bookings never reach. None of these rates was used to choose "
          "columns: notebook 06 never read an outcome. They show why timing, not score, has to decide.")
dep_order = ["No Deposit", "Non Refund", "Refundable"]
country = COUNTRY.reset_index()
charts = [("deposit_type", "Cancelled, by deposit type (all bookings)", dep_order, [float(DEPOSIT[k]) for k in dep_order], [1],
           "Likely set by payments up to the cancellation itself"),
          ("required_car_parking_spaces", f"Cancelled, Train ({PARKING_N:,} with parking)", list(PARKING), [float(v) for v in PARKING.values()],
           [0], "Probably recorded on arrival, which only stays reach"),
          ("country", "Cancelled, five largest countries (Train)", list(country["country"]), [float(v) for v in country["mean"]], [0],
           "Nationality is often corrected at check-in")]
for i, (col, cap, cats, vals, hl, why) in enumerate(charts):
    x = 0.6 + i * 4.1
    box(s, x, 2.3, 3.9, 4.45, TINT, radius=0.04)
    text(s, x + 0.2, 2.42, 3.5, 0.32, col, size=13, font=MONO, bold=True)
    text(s, x + 0.2, 2.78, 3.5, 0.28, cap, size=10.5, color=MUTED)
    bar_chart(s, x + 0.1, 3.1, 3.7, 2.55, cats, vals, highlight=hl, maximum=1.15, size=10.5)
    box(s, x + 0.2, 5.82, 3.5, 0.75, PAPER, radius=0.1, label=why, size=11, color=CRIT, bold=True)

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

# ============================================================ 12. Reorder, then check (source slide 5 is replaced by the two cleaning slides)
ids = prs.slides._sldIdLst
for el in list(ids):
    ids.remove(el)
prs.part.drop_rel(OLD_IDS[5].get(qn("r:id")))
for key, _, _ in ORDER:
    ids.append(OLD_IDS[key] if isinstance(key, int) else NEW[key])

assert len(prs.slides) == len(ORDER) == 26
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
