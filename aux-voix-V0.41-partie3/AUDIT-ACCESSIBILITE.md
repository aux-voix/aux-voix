# Contrôle d'accessibilité : V0.27 (19 octobre 2026)

Contrôle automatique et semi-automatique, fait par un assistant IA. Il ne remplace pas un audit RGAA complet,
qui demande une personne et des lecteurs d'écran réels (voir « Reste à faire »).

## Ce qui a été testé

| Contrôle | Pages | Résultat |
|---|---|---|
| axe-core (WCAG 2.0, 2.1, 2.2 A et AA, bonnes pratiques), thèmes clair et sombre, largeurs 1360, 390 et 320 px | Accueil, À venir, Signaler, Comment on vérifie, Comparateur, Candidats, Députés, Groupes, Code civil, une loi, Méthode | 0 erreur |
| Défilement horizontal à 320 px et avec le texte agrandi à 200 % | Les mêmes | Aucun |
| Navigation au clavier (40 tabulations par page) : chaque élément atteint a un contour de focus visible | Accueil, À venir, Signaler, Vérifier, Comparateur, Candidats, Députés, Code civil | Aucun focus invisible |
| Titres : un seul h1 par page, aucun niveau sauté | Les mêmes | Conforme |
| Titre de l'onglet propre à chaque page | Les mêmes | Conforme |
| Formulaire de signalement : étiquettes, champ obligatoire signalé, erreur annoncée (zone `aria-live`), champ fautif marqué `aria-invalid` et focus replacé dessus | Signaler | Conforme |
| Taille des cibles tactiles (24 × 24 px minimum, WCAG 2.5.8) | Les mêmes, sur téléphone | Conforme, sauf les mots du lexique soulignés dans une phrase, couverts par l'exception « cible dans une phrase » |
| Lecture simulée au lecteur d'écran (Guidepup Virtual Screen Reader, 700 éléments par page) | Accueil, député, scrutin, loi, Lois, Votes, Députés, groupe, Comparateur, Signaler, À venir, Présidentielle, Candidats, La semaine, Thèmes, article de la Constitution, Méthode, Quiz | Aucun bouton, lien ou image sans nom. Chaque page commence par « Aller au contenu », puis le menu « Rubriques » et la recherche ; les boutons de tri disent la colonne et l'action (« Date, Trier par date ») ; les cases P/C/A des thèmes sont lues « LFI-NFP : Contre » |
| Changement de page : le focus va sur le titre de la nouvelle page et le titre de l'onglet change | Accueil → Lois → une loi → Votes → un scrutin | Conforme |
| axe-core sur les pages ouvertes directement par un lien (V0.27), mêmes thèmes et largeurs | Accueil, député, scrutin, loi, Lois, Votes, Députés, groupe, Comparateur, La semaine, Le mois, Thèmes, Actualités, Comment on vérifie, Méthode (90 états) | 0 erreur |
| Pages ouvertes directement (V0.27) : le contenu affiché depuis le petit fichier de la page est identique, au caractère près, à celui affiché avec les données complètes | 254 pages tirées au hasard (députés, scrutins, lois, groupes, listes, semaine, mois, thèmes, comparateur) | Identiques |
| Taille réelle des cibles sur téléphone (390 px) | Accueil, député, Lois, scrutin, Comparateur, Signaler | Toutes au moins 24 px ; 80 % au moins 44 × 44 px (les autres : liens du menu, étroits mais hauts de 49 px, cases à cocher, en-têtes de tri) |

## Corrigé pendant ce contrôle

- Repères des boutons segmentés (niveau de lecture, onglets d'un groupe) : recalés quand les polices arrivent après l'affichage de la page.
- Page d'une loi sans texte déposé en ligne : plus d'erreur dans la console du navigateur.

## Reste à faire par une personne

1. Parcourir le site avec VoiceOver (Mac et iPhone), puis NVDA et Firefox (Windows) et TalkBack (Android) : ordre de lecture, annonce des changements de page, fenêtres de dialogue, lexique. Point à juger en priorité : les mots du lexique sont des boutons au milieu des phrases, et le lecteur d'écran annonce « bouton, réduit » en pleine lecture. Est-ce gênant ?
2. Vérifier que les dessins de l'hémicycle sont lus une seule fois (le nom des groupes écrit dans le dessin ne doit pas être relu après la description).
3. Juger ce qu'un outil ne peut pas juger : pertinence des textes de liens et des alternatives des images, clarté des consignes, cohérence de la navigation.
4. Vérifier les grilles RGAA 4.1 thème par thème (106 critères) sur un échantillon de pages, puis publier une déclaration d'accessibilité avec le taux obtenu.
