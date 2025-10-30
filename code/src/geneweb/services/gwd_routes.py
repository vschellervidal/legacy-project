"""Services pour les routes HTTP gwd (Issue #34).

Ce module implémente les routes de lecture (consultation) du serveur GeneWeb.
Pour l'instant, les routes retournent des données structurées (JSON).
Le rendu HTML sera ajouté progressivement.
"""

from __future__ import annotations

from pathlib import Path

from geneweb.io.gwb import load_gwb_minimal


def get_person_page(base_dir: str, person_id: str | None = None) -> dict:
    """Génère la page d'accueil ou la fiche d'un individu (route `""` ou `PERSO`).
    
    Args:
        base_dir: Chemin vers le répertoire GWB
        person_id: ID de l'individu (optionnel, pour fiche individu)
    
    Returns:
        Dict avec les données de la page (à convertir en HTML plus tard)
    """
    individus, familles, sources = load_gwb_minimal(base_dir)
    
    if person_id:
        # Chercher l'individu
        person = next((ind for ind in individus if ind.id == person_id), None)
        if not person:
            raise ValueError(f"Individu {person_id} introuvable")
        
        return {
            "type": "person",
            "person": {
                "id": person.id,
                "nom": person.nom,
                "prenom": person.prenom,
                "sexe": person.sexe.value if person.sexe else None,
                "date_naissance": str(person.date_naissance) if person.date_naissance else None,
                "lieu_naissance": person.lieu_naissance,
                "date_deces": str(person.date_deces) if person.date_deces else None,
                "lieu_deces": person.lieu_deces,
                "note": person.note,
            },
        }
    
    # Page d'accueil : retourner un résumé de la base
    return {
        "type": "home",
        "base": {
            "total_individus": len(individus),
            "total_familles": len(familles),
            "total_sources": len(sources),
        },
    }


def search_persons(base_dir: str, query: str | None = None) -> dict:
    """Recherche d'individus (route `S` ou `NG`).
    
    Args:
        base_dir: Chemin vers le répertoire GWB
        query: Terme de recherche (optionnel)
    
    Returns:
        Dict avec les résultats de recherche
    """
    individus, _, _ = load_gwb_minimal(base_dir)
    
    if not query:
        # Retourner tous les individus (triés par nom)
        sorted_individus = sorted(
            individus,
            key=lambda ind: (ind.nom or "", ind.prenom or ""),
        )
        return {
            "type": "search_all",
            "results": [
                {
                    "id": ind.id,
                    "nom": ind.nom,
                    "prenom": ind.prenom,
                }
                for ind in sorted_individus
            ],
            "total": len(sorted_individus),
        }
    
    # Recherche par nom/prénom
    query_lower = query.lower()
    results = []
    for ind in individus:
        nom = (ind.nom or "").lower()
        prenom = (ind.prenom or "").lower()
        if query_lower in nom or query_lower in prenom:
            results.append({
                "id": ind.id,
                "nom": ind.nom,
                "prenom": ind.prenom,
            })
    
    return {
        "type": "search",
        "query": query,
        "results": results,
        "total": len(results),
    }


def get_family_page(base_dir: str, family_id: str | None = None) -> dict:
    """Génère la fiche d'une famille (route `F`).
    
    Args:
        base_dir: Chemin vers le répertoire GWB
        family_id: ID de la famille (optionnel, peut être dérivé d'un individu)
    
    Returns:
        Dict avec les données de la famille
    """
    individus, familles, _ = load_gwb_minimal(base_dir)
    
    if not family_id:
        raise ValueError("family_id requis pour la route F")
    
    famille = next((fam for fam in familles if fam.id == family_id), None)
    if not famille:
        raise ValueError(f"Famille {family_id} introuvable")
    
    # Récupérer les détails des parents et enfants
    pere = next((ind for ind in individus if ind.id == famille.pere_id), None) if famille.pere_id else None
    mere = next((ind for ind in individus if ind.id == famille.mere_id), None) if famille.mere_id else None
    enfants = [ind for ind in individus if ind.id in famille.enfants_ids]
    
    return {
        "type": "family",
        "family": {
            "id": famille.id,
            "pere": {
                "id": pere.id,
                "nom": pere.nom,
                "prenom": pere.prenom,
            } if pere else None,
            "mere": {
                "id": mere.id,
                "nom": mere.nom,
                "prenom": mere.prenom,
            } if mere else None,
            "enfants": [
                {
                    "id": enfant.id,
                    "nom": enfant.nom,
                    "prenom": enfant.prenom,
                }
                for enfant in enfants
            ],
            "note": famille.note,
        },
    }


def get_ascendance(base_dir: str, person_id: str) -> dict:
    """Calcule l'ascendance d'un individu (route `A`).
    
    Args:
        base_dir: Chemin vers le répertoire GWB
        person_id: ID de l'individu
    
    Returns:
        Dict avec l'arbre d'ascendance (2 parents par niveau lorsque disponibles)
    """
    individus, familles, _ = load_gwb_minimal(base_dir)

    # Index accélérateurs
    ind_by_id = {ind.id: ind for ind in individus}
    fam_by_id = {fam.id: fam for fam in familles}
    child_to_family: dict[str, str] = {}
    for fam in familles:
        for child_id in fam.enfants_ids:
            # Si un enfant apparaît dans plusieurs familles (cas rares),
            # on garde la première occurrence.
            child_to_family.setdefault(child_id, fam.id)

    if person_id not in ind_by_id:
        raise ValueError(f"Individu {person_id} introuvable")

    # BFS sur les ascendants avec niveaux, pour capturer père et mère
    max_levels = 5
    visited: set[str] = set()
    queue: list[tuple[str, int]] = [(person_id, 0)]
    ancestors: list[dict] = []

    while queue:
        current_id, level = queue.pop(0)
        if current_id in visited or level > max_levels:
            continue
        visited.add(current_id)

        person = ind_by_id.get(current_id)
        if not person:
            continue

        # Ajoute la personne courante au résultat
        ancestors.append(
            {
                "id": person.id,
                "nom": person.nom,
                "prenom": person.prenom,
                "level": level,
            }
        )

        # Ajouter les parents pour le prochain niveau
        if level < max_levels:
            # D'abord essayer via la famille d'enfance si elle est présente
            fam_id = person.famille_enfance_id
            # Sinon, reconstruire via l'index enfant -> famille (format GWB minimal)
            if not fam_id:
                fam_id = child_to_family.get(person.id)
            if fam_id:
                fam = fam_by_id.get(fam_id)
                if fam:
                    if fam.pere_id:
                        queue.append((fam.pere_id, level + 1))
                    if fam.mere_id:
                        queue.append((fam.mere_id, level + 1))

    return {
        "type": "ascendance",
        "person_id": person_id,
        "ancestors": ancestors,
    }


def get_descendance(base_dir: str, person_id: str) -> dict:
	"""Calcule la descendance d'un individu (route `D`).
	
	Args:
		base_dir: Chemin vers le répertoire GWB
		person_id: ID de l'individu
	
	Returns:
		Dict avec l'arbre de descendance
	"""
	individus, familles, _ = load_gwb_minimal(base_dir)
	
	person = next((ind for ind in individus if ind.id == person_id), None)
	if not person:
		raise ValueError(f"Individu {person_id} introuvable")
	
	# Trouver toutes les familles où cette personne est parent
	descendance = []
	processed_ids = set()
	
	# Créer un index des individus et familles pour accès rapide
	individus_dict = {ind.id: ind for ind in individus}
	familles_dict = {fam.id: fam for fam in familles}
	
	def add_descendants(current_person_id: str, level: int = 0, max_levels: int = 5) -> None:
		if current_person_id in processed_ids or level >= max_levels:
			return
		processed_ids.add(current_person_id)
		
		current_person = individus_dict.get(current_person_id)
		if not current_person:
			return
		
		descendance.append({
			"id": current_person.id,
			"nom": current_person.nom,
			"prenom": current_person.prenom,
			"level": level,
		})
		
		# Chercher toutes les familles où cette personne est parent
		for famille in familles:
			if famille.pere_id == current_person_id or famille.mere_id == current_person_id:
				for enfant_id in famille.enfants_ids:
					if enfant_id and enfant_id not in processed_ids:
						add_descendants(enfant_id, level + 1, max_levels)
	
	# Démarrer avec la personne initiale (niveau 0)
	current_person = individus_dict.get(person_id)
	if current_person:
		descendance.append({
			"id": current_person.id,
			"nom": current_person.nom,
			"prenom": current_person.prenom,
			"level": 0,
		})
		processed_ids.add(person_id)
	
	# Ajouter les descendants
	for famille in familles:
		if famille.pere_id == person_id or famille.mere_id == person_id:
			for enfant_id in famille.enfants_ids:
				if enfant_id:
					add_descendants(enfant_id, level=1, max_levels=5)
	
	return {
		"type": "descendance",
		"person_id": person_id,
		"descendants": descendance,
	}


def get_notes(base_dir: str, note_file: str | None = None, ajax: bool = False) -> dict:
    """Récupère les notes (route `NOTES`).
    
    Args:
        base_dir: Chemin vers le répertoire GWB
        note_file: Fichier de notes spécifique (optionnel)
        ajax: Mode AJAX (retourne JSON)
    
    Returns:
        Dict avec les notes
    """
    individus, familles, sources = load_gwb_minimal(base_dir)
    
    # Récupérer toutes les notes des individus
    person_notes = []
    for ind in individus:
        if ind.note:
            person_notes.append({
                "type": "person",
                "id": ind.id,
                "nom": ind.nom,
                "prenom": ind.prenom,
                "note": ind.note,
            })
    
    # Récupérer toutes les notes des familles
    family_notes = []
    for fam in familles:
        if fam.note:
            family_notes.append({
                "type": "family",
                "id": fam.id,
                "note": fam.note,
            })
    
    # Récupérer toutes les notes des sources
    source_notes = []
    for src in sources:
        if src.note:
            source_notes.append({
                "type": "source",
                "id": src.id,
                "titre": src.titre,
                "note": src.note,
            })
    
    return {
        "type": "notes",
        "person_notes": person_notes,
        "family_notes": family_notes,
        "source_notes": source_notes,
        "total": len(person_notes) + len(family_notes) + len(source_notes),
    }

