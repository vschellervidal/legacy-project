from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from geneweb.adapters.ocaml_bridge.bridge import (
    OcamlCommandError,
    run_connex,
    run_consang,
    run_ged2gwb,
    run_gwb2ged,
)
from geneweb.services.connectivity import compute_connected_components_from_gwb
from geneweb.services.consanguinity import compute_inbreeding_from_gwb
from geneweb.services.ged2gwb import ged2gwb_python
from geneweb.services.gwb2ged import gwb2ged_python

app = typer.Typer(add_completion=False, help="CLI GeneWeb (pont OCaml et commandes Python)")

GENEWEB_USE_PYTHON_ENV = "GENEWEB_USE_PYTHON"


def _should_use_python() -> bool:
    """Vérifie si l'implémentation Python doit être utilisée (Issue #20).

    Par défaut, utilise OCaml pour compatibilité.
    """
    return os.getenv(GENEWEB_USE_PYTHON_ENV, "").lower() in ("1", "true", "yes")


@app.callback()
def _version(ctx: typer.Context) -> None:
    """Entry point for future global options."""


@app.command()
def gwb2ged(
    input_dir: Annotated[
        Path, typer.Option("-i", "--input-dir", exists=True, file_okay=False, readable=True, help="Répertoire base GWB")
    ],
    output_file: Annotated[
        Path, typer.Option("-o", "--output-file", dir_okay=False, writable=True, help="Fichier GEDCOM de sortie")
    ],
    use_python: Annotated[
        bool,
        typer.Option(
            "--python/--ocaml",
            help="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)",
        ),
    ] = None,
) -> None:
    """Convertit une base GWB en fichier GEDCOM."""
    # Priorité: option CLI > variable d'environnement > défaut OCaml
    use_py = use_python if use_python is not None else _should_use_python()

    if use_py:
        # Implémentation Python native (Issue #20)
        try:
            content = gwb2ged_python(input_dir, output_file)
            typer.echo(f"Converti en GEDCOM (Python): {output_file}", err=True)
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Erreur Python: {e}", err=True)
            raise typer.Exit(1) from e
    else:
        # Bridge OCaml (défaut)
        try:
            out = run_gwb2ged(["-i", str(input_dir), "-o", str(output_file)])
            typer.echo(out)
        except OcamlCommandError as e:
            typer.echo(e.stderr, err=True)
            raise typer.Exit(e.returncode) from e


@app.command()
def ged2gwb(
    input_file: Annotated[
        Path, typer.Option(exists=True, file_okay=True, readable=True, help="GEDCOM d'entrée")
    ],
    output_dir: Annotated[Path, typer.Option(file_okay=False, help="Répertoire GWB cible")],
    use_python: Annotated[
        bool,
        typer.Option(
            "--python/--ocaml",
            help="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)",
        ),
    ] = None,
) -> None:
    """Convertit un fichier GEDCOM en base GWB."""
    # Priorité: option CLI > variable d'environnement > défaut OCaml
    use_py = use_python if use_python is not None else _should_use_python()

    if use_py:
        # Implémentation Python native (Issue #28)
        try:
            ged2gwb_python(input_file, output_dir)
            typer.echo(f"Converti en GWB (Python): {output_dir}", err=True)
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Erreur Python: {e}", err=True)
            raise typer.Exit(1) from e
    else:
        # Bridge OCaml (défaut)
        try:
            out = run_ged2gwb(["-i", str(input_file), "-o", str(output_dir)])
            typer.echo(out)
        except OcamlCommandError as e:
            typer.echo(e.stderr, err=True)
            raise typer.Exit(e.returncode) from e


@app.command()
def consang(
    base_dir: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=False, readable=True, help="Répertoire base GWB"),
    ],
    use_python: Annotated[
        bool,
        typer.Option(
            "--python/--ocaml",
            help="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)",
        ),
    ] = None,
    quiet: Annotated[
        bool, typer.Option("-q", "--quiet", help="Mode silencieux (Python uniquement)")
    ] = False,
) -> None:
    """Calcule les coefficients de consanguinité pour une base GWB (Issue #32)."""
    # Priorité: option CLI > variable d'environnement > défaut OCaml
    use_py = use_python if use_python is not None else _should_use_python()

    if use_py:
        # Implémentation Python native (Issue #30)
        try:
            # Pour Python, on attend le répertoire racine GWB (qui contient index.json)
            # Mais le paramètre peut aussi être base.gwb -> on extrait le dossier parent
            if base_dir.name.endswith(".gwb"):
                base_path = base_dir
            else:
                # Chercher base.gwb dans le répertoire ou utiliser directement
                potential_base = base_dir / "base"
                if potential_base.exists():
                    base_path = potential_base
                else:
                    base_path = base_dir
            
            f_coefficients = compute_inbreeding_from_gwb(str(base_path))
            
            if not quiet:
                # Afficher les résultats (format simple)
                typer.echo("Coefficients de consanguinité:", err=True)
                for ind_id, f_value in sorted(f_coefficients.items()):
                    if f_value > 0.0:  # Afficher seulement les non-nuls
                        typer.echo(f"  {ind_id}: F = {f_value:.6f}")
                
                # Statistiques
                non_zero = [f for f in f_coefficients.values() if f > 0.0]
                if non_zero:
                    typer.echo(f"\nIndividus avec consanguinité: {len(non_zero)}/{len(f_coefficients)}", err=True)
                    typer.echo(f"F maximum: {max(non_zero):.6f}", err=True)
                else:
                    typer.echo("\nAucune consanguinité détectée.", err=True)
            else:
                # Mode silencieux: juste exécuter
                pass
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Erreur Python: {e}", err=True)
            raise typer.Exit(1) from e
    else:
        # Bridge OCaml (défaut)
        try:
            # OCaml consang attend le chemin vers "base" dans le répertoire GWB
            base_path = str(base_dir / "base") if (base_dir / "base").exists() else str(base_dir)
            out = run_consang([base_path])
            typer.echo(out)
        except OcamlCommandError as e:
            typer.echo(e.stderr, err=True)
            raise typer.Exit(e.returncode) from e


@app.command()
def connex(
    base_dir: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=False, readable=True, help="Répertoire base GWB"),
    ],
    use_python: Annotated[
        bool,
        typer.Option(
            "--python/--ocaml",
            help="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)",
        ),
    ] = None,
    all_components: Annotated[
        bool, typer.Option("-a", "--all", help="Afficher toutes les composantes (défaut: Python uniquement)")
    ] = False,
) -> None:
    """Calcule les composantes connexes d'une base GWB (Issue #32)."""
    # Priorité: option CLI > variable d'environnement > défaut OCaml
    use_py = use_python if use_python is not None else _should_use_python()

    if use_py:
        # Implémentation Python native (Issue #31)
        try:
            # Pour Python, on attend le répertoire racine GWB
            if base_dir.name.endswith(".gwb"):
                base_path = base_dir
            else:
                potential_base = base_dir / "base"
                if potential_base.exists():
                    base_path = potential_base
                else:
                    base_path = base_dir
            
            components = compute_connected_components_from_gwb(str(base_path))
            
            typer.echo(f"Composantes connexes trouvées: {len(components)}", err=True)
            if all_components:
                for i, comp in enumerate(components, 1):
                    typer.echo(f"\nComposante {i} ({len(comp)} individus):", err=True)
                    typer.echo(f"  {', '.join(sorted(comp))}")
            else:
                # Afficher seulement la plus grande
                if components:
                    largest = components[0]
                    typer.echo(f"Plus grande composante: {len(largest)} individus", err=True)
                    if len(largest) <= 20:  # Afficher si pas trop grand
                        typer.echo(f"  {', '.join(sorted(largest))}")
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Erreur Python: {e}", err=True)
            raise typer.Exit(1) from e
    else:
        # Bridge OCaml (défaut)
        try:
            base_path = str(base_dir / "base") if (base_dir / "base").exists() else str(base_dir)
            args = ["-a", base_path] if all_components else [base_path]
            out = run_connex(args)
            typer.echo(out)
        except OcamlCommandError as e:
            typer.echo(e.stderr, err=True)
            raise typer.Exit(e.returncode) from e


if __name__ == "__main__":
    app()

def main() -> None:
    app()
