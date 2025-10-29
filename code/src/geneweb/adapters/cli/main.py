from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from geneweb.adapters.ocaml_bridge.bridge import OcamlCommandError, run_ged2gwb, run_gwb2ged
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
) -> None:
    try:
        out = run_ged2gwb(["-i", str(input_file), "-o", str(output_dir)])
        typer.echo(out)
    except OcamlCommandError as e:
        typer.echo(e.stderr, err=True)
        raise typer.Exit(e.returncode) from e


if __name__ == "__main__":
    app()

def main() -> None:
    app()
