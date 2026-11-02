# CARNET DE BORD — Plan du jour

Journal daté de toutes les opérations sur le projet, pour savoir où il en est et le reprendre. Les entrées du 31 octobre au 2 novembre 2026 sont reconstituées à partir de l'historique des commits (39 commits) ; les entrées suivantes sont écrites au fil des sessions.

Voir aussi : [STATUS.md](STATUS.md) (état par lot), [ARCHITECTURE.md](ARCHITECTURE.md), [CONVENTIONS.md](CONVENTIONS.md).

## Où en est le projet (2 novembre 2026)

- Version **0.23.0**, poussée sur GitHub Pages (à valider sur appareil). Données de l'iPhone réinitialisées par l'utilisateur : base saine. L'iPad n'a pas été touché (anciennes données, sans effet : les champs retirés ne sont plus recopiés au chargement et rien n'est exporté sans la case `toCal`, d'après la lecture du code).
- Calendrier : export seul, par case à cocher ; plus d'import. À tester : un bloc coché exporté en `.ics` vers le calendrier « Plan du jour » (ajout dans Calendrier), après suppression des anciens `.ics`.
- Regroupements par catégorie en menus repliables, fermés au départ (0.21.0) : page du jour (« Sans heure »), Réglages (Activités, Tâches habituelles). À valider sur appareil.
- Sous-activités cochables (0.22.0) : case « fait » par sous-activité et par jour, cochée d'office à l'arrêt du chrono ou à la saisie d'un temps, progression « n/m » dans « Sans heure ». À valider sur appareil.
- Catégories en arbre (0.23.0) : un seul parent, jusqu'à 8 niveaux, chemin « A › B » affiché. Prochain lot : 0.24.0, Stats en arbre avec un total par niveau.
- Livré : lots 1 à 9 et leurs correctifs (voir détail ci-dessous). Presque tout reste **à valider sur appareil** (iPhone, iPad).
- En suspens : lot 5 bis (chrono sur chaque sous-tâche libre du jour). Les sous-activités cochables couvrent le besoin ; abandon à confirmer avec l'utilisateur.
- Non décidé : retirer du suivi git les `.pyc` de `tests/__pycache__/` et ajouter un `.gitignore` (question posée, pas de réponse). D'ici là, lancer les tests avec `PYTHONDONTWRITEBYTECODE=1`.

## 2 novembre 2026

### Session de la 0.23.0 (catégories en arbre)
- Décisions : licence « Tous droits réservés » ajoutée à tous les dépôts publics (pas de dépôt privé payant : le site Pages reste public de toute façon) ; lot 5 bis abandonné ; canaux de réception = sous-activités de « Traitement des dossiers » ; `.pyc` retirés du suivi, `.gitignore` ajouté ; le message « dépôt déplacé » vient seulement de la casse de l'adresse (le dépôt n'a pas été renommé).
- **0.23.0** : `parent` sur les catégories (`catPath`, `fixParents`, `sortCats`, `parentOptionsHtml`), liste « Dans » dans Réglages, chemin affiché partout. Simplification par rapport au plan : les catégories servent de nœuds, pas de table séparée, pas de racines imposées. `tests/test_arborescence.py` (13 vérifications), contrôle négatif fait ; 110 vérifications OK.

### Session de la 0.22.0 (sous-activités cochables)
- Besoin exprimé : des tâches quotidiennes à la fois cochées et chronométrées. Confusion levée entre sous-activité (permanente, chronométrée, dans les Stats) et sous-tâche libre (propre au jour, sans temps).
- **0.22.0** : champ additif `kidsDone` par jour ; `markKidDone` appelé par `closeRunning`, `stopNow` et `addSeg` ; `kidsProgress` / `kidRowHtml` ; cases dans « Sans heure » et dans le panneau du bloc ; jours passés avec cases sans chrono. `tests/test_cochables.py` (23 vérifications), contrôle négatif fait ; au total 97 vérifications OK.
- Décisions de conception pour la suite : arborescence à plusieurs niveaux, table unique à parent unique (pas de multi-parents : double comptage), profondeur modulable (plafond 8), temps compté au niveau le plus fin avec totaux à chaque niveau, trajets en groupe distinct pour délimiter les blocs flottants.
- Choix volontaire : le détail de l'organisation réelle de l'utilisateur n'est pas consigné ici (dépôt public).
- Questions ouvertes : abandon du lot 5 bis ; `.gitignore` pour les `.pyc` ; message « dépôt déplacé » au push ; validation sur appareil de l'export et des versions 0.21.0 et 0.22.0.

### Session de la 0.21.0 (regroupements repliables)
- Reprise : dépôt cloné à `2d78de2` (0.20.0), tests relus et relancés (48 vérifications OK).
- Constats : ligne 3 de `STATUS.md` périmée (0.17.1) et dupliquée, corrigée ; `README.md` des tests citait un fichier inexistant (`test_calendrier (export).py`) et l'import supprimé en 0.20.0, corrigé ; `.pyc` suivis par git dans `tests/__pycache__/` (le dépôt les modifie à chaque lancement de test).
- Retours de l'utilisateur : « tout cocher / tout décocher » refusé (aucun intérêt avec les cases) ; l'iPad n'a pas été réinitialisé ; le lot 5 bis est voulu : un chrono par sous-tâche, apparaissant dans les Stats. Constat vérifié dans le code : les **sous-activités** (Réglages, `segs` avec `cid`) sont chronométrées et dans les Stats, pas les **sous-tâches** du jour (`subtasks`, sans champ de temps).
- Demande prioritaire, avant le lot 5 bis : catégories en menus déroulants dans « Sans heure » (page du jour) et dans tous les regroupements de Réglages. Décisions : tout fermé au départ (« pour libérer la vision globale »), seuls Activités et Tâches habituelles ont des regroupements dans Réglages, ordre de Réglages dans « Sans heure ».
- **0.21.0** : `catBuckets` / `grpHtml` (menus `details.grp`), `sansCatOpen`, ouverture de « Sans catégorie » à l'ajout, suppression du groupe vide, compteurs, ouverture sur erreur de saisie. `tests/test_regroupements.py` (26 vérifications) ; contrôle négatif fait (le test échoue sur l'ancien code) ; captures vérifiées sur écran d'iPhone (390 px). Au total 74 vérifications OK.
- Questions ouvertes pour le lot 5 bis : (a) sur quel bloc chronométrer des sous-tâches, et un bloc peut-il avoir sous-activités et sous-tâches ? (b) Stats : cumuler par libellé identique d'un jour à l'autre, ou seulement le détail du jour ? (c) cocher une sous-tâche arrête-t-il son chrono ? Valeurs proposées par défaut : chrono seulement aujourd'hui (saisie à la main les autres jours), un seul chrono à la fois, le temps passé reste sur le jour d'origine lors d'un report.

### Session de reprise (après 0.17.1)
- Dépôt cloné, `STATUS.md`, `CONVENTIONS.md` et `README.md` relus. Versions `index.html` et `sw.js` cohérentes (0.17.1).
- Constats : les fichiers `test_lot*.js` cités dans la documentation ne sont pas dans le dépôt ; la ligne 3 de `STATUS.md` est dupliquée et le tableau des lots s'arrête au lot 4.
- Création de `CARNET.md` (ce fichier) et de `ARCHITECTURE.md`.
- Correction demandée : les rendez-vous importés du calendrier sont réexportés vers le calendrier, et ce que l'app exporte peut être réimporté (deux sens du même problème).
- Décisions de l'utilisateur : case « Vient de mon calendrier » validée ; l'export ira dans un nouveau calendrier dédié « Plan du jour » (à créer sur l'iPhone) que le raccourci d'import ne lira pas ; questions sur les retours de test et le nettoyage de `STATUS.md` abandonnées.
- **0.17.2** : champ `fromCal` sur les blocs ponctuels, posé à l'import, exclu de l'export, case dans l'éditeur du bloc. Vérifié en navigateur automatisé : import marqué, marque conservée après rechargement, export sans les rendez-vous importés, case cochée puis décochée.
- Question posée : un code unique par événement, pour retrouver un rendez-vous malgré un changement d'heure ou de nom. L'utilisateur a envoyé deux captures : Raccourcis ne fournit **aucun identifiant d'événement** (détails disponibles : titre, dates, calendrier, notes, URL, date de création…). Il a aussi envoyé son raccourci « Plan du jour RDV » : recherche des événements des 7 prochains jours, texte `date début / heure début / heure fin / titre`, copie dans le presse-papiers.
- Décisions : principe « code dans les Notes pour ce que l'app exporte, date de création pour ce qui vient du calendrier » à essayer ; dossier `tests/` accepté. L'utilisateur ne connaissait pas les `test_lot*.js` : ils ont sans doute été perdus avec les sessions précédentes.
- **0.18.0** : export avec code dans les Notes et UID stable des blocs ponctuels ; import qui reconnaît par code, puis par date de création (`calKey`, seulement si unique), et met à jour au lieu de dupliquer ; calendrier « Plan du jour » sans code ignoré ; `tests/test_calendrier.py` (33 vérifications, toutes passées).
- À faire par l'utilisateur : modifier le raccourci (calendrier, date de création `yyyyMMddHHmmss`, notes) et vérifier sur l'iPhone que la date de création est renseignée et stable.

### Commits du jour
- **0.21.0** : regroupements par catégorie en menus repliables (voir la session ci-dessus).
- **0.20.0** : décisions de l'utilisateur après la 0.19.1 : « on n'importe plus, on exporte juste », case à cocher plutôt que filtre par rappel, réinitialisation faite donc base saine. Import retiré, `noCal` remplacé par `toCal`, tests réécrits (48 vérifications).
- **0.19.1** : l'utilisateur décide de se servir de l'app comme outil principal et de n'exporter que les tâches pour lesquelles il veut un rappel. L'export ne garde que les blocs avec « Rappel dans Calendrier ». Tests : 69 vérifications (37 + 10 + 22) passées. Questions calendrier précédentes (message après export, Notes de l'aperçu, titres ignorés, trains en double, correction du raccourci) : suspendues, l'import n'étant plus au centre.
- `48a12bd` **0.19.0** : réinitialisation à la place de « Rétablir les valeurs de départ ». Décisions de l'utilisateur : les deux modes (tout / jours seulement), réglages **vierges**, **pas de copie de sécurité**, confirmation (interprétée comme renforcée : taper EFFACER). `tests/test_reinitialisation.py`, 22 vérifications ; les trois fichiers de tests (65 vérifications) passent.
- `7316164` **0.18.1** : toutes les cartes repliables fermées au départ (Présence au travail, Sans heure devenue repliable avec son compteur, Revue du jour même pour un jour passé). `tests/test_pliage.py`, 10 vérifications.
- `ff029ae` **0.18.0** : codes d'événements et mise à jour à l'import (voir ci-dessus).
- `8875ba4` **0.17.2** : rendez-vous importés marqués et jamais réexportés.
- `f1715cf` Documentation : carnet de bord et architecture du projet.
- `94d6e2b` **0.14.0** : présence au travail (chrono parallèle, pauses, départ conseillé).
- `26dd854` **0.14.1** : Récap en semaine réelle ou semaine type.
- `0f417d1` **0.15.0** : tâches habituelles (modèles de blocs ponctuels).
- `2d03a9f` **0.15.1** : recherche de tâche et option « à confirmer » dans les modèles.
- `268652d` **0.15.2** : une activité sans heure à sous-activités reste proposée après une sous-activité terminée.
- `9fa9aa7` **0.15.3** : tâches habituelles repliables et triées par catégorie puis nom.
- `8b120b3` **0.15.4** : tri des catégories et des activités dans Réglages.
- `475a7c3` **0.15.5** : un créneau par sous-activité dans la frise, plus de fausse alerte de chevauchement.
- `e77c7a2` **0.16.0** : Récap par sous-tâche, présence et blocs à heure fixe passés dans les stats.
- `18f06ac` **0.16.1** : la présence compte dans le Travail des stats (décompte 7 h 42).
- `fe17c60` **0.17.0** : le temps de travail des stats est la présence seule (badgeuse).
- `2970b10` **0.17.1** : Récap sans carte « Sans heure » en semaine réelle.

## 1er novembre 2026

- `3e2bcde` **Lot 3 ter** : profils de journée (lever, coucher, jours, activités retirées).
- `ad90fd4` Réglages : cartes, profils et activités repliables.
- `ce1c6fe` **Lot 4** : export, import, statistiques (onglet Stats).
- `6b1504d` Relance du déploiement GitHub Pages (deux déploiements s'étaient chevauchés).
- `fd436d0` **Lot 4 bis** : lever et coucher libres, profils Vendredi / Samedi / Dimanche, Congé avec période.
- `7412c45` **0.8.1** : indicateur ▾ / ▴ sur les lignes repliables.
- `daead8c` **0.9.0** : congés en section séparée des profils, périodes multiples, migration.
- `69ee26a` **0.9.1** : détente retirée (réglage, encart, alerte).
- `6aa08c6` **0.9.2** : durée entre parenthèses à côté des heures.
- `5bec6b7` **0.9.3** : Récapitulatif, durée après le nom, heures lisibles.
- `e16bdbf` **0.10.0** : « sans heure », durée supprimée.
- `8182f1a` **Lot 5 / 0.11.0** : sous-activités chronométrées et Stats détaillées.
- `d869c43` **0.11.1** : cartes de Réglages repliées au départ.
- `d1113ad` **0.11.2** : sous-activités visibles dans « Sans heure » et hors aujourd'hui.
- `52ae393` **Lot 6 / 0.12.0** : catégories, suivi du temps de travail, boutons de sous-activités.
- `fa0f639` **0.12.1** : travail pendant un trajet, activités en parallèle sans alerte.
- `004d4ed` **0.12.2** : Stats, vue journalière.
- `8e6957a` **Lot 7 / 0.13.0** : export `.ics` vers Calendrier et import de rendez-vous.
- `5ce71e1` **0.13.1** : trajets non exportés, titres ignorés à l'import.
- `03c9489` **0.13.2** : rappels par activité à l'export Calendrier (VALARM).
- `9e1dd73` **0.13.3** : export Calendrier limité aux jours suivants, sans choix plan / réel.

## 31 octobre 2026

- `76621c0` Initial commit.
- `8703567` **Lot 1** : saisie et stockage des contraintes.
- `d54d57a` **Lot 2** : plan du jour et recalage autour des rendez-vous.
- `b90bfb3` **Lot 2 bis** : modèle unique d'activités, chrono et glissement.
- `f40a66f` **Lot 3** : sous-tâches, blocs à confirmer et détente permanente.
- `126d404` **Lot 3 bis** : reporter ce qui n'a pas été fait (revue du jour).

## Règle de tenue

À chaque session : ajouter une entrée datée en haut de ce fichier (ce qui a été fait, constats, décisions, questions ouvertes), mettre à jour « Où en est le projet », et relier le commit correspondant. `STATUS.md` reste l'état par lot ; ce carnet est le journal chronologique.
