"""Lecture et écriture GWB minimales (Issues #13, #22, #23, #24, #25, #26).

Format minimal supporté à ce stade:
- Fichier `index.json` placé à la racine du dossier GWB
- Deux formats supportés (rétrocompatibilité):
  1. Format simple (Issues #13-23): liste d'individus
  2. Format complet (Issue #24+): objet {"individus": [...], "familles": [...], "sources": [...]}

Individus: {"id", "nom", "prenom", "sexe", "date_naissance", "lieu_naissance", "date_deces", "lieu_deces", "note", "sources": [...]}
Familles: {"id", "pere_id", "mere_id", "enfants_ids": [...], "note", "sources": [...]}
Sources: {"id", "titre", "auteur", "date_publication", "url", "fichier", "note"}

Normalisation Unicode (Issue #26): toutes les chaînes sont normalisées en NFC pour assurer
la parité avec la sérialisation GEDCOM. Encodage UTF-8 avec ensure_ascii=False.

Objectif: charger/écrire les individus, familles et sources avec métadonnées pour amorcer
le portage; la prise en charge du format GWB natif sera ajoutée ensuite.
"""

from __future__ import annotations

import json
import unicodedata
from datetime import date
from pathlib import Path
from typing import Iterable, List

from geneweb.domain.models import Famille, Individu, Sexe, Source


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


def _parse_date_iso(value: object) -> date | None:
    """Parse une date au format ISO YYYY-MM-DD."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        return None


def _normalize_unicode(value: str | None) -> str | None:
    """Normalise une chaîne Unicode en NFC (Issue #26).

    Cette fonction assure la parité avec la sérialisation GEDCOM qui utilise aussi
    la normalisation NFC. Les données stockées dans GWB seront donc dans une forme
    canonique cohérente.

    Args:
        value: Chaîne à normaliser ou None

    Returns:
        Chaîne normalisée en NFC ou None si l'entrée était None
    """
    if value is None:
        return None
    if not value:
        return ""
    # Normaliser en NFC (Canonical Composition)
    return unicodedata.normalize("NFC", value)


def load_gwb_minimal(root_dir: str | Path) -> tuple[List[Individu], List[Famille], List[Source]]:
    """Charge les individus, familles et sources depuis `root_dir/index.json` (Issues #13, #23, #24, #25).

    Supporte deux formats pour rétrocompatibilité:
    - Format simple (ancien): liste d'individus directement
    - Format complet (nouveau): objet {"individus": [...], "familles": [...], "sources": [...]}

    Renvoie un tuple (liste_individus, liste_familles, liste_sources) avec:
    - Individus: id/nom/prenom/sexe + date_naissance/lieu_naissance/date_deces/lieu_deces + note/sources
    - Familles: id/pere_id/mere_id/enfants_ids + note/sources
    - Sources: id/titre/auteur/date_publication/url/fichier/note
    """

    root_path = Path(root_dir)
    index_path = root_path / "index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Index GWB minimal introuvable: {index_path}")

    data = json.loads(index_path.read_text(encoding="utf-8"))

    individus: list[Individu] = []
    familles: list[Famille] = []
    sources: list[Source] = []

    # Détecter le format (rétrocompatibilité)
    if isinstance(data, list):
        # Format ancien (liste simple d'individus)
        for item in data:
            if not isinstance(item, dict):
                continue
            iid = str(item.get("id", "")).strip()
            if not iid:
                continue
            nom = _normalize_unicode(item.get("nom"))
            prenom = _normalize_unicode(item.get("prenom"))
            sexe = _parse_sexe(item.get("sexe"))
            date_naissance = _parse_date_iso(item.get("date_naissance"))
            lieu_naissance = _normalize_unicode(item.get("lieu_naissance"))
            date_deces = _parse_date_iso(item.get("date_deces"))
            lieu_deces = _normalize_unicode(item.get("lieu_deces"))
            # Notes et sources (Issue #25)
            note = _normalize_unicode(item.get("note"))
            sources_ids = item.get("sources", [])
            if not isinstance(sources_ids, list):
                sources_ids = []
            individus.append(
                Individu(
                    id=iid,
                    nom=nom,
                    prenom=prenom,
                    sexe=sexe,
                    date_naissance=date_naissance,
                    lieu_naissance=lieu_naissance,
                    date_deces=date_deces,
                    lieu_deces=lieu_deces,
                    note=note,
                    sources=[str(sid).strip() for sid in sources_ids if sid],
                )
            )
    elif isinstance(data, dict):
        # Format nouveau (objet avec individus et familles)
        individus_data = data.get("individus", [])
        familles_data = data.get("familles", [])

        # Parser les individus
        for item in individus_data:
            if not isinstance(item, dict):
                continue
            iid = str(item.get("id", "")).strip()
            if not iid:
                continue
            nom = _normalize_unicode(item.get("nom"))
            prenom = _normalize_unicode(item.get("prenom"))
            sexe = _parse_sexe(item.get("sexe"))
            date_naissance = _parse_date_iso(item.get("date_naissance"))
            lieu_naissance = _normalize_unicode(item.get("lieu_naissance"))
            date_deces = _parse_date_iso(item.get("date_deces"))
            lieu_deces = _normalize_unicode(item.get("lieu_deces"))
            # Notes et sources (Issue #25)
            note = _normalize_unicode(item.get("note"))
            sources_ids = item.get("sources", [])
            if not isinstance(sources_ids, list):
                sources_ids = []
            individus.append(
                Individu(
                    id=iid,
                    nom=nom,
                    prenom=prenom,
                    sexe=sexe,
                    date_naissance=date_naissance,
                    lieu_naissance=lieu_naissance,
                    date_deces=date_deces,
                    lieu_deces=lieu_deces,
                    note=note,
                    sources=[str(sid).strip() for sid in sources_ids if sid],
                )
            )

        # Parser les familles (Issue #24)
        for item in familles_data:
            if not isinstance(item, dict):
                continue
            fid = str(item.get("id", "")).strip()
            if not fid:
                continue
            pere_id = item.get("pere_id")
            mere_id = item.get("mere_id")
            enfants_ids = item.get("enfants_ids", [])
            if not isinstance(enfants_ids, list):
                enfants_ids = []
            # Nettoyer les IDs d'enfants (convertir en str, enlever vides)
            enfants_ids_clean = [str(eid).strip() for eid in enfants_ids if eid and str(eid).strip()]
            # Notes et sources (Issue #25)
            note = item.get("note")
            sources_ids = item.get("sources", [])
            if not isinstance(sources_ids, list):
                sources_ids = []
            familles.append(
                Famille(
                    id=fid,
                    pere_id=pere_id if pere_id else None,
                    mere_id=mere_id if mere_id else None,
                    enfants_ids=enfants_ids_clean,
                    note=note,
                    sources=[str(sid).strip() for sid in sources_ids if sid],
                )
            )

        # Parser les sources (Issue #25)
        sources_data = data.get("sources", [])
        for item in sources_data:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("id", "")).strip()
            if not sid:
                continue
            titre = _normalize_unicode(item.get("titre"))
            auteur = _normalize_unicode(item.get("auteur"))
            date_publication = _parse_date_iso(item.get("date_publication"))
            url = _normalize_unicode(item.get("url"))
            fichier = _normalize_unicode(item.get("fichier"))
            note = _normalize_unicode(item.get("note"))
            sources.append(
                Source(
                    id=sid,
                    titre=titre,
                    auteur=auteur,
                    date_publication=date_publication,
                    url=url,
                    fichier=fichier,
                    note=note,
                )
            )
    else:
        raise ValueError("index.json invalide: attendu une liste ou un objet")

    return (individus, familles, sources)


def _serialize_sexe(sexe: Sexe | None) -> str | None:
    """Sérialise un Sexe enum vers une chaîne JSON."""
    if sexe is None:
        return None
    return sexe.value


def write_gwb_minimal(
    individus: Iterable[Individu],
    familles: Iterable[Famille],
    root_dir: str | Path,
    sources: Iterable[Source] | None = None,
) -> None:
    """Écrit les individus, familles et sources dans `root_dir/index.json` (Issues #22, #23, #24, #25).

    Args:
        individus: Liste d'individus à écrire (avec événements vitaux et métadonnées)
        familles: Liste de familles à écrire (avec métadonnées)
        root_dir: Répertoire GWB cible où créer index.json
        sources: Liste de sources à écrire (Issue #25, optionnel)

    Raises:
        OSError: Si le répertoire ne peut pas être créé ou le fichier écrit
        ValueError: Si les données sont invalides

    Note:
        Utilise le format complet (objet {"individus": [...], "familles": [...], "sources": [...]})
        si des familles ou sources sont présentes, sinon format simple pour rétrocompatibilité.
    """
    root_path = Path(root_dir)
    # Créer le répertoire s'il n'existe pas
    root_path.mkdir(parents=True, exist_ok=True)

    index_path = root_path / "index.json"

    # Sérialiser les individus
    individus_data: list[dict[str, str | None]] = []
    for ind in individus:
        if not ind.id or not ind.id.strip():
            continue  # Ignorer les individus sans ID valide

        item: dict[str, str | None] = {
            "id": ind.id.strip(),
        }

        # Ajouter nom/prenom/sexe seulement s'ils sont définis (normalisation Unicode, Issue #26)
        if ind.nom is not None:
            item["nom"] = _normalize_unicode(ind.nom)
        if ind.prenom is not None:
            item["prenom"] = _normalize_unicode(ind.prenom)
        if ind.sexe is not None:
            sexe_str = _serialize_sexe(ind.sexe)
            if sexe_str is not None:
                item["sexe"] = sexe_str

        # Événements vitaux (Issue #23) avec normalisation Unicode (Issue #26)
        if ind.date_naissance is not None:
            item["date_naissance"] = ind.date_naissance.isoformat()
        if ind.lieu_naissance is not None:
            item["lieu_naissance"] = _normalize_unicode(ind.lieu_naissance)
        if ind.date_deces is not None:
            item["date_deces"] = ind.date_deces.isoformat()
        if ind.lieu_deces is not None:
            item["lieu_deces"] = _normalize_unicode(ind.lieu_deces)

        # Notes et sources (Issue #25) avec normalisation Unicode (Issue #26)
        if ind.note is not None:
            item["note"] = _normalize_unicode(ind.note)
        if ind.sources:
            item["sources"] = ind.sources

        individus_data.append(item)

    # Sérialiser les familles (Issue #24)
    familles_data: list[dict[str, str | list[str] | None]] = []
    for fam in familles:
        if not fam.id or not fam.id.strip():
            continue  # Ignorer les familles sans ID valide

        item: dict[str, str | list[str] | None] = {
            "id": fam.id.strip(),
        }

        if fam.pere_id:
            item["pere_id"] = fam.pere_id
        if fam.mere_id:
            item["mere_id"] = fam.mere_id
        if fam.enfants_ids:
            item["enfants_ids"] = fam.enfants_ids

        # Notes et sources (Issue #25) avec normalisation Unicode (Issue #26)
        if fam.note is not None:
            item["note"] = _normalize_unicode(fam.note)
        if fam.sources:
            item["sources"] = fam.sources

        familles_data.append(item)

    # Sérialiser les sources (Issue #25)
    sources_data: list[dict[str, str | None]] = []
    if sources:
        for src in sources:
            if not src.id or not src.id.strip():
                continue  # Ignorer les sources sans ID valide

            item: dict[str, str | None] = {
                "id": src.id.strip(),
            }

            if src.titre is not None:
                item["titre"] = _normalize_unicode(src.titre)
            if src.auteur is not None:
                item["auteur"] = _normalize_unicode(src.auteur)
            if src.date_publication is not None:
                item["date_publication"] = src.date_publication.isoformat()
            if src.url is not None:
                item["url"] = _normalize_unicode(src.url)
            if src.fichier is not None:
                item["fichier"] = _normalize_unicode(src.fichier)
            if src.note is not None:
                item["note"] = _normalize_unicode(src.note)

            sources_data.append(item)

    # Choisir le format selon si on a des familles ou sources
    if familles_data or sources_data:
        # Format complet avec familles et/ou sources
        output_data: dict[str, list] = {
            "individus": individus_data,
            "familles": familles_data,
        }
        if sources_data:
            output_data["sources"] = sources_data
    else:
        # Format simple (rétrocompatibilité) : liste d'individus uniquement
        output_data = individus_data

    # Écrire le fichier JSON
    index_path.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


