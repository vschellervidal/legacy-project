from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

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


def _should_use_python() -> bool:
	"""Vérifie si l'implémentation Python doit être utilisée (via variable d'environnement)."""
	return os.getenv("GENEWEB_USE_PYTHON", "").lower() in ("1", "true", "yes")


@app.get("/export/gwb2ged")
def export_gwb2ged(
	input_dir: str = Query(
		..., description="Chemin répertoire GWB (absolu ou relatif à GENEWEB_OCAML_ROOT)"
	),
	use_python: bool = Query(
		False, description="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)"
	),
) -> dict[str, str]:
	"""Exporte une base GWB en GEDCOM."""
	# Priorité: paramètre API > variable d'environnement > défaut OCaml
	use_py = use_python or _should_use_python()

	try:
		resolved = _resolve_input_dir(input_dir)
		if use_py:
			# Implémentation Python native (Issue #20)
			with tempfile.NamedTemporaryFile(delete=False, suffix=".ged") as tmp:
				tmp_path = Path(tmp.name)
			try:
				gwb2ged_python(resolved, tmp_path)
				content = tmp_path.read_text(encoding="utf-8", errors="ignore")
				return {"stdout": content}
			finally:
				with suppress(Exception):
					os.unlink(tmp_path)
		else:
			# Bridge OCaml (défaut)
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


@app.post("/import/ged2gwb")
def import_ged2gwb(
	input_file: str = Query(
		..., description="Chemin fichier GEDCOM (absolu ou relatif à GENEWEB_OCAML_ROOT)"
	),
	output_dir: str = Query(
		..., description="Répertoire GWB de sortie (absolu ou relatif à GENEWEB_OCAML_ROOT)"
	),
	use_python: bool = Query(
		False, description="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)"
	),
) -> dict[str, str]:
	"""Importe un fichier GEDCOM dans une base GWB."""
	# Priorité: paramètre API > variable d'environnement > défaut OCaml
	use_py = use_python or _should_use_python()

	try:
		# Résoudre le chemin du fichier GEDCOM (absolu ou relatif)
		input_path = Path(input_file)
		if not input_path.is_absolute():
			root = os.getenv("GENEWEB_OCAML_ROOT")
			if root:
				input_path = Path(root) / "distribution" / input_file
		
		if not input_path.exists():
			raise FileNotFoundError(f"Fichier GEDCOM introuvable: {input_file}")

		# Résoudre le répertoire de sortie (absolu ou relatif)
		output_path = Path(output_dir)
		if not output_path.is_absolute():
			root = os.getenv("GENEWEB_OCAML_ROOT")
			if root:
				output_path = Path(root) / "distribution" / output_dir

		if use_py:
			# Implémentation Python native (Issue #28)
			ged2gwb_python(input_path, output_path)
			return {"status": "ok", "output_dir": str(output_path)}
		else:
			# Bridge OCaml (défaut)
			run_ged2gwb(["-i", str(input_path), "-o", str(output_path)])
			return {"status": "ok", "output_dir": str(output_path)}
	except OcamlCommandError as e:
		raise HTTPException(status_code=502, detail=e.stderr) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except Exception as e:  # Autres erreurs
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/analytical/consang")
def analytical_consang(
	base_dir: str = Query(
		..., description="Chemin répertoire GWB (absolu ou relatif à GENEWEB_OCAML_ROOT)"
	),
	use_python: bool = Query(
		False, description="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)"
	),
) -> dict[str, str | dict[str, float]]:
	"""Calcule les coefficients de consanguinité pour une base GWB (Issue #32)."""
	# Priorité: paramètre API > variable d'environnement > défaut OCaml
	use_py = use_python or _should_use_python()

	try:
		resolved = _resolve_input_dir(base_dir)
		if use_py:
			# Implémentation Python native (Issue #30)
			# Chercher base.gwb dans le répertoire ou utiliser directement
			base_path = Path(resolved)
			if (base_path / "base").exists():
				base_path = base_path / "base"
			
			f_coefficients = compute_inbreeding_from_gwb(str(base_path))
			
			# Retourner en format JSON structuré
			return {
				"status": "ok",
				"implementation": "python",
				"coefficients": f_coefficients,
				"summary": {
					"total": len(f_coefficients),
					"non_zero": len([f for f in f_coefficients.values() if f > 0.0]),
					"max_f": max(f_coefficients.values()) if f_coefficients else 0.0,
				},
			}
		else:
			# Bridge OCaml (défaut)
			base_path_str = str(Path(resolved) / "base") if (Path(resolved) / "base").exists() else resolved
			output = run_consang([base_path_str])
			return {"status": "ok", "implementation": "ocaml", "stdout": output}
	except OcamlCommandError as e:
		raise HTTPException(status_code=502, detail=e.stderr) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except Exception as e:  # Autres erreurs
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/analytical/connex")
def analytical_connex(
	base_dir: str = Query(
		..., description="Chemin répertoire GWB (absolu ou relatif à GENEWEB_OCAML_ROOT)"
	),
	use_python: bool = Query(
		False, description="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)"
	),
	all_components: bool = Query(
		False, description="Retourner toutes les composantes (défaut: seulement la plus grande pour Python)"
	),
) -> dict[str, str | list[list[str]]]:
	"""Calcule les composantes connexes d'une base GWB (Issue #32)."""
	# Priorité: paramètre API > variable d'environnement > défaut OCaml
	use_py = use_python or _should_use_python()

	try:
		resolved = _resolve_input_dir(base_dir)
		if use_py:
			# Implémentation Python native (Issue #31)
			base_path = Path(resolved)
			if (base_path / "base").exists():
				base_path = base_path / "base"
			
			components = compute_connected_components_from_gwb(str(base_path))
			
			# Retourner en format JSON structuré
			if all_components:
				return {
					"status": "ok",
					"implementation": "python",
					"components": components,
					"count": len(components),
				}
			else:
				# Retourner seulement la plus grande
				largest = components[0] if components else []
				return {
					"status": "ok",
					"implementation": "python",
					"largest_component": largest,
					"largest_size": len(largest),
					"total_components": len(components),
				}
		else:
			# Bridge OCaml (défaut)
			base_path_str = str(Path(resolved) / "base") if (Path(resolved) / "base").exists() else resolved
			args = ["-a", base_path_str] if all_components else [base_path_str]
			output = run_connex(args)
			return {"status": "ok", "implementation": "ocaml", "stdout": output}
	except OcamlCommandError as e:
		raise HTTPException(status_code=502, detail=e.stderr) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except Exception as e:  # Autres erreurs
		raise HTTPException(status_code=500, detail=str(e)) from e
