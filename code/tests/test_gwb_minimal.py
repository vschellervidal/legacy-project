from __future__ import annotations

import json
from pathlib import Path

from geneweb.domain.models import Sexe
from geneweb.io.gwb import load_gwb_minimal


def test_load_gwb_minimal_ok(tmp_path: Path) -> None:
    data = [
        {"id": "I001", "nom": "DUPONT", "prenom": "Jean", "sexe": "M"},
        {"id": "I002", "nom": "MARTIN", "prenom": "Anne", "sexe": "F"},
        {"id": "I003", "nom": "UNKNOWN", "prenom": "X", "sexe": "X"},
    ]
    (tmp_path / "index.json").write_text(json.dumps(data), encoding="utf-8")

    individus = load_gwb_minimal(tmp_path)

    assert len(individus) == 3
    assert individus[0].id == "I001" and individus[0].nom == "DUPONT" and individus[0].prenom == "Jean"
    assert individus[0].sexe == Sexe.M
    assert individus[1].sexe == Sexe.F
    assert individus[2].sexe == Sexe.X


def test_load_gwb_minimal_missing_file(tmp_path: Path) -> None:
    # Pas d'index.json
    try:
        load_gwb_minimal(tmp_path)
        assert False, "Devrait lever FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_gwb_minimal_invalid_entries(tmp_path: Path) -> None:
    # Entrées invalides (sans id) ou mauvais types sont ignorées
    data = [
        {"id": ""},
        123,
        {"id": "I001", "sexe": "Z"},
    ]
    (tmp_path / "index.json").write_text(json.dumps(data), encoding="utf-8")

    individus = load_gwb_minimal(tmp_path)
    assert len(individus) == 1
    assert individus[0].id == "I001" and individus[0].sexe is None


