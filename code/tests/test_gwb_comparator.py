"""Tests pour le comparateur GWB (Issue #27)."""

from __future__ import annotations

from datetime import date as date_type

from geneweb.domain.models import Famille, Individu, Sexe, Source
from geneweb.services.comparator import compare_gwb


def test_compare_gwb_equal_basic() -> None:
	"""Test que deux bases GWB identiques sont détectées comme égales."""
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus, familles, sources)
	right = (individus.copy(), familles.copy(), sources.copy())
	
	result = compare_gwb(left, right)
	assert result.are_equal is True
	assert result.diff == ""
	assert result.left_count == 2
	assert result.right_count == 2


def test_compare_gwb_equal_with_familles() -> None:
	"""Test comparaison de bases GWB identiques avec familles."""
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
		Individu(id="I003", nom="DUPONT", prenom="Pierre", sexe=Sexe.M),
	]
	familles = [
		Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=["I003"]),
	]
	sources: list[Source] = []
	
	left = (individus, familles, sources)
	right = (individus.copy(), familles.copy(), sources.copy())
	
	result = compare_gwb(left, right)
	assert result.are_equal is True
	assert result.diff == ""
	assert result.left_count == 3 + 1
	assert result.right_count == 3 + 1


def test_compare_gwb_equal_with_sources() -> None:
	"""Test comparaison de bases GWB identiques avec sources."""
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, sources=["S001"]),
	]
	familles: list[Famille] = []
	sources = [
		Source(id="S001", titre="Acte de naissance", auteur="Mairie Paris"),
	]
	
	left = (individus, familles, sources)
	right = (individus.copy(), familles.copy(), sources.copy())
	
	result = compare_gwb(left, right)
	assert result.are_equal is True
	assert result.diff == ""
	assert result.left_count == 2
	assert result.right_count == 2


def test_compare_gwb_diff_individu_missing() -> None:
	"""Test détection quand un individu manque dans une base."""
	individus_left = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
	]
	individus_right = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus_left, familles, sources)
	right = (individus_right, familles, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert result.left_count == 2
	assert result.right_count == 1
	assert "I002" in result.diff or "MARTIN" in result.diff


def test_compare_gwb_diff_individu_different_name() -> None:
	"""Test détection quand un individu a un nom différent."""
	individus_left = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
	]
	individus_right = [
		Individu(id="I001", nom="MARTIN", prenom="Jean", sexe=Sexe.M),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus_left, familles, sources)
	right = (individus_right, familles, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert "DUPONT" in result.diff or "MARTIN" in result.diff


def test_compare_gwb_diff_famille_missing() -> None:
	"""Test détection quand une famille manque dans une base."""
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
	]
	familles_left = [
		Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=[]),
	]
	familles_right: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus, familles_left, sources)
	right = (individus, familles_right, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert result.left_count == 3  # 2 individus + 1 famille
	assert result.right_count == 2  # 2 individus seulement


def test_compare_gwb_diff_famille_different_parent() -> None:
	"""Test détection quand une famille a un parent différent."""
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
		Individu(id="I003", nom="SMITH", prenom="Bob", sexe=Sexe.M),
	]
	familles_left = [
		Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=[]),
	]
	familles_right = [
		Famille(id="F001", pere_id="I001", mere_id="I003", enfants_ids=[]),
	]
	sources: list[Source] = []
	
	left = (individus, familles_left, sources)
	right = (individus, familles_right, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert "I002" in result.diff or "I003" in result.diff


def test_compare_gwb_diff_source_missing() -> None:
	"""Test détection quand une source manque dans une base."""
	individus = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
	]
	familles: list[Famille] = []
	sources_left = [
		Source(id="S001", titre="Acte de naissance", auteur="Mairie Paris"),
	]
	sources_right: list[Source] = []
	
	left = (individus, familles, sources_left)
	right = (individus, familles, sources_right)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert result.left_count == 2  # 1 individu + 1 source
	assert result.right_count == 1  # 1 individu seulement


def test_compare_gwb_diff_source_different_title() -> None:
	"""Test détection quand une source a un titre différent."""
	individus: list[Individu] = []
	familles: list[Famille] = []
	sources_left = [
		Source(id="S001", titre="Acte de naissance", auteur="Mairie Paris"),
	]
	sources_right = [
		Source(id="S001", titre="Acte de décès", auteur="Mairie Paris"),
	]
	
	left = (individus, familles, sources_left)
	right = (individus, familles, sources_right)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert "Acte de naissance" in result.diff or "Acte de décès" in result.diff


def test_compare_gwb_with_events() -> None:
	"""Test comparaison avec événements vitaux (dates et lieux)."""
	individus_left = [
		Individu(
			id="I001",
			nom="DUPONT",
			prenom="Jean",
			sexe=Sexe.M,
			date_naissance=date_type(1990, 1, 15),
			lieu_naissance="Paris, France",
		),
	]
	individus_right = [
		Individu(
			id="I001",
			nom="DUPONT",
			prenom="Jean",
			sexe=Sexe.M,
			date_naissance=date_type(1990, 1, 16),
			lieu_naissance="Paris, France",
		),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus_left, familles, sources)
	right = (individus_right, familles, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert "1990-01-15" in result.diff or "1990-01-16" in result.diff


def test_compare_gwb_order_independent() -> None:
	"""Test que l'ordre des individus n'affecte pas la comparaison."""
	individus_left = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
	]
	individus_right = [
		Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus_left, familles, sources)
	right = (individus_right, familles, sources)
	
	result = compare_gwb(left, right)
	# Les bases doivent être égales car elles sont triées par ID avant comparaison
	assert result.are_equal is True


def test_compare_gwb_with_notes() -> None:
	"""Test comparaison avec notes."""
	individus_left = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, note="Note 1"),
	]
	individus_right = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, note="Note 2"),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus_left, familles, sources)
	right = (individus_right, familles, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert "Note 1" in result.diff or "Note 2" in result.diff


def test_compare_gwb_with_sources_references() -> None:
	"""Test comparaison avec références aux sources dans individus."""
	individus_left = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, sources=["S001", "S002"]),
	]
	individus_right = [
		Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, sources=["S001"]),
	]
	familles: list[Famille] = []
	sources: list[Source] = []
	
	left = (individus_left, familles, sources)
	right = (individus_right, familles, sources)
	
	result = compare_gwb(left, right)
	assert result.are_equal is False
	assert "S002" in result.diff

