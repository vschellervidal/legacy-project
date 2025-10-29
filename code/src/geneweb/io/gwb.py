"""Lecture GWB minimale (Issue #13).

Format minimal supporté à ce stade:
- Fichier `index.json` placé à la racine du dossier GWB
- Contenu: liste d'objets {"id", "nom", "prenom", "sexe"}
  - `sexe` est une chaîne parmi "M", "F", "X" (autre -> None)

Objectif: charger les individus basiques (ids/nom/prenom/sexe) pour amorcer
le portage; la prise en charge du format GWB natif sera ajoutée ensuite.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from geneweb.domain.models import Individu, Sexe


def _parse_sexe(value: object) -> Sexe | None:
    if not isinstance(value, str):
        return None
    upper = value.upper()
    if upper == "M":
        return Sexe.M
    if upper == "F":
        return Sexe.F
    if upper == "X":
        return Sexe.X
    return None


def load_gwb_minimal(root_dir: str | Path) -> List[Individu]:
    """Charge les individus basiques depuis `root_dir/index.json`.

    Renvoie une liste d'`Individu` avec id/nom/prenom/sexe remplis si disponibles.
    """

    root_path = Path(root_dir)
    index_path = root_path / "index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Index GWB minimal introuvable: {index_path}")

    data = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("index.json invalide: attendu une liste d'individus")

    individus: list[Individu] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        iid = str(item.get("id", "")).strip()
        if not iid:
            continue
        nom = item.get("nom")
        prenom = item.get("prenom")
        sexe = _parse_sexe(item.get("sexe"))
        individus.append(Individu(id=iid, nom=nom, prenom=prenom, sexe=sexe))

    return individus


