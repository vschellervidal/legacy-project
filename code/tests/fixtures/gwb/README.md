# Fixtures GWB (GeneWeb Base)

Ce dossier contient des bases GWB miniatures pour les tests.

- small/: très petites bases (quelques individus/familles)
- medium/: bases de taille moyenne (extraits de la démo)
- edge/: cas tordus (encodages, champs manquants, structures minimales)

Provenance:
- Dérivées de la démo fournie par GeneWeb (distribution/bases/demo) et/ou reconstruites artificiellement.
- Pas de données réelles sensibles.

Règles:
- Versionner uniquement des bases minimales nécessaires aux tests.
- Documenter ici tout script ou processus de génération.

Génération locale (exemple):
- Copier la base de démo complète (non versionnée) pour référence:
  - cp -R ../../../../geneweb/distribution/bases/demo ./medium/demo_full  # ignorer dans git
- Créer une mini-base small/demo_min en ne gardant que les fichiers obligatoires (base, index minimaux) puis vérifier l’export gwb2ged.
