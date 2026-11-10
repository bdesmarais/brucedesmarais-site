#!/usr/bin/env python3
"""Generate site data from the CV source (single source of truth).

Reads ../desmarais-lab.github.io/cv/desmarais_cv.tex and vitabib.bib and writes
_data/{talks,press,awards,grants,advisees}.yml plus one _publications/<key>.md per
publication, each with Google Scholar (Highwire) citation metadata.
Re-run after every CV edit:  python3 scripts/build_data.py
"""
import re, os, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT.parent / "desmarais-lab.github.io" / "cv"
tex = (CV / "desmarais_cv.tex").read_text(errors="replace")
bib = (CV / "vitabib.bib").read_text(errors="replace")

def delatex(s):
    s = re.sub(r"%.*", "", s)
    s = s.replace("``", "\u201c").replace("''", "\u201d").replace("--", "\u2013")
    s = re.sub(r"\{\\(?:em|it|bf)\s+([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:emph|textit|textbf|url)\{([^{}]*)\}", r"\1", s)
    for a, b in [(r"\&", "&"), (r"\$", "$"), (r"\%", "%"), ("~", " "), (r"\'e", "é"), (r"\"o", "ö"),
                 (r"\u{g}", "ğ"), (r"\.I", "İ"), (r"\c{c}", "ç"), (r"\'a", "á"), (r"\'i", "í"), (r"\'o", "ó")]:
        s = s.replace(a, b)
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip(" .")

# ---- bib parsing (brace-balanced) ----
entries = {}
for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", bib):
    typ, key, i = m.group(1).lower(), m.group(2), m.end()
    depth, j = 1, i
    while j < len(bib) and depth:
        depth += {"{": 1, "}": -1}.get(bib[j], 0); j += 1
    body = bib[i:j - 1]
    f = {}
    for fm in re.finditer(r"(\w+)\s*=\s*", body):
        k, p = fm.group(1).lower(), fm.end()
        if p < len(body) and body[p] == "{":
            d, q = 1, p + 1
            while q < len(body) and d:
                d += {"{": 1, "}": -1}.get(body[q], 0); q += 1
            v = body[p + 1:q - 1]
        elif p < len(body) and body[p] == '"':
            q = body.index('"', p + 1); v = body[p + 1:q]
        else:
            v = re.match(r"[^,\n]*", body[p:]).group(0)
        f.setdefault(k, v)
    entries[key] = (typ, f)

def section(name):
    m = re.search(r"\\section\{\\bf " + re.escape(name) + r"\}(.*?)(?=\\section\{|\\end\{document\})", tex, re.S)
    return m.group(1) if m else ""

def items(block):
    block = re.sub(r"(?m)^\s*%.*$", "", block)
    return [delatex(x) for x in re.split(r"\\item\s+", block)[1:]
            if delatex(re.sub(r"\\end\{etaremune\}.*", "", x, flags=re.S))]

def clean_item(x):
    return re.sub(r"\s*end\{etaremune\}.*$", "", x).strip(" .")

# ---- publications ----
pubsec = section("Publications")
kinds = [("Book", "book"), ("Journal Articles", "article"), ("Peer Refereed Proceedings", "proceedings"),
         ("Chapters in Edited Volumes", "chapter")]
order = []
for label, kind in kinds:
    m = re.search(r"\\emph\{" + re.escape(label) + r"\}(.*?)\\end\{etaremune\}", pubsec, re.S)
    if m:
        for k in re.findall(r"\\bibentry\{([^}]+)\}", m.group(1)):
            order.append((k, kind))
softsec = section("Software")
for k in re.findall(r"\\bibentry\{([^}]+)\}", softsec):
    order.append((k, "software"))

def authors(a):
    out = []
    for p in re.split(r"\s+and\s+", delatex(a)):
        p = p.strip()
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
            out.append(f"{first} {last}".strip())
        elif p:
            out.append(p)
    return out

def slug(k):
    return re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")

pubdir = ROOT / "_publications"
for old in pubdir.glob("*.md"):
    old.unlink()
n = 0
for rank, (k, kind) in enumerate(order):
    if k not in entries:
        continue
    typ, f = entries[k]
    year = delatex(f.get("year", ""))
    venue = delatex(f.get("journal") or f.get("booktitle") or f.get("publisher") or f.get("note") or "")
    url = f.get("url", "").strip()
    doi = f.get("doi", "").strip()
    if not url and doi:
        url = "https://doi.org/" + doi
    fm = {
        "title": delatex(f.get("title", k)),
        "authors": authors(f.get("author", "")),
        "venue": venue,
        "year": year,
        "kind": kind,
        "status": "Accepted" if year.lower() in ("accepted", "forthcoming", "in press") else "",
        "volume": delatex(f.get("volume", "")),
        "number": delatex(f.get("number", "")),
        "pages": delatex(f.get("pages", "")),
        "doi": doi,
        "link": url,
        "bibkey": k,
        "rank": rank,
    }
    fm = {a: b for a, b in fm.items() if b not in ("", [], None)}
    (pubdir / f"{slug(k)}.md").write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n")
    n += 1

# ---- other CV sections ----
def dump(name, data):
    (ROOT / "_data" / f"{name}.yml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000))

talks = []
for x in items(section("Presentations")):
    x = clean_item(x)
    m = re.match(r"\u201c(.*?)[.,]?\u201d\.?\s*(.*)", x)
    title, rest = (m.group(1), m.group(2)) if m else ("", x)
    ym = re.findall(r"(19|20)\d\d", rest)
    talks.append({"title": title.strip(" ."), "where": rest.strip(" ."),
                  "year": int(re.findall(r"(?:19|20)\d\d", rest)[-1]) if ym else None})
dump("talks", talks)
dump("press", [clean_item(x) for x in items(section("Press Coverage"))])
dump("awards", [clean_item(x) for x in items(section("Awards"))])
dump("grants", [clean_item(x) for x in items(section("Grants"))])

adv = section("Students Advised")
def sub(label):
    m = re.search(r"\\emph\{" + re.escape(label) + r"\}(.*?)\\end\{etaremune\}", adv, re.S)
    return [clean_item(x) for x in items(m.group(1))] if m else []
dump("advisees", {"phd": sub("Dissertation advisees"), "postdocs": sub("Postdoctoral Scholars Supervised"),
                  "honors": sub("Undergraduate honors thesis advisees")})
print(f"publications: {n} of {len(order)} keys; talks {len(talks)}")
