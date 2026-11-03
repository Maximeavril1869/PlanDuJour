# STATUS — Plan du jour

Version actuelle : **0.29.0**. Règles de travail : voir `CONVENTIONS.md`. Journal daté : voir `CARNET.md`. Le tableau ci-dessous s'arrête au lot 4 ; les lots 5 à 9 et les correctifs suivants sont décrits plus bas, version par version.

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

## Lot 5 bis : chrono sur les sous-tâches libres du jour — abandonné
Décision de l'utilisateur (2 novembre 2026) : remplacé par les sous-activités cochables (0.22.0).


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

## 0.17.2 — Calendrier : les rendez-vous importés ne sont plus réexportés — livré, à valider sur appareil
Les rendez-vous importés depuis le calendrier sont marqués « Vient de mon calendrier » et ne partent plus jamais à l'export. La case existe dans l'éditeur d'un bloc ponctuel, pour marquer à la main ceux importés avant cette version. Usage prévu : exporter dans un calendrier dédié « Plan du jour » (choisi à l'ajout) que le raccourci d'import ne lit pas. Point ouvert : un code unique par événement pour la mise à jour réciproque (voir CARNET.md).

## 0.18.0 — Calendrier : codes pour retrouver un événement après un changement — livré, à valider sur appareil
Fini quand : (1) ce que l'app exporte porte un code dans le champ Notes (`PDJ-p-<id>` pour un bloc ponctuel, `PDJ-a-<activité>-<jour>` pour une occurrence d'activité) ; si tu changes l'heure, le jour ou le nom d'un bloc exporté dans Calendrier, l'import suivant le **met à jour** dans l'app au lieu de créer un doublon ; (2) ce qui vient du calendrier est retrouvé par sa **date de création**, si le raccourci la renvoie ; (3) les événements du calendrier dédié « Plan du jour » sans code sont ignorés.
Le raccourci iOS « Plan du jour RDV » doit être modifié pour renvoyer calendrier, date de création et notes (voir CONVENTIONS §31). Tests : `tests/test_calendrier.py` (33 vérifications).

## 0.18.1 — Tout est replié au départ — livré, à valider sur appareil
Fini quand, à l'ouverture de l'app : sur la page du jour, « Présence au travail », « Sans heure » (maintenant une carte repliable, avec le nombre de tâches dans le titre) et « Revue du jour » (même pour un jour passé) sont fermées ; dans Réglages, aucune carte ni ligne n'est dépliée. Un tap sur le titre déplie ; l'état déplié est gardé tant que l'app reste ouverte (pas après fermeture). Le Récap garde sa carte « Sans heure » en semaine type, non repliable. Tests : `tests/test_pliage.py` (10 vérifications).

## 0.19.0 — Réinitialisation (remplace « Rétablir les valeurs de départ ») — livré, à valider sur appareil
Fini quand, en bas de Réglages, « Réinitialiser… » ouvre un panneau avec deux choix : **Tout effacer** (réglages vierges : aucune activité, catégorie, tâche habituelle ni titre ignoré ; un seul profil « Journée » à heures libres, tous les jours ; aucun congé ; plus tous les jours) ou **Effacer seulement les jours** (réglages gardés). Confirmation obligatoire en tapant EFFACER (la casse n'a pas d'importance) ; un mot incorrect n'efface rien. **Définitif : aucune copie de sécurité** ; les anciennes copies d'import sont effacées aussi. L'app reste vierge après fermeture et réouverture. Tests : `tests/test_reinitialisation.py` (22 vérifications).
À valider : la cible de travail reste 7 h 42 (valeur obligatoire) ; modifiable dans « Catégories et travail ».

## 0.19.1 — Export vers Calendrier : seulement les blocs avec rappel — livré, à valider sur appareil
Décision de l'utilisateur : l'app devient l'outil principal ; on n'exporte vers Calendrier que les tâches pour lesquelles on veut un rappel. L'export ne retient plus que les activités et blocs ponctuels dont le champ « Rappel dans Calendrier » est réglé (« à l'heure » compte). Un bloc sans rappel, un trajet (`noCal`) ou un rendez-vous venu du calendrier (`fromCal`) n'est jamais exporté. Sans aucun bloc avec rappel sur la période, le message l'explique. L'import depuis le calendrier est inchangé. À valider : que le fichier `.ics` s'ajoute à Calendrier (l'aperçu sans option vu sur l'iPhone reste inexpliqué : hypothèse d'un ancien fichier). Tests : `tests/test_calendrier.py` (37 vérifications).
À valider sur l'iPhone (0.18.0) : que « Date de création » est bien renseignée pour un événement du calendrier et ne change pas quand on le modifie ; que rouvrir un `.ics` de même code dans le calendrier « Plan du jour » met l'événement à jour au lieu de le dupliquer.

## 0.20.0 — Export par case à cocher, import retiré — livré, à valider sur appareil
Décision de l'utilisateur : on n'importe plus, on exporte seulement, avec une case à cocher. Case « Exporter vers Calendrier » (`toCal`, décochée par défaut) sur les activités, les tâches habituelles et les blocs ponctuels ; le rappel devient facultatif. Retirés : import (zone de collage, bouton, raccourci), « Titres à ignorer », `fromCal`, `calKey`, `noCal`. À valider : l'ajout du `.ics` dans Calendrier après un export d'un seul bloc coché. Tests : 48 vérifications (`test_calendrier` 16, `test_pliage` 10, `test_reinitialisation` 22).

## 0.21.0 — Regroupements par catégorie en menus repliables — livré, à valider sur appareil
Fini quand : (1) sur la page du jour, la carte « Sans heure » contient un menu par catégorie (titre « Travail · 3 »), tous **fermés au départ**, dans l'ordre des catégories de Réglages (A à Z, « Sans catégorie » en dernier), les tâches triées par nom ; l'état déplié est gardé tant que l'app reste ouverte ; (2) dans Réglages, les catégories de « Activités » et de « Tâches habituelles » sont des menus repliables, fermés au départ ; (3) « + Ajouter » ouvre « Sans catégorie » et montre la nouvelle ligne ; une erreur de saisie ouvre le menu concerné. Demande de l'utilisateur, décision « fermé pour libérer la vision globale ». Tests : `tests/test_regroupements.py` (26 vérifications) ; au total 74 vérifications passent (16 + 10 + 22 + 26).
À valider : le coût en taps sur la page du jour (carte, puis catégorie) ; le changement de catégorie d'une ligne ne la déplace qu'à l'enregistrement (voir CONVENTIONS §35).

## 0.22.0 — Sous-activités cochables — livré, à valider sur appareil
Fini quand : dans « Sans heure » et dans le panneau d'un bloc, chaque sous-activité a une case « fait » propre au jour ; arrêter son chrono (ou passer à une autre sous-activité) ou saisir un temps à la main la coche d'office ; on peut la cocher ou la décocher à la main (décocher garde le temps) ; la progression « n/m » s'affiche dans « Sans heure » ; un jour passé affiche aussi les cases, sans chrono. Demande de l'utilisateur : des tâches quotidiennes à cocher **et** chronométrer. Tests : `tests/test_cochables.py` (23 vérifications) ; au total 97 vérifications passent (16 + 10 + 22 + 26 + 23).
À valider : la coche d'office à la saisie manuelle d'un temps (choix fait pour économiser des taps) ; le lot 5 bis est en suspens.

## 0.23.0 — Catégories en arbre — livré, à valider sur appareil
Fini quand : dans Réglages > Catégories, chaque catégorie se range « Dans » une autre (jusqu'à 8 niveaux, un seul parent) ; les listes, « Sans heure » et les Stats affichent le chemin « Pro › RH » ; supprimer une catégorie remonte ses enfants ; les données invalides sont réparées. Tests : `tests/test_arborescence.py` (13 vérifications) ; 110 au total.
Écart avec le plan initial : on réutilise les catégories comme nœuds de l'arbre (pas de table séparée) ; pas de racines Pro / Perso / Trajets imposées ni de migration automatique ; l'utilisateur crée son arbre.

## 0.23.1 — Statuts Travail / Perso / Hors et arbre en menus imbriqués — livré, à valider sur appareil
Fini quand : dans Réglages > « Catégories et travail », (1) trois menus **Travail · n**, **Perso · n**, **Hors · n**, fermés au départ, chacun avec une pastille de couleur ; (2) chaque catégorie est un menu qui contient son éditeur (nom, « Dans », statut, ✕) et ses sous-catégories, jusqu'à 8 niveaux, avec un trait de couleur par statut ; (3) le **statut** se choisit sur la catégorie de niveau supérieur seulement : les sous-catégories l'héritent (case grisée « Statut (hérité) »), donc aucun mélange possible ; (4) « Hors » = ni travail ni perso (trajets) et sert aussi aux activités sans catégorie ; (5) une ligne modifiée reste en place jusqu'à l'enregistrement, puis se range ; (6) « + Catégorie » crée une racine Perso et ouvre le menu ; supprimer une catégorie laisse ses sous-catégories un niveau plus haut. La case « Travail » est remplacée par ce statut (une ancienne case cochée donne Travail, décochée donne Perso, la catégorie de départ « Trajets » donne Hors). Les Stats « Par catégorie » étiquettent « · travail » et « · hors ». Tests : `tests/test_statuts.py` ; l'étiquette « · travail » / « · hors » des Stats est remplacée en 0.24.0 par l'arbre.
À valider sur l'iPhone : lisibilité de l'arbre à plusieurs niveaux, coût en taps pour éditer une catégorie (menu, puis ligne), couleurs en mode clair et sombre.

## 0.24.0 — Stats en arbre repliable — livré, à valider sur appareil
Fini quand, dans l'onglet **Stats** (jour, semaine ou mois), la carte « Par catégorie » montre : (1) trois menus **Travail**, **Perso**, **Hors**, toujours présents, fermés au départ, avec leur **total à droite** (somme de leurs catégories de niveau supérieur) ; un statut sans temps affiche 0 min et n'a rien à déplier ; (2) dedans, un menu par catégorie, imbriqué comme dans Réglages, avec **son total** (ses activités plus ses sous-catégories) ; (3) au bout de chaque branche, les **activités** (durée, barre = part de la catégorie) et leurs **sous-activités** ; (4) une activité sans catégorie, ou dont la catégorie a été supprimée, est dans **Hors › Sans catégorie** (en dernier) ; (5) une catégorie sans temps sur la période n'apparaît pas ; (6) l'état déplié est gardé tant que l'app reste ouverte (changement de jour, semaine, mois compris), pas après fermeture. La somme Travail + Perso + Hors égale le total des activités : aucun temps n'est compté deux fois. La carte « Par activité » (classement à plat) et la carte « Présence au travail » (badgeuse, cible 7 h 42) sont inchangées. Tests : `tests/test_stats_arbre.py` (25 vérifications), contrôle négatif fait ; au total 169 vérifications passent.
Validé sur l'iPhone par l'utilisateur (3 novembre 2026, liste de contrôles). Décision : on garde les deux cartes, « Par catégorie » (arbre) et « Par activité » (à plat).

## 0.25.0 — Rappel de sauvegarde — livré, à valider sur appareil
Fini quand : (1) sur la page du jour, un bandeau **« Pense à sauvegarder tes données »** apparaît quand des modifications ne sont pas sauvegardées depuis au moins N jours (7 par défaut), avec la date de la première modification, la date de la dernière sauvegarde (ou « aucune ») et deux boutons : **Exporter maintenant** (même export que dans Réglages) et **Plus tard** (le bandeau revient demain) ; (2) dans **Réglages › Sauvegarde**, un résumé (« Dernière sauvegarde : … ; modifications non sauvegardées depuis … ») et un choix du délai : Jamais, 3, 7, 14 ou 30 jours, appliqué tout de suite sans « Enregistrer » ; (3) une **modification** = une saisie sur la page du jour ou l'enregistrement des réglages ; ouvrir l'app ne compte pas, donc une app qu'on n'a pas touchée ne réclame rien ; (4) **exporter** (bandeau ou Réglages) remet le compte à zéro ; annuler la feuille de partage ne compte pas comme une sauvegarde ; (5) **importer un fichier en remplaçant tout** remet le compte à zéro (l'appareil est identique au fichier), **réglages seulement** ou **effacer les jours** comptent comme une modification ; **tout effacer** efface aussi l'état de sauvegarde ; (6) l'état est propre à chaque appareil et n'entre jamais dans le fichier exporté ; une app déjà utilisée avant la 0.25.0 commence le compte à la première ouverture. Tests : `tests/test_sauvegarde.py` (50 vérifications), deux contrôles négatifs faits ; au total 219 vérifications passent (voir 0.25.1 pour le bandeau).
Tests iPhone faits le 3 novembre 2026 : « ça semble fonctionner correctement » ; le bandeau, qui demande au moins 3 jours de modifications non sauvegardées, reste à voir apparaître ; iPad à faire. À valider : la feuille de partage (« Enregistrer dans Fichiers ») compte bien comme une sauvegarde même si on choisit un autre emplacement (l'app ne peut pas le savoir) ; le délai de 7 jours est-il le bon .

## 0.25.1 — Bandeau de sauvegarde sur tous les onglets — livré, à valider sur appareil
Décision de l'utilisateur (3 novembre 2026). Fini quand le bandeau « Pense à sauvegarder tes données » est visible en tête de **Jour, Récapitulatif, Stats et Réglages** dès que le délai est atteint ; « Plus tard » et « Exporter maintenant » le cachent partout, depuis n'importe quel onglet ; changer le délai dans Réglages le met à jour tout de suite ; il suit le changement de jour (vérifié toutes les 15 secondes). Tests : `tests/test_sauvegarde.py` (59 vérifications), contrôle négatif fait ; au total 228 vérifications passent.

## 0.25.2 — Demande de stockage persistant — livré, à valider sur appareil
Décision de l'utilisateur (3 novembre 2026), après vérification des sources de WebKit : l'app est ouverte depuis l'icône de l'écran d'accueil sur l'iPhone et l'iPad (donc hors du plafond de 7 jours de Safari). Fini quand, au démarrage, l'app demande au système de ne pas supprimer ses données pour faire de la place, et que **Réglages › Sauvegarde** affiche le résultat : « accordée », « non accordée par le système » (avec le conseil d'exporter régulièrement) ou « non disponible sur cet appareil ». La demande n'est faite qu'une fois par ouverture, sans action de l'utilisateur ; une erreur ou l'absence de l'interface ne casse rien. Ce n'est pas une garantie (WebKit accorde selon des critères) : l'export reste la vraie sauvegarde. Tests : `tests/test_stockage.py` (14 vérifications, système simulé), contrôle négatif fait ; au total 242 vérifications passent.
À valider sur l'iPhone et l'iPad : quel état s'affiche (accordée ou non).

## 0.25.3 — Tâches « sans heure » refaisables plusieurs fois par jour — livré, à valider sur appareil
Décisions de l'utilisateur (3 novembre 2026) : après ■, la tâche reste dans « Sans heure » avec le temps fait aujourd'hui ; chaque ▶ ouvre un nouveau passage ; chaque passage a son créneau dans la frise et se cumule dans les Stats ; ça vaut pour **toutes** les tâches sans heure sans sous-activité (activités de Réglages et blocs ponctuels), sans case à cocher à régler ; pas de case « fait » (le chrono prouve que c'est fait) : on affiche « N passages · durée ». Pour nommer un passage (ex. le dossier traité), on utilise les sous-tâches libres du jour, qui n'ont pas de temps propre. Les tâches à sous-activités gardent leur fonctionnement (l'utilisateur n'en a pas pour l'instant).
Fini quand, sur l'iPhone : ▶ puis ■ sur une tâche sans heure la laisse dans « Sans heure » avec sa durée ; un second ▶ crée un second passage (« 2 passages ») ; la frise montre un créneau par passage ; Stats additionne ; Détails permet d'ajouter ou supprimer un passage à la main et « Effacer les passages ».

## 0.26.0 — Ligne « maintenant » — livré, à valider sur appareil
Demande de l'utilisateur (3 novembre 2026) : un curseur qui avance avec l'heure, pour se situer par rapport aux blocs et aux temps libres. Décisions : une ligne (pas une barre de progression) sur la frise du jour **et** dans le Récap de la journée courante ; la page se place sur la ligne à l'ouverture et au retour sur « aujourd'hui », puis il défile librement ; rien avant le lever, après le coucher ni sur un autre jour ; pas de grisé du passé.
Fini quand, sur l'iPhone : une ligne rouge avec l'heure suit le temps sur la frise (mise à jour toutes les 15 secondes) ; à l'ouverture l'écran est centré dessus ; on peut défiler sans que la page revienne ; « Maintenant » apparaît dans le Récap, entre les bons blocs.

## 0.26.1 — Toucher « Jour » recentre sur la ligne — livré, à valider sur appareil
Demande de l'utilisateur (3 novembre 2026) : l'app reste ouverte des heures ; toucher l'onglet « Jour » doit recentrer l'écran sur la ligne « maintenant ». Vaut depuis un autre onglet comme depuis « Jour » lui-même, seulement si le jour affiché est aujourd'hui.

## 0.27.0 — Export vers Calendrier du jour même — livré, à valider sur appareil
Demande de l'utilisateur (3 novembre 2026) : tout se met à jour dans l'app, donc le jour même doit aussi être exportable (la 0.13.3 l'avait retiré). Décisions : périodes « Aujourd'hui » et « 7 jours à partir d'aujourd'hui » ajoutées à « Demain » et « 7 jours à partir de demain » ; uniquement dans Réglages › Calendrier ; contenu = plan actuel de l'app (blocs terminés à leurs heures réelles, bloc en cours jusqu'à maintenant, blocs à venir à leur heure recalée), seuls les blocs cochés ; une tâche sans heure à passages = un événement par passage ; réexporter doit mettre à jour (mêmes identifiants), un bloc retiré du plan reste dans Calendrier.
Fini quand, sur l'iPhone : exporter « Aujourd'hui », l'ajouter à Calendrier, changer un bloc dans l'app, réexporter : l'événement est mis à jour et non dupliqué (**à confirmer sur iOS**, non testable ici).

## 0.28.0 — Envoi vers l'app Raccourcis (plan B du .ics) — livré, à valider sur appareil
Constat de l'utilisateur (3 novembre 2026) : ni la feuille de partage ni l'enregistrement dans Fichiers ne propose Calendrier pour le fichier `.ics`. Décisions : passer par l'app Raccourcis (pas par le Mac) ; agenda dédié « Plan du jour » (existe déjà) vidé puis recréé à chaque envoi ; rappel fixe à l'heure de l'événement. Bouton « Envoyer vers Raccourcis » dans Réglages › Calendrier (le bouton .ics reste). Procédure du raccourci : `RACCOURCI.md`.
Fini quand, sur l'iPhone : le raccourci « Plan du jour » est construit ; « Envoyer vers Raccourcis » ouvre Raccourcis (sinon lancer le raccourci à la main) ; les événements apparaissent dans l'agenda « Plan du jour » ; un second envoi les remplace sans doublon. **À confirmer** : ouverture du lien `shortcuts://` depuis l'app installée ; lecture des dates ISO par Raccourcis.

## 0.29.0 — Identifiant stable par événement envoyé à Raccourcis — livré, raccourci à reconstruire et à valider sur appareil
Constat de l'utilisateur (3 novembre 2026) : le raccourci « supprimer puis recréer » (0.28.0) est validé sur appareil (second envoi sans doublon avec le vrai envoi de l'app), mais il efface à chaque envoi les réglages faits à la main dans Calendrier (alertes, lieu, délai de route). Décisions : chaque événement du JSON porte un `id` (le code de l'export `.ics`, entre crochets : `[PDJ-p-<id>]`, `[PDJ-a-<activité>-<jour>]`, avec `-<rang>` pour un passage) que le raccourci écrit dans les Notes ; à chaque envoi il retrouve l'événement (Notes **contient** l'id), le met à jour (titre, début, fin) ou le crée ; le plan de l'app l'emporte sur le titre et les heures modifiés à la main, le reste est conservé. Un bloc retiré du plan **n'est pas supprimé** de Calendrier ; sa détection (et une notification) est reportée à une version suivante (décision de l'utilisateur). Aucun événement coché : le raccourci n'est plus ouvert (toast « rien à envoyer »). Texte d'aide de Réglages › Calendrier corrigé.
Décision de l'utilisateur (3 novembre 2026, en construisant le raccourci) : l'agenda cible est **Travail** (plus d'agenda séparé « Plan du jour » pour les exports) ; l'étape « supprimer » a été retirée du raccourci (elle aurait effacé les vrais rendez-vous). Raccourci reconstruit et utilisé, « tout fonctionne » selon l'utilisateur ; détails à confirmer ci-dessous.
Fini quand, sur l'iPhone : le raccourci est reconstruit selon `RACCOURCI.md` ; un envoi crée les événements avec leur id dans les Notes ; un second envoi après changement d'heure ou de titre dans l'app met l'événement à jour sans doublon ; une alerte ou un lieu réglé à la main dans Calendrier survit à l'envoi suivant. **Migration** : les événements créés par la 0.28.0 (ancien agenda « Plan du jour », sans id) sont à supprimer à la main. Tests : `tests/test_raccourcis.py` (19 vérifications), deux contrôles négatifs faits ; 334 vérifications.

## Prochains lots décidés (arborescence, 2 novembre 2026)
Décisions : arbre à plusieurs niveaux, **table unique à parent unique** (jamais plusieurs parents, sinon un temps serait compté deux fois) ; profondeur plafonnée à 8 ; **pas de racines imposées** ; le temps est enregistré au niveau le plus fin (activité ou sous-activité) ; le statut Travail / Perso / Hors est porté par la racine et hérité (0.23.1) ; le temps de travail réel vient de la présence ; une activité sans catégorie compte comme Hors.
- 0.23.0 : modèle de données, éditeur d'arbre, chemin « A › B » affiché. Livré.
- 0.23.1 : statuts et menus imbriqués dans Réglages. Livré.
- 0.24.0 : Stats en arbre repliable, un total à chaque niveau, plus les totaux Travail / Perso / Hors. Livré.
- 0.25.0 : rappel de sauvegarde. Livré.
- 0.25.1 : le bandeau de sauvegarde sur tous les onglets. Livré.
- 0.25.2 : demande de stockage persistant au démarrage. Livré.
- 0.25.3 : tâches sans heure refaisables plusieurs fois par jour (passages). Livré.
- 0.26.0 : ligne « maintenant » sur la frise et dans le Récap. Livré.
- 0.26.1 : toucher « Jour » recentre sur la ligne. Livré.
- 0.27.0 : export Calendrier du jour même, un événement par passage. Livré.
- 0.28.0 : envoi vers Raccourcis (agenda dédié). Livré.
- 0.29.0 : id stable par événement, mise à jour au lieu de recréer. Livré (raccourci à reconstruire).
- À venir (décidé) : nom saisi par passage d'une tâche sans heure (titre de l'événement dans Calendrier) ; détection des événements disparus du plan.
- Avant la 1.0 : liste de contrôles sur appareil (iPhone puis iPad), période d'usage facultative d'environ deux semaines.
