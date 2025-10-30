"""Tests pour le service Python ged2gwb (Issue #28)."""

from __future__ import annotations

from pathlib import Path

from geneweb.io.gwb import load_gwb_minimal
from geneweb.services.ged2gwb import ged2gwb_python


def test_ged2gwb_python_basic(tmp_path: Path) -> None:
	"""Test basique du service Python ged2gwb."""
	# Créer un fichier GEDCOM minimal
	gedcom_file = tmp_path / "input.ged"
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
0 TRLR
"""
	gedcom_file.write_text(gedcom_content, encoding="utf-8")

	# Répertoire GWB de sortie
	output_dir = tmp_path / "output_gwb"

	# Exécuter la conversion
	ged2gwb_python(gedcom_file, output_dir)

	# Vérifications
	assert output_dir.exists()
	index_path = output_dir / "index.json"
	assert index_path.exists()

	# Vérifier le contenu
	individus, familles, sources = load_gwb_minimal(output_dir)
	assert len(individus) == 1
	assert individus[0].id == "@I1@"  # Le parser GEDCOM garde les @ dans les IDs
	assert individus[0].nom == "DUPONT"
	assert individus[0].prenom == "Jean"


def test_ged2gwb_python_missing_file(tmp_path: Path) -> None:
	"""Test que FileNotFoundError est levée si le fichier n'existe pas."""
	missing_file = tmp_path / "missing.ged"
	output_dir = tmp_path / "output"

	import pytest
	with pytest.raises(FileNotFoundError):
		ged2gwb_python(missing_file, output_dir)


def test_ged2gwb_python_with_familles(tmp_path: Path) -> None:
	"""Test avec familles."""
	gedcom_file = tmp_path / "input.ged"
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
0 @I2@ INDI
1 NAME Anne /MARTIN/
1 SEX F
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
0 @I3@ INDI
1 NAME Pierre /DUPONT/
1 SEX M
0 TRLR
"""
	gedcom_file.write_text(gedcom_content, encoding="utf-8")

	output_dir = tmp_path / "output_gwb"

	ged2gwb_python(gedcom_file, output_dir)

	# Vérifier
	individus, familles, sources = load_gwb_minimal(output_dir)
	assert len(individus) == 3
	assert len(familles) == 1
	assert familles[0].pere_id == "@I1@"
	assert familles[0].mere_id == "@I2@"
	# Le parser transforme les IDs enfants: @I3@ devient I3
	assert "I3" in familles[0].enfants_ids


def test_ged2gwb_python_with_events(tmp_path: Path) -> None:
	"""Test avec événements vitaux."""
	gedcom_file = tmp_path / "input.ged"
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
1 BIRT
2 DATE 1990-01-15
2 PLAC Paris, France
1 DEAT
2 DATE 2050-12-31
2 PLAC Lyon, France
0 TRLR
"""
	gedcom_file.write_text(gedcom_content, encoding="utf-8")

	output_dir = tmp_path / "output_gwb"

	ged2gwb_python(gedcom_file, output_dir)

	# Vérifier
	individus, familles, sources = load_gwb_minimal(output_dir)
	assert len(individus) == 1
	assert individus[0].date_naissance is not None
	assert individus[0].lieu_naissance == "Paris, France"
	assert individus[0].date_deces is not None
	assert individus[0].lieu_deces == "Lyon, France"

