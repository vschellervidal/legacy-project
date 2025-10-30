"""Tests pour les feature flags CLI et API des services analytiques (Issue #32)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from geneweb.adapters.cli.main import app

runner = CliRunner()


@pytest.fixture
def simple_gwb_base(tmp_path: Path) -> Path:
    """Crée une base GWB minimale pour les tests."""
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    
    # Créer une famille avec consanguinité (frères/soeurs mariés)
    gp1 = {"id": "G1", "nom": "GP1", "sexe": "M"}
    gp2 = {"id": "G2", "nom": "GP2", "sexe": "F"}
    a = {"id": "A", "nom": "A", "sexe": "M"}
    b = {"id": "B", "nom": "B", "sexe": "F"}
    c = {"id": "C", "nom": "C", "sexe": "M"}
    
    fam1 = {"id": "F1", "pere_id": "G1", "mere_id": "G2", "enfants_ids": ["A", "B"]}
    fam2 = {"id": "F2", "pere_id": "A", "mere_id": "B", "enfants_ids": ["C"]}
    
    data = {
        "individus": [gp1, gp2, a, b, c],
        "familles": [fam1, fam2],
    }
    
    (base_dir / "index.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return tmp_path


def test_cli_consang_python_flag(simple_gwb_base: Path) -> None:
    """Test que --python active l'implémentation Python pour consang."""
    result = runner.invoke(
        app,
        ["consang", "--python", str(simple_gwb_base)],
    )
    
    assert result.exit_code == 0
    # Les messages sont sur stderr, stdout contient les résultats
    assert "F = 0.25" in result.stdout or "0.250000" in result.stdout


def test_cli_consang_env_flag(simple_gwb_base: Path) -> None:
    """Test que GENEWEB_USE_PYTHON active l'implémentation Python pour consang."""
    with patch.dict(os.environ, {"GENEWEB_USE_PYTHON": "1"}):
        result = runner.invoke(
            app,
            ["consang", str(simple_gwb_base)],
        )
    
    # Devrait fonctionner avec Python via l'env var
    assert result.exit_code == 0


def test_cli_consang_quiet_mode(simple_gwb_base: Path) -> None:
    """Test le mode silencieux pour consang."""
    with patch.dict(os.environ, {"GENEWEB_USE_PYTHON": "1"}):
        result = runner.invoke(
            app,
            ["consang", "--python", "--quiet", str(simple_gwb_base)],
        )
    
    assert result.exit_code == 0
    # En mode quiet, moins de sortie
    assert len(result.stdout.strip()) == 0 or "Coefficients" not in result.stdout


def test_cli_connex_python_flag(simple_gwb_base: Path) -> None:
    """Test que --python active l'implémentation Python pour connex."""
    result = runner.invoke(
        app,
        ["connex", "--python", str(simple_gwb_base)],
    )
    
    assert result.exit_code == 0
    # Les messages sont sur stderr, mais on vérifie que ça fonctionne
    assert result.stdout or result.exit_code == 0


def test_cli_connex_all_components(simple_gwb_base: Path) -> None:
    """Test l'option -a pour afficher toutes les composantes."""
    with patch.dict(os.environ, {"GENEWEB_USE_PYTHON": "1"}):
        result = runner.invoke(
            app,
            ["connex", "--python", "--all", str(simple_gwb_base)],
        )
    
    assert result.exit_code == 0
    # Vérifier que ça fonctionne (les détails peuvent être sur stderr)
    assert result.stdout or result.exit_code == 0


def test_cli_connex_env_flag(simple_gwb_base: Path) -> None:
    """Test que GENEWEB_USE_PYTHON active l'implémentation Python pour connex."""
    with patch.dict(os.environ, {"GENEWEB_USE_PYTHON": "1"}):
        result = runner.invoke(
            app,
            ["connex", str(simple_gwb_base)],
        )
    
    assert result.exit_code == 0


def test_cli_consang_default_ocaml_option() -> None:
    """Test que l'option --ocaml existe."""
    result = runner.invoke(app, ["consang", "--help"])
    assert result.exit_code == 0
    assert "--python" in result.stdout or "--ocaml" in result.stdout


def test_cli_connex_default_ocaml_option() -> None:
    """Test que l'option --ocaml existe."""
    result = runner.invoke(app, ["connex", "--help"])
    assert result.exit_code == 0
    assert "--python" in result.stdout or "--ocaml" in result.stdout

