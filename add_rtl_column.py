#!/usr/bin/env python3
import csv, os

CAVEATS = ["motion-driven","parallax","hero-centric","storytelling","kinetic typography","3d","hyperrealism","retro-futurism","hud","sci-fi","fui","interactive product","vaporwave","spatial ui","predictive","drill-down","scroll"]
FULL = ["minimalism","swiss","flat design","accessible","inclusive","brutalism","neubrutalism","zero interface","e-ink","paper","dark mode","exaggerated minimalism","biophilic","nature distilled","editorial","ai-native","bento","soft ui evolution","data-dense","executive dashboard","heat map","financial","saas","portfolio","blog","documentation","enterprise","productivity","e-commerce","admin"]

def rtl(name):
    n = name.lower()
    for k in CAVEATS:
        if k in n: return "caveats"
    for k in FULL:
        if k in n: return "full"
    return "partial"

def process(path, col):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if "rtl_level" not in fields:
        fields.append("rtl_level")
    for row in rows:
        if not row.get("rtl_level"):
            row["rtl_level"] = rtl(row.get(col, ""))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Done: {os.path.basename(path)} ({len(rows)} rows)")

base = os.path.join("src","ui-ux-pro-max","data")
process(os.path.join(base,"styles.csv"), "Style Category")
process(os.path.join(base,"products.csv"), "Product Type")
print("All done!")
