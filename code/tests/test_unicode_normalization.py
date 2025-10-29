from __future__ import annotations

import unicodedata

from datetime import date as date_type

from geneweb.domain.models import Individu, Sexe, Source
from geneweb.io.gedcom import serialize_gedcom_minimal


def _norm(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def test_unicode_name_nfc_and_accents() -> None:
    # "Elise" avec E accent aigu en forme décomposée, et apostrophe
    prenom_decomposed = "E\u0301lise"  # É en NFD
    nom = "D'Hôtel"
    i = Individu(id="I1", nom=nom, prenom=prenom_decomposed, sexe=Sexe.F)
    content = serialize_gedcom_minimal([i])
    lines = _norm(content)

    indi_start = lines.index("0 @I1@ INDI")
    indi_block = lines[indi_start : indi_start + 5]

    # Après normalisation NFC, la sortie doit contenir É (composée)
    expected_name = f"1 NAME {unicodedata.normalize('NFC', prenom_decomposed)}/{unicodedata.normalize('NFC', nom)}/"
    assert expected_name in indi_block


def test_unicode_places_and_notes_and_sources() -> None:
    # Lieu avec accents, emoji; note contenant des retours à la ligne à nettoyer
    place = "Łódź – 😀"
    note = "Ligne1\nLigne2\tTab"
    source = Source(id="S1", titre="Źródło Étude", auteur="François")
    i = Individu(
        id="I1",
        nom="José",
        prenom="Álvaro",
        sexe=Sexe.M,
        lieu_naissance=place,
        note=note,
        sources=["S1"],
        date_naissance=date_type(2000, 1, 1),
    )

    content = serialize_gedcom_minimal([i], sources=[source])
    lines = _norm(content)

    # Vérifier PLAC normalisé et présent
    i_start = lines.index("0 @I1@ INDI")
    sub = lines[i_start : i_start + 20]
    assert "2 PLAC Łódź – 😀" in sub

    # NOTE doit être présente et sans CR/LF/TAB bruts (remplacés par espaces)
    joined = " ".join(sub)
    assert "1 NOTE" in joined
    assert "Ligne1 Ligne2 Tab" in joined

    # Source sérialisée avec accents et NFC
    assert "0 @S1@ SOUR" in lines
    assert "1 TITL Źródło Étude" in lines
    assert "1 AUTH François" in lines


