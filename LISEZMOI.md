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
2. Faire relire les mentions légales et la méthode par un juriste (une clinique juridique universitaire convient).
3. Dans le même fichier, passer `"public": false` à `"public": true`. C'est le seul interrupteur :
   au passage suivant, toutes les pages deviennent visibles des moteurs de recherche, le plan du site est
   publié et `robots.txt` autorise l'exploration. Pour refermer, remettre `false`.
4. Déclarer `https://aux-voix.github.io/sitemap.xml` dans Google Search Console (gratuit) pour accélérer l'indexation.

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
Le champ « url » de `site/contenu/site.json` vaut https://aux-voix.github.io. Pour un nom de domaine acheté (auxvoix.fr), remplacer ce champ et saisir le domaine dans Settings, Pages, « Custom domain ».

## Présidentielle 2027 : candidats et actualités

Les fiches se remplissent dans `site/contenu/candidats.json` et `site/contenu/actualites.json`, sur le modèle de `modeles/fiche-candidat.json` et `modeles/fiche-actualite.json`.
Règles, vérifiées automatiquement : chaque information a une source en https ; l'auteur et le vérificateur sont deux personnes différentes ; une fiche n'apparaît que si « publie » vaut true.
Règles de neutralité, à respecter par la personne qui rédige : propositions reprises des documents officiels des candidats, sans reformulation qui en change le sens ; mêmes thèmes pour tous ; pas d'adjectif ni de jugement ; pas de « pressentis » ni de sondages ; la liste officielle du Conseil constitutionnel remplace les candidatures déclarées dès sa publication.

## Outils pour le public

- **Lexique** (`#/lexique`) : les mots techniques sont soulignés en pointillé dans tout le site et s'expliquent au toucher. Les définitions sont dans `site/index.html` (tableau `LEX`).
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
