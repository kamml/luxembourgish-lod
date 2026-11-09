#!/usr/bin/env python3
"""Build the luxembourgish-lod local LOD JSON from the official LOD open-data
XML dumps (articles + conjugation/declension tables), published CC0 by the
Zenter fir d'Lëtzebuerger Sprooch at https://data.public.lu/.

Extracts English + Luxembourgish content only (no DE/FR/PT/NL).

Outputs, into --out:
  lod-index.json          lemma -> [ {id, pos}, ... ]  (homograph-aware)
  lod-{A..Z}.json         full entries by first letter of lemma
  lod-Ae/Eacute/Euml/Oe/Ue/other.json   accented / non-alpha initials

Usage: python3 build_lod_json.py --art new_lod-art.xml --tab new_lod-tab.xml --out outdir
"""
import argparse, json, os, re, sys
import xml.etree.ElementTree as ET
from collections import defaultdict

APOS = "'’"  # straight + typographic apostrophe
PUNCT_ONLY = re.compile(r"^[?!.,;:…»«\)\]]+$")

LETTER_MAP = {"Ä": "Ae", "É": "Eacute", "Ë": "Euml", "Ö": "Oe", "Ü": "Ue"}


def letter_file(lemma):
    first = lemma[0].upper()
    if first in LETTER_MAP:
        return LETTER_MAP[first]
    if "A" <= first <= "Z":
        return first
    return "other"


def join_words(elem):
    """Join <word>/<inflectedHeadword> tokens into a sentence.
    Attaches d'/w'-style clitics to the following token and closes up
    space before standalone punctuation."""
    toks = [
        (t.text or "").strip()
        for t in elem
        if t.tag in ("word", "inflectedHeadword") and (t.text or "").strip()
    ]
    out = ""
    for tok in toks:
        if not out:
            out = tok
        elif out[-1] in APOS or PUNCT_ONLY.match(tok):
            out += tok
        else:
            out += " " + tok
    return out


def texts(parent, tag):
    return [
        (e.text or "").strip() for e in parent.findall(tag) if (e.text or "").strip()
    ]


def parse_tab(path):
    """Return (verb_tables, adj_tables) keyed by entry id."""
    verbs, adjs = {}, {}
    for _, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "verbConjugation":
            vid = elem.get("id")
            t = {}
            if elem.get("separableVerb") == "yes":
                t["sep"] = True
            for mood in ("indicative", "conditional"):
                m = elem.find(mood)
                if m is None:
                    continue
                for tense in m:
                    forms = {p.tag: p.text for p in tense if p.text}
                    if not forms:
                        continue
                    # indicative present is already stored as entry["conj"]
                    if mood == "indicative" and tense.tag == "present":
                        t.setdefault("_present", forms)
                        continue
                    key = tense.tag if mood == "indicative" else "cond_" + tense.tag
                    t[key] = forms
            imp = elem.find("imperative/present")
            if imp is not None:
                forms = {p.tag: p.text for p in imp if p.text}
                if forms:
                    t["imperative"] = forms
            t["_inf"] = elem.findtext("infinitive")
            t["_pp"] = elem.findtext("pastParticiple")
            t["_aux"] = elem.findtext("auxiliaryVerb")
            verbs[vid] = t
            elem.clear()
        elif elem.tag == "adjDeclension":
            aid = elem.get("id")
            a = {}
            bf = elem.find("basicForms")
            if bf is not None:
                for deg in ("positive", "comparative", "superlative"):
                    v = bf.findtext(deg)
                    if v:
                        a[deg] = v
            decl = elem.find("declension")
            if decl is not None:
                dd = {}
                for deg in decl:  # positive / comparative / superlative
                    block = {}
                    sg = deg.find("singular")
                    if sg is not None:
                        for gen, key in (
                            ("masculine", "m"),
                            ("feminine", "f"),
                            ("neutral", "n"),
                        ):
                            g = sg.find(gen)
                            if g is not None:
                                block[key] = [
                                    g.findtext(c)
                                    for c in (
                                        "nominative",
                                        "accusative",
                                        "dative",
                                        "genitive",
                                    )
                                ]
                    pl = elem.find(f"declension/{deg.tag}/plural/masculineFeminineNeutral")
                    if pl is not None:
                        block["pl"] = [
                            pl.findtext(c)
                            for c in ("nominative", "accusative", "dative", "genitive")
                        ]
                    if block:
                        dd[deg.tag] = block
                if dd:
                    a["decl"] = dd
            adjs[aid] = a
            elem.clear()
    return verbs, adjs


def parse_meaning(m):
    """One <meaning> -> sense dict (EN + LB only)."""
    s = {}
    n = m.findtext("number")
    if n:
        s["n"] = int(n)
    infl = m.find("inflection[@type='plural']/form")
    if infl is not None and (infl.text or "").strip():
        s["plural"] = infl.text.strip()
        if infl.get("nRuleForm"):
            s["plural_nrule"] = infl.get("nRuleForm")
    ph = m.findtext("secondaryHeadword")
    if ph:
        s["phrase"] = ph.strip()
    en = m.find("targetLanguage[@lang='en']")
    if en is not None:
        tr = texts(en, "translation")
        if tr:
            s["en"] = tr
        cl = en.findtext("semanticClarifier")
        if cl:
            s["en_note"] = cl.strip()
    regs = texts(m, "attribute")
    if regs:
        s["register"] = regs
    gram = texts(m, "grammaticalInformation")
    if gram:
        s["gram"] = gram
    di = m.findtext("declensionInfo")
    if di:
        s["note"] = di.strip()
    exs = []
    for ex in m.findall("examples/example"):
        txt = ex.find("text")
        if txt is None:
            continue
        e = {"t": join_words(txt)}
        reg = texts(txt, "attribute")
        if reg:
            e["reg"] = reg[0] if len(reg) == 1 else reg
        gl = ex.find("gloss")
        if gl is not None:
            g = join_words(gl)
            if g:
                e["gloss"] = g
        if e["t"]:
            exs.append(e)
    if exs:
        s["examples"] = exs
    return s


def parse_art(path, verbs, adjs):
    entries = []
    for _, elem in ET.iterparse(path, events=("end",)):
        if elem.tag != "entry":
            continue
        eid = elem.get("id")
        lem = elem.find("lemma")
        lemma = (lem.text or "").strip() if lem is not None else ""
        if not lemma:
            elem.clear()
            continue
        e = {"id": eid, "lemma": lemma}
        nr = lem.get("nRuleForm")
        if nr:
            e["lemma_nrule"] = nr
        ipa = elem.findtext("ipa")
        if ipa:
            e["ipa"] = ipa.strip()

        pos_all, gender, aux, pp, gram_entry = [], None, None, None, []
        plural = plural_nrule = None
        senses = []
        for ms in elem.findall("microStructure"):
            p = ms.find("partOfSpeech")
            if p is not None and p.text:
                pos_all.append(p.text.strip())
                if gender is None:
                    gender = p.get("gen")
            if aux is None:
                aux = ms.findtext("auxiliaryVerb")
            if pp is None:
                pp = ms.findtext("pastParticiple")
            infl = ms.find("inflection[@type='plural']/form")
            if infl is not None and plural is None:
                plural = (infl.text or "").strip() or None
                plural_nrule = infl.get("nRuleForm")
            for gu in ms.findall("grammaticalUnit"):
                for gi in texts(gu, "grammaticalInformation"):
                    if gi not in gram_entry:
                        gram_entry.append(gi)
                for m in gu.findall("meaning"):
                    senses.append(parse_meaning(m))

        e["pos"] = pos_all[0] if pos_all else None
        if len(pos_all) > 1:
            e["pos_all"] = pos_all
        e["gender"] = gender
        if plural is None:
            # plural may be recorded per-sense rather than per-entry
            plural = next((s["plural"] for s in senses if s.get("plural")), None)
            plural_nrule = next(
                (s["plural_nrule"] for s in senses if s.get("plural_nrule")), None
            )
        e["plural"] = plural
        if plural_nrule:
            e["plural_nrule"] = plural_nrule

        # legacy convenience fields: first sense EN + first example
        first_en = next((s["en"] for s in senses if s.get("en")), None)
        e["en"] = first_en or []
        first_ex = next(
            (s["examples"][0]["t"] for s in senses if s.get("examples")), None
        )
        e["example"] = first_ex

        if aux:
            e["aux"] = aux.upper()
        if pp:
            e["pp"] = pp
        if gram_entry:
            e["gram"] = gram_entry
        if senses:
            e["senses"] = senses

        # synonyms
        syns = []
        for sg in elem.findall("allSynonyms/synonymGroup"):
            g = {}
            ft = texts(sg, "fromTerms/term")
            if ft:
                g["from"] = ft[0] if len(ft) == 1 else ft
            to = texts(sg, "toSynonyms/syn")
            if to:
                g["to"] = to
            reg = texts(sg, "attribute")
            if reg:
                g["reg"] = reg[0] if len(reg) == 1 else reg
            if g.get("to"):
                syns.append(g)
        if syns:
            e["syn"] = syns

        # see-also / variant links from infoboxes
        see = []
        for il in elem.findall("infobox/infoboxList/infoboxListItem/internalLink"):
            ref = il.get("idRef")
            if ref and (il.text or "").strip():
                see.append({"id": ref, "lemma": il.text.strip()})
        if see:
            e["see"] = see

        # merge tab data
        vt = verbs.get(eid)
        if vt:
            pres = vt.get("_present")
            if pres:
                e["conj"] = pres
            # tab pp "voll Form / N-Reegel-Form" carries the n-rule variant
            tab_pp = vt.get("_pp")
            if tab_pp and " / " in tab_pp:
                full, nrule = (x.strip() for x in tab_pp.split(" / ", 1))
                if not e.get("pp"):
                    e["pp"] = full
                if e.get("pp") == full:
                    e["pp_nrule"] = nrule
            elif not e.get("pp") and tab_pp:
                e["pp"] = tab_pp
            if not e.get("aux") and vt.get("_aux"):
                e["aux"] = vt["_aux"].upper()
            if vt.get("sep"):
                e["sep"] = True
            tenses = {
                k: v for k, v in vt.items() if not k.startswith("_") and k != "sep"
            }
            if tenses:
                e["tenses"] = tenses
        at = adjs.get(eid)
        if at:
            e["adj"] = at

        entries.append(e)
        elem.clear()
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", required=True)
    ap.add_argument("--tab", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("parsing tab...", file=sys.stderr)
    verbs, adjs = parse_tab(args.tab)
    print(f"  {len(verbs)} verb tables, {len(adjs)} adj tables", file=sys.stderr)
    print("parsing art...", file=sys.stderr)
    entries = parse_art(args.art, verbs, adjs)
    print(f"  {len(entries)} entries", file=sys.stderr)

    by_letter = defaultdict(list)
    index = defaultdict(list)
    for e in entries:
        by_letter[letter_file(e["lemma"])].append(e)
        index[e["lemma"]].append({"id": e["id"], "pos": e["pos"]})

    for letter, ents in sorted(by_letter.items()):
        with open(os.path.join(args.out, f"lod-{letter}.json"), "w") as f:
            json.dump(ents, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(args.out, "lod-index.json"), "w") as f:
        json.dump(dict(index), f, ensure_ascii=False, separators=(",", ":"))
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
