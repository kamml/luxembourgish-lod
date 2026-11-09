# luxembourgish-lod

Deterministic, dictionary-backed verification of Luxembourgish (Lëtzebuergesch) text —
built for checking what a language model produces, usable by anyone who needs a mechanical
answer to "is this word, form, article or word order actually attested?"

Large language models write fluent Luxembourgish that is often wrong, and with a few hundred
thousand speakers there is rarely a corpus large enough to correct them or a reader who can.
This package does not try to make the model better. It makes the check independent of the
model: open the LOD data and compare.

## What you get

- **An offline copy of LOD** — the *Lëtzebuerger Online Dictionnaire* open data (33,737
  entries) as per-letter JSON: all senses, all example sentences, full verb paradigms,
  adjective declension, IPA, register labels, synonyms, and LOD's own N-rule variant forms.
- **A 58,375-sentence example corpus** drawn from those entries — the only mechanical
  evidence available for Luxembourgish syntax.
- **`verify.py`** — a command-line checker (also importable) for lexical existence, gender
  and plural, conjugation, N-rule (Eifeler Regel) application, article derivation, and
  word-order / phrase attestation. Standard library only.
- **A skill file** (`SKILL.md`) so an AI assistant that supports skills applies the check
  before presenting Luxembourgish.
- **Reference notes** on the N-rule and the article system, every example quoted from LOD.

## Install

```
git clone https://github.com/kamml/luxembourgish-lod
cd luxembourgish-lod
python3 scripts/verify.py word Buch
```

Or, for the `lod-verify` command and the importable module (editable install, so the data stays in the checkout):

```
pip install -e .
lod-verify word Buch
```

Python 3.8 or later. The first run builds an index of every attested surface form (a few
seconds) and caches it under `~/.cache/luxembourgish-lod/`.

## Usage

```
$ lod-verify word Buch
✅ VERIFIED  'Buch' found in LOD [BUCH1] pos=SUBST gender=N plural=Bicher
   ·         en: book
   ·         ex: …

$ lod-verify article Mann
✅ VERIFIED  de Mann   (M nom: base 'den', next letter 'M' not in UNITED ZOAH → drop)  [gender from LOD MANN1]
✅ VERIFIED  de Mann   (M acc: …)
✅ VERIFIED  dem Mann  (M dat: 'dem' (no N-rule; does not end in -n))

$ lod-verify text "Ech gi net gär an d'Schoul."
   ·         possible OVER-APPLIED drop: 'gi' | 'net' — 'ginn' is attested (ginn [GINN1]) and
             'net' starts with a UNITED ZOAH letter, so the -n should probably be KEPT.
   ·         N-rule boundary: 'an' | 'd'Schoul.' → keep (next letter 'd' in UNITED ZOAH → keep)
✅ VERIFIED  'gi' is the N-rule form of 'ginn' in LOD [GINN1]
✅ VERIFIED  'Schoul' in LOD [SCHOUL1] (SUBST)

$ lod-verify check Buch --gender M
   ·         LOD entry BUCH1: pos=SUBST gender=N plural=Bicher
❌ WRONG     gender: generated 'M' but LOD says 'N' [BUCH1]

$ lod-verify order "(owes|moies|mëttes) (dacks|ëmmer|meeschtens)" \
                   "(dacks|ëmmer|meeschtens) (owes|moies|mëttes)"
   ·         A '(owes|moies|mëttes) (dacks|ëmmer|meeschtens)' -> 7
   ·         B '(dacks|ëmmer|meeschtens) (owes|moies|mëttes)' -> 1
✅ VERIFIED  '(owes|moies|mëttes) (dacks|ëmmer|meeschtens)' dominates 7:1 — prefer it; …

$ lod-verify phrase "^ et muss een"
✅ VERIFIED  '^ et muss een' attested 25x in LOD examples
```

Subcommands: `word`, `article`, `nrule`, `text`, `order`, `phrase`, `check`, `tsv`.
`lod-verify --help` lists them; `SKILL.md` documents the pattern syntax and the verdicts.
Exit status is 1 when any line is ❌ WRONG, so it works in a script or a CI step.

From Python:

```python
from luxembourgish_lod import verify
verify.lookup("Buch")["gender"]        # 'N'
verify.lookup_form("Bicher")           # ('Buch', 'BUCH1', 'plural of')
verify.nrule_keep("Mann")              # (False, "next letter 'M' not in UNITED ZOAH → drop")
verify.corpus_hits("^ et muss een")    # [(entry_id, sentence), …]
```

## What it will not do

- **Compose Luxembourgish.** It quotes and checks; it never generates.
- **Judge meaning, register or style.** It confirms that a form exists and that a pattern is
  attested — nothing more.
- **Call an absent word wrong.** The snapshot lags the live dictionary. Absence is reported
  as UNVERIFIED with a pointer to [lod.lu](https://lod.lu); WRONG is reserved for a claim
  that contradicts what LOD records.
- **Decide syntax on its own.** The corpus is a sample. An unattested order is "inferred",
  not "wrong"; two attested orders are variation, not an error.

## Data and licensing

The dictionary data in `references/lod/` is derived from the
[Lëtzebuerger Online Dictionnaire (LOD) – Linguistesch Daten](https://data.public.lu/en/datasets/6407416d041911a8915b1071)
published by the Zenter fir d'Lëtzebuerger Sprooch under
[Creative Commons Zero (CC0)](https://creativecommons.org/publicdomain/zero/1.0/).
`scripts/build_lod_json.py` performs the extraction (English and Luxembourgish content only;
German, French and Portuguese glosses are dropped). To refresh, download the current
articles and tables XML from data.public.lu and run:

```
python3 scripts/build_lod_json.py --art <lod-art.xml> --tab <lod-tab.xml> --out references/lod
```

Snapshot in this repository: LOD open data as of July 2026.

Grammar references cite the *Grammaire de la langue luxembourgeoise* (Zenter fir
d'Lëtzebuerger Sprooch, 2020) by page.

The code and documentation in this repository are released under the MIT License (see
`LICENSE`).

## Background

This grew out of studying for Luxembourg's Sproochentest. The study itself ran on lessons,
tutors and textbooks; an AI assistant was one tool alongside them, for drills and vocabulary
work. Its errors turned out to be confident, plausible and unflagged — exactly the kind a
learner has no way to catch. The verification architecture here is what fixed that: assume
the model is wrong and make it prove otherwise against the dictionary, every time.
