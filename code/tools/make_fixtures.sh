#!/usr/bin/env bash
set -euo pipefail

# Génère des mini-fixtures GWB à partir d'une base source
# Usage: GENEWEB_OCAML_ROOT=/path/to/geneweb ./tools/make_fixtures.sh

ROOT="${GENEWEB_OCAML_ROOT:-}"
if [[ -z "$ROOT" ]]; then
  echo "GENEWEB_OCAML_ROOT non défini" >&2
  exit 1
fi

SRC_DEMO_BASE="$ROOT/distribution/bases/demo.gwb"
DEST_DIR="tests/fixtures/gwb"

if [[ ! -f "$SRC_DEMO_BASE/base" ]]; then
  echo "Base de démo introuvable: $SRC_DEMO_BASE" >&2
  exit 1
fi

mkdir -p "$DEST_DIR/small/demo_min" "$DEST_DIR/medium/demo_copy" "$DEST_DIR/edge"

# small/demo_min: copie minimale (uniquement base)
cp -f "$SRC_DEMO_BASE/base" "$DEST_DIR/small/demo_min/base"

# medium/demo_copy: copie plus large (base + quelques index si présents)
cp -f "$SRC_DEMO_BASE/base" "$DEST_DIR/medium/demo_copy/base" || true
for f in ind indn fam famn occ occn; do
  [[ -f "$SRC_DEMO_BASE/$f" ]] && cp -f "$SRC_DEMO_BASE/$f" "$DEST_DIR/medium/demo_copy/$f"
done

# edge/encodage_min: base minimale avec caractères spéciaux (note: artificiel)
EDGE_DIR="$DEST_DIR/edge/encodage_min"
mkdir -p "$EDGE_DIR"
# Crée un fichier base vide pour placeholder, à enrichir plus tard par générateur Python
: > "$EDGE_DIR/base"

echo "Fixtures générées dans $DEST_DIR"
