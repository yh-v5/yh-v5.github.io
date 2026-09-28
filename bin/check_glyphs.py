"""List em dashes (—) and middle dots (·) in the visible text of a built site.

The site uses neither (use "/", commas, colons or parentheses instead). Run after
a build; exits 1 if any are found.

Usage:
    python3 bin/check_glyphs.py _site
"""
import os
import sys
from html.parser import HTMLParser

GLYPHS = "—·"  # em dash, middle dot


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.hits = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and any(g in data for g in GLYPHS):
            self.hits.append(" ".join(data.split())[:100])


def main(root):
    found = 0
    for dirpath, _, files in os.walk(root):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            parser = VisibleText()
            with open(path, encoding="utf-8", errors="ignore") as f:
                parser.feed(f.read())
            for hit in parser.hits:
                print(f"{os.path.relpath(path, root)}: {hit}")
                found += 1
    print(f"{found} occurrence(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "_site"))
