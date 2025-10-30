# Fixtures pour services analytiques (consang, connex)

Ce dossier contient les fixtures et snapshots pour les tests de caractérisation des services analytiques (Issue #29).

## Structure

```
analytical/
├── consang/
│   ├── simple_consang.gwb/    # Base avec cas de consanguinité (cousins)
│   └── snapshots/              # Snapshots des sorties OCaml
├── connex/
│   ├── disconnected.gwb/       # Base avec composantes connexes séparées
│   └── snapshots/              # Snapshots des sorties OCaml
└── README.md                   # Ce fichier
```

## Génération des fixtures

Les fixtures GWB sont générées dynamiquement dans les tests à partir de GEDCOM.
Les snapshots sont capturés en exécutant les commandes OCaml :

```bash
# Générer snapshot consang
consang -qq <base.gwb/base> > snapshots/consang_simple.txt

# Générer snapshot connex
connex -a <base.gwb/base> > snapshots/connex_disconnected.txt
```

## Budgets de performance

Pour une base avec ~10 individus :
- `consang`: < 5s en mode `-fast`, < 10s en mode normal
- `connex`: < 5s

Ces budgets seront utilisés pour valider les implémentations Python (Issues #30, #31).

## Usage

Les tests sont marqués avec `@pytest.mark.skipif` et nécessitent :
- `RUN_OCAML_TESTS=1` dans l'environnement
- `GENEWEB_OCAML_ROOT` pointant vers le repo OCaml compilé

