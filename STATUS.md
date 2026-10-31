# STATUS — Plan du jour

Version actuelle : **0.5.0** (lots 1 à 3 et option « à reporter »). Règles de travail : voir `CONVENTIONS.md`.

## Lots

| # | Lot | Statut | « Fini » veut dire |
|---|---|---|---|
| 1 | Saisie et stockage des contraintes | **Livré, à tester sur iPhone** | Voir ci-dessous |
| 2 | Plan du jour et recalage autour des rendez-vous | **Livré, à tester sur iPhone** | J'ajoute un rendez-vous à 9h et le bloc « 1h30 de concentration » se décale seul ; la journée s'affiche en timeline ; je saisis l'heure réelle d'arrivée et de départ du jour |
| 3 | Sous-tâches, détente et blocs à confirmer | **Livré, à tester sur iPhone** | Je coche des sous-tâches et je les retrouve après fermeture de l'app ; la détente s'affiche en permanence ; les blocs « à confirmer » se confirment en un tap ; quand ça déborde, l'app le dit sans rien supprimer |
| 3 bis | Reporter ce qui n'a pas été fait | **Livré, à tester sur iPhone** | Dans le train, j'ouvre « Revue du jour » et je reporte au lendemain (ou à un autre jour) ce que je n'ai pas fait, avec ses sous-tâches non cochées ; je peux annuler |
| 4 | Export, import, statistiques et finitions iPhone / iPad | À faire | Je sauvegarde et restaure mes données par fichier ; l'app est confortable sur iPhone et iPad |

### Lot 3 bis (« à reporter ») est fini quand, sur ton iPhone

1. Dans **Réglages**, chaque activité a une case « À reporter » (cochée par défaut pour le saxophone, le ménage et la concentration). La même case existe dans un bloc ponctuel.
2. Sur la page **Jour** (aujourd'hui ou un jour passé), la carte **Revue du jour** liste ce qui est « à reporter » et n'est pas fait, ou fait avec des sous-tâches non cochées. Elle est repliée pour aujourd'hui (tu l'ouvres dans le train) et ouverte d'office pour un jour passé.
3. Pour chaque ligne : **→ Demain** (ou **→ Jour suivant** sur un jour passé), **Autre jour…** (choix d'une date) ou **Abandonner**.
4. Un bloc non fait part vers le jour choisi comme bloc « sans heure » de même durée, avec ses sous-tâches non cochées, et la mention « reporté de lun 02/11 ». Il quitte le plan du jour d'origine. Un bloc fait garde sa place : seules ses sous-tâches non cochées partent (sur la même activité si elle est prévue ce jour-là).
5. Un bloc **Raté** a aussi un bouton **Reporter…**. La liste « Déjà traités » permet d'**Annuler** un report ou un abandon (la copie disparaît du jour cible).
6. Tout est conservé après fermeture de l'app.

Vérifié côté code (navigateur automatisé, écran d'iPhone, mode sombre) : tous les points, et les tests des lots 1 à 3 passent toujours.

### Lot 3 est fini quand, sur ton iPhone

1. Dans **Réglages**, chaque activité a une case « À confirmer » (cochée par défaut pour le saxophone et le ménage). Elle est masquée pour une activité « sans heure ».
2. Après l'heure de fin d'un bloc à confirmer, la carte **À confirmer** apparaît en haut du jour avec **Fait** et **Raté**. « Fait » enregistre les heures prévues ; « Raté » retire le bloc du plan et libère son temps (liste « Ratés », avec « Rétablir »). Pour un jour passé, tous les blocs à confirmer non pointés sont proposés.
3. Sous un bloc (tape dessus, ou « Détails » pour un bloc sans heure), la section **Sous-tâches** accepte autant de lignes que nécessaire : libellé + action courte, case à cocher, suppression. La progression (par exemple 3/8) s'affiche sur le bloc et dans la liste « Sans heure ».
4. Tout est conservé après fermeture de l'app.
5. L'encart **Détente avant le coucher** est affiché en permanence en haut du jour ; il passe en alerte sous le minimum réglé.

Vérifié côté code (navigateur automatisé, écran d'iPhone, mode sombre) : tous les points, et les tests des lots 1 et 2 passent toujours.

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
- Durée du ménage : 30 min par défaut, valeur inventée pour démarrer.
- Durée du cours de saxophone et de l'orchestre : non renseignées, 1 h supposée en attendant (modifiable dans Réglages).
- Jours et heure du ménage : lundi et jeudi à 17:30 par défaut, valeurs inventées pour démarrer.
- Sous-tâches : propres à chaque jour (pas de liste récurrente) ; à confirmer à l'usage.
- Report : un bloc non fait revient en bloc « sans heure » sur le jour cible (pas de nouvelle heure) ; à confirmer à l'usage. Les réglages déjà enregistrés avant la 0.5.0 reçoivent « à reporter » coché pour saxophone, ménage et concentration.

## À revoir plus tard

- Les propositions de coupe automatiques (ménage, « temps d'app », détente) du cahier initial sont abandonnées : l'app signale le débordement sans rien proposer. À reprendre si le besoin revient.
- Catégories pour les statistiques : pas créées ; regroupement par nom d'activité en attendant.
- Les deux champs de fourchette sont limités à des heures du même jour ; pas de coucher après minuit.
- Week-end : non planifié en version 1 (les jours de saxophone peuvent déjà inclure sam. et dim.).
- Un bloc n'est jamais coupé en deux.
- Pas de glisser-déposer.
- Statistiques : les heures réelles, les confirmations et les « ratés » sont déjà conservés (400 jours) ; l'écran de statistiques reste à définir (lot 4 ?).
- Le chrono tourne à la minute ; le bloc « en cours » se rafraîchit toutes les 15 secondes.
- Report : pas de « prochain jour prévu » automatique pour une activité récurrente (demain par défaut, ou une date choisie) ; pas de report en chaîne annulable de bout en bout.
- Statistiques : compter les reports et abandons (conservés dans les données du jour) par semaine et par mois, avec le lot 4.
- Rappels et alarmes : export `.ics` à étudier.
