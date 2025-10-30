from __future__ import annotations

from pathlib import Path
from typing import Literal

from geneweb.domain.models import Individu, Sexe, Famille
from geneweb.io.gwb import load_gwb_minimal, write_gwb_minimal


def _resolve_base_dir(base_dir: str | Path) -> Path:
    p = Path(base_dir)
    if not p.exists():
        raise FileNotFoundError(f"Base GWB introuvable: {base_dir}")
    return p


def add_individu(
    base_dir: str | Path,
    *,
    id: str,
    nom: str | None = None,
    prenom: str | None = None,
    sexe: Literal["M", "F", "X", None] = None,
) -> Individu:
    base_path = _resolve_base_dir(base_dir)
    individus, familles, sources = load_gwb_minimal(base_path)

    if any(ind.id == id for ind in individus):
        raise ValueError(f"Individu {id} existe déjà")

    sexe_enum = None
    if sexe:
        sexe_enum = Sexe(sexe)

    new_ind = Individu(
        id=id,
        nom=nom,
        prenom=prenom,
        sexe=sexe_enum,
    )
    individus.append(new_ind)
    write_gwb_minimal(individus, familles, base_path, sources=sources)
    return new_ind


def mod_individu(
    base_dir: str | Path,
    *,
    id: str,
    nom: str | None = None,
    prenom: str | None = None,
    sexe: Literal["M", "F", "X", None] | None = None,
) -> Individu:
    base_path = _resolve_base_dir(base_dir)
    individus, familles, sources = load_gwb_minimal(base_path)

    ind = next((x for x in individus if x.id == id), None)
    if not ind:
        raise ValueError(f"Individu {id} introuvable")

    if nom is not None:
        ind.nom = nom
    if prenom is not None:
        ind.prenom = prenom
    if sexe is not None:
        ind.sexe = Sexe(sexe) if sexe else None

    write_gwb_minimal(individus, familles, base_path, sources=sources)
    return ind


# --- Familles ---


def add_famille(
    base_dir: str | Path,
    *,
    id: str,
    pere_id: str | None = None,
    mere_id: str | None = None,
    enfants_ids: list[str] | None = None,
) -> Famille:
    base_path = _resolve_base_dir(base_dir)
    individus, familles, sources = load_gwb_minimal(base_path)

    if any(f.id == id for f in familles):
        raise ValueError(f"Famille {id} existe déjà")

    # Valider existence des personnes référencées (si fournies)
    ind_ids = {ind.id for ind in individus}
    if pere_id and pere_id not in ind_ids:
        raise ValueError(f"Père introuvable: {pere_id}")
    if mere_id and mere_id not in ind_ids:
        raise ValueError(f"Mère introuvable: {mere_id}")
    enfants_ids = enfants_ids or []
    for eid in enfants_ids:
        if eid not in ind_ids:
            raise ValueError(f"Enfant introuvable: {eid}")

    new_fam = Famille(
        id=id,
        pere_id=pere_id,
        mere_id=mere_id,
        enfants_ids=list(enfants_ids),
    )
    familles.append(new_fam)
    write_gwb_minimal(individus, familles, base_path, sources=sources)
    return new_fam


def mod_famille(
    base_dir: str | Path,
    *,
    id: str,
    pere_id: str | None = None,
    mere_id: str | None = None,
    enfants_ids: list[str] | None = None,
) -> Famille:
    base_path = _resolve_base_dir(base_dir)
    individus, familles, sources = load_gwb_minimal(base_path)

    fam = next((f for f in familles if f.id == id), None)
    if not fam:
        raise ValueError(f"Famille {id} introuvable")

    ind_ids = {ind.id for ind in individus}
    if pere_id is not None:
        if pere_id != "" and pere_id not in ind_ids:
            raise ValueError(f"Père introuvable: {pere_id}")
        fam.pere_id = pere_id or None
    if mere_id is not None:
        if mere_id != "" and mere_id not in ind_ids:
            raise ValueError(f"Mère introuvable: {mere_id}")
        fam.mere_id = mere_id or None
    if enfants_ids is not None:
        for eid in enfants_ids:
            if eid not in ind_ids:
                raise ValueError(f"Enfant introuvable: {eid}")
        fam.enfants_ids = list(enfants_ids)

    write_gwb_minimal(individus, familles, base_path, sources=sources)
    return fam


# --- Suppressions ---


def del_individu(base_dir: str | Path, *, id: str, force: bool = False) -> None:
    base_path = _resolve_base_dir(base_dir)
    individus, familles, sources = load_gwb_minimal(base_path)

    ind = next((x for x in individus if x.id == id), None)
    if not ind:
        raise ValueError(f"Individu {id} introuvable")

    # Vérifier liens
    linked = []
    for fam in familles:
        if fam.pere_id == id or fam.mere_id == id or id in fam.enfants_ids:
            linked.append(fam.id)
    if linked and not force:
        raise ValueError(f"Individu {id} lie aux familles {linked} (utiliser force=true)")

    # Si force, nettoyer les liens
    if linked:
        for fam in familles:
            if fam.pere_id == id:
                fam.pere_id = None
            if fam.mere_id == id:
                fam.mere_id = None
            if id in fam.enfants_ids:
                fam.enfants_ids = [e for e in fam.enfants_ids if e != id]

    # Supprimer l'individu
    individus = [x for x in individus if x.id != id]
    write_gwb_minimal(individus, familles, base_path, sources=sources)


def del_famille(base_dir: str | Path, *, id: str, force: bool = False) -> None:
    base_path = _resolve_base_dir(base_dir)
    individus, familles, sources = load_gwb_minimal(base_path)

    fam = next((f for f in familles if f.id == id), None)
    if not fam:
        raise ValueError(f"Famille {id} introuvable")

    # Famille avec parents/enfants => demander force
    if not force and (fam.pere_id or fam.mere_id or fam.enfants_ids):
        raise ValueError(f"Famille {id} a des liens (utiliser force=true)")

    # Nettoyer les liens (force)
    for ind in individus:
        if ind.famille_enfance_id == id:
            ind.famille_enfance_id = None
        if ind.famille_adultes and id in ind.famille_adultes:
            ind.famille_adultes = [fid for fid in ind.famille_adultes if fid != id]

    familles = [f for f in familles if f.id != id]
    write_gwb_minimal(individus, familles, base_path, sources=sources)


