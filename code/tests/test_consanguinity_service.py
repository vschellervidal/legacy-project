from __future__ import annotations

from geneweb.domain.models import Famille, Individu, Sexe
from geneweb.services.consanguinity import (
    compute_inbreeding_coefficients,
    compute_inbreeding_for_individual,
)


def _ind(i: str, sexe: str | None = None) -> Individu:
    return Individu(id=i, sexe=Sexe(sexe) if sexe else None)


def test_founders_have_zero_inbreeding() -> None:
    # Deux fondateurs sans parents connus
    individus = [_ind("I1", "M"), _ind("I2", "F")]
    familles: list[Famille] = []

    F = compute_inbreeding_coefficients(individus, familles)
    assert F["I1"] == 0.0
    assert F["I2"] == 0.0


def test_child_of_founders_has_zero_inbreeding() -> None:
    # Parents fondateurs -> enfant non consanguin
    pere = _ind("I1", "M")
    mere = _ind("I2", "F")
    enfant = _ind("I3")
    fam = Famille(id="F1", pere_id=pere.id, mere_id=mere.id, enfants_ids=[enfant.id])

    F = compute_inbreeding_coefficients([pere, mere, enfant], [fam])
    assert F[enfant.id] == 0.0


def test_child_of_full_siblings_has_F_quarter() -> None:
    # Grand-parents fondateurs
    gp1 = _ind("G1", "M")
    gp2 = _ind("G2", "F")
    fam_gp = Famille(id="FG", pere_id=gp1.id, mere_id=gp2.id, enfants_ids=["A", "B"])  # frères/soeurs

    # Frère et soeur (A et B)
    A = _ind("A", "M")
    B = _ind("B", "F")

    # Enfant C de A x B (union consanguine)
    C = _ind("C")
    fam_union = Famille(id="FU", pere_id=A.id, mere_id=B.id, enfants_ids=[C.id])

    individus = [gp1, gp2, A, B, C]
    familles = [fam_gp, fam_union]

    Fc = compute_inbreeding_for_individual(C.id, individus, familles)
    assert abs(Fc - 0.25) < 1e-9


def test_child_of_first_cousins_has_F_one_sixteenth() -> None:
    # Structure pour cousins germains:
    # - GPA x GMA (fondateurs) -> enfants P1 et P2 (frères/soeurs)
    # - P1 x P1_partenaire -> A1, A2
    # - P2 x P2_partenaire -> B1, B2
    # - A2 x B2 -> X (cousins germains)
    
    # Fondateurs
    gpa = _ind("GPA", "M")
    gma = _ind("GMA", "F")
    
    # Parents de A (P1 et son partenaire)
    p1 = _ind("P1", "M")
    p1_part = _ind("P1P", "F")
    
    # Parents de B (P2 et son partenaire)
    p2 = _ind("P2", "M")
    p2_part = _ind("P2P", "F")

    # Famille fondatrice: GPA x GMA -> P1, P2 (frères/soeurs)
    fam_founders = Famille(id="FF", pere_id=gpa.id, mere_id=gma.id, enfants_ids=["P1", "P2"])
    
    # Famille A: P1 x P1_part -> A1, A2
    A1 = _ind("A1", "M")
    A2 = _ind("A2", "F")
    famA = Famille(id="FA", pere_id=p1.id, mere_id=p1_part.id, enfants_ids=["A1", "A2"])
    
    # Famille B: P2 x P2_part -> B1, B2
    B1 = _ind("B1", "M")
    B2 = _ind("B2", "F")
    famB = Famille(id="FB", pere_id=p2.id, mere_id=p2_part.id, enfants_ids=["B1", "B2"])
    
    # Enfant X de A2 x B2 (cousins germains: parents P1 et P2 sont frères/soeurs)
    X = _ind("X")
    fam_union = Famille(id="FU", pere_id=A2.id, mere_id=B2.id, enfants_ids=[X.id])

    individus = [gpa, gma, p1, p1_part, p2, p2_part, A1, A2, B1, B2, X]
    familles = [fam_founders, famA, famB, fam_union]

    Fx = compute_inbreeding_for_individual(X.id, individus, familles)
    assert abs(Fx - 1.0 / 16.0) < 1e-9


