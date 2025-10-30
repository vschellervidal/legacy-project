# Manuel utilisateur – Routes gwd (Notes wizard, Images avancées, Utilitaires)

Ce guide explique simplement à quoi servent ces routes, comment les appeler et quoi attendre en retour.

Prérequis
- Démarrer l’API: `uvicorn geneweb.adapters.http.app:app --reload --port 8000`
- Avoir une base de test: `python scripts/test_gwd_routes.py --create-base` (créée dans `/tmp/gwb_test`)
- Remplacer les chemins/IDs si besoin

Conseils
- Pour formater l’affichage JSON: ajouter `| python3 -m json.tool` (ou `| jq .`)
- Les paramètres sont passés en query (dans l’URL), même pour POST/PUT/DELETE

---

## 1) Notes Wizard (privées)
But: gérer des notes privées “wizard” (administration). Stockées dans `wizard_notes.json` à la racine de la base.

Lister toutes les notes (filtre optionnel)
- Usage: Afficher toutes les notes ou filtrer par mot-clé
- Appel:
  - Toutes: `GET /gwd/wiznotes?base=/tmp/gwb_test`
  - Filtre: `GET /gwd/wiznotes?base=/tmp/gwb_test&q=Jean`
- Attendu: `{ "notes": {"IND:I001": "...", "FAM:F001": "..."} }`

Lire une note
- Usage: Récupérer la note liée à une clé (ex: individu/famille)
- Appel: `GET /gwd/wiznotes/item?base=/tmp/gwb_test&key=IND:I001`
- Attendu: `{ "key": "IND:I001", "note": "..." }` (404 si inconnue)

Créer/éditer une note
- Usage: Créer ou remplacer la note liée à une clé
- Appel: `PUT /gwd/wiznotes/item?base=/tmp/gwb_test&key=IND:I001&note=Note%20priv%C3%A9e`
- Attendu: `{ "key": "IND:I001", "note": "Note privée" }`

Supprimer une note
- Usage: Effacer une note
- Appel: `DELETE /gwd/wiznotes/item?base=/tmp/gwb_test&key=IND:I001`
- Attendu: `{ "status": "ok" }` (404 si inconnue)

---

## 2) Images avancées (carrousel/blason)
But: faciliter la navigation des images et associer un blason à un individu.

Lister les images pour carrousel
- Usage: Lister les fichiers images (filtrage heuristique par ID dans le nom)
- Appel: `GET /gwd/images/carrousel?base=/tmp/gwb_test&i=I001`
- Attendu: `{ "images": ["/abs/path/.../I001_photo.png", ...] }`
- Remarques: les images sont cherchées dans `images/`, sinon `img/`, `media/`, sinon la racine de la base

Télécharger une image (binaire)
- Usage: Récupérer le fichier image
- Appel: `GET /gwd/images/file?base=/tmp/gwb_test&path=images/I001_photo.png`
- Attendu: octets du fichier + `Content-Type` correct (ex: `image/png`)

Associer un blason à un individu
- Usage: Renseigner l’image blason principale d’un individu
- Appel: `PUT /gwd/images/blason?base=/tmp/gwb_test&i=I001&image=blason.png`
- Attendu: `{ "person_id": "I001", "blason": "blason.png" }`
- Détails: associations stockées dans `blasons.json`

---

## 3) Utilitaires (pratiques)
But: diagnostics et vérifications rapides.

Echo requête (debug)
- Usage: Voir le verbe, l’URL et les en-têtes reçus par l’API
- Appel: `GET /gwd/util/request`
- Attendu: `{ "method": "GET", "url": "...", "headers": { ... } }`

Vérification de cohérence (liens)
- Usage: détecter les IDs référencés inexistants (parents/enfants)
- Appel: `GET /gwd/util/chk_data?base=/tmp/gwb_test`
- Attendu: `{ "ok": true|false, "errors": ["FAMILLE F1: père inconnu I999", ...] }`

Historique (placeholder)
- Usage: point d’extension pour un historique web
- Appel: `GET /gwd/util/hist`
- Attendu: `{ "events": [] }` (facile à enrichir)

---

## Codes d’erreur usuels
- 400 Bad Request: paramètres manquants/invalides
- 404 Not Found: base ou ressource introuvable (image/note/clé)
- 500 Internal Server Error: erreur interne inattendue

---

## Exemples rapides (copier-coller)

Lister les notes:
```bash
curl "http://localhost:8000/gwd/wiznotes?base=/tmp/gwb_test" | python3 -m json.tool
```
Mettre une note:
```bash
curl -X PUT "http://localhost:8000/gwd/wiznotes/item?base=/tmp/gwb_test&key=IND:I001&note=Note%20priv%C3%A9e" | python3 -m json.tool
```
Lister des images:
```bash
curl "http://localhost:8000/gwd/images/carrousel?base=/tmp/gwb_test&i=I001" | python3 -m json.tool
```
Télécharger une image:
```bash
curl -OJ "http://localhost:8000/gwd/images/file?base=/tmp/gwb_test&path=images/I001_photo.png"
```
Associer un blason:
```bash
curl -X PUT "http://localhost:8000/gwd/images/blason?base=/tmp/gwb_test&i=I001&image=blason.png" | python3 -m json.tool
```
Vérifier la cohérence:
```bash
curl "http://localhost:8000/gwd/util/chk_data?base=/tmp/gwb_test" | python3 -m json.tool
```

---

Besoin d’autres exemples? Ouvrir Swagger: `http://localhost:8000/docs` (bouton “Try it out”).
