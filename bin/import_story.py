"""Convert a story exported as HTML (h1 / h2 / p / hr / blockquote / em) into
_stories/<slug>.md for the Stories section.

Usage:
    python3 bin/import_story.py EXPORT.html --slug neoui-ullim --year 2021 --num 01 \
        --title "Your Resonance" --description "One line, in English."

The site shows an English title and a one-line English description (list page
and story header); the export's h1 is kept only as `title_ko`. A first
paragraph that is entirely italic (a subtitle) is dropped.
Chapters (h2) get stable anchors (#ch-1, #ch-2, ...) for the table of contents.
Line breaks inside a paragraph are kept as hard breaks, and paragraphs that are
only a scene-break glyph (◇ etc.) are marked with the "sep" class.

The site shows no em dashes (—) or middle dots (·). Separators in chapter
titles are rewritten ("1 · 제목" -> "1. 제목", "제목 — 부제" -> "제목: 부제",
"제목 — 〈연재명〉 N번째" -> small second line). Any left in the prose are
listed at the end so they can be fixed by hand.

Re-running the script overwrites _stories/<slug>.md.
"""
import argparse
import os
import re
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


class Blocks(HTMLParser):
    """Flatten the export body into (kind, text) blocks; inline <em> -> *...*."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.buf = None
        self.kind = None
        self.in_quote = False
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if not self.in_body:
            return
        if tag in ("h1", "h2", "p"):
            self.kind = ("quote-p" if self.in_quote and tag == "p" else tag)
            self.buf = []
        elif tag == "em" and self.buf is not None:
            self.buf.append("\x01")
        elif tag == "br" and self.buf is not None:
            self.buf.append("\n")
        elif tag == "hr":
            self.blocks.append(("hr", ""))
        elif tag == "blockquote":
            self.in_quote = True
            self.blocks.append(("quote-start", ""))

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "p") and self.buf is not None:
            self.blocks.append((self.kind, "".join(self.buf)))
            self.buf = None
        elif tag == "em" and self.buf is not None:
            self.buf.append("\x02")
        elif tag == "blockquote":
            self.in_quote = False
            self.blocks.append(("quote-end", ""))

    def handle_data(self, data):
        if self.buf is not None:
            self.buf.append(data)


def escape_md(text):
    text = text.replace("\\", "\\\\")
    for ch in "`*_[]<>|":
        text = text.replace(ch, "\\" + ch)
    return text


def inline(raw):
    """Escape Markdown, restore italics, keep in-paragraph line breaks."""
    lines = []
    for line in raw.strip().split("\n"):
        line = escape_md(line.strip())
        line = line.replace("\x01", "*").replace("\x02", "*")
        # things that would start a block construct at the beginning of a line
        line = re.sub(r"^(\d+)\.(\s)", r"\1\\.\2", line)
        line = re.sub(r"^([-+#>=])", r"\\\1", line)
        lines.append(line)
    return "<br>\n".join(l for l in lines if l)


# Paragraphs that are only a scene-break glyph get centred (class "sep").
SCENE_BREAKS = {"◇", "◆", "＊", "\\*", "\\* \\* \\*", "⁂", "·", "· · ·"}


def heading(text):
    """Chapter title without em dashes / middle dots (see module docstring)."""
    t = " ".join(text.split())
    t = re.sub(r"^(\d+)\s*[·—]\s*", r"\1. ", t)
    m = re.match(r"^(.*?)\s+—\s+(〈.*)$", t)
    if m:
        return f"{escape_md(m.group(1))} <small>{escape_md(m.group(2))}</small>"
    t = re.sub(r"\s*[—·]\s*", ": ", t, count=1)
    return escape_md(t)


def is_all_italic(raw):
    r = raw.strip()
    return r.startswith("\x01") and r.endswith("\x02") and r.count("\x01") == 1


def convert(path):
    p = Blocks()
    p.feed(open(path, encoding="utf-8").read())
    blocks = p.blocks
    title = next(t for k, t in blocks if k == "h1").strip()
    i = [k for k, _ in blocks].index("h1") + 1
    subtitle = None
    if i < len(blocks) and blocks[i][0] == "p" and is_all_italic(blocks[i][1]):
        subtitle = blocks[i][1].strip().strip("\x01\x02").strip()
        i += 1
        if i < len(blocks) and blocks[i][0] == "hr":
            i += 1
    out, ch, quote = [], 0, None
    for kind, text in blocks[i:]:
        if kind == "h2":
            ch += 1
            out.append(f"## {heading(text)} {{#ch-{ch}}}")
        elif kind == "p":
            s = inline(text)
            if s in SCENE_BREAKS:
                out.append("◇\n{: .sep}")  # one glyph for every scene break
            elif s:
                out.append(s)
        elif kind == "quote-start":
            quote = []
        elif kind == "quote-p":
            s = inline(text)
            if s:
                quote.append("\n".join("> " + l for l in s.split("\n")))
        elif kind == "quote-end":
            if quote:
                out.append("\n>\n".join(quote))
            quote = None
        elif kind == "hr":
            out.append("---")
    return title, subtitle, "\n\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--year", required=True, type=int)
    ap.add_argument("--num", required=True)
    ap.add_argument("--title", required=True, help="English title shown on the site")
    ap.add_argument("--description", required=True, help="one-line English description")
    a = ap.parse_args()
    title_ko, subtitle, body = convert(a.export)
    q = lambda v: '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    fm = [
        "---",
        f"title: {q(a.title)}",
        f"title_ko: {q(title_ko)}",
        f'num: "{a.num}"',
        f"year: {a.year}",
        f"date: {a.year}-01-01",
        f"description: {q(a.description)}",
        "---",
    ]
    dest = os.path.join(ROOT, "_stories", a.slug + ".md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(fm) + "\n\n" + body)
    print("wrote", os.path.relpath(dest, ROOT))
    if subtitle:
        print("dropped subtitle:", subtitle)
    lines = ("\n".join(fm) + "\n\n" + body).split("\n")
    left = [(i, l) for i, l in enumerate(lines, 1) if re.search("[—·]", l)]
    for i, l in left:
        print(f"  line {i}: em dash / middle dot left in the text: {l[:80]}")
    if left:
        print("fix these by hand (comma, colon, parentheses or …)")


if __name__ == "__main__":
    main()
