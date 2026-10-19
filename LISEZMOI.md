# Aux Voix

Site d'information sur le Parlement : votes, élus, lois et codes, d'après les données officielles
de l'Assemblée nationale et de la DILA (Légifrance), sous Licence Ouverte. Mise à jour automatique
deux fois par jour (vers 7 h 15 et 21 h 15) ; codes et amendements relus une fois par semaine.

## Contenu

- `site/index.html` : le site.
- `site/contenu/site.json` : réglages et mentions légales (voir « Ouvrir au public »).
- `site/contenu/lois.json`, `site/contenu/articles.json` : résumés de lois et explications d'articles rédigés à la main (facultatif).
- `site/contenu/corrections.json` : journal des corrections.
- `scripts/construire_donnees.py` : votes, élus, lois ; `scripts/codes.py` : codes ; `scripts/communes.py` : communes et circonscriptions ; `scripts/textes.py` : exposé des motifs des textes déposés ; `scripts/pages.py` : pages publiques, plan du site, flux RSS, cartes intégrables.
- `site/manifest.webmanifest`, `site/sw.js`, `site/icones/` : installation comme application et lecture hors connexion.
- `site/integrer.html` : carte d'un vote à intégrer sur un autre site.
- `.github/workflows/mise-a-jour.yml` : automatisation (dossier caché sur Mac : Cmd + Maj + point pour l'afficher).

## Ouvrir au public (le jour venu)

1. Remplir `site/contenu/site.json`, rubrique `mentions`.
   - **Éditeur non professionnel qui reste anonyme** (cas actuel) : laisser `"anonyme": true`, ne rien écrire dans
     `editeur` ni `directeur_publication`, renseigner `contact` (adresse e-mail dédiée au site) et garder les
     coordonnées de l'hébergeur. L'identité de l'éditeur doit avoir été communiquée à l'hébergeur (loi du
     21 juin 2004, art. 1-1, II). Ce régime est réservé aux sites sans publicité, vente ni don.
   - **Éditeur identifié** : passer `anonyme` à `false` et remplir `editeur`, `directeur_publication` et `contact`.
   Si les mentions sont incomplètes, la mise à jour s'arrête avec un message d'erreur et le site en ligne n'est pas modifié.
2. Faire relire les mentions légales et la méthode par un juriste. Gratuit et sans rendez-vous possible :
   - clinique juridique de l'Université Paris Cité (faculté de droit, 10 avenue Pierre Larousse, Malakoff) :
     clinique.juridique.deg@u-paris.fr ; consultations gratuites pour particuliers, entreprises et associations ;
   - clinique juridique de Paris 8, à la BnF (site François-Mitterrand, salle de l'Aquarium), le mercredi de 16 h 30 à 19 h 30,
     d'octobre à mai, pour tout public ; lacliniquejuridique@gmail.com, 01 49 40 65 29 ;
   - clinique juridique de l'Université Paris-Panthéon-Assas : cliniquejuridique.contact@gmail.com ;
   - pour la question des données personnelles seulement : CNIL, 01 53 73 22 22 (touche 2, lundi, mardi, jeudi et
     vendredi de 10 h à 12 h) ou formulaire « Je veux poser une question » sur cnil.fr.
   L'anonymat vaut à l'égard du public, pas de son conseil : on peut écrire à une clinique depuis son adresse personnelle.
   (Avec SimpleLogin, écrire un nouveau message depuis l'alias du site demande l'offre payante.)
3. Dans le même fichier, passer `"public": false` à `"public": true`. C'est le seul interrupteur :
   au passage suivant, toutes les pages deviennent visibles des moteurs de recherche, le plan du site est
   publié et `robots.txt` autorise l'exploration. Pour refermer, remettre `false`.
4. Déclarer `<adresse du site>/sitemap.xml` (par exemple `https://auxvoix.fr/sitemap.xml`) dans Google Search Console (gratuit) pour accélérer l'indexation.

## Pages publiques et liens permanents

Chaque député (`/depute/PA…/`), vote important (`/vote/17/1234/`), loi (`/loi/DLR…/`) et article de code
(`/code/civil/1240/`) a sa propre page, lisible sans JavaScript et citable. Les boutons « Citer » du site
donnent ces adresses.

## Flux de suivi (RSS)

`/flux/votes.xml`, `/flux/lois.xml`, `/flux/agenda.xml` (votes solennels annoncés), `/flux/presidentielle.xml`
(candidatures publiées et titres de la campagne), `/flux/depute/PA….xml` (un par député), `/flux/code/civil.xml` (un par code).

## Rédiger un résumé de loi ou une explication d'article

Copier `modeles/fiche-loi.json` ou `modeles/fiche-article.json` dans le fichier de contenu correspondant
(entre les crochets), remplir chaque champ, mettre `"publie": true`. L'auteur et le vérificateur doivent être
deux personnes différentes. En cas d'erreur de saisie, l'onglet Actions affiche la ligne en cause et le
site en ligne reste inchangé.

## Proposer un partenariat à une association d'étudiants en droit (modèle de message)

> Bonjour, je développe Aux Voix, un site gratuit et indépendant qui rend accessibles les votes des députés,
> le parcours des lois et les principaux codes, avec la référence prête à citer pour chaque article
> (https://aux-voix.github.io). Nous aimerions publier de courtes explications des articles les plus
> étudiés, rédigées par des étudiants et relues par un enseignant, avec le nom des auteurs.
> Seriez-vous intéressés par un échange ? Bien cordialement.


## Adresse du site : https://aux-voix.github.io

Organisation GitHub « aux-voix », dépôt « aux-voix.github.io » (renommés le 6 octobre 2026 ; le nom « auxvoix » sans tiret est pris sur GitHub).
Le champ « url » de `site/contenu/site.json` vaut https://aux-voix.github.io. C'est la seule adresse écrite dans le site :
liens des pages publiques, plan du site, flux RSS, code d'intégration, fiches imprimées et compteur de visites la lisent toutes.

### Passer à un nom de domaine (auxvoix.fr, libre le 19 octobre 2026)

Le site reste hébergé par GitHub Pages (gratuit, mis à jour deux fois par jour, HTTPS automatique) : on n'achète que le nom.

1. Acheter le nom chez OVHcloud, sans hébergement ni option (5,99 € TTC la première année, puis 9,35 € TTC par an,
   tarifs relevés le 19 octobre 2026). Pour un particulier, l'Afnic ne publie ni le nom ni l'adresse du titulaire.
2. GitHub, organisation aux-voix : Settings, Pages, « Add a domain », saisir `auxvoix.fr`. GitHub donne un
   enregistrement TXT `_github-pages-challenge-aux-voix.auxvoix.fr` : l'ajouter dans OVH (Zone DNS), puis « Verify ».
   Cela empêche quiconque d'utiliser le domaine sur GitHub. Garder cet enregistrement ensuite.
3. Dépôt aux-voix.github.io : Settings, Pages, « Custom domain » : `auxvoix.fr`, Save. (Pas de fichier CNAME à créer :
   le site est publié par GitHub Actions, qui l'ignore.)
4. OVH, Zone DNS de auxvoix.fr : supprimer les enregistrements A et AAAA du nom nu et de `www` créés par OVH, puis ajouter :
   - A (nom vide) : 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 (quatre lignes) ;
   - AAAA (nom vide) : 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 ;
   - CNAME `www` vers `aux-voix.github.io.`
   Ne pas toucher aux enregistrements MX, SPF ou DKIM si une adresse e-mail OVH est utilisée.
5. Attendre que GitHub affiche « DNS check successful » (quelques minutes à 24 heures), puis cocher « Enforce HTTPS »
   dès que la case est disponible.
6. Seulement alors, mettre `"url": "https://auxvoix.fr"` dans `site/contenu/site.json` et téléverser. L'ancienne adresse
   aux-voix.github.io redirige ensuite toute seule vers la nouvelle.

## Compteur de visites (GoatCounter, sans cookie)

Éteint tant que `"goatcounter"` est vide dans `site/contenu/site.json` (bloc `mesure_audience`). Pour l'allumer :

1. Créer un compte sur goatcounter.com (gratuit pour un site comme celui-ci). Code du site : par exemple `auxvoix`,
   ce qui donne le tableau de bord https://auxvoix.goatcounter.com. Adresse e-mail : l'alias SimpleLogin convient.
2. Écrire ce code dans `site/contenu/site.json` : `"mesure_audience": {"goatcounter": "auxvoix"}`, puis téléverser.

Ce qui se passe alors :
- aucun script n'est chargé depuis un autre site : `app.js` (pages du site) et `statique.js` (pages publiques) envoient
  un seul appel par page à https://auxvoix.goatcounter.com/count, une fois la page affichée (vitesse inchangée) ;
- l'adresse envoyée ne contient jamais ce qui suit « ? » (recherche tapée, filtres) ;
- rien n'est compté ailleurs qu'à l'adresse du champ « url » (ni l'aperçu, ni une copie de test), ni pour un visiteur
  qui a refusé (bouton dans Méthode, Données personnelles) ou dont le navigateur envoie Do Not Track ou Global
  Privacy Control ;
- la page Données personnelles et le pied de page décrivent automatiquement ce qui est compté.
Pour ne pas compter tes propres visites : clique « Ne pas compter mes visites » dans Méthode, sur chacun de tes appareils.

## Présidentielle 2027 : candidats et actualités

Les fiches se remplissent dans `site/contenu/candidats.json` et `site/contenu/actualites.json`, sur le modèle de `modeles/fiche-candidat.json` et `modeles/fiche-actualite.json`.
Règles, vérifiées automatiquement : chaque information a une source en https ; une fiche n'apparaît que si « publie » vaut true ; pour les propositions, les programmes et les actualités rédigées, l'auteur et le vérificateur sont deux personnes différentes. Une simple annonce de candidature (statut « annonce ») doit seulement citer sa source : le site dit qu'elle est relevée d'après LCP et Public Sénat, sans parler de double vérification.
Règles de neutralité, à respecter par la personne qui rédige : propositions reprises des documents officiels des candidats, sans reformulation qui en change le sens ; mêmes thèmes pour tous ; pas d'adjectif ni de jugement ; pas de « pressentis » ni de sondages ; la liste officielle du Conseil constitutionnel remplace les candidatures déclarées dès sa publication.

## Outils pour le public

- **Lexique** (`#/lexique`) : les mots techniques sont soulignés en pointillé dans tout le site et s'expliquent au toucher. Les définitions sont dans `site/app.js` (tableau `LEX`).
- **Quiz** (`#/quiz`) et **Aux Voix en classe** (`#/classe`) : questions de fonctionnement et fiches d'activités imprimables (tableaux `QUIZ` et `CLASSE`).
- **Trouver son député** par commune ou code postal : `site/communes.json`, construit à chaque mise à jour par `scripts/communes.py` à partir des résultats officiels des législatives 2024 par bureau de vote (gardés en cache) et de l'API Découpage administratif. En cas de panne, le choix par département reste proposé.
- **Mes suivis** (`#/suivis`) : sans compte, enregistrés dans le navigateur de chaque personne.
- **La semaine à l'Assemblée** (`#/semaine`) : bilan calculé selon des règles fixes, avec une image à partager.
- **Intégrer un vote** : bouton « Partager et citer » d'un scrutin, puis « Intégrer sur un site ». Les données des cartes sont dans `site/carte/` (générées).
- **Application** : bouton « Installer l'application » en bas de page. Après une modification importante de `sw.js`, changer sa première ligne (`av-1` en `av-2`…) pour forcer la mise à jour chez tout le monde.
- **Ce que propose un texte** : sur chaque page de loi, extraits mot pour mot de l'exposé des motifs (la présentation écrite par les auteurs), lus sur le site de l'Assemblée par `scripts/textes.py`. Environ 350 textes sont lus à chaque mise à jour, les plus actifs d'abord ; chaque texte n'est lu qu'une fois (cache). Il faut donc quelques jours pour couvrir tous les textes. Les textes tout juste déposés apparaissent quand l'Assemblée les met en ligne.
- **À venir à l'Assemblée** (`#/agenda`) : l'ordre du jour officiel des prochaines séances, lu à chaque mise à jour par `scripts/agenda.py` (jeu « Agenda » des données ouvertes de l'Assemblée). Les votes solennels annoncés apparaissent aussi sur l'accueil et sur la page de chaque loi concernée. Bilan dans l'annotation « Agenda » de GitHub Actions.
- **Signaler une erreur** (`#/signaler`, lien en bas de chaque page) : le visiteur prépare son message ; le site n'envoie et n'enregistre rien. Le bouton « Préparer l'e-mail » apparaît dès que `contact` est rempli dans `site/contenu/site.json`. Réglages dans la rubrique `signalement` du même fichier : `delai_jours` (délai de réponse annoncé, 7 par défaut, 0 pour ne rien annoncer) et `github` (false par défaut). Attention : passer `github` à true ouvre les signalements publics sur GitHub ; y répondre avec un compte personnel rendrait ce compte visible.
- **Corriger une erreur** : ajouter une ligne dans `site/contenu/corrections.json`, par exemple `{"date": "2026-10-20", "texte": "Candidats : la date d'annonce de X était fausse (12 au lieu du 21 septembre)."}`. Elle apparaît dans le journal des corrections, en bas de page et sur la page de signalement.
- **Comment on vérifie** (`#/verifier`) : le dernier vote solennel, pas à pas, de la donnée officielle à la page, avec ce qui est recopié et ce qui est calculé.
- **Comparateur** (`#/comparateur`) : bouton « Copier le lien de cette comparaison » (adresses du type `#/comparateur?a=PA…&b=PA…` ou `?g=PO…&g2=PO…`) et accès rapide aux députés suivis.
- **Codes** : les intitulés de parties fusionnés ou en double (ancien et nouvel intitulé d'un même titre ou chapitre) sont nettoyés par `scripts/codes.py` ; la Constitution ne garde que les articles de celle de 1958.
- **Poids des données** : le vote de chaque député est rangé dans `votes-17.json`, à part de `data-17.json`. L'accueil n'en a pas besoin et s'affiche donc deux fois plus vite ; les pages qui en ont besoin (fiche d'un député, détail d'un scrutin, comparateur, suivis, « Comment on vérifie ») le chargent à la demande, dès qu'on survole ou touche un lien vers elles.
- **Tests automatiques** : `scripts/tests/` (lancés par `python -m unittest discover -s scripts/tests`) et une vérification de la syntaxe du site tournent avant chaque mise à jour. Si l'un échoue, la mise à jour s'arrête et le site en ligne reste tel quel : l'onglet Actions indique lequel.
- **Bilan de chaque mise à jour** : onglet « Actions » du dépôt, cliquer sur le passage le plus récent (« Mise à jour quotidienne »). Le tableau « Bilan de la mise à jour » s'affiche en haut de la page, une ligne par rubrique (Votes, Actualités, Agenda, Communes, Textes, Codes) : ✅ tout va bien, ⚠️ à regarder.
- **Vitesse** (mesurée avec Lighthouse, téléphone lent simulé) : l'accueil et les pages publiques (`/depute/…`, `/loi/…`, `/vote/…`, `/code/…`) obtiennent 97 à 100 sur 100 ; depuis la V0.27, les pages du site ouvertes directement par un lien (fiche d'un député, vote, loi, listes) obtiennent 93 à 100, contre 53 à 80 avant ; le comparateur, qui doit lire tous les scrutins, 80 à 90. Comment :
  - **Graines** (`scripts/graines.py`, dossier `g/17/` du site, environ 4 200 petits fichiers refaits à chaque mise à jour) : chaque page a son petit fichier, qui contient seulement ce qu'elle affiche. Une fiche de député ouverte par un lien lit environ 25 Ko au lieu de 1,7 Mo. Le fichier complet n'est téléchargé qu'au premier geste qui en a besoin (filtrer une liste, chercher dans le site, choisir un autre député dans le comparateur). Le tronc commun (groupes, périodes, médianes) est dans `demarrage.json`. Les règles de choix recopient celles de `app.js` : si l'on change par exemple le nombre de « derniers votes » d'une fiche (25), il faut le changer aussi dans `graines.py`. Les tests de `scripts/tests` vérifient ces règles avant chaque mise à jour. Si l'écriture des graines échoue, le bilan l'indique et le site charge simplement les données complètes, comme avant.
  - `site/app.js` contient tout le code du site ; `index.html` le charge avec une empreinte (`app.js?v=…`) posée automatiquement à chaque mise à jour, pour que les navigateurs prennent toujours la dernière version. Après une modification de `app.js`, rien d'autre à faire.
  - `accueil-17.json` (environ 15 Ko compressé) suffit pour l'accueil, la présidentielle, les candidats, l'agenda, les codes, le lexique, le quiz, la méthode… Le fichier complet `data-17.json` n'est chargé que pour les pages de votes, de lois et de députés, ou dès qu'on s'apprête à les ouvrir.
  - `demarrage.json` regroupe l'index et tous les fichiers de `site/contenu/` en un seul téléchargement ; il est refait à chaque mise à jour. Les fichiers séparés restent la référence à modifier.
  - Les polices sont converties en WOFF2 allégé (5 à 10 fois plus léger que le TTF) à chaque mise à jour.
  - Le haut de l'accueil est écrit directement dans `index.html` : il s'affiche avant même le chargement du code. S'il change dans `app.js` (fonction `pageHome`), le recopier aussi dans `index.html` (bloc `<main>`).
