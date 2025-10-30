# Proxy de compatibilité gwd (Issue #37)

Objectif: ne pas casser les anciens liens gwd (ex: `gw.cgi`) en les redirigeant vers les nouvelles routes `/gwd`.

## Routes
- GET /gw.cgi (ancien)
- GET /compat/gw (alias)

Ces routes redirigent (301) vers `/gwd` avec les paramètres convertis.

## Paramètres legacy pris en charge
- b ou base : chemin/nom de la base
- m : mode (ex: F, S, NG, A, D, NOTES, PERSO)
- i : id individu (iper)
- f : id famille (ifam)
- v : valeur générique (recherche)
- use_python : true pour forcer Python

## Exemples
- Ancien lien famille:
  - Entrée: /gw.cgi?b=/tmp/gwb_test&m=F&f=F001
  - Redirection: /gwd?base=/tmp/gwb_test&mode=F&f=F001

- Ancien lien recherche avancée:
  - Entrée: /gw.cgi?b=/tmp/gwb_test&m=NG&v=DUPONT&use_python=true
  - Redirection: /gwd?base=/tmp/gwb_test&mode=NG&v=DUPONT&use_python=true

- Ancien lien ascendance:
  - Entrée: /gw.cgi?b=/tmp/gwb_test&m=A&i=I003
  - Redirection: /gwd?base=/tmp/gwb_test&mode=A&i=I003

## Test rapide
- Voir l’URL de redirection:
```bash
curl -I "http://localhost:8000/gw.cgi?b=/tmp/gwb_test&m=A&i=I003"
```
- Suivre la redirection et afficher le JSON:
```bash
curl -L "http://localhost:8000/compat/gw?base=/tmp/gwb_test&m=NG&v=DUPONT&use_python=true" | python3 -m json.tool
```

## Remarques
- Redirection 301 = mise à jour durable des liens (navigateur/moteurs la mémorisent)
- Paramètres non listés: transmis tels quels dans mode (best-effort)
