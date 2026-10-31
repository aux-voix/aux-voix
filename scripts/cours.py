# -*- coding: utf-8 -*-
"""Pages « Cours et TD » : /cours/ et /cours/<slug>/ (cours, TD, corrigé). Contenu dans site/contenu/cours.json."""
import json, os
from html import escape as ESC


def _ld(g, chemin, titre, desc, fil):
    return [{"@context": "https://schema.org", "@type": "LearningResource", "name": titre, "description": desc, "inLanguage": "fr",
             "url": g.url + chemin, "learningResourceType": "Cours et exercices", "educationalLevel": "Collège, lycée",
             "publisher": {"@type": "Organization", "name": "Aux Voix", "url": g.url}},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": g.url + h} for i, (n, h) in enumerate(fil)]}]


def pages_cours(g):
    chemin_json = os.path.join(g.site, "contenu", "cours.json")
    if not os.path.exists(chemin_json):
        return
    C = json.load(open(chemin_json, encoding="utf-8"))["cours"]
    for c in C:
        s = c["slug"]
        chemin = f"/cours/{s}/"
        parties = "".join(f"<h3>{ESC(p['h'])}</h3>" + "".join(f"<p>{ESC(t)}</p>" for t in p["p"]) for p in c["parties"])
        retenir = "".join(f"<li>{ESC(x)}</li>" for x in c["retenir"])
        mots = "".join(f"<dt>{ESC(m)}</dt><dd>{ESC(d)}</dd>" for m, d in c["mots"])
        td = c["td"]
        doc = f'<blockquote class="art"><p>{ESC(td["doc"])}</p></blockquote>' if td.get("doc") else ""
        qs = ""
        for q in td["questions"]:
            ch = "".join(f"<li>{ESC(x)}</li>" for x in q.get("choix", []))
            qs += f'<li>{ESC(q["q"])}' + (f'<ol type="a" class="choix">{ch}</ol>' if ch else "") + "</li>"
        corr = "".join(f'<li>{ESC(q["rep"])}</li>' for q in td["questions"])
        liens = "".join(f'<li><a href="{ESC(u)}" rel="noopener">{ESC(t)}</a></li>' for t, u in c.get("liens", []))
        titre = f"{c['titre']} : cours et TD corrigé"
        desc = f"{c['objectif']} Cours simple, vocabulaire, exercices et corrigé, à télécharger en PDF."
        corps = f"""<p class="fil"><a href="/cours/">Cours et TD</a></p><h1>{ESC(c['titre'])}</h1>
<p class="lede">{ESC(c['objectif'])}</p>
<p class="meta">{ESC(c['niveau'])} · {ESC(c['duree'])}</p>
<p><a class="cta" href="/cours/pdf/{s}-cours.pdf">Cours en PDF</a><a class="cta s" href="/cours/pdf/{s}-td.pdf">TD en PDF</a><a class="cta s" href="/cours/pdf/{s}-corrige.pdf">Corrigé en PDF</a></p>
<h2>Le cours</h2><p>{ESC(c['intro'])}</p>{parties}
<h2>À retenir</h2><ul class="retenir">{retenir}</ul>
<h2>Vocabulaire</h2><dl>{mots}</dl>
<h2>TD</h2><p class="meta">{ESC(td['consigne'])}</p>{doc}<ol class="q">{qs}</ol>
<details class="corr"><summary>Corrigé (pour l'enseignant)</summary><ol class="q">{corr}</ol></details>
<h2>Pour aller plus loin</h2><ul>{liens}</ul>
<p class="meta">Contenu neutre, fondé sur les textes officiels, rédigé avec l'aide d'une intelligence artificielle : vérifie toujours avec les textes cités. <a href="/#/methode/ia">Comment sont rédigés nos contenus</a>. Une erreur ? <a href="/#/signaler">Signale-la</a>.</p>"""
        fil = [("Cours et TD", "/cours/"), (c["titre"], chemin)]
        g.page(chemin, titre, desc, corps, jsonld=_ld(g, chemin, titre, desc, fil), og_type="article")
        g.urls.setdefault("fonds", []).append((chemin, g.aujourdhui))
    def cartes(groupe):
        return "".join(
            f'<li><a href="/cours/{c["slug"]}/"><span class="n">Cours + TD</span><span class="h">{ESC(c["titre"])}</span><span class="d">{ESC(c["objectif"])}</span></a></li>'
            for c in C if c.get("groupe") == groupe)
    n = len(C)
    chemin = "/cours/"
    titre = "Cours et TD d'éducation civique, du collège au lycée : institutions, lois, élections"
    desc = f"{n} cours et TD corrigés, neutres et gratuits, du collège au lycée : institutions, vote des lois, élections, libertés, justice, médias. En ligne et en PDF."
    corps = f"""<h1>Cours et TD</h1><p class="lede">{n} cours courts, chacun avec un TD et son corrigé, pour comprendre le fonctionnement de la démocratie. Conçus pour la classe, utilisables seul.</p>
<h2>Collège (3e)</h2><p class="meta">Les bases : qui décide, comment, et comment s'informer.</p><ul class="cartes">{cartes("college")}</ul>
<h2>Lycée</h2><p class="meta">Pour aller plus loin : procédures, calculs, textes de droit, analyse et rédaction.</p><ul class="cartes">{cartes("lycee")}</ul>
<h2>Pour les enseignants</h2><p>Chaque cours est lisible en ligne et téléchargeable en PDF, avec le TD (version élève) et le corrigé (version enseignant). Ils sont en lien avec l'éducation morale et civique (EMC) et peuvent servir en histoire-géographie. Le contenu reste factuel et neutre : aucune opinion n'est demandée aux élèves, seulement l'analyse de textes et de faits vérifiables. Ces supports sont rédigés avec l'aide d'une intelligence artificielle à partir de sources officielles : les enseignants restent libres de les adapter, et les textes cités font foi.</p>
<p>Pour illustrer un cours avec un texte réel : <a href="/lois-par-theme/">les lois par thème</a>, <a href="/lexique/">le lexique</a>.</p>"""
    g.page(chemin, titre, desc, corps, jsonld=_ld(g, chemin, titre, desc, [("Cours et TD", chemin)]), og_type="website")
    g.urls.setdefault("fonds", []).append((chemin, g.aujourdhui))
