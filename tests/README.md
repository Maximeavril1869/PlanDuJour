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
| `test_passages.py` | Passages d'une tâche sans heure : chrono répété, créneaux et Stats, panneau (saisie, suppression, effacement), ancien temps réel converti, bloc ponctuel, sous-activités inchangées |
| `test_maintenant.py` | Ligne « maintenant » (horloge simulée) : position proportionnelle, avance seule, absente hors plage et sur un autre jour, défilement à l'ouverture sans reprise de la page, ligne dans le Récap |
| `test_export_jour.py` | Export Calendrier du jour même (heure simulée) : choix de période, heures réelles / en cours / à venir, 7 jours dès aujourd'hui ou dès demain, un événement par passage, identifiants stables, rien de coché |
| `test_raccourcis.py` | Envoi vers Raccourcis (presse-papiers et lien simulés, heure simulée) : lien et JSON, id entre crochets (unicité, non-inclusion, stabilité après changement de titre et d'heure), périodes, un événement par passage, envoi vide sans ouverture du raccourci, repli par le texte, bouton .ics conservé |
| `test_temps_restant.py` | Temps restant avant le coucher sur la ligne « maintenant » (heure simulée : 10 h 30, diminue avec l'heure, 45 min, rien si coucher libre) ; Récap rattrapé à l'ouverture de l'onglet et au retour dans l'app (`visibilitychange`) |
| `test_noms_passages.py` | Nom d'un passage : champ « Dossier » au ▶, nom dans la barre « en cours » et la frise, espaces réduits et 60 caractères, correction dans le panneau, relu au chargement, Stats par nom sous la tâche (« Sans détail »), titre Calendrier « Tâche · Nom », ids Raccourcis inchangés |
| `test_reperes.py` | Départ et retour de chez soi (0.32.0) : carte fermée au départ, boutons à l'heure du moment, lignes de la frise et du Récap (six lignes triées, présence ouverte sans ligne de départ, pause ouverte sans fin), correction à la main (heure invalide, retour avant départ, champ vidé), jour passé, `cleanTrip`, plage de la frise et libellés qui ne se chevauchent pas, rien en semaine type |
| `test_stockage.py` | Demande de stockage persistant : accordée, déjà accordée, refusée, en erreur, interface absente (système simulé) ; affichage dans Réglages |
| `test_cochables.py` | Sous-activités cochables : cases à la main, coche d'office à l'arrêt du chrono et à la saisie d'un temps, panneau du bloc, jour passé, lecture de données invalides |
| `test_calendrier.py` | Démarrage sans erreur, export vers Calendrier par case à cocher (`toCal`, codes, rappel facultatif, `.ics`), premier lancement vierge (aucune activité, rien d'enregistré, bandeau, réglages illisibles), case conservée après rechargement ; fournit aussi `seed_defaults` (anciennes valeurs d'origine en fixture) |

## Règles

- Aucune donnée réelle : libellés inventés (`Réunion test`, `Rdv app`).
- Depuis la 0.31.1 l'app démarre **vierge** : un test qui a besoin des anciens profils ou activités les enregistre avec `seed_defaults(pg)` (`tests/test_calendrier.py`).
- Les tests lisent le stockage du navigateur (`localStorage`) ; chaque test démarre avec un navigateur vierge.
- Les anciens fichiers `test_lot*.js` cités dans `STATUS.md` et `CONVENTIONS.md` ne sont pas dans le dépôt ; ces tests-ci les remplacent progressivement, un domaine à la fois.
