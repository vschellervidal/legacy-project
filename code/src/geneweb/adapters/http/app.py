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
from geneweb.services.gwd_routes import (
    get_ascendance,
    get_descendance,
    get_family_page,
    get_notes,
    get_person_page,
    search_persons,
)
from geneweb.services.gwd_modify import (
    add_individu,
    mod_individu,
    add_famille,
    mod_famille,
    del_individu,
    del_famille,
)

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


# ============================================================================
# Routes gwd - Issue #35 : Modifications (ajout/modif individu - lot 1)
# ============================================================================


@app.post("/gwd/add_ind")
def gwd_add_ind(
	base: str = Query(..., description="Chemin répertoire GWB (absolu ou relatif GENEWEB_OCAML_ROOT)"),
	id: str = Query(..., description="ID individu (unique)"),
	nom: str | None = Query(None, description="Nom"),
	prenom: str | None = Query(None, description="Prénom"),
	sexe: str | None = Query(None, description="Sexe: M/F/X"),
	use_python: bool = Query(False, description="Forcer Python"),
) -> dict:
	use_py = use_python or _should_use_python()
	try:
		resolved = _resolve_input_dir(base)
		if use_py:
			ind = add_individu(resolved, id=id, nom=nom, prenom=prenom, sexe=sexe)  # type: ignore[arg-type]
			return {
				"status": "ok",
				"implementation": "python",
				"individu": {
					"id": ind.id,
					"nom": ind.nom,
					"prenom": ind.prenom,
					"sexe": ind.sexe.value if ind.sexe else None,
				},
			}
		else:
			raise HTTPException(status_code=501, detail="Mode OCaml non implémenté pour add_ind")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.put("/gwd/mod_ind")
def gwd_mod_ind(
	base: str = Query(..., description="Chemin répertoire GWB (absolu ou relatif GENEWEB_OCAML_ROOT)"),
	id: str = Query(..., description="ID individu existant"),
	nom: str | None = Query(None, description="Nom (optionnel)"),
	prenom: str | None = Query(None, description="Prénom (optionnel)"),
	sexe: str | None = Query(None, description="Sexe: M/F/X (optionnel)"),
	use_python: bool = Query(False, description="Forcer Python"),
) -> dict:
	use_py = use_python or _should_use_python()
	try:
		resolved = _resolve_input_dir(base)
		if use_py:
			ind = mod_individu(resolved, id=id, nom=nom, prenom=prenom, sexe=sexe)  # type: ignore[arg-type]
			return {
				"status": "ok",
				"implementation": "python",
				"individu": {
					"id": ind.id,
					"nom": ind.nom,
					"prenom": ind.prenom,
					"sexe": ind.sexe.value if ind.sexe else None,
				},
			}
		else:
			raise HTTPException(status_code=501, detail="Mode OCaml non implémenté pour mod_ind")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/gwd/add_fam")
def gwd_add_fam(
	base: str = Query(..., description="Chemin répertoire GWB"),
	id: str = Query(..., description="ID famille"),
	pere_id: str | None = Query(None),
	mere_id: str | None = Query(None),
	enfants_ids: str | None = Query(None, description="Liste enfants séparés par ','"),
	use_python: bool = Query(False),
) -> dict:
	use_py = use_python or _should_use_python()
	try:
		resolved = _resolve_input_dir(base)
		if use_py:
			enfants = [e for e in (enfants_ids or "").split(",") if e]
			fam = add_famille(resolved, id=id, pere_id=pere_id, mere_id=mere_id, enfants_ids=enfants)
			return {"status": "ok", "implementation": "python", "famille": {"id": fam.id, "pere_id": fam.pere_id, "mere_id": fam.mere_id, "enfants_ids": fam.enfants_ids}}
		else:
			raise HTTPException(status_code=501, detail="Mode OCaml non implémenté pour add_fam")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.put("/gwd/mod_fam")
def gwd_mod_fam(
	base: str = Query(..., description="Chemin répertoire GWB"),
	id: str = Query(..., description="ID famille"),
	pere_id: str | None = Query(None),
	mere_id: str | None = Query(None),
	enfants_ids: str | None = Query(None, description="Liste enfants séparés par ','"),
	use_python: bool = Query(False),
) -> dict:
	use_py = use_python or _should_use_python()
	try:
		resolved = _resolve_input_dir(base)
		if use_py:
			enfants = [e for e in (enfants_ids or "").split(",") if e]
			fam = mod_famille(resolved, id=id, pere_id=pere_id, mere_id=mere_id, enfants_ids=enfants if enfants_ids is not None else None)
			return {"status": "ok", "implementation": "python", "famille": {"id": fam.id, "pere_id": fam.pere_id, "mere_id": fam.mere_id, "enfants_ids": fam.enfants_ids}}
		else:
			raise HTTPException(status_code=501, detail="Mode OCaml non implémenté pour mod_fam")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/gwd/del_ind")
def gwd_del_ind(
	base: str = Query(..., description="Chemin répertoire GWB"),
	id: str = Query(..., description="ID individu"),
	force: bool = Query(False),
	use_python: bool = Query(False),
) -> dict:
	use_py = use_python or _should_use_python()
	try:
		resolved = _resolve_input_dir(base)
		if use_py:
			del_individu(resolved, id=id, force=force)
			return {"status": "ok", "implementation": "python"}
		else:
			raise HTTPException(status_code=501, detail="Mode OCaml non implémenté pour del_ind")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/gwd/del_fam")
def gwd_del_fam(
	base: str = Query(..., description="Chemin répertoire GWB"),
	id: str = Query(..., description="ID famille"),
	force: bool = Query(False),
	use_python: bool = Query(False),
) -> dict:
	use_py = use_python or _should_use_python()
	try:
		resolved = _resolve_input_dir(base)
		if use_py:
			del_famille(resolved, id=id, force=force)
			return {"status": "ok", "implementation": "python"}
		else:
			raise HTTPException(status_code=501, detail="Mode OCaml non implémenté pour del_fam")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# Routes gwd - Issue #34 : Routes de lecture (consultation)
# ============================================================================


@app.get("/gwd")
def gwd_route(
	base: str = Query(..., description="Nom de la base (ex: demo)"),
	mode: str = Query("", description="Mode/route (ex: '', 'S', 'NG', 'F', 'A', 'D', 'NOTES')"),
	i: str | None = Query(None, description="ID individu (iper)"),
	f: str | None = Query(None, description="ID famille (ifam)"),
	v: str | None = Query(None, description="Valeur variable"),
	ajax: bool = Query(False, description="Mode AJAX (retourne JSON)"),
	use_python: bool = Query(
		False, description="Utiliser l'implémentation Python (défaut: OCaml, ou GENEWEB_USE_PYTHON=1)"
	),
) -> dict:
	"""Route générique pour les pages gwd (Issue #34).
	
	Cette route supporte les modes de lecture suivants :
	- `""` (vide) : Page d'accueil ou fiche individu (si `i` fourni)
	- `S` : Recherche simple
	- `NG` : Recherche avancée
	- `F` : Fiche famille
	- `A` : Ascendance
	- `D` : Descendance
	- `NOTES` : Notes
	"""
	use_py = use_python or _should_use_python()
	
	try:
		# Résoudre le chemin de la base
		resolved = _resolve_input_dir(base)
		
		if use_py:
			# Implémentation Python native (Issue #34)
			if mode == "" or mode == "PERSO":
				# Page d'accueil ou fiche individu
				result = get_person_page(resolved, person_id=i)
				return {
					"status": "ok",
					"implementation": "python",
					"mode": mode or "home",
					**result,
				}
			elif mode == "S" or mode == "NG":
				# Recherche
				result = search_persons(resolved, query=v)
				return {
					"status": "ok",
					"implementation": "python",
					"mode": "search",
					**result,
				}
			elif mode == "F":
				# Fiche famille
				fam_id = f or i  # Peut être dérivé de l'individu
				result = get_family_page(resolved, family_id=fam_id)
				return {
					"status": "ok",
					"implementation": "python",
					"mode": "family",
					**result,
				}
			elif mode == "A":
				# Ascendance
				if not i:
					raise ValueError("Paramètre 'i' requis pour la route A (ascendance)")
				result = get_ascendance(resolved, person_id=i)
				return {
					"status": "ok",
					"implementation": "python",
					"mode": "ascendance",
					**result,
				}
			elif mode == "D":
				# Descendance
				if not i:
					raise ValueError("Paramètre 'i' requis pour la route D (descendance)")
				result = get_descendance(resolved, person_id=i)
				return {
					"status": "ok",
					"implementation": "python",
					"mode": "descendance",
					**result,
				}
			elif mode == "NOTES":
				# Notes
				result = get_notes(resolved, note_file=v, ajax=ajax)
				return {
					"status": "ok",
					"implementation": "python",
					"mode": "notes",
					**result,
				}
			else:
				raise HTTPException(
					status_code=400,
					detail=f"Mode '{mode}' non implémenté en Python. Utilisez use_python=false pour OCaml.",
				)
		else:
			# Bridge OCaml (défaut) - Pour l'instant, retourner une erreur
			# car gwd nécessite un serveur HTTP actif
			raise HTTPException(
				status_code=501,
				detail="Bridge OCaml pour gwd non encore implémenté. Utilisez use_python=true pour les routes Python.",
			)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e)) from e
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e)) from e
	except Exception as e:  # Autres erreurs
		raise HTTPException(status_code=500, detail=str(e)) from e
