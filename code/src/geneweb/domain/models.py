"""Modèles de domaine pour GeneWeb Python.

Ce module définit les structures de données de base pour représenter
les entités généalogiques : individus, familles, événements et sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

import pydantic


class Sexe(Enum):
    """Sexe d'un individu."""

    M = "M"  # Masculin
    F = "F"  # Féminin
    X = "X"  # Non spécifié


class TypeEvenement(Enum):
    """Types d'événements généalogiques."""

    NAISSANCE = "BIRTH"
    BAPTEME = "BAPTISM"
    MARIAGE = "MARRIAGE"
    DECES = "DEATH"
    ENTERREMENT = "BURIAL"
    DIVORCE = "DIVORCE"
    AUTRE = "OTHER"


@dataclass
class Individu:
    """Représente un individu dans l'arbre généalogique."""

    # Identifiant unique
    id: str

    # Informations personnelles
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[Sexe] = None

    # Dates de naissance et décès
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = None
    date_deces: Optional[date] = None
    lieu_deces: Optional[str] = None

    # Références aux familles
    famille_enfance_id: Optional[str] = None
    famille_adultes: list[str] = field(default_factory=list)  # IDs des familles où il est parent

    # Métadonnées
    note: Optional[str] = None
    sources: list[str] = field(default_factory=list)  # IDs des sources


@dataclass
class Famille:
    """Représente une famille (couple et enfants)."""

    # Identifiant unique
    id: str

    # Références aux parents
    pere_id: Optional[str] = None
    mere_id: Optional[str] = None

    # Références aux enfants
    enfants_ids: list[str] = field(default_factory=list)

    # Références aux événements familiaux
    evenements: list[str] = field(default_factory=list)  # IDs des événements

    # Métadonnées
    note: Optional[str] = None
    sources: list[str] = field(default_factory=list)  # IDs des sources


@dataclass
class Evenement:
    """Représente un événement généalogique."""

    # Identifiant unique
    id: str

    # Type d'événement
    type: TypeEvenement

    # Date et lieu
    date: Optional[date] = None
    lieu: Optional[str] = None

    # Références aux personnes concernées
    personnes_ids: list[str] = field(default_factory=list)

    # Informations complémentaires
    note: Optional[str] = None
    sources: list[str] = field(default_factory=list)  # IDs des sources


@dataclass
class Source:
    """Représente une source documentaire."""

    # Identifiant unique
    id: str

    # Informations sur la source
    titre: Optional[str] = None
    auteur: Optional[str] = None
    date_publication: Optional[date] = None

    # Références
    url: Optional[str] = None
    fichier: Optional[str] = None

    # Métadonnées
    note: Optional[str] = None


# Modèles Pydantic pour la sérialisation/désérialisation
class IndividuSchema(pydantic.BaseModel):
    """Schema Pydantic pour Individu."""

    id: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[str] = None  # "M", "F", "X"
    date_naissance: Optional[str] = None  # Format ISO: YYYY-MM-DD
    lieu_naissance: Optional[str] = None
    date_deces: Optional[str] = None
    lieu_deces: Optional[str] = None
    famille_enfance_id: Optional[str] = None
    famille_adultes: list[str] = pydantic.Field(default_factory=list)
    note: Optional[str] = None
    sources: list[str] = pydantic.Field(default_factory=list)

    class Config:
        """Configuration Pydantic."""

        frozen = True  # Immutable


class FamilleSchema(pydantic.BaseModel):
    """Schema Pydantic pour Famille."""

    id: str
    pere_id: Optional[str] = None
    mere_id: Optional[str] = None
    enfants_ids: list[str] = pydantic.Field(default_factory=list)
    evenements: list[str] = pydantic.Field(default_factory=list)
    note: Optional[str] = None
    sources: list[str] = pydantic.Field(default_factory=list)

    class Config:
        """Configuration Pydantic."""

        frozen = True  # Immutable


class EvenementSchema(pydantic.BaseModel):
    """Schema Pydantic pour Evenement."""

    id: str
    type: str  # TypeEvenement enum
    date: Optional[str] = None  # Format ISO: YYYY-MM-DD
    lieu: Optional[str] = None
    personnes_ids: list[str] = pydantic.Field(default_factory=list)
    note: Optional[str] = None
    sources: list[str] = pydantic.Field(default_factory=list)

    class Config:
        """Configuration Pydantic."""

        frozen = True  # Immutable


class SourceSchema(pydantic.BaseModel):
    """Schema Pydantic pour Source."""

    id: str
    titre: Optional[str] = None
    auteur: Optional[str] = None
    date_publication: Optional[str] = None  # Format ISO: YYYY-MM-DD
    url: Optional[str] = None
    fichier: Optional[str] = None
    note: Optional[str] = None

    class Config:
        """Configuration Pydantic."""

        frozen = True  # Immutable

