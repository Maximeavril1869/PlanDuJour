# STATUS — Plan du jour

Version actuelle : **0.3.0** (lots 1, 2 et refonte du modèle d'activités). Règles de travail : voir `CONVENTIONS.md`.

## Lots

| # | Lot | Statut | « Fini » veut dire |
|---|---|---|---|
| 1 | Saisie et stockage des contraintes | **Livré, à tester sur iPhone** | Voir ci-dessous |
| 2 | Plan du jour et recalage autour des rendez-vous | **Livré, à tester sur iPhone** | J'ajoute un rendez-vous à 9h et le bloc « 1h30 de concentration » se décale seul ; la journée s'affiche en timeline ; je saisis l'heure réelle d'arrivée et de départ du jour |
| 3 | Sous-tâches, détente et débordement | À faire | Je coche des sous-tâches et je les retrouve après fermeture de l'app ; la détente s'affiche en permanence ; quand ça déborde, l'app le dit et propose les coupes une par une |
| 4 | Export, import et finitions iPhone / iPad | À faire | Je sauvegarde et restaure mes données par fichier ; l'app est confortable sur iPhone et iPad |

### Lot 2 est fini quand, sur ton iPhone

1. Dans **Réglages**, chaque activité (trajets, cours, saxophone, ménage, concentration…) se règle avec les mêmes champs : nom, jours, comportement (fixe, prévue, sans heure), début + fin ou début + durée. Le bouton « + » en ajoute une.
2. L'onglet **Jour** montre la journée en timeline avec le **temps disponible** entre deux blocs. L'onglet **Récapitulatif** montre la même chose pour chaque jour de la semaine type.
3. « + Bloc ponctuel » ajoute un rendez-vous pour ce jour seulement (fixe, prévu ou sans heure).
4. Le **chrono** (▶ Démarrer, ■ Arrêter) existe sur tous les blocs. Il enregistre l'heure réelle.
5. Si le trajet retour dure plus longtemps que prévu (arrêt du chrono à 17:50 au lieu de 17:15), le saxophone et le ménage glissent à la suite. Un bloc « sans heure » (concentration) se lance quand tu veux et pousse la suite.
6. Tout est conservé après fermeture de l'app.

Vérifié côté code (navigateur automatisé, écran d'iPhone, iPad, mode sombre, hors ligne) : tous les points, ainsi que les migrations depuis les versions précédentes.

### Lot 1 est fini quand, sur ton iPhone

1. L'app s'ouvre depuis l'adresse GitHub Pages et s'ajoute à l'écran d'accueil (plein écran).
2. Les valeurs de départ s'affichent en 24 h (Récapitulatif, puis Réglages).
3. Tu modifies une heure (en tapant par exemple `0653`), tu enregistres, tu fermes complètement l'app, tu la rouvres : la valeur est conservée.
4. Une heure invalide (`25h`, `12:60`) est refusée avec un message sous le champ, sans rien enregistrer.
5. Tu peux ajouter, modifier et supprimer un rendez-vous régulier, régler les jours de saxophone, la fréquence du ménage et le plancher de détente.

Vérifié côté code (navigateur automatisé, écran d'iPhone, mode sombre, hors ligne) : points 2 à 5 et fonctionnement hors ligne. Le point 1 et le comportement du clavier iPhone restent à vérifier par toi.

## Décisions prises

- Heures saisies et affichées en 24 h (`HH:MM`). Plus de fourchettes : l'arrivée et le départ du travail sont les heures réelles du trajet aller (fin) et du trajet retour (début), saisies à la main ou avec le chrono.
- Nom du dépôt : `PlanDuJour`, public. Hébergement : GitHub Pages.
- Fichiers : `index.html` (code, style et script), `manifest.json`, `sw.js`, icônes.
- **Un seul modèle d'activité** (voir CONVENTIONS §13) : plus d'éditeurs séparés pour le saxophone, le ménage ou les rendez-vous réguliers. Le mensuel et le « tous les N jours » sont abandonnés.
- Valeurs de départ : trajet aller 06:30–07:30, trajet retour 16:00–17:15 (lun.–ven., heure fixe) ; cours de saxophone mercredi 19:00 et orchestre vendredi 19:30 (1 h supposée, heure fixe) ; saxophone 15 min à 17:15 (souple, tous les jours sauf mercredi et vendredi) ; ménage 30 min à 17:30 (souple, lundi et jeudi) ; concentration 1 h 30 sans heure (lun.–ven.). Tout se modifie.
- Le week-end est géré comme les autres jours (les activités choisissent leurs jours).
- Un bloc « sans heure » n'a pas de place dans la timeline tant qu'il n'est pas lancé ; il est listé avec le plus grand temps disponible. Le chrono est un chrono qui monte, avec la durée prévue en repère.
- Un seul bloc tourne à la fois : en démarrer un arrête le précédent.

## À valider

- Plancher de détente : 30 min par défaut, ou autre valeur.
- Ordre de coupe en cas de débordement : ménage, puis temps d'app, puis détente (lot 3).
- Contenu du champ « dossier » : libellé court ou autre chose (lot 3).
- Durée du ménage : 30 min par défaut, valeur inventée pour démarrer.
- Durée du cours de saxophone et de l'orchestre : non renseignées, 1 h supposée en attendant (modifiable dans Réglages).
- Jours et heure du ménage : lundi et jeudi à 17:30 par défaut, valeurs inventées pour démarrer.

## À revoir plus tard

- « Temps d'app » (dans l'ordre de coupe) n'est pas encore défini : qu'est-ce que c'est exactement ?
- Les deux champs de fourchette sont limités à des heures du même jour ; pas de coucher après minuit.
- Week-end : non planifié en version 1 (les jours de saxophone peuvent déjà inclure sam. et dim.).
- Un bloc n'est jamais coupé en deux.
- Pas de glisser-déposer.
- Statistiques : les heures réelles sont déjà conservées (400 jours) ; l'écran de statistiques reste à définir.
- Le chrono tourne à la minute ; le bloc « en cours » se rafraîchit toutes les 15 secondes.
- Rappels et alarmes : export `.ics` à étudier.
