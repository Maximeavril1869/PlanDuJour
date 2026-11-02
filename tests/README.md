# Tests

Vérifications automatiques de l'app : un navigateur (Chromium) est piloté par un script, ouvre `index.html` et contrôle le comportement. Ils ne servent pas à utiliser l'app, seulement à vérifier qu'une modification n'a rien cassé.

## Lancer

Depuis la racine du dépôt (Python 3 requis) :

```
pip install playwright
playwright install chromium
python3 tests/test_calendrier (export).py
```

Le script affiche `OK` ou `ECHEC` pour chaque vérification et se termine par le nombre d'échecs.

## Contenu

| Fichier | Vérifie |
|---|---|
| `test_reinitialisation.py` | Réinitialisation : confirmation par mot, réglages vierges, effacement des jours et des copies, rechargement, ajout d'un bloc dans l'app vierge |
| `test_pliage.py` | Cartes repliables fermées au départ (Réglages, page du jour : Présence, Sans heure, Revue du jour), dépliage au tap et conservation de l'état |
| `test_calendrier (export).py` | Démarrage sans erreur, export vers Calendrier (codes, exclusions), lecture des lignes et des `.ics`, import (mise à jour par code, par date de création, doublons, calendrier (export) dédié), conservation du lien dans l'éditeur |

## Règles

- Aucune donnée réelle : libellés inventés (`Réunion test`, `Rdv app`).
- Les tests lisent le stockage du navigateur (`localStorage`) ; chaque test démarre avec un navigateur vierge.
- Les anciens fichiers `test_lot*.js` cités dans `STATUS.md` et `CONVENTIONS.md` ne sont pas dans le dépôt ; ces tests-ci les remplacent progressivement, un domaine à la fois.
