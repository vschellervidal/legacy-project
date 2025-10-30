"""Service de calcul de consanguinité (Issue #30).

Ce module implémente le calcul des coefficients de consanguinité F(i)
pour les individus d'un arbre généalogique en utilisant la relation de
parenté (kinship) φ(i, j).

Références:
- Méthode récursive standard: F(i) = φ(père(i), mère(i))
- φ(i, j) = (φ(père(i), j) + φ(mère(i), j)) / 2 pour i ≠ j
- φ(i, i) = (1 + F(i)) / 2

Entrées: listes d'`Individu` et de `Famille` (modèles de domaine).
Sortie: dictionnaire {id_individu: F}
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple

from geneweb.domain.models import Famille, Individu
from geneweb.io.gwb import load_gwb_minimal


ParentsMap = Dict[str, Tuple[Optional[str], Optional[str]]]


def _build_parents_map(individus: Iterable[Individu], familles: Iterable[Famille]) -> ParentsMap:
    """Construit une table id_individu -> (pere_id, mere_id).

    Les liens enfants->famille sont déterminés à partir des objets `Famille`.
    Si des individus n'ont pas de parents connus, ils sont laissés avec (None, None).
    """
    # Initialiser tous les individus avec (None, None)
    parents_map: ParentsMap = {ind.id: (None, None) for ind in individus}

    # Mettre à jour avec les parents depuis les familles
    for fam in familles:
        pere_id = fam.pere_id
        mere_id = fam.mere_id
        if not fam.enfants_ids:
            continue
        for child_id in fam.enfants_ids:
            # Ajouter l'enfant au map s'il n'y est pas déjà (cas où enfant n'est pas dans la liste initiale)
            if child_id not in parents_map:
                parents_map[child_id] = (None, None)
            # Mettre à jour avec les parents de cette famille
            parents_map[child_id] = (pere_id, mere_id)

    return parents_map


class InbreedingCalculator:
    """Calculateur de consanguinité basé sur φ (kinship) avec mémoïsation."""

    def __init__(self, individus: Iterable[Individu], familles: Iterable[Famille]) -> None:
        self.individus_index: Dict[str, Individu] = {i.id: i for i in individus}
        self.parents_map: ParentsMap = _build_parents_map(individus, familles)

        # Caches explicites pour contrôler l'ordre des dépendances mutuelles
        self._f_cache: Dict[str, float] = {}
        self._kinship_cache: Dict[Tuple[Optional[str], Optional[str]], float] = {}

    def father_of(self, ind_id: Optional[str]) -> Optional[str]:
        if not ind_id:
            return None
        return self.parents_map.get(ind_id, (None, None))[0]

    def mother_of(self, ind_id: Optional[str]) -> Optional[str]:
        if not ind_id:
            return None
        return self.parents_map.get(ind_id, (None, None))[1]

    def kinship(self, a_id: Optional[str], b_id: Optional[str]) -> float:
        """Calcule φ(a, b). Symétrique. Fondateurs -> 0 par défaut.

        Règles:
        - Si l'un est inconnu: 0
        - φ(i, i) = (1 + F(i)) / 2
        - φ(i, j) = (φ(père(i), j) + φ(mère(i), j)) / 2 pour i ≠ j
        """
        if not a_id or not b_id:
            return 0.0

        # Normaliser la paire pour garantir la symétrie du cache
        # Utiliser un tuple ordonné pour le cache
        cache_key = (a_id, b_id) if a_id <= b_id else (b_id, a_id)
        
        if cache_key in self._kinship_cache:
            return self._kinship_cache[cache_key]

        if a_id == b_id:
            # φ(i, i) = (1 + F(i)) / 2
            # Attention: F(i) peut dépendre de kinship via les parents
            # On doit calculer F(i) d'abord pour éviter la récursion infinie
            # En fait, F(i) = φ(père(i), mère(i)), donc pas de dépendance circulaire
            # car F(i) utilise kinship des parents, pas de i lui-même
            f_i = self.F(a_id)
            result = (1.0 + f_i) / 2.0
            self._kinship_cache[cache_key] = result
            return result

        # φ(i, j) pour i ≠ j
        # Formule standard: φ(i, j) = (φ(père(i), j) + φ(mère(i), j)) / 2
        # Cette formule fonctionne en remontant depuis i jusqu'à trouver j ou un ancêtre commun
        # Pour optimiser, on peut aussi remonter depuis j, mais la formule de base
        # fonctionne correctement car elle est récursive et explore tous les chemins
        fa = self.father_of(a_id)
        ma = self.mother_of(a_id)
        
        # Si les deux parents sont None, alors a_id est un fondateur
        # et φ(fondateur, j) = 0 sauf si j == fondateur (déjà géré) ou j est un descendant
        # Mais la récursion va quand même explorer depuis j jusqu'à trouver le fondateur
        if not fa and not ma:
            # a_id est un fondateur, donc on obtient 0 en remontant depuis a_id
            # Mais la vraie valeur devrait être calculée depuis b_id
            # Pour garantir la symétrie, si l'un est fondateur, on essaie depuis l'autre
            fb = self.father_of(b_id)
            mb = self.mother_of(b_id)
            if not fb and not mb:
                # Les deux sont fondateurs et différents -> 0
                result = 0.0
            else:
                # b_id n'est pas fondateur, calculer depuis b_id pour trouver a_id
                result = (self.kinship(a_id, fb) + self.kinship(a_id, mb)) / 2.0
        else:
            # Remonter depuis a_id (formule standard)
            result = (self.kinship(fa, b_id) + self.kinship(ma, b_id)) / 2.0
        
        self._kinship_cache[cache_key] = result
        return result

    def F(self, ind_id: str) -> float:
        """Coefficient de consanguinité F(ind_id).

        - Fondateur (aucun parent connu) -> 0.0
        - Sinon F(i) = φ(père(i), mère(i))
        """
        if ind_id in self._f_cache:
            return self._f_cache[ind_id]

        father = self.father_of(ind_id)
        mother = self.mother_of(ind_id)
        if not father and not mother:
            self._f_cache[ind_id] = 0.0
            return 0.0

        value = self.kinship(father, mother)
        self._f_cache[ind_id] = value
        return value


def compute_inbreeding_coefficients(
    individus: Iterable[Individu], familles: Iterable[Famille]
) -> Dict[str, float]:
    """Calcule F pour tous les individus.

    Retourne un dict {id_individu: F} (valeurs en float entre 0 et 1).
    """
    calc = InbreedingCalculator(individus, familles)
    return {ind.id: calc.F(ind.id) for ind in individus}


def compute_inbreeding_for_individual(
    ind_id: str, individus: Iterable[Individu], familles: Iterable[Famille]
) -> float:
    """Calcule F pour un individu spécifique."""
    calc = InbreedingCalculator(individus, familles)
    return calc.F(ind_id)


def compute_inbreeding_from_gwb(root_dir: str) -> Dict[str, float]:
    """Charge une base GWB minimale et calcule F pour tous les individus.

    Utile pour des validations rapides sur des fixtures. Cette fonction
    s'appuie sur `load_gwb_minimal` (rétrocompatible formats simple/complet).
    """
    individus, familles, _sources = load_gwb_minimal(root_dir)
    return compute_inbreeding_coefficients(individus, familles)


