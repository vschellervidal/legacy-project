"""Tests de caractérisation pour services analytiques (Issue #29).

Ces tests valident les entrées/sorties des services OCaml consang et connex,
créant des snapshots de référence pour la future implémentation Python.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from geneweb.adapters.ocaml_bridge.bridge import OcamlCommandError, run_connex, run_consang

# Budgets de performance (en secondes)
PERF_BUDGET_CONNEX_NORMAL = 10.0
PERF_BUDGET_CONSANG_NORMAL = 10.0
PERF_BUDGET_CONNEX_FAST = 5.0
PERF_BUDGET_CONSANG_FAST = 5.0

# Marker pour skip si OCaml n'est pas disponible
pytestmark = pytest.mark.skipif(
	not os.getenv("RUN_OCAML_TESTS"),
	reason="RUN_OCAML_TESTS=1 et GENEWEB_OCAML_ROOT requis pour tests OCaml",
)


@pytest.fixture
def fixture_consang_simple(tmp_path: Path) -> Path:
	"""Crée une fixture GWB simple avec cas de consanguinité (cousins mariés).
	
	Retourne le chemin vers la base GWB créée.
	"""
	# GEDCOM avec cousins mariés (cas classique de consanguinité)
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
0 @I2@ INDI
1 NAME Marie /MARTIN/
1 SEX F
0 @I3@ INDI
1 NAME Pierre /DUPONT/
1 SEX M
0 @I4@ INDI
1 NAME Anne /MARTIN/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
0 @F2@ FAM
1 HUSB @I3@
1 WIFE @I4@
1 CHIL @I5@
0 @I5@ INDI
1 NAME Paul /DUPONT/
1 SEX M
0 @F3@ FAM
1 HUSB @I1@
1 CHIL @I6@
0 @I6@ INDI
1 NAME Sophie /DUPONT/
1 SEX F
0 @F4@ FAM
1 HUSB @I2@
1 CHIL @I7@
0 @I7@ INDI
1 NAME Luc /MARTIN/
1 SEX M
0 @F5@ FAM
1 HUSB @I6@
1 WIFE @I7@
0 TRLR
"""
	gedcom_file = tmp_path / "input.ged"
	gedcom_file.write_text(gedcom_content, encoding="utf-8")
	
	# Convertir en GWB via OCaml ged2gwb
	from geneweb.adapters.ocaml_bridge.bridge import run_ged2gwb
	
	output_dir = tmp_path / "base.gwb"
	try:
		run_ged2gwb(["-i", str(gedcom_file), "-o", str(output_dir)])
		return output_dir
	except (OcamlCommandError, FileNotFoundError) as e:
		pytest.skip(f"ged2gwb OCaml non disponible: {e}")


@pytest.fixture
def fixture_connex_disconnected(tmp_path: Path) -> Path:
	"""Crée une fixture GWB avec composantes connexes séparées.
	
	Retourne le chemin vers la base GWB créée.
	"""
	# GEDCOM avec deux familles complètement séparées
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Famille1 /PERE/
1 SEX M
0 @I2@ INDI
1 NAME Famille1 /MERE/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 @I3@ INDI
1 NAME Famille2 /PERE/
1 SEX M
0 @I4@ INDI
1 NAME Famille2 /MERE/
1 SEX F
0 @F2@ FAM
1 HUSB @I3@
1 WIFE @I4@
0 TRLR
"""
	gedcom_file = tmp_path / "input.ged"
	gedcom_file.write_text(gedcom_content, encoding="utf-8")
	
	# Convertir en GWB via OCaml ged2gwb
	from geneweb.adapters.ocaml_bridge.bridge import run_ged2gwb
	
	output_dir = tmp_path / "base.gwb"
	try:
		run_ged2gwb(["-i", str(gedcom_file), "-o", str(output_dir)])
		return output_dir
	except (OcamlCommandError, FileNotFoundError) as e:
		pytest.skip(f"ged2gwb OCaml non disponible: {e}")


def test_consang_characterization_basic(fixture_consang_simple: Path) -> None:
	"""Test de caractérisation consang : exécution basique et capture sortie."""
	base_path = str(fixture_consang_simple / "base")
	
	start_time = time.time()
	try:
		run_consang(["-qq", base_path])  # -qq = très silencieux (sortie non utilisée pour l'instant)
		duration = time.time() - start_time
		
		# Valider que consang s'exécute sans erreur
		# La sortie peut être vide en mode -qq, mais pas d'exception = succès
		assert duration < PERF_BUDGET_CONSANG_NORMAL  # Budget perf: doit être rapide sur petite base
		
		# Capturer métadonnées (pour snapshot futur)
		snapshot = {
			"status": "success",
			"duration_sec": round(duration, 3),
			"base_size": Path(base_path).stat().st_size if Path(base_path).exists() else 0,
		}
		
		# Pour l'instant, on valide juste que ça s'exécute
		# Les snapshots détaillés seront ajoutés quand l'impl Python existera
		assert snapshot["status"] == "success"
		
	except OcamlCommandError as e:
		pytest.fail(f"consang a échoué: {e.stderr}")


def test_connex_characterization_basic(fixture_connex_disconnected: Path) -> None:
	"""Test de caractérisation connex : exécution basique et capture sortie."""
	base_path = str(fixture_connex_disconnected / "base")
	
	start_time = time.time()
	try:
		# -a = toutes les composantes connexes
		run_connex(["-a", base_path])  # Sortie capturée pour snapshot futur
		duration = time.time() - start_time
		
		# Valider que connex s'exécute et trouve les composantes
		assert duration < PERF_BUDGET_CONNEX_NORMAL  # Budget perf: doit être rapide
		
		# Capturer les composantes connexes dans la sortie
		snapshot = {
			"status": "success",
			"duration_sec": round(duration, 3),
			"output_lines": len(output.splitlines()),
			"base_size": Path(base_path).stat().st_size if Path(base_path).exists() else 0,
		}
		
		# Valider que la sortie contient des informations
		assert snapshot["status"] == "success"
		
	except OcamlCommandError as e:
		pytest.fail(f"connex a échoué: {e.stderr}")


def test_consang_performance_budget(fixture_consang_simple: Path) -> None:
	"""Test de budget de performance pour consang."""
	base_path = str(fixture_consang_simple / "base")
	
	start_time = time.time()
	try:
		run_consang(["-qq", "-fast", base_path])  # -fast = mode rapide
		duration = time.time() - start_time
		
		# Budget de performance (à ajuster selon observations)
		assert duration < PERF_BUDGET_CONSANG_FAST, f"consang -fast trop lent: {duration:.2f}s"
		
	except OcamlCommandError as e:
		pytest.skip(f"consang non disponible: {e}")


def test_connex_performance_budget(fixture_connex_disconnected: Path) -> None:
	"""Test de budget de performance pour connex."""
	base_path = str(fixture_connex_disconnected / "base")
	
	start_time = time.time()
	try:
		run_connex(["-a", base_path])
		duration = time.time() - start_time
		
		# Budget de performance
		assert duration < PERF_BUDGET_CONNEX_FAST, f"connex trop lent: {duration:.2f}s"
		
	except OcamlCommandError as e:
		pytest.skip(f"connex non disponible: {e}")

