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
