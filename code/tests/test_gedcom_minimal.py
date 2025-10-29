from __future__ import annotations

from datetime import date as date_type

from geneweb.domain.models import Famille, Individu, Sexe, Source
from geneweb.io.gedcom import serialize_gedcom_minimal


def _norm(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def test_gedcom_minimal_head_and_trailer() -> None:
    content = serialize_gedcom_minimal([])
    lines = _norm(content)
    assert lines[0] == "0 HEAD"
    assert any(line.startswith("1 SOUR ") for line in lines)
    assert any(line.startswith("1 CHAR ") for line in lines)
    assert any(line.startswith("1 SUBM") for line in lines)
    assert lines[-1] == "0 TRLR"


def test_gedcom_minimal_one_individu_name_and_sex() -> None:
    jean = Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M)
    content = serialize_gedcom_minimal([jean])
    lines = _norm(content)

    # Trouver le bloc INDI
    indi_start = lines.index("0 @I1@ INDI")
    indi_block = lines[indi_start : indi_start + 3]

    assert "1 NAME Jean/DUPONT/" in indi_block
    assert "1 SEX M" in indi_block


def test_gedcom_minimal_missing_fields_defaults() -> None:
    unknown = Individu(id="I002")
    content = serialize_gedcom_minimal([unknown])
    lines = _norm(content)
    indi_start = lines.index("0 @I1@ INDI")
    indi_block = lines[indi_start : indi_start + 2]

    # NAME doit exister même sans prénom/nom, avec slashes
    assert "1 NAME /" in indi_block[1]


def test_gedcom_minimal_birt_deat_date_place() -> None:
    p = Individu(
        id="I010",
        nom="DOE",
        prenom="John",
        sexe=Sexe.M,
        date_naissance=date_type(1990, 1, 2),
        lieu_naissance="Paris, France",
        date_deces=date_type(2050, 12, 31),
        lieu_deces="Lyon, France",
    )
    content = serialize_gedcom_minimal([p])
    lines = _norm(content)

    i = lines.index("0 @I1@ INDI")
    # Cherche les blocs BIRT et DEAT
    sub = lines[i : i + 20]
    assert "1 BIRT" in sub
    assert "2 DATE 1990-01-02" in sub
    assert "2 PLAC Paris, France" in sub
    assert "1 DEAT" in sub
    assert "2 DATE 2050-12-31" in sub
    assert "2 PLAC Lyon, France" in sub


def test_gedcom_minimal_famille_husb_wife_chil() -> None:
    """Test de sérialisation FAM avec HUSB/WIFE/CHIL (Issue #16)."""
    pere = Individu(id="I001", nom="DUPONT", prenom="Pierre", sexe=Sexe.M)
    mere = Individu(id="I002", nom="MARTIN", prenom="Marie", sexe=Sexe.F)
    enfant1 = Individu(id="I003", nom="DUPONT", prenom="Jean", sexe=Sexe.M)
    enfant2 = Individu(id="I004", nom="DUPONT", prenom="Sophie", sexe=Sexe.F)

    famille = Famille(
        id="F001",
        pere_id="I001",
        mere_id="I002",
        enfants_ids=["I003", "I004"],
    )

    content = serialize_gedcom_minimal(
        [pere, mere, enfant1, enfant2], familles=[famille]
    )
    lines = _norm(content)

    # Vérifier que les individus sont présents
    assert "0 @I1@ INDI" in lines  # pere
    assert "0 @I2@ INDI" in lines  # mere
    assert "0 @I3@ INDI" in lines  # enfant1
    assert "0 @I4@ INDI" in lines  # enfant2

    # Vérifier la structure FAM
    fam_start = lines.index("0 @F1@ FAM")
    fam_block = lines[fam_start : fam_start + 10]

    assert "1 HUSB @I1@" in fam_block  # père
    assert "1 WIFE @I2@" in fam_block  # mère
    assert "1 CHIL @I3@" in fam_block  # enfant1
    assert "1 CHIL @I4@" in fam_block  # enfant2


def test_gedcom_minimal_famille_partielle() -> None:
    """Test avec famille incomplète (père ou mère manquant, pas d'enfants)."""
    pere = Individu(id="I001", nom="DUPONT", prenom="Pierre", sexe=Sexe.M)
    famille = Famille(id="F001", pere_id="I001", mere_id=None, enfants_ids=[])

    content = serialize_gedcom_minimal([pere], familles=[famille])
    lines = _norm(content)

    fam_start = lines.index("0 @F1@ FAM")
    fam_block = lines[fam_start : fam_start + 5]

    assert "1 HUSB @I1@" in fam_block
    assert "1 WIFE" not in " ".join(fam_block)  # Pas de WIFE si None
    assert "1 CHIL" not in " ".join(fam_block)  # Pas d'enfants


def test_gedcom_minimal_note_individu() -> None:
    """Test de sérialisation NOTE pour un individu (Issue #17)."""
    individu = Individu(
        id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, note="Note simple"
    )
    content = serialize_gedcom_minimal([individu])
    lines = _norm(content)

    indi_start = lines.index("0 @I1@ INDI")
    indi_block = lines[indi_start : indi_start + 10]
    assert "1 NOTE Note simple" in indi_block


def test_gedcom_minimal_note_longue() -> None:
    """Test de sérialisation NOTE longue avec continuation CONT (Issue #17)."""
    note_longue = "A" * 300  # Plus de 255 caractères
    individu = Individu(id="I001", nom="DUPONT", prenom="Jean", note=note_longue)
    content = serialize_gedcom_minimal([individu])
    lines = _norm(content)

    indi_start = lines.index("0 @I1@ INDI")
    # Chercher NOTE et au moins un CONT
    indi_section = " ".join(lines[indi_start : indi_start + 20])
    assert "1 NOTE" in indi_section
    assert "2 CONT" in indi_section


def test_gedcom_minimal_sources_individu() -> None:
    """Test de sérialisation SOUR pour un individu (Issue #17)."""
    source1 = Source(id="S001", titre="Acte de naissance", auteur="Mairie")
    source2 = Source(id="S002", titre="Recensement", auteur="INSEE")
    individu = Individu(
        id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, sources=["S001", "S002"]
    )

    content = serialize_gedcom_minimal([individu], sources=[source1, source2])
    lines = _norm(content)

    # Vérifier que les sources sont sérialisées comme objets SOUR
    assert "0 @S1@ SOUR" in lines
    assert "1 TITL Acte de naissance" in lines
    assert "0 @S2@ SOUR" in lines
    assert "1 TITL Recensement" in lines

    # Vérifier que l'individu référence les sources
    indi_start = lines.index("0 @I1@ INDI")
    indi_block = lines[indi_start : indi_start + 15]
    assert "1 SOUR @S1@" in indi_block
    assert "1 SOUR @S2@" in indi_block


def test_gedcom_minimal_note_famille() -> None:
    """Test de sérialisation NOTE pour une famille (Issue #17)."""
    famille = Famille(id="F001", pere_id="I001", mere_id="I002", note="Note famille")
    content = serialize_gedcom_minimal([], familles=[famille])
    lines = _norm(content)

    fam_start = lines.index("0 @F1@ FAM")
    fam_block = lines[fam_start : fam_start + 10]
    assert "1 NOTE Note famille" in fam_block


def test_gedcom_minimal_source_complete() -> None:
    """Test de sérialisation complète d'une source avec tous les champs (Issue #17)."""
    source = Source(
        id="S001",
        titre="Livre généalogique",
        auteur="Auteur Test",
        date_publication=date_type(2020, 1, 1),
        url="https://example.com",
        note="Note sur la source",
    )

    content = serialize_gedcom_minimal([], sources=[source])
    lines = _norm(content)

    assert "0 @S1@ SOUR" in lines
    sour_idx = lines.index("0 @S1@ SOUR")
    sour_block = lines[sour_idx : sour_idx + 10]

    assert "1 TITL Livre généalogique" in sour_block
    assert "1 AUTH Auteur Test" in sour_block
    assert "1 PUBL" in sour_block
    assert "2 DATE 2020-01-01" in sour_block
    assert "1 URL https://example.com" in sour_block
    assert "1 NOTE Note sur la source" in sour_block

