# Raccourci iOS « Plan du jour » (0.28.0)

Le bouton « Envoyer vers Raccourcis » (Réglages › Calendrier) copie dans le presse-papiers un texte JSON, puis ouvre le lien
`shortcuts://run-shortcut?name=Plan%20du%20jour&input=clipboard`. Le raccourci vide l'agenda « Plan du jour » sur la période, puis recrée les événements.

## Texte envoyé

```json
{"from":"2026-11-03T00:00:00","to":"2026-11-03T23:59:00","events":[{"title":"Réunion test","start":"2026-11-03T09:10:00","end":"2026-11-03T09:50:00"}]}
```

Heures locales, sans fuseau. `events` peut être vide : le raccourci vide alors seulement la période.

## Construction du raccourci (à faire une fois, dans l'app Raccourcis)

Nom du raccourci : `Plan du jour` (exactement). L'agenda « Plan du jour » doit exister dans Calendrier. Les libellés ci-dessous sont indicatifs : chercher l'action par son nom dans la recherche d'actions.

1. **Obtenir le presse-papiers**
2. **Obtenir le dictionnaire à partir de l'entrée** (entrée : Presse-papiers)
3. **Obtenir la valeur du dictionnaire** : clé `from` du Dictionnaire, puis **Obtenir des dates à partir de l'entrée**, puis **Définir la variable** `debutPeriode`
4. Idem avec la clé `to`, variable `finPeriode`
5. **Rechercher des événements de calendrier** : Calendrier = « Plan du jour » ; Date de début est entre `debutPeriode` et `finPeriode`
6. **Supprimer les événements** (entrée : les événements trouvés)
7. **Obtenir la valeur du dictionnaire** : clé `events` du Dictionnaire
8. **Répéter avec chaque élément** (de la liste obtenue à l'étape 7), et dedans :
   1. Obtenir la valeur du dictionnaire : clé `title` de l'Élément répété, puis Définir la variable `titre`
   2. Obtenir la valeur du dictionnaire : clé `start` de l'Élément répété, puis Obtenir des dates à partir de l'entrée, puis Définir la variable `debut`
   3. Idem avec la clé `end`, variable `fin`
   4. **Ajouter un nouvel événement** : titre = `titre`, début = `debut`, fin = `fin`, calendrier = « Plan du jour », alerte = à l'heure de l'événement
9. (facultatif) **Afficher la notification** « Calendrier à jour »

## Limites

- Pas de rappel différent par bloc : un rappel fixe, à l'heure de l'événement.
- Un événement ajouté à la main dans l'agenda « Plan du jour » sur la période est supprimé à l'envoi suivant : y réserver les événements de l'app.
- Le fonctionnement du lien `shortcuts://` depuis l'app installée sur l'écran d'accueil est à confirmer sur appareil ; sinon lancer le raccourci à la main (il lit le presse-papiers).
