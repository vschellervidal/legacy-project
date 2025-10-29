# Geneweb Python

## Utilisation

- Environnement:
  - python3 -m venv code/.venv && source code/.venv/bin/activate
  - pip install -e 'code/.[dev]'
- Tests smoke (OCaml activable):
  - export RUN_OCAML_TESTS=1 && pytest -q -m smoke -C code
- API:
  - uvicorn geneweb.adapters.http.app:app --reload -C code
- CLI:
  - geneweb --help

## ADRs

- Voir `docs/adr/0001-strangler-fig.md`
