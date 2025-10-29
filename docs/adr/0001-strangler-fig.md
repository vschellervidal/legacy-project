# ADR 0001 — Strangler Fig pour migration OCaml → Python

Statut: accepté
Date: 2025-09-15

## Contexte
Le projet GeneWeb est historiquement en OCaml. Nous introduisons une refonte Python sans interrompre l'existant.

## Décision
Adopter le pattern « Strangler Fig »:
- Conserver l'OCaml comme oracle de référence.
- Ajouter un bridge Python→OCaml (subprocess/RPC) pour caractériser le comportement.
- Remplacer progressivement par des implémentations Python, domaine par domaine.
- Mettre des flags de bascule (CLI/API) et des tests de parité.

## Conséquences
- Réduction des risques de régression.
- Possibilité de livrer par incréments.
- Nécessité de maintenir deux piles pendant la transition.

## Alternatives étudiées
- Réécriture Big-Bang: risquée et longue sans livrables intermédiaires.
- Traduction automatique: non réaliste pour le métier et la perf.

# ADR 0001 — Strangler Fig pour migration OCaml → Python

Statut: accepté
Date: 2025-09-15

## Contexte
Le projet GeneWeb est historiquement en OCaml. Nous introduisons une refonte Python sans interrompre l'existant.

## Décision
Adopter le pattern « Strangler Fig »:
- Conserver l'OCaml comme oracle de référence.
- Ajouter un bridge Python→OCaml (subprocess/RPC) pour caractériser le comportement.
- Remplacer progressivement par des implémentations Python, domaine par domaine.
- Mettre des flags de bascule (CLI/API) et des tests de parité.

## Conséquences
- Réduction des risques de régression.
- Possibilité de livrer par incréments.
- Nécessité de maintenir deux piles pendant la transition.

## Alternatives étudiées
- Réécriture Big-Bang: risquée et longue sans livrables intermédiaires.
- Traduction automatique: non réaliste pour le métier et la perf.
