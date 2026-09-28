"""Generate blueprint-style schematic SVGs for the exhibit pages.

Output goes to _includes/works/fig-*.svg and is inlined by _layouts/exhibit.html,
so every colour comes from site CSS classes (bp-*) and follows the light/dark theme.

Usage: python3 bin/gen_work_figures.py
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_includes", "works")
W, H = 960, 540


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, fid, title, desc):
        self.fid = fid
        self.parts = []
        self.title = title
        self.desc = desc

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, cls="bp-ln", extra=""):
        self.add(f'<rect class="{cls}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{extra}/>')

    def line(self, x1, y1, x2, y2, cls="bp-ln", extra=""):
        self.add(f'<line class="{cls}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"{extra}/>')

    def path(self, d, cls="bp-ln", extra=""):
        self.add(f'<path class="{cls}" d="{d}"{extra}/>')

    def text(self, x, y, s, cls="bp-t", anchor="start", extra=""):
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        self.add(f'<text class="{cls}" x="{x:g}" y="{y:g}"{a}{extra}>{esc(s)}</text>')

    def arrow(self, x1, y1, x2, y2, cls="bp-ln"):
        self.line(x1, y1, x2, y2, cls, f' marker-end="url(#ah-{self.fid})"')

    def dim_h(self, x1, x2, y, label, cls="bp-t2"):
        """Horizontal dimension line with end ticks and a centred label."""
        self.line(x1, y, x2, y, "bp-dim")
        self.line(x1, y - 5, x1, y + 5, "bp-dim")
        self.line(x2, y - 5, x2, y + 5, "bp-dim")
        mid = (x1 + x2) / 2
        tw = len(label) * 7.4 + 14
        self.rect(mid - tw / 2, y - 8, tw, 16, "bp-paper")
        self.text(mid, y + 4, label, cls, "middle")

    def dim_v(self, x, y1, y2, label, cls="bp-t2"):
        self.line(x, y1, x, y2, "bp-dim")
        self.line(x - 5, y1, x + 5, y1, "bp-dim")
        self.line(x - 5, y2, x + 5, y2, "bp-dim")
        mid = (y1 + y2) / 2
        self.add(
            f'<text class="{cls}" x="{x - 10:g}" y="{mid:g}" text-anchor="middle" '
            f'transform="rotate(-90 {x - 10:g} {mid:g})">{esc(label)}</text>'
        )

    def frame(self, no, name, sheet):
        # outer sheet + inner margin, registration crosses, title block
        self.rect(10, 10, W - 20, H - 20, "bp-hair")
        self.rect(24, 24, W - 48, H - 48, "bp-ln2")
        for cx, cy in [(24, 24), (W - 24, 24), (24, H - 24), (W - 24, H - 24)]:
            self.line(cx - 9, cy, cx + 9, cy, "bp-ln")
            self.line(cx, cy - 9, cx, cy + 9, "bp-ln")
        self.text(44, 56, f"FIG. {no} / {name}", "bp-tb")
        # title block, bottom-right
        bx, by, bw, bh = W - 24 - 300, H - 24 - 48, 300, 48
        self.rect(bx, by, bw, bh, "bp-ln")
        self.line(bx + 80, by, bx + 80, by + bh, "bp-ln")
        self.line(bx + 220, by, bx + 220, by + bh, "bp-ln")
        self.line(bx, by + 24, bx + bw, by + 24, "bp-hair")
        self.text(bx + 8, by + 16, "FIG.", "bp-t3")
        self.text(bx + 8, by + 40, no, "bp-t")
        self.text(bx + 88, by + 16, "SUBJECT", "bp-t3")
        self.text(bx + 88, by + 40, sheet, "bp-t")
        self.text(bx + 228, by + 16, "SCALE", "bp-t3")
        self.text(bx + 228, by + 40, "N.T.S.", "bp-t")

    def cells(self, x, y, bits, size=20, gap=4, on="bp-on", off="bp-off"):
        for i, b in enumerate(bits):
            cx = x + i * (size + gap)
            self.rect(cx, y, size, size, on if b == "1" else off)
        return x + len(bits) * (size + gap) - gap

    def render(self):
        defs = (
            f'<defs>'
            f'<marker id="ah-{self.fid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            f'<path class="bp-fill" d="M0 0 L10 5 L0 10 z"/></marker>'
            f'<pattern id="hatch-{self.fid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<line class="bp-hatchline" x1="0" y1="0" x2="0" y2="7"/></pattern>'
            f'</defs>'
        )
        body = "\n".join(self.parts).replace("HATCH", f"url(#hatch-{self.fid})")
        return (
            f'<svg class="bp" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t-{self.fid} d-{self.fid}" '
            f'xmlns="http://www.w3.org/2000/svg">\n'
            f'<title id="t-{self.fid}">{esc(self.title)}</title>\n'
            f'<desc id="d-{self.fid}">{esc(self.desc)}</desc>\n'
            f'{defs}\n{body}\n</svg>\n'
        )


def tree(s, x, y, w, h, active_leaves=None, levels=3):
    """Binary adder tree from 2**levels leaves (top) to one root (bottom).
    active_leaves: set of leaf indices that carry a non-zero; None = all active."""
    n = 2 ** levels
    xs = [x + (i + 0.5) * w / n for i in range(n)]
    ys = [y + j * h / levels for j in range(levels + 1)]
    act = [True] * n if active_leaves is None else [i in active_leaves for i in range(n)]
    for i, cx in enumerate(xs):
        s.rect(cx - 5, ys[0] - 5, 10, 10, "bp-on" if act[i] else "bp-off")
    for lvl in range(levels):
        nxt, nact = [], []
        for i in range(0, len(xs), 2):
            px = (xs[i] + xs[i + 1]) / 2
            a = act[i] or act[i + 1]
            for k in (i, i + 1):
                cls = "bp-ln" if act[k] else "bp-ghost"
                s.line(xs[k], ys[lvl] + 5, px, ys[lvl + 1] - 6, cls)
            node_cls = "bp-node" if a else "bp-node-off"
            s.add(f'<circle class="{node_cls}" cx="{px:g}" cy="{ys[lvl + 1]:g}" r="6"/>')
            s.text(px, ys[lvl + 1] + 3.5, "+", "bp-plus" if a else "bp-plus-off", "middle")
            nxt.append(px)
            nact.append(a)
        xs, act = nxt, nact


def fig_hyperspace():
    s = Svg(
        "01",
        "HyperSPACE: XOR-binding versus AND-binding",
        "Schematic. With XOR-binding about half of the bound bits are ones, so popcount needs an exact adder tree. "
        "With AND-binding and sparsity-tuned projection almost every bit is zero, so a sparse adder tree only sums the few non-zeros.",
    )
    s.frame("01", "BINDING SPARSITY", "HYPERSPACE")
    x0 = 170
    lanes = [
        (96, "A / XOR-BINDING", ("1011001110100101", "0110101011001100", "1101100101101001"), "⊕", "ρ ≈ 0.5", "EXACT ADDER TREE", None, "EVERY BIT IS SUMMED"),
        (296, "B / AND-BINDING", ("0000100000010000", "0000100100000010", "0000100000000000"), "∧", "ρ > 0.99", "SPARSE ADDER TREE", {2}, "ONLY NON-ZEROS ARE SUMMED"),
    ]
    for y, name, (h, k, r), op, rho, tname, act, tsub in lanes:
        s.text(44, y + 14, name, "bp-t")
        rows = [("H", h, y + 30), ("K", k, y + 58), (f"H {op} K", r, y + 100)]
        for lab, bits, ry in rows:
            s.text(x0 - 14, ry + 14, lab, "bp-t2", "end")
            xe = s.cells(x0, ry, bits)
        s.line(x0, y + 88, xe, y + 88, "bp-ln")
        s.dim_h(x0, xe, y + 138, f"SPARSITY {rho}")
        # arrow to tree box
        s.arrow(xe + 14, y + 110, 610, y + 110)
        bx, by = 620, y + 36
        s.rect(bx, by, 270, 128, "bp-ln")
        s.text(bx + 12, by + 20, tname, "bp-t")
        s.text(bx + 12, by + 118, tsub, "bp-t3")
        leaves = None if act is None else act
        tree(s, bx + 110, by + 34, 150, 66, leaves)
    s.text(44, 500, "ENCODING ENERGY ↓ UP TO 13.03×  /  ACCURACY ↑ UP TO 3.82%", "bp-tb")
    return s


def fig_dipmemhd():
    s = Svg(
        "02",
        "DiP-MEMHD: pruning dimensions to fit a compact IMC array",
        "Schematic. A long class hypervector of D dimensions is pruned to D-prime, the number of array rows, "
        "using calibration and variance-based weighting. Each class occupies several centroid columns, so the whole compact array is used in one search cycle.",
    )
    s.frame("02", "DIMENSION PRUNING", "DIP-MEMHD")
    # long vector, D dims
    vx, vy, cs, gap = 70, 92, 13, 3
    keep = {1, 4, 6, 9, 13, 15, 18, 21}
    for i in range(24):
        cy = vy + i * (cs + gap)
        if i in keep:
            s.rect(vx, cy, cs * 2, cs, "bp-on")
        else:
            s.rect(vx, cy, cs * 2, cs, "bp-pruned", ' fill="HATCH"')
    s.dim_v(vx - 16, vy, vy + 24 * (cs + gap) - gap, "D DIMENSIONS")
    s.text(vx - 4, 80, "CLASS HV", "bp-t2")
    # prune arrow
    s.arrow(118, 260, 238, 260)
    s.text(178, 246, "PRUNE", "bp-t", "middle")
    s.text(178, 280, "CALIBRATION +", "bp-t3", "middle")
    s.text(178, 294, "VARIANCE WEIGHT", "bp-t3", "middle")
    # array 8x8
    ax, ay, c, g = 330, 112, 33, 4
    classes = ["A", "A", "B", "B", "C", "C", "D", "D"]
    tint = {"A": "bp-t-a", "B": "bp-t-b", "C": "bp-t-c", "D": "bp-t-d"}
    # pruned query D' feeding rows
    qx = 262
    for r in range(8):
        cy = ay + r * (c + g)
        s.rect(qx, cy + 8, 22, c - 16, "bp-on")
        s.line(qx + 22, cy + c / 2, ax, cy + c / 2, "bp-hair")
    s.text(qx + 11, ay - 12, "D′", "bp-t", "middle")
    for col in range(8):
        for r in range(8):
            s.rect(ax + col * (c + g), ay + r * (c + g), c, c, tint[classes[col]])
        s.text(ax + col * (c + g) + c / 2, ay - 12, f"{classes[col]}{col % 2 + 1}", "bp-t2", "middle")
    aw = 8 * (c + g) - g
    s.dim_h(ax, ax + aw, ay - 36, "COLUMNS = CLASSES × CENTROIDS")
    s.dim_v(ax + aw + 26, ay, ay + aw, "ROWS = D′")
    # output: one search cycle
    oy = ay + aw + 10
    for col in range(8):
        cx = ax + col * (c + g) + c / 2
        hgt = [10, 22, 8, 12, 30, 14, 9, 6][col]
        s.rect(cx - 6, oy + 34 - hgt, 12, hgt, "bp-on" if col == 4 else "bp-off")
    s.text(ax, oy + 50, "SIMILARITY IN ONE SEARCH CYCLE → ARGMAX", "bp-t3")
    s.text(720, 118, "COMPACT IMC", "bp-t")
    s.text(720, 136, "64 × 64 / 128 × 128", "bp-t2")
    s.text(720, 184, "+22.4% ACC.", "bp-t")
    s.text(720, 202, "VS. BINARY HDC", "bp-t2")
    s.text(720, 250, "6–8× ENERGY", "bp-t")
    s.text(720, 268, "EFFICIENCY", "bp-t2")
    s.text(720, 316, "+2.47% ACC.", "bp-t")
    s.text(720, 334, "VS. PRUNING METRICS", "bp-t2")
    return s


def fig_memhd():
    s = Svg(
        "03",
        "MEMHD: array utilization with one versus many centroids per class",
        "Schematic. With one vector per class only a few columns of the IMC array are used, and vectors longer than the array need extra cycles. "
        "With multi-centroid class memories every column is used and inference takes one cycle.",
    )
    s.frame("03", "ARRAY UTILIZATION", "MEMHD")
    c, g, cols, rows = 30, 5, 8, 6
    aw = cols * (c + g) - g
    ah = rows * (c + g) - g
    tint = ["bp-t-a", "bp-t-b", "bp-t-c", "bp-t-d"]
    panels = [
        (72, "A / ONE VECTOR PER CLASS", False),
        (520, "B / MULTI-CENTROID (MEMHD)", True),
    ]
    ay = 124
    for ax, name, multi in panels:
        s.text(ax, 90, name, "bp-t")
        for col in range(cols):
            for r in range(rows):
                x, y = ax + col * (c + g), ay + r * (c + g)
                if multi:
                    s.rect(x, y, c, c, tint[col // 2])
                elif col < 4:
                    s.rect(x, y, c, c, tint[col])
                else:
                    s.rect(x, y, c, c, "bp-idle", ' fill="HATCH"')
            lab = f"{'ABCD'[col // 2]}{col % 2 + 1}" if multi else ("ABCD"[col] if col < 4 else "")
            if lab:  # unused (hatched) columns stay unlabelled
                s.text(ax + col * (c + g) + c / 2, ay - 10, lab, "bp-t2", "middle")
        s.rect(ax - 6, ay - 6, aw + 12, ah + 12, "bp-ln")
        if not multi:
            # vector longer than the array: overflow rows, dashed
            for col in range(4):
                for r in range(2):
                    x, y = ax + col * (c + g), ay + ah + 12 + r * (c + g)
                    s.rect(x, y, c, c, "bp-overflow")
            s.text(ax + 4 * (c + g) + 8, ay + ah + 44, "D > ROWS →", "bp-t2")
            s.text(ax + 4 * (c + g) + 8, ay + ah + 60, "EXTRA CYCLES", "bp-t2")
            ix, iy = ax + 6 * (c + g) - g / 2, ay + ah / 2
            s.rect(ix - 26, iy - 9, 52, 18, "bp-paper")
            s.text(ix, iy + 4, "IDLE", "bp-t2", "middle")
            label = "50% USED, ≥ 2 CYCLES"
        else:
            label = "100% USED, 1 CYCLE"
        s.dim_h(ax, ax + aw, ay + ah + 100, label)
    s.text(44, 500, "ACC. ↑ UP TO 13.69% AT EQUAL MEMORY  /  MEMORY EFF. ↑ 13.25×", "bp-tb")
    return s


def fig_hdcnorm():
    s = Svg(
        "04",
        "HDC normalization: class hypervector norm during online retraining",
        "Schematic after Figure 2 of the paper. Without normalization the L2 norm of class hypervectors grows steadily with epochs, "
        "so later updates move the model less. With per-epoch normalization the norm is reset to one after every epoch.",
    )
    s.frame("04", "CLASS-HV NORM", "HDC-NORM")
    px, py, pw, ph = 120, 96, 560, 312  # plot box
    ymax = 10.0

    def X(e):
        return px + e / 100 * pw

    def Y(v):
        return py + ph - v / ymax * ph

    # axes + ticks
    s.line(px, py, px, py + ph, "bp-ln")
    s.line(px, py + ph, px + pw, py + ph, "bp-ln")
    for e in range(0, 101, 20):
        s.line(X(e), py + ph, X(e), py + ph + 6, "bp-ln")
        s.text(X(e), py + ph + 22, str(e), "bp-t3", "middle")
        if e:
            s.line(X(e), py, X(e), py + ph, "bp-hair")
    for v in range(0, 11, 2):
        s.line(px - 6, Y(v), px, Y(v), "bp-ln")
        s.text(px - 12, Y(v) + 4, str(v), "bp-t3", "end")
        if v:
            s.line(px, Y(v), px + pw, Y(v), "bp-hair")
    s.text(px + pw / 2, py + ph + 44, "EPOCH", "bp-t2", "middle")
    s.add(
        f'<text class="bp-t2" x="{px - 44:g}" y="{py + ph / 2:g}" text-anchor="middle" '
        f'transform="rotate(-90 {px - 44:g} {py + ph / 2:g})">‖C‖₂ (MEAN OVER CLASSES)</text>'
    )
    # without normalization: grows roughly like sqrt(epoch)
    pts = [(e, 1 + 8.6 * math.sqrt(e / 100)) for e in range(0, 101, 2)]
    d = "M" + " L".join(f"{X(e):.1f} {Y(v):.1f}" for e, v in pts)
    s.path(d, "bp-curve")
    s.text(X(56), Y(7.9) - 10, "WITHOUT NORMALIZATION", "bp-t", "middle")
    # with normalization: sawtooth reset to 1 each epoch (drawn every 5 epochs for legibility)
    d = f"M{X(0):.1f} {Y(1):.1f}"
    for e in range(0, 100, 5):
        d += f" L{X(e + 5):.1f} {Y(1.45):.1f} L{X(e + 5):.1f} {Y(1):.1f}"
    s.path(d, "bp-curve2")
    s.text(X(56), Y(1) - 30, "PER-EPOCH NORMALIZATION → ‖C‖₂ = 1", "bp-t", "middle")
    # side notes
    s.text(720, 118, "+2.04% MNIST", "bp-t")
    s.text(720, 136, "+1.54% CIFAR-10", "bp-t")
    s.text(720, 154, "AT 100-D HVS", "bp-t2")
    s.text(720, 202, "+1.08% TIME", "bp-t")
    s.text(720, 220, "TRAINING OVERHEAD", "bp-t2")
    s.text(720, 268, "SCHEMATIC", "bp-t3")
    s.text(720, 284, "AFTER FIG. 2 (CIFAR-10,", "bp-t3")
    s.text(720, 300, "D = 10,000, LR = 1E-3)", "bp-t3")
    return s


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [
        ("fig-hyperspace.svg", fig_hyperspace),
        ("fig-dipmemhd.svg", fig_dipmemhd),
        ("fig-memhd.svg", fig_memhd),
        ("fig-hdcnorm.svg", fig_hdcnorm),
    ]:
        with open(os.path.join(OUT, name), "w") as f:
            f.write(fn().render())
        print("wrote", name)
