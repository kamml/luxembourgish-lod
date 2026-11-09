---
name: luxembourgish-lod
description: >
  Deterministic verification of Luxembourgish (Lëtzebuergesch) against the LOD dictionary.
  Use whenever you are about to present a Luxembourgish word, form, article, N-rule call,
  example sentence or word-order claim — to a learner, in generated content, or in a
  correction. Provides a bundled offline copy of LOD (33,737 entries), a 58,375-sentence
  example corpus, and `scripts/verify.py`, which checks lexical existence, gender, plural,
  conjugation, N-rule application and corpus attestation mechanically. Never generate
  Luxembourgish from memory and present it as correct without running this check.
---

# luxembourgish-lod

## Core principle

**Verified over plausible.** A language model produces fluent Luxembourgish that is often
wrong — German-shaped paradigms, invented genders, misapplied N-rule, word orders that no
speaker uses — and there is rarely a reader who can tell. This skill makes the check
mechanical: open the dictionary data and compare, rather than reread the sentence and ask
whether it looks right. The generator and the checker must be independent, so an error has
to survive both.

Three rules follow:

1. **A verified label requires a lookup performed this turn.** Never from memory, never
   inherited from earlier in the conversation, never because the form "is obviously right".
2. **Do not compose Luxembourgish; quote it.** Example sentences shown to a reader come
   verbatim from LOD's `example` fields. A composed sentence is marked UNVERIFIED and said
   to be composed.
3. **Absence from the data is UNVERIFIED, never WRONG.** The local snapshot has gaps and
   lags the live dictionary. WRONG is reserved for a claim that contradicts a positive LOD
   attestation.

## What is bundled

- `references/lod/lod-index.json` — every lemma → `[{id, pos}, …]`, homograph-aware.
- `references/lod/lod-{A..Z}.json`, `lod-Ae/Eacute/Euml/Oe/Ue.json`, `lod-other.json` —
  full entries by first letter: all senses, all example sentences, full verb paradigms,
  adjective comparison and declension, IPA, register labels, synonym groups, and LOD's own
  N-rule variant forms. ~1,800 place-name entries (`NP`); no personal names.
- `scripts/verify.py` — the checker (below).
- `scripts/build_lod_json.py` — rebuilds the JSON from the LOD open-data XML.
- `references/n-rule.md` — the N-rule in full, with LOD-attested examples.
- `references/articles.md` — the article system, from the *Grammaire* with LOD cross-checks.

The data is a snapshot of the LOD open data (CC0, Zenter fir d'Lëtzebuerger Sprooch,
https://data.public.lu/). Words added to LOD after the snapshot date are absent; check
https://lod.lu for those.

## The checker: `scripts/verify.py`

```
verify.py word    <lemma>                         # existence + full LOD entry
verify.py article <lemma> [nom|acc|dat]           # article from LOD gender + N-rule
verify.py nrule   "<word> <nextword>"             # one -n boundary
verify.py text    "<sentence>"                    # unknown-word scan + every -n boundary
verify.py order   "<pattern A>" ["<pattern B>"]   # word order against the example corpus
verify.py phrase  "<pattern>"                     # is this exact sequence attested?
verify.py check   <lemma> --gender F --plural Xen --pos SUBST   # claims vs LOD
verify.py tsv     <file.tsv>                      # batch-check a TSV (lemma/gender/plural/pos)
```

Output lines are `✅ VERIFIED`, `⚠️ UNVERIFIED` or `❌ WRONG`, each citing the LOD entry id.
Exit status is 1 if anything is WRONG. Python 3.8+, standard library only. The first run
builds an index of every attested surface form (a few seconds) and caches it under
`~/.cache/luxembourgish-lod/`.

**Corpus patterns** (`order`, `phrase`) are matched case- and diacritic-insensitively over
the 58,375 deduplicated LOD example sentences:

```
word        literal token
(a|b|c)     alternation of tokens
*           exactly one arbitrary token
..          a gap of 0–4 arbitrary tokens
^   $       anchor to start / end of the sentence
```

`order` with two patterns reports both counts and a verdict: attested-vs-zero (use the
attested one), dominance ≥ 5:1 (prefer it; the minority is not necessarily wrong), both
attested (variation — mark neither wrong), or neither attested (the corpus cannot decide).

```
verify.py order "(owes|moies|mëttes) (dacks|ëmmer|meeschtens)" \
                "(dacks|ëmmer|meeschtens) (owes|moies|mëttes)"
→ A 7 · B 1 · '(owes|moies|mëttes) (dacks|ëmmer|meeschtens)' dominates 7:1
```

The corpus is a sample, not an inventory. Absence from it is weaker evidence than absence
from the lemma index, so an unattested pattern is INFERRED, never WRONG on its own.

## What must be verified before output

- Headword spelling and capitalisation
- Part of speech
- Noun gender and plural
- Verb infinitive and paradigm
- Every example sentence (verbatim from LOD, or marked as composed)
- Every N-rule call (see § N-rule)
- Any word-order or constituency claim (against the corpus)

## Flagging convention

- `✅ LOD-verified` — confirmed against the bundled data or lod.lu this turn
- `⚠️ UNVERIFIED` — not confirmed against LOD; say so to the reader
- `🔁 INFERRED` — derived by rule from a verified root (an article from an attested gender,
  an N-rule drop from an attested `-n` form); name the root. A word-order call with no
  corpus attestation is INFERRED, not verified.
- `❌ WRONG` — contradicts a positive LOD attestation; cite the entry id

The label is a guarantee about *what was checked this turn*, not a generic stamp of
approval. If LOD is unavailable and nothing else can confirm a form, stop and say which
word cannot be verified rather than presenting it anyway.

## Looking up a word

**Quick check:** read `references/lod/lod-index.json`. It maps every lemma, in LOD's exact
spelling (case-sensitive; multiword lemmas use real spaces), to an array of `{id, pos}` —
one per homograph.

**Full entry:** read `references/lod/lod-{X}.json` where `{X}` is the capitalised first
letter of the lemma, with these ASCII-safe names for accented initials:

| First letter | File |
|---|---|
| Ä | `lod-Ae.json` |
| É | `lod-Eacute.json` |
| Ë | `lod-Euml.json` |
| Ö | `lod-Oe.json` |
| Ü | `lod-Ue.json` |
| other / non-alpha | `lod-other.json` |

Search the array for the entry whose `lemma` matches. `verify.py word <lemma>` does this.

### Entry structure

Core fields (absent optional fields are omitted, not null):

```json
{
  "id":      "KOMMEN1",
  "lemma":   "kommen",
  "lemma_nrule": "komme",         // OPTIONAL: LOD's own N-rule (dropped -n) form
  "ipa":     "kˈomən",            // OPTIONAL
  "pos":     "VRB",               // SUBST | VRB | ADJ | ADV | NP | NB | PRON | PREP | CONJ | INTERJ | ART | …
  "pos_all": ["ADJ","ADV"],       // OPTIONAL: all POS when an entry has more than one
  "gender":  null,                // "M" | "F" | "N" | "MF" | "MN" | "FN" — nouns only
  "plural":  null,                // nouns only
  "plural_nrule": "Ae",           // OPTIONAL: N-rule form of the plural
  "en":      ["to come"],         // English, first sense (convenience copy)
  "example": "kenns du de Mann, deen do kënnt?",  // first LOD example (convenience copy)
  "aux":     "SINN",              // "HUNN" | "SINN" — verbs only
  "pp":      "komm",              // past participle — verbs only
  "pp_nrule": "…",                // OPTIONAL
  "sep":     true,                // OPTIONAL: separable verb
  "gram":    ["intransitiv"],     // OPTIONAL: transitiv / intransitiv / reflexiv / mam Dativ / …
  "conj": { "p1": "kommen", "p2": "kënns", "p3": "kënnt",
            "p4": "kommen", "p5": "kommt", "p6": "kommen" }   // present; p1=ech … p6=si
}
```

Rich fields:

```json
{
  "senses": [ { "n": 1, "en": ["to come"], "en_note": "to approach",
                "phrase": "…",            // OPTIONAL: idiom this sense belongs to
                "register": ["EGS"],      // OPTIONAL: EGS FAM VULG PEJ VEREELZT GEHUEW NEOL KANNERSPROOCH IRON
                "gram": ["transitiv"], "note": "kee Pluriel", "plural": "…",
                "examples": [ { "t": "ech kommen haut mam Auto op d'Aarbecht" },
                              { "t": "…", "reg": "EGS", "gloss": "LOD's plain-Luxembourgish paraphrase" } ] } ],
  "tenses": { "pastSimple": {}, "presentPerfect": {}, "pastPerfect": {},
              "cond_presentSimple": {}, "cond_presentPerfect": {}, "cond_pastPerfect": {},
              "imperative": { "p2": "komm!", "p5": "kommt!" } },
  "adj": { "positive": "schéin", "comparative": "méi schéin", "superlative": "am schéinsten",
           "decl": { "positive": { "m": ["schéinen","schéinen","schéinen","schéinen"],
                                   "f": ["schéin","schéin","schéiner","schéiner"],
                                   "n": ["schéint","schéint","schéinen","schéinen"],
                                   "pl": ["schéin","schéin","schéinen","schéiner"] } } },
  "syn": [ { "from": "kommen", "to": ["geroden"], "reg": "EGS" } ],
  "see": [ { "id": "UKOMMEN1", "lemma": "ukommen" } ]
}
```

Declension arrays are ordered [nominative, accusative, dative, genitive].
`tenses.cond_presentPerfect` is LOD's label for the periphrastic *géif/géing* conditional.
The `_nrule` fields are LOD's **own attested** N-rule variants — check them before falling
back to the mechanical rule.

**Multi-sense entries:** `en` holds the first sense only; `senses[]` holds all of them. When
glossing a word, show the first sense and name the others rather than merging them.

**Proper names:** LOD covers places (*Lëtzebuerg*, LETZEBUERG1), not people. Do not correct
a personal name's spelling and label it LOD-verified.

## N-rule (Eifeler Regel)

A final `-n` or `-nn` is **kept** before **n, d, t, z, h, a, e, i, o, u** (mnemonic:
UNITED ZOAH) and **dropped** before every other consonant. Accented vowels count as their
base letter. Five exceptions: proper nouns are never altered; the `-n` is kept before
punctuation; `-nn` drops or keeps as a pair; a stem-final `-n` (*Persoun*, *Frënn*, the
feminine `-in` suffix) never drops — LOD marks droppable forms with a `_nrule` sibling; and
an over-applied drop (*ech gi net* for *ech ginn net*) is an error that checking only
`-n`-final words cannot see.

**Mandatory mechanical check before any N-rule call:** identify the first letter of the
following word, spell out U-N-I-T-E-D-Z-O-A-H, and test membership letter by letter. Do not
paraphrase the keep-list from memory. `verify.py nrule` and `verify.py text` do this and
apply the exceptions from LOD data. Full treatment: `references/n-rule.md`.

## Articles

Derive from the noun's LOD-attested gender, then apply the N-rule to the article–noun
boundary.

| Gender | Nom / Acc | Dative |
|---|---|---|
| Masculine | de(n) | dem |
| Feminine | d' | der |
| Neuter | d' | dem |
| Plural | d' | den |

| Indefinite | Nom / Acc | Dative |
|---|---|---|
| Masculine | e(n) | engem |
| Feminine | eng | enger |
| Neuter | e(n) | engem |

**Never generate from a remembered German-shaped paradigm.** `dën` is not an article; `dat`
and `déi` are demonstratives, not default articles; `der` is the **feminine dative** only
(DER4) and never marks masculine. `verify.py article <lemma>` derives the form from LOD.
Full paradigms, accented, negative and possessive articles, fused prepositional forms:
`references/articles.md`.

## Word order

The only mechanical evidence for syntax is the example corpus. Before stating or correcting
a word-order, constituency, expletive or coordination claim, run `verify.py order` with both
competing orders. Memory holds on lexis and fails on syntax; the corpus check exists for that
gap. Two findings it settles, for illustration:

- Time-of-day precedes frequency (*owes dacks*, *moies meeschtens*): 7:1 in LOD.
- Impersonal *een* follows a filled first position, usually expletive *et* (*et muss een…*):
  25 sentence-initial attestations of *et muss een*, none of *een muss*.

## Verification discipline

Run the second pass over anything a reader will keep, copy forward or study from — including
corrections delivered in chat, and over the corrected sentences themselves, not only the
originals. Run it before marking anyone's answer wrong on gender, plural, article, N-rule or
word-order grounds, and whenever tempted to flag a word as cross-language contamination
(confirm it is absent from LOD first, and even then downgrade to UNVERIFIED).

What the check does **not** cover: meaning, register, pedagogical fit. Those remain the
model's responsibility. The mechanical pass confirms lexical existence, gender and plural,
N-rule application and corpus attestation — nothing more, and that is the point.

## Refreshing the data

Download the current LOD open data from https://data.public.lu/ (dataset: *Lëtzebuerger
Online Dictionnaire (LOD) – Linguistesch Daten*; the articles file and the tables file),
then:

```
python3 scripts/build_lod_json.py --art <lod-art.xml> --tab <lod-tab.xml> --out references/lod
```

The forms cache under `~/.cache/luxembourgish-lod/` is keyed by the data's modification
time and rebuilds itself.
