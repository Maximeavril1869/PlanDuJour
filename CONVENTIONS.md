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
- **Temps disponible** : écart entre deux blocs consécutifs, du lever au premier bloc, et du dernier bloc au coucher (comparé à la détente minimale `relaxFloor`). Affiché dans le Récapitulatif et sur la page du jour.
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
