# Plan de Migration GeneWeb OCaml vers Python

## 🎯 **Vue d'ensemble**

Ce document présente le plan complet de migration du projet GeneWeb d'OCaml vers Python, organisé en **épiques** (milestones) avec des issues petites et homogènes. Chaque issue inclut : objectif et critères d'acceptation.

## 📋 **Épiques de Migration**

### **0) Initialisation et standards** ✅ **TERMINÉ**

#### **Issue #1 : Mettre en place pyproject, arborescence, venv et deps**
- **Objectif** : Structure de base du projet Python
- **Acceptation** : `pyproject.toml`, `src/geneweb/`, `tests/`, venv OK, `install -e` OK
- **Statut** : ✅ **TERMINÉ**

#### **Issue #2 : Configurer Ruff/Mypy/Pytest/Pre-commit**
- **Objectif** : Outils de qualité de code
- **Acceptation** : `ruff format + lint` OK, `mypy` OK, `pytest` OK, hooks installés
- **Statut** : ✅ **TERMINÉ**

#### **Issue #3 : Pipeline CI (lint + mypy + tests)**
- **Objectif** : Intégration continue automatisée
- **Acceptation** : workflow GitHub vert sur PR ; matrice Python 3.11/3.12
- **Statut** : ✅ **TERMINÉ**

### **1) Pont OCaml et tests de fumée (oracle)** ✅ **TERMINÉ**

#### **Issue #4 : Bridge subprocess vers binaires OCaml**
- **Objectif** : Interface Python vers binaires OCaml
- **Acceptation** : exécuter `gwb2ged`, `ged2gwb`, `gwd` via env `GENEWEB_OCAML_ROOT`, timeouts/erreurs gérés
- **Statut** : ✅ **TERMINÉ**

#### **Issue #5 : Test smoke parité gwb2ged (demo.gwb)**
- **Objectif** : Validation de parité fonctionnelle
- **Acceptation** : test passe/skip si demo manquante ; GEDCOM commence par `HEAD`
- **Statut** : ✅ **TERMINÉ**

#### **Issue #6 : Doc d'utilisation (README + ADR "strangler fig")**
- **Objectif** : Documentation stratégique et utilisateur
- **Acceptation** : README clair ; 1 ADR expliquant la stratégie de migration
- **Statut** : ✅ **TERMINÉ**

### **2) CLI et API squelette** ✅ **TERMINÉ**

#### **Issue #7 : CLI Typer de base (gwb2ged, ged2gwb via bridge)**
- **Objectif** : Interface ligne de commande moderne
- **Acceptation** : `geneweb gwb2ged -i … -o …` fonctionne ; codes retour mappés
- **Statut** : ✅ **TERMINÉ**

#### **Issue #8 : API FastAPI minimale (healthz + export proxy)**
- **Objectif** : Interface web API de base
- **Acceptation** : `/healthz` OK ; `/export/gwb2ged?input_dir=…` renvoie stdout ou erreur
- **Statut** : ✅ **TERMINÉ**

### **3) Caractérisation approfondie de gwb2ged (tests de parité)** 📅 **PLANNIFIÉ**

#### **Issue #9 : Fixtures d'entrée GWB (petites, moyennes, cas tordus)**
- **Objectif** : Jeu de données de test varié
- **Acceptation** : dossier fixtures versionné ; README sur la provenance
- **Statut** : ✅ **TERMINÉ**

#### **Issue #10 : Snapshots GEDCOM (normalisés)**
- **Objectif** : Tests de régression automatisés
- **Acceptation** : tests qui comparent sortie OCaml vs snapshots avec normalisation espaces/ordre

#### **Issue #11 : Benchmarks de base (temps/mémoire)**
- **Objectif** : Métriques de performance de référence
- **Acceptation** : `pytest-benchmark` sur 2-3 fixtures ; seuils et rapport

### **4) Portage Python de gwb2ged (par étapes atomiques)** 📅 **PLANNIFIÉ**

#### **Issue #12 : Modèles de domaine (individus, familles, événements, sources)**
- **Objectif** : Structure de données pour la logique métier
- **Acceptation** : dataclasses/typing Pydantic pour I/O ; mypy OK

#### **Issue #13 : Lecture GWB minimal (index + individus basiques)**
- **Objectif** : Parser GWB de base
- **Acceptation** : charger noms/ids/sexes ; test unitaire sur petite fixture

#### **Issue #14 : Sérialisation GEDCOM minimal (HEAD, INDI avec NOM/SEX)**
- **Objectif** : Générateur GEDCOM de base
- **Acceptation** : générer GEDCOM valide ; snapshot de parité partielle passe

#### **Issue #15 : Événements vitaux (BIRT/DEAT avec dates/lieux)**
- **Objectif** : Support des événements de naissance et décès
- **Acceptation** : parité sur ces champs ; tests props sur dates

#### **Issue #16 : Familles et liens (FAM, HUSB/WIFE/CHIL)**
- **Objectif** : Structure des familles et relations
- **Acceptation** : structure FAM correcte ; parité structurelle

#### **Issue #17 : Notes, sources et médias (NOTE/SOUR/OBJE) — si pertinents**
- **Objectif** : Métadonnées et médias
- **Acceptation** : champs supportés avec fallback propre si manquants

#### **Issue #18 : Encodage/Unicode/normalisation**
- **Objectif** : Gestion robuste des caractères spéciaux
- **Acceptation** : sorties UTF‑8 stables ; tests sur caractères spéciaux

#### **Issue #19 : Comparateur complet Python vs OCaml (diff lisible)**
- **Objectif** : Outil de validation de parité
- **Acceptation** : outil qui met en évidence différences sémantiques

#### **Issue #20 : Bascule CLI/API gwb2ged sur impl Python (feature flag)**
- **Objectif** : Migration progressive avec rollback
- **Acceptation** : flag env/CLI pour choisir Python ou OCaml ; default=OCaml

### **5) Portage Python de ged2gwb (mêmes étapes symétriques)** 📅 **PLANNIFIÉ**

#### **Issue #21 : Parser GEDCOM minimal → modèle**
- **Objectif** : Import de données GEDCOM de base
- **Acceptation** : importer INDI/FAM de base ; tests unitaires

#### **Issue #22 : Écriture GWB minimal**
- **Objectif** : Export vers format GWB
- **Acceptation** : produire structure GWB simple ; parité structurelle

#### **Issue #23 : Événements ged2gwb**
- **Objectif** : Support des événements dans ged2gwb
- **Acceptation** : parité sur événements ; tests de régression

#### **Issue #24 : Familles ged2gwb**
- **Objectif** : Support des familles dans ged2gwb
- **Acceptation** : parité sur familles ; tests de régression

#### **Issue #25 : Notes/sources ged2gwb**
- **Objectif** : Support des métadonnées dans ged2gwb
- **Acceptation** : parité sur notes/sources ; tests de régression

#### **Issue #26 : Encodage ged2gwb**
- **Objectif** : Gestion des caractères spéciaux dans ged2gwb
- **Acceptation** : parité sur encodage ; tests de régression

#### **Issue #27 : Diff GWB (comparateur)**
- **Objectif** : Outil de validation pour ged2gwb
- **Acceptation** : outil qui met en évidence différences sémantiques

#### **Issue #28 : Switch CLI/API ged2gwb sur impl Python**
- **Objectif** : Migration progressive ged2gwb
- **Acceptation** : flag env/CLI pour choisir Python ou OCaml ; default=OCaml

### **6) Services analytiques (exécutables OCaml: consang, connex…)** 📅 **PLANNIFIÉ**

#### **Issue #29 : Tests de caractérisation (entrées/sorties)**
- **Objectif** : Validation des services analytiques
- **Acceptation** : fixtures + snapshots ; budgets perf

#### **Issue #30 : Impl Python consanguinité (algorithmes + tests props)**
- **Objectif** : Calcul de consanguinité en Python
- **Acceptation** : parité chiffrée sur fixtures

#### **Issue #31 : Impl Python connexité**
- **Objectif** : Calcul de connexité en Python
- **Acceptation** : parité chiffrée sur fixtures

#### **Issue #32 : Switch CLI/API pour ces services**
- **Objectif** : Migration des services analytiques
- **Acceptation** : flag de bascule ; doc utilisateur

### **7) Migration du serveur HTTP gwd (par groupes de routes)** 📅 **PLANNIFIÉ**

#### **Issue #33 : Inventaire routes gwd (+ params, auth, headers)**
- **Objectif** : Cartographie des fonctionnalités web
- **Acceptation** : doc table routes ; priorisation

#### **Issue #34 : Groupe 1 routes "lecture" (ex: fiche individu)**
- **Objectif** : Migration des routes de consultation
- **Acceptation** : réponses identiques (HTML/JSON) sur fixtures

#### **Issue #35 : Groupe 2 routes (répéter par groupes fonctionnels)**
- **Objectif** : Migration des routes de groupe 2
- **Acceptation** : parité ; benchs ; logs structurés

#### **Issue #36 : Groupe N routes (répéter par groupes fonctionnels)**
- **Objectif** : Migration des routes de groupe N
- **Acceptation** : parité ; benchs ; logs structurés

#### **Issue #37 : Proxy de compatibilité URL + redirections**
- **Objectif** : Maintien de la compatibilité des liens
- **Acceptation** : liens historiques non cassés

### **8) Observabilité, qualité et distribution** 📅 **PLANNIFIÉ**

#### **Issue #38 : Logs structurés + correlation id**
- **Objectif** : Observabilité et debugging
- **Acceptation** : format JSON, niveau, docs extraction

#### **Issue #39 : Metrics Prometheus (si utile)**
- **Objectif** : Monitoring des performances
- **Acceptation** : endpoint `/metrics` ; compteurs de base

#### **Issue #40 : Packaging release (versioning, changelog)**
- **Objectif** : Distribution du projet
- **Acceptation** : tags semver, CHANGELOG, build wheel

#### **Issue #41 : Doc utilisateur + API (OpenAPI/Jinja2)**
- **Objectif** : Documentation complète
- **Acceptation** : doc up-to-date ; exemples CLI/API

### **9) Décommission progressif OCaml** 📅 **PLANNIFIÉ**

#### **Issue #42 : Supprimer le recours au bridge pour gwb2ged**
- **Objectif** : Finalisation de la migration gwb2ged
- **Acceptation** : flag par défaut sur Python ; tests verts ; doc mise à jour

#### **Issue #43 : Supprimer le recours au bridge pour ged2gwb**
- **Objectif** : Finalisation de la migration ged2gwb
- **Acceptation** : flag par défaut sur Python ; tests verts ; doc mise à jour

#### **Issue #44 : Supprimer le recours au bridge pour consang/connex**
- **Objectif** : Finalisation de la migration des services analytiques
- **Acceptation** : flag par défaut sur Python ; tests verts ; doc mise à jour

#### **Issue #45 : Supprimer le recours au bridge pour routes migrées**
- **Objectif** : Finalisation de la migration des routes web
- **Acceptation** : flag par défaut sur Python ; tests verts ; doc mise à jour

## 🏗️ **Architecture Technique**

### **Pattern Strangler Fig**
```
┌─────────────────────────────────────────────────────────────┐
│                      GENE-WEB PYTHON                        │
├─────────────────────────────────────────────────────────────┤
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│    │    CLI      │  │     API     │  │   WEB UI    │        │
│    │   (Typer)   │  │  (FastAPI)  │  │  (Future)   │        │
│    └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│    │   Python    │  │   Python    │  │   Python    │        │
│    │   Native    │  │   Native    │  │   Native    │        │
│    │   gwb2ged   │  │   ged2gwb   │  │   gwd       │        │
│    └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│    │   Bridge    │  │   Bridge    │  │   Bridge    │        │
│    │   OCaml     │  │   OCaml     │  │   OCaml     │        │
│    │   gwb2ged   │  │   ged2gwb   │  │   gwd       │        │
│    └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    GENE-WEB OCAML                           │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│    │   gwb2ged   │  │   ged2gwb   │  │     gwd     │        │
│    │   (OCaml)   │  │   (OCaml)   │  │   (OCaml)   │        │
│    └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### **Structure du Projet**
```
geneweb_python/
├── geneweb/                   # Code OCaml original
│   ├── bin/
│   ├── distribution/
│   └── ...
├── code/                      # Code Python
│   ├── src/geneweb/
│   │   ├── adapters/
│   │   │   ├── cli/           # Interface ligne de commande
│   │   │   ├── http/          # Interface web API
│   │   │   └── ocaml_bridge/  # Pont vers OCaml
│   │   ├── domain/            # Logique métier
│   │   └── infrastructure/    # Infrastructure technique
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
└── docs/
    ├── PRESENTATION_ORAL.md
    ├── PLAN_MIGRATION_COMPLET.md
    └── adr/
        └── 0001-strangler-fig.md
```

## 🔧 **Technologies Utilisées**

### **Python**
- **Typer** : CLI moderne et intuitive
- **FastAPI** : API web performante
- **Pytest** : Tests unitaires et d'intégration
- **Ruff** : Linting et formatting
- **MyPy** : Vérification de types statiques

### **OCaml**
- **Dune** : Build system
- **OPAM** : Gestionnaire de paquets
- **Binaires existants** : gwb2ged, ged2gwb, gwd

### **DevOps**
- **GitHub Actions** : CI/CD
- **Pre-commit** : Hooks de qualité
- **Docker** : Containerisation (future)

## 📊 **Métriques de Succès**

### **Phase 1 : Bridge (Terminée)**
- ✅ **Parité fonctionnelle** : gwb2ged Python = gwb2ged OCaml
- ✅ **Performance** : < 10% de différence
- ✅ **Stabilité** : 0 crash, erreurs gérées

### **Phase 2 : Implémentation Native**
- 🎯 **Performance** : ≥ 90% de la performance OCaml
- 🎯 **Mémoire** : ≤ 110% de la consommation OCaml
- 🎯 **Stabilité** : 0 régression fonctionnelle

### **Phase 3 : Production**
- 🎯 **Uptime** : 99.9%
- 🎯 **Latence** : < 100ms pour les opérations simples
- 🎯 **Throughput** : ≥ 1000 requêtes/minute

## 🚀 **Prochaines Étapes**

### **Immédiat (Semaine 1)**
1. **Issue #9** : Fixtures d'entrée GWB
2. **Issue #10** : Snapshots GEDCOM
3. **Issue #11** : Benchmarks de base

### **Court terme (Semaine 2-3)**
1. **Issue #12** : Modèles de domaine
2. **Issue #13** : Lecture GWB minimal
3. **Issue #14** : Sérialisation GEDCOM minimal

### **Moyen terme (Mois 1-2)**
1. **Issues #15-20** : Portage complet gwb2ged
2. **Issues #21-28** : Portage complet ged2gwb
3. **Issues #29-32** : Services analytiques

### **Long terme (Mois 3-6)**
1. **Issues #33-37** : Migration serveur HTTP
2. **Issues #38-41** : Observabilité et distribution
3. **Issues #42-45** : Décommission OCaml

## 📝 **Notes Importantes**

### **Risques Identifiés**
- **Performance** : Python peut être plus lent qu'OCaml
- **Mémoire** : Consommation potentiellement plus élevée
- **Compatibilité** : Risque de régression fonctionnelle

### **Mitigations**
- **Tests exhaustifs** : Parité fonctionnelle garantie
- **Profiling continu** : Monitoring des performances
- **Rollback** : Possibilité de revenir à OCaml si nécessaire

### **Dépendances**
- **OCaml** : Doit rester fonctionnel pendant la transition
- **Bases de données** : Compatibilité avec les formats existants
- **Utilisateurs** : Formation et support nécessaires

## 🎉 **Conclusion**

Ce plan de migration utilise le pattern **Strangler Fig** pour une transition progressive et sécurisée. Chaque issue est atomique et testable, garantissant la stabilité et la qualité du système final.

La documentation complète est disponible dans `docs/PRESENTATION_ORAL.md` et les décisions architecturales dans `docs/adr/0001-strangler-fig.md`.
