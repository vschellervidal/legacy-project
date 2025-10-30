"""Tests pour les routes gwd de lecture (Issue #34)."""

from __future__ import annotations

from pathlib import Path

import pytest

from geneweb.io.gwb import write_gwb_minimal
from geneweb.services.gwd_routes import (
    get_ascendance,
    get_descendance,
    get_family_page,
    get_notes,
    get_person_page,
    search_persons,
)


def test_get_person_page_home(tmp_path: Path) -> None:
	"""Test de la page d'accueil (sans person_id)."""
	from geneweb.domain.models import Individu, Sexe
	
	# Créer une base GWB minimale
	individus = [
		Individu(
			id="I001",
			nom="DUPONT",
			prenom="Jean",
			sexe=Sexe.M,
		),
		Individu(
			id="I002",
			nom="MARTIN",
			prenom="Marie",
			sexe=Sexe.F,
		),
	]
	
	write_gwb_minimal(individus, [], tmp_path)
	
	# Tester la page d'accueil
	result = get_person_page(str(tmp_path))
	
	assert result["type"] == "home"
	assert result["base"]["total_individus"] == 2
	assert result["base"]["total_familles"] == 0


def test_get_person_page_person(tmp_path: Path) -> None:
	"""Test de la fiche individu."""
	from geneweb.domain.models import Individu, Sexe
	
	# Créer une base GWB minimale
	individus = [
		Individu(
			id="I001",
			nom="DUPONT",
			prenom="Jean",
			sexe=Sexe.M,
		),
	]
	
	write_gwb_minimal(individus, [], tmp_path)
	
	# Tester la fiche individu
	result = get_person_page(str(tmp_path), person_id="I001")
	
	assert result["type"] == "person"
	assert result["person"]["id"] == "I001"
	assert result["person"]["nom"] == "DUPONT"
	assert result["person"]["prenom"] == "Jean"


def test_get_person_page_not_found(tmp_path: Path) -> None:
	"""Test que ValueError est levée si l'individu n'existe pas."""
	from geneweb.domain.models import Individu, Sexe
	
	individus = [Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M)]
	write_gwb_minimal(individus, [], tmp_path)
	
	with pytest.raises(ValueError, match="introuvable"):
		get_person_page(str(tmp_path), person_id="I999")


def test_search_persons_all(tmp_path: Path) -> None:
	"""Test de la recherche sans query (tous les individus)."""
	from geneweb.domain.models import Individu, Sexe
	
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Marie", sexe=Sexe.F),
	]
	write_gwb_minimal(individus, [], tmp_path)
	
	result = search_persons(str(tmp_path), query=None)
	
	assert result["type"] == "search_all"
	assert result["total"] == 2
	assert len(result["results"]) == 2


def test_search_persons_query(tmp_path: Path) -> None:
	"""Test de la recherche avec query."""
	from geneweb.domain.models import Individu, Sexe
	
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Marie", sexe=Sexe.F),
	]
	write_gwb_minimal(individus, [], tmp_path)
	
	result = search_persons(str(tmp_path), query="DUPONT")
	
	assert result["type"] == "search"
	assert result["total"] == 1
	assert result["results"][0]["nom"] == "DUPONT"


def test_get_family_page(tmp_path: Path) -> None:
	"""Test de la fiche famille."""
	from geneweb.domain.models import Famille, Individu, Sexe
	
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Marie", sexe=Sexe.F),
		Individu(id="I003", nom="DUPONT", prenom="Pierre", sexe=Sexe.M),
	]
	familles = [
		Famille(
			id="F001",
			pere_id="I001",
			mere_id="I002",
			enfants_ids=["I003"],
		),
	]
	
	write_gwb_minimal(individus, familles, tmp_path)
	
	result = get_family_page(str(tmp_path), family_id="F001")
	
	assert result["type"] == "family"
	assert result["family"]["id"] == "F001"
	assert result["family"]["pere"]["nom"] == "DUPONT"
	assert result["family"]["mere"]["nom"] == "MARTIN"
	assert len(result["family"]["enfants"]) == 1


def test_get_ascendance(tmp_path: Path) -> None:
	"""Test de l'ascendance."""
	from geneweb.domain.models import Famille, Individu, Sexe
	
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Marie", sexe=Sexe.F),
		Individu(id="I003", nom="DUPONT", prenom="Pierre", sexe=Sexe.M, famille_enfance_id="F001"),
	]
	familles = [
		Famille(
			id="F001",
			pere_id="I001",
			mere_id="I002",
			enfants_ids=["I003"],
		),
	]
	
	write_gwb_minimal(individus, familles, tmp_path)
	
	result = get_ascendance(str(tmp_path), person_id="I003")
	
	assert result["type"] == "ascendance"
	assert result["person_id"] == "I003"
	assert len(result["ancestors"]) >= 1


def test_get_descendance(tmp_path: Path) -> None:
	"""Test de la descendance."""
	from geneweb.domain.models import Famille, Individu, Sexe
	
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Marie", sexe=Sexe.F),
		Individu(id="I003", nom="DUPONT", prenom="Pierre", sexe=Sexe.M, famille_enfance_id="F001"),
	]
	familles = [
		Famille(
			id="F001",
			pere_id="I001",
			mere_id="I002",
			enfants_ids=["I003"],
		),
	]
	
	write_gwb_minimal(individus, familles, tmp_path)
	
	result = get_descendance(str(tmp_path), person_id="I001")
	
	assert result["type"] == "descendance"
	assert result["person_id"] == "I001"
	assert len(result["descendants"]) >= 1


def test_get_notes(tmp_path: Path) -> None:
	"""Test des notes."""
	from geneweb.domain.models import Famille, Individu, Sexe
	
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, note="Note sur Jean"),
	]
	familles = [
		Famille(id="F001", pere_id="I001", note="Note famille"),
	]
	
	write_gwb_minimal(individus, familles, tmp_path)
	
	result = get_notes(str(tmp_path))
	
	assert result["type"] == "notes"
	assert len(result["person_notes"]) == 1
	assert len(result["family_notes"]) == 1
	assert result["total"] == 2

