# Tests

Vérifications automatiques de l'app : un navigateur (Chromium) est piloté par un script, ouvre `index.html` et contrôle le comportement. Ils ne servent pas à utiliser l'app, seulement à vérifier qu'une modification n'a rien cassé.

## Lancer

Depuis la racine du dépôt (Python 3 requis) :

```
pip install playwright
playwright install chromium
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_calendrier.py
```

Le script affiche `OK` ou `ECHEC` pour chaque vérification et se termine par le nombre d'échecs. `PYTHONDONTWRITEBYTECODE=1` évite de modifier les fichiers `.pyc` que git suit dans `tests/__pycache__/`.

## Contenu

| Fichier | Vérifie |
|---|---|
| `test_reinitialisation.py` | Réinitialisation : confirmation par mot, réglages vierges, effacement des jours et des copies, rechargement, ajout d'un bloc dans l'app vierge |
| `test_pliage.py` | Cartes repliables fermées au départ (Réglages, page du jour : Présence, Sans heure, Revue du jour), dépliage au tap et conservation de l'état |
| `test_regroupements.py` | Catégories en menus repliables fermés au départ : « Sans heure » (ordre, compteur, tri, état conservé) et Réglages (Activités, Tâches habituelles : ajout, suppression, ouverture sur erreur de saisie) |
| `test_arborescence.py` | Catégories en arbre : chemin dans les listes et « Sans heure », choix du parent, suppression qui remonte les enfants, profondeur 8, réparation des boucles et parents inexistants |
| `test_statuts.py` | Statuts Travail / Perso / Hors : lecture et héritage, trois menus et arbre imbriqué dans Réglages, changement de statut, rangement sous un autre parent, ajout et suppression, anciens réglages |
| `test_stats_arbre.py` | Stats en arbre : totaux par statut et par catégorie, activités et sous-activités, « Sans catégorie » en Hors, catégorie supprimée, période sans temps, absence de double compte, pliage conservé |
| `test_sauvegarde.py` | Rappel de sauvegarde : bandeau présent sur les quatre onglets, quand il apparaît (délai, report, état illisible), « Exporter maintenant » (téléchargement, feuille de partage acceptée ou annulée), ce qui compte comme une modification, réglage du délai, import et réinitialisation |
| `test_cochables.py` | Sous-activités cochables : cases à la main, coche d'office à l'arrêt du chrono et à la saisie d'un temps, panneau du bloc, jour passé, lecture de données invalides |
| `test_calendrier.py` | Démarrage sans erreur, export vers Calendrier par case à cocher (`toCal`, codes, rappel facultatif, `.ics`), valeurs par défaut, case conservée après rechargement |

## Règles

- Aucune donnée réelle : libellés inventés (`Réunion test`, `Rdv app`).
- Les tests lisent le stockage du navigateur (`localStorage`) ; chaque test démarre avec un navigateur vierge.
- Les anciens fichiers `test_lot*.js` cités dans `STATUS.md` et `CONVENTIONS.md` ne sont pas dans le dépôt ; ces tests-ci les remplacent progressivement, un domaine à la fois.
