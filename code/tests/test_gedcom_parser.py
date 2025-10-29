"""Tests pour le parser GEDCOM (Issue #21)."""

from __future__ import annotations

from datetime import date as date_type
from pathlib import Path

from geneweb.domain.models import Sexe
from geneweb.io.gedcom import load_gedcom, parse_gedcom_minimal


def test_parse_gedcom_minimal_indi_basic() -> None:
    """Test parsing INDI de base avec NAME et SEX."""
    gedcom = """
0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean/DUPONT/
1 SEX M
0 TRLR
"""
    individus, familles = parse_gedcom_minimal(gedcom)

    assert len(individus) == 1
    assert len(familles) == 0

    indi = individus[0]
    assert indi.id == "@I1@"
    assert indi.prenom == "Jean"
    assert indi.nom == "DUPONT"
    assert indi.sexe == Sexe.M


def test_parse_gedcom_minimal_indi_birt_deat() -> None:
    """Test parsing INDI avec BIRT et DEAT."""
    gedcom = """
0 HEAD
0 @I1@ INDI
1 NAME John/DOE/
1 SEX M
1 BIRT
2 DATE 1990-01-02
2 PLAC Paris, France
1 DEAT
2 DATE 2050-12-31
2 PLAC Lyon, France
0 TRLR
"""
    individus, _ = parse_gedcom_minimal(gedcom)

    assert len(individus) == 1
    indi = individus[0]
    assert indi.date_naissance == date_type(1990, 1, 2)
    assert indi.lieu_naissance == "Paris, France"
    assert indi.date_deces == date_type(2050, 12, 31)
    assert indi.lieu_deces == "Lyon, France"


def test_parse_gedcom_minimal_fam() -> None:
    """Test parsing FAM avec HUSB/WIFE/CHIL."""
    gedcom = """
0 HEAD
0 @I1@ INDI
1 NAME Pierre/DUPONT/
1 SEX M
0 @I2@ INDI
1 NAME Marie/MARTIN/
1 SEX F
0 @I3@ INDI
1 NAME Jean/DUPONT/
1 SEX M
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
0 TRLR
"""
    individus, familles = parse_gedcom_minimal(gedcom)

    assert len(individus) == 3
    assert len(familles) == 1

    fam = familles[0]
    assert fam.id == "@F1@"
    assert fam.pere_id == "@I1@"
    assert fam.mere_id == "@I2@"
    assert "@I3@" in fam.enfants_ids


def test_parse_gedcom_minimal_multiple_indi() -> None:
    """Test parsing de plusieurs individus."""
    gedcom = """
0 HEAD
0 @I1@ INDI
1 NAME Alice/ONE/
1 SEX F
0 @I2@ INDI
1 NAME Bob/TWO/
1 SEX M
0 @I3@ INDI
1 NAME Charlie/THREE/
1 SEX M
0 TRLR
"""
    individus, _ = parse_gedcom_minimal(gedcom)

    assert len(individus) == 3
    assert individus[0].prenom == "Alice"
    assert individus[1].prenom == "Bob"
    assert individus[2].prenom == "Charlie"


def test_load_gedcom_file(tmp_path: Path) -> None:
    """Test chargement depuis fichier."""
    gedcom_file = tmp_path / "test.ged"
    gedcom_content = """
0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Test/LOAD/
1 SEX F
0 TRLR
"""
    gedcom_file.write_text(gedcom_content, encoding="utf-8")

    individus, familles = load_gedcom(gedcom_file)

    assert len(individus) == 1
    assert individus[0].prenom == "Test"
    assert individus[0].nom == "LOAD"
    assert len(familles) == 0

