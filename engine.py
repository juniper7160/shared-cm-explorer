"""Ranking + tree guidance. Data: Shared cM Project v4.0 (Bettinger, CC BY 4.0)."""
import csv, json, math

RELS = list(csv.DictReader(open("data/relationships.csv")))
HIST = json.load(open("data/histograms.json"))["histograms"]

def anc(g, plural=False):
    base = {1: "parent", 2: "grandparent", 3: "great-grandparent"}.get(g, f"{g-2}x-great-grandparent")
    return base + ("s" if plural else "")

def density(r, cm):
    """Probability density of this cM under the relationship's histogram."""
    h, N = HIST[r["id"]], int(r["submissions"])
    if "bins" not in h:  # Parent/Child: normal approximation
        mu, sd = float(r["avg_cm"]), float(r["sd_cm"])
        return math.exp(-0.5 * ((cm - mu) / sd) ** 2) / (sd * 2.5066)
    if not (float(r["min_cm"]) <= cm <= float(r["max_cm"])):
        return 1e-9  # outside the published range: effectively ruled out
    w = h["bin_width"]
    floor = 0.1 / (N * w)  # tiny floor so no relationship is ever ruled out entirely
    for b in h["bins"]:
        if (b["lo"] < cm <= b["hi"]) or (cm == 0 and b["lo"] == 0 and b["hi"] > 0):
            return max(b["n"] / (N * w), floor)
    return floor

def rank(cm):
    """Ranked candidates (equal prior; submission counts are NOT used as a prior)."""
    rows = []
    for r in RELS:
        rows.append({"r": r, "d": density(r, cm),
                     "in_range": float(r["min_cm"]) <= cm <= float(r["max_cm"])})
    tot = sum(x["d"] for x in rows)
    for x in rows:
        x["p"] = 100 * x["d"] / tot
    return sorted(rows, key=lambda x: -x["p"])

FIXED = {
 "PARENT_CHILD": ["Your parent or your child. Check your own household and birth records."],
 "SIBLING": ["A full sibling: same two parents. Check parents' children, including any unknown or unrecorded births."],
 "HALF_SIBLING": ["Shares one parent. Look at each of your parents for other partners and other children."],
 "AUNT_NIECE": ["Aunt/uncle (a sibling of your parent) or niece/nephew (a child of your sibling). Check your parents' siblings and your siblings' children."],
 "GRANDPARENT": ["Your grandparent or grandchild. Check your four grandparents (or your children's children)."],
 "GREAT_AUNT": ["Sibling of a grandparent, or the child of a cousin-level sibling line: check your grandparents' siblings and their children."],
 "GREAT_GRANDPARENT": ["Your great-grandparent or great-grandchild. Check your eight great-grandparents."],
 "HALF_AUNT_NIECE": ["Half-sibling of a parent. Look at each parent for a second partner; half-aunts/uncles descend from that parent's other relationship."],
 "GG_AUNT": ["Sibling of a great-grandparent. Check your great-grandparents' siblings."],
 "HALF_GREAT_AUNT": ["Half-sibling of a grandparent. Check each grandparent for a second partner."],
 "HALF_GG_AUNT": ["Half-sibling of a great-grandparent. Check each great-grandparent for a second partner."],
}

def guidance(r):
    """Plain-language 'where to look in your tree' steps for one relationship."""
    if r["id"] in FIXED:
        return FIXED[r["id"]]
    n, m, half = int(r["cousin_degree"]), int(r["removed"]), int(r["half"])
    a = n + 1
    L = []
    if m == 0:
        L.append(f"Common ancestor: your {anc(a, True) if not half else anc(a)} "
                 f"({'one ancestor only, not a couple' if half else 'a couple'}).")
        L.append(f"The match descends from a sibling of your {anc(n)}, {a} generations down.")
    else:
        L.append(f"If the match is {m} generation{'s' if m > 1 else ''} YOUNGER than you: look at your {anc(a, True) if not half else anc(a)}.")
        L.append(f"If the match is {m} generation{'s' if m > 1 else ''} OLDER than you: look at your {anc(a + m, True) if not half else anc(a + m)}.")
        L.append(f"Descendants: the match's line splits off from yours at that ancestor.")
    if half:
        L.append("Half relationship: find the ancestor's OTHER partner. Check second marriages, remarriages, and children born outside the marriage.")
    else:
        L.append("Full relationship: both members of the ancestor couple are candidates. Try each.")
    L.append("Check paternal and maternal sides separately. If you know which side the match is on, search only that side.")
    return L


# ---------- Relationship diagram ----------
# (generations from common ancestor down to YOU, down to the MATCH, half?)
SPEC = {"PARENT_CHILD": (1, 0, 0), "GRANDPARENT": (2, 0, 0), "GREAT_GRANDPARENT": (3, 0, 0),
        "SIBLING": (1, 1, 0), "HALF_SIBLING": (1, 1, 1),
        "AUNT_NIECE": (2, 1, 0), "HALF_AUNT_NIECE": (2, 1, 1),
        "GREAT_AUNT": (3, 2, 0), "HALF_GREAT_AUNT": (3, 2, 1),
        "GG_AUNT": (4, 3, 0), "HALF_GG_AUNT": (4, 3, 1)}

def paths(r):
    if r["id"] in SPEC:
        return SPEC[r["id"]]
    n, m = int(r["cousin_degree"]), int(r["removed"])
    return n + 1, n + 1 + m, int(r["half"])

def diagram(r):
    """Inline SVG: you and the match joined through the common ancestor(s)."""
    a, b, half = paths(r)
    step, top, W, C, L, R = 34, 52, 440, 220, 150, 290
    H = top + max(a, b) * step + 30
    e, n = [], []                       # edges, nodes (drawn on top)
    def node(x, y, cls, r_=8): n.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r_}"/>')
    def text(x, y, t, anchor="middle"): n.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}">{t}</text>')
    def edge(x1, y1, x2, y2): e.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    if b == 0:                          # direct line: the match IS the ancestor
        node(C, top, "ca"); text(C, top - 16, "Match")
        prev = (C, top)
        for k in range(1, a + 1):
            y = top + k * step; edge(*prev, C, y)
            node(C, y, "you" if k == a else "mid"); prev = (C, y)
            text(C - 14, y + 4, "You" if k == a else anc(a - k), "end")
    else:
        if half:
            node(C, top, "ca"); text(C, top - 16, "Common ancestor (one)")
        else:
            edge(C - 14, top, C + 14, top); node(C - 14, top, "ca"); node(C + 14, top, "ca")
            text(C, top - 16, "Common ancestor couple")
        for x, cnt, who, anchor, off in ((L, a, "You", "end", -14), (R, b, "Match", "start", 14)):
            prev = (C, top)
            for k in range(1, cnt + 1):
                y = top + k * step; edge(*prev, x, y)
                last = k == cnt
                node(x, y, ("you" if who == "You" else "mt") if last else "mid"); prev = (x, y)
                text(x + off, y + 4, who if last else anc(cnt - k), anchor)
    svg = (f'<svg class="dia" viewBox="0 0 {W} {H}" role="img" aria-label="Relationship path diagram">'
           + "".join(e) + "".join(n) + "</svg>")
    cap = f'{r["meioses"]} meioses separate you and the match.'
    if r["category"] != "cousin" and b <= 2:
        cap += " Shown with you on the younger side; read it in reverse if you are the older."
    return f'<div class="dwrap">{svg}<div class="dim">{cap}</div></div>'
