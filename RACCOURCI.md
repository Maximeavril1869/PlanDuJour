# Raccourci iOS « Plan du jour » (0.29.0)

Le bouton « Envoyer vers Raccourcis » (Réglages › Calendrier) copie dans le presse-papiers un texte JSON, puis ouvre le lien
`shortcuts://run-shortcut?name=Plan%20du%20jour&input=clipboard`. Depuis la 0.29.0 le raccourci **met à jour** les événements (retrouvés par leur `id` dans les Notes) ou les crée ; il **ne supprime plus rien**.

**Agenda cible : « Travail »** (décision de l'utilisateur, 3 novembre 2026 : il n'y a plus d'agenda séparé « Plan du jour » pour les exports). Le même agenda dans « Rechercher » et dans « Ajouter ».

## Texte envoyé

```json
{"from":"2026-11-03T00:00:00","to":"2026-11-03T23:59:00","events":[{"id":"[PDJ-p-p1]","title":"Réunion test","start":"2026-11-03T09:10:00","end":"2026-11-03T09:50:00"}]}
```

Heures locales, sans fuseau. `id` = code stable de l'événement, déjà entouré de crochets : à écrire tel quel dans les Notes et à chercher avec « Notes contient » (les crochets évitent qu'un id soit trouvé dans un autre). L'app n'ouvre pas le raccourci si rien n'est coché.

## Construction du raccourci (app Raccourcis, en français)

Nom du raccourci : `Plan du jour` (exactement). Les libellés ci-dessous sont ceux de l'app ; chercher l'action par son nom dans la recherche d'actions. Construit et utilisé sur iPhone le 3 novembre 2026 (l'utilisateur confirme que « tout fonctionne » ; voir plus bas ce qui reste à confirmer).

Avant la boucle (validé en 0.28.0) :
1. **Obtenir le presse-papiers** (pendant les essais : une action « Texte » contenant le JSON de test) → **Obtenir le dictionnaire** → **Définir la variable** `Données`.
2. **Obtenir la valeur du dictionnaire** (clé `from`, dans `Données`) → **Obtenir les dates de** → **Définir la variable** `Début période` sur « Dates ».
3. Idem avec la clé `to` → variable `Fin période` (**chaque bloc a sa propre action « Obtenir les dates de »**).
4. **Obtenir la valeur du dictionnaire** (clé `events`, dans `Données`).

La boucle : **Répéter avec chaque élément** (dans la valeur du dictionnaire de l'étape 4) :
1. **Définir la variable** `Élément` sur « Élément de répétition ».
2. Clé `title` dans `Élément` → **Définir la variable** `Titre`.
3. Clé `start` dans `Élément` → **Obtenir les dates de** → **Définir la variable** `Début`.
4. Clé `end` dans `Élément` → **Obtenir les dates de** → **Définir la variable** `Fin`.
5. Clé `id` dans `Élément` → **Définir la variable** `Id`.
6. **Rechercher des événements de calendrier**, « l'ensemble des éléments suivants sont vrais » : Calendrier est **Travail** ; Notes **contient** `Id` ; (la date de début est entre `Début période` et `Fin période` : voir « Limites »).
7. **Si** « Évènements du calendrier » **possède n'importe quelle valeur** :
   - **Régler** Titre de « Évènements du calendrier » sur `Titre` ;
   - **Régler** La date de début de « Évènements du calendrier » sur `Début` ;
   - **Régler** Date de fin de « Évènements du calendrier » sur `Fin`.
8. **Sinon** : **Ajouter un nouvel événement** : titre `Titre`, début `Début`, fin `Fin`, Position vide, Calendrier **Travail**, Toute la journée non coché, Alerte **à l'heure de l'événement**, Notes = `Id`.
9. **Terminer si**, **Fin de la répétition**.

Après la boucle, l'utilisateur a mis **Ouvrir Calendrier**.

### Pièges

- **Après un « Définir la variable », l'action suivante ne reprend plus le dictionnaire par défaut** : dans chaque action « Obtenir la valeur du dictionnaire », toucher le champ du dictionnaire et choisir la variable à la main (`Données`, ou `Élément` dans la boucle).
- **Une action « Obtenir les dates de » par bloc** : le bloc Fin lisait par erreur celle du bloc Début.
- Dans « Régler », l'entrée doit être le **résultat de la recherche** (« Évènements du calendrier »), choisi à la main ; une action « Régler » par propriété.
- **Le calendrier du filtre de « Rechercher » et celui de « Ajouter » doivent être le même** : sinon la recherche ne trouve rien et chaque envoi recrée tout.
- **Ne jamais remettre une action « Supprimer les événements » sur Travail** : elle effacerait tous les rendez-vous de la période, pas seulement ceux de l'app. (La 0.28.0 supprimait puis recréait dans un agenda dédié ; la 0.29.0 n'en a plus besoin.)

## Limites

- Pas de rappel différent par bloc : un rappel fixe, à l'heure de l'événement.
- Le plan de l'app l'emporte sur le titre et les heures : un titre ou une heure changé à la main dans Calendrier est remis comme dans l'app au prochain envoi. Alertes, lieu et délai de route faits à la main sont conservés (à confirmer sur appareil).
- Un bloc retiré du plan **reste** dans Calendrier ; la détection et une notification sont prévues dans une version suivante.
- Le filtre « date de début entre `Début période` et `Fin période` » limite la recherche à la période envoyée : un bloc ponctuel déplacé **hors** de cette période serait recréé au lieu d'être mis à jour (l'id ne contient pas le jour). Retirer ce filtre le retrouverait partout (décision à prendre).
- Les événements créés avec la 0.28.0 n'ont pas d'id dans les Notes : ils ne sont jamais retrouvés. Les supprimer à la main (ils sont dans l'ancien agenda « Plan du jour »).
- Le lien `shortcuts://` depuis l'app installée sur l'écran d'accueil lance le raccourci tout seul, mais iOS demande une **confirmation à chaque fois** (confirmation système, à ne pas supposer supprimable).

## À confirmer sur appareil

- Un second envoi après changement d'heure ou de titre dans l'app met l'événement à jour sans doublon.
- Une alerte, un lieu ou un délai de route réglé à la main dans Calendrier survit à l'envoi suivant.
- Le bloc ponctuel déplacé d'un jour à l'autre (voir Limites).
