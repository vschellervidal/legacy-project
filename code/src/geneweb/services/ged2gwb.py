"""Service Python natif pour convertir GEDCOM vers GWB (Issue #28).

Ce service utilise l'implémentation Python native plutôt que le bridge OCaml.
Il parse le fichier GEDCOM via parse_gedcom_minimal puis écrit en GWB via write_gwb_minimal.
"""

from __future__ import annotations

from pathlib import Path

from geneweb.io.gedcom import load_gedcom
from geneweb.io.gwb import write_gwb_minimal


def ged2gwb_python(input_file: str | Path, output_dir: str | Path) -> None:
	"""Convertit un fichier GEDCOM en répertoire GWB en utilisant l'implémentation Python native.

	Args:
		input_file: Fichier GEDCOM d'entrée
		output_dir: Répertoire GWB de sortie (sera créé si nécessaire)

	Raises:
		FileNotFoundError: Si le fichier GEDCOM est introuvable
		ValueError: Si les données sont invalides
	"""
	input_path = Path(input_file)
	if not input_path.exists():
		raise FileNotFoundError(f"Fichier GEDCOM introuvable: {input_file}")

	# Parser le GEDCOM en individus et familles (Issue #21)
	individus, familles = load_gedcom(input_path)

	# Note: parse_gedcom_minimal ne récupère pas encore les sources depuis GEDCOM
	# On passe None pour sources, elles seront ajoutées dans une issue future si nécessaire
	sources = None

	# Écrire le répertoire GWB (Issues #22-26)
	write_gwb_minimal(individus, familles, output_dir, sources=sources)

