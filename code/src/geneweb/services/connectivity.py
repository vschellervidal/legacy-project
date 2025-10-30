"""Service de calcul de connexité (Issue #31).

Ce module implémente le calcul des composantes connexes d'un arbre généalogique.
Une composante connexe est un groupe d'individus connectés via les relations
familiales (parent-enfant, conjoints).

Références:
- Graphe non-orienté où les nœuds sont des individus
- Arêtes entre individus connectés via familles (parents-enfants, conjoints)
- Algorithme de parcours en profondeur (DFS) pour trouver les composantes

Entrées: listes d'`Individu` et de `Famille` (modèles de domaine).
Sortie: liste de composantes connexes (chaque composante = liste d'IDs d'individus)
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Set

from geneweb.domain.models import Famille, Individu
from geneweb.io.gwb import load_gwb_minimal


def _build_adjacency_graph(
    individus: Iterable[Individu], familles: Iterable[Famille]
) -> Dict[str, Set[str]]:
    """Construit un graphe d'adjacence pour les individus.

    Le graphe est non-orienté : si A est connecté à B, alors B est connecté à A.

    Connexions créées :
    - Parent ↔ Enfant (bidirectionnel)
    - Conjoint ↔ Conjoint (via famille)

    Returns:
        Dictionnaire {id_individu: set(ids_voisins)}
    """
    # Initialiser avec tous les individus (aucun voisin pour l'instant)
    graph: Dict[str, Set[str]] = {ind.id: set() for ind in individus}

    # Pour chaque famille, créer les connexions
    for fam in familles:
        # Connexions conjoints
        if fam.pere_id and fam.mere_id:
            # Les parents sont connectés entre eux
            if fam.pere_id in graph:
                graph[fam.pere_id].add(fam.mere_id)
            if fam.mere_id in graph:
                graph[fam.mere_id].add(fam.pere_id)

        # Connexions parent-enfant (bidirectionnel)
        parents = [p for p in [fam.pere_id, fam.mere_id] if p]
        for child_id in fam.enfants_ids:
            if child_id in graph:
                # Enfant → parents
                for parent_id in parents:
                    graph[child_id].add(parent_id)
                # Parents → enfant
                for parent_id in parents:
                    if parent_id in graph:
                        graph[parent_id].add(child_id)

    return graph


def _dfs_component(node: str, graph: Dict[str, Set[str]], visited: Set[str]) -> Set[str]:
    """Parcours en profondeur pour trouver une composante connexe depuis un nœud.

    Args:
        node: ID du nœud de départ
        graph: Graphe d'adjacence
        visited: Ensemble des nœuds déjà visités (modifié sur place)

    Returns:
        Ensemble des IDs dans la même composante connexe
    """
    if node in visited:
        return set()

    component: Set[str] = set()
    stack: List[str] = [node]

    while stack:
        current = stack.pop()
        if current in visited:
            continue

        visited.add(current)
        component.add(current)

        # Ajouter tous les voisins non visités
        for neighbor in graph.get(current, set()):
            if neighbor not in visited:
                stack.append(neighbor)

    return component


def compute_connected_components(
    individus: Iterable[Individu], familles: Iterable[Famille]
) -> List[List[str]]:
    """Calcule toutes les composantes connexes du graphe généalogique.

    Une composante connexe est un groupe d'individus connectés via les relations
    familiales (parent-enfant, conjoints).

    Args:
        individus: Liste des individus
        familles: Liste des familles

    Returns:
        Liste de composantes connexes. Chaque composante est une liste d'IDs d'individus.
        Les composantes sont triées par taille décroissante (plus grande d'abord).
    """
    graph = _build_adjacency_graph(individus, familles)
    visited: Set[str] = set()
    components: List[List[str]] = []

    # Parcourir tous les nœuds non visités
    for ind in individus:
        if ind.id not in visited:
            component = _dfs_component(ind.id, graph, visited)
            if component:
                # Trier les IDs pour avoir un ordre déterministe
                components.append(sorted(list(component)))

    # Trier les composantes par taille décroissante
    components.sort(key=len, reverse=True)
    return components


def compute_connected_components_from_gwb(root_dir: str) -> List[List[str]]:
    """Charge une base GWB minimale et calcule les composantes connexes.

    Utile pour des validations rapides sur des fixtures. Cette fonction
    s'appuie sur `load_gwb_minimal` (rétrocompatible formats simple/complet).

    Args:
        root_dir: Chemin vers le répertoire racine de la base GWB

    Returns:
        Liste de composantes connexes (liste d'IDs d'individus)
    """
    individus, familles, _sources = load_gwb_minimal(root_dir)
    return compute_connected_components(individus, familles)


def get_largest_component(
    individus: Iterable[Individu], familles: Iterable[Famille]
) -> List[str]:
    """Retourne la plus grande composante connexe.

    Args:
        individus: Liste des individus
        familles: Liste des familles

    Returns:
        Liste d'IDs d'individus de la plus grande composante (vide si aucun individu)
    """
    components = compute_connected_components(individus, familles)
    return components[0] if components else []

