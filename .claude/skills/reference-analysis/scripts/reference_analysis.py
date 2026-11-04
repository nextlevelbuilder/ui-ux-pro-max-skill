#!/usr/bin/env python3
"""reference_analysis.py - validate, merge, colour-extract, summarise and convert
`reference-analysis.json` documents (schema `vdp-reference-analysis/1`).

Subcommands
  validate        check one analysis file against the rules in references/extraction-schema.md
  merge           combine several per-image analyses into one document (roles, conflicts)
  extract-colors  pixel-share palette of an image (Pillow optional; BLOCKED without it)
  to-profile      emit a partial Visual Direction Profile (vdp/1, "_partial": true)
  summary         <= 12-line human summary of an analysis
  template        print the empty skeleton

Exit codes: 0 ok, 1 validation failed / merge rejected / malformed JSON,
2 usage or missing input file, 3 BLOCKED (Pillow missing, unreadable image).

Standard library only. Pillow is imported lazily inside `extract_colors` and its
absence is reported as a BLOCKED result, never as a traceback. Python 3.8+.
"""

import argparse
import copy
import json
import math
import os
import re
import sys

SCHEMA = "vdp-reference-analysis/1"
PROFILE_SCHEMA = "vdp/1"
DEFAULT_STYLE_ID = "reference-derived-custom"

ROLES = ["color", "shapes", "characters", "buttons", "hud", "popup", "icons",
         "typography", "layout", "motion"]
VIEWED_BY = ["model-vision", "human-description", "none"]
SCREEN_TYPES = ["home", "gameplay", "popup", "shop", "other"]
OWNERS = ["user", "third-party", "unknown"]
LICENSES = ["own-work", "licensed", "fair-use-reference", "unknown"]
CATEGORIES = ["layout", "color", "shape", "shading", "typography", "component",
              "character", "motion", "accessibility", "iconography"]
CONFIDENCE = ["observed", "high", "assumption", "not-derivable"]
CONF_RANK = {"observed": 3, "high": 2, "assumption": 1, "not-derivable": 0}
RULE_CONFIDENCE = ["observed", "high", "assumption"]
CONFLICT_STATUS = ["resolved", "open"]
ROLE_GUESS = ["background", "surface", "primary", "secondary", "accent", "text",
              "outline", "shadow", "highlight", "unknown"]
TARGET_VOCAB = ["palette", "radius", "outline", "shading", "shadow", "typography",
                "icon", "hud", "popup", "card", "character", "layout", "motion",
                "button.primary", "button.secondary", "button.icon", "chip", "tab-bar",
                "dialog", "toast", "progress", "reward"]
STANDARD_NOT_DERIVABLE = ["animation timing and easing", "pressed and disabled states",
                          "font family names", "exact pixel values at device scale"]
REQUIRED_KEYS = ["schema", "references", "observations", "rules", "conflicts",
                 "not_derivable", "palette_observed"]
KNOWN_TOP_KEYS = REQUIRED_KEYS + ["project"]
SEQUENCE_EXT = (".gif", ".mp4", ".webm", ".mov")
SEQUENCE_WORDS = ("frames", "sequence", "video")

ID_PATTERNS = {"ref": re.compile(r"^ref-[0-9]+$"),
               "obs": re.compile(r"^obs-[0-9]+$"),
               "rule": re.compile(r"^rule-[0-9]+$")}
HEX_RE = re.compile(r"^#[0-9A-F]{6}$")
HEX_CI_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SCOPE_RE = re.compile(r"^(global|context:(home|gameplay|popup|shop|other))$")
WINS_RE = re.compile(r"\b(ref-[0-9]+) wins\b")
ARTICLES = {"a", "an", "the"}

# Topic -> role map (references/multi-reference-reconciliation.md section 1.2).
# Component rows are checked first, then the generic rows, in this order.
TOPIC_ROLE_ROWS = [
    ("characters", ["character", "mascot", "illustration", "avatar"]),
    ("buttons", ["button", "cta", "chip"]),
    ("hud", ["hud", "counter", "progress", "timer", "lives", "score", "top bar"]),
    ("popup", ["popup", "dialog", "modal", "sheet", "toast", "overlay"]),
    ("icons", ["icon", "glyph"]),
    ("color", ["palette", "color", "colour", "hue", "saturation", "contrast"]),
    ("shapes", ["radius", "outline", "silhouette", "corner", "shape", "shading",
                "shadow", "highlight", "elevation"]),
    ("typography", ["typography", "font", "label case", "weight", "text style"]),
    ("layout", ["layout", "grid", "spacing", "density", "hierarchy", "safe area",
                "tab-bar", "navigation"]),
    ("motion", ["motion", "animation", "easing", "transition", "timing"]),
]


class MergeError(Exception):
    """Raised by `merge_analyses` when inputs cannot be combined."""


class Blocked(Exception):
    """Raised internally by image helpers when the capability is unavailable."""

    def __init__(self, reason, message):
        Exception.__init__(self, message)
        self.reason = reason
        self.message = message


# --------------------------------------------------------------------------- helpers

def topic_to_role(text):
    """Map a rule target or conflict topic to a role (None when unowned topic)."""
    low = (text or "").lower()
    for role, needles in TOPIC_ROLE_ROWS:
        for needle in needles:
            if needle in low:
                return role
    return None


def role_owners(doc):
    """Return {role: [ref ids that list it]} for a document."""
    owners = {}
    for ref in doc.get("references", []) or []:
        if not isinstance(ref, dict):
            continue
        for role in ref.get("roles", []) or []:
            owners.setdefault(role, []).append(ref.get("id"))
    return owners


def single_owner(doc, role):
    owners = role_owners(doc).get(role, [])
    return owners[0] if len(owners) == 1 else None


def is_sequence_ref(ref):
    path = str(ref.get("path", "")).lower()
    label = str(ref.get("label", "")).lower()
    if path.endswith(SEQUENCE_EXT):
        return True
    return any(w in label for w in SEQUENCE_WORDS)


def safe_slug(name):
    slug = re.sub(r"[^a-z0-9_-]+", "-", str(name or "").lower()).strip("-")
    return slug or "default"


def norm_text(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def topic_key(statement):
    """Normalised topic phrase of an observation: text before an early colon, else the
    first four words; articles stripped, lower-case."""
    s = str(statement or "").strip()
    head = s
    if ":" in s:
        before = s.split(":", 1)[0]
        if len(before.split()) <= 6:
            head = before
    words = [w for w in re.findall(r"[a-z0-9'-]+", head.lower()) if w not in ARTICLES]
    return " ".join(words[:4])


def hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def min_confidence(values):
    values = [v for v in values if v in CONF_RANK]
    if not values:
        return None
    return min(values, key=lambda v: CONF_RANK[v])


def load_json_file(path):
    """Return (doc, None) or (None, (exit_code, message))."""
    if not os.path.isfile(path):
        return None, (2, "file not found: %s" % path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except json.JSONDecodeError as exc:
        return None, (1, "invalid JSON in %s: %s (line %d column %d)"
                      % (path, exc.msg, exc.lineno, exc.colno))
    except OSError as exc:
        return None, (2, "cannot read %s: %s" % (path, exc))


# --------------------------------------------------------------------------- validate

class _Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, code, path, message):
        self.errors.append({"code": code, "path": path, "message": message})

    def warn(self, code, path, message):
        self.warnings.append({"code": code, "path": path, "message": message})


def _check_ids(rep, items, kind, section):
    seen = {}
    ids = []
    pattern = ID_PATTERNS[kind]
    for i, item in enumerate(items):
        path = "%s[%d]" % (section, i)
        if not isinstance(item, dict):
            rep.error("R-TYPE", path, "entry must be an object")
            ids.append(None)
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not pattern.match(ident):
            rep.error("R-ID", path + ".id",
                      "id %r must match %s" % (ident, pattern.pattern))
        elif ident in seen:
            rep.error("R-ID-DUP", path + ".id",
                      "duplicate id %s (also at %s[%d])" % (ident, section, seen[ident]))
        else:
            seen[ident] = i
        ids.append(ident if isinstance(ident, str) else None)
    return ids


def _nonempty_str(rep, obj, key, path):
    val = obj.get(key)
    if not isinstance(val, str) or not val.strip():
        rep.error("R-FIELD", "%s.%s" % (path, key), "%s must be a non-empty string" % key)
        return False
    return True


def _enum(rep, obj, key, path, allowed, code, label=None):
    val = obj.get(key)
    if val not in allowed:
        rep.error(code, "%s.%s" % (path, key),
                  "%s %r is not one of %s" % (label or key, val, ", ".join(allowed)))
        return False
    return True


def validate(doc, strict=False):
    """Full validation. Returns {"status", "errors", "warnings", "counts"}."""
    rep = _Report()
    if not isinstance(doc, dict):
        rep.error("R-TYPE", "$", "document must be a JSON object")
        return {"status": "FAIL", "errors": rep.errors, "warnings": rep.warnings, "counts": {}}

    # 1. schema
    if doc.get("schema") != SCHEMA:
        rep.error("R-SCHEMA", "schema", "schema must be %r (got %r)" % (SCHEMA, doc.get("schema")))
    # 2. required keys / types
    for key in REQUIRED_KEYS:
        if key not in doc:
            rep.error("R-KEYS", key, "required key %r is missing" % key)
        elif key != "schema" and not isinstance(doc[key], list):
            rep.error("R-TYPE", key, "%s must be an array" % key)
    for key in doc:
        if key not in KNOWN_TOP_KEYS and not str(key).startswith("_"):
            rep.warn("W-KEY", key, "unknown top-level key %r ignored" % key)
    if "project" in doc and not isinstance(doc["project"], str):
        rep.error("R-TYPE", "project", "project must be a string")

    references = doc.get("references") if isinstance(doc.get("references"), list) else []
    observations = doc.get("observations") if isinstance(doc.get("observations"), list) else []
    rules = doc.get("rules") if isinstance(doc.get("rules"), list) else []
    conflicts = doc.get("conflicts") if isinstance(doc.get("conflicts"), list) else []
    not_derivable = doc.get("not_derivable") if isinstance(doc.get("not_derivable"), list) else []
    palette = doc.get("palette_observed") if isinstance(doc.get("palette_observed"), list) else []

    # 3. ids
    ref_ids = _check_ids(rep, references, "ref", "references")
    obs_ids = _check_ids(rep, observations, "obs", "observations")
    rule_ids = _check_ids(rep, rules, "rule", "rules")
    ref_set = set(i for i in ref_ids if i)
    obs_set = set(i for i in obs_ids if i)
    ref_by_id = {}
    for ref in references:
        if isinstance(ref, dict) and isinstance(ref.get("id"), str):
            ref_by_id[ref["id"]] = ref
    obs_by_id = {}
    for obs in observations:
        if isinstance(obs, dict) and isinstance(obs.get("id"), str):
            obs_by_id[obs["id"]] = obs

    if not references:
        rep.error("R-REFS", "references", "references must have at least one entry")

    # 4. references
    for i, ref in enumerate(references):
        if not isinstance(ref, dict):
            continue
        path = "references[%d]" % i
        _nonempty_str(rep, ref, "path", path)
        _nonempty_str(rep, ref, "label", path)
        roles = ref.get("roles")
        if not isinstance(roles, list):
            rep.error("R-ROLE-ENUM", path + ".roles", "roles must be an array of %s" % ", ".join(ROLES))
        else:
            bad = [r for r in roles if r not in ROLES]
            if bad:
                rep.error("R-ROLE-ENUM", path + ".roles",
                          "unknown role(s) %s; allowed roles: %s" % (", ".join(map(repr, bad)), ", ".join(ROLES)))
            if len(set(roles)) != len(roles):
                rep.error("R-ROLE-DUP", path + ".roles", "duplicate role within one reference")
        _enum(rep, ref, "viewed_by", path, VIEWED_BY, "R-VIEW-ENUM")
        _enum(rep, ref, "screen_type", path, SCREEN_TYPES, "R-SCREEN-ENUM")
        prov = ref.get("provenance")
        if not isinstance(prov, dict):
            rep.error("R-PROV", path + ".provenance", "provenance must be an object with owner and license")
        else:
            _enum(rep, prov, "owner", path + ".provenance", OWNERS, "R-PROV-OWNER")
            _enum(rep, prov, "license", path + ".provenance", LICENSES, "R-PROV-LICENSE")

    # 5. observations
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict):
            continue
        path = "observations[%d]" % i
        oid = obs.get("id") if isinstance(obs.get("id"), str) else path
        _enum(rep, obs, "category", path, CATEGORIES, "R-OBS-CAT")
        _nonempty_str(rep, obs, "statement", path)
        refs = obs.get("refs")
        if not isinstance(refs, list) or not refs:
            rep.error("R-OBS-REF", path + ".refs", "%s must list at least one reference id" % oid)
        else:
            for r in refs:
                if r not in ref_set:
                    rep.error("R-OBS-REF", path + ".refs", "%s refers to unknown reference %s" % (oid, r))
        conf = obs.get("confidence")
        if conf not in CONFIDENCE:
            rep.error("R-CONF-ENUM", path + ".confidence",
                      "%s has confidence %r; expected one of %s" % (oid, conf, ", ".join(CONFIDENCE)))
        if _nonempty_str(rep, obs, "evidence", path) and conf == "not-derivable":
            if not str(obs["evidence"]).strip().lower().startswith("n/a"):
                rep.error("R-OBS-EVIDENCE", path + ".evidence",
                          "%s is not-derivable; evidence must start with 'n/a' and give the reason" % oid)

    # 6. rules
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        path = "rules[%d]" % i
        rid = rule.get("id") if isinstance(rule.get("id"), str) else path
        if _nonempty_str(rep, rule, "target", path):
            if rule["target"] not in TARGET_VOCAB:
                rep.warn("W-TARGET", path + ".target",
                         "%s target %r is outside the recommended vocabulary (%s)"
                         % (rid, rule["target"], ", ".join(TARGET_VOCAB)))
        _nonempty_str(rep, rule, "statement", path)
        derived = rule.get("derived_from")
        if not isinstance(derived, list) or not derived:
            rep.error("R-RULE-REF", path + ".derived_from", "%s must derive from at least one observation" % rid)
        else:
            for o in derived:
                if o not in obs_set:
                    rep.error("R-RULE-REF", path + ".derived_from", "%s refers to unknown observation %s" % (rid, o))
        conf = rule.get("confidence")
        if conf == "not-derivable":
            rep.error("R-RULE-ND", path + ".confidence",
                      "%s: a rule may never be not-derivable; drop the rule and list the topic in not_derivable" % rid)
        elif conf not in RULE_CONFIDENCE:
            rep.error("R-CONF-ENUM", path + ".confidence",
                      "%s has confidence %r; expected one of %s" % (rid, conf, ", ".join(RULE_CONFIDENCE)))
        scope = rule.get("scope")
        if not isinstance(scope, str) or not SCOPE_RE.match(scope):
            rep.error("R-SCOPE", path + ".scope",
                      "%s scope %r must be 'global' or 'context:<%s>'" % (rid, scope, "|".join(SCREEN_TYPES)))

    # 7. conflicts
    topics_seen = {}
    for i, c in enumerate(conflicts):
        if not isinstance(c, dict):
            rep.error("R-TYPE", "conflicts[%d]" % i, "entry must be an object")
            continue
        path = "conflicts[%d]" % i
        if _nonempty_str(rep, c, "topic", path):
            key = c["topic"].strip().lower()
            if key in topics_seen:
                rep.error("R-CONF-TOPIC", path + ".topic", "duplicate conflict topic %r" % c["topic"])
            topics_seen[key] = i
        between = c.get("between")
        if not isinstance(between, list) or len(between) < 2:
            rep.error("R-CONF-BETWEEN", path + ".between", "between must list at least two reference ids")
        else:
            if len(set(between)) != len(between):
                rep.error("R-CONF-BETWEEN", path + ".between", "between contains duplicate reference ids")
            for r in between:
                if r not in ref_set:
                    rep.error("R-CONF-BETWEEN", path + ".between", "conflict refers to unknown reference %s" % r)
        _nonempty_str(rep, c, "resolution", path)
        _enum(rep, c, "status", path, CONFLICT_STATUS, "R-CONF-STATUS")

    # 8. not_derivable
    seen_nd = set()
    for i, entry in enumerate(not_derivable):
        if not isinstance(entry, str) or not entry.strip():
            rep.error("R-ND", "not_derivable[%d]" % i, "entries must be non-empty strings")
            continue
        key = entry.strip().lower()
        if key in seen_nd:
            rep.error("R-ND-DUP", "not_derivable[%d]" % i, "duplicate entry %r" % entry)
        seen_nd.add(key)

    # 9. palette_observed
    for i, p in enumerate(palette):
        if not isinstance(p, dict):
            rep.error("R-TYPE", "palette_observed[%d]" % i, "entry must be an object")
            continue
        path = "palette_observed[%d]" % i
        hx = p.get("hex")
        if not isinstance(hx, str) or not HEX_RE.match(hx):
            if isinstance(hx, str) and HEX_CI_RE.match(hx):
                rep.warn("W-HEX-CASE", path + ".hex", "hex %s should be upper-case (%s)" % (hx, hx.upper()))
            else:
                rep.error("R-PAL-HEX", path + ".hex", "hex %r must match #RRGGBB upper-case" % (hx,))
        share = p.get("share")
        if isinstance(share, bool) or not isinstance(share, (int, float)) or not (0 < share <= 1):
            rep.error("R-PAL-SHARE", path + ".share", "share %r must be a number in (0, 1]" % (share,))
        elif round(share, 4) != share:
            rep.error("R-PAL-SHARE", path + ".share", "share %r has more than 4 decimals" % (share,))
        _enum(rep, p, "role_guess", path, ROLE_GUESS, "R-PAL-ROLE")
        if p.get("ref") not in ref_set:
            rep.error("R-PAL-REF", path + ".ref", "palette entry refers to unknown reference %r" % (p.get("ref"),))

    # 10. R-ROLE-1 ownership
    for role, owners in sorted(role_owners(doc).items()):
        owners = [o for o in owners if o]
        if len(owners) > 1:
            rep.error("R-ROLE-1", "references", "role '%s' owned by %s" % (role, " and ".join(owners)))

    # 11. viewed_by constraints
    for i, ref in enumerate(references):
        if isinstance(ref, dict) and ref.get("viewed_by") == "none" and ref.get("roles"):
            rep.warn("R-VIEW-1", "references[%d].roles" % i,
                     "role reserved on an unviewed reference %s; no rules may derive from it" % ref.get("id"))
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict) or not isinstance(obs.get("refs"), list):
            continue
        refs = [ref_by_id.get(r) for r in obs["refs"] if ref_by_id.get(r)]
        if not refs:
            continue
        oid = obs.get("id")
        viewed = [r.get("viewed_by") for r in refs]
        if "none" in viewed and obs.get("confidence") != "not-derivable":
            rep.error("R-VIEW-2", "observations[%d].confidence" % i,
                      "%s cites a reference with viewed_by 'none'; confidence must be not-derivable" % oid)
        if viewed and all(v == "human-description" for v in viewed) and obs.get("confidence") == "observed":
            rep.error("R-VIEW-3", "observations[%d].confidence" % i,
                      "%s derives only from human descriptions; cap confidence at 'high'" % oid)

    # 12. R-OBS-1 / R-OBS-2
    sequence_ids = set(r["id"] for r in ref_by_id.values() if is_sequence_ref(r))
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict):
            continue
        refs = obs.get("refs") if isinstance(obs.get("refs"), list) else []
        if obs.get("category") == "motion":
            has_seq = any(r in sequence_ids for r in refs)
            if not has_seq and obs.get("confidence") != "not-derivable":
                rep.error("R-OBS-1", "observations[%d].confidence" % i,
                          "%s is a motion observation without a sequence input; must be not-derivable" % obs.get("id"))
            elif has_seq and obs.get("confidence") == "not-derivable":
                rep.warn("R-OBS-1", "observations[%d].confidence" % i,
                         "%s cites a sequence input but is still not-derivable" % obs.get("id"))
        if len(set(refs)) >= 2 and re.search(r"\b(differs?|versus|vs\.?|contradict|whereas|rather than)\b",
                                             str(obs.get("statement", "")).lower()):
            tkey = topic_key(obs.get("statement"))
            covered = any(isinstance(c, dict) and norm_text(c.get("topic")) and
                          (norm_text(c.get("topic")) in norm_text(obs.get("statement")))
                          for c in conflicts)
            has_ctx = any(isinstance(r, dict) and str(r.get("scope", "")).startswith("context:")
                          and obs.get("id") in (r.get("derived_from") or []) for r in rules)
            if not covered and not has_ctx:
                rep.warn("R-OBS-2", "observations[%d]" % i,
                         "%s records a difference across references (%r) without a matching conflict or context rule"
                         % (obs.get("id"), tkey))

    # 13. rule confidence and ownership
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        rid = rule.get("id")
        derived = [obs_by_id.get(o) for o in (rule.get("derived_from") or []) if obs_by_id.get(o)]
        confs = [o.get("confidence") for o in derived]
        floor = min_confidence(confs)
        if floor is not None and rule.get("confidence") in CONF_RANK:
            if floor == "not-derivable":
                rep.error("R-RULE-1", "rules[%d].confidence" % i,
                          "%s derives from a not-derivable observation; the rule cannot exist" % rid)
            elif CONF_RANK[rule["confidence"]] > CONF_RANK[floor]:
                rep.error("R-RULE-1", "rules[%d].confidence" % i,
                          "%s confidence %r exceeds the minimum of its observations (%r)"
                          % (rid, rule["confidence"], floor))
        role = topic_to_role(rule.get("target"))
        if role and derived:
            cited = set()
            for o in derived:
                cited.update(o.get("refs") or [])
            if len(cited) == 1:
                only = next(iter(cited))
                owner = single_owner(doc, role)
                if owner is not None and owner != only:
                    rep.error("R-RULE-2", "rules[%d]" % i,
                              "%s (target %r -> role '%s') derives only from %s but the role is owned by %s"
                              % (rid, rule.get("target"), role, only, owner))
        if rule.get("scope") == "global" and rule.get("confidence") == "assumption":
            rep.warn("R-RULE-3", "rules[%d]" % i,
                     "%s is a global assumption; it cannot enter MASTER and will be routed to unknowns" % rid)

    # 14. conflicts cross-field
    for i, c in enumerate(conflicts):
        if not isinstance(c, dict):
            continue
        between = c.get("between") if isinstance(c.get("between"), list) else []
        if c.get("status") == "resolved":
            m = WINS_RE.search(str(c.get("resolution", "")))
            if not m or m.group(1) not in between:
                rep.error("R-CONF-1", "conflicts[%d].resolution" % i,
                          "resolved conflict %r must say '<ref-N> wins' with ref-N in between" % c.get("topic"))
        elif c.get("status") == "open":
            role = topic_to_role(c.get("topic"))
            owner = single_owner(doc, role) if role else None
            if owner is not None:
                rep.error("R-CONF-2", "conflicts[%d]" % i,
                          "open conflict %r maps to role '%s' owned by %s; resolve it by ownership"
                          % (c.get("topic"), role, owner))
            if strict:
                rep.error("R-CONF-OPEN", "conflicts[%d]" % i,
                          "open conflict %r (strict mode): %s" % (c.get("topic"), c.get("resolution")))

    # 15. palette cross-field
    by_ref = {}
    for i, p in enumerate(palette):
        if isinstance(p, dict):
            by_ref.setdefault(p.get("ref"), []).append((i, p))
    for ref_id, entries in by_ref.items():
        total = sum(p.get("share", 0) for _, p in entries
                    if isinstance(p.get("share"), (int, float)) and not isinstance(p.get("share"), bool))
        if total > 1.01:
            rep.error("R-PAL-1", "palette_observed", "shares for %s sum to %.4f (> 1.01)" % (ref_id, total))
        for role in ("background", "text"):
            n = sum(1 for _, p in entries if p.get("role_guess") == role)
            if n > 1:
                rep.warn("R-PAL-2", "palette_observed", "%s has %d entries guessed as %s" % (ref_id, n, role))
        valid = [(i, p) for i, p in entries if isinstance(p.get("hex"), str) and HEX_CI_RE.match(p["hex"])]
        for a in range(len(valid)):
            for b in range(a + 1, len(valid)):
                d = rgb_distance(hex_to_rgb(valid[a][1]["hex"]), hex_to_rgb(valid[b][1]["hex"]))
                if d < 24:
                    rep.warn("R-PAL-3", "palette_observed[%d]" % valid[b][0],
                             "%s and %s are near-duplicates (distance %.1f)" % (valid[a][1]["hex"], valid[b][1]["hex"], d))

    # 16. advisory checks
    viewed_any = any(isinstance(r, dict) and r.get("viewed_by") in ("model-vision", "human-description")
                     for r in references)
    if viewed_any and not observations:
        rep.warn("W-OBS-EMPTY", "observations", "no observations yet although a reference was viewed or described")
    if references and not sequence_ids:
        missing = [s for s in STANDARD_NOT_DERIVABLE if s not in seen_nd]
        if missing and observations:
            rep.warn("W-ND-STD", "not_derivable", "static inputs: consider listing %s" % ", ".join(map(repr, missing)))

    counts = {
        "references": len(references),
        "observations": len(observations),
        "rules": len(rules),
        "conflicts": len(conflicts),
        "conflicts_open": sum(1 for c in conflicts if isinstance(c, dict) and c.get("status") == "open"),
        "not_derivable": len(not_derivable),
        "palette_observed": len(palette),
        "observations_by_confidence": {c: sum(1 for o in observations if isinstance(o, dict) and o.get("confidence") == c)
                                       for c in CONFIDENCE},
        "rules_by_confidence": {c: sum(1 for r in rules if isinstance(r, dict) and r.get("confidence") == c)
                                for c in RULE_CONFIDENCE},
    }
    return {"status": "OK" if not rep.errors else "FAIL", "errors": rep.errors,
            "warnings": rep.warnings, "counts": counts}


def validate_analysis(doc, strict=False):
    """Errors only (list of {code, path, message}); [] means valid."""
    return validate(doc, strict=strict)["errors"]


# --------------------------------------------------------------------------- merge

def _next_id(prefix, existing):
    n = 0
    for ident in existing:
        m = re.match(r"^%s-([0-9]+)$" % prefix, str(ident))
        if m:
            n = max(n, int(m.group(1)))
    return "%s-%d" % (prefix, n + 1)


def parse_role_specs(specs):
    """`ref-1:color,shapes` -> {"ref-1": ["color", "shapes"]}. Raises ValueError."""
    out = {}
    for spec in specs or []:
        if ":" not in spec:
            raise ValueError("role spec %r must look like ref-1:color,shapes" % spec)
        ref_id, roles = spec.split(":", 1)
        ref_id = ref_id.strip()
        if not ID_PATTERNS["ref"].match(ref_id):
            raise ValueError("role spec %r: %r is not a ref-N id" % (spec, ref_id))
        role_list = [r.strip() for r in roles.split(",") if r.strip()]
        bad = [r for r in role_list if r not in ROLES]
        if bad:
            raise ValueError("role spec %r: unknown role(s) %s; allowed: %s" % (spec, ", ".join(bad), ", ".join(ROLES)))
        out.setdefault(ref_id, [])
        for r in role_list:
            if r not in out[ref_id]:
                out[ref_id].append(r)
    return out


def detect_conflicts(doc):
    """Pairwise conflict detection over observations (reconciliation doc section 2).
    Mutates `doc`: appends conflicts, cross-ref observations, winning rules.
    Returns a list of warning strings."""
    warnings = []
    refs = {r["id"]: r for r in doc["references"]}
    existing_topics = set(norm_text(c.get("topic")) for c in doc["conflicts"])
    obs = [o for o in doc["observations"] if o.get("confidence") != "not-derivable"]
    handled = set()
    new_conflicts = []
    for a_i in range(len(obs)):
        for b_i in range(a_i + 1, len(obs)):
            a, b = obs[a_i], obs[b_i]
            if a.get("category") != b.get("category"):
                continue
            if set(a.get("refs", [])) & set(b.get("refs", [])):
                continue
            key = topic_key(a.get("statement"))
            if not key or key != topic_key(b.get("statement")):
                continue
            if norm_text(a.get("statement")) == norm_text(b.get("statement")):
                continue
            if key in existing_topics or key in handled:
                continue
            handled.add(key)
            between = []
            for r in list(a.get("refs", [])) + list(b.get("refs", [])):
                if r not in between:
                    between.append(r)
            role = topic_to_role(key) or topic_to_role(a.get("category"))
            owner = single_owner(doc, role) if role else None
            if owner is not None and refs.get(owner, {}).get("viewed_by") == "none":
                owner = None
            ref_a = ", ".join(a.get("refs", []))
            ref_b = ", ".join(b.get("refs", []))
            if owner is None:
                conflict = {"topic": key, "between": between, "status": "open",
                            "resolution": "No reference owns role %s. %s (%s) vs %s (%s); user must assign the role "
                                          "or declare the difference intentional."
                                          % (role or "(unmapped)", a["statement"], ref_a, b["statement"], ref_b)}
                new_conflicts.append((conflict, a, b, None))
            else:
                winner, loser = (a, b) if owner in a.get("refs", []) else (b, a)
                loser_ref = refs.get(loser.get("refs", [None])[0], {})
                conflict = {"topic": key, "between": between, "status": "resolved",
                            "resolution": "%s wins (role %s): %s globally. %s from %s recorded; ask user whether %s "
                                          "should intentionally differ."
                                          % (owner, role, winner["statement"], loser["statement"],
                                             ", ".join(loser.get("refs", [])), loser_ref.get("screen_type", "that screen"))}
                new_conflicts.append((conflict, a, b, winner))
    for conflict, a, b, winner in new_conflicts:
        doc["conflicts"].append(conflict)
        cross_id = _next_id("obs", [o.get("id") for o in doc["observations"]])
        cross_conf = min_confidence([a.get("confidence"), b.get("confidence")]) or "assumption"
        doc["observations"].append({
            "id": cross_id, "category": a.get("category"),
            "statement": "%s differs: %s (%s) vs %s (%s)" % (conflict["topic"], a["statement"],
                                                             ", ".join(a.get("refs", [])), b["statement"],
                                                             ", ".join(b.get("refs", []))),
            "refs": conflict["between"], "evidence": "merge: conflict detection over %s and %s" % (a["id"], b["id"]),
            "confidence": cross_conf})
        if winner is not None:
            rule_id = _next_id("rule", [r.get("id") for r in doc["rules"]])
            doc["rules"].append({"id": rule_id, "target": conflict["topic"], "statement": winner["statement"],
                                 "derived_from": [winner["id"]], "confidence": winner.get("confidence", "high"),
                                 "scope": "global"})
            warnings.append("conflict %r resolved by role ownership; added %s from %s" % (conflict["topic"], rule_id, winner["id"]))
        else:
            dropped = []
            for rule in list(doc["rules"]):
                if a["id"] in rule.get("derived_from", []) or b["id"] in rule.get("derived_from", []):
                    doc["rules"].remove(rule)
                    dropped.append(rule.get("id"))
            msg = "open conflict %r (no owner for role %s)" % (conflict["topic"], topic_to_role(conflict["topic"]) or "(unmapped)")
            if dropped:
                msg += "; dropped rule(s) %s" % ", ".join(dropped)
            warnings.append(msg)
    return warnings


def drop_non_owner_rules(doc):
    """R-RULE-2 at merge time: a rule on an owned topic that derives only from a
    non-owner reference is dropped (with a warning), never kept silently."""
    warnings = []
    obs_by_id = {o.get("id"): o for o in doc["observations"]}
    for rule in list(doc["rules"]):
        role = topic_to_role(rule.get("target"))
        if not role:
            continue
        cited = set()
        for o in rule.get("derived_from", []):
            cited.update(obs_by_id.get(o, {}).get("refs", []))
        owner = single_owner(doc, role)
        if owner is not None and len(cited) == 1 and owner not in cited:
            doc["rules"].remove(rule)
            warnings.append("dropped %s: target %r maps to role '%s' owned by %s, but it derives only from %s"
                            % (rule.get("id"), rule.get("target"), role, owner, next(iter(cited))))
    return warnings


def rederive_rule_confidence(doc):
    """R-RULE-1: downgrade rule confidence to the minimum of its observations; drop rules
    whose observations are not-derivable. Returns warning strings."""
    warnings = []
    obs_by_id = {o.get("id"): o for o in doc["observations"]}
    for rule in list(doc["rules"]):
        confs = [obs_by_id[o].get("confidence") for o in rule.get("derived_from", []) if o in obs_by_id]
        floor = min_confidence(confs)
        if floor is None:
            continue
        if floor == "not-derivable":
            doc["rules"].remove(rule)
            warnings.append("dropped %s: derived from a not-derivable observation" % rule.get("id"))
        elif rule.get("confidence") in CONF_RANK and CONF_RANK[rule["confidence"]] > CONF_RANK[floor]:
            warnings.append("downgraded %s from %s to %s (R-RULE-1)" % (rule.get("id"), rule["confidence"], floor))
            rule["confidence"] = floor
    return warnings


def merge_analyses(docs, names=None, roles=None):
    """Merge several analysis documents. Pure: inputs are deep-copied.
    Returns (merged_doc, warnings). Raises MergeError on id collision, duplicate
    role owner, or an invalid input."""
    names = names or ["input-%d" % (i + 1) for i in range(len(docs))]
    docs = [copy.deepcopy(d) for d in docs]
    for name, d in zip(names, docs):
        errors = validate_analysis(d)
        if errors:
            raise MergeError("%s is not a valid analysis: %s" % (name, "; ".join(e["message"] for e in errors[:3])))
    merged = {"schema": SCHEMA, "references": [], "observations": [], "rules": [], "conflicts": [],
              "not_derivable": [], "palette_observed": []}
    projects = [d["project"] for d in docs if isinstance(d.get("project"), str) and d["project"].strip()]
    if projects:
        merged["project"] = projects[0]
    warnings = []
    seen = {}
    for name, d in zip(names, docs):
        for section, kind in (("references", "ref"), ("observations", "obs"), ("rules", "rule")):
            for item in d[section]:
                ident = item["id"]
                if ident in seen:
                    raise MergeError("id collision: %s appears in %s and %s (ids must be disjoint across inputs)"
                                     % (ident, seen[ident], name))
                seen[ident] = name
                merged[section].append(item)
        for c in d["conflicts"]:
            dup = next((m for m in merged["conflicts"] if norm_text(m.get("topic")) == norm_text(c.get("topic"))), None)
            if dup is None:
                merged["conflicts"].append(c)
            else:
                for r in c.get("between", []):
                    if r not in dup["between"]:
                        dup["between"].append(r)
                warnings.append("conflict topic %r appears in several inputs; kept the first, merged between" % c.get("topic"))
        for s in d["not_derivable"]:
            if norm_text(s) not in [norm_text(x) for x in merged["not_derivable"]]:
                merged["not_derivable"].append(s)
        merged["palette_observed"].extend(d["palette_observed"])

    # role overrides: a role named in --roles belongs exactly to the ref it names
    if roles:
        by_id = {r["id"]: r for r in merged["references"]}
        for ref_id in roles:
            if ref_id not in by_id:
                raise MergeError("--roles names %s which is not a merged reference" % ref_id)
        assigned = set()
        for ref_id, role_list in roles.items():
            assigned.update(role_list)
        for ref in merged["references"]:
            if ref["id"] in roles:
                ref["roles"] = list(roles[ref["id"]])
            else:
                ref["roles"] = [r for r in ref.get("roles", []) if r not in assigned]
            if ref["id"] in roles:
                ref.setdefault("provenance", {})["note"] = (
                    (ref["provenance"].get("note") or "").rstrip(". ") + "; roles assigned at merge").lstrip("; ")

    for role, owners in sorted(role_owners(merged).items()):
        if len(owners) > 1:
            raise MergeError("role '%s' owned by %s (%s)" % (
                role, " and ".join(owners), ", ".join(sorted(set(seen[o] for o in owners)))))

    warnings.extend(drop_non_owner_rules(merged))
    warnings.extend(detect_conflicts(merged))
    warnings.extend(rederive_rule_confidence(merged))
    errors = validate_analysis(merged)
    if errors:
        raise MergeError("merged document is invalid: %s" % "; ".join(
            "%s %s: %s" % (e["code"], e["path"], e["message"]) for e in errors))
    return merged, warnings


def merge_report(merged, warnings):
    conflicts = merged.get("conflicts", [])
    return {
        "status": "OK",
        "references": [{"id": r["id"], "label": r.get("label"), "roles": r.get("roles", []),
                        "viewed_by": r.get("viewed_by")} for r in merged["references"]],
        "roles": {role: owners[0] for role, owners in role_owners(merged).items()},
        "conflicts": {"open": [c["topic"] for c in conflicts if c.get("status") == "open"],
                      "resolved": [c["topic"] for c in conflicts if c.get("status") == "resolved"]},
        "rules_by_confidence": {c: sum(1 for r in merged["rules"] if r.get("confidence") == c) for c in RULE_CONFIDENCE},
        "observations": len(merged["observations"]),
        "not_derivable": len(merged["not_derivable"]),
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- extract-colors

def _luminance(rgb):
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _saturation(rgb):
    mx = max(rgb)
    return 0.0 if mx == 0 else (mx - min(rgb)) / float(mx)


def guess_roles(entries):
    """Assign `role_guess` to palette entries in place.

    Every guess is an assumption - verify against the image. Thresholds follow
    references/extraction-schema.md section 10 step 8; each colour gets the first
    role it qualifies for in the order background, text, outline, accent, surface,
    primary, secondary; the rest are 'unknown'."""
    for e in entries:
        e["role_guess"] = "unknown"
    if not entries:
        return entries
    info = []
    for e in entries:
        rgb = hex_to_rgb(e["hex"])
        info.append({"e": e, "Y": _luminance(rgb), "S": _saturation(rgb), "share": e["share"], "taken": False})

    def remaining():
        return [i for i in info if not i["taken"]]

    def take(item, role):
        item["taken"] = True
        item["e"]["role_guess"] = role

    bg = next((i for i in info if i["Y"] >= 0.55), None) or info[0]
    take(bg, "background")
    if bg["Y"] >= 0.45:
        cands = [i for i in remaining() if i["Y"] <= 0.25 and i["share"] >= 0.01]
        txt = min(cands, key=lambda i: i["Y"]) if cands else None
    else:
        cands = [i for i in remaining() if i["Y"] >= 0.75 and i["share"] >= 0.01]
        txt = max(cands, key=lambda i: i["Y"]) if cands else None
    if txt:
        take(txt, "text")
    cands = [i for i in remaining() if i["Y"] <= 0.30 and i["S"] <= 0.6 and i["share"] >= 0.02]
    if cands:
        take(max(cands, key=lambda i: i["share"]), "outline")
    cands = [i for i in remaining() if 0.03 <= i["share"] <= 0.35 and i["S"] >= 0.45]
    if cands:
        take(max(cands, key=lambda i: i["S"]), "accent")
    cands = [i for i in remaining() if abs(i["Y"] - bg["Y"]) <= 0.15 and i["share"] >= 0.05]
    if cands:
        take(max(cands, key=lambda i: i["share"]), "surface")
    for role in ("primary", "secondary"):
        cands = [i for i in remaining() if i["S"] >= 0.30]
        if cands:
            take(max(cands, key=lambda i: i["share"] * i["S"]), role)
    return entries


def extract_colors(path, k=10, ref_id=None):
    """Pixel-share palette of an image. Returns a dict with status OK or BLOCKED.
    Never raises ImportError: a missing Pillow yields status BLOCKED."""
    if not os.path.isfile(path):
        return {"status": "BLOCKED", "reason": "file-not-found", "message": "file not found: %s" % path}
    try:
        from PIL import Image
    except ImportError:
        return {"status": "BLOCKED", "reason": "pillow-missing",
                "message": "Pillow (PIL) is not installed (pip install Pillow); palette extraction unavailable"}
    try:
        img = Image.open(path)
        img.load()
    except Exception as exc:  # UnidentifiedImageError is an OSError subclass
        return {"status": "BLOCKED", "reason": "unreadable-image",
                "message": "unreadable image %s: %s" % (path, exc)}
    try:
        resampling = Image.Resampling.LANCZOS
    except AttributeError:  # Pillow < 9.1
        resampling = getattr(Image, "LANCZOS", 1)
    try:
        method = Image.Quantize.MEDIANCUT
        dither = Image.Dither.NONE
    except AttributeError:
        method, dither = 0, 0
    img.thumbnail((200, 200), resampling)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and img.info.get("transparency") is not None)
    if has_alpha:
        rgba = img.convert("RGBA")
        pixels = [(r, g, b) for (r, g, b, a) in rgba.getdata() if a >= 128]
        total_px = rgba.size[0] * rgba.size[1]
        if total_px == 0 or len(pixels) < 0.01 * total_px:
            return {"status": "BLOCKED", "reason": "image-transparent",
                    "message": "fewer than 1%% of pixels are opaque in %s" % path}
        work = Image.new("RGB", (len(pixels), 1))
        work.putdata(pixels)
    else:
        work = img.convert("RGB")
    q = work.quantize(colors=k, method=method, dither=dither)
    palette = q.getpalette()
    colors = q.getcolors(maxcolors=max(k, 256)) or []
    total = float(sum(c for c, _ in colors)) or 1.0
    entries = []
    for count, index in colors:
        r, g, b = palette[index * 3: index * 3 + 3]
        entries.append({"hex": "#%02X%02X%02X" % (r, g, b), "share": round(count / total, 4)})
    entries.sort(key=lambda e: (-e["share"], e["hex"]))
    kept = []
    for e in entries:
        merged_into = None
        for kpt in kept:
            if rgb_distance(hex_to_rgb(kpt["hex"]), hex_to_rgb(e["hex"])) < 24:
                merged_into = kpt
                break
        if merged_into is not None:
            merged_into["share"] = round(merged_into["share"] + e["share"], 4)
        else:
            kept.append(e)
    kept.sort(key=lambda e: (-e["share"], e["hex"]))
    guess_roles(kept)
    for e in kept:
        e["ref"] = ref_id
    return {"status": "OK", "ref": ref_id, "image": path, "size_analysed": [work.size[0], work.size[1]]
            if not has_alpha else [img.size[0], img.size[1]],
            "colors_requested": k, "colors_kept": len(kept), "confidence": "assumption",
            "palette_observed": kept}


# --------------------------------------------------------------------------- to-profile

RADIUS_CLASSES = ["pill", "xl", "lg", "md", "sm", "none"]
CONTAINER_WORDS = ("container", "panel", "card", "surface", "sheet", "dialog", "popup", "tile")
BUTTON_WORDS = ("button", "chip", "control", "cta", "pill-shaped")
RADIUS_PX_LADDER = ((2, "none"), (6, "sm"), (10, "md"), (16, "lg"), (32, "xl"))
TYPO_ADJECTIVES = ("heavy", "bold", "light", "thin", "condensed", "wide", "rounded", "geometric", "humanist",
                   "grotesque", "handwritten", "hand-lettered", "brush", "stencil", "bubbly", "chunky")
TYPO_WEIGHTS = ("heavy", "bold", "light", "thin")
TYPO_BASES = (("sans-serif", "sans"), ("sans serif", "sans"), ("sans", "sans"), ("slab", "slab"), ("serif", "serif"),
              ("monospace", "monospace"), ("mono", "monospace"), ("script", "script"), ("pixel", "pixel"),
              ("bitmap", "pixel"))
BODY_WORDS = ("body", "caption", "sub-label", "sublabel", "subtitle", "paragraph", "regular weight", "regular",
              "humanist", "secondary text")
SURFACE_ROLES = ("background", "surface", "text", "outline")
SEED_MAP = (("brand", ("primary",)), ("secondary", ("secondary",)), ("accent", ("accent", "cta")),
            ("neutral", ("text", "neutral")))


def _px_values(text):
    return [float(v) for v in re.findall(r"(\d+(?:\.\d+)?)\s*px\b", str(text or "").lower())]


def _radius_class_from_px(values):
    """Median px -> class: <=2 none, <=6 sm, <=10 md, <=16 lg, <=32 xl, >32 pill."""
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0
    for limit, name in RADIUS_PX_LADDER:
        if median <= limit:
            return name
    return "pill"


def _radius_class(statement):
    """Dominant container radius class named in a rule statement, judged clause by
    clause ("xl for containers", "pill for buttons"); None when no class word appears."""
    low = statement.lower()
    found = []
    offset = 0
    for clause in re.split(r"[,;.]", low):
        for cls in RADIUS_CLASSES:
            for m in re.finditer(r"\b%s\b" % re.escape(cls), clause):
                found.append((offset + m.start(), cls, any(w in clause for w in CONTAINER_WORDS),
                              any(w in clause for w in BUTTON_WORDS)))
        offset += len(clause) + 1
    if "sharp" in low or "square corners" in low:
        found.append((len(low), "none", True, False))
    if not found:
        return None
    container = [f for f in found if f[2] and not f[3]]
    if container:
        return sorted(container)[0][1]
    non_button = [f for f in found if not f[3]]
    if non_button:
        return sorted(non_button)[0][1]
    return sorted(found)[0][1]


def _silhouette(statement, radius_class):
    low = statement.lower()
    if "blob" in low:
        return "rounded-blob"
    if "bevel" in low:
        return "bevelled"
    if radius_class == "none" or "sharp" in low:
        return "sharp"
    if radius_class == "pill" or re.search(r"\bpill\b|fully rounded|circular", low):
        return "pill"
    return "rounded-rect"


def _outline_color_rule(low):
    if re.search(r"light(?:er)? tint|lighter|tint of|light shade", low):
        return "lighter-tint-of-fill"
    if re.search(r"darker|own fill|tonal|same hue", low):
        return "darker-shade-of-fill"
    if re.search(r"\bblack\b|\bdark\b|navy|near-black", low):
        return "contrast-dark"
    if re.search(r"no outline|\bnone\b", low):
        return "none"
    return "darker-shade-of-fill"


def _outline(statement, evidence_text=None):
    """shape.outline from a rule statement (+ its observations). Returns (dict, px_known)."""
    low = statement.lower()
    px = _px_values(evidence_text or statement)
    if re.search(r"\b(no outline|without outline|outline[- ]?free|outline: none)\b", low):
        return {"width": 0, "color_rule": "none"}, True
    rule = _outline_color_rule(low)
    if rule == "none":
        return {"width": 0, "color_rule": "none"}, True
    if px:
        width = max(1, int(round(px[0])))
    else:
        width = 3 if re.search(r"thick|heavy", low) else 2
    return {"width": width, "color_rule": rule}, bool(px)


def _shading(statement):
    low = statement.lower()
    for key, value in (("pixel", "pixel"), ("painterly", "painterly"), ("brush", "painterly"), ("clay", "clay"),
                       ("gloss", "glossy"), ("specular", "glossy"), ("soft cel", "soft-cel"),
                       ("cel shadow", "soft-cel"), ("soft-cel", "soft-cel"), ("hard shadow", "cel"),
                       ("cel", "cel"), ("blur", "soft"), ("soft shadow", "soft"), ("gradient", "soft"),
                       ("flat", "flat")):
        if key in low:
            return value
    return None


def _highlight(statement):
    low = statement.lower()
    if "gloss" in low or "specular" in low:
        return "top-left-gloss"
    if "band" in low or "top third" in low:
        return "top-band"
    if "rim" in low:
        return "rim-light"
    if "no highlight" in low:
        return "none"
    return None


def _shadow(statement):
    low = statement.lower()
    if "hard" in low and ("soft" in low or "blur" in low):
        return "double-clay"
    if "hard" in low or "bottom edge" in low or "bottom-edge" in low:
        return "hard-offset"
    if "glow" in low:
        return "glow"
    if "inner" in low or "inset" in low:
        return "inset"
    if "no shadow" in low or "shadow: none" in low:
        return "none"
    if "shadow" in low or "blur" in low:
        return "offset-soft"
    return None


def _classify_typography(text):
    """Classification string such as 'heavy rounded sans' (CC-4), never a family name."""
    low = str(text or "").lower()
    adjectives = [a for a in TYPO_ADJECTIVES if re.search(r"\b%s\b" % re.escape(a), low)]
    base = "sans"
    for needle, value in TYPO_BASES:
        if re.search(r"\b%s\b" % re.escape(needle), low):
            base = value
            break
    return " ".join(adjectives + [base])


def _typography_classes(text):
    """(display, body, body_inferred): clauses mentioning body/caption/regular/humanist classify
    the body family; the rest classify display. Without a body clause the body is the display
    family without its weight adjective (body_inferred=True)."""
    clauses = [c.strip() for c in re.split(r"[;.,]|\bversus\b|\bvs\b", str(text or "")) if c.strip()]
    body_clauses = [c for c in clauses if any(w in c.lower() for w in BODY_WORDS)]
    display_clauses = [c for c in clauses if c not in body_clauses] or clauses
    display = _classify_typography(" ".join(display_clauses))
    if body_clauses:
        return display, _classify_typography(" ".join(body_clauses)), False
    words = [w for w in display.split() if w not in TYPO_WEIGHTS]
    return display, " ".join(words), True


def _case(statement):
    low = statement.lower()
    found = []
    for key, value in (("title case", "title"), ("all caps", "upper"), ("uppercase", "upper"), ("upper", "upper"),
                       ("lower-case", "lower"), ("lowercase", "lower"), ("sentence case", "sentence")):
        if key in low and value not in found:
            found.append(value)
    if not found:
        return None
    return found[0] if len(found) == 1 else "mixed"


def _icon_style(statement):
    low = statement.lower()
    if "outline" in low and "filled" not in low:
        return "outline"
    if "two-tone" in low or "two tone" in low:
        return "filled-two-tone"
    if "pixel" in low:
        return "pixel"
    if "filled" in low:
        return "filled-rounded" if "round" in low else "filled"
    return "mixed"


def _first_clause(statement, limit=110):
    """First ';'/'.' clause; longer than `limit` -> cut to limit-1 characters plus an ellipsis
    (shared convention with vd.py, so both profile routes produce identical text)."""
    text = str(statement or "").strip()
    part = re.split(r"[;.]", text, maxsplit=1)[0].strip() or text
    if len(part) <= limit:
        return part.rstrip(" ,")
    return part[:limit - 1].rstrip(" ,") + "\u2026"


def _anti_patterns(statement):
    """Negations in a rule ('no thin-stroke icons') become 'Do not use ...' anti-patterns; same rule
    as vd.py: at least four words after 'Do not use', clauses with except/unless are skipped."""
    out = []
    for clause in re.split(r"[;.]\s*", str(statement or "")):
        c = clause.strip().rstrip(".")
        m = re.match(r"^(?:no|never|not|nothing)\s+(.+)$", c, re.I) if c else None
        if not m:
            continue
        rest = m.group(1).strip()
        if re.match(r"^(use|add|mix|rely|allow|place|animate|apply)\b", rest, re.I):
            text = "Do not %s" % rest
        else:
            text = "Do not use %s" % rest
        if len(text.split()) - 2 >= 4 and not re.search(r"\b(except|unless)\b", text, re.I):
            out.append(text)
    return out


def surfaces_from_palette_observed(palette_observed):
    """palette.surfaces: highest-share hex per background / surface / text / outline role guess."""
    best = {}
    for entry in palette_observed or []:
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("role_guess", "")).lower()
        hx = entry.get("hex")
        if role not in SURFACE_ROLES or not isinstance(hx, str) or not HEX_CI_RE.match(hx):
            continue
        share = float(entry.get("share") or 0)
        if role not in best or share > best[role][0]:
            best[role] = (share, hx.upper())
    return dict((role, hx) for role, (_s, hx) in best.items())


def seeds_from_palette_observed(palette_observed):
    """palette.seeds guesses with the same role mapping as `vd.py profile --reference`:
    primary -> brand, secondary -> secondary, accent/cta -> accent, text/neutral -> neutral
    (the raw observed text colour; vd.py derives the tinted neutral from it). Highest share wins."""
    best = {}
    for p in palette_observed or []:
        if not isinstance(p, dict) or not isinstance(p.get("hex"), str) or not HEX_CI_RE.match(p["hex"]):
            continue
        role = p.get("role_guess")
        if role not in best or float(p.get("share") or 0) > float(best[role].get("share") or 0):
            best[role] = p
    seeds = {}
    for seed, roles in SEED_MAP:
        for role in roles:
            if role in best:
                seeds[seed] = best[role]["hex"].upper()
                break
    return seeds


def to_profile_fragment(doc, style_id=DEFAULT_STYLE_ID, project=None, analysis_ref="reference-analysis.json"):
    """Map an analysis to a partial Visual Direction Profile (schema vdp/1).

    Emits everything `../visual-direction/scripts/vd.py profile --reference <analysis>`
    derives from the raw analysis, so the fragment route and the raw route agree:
    only observed/high rules populate contract fields; assumptions, open conflicts
    and not_derivable entries go to `unknowns`; `palette_observed` yields
    `palette.seeds`, `palette.surfaces` and `palette.observed`. The result carries
    "_partial": true and is completed by `vd.py profile`."""
    refs = doc.get("references", [])
    rules = doc.get("rules", [])
    obs_by_id = {o.get("id"): o for o in doc.get("observations", []) if isinstance(o, dict)}
    owned = []
    for r in refs:
        for role in r.get("roles", []):
            if role not in owned:
                owned.append(role)
    unknowns = []
    profile = {"schema": PROFILE_SCHEMA, "_partial": True,
               "_partial_note": "partial profile from reference analysis; product.* and style catalog fields "
                                "are completed by vd.py profile, which strips _partial"}
    name = project or (doc.get("project") if isinstance(doc.get("project"), str) else None)
    if name:
        profile["project"] = {"name": name, "slug": safe_slug(name)}
    profile["sources"] = [{"type": "reference-analysis", "ref": analysis_ref, "roles": owned}]
    if style_id == DEFAULT_STYLE_ID:
        # same inference as `vd.py profile --reference <raw>` without --style
        screen_types = set(str(r.get("screen_type", "")) for r in refs if isinstance(r, dict))
        is_game = bool(screen_types & {"gameplay", "shop"} or set(owned) & {"hud", "characters"})
        profile["product"] = {"kind": "game" if is_game else "app"}
        unknowns.append("product.kind '%s' inferred from reference screen types and roles; confirm"
                        % profile["product"]["kind"])
    shape, rendering, typography, iconography, illustration, motion, components = {}, {}, {}, {}, {}, {}, {}
    principles, qa, anti, exceptions = [], [], [], []
    palette_strategy = None
    strong_global = []

    def evidence(rule):
        return " ".join([str(rule.get("statement") or "")] +
                        [str(obs_by_id.get(o, {}).get("statement") or "") for o in rule.get("derived_from", [])])

    for rule in rules:
        target = str(rule.get("target", ""))
        statement = str(rule.get("statement", "")).strip()
        conf = rule.get("confidence")
        scope = str(rule.get("scope", "global"))
        derived = list(rule.get("derived_from", []))
        if conf not in ("observed", "high"):
            unknowns.append("assumption (%s, %s): %s" % (rule.get("id"), conf, statement[:120]))
            continue
        if scope.startswith("context:"):
            exceptions.append({"scope": scope.split(":", 1)[1], "rule": statement,
                               "reason": "observed in %s (%s)" % (", ".join(derived), rule.get("id"))})
            continue
        low = statement.lower()
        strong_global.append(rule)
        qa.append("%s: %s" % (target, statement))
        if len(principles) < 5:
            principles.append(_first_clause(statement, 110))
        for a in _anti_patterns(statement):
            if a not in anti:
                anti.append(a)
        if target == "palette":
            palette_strategy = statement
        elif target == "radius":
            cls = _radius_class_from_px(_px_values(evidence(rule))) or _radius_class(statement)
            if cls:
                shape["radius_class"] = cls
                shape["silhouette"] = _silhouette(statement, cls)
                unknowns.append("shape.radius_class %r inferred from %s; verify the dominant container class"
                                % (cls, rule.get("id")))
            else:
                unknowns.append("radius: %s (no px value or radius class word in %s; set shape.radius_class by hand)"
                                % (statement, rule.get("id")))
            components.setdefault("radius", statement)
        elif target == "outline":
            o, px_known = _outline(statement, evidence(rule))
            shape["outline"] = o
            if o.get("width") and not px_known:
                unknowns.append("outline px value is an assumption from a %% estimate (%s)" % rule.get("id"))
        elif target == "shading":
            s = _shading(statement)
            if s:
                rendering["shading"] = s
            h = _highlight(statement)
            if h:
                rendering["highlight"] = h
            sh = _shadow(statement)
            if sh:
                rendering["shadow"] = sh
        elif target == "shadow":
            sh = _shadow(statement)
            if sh:
                rendering["shadow"] = sh
        elif target == "typography":
            fam = re.search(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:family|font)\b", statement)
            unknown_family = re.search(r"family (?:name )?(?:is )?(?:unknown|not (?:known|identified|derivable))", low)
            if fam and not unknown_family:
                typography["display"] = fam.group(1)
                typography["body"] = fam.group(1)
            else:
                display, body, inferred = _typography_classes(evidence(rule))
                typography["display"] = display
                typography["body"] = body
                unknowns.append("typography.display family not identified; classification '%s' from %s (CC-4)"
                                % (display, ", ".join(derived) or rule.get("id")))
                if inferred:
                    unknowns.append("typography.body classification '%s' inferred from the display family (no body "
                                    "text observed in %s); confirm" % (body, rule.get("id")))
            case = _case(statement)
            if case:
                typography["case"] = case
            if "heavy" in low or "bold" in low:
                typography["weight_rule"] = "display bold / body medium"
        elif target == "icon":
            iconography["style"] = _icon_style(statement)
            iconography["stroke"] = None
            iconography["library_hint"] = "custom"
        elif target == "character":
            illustration["character_style"] = _first_clause(statement, 60).lower()
            illustration["asset_rendering"] = statement[:160]
        elif target == "motion":
            cls = next((c for c in ("bouncy", "snappy", "dramatic", "static", "soft") if re.search(r"\b%s\b" % c, low)), None)
            if cls:
                motion["class"] = cls
        elif target == "layout":
            pass  # layout rules live in principles / qa_criteria only
        else:
            components[target] = statement

    for entry in doc.get("not_derivable", []):
        unknowns.append("not derivable from references: %s" % entry)
    for c in doc.get("conflicts", []):
        if c.get("status") == "open":
            unknowns.append("open conflict on %s between %s" % (c.get("topic"), ", ".join(c.get("between", []))))
    if "class" not in motion:
        unknowns.append("motion class not derivable from static references")
    present = set(r.get("target") for r in strong_global)
    missing = [t for t in ("radius", "outline", "shading", "typography", "icon", "character", "palette")
               if t not in present]
    if missing:
        unknowns.append("no observed/high rule for: %s" % ", ".join(missing))
    if any("default precedence" in str(r.get("provenance", {}).get("note", "")).lower() for r in refs):
        unknowns.append("role assignment was defaulted; confirm before promoting rules to MASTER")

    observed = doc.get("palette_observed", []) or []
    palette = {}
    seeds = seeds_from_palette_observed(observed)
    if seeds:
        palette["seeds"] = seeds
        unknowns.append("palette.seeds are role guesses (assumption) from palette_observed; confirm before tokens")
    surfaces = surfaces_from_palette_observed(observed)
    if surfaces:
        palette["surfaces"] = surfaces
    if observed:
        palette["observed"] = copy.deepcopy(observed)

    open_conflicts = any(c.get("status") == "open" for c in doc.get("conflicts", []))
    confidence = "high" if len(strong_global) >= 5 and not open_conflicts else "assumption"
    profile["style"] = {"id": style_id, "name": " ".join(w.capitalize() for w in style_id.split("-")),
                        "confidence": confidence}
    profile["principles"] = principles
    profile["shape"] = shape
    profile["rendering"] = rendering
    profile["typography"] = typography
    if palette_strategy:
        profile["palette_strategy"] = palette_strategy
    if palette:
        profile["palette"] = palette
    if iconography:
        profile["iconography"] = iconography
    if illustration:
        profile["illustration"] = illustration
    profile["motion"] = motion
    profile["components"] = components
    profile["anti_patterns"] = anti
    profile["qa_criteria"] = qa
    profile["intentional_exceptions"] = exceptions
    seen = set()
    profile["unknowns"] = [u for u in unknowns if not (u in seen or seen.add(u))]
    return profile


# --------------------------------------------------------------------------- summary

def summarize(doc, max_lines=12):
    """<= 12 lines: references and roles, counts per confidence, owners, open conflicts."""
    result = validate(doc)
    counts = result["counts"]
    lines = []
    refs = doc.get("references", []) if isinstance(doc.get("references"), list) else []
    lines.append("Reference analysis: %d reference(s), status %s (%d error(s), %d warning(s))"
                 % (len(refs), result["status"], len(result["errors"]), len(result["warnings"])))
    for r in refs[:3]:
        if isinstance(r, dict):
            verb = {"model-vision": "viewed", "human-description": "per your description", "none": "not analysed"}.get(
                r.get("viewed_by"), "?")
            lines.append("  %s %s [%s] roles: %s" % (r.get("id"), r.get("label"), verb,
                                                     ", ".join(r.get("roles", []) or ["-"])))
    unowned = [role for role in ROLES if role not in role_owners(doc)]
    lines.append("Unowned roles: %s" % (", ".join(unowned) or "none"))
    obc = counts.get("observations_by_confidence", {})
    lines.append("Observations: %d (observed %d, high %d, assumption %d, not-derivable %d)"
                 % (counts.get("observations", 0), obc.get("observed", 0), obc.get("high", 0),
                    obc.get("assumption", 0), obc.get("not-derivable", 0)))
    rbc = counts.get("rules_by_confidence", {})
    lines.append("Rules: %d (observed %d, high %d, assumption %d)" % (
        counts.get("rules", 0), rbc.get("observed", 0), rbc.get("high", 0), rbc.get("assumption", 0)))
    conflicts = doc.get("conflicts", []) if isinstance(doc.get("conflicts"), list) else []
    open_c = [c for c in conflicts if isinstance(c, dict) and c.get("status") == "open"]
    lines.append("Conflicts: %d (%d open)" % (len(conflicts), len(open_c)))
    for c in open_c[:2]:
        lines.append("  OPEN %s: %s" % (c.get("topic"), c.get("resolution")))
    rules = [r for r in doc.get("rules", []) if isinstance(r, dict) and r.get("confidence") in ("observed", "high")]
    for r in rules[:2]:
        lines.append("  %s %s: %s" % (r.get("id"), r.get("target"), _first_clause(str(r.get("statement", "")))))
    nd = doc.get("not_derivable", []) if isinstance(doc.get("not_derivable"), list) else []
    lines.append("Not derivable: %d (%s)" % (len(nd), "; ".join(map(str, nd[:3])) + (" ..." if len(nd) > 3 else "")))
    if len(lines) > max_lines:
        lines = lines[:max_lines - 1] + ["  ... (truncated to %d lines)" % max_lines]
    return "\n".join(lines)


# --------------------------------------------------------------------------- template

def template_doc():
    return {
        "schema": SCHEMA,
        "_help": "Fill references first (ids ref-N in the order the user listed the images), validate, then add "
                 "observations (obs-N), rules (rule-N), conflicts, not_derivable, palette_observed. Keys starting "
                 "with '_' are comments and are ignored by validate.",
        "project": "",
        "references": [{
            "id": "ref-1", "path": "refs/REPLACE.png", "label": "REPLACE: user's words or filename",
            "roles": [], "viewed_by": "none", "screen_type": "other",
            "provenance": {"owner": "unknown", "license": "unknown", "note": "REPLACE: where it came from"},
            "_help": "roles: subset of %s, one owner per role; viewed_by: model-vision | human-description | none; "
                     "screen_type: %s" % (", ".join(ROLES), ", ".join(SCREEN_TYPES)),
        }],
        "_help_observations": "{id: obs-N, category: %s, statement: one claim, refs: [ref-N], evidence: region or "
                              "'user description, paragraph N' or 'n/a <reason>' when not-derivable, confidence: %s}"
                              % ("|".join(CATEGORIES), "|".join(CONFIDENCE)),
        "observations": [],
        "_help_rules": "{id: rule-N, target: %s, statement: imperative, derived_from: [obs-N], confidence: %s "
                       "(min of derived observations), scope: global | context:<screen_type>}"
                       % ("|".join(TARGET_VOCAB), "|".join(RULE_CONFIDENCE)),
        "rules": [],
        "_help_conflicts": "{topic: lower-case noun phrase, between: [ref-N, ref-M], resolution: 'ref-N wins (role x): "
                           "...' when resolved or the question for the user when open, status: resolved | open}",
        "conflicts": [],
        "_help_not_derivable": "strings; static images usually need: %s" % ", ".join(STANDARD_NOT_DERIVABLE),
        "not_derivable": [],
        "_help_palette_observed": "{hex: #RRGGBB upper-case, share: 0..1 (<= 4 decimals, sums <= 1 per ref), "
                                  "role_guess: %s (always an assumption), ref: ref-N}" % "|".join(ROLE_GUESS),
        "palette_observed": [],
    }


# --------------------------------------------------------------------------- CLI

def write_json(path, obj):
    """Write `obj` as JSON, creating missing parent directories (CC-14)."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def _print_json(obj):
    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def _fail_load(err, as_json, extra=None):
    code, message = err
    sys.stderr.write("ERROR: %s\n" % message)
    if as_json:
        payload = {"status": "FAIL", "errors": [{"code": "E-IO" if code == 2 else "E-JSON", "path": "$",
                                                  "message": message}], "warnings": []}
        if extra:
            payload.update(extra)
        _print_json(payload)
    return code


def cmd_validate(args):
    doc, err = load_json_file(args.file)
    if err:
        return _fail_load(err, args.json, {"file": args.file})
    result = validate(doc, strict=args.strict)
    if args.check_paths:
        base = os.path.dirname(os.path.abspath(args.file))
        for i, ref in enumerate(doc.get("references", []) or []):
            if isinstance(ref, dict) and isinstance(ref.get("path"), str):
                p = ref["path"] if os.path.isabs(ref["path"]) else os.path.join(base, ref["path"])
                if not os.path.isfile(p):
                    result["warnings"].append({"code": "W-PATH", "path": "references[%d].path" % i,
                                               "message": "image not found: %s" % ref["path"]})
    result["file"] = args.file
    for w in result["warnings"]:
        sys.stderr.write("WARN %s %s: %s\n" % (w["code"], w["path"], w["message"]))
    if args.json:
        _print_json(result)
    else:
        c = result["counts"]
        if result["status"] == "OK":
            obc = c["observations_by_confidence"]
            sys.stdout.write("OK %s: %d references, %d observations (observed %d, high %d, assumption %d, "
                             "not-derivable %d), %d rules, %d conflicts (%d open), %d warnings\n"
                             % (args.file, c["references"], c["observations"], obc["observed"], obc["high"],
                                obc["assumption"], obc["not-derivable"], c["rules"], c["conflicts"],
                                c["conflicts_open"], len(result["warnings"])))
        else:
            for e in result["errors"]:
                sys.stdout.write("ERROR %s %s: %s\n" % (e["code"], e["path"], e["message"]))
            sys.stdout.write("FAIL %s: %d error(s)\n" % (args.file, len(result["errors"])))
    return 0 if result["status"] == "OK" else 1


def cmd_merge(args):
    if len(args.inputs) < 2:
        sys.stderr.write("ERROR: merge needs at least two input files\n")
        return 2
    docs = []
    for path in args.inputs:
        doc, err = load_json_file(path)
        if err:
            return _fail_load(err, args.json)
        docs.append(doc)
    try:
        roles = parse_role_specs(args.roles)
    except ValueError as exc:
        sys.stderr.write("ERROR: %s\n" % exc)
        return 2
    try:
        merged, warnings = merge_analyses(docs, names=args.inputs, roles=roles)
    except MergeError as exc:
        sys.stderr.write("ERROR: merge rejected: %s\n" % exc)
        if args.json:
            _print_json({"status": "FAIL", "errors": [{"code": "E-MERGE", "path": "$", "message": str(exc)}],
                         "warnings": []})
        return 1
    write_json(args.out, merged)
    report = merge_report(merged, warnings)
    report["out"] = args.out
    for w in warnings:
        sys.stderr.write("WARN %s\n" % w)
    if args.json:
        _print_json(report)
    else:
        sys.stdout.write("OK merged %d inputs -> %s\n" % (len(docs), args.out))
        for r in report["references"]:
            sys.stdout.write("  %s %s [%s] roles: %s\n" % (r["id"], r["label"], r["viewed_by"], ", ".join(r["roles"]) or "-"))
        sys.stdout.write("  conflicts: %d open (%s), %d resolved\n" % (
            len(report["conflicts"]["open"]), ", ".join(report["conflicts"]["open"]) or "-",
            len(report["conflicts"]["resolved"])))
        rb = report["rules_by_confidence"]
        sys.stdout.write("  rules: observed %d, high %d, assumption %d; observations %d; not derivable %d\n"
                         % (rb["observed"], rb["high"], rb["assumption"], report["observations"], report["not_derivable"]))
    return 0


def cmd_extract_colors(args):
    k = args.k
    if k < 8 or k > 12:
        sys.stderr.write("ERROR: --k must be between 8 and 12 (got %d)\n" % k)
        return 2
    if not os.path.isfile(args.image):
        sys.stderr.write("ERROR: file not found: %s\n" % args.image)
        return 2
    result = extract_colors(args.image, k=k, ref_id=args.ref_id)
    if result["status"] == "BLOCKED":
        sys.stderr.write("BLOCKED: %s\n" % result["message"])
        if args.json:
            _print_json(result)
        return 3
    if args.out:
        write_json(args.out, result)
    if args.json:
        _print_json(result)
    else:
        sys.stdout.write("%s: %d colours (requested %d), analysed at %dx%d; role guesses are assumptions\n"
                         % (args.image, result["colors_kept"], k, result["size_analysed"][0], result["size_analysed"][1]))
        for e in result["palette_observed"]:
            sys.stdout.write("%s  %6.2f%%  %s (assumption)\n" % (e["hex"], e["share"] * 100, e["role_guess"]))
        if args.out:
            sys.stdout.write("written %s\n" % args.out)
    return 0


def cmd_to_profile(args):
    doc, err = load_json_file(args.file)
    if err:
        return _fail_load(err, args.json)
    errors = validate_analysis(doc)
    if errors:
        sys.stderr.write("ERROR: %s is not a valid analysis (%d error(s)); run validate first\n" % (args.file, len(errors)))
        for e in errors:
            sys.stderr.write("  %s %s: %s\n" % (e["code"], e["path"], e["message"]))
        if args.json:
            _print_json({"status": "FAIL", "errors": errors, "warnings": []})
        return 1
    profile = to_profile_fragment(doc, style_id=args.style_id, project=args.project,
                                  analysis_ref=os.path.basename(args.file))
    if args.out:
        write_json(args.out, profile)
    if args.json or not args.out:
        _print_json(profile)
    else:
        sys.stdout.write("OK partial profile -> %s (style %s, confidence %s, %d components, %d unknowns)\n"
                         % (args.out, profile["style"]["id"], profile["style"]["confidence"],
                            len(profile["components"]), len(profile["unknowns"])))
    return 0


def cmd_summary(args):
    doc, err = load_json_file(args.file)
    if err:
        return _fail_load(err, False)
    sys.stdout.write(summarize(doc) + "\n")
    return 0


def cmd_template(args):
    doc = template_doc()
    if args.out:
        write_json(args.out, doc)
        sys.stdout.write("OK template -> %s\n" % args.out)
    else:
        _print_json(doc)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="reference_analysis.py",
                                     description="Validate, merge, colour-extract, summarise and convert "
                                                 "reference-analysis.json documents (vdp-reference-analysis/1).")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("validate", help="check an analysis file against the extraction schema rules")
    p.add_argument("file")
    p.add_argument("--strict", action="store_true", help="treat open conflicts as errors")
    p.add_argument("--check-paths", action="store_true", help="warn when referenced image files are missing")
    p.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("merge", help="merge two or more analyses into one document")
    p.add_argument("inputs", nargs="+", help="analysis files (ids must be disjoint)")
    p.add_argument("--out", required=True, help="output file (written only when the result validates)")
    p.add_argument("--roles", nargs="*", default=[], metavar="REF:ROLES",
                   help="role assignment, e.g. ref-1:color,shapes ref-2:buttons")
    p.add_argument("--json", action="store_true", help="machine-readable report on stdout")
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("extract-colors", help="pixel-share palette of an image (needs Pillow; BLOCKED otherwise)")
    p.add_argument("image")
    p.add_argument("--k", "--colors", dest="k", type=int, default=10, help="quantisation colours, 8..12 (default 10)")
    p.add_argument("--ref-id", "--ref", dest="ref_id", default=None, help="reference id to stamp on entries (ref-N)")
    p.add_argument("--out", default=None, help="also write the JSON result to this file")
    p.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    p.set_defaults(func=cmd_extract_colors)

    p = sub.add_parser("to-profile", help="emit a partial Visual Direction Profile (vdp/1, _partial)")
    p.add_argument("file")
    p.add_argument("--style-id", default=DEFAULT_STYLE_ID, help="style id to record (default %s)" % DEFAULT_STYLE_ID)
    p.add_argument("--project", default=None, help="project name for project.name/slug")
    p.add_argument("--out", default=None, help="output file; printed to stdout when omitted")
    p.add_argument("--json", action="store_true", help="print the profile on stdout as well")
    p.set_defaults(func=cmd_to_profile)

    p = sub.add_parser("summary", help="<= 12-line human summary of an analysis")
    p.add_argument("file")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("template", help="print the empty analysis skeleton")
    p.add_argument("--out", default=None, help="write the skeleton to this file")
    p.set_defaults(func=cmd_template)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_usage(sys.stderr)
        sys.stderr.write("error: a subcommand is required (validate, merge, extract-colors, to-profile, summary, template)\n")
        return 2
    try:
        return args.func(args)
    except KeyboardInterrupt:
        sys.stderr.write("error: interrupted\n")
        return 2
    except Exception as exc:  # CC-14: never a traceback; one line, exit 2
        sys.stderr.write("error: %s failed: %s: %s\n" % (args.command, type(exc).__name__, exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
