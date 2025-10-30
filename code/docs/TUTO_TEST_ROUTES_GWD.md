# Tutoriel : Tester les routes gwd (Issue #34)

Ce guide vous explique étape par étape comment tester les routes de lecture implémentées pour l'issue #34.

---

## 📋 Prérequis

- Python 3.12+ installé
- Environnement virtuel activé
- Dépendances installées
- Une base GWB de test (ou créer une base minimale)

---

## Étape 1 : Vérifier l'environnement

```bash
cd /Users/valentin/Desktop/tek5/piscine/legacy/legacy-project/code
source .venv/bin/activate
python --version  # Doit afficher Python 3.12+
```

Vérifier que les dépendances sont installées :
```bash
pip list | grep fastapi  # Doit être installé
```

---

## Étape 2 : Créer une base GWB de test

### Option A : Utiliser une base existante (si disponible)

Si vous avez déjà une base GWB dans `geneweb/distribution/bases/demo/`, vous pouvez l'utiliser.

### Option B : Créer une base minimale de test

Créez un script Python pour générer une base de test :

```bash
cd /Users/valentin/Desktop/tek5/piscine/legacy/legacy-project/code
python << 'EOF'
from pathlib import Path
from geneweb.domain.models import Individu, Famille, Sexe
from geneweb.io.gwb import write_gwb_minimal

# Créer un répertoire pour la base
test_base = Path("/tmp/gwb_test")
test_base.mkdir(exist_ok=True)

# Créer quelques individus
individus = [
    Individu(
        id="I001",
        nom="DUPONT",
        prenom="Jean",
        sexe=Sexe.M,
        date_naissance=None,
        lieu_naissance="Paris",
        note="Test individu 1",
    ),
    Individu(
        id="I002",
        nom="MARTIN",
        prenom="Marie",
        sexe=Sexe.F,
        date_naissance=None,
        lieu_naissance="Lyon",
        note="Test individu 2",
    ),
    Individu(
        id="I003",
        nom="DUPONT",
        prenom="Pierre",
        sexe=Sexe.M,
        famille_enfance_id="F001",
        note="Enfant de Jean et Marie",
    ),
]

# Créer une famille
familles = [
    Famille(
        id="F001",
        pere_id="I001",
        mere_id="I002",
        enfants_ids=["I003"],
        note="Famille test",
    ),
]

# Écrire la base
write_gwb_minimal(individus, familles, test_base)

print(f"✅ Base de test créée dans : {test_base}")
print(f"   - {len(individus)} individus")
print(f"   - {len(familles)} familles")
EOF
```

Cette commande crée une base dans `/tmp/gwb_test` avec :
- 3 individus (Jean DUPONT, Marie MARTIN, Pierre DUPONT)
- 1 famille (Jean + Marie = Pierre)

---

## Étape 3 : Démarrer le serveur API

Dans un terminal, démarrez le serveur FastAPI :

```bash
cd /Users/valentin/Desktop/tek5/piscine/legacy/legacy-project/code
source .venv/bin/activate
uvicorn geneweb.adapters.http.app:app --reload --port 8000
```

Vous devriez voir :
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

**Gardez ce terminal ouvert** pendant les tests.

---

## Étape 4 : Tester les routes

Ouvrez un **nouveau terminal** (gardez le serveur en arrière-plan).

### Test 1 : Page d'accueil (route vide)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&use_python=true" | python -m json.tool
```

**Résultat attendu** :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "home",
    "type": "home",
    "base": {
        "total_individus": 3,
        "total_familles": 1,
        "total_sources": 0
    }
}
```

**⚠️ Note** : Si vous utilisez une base depuis `GENEWEB_OCAML_ROOT`, remplacez `/tmp/gwb_test` par le nom de la base (ex: `demo`).

---

### Test 2 : Fiche individu (route avec `i`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&i=I001&use_python=true" | python -m json.tool
```

**Résultat attendu** :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "home",
    "type": "person",
    "person": {
        "id": "I001",
        "nom": "DUPONT",
        "prenom": "Jean",
        "sexe": "M",
        "date_naissance": null,
        "lieu_naissance": "Paris",
        "date_deces": null,
        "lieu_deces": null,
        "note": "Test individu 1"
    }
}
```

---

### Test 3 : Recherche simple (mode `S`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=S&use_python=true" | python -m json.tool
```

**Résultat attendu** : Liste de tous les individus triés par nom.

---

### Test 4 : Recherche avec query (mode `NG`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=NG&v=DUPONT&use_python=true" | python -m json.tool
```

**Résultat attendu** :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "search",
    "type": "search",
    "query": "DUPONT",
    "results": [
        {
            "id": "I001",
            "nom": "DUPONT",
            "prenom": "Jean"
        },
        {
            "id": "I003",
            "nom": "DUPONT",
            "prenom": "Pierre"
        }
    ],
    "total": 2
}
```

---

### Test 5 : Fiche famille (mode `F`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=F&f=F001&use_python=true" | python -m json.tool
```

**Résultat attendu** :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "family",
    "type": "family",
    "family": {
        "id": "F001",
        "pere": {
            "id": "I001",
            "nom": "DUPONT",
            "prenom": "Jean"
        },
        "mere": {
            "id": "I002",
            "nom": "MARTIN",
            "prenom": "Marie"
        },
        "enfants": [
            {
                "id": "I003",
                "nom": "DUPONT",
                "prenom": "Pierre"
            }
        ],
        "note": "Famille test"
    }
}
```

---

### Test 6 : Ascendance (mode `A`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=A&i=I003&use_python=true" | python -m json.tool
```

**Résultat attendu** : Liste des ancêtres de I003 (Pierre) :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "ascendance",
    "type": "ascendance",
    "person_id": "I003",
    "ancestors": [
        {
            "id": "I003",
            "nom": "DUPONT",
            "prenom": "Pierre",
            "level": 0
        },
        {
            "id": "I001",
            "nom": "DUPONT",
            "prenom": "Jean",
            "level": 1
        },
        {
            "id": "I002",
            "nom": "MARTIN",
            "prenom": "Marie",
            "level": 1
        }
    ]
}
```

---

### Test 7 : Descendance (mode `D`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=D&i=I001&use_python=true" | python -m json.tool
```

**Résultat attendu** : Liste des descendants de I001 (Jean), incluant lui-même et ses enfants :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "descendance",
    "type": "descendance",
    "person_id": "I001",
    "descendants": [
        {
            "id": "I001",
            "nom": "DUPONT",
            "prenom": "Jean",
            "level": 0
        },
        {
            "id": "I003",
            "nom": "DUPONT",
            "prenom": "Pierre",
            "level": 1
        }
    ]
}
```

---

### Test 8 : Notes (mode `NOTES`)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=NOTES&use_python=true" | python -m json.tool
```

**Résultat attendu** : Liste de toutes les notes (individus, familles, sources) :
```json
{
    "status": "ok",
    "implementation": "python",
    "mode": "notes",
    "type": "notes",
    "person_notes": [
        {
            "type": "person",
            "id": "I001",
            "nom": "DUPONT",
            "prenom": "Jean",
            "note": "Test individu 1"
        },
        {
            "type": "person",
            "id": "I003",
            "nom": "DUPONT",
            "prenom": "Pierre",
            "note": "Enfant de Jean et Marie"
        }
    ],
    "family_notes": [
        {
            "type": "family",
            "id": "F001",
            "note": "Famille test"
        }
    ],
    "source_notes": [],
    "total": 3
}
```

---

## Étape 5 : Tester les erreurs

### Test d'une erreur 404 (individu introuvable)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&i=I999&use_python=true" | python -m json.tool
```

**Résultat attendu** :
```json
{
    "detail": "Individu I999 introuvable"
}
```
Status code : `400 Bad Request`

---

### Test d'une erreur 400 (paramètre manquant)

```bash
curl -X GET "http://localhost:8000/gwd?base=/tmp/gwb_test&mode=A&use_python=true" | python -m json.tool
```

**Résultat attendu** :
```json
{
    "detail": "Paramètre 'i' requis pour la route A (ascendance)"
}
```

---

## Étape 6 : Tester avec le navigateur

Ouvrez votre navigateur et allez sur :

```
http://localhost:8000/docs
```

Vous verrez la documentation interactive Swagger de FastAPI. Vous pouvez tester les routes directement depuis l'interface :

1. Cliquez sur `/gwd`
2. Cliquez sur "Try it out"
3. Remplissez les paramètres :
   - `base` : `/tmp/gwb_test`
   - `mode` : (optionnel, vide pour page d'accueil)
   - `i` : (optionnel, `I001` pour fiche individu)
   - `use_python` : `true`
4. Cliquez sur "Execute"

---

## Étape 7 : Vérifier les logs du serveur

Dans le terminal du serveur, vous devriez voir les requêtes entrantes :

```
INFO:     127.0.0.1:XXXXX - "GET /gwd?base=/tmp/gwb_test&use_python=true HTTP/1.1" 200 OK
```

---

## 🎯 Bonus : Script de test automatique

Créez un script `test_routes.sh` pour tester toutes les routes automatiquement :

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/gwd"
BASE_PARAM="/tmp/gwb_test"

echo "🧪 Test 1: Page d'accueil"
curl -s "$BASE_URL?base=$BASE_PARAM&use_python=true" | python -m json.tool | head -10
echo ""

echo "🧪 Test 2: Fiche individu"
curl -s "$BASE_URL?base=$BASE_PARAM&i=I001&use_python=true" | python -m json.tool | head -15
echo ""

echo "🧪 Test 3: Recherche"
curl -s "$BASE_URL?base=$BASE_PARAM&mode=S&v=DUPONT&use_python=true" | python -m json.tool | head -15
echo ""

echo "🧪 Test 4: Fiche famille"
curl -s "$BASE_URL?base=$BASE_PARAM&mode=F&f=F001&use_python=true" | python -m json.tool | head -20
echo ""

echo "🧪 Test 5: Ascendance"
curl -s "$BASE_URL?base=$BASE_PARAM&mode=A&i=I003&use_python=true" | python -m json.tool | head -20
echo ""

echo "🧪 Test 6: Descendance"
curl -s "$BASE_URL?base=$BASE_PARAM&mode=D&i=I001&use_python=true" | python -m json.tool | head -20
echo ""

echo "🧪 Test 7: Notes"
curl -s "$BASE_URL?base=$BASE_PARAM&mode=NOTES&use_python=true" | python -m json.tool | head -25
echo ""

echo "✅ Tous les tests terminés"
```

Rendez-le exécutable et lancez-le :
```bash
chmod +x test_routes.sh
./test_routes.sh
```

---

## 🐛 Dépannage

### Erreur : "Chemin relatif fourni sans GENEWEB_OCAML_ROOT"

**Solution** : Utilisez un chemin absolu pour `base` :
```bash
curl "http://localhost:8000/gwd?base=/tmp/gwb_test&use_python=true"
```

Ou définissez la variable d'environnement :
```bash
export GENEWEB_OCAML_ROOT=/path/to/geneweb
```

### Erreur : "Base introuvable"

**Solution** : Vérifiez que le répertoire existe et contient `index.json` :
```bash
ls -la /tmp/gwb_test/
cat /tmp/gwb_test/index.json
```

### Le serveur ne démarre pas

**Solution** : Vérifiez que le port 8000 est libre :
```bash
lsof -i :8000  # Voir ce qui utilise le port
```

Ou utilisez un autre port :
```bash
uvicorn geneweb.adapters.http.app:app --reload --port 8001
```

---

## ✅ Vérification finale

Si tous les tests passent, vous devriez voir :

- ✅ Page d'accueil retourne les statistiques de la base
- ✅ Fiche individu retourne les détails de la personne
- ✅ Recherche retourne les individus correspondants
- ✅ Fiche famille retourne les membres de la famille
- ✅ Ascendance retourne les ancêtres
- ✅ Descendance retourne les descendants
- ✅ Notes retourne toutes les notes
- ✅ Les erreurs sont bien gérées (404, 400)

**Félicitations ! Les routes de lecture (Issue #34) fonctionnent ! 🎉**

