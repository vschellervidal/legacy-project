from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

GENEWEB_OCAML_ROOT_ENV = "GENEWEB_OCAML_ROOT"


class OcamlCommandError(RuntimeError):
    def __init__(self, cmd: Sequence[str], returncode: int, stdout: str, stderr: str) -> None:
        super().__init__(f"Command failed: {' '.join(cmd)} (code={returncode})")
        self.cmd = list(cmd)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _default_root() -> Path:
    # Default to sibling 'geneweb' repo if env unset
    env = os.getenv(GENEWEB_OCAML_ROOT_ENV)
    if env:
        return Path(env).expanduser().resolve()
    # Heuristics:
    # 1) geneweb/ at repository root (python mono-repo case)
    # 2) ../geneweb relative to this file (two-repo side-by-side)
    here = Path(__file__).resolve()
    mono_repo = here.parents[5] / "geneweb"
    if mono_repo.exists():
        return mono_repo
    side_by_side = here.parents[5].parent / "geneweb"
    return side_by_side


def _bin_path(root: Path, relative: str) -> Path:
    # Prefer dune exec path if available, else built bin, else source path
    dune_bin = root / "_build" / "default" / "bin" / relative
    if dune_bin.exists():
        return dune_bin
    src_bin = root / "bin" / relative
    return src_bin


def _run(cmd: Sequence[str], cwd: Path | None = None, timeout: int = 120) -> str:
    completed = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        check=False,
        capture_output=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise OcamlCommandError(cmd, completed.returncode, completed.stdout, completed.stderr)
    return completed.stdout


def run_gwb2ged(args: Sequence[str]) -> str:
    root = _default_root()
    exe = _bin_path(root, "gwb2ged/gwb2ged.exe")

    if exe.exists():
        return _run([str(exe), *args], cwd=root)
    dune = shutil.which("dune")
    if dune:
        return _run([dune, "exec", str(root / "bin/gwb2ged/gwb2ged.exe"), "--", *args], cwd=root)
    raise FileNotFoundError(
        f"gwb2ged introuvable. Compilez avec dune dans {root} ou définissez {GENEWEB_OCAML_ROOT_ENV} vers un dépôt compilé."
    )


def run_ged2gwb(args: Sequence[str]) -> str:
    root = _default_root()
    exe = _bin_path(root, "ged2gwb/ged2gwb.exe")

    if exe.exists():
        return _run([str(exe), *args], cwd=root)
    dune = shutil.which("dune")
    if dune:
        return _run([dune, "exec", str(root / "bin/ged2gwb/ged2gwb.exe"), "--", *args], cwd=root)
    raise FileNotFoundError(
        f"ged2gwb introuvable. Compilez avec dune dans {root} ou définissez {GENEWEB_OCAML_ROOT_ENV} vers un dépôt compilé."
    )


def run_gwd(args: Sequence[str]) -> str:
    root = _default_root()
    exe = _bin_path(root, "gwd/gwd.exe")

    if exe.exists():
        return _run([str(exe), *args], cwd=root)
    dune = shutil.which("dune")
    if dune:
        return _run([dune, "exec", str(root / "bin/gwd/gwd.exe"), "--", *args], cwd=root)
    raise FileNotFoundError(
        f"gwd introuvable. Compilez avec dune dans {root} ou définissez {GENEWEB_OCAML_ROOT_ENV} vers un dépôt compilé."
    )
