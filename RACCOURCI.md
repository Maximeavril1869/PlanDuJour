# Raccourci iOS « Plan du jour » (0.29.0)

Le bouton « Envoyer vers Raccourcis » (Réglages › Calendrier) copie dans le presse-papiers un texte JSON, puis ouvre le lien
`shortcuts://run-shortcut?name=Plan%20du%20jour&input=clipboard`. Depuis la 0.29.0 le raccourci **met à jour** les événements de l'agenda « Plan du jour » (retrouvés par leur `id` dans les Notes) ou les crée ; il ne supprime plus rien.

## Texte envoyé

```json
{"from":"2026-11-03T00:00:00","to":"2026-11-03T23:59:00","events":[{"id":"[PDJ-p-p1]","title":"Réunion test","start":"2026-11-03T09:10:00","end":"2026-11-03T09:50:00"}]}
```

Heures locales, sans fuseau. `id` = code stable de l'événement, déjà entouré de crochets : à écrire tel quel dans les Notes et à chercher avec « Notes contient » (les crochets évitent qu'un id soit trouvé dans un autre). L'app n'ouvre pas le raccourci si rien n'est coché.

## Construction du raccourci (à faire une fois, dans l'app Raccourcis, en français)

Nom du raccourci : `Plan du jour` (exactement). L'agenda « Plan du jour » doit exister dans Calendrier. Les libellés ci-dessous sont ceux de l'app en français ; chercher l'action par son nom dans la recherche d'actions.

Procédure **validée de bout en bout sur iPhone** avec le JSON de test (action « Texte » contenant le JSON de test, à la place du presse-papiers) :

1. **Texte** (le JSON) → **Obtenir le dictionnaire** → **Définir la variable** `Données`.
2. Bloc **Début période** : **Obtenir la valeur pour la clé** `from` dans `Données` → **Obtenir les dates de** → **Définir la variable** `Début période` sur « Dates ».
3. Bloc **Fin période** : idem avec la clé `to`, variable `Fin période`. **Chaque bloc a sa propre action « Obtenir les dates de »**.
4. **Rechercher des événements de calendrier** : Calendrier = « Plan du jour » ; Date de début est entre `Début période` et `Fin période` → **Supprimer les événements**.
5. **Obtenir la valeur pour la clé** `events` dans `Données` → **Répéter avec chaque élément** → **Définir la variable** `element` ; dedans, lire `title`, `start` et `end` dans `element` (dates converties pour `start` et `end`) → **Ajouter un nouvel événement** dans « Plan du jour », alerte à l'heure de l'événement.

Pour l'usage réel, l'entrée du raccourci est le presse-papiers (`input=clipboard`) : remplacer l'action « Texte » par **Obtenir le presse-papiers**. Cette variante avec le vrai envoi depuis l'app n'a pas encore été confirmée sur appareil.

### Vérifié sur appareil (JSON de test)

- Les dates ISO sont lues sans décalage (Début 00:00, Fin 23:59).
- L'événement de test « Test suppression » est supprimé ; les événements recréés ont les bonnes heures.
- Pas de doublon au second lancement ; aucune demande d'autorisation Calendrier.

## Version 0.29.0 : mise à jour au lieu de recréer (à construire et à valider sur appareil)

Les étapes 1 à 3 (Données, Début période, Fin période) restent identiques. Le reste change :

1. **Migration, une seule fois** : les événements créés avant la 0.29.0 n'ont pas d'id ; au premier envoi ils feraient doublon. Garder l'étape « Rechercher… puis Supprimer les événements » de la 0.28.0 pour ce premier envoi, puis la retirer (ou supprimer à la main les événements de la période dans Calendrier).
2. **Répéter avec chaque élément** de `events` → **Définir la variable** `element` → lire `id`, `title`, `start`, `end` dans `element` (dates converties pour `start` et `end`).
3. **Rechercher des événements de calendrier** : Calendrier = « Plan du jour » ; **Notes contient** `id` (filtres Notes disponibles : se termine par, commence par, ne contient pas, contient, n'est pas, est).
4. **Si** le résultat a une valeur : **Régler les détails des événements de calendrier** (titre, début, fin) ; **Sinon** : **Ajouter un nouvel événement** (titre, début, fin, calendrier « Plan du jour », **Notes = `id`**, alerte à l'heure de l'événement).
5. (facultatif) **Afficher la notification** « Calendrier à jour ».

Réglages exacts de « Régler les détails des événements de calendrier » : **à relever sur l'appareil**, puis à consigner ici.

## Pièges

- **Après un « Définir la variable », l'action suivante ne reprend plus le dictionnaire par défaut** : dans chaque action « Obtenir la valeur pour la clé », toucher le champ du dictionnaire et choisir la variable à la main (`Données`, ou `element` dans la boucle).
- **Une action « Obtenir les dates de » par bloc** : le bloc Fin lisait par erreur celle du bloc Début. Vérifier que chaque bloc a la sienne.

## Limites

- Pas de rappel différent par bloc : un rappel fixe, à l'heure de l'événement.
- 0.28.0 (« supprimer puis recréer ») effaçait à chaque envoi les réglages faits à la main dans Calendrier (alertes, lieu, délai de route…) : corrigé par la 0.29.0, qui conserve ces réglages mais remet titre et heures comme dans l'app.
- Un bloc retiré du plan **reste** dans Calendrier (la détection et une notification sont prévues dans une version suivante).
- Le lien `shortcuts://` depuis l'app installée sur l'écran d'accueil lance le raccourci tout seul, mais iOS demande une **confirmation à chaque fois** (confirmation système, à ne pas supposer supprimable).
