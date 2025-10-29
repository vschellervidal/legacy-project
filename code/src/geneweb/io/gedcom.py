"""Sérialisation GEDCOM minimale (Issue #14).

Ce module génère un GEDCOM minimal conforme aux besoins actuels:
- En-tête `HEAD` avec quelques balises usuelles
- Individus `INDI` avec `NAME` et `SEX`
- Pied de fichier `TRLR`

Objectif: établir une base testable, extensible par la suite
pour ajouter événements, familles, etc.
"""

from __future__ import annotations

from typing import Iterable, Optional
import unicodedata

from geneweb.domain.models import Famille, Individu, Sexe, Source


def _format_name(individu: Individu) -> str:
    """Retourne le tag NAME au format GEDCOM: "Prenom/NOM/".

    - Le nom de famille est encadré par des slashes.
    - Si un champ est manquant, on le remplace par une chaîne vide.
    """

    prenom = _normalize_text(individu.prenom or "")
    nom = _normalize_text(individu.nom or "")
    # Concatène en respectant le format GEDCOM: Given /Surname/
    return f"1 NAME {prenom}/{nom}/".rstrip()


def _format_sex(individu: Individu) -> str | None:
    """Retourne la ligne SEX si le sexe est disponible.

    Mappage:
    - Sexe.M -> M
    - Sexe.F -> F
    - Sinon -> U (unknown)
    """

    if individu.sexe is None:
        return None
    if individu.sexe == Sexe.M:
        code = "M"
    elif individu.sexe == Sexe.F:
        code = "F"
    else:
        code = "U"
    return f"1 SEX {code}"


def _serialize_header() -> list[str]:
    """Génère un en-tête minimal `HEAD`.

    Certaines balises usuelles sont incluses pour compatibilité:
    - SOUR: identifiant de la source
    - GEDC / VERS
    - CHAR: encodage
    - SUBM: soumission par défaut
    """

    lines: list[str] = []
    lines.append("0 HEAD")
    lines.append("1 SOUR GENEWEBPY")
    lines.append("1 GEDC")
    lines.append("2 VERS 5.5.1")
    lines.append("1 CHAR UTF-8")
    lines.append("1 SUBM @SUBM@")
    return lines


def _serialize_trailer() -> list[str]:
    return ["0 TRLR"]


def _normalize_text(value: str) -> str:
    """Normalise le texte en NFC et remplace CR/LF/TAB par des espaces.

    - Conserve l'Unicode (UTF-8) tel quel; pas de translitération.
    - Enlève les contrôles de base susceptibles de casser les lignes GEDCOM.
    """

    if not value:
        return ""
    # Normaliser en NFC
    normalized = unicodedata.normalize("NFC", value)
    # Remplacer CR/LF/TAB par un espace
    normalized = normalized.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return normalized


def _serialize_note(note: str) -> list[str]:
    """Sérialise une note en format GEDCOM (Issue #17).

    Les notes longues sont automatiquement coupées et continuées avec 2 CONT si nécessaire.
    Limite: 255 caractères par ligne (conformité GEDCOM 5.5).
    """
    if not note or not note.strip():
        return []

    lines: list[str] = []
    # Premier ligne avec tag NOTE
    first_line = note[:255].strip()
    lines.append(f"1 NOTE {first_line}")

    # Continuer avec CONT pour le reste si nécessaire
    remaining = note[255:]
    while remaining:
        chunk = remaining[:255].strip()
        if chunk:
            lines.append(f"2 CONT {chunk}")
        remaining = remaining[255:]

    return lines


def _serialize_individu(ref: str, individu: Individu, id_to_source_ref: dict[str, str] | None = None) -> list[str]:
    """Sérialise un individu minimal en GEDCOM.

    - ref: identifiant GEDCOM (ex: "@I1@"), fourni par l'appelant
    - NAME: "Prenom/NOM/"
    - SEX: M/F/U si disponible
    - BIRT/DEAT: événements vitaux (Issue #15)
    - NOTE: note en ligne si présente (Issue #17)
    - SOUR: références aux sources si présentes (Issue #17)
    """

    lines: list[str] = []
    lines.append(f"0 {ref} INDI")
    lines.append(_format_name(individu))
    sex_line = _format_sex(individu)
    if sex_line is not None:
        lines.append(sex_line)
    # Événements vitaux (Issue #15): BIRT/DEAT avec DATE/PLAC si disponibles
    if individu.date_naissance or individu.lieu_naissance:
        lines.append("1 BIRT")
        if individu.date_naissance is not None:
            lines.append(f"2 DATE {individu.date_naissance.isoformat()}")
        if individu.lieu_naissance:
            lines.append(f"2 PLAC { _normalize_text(individu.lieu_naissance) }")
    if individu.date_deces or individu.lieu_deces:
        lines.append("1 DEAT")
        if individu.date_deces is not None:
            lines.append(f"2 DATE {individu.date_deces.isoformat()}")
        if individu.lieu_deces:
            lines.append(f"2 PLAC { _normalize_text(individu.lieu_deces) }")
    # Notes et sources (Issue #17)
    if individu.note:
        lines.extend(_serialize_note(_normalize_text(individu.note)))
    if id_to_source_ref and individu.sources:
        for source_id in individu.sources:
            if source_id in id_to_source_ref:
                lines.append(f"1 SOUR {id_to_source_ref[source_id]}")
    return lines


def _serialize_famille(
    ref: str, famille: Famille, id_to_indi_ref: dict[str, str], id_to_source_ref: dict[str, str] | None = None
) -> list[str]:
    """Sérialise une famille en GEDCOM (Issue #16, #17).

    - ref: identifiant GEDCOM (ex: "@F1@"), fourni par l'appelant
    - famille: objet Famille à sérialiser
    - id_to_indi_ref: mapping des IDs individu Python vers références GEDCOM (@Ix@)
    - id_to_source_ref: mapping des IDs source Python vers références GEDCOM (@Sx@), optionnel

    Structure GEDCOM:
    - 0 @Fx@ FAM
    - 1 HUSB @Ix@ (si pere_id existe)
    - 1 WIFE @Iy@ (si mere_id existe)
    - 1 CHIL @Iz@ (pour chaque enfant)
    - 1 NOTE ... (si note présente, Issue #17)
    - 1 SOUR @Sx@ (si sources présentes, Issue #17)
    """

    lines: list[str] = []
    lines.append(f"0 {ref} FAM")

    if famille.pere_id and famille.pere_id in id_to_indi_ref:
        lines.append(f"1 HUSB {id_to_indi_ref[famille.pere_id]}")

    if famille.mere_id and famille.mere_id in id_to_indi_ref:
        lines.append(f"1 WIFE {id_to_indi_ref[famille.mere_id]}")

    for enfant_id in famille.enfants_ids:
        if enfant_id in id_to_indi_ref:
            lines.append(f"1 CHIL {id_to_indi_ref[enfant_id]}")

    # Notes et sources (Issue #17)
    if famille.note:
        lines.extend(_serialize_note(_normalize_text(famille.note)))
    if id_to_source_ref and famille.sources:
        for source_id in famille.sources:
            if source_id in id_to_source_ref:
                lines.append(f"1 SOUR {id_to_source_ref[source_id]}")

    return lines


def serialize_gedcom_minimal(
    individus: Iterable[Individu],
    familles: Optional[Iterable[Famille]] = None,
    sources: Optional[Iterable[Source]] = None,
) -> str:
    """Génère un GEDCOM minimal pour des individus, familles et sources optionnelles (Issue #16, #17).

    Chaque individu reçoit une référence séquentielle @I{n}@ basée sur l'ordre d'itération.
    Chaque famille reçoit une référence séquentielle @F{n}@ si des familles sont fournies.
    Chaque source reçoit une référence séquentielle @S{n}@ si des sources sont fournies.
    Les références HUSB/WIFE/CHIL pointent vers les références @Ix@ créées.
    Les références SOUR pointent vers les références @Sx@ créées.
    """

    out_lines: list[str] = []
    out_lines.extend(_serialize_header())

    # Construire le mapping ID Python → référence GEDCOM pour les sources (Issue #17)
    id_to_source_ref: dict[str, str] = {}
    if sources:
        for idx, source in enumerate(sources, start=1):
            ref = f"@S{idx}@"
            id_to_source_ref[source.id] = ref
            # Sérialiser la source en tant qu'objet SOUR
            out_lines.append(f"0 {ref} SOUR")
            if source.titre:
                out_lines.append(f"1 TITL { _normalize_text(source.titre) }")
            if source.auteur:
                out_lines.append(f"1 AUTH { _normalize_text(source.auteur) }")
            if source.date_publication:
                out_lines.append(f"1 PUBL")
                out_lines.append(f"2 DATE {source.date_publication.isoformat()}")
            if source.url:
                out_lines.append(f"1 URL { _normalize_text(source.url) }")
            if source.note:
                out_lines.extend(_serialize_note(_normalize_text(source.note)))

    # Construire le mapping ID Python → référence GEDCOM pour les individus
    id_to_indi_ref: dict[str, str] = {}
    individus_list = list(individus)

    for idx, individu in enumerate(individus_list, start=1):
        ref = f"@I{idx}@"
        id_to_indi_ref[individu.id] = ref
        out_lines.extend(_serialize_individu(ref, individu, id_to_source_ref if id_to_source_ref else None))

    # Sérialiser les familles si fournies (Issue #16)
    if familles:
        for idx, famille in enumerate(familles, start=1):
            ref = f"@F{idx}@"
            out_lines.extend(_serialize_famille(ref, famille, id_to_indi_ref, id_to_source_ref if id_to_source_ref else None))

    out_lines.extend(_serialize_trailer())
    # Joindre avec des fins de lignes Unix
    return "\n".join(out_lines) + "\n"


