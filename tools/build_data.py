"""
Builds data/relationships.csv and data/histograms.json from the
Shared cM Project v4.0 (Blaine T. Bettinger, March 2020, CC BY 4.0).
Source pages: summary table pp. 52-53, histograms pp. 23-47.

Every histogram is verified: bin counts must sum to the published N, and the
published min/max must fall inside the first/last non-empty bin.
Run:  python tools/build_data.py
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# id, label, category, half, n(cousin degree), m(removed), meioses, group,
# N, min, avg, max, sd, expected
# category: lineal | collateral | cousin
R = []
def add(id_, label, cat, half, n, m, meioses, grp, N, mn, av, mx, sd, exp):
    R.append(dict(id=id_, label=label, category=cat, half=half, cousin_degree=n,
                  removed=m, meioses=meioses, grouping=grp, submissions=N,
                  min_cm=mn, avg_cm=av, max_cm=mx, sd_cm=sd, expected_cm=exp))

add("PARENT_CHILD","Parent/Child","lineal",0,"","",1,"",2412,2376,3485,3720,115,"")
add("SIBLING","Sibling","collateral",0,"","",2,1,2465,1613,2613,3488,203,2550)
add("AUNT_NIECE","Aunt/Uncle/Niece/Nephew","collateral",0,"","",3,2,2695,1201,1741,2282,180,1700)
add("GRANDPARENT","Grandparent/Grandchild","lineal",0,"","",3,2,1106,984,1754,2462,236,1700)
add("HALF_SIBLING","Half Sibling","collateral",1,"","",3,2,1266,1160,1759,2436,207,1700)
add("1C","1C","cousin",0,1,0,4,3,3337,396,866,1397,161,850)
add("GREAT_AUNT","Great-Aunt/Uncle/Niece/Nephew","collateral",0,"","",4,3,833,330,850,1467,118,850)
add("GREAT_GRANDPARENT","Great-Grandparent/Great-Grandchild","lineal",0,"","",4,3,149,485,887,1486,181,850)
add("HALF_AUNT_NIECE","Half Aunt/Uncle/Niece/Nephew","collateral",1,"","",4,3,815,492,871,1315,165,850)
add("1C1R","1C1R","cousin",0,1,1,5,4,3700,102,433,980,123,425)
add("GG_AUNT","Great-Great-Aunt/Uncle/Niece/Nephew","collateral",0,"","",5,4,137,186,420,713,121,425)
add("HALF_1C","Half 1C","cousin",1,1,0,5,4,691,156,449,979,134,425)
add("HALF_GREAT_AUNT","Half Great-Aunt/Uncle/Niece/Nephew","collateral",1,"","",5,4,238,184,431,668,105,425)
add("1C2R","1C2R","cousin",0,1,2,6,5,1187,33,221,471,83,213)
add("2C","2C","cousin",0,2,0,6,5,4172,41,229,592,86,213)
add("HALF_1C1R","Half 1C1R","cousin",1,1,1,6,5,605,62,224,469,80,213)
add("HALF_GG_AUNT","Half Great-Great-Aunt/Uncle/Niece/Nephew","collateral",1,"","",6,5,34,103,208,284,43,213)
add("1C3R","1C3R","cousin",0,1,3,7,6,202,25,117,238,48,106)
add("2C1R","2C1R","cousin",0,2,1,7,6,5281,14,122,353,59,106)
add("HALF_1C2R","Half 1C2R","cousin",1,1,2,7,6,165,16,125,269,54,106)
add("HALF_2C","Half 2C","cousin",1,2,0,7,6,512,10,120,325,62,106)
add("2C2R","2C2R","cousin",0,2,2,8,7,1404,0,71,244,42,53)
add("3C","3C","cousin",0,3,0,8,7,4775,0,73,234,43,53)
add("HALF_1C3R","Half 1C3R","cousin",1,1,3,8,7,33,0,60,120,32,53)
add("HALF_2C1R","Half 2C1R","cousin",1,2,1,8,7,474,0,66,190,39,53)
add("2C3R","2C3R","cousin",0,2,3,9,8,163,0,51,154,32,27)
add("3C1R","3C1R","cousin",0,3,1,9,8,4514,0,48,192,32,27)
add("HALF_2C2R","Half 2C2R","cousin",1,2,2,9,8,98,0,48,144,32,27)
add("HALF_3C","Half 3C","cousin",1,3,0,9,8,302,0,48,168,33,27)
add("3C2R","3C2R","cousin",0,3,2,10,9,965,0,36,166,27,13)
add("4C","4C","cousin",0,4,0,10,9,2752,0,35,139,23,13)
add("HALF_3C1R","Half 3C1R","cousin",1,3,1,10,9,249,0,37,139,24,13)
add("3C3R","3C3R","cousin",0,3,3,11,10,106,0,27,98,19,7)
add("4C1R","4C1R","cousin",0,4,1,11,10,2383,0,28,126,20,7)
add("HALF_3C2R","Half 3C2R","cousin",1,3,2,11,10,55,0,27,78,15,7)
add("HALF_4C","Half 4C","cousin",1,4,0,11,10,89,0,30,74,18,7)
add("4C2R","4C2R","cousin",0,4,2,12,"",603,0,22,93,16,3.3)
add("5C","5C","cousin",0,5,0,12,"",1130,0,25,117,18,3.3)
add("4C3R","4C3R","cousin",0,4,3,13,"",89,0,19,60,12,1.7)
add("5C1R","5C1R","cousin",0,5,1,13,"",975,0,21,80,15,1.7)
add("5C2R","5C2R","cousin",0,5,2,14,"",242,0,18,65,12,0.8)
add("6C","6C","cousin",0,6,0,14,"",441,0,18,71,13,0.8)
add("5C3R","5C3R","cousin",0,5,3,15,"",34,0,13,30,7,0.4)
add("6C1R","6C1R","cousin",0,6,1,15,"",441,0,15,56,9,0.4)
add("6C2R","6C2R","cousin",0,6,2,16,"",161,0,13,45,8,0.2)
add("7C","7C","cousin",0,7,0,16,"",258,0,14,57,9,0.2)
add("7C1R","7C1R","cousin",0,7,1,17,"",330,0,12,50,7,0.1)
add("8C","8C","cousin",0,8,0,18,"",239,0,11,42,5,0.05)

# Histograms: id -> (first_bin_upper_edge, step, counts). Bins are (hi-step, hi].
H = {
 "SIBLING":(1600,100,[0,9,6,8,10,9,18,56,155,333,521,566,425,218,91,19,6,1,9,5,0]),
 "AUNT_NIECE":(1200,100,[0,26,66,158,333,513,605,486,311,144,41,12,0]),
 "GRANDPARENT":(900,100,[0,2,4,12,22,35,69,110,196,199,174,128,85,28,28,11,3,0]),
 "HALF_SIBLING":(1100,100,[0,6,20,33,80,117,226,245,234,158,87,37,14,6,3,0]),
 "1C":(300,100,[0,2,34,108,342,653,870,680,419,147,52,30,0]),
 "GREAT_AUNT":(300,100,[0,7,24,39,68,176,201,161,94,43,15,4,1,0]),
 "GREAT_GRANDPARENT":(400,100,[0,1,4,15,31,28,35,19,7,5,2,2,0]),
 "HALF_AUNT_NIECE":(400,100,[0,3,42,82,144,188,182,100,51,20,3,0]),
 "1C1R":(100,100,[0,97,374,1015,1196,701,235,55,18,9,0]),
 "GG_AUNT":(100,100,[0,2,27,32,38,30,7,1,0]),
 "HALF_1C":(100,100,[0,9,63,180,243,119,44,16,11,6,0]),
 "HALF_GREAT_AUNT":(150,50,[0,1,9,15,28,47,46,28,28,18,15,3,0]),
 "1C2R":(0,50,[0,9,63,173,261,265,216,119,55,21,5,0]),
 "2C":(0,50,[0,23,162,534,943,1001,761,386,197,92,50,14,9,0]),
 "HALF_1C1R":(50,50,[0,19,89,148,159,83,56,34,15,2,0]),
 "HALF_GG_AUNT":(100,25,[0,1,2,4,9,9,1,5,3,0]),
 "1C3R":(0,25,[0,1,15,28,33,46,23,29,17,8,2,0]),
 "2C1R":(25,25,[89,500,725,667,1020,791,563,400,227,151,82,35,17,10,4,0]),
 "HALF_1C2R":(25,25,[2,13,22,17,32,20,29,18,7,3,2,0]),
 "HALF_2C":(25,25,[22,45,72,68,96,60,54,39,25,13,7,7,4,0]),
 "2C2R":(25,25,[156,408,302,205,168,89,49,19,7,1,0]),
 "3C":(25,25,[425,1311,1154,689,604,304,149,84,46,9,0]),
 "HALF_1C3R":(25,25,[4,9,9,7,4,0]),
 "HALF_2C1R":(25,25,[60,128,128,60,52,34,8,4,0]),
 "2C3R":(25,25,[35,60,39,14,8,6,1,0]),
 "3C1R":(25,25,[1140,1686,955,387,208,96,30,12,0]),
 "HALF_2C2R":(25,25,[29,29,23,9,4,4,0]),
 "HALF_3C":(25,25,[75,117,61,21,19,3,6,0]),
 "3C2R":(10,10,[96,219,186,140,111,69,53,21,10,23,10,9,8,3,1,5,1,0]),
 "4C":(10,10,[245,579,582,433,330,222,148,78,44,42,19,20,4,6,0]),
 "HALF_3C1R":(10,10,[19,43,57,50,29,15,15,8,2,3,3,2,2,1,0]),
 "3C3R":(10,10,[17,35,23,8,10,6,3,2,1,1,0]),
 "4C1R":(10,10,[335,671,531,342,217,133,62,34,15,18,16,5,4,0]),
 "HALF_3C2R":(10,10,[6,13,18,10,5,1,1,1,0]),
 "HALF_4C":(10,10,[5,29,18,16,8,5,5,3,0]),
 "4C2R":(10,10,[140,200,132,63,26,22,9,5,4,2,0]),
 "5C":(10,10,[213,353,246,120,80,52,31,19,5,6,2,3,0]),
 "4C3R":(10,10,[22,32,19,11,3,1,1,0]),
 "5C1R":(10,10,[262,325,178,96,49,37,21,7,0]),
 "5C2R":(10,10,[71,97,47,11,8,7,1,0]),
 "6C":(10,10,[140,172,64,38,15,5,5,2,0]),
 "5C3R":(10,10,[14,15,5,0]),
 "6C1R":(10,10,[170,174,70,16,9,2,0]),
 "6C2R":(10,10,[74,61,21,3,2,0]),
 "7C":(10,10,[113,104,28,7,3,3,0]),
 "7C1R":(10,10,[175,113,29,8,5,0]),
 "8C":(10,10,[142,81,13,2,1,0]),
}
# Parent/Child: the PDF text did not carry bin labels, so counts are stored
# unbinned and the engine treats it as a range-only relationship.
PC_COUNTS = [0,1,2,0,3,3,2,0,2,1,7,742,746,733,28,142,0]

by_id = {r["id"]: r for r in R}
problems, hist_out = [], {}
for rid, (first, step, counts) in H.items():
    r = by_id[rid]; bins = []
    for i, c in enumerate(counts):
        hi = first + i*step
        bins.append({"lo": max(0, hi-step), "hi": hi, "n": c})
    if sum(counts) != r["submissions"]:
        problems.append(f"{rid}: bin sum {sum(counts)} != N {r['submissions']}")
    nz = [b for b in bins if b["n"] > 0]
    f, l = nz[0], nz[-1]
    if not (r["min_cm"] <= f["hi"] and (r["min_cm"] > f["lo"] or r["min_cm"] == 0 or f["lo"] == 0)):
        problems.append(f"{rid}: min {r['min_cm']} not in first bin ({f['lo']},{f['hi']}]")
    # 1 cM tolerance: published min/max are rounded, bin edges use unrounded values
    if not (l["lo"] - 1 < r["max_cm"] <= l["hi"]):
        problems.append(f"{rid}: max {r['max_cm']} not in last bin ({l['lo']},{l['hi']}]")
    hist_out[rid] = {"bin_width": step, "total": r["submissions"], "bins": bins}
if sum(PC_COUNTS) != 2412: problems.append("PARENT_CHILD sum mismatch")

# Meiosis/grouping consistency: group g <=> g+1 meioses
for r in R:
    if r["grouping"] != "" and r["meioses"] != r["grouping"] + 1:
        problems.append(f"{r['id']}: meioses {r['meioses']} vs group {r['grouping']}")
    if r["category"] == "cousin":
        expect = 2*r["cousin_degree"] + 2 + r["removed"] + r["half"]
        if expect != r["meioses"]:
            problems.append(f"{r['id']}: cousin formula {expect} vs {r['meioses']}")
    if not (r["min_cm"] <= r["avg_cm"] <= r["max_cm"]):
        problems.append(f"{r['id']}: min/avg/max out of order")
missing = [r["id"] for r in R if r["id"] not in H and r["id"] != "PARENT_CHILD"]
if missing: problems.append(f"no histogram for: {missing}")

hist_out["PARENT_CHILD"] = {"bin_width": None, "total": 2412,
    "unbinned_counts": PC_COUNTS,
    "note": "Bin labels not recoverable from PDF text; use min/avg/max/sd only."}

os.makedirs(DATA, exist_ok=True)
cols = list(R[0].keys())
with open(os.path.join(DATA, "relationships.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R)
with open(os.path.join(DATA, "histograms.json"), "w") as f:
    json.dump({"source": "The Shared cM Project, Version 4.0 (March 2020), Blaine T. Bettinger, CC BY 4.0",
               "histograms": hist_out}, f, indent=1)

print(f"relationships: {len(R)}   histograms: {len(hist_out)}")
if problems:
    print("\nPROBLEMS:"); [print(" -", p) for p in problems]; sys.exit(1)
print("All checks passed.")
