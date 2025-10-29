from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from geneweb.adapters.ocaml_bridge.bridge import OcamlCommandError, run_gwb2ged

app = FastAPI(title="GeneWeb Python API", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

def _resolve_input_dir(raw: str) -> str:
    # Si chemin absolu, utiliser tel quel
    p = Path(raw)
    if p.is_absolute():
        return str(p)

    root = os.getenv("GENEWEB_OCAML_ROOT")
    if not root:
        raise HTTPException(
            status_code=400,
            detail="Chemin relatif fourni sans GENEWEB_OCAML_ROOT. Définissez la variable d'environnement ou passez un chemin absolu.",
        )
    root_path = Path(root)

    # Alias pratiques
    if raw in ("demo", "bases/demo"):
        return str(root_path / "distribution" / "bases" / "demo")
    if raw == "demo.gwb":
        return str(root_path / "distribution" / "demo.gwb")

    # Si commence par bases/… => distribution/bases/…
    if raw.startswith("bases/"):
        return str(root_path / "distribution" / raw)
    # Si termine par .gwb => distribution/<raw>
    if raw.endswith(".gwb"):
        return str(root_path / "distribution" / raw)

    # Par défaut, joindre sous distribution/
    return str(root_path / "distribution" / raw)


@app.get("/export/gwb2ged")
def export_gwb2ged(
    input_dir: str = Query(
        ..., description="Chemin répertoire GWB (absolu ou relatif à GENEWEB_OCAML_ROOT)"
    ),
) -> dict[str, str]:
    try:
        resolved = _resolve_input_dir(input_dir)
        # Certaines versions n'acceptent pas -o - (stdout). Utilisons un fichier temporaire.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ged") as tmp:
            tmp_path = Path(tmp.name)
        try:
            # gwb2ged attend <BASE> en positionnel, pas d'option -i
            run_gwb2ged([resolved, "-o", str(tmp_path)])
            content = tmp_path.read_text(encoding="utf-8", errors="ignore")
            return {"stdout": content}
        finally:
            with suppress(Exception):
                os.unlink(tmp_path)
    except OcamlCommandError as e:
        raise HTTPException(status_code=502, detail=e.stderr) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:  # Autres erreurs
        raise HTTPException(status_code=500, detail=str(e)) from e
