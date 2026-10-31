#!/usr/bin/env python3
"""Aux Voix : pages « de fond » pour les moteurs de recherche et les enseignants.
- trois pages d'explication (comment une loi est votée ; projet ou proposition de loi ; le 49.3) ;
- le lexique complet (lu dans app.js, une seule source) ;
- une page par thème (logement, santé, éducation…) qui liste les fiches ;
- une image de partage par fiche (si Pillow est installé ; sinon l'image commune est conservée).
Tout est neutre : ce sont des faits de la Constitution et du règlement des assemblées."""
import html, json, os, re, unicodedata

ESC = lambda s: html.escape(str(s if s is not None else ""), quote=True)


def norm(s):
    return unicodedata.normalize("NFKD", str(s).lower()).encode("ascii", "ignore").decode()


# ---------------------------------------------------------------- données lues dans app.js
def lire_themes(app_js):
    """[(slug, libellé, regex)] : la même liste de mots-clés que l'application (une seule source)."""
    s = open(app_js, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'^\s*\["([a-z]+)","([^"]+)",RX\("((?:[^"\\]|\\.)*)"\)\]', s, re.M):
        try:
            out.append((m.group(1), m.group(2), re.compile(r"\b(?:" + m.group(3).replace("\\\\", "\\") + ")")))
        except re.error:
            pass
    return out


def lire_lexique(app_js):
    s = open(app_js, encoding="utf-8").read()
    i = s.index("const LEX=[")
    j = s.index("\n];", i)
    out = []
    for m in re.finditer(r'^\s*\["([^"]+)","([^"]+)","((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)"(?:,(?:"([^"]*)"|null))?(?:,[^\]\n]*)?\]', s[i:j + 3], re.M):
        lien = m.group(5) or ""
        if lien.startswith("#/"):
            lien = "/" + lien
        out.append((m.group(1), m.group(2), json.loads('"' + m.group(4) + '"'), lien))
    return out


def charger_themes(site):
    """Thèmes de l'application + thèmes ajoutés + thème choisi à la main pour chaque fiche."""
    liste = lire_themes(os.path.join(site, "app.js"))
    choix, extra = {}, {}
    try:
        j = json.load(open(os.path.join(site, "contenu", "themes_fiches.json"), encoding="utf-8"))
        choix, extra = j.get("fiches") or {}, j.get("extra") or {}
    except Exception:
        pass
    libs = {s: l for s, l, _ in liste}
    intro = dict(INTRO_THEME)
    for s, v in extra.items():
        libs[s] = v[0]
        intro[s] = v[1]
    return {"liste": liste, "choix": choix, "libs": libs, "intro": intro}


def theme_fiche(dossier, titre, T):
    """(slug, libellé) : le choix fait à la main, sinon les mots du titre."""
    s = T["choix"].get(dossier.split("N")[-1])
    if s and s in T["libs"]:
        return s, T["libs"][s]
    return theme_de(titre, T["liste"])


def theme_de(titre, themes):
    t = norm(titre)
    for slug, lib, rx in themes:
        if rx.search(t):
            return slug, lib
    return None, None


# ---------------------------------------------------------------- pages d'explication
def fil(*liens):
    return '<p class="fil">' + ", ".join(f'<a href="{h}">{ESC(t)}</a>' for h, t in liens) + "</p>"


EXPLICATIONS = {
    "comment-une-loi-est-votee": {
        "titre": "Comment une loi est-elle votée en France ?",
        "seo": "Comment une loi est votée en France : les étapes, du dépôt à la promulgation",
        "desc": "Du dépôt d'un texte à sa publication au Journal officiel : l'Assemblée nationale, le Sénat, la navette, la commission mixte paritaire, le Conseil constitutionnel et la promulgation, expliqués simplement.",
        "lede": "Une loi passe par plusieurs étapes avant d'entrer en vigueur : un texte est déposé, discuté et voté par l'Assemblée nationale et par le Sénat, parfois contrôlé par le Conseil constitutionnel, puis promulgué par le président de la République.",
        "corps": """
<h2>1. Un texte est déposé</h2>
<p>Un texte de loi naît de deux façons : le Gouvernement dépose un <strong>projet de loi</strong>, ou un député ou un sénateur dépose une <strong>proposition de loi</strong> (<a href="/comprendre/projet-de-loi-proposition-de-loi/">voir la différence</a>). Il est déposé sur le bureau de l'Assemblée nationale ou du Sénat. Les projets de loi sont d'abord examinés par le Conseil d'État, puis adoptés en Conseil des ministres.</p>
<h2>2. La commission l'examine</h2>
<p>Avant d'arriver dans l'hémicycle, le texte est étudié par une commission (affaires sociales, lois, finances…). Un <strong>rapporteur</strong> le présente. Les élus peuvent proposer des <strong>amendements</strong>, c'est-à-dire des modifications, que la commission adopte ou rejette.</p>
<h2>3. Le débat et le vote en séance publique</h2>
<p>Le texte est ensuite discuté dans l'hémicycle, article par article. Les amendements sont votés, puis l'assemblée vote sur l'<strong>ensemble du texte</strong>. Le vote peut se faire à main levée, ou par <strong>scrutin public</strong> : dans ce cas, le choix de chaque député est enregistré et publié.</p>
<h2>4. La navette entre les deux assemblées</h2>
<p>Pour devenir une loi, un texte doit être adopté <strong>dans les mêmes termes</strong> par l'Assemblée nationale et par le Sénat. Il fait donc des allers-retours entre les deux : c'est la <strong>navette parlementaire</strong>. Chaque passage dans une assemblée s'appelle une lecture.</p>
<h2>5. Si les deux assemblées ne sont pas d'accord</h2>
<p>Une <strong>commission mixte paritaire</strong> (CMP) réunit 7 députés et 7 sénateurs pour proposer un texte de compromis. Si ce texte est adopté par les deux assemblées, la loi est votée. En cas d'échec, le Gouvernement peut demander une nouvelle lecture, puis une lecture définitive : l'Assemblée nationale a alors le dernier mot.</p>
<p>Le Gouvernement peut aussi demander la <strong>procédure accélérée</strong> : la CMP peut alors être réunie après une seule lecture dans chaque assemblée.</p>
<h2>6. Le contrôle du Conseil constitutionnel</h2>
<p>Avant sa promulgation, une loi peut être soumise au <strong>Conseil constitutionnel</strong>, qui vérifie qu'elle respecte la Constitution. Il peut être saisi par le président de la République, le Premier ministre, les présidents des assemblées, ou par 60 députés ou 60 sénateurs. Il rend sa décision en un mois au plus. Il peut valider la loi, la censurer en partie ou en totalité, ou la valider en précisant comment l'appliquer.</p>
<h2>7. La promulgation et la publication</h2>
<p>Le président de la République <strong>promulgue</strong> la loi dans les quinze jours qui suivent son adoption définitive. Elle est ensuite publiée au <strong>Journal officiel</strong> et entre en vigueur. Souvent, des <strong>décrets d'application</strong> du Gouvernement précisent comment elle s'applique.</p>
<h2>Et le 49.3 ?</h2>
<p>Dans certains cas, le Premier ministre peut faire adopter un texte sans vote : c'est l'<a href="/comprendre/article-49-3/">article 49, alinéa 3</a> de la Constitution.</p>
<h2>Suivre un texte sur Aux Voix</h2>
<p>Chaque fiche de loi d'Aux Voix indique où en est le texte, ce qu'il change, les arguments de chaque camp et le détail des votes. <a href="/lois-par-theme/">Parcourir les lois par thème</a>.</p>
<p class="meta">Sources : Constitution du 4 octobre 1958 (articles 39, 42, 45, 46, 61, 10 et 49) ; règlements de l'Assemblée nationale et du Sénat.</p>""",
    },
    "projet-de-loi-proposition-de-loi": {
        "titre": "Projet de loi ou proposition de loi : quelle différence ?",
        "seo": "Projet de loi ou proposition de loi : la différence expliquée simplement",
        "desc": "Un projet de loi vient du Gouvernement, une proposition de loi vient d'un député ou d'un sénateur. Ce qui change dans leur parcours, avec des exemples.",
        "lede": "La différence tient à l'auteur du texte : un projet de loi est déposé par le Gouvernement, une proposition de loi par un ou plusieurs parlementaires.",
        "corps": """
<h2>Le projet de loi : le texte du Gouvernement</h2>
<p>Un <strong>projet de loi</strong> est préparé par le Gouvernement, sur décision du Premier ministre. Il est examiné par le <strong>Conseil d'État</strong>, qui donne un avis, puis adopté en Conseil des ministres avant d'être déposé devant l'Assemblée nationale ou le Sénat. Les lois de finances (le budget de l'État) et les lois de financement de la Sécurité sociale sont des projets de loi.</p>
<h2>La proposition de loi : le texte des parlementaires</h2>
<p>Une <strong>proposition de loi</strong> est déposée par un député ou un sénateur, seul ou avec d'autres. Elle ne passe pas obligatoirement par le Conseil d'État. Les groupes d'opposition ou minoritaires peuvent faire examiner leurs propres propositions de loi lors de la journée qui leur est réservée chaque mois, appelée parfois « niche parlementaire ».</p>
<h2>Ce qui est pareil ensuite</h2>
<p>Une fois déposés, les deux types de textes suivent le même parcours : examen en commission, débat et vote en séance, navette entre l'Assemblée nationale et le Sénat, éventuel contrôle du Conseil constitutionnel, puis promulgation. <a href="/comprendre/comment-une-loi-est-votee/">Voir toutes les étapes</a>.</p>
<h2>Et les accords internationaux ?</h2>
<p>Pour qu'un traité ou un accord international signé par la France s'applique dans certains domaines, le Parlement doit l'approuver. Cela passe par un projet de loi « autorisant l'approbation » de l'accord. De nombreux textes de ce type sont adoptés sans vote public.</p>
<h2>Un exemple sur Aux Voix</h2>
<p>Sur le site, le titre de chaque fiche commence par « Projet de loi » ou « Proposition de loi » : c'est ce qui indique d'où vient le texte. <a href="/lois-par-theme/">Parcourir les fiches par thème</a>.</p>
<p class="meta">Sources : Constitution du 4 octobre 1958 (articles 39 et 48) ; règlements de l'Assemblée nationale et du Sénat.</p>""",
    },
    "article-49-3": {
        "titre": "Le 49.3, c'est quoi ?",
        "seo": "Le 49.3 : c'est quoi, comment ça marche, qui peut s'y opposer ?",
        "desc": "L'article 49, alinéa 3 de la Constitution permet au Premier ministre de faire adopter un texte sans vote, sauf si une motion de censure est adoptée. Les règles, expliquées simplement.",
        "lede": "Le 49.3 est une procédure de la Constitution : le Premier ministre engage la responsabilité du Gouvernement sur un texte, qui est alors considéré comme adopté sans vote, sauf si une motion de censure renverse le Gouvernement.",
        "corps": """
<h2>Comment ça marche</h2>
<p>L'<strong>article 49, alinéa 3</strong> de la Constitution permet au Premier ministre, après délibération du Conseil des ministres, d'engager la responsabilité du Gouvernement devant l'Assemblée nationale sur le vote d'un texte.</p>
<ol class="l">
<li>Le Premier ministre annonce l'utilisation du 49.3 en séance.</li>
<li>Le texte n'est pas mis aux voix. Il est <strong>considéré comme adopté</strong>, sauf si une <strong>motion de censure</strong> est déposée dans les <strong>24 heures</strong> et adoptée.</li>
<li>Les députés qui veulent s'y opposer peuvent déposer une motion de censure. Elle doit être signée par au moins un dixième des députés (58).</li>
<li>La motion est votée. Pour être adoptée, elle doit réunir la <strong>majorité absolue des membres</strong> de l'Assemblée : 289 voix sur 577. Seules les voix « pour » comptent.</li>
<li>Si la motion est adoptée, le texte est rejeté et le Gouvernement doit remettre sa démission au président de la République. Sinon, le texte est adopté.</li>
</ol>
<h2>Dans quels cas peut-on l'utiliser ?</h2>
<p>Depuis la révision constitutionnelle de 2008, le 49.3 peut être utilisé pour les <strong>projets de loi de finances</strong> et les <strong>projets de loi de financement de la Sécurité sociale</strong>, ainsi que pour <strong>un seul autre texte par session</strong>.</p>
<h2>Les arguments des uns et des autres</h2>
<p>Ceux qui défendent la procédure estiment qu'elle permet de faire adopter un texte quand aucune majorité claire ne se dégage, tout en laissant à l'Assemblée la possibilité de renverser le Gouvernement. Ceux qui la critiquent estiment qu'elle réduit le débat et le vote des députés sur le texte lui-même. Les deux positions sont défendues à droite comme à gauche, selon que l'on est au Gouvernement ou dans l'opposition.</p>
<h2>Le retrouver sur Aux Voix</h2>
<p>Les motions de censure sont des votes publics : on peut voir qui a voté pour ou contre. <a href="/#/votes">Voir les votes</a>. Pour lire l'article de la Constitution, <a href="/#/code/constitution/49">c'est ici</a>.</p>
<p class="meta">Sources : Constitution du 4 octobre 1958, article 49 ; règlement de l'Assemblée nationale.</p>""",
    },
}


def _ld(g, chemin, titre, desc, fil_noms):
    items = [{"@type": "ListItem", "position": 1, "name": "Aux Voix", "item": g.url + "/"}]
    for k, (nom, ch) in enumerate(fil_noms, 2):
        items.append({"@type": "ListItem", "position": k, "name": nom, "item": g.url + ch})
    return [{"@context": "https://schema.org", "@type": "Article", "headline": titre[:110], "description": desc, "inLanguage": "fr", "mainEntityOfPage": g.url + chemin,
             "image": g.url + "/icones/partage.png", "author": {"@type": "Organization", "name": "Aux Voix", "url": g.url},
             "publisher": {"@type": "Organization", "name": "Aux Voix", "url": g.url, "logo": {"@type": "ImageObject", "url": g.url + "/icones/partage.png"}},
             "dateModified": g.aujourdhui},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]


def pages_explication(g):
    for slug, p in EXPLICATIONS.items():
        chemin = f"/comprendre/{slug}/"
        corps = f"""{fil(("/#/comprendre", "Comprendre"))}<h1>{ESC(p['titre'])}</h1><p class="lede">{ESC(p['lede'])}</p>{p['corps']}"""
        g.page(chemin, p["seo"], p["desc"], corps, jsonld=_ld(g, chemin, p["titre"], p["desc"], [("Comprendre", "/#/comprendre"), (p["titre"], chemin)]), og_type="article")
        g.urls.setdefault("fonds", []).append((chemin, g.aujourdhui))


def page_lexique(g, lex):
    if not lex:
        return
    chemin = "/lexique/"
    n = len(lex)
    dl = "".join(f'<dt id="{ESC(e[0])}">{ESC(e[1])}</dt><dd>{ESC(e[2])}' + (f' <a href="{ESC(e[3])}">En savoir plus</a>' if e[3] else "") + "</dd>" for e in sorted(lex, key=lambda e: norm(e[1])))
    corps = f"""{fil(("/#/comprendre", "Comprendre"))}<h1>Lexique de la vie politique et parlementaire</h1>
<p class="lede">{n} mots que l'on entend à l'Assemblée nationale, au Sénat et pendant les élections, expliqués en une ou deux phrases.</p><dl>{dl}</dl>
<p class="meta">Définitions rédigées d'après la Constitution et le règlement de l'Assemblée nationale. Une erreur ? <a href="/#/signaler?p=lexique">Signalez-la</a>.</p>"""
    titre = f"Lexique politique : {n} mots expliqués simplement"
    desc = "Amendement, navette, 49.3, motion de censure, dissolution, parrainage, scrutin public… le vocabulaire de l'Assemblée nationale et des élections, expliqué simplement."
    ld = _ld(g, chemin, "Lexique de la vie politique et parlementaire", desc, [("Comprendre", "/#/comprendre"), ("Lexique", chemin)])
    ld.append({"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Lexique Aux Voix", "inLanguage": "fr",
               "hasDefinedTerm": [{"@type": "DefinedTerm", "name": e[1], "description": e[2], "url": g.url + chemin + "#" + e[0]} for e in lex]})
    g.page(chemin, titre, desc, corps, jsonld=ld, og_type="article")
    g.urls.setdefault("fonds", []).append((chemin, g.aujourdhui))


# ---------------------------------------------------------------- thèmes
INTRO_THEME = {
    "agriculture": "agriculteurs, alimentation, pêche et forêts",
    "logement": "logement, loyers, urbanisme et immobilier",
    "energie": "énergie, climat, eau, déchets et environnement",
    "sante": "santé, hôpitaux, soins et fin de vie",
    "social": "travail, emploi, retraites et protection sociale",
    "economie": "budget de l'État, impôts, entreprises et commerce",
    "securite": "police, justice, prisons et sécurité",
    "immigration": "immigration, asile et nationalité",
    "education": "école, université, recherche et apprentissage",
    "numerique": "internet, données, réseaux sociaux et intelligence artificielle",
    "transports": "trains, routes, avions et mobilité",
    "institutions": "élections, collectivités, outre-mer et fonctionnement des institutions",
    "defense": "défense, armées, traités et accords internationaux",
    "culture": "culture, sport, médias et patrimoine",
}


def charger_fiches(site):
    rep = os.path.join(site, "contenu", "fiches")
    out = []
    for fn in (sorted(os.listdir(rep)) if os.path.isdir(rep) else []):
        try:
            f = json.load(open(os.path.join(rep, fn), encoding="utf-8"))
        except Exception:
            continue
        if isinstance(f, dict) and f.get("publie") is True and f.get("dossier") and f.get("titre_officiel"):
            out.append(f)
    return out


def pages_themes(g, T, fiches):
    existantes = {c for c, _ in g.urls.get("lois", [])}
    par = {}
    for f in fiches:
        slug, _ = theme_fiche(f["dossier"], f["titre_officiel"], T)
        if slug and f"/loi/{f['dossier']}/" in existantes:
            par.setdefault(slug, []).append(f)
    lib = T["libs"]
    hub = []
    for slug, L in sorted(par.items(), key=lambda kv: -len(kv[1])):
        chemin = f"/theme/{slug}/"
        nom = lib[slug]
        L.sort(key=lambda f: (f.get("version") or {}).get("date", ""), reverse=True)
        items = "".join(
            f'<li><a href="/loi/{ESC(f["dossier"])}/"><span class="h">{ESC(f["titre_officiel"][:1].upper() + f["titre_officiel"][1:])}</span>'
            + (f'<span class="d">{ESC(f.get("phrase", ""))}' + (f" {ESC(f['note'])}" if f.get("note") else "") + "</span>" if f.get("phrase") else "") + "</a></li>" for f in L)
        titre = f"{nom} : les lois et propositions de loi, ce qui change et qui a voté"
        desc = f"{len(L)} textes concernant {T['intro'].get(slug, nom.lower())} : pour chacun, ce qui change, les arguments de chaque camp, le parcours et les votes. Sources officielles."
        corps = f"""{fil(("/lois-par-theme/", "Lois par thème"))}<h1>{ESC(nom)}</h1>
<p class="lede">{len(L)} textes concernant {ESC(T['intro'].get(slug, nom.lower()))}. Pour chacun : ce qui change, les arguments de chaque camp, le parcours au Parlement et les votes.</p>
<ul class="textes">{items}</ul>
<p class="meta">Chaque texte est rangé dans un seul thème, choisi par la rédaction d'après son objet principal. Un texte peut toucher plusieurs sujets.</p>"""
        g.page(chemin, titre, desc, corps, jsonld=_ld(g, chemin, titre, desc, [("Lois par thème", "/lois-par-theme/"), (nom, chemin)]), og_type="article")
        g.urls.setdefault("fonds", []).append((chemin, g.aujourdhui))
        hub.append((slug, nom, len(L)))
    if hub:
        chemin = "/lois-par-theme/"
        lis = "".join(f'<li><a href="/theme/{s}/"><span class="n">{k} texte{"s" if k > 1 else ""}</span><span class="h">{ESC(n)}</span><span class="d">{ESC(T["intro"].get(s, "")[:1].upper() + T["intro"].get(s, "")[1:])}</span></a></li>' for s, n, k in hub)
        titre = "Les lois par thème : logement, santé, école, travail, sécurité…"
        desc = "Retrouvez les lois et propositions de loi classées par thème : logement, santé, éducation, travail, sécurité, énergie… avec, pour chacune, une explication simple et les votes."
        corps = f"""{fil(("/#/lois", "Lois"))}<h1>Les lois par thème</h1><p class="lede">Choisissez un sujet pour voir les textes qui le concernent.</p><ul class="cartes">{lis}</ul>
<p>Pour comprendre le parcours d'un texte : <a href="/comprendre/comment-une-loi-est-votee/">comment une loi est votée</a>, <a href="/comprendre/projet-de-loi-proposition-de-loi/">projet ou proposition de loi</a>, <a href="/lexique/">le lexique</a>.</p>"""
        g.page(chemin, titre, desc, corps, jsonld=_ld(g, chemin, titre, desc, [("Lois par thème", chemin)]), og_type="article")
        g.urls.setdefault("fonds", []).append((chemin, g.aujourdhui))


# ---------------------------------------------------------------- images de partage
def _police(taille, poids=600):
    from PIL import ImageFont
    chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site", "fonts", "Lexend.ttf")
    f = ImageFont.truetype(chemin, taille)
    try:
        f.set_variation_by_axes([poids])
    except Exception:
        pass
    return f


def _lignes(dessin, texte, police, largeur, max_lignes):
    mots, lignes, cour = texte.split(), [], ""
    for m in mots:
        essai = (cour + " " + m).strip()
        if dessin.textlength(essai, font=police) <= largeur:
            cour = essai
        else:
            lignes.append(cour)
            cour = m
    lignes.append(cour)
    if len(lignes) > max_lignes:
        lignes = lignes[:max_lignes]
        lignes[-1] = lignes[-1].rstrip(" ,;:.") + "…"
    return lignes


def image_partage(fichier, etiquette, texte, bas):
    from PIL import Image, ImageDraw
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (18, 59, 109))
    d = ImageDraw.Draw(im)
    # emblème : quatre arcs en trois segments, comme le logo
    cx, cy = 1060, 150
    for r in (28, 56, 84, 112):
        for a, b in ((180, 234), (246, 294), (306, 360)):
            d.arc([cx - r, cy - r, cx + r, cy + r], a, b, fill=(255, 255, 255), width=10)
    d.text((70, 62), etiquette.upper(), font=_police(26, 600), fill=(190, 212, 238))
    f = _police(50, 600)
    y = 130
    # les deux premières lignes restent à gauche de l'emblème, les suivantes prennent toute la largeur
    mots, lignes, cour, restant = texte.split(), [], "", 6
    for m in mots:
        larg = 840 if len(lignes) < 2 else 1050
        essai = (cour + " " + m).strip()
        if d.textlength(essai, font=f) <= larg:
            cour = essai
        else:
            lignes.append(cour)
            cour = m
    lignes.append(cour)
    if len(lignes) > restant:
        lignes = lignes[:restant]
        lignes[-1] = lignes[-1].rstrip(" ,;:.") + "…"
    for ligne in lignes:
        d.text((70, y), ligne, font=f, fill=(255, 255, 255))
        y += 68
    d.text((70, H - 96), bas, font=_police(26, 400), fill=(190, 212, 238))
    d.text((70, H - 56), "Aux Voix", font=_police(34, 800), fill=(255, 255, 255))
    d.text((W - 70 - d.textlength("auxvoix.fr", font=_police(26, 400)), H - 52), "auxvoix.fr", font=_police(26, 400), fill=(190, 212, 238))
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    im.save(fichier, optimize=True)


def images_fiches(g, fiches):
    """Une image de partage par fiche, dans site/partage/. Renvoie {dossier: chemin} (vide sans Pillow)."""
    try:
        import PIL  # noqa: F401
    except Exception:
        print("Images de partage : Pillow absent, image commune conservée.")
        return {}
    out = {}
    for f in fiches:
        try:
            statut = (f.get("note") or "").strip().split(". ")[0].rstrip(".")
            if len(statut) > 72 and ", " in statut:
                statut = statut.split(", ")[0]
            if len(statut) > 72:
                statut = statut[:72].rsplit(" ", 1)[0] + "…"
            image_partage(os.path.join(g.site, "partage", f["dossier"] + ".png"), "Loi · ce qui change", f.get("phrase", "") or f["titre_officiel"], statut)
            out[f["dossier"]] = f"/partage/{f['dossier']}.png"
        except Exception as e:
            print(f"Image de partage {f.get('dossier')} : {e}")
    return out


def generer_fonds(g):
    app = os.path.join(g.site, "app.js")
    fiches = charger_fiches(g.site)
    T = charger_themes(g.site) if os.path.exists(app) else None
    lex = lire_lexique(app) if os.path.exists(app) else []
    pages_explication(g)
    try:
        from avis import pages_avis
        pages_avis(g)
    except ImportError:
        pass
    try:
        from cours import pages_cours
        pages_cours(g)
    except ImportError:
        pass
    page_lexique(g, lex)
    if T:
        pages_themes(g, T, fiches)
