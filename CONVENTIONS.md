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

## 13. Ajouts du lot 2 (rien de ce qui précède n'est modifié)

- **Section `5B. PLANNING`** : fonctions pures `buildPlan(réglages, jours, date)`, `layoutColumns`, calculs de dates. Elles ne touchent ni le DOM ni le stockage.
- **Jours** : clé `plandujour.jours`, objet versionné `{ version: 1, days: { "AAAA-MM-JJ": { arrival, departure, appointments, done } } }`. Les jours de plus de 90 jours sont purgés à l'enregistrement. Si les données sont illisibles, une copie brute est gardée sous `plandujour.jours.sauvegarde`.
- **Enregistrement immédiat** pour les données du jour (rendez-vous, heures réelles, cases cochées) : pas de bouton « Enregistrer ». Le principe « Enregistrer » du §9 reste réservé aux réglages.
- **Réglages en version 2** : ajout de `mobileBlocks`. La version 1 est migrée à la lecture (concentration par défaut ajoutée) et réécrite en version 2 au prochain enregistrement.
- **Zones** : `morning` (lever → départ de chez soi), `work` (arrivée → départ du travail), `evening` (retour à la maison → coucher). Un bloc mobile se place dans la première plage libre de sa zone assez longue, par priorité croissante (1 = d'abord), à égalité dans l'ordre de saisie. Le saxophone a la priorité 2 et le ménage la priorité 3, tous deux le soir.
- **Heure réelle absente** : le plan prend le cas prudent (arrivée la plus tardive de la fourchette, départ le plus précoce) et le dit à l'écran. La fourchette n'est jamais modifiée.
- **Ménage** : dû si jamais fait, ou si le dernier ménage coché avant ce jour date d'au moins N jours.
- **Rien n'est supprimé** quand un bloc ne tient pas : il est signalé (les propositions de coupe viennent au lot 3).
- **Point d'accès pour les tests** : `window.PDJ` expose `buildPlan` et quelques utilitaires.
