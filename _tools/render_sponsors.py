#!/usr/bin/env python3
"""Render sponsors.json into the static pages (no JS needed, crawlable).

Regions are delimited by HTML comment markers:
  index.html     <!--sponsor-strip:start--> ... <!--sponsor-strip:end-->       (Founding Partners; empty = hidden)
  sponsors.html  <!--sponsor-spotlight:start--> ... <!--sponsor-spotlight:end--> (Founding Partners)
                 <!--sponsor-directory:start--> ... <!--sponsor-directory:end--> (all active tiers)
  featured_page  <!--sponsor-feature:start--> ... <!--sponsor-feature:end-->   (inserted before </main>)
"""
import glob, html, os, re, sys
import sponsors_lib as L

ORDER = {"founding": 0, "featured": 1, "neighbor": 2}
LABEL = {"founding": "Founding Partner", "featured": "Featured Sponsor", "neighbor": "Sponsor"}
e = lambda s: html.escape(str(s or ""), quote=True)


def link(s, inner):
    return f'<a href="{e(s["url"])}" rel="sponsored noopener" target="_blank">{inner}</a>'


def logo(s, cls="sponsor-logo"):
    return f'<img class="{cls}" src="{e(s["logo"])}" alt="{e(s["name"])} logo" loading="lazy">'


def strip(sp):
    f = [s for s in sp if s["tier"] == "founding"]
    if not f:
        return ""
    items = "".join(f'<li>{link(s, logo(s))}</li>' for s in f)
    return (f'<section class="sponsor-strip" aria-label="Founding Partners"><p class="kicker">Founding Partners</p>'
            f'<ul>{items}</ul><p class="small-note"><a href="sponsors.html">Sponsored placements</a></p></section>')


def spotlight(sp):
    f = [s for s in sp if s["tier"] == "founding"]
    if not f:
        return ""
    cards = "".join(
        f'<div class="card spotlight"><p class="kicker">Founding Partner &middot; {e(s["category"]).title()}</p>'
        f'{link(s, logo(s))}<h3>{link(s, e(s["name"]))}</h3>'
        + (f'<p>{e(s["blurb"])}</p>' if s.get("blurb") else "") + '</div>' for s in f)
    return f'<h2 id="founding-partners">Founding Partner spotlight</h2><div class="grid">{cards}</div>'


def directory(sp):
    head = '<h2 id="sponsor-directory">Sponsor directory</h2>'
    if not sp:
        return head + ('<p class="note" id="sponsor-directory-empty">Sponsor listings will appear here. '
                       'Every listing is a paid placement and is labeled as one.</p>')
    cats = {}
    for s in sorted(sp, key=lambda s: (ORDER[s["tier"]], s["name"].lower())):
        cats.setdefault(s["category"], []).append(s)
    out = [head, '<p class="small-note">Paid placements. Listing is not an endorsement.</p><div class="sponsor-dir">']
    for c in sorted(cats):
        out.append(f'<h3>{e(c).title()}</h3><ul class="sponsor-list">')
        for s in cats[c]:
            lg = logo(s, "sponsor-logo sm") + " " if s["tier"] in ("featured", "founding") and s.get("logo") else ""
            out.append(f'<li>{link(s, lg + e(s["name"]))} <span class="tier-tag">{LABEL[s["tier"]]}</span></li>')
        out.append('</ul>')
    out.append('</div>')
    return "".join(out)


def feature(s):
    return (f'<aside class="sponsor-feature card" aria-label="Sponsored"><p class="kicker">Sponsored &middot; '
            f'{LABEL[s["tier"]]}</p>{link(s, logo(s))}<h3>{link(s, e(s["name"]))}</h3>'
            + (f'<p>{e(s["blurb"])}</p>' if s.get("blurb") else "") +
            '<p class="small-note"><a href="sponsors.html">About sponsorships</a></p></aside>')


def put(text, name, body, path):
    pat = re.compile(rf"<!--{name}:start-->.*?<!--{name}:end-->", re.S)
    if not pat.search(text):
        sys.exit(f"render: marker {name} missing in {path}")
    return pat.sub(lambda m: f"<!--{name}:start-->{body}<!--{name}:end-->", text)


def rw(path, fn):
    p = os.path.join(L.ROOT, path)
    with open(p, encoding="utf-8") as f:
        old = f.read()
    new = fn(old)
    if new != old:
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        print("updated", path)


def main():
    data = L.load()
    errs = L.validate(data)
    if errs:
        print("Refusing to render; sponsors.json invalid:\n  - " + "\n  - ".join(errs))
        return 1
    sp = sorted(L.active(data), key=lambda s: (ORDER[s["tier"]], s["start_date"], s["name"].lower()))
    rw("index.html", lambda t: put(t, "sponsor-strip", strip(sp), "index.html"))
    rw("sponsors.html", lambda t: put(put(t, "sponsor-spotlight", spotlight(sp), "sponsors.html"),
                                      "sponsor-directory", directory(sp), "sponsors.html"))
    feats = {}
    for s in sp:
        if s["tier"] in ("featured", "founding"):
            feats.setdefault(s["featured_page"], []).append(s)
    feat_pat = re.compile(r"<!--sponsor-feature:start-->.*?<!--sponsor-feature:end-->", re.S)
    for p in sorted(glob.glob(os.path.join(L.ROOT, "*.html"))):
        rel = os.path.basename(p)
        if rel in ("index.html", "sponsors.html", "404.html"):
            continue
        def fix(t, rel=rel):
            t = feat_pat.sub("", t)
            if rel in feats:
                block = "".join(feature(s) for s in feats[rel])
                t = t.replace("</main>", f"<!--sponsor-feature:start-->{block}<!--sponsor-feature:end--></main>", 1)
            return t
        rw(rel, fix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
