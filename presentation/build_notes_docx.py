"""Write the speaker notes from Hotel_Overbooking_New_Deck.pptx into a Word file, so the two never disagree.

Run from the repository root after build_deck.py:
    python presentation/build_notes_docx.py [deck.pptx] [out.docx]
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
DECK = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Hotel_Overbooking_New_Deck.pptx"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Hotel_Overbooking_Speaker_Notes.docx"
INK, ORANGE, MUTED, TINT = RGBColor(0x14, 0x21, 0x2B), RGBColor(0xEB, 0x68, 0x34), RGBColor(0x56, 0x61, 0x6B), "F2F4F6"


def slide_texts(slide):
    """Section label and title: the first two text boxes each slide builder writes."""
    texts = [s.text_frame.text.strip() for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()]
    return texts[0], texts[1]


def parse(notes):
    """Split a note written by speaker_notes.py into its parts."""
    time = re.match(r"\[(.+?)\]", notes).group(1)
    part = lambda key: re.search(rf"{key}: (.+)", notes).group(1).strip()
    asked = [line[2:].strip() for line in notes.split("IF ASKED:")[1].splitlines() if line.startswith("• ")] if "IF ASKED:" in notes else []
    return {"time": time, "say": part("SAY"), "point": part("POINT TO"), "next": part("NEXT"), "asked": asked}


def seconds(time):
    return int(re.search(r"(\d+)", time).group(1))


def shade(cell, fill):
    pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def rule(paragraph):
    """A thin line under a paragraph (instead of a table used as a rule)."""
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for k, v in {"w:val": "single", "w:sz": "4", "w:space": "4", "w:color": "D5DAE0"}.items():
        bottom.set(qn(k), v)
    pbdr.append(bottom)
    paragraph._p.get_or_add_pPr().append(pbdr)


def run(paragraph, text, size=11, bold=False, color=INK, font="Calibri", italic=False):
    r = paragraph.add_run(text)
    r.font.name, r.font.size, r.font.bold, r.font.italic, r.font.color.rgb = font, Pt(size), bold, italic, color
    return r


prs = Presentation(DECK)
slides = []
for n, s in enumerate(prs.slides, 1):
    section, title = slide_texts(s)
    section = "Title and answer" if n == 1 else " · ".join(
        w if w[0].isdigit() else w.capitalize() if "ROHIT" not in w else "Rohit Pandey" for w in section.split(" · "))
    slides.append({"n": n, "section": section, "title": title, **parse(s.notes_slide.notes_text_frame.text)})

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)
normal = doc.styles["Normal"]
normal.font.name, normal.font.size = "Calibri", Pt(11)
normal.paragraph_format.space_after = Pt(4)
for name, size, before, after in [("Heading 1", 16, 18, 6), ("Heading 2", 13, 14, 4)]:
    st = doc.styles[name]
    st.font.name, st.font.size, st.font.bold, st.font.color.rgb = "Cambria", Pt(size), True, INK
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):  # use Cambria, not the theme heading font
        st.element.rPr.rFonts.attrib.pop(qn(attr), None)
    st.paragraph_format.space_before, st.paragraph_format.space_after, st.paragraph_format.keep_with_next = Pt(before), Pt(after), True

# Title block
p = doc.add_paragraph()
run(p, "SPEAKER NOTES", 10, True, ORANGE)
p = doc.add_paragraph()
run(p, "How many rooms can each hotel safely oversell tonight?", 22, True, INK, "Cambria")
total_s = sum(seconds(s["time"]) for s in slides)
words = sum(len(s["say"].split()) for s in slides)
p = doc.add_paragraph()
run(p, f"{len(slides)} slides · about {total_s // 60} min {total_s % 60:02d} s planned · {words:,} spoken words "
       f"(about {words / 150:.1f} min at a normal pace) · deck: {DECK.name}", 10, color=MUTED)
rule(p)
p = doc.add_paragraph()
run(p, "How to use: ", 10.5, True)
run(p, "read the SAY text aloud until it comes naturally, then speak from memory. POINT TO says where to direct the panel's eyes; "
       "NEXT is the line that leads into the following slide. IF ASKED gives short answers to the questions most likely on that slide. "
       "The same notes are in the PowerPoint's speaker notes.", 10.5, color=MUTED)

# Run sheet
doc.add_heading("Run sheet", level=1)
table = doc.add_table(rows=1, cols=4)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
widths = [Cm(1.4), Cm(4.6), Cm(8.6), Cm(2.0)]
for cell, head, w in zip(table.rows[0].cells, ["Slide", "Section", "Title", "Time"], widths):
    cell.width = w
    shade(cell, "14212B")
    run(cell.paragraphs[0], head, 10, True, RGBColor(0xFF, 0xFF, 0xFF))
elapsed = 0
for i, s in enumerate(slides):
    row = table.add_row().cells
    elapsed += seconds(s["time"])
    values = [str(s["n"]), s["section"], s["title"],
              f"{seconds(s['time'])} s"]
    for cell, value, w in zip(row, values, widths):
        cell.width = w
        if i % 2:
            shade(cell, TINT)
        run(cell.paragraphs[0], value, 9.5)
    row[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
p = doc.add_paragraph()
run(p, f"Total planned: {total_s // 60} min {total_s % 60:02d} s, including the live run on slide 17. If time is short, "
       "slides 13–15 compress most easily: they recap reasoning already shown.", 9.5, color=MUTED, italic=True)

# One block per slide
doc.add_heading("Slide by slide", level=1)
for s in slides:
    h = doc.add_heading(level=2)
    h.add_run(f"Slide {s['n']} · {s['title']}")
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    run(p, f"{s['section'].upper()}   ", 9, True, ORANGE)
    run(p, s["time"], 9, color=MUTED)
    for label, text in [("SAY", s["say"]), ("POINT TO", s["point"]), ("NEXT", s["next"])]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.3)
        run(p, f"{label}  ", 9, True, ORANGE)
        run(p, text, 11.5 if label == "SAY" else 10.5, color=INK if label == "SAY" else MUTED)
    if s["asked"]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.3)
        p.paragraph_format.keep_with_next = True
        run(p, "IF ASKED", 9, True, ORANGE)
        for qa in s["asked"]:
            q, _, a = qa.partition(" — ")
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Cm(1.0)
            run(p, q + " ", 10.5, True)
            run(p, a, 10.5, color=MUTED)
    rule(doc.add_paragraph())

for zoom in doc.settings.element.iter(qn("w:zoom")):  # python-docx's template omits the required percent
    zoom.set(qn("w:percent"), "100")
doc.core_properties.title = "Speaker notes: Hotel overbooking deck"
doc.save(OUT)
print("saved", OUT, "slides:", len(slides), "planned seconds:", total_s, "spoken words:", words)
