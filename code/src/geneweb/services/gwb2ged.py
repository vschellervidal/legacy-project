"""Service Python natif pour convertir GWB vers GEDCOM (Issue #20).

Ce service utilise l'implémentation Python native plutôt que le bridge OCaml.
Il charge les données GWB via load_gwb_minimal puis sérialise en GEDCOM.
"""

from __future__ import annotations

from pathlib import Path

from geneweb.io.gedcom import serialize_gedcom_minimal
from geneweb.io.gwb import load_gwb_minimal


def gwb2ged_python(input_dir: str | Path, output_file: str | Path) -> str:
    """Convertit un répertoire GWB en fichier GEDCOM en utilisant l'implémentation Python native.

    Args:
        input_dir: Répertoire contenant la base GWB (doit contenir index.json)
        output_file: Fichier GEDCOM de sortie

    Returns:
        Contenu GEDCOM généré

    Raises:
        FileNotFoundError: Si le répertoire ou index.json est introuvable
        ValueError: Si les données sont invalides
    """
    root_path = Path(input_dir)
    if not root_path.exists():
        raise FileNotFoundError(f"Répertoire GWB introuvable: {input_dir}")

    # Charger les individus, familles et sources depuis GWB (Issues #24, #25)
    individus, familles, sources = load_gwb_minimal(root_path)

    # Sérialiser en GEDCOM
    gedcom_content = serialize_gedcom_minimal(individus, familles, sources)

    # Écrire le fichier de sortie
    out_path = Path(output_file)
    out_path.write_text(gedcom_content, encoding="utf-8")

    return gedcom_content

