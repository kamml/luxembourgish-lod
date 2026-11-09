# N-Rule (Eifeler Regel)

**Sources:**
- LOD (Lëtzebuerger Online Dictionnaire) — the `lemma_nrule`, `plural_nrule` and `pp_nrule`
  fields record LOD's own attested dropped forms, and the example corpus attests the rule in
  running text. Every example sentence below is quoted verbatim from LOD, with its entry id.
- *Grammaire de la langue luxembourgeoise* (Zenter fir d'Lëtzebuerger Sprooch, 2020) and the
  official orthography (*D'Lëtzebuerger Orthografie*, ZLS) describe the rule normatively.
  [Page references to be confirmed against the printed editions before publication.]

---

## What it is

The N-rule (Luxembourgish *Eifeler Regel*) governs whether a word-final `-n` (or `-nn`) is
kept or dropped, depending on the sound that follows. Because Luxembourgish orthography is
phonetic, the rule applies to both pronunciation **and** spelling: if the `n` is dropped in
speech, it is dropped in writing.

---

## The general rule

> Final `-n` is **kept** before **n, d, t, z, h** and the vowels **a, e, i, o, u**.
> Before any other consonant it is **dropped**.

**Mnemonic:** **UNITED ZOAH** — the ten letters that keep the `n`.

Accented vowels count as their base letter: `é è ê ë` → e, `ä à â` → a, `ï î` → i,
`ö ô` → o, `ü û` → u. The `-n` is therefore kept before all of them:
*den éischte Band vum Lexikon ass 1956 erauskomm* (LOD), *Froen an Äntwerten* (LOD). The ten
letters are a mnemonic for sounds, not a literal character set.

---

## Mechanical check protocol

The keep-list must be checked letter by letter, **not paraphrased from memory**. The dominant
failure mode in practice is confidently reciting a *wrong version* of the rule — claiming `z`
is not in UNITED ZOAH when it is, or that `n` triggers a drop when it triggers a keep.

1. Identify the **first letter of the next word**.
2. Spell out the keep-list: **U, N, I, T, E, D, Z, O, A, H** (fold accents first).
3. Is the first letter in that set? Yes → `-n` **kept**. No → `-n` **dropped**.
4. Check the exceptions below.

`scripts/verify.py nrule "<word> <nextword>"` performs exactly this check;
`scripts/verify.py text "<sentence>"` runs it over every boundary in a sentence and also
checks each `-n` form against LOD's attested `_nrule` data.

**Failure modes this protocol prevents:**

- *"Negation drops -n."* There is no such rule. *net* starts with `n`, which keeps the `-n`:
  *ech sinn net mat him bestuet* (BESTUET1).
- *"Z drops."* `z` is in UNITED ZOAH: *den Zuch* (58 LOD attestations), never *de Zuch*.
- *Pattern autopilot.* After several boundaries that dropped the `-n`, a vowel-initial next
  word is easy to miss. Check the actual next letter every time.
- *Confirming without checking.* Confirming an existing form is not exempt from the check.

---

## Exceptions

### 1. Proper nouns are never modified

The rule applies to common words, not to names of people, places or organisations. A name
keeps its `-n` whatever follows.

### 2. Before punctuation, keep the `n`

Commas, full stops, question marks and the like keep the `-n`, regardless of what follows
the punctuation: *ech si frou, datt dir esou séier konnt kommen* (DATT1) — *kommen* keeps
its `n` at the end of the sentence.

### 3. Double `-nn` behaves like single `-n`

Both n's are kept before UNITED ZOAH letters or punctuation, and both are dropped before any
other consonant: *ech sinn net* (36 attestations) vs *ech si frou* (6), *ech hunn alles
duerchsicht* (DUERCHSICHEN1) vs *ech hu vill exotesch Fësch* (AQUARIUM1).

### 4. A stem-final `-n` never drops

The rule applies to *inflectional* `-n`, not to an `-n` that is part of the word itself.
*Persoun*, *Frënn* and the feminine **`-in`** suffix (*Informatikerin*, *Cheffin*) keep
their `-n` before any letter.

**The mechanical test:** LOD records a dropped variant in `lemma_nrule` / `plural_nrule` /
`pp_nrule`. If a form is in LOD and has **no** matching `_nrule` sibling, its `-n` is stem
and does not drop. PERSOUN1 carries `plural_nrule: "Persoune"` but no `lemma_nrule`, so
*Persounen* → *Persoune* while *Persoun* never changes. `verify.py text` applies this test.

### 5. An over-applied drop is an error too

Checking only words that still end in `-n` cannot catch an `-n` that was wrongly removed.
*ech gi net gär* is wrong — the LOD corpus has *ginn net* 33 times and *gi net* never —
yet nothing in it ends in `-n`. When confirming a dropped form, check that the next word
does **not** begin with a UNITED ZOAH letter. `verify.py text` flags these as advisories.

---

## Worked examples (all quoted from LOD)

| Keep the `n` (UNITED ZOAH letter follows) | Drop the `n` (other consonant follows) |
|---|---|
| *ech sinn net mat him bestuet* (BESTUET1) — n before n | *ech si frou, datt dir…* (DATT1) — nn before f |
| *d'Artikele sinn immens!* (ABONNENTIN1) — n before i | *ech hu vill exotesch Fësch* (AQUARIUM1) — nn before v |
| *ech hunn alles duerchsicht* (DUERCHSICHEN1) — nn before a | *ënner den Arkade si kleng Geschäfter opgaangen* (ARKAD1) — nn before k |
| *fir den Zuch* (ABONNEMENT1) — n before Z | *de Mann gouf…* (AGGRESSEIEREN1) — n before M |
| *ënner den Arkade* (ARKAD1) — n before A | *schaffe mir mat engem externen Déngschtleeschter* (DENGSCHTLEESCHTER1) — n before m |
| | *dat ee mat de Kanner ka sangen* (ADVENTSLIDD1) — n before K, nn before s |

---

## Quick decision checklist

For every word ending in `-n` or `-nn`:

1. Look at the next word's first letter (fold accents).
2. In UNITED ZOAH? → **keep**.
3. Any other consonant? → **drop**.
4. Overrides, applied before 2–3: proper noun → keep; punctuation or end of utterance →
   keep; stem-final `-n` (no `_nrule` sibling in LOD) → keep.
5. Then check the opposite direction: for every word that does **not** end in `-n`, would
   adding one give an attested form, and does the next word start with a UNITED ZOAH letter?
   If so the `-n` should have been kept.

---

## Full letter inventory

| Action | Letters |
|---|---|
| **Keep `n` before** | n, d, t, z, h, a, e, i, o, u — plus their accented forms é è ê ë ä à â ï î ö ô ü û |
| **Drop `n` before** | b, c, f, g, j, k, l, m, p, q, r, s, v, w, x, y |

`q`, `x`, `y` are rare word-initial letters in Luxembourgish, appearing mostly in loanwords
(*Quetsch*) and proper nouns (*Xavier*, *Yves*). Since the rule does not apply before proper
nouns, the drop applies to q/x/y only when they begin common-noun loanwords.

---

## What the rule covers

Articles (*den* ↔ *de*, *en* ↔ *e*), pronouns (*en* ↔ *e*), plural nouns in `-en`, verb forms
in `-en` (infinitive, 1st/3rd person plural), prepositions, conjunctions, adverbs, numerals.
