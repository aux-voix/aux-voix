# Contrôle d'accessibilité : V0.22 (18 octobre 2026)

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

## Corrigé pendant ce contrôle

- La page À venir et le comparateur n'annoncent plus tout leur contenu aux lecteurs d'écran à chaque changement : seule la phrase de résultat du comparateur est annoncée.
- Les cases à cocher font 24 px sur écran tactile.
- Les mots du lexique dans la liste de l'ordre du jour ont une zone de toucher de 24 px de haut.

## Reste à faire par une personne

1. Parcourir le site avec NVDA et Firefox (Windows), VoiceOver (iPhone) et TalkBack (Android) : ordre de lecture, annonce des changements de page, fenêtres de dialogue, lexique.
2. Juger ce qu'un outil ne peut pas juger : pertinence des textes de liens et des alternatives des images, clarté des consignes, cohérence de la navigation.
3. Vérifier les grilles RGAA 4.1 thème par thème (106 critères) sur un échantillon de pages, puis publier une déclaration d'accessibilité avec le taux obtenu.
