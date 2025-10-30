from __future__ import annotations

from pathlib import Path

from geneweb.domain.models import Individu, Sexe
from geneweb.io.gwb import load_gwb_minimal, write_gwb_minimal
from geneweb.services.gwd_modify import add_individu, mod_individu


def test_add_individu(tmp_path: Path) -> None:
    # base vide
    write_gwb_minimal([], [], tmp_path)

    ind = add_individu(tmp_path, id="I100", nom="TEST", prenom="Alice", sexe="F")

    individus, familles, sources = load_gwb_minimal(tmp_path)
    assert any(x.id == "I100" and x.nom == "TEST" and x.prenom == "Alice" for x in individus)
    assert ind.sexe == Sexe.F


def test_mod_individu(tmp_path: Path) -> None:
    # base avec un individu
    write_gwb_minimal([Individu(id="I200", nom="OLD", prenom="Bob", sexe=Sexe.M)], [], tmp_path)

    ind = mod_individu(tmp_path, id="I200", nom="NEW", prenom="Bobby", sexe="X")

    individus, familles, sources = load_gwb_minimal(tmp_path)
    updated = next(x for x in individus if x.id == "I200")
    assert updated.nom == "NEW"
    assert updated.prenom == "Bobby"
    assert updated.sexe == Sexe.X

