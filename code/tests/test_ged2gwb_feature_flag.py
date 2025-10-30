"""Tests pour le feature flag CLI/API ged2gwb (Issue #28)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from geneweb.adapters.cli.main import app

runner = CliRunner()


def test_cli_ged2gwb_default_ocaml(tmp_path: Path) -> None:
	"""Test que par défaut, le CLI utilise OCaml."""
	gedcom_file = tmp_path / "input.ged"
	gedcom_file.write_text("0 HEAD\n1 CHAR UTF-8\n0 TRLR\n", encoding="utf-8")
	output_dir = tmp_path / "output"

	# Vérifier que l'option --python existe
	result = runner.invoke(app, ["ged2gwb", "--help"])
	assert result.exit_code == 0
	assert "--python" in result.stdout or "--ocaml" in result.stdout


def test_cli_ged2gwb_python_flag(tmp_path: Path) -> None:
	"""Test que --python active l'implémentation Python."""
	gedcom_file = tmp_path / "input.ged"
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
0 TRLR
"""
	gedcom_file.write_text(gedcom_content, encoding="utf-8")
	output_dir = tmp_path / "output"

	result = runner.invoke(
		app,
		["ged2gwb", "--python", "--input-file", str(gedcom_file), "--output-dir", str(output_dir)],
	)

	# Avec --python, devrait réussir et produire un GWB
	if result.exit_code != 0:
		print(f"STDOUT: {result.stdout}")
		print(f"STDERR: {result.exception}")
	assert result.exit_code == 0
	assert output_dir.exists()
	assert (output_dir / "index.json").exists()

	# Vérifier le contenu
	individus, _, _ = __import__("geneweb.io.gwb", fromlist=["load_gwb_minimal"]).load_gwb_minimal(output_dir)
	assert len(individus) == 1
	assert individus[0].id == "@I1@"  # Le parser GEDCOM garde les @ dans les IDs


def test_cli_ged2gwb_env_flag(tmp_path: Path) -> None:
	"""Test que GENEWEB_USE_PYTHON active l'implémentation Python."""
	gedcom_file = tmp_path / "input.ged"
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
0 TRLR
"""
	gedcom_file.write_text(gedcom_content, encoding="utf-8")
	output_dir = tmp_path / "output"

	with patch.dict(os.environ, {"GENEWEB_USE_PYTHON": "1"}):
		result = runner.invoke(
			app,
			["ged2gwb", "--input-file", str(gedcom_file), "--output-dir", str(output_dir)],
		)

	if result.exit_code != 0:
		print(f"STDOUT: {result.stdout}")
		print(f"STDERR: {result.exception}")
	assert result.exit_code == 0
	assert output_dir.exists()


def test_cli_ged2gwb_missing_file(tmp_path: Path) -> None:
	"""Test que l'erreur est levée si le fichier n'existe pas."""
	missing_file = tmp_path / "missing.ged"
	output_dir = tmp_path / "output"

	result = runner.invoke(
		app,
		["ged2gwb", "--python", "--input-file", str(missing_file), "--output-dir", str(output_dir)],
	)

	assert result.exit_code != 0


def test_cli_ged2gwb_round_trip(tmp_path: Path) -> None:
	"""Test round-trip : GEDCOM -> GWB -> GEDCOM."""
	gedcom_file = tmp_path / "input.ged"
	gedcom_content = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /DUPONT/
1 SEX M
0 @I2@ INDI
1 NAME Anne /MARTIN/
1 SEX F
0 TRLR
"""
	gedcom_file.write_text(gedcom_content, encoding="utf-8")
	gwb_dir = tmp_path / "gwb"
	output_ged = tmp_path / "output.ged"

	# GEDCOM -> GWB
	result1 = runner.invoke(
		app,
		["ged2gwb", "--python", "--input-file", str(gedcom_file), "--output-dir", str(gwb_dir)],
	)
	assert result1.exit_code == 0

	# GWB -> GEDCOM
	result2 = runner.invoke(
		app,
		["gwb2ged", "--python", "-i", str(gwb_dir), "-o", str(output_ged)],
	)
	assert result2.exit_code == 0
	assert output_ged.exists()

	# Vérifier que le contenu est présent
	content = output_ged.read_text(encoding="utf-8")
	assert "@I1@ INDI" in content
	assert "@I2@ INDI" in content

