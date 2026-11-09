# Article Declension — Full Reference

This file documents the Luxembourgish article system: definite, indefinite, accented
(demonstrative), negative, and possessive articles, plus fused prepositional forms.

**Sources:**
- *Grammaire De La Langue Luxembourgeoise* (Zenter fir d'Lëtzebuerger Sprooch, 2020),
  Chapter 5 "Le Groupe Nominal" — printed pages 67–88. Cite as `Grammaire pp. 67–88`.
- LOD entries for cross-checking every form. Each form below is annotated with the LOD
  entry ID where applicable.

**Cross-cutting rules** (verification discipline, the N-rule) live in `SKILL.md` and
`references/n-rule.md`. This file is the deep article-paradigm reference.

---

## Contents

1. Three-gender, four-case overview
2. Definite article (full paradigm)
3. Indefinite article (full paradigm)
4. Accented (demonstrative) article
5. Negative article
6. Possessive articles
7. Article absence
8. Fused prepositional forms
9. Preposition-case rules
10. The article system and the N-rule
11. Taxonomic note: LOD vs Grammaire

---

## 1. Three-gender, four-case overview

Luxembourgish nouns have three genders (Maskulin, Feminin, Neutrum) and three productive
cases (Nominative, Accusative, Dative). A vestigial Genitive survives only in fixed
expressions (e.g. *des Doudes*, *enges Daags*). Plural collapses to a single form across
all genders for the article system.

| Case | Function |
|---|---|
| Nominative | Subject / subject attribute |
| Accusative | Direct object (COD) |
| Dative | Indirect object (COI), most prepositions, attribution |

Nominative and accusative are **identical** for the article system. Dative is the only
case that distinguishes itself by form. (Grammaire p. 77: *"Les formes du nominatif et de
l'accusatif sont identiques."*)

---

## 2. Definite article (full paradigm)

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **de(n)** | **d'** | **d'** | **d'** |
| Dative | **dem** | **der** | **dem** | **den** |

**LOD cross-check (`✅ LOD-verified`):**
- `de(n)` → DE1 (PRON "you") for the N-dropped form is not separately catalogued; **DEN1** is the article entry, with the `n` dropped under the N-rule (`references/n-rule.md`).
- `dem` → **DEM1** (ART "the")
- `der` → **DER4** (ART "the")
- `den` (plural dative) → **DEN1** (same surface as masc nom/acc; context disambiguates)

**Worked examples (Grammaire p. 77):**

| Form | Example |
|---|---|
| Nom (Masc) | *Den Auto steet an der Garage.* |
| Acc (Masc) | *Hie stellt den Auto an d'Garage.* |
| Dat (Masc) | *Hie verkeeft dem Direkter en Auto.* |
| Dat (Fem) | *De Coiffer schneit der Fra d'Hoer.* |
| Dat (Plural) | *De Patron schreift den Elteren d'Rechnung.* |

**Note on the apostrophe in `d'`:** always use the typographic apostrophe **'** (U+2019),
never the straight apostrophe.

---

## 3. Indefinite article (full paradigm)

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **e(n)** | **eng** | **e(n)** | — *(no plural indefinite)* |
| Dative | **engem** | **enger** | **engem** | — |

**LOD cross-check (`✅ LOD-verified`):**
- `e(n)` → **EN2** (ART "a, an"); N-rule applied per `references/n-rule.md`
- `eng` → **ENG1** (ART "a, an")
- `engem` → **ENGEM1** (ART)
- `enger` → **ENGER1** (ART)

**Worked examples (Grammaire pp. 73–74):**

- Nom: *Hien huet en Auto.*
- Acc: *Si huet en Hond.*
- Dat: *De Léierbouf wäscht engem Kand de Kapp.*

**No plural indefinite.** Where English uses "some" or bare plurals, Luxembourgish uses no
article: *Si huet Kanner* ("She has children") vs. *Si huet keng Kanner* ("She has no
children"). See §5 and §7.

**Disambiguation from `een`/`eenen`:** these are the **adjective/pronoun** "one" (LOD
**EEN1** PRON, **EEN2** ADJ), not the indefinite article (LOD: `en` = ART EN2, `eng` = ART ENG1).

---

## 4. Accented (demonstrative) article

When emphasis or demonstration is needed, or when the noun is modified by an adjective,
the accented form is used. Functions as a demonstrative ("that, that one").

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **deen** | **déi** | **dat** | **déi** |
| Dative | **deem** | **dëer** / déer | **deem** | **deenen** |

**LOD cross-check (`✅ LOD-verified`):**
- `deen` → **DEEN3** (ART "the")
- `déi` → **DEI3** (ART "the")
- `dat` → **DAT3** (ART "the")
- `deem` → **DEEM3** (ART "the")
- `deenen` → **DEENEN3** (ART "the")
- The feminine accented dative (*dëer / déer*) is not catalogued as a separate LOD ART entry — it surfaces in context with the spelling shown in the Grammaire.

**Worked examples (Grammaire p. 74):**

- *Dee Mann huet en neien Auto.* — emphasis on "that man"
- *Dat déckt Buch huet vill Säiten.* — accented + adjective
- *Déi Kanner fuere mat.* — plural
- *Mat dëer Frabrauch keen Auto.* — feminine dative (Grammaire spelling varies)

**With an adjective, the accented form is mandatory.** *Den dicke Mann* is grammatical but
unmarked; *Deen dicke Mann* foregrounds the man. *Déi al Autoen* ("the old cars")
specifically uses the accented plural.

---

## 5. Negative article

Used to negate an indefinite noun phrase. Declines like the indefinite article.

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **kee(n)** | **keng** | **kee(n)** | **keng** |
| Dative | **kengem** | **kenger** | **kengem** | **kengen** |

**LOD cross-check:** `keen`, `keng`, `kengem`, `kengen`, `kenger` are all attested in LOD
(`KEEN1`, `KENG3`, `KENGEM1`, `KENGEN2`, `KENGER1`). LOD classifies them as PRON; the
Grammaire calls them "article négatif." See §11 for the taxonomic discrepancy.

**Worked examples (Grammaire p. 74):**

- *De Mann huet keen Auto.*
- *D'Kand huet keng Mëllech gedronk.*
- *Hie gëtt kengem Kand eng Kamell.*

---

## 6. Possessive articles

The possessive form depends on **both** the possessor (1sg, 2sg, 3sg-masc, 3sg-fem/pl,
1pl, 2pl-formal) **and** the gender/number/case of what's possessed. They decline like
the indefinite article.

### 1st person singular ("my")

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **mäi(n)** | **meng** | **mäi(n)** | **meng** |
| Dative | **mengem** | **menger** | **mengem** | **mengen** |

LOD: `mäin` (**MAIN1**), `meng` (**MENG1**), `mengem` (**MENGEM1**),
`mengen` (**MENGEN2**), `menger` (**MENGER1/2**).

### 2nd person singular ("your" — informal)

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **däi(n)** | **deng** | **däi(n)** | **deng** |
| Dative | **dengem** | **denger** | **dengem** | **dengen** |

LOD: `däin` (**DAIN1**), `deng` (**DENG2**), `dengem` (**DENGEM1**),
`dengen` (**DENGEN4**), `denger` (**DENGER1/2**).

### 3rd person singular masculine ("his") / and "its" referring to a masc/neut antecedent

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **säi(n)** | **seng** | **säi(n)** | **seng** |
| Dative | **sengem** | **senger** | **sengem** | **sengen** |

LOD: `säin` (**SAIN1**), `seng` (**SENG1**), `sengem` (**SENGEM1**),
`sengen` (**SENGEN1**), `senger` (**SENGER1/2**).

### 3rd person singular feminine / 3rd person plural ("her" / "their")

The same form is used for both "her" and "their" — context disambiguates.

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **hire(n)** | **hir** | **hiert** | **hir** |
| Dative | **hirem** | **hirer** | **hirem** | **hiren** |

LOD: `hir` (**HIR2/3**), `hiert` (**HIERT2** — neuter Nom/Acc), `hiren` (**HIREN1**),
`hirem` (**HIREM1**), `hirer` (**HIRER1/2**).

### 1st person plural ("our")

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **eise(n)** | **eis** | **eist** | **eis** |
| Dative | **eisem** | **eiser** | **eisem** | **eisen** |

LOD: `eis` (**EIS3** PRON "our, ours"), `eist` (**EIST1** — neuter Nom/Acc),
`eisen` (**EISEN3**), `eisem` (**EISEM1**), `eiser` (**EISER1/2**).

### 2nd person plural / formal ("your" — plural or polite)

| Case | Masc | Fem | Neut | Plural |
|---|---|---|---|---|
| Nom / Acc | **äre(n)** | **är** | **äert / är** | **är** |
| Dative | **ärem** | **ärer** | **ärem** | **ären** |

LOD: `är` (**AR2/AR3**), `ären` (**AREN1/2**), `ärem` (**AREM2/3**),
`ärer` (**ARER1-4**), `äert` (**AERT1/2** — neuter Nom/Acc form).

**Neuter Nom/Acc takes -t across the whole hir / eis / är family.** *hiert Kand*, *eist Kand*,
*äert Kand* — never bare *hir Kand* / *eis Kand*. This is systematic, not an *äert*-only quirk.
✅ LOD-verified: HIERT2 (*hiert Liewe war eng eenzeg Plo*), EIST1 (*eist Duerf läit matzen an de
Wéngerten*), AERT1 (*äert Haus huet eng schéi Fassad*); corpus counts 175 / 283 / 16 attestations
respectively, with no bare-form counterexample. The **mäi / däi / säi** family is unaffected —
there the neuter correctly patterns with the masculine (*mäi Kand*).

**Capitalization for politeness:** the formal *Är, Ären, Ärem, Ärer* are capitalized when
addressing someone politely (parallel to German *Sie*). LOD lists both lowercase and
capitalized forms (AR2 vs AR3, AREN1 vs AREN2, etc.).

**Worked examples (Grammaire pp. 86–87):**

- *Dat ass net mäi Mantel, dat ass säi Mantel.*
- *D'Mamm rifft hir Kanner fir z'iessen.*
- *D'Mamm schwätzt mat hire Kanner a mat hirem Mann.*  
  (Grammaire p. 86. *hire* drops its -n before **K**; the LOD corpus has 42 attestations of
  *hire* before a K-initial word and 0 of *hiren*.)
- *Dem Hond säi Pelz ass gelommen ginn.* (possessive construction with dative possessor)
- *Ech hu menge Kanner hir Bicher schonn all kaaft.*

---

## 7. Article absence

Three contexts where no article is used:

### Mass nouns / partitive

For a portion of an uncountable substance, no article. (Grammaire p. 74.)

- *Hien drénkt gär Wäin, si huet léiwer Béier.*
- *D'Meedche mécht Botter op d'Schmier.*

### Bare plurals

Plural indefinites have no positive article (only the negative *keng* exists for plurals).

- *Si huet Kanner.* ("She has children")
- *Si kaaft Äppel.* ("She buys apples")

### Country and place names (mostly)

Most country names appear without an article — see Grammaire p. 69 for the small list of
exceptions that take articles (*d'Belsch*, *d'Schwäiz*, *d'Tierkei*, *den Iran*, etc.).

---

## 8. Fused prepositional forms (Grammaire p. 79)

When certain prepositions combine with **the definite dative article** (`dem` / `der`),
they fuse into a single word. These are extremely common and worth memorizing as units.

### Preposition + `dem` (masc/neut dative)

| Preposition | + dem | Fused form |
|---|---|---|
| mat | mat dem | **mam** |
| an | an dem | **am** |
| no | no dem | **nom** |
| op | op dem | **um** |
| vun | vun dem | **vum** |
| un | un dem | **um** *(same surface as `op + dem` — context disambiguates)* |
| zu | zu dem | **zum** |
| bei | bei dem | **beim** |
| énnert | énnert dem | **énnerem** |
| widdert | widdert dem | **widderem** |
| iwwert | iwwert dem | **iwwerem** |
| virun | virun dem | **virum** |
| hannert | hannert dem | **hannerem** |

### Preposition + `der` (feminine dative)

Only `zu + der → zur` is regularly fused (Grammaire p. 79). Other prepositions keep the
two-word form: *mat der*, *bei der*, *vun der*, etc.

- *Komm zur Saach!*
- *Zur Zäit vum Keeser Augustus ...*

### When to use the fused form vs. the full form

Use the fused form by default in modern Luxembourgish. The unfused form (*mat dem*) is
strictly grammatical but feels archaic or emphatic. Generated content should use the
fused form unless a specific contrast or emphasis calls for the full form.

---

## 9. Preposition-case rules (Grammaire p. 78)

Three categories of prepositions:

### Accusative-only

Always followed by accusative (regardless of meaning):

> **fir, duerch, ouni, géint, ëm, bis, laanscht**

### Dative-only

Always followed by dative:

> **aus, mat, no, zënter, vun, zu, wéinst, bannent, trotz, virun** *(temporal)*

### Two-way (dative or accusative depending on meaning)

These prepositions take **accusative for direction/motion** ("wuer? wouhin?") and
**dative for location/state** ("wou?"):

> **an, op, un, iwwert, énnert, virun, hannert, téschent, niewent, widdert, bei, baussent**

**Example pair (Grammaire p. 79):**

- *Hie geet an de Gaart.* (accusative — direction)
- *Hie schafft am Gaart.* (dative + fused — location)

This direction-vs-location split is a high-frequency error source for learners.

---

## 10. The article system and the N-rule

The article system interacts heavily with the N-rule (see `references/n-rule.md`). Forms
ending in `-n` (or `-nn`) follow the UNITED ZOAH rule before the next word:

- **den** → *den Auto* (vowel: keep), *de Mann* (m: drop)
- **een** / **kee(n)** → *een Auto* (keep), *e Mann* (drop)
- **mäin** → *mäin Auto* (keep), *mäi Mann* (drop)
- **säin** → *säin Hond* (h: keep), *säi Bouf* (b: drop)
- **deen** → *deen Auto* (keep), *dee Mann* (drop)

For the dative forms in `-em`, `-en`, `-er`, the same rule applies:
- *dem Mann* but *dem Hond* (h is in UNITED ZOAH; dem keeps `-m`, but the trailing letter
  here is `m` not `n`, so this is a non-issue)
- *engem Mann*, *kengem Kand* — `m` is not affected by the N-rule

Proper nouns are always exempt (Grammaire convention + N-rule reference §Exceptions).

---

## 11. Taxonomic note: LOD vs Grammaire

LOD and the Grammaire classify some words differently:

| Word category | Grammaire calls it | LOD `pos` |
|---|---|---|
| Definite article | article défini | ART (`DEN1`, `DEM1`, `DER4`, etc.) |
| Indefinite article | article indéfini | ART (`EN2`, `ENG1`, `ENGEM1`, etc.) |
| Accented / demonstrative | article accentué | ART (`DEEN3`, `DEI3`, `DAT3`, `DEEM3`, `DEENEN3`) |
| **Negative article** | article négatif | **PRON** (`KEEN1`, `KENG3`, `KENGEM1`, etc.) |
| **Possessive article** | article possessif | **PRON** (`MAIN1`, `MENG1`, `MAI1`, `HIR2`, `EIS3`, `AR2`, etc.) |

For verification purposes:

- When LOD lists a possessive or negative form as `PRON`, treat the form as **LOD-verified**
  for the surface form, and use the Grammaire's article classification for the function.

---

## Cross-references

- `SKILL.md` § **Articles** — the quick-reference tables
- `SKILL.md` § **Looking up a word** — how the LOD entries cited above are looked up
- `references/n-rule.md` — full N-rule reference (heavily used with all `-n`-ending articles)
