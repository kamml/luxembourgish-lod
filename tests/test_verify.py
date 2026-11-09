"""Smoke tests for luxembourgish_lod.verify against the bundled LOD data.
Run: python3 -m pytest tests/   (or python3 tests/test_verify.py)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from luxembourgish_lod import verify  # noqa: E402


def test_lookup_noun():
    e = verify.lookup("Buch")
    assert e["id"] == "BUCH1" and e["gender"] == "N" and e["plural"] == "Bicher"


def test_lookup_missing_is_none():
    assert verify.lookup("Xqzzy") is None


def test_inflected_form_resolves_to_lemma():
    lemma, eid, kind = verify.lookup_form("Bicher")
    assert (lemma, eid, kind) == ("Buch", "BUCH1", "plural of")


def test_nrule_keep_set():
    assert verify.nrule_keep("Dag")[0] is True       # d keeps
    assert verify.nrule_keep("Mann")[0] is False     # m drops
    assert verify.nrule_keep("Zuch")[0] is True      # z keeps
    assert verify.nrule_keep("éischte")[0] is True   # accented vowel folds to e
    assert verify.nrule_keep(", an")[0] is True      # punctuation keeps


def test_article_derivation():
    assert verify.derive_article("M", "nom", "Mann")[0] == "de"
    assert verify.derive_article("M", "nom", "Dag")[0] == "den"
    assert verify.derive_article("F", "dat", "Fra")[0] == "der"
    assert verify.derive_article("N", "nom", "Buch")[0] == "d'"


def test_stem_final_n_does_not_drop():
    attested, _ = verify.has_attested_drop("Persoun")
    assert attested is False
    attested, _ = verify.has_attested_drop("Persounen")
    assert attested is True


def test_overapplied_drop_detected():
    hit = verify.check_overapplied_drop("gi", "net")
    assert hit is not None and hit[0] == "ginn"


def test_corpus_phrase_attested():
    assert len(verify.corpus_hits("ginn net")) >= 30
    assert verify.corpus_hits("^ een muss") == []


def test_corpus_order_dominance():
    a = verify.corpus_hits("(owes|moies|mëttes) (dacks|ëmmer|meeschtens)")
    b = verify.corpus_hits("(dacks|ëmmer|meeschtens) (owes|moies|mëttes)")
    assert len(a) > len(b)


def test_diacritic_insensitive_patterns():
    assert len(verify.corpus_hits("schein")) == len(verify.corpus_hits("schéin"))


if __name__ == "__main__":
    import inspect
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and inspect.isfunction(fn):
            try:
                fn(); print("ok  ", name)
            except AssertionError as ex:
                failures += 1; print("FAIL", name, ex)
    sys.exit(1 if failures else 0)
