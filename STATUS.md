# STATUS — Plan du jour

Version actuelle : **0.1.0** (lot 1). Règles de travail : voir `CONVENTIONS.md`.

## Lots

| # | Lot | Statut | « Fini » veut dire |
|---|---|---|---|
| 1 | Saisie et stockage des contraintes | **Livré, à tester sur iPhone** | Voir ci-dessous |
| 2 | Plan du jour et recalage autour des rendez-vous | À faire | J'ajoute un rendez-vous à 9h et le bloc « 1h30 de concentration » se décale seul ; la journée s'affiche en timeline ; je saisis l'heure réelle d'arrivée et de départ du jour |
| 3 | Sous-tâches, détente et débordement | À faire | Je coche des sous-tâches et je les retrouve après fermeture de l'app ; la détente s'affiche en permanence ; quand ça déborde, l'app le dit et propose les coupes une par une |
| 4 | Export, import et finitions iPhone / iPad | À faire | Je sauvegarde et restaure mes données par fichier ; l'app est confortable sur iPhone et iPad |

### Lot 1 est fini quand, sur ton iPhone

1. L'app s'ouvre depuis l'adresse GitHub Pages et s'ajoute à l'écran d'accueil (plein écran).
2. Les valeurs de départ s'affichent en 24 h (Récapitulatif, puis Réglages).
3. Tu modifies une heure (en tapant par exemple `0653`), tu enregistres, tu fermes complètement l'app, tu la rouvres : la valeur est conservée.
4. Une heure invalide (`25h`, `12:60`) est refusée avec un message sous le champ, sans rien enregistrer.
5. Tu peux ajouter, modifier et supprimer un rendez-vous régulier, régler les jours de saxophone, la fréquence du ménage et le plancher de détente.

Vérifié côté code (navigateur automatisé, écran d'iPhone, mode sombre, hors ligne) : points 2 à 5 et fonctionnement hors ligne. Le point 1 et le comportement du clavier iPhone restent à vérifier par toi.

## Décisions prises

- Heures saisies et affichées en 24 h (`HH:MM`). Les fourchettes (arrivée 07:30–07:40, départ 16:00–16:15) sont conservées telles quelles ; l'app ne choisit aucune valeur, tu saisiras l'heure réelle chaque jour (lot 2).
- Nom du dépôt : `PlanDuJour`, public. Hébergement : GitHub Pages.
- Fichiers : `index.html` (code, style et script), `manifest.json`, `sw.js`, icônes.
- Saxophone : valeur de départ tous les jours sauf mercredi et vendredi. Ménage : tous les 3 jours, 30 min. Tout se règle dans l'app.
- Rendez-vous réguliers : liste libre (nom, jour, heure, durée facultative), pas seulement cours et orchestre.

## À valider

- Plancher de détente : 30 min par défaut, ou autre valeur.
- Ordre de coupe en cas de débordement : ménage, puis temps d'app, puis détente (lot 3).
- Contenu du champ « dossier » : libellé court ou autre chose (lot 3).
- Durée du ménage : 30 min par défaut, valeur inventée pour démarrer.
- Durée du cours de saxophone et de l'orchestre : non renseignées, nécessaires au lot 2.

## À revoir plus tard

- « Temps d'app » (dans l'ordre de coupe) n'est pas encore défini : qu'est-ce que c'est exactement ?
- Les deux champs de fourchette sont limités à des heures du même jour ; pas de coucher après minuit.
- Week-end : non planifié en version 1 (les jours de saxophone peuvent déjà inclure sam. et dim.).
- Rappels et alarmes : export `.ics` à étudier.
