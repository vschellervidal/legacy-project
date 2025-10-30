# Tutoriel: Tester toutes les nouvelles routes (Lecture + Familles + Suppressions)

## 1) Démarrer l'API

```bash
cd /Users/valentin/Desktop/tek5/piscine/legacy/legacy-project/code
source .venv/bin/activate
uvicorn geneweb.adapters.http.app:app --reload --port 8000
```

## 2) Créer/initialiser une base de test

```bash
python scripts/test_gwd_routes.py --create-base
```

La base est créée dans `/tmp/gwb_test` (I001/I002/I003 + F001).

## 3) Lecture (vérifications rapides)
 
- Accueil
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&use_python=true" | python -m json.tool
```

- Fiche individu (I001)
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&i=I001&use_python=true" | python -m json.tool
```

- Famille F001
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=F&f=F001&use_python=true" | python -m json.tool
```

## 4) Individus (ajout/modification/suppression)

- Ajouter individu (POST, paramètres en query)
```bash
curl -X POST "http://localhost:8000/gwd/add_ind?base=/tmp/gwb_test&id=I900&nom=DOE&prenom=Jane&sexe=F&use_python=true" \
  | python -m json.tool
```

- Vérifier l'ajout
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=NG&v=DOE&use_python=true" | python -m json.tool
```

- Modifier individu (PUT)
```bash
curl -X PUT "http://localhost:8000/gwd/mod_ind?base=/tmp/gwb_test&id=I900&prenom=Janet&use_python=true" \
  | python -m json.tool
```

- Vérifier la modification
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&i=I900&use_python=true" | python -m json.tool
```

- Supprimer individu lié (erreur attendue)
```bash
curl -X DELETE "http://localhost:8000/gwd/del_ind?base=/tmp/gwb_test&id=I001&use_python=true" \
  | python -m json.tool
```

- Supprimer individu lié (force)
```bash
curl -X DELETE "http://localhost:8000/gwd/del_ind?base=/tmp/gwb_test&id=I001&force=true&use_python=true" \
  | python -m json.tool
```

- Vérifier nettoyage des liens
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=F&f=F001&use_python=true" | python -m json.tool
```

## 5) Familles (ajout/modification/suppression)

- Ajouter famille (POST) avec enfants
```bash
curl -X POST "http://localhost:8000/gwd/add_fam?base=/tmp/gwb_test&id=F900&pere_id=I002&mere_id=I003&enfants_ids=I900&use_python=true" \
  | python -m json.tool
```

- Vérifier l'ajout
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=F&f=F900&use_python=true" | python -m json.tool
```

- Modifier famille (PUT) — changer enfants
```bash
curl -X PUT "http://localhost:8000/gwd/mod_fam?base=/tmp/gwb_test&id=F900&enfants_ids=I900&use_python=true" \
  | python -m json.tool
```

- Vérifier la modification
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=F&f=F900&use_python=true" | python -m json.tool
```

- Supprimer famille avec liens (erreur attendue)
```bash
curl -X DELETE "http://localhost:8000/gwd/del_fam?base=/tmp/gwb_test&id=F900&use_python=true" \
  | python -m json.tool
```

- Supprimer famille (force)
```bash
curl -X DELETE "http://localhost:8000/gwd/del_fam?base=/tmp/gwb_test&id=F900&force=true&use_python=true" \
  | python -m json.tool
```

- Vérifier suppression
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=F&f=F900&use_python=true" | python -m json.tool
```

## 6) Notes

- Lister toutes les notes
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=NOTES&use_python=true" | python -m json.tool
```

## 7) Interface Swagger

Ouvrir: `http://localhost:8000/docs`, puis utiliser:
- /gwd (lecture)
- /gwd/add_ind (POST)
- /gwd/mod_ind (PUT)
- /gwd/add_fam (POST)
- /gwd/mod_fam (PUT)
- /gwd/del_ind (DELETE)
- /gwd/del_fam (DELETE)

## Notes
- Tous les paramètres sont lus en query (même pour POST/PUT/DELETE).
- Toujours passer `use_python=true` pour forcer l’implémentation Python.
