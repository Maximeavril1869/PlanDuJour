# Raccourci iOS « Plan du jour » (0.28.0)

Le bouton « Envoyer vers Raccourcis » (Réglages › Calendrier) copie dans le presse-papiers un texte JSON, puis ouvre le lien
`shortcuts://run-shortcut?name=Plan%20du%20jour&input=clipboard`. Le raccourci vide l'agenda « Plan du jour » sur la période, puis recrée les événements.

## Texte envoyé

```json
{"from":"2026-11-03T00:00:00","to":"2026-11-03T23:59:00","events":[{"title":"Réunion test","start":"2026-11-03T09:10:00","end":"2026-11-03T09:50:00"}]}
```

Heures locales, sans fuseau. `events` peut être vide : le raccourci vide alors seulement la période.

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

## Pièges

- **Après un « Définir la variable », l'action suivante ne reprend plus le dictionnaire par défaut** : dans chaque action « Obtenir la valeur pour la clé », toucher le champ du dictionnaire et choisir la variable à la main (`Données`, ou `element` dans la boucle).
- **Une action « Obtenir les dates de » par bloc** : le bloc Fin lisait par erreur celle du bloc Début. Vérifier que chaque bloc a la sienne.

## Limites

- Pas de rappel différent par bloc : un rappel fixe, à l'heure de l'événement.
- « Supprimer puis recréer » efface à chaque envoi les réglages faits à la main dans Calendrier (alertes, lieu, délai de route…) et tout événement ajouté à la main dans l'agenda « Plan du jour » sur la période. Piste : 0.29.0 (identifiant stable par événement, mise à jour au lieu de recréer).
- Le lien `shortcuts://` depuis l'app installée sur l'écran d'accueil lance le raccourci tout seul, mais iOS demande une **confirmation à chaque fois** (confirmation système, à ne pas supposer supprimable).
