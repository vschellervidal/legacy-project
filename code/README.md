# GeneWeb Python

Projet de refonte Python de GeneWeb avec approche par paliers (strangler fig). Ce dépôt s'appuie sur le dépôt OCaml existant comme oracle de tests, puis remplace progressivement ses fonctions.

## Démarrage

```bash
# 1) Créer un venv
python3 -m venv .venv
source .venv/bin/activate

# 2) Installer le paquet en editable + deps dev
pip install -U pip
pip install -e .[dev]

# 3) Lancer tests smoke (nécessite le repo OCaml local)
# Repo OCaml intégré localement
pytest -q -m smoke

# 4) Lancer l'API
uvicorn geneweb.adapters.http.app:app --reload

# 5) Utiliser le CLI
geneweb --help
```

## Pont OCaml

- Le dépôt OCaml est copié dans `../geneweb_python/geneweb`.
- Variable d'environnement optionnelle `GENEWEB_OCAML_ROOT` pour override.
- Pour activer les tests smoke OCaml: `RUN_OCAML_TESTS=1 pytest -q -m smoke`.

## Structure

- `src/geneweb/` paquet principal (domain, io, services, adapters, infra)
- `tests/` tests unitaires et de parité
