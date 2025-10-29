"""Tests pour le service Python gwb2ged (Issue #20)."""

from __future__ import annotations

import json
from pathlib import Path

from geneweb.domain.models import Sexe
from geneweb.io.gedcom import serialize_gedcom_minimal
from geneweb.io.gwb import load_gwb_minimal
from geneweb.services.gwb2ged import gwb2ged_python


def test_gwb2ged_python_basic(tmp_path: Path) -> None:
    """Test basique du service Python gwb2ged."""
    # Créer un répertoire GWB minimal
    gwb_dir = tmp_path / "base"
    gwb_dir.mkdir()

    # Créer index.json
    data = [
        {"id": "I001", "nom": "DUPONT", "prenom": "Jean", "sexe": "M"},
        {"id": "I002", "nom": "MARTIN", "prenom": "Marie", "sexe": "F"},
    ]
    (gwb_dir / "index.json").write_text(json.dumps(data), encoding="utf-8")

    # Fichier de sortie
    output_file = tmp_path / "output.ged"

    # Exécuter la conversion
    content = gwb2ged_python(gwb_dir, output_file)

    # Vérifications
    assert output_file.exists()
    assert "0 HEAD" in content
    assert "0 @I1@ INDI" in content
    assert "1 NAME Jean/DUPONT/" in content
    assert "0 TRLR" in content


def test_gwb2ged_python_missing_dir(tmp_path: Path) -> None:
    """Test que FileNotFoundError est levée si le répertoire n'existe pas."""
    missing_dir = tmp_path / "nonexistent"
    output_file = tmp_path / "output.ged"

    try:
        gwb2ged_python(missing_dir, output_file)
        assert False, "Devrait lever FileNotFoundError"
    except FileNotFoundError:
        pass

