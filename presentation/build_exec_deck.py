"""Rebuild Hotel_Overbooking_Deck_By_Lead.pptx as a decision-ready deck: Part A main story, Part B technical appendix.

Every table, chart value, caveat, source line and speaker note of the source deck is carried over: tables, chart data and
notes are read from the source file itself, so numbers keep their original formatting. The script ends by checking that
every number written on a source slide appears somewhere in the new deck, and writes the slide map to
PRESENTATION_EXEC_MAPPING.md.

Run from the repository root:
    python presentation/build_exec_deck.py [source.pptx] [out.pptx]
"""
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Hotel_Overbooking_Deck_By_Lead.pptx"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Hotel_Overbooking_Executive_Deck.pptx"

# ---- palette: one accent for the recommended option, greys for the rest, red/amber only for breaches and risks
INK, BODY_C, MUTED, SOFT, RULE, TINT, PAPER = "1B2430", "2E3A46", "5C6873", "8B96A0", "D8DDE2", "F3F5F7", "FFFFFF"
ACCENT, ACCENT_TINT = "1F5FBF", "E3ECF9"          # the recommended rule: flat rule, 17-room margin
ALT, ALT_LIGHT = "6B7682", "B8C0C8"                # every alternative
RED, RED_TINT, AMBER, AMBER_TINT = "C0392B", "F8E1DE", "A86A00", "F6ECD6"
FONT, HEADF = "Calibri", "Calibri"

src = Presentation(SRC_PATH)
assert len(src.slides) == 27, len(src.slides)
CHIPS = {"Client", "Data", "Model", "Build"}


def s_texts(n):
    return [sh.text_frame.text.strip() for sh in src.slides[n - 1].shapes
            if sh.has_text_frame and sh.text_frame.text.strip() and sh.text_frame.text.strip() not in CHIPS]


def s_table(n, k=0):
    tables = [sh.table for sh in src.slides[n - 1].shapes if sh.has_table]
    return [[c.text for c in r.cells] for r in tables[k].rows]


def s_chart(n, k=0):
    charts = [sh.chart for sh in src.slides[n - 1].shapes if sh.has_chart]
    plot = charts[k].plots[0]
    return list(plot.categories), [(se.name, list(se.values)) for se in plot.series]


def s_notes(n):
    return src.slides[n - 1].notes_slide.notes_text_frame.text


def s_source(n):
    return next(t for t in s_texts(n) if t.startswith("Source:"))[len("Source: "):]


def has(n, fragment):
    assert any(fragment in t for t in s_texts(n)), (n, fragment)
    return fragment


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
MAP = {}          # new slide number -> list of source slide numbers it carries
INDEX = []        # (code, number, topic) for the appendix index


def rgb(h):
    return RGBColor.from_string(h)


def text(slide, x, y, w, h, paras, size=13, color=BODY_C, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         italic=False, space_after=0, font=FONT):
    assert size >= 10, size
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate([paras] if isinstance(paras, str) else paras):
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


def box(slide, x, y, w, h, fill=None, line=None, radius=None, label=None, size=12, color=BODY_C, bold=False,
        align=PP_ALIGN.CENTER, shape=None, lw=1.25):
    kind = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE)
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(lw)
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
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), bold, rgb(color)
    return s


def line(slide, x1, y1, x2, y2, color=SOFT, width=1.5, dash=False, head=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    if dash:
        ln.append(ln.makeelement(qn("a:prstDash"), {"val": "dash"}))
    if head:
        ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
    return c


NUMERIC = re.compile(r"^[\s€+\-−–0-9.,%/×→()kM≈<>≤]+$|^—$")


def table(slide, x, y, rows, widths, row_h=0.36, size=12, key_rows=(), right=None, bold_first=True, fills=None, colors=None):
    assert size >= 12
    gf = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * len(rows)))
    tbl = gf.table
    for c, w in enumerate(widths):
        tbl.columns[c].width = Inches(w)
    # right-align numeric columns (decided from the body cells)
    if right is None:
        right = {c for c in range(len(rows[0])) if c > 0 and all(NUMERIC.match(r[c].strip() or "—") for r in rows[1:])}
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(row_h)
        for c, value in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.07)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            head = r == 0
            fill = INK if head else (ACCENT_TINT if r in key_rows else (PAPER if r % 2 else TINT))
            fill = (fills or {}).get((r, c), fill)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(fill)
            p = cell.text_frame.paragraphs[0]
            cell.text_frame.word_wrap = True
            p.alignment = PP_ALIGN.RIGHT if c in right else PP_ALIGN.LEFT
            run = p.add_run()
            run.text = str(value)
            run.font.name, run.font.size = FONT, Pt(size)
            run.font.bold = head or r in key_rows or (bold_first and c == 0)
            run.font.color.rgb = rgb((colors or {}).get((r, c), PAPER if head else INK))
    return tbl


def pill(slide, x, y, label, fill, color, w=None, size=10.5, bold=True, line_c=None):
    w = w or (0.22 + 0.075 * len(label))
    box(slide, x, y, w, 0.27, fill, line=line_c, radius=0.5, label=label, size=size, color=color, bold=bold)
    return x + w + 0.08


CONF_STYLE = {"High": (PAPER, INK), "Medium": (PAPER, INK), "Low": (PAPER, INK)}
NAV = ["Data", "Inputs", "Probability", "Oversell rule", "Cost", "Walk limit"]


def frame(code, title, roles=(), conf=None, source="", foot="", sowhat=None, notes="", nav=None, carries=(), topic=None,
          part="A"):
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, 13.333, 7.5, PAPER)
    n = len(prs.slides._sldIdLst)
    x = pill(s, 0.55, 0.3, f"{code} · {'MAIN STORY' if part == 'A' else 'APPENDIX'}", INK if part == "A" else ALT, PAPER)
    for r in roles:
        x = pill(s, x, 0.3, r, TINT, MUTED, bold=False)
    if nav is not None:  # the process diagram (A4), reused as a small step strip
        nx = 6.2
        for i, step in enumerate(NAV):
            on = i in (nav if isinstance(nav, (list, tuple)) else [nav])
            nx = pill(s, nx, 0.3, step, ACCENT if on else TINT, PAPER if on else SOFT, bold=on, size=10)
    if conf:
        box(s, 11.05, 0.3, 1.73, 0.27, PAPER, line=INK if conf == "High" else (ALT if conf == "Medium" else AMBER), radius=0.5,
            label=f"Evidence: {conf}", size=10.5, color=INK if conf != "Low" else AMBER, bold=True)
    text(s, 0.55, 0.68, 12.25, 1.0, title, size=24, color=INK, bold=True, font=HEADF, anchor=MSO_ANCHOR.TOP)
    if sowhat:
        box(s, 0.55, 5.98, 0.08, 0.58, ACCENT)
        box(s, 0.63, 5.98, 12.15, 0.58, TINT)
        text(s, 0.8, 5.98, 11.9, 0.58, [[("So what  ", {"bold": True, "color": ACCENT}), (sowhat, {})]], size=13,
             anchor=MSO_ANCHOR.MIDDLE)
    if source:
        text(s, 0.55, 6.7, 11.6, 0.28, "Source: " + source, size=10.5, color=SOFT)
    if foot:
        text(s, 0.55, 6.97, 11.6, 0.3, foot, size=10.5, color=SOFT, italic=True)
    text(s, 12.25, 6.97, 0.55, 0.3, str(n), size=10.5, color=SOFT, align=PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = notes + "".join(
        f"\n\n[Original slide {c}] {s_notes(c)}" for c in carries if c not in CARRIED)
    CARRIED.update(carries)
    MAP[n] = list(carries)
    if part == "B":
        INDEX.append((code, n, topic or title))
    return s


CARRIED = set()


def hbars(s, x, y, w, rows, vmax, label_w=2.7, bar_h=0.34, gap=0.17, ref=None, fmt=None, size=12, value_w=1.9, vmin=0.0):
    """Horizontal bars or ranges. rows: dict(label, value | (lo, hi), color, text, sub)."""
    plot_x, plot_w = x + label_w, w - label_w - value_w
    X = lambda v: plot_x + plot_w * (v - vmin) / (vmax - vmin)
    for i, r in enumerate(rows):
        yy = y + i * (bar_h + gap)
        text(s, x, yy - 0.02, label_w - 0.12, bar_h + 0.06, [[(r["label"], {"bold": r.get("bold", False)})]] +
             ([[(r["sub"], {"size": 10.5, "color": MUTED})]] if r.get("sub") else []), size=size, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.RIGHT)
        v = r["value"]
        if isinstance(v, tuple):
            box(s, X(v[0]), yy + 0.04, max(X(v[1]) - X(v[0]), 0.04), bar_h - 0.08, r.get("color", ALT_LIGHT), radius=0.4)
            end = X(v[1])
        elif v is None:
            end = X(vmin)
        else:
            box(s, X(vmin), yy, max(X(v) - X(vmin), 0.02), bar_h, r.get("color", ALT_LIGHT))
            end = X(v)
        if r.get("text"):
            text(s, end + 0.08, yy - 0.02, value_w + plot_w - (end - plot_x), bar_h + 0.06,
                 [[(r["text"], {"bold": r.get("bold", False), "color": r.get("text_color", INK)})]], size=size,
                 anchor=MSO_ANCHOR.MIDDLE)
    if ref:
        rv, rl, rc = ref
        top, bottom = y - 0.15, y + len(rows) * (bar_h + gap) - gap + 0.1
        line(s, X(rv), top, X(rv), bottom, color=rc, width=2, dash=True)
        text(s, X(rv) - 1.2, bottom + 0.02, 2.4, 0.28, rl, size=11, color=rc, bold=True, align=PP_ALIGN.CENTER)
    return X


def key_numbers(s, y, items, x=0.55, w=12.25, h=0.95):
    cw = w / len(items)
    for i, (value, label, accent) in enumerate(items):
        xx = x + i * cw
        box(s, xx, y, cw - 0.15, h, ACCENT_TINT if accent else TINT, radius=0.06)
        text(s, xx + 0.18, y + 0.08, cw - 0.45, 0.5, value, size=24, bold=True, color=ACCENT if accent else INK)
        text(s, xx + 0.18, y + 0.56, cw - 0.45, 0.4, label, size=12, color=MUTED)


def card(s, x, y, w, h, head, body, tag=None, tag_color=ACCENT, fill=TINT, size=13, head_size=14):
    box(s, x, y, w, h, fill, radius=0.05)
    yy = y + 0.14
    if tag:
        text(s, x + 0.2, yy, w - 0.4, 0.26, tag.upper(), size=11, color=tag_color, bold=True)
        yy += 0.3
    text(s, x + 0.2, yy, w - 0.4, 0.4, head, size=head_size, bold=True, color=INK)
    text(s, x + 0.2, yy + 0.4, w - 0.4, h - (yy - y) - 0.45, body, size=size, color=BODY_C)


def bullets(s, x, y, w, h, items, size=13, gap=6):
    text(s, x, y, w, h, [[("▪  ", {"color": ACCENT, "bold": True}), (t, {})] if isinstance(t, str) else
                         [("▪  ", {"color": ACCENT, "bold": True})] + t for t in items], size=size, space_after=gap)


def flow(s, x, y, steps, w_box, h_box, gap, fills=None, size=12, head_size=12):
    """A left-to-right step flow with arrows. steps: (head, body)."""
    for i, (head, body) in enumerate(steps):
        xx = x + i * (w_box + gap)
        f = (fills or {}).get(i, TINT)
        box(s, xx, y, w_box, h_box, f, radius=0.08)
        text(s, xx + 0.12, y + 0.1, w_box - 0.24, 0.35, head, size=head_size, bold=True,
             color=PAPER if f in (ACCENT, INK) else INK, align=PP_ALIGN.CENTER)
        text(s, xx + 0.12, y + 0.48, w_box - 0.24, h_box - 0.55, body, size=size,
             color=PAPER if f in (ACCENT, INK) else BODY_C, align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            line(s, xx + w_box + 0.03, y + h_box / 2, xx + w_box + gap - 0.03, y + h_box / 2, color=SOFT, width=2, head=True)


# ======================================================================================================== PART A
# ---- A0 title
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 7.5, INK)
t1 = s_texts(1)
text(s, 0.7, 0.6, 12, 0.3, t1[0], size=12, color="9FB3C8", bold=True)
text(s, 0.7, 1.1, 12, 1.5, "Keep the client's flat rule with a 17-room safety margin: no model-based rule beat it within the walk limit",
     size=32, bold=True, color=PAPER)
text(s, 0.7, 2.75, 12, 0.5, t1[1], size=16, color="C9D4DF", italic=True)
text(s, 0.7, 3.25, 11.8, 0.8, t1[2], size=14, color="C9D4DF")
for i, (v, l) in enumerate([(t1[3], t1[4]), (t1[5], t1[6]), (t1[7], t1[8])]):
    xx = 0.7 + i * 4.0
    box(s, xx, 4.3, 3.75, 1.2, "26323F", radius=0.06)
    text(s, xx + 0.2, 4.38, 3.4, 0.6, v, size=30, bold=True, color=PAPER if i else "8DB6F2")
    text(s, xx + 0.2, 5.0, 3.4, 0.45, l, size=12, color="C9D4DF")
text(s, 0.7, 6.15, 12, 0.35, t1[9], size=14, color=PAPER, bold=True)
text(s, 0.7, 6.55, 12, 0.35, t1[10], size=11, color="9FB3C8")
text(s, 0.7, 6.9, 12, 0.35, "Part A: the decision and its evidence (slides 2–15) · Part B: technical appendix (slides 16 onward)", size=11,
     color="9FB3C8")
s.notes_slide.notes_text_frame.text = f"[Original slide 1] {s_notes(1)}"
CARRIED.add(1)
MAP[1] = [1]

# ---- A1 executive summary
s = frame("A1", "Recommendation: keep the flat rule with a 17-room margin, and confirm any change on new nights before adopting it",
          roles=("Client Lead",), conf="Medium",
          source="evidence/proof_evaluation · evidence/choose_policy_selection · notebooks/pipeline/11–12 · notebooks 12–16 (earlier runs)",
          foot="Choose = Jul–Dec 2016 (settings chosen); Test = Jan–Aug 2017 (retrospective: already examined in earlier runs). Euros are simulated contract costs.",
          sowhat="The client's own rule, with a data-chosen margin, is the cheapest rule that keeps walks under the brand limit; a model adds no value yet.",
          notes="Executive summary. Recommendation first, then the three strongest proof points, the main risk and the decision needed. "
                "Every figure is from the source deck: the 2017 test result and best model rule (original slide 25), the Choose "
                "selection (original slide 23), the per-hotel result (original slides 24 and 25), and the proposed next steps "
                "(original slide 27).")
key_numbers(s, 1.72, [("€3,935,876", "flat rule, 17 rooms · 2017 test · 486 hotel-nights", True),
                      ("6.21", "walks per 1,000 on the test (limit: 10)", True),
                      ("+€236,784", "extra cost of the best model rule, which breached at 11.11", False),
                      ("15 + 5", "probability models · rule families tried", False)])
box(s, 0.55, 2.82, 6.0, 3.0, ACCENT_TINT, radius=0.04)
text(s, 0.75, 2.92, 5.6, 0.28, "THREE STRONGEST PROOF POINTS", size=11, color=ACCENT, bold=True)
proofs = [("High", "Cheapest of 134 rules within the limit on Choose: €2,414,409 at 9.06 walks per 1,000"),
          ("Medium", "On the 2017 test: €3,935,876 at 6.21 walks per 1,000, inside the limit of 10"),
          ("Medium", "Best model-based rule (margin 18) cost €4,172,660 on the same nights and breached at 11.11")]
for i, (c, p) in enumerate(proofs):
    yy = 3.28 + i * 0.83
    box(s, 0.75, yy + 0.02, 0.36, 0.36, ACCENT, shape=MSO_SHAPE.OVAL, label=str(i + 1), size=12, color=PAPER, bold=True)
    text(s, 1.25, yy - 0.02, 4.0, 0.75, p, size=13, color=INK)
    box(s, 5.3, yy + 0.04, 1.1, 0.27, PAPER, line=ALT, radius=0.5, label=c, size=10.5, color=INK, bold=True)
box(s, 6.75, 2.82, 6.05, 1.45, AMBER_TINT, radius=0.04)
text(s, 6.95, 2.92, 5.7, 0.28, "MAIN RISK", size=11, color=AMBER, bold=True)
text(s, 6.95, 3.2, 5.7, 1.05, ["Retrospective, not blind: the 2017 period was already examined in earlier runs.",
                               "Euros are simulated; four inputs have unverified timing."], size=13, space_after=3)
box(s, 6.75, 4.37, 6.05, 1.45, TINT, radius=0.04)
text(s, 6.95, 4.47, 5.7, 0.28, "DECISION NEEDED (PROPOSED, NOT APPROVED)", size=11, color=INK, bold=True)
text(s, 6.95, 4.75, 5.7, 1.05, ["Agree the next steps: booking snapshots, a shadow run on new nights.",
                                "Client view: may margins differ by hotel? (City 20, Resort 4 cost €3.21M at 7.18, seen only on the test)"],
     size=13, space_after=3)

# ---- A2 how to read
s = frame("A2", "How to read this deck: periods, evidence tags and colours are used the same way on every slide",
          roles=(), conf=None, source="src/contract.py (periods) · docs/ROLES.md (roles) · this deck's conventions",
          sowhat="Anything chosen on Choose and shown on Test is marked; the 2017 test is a retrospective check, not a blind test.",
          notes="Reading guide. The three periods are the contract's train, choose and proof periods; this deck calls them Train, Choose "
                "and Test. Evidence tags are a reading of the source's own caveats only: High = measured on the period it was chosen "
                "for, under a rule fixed in advance; Medium = measured, but retrospective or resting on a judgment; Low = seen only "
                "once, after the fact, and needing confirmation. Role tags show which lead owned the work; the deck itself is "
                "organised by the reader's questions.")
rows = [["Term or mark", "Meaning in this deck"],
        ["Train · Choose · Test", "The contract's periods: train (before Jul 2016), choose (Jul–Dec 2016), proof (Jan–Aug 2017)"],
        ["Chosen on Choose, proved on Test", "Every setting was fixed on Train folds or Choose, then scored on Test"],
        ["Retrospective, not blind", "The 2017 Test period was examined in earlier runs before the final pipeline's run"],
        ["Evidence: High / Medium / Low", "High = chosen by a rule fixed in advance and measured on that period; Medium = retrospective or judgment-based; Low = seen once, after the fact"],
        ["Blue", "The recommended rule (flat rule, 17-room margin) or the key number"],
        ["Grey", "Alternatives and baselines, always shown next to the recommendation"],
        ["Red · amber", "Red = a walk-limit breach; amber = a risk or an unverified input"],
        ["Dashed red line", "The guardrail: 10 walked guests per 1,000 arrivals, group-wide"],
        ["Small role tags", "Client, Data, Model or Build Lead: who owned the work (all held by Rohit Pandey)"]]
table(s, 0.55, 1.75, rows, [3.3, 8.95], row_h=0.41, size=12, right=set())

# ---- A3 decision and scoring
t6, t3 = s_texts(6), s_texts(3)
s = frame("A3", "Each night the hotel picks one oversell number; it is scored in euros and rejected if walks exceed 10 per 1,000",
          roles=("Client Lead",), conf="High", carries=(6, 3),
          source="BRIEF.md · docs/EVALUATION_CONTRACT.md · docs/CHARTER.md §3 · src/contract.py (night_cost, WALK_COST, WALK_CEILING)",
          foot=has(6, "The data has booking rows, not rooms, and no record of real walks: every euro in this deck is a simulated contract cost."),
          sowhat="A rule competes on cost only after it passes the walk limit; full metric definitions are in appendix B2–B3.",
          notes="The decision: one whole number per hotel per night, how many rooms to sell beyond capacity. The north star is the total "
                "contract cost in euros, lower than the flat rule's on the same hotel-nights; the guardrail is at most 10 walks per "
                "1,000 arrivals, group-wide.")
box(s, 0.55, 1.75, 5.2, 1.0, INK, radius=0.05)
text(s, 0.75, 1.82, 4.9, 0.26, "NORTH STAR", size=11, color="8DB6F2", bold=True)
text(s, 0.75, 2.08, 4.9, 0.36, "Total contract cost, €", size=18, bold=True, color=PAPER)
text(s, 0.75, 2.42, 4.9, 0.3, "lower than the flat rule's, on the same hotel-nights", size=12, color="C9D4DF")
line(s, 1.85, 2.75, 1.85, 3.0, head=True)
line(s, 4.45, 2.75, 4.45, 3.0, head=True)
card(s, 0.55, 3.0, 2.55, 1.42, "Empty rooms × stay value", "stay value = the night's average adr × nights", tag="Too few oversold",
     tag_color=ALT, size=12)
card(s, 3.2, 3.0, 2.55, 1.42, "Walked guests × €300", "€300 is the client's own figure", tag="Too many oversold", tag_color=ALT, size=12)
box(s, 6.05, 1.75, 6.75, 1.25, PAPER, line=RED, radius=0.05)
text(s, 6.25, 1.83, 6.4, 0.26, "GUARDRAIL", size=11, color=RED, bold=True)
text(s, 6.25, 2.1, 6.4, 0.38, "≤ 10 walks per 1,000 arrivals", size=18, bold=True, color=INK)
text(s, 6.25, 2.5, 6.4, 0.45, "group-wide; a rule over it is rejected, whatever it saves", size=12, color=MUTED)
text(s, 6.05, 3.12, 6.75, 1.3, [[("Too few oversold: ", {"bold": True}), ("cancelled rooms stay empty; cost = empty rooms × the night's average booked stay", {})],
                                [("Too many oversold: ", {"bold": True}), ("guests arrive to a full hotel; cost = walked guests × €300", {})],
                                [("The hard limit: ", {"bold": True}), ("max 10 walks per 1,000 arrivals; a rule that breaks it is rejected, whatever it saves", {})]],
     size=12, space_after=4)
# timeline strip
periods = [("Train", "fit models · before Jul 2016", "49,157 bookings", ALT_LIGHT, INK),
           ("Choose", "settings · Jul–Dec 2016", "29,546 bookings", ACCENT_TINT, INK),
           ("Test", "Jan–Aug 2017 · retrospective", "40,687 bookings", INK, PAPER)]
total = 49157 + 29546 + 40687
xx = 0.55
for name, sub, n, f, c in periods:
    ww = 12.25 * int(n.split()[0].replace(",", "")) / total
    box(s, xx, 4.68, ww - 0.05, 0.78, f, radius=0.1)
    text(s, xx + 0.15, 4.72, ww - 0.3, 0.72, [[(name + " · ", {"bold": True}), (sub, {})], [(n, {})]], size=12, color=c,
         anchor=MSO_ANCHOR.MIDDLE)
    xx += ww
text(s, 0.55, 5.5, 12.25, 0.3, "chosen on Choose  →  proved on Test (scored more than once across runs; see A12 and B28)", size=11,
     color=MUTED, italic=True)

# ---- A4 process flow
t2 = s_texts(2)
s = frame("A4", "A forecast becomes a decision in six steps, and the walk limit is checked before any rule is compared on cost",
          roles=("Client Lead",), conf="High", carries=(2,),
          source=s_source(2) + " · src/contract.py (nightly_table, night_cost)",
          sowhat="The client asks for one number per night, not a list of risky bookings; this strip tracks each step on later slides.",
          notes="The client's question in its own words, then the decision process that the rest of the deck follows: data, the eight "
                "inputs, a probability per booking, an oversell rule that turns the night's expected cancellations into a whole number, "
                "the night's cost under the contract, and the walk-limit check. The same six steps appear as a small strip at the top "
                "of the later main-story slides.")
box(s, 0.55, 1.72, 12.25, 0.82, TINT, radius=0.05)
text(s, 0.75, 1.78, 11.9, 0.72, [[("The client's question  ", {"bold": True, "color": ACCENT}), (t2[6], {"italic": True})]], size=13,
     anchor=MSO_ANCHOR.MIDDLE)
steps = [("1 · Data", "119,390 bookings, two hotels"), ("2 · Inputs", "8 columns known on the decision morning"),
         ("3 · Probability", "each booking's chance of cancelling"), ("4 · Oversell rule", "expected cancellations → one whole number"),
         ("5 · Cost", "empty rooms × stay value + walks × €300"), ("6 · Walk limit", "≤ 10 per 1,000, else rejected")]
flow(s, 0.55, 2.8, steps, 1.82, 1.35, 0.27, fills={5: PAPER})
box(s, 0.55 + 5 * 2.09, 2.8, 1.82, 1.35, None, line=RED, radius=0.08, lw=2)
for i, (h, b) in enumerate([(t2[8], t2[9]), (t2[11], t2[12]), (t2[14], t2[15])]):
    xx = 0.55 + i * 4.12
    box(s, xx, 4.4, 3.95, 1.4, PAPER, line=RULE, radius=0.05)
    box(s, xx + 0.18, 4.55, 0.36, 0.36, ACCENT, shape=MSO_SHAPE.OVAL, label=str(i + 1), size=12, color=PAPER, bold=True)
    text(s, xx + 0.7, 4.5, 3.1, 0.5, h, size=13, bold=True, color=INK)
    text(s, xx + 0.7, 5.0, 3.1, 0.75, b, size=12, color=MUTED)

# ---- A5 worked night
s = frame("A5", "On one real night the flat rule oversold 22 rooms; 30 guests cancelled, so 8 rooms stood empty at a cost of €3,523",
          roles=("Client Lead",), conf="High", nav=[3, 4], carries=(4,),
          source=s_source(4), foot="Choose period night under the selected rule: hotel rate × bookings, rounded up, minus 17 rooms, never below 0.",
          sowhat=has(4, "Over all 368 validation nights: this rule cost €2,414,409 with 9.06 walks per 1,000; selling nothing extra would have cost €4,155,341. That gap is what the north star chases."),
          notes="One City Hotel night, Monday 4 July 2016, worked through with the selected rule. The other two example nights, one with "
                "too many oversold and one where the margin was too big for a small Resort night, are in appendix B4.")
text(s, 0.55, 1.72, 12, 0.3, has(2, "ONE MORNING · CITY HOTEL · ARRIVALS ON MON 04 JUL 2016"), size=12, color=ACCENT, bold=True)
night = [("On the books", "92", "bookings due to arrive"), ("Expected", "38.3", "92 × 41.7% = 38.3"), ("Round up", "39", "→ 39"),
         ("Margin", "− 17", "safety rooms held back"), ("Oversold", "22", "39 − 17 = 22"), ("Cancelled", "30", "what happened"),
         ("Result", "€3,523", "8 empty × €440; 0 walked")]
for i, (h, v, b) in enumerate(night):
    xx = 0.55 + i * 1.77
    last = i == len(night) - 1
    box(s, xx, 2.15, 1.55, 2.0, ACCENT if i == 4 else (ACCENT_TINT if last else TINT), radius=0.08)
    c = PAPER if i == 4 else INK
    text(s, xx + 0.08, 2.25, 1.39, 0.3, h, size=12, bold=True, color=c, align=PP_ALIGN.CENTER)
    text(s, xx + 0.08, 2.65, 1.39, 0.6, v, size=26, bold=True, color=c, align=PP_ALIGN.CENTER)
    text(s, xx + 0.08, 3.35, 1.39, 0.75, b, size=12, color=PAPER if i == 4 else MUTED, align=PP_ALIGN.CENTER)
    if not last:
        line(s, xx + 1.57, 3.15, xx + 1.75, 3.15, color=SOFT, width=2, head=True)
for i, (head, body) in enumerate([("Too many oversold · City Hotel · Sat 30 Jul 2016",
                                   "142 bookings × 41.7% = 59.2 → 60; 60 − 17 = 43 oversold; 27 cancelled; 16 walked × €300 = €4,800"),
                                  ("Margin too big for a small night · Resort Hotel · Tue 05 Jul 2016",
                                   "35 × 25.2% = 8.8 → 9; 9 − 17 → 0 oversold; 3 cancelled; 3 empty × €869 = €2,608")]):
    xx = 0.55 + i * 6.2
    box(s, xx, 4.4, 6.05, 1.4, TINT, radius=0.05)
    text(s, xx + 0.2, 4.5, 5.7, 0.3, head, size=12, bold=True, color=INK)
    text(s, xx + 0.2, 4.85, 5.7, 0.9, body, size=12.5, color=BODY_C)

# ---- A6 data
cats, series = s_chart(7)
t7 = s_texts(7)
s = frame("A6", "37% of 119,390 bookings cancel — 41.7% at the City Hotel against 27.8% at the Resort — and the rate moves with the season",
          roles=("Client Lead", "Data Lead"), conf="High", nav=0, carries=(7,),
          source=s_source(7), foot="Cancellation includes no-shows. The brief's 'one in four' is a client impression; the data says more than one in three.",
          sowhat="One rate per hotel already captures most of the difference; any forecast must beat that baseline.",
          notes="The data: 119,390 bookings, two hotels, July 2015 to August 2017.")
cd = CategoryChartData()
cd.categories = [c if c.strip() else " " * (i + 1) for i, c in enumerate(cats)]
for name, vals in series:
    cd.add_series(name, vals)
ch = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(0.45), Inches(1.7), Inches(7.6), Inches(4.15), cd).chart
ch.font.name, ch.font.size = FONT, Pt(11)
ch.font.color.rgb = rgb(MUTED)
ch.has_legend, ch.legend.position, ch.legend.include_in_layout = True, XL_LEGEND_POSITION.BOTTOM, False
ch.has_title = True
ch.chart_title.text_frame.text = "Share of bookings cancelled, by arrival month (n = 119,390)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
va = ch.value_axis
va.minimum_scale, va.maximum_scale, va.major_unit = 0, 0.8, 0.2
va.tick_labels.number_format, va.tick_labels.number_format_is_linked = "0%", False
va.major_gridlines.format.line.color.rgb = rgb("E6E9ED")
ch.category_axis.tick_labels.font.size = Pt(11)
body = ch.category_axis._element.txPr.find(qn("a:bodyPr"))
body.set("rot", "0")
for ser, c in zip(ch.plots[0].series, [ACCENT, ALT]):
    ser.format.line.color.rgb = rgb(c)
    ser.format.line.width = Pt(2.5)
    ser.smooth = False
    ser.marker.style = XL_MARKER_STYLE.NONE
hbars(s, 8.3, 2.0, 4.5, [dict(label="City Hotel", sub="n = 79,330", value=0.417, color=ALT, text="41.7%"),
                         dict(label="Resort Hotel", sub="n = 40,060", value=0.278, color=ALT_LIGHT, text="27.8%"),
                         dict(label="Both hotels", sub="n = 119,390", value=0.37, color=INK, text="37%", bold=True)],
      vmax=0.5, label_w=1.45, value_w=0.8, bar_h=0.42, gap=0.28)
text(s, 8.3, 4.0, 4.5, 1.85, [[(t7[9] + "  ", {"bold": True, "size": 16}), (t7[10].replace("see slide 9", "B7"), {})],
                              [(t7[11] + "  ", {"bold": True, "size": 16, "color": AMBER}), (t7[12].replace("see slide 18", "B17"), {})],
                              [(t7[5] + "  ", {"bold": True, "size": 16}), (t7[6], {})]], size=12, space_after=6)

# ---- A7 columns
s = frame("A7", "Only 8 of 44 columns are safe to use on the decision morning, and 4 of those rest on timing the source never states",
          roles=("Data Lead",), conf="Medium", nav=1, carries=(14,),
          source=s_source(14),
          foot=has(14, "Tests: not the outcome · known on the decision morning · won't change before arrival · about this booking only. “Unsure” normally means exclude; these four are used provisionally and their timing must be verified."),
          sowhat="Columns were judged by when the hotel knows them, not by score: a leaking column scores well everywhere and is useless on the morning.",
          notes="Every one of 44 columns faced four timing tests. Four pass all four and are inputs; four are provisional; 36 are "
                "excluded, for the reasons in the bars. The full test matrix, the reasons and the three 'tempting traps' are in "
                "appendix B9–B19.")
groups = [("Inputs: pass all 4 tests", 4, ACCENT, "hotel · market_segment · distribution_channel · agent"),
          ("Provisional: timing unsure", 4, AMBER, "company · is_repeated_guest · previous cancellations · previous bookings"),
          ("Excluded: pass, but not in the input set", 6, ALT_LIGHT, "lead_time · arrival date parts"),
          ("Excluded: changes until arrival", 11, ALT, "stay length, guests, meal, room type, requests, booking changes"),
          ("Excluded: the outcome itself", 3, ALT, "reservation status and its date · assigned room"),
          ("Excluded: corrected or recalculated later", 3, ALT, "adr · deposit_type · country"),
          ("Excluded: timing unknown", 3, ALT, "waiting list · parking · customer type"),
          ("Excluded: cleaning flags", 10, ALT_LIGHT, "inherit their source column's result")]
hbars(s, 0.55, 1.85, 12.25, [dict(label=g, value=n, color=c, text=f"{n}   {cols}", bold=i < 2) for i, (g, n, c, cols) in enumerate(groups)],
      vmax=11, label_w=3.75, value_w=6.4, bar_h=0.34, gap=0.15)
text(s, 0.55, 5.75 - 0.05, 12, 0.25, "Number of columns (44 in total)", size=11, color=MUTED)

# ---- A8 models
mt = s_table(21)
brier = lambda r: float(r[4]) if r[4] not in ("—", "") else None
s = frame("A8", "Models improved probability quality only modestly over simple rates; calibrated logistic regression scored best on Choose",
          roles=("Model Lead",), conf="High", nav=2, carries=(),
          source="evidence/baselines_pooling · train_model_experiments · hyperparameter_experiments · probability_calibration · data/models/val_scores.csv",
          foot="Choose Brier score on Jul–Dec 2016 (29,546 bookings); lower is better. Models without a Choose score are listed in B24.",
          sowhat="The best model is only about 0.03 Brier better than a one-rate-per-hotel baseline: a weak signal to build a decision on.",
          notes="Every model predicts each booking's chance of cancelling; this slide compares their Choose Brier scores with the baselines. "
                "The full table of 15 models, with settings, train-fold Brier, AUC and outcome, is in appendix B24–B25.")
rows = []
for r in mt[1:]:
    b = brier(r)
    if b is None:
        continue
    label = (r[0].strip() + (f" ({r[1]})" if r[1] and not r[0].strip().startswith("+") else "")).replace("  + ", "+ ")
    if r[0].strip().startswith("+"):
        label = "LR C = 0.1 + sigmoid calibration"
    sel = "SELECTED" in r[6]
    rows.append(dict(label=label, sub=f"{r[2]} set · {r[6]}", value=b, color=ACCENT if sel else (ALT if r[2] == "Final" and "Baseline" not in r[6] and "Same" not in r[6] else ALT_LIGHT),
                     text=r[4], bold=sel))
rows.sort(key=lambda d: d["value"])
hbars(s, 0.55, 1.75, 8.2, rows, vmax=0.24, vmin=0.19, label_w=4.3, value_w=0.75, bar_h=0.26, gap=0.07, size=12)
bullets(s, 9.05, 1.85, 3.75, 3.9, ["Baselines: global 0.2329, hotel rate 0.2299 — grey bars at the bottom",
                                  "Earlier set (XGBoost, CatBoost) sat close together: 0.2082–0.2112",
                                  "Selection was on Train folds (LR C = 0.1: 0.1731), then calibration was kept because it lowered Choose Brier"],
        size=12.5)

# ---- A9 calibration and uncertainty
t22 = s_texts(22)
s = frame("A9", "Calibration fixed the overall level, but a night's cancellations swing far more than the model's own uncertainty says",
          roles=("Model Lead",), conf="High", nav=2, carries=(22,),
          source=s_source(22), foot="All on Choose (Jul–Dec 2016, 29,546 bookings, 368 hotel-nights).",
          sowhat=t22[-1],
          notes="Left: the predicted cancellation rate before and after calibration, against the actual rate. Right: how often the "
                "actual nightly count fell inside a 90% interval.")
text(s, 0.55, 1.75, 6.0, 0.3, "Predicted cancellation rate vs actual", size=13, bold=True, color=INK)
hbars(s, 0.55, 2.2, 6.0, [dict(label="Before calibration", value=0.285, color=ALT_LIGHT, text="28.5%"),
                          dict(label="After calibration", value=0.36, color=ACCENT, text="36.0%", bold=True),
                          dict(label="Actual", value=0.369, color=INK, text="36.9%")],
      vmax=0.45, label_w=1.9, value_w=0.8, bar_h=0.4, gap=0.25)
text(s, 0.55, 4.25, 6.0, 1.5, [[(t22[8] + "  ", {"bold": True, "size": 18}), (t22[9], {})],
                               [("Before 28.5% → after 36.0% (actual 36.9%)", {"color": MUTED})]], size=13, space_after=4)
text(s, 6.95, 1.75, 5.85, 0.3, "Nights whose actual count fell inside the 90% interval", size=13, bold=True, color=INK)
hbars(s, 6.95, 2.2, 5.85, [dict(label="Textbook interval", sub="assumes bookings cancel independently", value=0.416, color=RED,
                                text="41.6% (shown as 42%)", text_color=RED),
                           dict(label="Conformal interval", sub="average width 53 rooms", value=0.943, color=ALT, text="94.3%")],
      vmax=1.0, label_w=2.25, value_w=1.75, bar_h=0.45, gap=0.45, ref=(0.9, "90% target", INK))
text(s, 6.95, 4.45, 5.85, 1.3, [[(t22[11] + " ", {"bold": True}), (t22[12], {})], [(t22[13] + " ", {"bold": True}), (t22[14], {})]],
     size=12.5, space_after=4)

# ---- A10 rules compared
s = frame("A10", "Only rules that hold back a fixed margin stay within the walk limit; the flat rule with 17 rooms is the cheapest of them",
          roles=("Model Lead",), conf="High", nav=[3, 4, 5], carries=(23,),
          source=s_source(23), foot="134 rules scored on Choose. Selection: drop every rule above 10 per 1,000, then take the lowest cost. Ranges show the family's spread.",
          sowhat="The winning rule does not use the model: holding back rooms absorbs the nightly swings that probabilities cannot predict.",
          notes="Each rule family turns the night's expected cancellations into a whole number of rooms. Walks per 1,000 on Choose, "
                "with the limit drawn at 10; labels give each family's cheapest cost within the limit.")
rt = s_table(23)
rows = [dict(label="No overbooking", sub="sell nothing extra", value=0.0, text="0.00 · €4.16M · within limit, most expensive", color=ALT),
        dict(label="Rate rules (3)", sub="global, hotel or hotel-month rate × bookings", value=(92, 135), color=RED,
             text="92–135 · none within limit", text_color=RED),
        dict(label="Model + spread buffer (8)", sub="expected count + 0 to 2 × spread", value=(72, 173), color=RED,
             text="72–173 · none within limit", text_color=RED),
        dict(label="Model with margin (61)", sub="expected count − 0 to 60 rooms", value=9.76, color=ALT,
             text="9.76 · €2.58M (margin 18)"),
        dict(label="Flat rule with margin (61)", sub="hotel rate × bookings − 0 to 60 rooms", value=9.06, color=ACCENT,
             text="9.06 · €2.41M (margin 17) · SELECTED", bold=True, text_color=ACCENT)]
hbars(s, 0.55, 1.95, 12.25, rows, vmax=180, label_w=3.6, value_w=3.6, bar_h=0.4, gap=0.32, ref=(10, "limit: 10 per 1,000", RED))
text(s, 0.55, 5.6, 12, 0.3, "Walks per 1,000 arrivals on Choose (0–180)  ·  " + has(23, "By hotel: with one shared margin the City Hotel carries the walks (13.96 per 1,000 on Choose) and the Resort almost none (0.30)."),
     size=11, color=MUTED)

# ---- A11 test result
s = frame("A11", "On the 2017 test the flat rule cost €3,935,876 within the limit; the best model rule cost €236,784 more and breached it",
          roles=("Model Lead",), conf="Medium", nav=[4, 5], carries=(25,),
          source=s_source(25), foot=has(25, "Retrospective, not blind. The 2017 period was already examined in the earlier runs (slide 24), so this confirms the choice rather than proving it.").replace("slide 24", "B27–B28"),
          sowhat="Chosen on Choose, proved on Test: the same rule wins on both periods, but the test is a confirmation, not a blind proof.",
          notes="The frozen rule on January–August 2017, 486 hotel-nights, against the best model-based rule chosen on Choose. Hotels "
                "are reported, not judged: the client set only a group-wide limit. Full table in appendix B29.")
text(s, 0.55, 1.75, 6, 0.3, "Cost on the 2017 test (486 hotel-nights)", size=13, bold=True, color=INK)
hbars(s, 0.55, 2.2, 6.0, [dict(label="Flat rule, 17 rooms", value=3935876, color=ACCENT, text="€3,935,876", bold=True),
                          dict(label="Best model, 18 rooms", value=4172660, color=ALT, text="€4,172,660")],
      vmax=4.6e6, label_w=2.1, value_w=1.3, bar_h=0.45, gap=0.35)
text(s, 0.55, 3.55, 6, 0.3, "Walks per 1,000 arrivals", size=13, bold=True, color=INK)
hbars(s, 0.55, 4.0, 6.0, [dict(label="Flat rule, 17 rooms", value=6.21, color=ACCENT, text="6.21 · met", bold=True),
                          dict(label="Best model, 18 rooms", value=11.11, color=RED, text="11.11 · breached", text_color=RED)],
      vmax=14, label_w=2.1, value_w=1.3, bar_h=0.4, gap=0.3, ref=(10, "limit 10", RED))
text(s, 6.95, 1.75, 5.85, 0.3, "Same flat rule, by hotel (reported, not judged)", size=13, bold=True, color=INK)
table(s, 6.95, 2.2, [["2017 test", "Cost", "Empty", "Walked", "Per 1k"], ["City Hotel", "€1,640,857", "4,383", "146", "9.23"],
                     ["Resort Hotel", "€2,295,019", "3,803", "9", "0.99"], ["Both hotels", "€3,935,876", "8,186", "155", "6.21"]],
      [1.6, 1.4, 0.95, 0.95, 0.95], row_h=0.42, key_rows=(3,))
text(s, 6.95, 4.1, 5.85, 1.6, [has(25, "Hotels are reported, not judged: the client set only a group-wide limit."),
                               "The model rule's extra cost: €4,172,660 − €3,935,876 = €236,784"], size=12.5, space_after=6)

# ---- A12 upside
s = frame("A12", "A separate margin per hotel looked cheaper still on the test (€3.21M at 7.18), but it was seen only there and needs new data",
          roles=("Model Lead",), conf="Low", nav=[3, 4, 5], carries=(24,),
          source=s_source(24), foot="Run 1 frozen before any test result; run 3 decided after run 1, refitted on Train + Choose. Run 2 (XGBoost, Train only) was frozen but never run. Earlier runs use floor(expected) − buffer.",
          sowhat="How the margin is split between the hotels matters more than the model; adopting 20 / 4 now would need the client's agreement and new data.",
          notes="All test runs side by side, as the contract requires: the final rule, the earlier per-hotel flat rule and models, and "
                "the run-3 refits that broke the limit.")
text(s, 0.55, 1.72, 12, 0.3, "Every 2017 test run: cost and walks per 1,000", size=13, bold=True, color=INK)
runs = [("Flat rule, 17 rooms (final)", 3935876, "€3,935,876", 6.21, "6.21 met", ACCENT),
        ("Best model, 18 rooms (final)", 4172660, "€4,172,660", 11.11, "11.11 breached", RED),
        ("Flat rule, 20 / 4 rooms (run 1)", 3.21e6, "€3.21M", 7.18, "7.18 met", ALT),
        ("CatBoost, 6 / 3 rooms (run 1)", 3.37e6, "€3.37M", 8.42, "8.42 met", ALT),
        ("CatBoost, refitted (run 3)", 2.80e6, "€2.80M", 13.11, "13.11 breached", RED),
        ("XGBoost, refitted (run 3)", 2.80e6, "€2.80M", 13.07, "13.07 breached", RED)]
hbars(s, 0.55, 2.15, 7.0, [dict(label=n, value=c, text=ct, color=ACCENT if col == ACCENT else ALT_LIGHT, bold=col == ACCENT)
                           for n, c, ct, w, wt, col in runs], vmax=4.6e6, label_w=3.2, value_w=1.1, bar_h=0.36, gap=0.2)
hbars(s, 7.75, 2.15, 5.05, [dict(label="", value=w, text=wt, color=col if col != ALT else ALT_LIGHT,
                                 text_color=RED if col == RED else INK, bold=col == ACCENT) for n, c, ct, w, wt, col in runs],
      vmax=16, label_w=0.05, value_w=1.55, bar_h=0.36, gap=0.2, ref=(10, "limit 10", RED))

# ---- A13 risks
s = frame("A13", "The result rests on simulated euros, final-book data and inputs whose timing is unverified, so it needs a live check",
          roles=("Client Lead", "Build Lead"), conf=None, carries=(27, 26),
          source="docs/ROADMAP.md · evidence/pipeline_run/run_manifest.json · tests/ · src/nightly.py · tests/test_nightly.py · docs/COMPARISON.md",
          sowhat=has(27, "Live booking data — the method is ready to be tested; the data is not"),
          notes="The limits stated in the source, grouped by type. No severity ranking is given in the source, so none is shown here.")
risks = [("Data", "No room counts: bookings stand in for rooms, so the euros are simulated"),
         ("Data", "No record of real walked guests to check against"),
         ("Data", "No 'as of' snapshots: the file holds every booking ever made"),
         ("Evidence", "Four inputs have unverified timing; the 2017 period was already seen"),
         ("Build", "Nightly command runs, but it serves the earlier per-hotel rule (20 / 4), not this 17-room rule"),
         ("Build", "No 'as of' booking filter: would score bookings not yet made on the decision morning"),
         ("Build", "Independent AI benchmark: branch never created, so no comparison is claimed")]
for i, (kind, t) in enumerate(risks):
    col, row = i % 2, i // 2
    xx, yy = 0.55 + col * 6.2, 1.8 + row * 1.02
    box(s, xx, yy, 6.05, 0.88, AMBER_TINT, radius=0.06)
    box(s, xx + 0.15, yy + 0.3, 0.95, 0.27, PAPER, line=AMBER, radius=0.5, label=kind, size=10.5, color=AMBER, bold=True)
    text(s, xx + 1.25, yy + 0.06, 4.7, 0.78, t, size=13, color=INK, anchor=MSO_ANCHOR.MIDDLE)

# ---- A14 decisions and next steps
s = frame("A14", "Four next steps are proposed and none is approved yet; the first is timestamped booking snapshots from the hotels",
          roles=("Client Lead",), conf=None, carries=(),
          source="docs/ROADMAP.md · " + s_source(25),
          foot=has(27, "Proposed, not approved: docs/ROADMAP.md is still blank, so no owners or hours are claimed."),
          sowhat="Ask for snapshots and a shadow run now; leave margins and models unchanged until new nights can test them.",
          notes="Decisions needed and next steps, as proposed in the source. The source assigns no owners, so the owner column says so.")
rows = [["Step", "Why", "Owner", "Status"],
        ["Get timestamped booking snapshots from the hotels' system", "The file holds the final book, not what was on the book on a given morning", "Not assigned", "Proposed, not approved"],
        ["Run the flat rule beside the revenue manager on new nights", "A shadow run on unseen nights is the first blind test", "Not assigned", "Proposed, not approved"],
        ["Ask the client whether margins may differ by hotel (City 20, Resort 4 cost less on the 2017 test)", "Seen only on the test; needs the client's agreement and new data", "Client", "Proposed, not approved"],
        ["Try models again only on unseen nights, with live data", "No model beat the flat rule within the limit", "Not assigned", "Proposed, not approved"]]
table(s, 0.55, 1.8, rows, [4.6, 4.45, 1.3, 1.9], row_h=0.78, right=set(),
      colors={(r, 3): AMBER for r in range(1, 5)})

# ======================================================================================================== PART B
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 7.5, INK)
text(s, 0.8, 2.6, 11, 0.5, "PART B", size=14, color="8DB6F2", bold=True)
text(s, 0.8, 3.1, 11.5, 1.0, "Technical appendix", size=40, bold=True, color=PAPER)
text(s, 0.8, 4.2, 11.5, 0.8, "Every remaining fact, table, caveat and source from the original deck: framing, cleaning, column timing "
                             "tests, encoding, settings, models, rules, earlier runs, the final choice and engineering.",
     size=14, color="C9D4DF")
s.notes_slide.notes_text_frame.text = "Divider for the technical appendix."
DIVIDER_NO = len(prs.slides._sldIdLst)
MAP[DIVIDER_NO] = []
INDEX_NO = DIVIDER_NO + 1
index_slide = prs.slides.add_slide(BLANK)   # filled at the end, once every appendix slide exists
MAP[INDEX_NO] = []

# ---- B1 roles
t5 = s_texts(5)
s = frame("B1", "All four roles were held by one person; each owned one question, in this order of work", part="B",
          topic="Who did what: the four lead roles", roles=("Client", "Data", "Model", "Build"), carries=(5,),
          source=s_source(5), sowhat=t5[-1].split(" The questions")[0] + " The main story is organised by question, with role tags.",
          foot="Original slide ranges refer to the source deck: " + " · ".join(t5[i] for i in (8, 12, 16, 20, 24)),
          notes="The source deck was organised by role; this deck is organised by the reader's questions, with roles kept as tags.")
for i in range(5):
    lead, q, tasks = t5[5 + 4 * i], t5[6 + 4 * i], t5[7 + 4 * i]
    xx = 0.55 + i * 2.48
    box(s, xx, 1.8, 2.3, 3.95, INK if i in (0, 4) else TINT, radius=0.05)
    dark = i in (0, 4)
    text(s, xx + 0.15, 1.92, 2.0, 0.3, lead, size=12, bold=True, color="8DB6F2" if dark else ACCENT)
    text(s, xx + 0.15, 2.3, 2.0, 1.3, q, size=13, bold=True, color=PAPER if dark else INK)
    text(s, xx + 0.15, 3.65, 2.0, 2.0, tasks.split("\n"), size=12, color="C9D4DF" if dark else BODY_C, space_after=3)
    if i < 4:
        line(s, xx + 2.31, 3.75, xx + 2.46, 3.75, color=SOFT, width=2, head=True)

# ---- B2 north star definitions
s = frame("B2", "The north star and the guardrail each have a stated numerator, denominator, window and exclusions", part="B",
          topic="North star and guardrail definitions", roles=("Client Lead",), carries=(3,), source=s_source(3),
          sowhat=s_texts(3)[2], notes="Full metric definitions.")
table(s, 0.55, 1.85, s_table(3), [2.0, 5.55, 4.7], row_h=0.62, right=set())

# ---- B3 contract periods and cards (verbatim)
s = frame("B3", "The contract fixes one decision per hotel-night, two error costs, a hard limit and three arrival-date periods",
          part="B", topic="The decision, error costs and periods (as stated in the contract)", roles=("Client Lead",), source=s_source(6),
          sowhat=t6[2], foot=t6[-1], notes="The contract's framing, verbatim from the source deck.")
for i in range(3):
    head, sub, body = t6[5 + 3 * i], t6[6 + 3 * i], t6[7 + 3 * i]
    card(s, 0.55 + i * 4.12, 1.85, 3.95, 1.9, head, [sub, body], tag=None, size=13, head_size=16)
for i, k in enumerate((14, 15, 16)):
    name, n = t6[k].split("\n") if "\n" in t6[k] else (t6[k].split(" / ")[0], "")
    box(s, 0.55 + i * 4.12, 4.05, 3.95, 1.0, [ALT_LIGHT, ACCENT_TINT, INK][i], radius=0.1)
    text(s, 0.75 + i * 4.12, 4.12, 3.6, 0.9, [[(name, {"bold": True})], [(n, {})]], size=13, color=PAPER if i == 2 else INK,
         anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.55, 5.2, 12.2, 0.55, "Note: the source labels the test 'once', while its later slides report the 2017 period was scored in "
                               "more than one run (see B28 and Questions for the author).", size=12, color=AMBER, italic=True)

# ---- B4 three nights
t4 = s_texts(4)
s = frame("B4", "Three Choose nights show both directions of error and why one shared margin is too big for a small night", part="B",
          topic="Three example nights in euros", roles=("Client Lead",), source=s_source(4), sowhat=t4[2],
          foot=t4[-1], notes="The three example nights from the source, in full.")
for i in range(3):
    base = 5 + 16 * i
    tag, head = t4[base], t4[base + 1]
    pairs = [(t4[base + 2 + 2 * j], t4[base + 3 + 2 * j]) for j in range(7)]
    xx = 0.55 + i * 4.12
    box(s, xx, 1.8, 3.95, 3.95, TINT, radius=0.04)
    text(s, xx + 0.2, 1.9, 3.6, 0.28, tag.upper(), size=11, bold=True, color=RED if i == 1 else (AMBER if i == 2 else ALT))
    text(s, xx + 0.2, 2.2, 3.6, 0.35, head, size=14, bold=True, color=INK)
    for j, (a, b) in enumerate(pairs):
        yy = 2.62 + j * 0.43
        last = j == 6
        text(s, xx + 0.2, yy, 1.6, 0.35, a, size=13 if not last else 14, color=MUTED if not last else INK, bold=last)
        text(s, xx + 1.7, yy, 2.05, 0.35, b, size=13 if not last else 16, bold=last or j == 2, align=PP_ALIGN.RIGHT,
             color=INK)

# ---- B5 cleaning rules
t8 = s_texts(8)
s = frame("B5", "Cleaning followed five rules written before any change: the raw file is evidence and outcomes never drive it",
          part="B", topic="Cleaning: the five rules", roles=("Data Lead",), carries=(8,), source=s_source(8), sowhat=t8[2],
          notes="The five cleaning principles.")
for i in range(5):
    code, head, body = t8[6 + 3 * i], t8[7 + 3 * i], t8[8 + 3 * i]
    yy = 1.8 + i * 0.8
    box(s, 0.55, yy + 0.05, 0.55, 0.55, INK, shape=MSO_SHAPE.OVAL, label=code, size=12, color=PAPER, bold=True)
    text(s, 1.3, yy, 4.5, 0.65, head, size=15, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 5.9, yy, 6.9, 0.65, body, size=14, color=BODY_C, anchor=MSO_ANCHOR.MIDDLE)

# ---- B6 cleaning C1-C4
s = frame("B6", "Only four kinds of value were recoded, each backed by the source paper; the label and status checks needed no action",
          part="B", topic="Cleaning: C1–C4 recodes", roles=("Data Lead",), source=s_source(8), sowhat=t8[-1],
          notes="The four recodes with row counts and the alternative rejected for each.")
table(s, 0.55, 1.85, s_table(8), [1.9, 2.4, 1.6, 3.6, 2.75], row_h=0.78, right={2})

# ---- B7 repeats and options
t9 = s_texts(9)
s = frame("B7", "Exact repeats were kept and flagged: removing them would cut the Train cancellation rate from 35.8% to 22.2%",
          part="B", topic="Cleaning: exact repeats and the options considered", roles=("Data Lead",), carries=(9,), source=s_source(9),
          sowhat=t9[2], notes="The repeats in Train and the four options considered.")
key_numbers(s, 1.8, [(t9[6], t9[7], False), (t9[8], t9[9], True), (t9[10], t9[11], False)])
text(s, 0.55, 2.85, 12, 0.3, t9[5] + " · " + t9[7], size=12, color=MUTED)
table(s, 0.55, 3.25, s_table(9, 0), [3.2, 9.05], row_h=0.5, right=set(), key_rows=(4,))

# ---- B8 flags
s = frame("B8", "Ten flags mark odd rows without changing them, and none of the flags is a model input", part="B",
          topic="Cleaning: the ten flags and C6", roles=("Data Lead",), source=s_source(9), sowhat=t9[-1],
          notes="Flag counts by period and why each row was kept.")
table(s, 0.55, 1.75, s_table(9, 1), [3.0, 1.1, 1.1, 1.0, 6.05], row_h=0.375, size=12)

# ---- B9 timeline
t10 = s_texts(10)
s = frame("B9", "A column is usable only if its value exists on the decision morning and does not change before arrival",
          part="B", topic="Column timing: when the hotel knows each value", roles=("Data Lead",), carries=(10,), source=s_source(10),
          sowhat="Only the first band is safe; the last band is used provisionally, with its doubt on record.",
          notes="The four timing bands.")
X0, XB, XM, XA, XO, X1 = 4.2, 4.4, 6.6, 9.6, 12.2, 12.75
line(s, X0, 2.1, X1, 2.1, color=INK, width=2.5, head=True)
for x, lab in [(XB, t10[5]), (XM, t10[6]), (XA, t10[7]), (XO, t10[8])]:
    box(s, x - 0.09, 2.01, 0.18, 0.18, ACCENT if x == XM else INK, shape=MSO_SHAPE.OVAL)
    text(s, x - 1.1, 1.72, 2.2, 0.28, lab, size=12, bold=True, color=ACCENT if x == XM else INK, align=PP_ALIGN.CENTER)
text(s, XM - 1.3, 2.25, 2.6, 0.28, t10[9], size=11, color=ACCENT, italic=True, align=PP_ALIGN.CENTER)
line(s, XM, 2.55, XM, 5.85, color=ACCENT, width=1.5, dash=True)
bands = [(10, ALT, (XB, X1)), (14, RED, (XB, XA)), (18, RED, (XA, X1)), (22, AMBER, (XB, X1))]
for i, (k, col, (a, b)) in enumerate(bands):
    yy = 2.62 + i * 0.82
    text(s, 0.55, yy, 3.55, 0.3, t10[k], size=13, bold=True, color=INK)
    text(s, 0.55, yy + 0.32, 3.55, 0.3, t10[k + 1], size=12, bold=True, color=col)
    box(s, a, yy + 0.02, b - a, 0.3, col, radius=0.5, label=t10[k + 2], size=11, color=PAPER, bold=True)
    tb = text(s, X0, yy + 0.38, X1 - X0, 0.4, t10[k + 3], size=12, color=MUTED)
    tb.fill.solid()
    tb.fill.fore_color.rgb = rgb(PAPER)

# ---- B10-B12 test slides
for code, n, title in [("B10", 11, "T1 and T2 decide 11 columns: values written because of the outcome, or only learned at check-in or later"),
                       ("B11", 12, "T3 decides 13 columns: the file holds each value's last version, and a cancelled booking stops changing"),
                       ("B12", 13, "T4 rules out values built by comparing rows; the 10 columns that pass every test were all set once, at booking")]:
    tt = s_texts(n)
    s = frame(code, title, part="B", topic=tt[0].title().replace("Data Lead · Columns · ", "Column tests: "), roles=("Data Lead",),
              carries=(n,), source=s_source(n), sowhat=tt[2], foot=tt[-1].replace("orange headers", "highlighted headers"),
              notes="The columns this test decides, with all four answers.")
    rows = s_table(n)
    marks = {"✓": (TINT, INK), "?": (AMBER_TINT, AMBER), "✗": (RED_TINT, RED)}
    fills, colors = {}, {}
    for r in range(1, len(rows)):
        for c in range(1, 5):
            fills[(r, c)], colors[(r, c)] = marks[rows[r][c]]
        colors[(r, 5)] = ACCENT if rows[r][5] == "Input" else (AMBER if rows[r][5] == "Provisional" else MUTED)
    rh = min(0.36, 4.0 / len(rows))
    table(s, 0.55, 1.75, rows, [3.1, 0.55, 0.55, 0.55, 0.55, 1.35], row_h=rh, size=12, right=set(), fills=fills, colors=colors)
    cards = [t for t in tt[5:-1]]
    k = 0
    yy = 1.75
    while k + 4 < len(cards) + 1 and k < len(cards):
        tag, head, reason, ex, verdict = cards[k:k + 5]
        h = 2.0 if len(cards) > 5 else 3.9
        box(s, 7.35, yy, 5.45, h - 0.1, TINT, radius=0.04)
        text(s, 7.55, yy + 0.1, 5.1, 0.26, tag, size=11, color=ACCENT, bold=True)
        text(s, 7.55, yy + 0.38, 5.1, 0.35, head, size=14, bold=True, color=INK)
        text(s, 7.55, yy + 0.75, 5.1, h - 1.0, [reason, [(ex, {"color": MUTED})], [(verdict, {"bold": True})]], size=12, space_after=3)
        yy += h
        k += 5

# ---- B13 columns chosen
t14 = s_texts(14)
s = frame("B13", "8 of 44 columns are used: four pass all four tests and four are used provisionally, with the doubt on record",
          part="B", topic="Columns chosen and why", roles=("Data Lead",), source=s_source(14), sowhat=t14[2],
          notes="The eight inputs and the summary of the 36 exclusions.")
table(s, 0.55, 1.75, s_table(14), [2.95, 1.7, 1.3, 3.7], row_h=0.48, right=set(),
      colors={(r, 2): ACCENT if r <= 4 else AMBER for r in range(1, 9)})
box(s, 10.4, 1.75, 2.4, 4.1, TINT, radius=0.04)
text(s, 10.55, 1.85, 2.15, 0.35, t14[5], size=14, bold=True, color=INK)
text(s, 10.55, 2.25, 2.15, 3.55, t14[6].split("\n"), size=12, color=BODY_C, space_after=4)

# ---- B14 safe inputs
t15 = s_texts(15)
s = frame("B14", "Each safe input says how, and through whom, the booking was made — facts set once, when the booking is created",
          part="B", topic="The four safe inputs", roles=("Data Lead",), carries=(15,), source=s_source(15), sowhat=t15[2],
          foot="'one 0/1 column' and '< 30 bookings pooled' describe notebook 10's encoding; the final pipeline's encoding is in B20–B21 (see Questions for the author).",
          notes="The four inputs that pass every test, with their most common Train values.")
i0 = 5
for i in range(4):
    blk = t15[i0:]
    name, what, common = blk[0], blk[1], blk[2]
    nvals = 2 if i == 0 else 3
    vals = [(blk[3 + 2 * j], blk[4 + 2 * j]) for j in range(nvals)]
    rest = blk[3 + 2 * nvals:]
    why_h, why, enc_h, enc = rest[0], rest[1], rest[2], rest[3]
    i0 += 3 + 2 * nvals + 4
    xx = 0.55 + i * 3.1
    box(s, xx, 1.75, 2.95, 4.1, TINT, radius=0.04)
    text(s, xx + 0.18, 1.85, 2.6, 0.3, name, size=14, bold=True, color=INK, font="Consolas")
    text(s, xx + 0.18, 2.17, 2.6, 0.3, what, size=12, color=MUTED)
    text(s, xx + 0.18, 2.5, 2.6, 0.3, common, size=11, bold=True, color=ACCENT)
    for j, (v, p) in enumerate(vals):
        yy = 2.82 + j * 0.36
        text(s, xx + 0.18, yy, 1.45, 0.3, v, size=12)
        share = float(p.rstrip("%")) / 100
        first = float(vals[0][1].rstrip("%")) / 100
        box(s, xx + 1.62, yy + 0.06, 0.75 * share / first, 0.2, ALT_LIGHT)
        text(s, xx + 2.25, yy, 0.55, 0.3, p, size=12, bold=True, align=PP_ALIGN.RIGHT)
    text(s, xx + 0.18, 3.95, 2.6, 0.26, why_h, size=11, bold=True, color=ACCENT)
    text(s, xx + 0.18, 4.22, 2.6, 0.75, why, size=12)
    text(s, xx + 0.18, 5.0, 2.6, 0.26, enc_h, size=11, bold=True, color=ACCENT)
    text(s, xx + 0.18, 5.27, 2.6, 0.5, enc, size=12, color=MUTED)

# ---- B15 provisional
t16 = s_texts(16)
cats16, ser16 = s_chart(16)
s = frame("B15", "Four inputs pass every test except timing, and one of them shifted sharply after Train", part="B",
          topic="The four provisional inputs", roles=("Data Lead",), carries=(16,), source=s_source(16), sowhat=t16[2],
          notes="What is unsure about each provisional input, and the prior-cancellation shift.")
text(s, 0.55, 1.75, 7, 0.28, t16[5], size=11, bold=True, color=AMBER)
for i in range(4):
    col, unsure, chk = t16[6 + 3 * i], t16[7 + 3 * i], t16[8 + 3 * i]
    yy = 2.08 + i * 0.95
    box(s, 0.55, yy, 7.0, 0.85, AMBER_TINT, radius=0.05)
    text(s, 0.75, yy + 0.06, 6.6, 0.3, col, size=13, bold=True, color=INK, font="Consolas")
    text(s, 0.75, yy + 0.42, 3.6, 0.4, unsure, size=12)
    text(s, 4.45, yy + 0.42, 3.0, 0.4, chk, size=12, color=MUTED)
text(s, 7.85, 1.75, 4.95, 0.28, t16[18] + " (Train n = 49,157; Validation n = 29,546)", size=11, bold=True, color=INK)
hbars(s, 7.85, 2.2, 4.95, [dict(label=cats16[0], value=ser16[0][1][0], color=AMBER, text=f"{ser16[0][1][0]:.1%}", bold=True),
                           dict(label=cats16[1], value=ser16[0][1][1], color=ALT_LIGHT, text=f"{ser16[0][1][1]:.1%}")],
      vmax=0.14, label_w=1.2, value_w=0.8, bar_h=0.45, gap=0.3)
text(s, 7.85, 3.7, 4.95, 2.1, t16[19].split("\n"), size=13, space_after=6)

# ---- B16 exclusions by reason
t17 = s_texts(17)
s = frame("B16", "The other 36 columns each fail a specific test: outcome, changes before arrival, corrected later or unknown timing",
          part="B", topic="The 36 excluded columns by reason", roles=("Data Lead",), carries=(17,), source=s_source(17), sowhat=t17[2],
          notes="All 36 exclusions grouped by reason.")
k = 5
for i in range(6):
    count, head, sub = t17[k], t17[k + 1], t17[k + 2]
    cols = t17[k + 3:k + 3 + int(count)]
    k += 3 + int(count)
    xx, yy = 0.55 + (i % 3) * 4.12, 1.75 + (i // 3) * 2.08
    box(s, xx, yy, 3.95, 1.95, TINT, radius=0.04)
    box(s, xx + 3.3, yy + 0.12, 0.5, 0.32, ACCENT if i == 5 else ALT, radius=0.5, label=count, size=12, color=PAPER, bold=True)
    text(s, xx + 0.18, yy + 0.1, 3.1, 0.3, head, size=13, bold=True, color=INK)
    text(s, xx + 0.18, yy + 0.42, 3.6, 0.28, sub, size=12, color=MUTED)
    text(s, xx + 0.18, yy + 0.75, 3.6, 1.15, " · ".join(cols), size=12, color=BODY_C)

# ---- B17-B19 traps, one slide each
t18 = s_texts(18)
for j, code in enumerate(("B17", "B18", "B19")):
    name, cap = t18[5 + 4 * j], t18[6 + 4 * j]
    steps = t18[8 + 4 * j].split("\n")
    cats_j, ser_j = s_chart(18, j)
    s = frame(code, f"{name} looks like a strong signal, but its value is written or corrected after the decision morning",
              part="B", topic=f"Tempting trap: {name}", roles=("Data Lead",), carries=(18,) if j == 0 else (),
              source=s_source(18), sowhat=t18[2],
              foot="None of these rates was used to choose columns: notebook 06 never read an outcome.",
              notes=f"How the {name} trap works.")
    text(s, 0.55, 1.75, 6.2, 0.3, cap, size=13, bold=True, color=INK)
    vals = ser_j[0][1]
    top = max(range(len(vals)), key=lambda q: vals[q]) if name != "required_car_parking_spaces" else 0
    hbars(s, 0.55, 2.2, 6.2, [dict(label=c, value=v, color=RED if q == top else ALT_LIGHT, text=f"{v:.1%}", bold=q == top)
                              for q, (c, v) in enumerate(zip(cats_j, vals))], vmax=1.1, label_w=1.9, value_w=0.8,
          bar_h=0.4, gap=0.18)
    text(s, 7.05, 1.75, 5.75, 0.3, t18[7 + 4 * j], size=11, bold=True, color=RED)
    for q, st in enumerate(steps):
        k_, v_ = st.split(": ", 1)
        yy = 2.15 + q * 0.92
        box(s, 7.05, yy, 5.75, 0.82, RED_TINT if k_ == "On the morning" else TINT, radius=0.05)
        text(s, 7.25, yy + 0.06, 5.4, 0.72, [[(k_ + ": ", {"bold": True}), (v_, {})]], size=13, anchor=MSO_ANCHOR.MIDDLE)

# ---- B20-B21 encoding
t19 = s_texts(19)
s = frame("B20", "Each booking's eight inputs become 451 numbers: 448 one-hot columns and three scaled counts, learnt on Train only",
          part="B", topic="Encoding: one booking step by step", roles=("Data Lead",), carries=(19,), source=s_source(19), sowhat=t19[2],
          notes="One Train booking taken through the encoding.")
text(s, 0.55, 1.72, 12, 0.28, t19[5], size=11, bold=True, color=ACCENT)
for i in range(4):
    head, tag, body = t19[6 + 3 * i], t19[7 + 3 * i], t19[8 + 3 * i]
    yy = 2.05 + i * 0.86
    box(s, 0.55, yy, 12.25, 0.76, TINT, radius=0.06)
    box(s, 0.55, yy, 0.1, 0.76, ACCENT)
    text(s, 0.8, yy + 0.06, 2.6, 0.3, head, size=13, bold=True, color=INK)
    text(s, 0.8, yy + 0.38, 2.6, 0.3, tag, size=11, bold=True, color=ACCENT)
    text(s, 3.5, yy + 0.04, 9.2, 0.7, body, size=12.5, anchor=MSO_ANCHOR.MIDDLE)
box(s, 0.55, 5.5, 12.25, 0.36, ACCENT_TINT, radius=0.3, label=t19[18], size=12.5, bold=True, color=INK)
s = frame("B21", "Unseen agents and companies get all-zero rows, and every statistic is refitted on each fold's training rows",
          part="B", topic="Encoding: categories, unseen values and refitting", roles=("Data Lead",), source=s_source(19),
          sowhat=t19[19], foot=t19[20], notes="Values per input in Train and how unseen values are handled.")
table(s, 0.55, 1.85, s_table(19), [3.0, 2.2, 2.6, 4.45], row_h=0.5)

# ---- B22-B23 settings
t20 = s_texts(20)
s = frame("B22", "The model was chosen inside the training year with three expanding time folds, always predicting forward",
          part="B", topic="Settings: the three time folds and six candidates", roles=("Model Lead",), carries=(20,), source=s_source(20),
          sowhat=t20[2], notes="Three expanding time folds inside Train and the six declared candidates.")
text(s, 0.55, 1.72, 12, 0.28, t20[5], size=11, bold=True, color=ACCENT)
X0f, X1f = 3.6, 12.8
mw = (X1f - X0f) / 12
for i in range(3):
    name, counts = t20[6 + 4 * i], t20[7 + 4 * i]
    yy = 2.1 + i * 0.55
    text(s, 0.55, yy, 0.9, 0.35, name, size=13, bold=True)
    text(s, 1.45, yy + 0.02, 2.1, 0.35, counts, size=12, color=MUTED)
    fit_m = 3 * (i + 1)
    box(s, X0f, yy, fit_m * mw - 0.03, 0.36, ALT, radius=0.4, label="fit", size=12, color=PAPER, bold=True)
    box(s, X0f + fit_m * mw, yy, 3 * mw - 0.03, 0.36, ACCENT, radius=0.4, label="check", size=12, color=PAPER, bold=True)
for q in range(4):
    text(s, X0f + q * 3 * mw, 3.75, 3 * mw, 0.3, t20[18 + q], size=12, color=MUTED, align=PP_ALIGN.CENTER)
cv = [("Logistic C = 0.1", 0.1731), ("Logistic C = 1", 0.1758), ("Forest 100 / leaf 10", 0.1760), ("Forest 150 / leaf 20", 0.1784),
      ("Logistic C = 10", 0.1802), ("Forest 150 / leaf 40", 0.1828)]
text(s, 0.55, 4.15, 6, 0.3, "Mean train-fold Brier of the six declared candidates (lower is better)", size=12, bold=True, color=INK)
hbars(s, 0.55, 4.5, 12.25, [dict(label=n, value=v, color=ACCENT if q == 0 else ALT_LIGHT, text=f"{v:.4f}", bold=q == 0) for q, (n, v) in enumerate(cv)][:3],
      vmax=0.185, vmin=0.17, label_w=2.6, value_w=0.9, bar_h=0.26, gap=0.08)
hbars(s, 6.7, 4.5, 6.1, [dict(label=n, value=v, color=ALT_LIGHT, text=f"{v:.4f}") for n, v in cv[3:]],
      vmax=0.185, vmin=0.17, label_w=2.3, value_w=0.9, bar_h=0.26, gap=0.08)
s = frame("B23", "Each setting was picked by a rule written in advance, then frozen with file fingerprints before the 2017 test",
          part="B", topic="Settings: every decision and the rule that made it", roles=("Model Lead",), source=s_source(20),
          sowhat=t20[2], notes="Every fixed decision, how it was chosen, and the result.")
table(s, 0.55, 1.75, s_table(20), [1.75, 3.2, 4.3, 3.0], row_h=0.57, right=set(), key_rows=(6,))

# ---- B24-B25 models
mrows = s_table(21)
foot21 = next(t for t in s_texts(21) if t.startswith("Train-fold Brier"))
for code, part_rows, title, topic in [("B24", [mrows[0]] + [r for r in mrows[1:] if r[2] == "Final"],
                                       "In the final set, logistic regression with C = 0.1 had the best train-fold Brier, and calibration made it the selected model",
                                       "Models tried: final set"),
                                      ("B25", [mrows[0]] + [r for r in mrows[1:] if r[2] == "Earlier"],
                                       "In the earlier set, four models sat close together on Choose; XGBoost ranked best and CatBoost was chosen",
                                       "Models tried: earlier set")]:
    s = frame(code, title, part="B", topic=topic, roles=("Model Lead",), carries=(21,) if code == "B24" else (),
              source=s_source(21), sowhat=s_texts(21)[2], foot=foot21, notes="Models tried, with settings, scores and outcome.")
    key = {i for i, r in enumerate(part_rows) if "SELECTED" in r[6] or "Chosen" in r[6]}
    table(s, 0.55, 1.75, part_rows, [2.6, 1.9, 0.9, 1.55, 1.4, 1.35, 2.55], row_h=min(0.36, 4.05 / len(part_rows)), key_rows=key)

# ---- B26 rules table
t23 = s_texts(23)
s = frame("B26", "Rules without a margin oversell too much; only margin rules stayed within the walk limit on Choose",
          part="B", topic="Rules tried: the five families", roles=("Model Lead",), source=s_source(23), sowhat=t23[2],
          notes="The five rule families scored on Choose.")
table(s, 0.55, 1.75, rt, [2.6, 3.4, 2.3, 1.55, 2.4], row_h=0.5, key_rows=(5,), colors={(2, 4): RED, (3, 4): RED})
text(s, 0.55, 4.9, 12.25, 0.9, t23[5].split("\n"), size=12.5, space_after=4)

# ---- B27-B28 earlier experiments
t24 = s_texts(24)
s = frame("B27", "With one buffer every earlier model looked cheaper on Choose, mostly because the flat rule needed a large shared buffer",
          part="B", topic="Earlier experiments: Choose results", roles=("Model Lead",), source=s_source(24), sowhat=t24[2],
          foot=t24[5], notes="The earlier set on Choose, with one shared buffer and with a buffer per hotel.")
table(s, 0.55, 1.85, s_table(24), [3.0, 2.0, 3.6, 3.65], row_h=0.6, key_rows=(5,))
s = frame("B28", "On the 2017 test the earlier models did not beat the flat rule within the limit; the refitted ones breached it",
          part="B", topic="Earlier experiments: every test run", roles=("Model Lead",), source=s_source(24), sowhat=t24[2],
          foot=t24[-1], notes="Every earlier test run.")
rows = [["Test run (Jan–Aug 2017)", "Method", "Cost", "Walks per 1,000", "Limit"],
        [t24[7], t24[8], t24[9], t24[10], t24[11]], [t24[7], t24[12], t24[13], t24[14], t24[15]],
        [t24[16], t24[17], t24[18], t24[19], t24[20]], [t24[16], t24[21], t24[22], t24[23], t24[24]]]
table(s, 0.55, 1.85, rows, [4.8, 2.8, 1.5, 1.75, 1.4], row_h=0.6, colors={(3, 4): RED, (4, 4): RED})
text(s, 0.55, 5.0, 12.2, 0.8, "Run 1 was frozen before any test result. Run 3 was decided after run 1, refitted on Train + Choose with "
                               "buffers unchanged. All runs are reported, as the contract requires.", size=12.5)

# ---- B29 the choice
t25 = s_texts(25)
s = frame("B29", "Two separate choices were frozen on Choose: the model (calibrated logistic regression) and the rule (flat rule, 17 rooms)",
          part="B", topic="The final choice and its 2017 result in full", roles=("Model Lead",), source=s_source(25), sowhat=t25[2],
          foot=t25[-1].split("\n")[1] if "\n" in t25[-1] else "", notes="The final choice in full.")
card(s, 0.55, 1.75, 5.9, 1.45, t25[6], t25[7], tag=t25[5], tag_color=ALT, size=12.5)
card(s, 0.55, 3.35, 5.9, 1.45, t25[9], t25[10], tag=t25[8], tag_color=ACCENT, fill=ACCENT_TINT, size=12.5)
table(s, 6.75, 1.75, s_table(25), [2.0, 1.25, 0.75, 0.8, 0.65, 0.6], row_h=0.5, key_rows=(1,), colors={(4, 5): RED})
text(s, 6.75, 4.4, 6.0, 1.4, [t25[11], [(t25[-1].split("\n")[0], {"color": AMBER})]], size=12.5, space_after=4)

# ---- B30 engineering
t26 = s_texts(26)
s = frame("B30", "The analysis reproduces end to end, but the nightly command still serves the earlier per-hotel rule",
          part="B", topic="Engineering and reproducibility", roles=("Build Lead",), source=s_source(26), sowhat=t26[2],
          notes="Engineering status.")
for i in range(6):
    head, sub, status = t26[5 + 3 * i], t26[6 + 3 * i], t26[7 + 3 * i]
    xx, yy = 0.55 + (i % 2) * 6.2, 1.8 + (i // 2) * 1.32
    ok = status == "Done"
    box(s, xx, yy, 6.05, 1.18, TINT if ok else AMBER_TINT, radius=0.05)
    text(s, xx + 0.2, yy + 0.12, 4.4, 0.35, head, size=14, bold=True, color=INK)
    text(s, xx + 0.2, yy + 0.52, 4.6, 0.6, sub, size=12.5, color=BODY_C)
    box(s, xx + 4.85, yy + 0.14, 1.0, 0.28, PAPER, line=INK if ok else AMBER, radius=0.5, label=status, size=11,
        color=INK if ok else AMBER, bold=True)

# ---- B31 questions for the author
s = frame("B31", "Questions for the author: points the source leaves unclear, flagged rather than guessed", part="B",
          topic="Questions for the author", source="Comparison of the source deck's slides with each other and with the repository",
          notes="Each question is something the source deck leaves open or states two ways. Nothing here changes a number.")
QUESTIONS = [
    "The formatting brief ends mid-sentence ('…and reuse a'). The process diagram (A4) is reused as a small step strip on later slides — is that what was meant?",
    "Source slide 6 labels the test period 'Test · once', while slides 24–25 say the 2017 period was examined in earlier runs. Which wording should stand?",
    "Source slide 15 says hotel is encoded as 'one 0/1 column' and agents '< 30 bookings pooled' (notebook 10), but slide 19 describes the final pipeline's one-hot encoding (hotel: 2 values, no pooling). Which encoding should B14 describe?",
    "Source slide 22 shows '42%' and '94% · 53 rooms'; its notes say 41.6% and 94.3%. Both are kept — which precision should the chart use?",
    "The repository has a second deck recommending the per-hotel flat rule (City 20 / Resort 4). This deck recommends the 17-room rule. Which is the client recommendation?",
    "The nightly command serves the 20 / 4 rule, not the 17-room rule. Should it be rewired before any shadow run?",
    "No owners are given for the next steps (docs/ROADMAP.md is blank). Who owns each step?",
    "The evidence tags (High / Medium / Low) are this deck's reading of the source's own caveats. Please confirm or adjust them.",
]
for i, q in enumerate(QUESTIONS):
    yy = 1.75 + i * 0.6
    box(s, 0.55, yy + 0.05, 0.36, 0.36, AMBER, shape=MSO_SHAPE.OVAL, label=str(i + 1), size=12, color=PAPER, bold=True)
    text(s, 1.1, yy, 11.7, 0.55, q, size=12.5, anchor=MSO_ANCHOR.MIDDLE)

# ---- B32 where each original slide went
s = frame("B32", "Where each original slide's content went: every slide of the source deck is carried into this one", part="B",
          topic="Map from the original deck to this one", source=str(SRC_PATH.name), notes="Slide map; also written to PRESENTATION_EXEC_MAPPING.md.")
MAP_NO = len(prs.slides._sldIdLst)
MAP[MAP_NO] = []

# ---- appendix index (filled now that every appendix slide exists)
s = index_slide
box(s, 0, 0, 13.333, 7.5, PAPER)
pill(s, 0.55, 0.3, "B0 · APPENDIX INDEX", ALT, PAPER)
text(s, 0.55, 0.68, 12.25, 1.0, "The appendix holds the full technical detail, grouped by topic in the order the work was done", size=24,
     bold=True, color=INK)
half = (len(INDEX) + 1) // 2
for col, chunk in enumerate([INDEX[:half], INDEX[half:]]):
    rows = [["Slide", "Code", "Topic"]] + [[str(n), c, t] for c, n, t in chunk]
    table(s, 0.55 + col * 6.2, 1.75, rows, [0.75, 0.75, 4.55], row_h=min(0.29, 4.9 / len(rows)), size=12, right={0})
text(s, 12.25, 6.97, 0.55, 0.3, str(INDEX_NO), size=10.5, color=SOFT, align=PP_ALIGN.RIGHT)
s.notes_slide.notes_text_frame.text = "Index of the appendix slides."

# ---- fill the slide map (B32) and the markdown copy
where = {}
for new, olds in MAP.items():
    for o in olds:
        where.setdefault(o, []).append(new)
# content carried by text or tables without the notes, recorded by hand from the build above
EXTRA = {1: [2], 2: [5, 6], 3: [4, 18], 4: [6, 20], 6: [4, 19], 7: [7], 8: [21, 22], 9: [23, 24], 10: [25], 11: [26], 12: [27],
         13: [28], 14: [8, 29], 15: [30], 16: [31], 17: [32], 18: [33, 34, 35], 19: [36, 37], 20: [38, 39], 21: [9, 40, 41],
         22: [10], 23: [11, 42], 24: [13, 43, 44], 25: [2, 12, 45], 26: [14, 46], 27: [14, 15], 5: [17]}
for o, news in EXTRA.items():
    where[o] = sorted(set(where.get(o, [])) | set(news))
rows = [["Original", "Topic in the original", "Now on slides"]]
for o in range(1, 28):
    topic = s_texts(o)[0].title() if o > 1 else "Title and answer"
    rows.append([str(o), topic[:46], ", ".join(map(str, where.get(o, [])))])
s = prs.slides[MAP_NO - 1]
half = 14
for col, chunk in enumerate([rows[1:half + 1], rows[half + 1:]]):
    table(s, 0.55 + col * 6.2, 1.75, [rows[0]] + chunk, [0.95, 3.6, 1.5], row_h=0.28, size=12, right={0})
md = ["# Executive deck: where each original slide went", "",
      f"Source: `{SRC_PATH.name}` (27 slides) → `{OUT.name}` ({len(prs.slides)} slides).", "",
      "| Original slide | Topic | Now on slides |", "|---|---|---|"]
md += [f"| {r[0]} | {r[1]} | {r[2]} |" for r in rows[1:]]
md += ["", "## Questions for the author", ""] + [f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS)]
(ROOT / "PRESENTATION_EXEC_MAPPING.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# ---- checks: every source note carried; every number on a source slide appears in the new deck
assert CARRIED >= set(range(1, 28)), sorted(set(range(1, 28)) - CARRIED)
num = re.compile(r"€?\d[\d,]*(?:\.\d+)?%?")
src_nums = set()
for i in range(1, 28):
    for t in s_texts(i):
        src_nums.update(m.group(0).rstrip(",") for m in num.finditer(t))
    for k in range(3):
        try:
            for r in s_table(i, k):
                for c in r:
                    src_nums.update(m.group(0).rstrip(",") for m in num.finditer(c))
        except IndexError:
            break
new_text = []
for sl in prs.slides:
    for sh in sl.shapes:
        if sh.has_text_frame:
            new_text.append(sh.text_frame.text)
        if sh.has_table:
            new_text += [c.text for r in sh.table.rows for c in r.cells]
    new_text.append(sl.notes_slide.notes_text_frame.text)
blob = "\n".join(new_text)
missing = sorted(n for n in src_nums if n not in blob)
print("source numbers:", len(src_nums), "missing:", missing)
prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
