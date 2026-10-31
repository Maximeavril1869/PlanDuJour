# STATUS — Plan du jour

Version actuelle : **0.2.0** (lots 1 et 2). Règles de travail : voir `CONVENTIONS.md`.

## Lots

| # | Lot | Statut | « Fini » veut dire |
|---|---|---|---|
| 1 | Saisie et stockage des contraintes | **Livré, à tester sur iPhone** | Voir ci-dessous |
| 2 | Plan du jour et recalage autour des rendez-vous | **Livré, à tester sur iPhone** | J'ajoute un rendez-vous à 9h et le bloc « 1h30 de concentration » se décale seul ; la journée s'affiche en timeline ; je saisis l'heure réelle d'arrivée et de départ du jour |
| 3 | Sous-tâches, détente et débordement | À faire | Je coche des sous-tâches et je les retrouve après fermeture de l'app ; la détente s'affiche en permanence ; quand ça déborde, l'app le dit et propose les coupes une par une |
| 4 | Export, import et finitions iPhone / iPad | À faire | Je sauvegarde et restaure mes données par fichier ; l'app est confortable sur iPhone et iPad |

### Lot 2 est fini quand, sur ton iPhone

1. L'onglet **Jour** montre ta journée de semaine en timeline : trajets, rendez-vous réguliers, blocs mobiles (concentration, saxophone, ménage).
2. Tu ajoutes un rendez-vous à 9h (bouton « + Rendez-vous ») : le bloc « Concentration » 1 h 30 se décale seul, sans autre action.
3. Tu saisis l'heure réelle d'arrivée (ex. 07:30) : la concentration revient avant le rendez-vous si elle tient.
4. Tu coches le ménage (tape sur le bloc), tu fermes l'app, tu la rouvres : la case est conservée.
5. Un rendez-vous qui prend toute la journée fait apparaître « Ne tient pas dans la journée », sans rien supprimer.

Vérifié côté code (navigateur automatisé, écran d'iPhone, iPad, mode sombre) : points 1 à 5, ainsi que la migration des réglages de la version 1 vers la 2.

### Lot 1 est fini quand, sur ton iPhone

1. L'app s'ouvre depuis l'adresse GitHub Pages et s'ajoute à l'écran d'accueil (plein écran).
2. Les valeurs de départ s'affichent en 24 h (Récapitulatif, puis Réglages).
3. Tu modifies une heure (en tapant par exemple `0653`), tu enregistres, tu fermes complètement l'app, tu la rouvres : la valeur est conservée.
4. Une heure invalide (`25h`, `12:60`) est refusée avec un message sous le champ, sans rien enregistrer.
5. Tu peux ajouter, modifier et supprimer un rendez-vous régulier, régler les jours de saxophone, la fréquence du ménage et le plancher de détente.

Vérifié côté code (navigateur automatisé, écran d'iPhone, mode sombre, hors ligne) : points 2 à 5 et fonctionnement hors ligne. Le point 1 et le comportement du clavier iPhone restent à vérifier par toi.

## Décisions prises

- Heures saisies et affichées en 24 h (`HH:MM`). Les fourchettes (arrivée 07:30–07:40, départ 16:00–16:15) sont conservées telles quelles ; l'app ne choisit aucune valeur, tu saisis l'heure réelle chaque jour (lot 2).
- Nom du dépôt : `PlanDuJour`, public. Hébergement : GitHub Pages.
- Fichiers : `index.html` (code, style et script), `manifest.json`, `sw.js`, icônes.
- Saxophone : valeur de départ tous les jours sauf mercredi et vendredi. Ménage : tous les 3 jours, 30 min. Tout se règle dans l'app.
- Lot 2 : le plan ne gère que les jours de semaine ; le week-end affiche « non géré » et l'app ouvre sur le prochain jour de semaine.
- Lot 2 : blocs mobiles personnalisables (nom, durée, zone matin / travail / soir, priorité). « Concentration » 1 h 30, zone travail, priorité 1, par défaut. Saxophone (priorité 2) et ménage (priorité 3) sont toujours le soir.
- Lot 2 : sans heure réelle saisie, le plan utilise le cas prudent de la fourchette et l'indique à l'écran.
- Lot 2 : le trajet aller va du départ de chez toi à l'arrivée au travail ; le trajet retour du départ du travail au retour à la maison.
- Lot 2 : un rendez-vous régulier sans durée renseignée est supposé durer 1 h, et l'écran le signale.
- Rendez-vous réguliers : liste libre (nom, jour, heure, durée facultative), pas seulement cours et orchestre.

## À valider

- Plancher de détente : 30 min par défaut, ou autre valeur.
- Ordre de coupe en cas de débordement : ménage, puis temps d'app, puis détente (lot 3).
- Contenu du champ « dossier » : libellé court ou autre chose (lot 3).
- Durée du ménage : 30 min par défaut, valeur inventée pour démarrer.
- Durée du cours de saxophone et de l'orchestre : non renseignées, 1 h supposée en attendant.
- Zones des blocs mobiles : la concentration est-elle bien uniquement pendant la journée de travail ?
- Cas prudent sans heure réelle (arrivée tardive, départ précoce) : ce choix te convient-il ?

## À revoir plus tard

- « Temps d'app » (dans l'ordre de coupe) n'est pas encore défini : qu'est-ce que c'est exactement ?
- Les deux champs de fourchette sont limités à des heures du même jour ; pas de coucher après minuit.
- Week-end : non planifié en version 1 (les jours de saxophone peuvent déjà inclure sam. et dim.).
- Un bloc mobile n'est pas coupé en deux (la concentration de 1 h 30 doit tenir d'un seul tenant).
- Pas de glisser-déposer ni de déplacement manuel d'un bloc mobile.
- Rappels et alarmes : export `.ics` à étudier.
