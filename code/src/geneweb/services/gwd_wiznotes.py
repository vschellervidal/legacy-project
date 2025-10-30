from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_FILENAME = "wizard_notes.json"


def _file_path(base_dir: str | Path) -> Path:
    p = Path(base_dir)
    if not p.exists():
        raise FileNotFoundError(f"Base GWB introuvable: {base_dir}")
    return p / _FILENAME


def _load(base_dir: str | Path) -> dict[str, Any]:
    fp = _file_path(base_dir)
    if not fp.exists():
        return {"notes": {}}
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return {"notes": {}}


def _save(base_dir: str | Path, data: dict[str, Any]) -> None:
    fp = _file_path(base_dir)
    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_wiznotes(base_dir: str | Path, query: str | None = None) -> dict[str, Any]:
    data = _load(base_dir)
    notes: dict[str, str] = data.get("notes", {})
    if query:
        filt = {k: v for k, v in notes.items() if query.lower() in v.lower()}
        return {"notes": filt}
    return {"notes": notes}


def get_wiznote(base_dir: str | Path, key: str) -> dict[str, Any]:
    data = _load(base_dir)
    note = data.get("notes", {}).get(key)
    if note is None:
        raise ValueError(f"Note wizard introuvable: {key}")
    return {"key": key, "note": note}


def set_wiznote(base_dir: str | Path, key: str, note: str) -> dict[str, Any]:
    data = _load(base_dir)
    notes: dict[str, str] = data.setdefault("notes", {})
    notes[key] = note
    _save(base_dir, data)
    return {"key": key, "note": note}


def del_wiznote(base_dir: str | Path, key: str) -> None:
    data = _load(base_dir)
    notes: dict[str, str] = data.setdefault("notes", {})
    if key not in notes:
        raise ValueError(f"Note wizard introuvable: {key}")
    del notes[key]
    _save(base_dir, data)


