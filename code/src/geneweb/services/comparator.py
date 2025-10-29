from __future__ import annotations

import difflib
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


def _normalize_line(line: str) -> str:
	# Trim, collapse spaces, NFC normalize
	s = unicodedata.normalize("NFC", line.rstrip())
	# Remove extraneous inner whitespace only where it's insignificant: collapse multiple spaces
	# Keep single spaces intact
	s = " ".join(chunk for chunk in s.split())
	return s


def normalize_gedcom(text: str) -> list[str]:
	"""Normalise un GEDCOM pour comparaison insensible aux espaces/retours.
	- supprime lignes vides
	- applique NFC
	- compresse espaces successifs
	"""
	lines = [l for l in (ln for ln in text.splitlines()) if l.strip()]
	return [_normalize_line(l) for l in lines]


@dataclass(frozen=True)
class CompareResult:
	are_equal: bool
	diff: str
	left_count: int
	right_count: int


def compare_gedcom(left_text: str, right_text: str, context: int = 3) -> CompareResult:
	left = normalize_gedcom(left_text)
	right = normalize_gedcom(right_text)
	are_equal = left == right
	if are_equal:
		return CompareResult(True, diff="", left_count=len(left), right_count=len(right))

	d = difflib.unified_diff(left, right, fromfile="left", tofile="right", n=context)
	diff_text = "\n".join(d)
	return CompareResult(False, diff=diff_text, left_count=len(left), right_count=len(right))


def compare_files(left_path: str | Path, right_path: str | Path, context: int = 3) -> CompareResult:
	left_text = Path(left_path).read_text(encoding="utf-8", errors="ignore")
	right_text = Path(right_path).read_text(encoding="utf-8", errors="ignore")
	return compare_gedcom(left_text, right_text, context=context)
