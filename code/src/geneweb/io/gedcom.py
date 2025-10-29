"""Sérialisation GEDCOM minimale (Issue #14).

Ce module génère un GEDCOM minimal conforme aux besoins actuels:
- En-tête `HEAD` avec quelques balises usuelles
- Individus `INDI` avec `NAME` et `SEX`
- Pied de fichier `TRLR`

Objectif: établir une base testable, extensible par la suite
pour ajouter événements, familles, etc.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional
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


# ============================================================================
# Parsing GEDCOM (Issue #21)
# ============================================================================


def _parse_gedcom_line(line: str) -> tuple[int, str, str] | None:
    """Parse une ligne GEDCOM et retourne (level, tag, value) ou None si invalide.

    Format: "LEVEL TAG VALUE" ou "LEVEL @REF@ TYPE"
    """
    line = line.rstrip()
    if not line:
        return None

    parts = line.split(None, 2)
    if len(parts) < 2:
        return None

    try:
        level = int(parts[0])
        tag = parts[1]
        value = parts[2] if len(parts) > 2 else ""
        return (level, tag, value)
    except ValueError:
        return None


def _parse_name_field(value: str) -> tuple[str | None, str | None]:
    """Parse un champ NAME GEDCOM "Given/Surname/" vers (prenom, nom).

    Exemple: "Jean/DUPONT/" -> ("Jean", "DUPONT")
    """
    if not value:
        return (None, None)

    # Format: "Given/Surname/" ou "/Surname/" ou "Given/"
    parts = value.split("/")
    prenom = parts[0].strip() if parts[0] else None
    nom = parts[1].strip() if len(parts) > 1 and parts[1] else None
    return (prenom, nom)


def _parse_date(value: str) -> date | None:
    """Parse une date GEDCOM (format ISO YYYY-MM-DD ou approximations).

    Support minimal: YYYY-MM-DD uniquement pour l'instant.
    """
    if not value:
        return None
    try:
        # Format ISO simple YYYY-MM-DD
        return date.fromisoformat(value)
    except ValueError:
        # Ignorer les dates malformées pour l'instant
        return None


def _parse_sex(value: str) -> Sexe | None:
    """Parse un champ SEX GEDCOM (M/F/U) vers Sexe enum."""
    value_upper = value.upper().strip()
    if value_upper == "M":
        return Sexe.M
    if value_upper == "F":
        return Sexe.F
    if value_upper in ("U", "X"):
        return Sexe.X
    return None


def parse_gedcom_minimal(gedcom_text: str) -> tuple[list[Individu], list[Famille]]:
    """Parse un GEDCOM minimal et retourne liste d'individus et familles (Issue #21).

    Support minimal:
    - INDI avec NAME, SEX, BIRT (DATE/PLAC), DEAT (DATE/PLAC)
    - FAM avec HUSB, WIFE, CHIL

    Args:
        gedcom_text: Contenu GEDCOM en texte

    Returns:
        Tuple (liste_individus, liste_familles)
    """
    lines = gedcom_text.splitlines()
    individus: list[Individu] = []
    familles: list[Famille] = []

    # Mapping GEDCOM ref (@Ix@) -> ID Python
    gedcom_ref_to_python_id: dict[str, str] = {}
    python_id_counter = 1

    # État du parsing
    current_indi: dict[str, Any] | None = None
    current_fam: dict[str, Any] | None = None
    current_level = -1
    current_tag = ""
    in_birt = False
    in_deat = False

    for line in lines:
        parsed = _parse_gedcom_line(line)
        if not parsed:
            continue

        level, tag, value = parsed

        # Nouveau record (level 0)
        if level == 0:
            # Finir le record précédent si nécessaire
            if current_indi:
                # Créer l'individu
                indi_id = current_indi.get("id", f"I{python_id_counter}")
                python_id_counter += 1
                individu = Individu(
                    id=indi_id,
                    nom=current_indi.get("nom"),
                    prenom=current_indi.get("prenom"),
                    sexe=current_indi.get("sexe"),
                    date_naissance=current_indi.get("date_naissance"),
                    lieu_naissance=current_indi.get("lieu_naissance"),
                    date_deces=current_indi.get("date_deces"),
                    lieu_deces=current_indi.get("lieu_deces"),
                )
                individus.append(individu)
                if "gedcom_ref" in current_indi:
                    gedcom_ref_to_python_id[current_indi["gedcom_ref"]] = indi_id
                current_indi = None

            if current_fam:
                # Créer la famille
                fam_id = current_fam.get("id", f"F{python_id_counter}")
                python_id_counter += 1
                famille = Famille(
                    id=fam_id,
                    pere_id=current_fam.get("pere_id"),
                    mere_id=current_fam.get("mere_id"),
                    enfants_ids=current_fam.get("enfants_ids", []),
                )
                familles.append(famille)
                current_fam = None

            # Début nouveau record
            # Format GEDCOM: "0 @REF@ TYPE" où tag="@REF@" et value="TYPE"
            if tag.startswith("@") and value == "INDI":
                # 0 @I1@ INDI
                current_indi = {"gedcom_ref": tag, "id": tag}
                current_fam = None
                in_birt = False
                in_deat = False
            elif tag.startswith("@") and value == "FAM":
                # 0 @F1@ FAM
                current_fam = {"gedcom_ref": tag, "id": tag}
                current_indi = None

            current_level = 0
            continue

        # Dans un bloc INDI
        if current_indi and level == 1:
            if tag == "NAME":
                prenom, nom = _parse_name_field(value)
                current_indi["prenom"] = prenom
                current_indi["nom"] = nom
            elif tag == "SEX":
                current_indi["sexe"] = _parse_sex(value)
            elif tag == "BIRT":
                in_birt = True
                in_deat = False
            elif tag == "DEAT":
                in_deat = True
                in_birt = False
            current_tag = tag

        # Sous-tags niveau 2 dans INDI
        if current_indi and level == 2:
            if current_tag == "BIRT" or in_birt:
                if tag == "DATE":
                    current_indi["date_naissance"] = _parse_date(value)
                elif tag == "PLAC":
                    current_indi["lieu_naissance"] = value.strip()
            elif current_tag == "DEAT" or in_deat:
                if tag == "DATE":
                    current_indi["date_deces"] = _parse_date(value)
                elif tag == "PLAC":
                    current_indi["lieu_deces"] = value.strip()

        # Dans un bloc FAM
        if current_fam and level == 1:
            if tag == "HUSB":
                # Convertir référence GEDCOM vers ID Python
                husb_id = gedcom_ref_to_python_id.get(value.strip(), value.strip("@"))
                current_fam["pere_id"] = husb_id
            elif tag == "WIFE":
                wife_id = gedcom_ref_to_python_id.get(value.strip(), value.strip("@"))
                current_fam["mere_id"] = wife_id
            elif tag == "CHIL":
                child_id = gedcom_ref_to_python_id.get(value.strip(), value.strip("@"))
                if "enfants_ids" not in current_fam:
                    current_fam["enfants_ids"] = []
                current_fam["enfants_ids"].append(child_id)

    # Finaliser les derniers records
    if current_indi:
        indi_id = current_indi.get("id", f"I{python_id_counter}")
        individu = Individu(
            id=indi_id,
            nom=current_indi.get("nom"),
            prenom=current_indi.get("prenom"),
            sexe=current_indi.get("sexe"),
            date_naissance=current_indi.get("date_naissance"),
            lieu_naissance=current_indi.get("lieu_naissance"),
            date_deces=current_indi.get("date_deces"),
            lieu_deces=current_indi.get("lieu_deces"),
        )
        individus.append(individu)

    if current_fam:
        fam_id = current_fam.get("id", f"F{python_id_counter}")
        famille = Famille(
            id=fam_id,
            pere_id=current_fam.get("pere_id"),
            mere_id=current_fam.get("mere_id"),
            enfants_ids=current_fam.get("enfants_ids", []),
        )
        familles.append(famille)

    return (individus, familles)


def load_gedcom(file_path: str | Path) -> tuple[list[Individu], list[Famille]]:
    """Charge un fichier GEDCOM et retourne individus et familles (Issue #21).

    Args:
        file_path: Chemin vers le fichier GEDCOM

    Returns:
        Tuple (liste_individus, liste_familles)
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="ignore")
    return parse_gedcom_minimal(content)

