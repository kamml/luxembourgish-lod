#!/usr/bin/env python3
"""
luxembourgish-lod — deterministic, LOD-backed verification of Luxembourgish text.

An INDEPENDENT check on Luxembourgish produced by a language model (or a
learner). It does not reason or guess: it reads the bundled LOD (Lëtzebuerger
Online Dictionnaire) data and applies the N-rule (Eifeler Regel) mechanically.
Its purpose is to catch the errors a model cannot catch in itself: confident
fabrication, German-shaped paradigms, wrong gender/plural/article, N-rule
misapplication, and unattested word order.

Design contract:
- NEVER asserts a word is wrong because it is "unusual." A word absent from the
  local LOD data is reported as UNVERIFIED (check lod.lu), not WRONG. The local
  snapshot has known gaps and lags the live dictionary.
- Reserves WRONG for claims that CONTRADICT a positive LOD attestation (e.g. a
  claimed gender M when LOD says F).
- All output is structured: VERIFIED / UNVERIFIED / WRONG, with the LOD entry id
  cited for every VERIFIED or WRONG verdict.

Usage:
  verify.py word    <lemma>                         # existence + full LOD entry
  verify.py article <lemma> [nom|acc|dat]           # article from LOD gender + N-rule
  verify.py nrule   "<word> <nextword>"             # one -n boundary
  verify.py text    "<sentence>"                    # unknown-word scan + every -n boundary
  verify.py order   "<pattern A>" ["<pattern B>"]   # word order against the example corpus
  verify.py phrase  "<pattern>"                     # is this exact sequence attested?
  verify.py check   <lemma> --gender M --plural Xen --pos SUBST   # claims vs LOD
  verify.py tsv     <file.tsv>                      # batch-check a TSV (lemma/gender/plural/pos)

Exit code is 0 if no WRONG verdicts, 1 if any WRONG verdict was emitted.

Data: references/lod/*.json, built from the LOD open data (CC0, Zenter fir
d'Lëtzebuerger Sprooch) by scripts/build_lod_json.py. Set LOD_DIR to point at
a different build.
"""

import sys
import os
import json
import pickle
import re
import argparse
import unicodedata

# ----- LOD data access -------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_lod_dir():
    """LOD_DIR env var, else references/lod beside this package (repo / skill layout)."""
    env = os.environ.get("LOD_DIR")
    if env:
        return env
    for cand in (os.path.join(SCRIPT_DIR, "..", "references", "lod"),
                 os.path.join(SCRIPT_DIR, "references", "lod")):
        cand = os.path.normpath(cand)
        if os.path.isfile(os.path.join(cand, "lod-index.json")):
            return cand
    return os.path.normpath(os.path.join(SCRIPT_DIR, "..", "references", "lod"))


LOD_DIR = _find_lod_dir()

# Accented-initial filename map (matches build_lod_json.py)
ACCENT_FILE = {
    "Ä": "lod-Ae.json", "ä": "lod-Ae.json",
    "É": "lod-Eacute.json", "é": "lod-Eacute.json",
    "Ë": "lod-Euml.json", "ë": "lod-Euml.json",
    "Ö": "lod-Oe.json", "ö": "lod-Oe.json",
    "Ü": "lod-Ue.json", "ü": "lod-Ue.json",
}

_INDEX = None
_FILE_CACHE = {}


def load_index():
    global _INDEX
    if _INDEX is None:
        with open(os.path.join(LOD_DIR, "lod-index.json"), encoding="utf-8") as f:
            _INDEX = json.load(f)
    return _INDEX


def file_for_lemma(lemma):
    if not lemma:
        return "lod-other.json"
    c = lemma[0]
    if c in ACCENT_FILE:
        return ACCENT_FILE[c]
    if c.isalpha() and c.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return f"lod-{c.upper()}.json"
    return "lod-other.json"


def load_file(fname):
    if fname not in _FILE_CACHE:
        path = os.path.join(LOD_DIR, fname)
        if not os.path.exists(path):
            _FILE_CACHE[fname] = []
        else:
            with open(path, encoding="utf-8") as f:
                _FILE_CACHE[fname] = json.load(f)
    return _FILE_CACHE[fname]


def lookup(lemma):
    """Return the full LOD entry for an exact lemma match, or None."""
    entries = load_file(file_for_lemma(lemma))
    for e in entries:
        if e.get("lemma") == lemma:
            return e
    return None


def lookup_ci(lemma):
    """Case-insensitive fallback: return list of entries whose lemma matches ignoring case."""
    entries = load_file(file_for_lemma(lemma))
    low = lemma.lower()
    return [e for e in entries if e.get("lemma", "").lower() == low]


# ----- N-rule (Eifeler Regel) ------------------------------------------------

# UNITED ZOAH: keep final -n before these. n, d, t, z, h + vowels a e i o u.
KEEP_SET = set("ndtzhaeiou")

# An accented or umlauted vowel behaves as its BASE letter for UNITED ZOAH
# membership, so the -n is kept before it. The ten letters are a mnemonic for
# sounds, not a literal character set.
#   é  LOD: "den éischte Band vum Lexikon ass 1956 erauskomm"  → keep
#   ä  LOD: "Froen an Äntwerten"                                → keep
# Testing membership character-by-character wrongly reports DROP at
# "den | éischte" and "mäin | éischten".
ACCENT_FOLD = {
    "\u00e9": "e", "\u00e8": "e", "\u00ea": "e", "\u00eb": "e",
    "\u00e4": "a", "\u00e0": "a", "\u00e2": "a",
    "\u00ef": "i", "\u00ee": "i",
    "\u00f6": "o", "\u00f4": "o",
    "\u00fc": "u", "\u00fb": "u",
}


def fold_accent(ch):
    """Map an accented vowel to its base letter; leave everything else alone."""
    if ch is None:
        return ch
    return ACCENT_FOLD.get(ch.lower(), ch.lower())


# ----- LOD-backed inflected-form index ---------------------------------------
# lod-index.json is keyed by LEMMA only, so without this index every plural,
# participle and conjugated form would come back UNVERIFIED. This index is
# built once from the bundled JSON (33.7k entries) and maps every attested
# SURFACE form back to its lemma, so an inflected form is recognised instead
# of being reported as unknown.

_FORMS = None
_DROPS = None

# Fields whose values are attested surface forms, and the label to report.
_FORM_FIELDS = (
    ("lemma", "lemma"),
    ("lemma_nrule", "N-rule form of"),
    ("plural", "plural of"),
    ("plural_nrule", "N-rule plural of"),
    ("pp", "past participle of"),
    ("pp_nrule", "N-rule past participle of"),
)


def _cache_path():
    """Cache file keyed by the newest mtime in the LOD folder, so it self-invalidates."""
    try:
        stamp = max(os.path.getmtime(os.path.join(LOD_DIR, f))
                    for f in os.listdir(LOD_DIR) if f.endswith(".json"))
    except (OSError, ValueError):
        return None
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    d = os.path.join(base, "luxembourgish-lod")
    return os.path.join(d, "forms-%d.pkl" % int(stamp))


def forms_index():
    """{surface_form_lower: (lemma, id, kind)} over every attested form in LOD.

    Built once (a few seconds over 33.7k entries) and then cached to disk, so
    that callers which spawn one process per sentence stay usable.
    """
    global _FORMS, _DROPS
    if _FORMS is not None:
        return _FORMS

    cp = _cache_path()
    if cp and os.path.exists(cp):
        try:
            with open(cp, "rb") as fh:
                blob = pickle.load(fh)
            _FORMS, _DROPS = blob["forms"], blob["drops"]
            return _FORMS
        except Exception:
            pass          # corrupt or stale cache — fall through and rebuild

    _FORMS = {}
    _DROPS = {}

    def add(val, lemma, eid, kind):
        """Register a surface form. Where several lemmas share a form, prefer the
        shortest lemma — 'maacht' should cite maachen, not amaachen or
        bekanntmaachen, which merely sort earlier by filename."""
        if not isinstance(val, str) or not val:
            return
        key = val.lower()
        cur = _FORMS.get(key)
        if cur is None or (lemma and cur[0] and len(lemma) < len(cur[0])):
            _FORMS[key] = (lemma, eid, kind)

    def add_verbform(val, lemma, eid, kind):
        """LOD writes paradigm cells as phrases, not bare forms.

        conj p5 of maachen is "maacht (iech)" — a reflexive parenthetical — and
        presentPerfect p1 of maachen is "hunn (mech) gemaach / gemaacht", an
        auxiliary plus two participle variants. Indexing those strings whole
        would mean bare 'maacht' and 'gemaacht' never match. Strip the
        parentheticals, split the variants, and register the phrase and each
        of its tokens.
        """
        if not isinstance(val, str) or not val:
            return
        cleaned = re.sub(r"\([^)]*\)", " ", val)
        for variant in cleaned.split("/"):
            variant = re.sub(r"\s+", " ", variant).strip()
            if not variant:
                continue
            add(variant, lemma, eid, kind)
            parts = variant.split()
            if len(parts) > 1:
                for tok in parts:
                    add(tok, lemma, eid, kind)

    for fname in sorted(os.listdir(LOD_DIR)):
        if not fname.startswith("lod-") or not fname.endswith(".json"):
            continue
        if fname == "lod-index.json":
            continue
        for e in load_file(fname):
            lemma, eid = e.get("lemma"), e.get("id")
            for field, kind in _FORM_FIELDS:
                add(e.get(field), lemma, eid, kind)
            # record, for every -n form, whether LOD attests a dropped variant
            for base, nrule in (("lemma", "lemma_nrule"),
                                ("plural", "plural_nrule"),
                                ("pp", "pp_nrule")):
                bv = e.get(base)
                if isinstance(bv, str) and bv.lower().endswith("n"):
                    _DROPS.setdefault(bv.lower(), (eid, base, bv, e.get(nrule), nrule))

            for k, v in (e.get("conj") or {}).items():
                add_verbform(v, lemma, eid, "%s of" % k)
            tenses = e.get("tenses") or {}
            if isinstance(tenses, dict):
                for k, v in tenses.items():
                    if isinstance(v, str):
                        add_verbform(v, lemma, eid, "%s of" % k)
                    elif isinstance(v, dict):
                        for k2, v2 in v.items():
                            add_verbform(v2, lemma, eid, "%s %s of" % (k, k2))
            # Declined adjective forms live under "adj" (groussen, grousst,
            # léifsten, béschte...).
            adjf = e.get("adj")
            if isinstance(adjf, dict):
                for key in ("positive", "comparative", "superlative"):
                    add_verbform(adjf.get(key), lemma, eid, "%s form of" % key)
                decl = adjf.get("decl")
                if isinstance(decl, dict):
                    for degree, table in decl.items():
                        if not isinstance(table, dict):
                            continue
                        for gender, forms in table.items():
                            if isinstance(forms, list):
                                for fm in forms:
                                    add(fm, lemma, eid,
                                        "%s %s form of" % (degree, gender))

    # Register the N-rule-dropped variant of every attested -n form. LOD spells
    # out lemma_nrule / plural_nrule / pp_nrule but records no dropped variant
    # for declined adjectives or most paradigm cells, so 'grousse' (from
    # groussen), 'ka' (kann), 'ugefaange' (ugefaangen) would otherwise report
    # UNVERIFIED while their -n forms are recognised. The drop is mechanical.
    for form, (lemma, eid, kind) in list(_FORMS.items()):
        if form.endswith("nn"):
            _FORMS.setdefault(form[:-2], (lemma, eid, "N-rule form of"))
        elif form.endswith("n"):
            _FORMS.setdefault(form[:-1], (lemma, eid, "N-rule form of"))

    if cp:
        try:
            os.makedirs(os.path.dirname(cp), exist_ok=True)
            tmp = cp + ".tmp%d" % os.getpid()
            with open(tmp, "wb") as fh:
                pickle.dump({"forms": _FORMS, "drops": _DROPS}, fh, protocol=4)
            os.replace(tmp, cp)
        except Exception:
            pass          # cache is an optimisation, never load-bearing
    return _FORMS


def lookup_form(token):
    """Recognise an inflected form. Returns (lemma, id, kind) or None."""
    return forms_index().get((token or "").lower())


def has_attested_drop(token):
    """Does this -n actually drop? Returns (verdict, detail).

    verdict True  = LOD attests a dropped form for this token
            False = LOD knows the token but records NO dropped form → the -n is
                    stem and never drops (Persoun, Frënn, the feminine -in suffix)
            None  = token not in LOD; fall back to the mechanical rule

    A purely mechanical UNITED ZOAH test applied to every word-final -n reports
    DROP on forms that never drop:
      · the feminine -in suffix — "Informatikerin vu Beruff" (LOD attestations
        keep the -n before non-UNITED-ZOAH consonants, no counterexamples)
      · stem-final -n — Persoun (PERSOUN1 has plural_nrule but NO lemma_nrule,
        so the lemma's own -n is stem), Frënn
    LOD already carries the data needed to tell these apart.
    """
    forms_index()          # ensures _DROPS is built
    t = (token or "").lower()
    if not t:
        return None, "empty token"
    hit = _DROPS.get(t)
    if hit is None:
        return None, "not in local LOD"
    eid, base, bval, dropped, nrule_field = hit
    if dropped:
        return True, "LOD [%s] attests %s='%s'" % (eid, nrule_field, dropped)
    return False, ("LOD [%s] records %s='%s' with no %s — this -n is stem and "
                   "does not drop" % (eid, base, bval, nrule_field))


def check_overapplied_drop(token, next_word):
    """FALSE-NEGATIVE guard: an -n that was wrongly DROPPED is invisible to a
    check that only inspects tokens still ending in -n.

    'Ech gi net gär' is wrong (LOD corpus: 'ginn net' is attested, 'gi net' is
    not) yet contains no token ending in -n. Returns (lemma, id, restored) or None.

    ADVISORY ONLY — 'gi' is perfectly correct before a non-UNITED-ZOAH consonant.
    """
    t = (token or "").strip()
    if not t or t.lower().endswith("n") or not t.isalpha():
        return None
    fa = first_alpha(next_word or "")
    if fa is None or fold_accent(fa) not in KEEP_SET:
        return None
    forms_index()
    cands = [t + "n", t + "nn"]
    # Prefer the candidate LOD positively attests as THIS token's dropped form —
    # otherwise "gi" matches the noun "Gin" (GIN1) before the verb "ginn" (GINN1)
    # and the advisory cites the wrong entry.
    for cand in cands:
        d = _DROPS.get(cand)
        if d and d[3] and d[3].lower() == t:
            return (d[2], d[0], cand)
    for cand in cands:
        hit = lookup_form(cand)
        if hit:
            return (hit[0], hit[1], cand)
    return None


def first_alpha(token):
    for ch in token:
        if ch.isalpha():
            return ch
    return None


PUNCT = ",.;:!?)]}\u2013\u2014-"


def nrule_keep(next_word, cur_word=None):
    """Return (keep: bool, reason: str) for a final -n before next_word.

    cur_word is the token the -n sits on. If it carries trailing punctuation
    (e.g. "formuléieren,"), exception 2 applies and the -n is kept regardless
    of what follows.
    """
    if cur_word is not None and cur_word.rstrip() and cur_word.rstrip()[-1] in PUNCT:
        return True, "punctuation follows the -n — keep (exception 2)"
    if next_word is None or next_word == "":
        return True, "end of string / nothing follows — keep"
    # punctuation immediately?
    stripped = next_word.lstrip()
    if stripped and stripped[0] in ",.;:!?)]}\u2013\u2014-":
        return True, "followed by punctuation — keep"
    fa = first_alpha(next_word)
    if fa is None:
        return True, "no alphabetic letter follows — keep (default)"
    # proper noun heuristic: capitalised mid-phrase -> rule does not apply to NAMES,
    # but common nouns are also capitalised in LB, so we only NOTE, never auto-drop.
    folded = fold_accent(fa)
    keep = folded in KEEP_SET
    base = "in UNITED ZOAH" if keep else "not in UNITED ZOAH"
    if folded != fa.lower():
        base += " (accented '%s' folds to '%s')" % (fa, folded)
    return keep, f"next letter '{fa}' {base} → {'keep' if keep else 'drop'}"


def ends_in_n(word):
    w = word.rstrip(",.;:!?)]}")
    return w.endswith("n")


def apply_nrule_to_form(form_with_n, next_word):
    """Given a form that (canonically) ends in -n, return the correct surface form."""
    keep, reason = nrule_keep(next_word)
    if keep:
        return form_with_n, reason
    # drop a single trailing n (double nn -> single? rule: both drop -> base without nn's trailing)
    if form_with_n.endswith("nn"):
        return form_with_n[:-2], reason  # both n's drop
    if form_with_n.endswith("n"):
        return form_with_n[:-1], reason
    return form_with_n, reason


# ----- Article derivation ----------------------------------------------------

def derive_article(gender, case, noun):
    """Return (article_surface, note). gender in M/F/N/PL, case in nom/acc/dat."""
    g = (gender or "").upper()
    case = case.lower()
    # base forms before N-rule
    if case in ("nom", "acc"):
        table = {"M": "den", "F": "d'", "N": "d'", "PL": "d'"}
    elif case == "dat":
        table = {"M": "dem", "F": "der", "N": "dem", "PL": "den"}
    else:
        return None, f"unknown case '{case}'"
    base = table.get(g)
    if base is None:
        return None, f"unknown gender '{gender}'"
    # N-rule applies to forms ending in -n: den (M nom/acc, PL dat). d', dem, der do not end in -n.
    if base.endswith("n"):
        surface, reason = apply_nrule_to_form(base, noun)
        return surface, f"{g} {case}: base '{base}', {reason}"
    return base, f"{g} {case}: '{base}' (no N-rule; does not end in -n)"


# ----- Verdict formatting ----------------------------------------------------

class Report:
    def __init__(self):
        self.lines = []
        self.has_wrong = False

    def verified(self, msg):
        self.lines.append(f"✅ VERIFIED  {msg}")

    def unverified(self, msg):
        self.lines.append(f"⚠️ UNVERIFIED {msg}")

    def wrong(self, msg):
        self.lines.append(f"❌ WRONG     {msg}")
        self.has_wrong = True

    def note(self, msg):
        self.lines.append(f"   ·         {msg}")

    def emit(self):
        try:
            print("\n".join(self.lines))
        except BrokenPipeError:
            try:
                sys.stdout.close()
            except Exception:
                pass
        return 1 if self.has_wrong else 0


# ----- Commands --------------------------------------------------------------

def cmd_word(args, rep):
    lemma = args.lemma
    e = lookup(lemma)
    if e:
        g = e.get("gender") or "—"
        pl = e.get("plural") or "—"
        rep.verified(f"'{lemma}' found in LOD [{e['id']}] pos={e.get('pos')} gender={g} plural={pl}")
        if e.get("en"):
            rep.note("en: " + "; ".join(e["en"]))
        if e.get("example"):
            rep.note("ex: " + e["example"])
        if e.get("conj"):
            c = e["conj"]
            rep.note("conj: " + ", ".join(f"{k}={v}" for k, v in c.items()))
            rep.note(f"aux={e.get('aux')} pp={e.get('pp')}")
    else:
        ci = lookup_ci(lemma)
        if ci:
            rep.unverified(f"'{lemma}' not found with that exact casing; case variants exist: "
                           + ", ".join(f"{x['lemma']} [{x['id']}]" for x in ci))
        else:
            rep.unverified(f"'{lemma}' not in local LOD. Web-check lod.lu before using or "
                           f"flagging as contamination — local data has gaps.")
    return rep


def cmd_article(args, rep):
    lemma = args.lemma
    e = lookup(lemma)
    if not e:
        rep.unverified(f"'{lemma}' not in local LOD — cannot derive article from verified gender. "
                       f"Web-check lod.lu.")
        return rep
    if e.get("pos") != "SUBST" or not e.get("gender"):
        rep.unverified(f"'{lemma}' [{e['id']}] is pos={e.get('pos')}, gender={e.get('gender')} "
                       f"— not a gendered noun; article derivation does not apply.")
        return rep
    cases = [args.case] if args.case else ["nom", "acc", "dat"]
    for cs in cases:
        art, note = derive_article(e["gender"], cs, lemma)
        rep.verified(f"{art} {lemma}   ({note})  [gender from LOD {e['id']}]")
    return rep


def cmd_nrule(args, rep):
    parts = args.phrase.split()
    if len(parts) < 2:
        # single token: just say whether it ends in -n
        w = parts[0] if parts else ""
        rep.unverified(f"need two tokens 'word nextword'; got '{args.phrase}'")
        return rep
    word, nxt = parts[0], parts[1]
    if not ends_in_n(word):
        rep.note(f"'{word}' does not end in -n; N-rule does not apply to this boundary.")
        return rep
    keep, reason = nrule_keep(nxt)
    correct = word if keep else (word[:-2] if word.rstrip(",.;:!?").endswith("nn") else word.rstrip(",.;:!?")[:-1])
    rep.verified(f"'{word}' before '{nxt}': {reason}. Correct surface: '{correct}'.")
    fa = first_alpha(nxt)
    if fa and fa.isupper():
        rep.note("next word is capitalised — if it is a PROPER NOUN, the N-rule does not "
                 "apply and the name is never altered; verdict above assumes common word.")
    return rep


def cmd_text(args, rep):
    text = args.sentence
    tokens = re.findall(r"\S+", text)
    # 1. N-rule boundaries — mechanical rule, then checked against LOD
    for i in range(len(tokens) - 1):
        w = tokens[i]
        nxt = tokens[i + 1]
        if ends_in_n(w):
            keep, reason = nrule_keep(nxt, w)
            if keep:
                rep.note(f"N-rule boundary: '{w}' | '{nxt}' → keep ({reason})")
            else:
                bare = w.rstrip(",.;:!?)]}")
                attested, detail = has_attested_drop(bare)
                if attested is False:
                    # the -n is stem: Persoun, Frënn, the feminine -in suffix
                    rep.note(f"N-rule boundary: '{w}' | '{nxt}' → keep — mechanical rule "
                             f"said DROP but {detail}")
                elif attested is True:
                    rep.note(f"N-rule boundary: '{w}' | '{nxt}' → DROP ({reason}); {detail}")
                else:
                    rep.note(f"N-rule boundary: '{w}' | '{nxt}' → DROP ({reason}); "
                             f"{detail} — verdict is mechanical only, confirm before applying")
        else:
            # FALSE-NEGATIVE guard: an -n wrongly dropped is invisible to the
            # loop above, which only inspects tokens still ending in -n.
            over = check_overapplied_drop(w, nxt)
            if over:
                lemma, eid, restored = over
                rep.note(f"possible OVER-APPLIED drop: '{w}' | '{nxt}' — '{restored}' is "
                         f"attested ({lemma} [{eid}]) and '{nxt}' starts with a UNITED ZOAH "
                         f"letter, so the -n should probably be KEPT. Advisory: '{w}' is "
                         f"correct before a non-UNITED-ZOAH consonant.")
    # 2. unknown-word scan (alpha tokens only, strip punctuation, skip pure-cap acronyms)
    seen = set()
    for tok in tokens:
        clean = re.sub(r"[^\wäëéöüÄËÉÖÜ']", "", tok)
        # strip leading article/pronoun contractions (d', n', s', t', m') so the bare lemma matches
        m = re.match(r"^([dnstmDNSTM])['\u2019](.+)$", clean)
        if m:
            clean = m.group(2)
        if not clean or clean.lower() in seen:
            continue
        seen.add(clean.lower())
        if clean.lower() in ("d", "de", "den", "dem", "der", "e", "en", "eng", "engem", "enger",
                             "ech", "du", "hien", "si", "et", "mir", "dir", "an", "a", "vu", "vun",
                             "op", "um", "am", "an", "zu", "fir", "mat", "net", "gär", "och"):
            continue  # high-frequency function words / contractions
        e = lookup(clean) or (lookup_ci(clean)[0] if lookup_ci(clean) else None)
        if e:
            rep.verified(f"'{clean}' in LOD [{e['id']}] ({e.get('pos')})")
        else:
            # lod-index.json is keyed by lemma only; the forms index recognises
            # plurals, participles and conjugated forms so that a wall of
            # spurious UNVERIFIED lines does not hide a real miss.
            form = lookup_form(clean)
            if form:
                lemma, eid, kind = form
                rep.verified(f"'{clean}' is the {kind} '{lemma}' in LOD [{eid}]")
            else:
                rep.unverified(f"'{clean}' not in local LOD (checked lemmas and all attested "
                               f"inflected forms) — web-check lod.lu before treating as "
                               f"verified or as contamination.")
    return rep


def cmd_check(args, rep):
    """Check generated claims (gender/plural/pos) against LOD. Emits WRONG on contradiction."""
    lemma = args.lemma
    e = lookup(lemma)
    if not e:
        rep.unverified(f"'{lemma}' not in local LOD — cannot confirm or contradict claims. "
                       f"Web-check lod.lu.")
        return rep
    rep.note(f"LOD entry {e['id']}: pos={e.get('pos')} gender={e.get('gender')} plural={e.get('plural')}")
    if args.pos and e.get("pos") and args.pos.upper() != e["pos"]:
        rep.wrong(f"pos: generated '{args.pos}' but LOD says '{e['pos']}' [{e['id']}]")
    elif args.pos:
        rep.verified(f"pos '{args.pos}' matches LOD [{e['id']}]")
    if args.gender and e.get("gender") and args.gender.upper() != e["gender"]:
        rep.wrong(f"gender: generated '{args.gender}' but LOD says '{e['gender']}' [{e['id']}]")
    elif args.gender and e.get("gender"):
        rep.verified(f"gender '{args.gender}' matches LOD [{e['id']}]")
    elif args.gender:
        rep.unverified(f"gender: LOD entry has no gender recorded; cannot confirm '{args.gender}'")
    if args.plural and e.get("plural") and args.plural != e["plural"]:
        rep.wrong(f"plural: generated '{args.plural}' but LOD says '{e['plural']}' [{e['id']}]")
    elif args.plural and e.get("plural"):
        rep.verified(f"plural '{args.plural}' matches LOD [{e['id']}]")
    elif args.plural:
        rep.unverified(f"plural: LOD entry has no plural recorded; cannot confirm '{args.plural}'")
    return rep


def cmd_tsv(args, rep):
    """Batch-check a TSV (e.g. a flashcard export). Expects a header row naming
    columns; checks lemma/gender/plural/pos against LOD."""
    path = args.file
    if not os.path.exists(path):
        rep.wrong(f"file not found: {path}")
        return rep
    with open(path, encoding="utf-8") as f:
        rows = [ln.rstrip("\n").split("\t") for ln in f if ln.strip() and not ln.startswith("#")]
    if not rows:
        rep.unverified("no data rows found")
        return rep
    header = [h.strip().lower() for h in rows[0]]
    def col(name):
        return header.index(name) if name in header else None
    li, gi, pli, poi = col("lemma"), col("gender"), col("plural"), col("pos")
    if li is None:
        rep.wrong("TSV has no 'lemma' column in header; cannot batch-check.")
        return rep
    checked = 0
    for r in rows[1:]:
        if li >= len(r):
            continue
        lemma = r[li].strip()
        if not lemma:
            continue
        checked += 1
        e = lookup(lemma)
        if not e:
            rep.unverified(f"row '{lemma}': not in local LOD — web-check lod.lu")
            continue
        probs = []
        if gi is not None and gi < len(r) and r[gi].strip() and e.get("gender") \
                and r[gi].strip().upper() != e["gender"]:
            probs.append(f"gender {r[gi].strip()}≠LOD {e['gender']}")
        if pli is not None and pli < len(r) and r[pli].strip() and r[pli].strip() not in ("", "-") \
                and e.get("plural") and r[pli].strip() != e["plural"]:
            probs.append(f"plural {r[pli].strip()}≠LOD {e['plural']}")
        if poi is not None and poi < len(r) and r[poi].strip() and e.get("pos") \
                and r[poi].strip().upper() != e["pos"]:
            probs.append(f"pos {r[poi].strip()}≠LOD {e['pos']}")
        if probs:
            rep.wrong(f"row '{lemma}' [{e['id']}]: " + "; ".join(probs))
        else:
            rep.verified(f"row '{lemma}' [{e['id']}] consistent with LOD")
    rep.note(f"checked {checked} rows")
    return rep


# ----- Example corpus (word order / phrase attestation) ----------------------
# LOD's example sentences are the only mechanical evidence available for
# syntax. The corpus is every `example` field plus every senses[].examples[].t,
# deduplicated on (entry id, text). It is a sample, not an inventory: absence
# from it is weaker evidence than absence from the lemma index, so an
# unattested pattern is INFERRED, never WRONG on its own.
#
# Pattern syntax (matched case- and diacritic-insensitively):
#   word        literal token
#   (a|b|c)     alternation of tokens
#   *           exactly one arbitrary token
#   ..          a gap of 0-4 arbitrary tokens
#   ^   $       anchor to start / end of the example sentence

_CORPUS = None


def fold_text(s):
    """Lower-case and strip diacritics, so un-accented input still matches."""
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def corpus():
    """[(entry_id, sentence)] over every attested LOD example, deduplicated."""
    global _CORPUS
    if _CORPUS is not None:
        return _CORPUS
    seen, out = set(), []
    for fname in sorted(os.listdir(LOD_DIR)):
        if not fname.startswith("lod-") or not fname.endswith(".json") or fname == "lod-index.json":
            continue
        for e in load_file(fname):
            eid = e.get("id") or "?"
            texts = [e["example"]] if e.get("example") else []
            for s in e.get("senses") or []:
                for x in s.get("examples") or []:
                    if x.get("t"):
                        texts.append(x["t"])
            for t in texts:
                if (eid, t) not in seen:
                    seen.add((eid, t))
                    out.append((eid, t))
    _CORPUS = out
    return _CORPUS


_TOKEN_END = r"(?=\s|$|[.,!?;:])"


def compile_pattern(p):
    out = []
    for tok in p.split():
        if tok == "^":
            out.append(r"^\s*")
            continue
        if tok == "$":
            out.append(r"\s*[.!?]?\s*$")
            continue
        sep = r"(?:^|\s)" if not out else ("" if out[-1].endswith(r"\s*") else r"\s+")
        if tok == "*":
            out.append(sep + r"\S+")
        elif tok == "..":
            out.append(r"(?:\s+\S+){0,4}" if out else r"(?:\S+\s+){0,4}")
            # the following token supplies its own separator
            out[-1] = out[-1] + r"\s*"
        elif tok.startswith("(") and tok.endswith(")"):
            alts = "|".join(re.escape(fold_text(a)) for a in tok[1:-1].split("|") if a)
            out.append(sep + "(?:" + alts + ")" + _TOKEN_END)
        else:
            out.append(sep + re.escape(fold_text(tok)) + _TOKEN_END)
    return re.compile("".join(out))


def corpus_hits(pattern):
    rx = compile_pattern(pattern)
    return [(eid, t) for eid, t in corpus() if rx.search(fold_text(t))]


def _show_hits(rep, hits, limit=4):
    for eid, t in hits[:limit]:
        rep.note(f"[{eid}] {t}")


def cmd_phrase(args, rep):
    """Is this exact sequence attested anywhere in the LOD example corpus?"""
    hits = corpus_hits(args.pattern)
    rep.note(f"corpus: {len(corpus())} sentences")
    if hits:
        rep.verified(f"{args.pattern!r} attested {len(hits)}x in LOD examples")
        _show_hits(rep, hits)
    else:
        rep.unverified(f"{args.pattern!r} not attested in LOD examples — INFERRED at best; "
                       f"do not present as verified")
    return rep


def cmd_order(args, rep):
    """Compare two competing orders against the example corpus."""
    A, B = args.pattern_a, args.pattern_b
    ha = corpus_hits(A)
    rep.note(f"corpus: {len(corpus())} sentences")
    rep.note(f"A {A!r} -> {len(ha)}")
    _show_hits(rep, ha)
    if B is None:
        if ha:
            rep.verified(f"{A!r} attested {len(ha)}x")
        else:
            rep.unverified(f"{A!r} not attested — INFERRED, do not present as verified")
        return rep
    hb = corpus_hits(B)
    rep.note(f"B {B!r} -> {len(hb)}")
    _show_hits(rep, hb)
    na, nb = len(ha), len(hb)
    hi, hn, ln = (A, na, nb) if na >= nb else (B, nb, na)
    if na == nb == 0:
        rep.unverified("neither order attested — the corpus cannot decide; mark INFERRED")
    elif ln == 0 and hn >= 3:
        rep.verified(f"{hi!r} attested {hn}x, the other ZERO — use the attested order")
    elif hn >= 5 * max(ln, 1):
        rep.verified(f"{hi!r} dominates {hn}:{ln} — prefer it; the minority is not necessarily wrong")
    elif ln == 0:
        rep.unverified(f"only {hn} hit(s) vs zero — too thin; mark INFERRED")
    else:
        rep.verified(f"both attested ({hn}:{ln}) — variation, NOT an error; do not mark either wrong")
    return rep


def main():
    p = argparse.ArgumentParser(
        description="luxembourgish-lod: deterministic, LOD-backed verification of Luxembourgish.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("word", help="existence + full LOD entry"); sp.add_argument("lemma")
    sp = sub.add_parser("article", help="article from LOD gender + N-rule")
    sp.add_argument("lemma"); sp.add_argument("case", nargs="?", default=None)
    sp = sub.add_parser("nrule", help="check one -n boundary"); sp.add_argument("phrase")
    sp = sub.add_parser("text", help="unknown-word scan + every -n boundary"); sp.add_argument("sentence")
    sp = sub.add_parser("order", help="compare word orders against the example corpus")
    sp.add_argument("pattern_a"); sp.add_argument("pattern_b", nargs="?", default=None)
    sp = sub.add_parser("phrase", help="is this sequence attested in LOD examples?")
    sp.add_argument("pattern")
    sp = sub.add_parser("tsv", help="batch-check a TSV with lemma/gender/plural/pos columns")
    sp.add_argument("file")
    sp = sub.add_parser("check", help="check claimed gender/plural/pos against LOD")
    sp.add_argument("lemma")
    sp.add_argument("--gender"); sp.add_argument("--plural"); sp.add_argument("--pos")

    args = p.parse_args()
    rep = Report()
    dispatch = {
        "word": cmd_word, "article": cmd_article, "nrule": cmd_nrule,
        "text": cmd_text, "order": cmd_order, "phrase": cmd_phrase,
        "tsv": cmd_tsv, "check": cmd_check,
    }
    dispatch[args.cmd](args, rep)
    sys.exit(rep.emit())


if __name__ == "__main__":
    main()
