# CARNET DE BORD — Plan du jour

Journal daté de toutes les opérations sur le projet, pour savoir où il en est et le reprendre. Les entrées du 31 octobre au 2 novembre 2026 sont reconstituées à partir de l'historique des commits (39 commits) ; les entrées suivantes sont écrites au fil des sessions.

Voir aussi : [STATUS.md](STATUS.md) (état par lot), [ARCHITECTURE.md](ARCHITECTURE.md), [CONVENTIONS.md](CONVENTIONS.md).

## Où en est le projet (3 novembre 2026)

- Version **0.32.0**, poussée sur GitHub Pages (à valider sur appareil : 0.30.0, 0.31.0, 0.31.1 et 0.32.0). Raccourci 0.29.0 reconstruit et validé sur iPhone (agenda cible Travail, voir `RACCOURCI.md`). Données de l'iPhone réinitialisées par l'utilisateur : base saine. L'iPad n'a pas été touché (anciennes données, sans effet : les champs retirés ne sont plus recopiés au chargement et rien n'est exporté sans la case `toCal`, d'après la lecture du code).
- Calendrier : export seul, par case à cocher ; plus d'import. À tester : un bloc coché exporté en `.ics` vers le calendrier « Plan du jour » (ajout dans Calendrier), après suppression des anciens `.ics`.
- Regroupements par catégorie en menus repliables, fermés au départ (0.21.0) : page du jour (« Sans heure »), Réglages (Activités, Tâches habituelles). À valider sur appareil.
- Sous-activités cochables (0.22.0) : case « fait » par sous-activité et par jour, cochée d'office à l'arrêt du chrono ou à la saisie d'un temps, progression « n/m » dans « Sans heure ». À valider sur appareil.
- Catégories en arbre (0.23.0) : un seul parent, jusqu'à 8 niveaux, chemin « A › B » affiché.
- Statuts Travail / Perso / Hors (0.23.1) : portés par la racine, hérités par les sous-catégories ; Réglages en trois menus de statut contenant un menu par catégorie, imbriqués. 
- Stats en arbre (0.24.0) : trois menus Travail / Perso / Hors, catégories imbriquées, activités et sous-activités au bout ; un total à chaque niveau ; fermé au départ.
- Rappel de sauvegarde (0.25.0) : bandeau en tête de tous les onglets (0.25.1) après N jours (7 par défaut) de modifications non sauvegardées ; résumé et délai dans Réglages › Sauvegarde ; état propre à l'appareil.
- Stockage persistant (0.25.2) : demandé au démarrage, résultat affiché dans Réglages › Sauvegarde.
- Tâches « sans heure » refaisables plusieurs fois par jour : livré en 0.25.3 (passages). Les sous-tâches libres nomment le travail mais n'ont pas de temps propre (pas de temps par dossier dans les Stats).
- Avant la 1.0 : validation sur iPhone puis iPad (liste de contrôles à fournir). La sauvegarde elle-même existe (Réglages > Sauvegarde : export / import JSON).
- Livré : lots 1 à 9 et leurs correctifs (voir détail ci-dessous). Presque tout reste **à valider sur appareil** (iPhone, iPad).
- Abandonné : lot 5 bis (chrono sur chaque sous-tâche libre du jour), remplacé par les sous-activités cochables.
- Tests : 401 vérifications (17 fichiers). Lancer avec `PYTHONDONTWRITEBYTECODE=1`. `.gitignore` en place, `.pyc` retirés du suivi.

## 3 novembre 2026 (suite)

### Session de reprise après la 0.31.0 (app vierge 0.31.1, lignes de repère 0.32.0)
- Dépôt cloné, docs relues. Versions `index.html` et `sw.js` : 0.31.0, 16 fichiers de tests (suite pas relancée à ce stade).
- Questions posées une à une avant tout code. Réponses : (1) saisie par deux boutons « Je pars » / « Je rentre » sur la page du Jour, heure du moment, correction manuelle possible ; (2) les lignes arrivée, départ et pauses se calculent à partir de la présence au travail existante, sans nouveau bouton ; (3) les valeurs de départ (dont les blocs de trajet) ont été abandonnées : il n'y a pas de trajet par défaut, les lignes s'ajoutent donc sans toucher aux blocs.
- Documentation : `STATUS.md` mis à jour (valeurs de départ abandonnées depuis la 0.19.0, points « à valider » correspondants marqués obsolètes).
- Constat : `defaultSettings()` existait toujours dans le code (premier lancement, migrations). Décision de l'utilisateur : **app vierge** dès le premier lancement (c'est pour cela qu'il avait demandé « Réinitialiser… »), il règle tout lui-même. Une première lecture de ma part (laisser les valeurs) était fausse.
- Réponses suivantes : (4) lignes **seulement réelles** (pas de profil prévu) ; (5) frise **et** Récap comme Lever et Coucher, pas d'export Calendrier ; « on ajuste pour l'avenir » : aucun rattrapage du passé.
- `0eced96` **0.31.1** : app vierge au premier lancement (voir CONVENTIONS §49). Migration d'anciennes données non touchée (iPad). `test_calendrier.py` réécrit pour le premier lancement, `test_temps_restant.py` enregistre les anciennes valeurs en fixture ; contrôle négatif fait ; 368 vérifications.
- **0.32.0** : départ et retour de chez soi (carte « Départ et retour », boutons « Je pars de chez moi » / « Je rentre chez moi », champs de correction) et lignes de repère sur la frise et dans le Récap, à partir des heures réellement enregistrées (départ de chez soi, arrivée, pauses, départ du travail, retour). Nom des boutons précisé « de chez moi » car « Je pars » existe déjà pour le départ du travail (à valider). `tests/test_reperes.py` (33 vérifications), quatre contrôles négatifs faits ; captures iPhone clair et sombre vérifiées ; 401 vérifications.

### Session de la 0.31.0 (temps restant, Récap rattrapé)
- Retours de l'utilisateur : il a quitté le travail et valide les versions demain (rappel demandé) ; le témoin du Récap est resté bloqué à 13 h 52 ; il veut, sur « Jour », le temps restant entre l'heure exacte et le coucher « avec l'heure ».
- Cause probable du Récap : pas de rafraîchissement à l'ouverture de l'onglet ni au retour dans l'app (seule la minuterie de 15 s). Corrigé (`refreshRecapNow`). Le blocage exact vu sur iPhone n'a pas été reproduit : à confirmer.
- `dd8914e` **0.31.0** : étiquette « X avant le coucher » sur la ligne « maintenant » (emplacement choisi sans lui demander : à valider) ; `tests/test_temps_restant.py` (10 vérifications) ; `test_maintenant.py` adapté (heure lue dans le `span`) ; trois contrôles négatifs faits ; 361 vérifications OK ; captures iPhone clair et sombre vérifiées.

### Session de la 0.30.0 (nom d'un passage)
- Réponses de l'utilisateur : nom saisi **à l'activation (▶)** ; pas de suggestions (« beaucoup trop de noms ») ; Stats par nom voulues ; il mettra un identifiant d'entreprise comme nom (aucun faux doublon à craindre) ; les sous-tâches ne servent plus que pour décomposer très finement une tâche (non modifiées). La notion de « passage » lui était floue : expliquée par un exemple (un ▶ puis ■ = un passage) ; confusion levée entre sous-tâche (propre au jour, sans temps), sous-activité (permanente, créée dans Réglages) et passage nommé.
- `1ecc230` **0.30.0** : `cleanPassName`, `cleanSegs` conserve `name`, `passDraft`, champ `[data-passname]`, champ `[data-seg-name]` dans le panneau, libellés (barre, frise, Calendrier), `timeEntries` (le nom comme détail dans les Stats). `tests/test_noms_passages.py` (17 vérifications) ; trois contrôles négatifs faits (le premier, nom non relu au chargement, n'était pas détecté : test renforcé, puis échec attendu) ; 351 vérifications OK ; captures iPhone 390 px clair et sombre vérifiées.
- Point signalé à l'utilisateur : un identifiant d'entreprise dans le titre part dans l'agenda Travail (peut-être synchronisé) et dans les exports de sauvegarde ; à lui de juger au regard du secret professionnel. Rien de réel dans le dépôt public.
- À valider sur appareil : le champ « Dossier » sous « ▶ Démarrer », le nom dans la frise, les Stats par nom, l'événement « Tâche · Nom » via Raccourcis.

### Session de la 0.29.0 (id stable par événement)
- Réponses de l'utilisateur : second envoi avec le vrai envoi de l'app sans doublon (0.28.0 validée) ; « Jour » doit ramener au jour courant mais « pas besoin, il y a déjà Aujourd'hui en haut » (rien à coder) ; aucune note écrite à la main dans l'agenda « Plan du jour » ; filtre Notes du raccourci : se termine par / commence par / ne contient pas / contient / n'est pas / est ; détection des événements disparus du plan : après ; format d'id validé ; migration : il veut être guidé ; **nom par passage : oui, il veut pouvoir détailler** (version à part, questions de conception en suspens).
- `4993d97` **0.29.0** : `shortcutPayload` ajoute `id` = `[` + code de l'export `.ics` + `]` ; `doShortcutSend` n'ouvre plus le raccourci si rien n'est coché ; texte d'aide de Réglages › Calendrier corrigé (ne dit plus que le raccourci vide l'agenda) ; `APP_VERSION` / `VERSION` 0.29.0. `tests/test_raccourcis.py` passe à 19 vérifications ; deux contrôles négatifs faits (crochets retirés : 4 échecs ; rang de passage retiré : 1 échec) ; 334 vérifications OK ; captures iPhone 390 px clair et sombre vérifiées (toast et texte d'aide).
- Décision prise sans question : un envoi sans aucun bloc coché n'ouvre plus le raccourci (il ne vide plus la période, l'ouvrir n'apporterait qu'une confirmation inutile). À défaire si l'utilisateur veut l'ancien comportement.
- Construction du raccourci guidée action par action avec l'utilisateur (captures relues) : variables `Données`, `Début période`, `Fin période`, `Élément`, `Titre`, `Début`, `Fin`, `Id` ; recherche « Notes contient Id » ; `Si` possède une valeur → trois actions « Régler » (titre, début, fin) ; `Sinon` → « Ajouter » avec l'id dans les Notes ; « Ouvrir Calendrier » après la boucle. L'action « Régler… sur… » existe bien (je l'avais mise en doute à tort).
- **Anomalie relevée sur capture** : le filtre de la recherche était sur le calendrier « Travail » alors que « Ajouter » écrivait dans « Plan du jour ». L'utilisateur : il exporte désormais directement dans **Travail** (plus d'agenda séparé). Risque identifié : l'étape « Supprimer » de la migration aurait effacé les rendez-vous de travail de la période ; **elle a été retirée** par l'utilisateur. Les événements créés en 0.28.0 (sans id, ancien agenda) sont à supprimer à la main.
- **0.29.0 validée sur iPhone** : second envoi après changement dans l'app = mise à jour sans doublon ; alerte et lieu réglés à la main conservés ; anciens événements et ancien agenda « Plan du jour » supprimés ; « Ouvrir Calendrier » voulu (second rappel ou adresse réglés à la main). Le filtre de date de la recherche est obligatoire selon l'utilisateur : un bloc ponctuel déplacé hors de la période envoyée serait recréé (non testé, limite connue ; contournement : envoyer « 7 jours »).

### Session de validation du raccourci (aucun code modifié, version toujours 0.28.0)
- Le raccourci iPhone « Plan du jour » est construit et **validé de bout en bout sur appareil avec le JSON de test** : lecture des dates ISO sans décalage (Début 00:00, Fin 23:59), suppression de l'événement de test, événements recréés aux bonnes heures, pas de doublon au second lancement, aucune demande d'autorisation Calendrier. Procédure détaillée dans `RACCOURCI.md`.
- Pièges consignés dans `RACCOURCI.md` : après un « Définir la variable », l'action suivante ne reprend plus le dictionnaire par défaut (le choisir à la main) ; chaque bloc (Début, Fin) doit avoir sa propre action « Obtenir les dates de ».
- Le lien `shortcuts://` depuis l'app installée lance le raccourci tout seul, mais avec une confirmation système à chaque fois (non supprimable, à ne pas supposer).
- Limite constatée : « supprimer puis recréer » efface à chaque envoi les réglages faits à la main dans Calendrier (alertes, lieu, délai de route). Piste 0.29.0 (à valider avec l'utilisateur avant de coder) : identifiant stable par événement dans le JSON, écrit dans les Notes par le raccourci ; mise à jour de l'événement retrouvé, création sinon ; événement disparu du plan non supprimé mais signalé par une notification.
- Reste à confirmer sur appareil : second envoi sans doublon avec le vrai envoi depuis l'app ; lecture sur iPhone des versions 0.25.3 à 0.28.0 ; validation iPad avant la 1.0.
- Questions ouvertes : « Jour » après minuit (afficher le jour courant ? réponse ambiguë, à reconfirmer) ; nommer les passages ou s'en tenir aux sous-tâches libres.

### Session de la 0.28.0 (envoi vers Raccourcis)
- Retour de l'utilisateur : l'export `.ics` (partage direct ou Fichiers) ne propose pas Calendrier ; plan B = Raccourcis, pas via le Mac. Réponses : agenda « Plan du jour » existant ; rappel à l'heure de l'événement.
- **0.28.0** : `doShortcutSend`, `shortcutPayload`, `calPeriod`, `copyText`, `openLink` ; `RACCOURCI.md` (procédure du raccourci). `tests/test_raccourcis.py` (14 vérifications), deux contrôles négatifs faits ; 329 vérifications OK. Vérifié dans Apple Support : lien `shortcuts://run-shortcut?name=…&input=clipboard|text`.
- À confirmer sur appareil : ouverture du lien depuis l'app installée, lecture des dates ISO, suppression sans doublon. Cause du `.ics` qui ne propose pas Calendrier : non élucidée.

### Session de la 0.27.0 (export du jour même)
- Demande : exporter aussi le jour même (« tout actualisation se fait dans l'app »). Réponses : périodes ajoutées (Aujourd'hui, 7 jours dès aujourd'hui) ; Réglages seulement ; plan actuel ; un événement par passage ; réexport accepté avec la limite (bloc retiré = reste dans Calendrier).
- **0.27.0** : `doCalExport` (4 périodes), `calendarEvents` (heure courante pour aujourd'hui, événements par passage). `tests/test_export_jour.py` (17 vérifications, heure simulée), deux contrôles négatifs faits ; 315 vérifications OK.
- À confirmer sur iOS : un réexport met bien à jour les événements existants.

### Session de la 0.26.1 (recentrage par l'onglet Jour)
- Demande : l'app reste ouverte, toucher « Jour » doit recentrer sur la ligne. **0.26.1** : le gestionnaire des onglets appelle `scrollToNow` pour « Jour » (aujourd'hui seulement). 3 vérifications ajoutées (`test_maintenant.py`, 25 au total), contrôle négatif fait (geste retiré : échecs), 298 vérifications OK.
- Limite connue : si l'app reste ouverte au-delà de minuit, le jour affiché reste la veille tant qu'on ne touche pas « Aujourd'hui » (comportement d'origine, non modifié).

### Session de la 0.26.0 (ligne « maintenant »)
- Demande : « un curseur d'avancement de temps, pour savoir où on en est dans la journée, qui défile à mesure que le temps passe ». Réponses : une ligne pour se situer par rapport aux blocs et temps libres (pas de barre de progression) ; page placée sur la ligne si on peut défiler librement ; rien hors plage ; pas de grisé ; aussi dans le Récap.
- `7ba0f5c` **0.26.0** : `div.nowline` sur la frise, `li.nowli` dans le Récap, `scrollToNow` à l'ouverture et au retour sur aujourd'hui. `tests/test_maintenant.py` (22 vérifications, horloge simulée) ; deux contrôles négatifs faits (filtre hors plage retiré : 3 échecs ; rafraîchissement qui défile : 1 échec) ; 295 vérifications OK ; captures iPhone clair et sombre vérifiées.

### Session de la 0.25.3 (passages d'une tâche sans heure)
- Réponses de l'utilisateur : oui à « la tâche reste dans Sans heure après ■, ▶ ouvre un nouveau passage, chaque passage visible dans la frise et cumulé dans les Stats » ; nommer = sous-tâches libres existantes ; vaut pour toutes les tâches sans heure, sans case à régler ; pas de case « fait » (le chrono prouve que c'est fait) ; pas de tâche à sous-activités pour l'instant.
- `6f21131` **0.25.3** : passages = entrées de `segs` à `cid` vide ; `isPlain`, `passesText`, `toPasses` ; `startNow`, `buildDay` (`reopen`), `timeEntries`, `markKidDone`, panneau, `savePanel`, effacement adaptés. `tests/test_passages.py` (31 vérifications), deux contrôles négatifs faits (la fonction rendue fausse, puis la tâche non reproposée : échecs), 273 vérifications OK. Captures iPhone clair et sombre vérifiées.
- Limite à rappeler : un passage ne porte pas de nom ; le temps par dossier n'existe pas.

## 2 novembre 2026

### Session de la 0.25.2 (stockage persistant)
- Retours de l'utilisateur : tests iPhone faits, « ça semble fonctionner correctement » ; l'app est ouverte depuis l'icône de l'écran d'accueil (iPhone et iPad) ; oui à la demande de stockage persistant ; hypothèse « iPhone validé jusqu'à la 0.23.1 » confirmée ; **on garde les deux cartes** « Par catégorie » et « Par activité ». Le délai de 7 jours du rappel n'a pas été discuté (toujours à confirmer). Le bandeau (au moins 3 jours) n'a pas pu être vu apparaître.
- `f0f2eb9` **0.25.2** : `requestPersistence` (`persisted()` puis `persist()`), état `persistState`, paragraphe `#persist-info` dans Réglages › Sauvegarde. `tests/test_stockage.py` (14 vérifications, système simulé), contrôle négatif fait (un refus affiché « accordée » : 1 échec) ; 242 vérifications OK.
- Retour sur l'usage : « les tâches sans heure disparaissent une fois qu'on appuie sur stop, cependant je peux les utiliser plusieurs fois dans une journée pour des dossiers différents ». Constat dans le code : une activité sans heure **sans sous-activités** n'a qu'un créneau par jour (`real[clé] = { start, end }`) et sort de la liste « Sans heure » à l'arrêt (état `done`) ; seule une activité **avec** sous-activités reste proposée (`reopen`, créneaux multiples dans `segs`). Conception en attente des réponses de l'utilisateur (relancer le même chrono plusieurs fois ? nommer chaque passage ? toutes les tâches sans heure ou seulement certaines ?).

### Session de la 0.25.1 (bandeau sur tous les onglets)
- Retours de l'utilisateur sur la 0.25.0 : le bandeau doit être sur toutes les pages ; liste de contrôles appareil acceptée ; réponse sur « Par catégorie » / « Par activité » reportée à l'enregistrement de vraies activités. Question posée par l'utilisateur : « l'iPhone peut vider les données, à quelle fréquence ? » (je n'avais pas dit ça dans cette conversation). Vérifié sur les sources de WebKit : dans Safari (onglet), le stockage d'un site est supprimé après 7 jours d'usage de Safari sans interaction avec le site ; une app ajoutée à l'écran d'accueil a son propre compteur, remis à zéro à chaque usage, et WebKit ne s'attend pas à supprimer ses données ; depuis iOS 17, tout reste « au mieux » (suppression possible sous pression de stockage ou après une longue inactivité, des plus anciens aux plus récents) sauf demande de stockage persistant, accordée selon des critères dont l'ouverture depuis l'écran d'accueil. Aucune fréquence fixe n'est donnée pour ces suppressions. Question ouverte : l'utilisateur ouvre-t-il l'app depuis l'icône de l'écran d'accueil ? Piste proposée, non faite : demander le stockage persistant au démarrage.
- `558b3da` **0.25.1** : un emplacement unique `#backup-slot` en tête de la page, `renderBackupBanner` (contenu réécrit seulement s'il change), écouteur de clics sur l'emplacement ; le bandeau n'est plus dans la page du jour. `tests/test_sauvegarde.py` (59 vérifications), contrôle négatif fait (bandeau limité à la page du jour : 2 échecs) ; 228 vérifications OK.

### Session de la 0.25.0 (rappel de sauvegarde)
- Demande : « passe au rappel de sauvegardes ». Sur la question « garder à la fois Par catégorie et Par activité », l'utilisateur répondra quand des activités seront enregistrées : question toujours ouverte.
- Choix par défaut (à confirmer à l'usage) : délai de 7 jours réglable (jamais, 3, 7, 14, 30) ; le rappel ne se déclenche que s'il y a des modifications non sauvegardées (pas sur une app inchangée) ; bandeau sur la page du jour seulement ; « Plus tard » = rappel demain ; le compte d'une app déjà utilisée commence à la première ouverture de la 0.25.0.
- `1bdaa7e` **0.25.0** : clé `plandujour.sauvegarde` (`last`, `since`, `snooze`, `every`), `backupDue`, bandeau, résumé et choix du délai dans Réglages, marquage dans `persistDays`, l'enregistrement des réglages, l'import et la réinitialisation, `doExport` marque la sauvegarde (feuille de partage acceptée ou téléchargement). `tests/test_sauvegarde.py` (50 vérifications) ; deux contrôles négatifs faits (seuil du délai : 2 échecs ; marquage des modifications : 1 échec) ; captures vérifiées sur écran d'iPhone (390 px, clair et sombre) ; 219 vérifications OK. Un conflit de nom avec une fonction existante (`isDateKey`) a fait échouer tous les tests au démarrage ; ma fonction a été renommée `isRealDateKey`, l'ancienne est inchangée.
- Limite connue : l'app ne peut pas savoir si le fichier exporté a été rangé au bon endroit (Fichiers, iCloud Drive) ; elle compte la sauvegarde dès que la feuille de partage est acceptée.
- Questions ouvertes : « Par catégorie » et « Par activité » ; délai de 7 jours ; liste de contrôles sur appareil toujours à livrer ; validation iPad.

### Session de la 0.24.0 (Stats en arbre)
- Retours de l'utilisateur sur la 0.23.1 : tout fonctionnait sur l'appareil ; on garde les catégories sans sous-catégorie derrière leur menu (un tap de plus), pas de ligne directe. Feu vert pour la 0.24.0.
- `f894be8` **0.24.0** : `statsTree` (totaux par statut et par catégorie, activités et sous-activités au bout, « Sans catégorie » en Hors), `statsFor` renvoie `kinds` à la place de la liste plate `cats`, rendu en menus imbriqués (`statsKindHtml`, `statsNodeHtml`), état déplié gardé en mémoire (`statsOpen`). `tests/test_stats_arbre.py` (25 vérifications) ; l'ancien test d'étiquette de `test_statuts.py` est retiré (34 vérifications). Contrôle négatif fait (7 échecs quand les sous-catégories sont oubliées dans les totaux) ; captures vérifiées sur écran d'iPhone (390 px, clair et sombre) ; 169 vérifications OK. Une erreur de calcul de ma part dans le premier jeu de test (280 min et non 290) a été corrigée dans le test, pas dans le code.
- Choix par défaut, à confirmer à l'usage : l'arbre remplace la carte « Par catégorie » ; « Par activité » (à plat) est gardée telle quelle ; les trois statuts sont toujours affichés, même à 0 ; les barres sont la part de la catégorie.
- Questions ouvertes : lisibilité de l'arbre sur une semaine réelle ; garder ou non « Par activité » ; rappel de sauvegarde et liste de contrôles appareil toujours à livrer ; validation iPad.

### Session de la 0.23.1 (statuts et menus imbriqués)
- Reprise : dépôt cloné à `194b330`, documents relus, 110 vérifications OK (Chrome du système, Playwright n'ayant pas pu télécharger le sien ; rien ajouté au dépôt).
- Constats : docs en retard sur les décisions (STATUS annonçait encore des racines Pro / Perso / Trajets imposées et la disparition de la case Travail ; lot 5 bis « en suspens » ; CONVENTIONS avait le §37 avant le §36 ; carnet disait « .pyc non décidé » alors que c'était fait). Corrigés. La sauvegarde (export / import JSON) existait déjà.
- Décisions de l'utilisateur : les trajets sont **hors** catégorie pro / perso ; héritage confirmé et **aucun mélange possible** (la case ne se choisit que sur la racine) ; une activité sans catégorie est **hors** ; arbre **entièrement imbriqué** ; visuel avec couleurs ; une ligne modifiée reste en place jusqu'à l'enregistrement ; 0.23.1 pour Réglages puis 0.24.0 pour les Stats ; rappel de sauvegarde et liste de contrôles appareil acceptés (à faire) ; pas de synchro automatique (aucun serveur) : export / import par iCloud Drive ou AirDrop.
- `a3d30e8` **0.23.1** : `kind` (`work` / `perso` / `hors`) avec `catKind`, `fixKinds`, `normCats` ; ancien `work` gardé synchronisé ; lecture des anciens réglages (case cochée = travail, sinon perso, « Trajets » de départ = hors) ; Réglages en trois menus de statut contenant des menus imbriqués (`catNodeHtml`, `catGroupsHtml`, `refreshCatTree`) ; pastilles et traits de couleur ; Stats « Par catégorie » : « · travail » / « · hors ». `tests/test_statuts.py` (36 vérifications), contrôle négatif fait (13 échecs avec l'héritage cassé), `test_arborescence.py` adapté ; captures vérifiées sur écran d'iPhone (390 px, clair et sombre) ; 146 vérifications OK.
- Questions ouvertes : coût en taps pour éditer une catégorie (menu puis ligne) ; validation sur appareil des versions 0.20.0 à 0.23.1 (l'iPad n'a pas été touché) ; rappel de sauvegarde et liste de contrôles appareil à livrer.

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
