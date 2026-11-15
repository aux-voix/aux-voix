"""Contrôle d'accessibilité automatique du site construit, avec axe-core (règles WCAG 2.0, 2.1 et 2.2, niveaux A et AA,
et bonnes pratiques), en thème clair et sombre, sur téléphone et sur ordinateur.

Usage : python scripts/accessibilite.py site chemin/vers/axe.min.js

Ce contrôle ne remplace pas un audit RGAA : il ne voit qu'une partie des critères. Le site reste « non audité ».
Lancé par la mise à jour automatique après la préparation du site ; son résultat n'empêche jamais la publication."""
import asyncio
import functools
import http.server
import os
import sys
import threading

PAGES = [("Accueil", "#/"), ("Présidentielle", "#/presidentielle"), ("Candidats", "#/candidats"), ("Calendrier électoral", "#/elections"),
         ("Actualités", "#/actualites"), ("Lois", "#/lois"), ("Votes", "#/votes"), ("Députés", "#/elus"), ("Groupes", "#/groupes"),
         ("Codes", "#/codes"), ("Comprendre", "#/comprendre"), ("Lexique", "#/lexique"), ("Quiz", "#/quiz"),
         ("Signaler une erreur", "#/signaler"), ("Méthode", "#/methode/ia"), ("Accessibilité", "#/methode/accessibilite")]
ECRANS = [("téléphone", 390, 844), ("ordinateur", 1360, 900)]
REGLES = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]


def servir(dossier):
    class Muet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass

    gest = functools.partial(Muet, directory=dossier)

    class Serveur(http.server.ThreadingHTTPServer):
        def handle_error(self, *a, **k):
            pass

    srv = Serveur(("127.0.0.1", 0), gest)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


async def controler(base, axe):
    from playwright.async_api import async_playwright
    erreurs, etats = [], 0
    async with async_playwright() as p:
        try:
            nav = await p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        except Exception:
            nav = await p.chromium.launch(args=["--no-sandbox"])
        for ecran, l, h in ECRANS:
            for theme in ("light", "dark"):
                ctx = await nav.new_context(viewport={"width": l, "height": h}, color_scheme=theme, service_workers="block")
                page = await ctx.new_page()
                for nom, ancre in PAGES:
                    await page.goto(base + "/" + ancre)
                    await page.reload()
                    await page.wait_for_timeout(1500)
                    await page.evaluate(axe)
                    res = await page.evaluate("axe.run(document,{runOnly:%r}).then(r=>r.violations.map(v=>[v.id,v.help,v.nodes.length]))" % REGLES)
                    deborde = await page.evaluate("document.documentElement.scrollWidth>window.innerWidth+1")
                    etats += 1
                    lieu = f"{nom}, {ecran}, thème {'clair' if theme == 'light' else 'sombre'}"
                    for ident, aide, nb in res:
                        erreurs.append(f"{lieu} : {ident} ({aide}), {nb} élément(s)")
                    if deborde:
                        erreurs.append(f"{lieu} : la page dépasse en largeur")
                await ctx.close()
        await nav.close()
    return etats, erreurs


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    site, axe = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
    srv = servir(site)
    try:
        etats, erreurs = asyncio.run(controler(f"http://127.0.0.1:{srv.server_address[1]}", axe))
    finally:
        srv.shutdown()
    bilan = f"{len(PAGES)} pages, {etats} états contrôlés avec axe : " + ("aucune erreur" if not erreurs else f"{len(erreurs)} erreur(s)")
    print(bilan)
    for e in erreurs:
        print("  " + e)
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{'warning' if erreurs else 'notice'} title=Accessibilité::{bilan}")
    resume = os.environ.get("GITHUB_STEP_SUMMARY")
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(f"\n## Contrôle d'accessibilité automatique\n\n{'⚠️' if erreurs else '✅'} {bilan}.\n\n")
            for e in erreurs[:40]:
                f.write(f"- {e}\n")
            f.write("\nContrôle automatique partiel : il ne remplace pas un audit RGAA.\n")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
