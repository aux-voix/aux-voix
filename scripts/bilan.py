"""Bilan de chaque mise à jour : affiché en haut de la page du passage dans l'onglet Actions de GitHub
(« Bilan de la mise à jour »), et en annotations."""
import os

LIGNES = []


def noter(niveau, titre, message):
    """niveau : "notice" (tout va bien) ou "warning" (à regarder)."""
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{niveau} title={titre}::{message}")
    LIGNES.append((niveau, titre, message))


def ecrire():
    chemin = os.environ.get("GITHUB_STEP_SUMMARY")
    if not chemin or not LIGNES:
        return
    with open(chemin, "a", encoding="utf-8") as f:
        f.write("## Bilan de la mise à jour\n\n| | Rubrique | Résultat |\n|---|---|---|\n")
        for niveau, titre, message in LIGNES:
            f.write(f"| {'✅' if niveau == 'notice' else '⚠️'} | {titre} | {message.replace('|', '/')} |\n")
        f.write("\n✅ : tout va bien. ⚠️ : à regarder, le reste du site est quand même publié.\n")
