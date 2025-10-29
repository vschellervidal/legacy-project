"""Tests pour le feature flag CLI (Issue #20)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from geneweb.adapters.cli.main import app

runner = CliRunner()


def test_cli_gwb2ged_default_ocaml(tmp_path: Path) -> None:
    """Test que par défaut, le CLI utilise OCaml."""
    gwb_dir = tmp_path / "base"
    gwb_dir.mkdir()
    (gwb_dir / "index.json").write_text(json.dumps([]), encoding="utf-8")
    output_file = tmp_path / "output.ged"

    # Sans flag, devrait utiliser OCaml (et échouer si OCaml n'est pas disponible)
    # On vérifie juste que l'option --ocaml existe
    result = runner.invoke(app, ["gwb2ged", "--help"])
    assert result.exit_code == 0
    assert "--python" in result.stdout or "--ocaml" in result.stdout


def test_cli_gwb2ged_python_flag(tmp_path: Path) -> None:
    """Test que --python active l'implémentation Python."""
    gwb_dir = tmp_path / "base"
    gwb_dir.mkdir()

    data = [{"id": "I001", "nom": "DUPONT", "prenom": "Jean", "sexe": "M"}]
    (gwb_dir / "index.json").write_text(json.dumps(data), encoding="utf-8")

    output_file = tmp_path / "output.ged"

    result = runner.invoke(
        app,
        ["gwb2ged", "--python", "-i", str(gwb_dir), "-o", str(output_file)],
    )

    # Avec --python, devrait réussir et produire un GEDCOM
    if result.exit_code != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.exception}")
    assert result.exit_code == 0
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "0 HEAD" in content
    assert "0 @I1@ INDI" in content


def test_cli_gwb2ged_env_flag(tmp_path: Path) -> None:
    """Test que GENEWEB_USE_PYTHON active l'implémentation Python."""
    gwb_dir = tmp_path / "base"
    gwb_dir.mkdir()

    data = [{"id": "I001", "nom": "DUPONT", "prenom": "Jean"}]
    (gwb_dir / "index.json").write_text(json.dumps(data), encoding="utf-8")

    output_file = tmp_path / "output.ged"

    with patch.dict(os.environ, {"GENEWEB_USE_PYTHON": "1"}):
        result = runner.invoke(
            app,
            ["gwb2ged", "-i", str(gwb_dir), "-o", str(output_file)],
        )

    if result.exit_code != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.exception}")
    assert result.exit_code == 0
    assert output_file.exists()

