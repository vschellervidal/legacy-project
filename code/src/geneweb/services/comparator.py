from __future__ import annotations

import difflib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from geneweb.domain.models import Famille, Individu, Source


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
	lines = [line for line in text.splitlines() if line.strip()]
	return [_normalize_line(line) for line in lines]


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


def _serialize_individu_for_diff(ind: Individu) -> str:
	"""Sérialise un Individu en format texte pour comparaison."""
	parts = [f"ID: {ind.id}"]
	if ind.nom is not None:
		parts.append(f"Nom: {ind.nom}")
	if ind.prenom is not None:
		parts.append(f"Prénom: {ind.prenom}")
	if ind.sexe is not None:
		parts.append(f"Sexe: {ind.sexe.value}")
	if ind.date_naissance is not None:
		parts.append(f"Date naissance: {ind.date_naissance.isoformat()}")
	if ind.lieu_naissance is not None:
		parts.append(f"Lieu naissance: {ind.lieu_naissance}")
	if ind.date_deces is not None:
		parts.append(f"Date décès: {ind.date_deces.isoformat()}")
	if ind.lieu_deces is not None:
		parts.append(f"Lieu décès: {ind.lieu_deces}")
	if ind.note is not None:
		parts.append(f"Note: {ind.note}")
	if ind.sources:
		parts.append(f"Sources: {', '.join(sorted(ind.sources))}")
	return " | ".join(parts)


def _serialize_famille_for_diff(fam: Famille) -> str:
	"""Sérialise une Famille en format texte pour comparaison."""
	parts = [f"ID: {fam.id}"]
	if fam.pere_id is not None:
		parts.append(f"Père: {fam.pere_id}")
	if fam.mere_id is not None:
		parts.append(f"Mère: {fam.mere_id}")
	if fam.enfants_ids:
		parts.append(f"Enfants: {', '.join(sorted(fam.enfants_ids))}")
	if fam.note is not None:
		parts.append(f"Note: {fam.note}")
	if fam.sources:
		parts.append(f"Sources: {', '.join(sorted(fam.sources))}")
	return " | ".join(parts)


def _serialize_source_for_diff(src: Source) -> str:
	"""Sérialise une Source en format texte pour comparaison."""
	parts = [f"ID: {src.id}"]
	if src.titre is not None:
		parts.append(f"Titre: {src.titre}")
	if src.auteur is not None:
		parts.append(f"Auteur: {src.auteur}")
	if src.date_publication is not None:
		parts.append(f"Date publication: {src.date_publication.isoformat()}")
	if src.url is not None:
		parts.append(f"URL: {src.url}")
	if src.fichier is not None:
		parts.append(f"Fichier: {src.fichier}")
	if src.note is not None:
		parts.append(f"Note: {src.note}")
	return " | ".join(parts)


def _serialize_gwb_for_diff(individus: list[Individu], familles: list[Famille], sources: list[Source]) -> list[str]:
	"""Sérialise un tuple GWB en liste de lignes pour comparaison."""
	lines: list[str] = []
	# Trier par ID pour une comparaison stable
	individus_sorted = sorted(individus, key=lambda x: x.id)
	familles_sorted = sorted(familles, key=lambda x: x.id)
	sources_sorted = sorted(sources, key=lambda x: x.id)
	# Ajouter individus
	if individus_sorted:
		lines.append("[INDIVIDUS]")
		for ind in individus_sorted:
			lines.append(_serialize_individu_for_diff(ind))
	# Ajouter familles
	if familles_sorted:
		lines.append("[FAMILLES]")
		for fam in familles_sorted:
			lines.append(_serialize_famille_for_diff(fam))
	# Ajouter sources
	if sources_sorted:
		lines.append("[SOURCES]")
		for src in sources_sorted:
			lines.append(_serialize_source_for_diff(src))
	return lines


def compare_gwb(
	left: tuple[list[Individu], list[Famille], list[Source]],
	right: tuple[list[Individu], list[Famille], list[Source]],
	context: int = 3,
) -> CompareResult:
	"""Compare deux bases GWB et retourne un diff lisible.
	
	Args:
		left: Tuple (individus, familles, sources) de la base de gauche
		right: Tuple (individus, familles, sources) de la base de droite
		context: Nombre de lignes de contexte dans le diff
		
	Returns:
		CompareResult avec are_equal, diff, left_count, right_count
	"""
	left_individus, left_familles, left_sources = left
	right_individus, right_familles, right_sources = right
	
	left_lines = _serialize_gwb_for_diff(left_individus, left_familles, left_sources)
	right_lines = _serialize_gwb_for_diff(right_individus, right_familles, right_sources)
	
	are_equal = left_lines == right_lines
	if are_equal:
		return CompareResult(
			are_equal=True,
			diff="",
			left_count=len(left_individus) + len(left_familles) + len(left_sources),
			right_count=len(right_individus) + len(right_familles) + len(right_sources),
		)
	
	d = difflib.unified_diff(left_lines, right_lines, fromfile="left", tofile="right", n=context, lineterm="")
	diff_text = "\n".join(d)
	return CompareResult(
		are_equal=False,
		diff=diff_text,
		left_count=len(left_individus) + len(left_familles) + len(left_sources),
		right_count=len(right_individus) + len(right_familles) + len(right_sources),
	)
