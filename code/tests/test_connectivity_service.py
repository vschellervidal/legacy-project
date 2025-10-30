"""Tests pour le service de connexité (Issue #31)."""

from __future__ import annotations

from geneweb.domain.models import Famille, Individu, Sexe
from geneweb.services.connectivity import (
    compute_connected_components,
    compute_connected_components_from_gwb,
    get_largest_component,
)


def _ind(i: str, sexe: str | None = None) -> Individu:
    return Individu(id=i, sexe=Sexe(sexe) if sexe else None)


def test_single_family_one_component() -> None:
    """Test: une famille simple doit former une seule composante."""
    pere = _ind("I1", "M")
    mere = _ind("I2", "F")
    enfant = _ind("I3")
    fam = Famille(id="F1", pere_id=pere.id, mere_id=mere.id, enfants_ids=[enfant.id])

    components = compute_connected_components([pere, mere, enfant], [fam])

    assert len(components) == 1
    assert set(components[0]) == {"I1", "I2", "I3"}


def test_disconnected_families_two_components() -> None:
    """Test: deux familles séparées doivent former deux composantes."""
    # Famille 1
    pere1 = _ind("I1", "M")
    mere1 = _ind("I2", "F")
    enfant1 = _ind("I3")

    # Famille 2 (complètement séparée)
    pere2 = _ind("I4", "M")
    mere2 = _ind("I5", "F")
    enfant2 = _ind("I6")

    fam1 = Famille(id="F1", pere_id=pere1.id, mere_id=mere1.id, enfants_ids=[enfant1.id])
    fam2 = Famille(id="F2", pere_id=pere2.id, mere_id=mere2.id, enfants_ids=[enfant2.id])

    components = compute_connected_components(
        [pere1, mere1, enfant1, pere2, mere2, enfant2], [fam1, fam2]
    )

    assert len(components) == 2
    # Vérifier que les composantes sont correctes
    component_sets = [set(comp) for comp in components]
    assert {"I1", "I2", "I3"} in component_sets
    assert {"I4", "I5", "I6"} in component_sets


def test_extended_family_one_component() -> None:
    """Test: famille étendue avec plusieurs générations = une composante."""
    # Grands-parents
    gp1 = _ind("GP1", "M")
    gp2 = _ind("GP2", "F")
    # Parents
    p1 = _ind("P1", "M")
    p2 = _ind("P2", "F")
    # Enfants
    e1 = _ind("E1")
    e2 = _ind("E2")

    fam_gp = Famille(id="FGP", pere_id=gp1.id, mere_id=gp2.id, enfants_ids=["P1", "P2"])
    fam_p = Famille(id="FP", pere_id=p1.id, mere_id=p2.id, enfants_ids=["E1", "E2"])

    components = compute_connected_components(
        [gp1, gp2, p1, p2, e1, e2], [fam_gp, fam_p]
    )

    assert len(components) == 1
    assert set(components[0]) == {"GP1", "GP2", "P1", "P2", "E1", "E2"}


def test_isolated_individual_separate_component() -> None:
    """Test: individu isolé forme sa propre composante."""
    # Famille
    pere = _ind("I1", "M")
    mere = _ind("I2", "F")
    enfant = _ind("I3")
    fam = Famille(id="F1", pere_id=pere.id, mere_id=mere.id, enfants_ids=[enfant.id])

    # Individu isolé (aucun lien)
    isolated = _ind("ISO")

    components = compute_connected_components(
        [pere, mere, enfant, isolated], [fam]
    )

    assert len(components) == 2
    component_sets = [set(comp) for comp in components]
    assert {"I1", "I2", "I3"} in component_sets
    assert {"ISO"} in component_sets


def test_largest_component() -> None:
    """Test: get_largest_component retourne la plus grande composante."""
    # Petite famille
    pere1 = _ind("I1", "M")
    mere1 = _ind("I2", "F")
    fam1 = Famille(id="F1", pere_id=pere1.id, mere_id=mere1.id, enfants_ids=[])

    # Grande famille
    pere2 = _ind("I3", "M")
    mere2 = _ind("I4", "F")
    enfant2a = _ind("I5")
    enfant2b = _ind("I6")
    enfant2c = _ind("I7")
    fam2 = Famille(
        id="F2",
        pere_id=pere2.id,
        mere_id=mere2.id,
        enfants_ids=[enfant2a.id, enfant2b.id, enfant2c.id],
    )

    largest = get_largest_component(
        [pere1, mere1, pere2, mere2, enfant2a, enfant2b, enfant2c], [fam1, fam2]
    )

    assert set(largest) == {"I3", "I4", "I5", "I6", "I7"}


def test_empty_input() -> None:
    """Test: entrées vides retournent liste vide."""
    components = compute_connected_components([], [])
    assert components == []


def test_single_individual() -> None:
    """Test: un seul individu isolé forme une composante."""
    ind = _ind("I1")
    components = compute_connected_components([ind], [])

    assert len(components) == 1
    assert components[0] == ["I1"]

