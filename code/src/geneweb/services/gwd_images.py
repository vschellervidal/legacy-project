from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any


def _images_dir(base_dir: str | Path) -> Path:
    # Cherche un sous-dossier images dans la base, sinon retourne la base elle-même
    p = Path(base_dir)
    if not p.exists():
        raise FileNotFoundError(f"Base GWB introuvable: {base_dir}")
    for name in ("images", "img", "media"):
        d = p / name
        if d.exists() and d.is_dir():
            return d
    return p


def list_carrousel_images(base_dir: str | Path, person_id: str | None = None) -> dict[str, Any]:
    # Heuristique: lier personne -> fichiers contenant son id
    images_root = _images_dir(base_dir)
    exts = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    files: list[str] = []
    for p in images_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            if person_id is None or person_id in p.name:
                files.append(str(p))
    files.sort()
    return {"images": files}


def get_image_file(base_dir: str | Path, relative_path: str) -> tuple[bytes, str]:
    # Sécurise le chemin (pas de traversée)
    root = _images_dir(base_dir)
    p = (root / relative_path).resolve()
    if root not in p.parents and p != root:
        raise ValueError("Chemin image invalide")
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(relative_path)
    content = p.read_bytes()
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return content, mime


def set_blason_image(base_dir: str | Path, person_id: str, image_name: str) -> dict[str, str]:
    # Place-holder: enregistre une association simple dans un fichier blasons.json
    import json

    p = Path(base_dir)
    if not p.exists():
        raise FileNotFoundError(base_dir)
    fp = p / "blasons.json"
    data: dict[str, str] = {}
    if fp.exists():
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data[person_id] = image_name
    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"person_id": person_id, "blason": image_name}


