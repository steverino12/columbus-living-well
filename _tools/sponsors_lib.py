"""Shared loading and validation for sponsors.json."""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "sponsors.json")
TIERS = ("neighbor", "featured", "founding")
MAX_FOUNDING = 3
LOGO_EXT = (".png", ".jpg", ".jpeg", ".svg", ".webp")
FORBIDDEN_TEXT = ("ryerson",)  # owner's personal name must never appear on the site


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def active(data):
    return [s for s in data.get("sponsors", []) if s.get("status", "active") == "active"]


def validate(data):
    errors = []
    sponsors = data.get("sponsors")
    if not isinstance(sponsors, list):
        return ["sponsors.json: 'sponsors' must be a list"]
    names, subs = set(), set()
    for i, s in enumerate(sponsors):
        tag = f"sponsor #{i + 1} ({s.get('name', '?')})"
        for k in ("name", "url", "tier", "category", "start_date", "stripe_subscription_id"):
            if not str(s.get(k, "")).strip():
                errors.append(f"{tag}: missing '{k}'")
        if s.get("status", "active") not in ("active", "ended"):
            errors.append(f"{tag}: status must be 'active' or 'ended'")
        if s.get("tier") not in TIERS:
            errors.append(f"{tag}: tier must be one of {TIERS}")
        if not re.match(r"^https://[^\s/]+\.[^\s]+$", str(s.get("url", ""))):
            errors.append(f"{tag}: url must start with https://")
        try:
            datetime.date.fromisoformat(str(s.get("start_date", "")))
        except ValueError:
            errors.append(f"{tag}: start_date must be YYYY-MM-DD")
        sub = str(s.get("stripe_subscription_id", ""))
        if sub and not sub.startswith("sub_"):
            errors.append(f"{tag}: stripe_subscription_id must start with sub_")
        if s.get("status", "active") == "active":
            key = str(s.get("name", "")).strip().lower()
            if key in names:
                errors.append(f"{tag}: duplicate active sponsor name")
            names.add(key)
            if sub in subs:
                errors.append(f"{tag}: duplicate stripe_subscription_id")
            subs.add(sub)
        if s.get("category") and s["category"] != s["category"].strip().lower():
            errors.append(f"{tag}: category must be lowercase with no extra spaces")
        if len(str(s.get("blurb", ""))) > 240:
            errors.append(f"{tag}: blurb over 240 characters")
        for field in ("name", "blurb", "url"):
            if any(w in str(s.get(field, "")).lower() for w in FORBIDDEN_TEXT):
                errors.append(f"{tag}: '{field}' contains a forbidden personal name")
        logo = s.get("logo")
        if s.get("tier") in ("featured", "founding") and s.get("status", "active") == "active":
            if not logo:
                errors.append(f"{tag}: logo required for tier '{s.get('tier')}'")
            fp = s.get("featured_page")
            if not fp:
                errors.append(f"{tag}: featured_page required for tier '{s.get('tier')}'")
            elif not re.match(r"^[a-z0-9-]+\.html$", fp) or not os.path.isfile(os.path.join(ROOT, fp)) \
                    or fp in ("index.html", "sponsors.html", "404.html"):
                errors.append(f"{tag}: featured_page '{fp}' is not a content page in the site")
        if logo:
            if not logo.startswith("img/sponsors/") or not logo.lower().endswith(LOGO_EXT) or ".." in logo:
                errors.append(f"{tag}: logo must be img/sponsors/<file>{LOGO_EXT}")
            elif not os.path.isfile(os.path.join(ROOT, logo)):
                errors.append(f"{tag}: logo file {logo} not found")
    founding = [s for s in active(data) if s.get("tier") == "founding"]
    if len(founding) > MAX_FOUNDING:
        errors.append(f"{len(founding)} active Founding Partners; the cap is {MAX_FOUNDING}")
    seen = {}
    for s in founding:
        c = s.get("category")
        if c in seen:
            errors.append(f"Founding Partner category '{c}' is taken by both {seen[c]} and {s.get('name')}")
        seen[c] = s.get("name")
    return errors


def founding_categories(data):
    return {s.get("category"): s.get("name") for s in active(data) if s.get("tier") == "founding"}
