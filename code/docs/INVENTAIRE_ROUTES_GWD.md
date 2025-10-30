# Inventaire des routes gwd - Issue #33

Ce document catalogue toutes les routes HTTP du serveur GeneWeb (gwd) pour préparer la migration vers Python.

**Source** : `geneweb/bin/gwd/request.ml` (match sur `m=` ligne 539-873)

**Date** : Après Issue #32 (Services analytiques)

---

## Légende

- **Auth** : Niveau d'authentification requis
  - `N` : Normal (public)
  - `F` : Friend (ami)
  - `W` : Wizard (administrateur)
  - `W+` : Wizard uniquement (pas friend)

- **Lock** : `✓` si nécessite un verrou d'écriture (`w_lock`)

- **Params** : Paramètres URL/query string
  - `b=base` : Nom de la base (requis sauf page d'accueil)
  - `v=value` : Paramètre variable selon la route
  - `i=iper`, `f=ifam` : Identifiants personne/famille

- **Response** : Type de réponse
  - `HTML` : Page HTML complète
  - `JSON` : Format JSON (pour AJAX)
  - `TEXT` : Texte brut
  - `IMAGE` : Image binaire

---

## Routes par catégorie

### 1. Routes de consultation (lecture seule)

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `""` (vide) | Page d'accueil / fiche individu | N | | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `P` | Liste prénoms | N | | `b=base`, `v=prenom`? | HTML | 🟡 MOYENNE |
| `N` | Liste noms | N | | `b=base`, `v=nom`? | HTML | 🟡 MOYENNE |
| `NG` | Recherche avancée | N | | `b=base`, `v=nom`, `fn=prenom`, `sn=nom`, `select=input`? | HTML | 🔴 HAUTE |
| `S` | Recherche par nom | N | | `b=base` | HTML | 🔴 HAUTE |
| `PERSO` | Fiche personnalisée individu | N | | `b=base`, `i=iper` | HTML | 🟡 MOYENNE |
| `F` | Fiche famille | N | | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `A` | Ascendance | N | | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `D` | Descendance | N | | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `R` | Relations entre individus | N | | `b=base`, `i=iper`, `em=R`? | HTML | 🟡 MOYENNE |
| `RL` | Liens de parenté | N | | `b=base` | HTML | 🟢 BASSE |
| `RLM` | Relations multiples | N | | `b=base` | HTML | 🟢 BASSE |
| `C` | Cousins | N | | `b=base`, `i=iper` | HTML | 🟡 MOYENNE |
| `DAG` | Graphe DAG | N | | `b=base` | HTML | 🟢 BASSE |
| `CAL` | Calendrier | N | | `b=base` | HTML | 🟡 MOYENNE |
| `NOTES` | Notes | N | | `b=base`, `ref=on`?, `ajax=on`?, `f=fichier`? | HTML/JSON | 🟡 MOYENNE |
| `LINKED` | Éléments liés à une note | N | | `b=base`, `i=iper` | HTML | 🟢 BASSE |
| `MISC_NOTES` | Notes diverses | N | | `b=base` | HTML | 🟢 BASSE |
| `MISC_NOTES_SEARCH` | Recherche notes diverses | N | | `b=base` | HTML | 🟢 BASSE |
| `SRC` | Sources | N | | `b=base`, `v=fichier` | HTML | 🟡 MOYENNE |
| `H` | Fichier d'aide | N | | `b=base`, `v=fichier` | HTML | 🟡 MOYENNE |
| `DOC` | Documentation | N | | `b=base`, `s=fichier` | HTML | 🟡 MOYENNE |
| `DOCH` | Documentation HTML | N | | `b=base`, `s=fichier` | HTML | 🟢 BASSE |
| `HIST` | Historique modifications | N | | `b=base` | HTML | 🟡 MOYENNE |
| `HIST_SEARCH` | Recherche historique | N | | `b=base` | HTML | 🟢 BASSE |
| `HIST_DIFF` | Diff historique | N | | `b=base` | HTML | 🟢 BASSE |
| `STAT` | Statistiques | N | | `b=base` | HTML | 🟡 MOYENNE |
| `TT` | Titres | N | | `b=base` | HTML | 🟡 MOYENNE |
| `PS` | Lieux avec noms | N | | `b=base` | HTML | 🟡 MOYENNE |
| `PPS` | Tous lieux avec noms | N | | `b=base` | HTML | 🟢 BASSE |
| `CHK_DATA` | Vérification données | N | | `b=base` | HTML | 🟢 BASSE |

---

### 2. Routes d'images et médias

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `IM` | Affichage image | N | | `b=base`, `v=filename` | IMAGE | 🟡 MOYENNE |
| `IM_C` | Carrousel images (non sauvegardé) | N | | `b=base` | HTML | 🟢 BASSE |
| `IM_C_S` | Carrousel images (sauvegardé) | N | | `b=base` | HTML | 🟢 BASSE |
| `IMH` | Image HTML | N | | `b=base` | HTML | 🟢 BASSE |
| `FIM` | Blason | N | | `b=base` | HTML | 🟢 BASSE |

---

### 3. Routes anniversaires et événements

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `ANM` | Anniversaires du mois | N | | `b=base` | HTML | 🟡 MOYENNE |
| `AN` | Anniversaires naissances | N | | `b=base`, `v=annee`? | HTML | 🟡 MOYENNE |
| `AD` | Anniversaires décès | N | | `b=base`, `v=annee`? | HTML | 🟡 MOYENNE |
| `AM` | Anniversaires mariages | N | | `b=base`, `v=annee`? | HTML | 🟡 MOYENNE |
| `LB` | Liste naissances (wizard/friend) | F/W | | `b=base` | HTML | 🟢 BASSE |
| `LD` | Liste décès (wizard/friend) | F/W | | `b=base` | HTML | 🟢 BASSE |
| `LM` | Liste mariages (wizard/friend) | F/W | | `b=base` | HTML | 🟢 BASSE |
| `LL` | Plus longévives | N | | `b=base` | HTML | 🟢 BASSE |
| `OA` | Plus anciens vivants (wizard/friend) | F/W | | `b=base` | HTML | 🟢 BASSE |
| `OE` | Plus anciens engagements (wizard/friend) | F/W | | `b=base` | HTML | 🟢 BASSE |
| `POP_PYR` | Pyramide population (wizard/friend) | F/W | | `b=base` | HTML | 🟢 BASSE |

---

### 4. Routes de recherche avancée

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `AS` | Recherche avancée | N | | `b=base` | HTML | 🟡 MOYENNE |
| `AS_OK` | Résultats recherche avancée | N | | `b=base` | HTML | 🟡 MOYENNE |

---

### 5. Routes de modification (Wizard uniquement)

#### 5.1. Ajout de données

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `ADD_IND` | Formulaire ajout individu | W | | `b=base` | HTML | 🔴 HAUTE |
| `ADD_IND_OK` | Validation ajout individu | W | ✓ | `b=base` | HTML | 🔴 HAUTE |
| `ADD_FAM` | Formulaire ajout famille | W | | `b=base` | HTML | 🔴 HAUTE |
| `ADD_FAM_OK` | Validation ajout famille | W | ✓ | `b=base` | HTML | 🔴 HAUTE |
| `ADD_PAR` | Ajout parents | W | | `b=base` | HTML | 🟡 MOYENNE |
| `ADD_PAR_OK` | Validation ajout parents | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |

#### 5.2. Modification de données

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `MOD_IND` | Formulaire modification individu | W | | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `MOD_IND_OK` | Validation modification individu | W | ✓ | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `MOD_FAM` | Formulaire modification famille | W | | `b=base`, `f=ifam` | HTML | 🔴 HAUTE |
| `MOD_FAM_OK` | Validation modification famille | W+ | ✓ | `b=base`, `f=ifam` | HTML | 🔴 HAUTE |
| `MOD_NOTES` | Modification notes | W | | `b=base`, `ajax=on`? | HTML/JSON | 🟡 MOYENNE |
| `MOD_NOTES_OK` | Validation modification notes | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `MOD_WIZNOTES` | Modification notes wizard | W | | `b=base` | HTML | 🟢 BASSE |
| `MOD_WIZNOTES_OK` | Validation notes wizard | W | ✓ | `b=base` | HTML | 🟢 BASSE |
| `MOD_DATA` | Modification données base | W | | `b=base` | HTML | 🟡 MOYENNE |
| `MOD_DATA_OK` | Validation modification données | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `CHG_CHN` | Changer ordre enfants | W | | `b=base`, `f=ifam` | HTML | 🟡 MOYENNE |
| `CHG_CHN_OK` | Validation ordre enfants | W | ✓ | `b=base`, `f=ifam` | HTML | 🟡 MOYENNE |
| `CHG_FAM_ORD` | Changer ordre familles | W | | `b=base`, `i=iper` | HTML | 🟡 MOYENNE |
| `CHG_FAM_ORD_OK` | Validation ordre familles | W | ✓ | `b=base`, `i=iper` | HTML | 🟡 MOYENNE |
| `CHG_EVT_IND_ORD` | Changer ordre événements individu | W | | `b=base`, `i=iper` | HTML | 🟢 BASSE |
| `CHG_EVT_IND_ORD_OK` | Validation ordre événements individu | W | ✓ | `b=base`, `i=iper` | HTML | 🟢 BASSE |
| `CHG_EVT_FAM_ORD` | Changer ordre événements famille | W | | `b=base`, `f=ifam` | HTML | 🟢 BASSE |
| `CHG_EVT_FAM_ORD_OK` | Validation ordre événements famille | W | ✓ | `b=base`, `f=ifam` | HTML | 🟢 BASSE |

#### 5.3. Suppression de données

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `DEL_IND` | Formulaire suppression individu | W | | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `DEL_IND_OK` | Validation suppression individu | W | ✓ | `b=base`, `i=iper` | HTML | 🔴 HAUTE |
| `DEL_FAM` | Formulaire suppression famille | W | | `b=base`, `f=ifam` | HTML | 🔴 HAUTE |
| `DEL_FAM_OK` | Validation suppression famille | W | ✓ | `b=base`, `f=ifam` | HTML | 🔴 HAUTE |
| `DEL_IMAGE` | Suppression image | W | | `b=base` | HTML | 🟡 MOYENNE |
| `DEL_IMAGE_OK` | Validation suppression image | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `DEL_IMAGE_C_OK` | Validation suppression image carrousel | W | ✓ | `b=base` | HTML | 🟢 BASSE |
| `KILL_ANC` | Supprimer ancêtres | W | ✓ | `b=base`, `i=iper` | HTML | 🟢 BASSE |

#### 5.4. Fusion de données

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `MRG` | Formulaire fusion individu | W | | `b=base`, `i=iper` | HTML | 🟡 MOYENNE |
| `MRG_IND` | Fusion individus | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_IND_OK` | Validation fusion individu | W | | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_MOD_IND_OK` | Validation fusion modifiée individu | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_FAM` | Formulaire fusion famille | W | | `b=base`, `f=ifam` | HTML | 🟡 MOYENNE |
| `MRG_FAM_OK` | Validation fusion famille | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_MOD_FAM_OK` | Validation fusion modifiée famille | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_DUP` | Fusion doublons | W | | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_DUP_IND_Y_N` | Confirmation fusion doublon individu | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `MRG_DUP_FAM_Y_N` | Confirmation fusion doublon famille | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |

#### 5.5. Inversion de relations

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `INV_FAM` | Inverser famille | W | | `b=base`, `f=ifam` | HTML | 🟡 MOYENNE |
| `INV_FAM_OK` | Validation inversion famille | W | ✓ | `b=base`, `f=ifam` | HTML | 🟡 MOYENNE |

---

### 6. Routes gestion images (Wizard)

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `SND_IMAGE` | Envoi image | W | | `b=base` | HTML | 🟡 MOYENNE |
| `SND_IMAGE_OK` | Validation envoi image | W | ✓ | `b=base` | HTML | 🟡 MOYENNE |
| `SND_IMAGE_C` | Carrousel envoi image | W | | `b=base`, `i=iper` | HTML | 🟢 BASSE |
| `SND_IMAGE_C_OK` | Validation carrousel envoi | W | ✓ | `b=base` | HTML | 🟢 BASSE |
| `IMAGE_TO_BLASON` | Conversion image → blason | W | | `b=base` | HTML | 🟢 BASSE |
| `PORTRAIT_TO_BLASON` | Conversion portrait → blason | W | | `b=base` | HTML | 🟢 BASSE |
| `BLASON_MOVE_TO_ANC` | Déplacer blason ancêtres | W | | `b=base` | HTML | 🟢 BASSE |
| `BLASON_STOP` | Arrêter blason | W | | `b=base` | HTML | 🟢 BASSE |
| `RESET_IMAGE_C_OK` | Réinitialiser carrousel | W | | `b=base` | HTML | 🟢 BASSE |

---

### 7. Routes notes wizard

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `WIZNOTES` | Notes wizard | W | | `b=base` | HTML | 🟢 BASSE |
| `WIZNOTES_SEARCH` | Recherche notes wizard | W | | `b=base` | HTML | 🟢 BASSE |
| `VIEW_WIZNOTES` | Visualisation notes wizard | W | | `b=base` | HTML | 🟢 BASSE |
| `CONN_WIZ` | Wizards connectés | W | | `b=base` | HTML | 🟢 BASSE |
| `CHANGE_WIZ_VIS` | Changer visibilité wizard | W | ✓ | `b=base` | HTML | 🟢 BASSE |

---

### 8. Routes utilitaires

| Route | Description | Auth | Lock | Params | Response | Priorité |
|-------|-------------|------|------|--------|----------|----------|
| `REQUEST` | Afficher requête HTTP brute | W | | `b=base` | TEXT | 🟢 BASSE |
| `U` | Menu mise à jour | W | | `b=base`, `i=iper` | HTML | 🟡 MOYENNE |
| `TP` | Template personnalisé | N | | `b=base`, `v=template`, `i=iper`? | HTML | 🟢 BASSE |
| `L` | Liste (template) | N | | `b=base` | HTML | 🟡 MOYENNE |

---

## Résumé par priorité

### 🔴 HAUTE (Routes critiques - migration en premier)
- Page d'accueil (`""`)
- Recherche (`NG`, `S`)
- Fiches individu/famille (`F`, `PERSO`)
- Ascendance/Descendance (`A`, `D`)
- Ajout/Modification/Suppression (`ADD_*`, `MOD_*`, `DEL_*`)

**Total : ~20 routes**

### 🟡 MOYENNE (Routes importantes)
- Anniversaires (`AN`, `AD`, `AM`, `ANM`)
- Notes (`NOTES`, `MOD_NOTES`)
- Statistiques (`STAT`)
- Recherche avancée (`AS`, `AS_OK`)
- Images (`IM`, `SND_IMAGE`)
- Fusion (`MRG_*`)
- Autres consultations

**Total : ~30 routes**

### 🟢 BASSE (Routes secondaires - migration ultérieure)
- Routes spécialisées wizard (`WIZNOTES_*`, `CONN_WIZ`)
- Manipulations images avancées (`*BLASON*`, `*IMAGE_C*`)
- Routes peu utilisées (`DAG`, `CHK_DATA`, etc.)

**Total : ~40 routes**

---

## Authentification et sécurité

### Schémas d'authentification
1. **Basic Auth** : `user:password` en base64 dans header `Authorization: Basic ...`
2. **Digest Auth** : Schéma digest (option `-digest`)
3. **Token Auth** : Token dans URL (`b=base_token`) ou cookie
4. **File Auth** : Fichier `.auth` avec `user:password`

### Contrôles d'accès
- **Verrous écriture** (`w_lock`) : Nécessaire pour toutes les routes de modification
- **Vérification wizard** (`w_wizard`) : Droit administrateur requis
- **Vérification friend** : Accès ami (lecture étendue)
- **Vérification base** (`w_base`) : Base de données valide requise
- **Vérification personne** (`w_person`) : Individu valide requis

### Routes sans authentification
Routes publiques (`N`) : Page d'accueil, recherche, consultation, statistiques de base

---

## Paramètres URL communs

| Param | Description | Exemple | Route |
|-------|-------------|---------|-------|
| `b` | Nom base | `b=demo` | Toutes |
| `m` | Mode/route | `m=NG` | Toutes |
| `i` | ID individu (iper) | `i=I001` | Routes individu |
| `f` | ID famille (ifam) | `f=F001` | Routes famille |
| `v` | Valeur variable | `v=annee` | Variables selon route |
| `lang` | Langue | `lang=fr` | Internationalisation |
| `w` | Mot de passe wizard/friend | `w=wizard` | Authentification |
| `ajax` | Mode AJAX | `ajax=on` | Retour JSON |
| `em` | Mode d'affichage | `em=R` (relations) | Variantes |
| `s` | Fichier source/doc | `s=help.txt` | Documentation |
| `fn` | Prénom | `fn=Jean` | Recherche |
| `sn` | Nom | `sn=Dupont` | Recherche |
| `select` | Mode sélection | `select=input` | Recherche avancée |

---

## Headers HTTP

### Headers requis
- `Host` : Nom d'hôte
- (Optionnel) `Authorization: Basic ...` ou `Digest ...`

### Headers optionnels
- `Accept-Language` : Pour détection langue navigateur (`-blang`)
- `Referer` : Loggé pour audit
- `User-Agent` : Détection robots
- `Content-Type` : Pour POST multipart/form-data

### Headers de réponse
- `Content-Type` : `text/html; charset=UTF-8` (défaut)
- `Content-Type: application/json` : Pour routes AJAX
- `Content-Type: image/*` : Pour routes images
- `WWW-Authenticate` : Pour 401 Unauthorized

---

## Format des réponses

### HTML
La plupart des routes retournent du HTML avec :
- Template Jinja2-like (`Templ.interp_templ`)
- Internationalisation via `transl conf`
- En-tête/pied de page (`Hutil.header/trailer`)

### JSON
Routes avec paramètre `ajax=on` :
- `MOD_NOTES` : `NotesDisplay.print_mod_json`
- `NOTES` : `NotesDisplay.print_json`

### Texte brut
- `REQUEST` : Retourne la requête HTTP brute

### Images binaires
- `IM` : Images stockées dans base
- Support formats : JPG, PNG, GIF, etc.

---

## Routes spéciales

### Mode IM (Images)
- `m=IM` : Affichage image via paramètre `v=filename`
- Ne nécessite pas de base de données (`b=base` optionnel)
- Géré avant le traitement principal (`image_request`)

### Mode robots.txt
- Route spéciale : `/robots.txt`
- Retourne fichier `robots` ou default si absent
- Géré avant traitement principal

### Pages d'erreur
- **404 Not Found** : Route `m=XXX` inconnue
- **401 Unauthorized** : Accès refusé (wizard/friend requis)
- **403 Forbidden** : Base réservée
- **400 Bad Request** : Requête incorrecte

---

## Priorisation pour migration

### Phase 1 (Issue #34) - Routes lecture critiques
1. Page d'accueil (`""`)
2. Recherche (`S`, `NG`)
3. Fiche individu (`PERSO`, route par défaut)
4. Fiche famille (`F`)
5. Ascendance/Descendance (`A`, `D`)
6. Notes (`NOTES`)

**Objectif** : Migration des consultations de base

### Phase 2 - Routes modification essentielles
1. Ajout individu/famille (`ADD_IND`, `ADD_FAM`)
2. Modification (`MOD_IND`, `MOD_FAM`)
3. Suppression (`DEL_IND`, `DEL_FAM`)
4. Fusion (`MRG_IND`, `MRG_FAM`)

**Objectif** : Migration des opérations CRUD principales

### Phase 3 - Routes avancées
1. Recherche avancée (`AS`)
2. Statistiques (`STAT`)
3. Anniversaires (`AN`, `AD`, `AM`)
4. Images (`IM`, `SND_IMAGE`)

**Objectif** : Migration des fonctionnalités secondaires

### Phase 4 - Routes spécialisées
1. Notes wizard (`WIZNOTES_*`)
2. Images avancées (`*BLASON*`)
3. Routes utilitaires (`REQUEST`, `TP`, etc.)

**Objectif** : Complétion migration

---

## Notes techniques

### Gestion des erreurs
- Toutes les routes passent par `incorrect_request` en cas d'erreur
- Erreurs capturées dans `treat_request` avec gestion exceptions
- Logging via `Logs.syslog` avec niveaux (`LOG_CRIT`, `LOG_WARNING`, etc.)

### Performance
- Compteur d'accès automatique (sauf routes `IM`, `IM_C`, `SRC`, `DOC`)
- Timeout configurable (`conn_timeout`, `login_timeout`)
- Support workers multiples (`n_workers`)

### Internationalisation
- Langue détectée via `Accept-Language` ou paramètre `lang=`
- Lexique chargé dynamiquement (`load_lexicon`)
- Support RTL (`is_rtl`)

### Plugins
- Routes peuvent être interceptées par plugins (`try_plugin`)
- Plugins peuvent ajouter leurs propres routes

---

## Prochaines étapes

1. ✅ **Issue #33** : Inventaire routes (ce document)
2. 🔲 **Issue #34** : Migration routes lecture (Phase 1)
3. 🔲 **Issue #35** : Migration routes modification (Phase 2)
4. 🔲 **Issue #36** : Migration routes avancées (Phase 3-4)
5. 🔲 **Issue #37** : Proxy compatibilité URL

---

**Statut** : ✅ Complété (Issue #33)

