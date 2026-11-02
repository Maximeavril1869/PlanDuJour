# STATUS — Plan du jour

Version actuelle : **0.17.1** (lots 1 à 4, profils de journée à heures libres et congé) (lots 1 à 3, option « à reporter » et profils de journée). Règles de travail : voir `CONVENTIONS.md`.

## Lots

| # | Lot | Statut | « Fini » veut dire |
|---|---|---|---|
| 1 | Saisie et stockage des contraintes | **Livré, à tester sur iPhone** | Voir ci-dessous |
| 2 | Plan du jour et recalage autour des rendez-vous | **Livré, à tester sur iPhone** | J'ajoute un rendez-vous à 9h et le bloc « 1h30 de concentration » se décale seul ; la journée s'affiche en timeline ; je saisis l'heure réelle d'arrivée et de départ du jour |
| 3 | Sous-tâches, détente et blocs à confirmer | **Livré, à tester sur iPhone** | Je coche des sous-tâches et je les retrouve après fermeture de l'app ; la détente s'affiche en permanence ; les blocs « à confirmer » se confirment en un tap ; quand ça déborde, l'app le dit sans rien supprimer |
| 3 bis | Reporter ce qui n'a pas été fait | **Livré, à tester sur iPhone** | Dans le train, j'ouvre « Revue du jour » et je reporte au lendemain (ou à un autre jour) ce que je n'ai pas fait, avec ses sous-tâches non cochées ; je peux annuler |
| 3 ter | Profils de journée (semaine, week-end, télétravail) | **Livré, à tester sur iPhone** | Le week-end a son lever et son coucher ; un jour de télétravail se choisit sur la page du jour, sans trajets |
| 4 | Export, import, statistiques et finitions iPhone / iPad | **Livré, à tester sur iPhone et iPad** | Je sauvegarde et restaure mes données par fichier ; je vois le temps réel par activité, par semaine et par mois ; l'app est confortable sur iPhone et iPad |

### Lot 4 bis (heures libres et congé) est fini quand, sur ton iPhone

1. Dans **Réglages**, le lever et le coucher d'un profil peuvent être **vides = libres**. Lever libre : rien n'est compté avant le premier bloc. Coucher libre : plus de temps disponible avant le coucher, plus d'encart Détente, plus d'alerte « après le coucher ».
2. Profils de départ : **Semaine** (lun.–jeu., 05:45–22:00), **Vendredi** (05:45, coucher libre), **Samedi** (libres), **Dimanche** (lever libre, coucher 22:00), **Télétravail** (choisi à la main, 06:45–22:00, sans trajets), **Congé** (libres, sans trajets).
3. Un profil peut avoir une **période** (« Du … Au … ») : il s'applique alors tout seul chaque jour de la période et passe avant les jours de la semaine. Deux heures facultatives l'accompagnent : **lever du dernier jour de travail avant** la période (dernier lundi–vendredi avant le début) et **coucher la veille de la reprise** (veille du premier lundi–vendredi après la fin ; le dimanche si le congé finit un vendredi). Un choix manuel du profil sur la page du jour passe avant ces ajustements.
4. Sur la page du jour, le sélecteur ne liste plus deux fois le profil habituel ; une note indique quand le lever ou le coucher a été ajusté pour un congé.
5. Les trajets sont retirés pendant un congé ; les autres activités restent (à retirer dans le profil si tu pars).

Vérifié côté code (navigateur automatisé) : tous les points, les calendriers de congé (début un lundi, fin un vendredi ou un dimanche), les anciens réglages à profils sans période, et les tests des lots précédents.

### Lot 4 est fini quand, sur ton iPhone et ton iPad

1. **Réglages → Sauvegarde → Exporter mes données** produit un fichier `plandujour-AAAA-MM-JJ.json` (réglages, profils, activités et tous les jours). Sur iPhone et iPad, la feuille de partage s'ouvre : « Enregistrer dans Fichiers » (iCloud Drive). L'export est refusé tant que des modifications de Réglages ne sont pas enregistrées.
2. **Importer un fichier…** lit le fichier, affiche un résumé (activités, profils, jours) et propose : **Tout remplacer sur cet appareil**, **Remplacer les réglages seulement (garder mes jours)** ou **Annuler**. Un fichier qui n'est pas un export de l'app est refusé sans rien modifier. Une copie de sécurité de l'état précédent est gardée dans l'appareil.
3. Usage prévu : tu configures sur l'iPhone, tu exportes, tu importes sur l'iPad avec « Réglages seulement » pour ne pas écraser le suivi de l'iPad.
4. L'onglet **Stats** affiche, pour une semaine (lun.–dim.) ou un mois, le temps réel passé par activité (fin réelle − début réel), avec des barres et le total. Flèches pour changer de période, « Aujourd'hui » pour revenir. Les blocs ratés, ou démarrés et pas arrêtés, ne comptent pas. Regroupement par nom d'activité.
5. Mise en page vérifiée sur un écran d'iPad (820 px) : aucun défilement horizontal sur les quatre onglets.

Vérifié côté code (navigateur automatisé, écrans iPhone et iPad) : tous les points, et les tests des lots 1 à 3 ter. Le partage vers Fichiers et le clavier se jugent sur l'appareil.

### Lot 3 ter (profils de journée) est fini quand, sur ton iPhone

1. Dans **Réglages**, la carte « Profils de journée » liste des profils : nom, lever, coucher, jours habituels, activités retirées. Le « + » en ajoute un. Valeurs de départ : Semaine (lun.–ven., 05:45–22:00), Week-end (sam.–dim., 07:30–22:30), Télétravail (sans jour, 06:45–22:00, retire les deux trajets). Les heures du week-end et du télétravail sont inventées : à régler.
2. Sur la page **Jour**, le sélecteur « Profil de la journée » propose « Habituel (…) » (selon le jour de la semaine) ou n'importe quel profil. Le choix ne vaut que pour ce jour.
3. Le lever, le coucher, le temps disponible, la détente et l'alerte « après le coucher » suivent le profil du jour. Les activités retirées par le profil disparaissent de ce jour.
4. Le **Récapitulatif** indique le profil habituel de chaque jour de la semaine.
5. Dans **Réglages**, les cartes « Profils de journée » et « Activités » se replient d'un tap ; chaque profil et chaque activité est une ligne repliée (nom, horaires, jours) qui se déplie d'un tap. Le résumé suit ce que tu tapes. Une erreur de saisie déplie la ligne concernée. La détente minimale a sa propre carte.
6. Supprimer un profil renvoie les jours qui l'utilisaient à leur profil habituel. Tout est conservé après fermeture de l'app. Le pliage lui-même n'est pas mémorisé après fermeture : au rouvrir, tout est replié.

Vérifié côté code (navigateur automatisé) : tous les points, la reprise des anciens réglages (lever et coucher repris dans les trois profils), et les tests des lots 1 à 3 bis.

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

- Congé : « dernier jour de travail » = dernier jour du lundi au vendredi avant le début de la période ; « reprise » = premier lundi–vendredi après la fin. Les jours fériés ne sont pas connus de l'app.
- Dernier lever et coucher de reprise du profil Congé : 05:45 et 22:00 pour démarrer (à régler).
- Lever du télétravail (06:45) et coucher du dimanche (22:00) : valeurs de départ à régler.
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
- Le chrono tourne à la minute ; le bloc « en cours » se rafraîchit toutes les 15 secondes.
- Report : pas de « prochain jour prévu » automatique pour une activité récurrente (demain par défaut, ou une date choisie) ; pas de report en chaîne annulable de bout en bout.
- Statistiques : seul le temps réel par activité est affiché. Temps prévu, nombre de faits / ratés / reportés / abandonnés et détente moyenne sont conservés dans les données mais non affichés (non souhaités pour l'instant).
- Import : pas de fusion de deux appareils (remplacement seulement).
- Profils : un seul congé à la fois n'est pas imposé ; si deux périodes se chevauchent, la première de la liste gagne. Si un jour appartient à deux profils, le premier de la liste gagne (pas d'alerte). Pas de profil par date récurrente (ex. télétravail tous les 15 jours).
- Rappels et alarmes : export `.ics` à étudier.


## Lot 5 : sous-activités chronométrées (0.13.1) — livré, à valider sur appareil
Fini quand : sous-activités créées en Réglages, chrono par sous-activité dans le bloc, temps à la main sur un autre jour, Stats avec détail. Test : test_lot10.js.

## Lot 5 bis : chrono sur les sous-tâches du jour — à faire


## Lot 6 : catégories et suivi du temps de travail (0.13.1) — livré, à valider sur appareil
Fini quand : catégories créées en Réglages et affectées aux activités et blocs, barre « Travail du jour » vs 7 h 42, Stats semaine et mois avec écart, week-ends travaillés visibles. Test : test_lot11.js.
À valider : catégories de départ (Trajets non comptés comme travail), cible 7 h 42 du lundi au vendredi, travail du soir (pas de repère d'heure pour l'instant : visible par le total du jour).


## Lot 7 : calendrier (0.13.1) — livré, à valider sur appareil
Fini quand : export .ics ajouté à Calendrier depuis la feuille de partage ; raccourci iOS « Plan du jour RDV » configuré ; import des RDV par le presse-papiers. Test : test_lot14.js.
À valider : l'option « Calendrier » dans la feuille de partage de l'iPhone ; le raccourci (à créer par l'utilisateur).

## Lot 8 : présence au travail (0.14.0) — livré, à valider sur appareil
Carte « Présence au travail » dans l'onglet Jour : boutons « Je suis arrivé », « Pause », « Reprise », « Je pars », saisie manuelle de l'arrivée, du départ et des pauses, heure de départ conseillée (pour atteindre 7 h 42). La présence est un chrono à part, en parallèle des activités. À valider : le calcul (présence + travail hors présence, sans double comptage) et la pause.

## Lot 9 : tâches habituelles (0.15.0) — livré, à valider sur appareil
Réglages > « Tâches habituelles » : modèles (nom, catégorie, heure, durée, à reporter, parallèle, ne pas exporter, rappel). Menu « Modèle » en haut du formulaire de création d'un bloc ponctuel : choisir un modèle préremplit les champs, tout reste modifiable. Les blocs ponctuels ont désormais aussi « en parallèle » et « ne pas exporter ».

## 0.15.1 — recherche d'une tâche et « à confirmer » dans les modèles — livré, à valider sur appareil
Champ « Rechercher une tâche » en haut de l'onglet Jour : liste toutes les occurrences (jours enregistrés passés, aujourd'hui et 60 jours à venir) avec heure et état (fait, raté, reporté, prévu, non fait) ; « Ouvrir » affiche le jour. Les modèles de tâches ont maintenant l'option « à confirmer ».

## 0.15.2 — correctif : activité sans heure à sous-activités — livré, à valider sur appareil
Une fois une sous-activité terminée, l'activité passait en « faite » et sa liste de sous-activités disparaissait de l'onglet Jour (les temps restaient enregistrés). Elle reste maintenant dans la carte « Sans heure », avec le temps déjà fait, pour enchaîner la suivante.

## 0.15.3 — tâches habituelles repliables et triées — livré, à valider sur appareil
Chaque tâche habituelle est repliée au départ (nom, catégorie et durée dans le résumé) ; la liste est triée par catégorie (ordre des catégories, « sans catégorie » en dernier) puis par nom, avec un titre par catégorie. Le tri s'applique à l'ouverture et à l'enregistrement, pas pendant la saisie.

## 0.15.4 — tri des catégories et des activités dans Réglages — livré, à valider sur appareil
Catégories triées de A à Z. Activités groupées par catégorie (un titre par catégorie, « Sans catégorie » en dernier) puis triées par nom. Comme pour les tâches habituelles, le tri se fait à l'ouverture et à l'enregistrement, pas pendant la saisie.

## 0.15.5 — un bloc par sous-activité dans la frise — livré, à valider sur appareil
Une activité à sous-activités n'est plus affichée comme une seule plage du premier au dernier chrono : chaque temps chronométré a son propre créneau (« Concentration · Dossier A »). Les alertes de chevauchement et le temps disponible se calculent sur ces créneaux, donc plus de fausse alerte quand une autre tâche a eu lieu entre deux sous-activités.

## 0.16.0 — Récap par sous-tâche, présence et blocs fixes dans les Stats — livré, à valider sur appareil
Récap : un créneau par temps chronométré (« Concentration · Dossier A »), et les noms des sous-tâches sous l'activité (semaine type, activités sans heure). Stats : un bloc à heure fixe passé, sans « à confirmer », ni raté ni reporté, est compté à sa durée prévue même sans chrono (rendez-vous, trajets), donc les catégories comme « Perso » apparaissent ; carte « Présence au travail » (temps net, en parallèle, non ajouté aux totaux par activité). À valider : le comptage automatique des trajets et rendez-vous (marquer « Raté » ce qui n'a pas eu lieu).

## 0.16.1 — correctif : la présence compte dans le « Travail » des Stats — livré, à valider sur appareil
Le décompte « Travail sur 7 h 42 » des Stats ignorait la présence encore ouverte (aujourd'hui). Elle est maintenant comptée en direct, avec le détail « présence / activités de travail hors présence » dans la carte Travail (et par jour en vue semaine). La carte séparée « Présence au travail » est supprimée.

## 0.17.0 — le temps de travail = la présence (badgeuse) — livré, à valider sur appareil
En haut des Stats et dans la barre du jour : uniquement le temps de présence (net des pauses, en direct pour aujourd'hui) face aux 7 h 42, avec l'écart. Plus aucun ajout des activités ni des tâches. Un jour passé dont le départ n'a pas été saisi est compté 0 et marqué « départ non saisi ». Le reste des Stats (par catégorie, par activité) est inchangé.

## 0.17.1 — Récap : plus de carte « Sans heure » en semaine réelle — livré, à valider sur appareil
La carte « Sans heure » reste dans la semaine type (rappel de ce qui est prévu sans heure) mais disparaît de la semaine réelle, où seuls les temps réellement chronométrés apparaissent.
