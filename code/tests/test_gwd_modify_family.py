from __future__ import annotations

from pathlib import Path

import pytest

from geneweb.domain.models import Individu, Sexe
from geneweb.io.gwb import load_gwb_minimal, write_gwb_minimal
from geneweb.services.gwd_modify import add_famille, mod_famille, del_individu, del_famille


def _setup_base(tmp_path: Path) -> None:
    write_gwb_minimal(
        [
            Individu(id="I1", nom="A", prenom="A", sexe=Sexe.M),
            Individu(id="I2", nom="B", prenom="B", sexe=Sexe.F),
            Individu(id="I3", nom="C", prenom="C", sexe=Sexe.M),
        ],
        [],
        tmp_path,
    )


def test_add_and_mod_famille(tmp_path: Path) -> None:
    _setup_base(tmp_path)

    fam = add_famille(tmp_path, id="F1", pere_id="I1", mere_id="I2", enfants_ids=["I3"])
    assert fam.id == "F1"
    assert fam.pere_id == "I1"
    assert fam.mere_id == "I2"
    assert fam.enfants_ids == ["I3"]

    fam2 = mod_famille(tmp_path, id="F1", enfants_ids=["I3", "I1"])  # autorisé, même si peu logique
    assert fam2.enfants_ids == ["I3", "I1"]


def test_del_individu_with_links_requires_force(tmp_path: Path) -> None:
    _setup_base(tmp_path)
    add_famille(tmp_path, id="F1", pere_id="I1", mere_id="I2", enfants_ids=["I3"])

    with pytest.raises(ValueError):
        del_individu(tmp_path, id="I1", force=False)

    # Avec force, supprime et nettoie les liens
    del_individu(tmp_path, id="I1", force=True)
    individus, familles, _ = load_gwb_minimal(tmp_path)
    assert all(ind.id != "I1" for ind in individus)
    fam = next(f for f in familles if f.id == "F1")
    assert fam.pere_id is None


def test_del_famille_needs_force_when_linked(tmp_path: Path) -> None:
    _setup_base(tmp_path)
    add_famille(tmp_path, id="F1", pere_id="I1", mere_id="I2", enfants_ids=["I3"])

    with pytest.raises(ValueError):
        del_famille(tmp_path, id="F1", force=False)

    # Avec force
    del_famille(tmp_path, id="F1", force=True)
    _, familles, _ = load_gwb_minimal(tmp_path)
    assert all(f.id != "F1" for f in familles)


