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

ORD = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
TIMES = {1: "once", 2: "twice", 3: "three times"}

def desc(k):
    return {1: "child", 2: "grandchild", 3: "great-grandchild"}.get(k, f"{k - 2}x-great-grandchild")

# (generations from common ancestor to YOU, to the MATCH, half?)  a + b + half = meioses
SPEC = {"SIBLING": (1, 1, 0), "HALF_SIBLING": (1, 1, 1),
        "AUNT_NIECE": (2, 1, 0), "HALF_AUNT_NIECE": (2, 1, 1),
        "GREAT_AUNT": (3, 1, 0), "HALF_GREAT_AUNT": (3, 1, 1),
        "GG_AUNT": (4, 1, 0), "HALF_GG_AUNT": (4, 1, 1)}

def paths(r):
    if r["id"] in SPEC:
        return SPEC[r["id"]]
    n, m = int(r["cousin_degree"]), int(r["removed"])
    return n + 1, n + 1 + m, int(r["half"])

# Close family: name + two examples (older = match is the older generation)
CLOSE = {
 "SIBLING": {"same": ("Your full sibling", ["your brother", "your sister"])},
 "HALF_SIBLING": {"same": ("Your half-sibling", ["your father's daughter by another partner", "your mother's son by another partner"])},
 "AUNT_NIECE": {"older": ("An aunt or uncle", ["your mother's brother", "your father's sister"]),
                "younger": ("A niece or nephew", ["your brother's daughter", "your sister's son"])},
 "HALF_AUNT_NIECE": {"older": ("A half aunt or uncle", ["your mother's half-brother", "your father's half-sister"]),
                     "younger": ("A half niece or nephew", ["your half-brother's daughter", "your half-sister's son"])},
 "GREAT_AUNT": {"older": ("A great-aunt or great-uncle", ["your grandmother's brother", "your grandfather's sister"]),
                "younger": ("A grand-niece or grand-nephew", ["your brother's granddaughter", "your sister's grandson"])},
 "HALF_GREAT_AUNT": {"older": ("A half great-aunt or great-uncle", ["your grandmother's half-brother", "your grandfather's half-sister"]),
                     "younger": ("A half grand-niece or grand-nephew", ["your half-brother's granddaughter", "your half-sister's grandson"])},
 "GG_AUNT": {"older": ("A great-great-aunt or great-great-uncle", ["your great-grandmother's brother", "your great-grandfather's sister"]),
             "younger": ("A great-grand-niece or great-grand-nephew", ["your brother's great-granddaughter", "your sister's great-grandson"])},
 "HALF_GG_AUNT": {"older": ("A half great-great-aunt or great-great-uncle", ["your great-grandmother's half-brother", "your great-grandfather's half-sister"]),
                  "younger": ("A half great-grand-niece or great-grand-nephew", ["your half-brother's great-granddaughter", "your half-sister's great-grandson"])},
}

LINEAL = {
 "PARENT_CHILD": ("Your parent or child", ["your mother", "your son"], "your own household", [
   "<b>Start at home.</b> A match this close is a parent or a child, which birth records, adoption papers, or family knowledge usually settle.",
   "<b>Unknown parent?</b> A parent matches relatives on one side of your family only. The match's shared matches show which side.",
   "<b>Check ages.</b> A parent is typically 18 to 45 years older than the child."]),
 "GRANDPARENT": ("Your grandparent or grandchild", ["your mother's mother", "your daughter's son"], "your grandparents (4 people: 2 paternal, 2 maternal)", [
   "<b>List your four grandparents</b> and your children's children. The match is one of them, unless it is an aunt, uncle, or half-sibling (same cM range).",
   "<b>Use the age gap.</b> A grandparent is usually 40 to 70 years older than you. A match closer to your age is more likely an aunt, uncle, or half-sibling.",
   "<b>Check shared matches.</b> A grandparent matches relatives on one side of your family only."]),
 "GREAT_GRANDPARENT": ("Your great-grandparent or great-grandchild", ["your father's father's mother", "your grandson's daughter"], "your great-grandparents (8 people: 4 paternal, 4 maternal)", [
   "<b>List your eight great-grandparents</b> and your grandchildren's children, and check which could have tested.",
   "<b>Use the age gap.</b> A great-grandparent is usually 60 to 100 years older. A match close in age is more likely a great-aunt, great-uncle, or half-aunt/uncle.",
   "<b>Check shared matches</b> to confirm one side of the family before narrowing to one ancestor."]),
}

def _n(k, w):
    return f"{k} {w}" + ("" if k == 1 else "s")

def _scen(title, name, exs, g, v, half):
    """One scenario: ancestor at your generation g, match v generations below that ancestor."""
    ppl = 2 ** g
    who = f"{'one of ' if half else ''}your {anc(g, True)} ({ppl} people: {ppl // 2} paternal, {ppl // 2} maternal)"
    if g >= 6:
        who += ". Start with the side you suspect rather than checking all of them"
    other = f"your {anc(g - 1)}" if g > 1 else "you"
    lo, hi = 25 * v, 35 * v
    if half:
        s1 = f"<b>Pick one ancestor.</b> Half relatives share only one, so test each of the {ppl} separately."
        s2 = ("<b>List their other partners and children.</b> Include second marriages, remarriages, and unmarried "
              "partners. The match comes from a partner who is NOT the one in your direct line.")
    else:
        s1 = "<b>Pick a couple.</b> " + ("Start with your parents." if g == 1 else
             f"Start with one {anc(g)} couple, on the side you think the match is on.")
        s2 = f"<b>List their other children.</b> Every child except {other}, including any who died young or moved away."
    below = "the ancestor" if half else ("your parents" if g == 1 else "the couple")
    s3 = ("<b>Follow those lines down.</b> " + (
          f"The match should be one of those children, born roughly {lo} to {hi} years after {below}. " if v == 1 else
          f"Trace each child's descendants {_n(v, 'generation')} below {below}. The match should be born roughly "
          f"{lo} to {hi} years after them. ") + "Look for surnames and places that fit your match.")
    s4 = ("<b>Confirm.</b> Shared matches should fall on the same side of your family. "
          "If nothing fits, try the next relationship on the list.")
    return {"title": title, "name": name, "examples": exs, "where": who, "steps": [s1, s2, s3, s4]}

def _cousin(r, g_you, g_match, half, n, m):
    """(younger-or-same scenario examples, older scenario examples) for a cousin relationship."""
    a, b, hs = n + 1, n + 1 + m, ("half-" if half else "")
    oth = lambda k, g: f"a {desc(k)} of one of your {anc(g, True)} by that ancestor's other partner"
    if m == 0:
        A = f"the {desc(n)} of your {anc(n)}'s {hs}sibling"
        B = (oth(a, a) if half else "another grandchild of one of your grandparents") if n == 1 else (
            oth(a, a) if half else f"the child of one of your parent's {ORD[n - 1]} cousins")
        return [A, B], None
    yA = f"the {desc(n + m)} of your {anc(n)}'s {hs}sibling"
    yB = oth(b, a) if half else (f"a {desc(b)} of one of your {anc(a, True)}" if n == 1 else
                                 f"the {desc(m + 1)} of one of your parent's {ORD[n - 1]} cousins")
    oA = f"your {anc(m)}'s {'half ' if half else ''}{ORD[n]} cousin"
    oB = oth(a, b) if half else f"a {desc(a)} of one of your {anc(b, True)}, outside your direct line"
    return [yA, yB], [oA, oB]

def _clean(r, half, n, m):
    """Single readable example for distant cousins."""
    hc = "half " if half else ""
    if m == 0:
        return [f"the child of one of your parent's {hc}{ORD[n - 1]} cousins"], None
    return [f"the {desc(m)} of your {hc}{ORD[n]} cousin"], [f"your {anc(m)}'s {hc}{ORD[n]} cousin"]

def guidance(r):
    """List of scenarios: title, name, two examples, where to look, four steps."""
    if r["id"] in LINEAL:
        name, exs, where, steps = LINEAL[r["id"]]
        return [{"title": "", "name": name, "examples": exs, "where": where, "steps": steps}]
    a, b, half = paths(r)
    d = b - a
    if r["category"] == "cousin":
        n, m = int(r["cousin_degree"]), int(r["removed"])
        name = f"A {'half ' if half else ''}{ORD[n]} cousin" + (f" {TIMES[m]} removed" if m else "")
        young, old = _cousin(r, a, b, half, n, m)
        import re
        if n >= 4 or re.search(r"\b[3-9]x-great", " ".join(young + (old or []))):
            young, old = _clean(r, half, n, m)
    else:
        name, young, old = None, None, None
    if d == 0:
        nm, ex = (name, young) if name else CLOSE[r["id"]]["same"]
        return [_scen("", nm, ex, a, b, half)]
    k = abs(d)
    out = []
    for word, g, v in (("younger" if d > 0 else "older", a, b), ("older" if d > 0 else "younger", b, a)):
        if name:
            nm, ex = name, (young if g == a else old)
        else:
            nm, ex = CLOSE[r["id"]][word]
        ago = "after" if word == "younger" else "before"
        out.append(_scen(f"If the match is {_n(k, 'generation')} {word} than you (born roughly {25 * k} to {35 * k} years {ago} you)",
                         nm, ex, g, v, half))
    return out
