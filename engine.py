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

SPEC = {"PARENT_CHILD": (1, 0, 0), "GRANDPARENT": (2, 0, 0), "GREAT_GRANDPARENT": (3, 0, 0),
        "SIBLING": (1, 1, 0), "HALF_SIBLING": (1, 1, 1),
        "AUNT_NIECE": (2, 1, 0), "HALF_AUNT_NIECE": (2, 1, 1),
        "GREAT_AUNT": (3, 2, 0), "HALF_GREAT_AUNT": (3, 2, 1),
        "GG_AUNT": (4, 3, 0), "HALF_GG_AUNT": (4, 3, 1)}

def paths(r):
    """(generations from common ancestor to YOU, to the MATCH, half?)"""
    if r["id"] in SPEC:
        return SPEC[r["id"]]
    n, m = int(r["cousin_degree"]), int(r["removed"])
    return n + 1, n + 1 + m, int(r["half"])

LINEAL = {
 "PARENT_CHILD": [("Parent or child", [
   "<b>Check your own household first.</b> A match this close is a parent or a child. Birth certificates, adoption papers, and family knowledge settle it quickly.",
   "<b>Unknown parent?</b> A parent matches relatives on ONE side of your family only (paternal or maternal). Use the match's shared matches to see which side.",
   "<b>Check the ages.</b> A parent is usually 18-45 years older than the child."])],
 "GRANDPARENT": [("Grandparent or grandchild", [
   "<b>List your four grandparents</b> and your children's children. The match is one of them, unless it is an aunt/uncle or half-sibling (same cM range).",
   "<b>Use the age gap to separate them.</b> A grandparent is usually 40-70 years older. An aunt/uncle or half-sibling is closer to your parents' or your own age.",
   "<b>Use shared matches.</b> A grandparent matches relatives on one side only. A half-sibling matches one parent's side only."])],
 "GREAT_GRANDPARENT": [("Great-grandparent or great-grandchild", [
   "<b>List your eight great-grandparents</b> (or your grandchildren's children) and check which could still be alive or have tested.",
   "<b>Check the ages.</b> A great-grandparent is usually 60-100 years older. A match close in age is more likely a great-aunt/uncle or half-aunt/uncle.",
   "<b>Use shared matches</b> to confirm one family side before narrowing to one ancestor."])],
}

def _n(k, w):
    return f"{k} {w}" + ("" if k == 1 else "s")

def _flow(g, v, half):
    """Step-by-step research flow: common ancestor at your generation g, match v generations below."""
    ancs, other = 2 ** g, (f"your {anc(g - 1)}" if g > 1 else "you")
    s = [f"<b>Find the ancestor{'' if half else ' couple'}.</b> Open your tree to your {anc(g, True)}: "
         f"{ancs} people ({ancs // 2} paternal, {ancs // 2} maternal). "
         + ("The match shares only ONE of them, so test each ancestor separately." if half else
            "The match descends from a couple, so work one couple at a time.")]
    s.append("<b>List every partner and child.</b> For each ancestor, list all spouses and partners (second marriages, "
             "remarriages, unmarried partners) and every child by each. The match descends from a partner who is NOT the "
             "one in your direct line. Check probate, church, and census records for step-children." if half else
             f"<b>List their other children.</b> For each couple, list every child except {other}, "
             "including children who died young or moved away.")
    s.append(f"<b>Build the descendants.</b> Follow each of those children down {_n(v, 'generation')} in total, until you "
             f"reach someone who could be the match. At 25-35 years per generation, the match should be born roughly "
             f"{25 * v}-{35 * v} years after the ancestor.")
    s.append("<b>Compare with the match.</b> Check the match's surnames, birthplaces, and tree (or username and location "
             "if the tree is private). Look for those names and places in the lines you just built.")
    s.append("<b>Confirm with shared matches.</b> Open the match's shared matches. Others who match both of you should "
             "sit on the same ancestor line. Group them by paternal or maternal side.")
    s.append("<b>If nothing fits.</b> The same cM fits neighboring relationships. Try the next candidate in the list, "
             "or the same search one ancestor level up or down. Also allow for unknown parentage in either line.")
    return s

def guidance(r):
    """List of (heading, [steps]) giving a research workflow for one relationship."""
    if r["id"] in LINEAL:
        return LINEAL[r["id"]]
    a, b, half = paths(r)
    d = b - a
    if d == 0:
        return [("Where to look", _flow(a, b, half))]
    k, out = abs(d), []
    for word, g, v in (("YOUNGER" if d > 0 else "OLDER", a, b), ("OLDER" if d > 0 else "YOUNGER", b, a)):
        gap = f"born roughly {25 * k}-{35 * k} years {'after' if word == 'YOUNGER' else 'before'} you"
        out.append((f"If the match is {_n(k, 'generation')} {word} than you ({gap})", _flow(g, v, half)))
    return out
