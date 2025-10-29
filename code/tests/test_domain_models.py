"""Tests pour les modèles de domaine GeneWeb."""

from __future__ import annotations

from datetime import date

import pytest

from geneweb.domain.models import (
    Evenement,
    Famille,
    Individu,
    IndividuSchema,
    Sexe,
    Source,
    TypeEvenement,
)


def test_create_individu() -> None:
    """Test de création d'un individu."""
    individu = Individu(
        id="I001",
        nom="DUPONT",
        prenom="Jean",
        sexe=Sexe.M,
        date_naissance=date(1990, 1, 1),
        lieu_naissance="Paris, France",
    )

    assert individu.id == "I001"
    assert individu.nom == "DUPONT"
    assert individu.prenom == "Jean"
    assert individu.sexe == Sexe.M
    assert individu.date_naissance == date(1990, 1, 1)
    assert individu.lieu_naissance == "Paris, France"


def test_create_famille() -> None:
    """Test de création d'une famille."""
    famille = Famille(
        id="F001",
        pere_id="I001",
        mere_id="I002",
        enfants_ids=["I003", "I004"],
    )

    assert famille.id == "F001"
    assert famille.pere_id == "I001"
    assert famille.mere_id == "I002"
    assert len(famille.enfants_ids) == 2
    assert "I003" in famille.enfants_ids
    assert "I004" in famille.enfants_ids


def test_create_evenement() -> None:
    """Test de création d'un événement."""
    evenement = Evenement(
        id="E001",
        type=TypeEvenement.NAISSANCE,
        date=date(1990, 1, 1),
        lieu="Paris, France",
        personnes_ids=["I003"],
    )

    assert evenement.id == "E001"
    assert evenement.type == TypeEvenement.NAISSANCE
    assert evenement.date == date(1990, 1, 1)
    assert evenement.lieu == "Paris, France"
    assert "I003" in evenement.personnes_ids


def test_create_source() -> None:
    """Test de création d'une source."""
    source = Source(
        id="S001",
        titre="Acte de naissance",
        auteur="Mairie de Paris",
        date_publication=date(1990, 1, 2),
        fichier="acte_naissances_1990.pdf",
    )

    assert source.id == "S001"
    assert source.titre == "Acte de naissance"
    assert source.auteur == "Mairie de Paris"
    assert source.date_publication == date(1990, 1, 2)
    assert source.fichier == "acte_naissances_1990.pdf"


def test_individu_schema() -> None:
    """Test de sérialisation Individu avec Pydantic."""
    individu = Individu(
        id="I001",
        nom="DUPONT",
        prenom="Jean",
        sexe=Sexe.M,
        date_naissance=date(1990, 1, 1),
        lieu_naissance="Paris, France",
        famille_adultes=["F001", "F002"],
    )

    # Créer le schema Pydantic
    schema_data = {
        "id": individu.id,
        "nom": individu.nom,
        "prenom": individu.prenom,
        "sexe": individu.sexe.value if individu.sexe else None,
        "date_naissance": individu.date_naissance.isoformat() if individu.date_naissance else None,
        "lieu_naissance": individu.lieu_naissance,
        "famille_adultes": individu.famille_adultes,
    }

    schema = IndividuSchema(**schema_data)
    assert schema.id == "I001"
    assert schema.nom == "DUPONT"
    assert schema.prenom == "Jean"
    assert schema.sexe == "M"
    assert schema.famille_adultes == ["F001", "F002"]


def test_famille_with_note() -> None:
    """Test de famille avec note."""
    famille = Famille(
        id="F001",
        pere_id="I001",
        mere_id="I002",
        enfants_ids=["I003"],
        note="Mariage célébré en 1980",
    )

    assert famille.id == "F001"
    assert famille.note == "Mariage célébré en 1980"


def test_individu_with_sources() -> None:
    """Test d'individu avec sources."""
    individu = Individu(
        id="I001",
        nom="DUPONT",
        prenom="Jean",
        sources=["S001", "S002", "S003"],
    )

    assert len(individu.sources) == 3
    assert "S001" in individu.sources
    assert "S002" in individu.sources
    assert "S003" in individu.sources


def test_evenement_all_types() -> None:
    """Test de tous les types d'événements."""
    for type_evt in TypeEvenement:
        evenement = Evenement(id=f"E{type_evt.value}", type=type_evt, date=date(2020, 1, 1))
        assert evenement.type == type_evt

