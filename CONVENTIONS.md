# CONVENTIONS — Plan du jour

Écrit une fois, au lot 1. **Rien ici n'est rouvert** dans les lots suivants : on applique, on ne refond pas.
Ce qui ne bloque pas mais mérite d'être revu va dans « À revoir plus tard » de `STATUS.md`.

## 1. Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Toute l'app : HTML + CSS + JS dans un seul fichier |
| `manifest.json` | Manifeste PWA |
| `sw.js` | Service worker (fonctionnement hors ligne) |
| `icon-180.png`, `icon-192.png`, `icon-512.png` | Icônes |
| `CONVENTIONS.md`, `STATUS.md`, `README.md` | Documentation |

Pas d'autre fichier de code tant qu'aucun lot ne le justifie.

## 2. Technique

- JavaScript natif, aucun framework, aucun outil de build, aucune dépendance externe (pas de CDN : l'app doit marcher hors ligne).
- Test local : ouvrir le dossier dans VSCode et lancer un petit serveur (`python3 -m http.server`) ou l'extension Live Server. Le service worker n'est pas enregistré sur `localhost` (sauf avec `?sw=1`), pour ne pas servir de vieux fichiers pendant le développement.
- Hébergement : GitHub Pages, branche `main`, racine du dépôt. Tous les chemins sont **relatifs** (`./`), car l'app vit sous `/PlanDuJour/`.

## 3. Structure du script (dans `index.html`)

Sections dans cet ordre fixe, repérées par un commentaire `// ==== N. NOM ====` :

1. CONFIG
2. TEMPS (lecture / affichage des heures)
3. VALEURS PAR DÉFAUT
4. STOCKAGE
5. VALIDATION
6. VUE (rendu)
7. ÉVÉNEMENTS
8. INIT

Un nouveau lot **ajoute** des sections ou des fonctions dans la section qui convient ; il ne réorganise pas l'existant.

## 4. Noms

- Identifiants JavaScript : anglais, `camelCase`. Textes affichés : français.
- `id` et classes CSS : `kebab-case`.
- Clés de stockage : préfixe `plandujour.`.

## 5. Heures, jours, durées

- En interne : **minutes depuis minuit** (entier, 0 à 1439). Durées en **minutes**.
- Affichage : `HH:MM` en **24 h** (`06:53`, `16:28`). Jamais d'AM/PM.
- Saisie : champ texte tolérant, accepte `6:53`, `6h53`, `06:53`, `0653`, `653`, `6h`. Le clavier numérique de l'iPhone n'a pas de `:` : taper `0653` doit suffire. La valeur est remise en `HH:MM` en quittant le champ.
- Jours : numéros ISO, `1` = lundi … `7` = dimanche.
- La journée va du lever au coucher, **le même jour** (pas de coucher après minuit en version 1).

## 6. Fourchettes horaires

- Stockées en `{ min, max }`.
- L'app **ne choisit jamais** une valeur à la place de l'utilisateur : la fourchette est indicative. L'heure réelle du jour est saisie par l'utilisateur chaque jour (prévu au lot 2).

## 7. Données

- Un seul objet JSON, versionné (`version`), par clé de stockage. Actuellement : `plandujour.reglages` (contraintes), `version: 1`.
- Changer le format = incrémenter `DATA_VERSION` **et** écrire la fonction de migration. On ne casse jamais les données déjà saisies.
- Tous les accès au stockage sont dans un `try/catch` ; l'app doit s'afficher et rester utilisable même si le stockage est indisponible.
- Le stockage du navigateur peut être vidé (Safari, mode privé, réinstallation de la PWA). L'export / import (lot 4) est la protection ; d'ici là, ne rien saisir d'irremplaçable.

## 8. Données et confidentialité

- Le dépôt ne contient **que du code**, jamais de données saisies.
- Aucun vrai SIREN ni vraie donnée dans le code, les tests ou les échanges. Les tests utilisent de faux libellés (`Dossier test 1`).
- Le champ « dossier » des sous-tâches (lot 3) est un texte libre : l'utilisateur décide de son contenu.

## 9. Interface

- Mobile d'abord (iPhone), utilisable sur iPad.
- Champs de saisie à 16 px minimum (sinon iOS zoome à la mise au point). Zones tactiles d'au moins 44 px.
- Mode sombre automatique (`prefers-color-scheme`). Marges de zone sûre (`env(safe-area-inset-*)`).
- Les erreurs de saisie s'affichent sous le champ concerné, jamais dans une alerte bloquante.
- Une modification n'est enregistrée que par le bouton **Enregistrer** (lot 1). Les lots suivants gardent ce principe pour les réglages.

## 10. Service worker et versions

- `APP_VERSION` (dans `index.html`) et `VERSION` (dans `sw.js`) portent la **même valeur**. À chaque livraison d'un lot, on incrémente les deux.
- Le nom du cache contient la version : un changement de version vide l'ancien cache.
- La version s'affiche en bas de l'écran Réglages, pour vérifier sur l'iPhone qu'il a bien la dernière.

## 11. Git

- Branche `main`. Un lot = un ou plusieurs commits, message `Lot N : résumé`.
- `STATUS.md` est mis à jour dans le même commit que le code du lot.

## 12. Consigne de début de session

> Applique les conventions, ne propose pas de nouvelle refonte. Ce qui n'est pas bloquant va dans « À revoir plus tard ».

Une session = un lot, avec un résultat que l'utilisateur teste sur son iPhone ou dans VSCode.

## 13. Modèle d'activités (lot 2 bis, remplace les ajouts du premier lot 2)

- **Une seule notion : l'activité.** Elle a un nom, des jours de la semaine, un comportement et un horaire.
  - Comportements : `fixed` (heure fixe, ne bouge jamais), `flex` (heure prévue, glisse si ce qui précède déborde), `free` (sans heure : durée seule, lancée au chrono).
  - Horaire : début + fin ou début + durée (`entry: 'end' | 'duration'`). En interne : `start` (minutes depuis minuit, `null` pour `free`) et `duration` (minutes). La fin est toujours calculée.
- **Réglages** (`plandujour.reglages`, `version: 3`) : `wake`, `bedtime`, `relaxFloor` et la liste `activities`. Tout ce qui est régulier s'y règle ; le modèle d'une nouvelle activité est créé par le bouton « + ».
- **Jours** (`plandujour.jours`, `version: 2`) : par date, `real` (heures réelles `{ start, end }` par clé de bloc, `act:<id>` ou `p:<id>`) et `ponctuels` (blocs d'un seul jour, mêmes champs qu'une activité sans les jours). Tout ce qui est ponctuel se saisit dans le jour concerné.
- **Chrono** : disponible sur tous les blocs. Démarrer et arrêter enregistrent l'heure réelle (minutes) ; un seul bloc tourne à la fois (en démarrer un arrête les autres). Les heures réelles, conservées 400 jours, servent aux statistiques futures.
- **Glissement** (`buildDay`) : les blocs sont triés par début ; un bloc `flex` non démarré commence à `max(heure prévue, fin la plus tardive des blocs précédents)`. Un bloc démarré mais non terminé finit à `max(début + durée, maintenant)` : il repousse la suite en direct. Un bloc `fixed` ne bouge jamais, un chevauchement est signalé.
- **Temps disponible** : écart entre deux éléments consécutifs (blocs, et depuis la 0.32.1 lignes de repère, § 51), du lever au premier élément, et du dernier élément au coucher (comparé à la détente minimale `relaxFloor`). Affiché dans le Récapitulatif et sur la page du jour.
- **Heures du jour** : plus de fourchette ni de champs d'arrivée et de départ. L'arrivée est la fin réelle du « Trajet aller », le départ le début réel du « Trajet retour ».
- **Enregistrement immédiat** pour les données du jour ; le bouton « Enregistrer » reste réservé aux réglages (§9).
- **Migrations** : les réglages 1 et 2 sont convertis à la lecture (trajets, rendez-vous réguliers, saxophone, ménage et blocs mobiles deviennent des activités) puis réécrits en version 3 au prochain enregistrement. Les jours 1 sont convertis en jours 2. Si les jours sont illisibles, une copie brute est gardée sous `plandujour.jours.sauvegarde`.
- **Point d'accès pour les tests** : `window.PDJ` expose `buildDay` et quelques utilitaires. `buildDay` est une fonction pure (réglages, données du jour, jour de semaine, heure actuelle) : aucun accès au DOM ni au stockage.

## 14. Ajouts du lot 3 (rien de ce qui précède n'est modifié)

- **« À confirmer »** : case facultative `confirm` sur une activité ou un bloc ponctuel (sans effet pour un bloc « sans heure », qui se confirme par le chrono). Quand l'heure de fin prévue est passée (ou que le jour est passé) sans heure réelle, le bloc apparaît dans la carte « À confirmer » avec « Fait » (enregistre les heures prévues comme heures réelles) et « Raté ».
- **Raté** : `real[clé] = { start: null, end: null, missed: true }`. Le bloc quitte le plan : il ne pousse rien, son temps redevient disponible, il est listé dans « Ratés » avec « Rétablir ». Les blocs ratés restent dans les données pour les statistiques.
- **Sous-tâches** : par jour et par bloc, dans `days[date].subtasks[clé]` = liste illimitée de `{ id, label, action, done }`. `label` et `action` (80 caractères maximum) sont des textes libres : l'utilisateur décide de leur contenu (voir §8). Elles sont supprimées avec le bloc ponctuel auquel elles appartiennent. Il n'existe pas de liste récurrente.
- **Détente** : temps entre la fin du dernier bloc et le coucher (`relax` dans `buildDay`), affiché en permanence en haut du jour ; l'encart passe en alerte sous `relaxFloor`.
- **Débordement** : l'app signale (chevauchement, détente trop courte, blocs après le coucher, bloc « sans heure » plus long que le plus grand temps disponible) sans rien supprimer ni proposer de coupe automatique. Les coupes automatiques de la première version du cahier des charges sont abandonnées.
- Ajouts de champs facultatifs, lus avec une valeur par défaut : pas de changement de `DATA_VERSION` (réglages 3) ni de `DAYS_VERSION` (jours 2).

## 15. Ajouts du lot 3 bis : reporter (rien de ce qui précède n'est modifié)

- **« À reporter »** : case facultative `carry` sur une activité ou un bloc ponctuel (tous comportements). Absente dans des réglages enregistrés avant la 0.5.0, elle vaut `true` pour `act-sax`, `act-menage`, `act-concentration` et `false` sinon ; une fois enregistrée, la valeur de l'utilisateur prime. Pas de changement de `DATA_VERSION` ni de `DAYS_VERSION`.
- **Revue du jour** (`buildDay` → `review`, `reviewed`) : bloc « à reporter » non traité et soit non fait (état `planned`, sans heure non lancé, ou raté), soit fait avec des sous-tâches non cochées. Un bloc en cours n'y figure pas. Disponible pour aujourd'hui et les jours passés, jamais pour un jour futur.
- **Trace** : `days[date].review[clé] = { status: 'carried' | 'dropped', part: 'block' | 'subs', to, pid, tkey, sids, setMissed }`. Elle sert à lister « Déjà traités », à compter plus tard (statistiques) et à annuler.
- **Reporter** (`carryItem`) : cible strictement après le jour d'origine. Bloc non fait → nouveau bloc ponctuel `free` de même nom et durée sur le jour cible (`from` = jour d'origine, `carry` conservé), avec copie des sous-tâches non cochées (décochées) ; l'original reçoit `real[clé] = { missed: true }` (sauf s'il l'était déjà, `setMissed` le retient). Bloc fait → seules les sous-tâches non cochées partent, sur la même activité si elle est prévue le jour cible (même clé), sinon dans un bloc ponctuel `free`. Les sous-tâches cochées restent sur le jour d'origine.
- **Abandonner** (`dropItem`) : un bloc non fait est marqué raté ; un bloc fait garde ses sous-tâches telles quelles ; dans les deux cas la trace `dropped` retire la ligne de la revue.
- **Annuler** (`undoReview`) : supprime la copie sur le jour cible (bloc ponctuel et sous-tâches copiées), retire le raté posé par le report, efface la trace. « Rétablir » sur un raté reporté annule d'abord le report.
- **Interface** : la carte est repliée pour aujourd'hui, ouverte pour un jour passé, repliée de nouveau quand on change de jour. Le choix du jour (`<input type="date">`) est une carte séparée en haut du jour ; le rafraîchissement automatique de 15 s est suspendu pendant le choix.

## 16. Ajouts du lot 3 ter : profils de journée (rien de ce qui précède n'est modifié)

- **Profil** : `{ id, name, wake, bedtime, days, removes }` dans `settings.profiles` (liste, au moins un). `wake` et `bedtime` au niveau des réglages restent ceux du premier profil (compatibilité) ; l'app lit toujours ceux du profil du jour. `relaxFloor` reste global.
- **Résolution** (`resolveProfile`) : profil choisi pour le jour (`days[date].profile`) s'il existe, sinon le premier profil dont `days` contient le jour de la semaine, sinon le premier de la liste. `buildDay` renvoie `profile` et n'utilise que lui (lever, coucher, activités retirées).
- **`removes`** : identifiants d'activités absentes de la journée (jamais des blocs ponctuels). Leurs données restent stockées.
- **Migration** : des réglages sans `profiles` reçoivent trois profils (Semaine, Week-end, Télétravail) qui reprennent tous l'ancien lever et l'ancien coucher ; le télétravail retire les deux trajets. Les valeurs inventées (week-end, télétravail) ne s'appliquent qu'aux réglages de départ. Pas de changement de `DATA_VERSION` ni de `DAYS_VERSION`.
- **Interface** : profils édités comme les activités (bouton « + », ✕, puces de jours et d'activités retirées, mises à jour quand les activités changent) ; sélecteur du profil sur la page du jour, enregistré immédiatement.

## 17. Pliage dans Réglages (0.6.1, rien de ce qui précède n'est modifié)

- Les cartes « Profils de journée » et « Activités » sont des `<details class="fold">` ; chaque profil et chaque activité est un `<details class="rowfold">` dont le résumé (nom, horaires, jours) est recalculé à chaque saisie (`updateSummary`). Les lignes sont repliées par défaut, une ligne ajoutée est dépliée.
- L'état de pliage vit en mémoire (`openRows`, `foldClosed`) et survit aux réaffichages du formulaire, pas à la fermeture de l'app. Aucune donnée enregistrée n'est concernée.
- `flag()` déplie les lignes et cartes qui contiennent un champ invalide. Les libellés des cases « activités retirées » se mettent à jour sur place (`syncActChips`) : on ne remplace jamais un champ pendant qu'il est en cours de saisie.

## 18. Ajouts du lot 4 : sauvegarde et statistiques (rien de ce qui précède n'est modifié)

- **Fichier d'export** : `{ app: 'plandujour', format: 1, appVersion, exportedAt, settings, days }` où `settings` et `days` ont exactement le format des clés `plandujour.reglages` et `plandujour.jours`. Pas de nouvelle version de données.
- **Import** : le fichier est lu et validé avec `sanitize` et `sanitizeDays` (les anciens formats sont donc migrés) avant tout choix ; rien n'est écrit tant que l'utilisateur n'a pas choisi. Deux modes : tout remplacer, ou réglages seulement. Avant d'écrire, l'état précédent est copié sous `plandujour.avant-import.reglages` et `plandujour.avant-import.jours` (une seule génération). Pas de fusion.
- **Export refusé** s'il reste des modifications de Réglages non enregistrées (on exporte l'enregistré).
- **Statistiques** (`statsFor`, `statsRange`, fonctions pures) : somme de `fin − début` des heures réelles complètes, regroupée par nom d'activité (clé `act:` → nom courant de l'activité, `p:` → nom du bloc ponctuel du jour, activité supprimée → « Activité supprimée »). Les blocs ratés ou sans fin sont ignorés. Semaine ISO lundi–dimanche, mois civil ; changer de mode garde la période affichée.

## 19. Ajouts du lot 4 bis : heures libres et congé (rien de ce qui précède n'est modifié)

- **Lever et coucher facultatifs** : `wake` et `bedtime` d'un profil valent `null` (« libre »). Lever libre : l'écart du lever au premier bloc n'existe pas. Coucher libre : ni dernier écart, ni `relax`, ni alerte de coucher ; un bloc « sans heure » n'est alors limité par rien. Les valeurs `wake` et `bedtime` au niveau des réglages ne servent plus qu'en secours (profils absents) et gardent la dernière valeur numérique.
- **Période** : `period: { from, to }` (dates incluses), facultative, sur n'importe quel profil. Un profil à période s'applique tout seul pour les dates concernées, avant les jours de la semaine (premier de la liste en cas de chevauchement). `lastWake` et `returnBedtime` (heures facultatives) ne comptent que si la période existe.
- **Ajustements de congé** (`resolveProfile`, avec la date) : le jour `lastWorkDay(period.from)` reçoit `lastWake` comme lever ; le jour `eveOfReturn(period.to)` reçoit `returnBedtime` comme coucher. `lastWorkDay(k)` = dernier lundi–vendredi avant `k` ; `eveOfReturn(k)` = veille du premier lundi–vendredi après `k`. Un profil choisi à la main pour le jour n'est jamais ajusté. `buildDay` prend la date en paramètre supplémentaire (le récapitulatif, sans date, ne voit que les jours de la semaine).
- **Profils de départ** : Semaine (lun.–jeu.), Vendredi, Samedi, Dimanche, Télétravail, Congé. Des profils enregistrés avant la 0.8.0 sont lus tels quels. Pas de changement de `DATA_VERSION` ni de `DAYS_VERSION`.

## 20. Lignes repliables (0.8.1)
Toute ligne `<details class="rowfold">` affiche un chevron ▾ (fermée) / ▴ (ouverte) à droite du résumé. Le marqueur natif est masqué. Un appui sur le titre de la ligne la plie ou la déplie.

## 21. Congés séparés des profils (0.9.0)
- `settings.leave = { periods:[{id,from,to}], wake, bedtime, removes, lastWake, returnBedtime }` : une seule série de règles, une liste de périodes. Champ additif, pas de changement de version des réglages.
- Les profils ne portent plus de période. Pendant une période, `resolveProfile` renvoie le profil virtuel « Congé » (id `conge`) : les profils de journée sont suspendus. Hors période, ils reprennent. Un choix manuel sur la page du jour reste prioritaire.
- `lastWake` s'applique au dernier jour de travail avant chaque période ; `returnBedtime` à la veille de la reprise (même si c'est un jour de congé).
- Migration à la lecture : un ancien profil `prof-conge` ou à période est converti en section Congés (périodes, heures, retraits) puis retiré des profils.
- Test : `test_lot9.js` ; `test_lot8.js` (ancien modèle) est abandonné.

## 22. Détente supprimée (0.9.1)
Plus de carte « Détente » dans Réglages, plus d'encart sur la page du jour, plus d'alerte de détente minimale. Le champ `relaxFloor` reste dans les données (inutilisé) pour que les anciens exports restent lisibles. Les alertes de chevauchement et de dépassement du coucher restent.

## 23. Activités sans heure : plus de durée (0.10.0)
Une activité ou un bloc « sans heure » n'a plus de durée prévue : le champ est masqué dans l'éditeur, la valeur stockée est neutre (1) et ignorée à l'affichage. Démarré, le bloc dure jusqu'à l'heure réelle d'arrêt (ou jusqu'à maintenant). Le chrono (▶ Démarrer / ■ Arrêter) n'existe que pour aujourd'hui : un autre jour se renseigne à la main (début/fin réels).

## 24. Sous-activités chronométrées (lot 5, 0.11.0)
- Une activité de Réglages peut avoir des sous-activités permanentes : `children: [{id,name}]` (20 max). Les blocs ponctuels n'en ont pas.
- Temps d'un jour : `day.segs[blockKey] = [{cid,start,end|null}]` (champ additif, pas de changement de version). Pour un bloc qui a des segments, `buildDay` remplace `real` par début = premier segment, fin = dernier segment (null tant qu'un segment tourne). Le bloc n'a plus d'heures réelles propres (champs masqués) : son temps = somme des segments.
- Un seul chrono à la fois : `closeRunning` arrête tout bloc et tout segment en cours avant d'en démarrer un autre. Chrono seulement aujourd'hui ; les autres jours se saisissent à la main (select + début + fin).
- Stats : le total d'une activité compte la somme des segments terminés ; détail par sous-activité, « Sans détail » pour le temps sans sous-activité, « Sous-activité supprimée » si l'id n'existe plus.
- Le bouton « ▶ Démarrer » d'une activité sans heure qui a des sous-activités ouvre le panneau (choix de la sous-activité).
- Lot 5 bis (en suspens depuis la 0.22.0, abandon à confirmer) : chrono sur les sous-tâches libres du jour (checklist actuelle). Les sous-activités cochables (§36) couvrent le besoin des tâches quotidiennes.

Mise à jour 0.11.1 : au premier affichage, les cartes Profils, Congés et Activités de Réglages sont repliées (les lignes l'étaient déjà). L'état de pliage reste en mémoire pendant la session.

Mise à jour 0.11.2 : les sous-activités sont nommées dans la carte « Sans heure » ; hors aujourd'hui, le panneau propose un bouton « + nom » par sous-activité (présélection pour saisir le temps à la main).

## 25. Catégories et suivi du travail (lot 6, 0.12.0)
- `settings.categories = [{id,name,work}]` (12 max) ; `settings.workTarget` (minutes, 462 = 7 h 42). Chaque activité a `cat` (id ou null) ; chaque bloc ponctuel aussi. Valeurs de départ : Travail (travail), Trajets, Musique, Maison, assignées aux activités d'origine par leur id (`DEFAULT_ACT_CAT`). Champs additifs, pas de changement de version.
- `timeEntries` donne tous les temps terminés (bloc ou segment de sous-activité) ; `statsFor` en tire activités, sous-activités et catégories ; `workReport` ne garde que les catégories « travail » et compare à la cible : lundi–vendredi, hors périodes de congé. Le week-end n'a pas de cible : tout y est « hors cible ».
- Page du jour : barre « Travail du jour » (temps terminés seulement). Stats : carte « Travail » (semaine : détail par jour ; mois : total + week-ends travaillés) puis « Par catégorie », puis activités.
- Carte « Sans heure » : un ▶ par sous-activité aujourd'hui ; pendant un chrono, boutons ▶/■ des sous-activités sous la barre en cours.
- Test : test_lot11.js.

Mise à jour 0.12.1 : champ `parallel` sur les activités (case « On peut faire autre chose pendant », cochée par défaut sur les trajets). Un chevauchement avec une telle activité ne déclenche plus l'alerte « À vérifier ». Le travail fait pendant un trajet se note en bloc ponctuel de catégorie Travail ; le trajet garde son temps (Trajets), le travail compte en plus. Test : test_lot12.js.

Mise à jour 0.12.2 : Stats → mode « Jour » (navigation jour par jour) en plus de Semaine et Mois ; travail du jour face à la cible, ou « jour sans cible » le week-end. Test : test_lot13.js.

## 26. Calendrier (lot 7, 0.13.0)
- Export : `calendarEvents` (mode `plan` = blocs placés ; `real` = temps terminés, un événement par segment de sous-activité) puis `buildIcs` : heures locales sans fuseau, UID stable `pdj-<date>-<clé>@plandujour` (un réexport met à jour les événements). Remis par la feuille de partage (type `text/calendar`, l'option « Calendrier » ajoute les événements), sinon téléchargement.
- Import : `parseCalendarText` lit des lignes `AAAA-MM-JJ HH:MM HH:MM Titre` (produites par un raccourci iOS) ou un .ics en heures locales ; `importCalendarEvents` crée des blocs ponctuels à heure fixe et ignore les doublons (même titre, début, durée).
- Pas de lien automatique : une PWA installée a un stockage séparé de Safari, donc un raccourci ne peut pas lui passer de données par une URL. Passage par le presse-papiers (bouton « Coller et importer ») ; aucune donnée de calendrier n'est envoyée à GitHub.
- Les champs de la carte ne marquent pas « modifications non enregistrées » (`data-nodirty`).
- Test : test_lot14.js.

Mise à jour 0.13.1 : champ `noCal` sur les activités (« Ne pas exporter vers Calendrier », coché par défaut sur les trajets, car le calendrier de l'utilisateur contient déjà un événement récurrent « Train »). `settings.calIgnore` (défaut `["Train"]`) : titres exacts (sans tenir compte de la casse) ignorés à l'import des rendez-vous. Test : test_lot14.js.

Mise à jour 0.13.2 : champ `alarm` (null ou 0/5/10/15/30/60 minutes avant) sur les activités et les ponctuels, éditable par un select « Rappel dans Calendrier (à l’export) » ; l'export .ics ajoute un `VALARM` (`TRIGGER:-PT<n>M`, `PT0S` si à l'heure) à chaque événement. Défaut : aucun rappel. Champ additif, pas de changement de version des données. Test : test_lot14.js.

Mise à jour 0.13.3 : l'export vers Calendrier ne propose plus « Aujourd'hui » ni le choix plan / temps réels (l'utilisateur n'exporte que les jours suivants) : périodes « Demain » ou « 7 jours à partir de demain », contenu = plan. `calendarEvents` garde le mode 'real' (inutilisé dans l'interface).

## 27. Présence au travail (0.14.0)
Champ additif `day.presence = { start, end|null, pauses:[{start,end|null}] }` (null par défaut, pas de changement de version des jours). Chrono indépendant des activités (plusieurs chronos peuvent tourner : un seul chrono d'activité, plus la présence). Temps de travail d'un jour = présence nette (pauses retirées) + activités de catégorie « travail » dont la partie située dans la fenêtre de présence est retirée (aucun double comptage). Présence ouverte : comptée en direct pour aujourd'hui seulement (`workReport(..., nowMin)`), ignorée ailleurs. Départ conseillé = maintenant + (cible − travail du jour). `timeEntries` expose maintenant `start` et `end`. Test : test_lot15.js.

Mise à jour 0.14.1 : le Récap a deux modes. « Semaine réelle » (défaut) : les 7 dates de la semaine avec le vrai profil de chaque jour, les congés, les blocs ponctuels et les reports (`buildDay` avec les données du jour) ; flèches pour changer de semaine. « Semaine type » : l'ancien affichage par jour de la semaine, avec le profil habituel seulement. Test : test_lot16.js.

## 28. Tâches habituelles (0.15.0)
`settings.templates = [{id,name,cat|null,mode,duration,carry,parallel,noCal,alarm|null}]` (30 max, additif, pas de changement de version ; `cleanTemplates`). Utilisés seulement à la création d'un bloc ponctuel (menu `#bp-tpl`, absent s'il n'y a aucun modèle) : copie des valeurs dans le formulaire, aucune liaison ensuite. Une catégorie supprimée vide la catégorie du modèle. Les ponctuels portent maintenant `parallel` et `noCal` (cases dans l'éditeur du bloc). Test : test_lot17.js.

Mise à jour 0.15.1 : recherche de tâche (`searchTasks`, onglet Jour) sans accent ni casse, 2 lettres minimum, 80 résultats affichés au plus, à venir d'abord puis passé récent d'abord ; les jours passés sans données enregistrées ne sont pas listés (seuls les jours enregistrés comptent). Les modèles portent `confirm`. Test : test_lot18.js.

Mise à jour 0.15.2 : un bloc « sans heure » à sous-activités dont le chrono est arrêté (état `done` dérivé de ses segments) reste listé dans `build.reopen` et s'affiche dans la carte « Sans heure » avec ses boutons de sous-activités et le temps fait ; il apparaît aussi dans la frise. Test : test_lot19.js.

Mise à jour 0.15.3 : les lignes de tâches habituelles utilisent le même repli que les activités (`foldStart`, `openRows`, résumé mis à jour à la saisie). Tri par `tplListHtml` : ordre des catégories puis nom (`localeCompare` fr), seulement au rendu du formulaire (ouverture, enregistrement) ; une ligne ajoutée reste en bas et ouverte jusqu'à l'enregistrement. Test : test_lot20.js.

Mise à jour 0.15.4 : `cleanCats` et `readForm` trient les catégories par nom (`byName`) ; `actsListHtml` groupe les activités par catégorie (ordre des catégories triées) puis par nom au rendu du formulaire (`doSort` vrai) ; l'ajout ou la suppression d'une ligne ne retrie pas (les titres suivent l'ordre courant). L'ordre des activités enregistrées suit donc l'ordre affiché. Tests : test_lot21.js (les anciens tests identifient les lignes par `data-id`, jamais par position).

Mise à jour 0.15.5 : `buildDay` produit `out.spans` (un créneau par temps chronométré d'un bloc à sous-activités, sinon un créneau par bloc) ; les temps disponibles, les alertes de chevauchement et la frise s'appuient sur `spans`. `out.placed` reste la liste des blocs (une entrée par bloc) pour le reste de l'app. Tests : test_lot22.js, test_lot10.js adapté.

## 29. Avancement de la journée dans les stats (0.16.0)
`timeEntries` ajoute des entrées `auto: true` pour les blocs placés par `buildDay` qui sont à heure fixe (`mode === 'fixed'`), sans `confirm`, en état `planned`, sans revue (ni reporté ni abandonné), dont la fin est passée (aujourd'hui : `end <= maintenant`) ; jours de la période entre le premier jour enregistré et aujourd'hui. Les ratés sont exclus (hors `placed`). Ces entrées alimentent `statsFor` et `workReport` (déduction du chevauchement avec la présence incluse). Blocs souples, sans heure et « à confirmer » : seulement avec chrono, heures saisies ou « Fait ». `statsFor().presence` = présence nette de la période (affichée à part, non ajoutée aux totaux). Récap : `b.spans` (créneaux) au lieu de `b.placed`. Tests : test_lot23.js ; test_lot7.js met les blocs fixes en « à confirmer » pour isoler les temps réels.

Mise à jour 0.16.1 : `renderStats` passe l'heure courante à `workReport` pour compter la présence ouverte d'aujourd'hui ; `workReport` renvoie `presence` (total et par jour). La présence n'a plus de carte à part dans les Stats : elle fait partie du « Travail ». `statsFor` ne calcule plus de présence. Test : test_lot23.js.

Mise à jour 0.17.0 : `workReport` = présence nette seulement (`presenceNet`), comme une badgeuse. Les catégories « travail » ne servent plus qu'à l'affichage des Stats par catégorie. La présence ouverte d'un jour passé n'est pas comptée (`unclosed`). Remplace la règle « présence + travail hors présence » de la section 27. Tests : test_lot15.js, test_lot23.js, test_lot11.js, test_lot13.js adaptés.

Mise à jour 0.17.1 : le Récap n'affiche la carte « Sans heure » qu'en semaine type. Test : test_lot23.js.

## 30. Origine calendrier (0.17.2)
Champ additif `fromCal` sur les blocs ponctuels (`false` par défaut, pas de changement de version des jours). `importCalendarEvents` le met à `true`. `calendarEvents` écarte les blocs `noCal` **et** `fromCal` : ce qui vient du calendrier n'y retourne jamais. Case « Vient de mon calendrier » dans l'éditeur du bloc ponctuel (pas dans les activités de Réglages). Sens inverse (ce que l'app exporte, réimporté par le raccourci) : traité par l'usage d'un calendrier dédié que le raccourci ne lit pas, pas par le code. Mise à jour réciproque par identifiant : voir §31.

## 31. Codes d'événements (0.18.0)
- **Raccourcis ne donne aucun identifiant d'événement** (liste vérifiée sur iPhone : titre, dates, calendrier, notes, URL, date de création…). Les codes passent par les **Notes** (ce que l'app crée) et la **date de création** (ce qui vient du calendrier).
- **Export** : chaque événement porte `DESCRIPTION:<code>` (champ Notes) : bloc ponctuel `PDJ-p-<id>` (UID `pdj-p-<id>`, sans date, donc stable si le bloc change de jour), occurrence d'activité `PDJ-a-<id>-<jour>`. Exporter dans un calendrier dédié `Plan du jour` (constante `CAL_APP_NAME`).
- **Ligne du raccourci** : `AAAA-MM-JJ HH:MM HH:MM Titre | Calendrier | AAAAMMJJHHMMSS | Notes` (séparateur espace-barre-espace ; la fin de ligne est facultative : l'ancien format reste lu). Dans un `.ics`, `DESCRIPTION` et `CREATED` jouent les mêmes rôles. Une date de création n'est retenue que si elle a 14 chiffres.
- **Import** (`importCalendarEvents`), dans cet ordre : code `PDJ-a-…` → ignoré ; code `PDJ-p-<id>` → le bloc ponctuel est mis à jour (titre, jour, début, durée ; heures réelles et sous-tâches suivent le bloc), jamais recréé s'il a été supprimé ; calendrier `Plan du jour` sans code → ignoré ; sinon date de création, **seulement si elle est unique dans le lot** (les occurrences d'une série la partagent) et unique parmi les blocs enregistrés (`calKey`) → mise à jour ; sinon doublon exact (jour, titre, début, durée) → ignoré, et la date de création lui est attachée si elle lui manque ; sinon ajout (`fromCal: true`, `calKey`).
- **Limites connues** : un événement créé dans le calendrier n'est jamais réécrit par l'app (il n'est pas exporté) ; un événement modifié des deux côtés prend la valeur du dernier import ; une occurrence d'activité modifiée dans le calendrier n'est pas reprise.
- Champ additif `calKey` (14 chiffres ou `null`) sur les blocs ponctuels, pas de changement de version des jours.
- Tests : `tests/test_calendrier.py` (navigateur automatisé, voir `tests/README.md`).

## 32. Cartes repliées au départ (0.18.1)
Toute carte ou ligne repliable est **fermée à l'ouverture de l'app** : Réglages (`foldClosed`, `openRows`) et page du jour (`presOpen`, `sansOpen`, `reviewOpen` valent `false` au départ). La carte « Sans heure » de la page du jour est un `<details class="card fold" data-fid="card-sansheure">` dont le titre porte le nombre de tâches. La « Revue du jour » est aussi repliée pour un jour passé : ce point remplace la règle « ouverte d'office pour un jour passé » du §15. L'état déplié vit en mémoire seulement (survit aux réaffichages, pas à la fermeture de l'app). Test : `tests/test_pliage.py`.

## 33. Réinitialisation (0.19.0)
- Le bouton « Rétablir les valeurs de départ » (qui remplissait le formulaire sans rien enregistrer) est **remplacé** par « Réinitialiser… » (`doReset`, panneau `#reset-box`, état `resetOpen` en mémoire).
- Deux modes : `all` (réglages vierges **enregistrés** + jours vides) et `days` (jours vides, réglages intacts). Confirmation : taper `EFFACER` (`RESET_WORD`, casse ignorée), sinon rien n'est effacé.
- **Réglages vierges** (`blankSettings`) : `activities`, `categories`, `templates`, `calIgnore` vides ; un profil `prof-journee` « Journée » (lever et coucher libres, jours 1 à 7, rien de retiré) ; congés sans période ; `workTarget` garde 462 (valeur obligatoire, 1 à 1440). Comme ils sont enregistrés, le statut de chargement est `ok` : les valeurs de départ ne reviennent pas à la réouverture.
- **Définitif** : pas de copie de sécurité (choix de l'utilisateur) ; `plandujour.jours.sauvegarde` et `plandujour.avant-import.jours` sont supprimées dans les deux modes, `plandujour.avant-import.reglages` en mode `all`. Les modifications non enregistrées du formulaire sont perdues en mode `all`.
- Export vers Calendrier (0.19.1) : `calendarEvents` (mode `plan`) ne garde que les blocs dont `alarm` est un entier (0 = à l'heure) ; cela s'ajoute aux exclusions `noCal` et `fromCal` (§26, §30, §31). L'import reste disponible.
- `defaultSettings` reste utilisé au premier lancement, pour une lecture impossible et pour les migrations. Test : `tests/test_reinitialisation.py`.

## 34. Export Calendrier par case à cocher, plus d'import (0.20.0)

- L'app est la source unique. L'import depuis le calendrier est retiré (zone de collage, raccourci, titres ignorés, `calIgnore`, `fromCal`, `calKey`). Les §26, §30 et §31 ne décrivent plus que l'export : les codes `PDJ-p-` / `PDJ-a-` restent écrits dans les Notes.
- Chaque activité, tâche habituelle et bloc ponctuel porte `toCal` (booléen, **décoché par défaut**). `calendarEvents` n'exporte que si `toCal === true`. Le rappel (`alarm`) est facultatif et indépendant : un bloc coché sans rappel est exporté sans alarme.
- `noCal` (case inversée « Ne pas exporter ») est remplacé par `toCal` ; aucune migration (données réinitialisées avant le passage).

## 35. Regroupements par catégorie en menus repliables (0.21.0)

- Les regroupements par catégorie sont des menus repliables `details.grp` (`catBuckets` calcule les groupes, `grpHtml` les écrit). Ils remplacent les titres fixes `h3.tplgroup` de Réglages.
- Trois endroits : page du jour, carte « Sans heure » (`data-fid="sans-<idCatégorie>"`, état dans `sansCatOpen`) ; Réglages, carte « Activités » (`grp-acts-<id>`) et carte « Tâches habituelles » (`grp-tpl-<id>`), état dans `openRows`. `<id>` vaut `none` pour « Sans catégorie ». Les autres cartes n'ont pas de sous-groupes : rien à changer.
- **Tout est fermé au départ** (décision de l'utilisateur : « pour libérer la vision globale »), sans exception pour une catégorie unique. L'état déplié vit en mémoire seulement, comme au §32. Le titre d'un groupe est « Nom · nombre ».
- Ordre : celui des catégories de Réglages (A à Z), « Sans catégorie » en dernier ; dans un groupe, tri par nom. Dans Réglages, le tri par nom se fait à l'ouverture et à l'enregistrement seulement (règle de la 0.15.4) ; un groupe réunit toutes les lignes de la même catégorie même hors tri.
- Une ligne dont on change la catégorie reste dans son groupe jusqu'à l'enregistrement ; les compteurs suivent l'ajout et la suppression d'une tâche habituelle, pas ce changement de catégorie.
- « + Ajouter » (activité ou tâche habituelle) ouvre le groupe « Sans catégorie » pour que la nouvelle ligne soit visible. Supprimer la dernière tâche habituelle d'un groupe supprime le groupe. Une erreur de saisie ouvre le groupe, comme la ligne et la carte (`flag`).
- Test : `tests/test_regroupements.py`.

## 36. Sous-activités cochables (0.22.0)

- Chaque jour, une sous-activité peut être cochée « faite » : `day.kidsDone[clé du bloc][idSousActivité] = true` (champ additif, pas de changement de `DAYS_VERSION`). `sanitizeDays` ne garde que les valeurs `true` ; `buildDay` expose `it.kd`. La case est propre à chaque jour, alors que les sous-activités elles-mêmes sont permanentes (§24).
- Cochée **d'office** par `markKidDone` quand son chrono s'arrête (`closeRunning`, donc aussi en passant à une autre sous-activité, et `stopNow`) et quand on saisit un temps à la main (`addSeg`). Démarrer un chrono ne coche pas. Cochable et décochable à la main ; décocher laisse le temps enregistré.
- Affichage : une case par sous-activité dans la carte « Sans heure » (aujourd'hui : case + ▶ ; un autre jour : case + nom) et dans le panneau du bloc ; progression « n/m » après le nom dans « Sans heure » (`kidsProgress`, `kidRowHtml`).
- Les sous-tâches libres du jour (§14) ne changent pas. Le lot 5 bis est en suspens (§24).
- Test : `tests/test_cochables.py`.

## 37. Catégories en arbre (0.23.0)

- Une catégorie a au plus **un parent** (`parent`, id ou `null`) : la chaîne d'ancêtres se retrouve en remontant, et un temps n'est jamais compté deux fois. Pas de multi-parents. Champ additif : pas de changement de `DATA_VERSION` ; une ancienne catégorie sans `parent` reste au niveau supérieur.
- Profondeur modulable, plafonnée à `MAX_DEPTH` = 8 niveaux ; 60 catégories au plus (`MAX_CATS`). `fixParents` (appelée par `cleanCats`, `catsFromForm` et l'enregistrement) remet au niveau supérieur tout parent inexistant, soi-même, boucle ou dépassement de profondeur.
- Réglages > Catégories : chaque ligne a une liste « Dans » (niveau supérieur ou une autre catégorie ; jamais elle-même, ses descendantes, ni un parent qui ferait dépasser 8 niveaux). Supprimer une catégorie remonte ses enfants d'un niveau.
- Affichage : le chemin « A › B › C » (`catPath`) sert de nom dans les listes de catégories, les groupes de « Sans heure » et de Réglages, les résumés de tâches habituelles et la ligne « Par catégorie » des Stats. Catégories triées par chemin (`sortCats`).
- Les activités et tâches gardent une seule catégorie (`cat`) : le temps est donc compté au niveau le plus fin. Les totaux par niveau arrivent en 0.24.0 (Stats en arbre).
- Le statut Travail / Perso / Hors (ex-case « Travail ») est décrit au §38 ; pas de racines imposées (l'utilisateur construit son arbre).
- Test : `tests/test_arborescence.py`.

## 38. Statuts des catégories et arbre en menus imbriqués (0.23.1)

- Un statut `kind` : `work` (Travail), `perso` ou `hors` (ni l'un ni l'autre, par exemple les trajets). Il se choisit **sur la catégorie de niveau supérieur** ; chaque sous-catégorie prend celui de sa racine (`catKind`, `fixKinds`, `normCats`) : aucun mélange possible, et un déplacement sous un autre parent change le statut. Le champ `work` (booléen, ancien) reste synchronisé (`kind === 'work'`) pour les anciens exports et les Stats. Champ additif : pas de changement de `DATA_VERSION`.
- Lecture d'un ancien réglage sans `kind` : case Travail cochée = `work`, sinon `perso` ; la catégorie de départ `cat-trajets` devient `hors`. Une catégorie absente (activité ou bloc sans catégorie) compte comme `hors`.
- Réglages > « Catégories et travail » : trois menus `details.grp` (`data-status`) Travail, Perso, Hors, toujours présents (même vides), fermés au départ, titre « Nom · nombre de catégories ». Dedans, un menu `details.catnode` par catégorie : titre « Nom · nombre de descendantes », corps = éditeur (`.cat-row`) puis sous-catégories imbriquées (`catNodeHtml`, `catGroupsHtml`). État dans `openRows` (`grp-kind-<statut>`, `catnode-<id>`), jamais conservé après fermeture (§32).
- Une ligne modifiée (« Dans », statut) **reste en place jusqu'à l'enregistrement**, puis le formulaire est redessiné et la range (comme au §35). En attendant, `refreshCatTree` met à jour le statut hérité affiché (liste grisée pour une sous-catégorie, modifiable pour une racine), les titres, les compteurs et la couleur du menu.
- « + Catégorie » crée une racine `perso` dans le menu Perso (ouvert, curseur sur le nom). Supprimer une catégorie laisse ses sous-catégories dans le menu parent, un niveau plus haut (leurs « Dans » et statuts sont recalculés).
- Couleurs : `--k-work`, `--k-perso`, `--k-hors` (clair et sombre) ; pastille dans le titre et trait vertical par niveau. L'attribut s'appelle `data-status` (et non `data-kind`, déjà utilisé par les champs de saisie).
- Stats : l'étiquette « · travail » / « · hors » de la 0.23.1 est remplacée par l'arbre des Stats (§39).
- Test : `tests/test_statuts.py` ; `test_arborescence.py` ouvre les menus avant de saisir.

## 39. Stats en arbre (0.24.0)

- `statsTree(entries, settings)` (appelée par `statsFor`, qui renvoie `kinds` à la place de l'ancienne liste plate `cats`) construit trois statuts `{ kind, nodes, minutes }`. Le temps est compté **au niveau le plus fin** (activité, sous-activité) ; chaque nœud-catégorie `{ id, name, kind, acts, kids, minutes }` vaut ses activités plus ses sous-catégories ; chaque statut vaut la somme de ses racines. Un temps n'est donc jamais compté deux fois : Travail + Perso + Hors = total des activités.
- Une activité sans catégorie, ou dont la catégorie n'existe plus, va dans un nœud « Sans catégorie » de **Hors**, placé en dernier. Les nœuds sans temps sur la période sont omis ; les trois statuts sont toujours affichés (0 min, sans rien à déplier : classe `nokids`).
- Affichage (`statsKindHtml`, `statsNodeHtml`, `statsActHtml`) : `details.grp` par statut puis `details.catnode` imbriqués (mêmes styles que Réglages, §38, `data-status`), nom à gauche et **total à droite à chaque niveau** (`.stdur`), tout fermé au départ ; l'état déplié (`stk-<statut>`, `stn-<id>`) vit dans `statsOpen`, en mémoire seulement (§32). Les barres des activités sont leur part de la catégorie.
- Inchangés : la carte « Présence au travail » (le temps de travail réel reste la présence, §27) et la carte « Par activité » (classement à plat par nom). Le statut ne sert qu'à l'étiquette et au regroupement.
- Test : `tests/test_stats_arbre.py`.

## 40. Rappel de sauvegarde (0.25.0)

- Clé `plandujour.sauvegarde` (propre à l'appareil, **jamais exportée ni importée**) : `{ last, since, snooze, every }`. `last` = date du dernier export ; `since` = date de la **première** modification non sauvegardée (une nouvelle modification ne la repousse pas) ; `snooze` = rappel reporté jusqu'à cette date ; `every` = délai en jours parmi 0 (jamais), 3, 7 (défaut), 14, 30. Lecture tolérante (`readBackup`) : JSON illisible, date impossible ou délai inconnu retombent sur les valeurs par défaut, sans erreur.
- **Modification** (`backupMarkChanged`, qui n'écrit que si `since` est vide) : `persistDays` (toute saisie sur un jour), enregistrement du formulaire de Réglages, import « réglages seulement », « effacer seulement les jours ». Ouvrir l'app ne marque rien, sauf la première ouverture après la 0.25.0 avec des jours déjà enregistrés (`backupInit` : le compte commence ce jour-là).
- **Sauvegarde** (`backupMarkSaved` : `last` = aujourd'hui, `since` et `snooze` vidés) : à la fin de `doExport`, par la feuille de partage (une fois acceptée ; l'annulation `AbortError` ne compte pas) ou par le téléchargement. L'app ne peut pas savoir où le fichier a été rangé. Import « tout remplacer » : `backupMarkImported` (`since` vidé, `last` inchangé). « Tout effacer » supprime la clé.
- Affichage (`backupDue`) : le bandeau `#backup-banner` (classe `banner warn`, jamais replié car c'est une alerte), placé dans l'emplacement unique `#backup-slot` en tête de **tous les onglets** depuis la 0.25.1 (`renderBackupBanner`, appelée au changement d'onglet, par `renderDay`, par `refreshBackupUi` et toutes les 15 secondes ; le contenu n'est réécrit que s'il change, pour ne pas remplacer un bouton sous le doigt) apparaît si `every > 0`, `since` rempli, `snooze` absent ou passé (`snooze` = aujourd'hui compte comme passé) et `aujourd'hui − since ≥ every`. « Plus tard » règle `snooze` à demain. Boutons, gérés par l'écouteur de `#backup-slot` : `backup-now` (appelle `doExport`, qui refuse tant que Réglages a des modifications non enregistrées) et `backup-later`.
- Réglages › Sauvegarde : résumé `#backup-info` et choix `#backup-every` (dans un bloc `data-nodirty` : il s'applique tout de suite et ne rend pas le formulaire « modifié »). `refreshBackupUi` remet à jour le résumé et le bandeau.
- Test : `tests/test_sauvegarde.py`.

## 41. Stockage persistant (0.25.2)

- `requestPersistence` est appelée une fois à l'ouverture (après le premier rendu) : `navigator.storage.persisted()` d'abord, puis `persist()` si ce n'est pas déjà accordé. Résultat dans `persistState` : `pending`, `granted`, `denied` ou `na` (interface absente, ou erreur : le rejet est attrapé, rien n'est affiché comme erreur).
- Affichage : paragraphe `#persist-info` dans la carte Réglages › Sauvegarde, sous le résumé de la dernière sauvegarde ; il est réécrit à l'arrivée de la réponse et à chaque rendu de Réglages. Rien n'est stocké (l'état se redemande à chaque ouverture) et rien n'est exporté.
- Le système décide : WebKit accorde la demande selon des critères, dont l'ouverture depuis l'écran d'accueil ; ce n'est pas une garantie. Le texte « accordée » dit « ne devrait pas supprimer » et « non accordée » renvoie à l'export régulier (§40).
- Test : `tests/test_stockage.py` (le système est simulé par un script d'initialisation).

## 42. Passages d'une tâche sans heure (0.25.3)

- Une tâche `free` **sans sous-activité** (`isPlain`) se refait plusieurs fois par jour. Chaque passage est une entrée de `day.segs[clé]` avec `cid: ''` (chaîne vide, acceptée par `cleanSegs`). Pas de nouvelle clé de données, pas de migration de version.
- `startNow` sur une telle tâche : ferme le chrono en cours, convertit d'abord un ancien temps réel terminé (`day.real[clé]`) en premier passage (`toPasses`), puis ajoute `{ cid: '', start: maintenant, end: null }`. Les autres blocs gardent `day.real`.
- `buildDay` : toute tâche `free` terminée entre dans `reopen` (elle reste dans « Sans heure ») ; la frise a un créneau par passage (`spans`, déjà un par segment). `timeEntries` donne `child: null` pour un passage, donc les Stats additionnent par activité sans sous-activité inventée.
- `markKidDone` ignore un `cid` vide : un passage ne coche jamais rien. Pas de case « fait » pour ces tâches ; `passesText` affiche « N passages · durée » (rien avant 2 passages).
- Panneau du bloc : titre « Passages », liste numérotée, saisie à la main sans choix de sous-activité, bouton « Nouveau passage », « Effacer les passages » ; `savePanel` n'écrit pas de temps réel pour ces tâches (comme pour les sous-activités).
- Une tâche à sous-activités n'est pas concernée. Les sous-tâches libres nomment le travail fait mais n'ont pas de temps propre : le temps par dossier n'existe pas dans les Stats.
- Test : `tests/test_passages.py`.

## 43. Ligne « maintenant » (0.26.0, recentrage 0.26.1)

- Frise du jour (`renderDay`) : `div.nowline` posée à `y(maintenant)` si `dayNow()` n'est pas nul (jour affiché = aujourd'hui) et si l'heure est dans la plage réelle de la journée (`lo0`/`hi0` : lever ou premier bloc → coucher ou dernier bloc, avant l'arrondi à l'heure). Elle ne reçoit pas les touches (`pointer-events: none`) et passe au-dessus des blocs. L'étiquette d'heure est dans la colonne des heures. Couleur : variable `--now` (clair et sombre).
- Récap (`renderRecap`) : entrée `li.nowli` « Maintenant » triée par `at = minute + 0,2`, seulement en semaine réelle, pour la date du jour et dans la plage lever → coucher (ou premiers/derniers créneaux sans lever/coucher). `recapNowShown` mémorise la minute affichée.
- Rafraîchissement : la frise suit l'intervalle de 15 secondes existant ; le Récap est redessiné seulement si la minute a changé et que l'onglet est visible.
- Défilement : `scrollToNow` (ligne à 35 % de la hauteur de l'écran) est appelé **uniquement** à l'ouverture, au retour sur aujourd'hui et au toucher de l'onglet « Jour » (bouton « Aujourd'hui » ou navigation qui y arrive). Jamais dans le rafraîchissement : l'utilisateur doit pouvoir défiler librement. Depuis la 0.26.1, toucher l'onglet « Jour » (gestionnaire des boutons de la barre d'onglets) appelle aussi `scrollToNow`, y compris quand on y est déjà : c'est le geste volontaire pour se recentrer après un long moment en arrière-plan. Les autres changements d'onglet ne défilent pas.
- Test : `tests/test_maintenant.py` (horloge du navigateur simulée avec `page.clock`).

## 44. Export du jour même vers Calendrier (0.27.0)

- Remplace la mise à jour 0.13.3 (§ calendrier) : `doCalExport` propose `today`, `tomorrow`, `week0` (aujourd'hui + 6 jours) et `week` (demain + 6 jours). Contenu toujours = plan, seuls les blocs `toCal`.
- `calendarEvents` passe l'heure courante à `buildDay` pour le jour d'aujourd'hui seulement : un bloc en cours se termine à maintenant, les blocs recalés ont leur heure recalée. Les autres jours gardent `null`.
- Tâche sans heure sans sous-activité à passages (`isPlain` + `segs`) : un événement par passage (UID `pdj-<jour>-<clé>-<n>` ou `pdj-p-<id>-<n>`, code `PDJ-a-<id>-<jour>-<n>` ou `PDJ-p-<id>-<n>`), passage en cours jusqu'à maintenant, sans rappel. Les autres blocs gardent un événement par bloc.
- Les identifiants ne changent pas d'un export à l'autre : c'est ce qui doit permettre à Calendrier de mettre à jour au lieu de dupliquer (à confirmer sur iOS). Un bloc retiré du plan n'est pas supprimé de Calendrier.
- Test : `tests/test_export_jour.py` (heure simulée, téléchargement forcé).

## 45. Envoi vers Raccourcis (0.28.0)

- Plan B quand l'iPhone ne propose pas Calendrier pour un `.ics`. `doShortcutSend` : même période (`calPeriod`) et même contenu que l'export (`calendarEvents`, mode plan) ; texte JSON `shortcutPayload` = `{from, to, events:[{title, start, end}]}` en heures locales ISO (`isoLocal`) ; copie dans le presse-papiers (`copyText`, repli `execCommand`), puis `openLink('shortcuts://run-shortcut?name=<SHORTCUT_NAME>&input=clipboard')`. Si la copie échoue et que le texte tient dans le lien (< 12 000 caractères), repli `input=text&text=…`.
- L'ouverture passe par un lien `<a>` cliqué par le code (testable : les tests interceptent le clic).
- Le raccourci (construit par l'utilisateur, voir `RACCOURCI.md`) supprimait en 0.28.0 les événements de l'agenda « Plan du jour » entre `from` et `to`, puis créait ceux de `events` ; remplacé en 0.29.0 (§46).
- Rappel : fixe, réglé dans le raccourci. Les rappels par bloc ne passent que par le `.ics`.
- Test : `tests/test_raccourcis.py` (presse-papiers et lien simulés).

## 46. Identifiant stable par événement envoyé (0.29.0)

- `shortcutPayload` = `{from, to, events:[{id, title, start, end}]}`. `id` = `'[' + code + ']'` où `code` est celui de l'export `.ics` (§31) : `PDJ-p-<id>` (bloc ponctuel, sans jour : stable si le bloc change de jour), `PDJ-a-<activité>-<jour>` (occurrence d'activité), suffixe `-<rang>` pour un passage. L'id ne dépend ni de l'heure ni du titre : il survit au recalage du plan. Repli sur `uid` si un événement n'a pas de `code`.
- **Les crochets sont obligatoires** : le raccourci cherche avec « Notes **contient** l'id », sans crochets `PDJ-p-p1` serait trouvé dans `PDJ-p-p12`, et `PDJ-a-x-<jour>` dans `PDJ-a-x-<jour>-0`. Test : aucun id contenu dans un autre.
- Un passage qu'on supprime décale le rang des suivants (limite connue). Un id ne contient jamais de donnée réelle (identifiants internes et date).
- Le raccourci ne supprime plus rien (et ne doit **jamais** recevoir d'action « Supprimer » : l'agenda cible est désormais « Travail », décision du 3 novembre 2026) : un bloc retiré du plan reste dans Calendrier (détection et notification : version à venir). Aucun événement coché : `doShortcutSend` n'ouvre pas le raccourci (toast « rien à envoyer »).
- Le plan de l'app l'emporte sur le titre et les heures ; alertes, lieu et délai de route faits à la main dans Calendrier sont conservés.
- Tests : `tests/test_raccourcis.py` (19 vérifications : ids, unicité, non-inclusion, stabilité après changement de titre et d'heure, envoi vide).

## 47. Nom d'un passage (0.30.0)

- Un passage (entrée de `segs` de `cid` vide) peut porter `name` : texte libre facultatif, `cleanPassName` (espaces superposés réduits, 60 caractères). `cleanSegs` le conserve pour les passages seulement (pas pour une sous-activité). Champ additif : pas de changement de version des jours.
- Saisie : champ `[data-passname]` « Dossier (facultatif) » sous « ▶ Démarrer » dans « Sans heure » ; la valeur vit dans `passDraft[clé]` (elle survit aux réaffichages de la page) et est consommée par `startNow`. Correction après coup : champ `[data-seg-name]` de chaque passage dans le panneau du bloc (vide = nom retiré).
- Affichage : barre « en cours », libellé de la frise (`Tâche · Nom`). Calendrier : titre `Tâche · Nom` (modes plan et réel) ; l'`id` envoyé à Raccourcis (§46) ne contient jamais le nom. Stats : le nom joue le rôle de la sous-activité (`child`) ; le temps sans nom tombe dans « Sans détail ».
- Choix assumé : pas de suggestions, pas de fusion au-delà des espaces (la casse compte) ; l'utilisateur y met un identifiant d'entreprise. Le nom part dans le titre Calendrier et dans les exports de sauvegarde : rien de réel dans le dépôt public (noms inventés dans les tests et la doc).
- Tests : `tests/test_noms_passages.py` (17 vérifications).

## 48. Temps restant avant le coucher et rafraîchissement du Récap (0.31.0)

- Ligne « maintenant » de la frise : `<em>` « X avant le coucher » (`formatDuration(bedtime − maintenant)`), seulement si le coucher du profil n'est pas libre et pas dépassé. L'heure reste dans le `<span>` (les tests la lisent là).
- `refreshRecapNow` (Récap de la journée courante en semaine réelle, minute différente de `recapNowShown`) est appelée par la minuterie de 15 s, à l'ouverture de l'onglet Récap (`switchTab`), au retour dans l'app (`visibilitychange`) et à `pageshow` : une app mise en veille rattrape l'heure tout de suite.
- Tests : `tests/test_temps_restant.py` ; l'heure qui passe sans minuterie se simule avec `page.clock.set_system_time`.

## 49. App vierge dès le premier lancement (0.31.1)

- Décision de l'utilisateur (3 novembre 2026) : aucune valeur de départ ; il règle tout lui-même. `loadSettings` renvoie `blankSettings()` (§33 réinitialisation) quand rien n'est enregistré (`status: 'empty'`), quand le stockage est illisible (`'corrupt'`) ou indisponible (`'unavailable'`). Rien n'est enregistré tant qu'il n'appuie pas sur « Enregistrer ».
- Messages : bandeaux « App vierge : … » (Récap, page du jour) ; pour des données illisibles, « une app vierge est affichée ».
- **Inchangé** : la migration de réglages anciens (versions 1 et 2) et la lecture d'exports sans catégories gardent `defaultSettings()` (l'iPad contient d'anciennes données). `defaultSettings()` reste exposée par `window.PDJ` : les tests s'en servent comme fixture (`seed_defaults` dans `tests/test_calendrier.py`). Ne pas la ressusciter comme valeur de démarrage.
- Les valeurs d'origine citées dans `STATUS.md` (« Décisions prises ») sont historiques.
- Tests : `tests/test_calendrier.py` (premier lancement vierge, réglages illisibles).

## 50. Départ et retour de chez soi, lignes de repère (0.32.0)

- Champ additif par jour : `trip: { leave, home }` (minutes ou `null`), `null` si rien n'est renseigné ; `cleanTrip` écarte un retour qui n'est pas après le départ. Pas de changement de version des jours.
- Saisie : carte repliable `card-trip` « Départ et retour » (fermée au départ, état `tripOpen` en mémoire). Boutons `trip-leave` « Je pars de chez moi » et `trip-home` « Je rentre chez moi » seulement pour **aujourd'hui** (heure du moment, `dayNow`) ; un bouton disparaît quand son heure est prise. Champs `[data-trip=leave|home]` pour corriger ou saisir un autre jour ; vide = retire l'heure ; une heure invalide ou un retour avant le départ est refusé avec un message, sans rien changer. **Nom des boutons** : « Je pars » seul reste le départ du **travail** de la carte Présence (§ 0.14.0).
- Lignes : `dayMarks(day)` = départ de chez soi, arrivée au travail, début de chaque pause, fin de chaque pause (si terminée), départ du travail (si terminé), retour chez soi, triées. **Seulement des heures réellement enregistrées** : aucune ligne prévue, aucun champ dans les profils.
- Frise : lignes `.marker.mk-day` (même style que Lever et Coucher) ; la plage de la frise (`lo`, `hi`) s'étend aux lignes ; deux libellés à moins de ~10 minutes sont décalés vers le bas (15 px par libellé) pour rester lisibles. Récap : entrées `li.mark` de la semaine **réelle** seulement (rien en semaine type) ; elles comptent dans la plage de la ligne « maintenant ».
- Pas d'export Calendrier ni d'envoi vers Raccourcis pour ces lignes (décision de l'utilisateur). Aucun effet sur le calcul de la journée, la présence nette ou les Stats.
- Tests : `tests/test_reperes.py` (33 vérifications).

## 51. Écarts entre blocs et lignes de repère (0.32.1)

- Règle de l'utilisateur : on voit **systématiquement** le temps entre deux éléments qui se suivent, qu'ils soient blocs ou lignes de repère (bloc–bloc, trait–bloc, bloc–trait, trait–trait). Toute nouvelle ligne de repère doit entrer dans ce calcul : l'ajouter à `dayMarks`, jamais la dessiner à part.
- `buildDay` : `sweep` = blocs (`spans`) + repères (`dayMarks`, instants de durée nulle) triés ; un écart apparaît quand un élément commence après la fin de tout ce qui précède (`prevEnd`). Un repère dans un bloc ne crée pas d'écart. Un repère ne compte jamais pour les alertes de chevauchement ni pour « les blocs vont après le coucher » (`blocksEnd`).
- Pause : pour chaque pause **terminée** de la présence, les écarts compris entre son début et sa fin reçoivent `pause: true` ; ils s'affichent grisés, « 45 min de pause » sur la frise (`.gap.pause`) et « pause » dans le Récap (`li.gapli.pausegap`), et ne sont plus du temps « disponible ». Une pause en cours n'est pas grisée.
- Semaine type du Récap : aucun repère (rien n'est prévu), écarts entre blocs seulement.
- Tests : `tests/test_reperes.py` (`test_ecarts`).
- Libellés (0.32.2) : un bloc est dessiné sur 22 px au moins ; le libellé d'un repère dont le trait tombe dans cette hauteur est décalé sous le bloc (`off` dans la boucle des repères de la frise).
