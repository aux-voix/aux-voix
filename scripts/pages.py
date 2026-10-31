#!/usr/bin/env python3
"""Aux Voix : pages statiques lisibles par les moteurs de recherche (députés, votes, lois, articles de code),
plan du site, robots.txt et flux RSS. Un seul interrupteur, "public" dans contenu/site.json, ouvre le site à
l'indexation ; tant qu'il vaut false, chaque page porte noindex et robots.txt interdit l'exploration."""
import datetime, html, json, os, re, statistics, unicodedata
from email.utils import format_datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fonds import theme_fiche, generer_fonds, images_fiches, charger_fiches, charger_themes

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
ESC = lambda s: html.escape(str(s if s is not None else ""), quote=True)


def fd(iso):
    if not iso:
        return ""
    a, m, j = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return f"{'1er' if j == 1 else j} {MOIS[m - 1]} {a}"


def ordinal(k):
    return "1re" if k == 1 else f"{k}e"


def pc(x):
    return "—" if x is None else f"{round(x * 100)}\u00a0%"


def slug_num(n):
    return re.sub(r"[^A-Za-z0-9-]+", "-", n.replace(".", "")).strip("-") or "0"


def mediane(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


CSS = """@font-face{font-family:"Lexend";src:url("/fonts/Lexend.woff2") format("woff2"),url("/fonts/Lexend.ttf") format("truetype");font-weight:300 800;font-display:swap}
@font-face{font-family:"Source Sans 3";src:url("/fonts/SourceSans3.woff2") format("woff2"),url("/fonts/SourceSans3.ttf") format("truetype");font-weight:200 900;font-display:swap}
:root{--t:#1B1D1F;--t2:#5A6169;--b:#DDE1E5;--b2:#EDF0F3;--g:#F5F7F9;--bl:#123B6D;--bl2:#1B58A3;--blc:#EAF0F7;--pour:#1F6FB2;--contre:#B42318;--abst:#8A9099}
*{box-sizing:border-box}body{margin:0;font:400 16.5px/1.6 "Source Sans 3",Helvetica,Arial,sans-serif;color:var(--t);background:#fff}
a{color:var(--bl2);text-underline-offset:.18em}h1,h2,h3{font-family:"Lexend","Source Sans 3",Arial,sans-serif;font-weight:600;letter-spacing:-.015em;line-height:1.22;margin:0}
.w{max-width:900px;margin:0 auto;padding:0 20px}.beta{background:var(--blc);border-bottom:1px solid #D2DFEC;font-size:14px;padding:8px 0}
header{border-bottom:1px solid var(--b)}header .w{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;min-height:62px}
.logo{display:inline-flex;align-items:center;gap:9px;font:20px/1 "Lexend",Arial,sans-serif;letter-spacing:-.03em;color:var(--t);text-decoration:none}.logo .emb{width:40px;height:22px;color:var(--bl)}.logo .wm1{font-weight:300}.logo .wm2{font-weight:800;color:var(--bl)}
nav a{display:inline-block;padding:6px 0;min-height:24px;font-weight:600;color:var(--t);text-decoration:none;margin-right:16px;font-size:15px}nav a:hover{color:var(--bl2)}
main{padding:30px 0 50px}.fil{font-size:14px;color:var(--t2);margin:0 0 6px}h1{font-size:clamp(24px,3.4vw,32px);margin-bottom:10px}
h2{font-size:20px;margin:30px 0 10px;padding-bottom:8px;border-bottom:2px solid var(--t)}.lede{font-size:18px;color:var(--t2);margin:0 0 14px}
.cta{display:inline-block;background:var(--bl);color:#fff;text-decoration:none;font-weight:600;padding:10px 16px;margin:8px 10px 8px 0}.cta:hover{background:var(--bl2)}
.cta.s{background:#fff;color:var(--t);border:1px solid var(--b)}dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:12px 0}dt{color:var(--t2)}dd{margin:0}
table{border-collapse:collapse;width:100%;font-size:15px}th{text-align:left;border-bottom:2px solid var(--t);padding:8px 10px 8px 0;font-size:14px}td{border-bottom:1px solid var(--b2);padding:9px 10px 9px 0;vertical-align:top}
.v{font-weight:600;white-space:nowrap}.v:before{content:"";display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;background:var(--c,var(--abst))}
.v1{--c:var(--pour)}.v2{--c:var(--contre)}.v3{--c:var(--abst)}.art{border-left:4px solid var(--bl);background:var(--g);padding:16px 20px;font-size:18px;line-height:1.65;margin:16px 0}
.art p{margin:0 0 .6em}.cite{border:1px solid var(--b);padding:12px 16px;margin:18px 0;font-size:15px}.cite p{margin:0 0 6px}.cite button{font:600 14px inherit;padding:6px 10px;border:1px solid var(--b);background:#fff;cursor:pointer;margin-right:6px}
.cite button:hover{border-color:var(--bl2);color:var(--bl2)}.meta{font-size:14px;color:var(--t2)}.noms{font-size:14.5px;line-height:1.7}ul.l{padding-left:1.1em}
footer{border-top:1px solid var(--b);background:var(--g);font-size:14px;color:var(--t2);padding:22px 0}footer a{margin-right:14px}
ol.q{padding-left:1.3em}ol.q>li{margin:0 0 12px}ol.choix{margin:4px 0 0;padding-left:1.4em;color:var(--t2)}ul.retenir{padding-left:1.2em}ul.retenir li{margin-bottom:4px}
div.avis-act{margin:14px 0 6px}.encart{border:1px solid var(--b);border-top:3px solid #F3C24F;border-left:4px solid var(--bl);background:var(--blc);padding:12px 18px;margin:14px 0}.encart ul{margin:0;padding-left:1.1em}.encart li{margin:4px 0}.encart.att{border-left-color:#F3C24F;background:#FFF8E5}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}#avis-cadre iframe{border:1px solid var(--b);min-height:700px;background:#fff}button.cta{font-family:inherit;font-weight:600;font-size:16.5px;line-height:1.6;border:1px solid var(--bl);cursor:pointer}a:focus-visible,button:focus-visible,iframe:focus-visible,summary:focus-visible{outline:3px solid #F3C24F;outline-offset:2px}.beta a{margin-left:14px;font-weight:600}
details.corr{border:1px solid var(--b);background:var(--g);padding:12px 18px;margin:18px 0}details.corr summary{cursor:pointer;font-weight:600}h3{font-size:18px;margin:22px 0 6px}
.tw{overflow-x:auto;margin:0 0 8px}.cite span,.art,.lede,dd{overflow-wrap:anywhere}
ul.cartes{list-style:none;padding:0;margin:20px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
ul.cartes li{margin:0}ul.cartes a{display:flex;flex-direction:column;gap:6px;height:100%;padding:16px 18px;border:1px solid var(--b);border-left:4px solid var(--bl);background:#fff;color:var(--t);text-decoration:none}
ul.cartes a:hover,ul.cartes a:focus-visible{background:var(--blc);border-color:var(--bl2)}ul.cartes .h{font:600 17px/1.25 "Lexend","Source Sans 3",Arial,sans-serif;color:var(--bl)}
ul.cartes .n{font-size:13px;font-weight:600;color:var(--bl2);text-transform:uppercase;letter-spacing:.04em}ul.cartes .d{font-size:15px;color:var(--t2);line-height:1.45}
ul.textes{list-style:none;padding:0;margin:18px 0}ul.textes li{margin:0;border-bottom:1px solid var(--b2)}ul.textes a{display:block;padding:14px 4px;color:var(--t);text-decoration:none}
ul.textes a:hover,ul.textes a:focus-visible{background:var(--g)}ul.textes .h{display:block;font-weight:600;font-size:17px;line-height:1.35;color:var(--bl)}ul.textes a:hover .h{text-decoration:underline}
ul.textes .d{display:block;margin-top:3px;font-size:15px;color:var(--t2);line-height:1.45}
@media(max-width:600px){dl{grid-template-columns:1fr;gap:2px}dd{margin-bottom:8px}table{font-size:14px}}"""

JS = """document.addEventListener("click",function(e){var b=e.target.closest("[data-copie]");if(!b)return;var t=document.getElementById(b.getAttribute("data-copie")).textContent;
function ok(){var x=b.textContent;b.textContent="Copié";setTimeout(function(){b.textContent=x;},1500);}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok);}else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy");ok();}catch(_){}a.remove();}});
/* Visites comptées par GoatCounter, sans cookie ni script tiers (voir app.js) : seulement si le site l'active, sur sa propre adresse */
(function(){var m=document.querySelector('meta[name="av-mesure"]'),c=document.querySelector('link[rel="canonical"]');if(!m||!c)return;
var r=false;try{r=localStorage.getItem("skipgc")==="t";}catch(_){}if(r||navigator.globalPrivacyControl===true||navigator.doNotTrack==="1"||navigator.webdriver)return;
var h=function(x){return x.replace(/^www\\./,"");};if(location.protocol!=="https:"||h(location.hostname)!==h(new URL(c.href).hostname))return;
var q={p:location.pathname,t:document.title,r:document.referrer,s:screen.width,rnd:Math.random().toString(36).slice(2,7)},u=m.content+"?";
for(var k in q)if(q[k]!=="")u+=k+"="+encodeURIComponent(q[k])+"&";
var go=function(){try{if(navigator.sendBeacon&&navigator.sendBeacon(u))return;}catch(_){}new Image().src=u;};
if(window.requestIdleCallback)requestIdleCallback(go,{timeout:4000});else setTimeout(go,1500);})();"""


class Generateur:
    def __init__(self, site_dir):
        self.site = site_dir
        cfg = {}
        try:
            cfg = json.load(open(os.path.join(site_dir, "contenu", "site.json"), encoding="utf-8"))
        except Exception:
            pass
        self.public = bool(cfg.get("public"))
        self.url = (cfg.get("url") or "https://auxvoix.fr").rstrip("/")
        from urllib.parse import urlparse
        self.base = urlparse(self.url).path.rstrip("/")   # « /Auxvoix.github.io » si le site n'est pas à la racine
        gc = str((cfg.get("mesure_audience") or {}).get("goatcounter") or "").strip().lower()
        # compteur de visites (GoatCounter) : rien n'est chargé depuis un autre site, statique.js envoie un seul appel
        self.audience = (f'<meta name="av-mesure" content="https://{gc}.goatcounter.com/count">'
                         if re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", gc) else "")
        self.urls = {"deputes": [], "votes": [], "lois": [], "codes": [], "fonds": []}
        self.deputes_faits = set()   # un député élu sous plusieurs législatures garde la page de la plus récente
        self.aujourdhui = datetime.date.today().isoformat()
        self.images = {}      # image de partage propre à chaque fiche (dossier -> chemin), si Pillow est disponible
        self.themes = None    # thèmes (voir fonds.py)

    def page(self, chemin, titre, description, corps, canonique=True, rss=None, jsonld=None, og_type="website", image=None):
        robots = "" if self.public else '<meta name="robots" content="noindex, nofollow">\n'
        ld = "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace("</", "<\\/") + "</script>\n" for x in (jsonld or []))
        alt = f'<link rel="alternate" type="application/rss+xml" title="{ESC(rss[1])}" href="{ESC(rss[0])}">\n' if rss else ""
        doc = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ESC(titre)} | Aux Voix</title><link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="icon" href="/favicon.ico" sizes="48x48">{self.audience}<meta name="description" content="{ESC(description[:300])}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Aux Voix"><meta property="og:locale" content="fr_FR"><meta property="og:title" content="{ESC(titre)}"><meta property="og:description" content="{ESC(description[:200])}"><meta property="og:url" content="{ESC(self.url + chemin)}"><meta property="og:image" content="{ESC(self.url)}{ESC(image or "/icones/partage.png")}"><meta name="twitter:card" content="summary_large_image">
{robots}<link rel="canonical" href="{ESC(self.url + chemin)}">{alt}{ld}<link rel="stylesheet" href="/statique.css"></head><body>
{'' if self.public else '<aside class="beta" aria-label="État du site"><div class="w">Version bêta du site.<a href="/avis/">Donner mon avis</a></div></aside>'}
<header><div class="w"><a class="logo" href="/" aria-label="Aux Voix, accueil"><svg class="emb" viewBox="0 2 120 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round"><path d="M43.0 60.0 A17 17 0 0 1 50.0 46.2"/><path d="M53.1 44.5 A17 17 0 0 1 66.9 44.5"/><path d="M70.0 46.2 A17 17 0 0 1 77.0 60.0"/><path d="M32.0 60.0 A28 28 0 0 1 43.5 37.3"/><path d="M48.6 34.4 A28 28 0 0 1 71.4 34.4"/><path d="M76.5 37.3 A28 28 0 0 1 88.0 60.0"/><path d="M21.0 60.0 A39 39 0 0 1 37.1 28.4"/><path d="M44.1 24.4 A39 39 0 0 1 75.9 24.4"/><path d="M82.9 28.4 A39 39 0 0 1 99.0 60.0"/><path d="M10.0 60.0 A50 50 0 0 1 30.6 19.5"/><path d="M39.7 14.3 A50 50 0 0 1 80.3 14.3"/><path d="M89.4 19.5 A50 50 0 0 1 110.0 60.0"/></g></svg><span><span class="wm1">Aux </span><span class="wm2">Voix</span></span></a><nav aria-label="Rubriques"><a href="/#/presidentielle">Présidentielle 2027</a><a href="/#/actualites">Actualités</a><a href="/#/lois">Lois</a><a href="/#/votes">Votes</a><a href="/#/elus">Députés</a><a href="/#/codes">Codes</a></nav></div></header>
<main id="main"><div class="w">{corps}</div></main>
<footer><div class="w"><p>Données officielles de l'Assemblée nationale et de la DILA (Légifrance), sous Licence Ouverte, mises à jour le {fd(self.aujourdhui)}.</p>
<p><a href="/comprendre/comment-une-loi-est-votee/">Comment une loi est votée</a><a href="/lois-par-theme/">Lois par thème</a><a href="/lexique/">Lexique</a><a href="/cours/">Cours et TD</a><a href="/comprendre/article-49-3/">Le 49.3</a></p>
<p><a href="/#/signaler">Signaler une erreur</a><a href="/avis/">Donner mon avis</a><a href="/#/methode/ia">Rédaction et IA</a><a href="/#/methode/sources">Sources</a><a href="/#/methode/mentions">Mentions légales</a><a href="/#/methode/accessibilite">Accessibilité</a><a href="/flux/">Flux de suivi</a></p></div></footer>
<script src="/statique.js" defer></script></body></html>"""
        doc = doc.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
        if self.base:
            doc = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{self.base}/', doc)
        dest = os.path.join(self.site, chemin.strip("/"), "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(doc)
        return chemin

    def bloc_citer(self, ident, lignes):
        out = '<div class="cite" aria-label="Citer cette page"><h2 style="font-size:16px;margin:0 0 8px">Citer cette page</h2>'
        for i, (lib, txt) in enumerate(lignes):
            out += f'<p><span class="meta">{ESC(lib)}</span><br><span id="{ident}-{i}">{ESC(txt)}</span> <button type="button" data-copie="{ident}-{i}">Copier</button></p>'
        return out + "</div>"

    # ---------------- législatures ----------------
    def legislature(self, d, courante):
        leg = d["legislature"]
        grp = d["groupes"]
        deps = d["deputes"]
        K = len(d["periodes"])
        G = lambda i: grp[i] if 0 <= i < len(grp) else {"sigle": "?", "nom": "Groupe inconnu", "ni": True}
        # médianes de groupe et de commission, pour mettre chaque chiffre en contexte
        par_g, par_c = {}, {}
        for x in deps:
            if not x["actif"] or x["st"][K]["el"] < 20:
                continue
            par_g.setdefault(x["groupe"], []).append(x["st"][K])
            if x.get("commission"):
                par_c.setdefault(x["commission"], []).append(x["st"][K])
        med = lambda L, c: mediane([s[c] for s in L])
        scr = d["scrutins"]
        idx_dep = {x["id"]: i for i, x in enumerate(deps)}
        retenus = [s for s in scr if s["t"] in ("SPS", "MOC") or re.match(r"l.ensemble|(la|le) (proposition|projet) de loi|l.article unique (du|de la|de l.) (projet|proposition) de loi", s["ti"], re.I)]
        num_retenus = {s["n"] for s in retenus}
        def lien_vote(n):
            return f"/vote/{leg}/{n}/" if n in num_retenus else f"/#/scrutin/{n}"
        # --- députés ---
        for i, x in enumerate(deps):
            if x["id"] in self.deputes_faits:
                continue
            self.deputes_faits.add(x["id"])
            nom = f"{x['prenom']} {x['nom']}".strip()
            g = G(x["groupe"])
            fem = x.get("civ") == "Mme"
            qual = "Députée" if fem else "Député"
            lieu = f"{x['dept']} ({x['numDept']}), {ordinal(x['circ'])} circonscription" if x.get("dept") else "circonscription non renseignée"
            st = x["st"][K]
            mg = par_g.get(x["groupe"], [])
            mc = par_c.get(x.get("commission"), [])
            lignes_ind = ""
            for lib, c in (("Participation aux scrutins solennels", "partS"), ("Participation à tous les scrutins publics", "part"), ("Vote comme son groupe", "align")):
                if c == "align" and g.get("ni"):
                    continue
                lignes_ind += f"<tr><td>{lib}</td><td><strong>{pc(st[c])}</strong></td><td>{pc(med(mg, c))}</td><td>{pc(med(mc, c)) if mc else '—'}</td><td>{pc(d['medianes'][K][c])}</td></tr>"
            votes = []
            for s in reversed(retenus):
                c = s["v"][i] if i < len(s["v"]) else "-"
                if c in "123":
                    votes.append(s)
                    if len(votes) >= 12:
                        break
            vl = {"1": "Pour", "2": "Contre", "3": "Abstention", "4": "Non-votant", "0": "N'a pas pris part"}
            tv = "".join(f'<tr><td class="meta">{fd(s["d"])}</td><td><a href="{lien_vote(s["n"])}">{ESC(s["ti"][:1].upper() + s["ti"][1:])}</a></td><td><span class="v v{s["v"][i]}">{vl[s["v"][i]]}</span></td></tr>' for s in votes)
            am = x.get("am")
            chemin = f"/depute/{x['id']}/"
            cit = [("Référence", f"{nom}, {qual.lower()}{(' (' + x['dept'] + ', ' + ordinal(x['circ']) + ' circonscription)') if x.get('dept') else ''}, groupe {g['nom']}, {d['label']}, Assemblée nationale."),
                   ("Avec la source", f"Aux Voix, fiche de {nom}, d'après les données de l'Assemblée nationale, {self.url}{chemin} (consulté le {fd(self.aujourdhui)}).")]
            corps = f"""<p class="fil"><a href="/#/elus">Députés</a>, {ESC(d['label'])}</p><h1>{ESC(nom)}</h1>
<p class="lede">{qual}{'' if x['actif'] else ' (mandat terminé)'}, {ESC(lieu)}. Groupe : {ESC(g['nom'])} ({ESC(g['sigle'])}).</p>
<a class="cta" href="/#/elu/{x['id']}">Ouvrir la fiche complète</a><a class="cta s" href="https://www.assemblee-nationale.fr/dyn/deputes/{x['id']}">Fiche officielle à l'Assemblée</a>
<dl><dt>Parti de rattachement</dt><dd>{ESC(x.get('parti') or 'Aucun déclaré')}</dd><dt>Commission</dt><dd>{ESC(x.get('commission') or '—')}</dd><dt>Mandat</dt><dd>Depuis le {fd(x.get('debut'))}</dd>
{f"<dt>Amendements</dt><dd>{am[0]} déposés en premier signataire, dont {am[1]} adoptés ; {am[2]} cosignés</dd>" if am else ""}</dl>
<h2>Participation aux votes, en contexte</h2><p class="meta">L'Assemblée ne publie pas de relevé de présence : ces chiffres mesurent la participation aux votes publics, comparée à la médiane de son groupe, de sa commission et de l'ensemble des députés.</p>
<table><thead><tr><th>Indicateur</th><th>{ESC(nom)}</th><th>Son groupe</th><th>Sa commission</th><th>Assemblée</th></tr></thead><tbody>{lignes_ind}</tbody></table>
{f"<h2>Ses derniers votes importants</h2><table><thead><tr><th>Date</th><th>Scrutin</th><th>Son vote</th></tr></thead><tbody>{tv}</tbody></table>" if tv else ""}
{self.bloc_citer("c", cit)}<p class="meta"><a href="/flux/depute/{x['id']}.xml">Suivre ses votes (flux RSS)</a></p>"""
            self.page(chemin, f"{nom}, {qual.lower()} : votes et participation", f"{nom}, {qual.lower()} {lieu}, groupe {g['nom']} : ses votes, sa participation et ses amendements, d'après les données officielles de l'Assemblée nationale.",
                      corps, rss=(f"/flux/depute/{x['id']}.xml", f"Votes de {nom}"))
            self.urls["deputes"].append((chemin, d["maj"][:10]))
            if courante:
                self.flux(f"/flux/depute/{x['id']}.xml", f"Aux Voix, votes de {nom}", f"Les derniers votes de {nom} à l'Assemblée nationale.",
                          [(f"{s['ti'][:1].upper() + s['ti'][1:]} : {vl[s['v'][i]].lower()}", self.url + lien_vote(s["n"]) if s["n"] in num_retenus else f"{self.url}/#/scrutin/{s['n']}", s["d"],
                            f"Vote de {nom} : {vl[s['v'][i]].lower()}. Résultat : {'adopté' if 'adopt' in s['so'] else 'rejeté'}, {s['po']} pour, {s['co']} contre.") for s in votes])
        # --- votes importants ---
        lois_par_scr = {}
        for l in d.get("lois", []):
            for k in l.get("scrutins", []):
                lois_par_scr[k] = l
        for s in retenus:
            adopte = "adopt" in s["so"]
            moc = s["t"] == "MOC"
            ti = s["ti"][:1].upper() + s["ti"][1:]
            titre = f"Motion de censure {'adoptée' if adopte else 'rejetée'} : {s['po']} voix" if moc else f"{'Adopté' if adopte else 'Rejeté'} : {ti}"
            pos = {1: [], 2: [], 3: []}
            for b in s["g"]:
                gg = G(b[0])
                if not gg.get("ni") and b[2] in pos:
                    pos[b[2]].append(gg["sigle"])
            noms = {"1": [], "2": [], "3": []}
            for i, x in enumerate(deps):
                c = s["v"][i] if i < len(s["v"]) else "-"
                if c in noms:
                    noms[c].append(f'<a href="/depute/{x["id"]}/">{ESC(x["prenom"] + " " + x["nom"])}</a>')
            l = lois_par_scr.get(s["n"])
            chemin = f"/vote/{leg}/{s['n']}/"
            cit = [("Référence", f"Assemblée nationale, scrutin public n° {s['n']} du {fd(s['d'])}, sur {s['ti']}."),
                   ("Avec la source", f"Aux Voix, d'après les données de l'Assemblée nationale, {self.url}{chemin} (consulté le {fd(self.aujourdhui)}).")]
            corps = f"""<p class="fil"><a href="/#/votes">Votes</a>, {ESC(d['label'])}, scrutin n° {s['n']}</p><h1>{ESC(titre)}</h1>
<p class="lede">Le {fd(s['d'])}, l'Assemblée a {'adopté' if adopte else 'rejeté'} {ESC(s['ti'])}{'' if moc else f", par {s['po']} voix pour et {s['co']} contre ({s['ab']} abstentions)"}.</p>
<a class="cta" href="/#/scrutin/{s['n']}">Voir l'hémicycle et les explications</a><a class="cta s" href="https://www.assemblee-nationale.fr/dyn/{leg}/scrutins/{s['n']}">Scrutin sur le site de l'Assemblée</a>
{f'<p>Texte concerné : <a href="/loi/{ESC(l["id"])}/">{ESC(l["titre"][:1].upper() + l["titre"][1:])}</a></p>' if l else ''}
<h2>Les groupes</h2><ul class="l"><li>Majoritairement pour : {', '.join(pos[1]) or 'aucun'}</li><li>Majoritairement contre : {', '.join(pos[2]) or 'aucun'}</li><li>Majoritairement abstention : {', '.join(pos[3]) or 'aucun'}</li></ul>
<h2>Le vote de chaque député</h2><p class="noms"><span class="v v1">Pour ({len(noms['1'])})</span> {', '.join(noms['1']) or '—'}</p><p class="noms"><span class="v v2">Contre ({len(noms['2'])})</span> {', '.join(noms['2']) or '—'}</p><p class="noms"><span class="v v3">Abstention ({len(noms['3'])})</span> {', '.join(noms['3']) or '—'}</p>
{self.bloc_citer("c", cit)}"""
            self.page(chemin, titre[:110], f"Scrutin public n° {s['n']} du {fd(s['d'])} à l'Assemblée nationale : {s['ti'][:160]}. Résultat et vote de chaque député.", corps)
            self.urls["votes"].append((chemin, s["d"]))
        # cartes à intégrer sur d'autres sites (integrer.html) : un petit fichier par centaine de scrutins, sans le vote nominatif
        try:
            dossier = os.path.join(self.site, "carte", str(leg))
            os.makedirs(dossier, exist_ok=True)
            gnoms = [[g.get("sigle", "?"), g.get("nom", ""), 1 if g.get("ni") else 0] for g in grp]
            paquets = {}
            for s in scr:
                paquets.setdefault(s["n"] // 100, []).append([s["n"], s["d"], s["ti"], s["t"], 1 if "adopt" in s["so"] else 0, s["po"], s["co"], s.get("ab", 0), s.get("rq", 0),
                                                            [[b[0], b[2]] for b in s.get("g", [])]])
            for k, L in paquets.items():
                with open(os.path.join(dossier, f"{k}.json"), "w", encoding="utf-8") as f:
                    json.dump({"leg": leg, "label": d.get("label", ""), "maj": d.get("maj", ""), "g": gnoms, "s": L}, f, ensure_ascii=False, separators=(",", ":"))
        except Exception as e:
            print(f"Cartes intégrables : {e}")
        if courante:
            self.flux("/flux/votes.xml", "Aux Voix, votes importants", "Les votes solennels, motions de censure et votes sur l'ensemble des textes à l'Assemblée nationale.",
                      [(f"{'Adopté' if 'adopt' in s['so'] else 'Rejeté'} : {s['ti'][:1].upper() + s['ti'][1:]}", f"{self.url}/vote/{leg}/{s['n']}/", s["d"],
                        f"{s['po']} pour, {s['co']} contre, {s['ab']} abstentions.") for s in list(reversed(retenus))[:50]])
        # --- lois ---
        evenements = []
        try:
            fiches = {f.get("dossier"): f for f in json.load(open(os.path.join(self.site, "contenu", "lois.json"), encoding="utf-8")) if isinstance(f, dict) and f.get("publie") is True}
        except Exception:
            fiches = {}
        rep = os.path.join(self.site, "contenu", "fiches")
        for fn in (sorted(os.listdir(rep)) if os.path.isdir(rep) else []):
            try:
                f = json.load(open(os.path.join(rep, fn), encoding="utf-8"))
            except Exception:
                continue
            if isinstance(f, dict) and f.get("publie") is True and f.get("dossier"):
                fiches[f["dossier"]] = f
        for l in d.get("lois", []):
            E = l.get("etapes") or []
            chemin = f"/loi/{l['id']}/"
            titre = l["titre"][:1].upper() + l["titre"][1:]
            etapes = "".join(f"<tr><td class='meta'>{fd(e[2])}</td><td>{ESC(libelle_etape(e, E))}</td><td>{ESC((e[3] if len(e) > 3 else '') or '')}</td></tr>" for e in E if i_utile(e, E))
            prom = l.get("prom")
            statut = f"Promulguée le {fd(prom['date'])}" if prom else (f"En cours : {libelle_etape(E[-1], E).lower()} le {fd(E[-1][2])}" if E else "En cours")
            fin = [scr_n for scr_n in l.get("scrutins", []) if scr_n in num_retenus]
            cit = [("Référence", ((prom or {}).get("titre") or titre) + (f", JO du {fd(prom['date'])}" if prom else f" ({d['label']}, dossier législatif de l'Assemblée nationale)")),
                   ("Avec la source", f"Aux Voix, d'après les données de l'Assemblée nationale, {self.url}{chemin} (consulté le {fd(self.aujourdhui)}).")]
            # ce que propose le texte, selon ses auteurs (exposé des motifs, s'il a déjà été lu)
            expo = ""
            try:
                tx = json.load(open(os.path.join(self.site, "textes", str(leg), l["id"] + ".json"), encoding="utf-8"))
                qui = "le Gouvernement" if str(tx.get("u", "")).startswith("PRJL") else "ses auteurs"
                P, Ex = tx.get("p") or [], tx.get("e") or []
                if P or Ex:
                    expo = (f"<h2>Ce que propose ce texte</h2><p><em>Extraits de l'exposé des motifs, écrits par {qui} et recopiés mot pour mot ; Aux Voix ne les reprend pas à son compte.</em></p>"
                            + (f"<h3>Ce que prévoit le texte, selon {qui}</h3><ul class='l'>" + "".join(f"<li>{ESC(x)}</li>" for x in P[:6]) + "</ul>" if P else "")
                            + (f"<h3>Pourquoi ce texte est proposé, selon {qui}</h3>" + "".join(f"<p>{ESC(x)}</p>" for x in Ex[:2]) if Ex else ""))
            except Exception:
                pass
            fiche = ""
            f = fiches.get(l["id"])
            if f:
                A = f.get("arguments") or {}
                cote = lambda L: "<ul class='l'>" + "".join(f"<li><strong>{ESC(a.get('qui', ''))}</strong> : {ESC(a.get('arg', ''))}</li>" for a in L if isinstance(a, dict)) + "</ul>"
                lignes = [r for r in (f.get("change") or []) if isinstance(r, list) and len(r) >= 3]
                fiche = (f"<p class='lede'><strong>{ESC(f.get('phrase', ''))}</strong></p>"
                         + "<p class='meta'>Fiche rédigée avec l'aide d'une intelligence artificielle, à partir des sources officielles citées plus bas" + (f", relue par {ESC(f['verif'])}" if f.get("verif") else ", pas encore relue") + ". <a href='/#/methode/ia'>Comment sont rédigées les fiches</a>.</p>"
                         + ("<h2>En bref</h2>" + "".join(f"<p>{ESC(x)}</p>" for x in f.get("resume") or []) if f.get("resume") else "")
                         + ("<h2>Pourquoi ce texte</h2>" + "".join(f"<p>{ESC(x)}</p>" for x in ([f["pourquoi"]] if isinstance(f.get("pourquoi"), str) else f.get("pourquoi") or [])) if f.get("pourquoi") else "")
                         + ("<h2>Ce qui change</h2><table><thead><tr><th>Avant</th><th>Après</th><th>Qui est concerné</th><th>À partir de quand</th></tr></thead><tbody>"
                            + "".join("<tr>" + "".join(f"<td>{ESC((r + ['', ''])[k] or '—')}</td>" for k in range(4)) + "</tr>" for r in lignes) + "</tbody></table>" if lignes else "")
                         + (f"<h2>Ce qu’en disent les différents camps</h2><h3>Ceux qui le soutiennent</h3>{cote(A.get('pour') or [])}<h3>Ceux qui s’y opposent ou le critiquent</h3>{cote(A.get('contre') or [])}"
                            "<p><em>Chaque argument est rapporté tel que son auteur le présente ; Aux Voix ne tranche pas.</em></p>" if A.get("pour") and A.get("contre") else
                            (f"<h2>Ce qu’en disent les différents camps</h2><h3>Ceux qui le soutiennent</h3>{cote(A.get('pour') or [])}<h3>Pas d’opposition au vote</h3><p>{ESC(A['consensus'])}</p>" if A.get("pour") and A.get("consensus") else ""))
                         + (lambda K: ("<h2>En classe : mots à retenir, quiz et question de débat</h2><p><em>Pour l’enseignement moral et civique ou l’histoire-géographie"
                             + (f" ({ESC(K['niveau'])}, {ESC(K['duree'])})" if K.get("niveau") and K.get("duree") else "") + ".</em></p>"
                             + "<h3>Mots à retenir</h3><dl>" + "".join(f"<dt>{ESC(m['terme'])}</dt><dd>{ESC(m['def'])}</dd>" for m in K.get("mots") or [] if isinstance(m, dict)) + "</dl>"
                             + "<h3>Quiz</h3><ol>" + "".join(f"<li><p><strong>{ESC(q['q'])}</strong></p><ul class='l'>" + "".join(f"<li>{ESC(c)}</li>" for c in q.get("choix") or []) + f"</ul><details><summary>Voir la réponse</summary><p><strong>Réponse : {'ABC'[q['bonne']]}.</strong> {ESC(q.get('expl', ''))}</p></details></li>" for q in K.get("quiz") or [] if isinstance(q, dict) and q.get("bonne") in (0, 1, 2)) + "</ol>"
                             + (f"<h3>Question de débat</h3><p><strong>{ESC(K['debat']['question'])}</strong></p><p>{ESC(K['debat'].get('consigne', ''))}</p>" if (K.get("debat") or {}).get("question") else "")) if isinstance(K, dict) else "")(f.get("classe"))
                         + ("<h2>Sources de cette fiche</h2><ul class='l'>" + "".join(f"<li><a href=\"{ESC(x['url'])}\">{ESC(x.get('titre') or x['url'])}</a></li>" for x in f.get("sources") or [] if isinstance(x, dict) and str(x.get("url", "")).startswith("https://")) + "</ul>" if f.get("sources") else ""))
            th_slug, th_lib = (theme_fiche(l["id"], l["titre"], self.themes) if f and self.themes else (None, None))
            lien_th = f', <a href="/theme/{th_slug}/">{ESC(th_lib)}</a>' if th_slug else ""
            corps = f"""<p class="fil"><a href="/#/lois">Lois</a>, {ESC(d['label'])}{lien_th}</p><h1>{ESC(titre)}</h1><p class="lede">{ESC(statut)}.</p>{fiche}
<a class="cta" href="/#/loi/{ESC(l['id'])}">Voir le parcours et les votes</a>{f'<a class="cta s" href="{ESC(prom["url"])}">Texte sur Légifrance</a>' if prom and prom.get("url") else ''}
{expo}
{f'<h2>Son parcours</h2><table><thead><tr><th>Date</th><th>Étape</th><th>Résultat</th></tr></thead><tbody>{etapes}</tbody></table>' if etapes else ''}
{f'<h2>Votes à l’Assemblée</h2><ul class="l">' + ''.join(f'<li><a href="/vote/{leg}/{k}/">Scrutin n° {k}</a></li>' for k in fin) + '</ul>' if fin else ''}
{self.bloc_citer("c", cit)}"""
            if f:
                t_seo = f"{titre[:90]} : ce qui change, qui a voté"
                d_seo = f"{f.get('phrase', '').strip()} Explication simple, arguments de chaque camp, parcours et votes ; sources officielles. {statut}."
                dv = (f.get("version") or {}).get("date")
                ld = [{"@context": "https://schema.org", "@type": "Article", "headline": titre[:110], "description": f.get("phrase", ""),
                       "inLanguage": "fr", "mainEntityOfPage": self.url + chemin, "image": self.url + self.images.get(l["id"], "/icones/partage.png"),
                       "author": {"@type": "Organization", "name": "Aux Voix", "url": self.url},
                       "publisher": {"@type": "Organization", "name": "Aux Voix", "url": self.url, "logo": {"@type": "ImageObject", "url": self.url + "/icones/partage.png"}},
                       "about": {"@type": "Legislation", "name": titre, "legislationType": l.get("proc") or "Texte de loi"},
                       **({"datePublished": dv, "dateModified": dv} if dv else {})},
                      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                          {"@type": "ListItem", "position": 1, "name": "Aux Voix", "item": self.url + "/"},
                          {"@type": "ListItem", "position": 2, "name": "Lois", "item": self.url + "/#/lois"},
                          {"@type": "ListItem", "position": 3, "name": titre[:110], "item": self.url + chemin}]}]
                self.page(chemin, t_seo, d_seo, corps, jsonld=ld, og_type="article", image=self.images.get(l["id"]))
            else:
                self.page(chemin, titre[:110], f"{titre[:200]} : parcours au Parlement, votes et statut. {statut}.", corps)
            self.urls["lois"].append((chemin, (prom or {}).get("date") or (E[-1][2] if E else d["maj"][:10])))
            if E:
                evenements.append((E[-1][2], titre, chemin, statut))
        if courante:
            evenements.sort(reverse=True)
            self.flux("/flux/lois.xml", "Aux Voix, lois", "Les dernières étapes franchies par les textes de loi au Parlement.",
                      [(t, self.url + c, dt, st) for dt, t, c, st in evenements[:50]])

    # ---------------- codes ----------------
    def codes(self):
        dossier = os.path.join(self.site, "codes")
        try:
            ix = json.load(open(os.path.join(dossier, "index.json"), encoding="utf-8"))
        except Exception:
            return
        limite = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
        for c in ix.get("codes", []):
            try:
                code = json.load(open(os.path.join(dossier, c["slug"] + ".json"), encoding="utf-8"))
            except Exception:
                continue
            nom_code = f"du {code['titre']}" if code["code"] else f"de la {code['titre']}"
            recents = []
            for a in code["articles"]:
                num = a["n"]
                chemin = f"/code/{code['slug']}/{slug_num(num)}/"
                art_l = num if re.match(r"^\d", num) else re.sub(r"^([A-Z]+)\.?\s*", r"\1. ", num)
                url_lf = f"https://www.legifrance.gouv.fr/{'codes' if code['code'] else 'loda'}/article_lc/{a['id']}"
                src = re.sub(r"\s*-\s*art\..*$", "", a.get("m") or "")
                paras = "".join(f"<p>{ESC(p).replace(chr(10), '<br>')}</p>" for p in a["t"].split("\n\n"))
                fil = " / ".join(ESC(code["toc"][k]) for k in a.get("p", []))
                cit = [("Référence", f"{code['abr']}, art. {art_l}"),
                       ("Dans une phrase", f"Article {art_l} {nom_code}" + (f", dans sa rédaction issue de {src[:1].lower() + src[1:]}" if src else "") + "."),
                       ("Note de bas de page", f"{code['abr']}, art. {art_l} ; Légifrance, {url_lf}, consulté le {fd(self.aujourdhui)}.")]
                prec = a.get("v")
                corps = f"""<p class="fil"><a href="/#/codes">Codes</a>, <a href="/#/code/{code['slug']}">{ESC(code['titre'])}</a></p>{f'<p class="meta">{fil}</p>' if fil else ''}
<h1>Article {ESC(art_l)} {ESC(nom_code)}</h1><p class="lede">En vigueur depuis le {fd(a['d'])}{', issu de ' + ESC(src[:1].lower() + src[1:]) if src else ''}.</p>
<blockquote class="art">{paras}</blockquote>
<a class="cta" href="/#/code/{code['slug']}/{ESC(num)}">Voir ce qui a changé et les articles voisins</a><a class="cta s" href="{ESC(url_lf)}">Lire sur Légifrance</a>
{self.bloc_citer("c", cit)}
{f'<h2>Version précédente</h2><p class="meta">En vigueur du {fd(prec["d"])} au {fd(a["d"])}.</p><blockquote class="art" style="border-left-color:var(--abst);font-size:16px">' + ''.join(f"<p>{ESC(p)}</p>" for p in prec["t"].split(chr(10) + chr(10))) + '</blockquote>' if prec else ''}
<p class="meta">Texte : DILA, base LEGI (Légifrance), Licence Ouverte. Seule la publication au Journal officiel fait foi.</p>"""
                self.page(chemin, f"Article {art_l} {nom_code}", f"Article {art_l} {nom_code}, version en vigueur : {a['t'][:200]}", corps,
                          rss=(f"/flux/code/{code['slug']}.xml", f"Modifications du {code['titre']}"))
                self.urls["codes"].append((chemin, a["d"] if a["d"] and a["d"] < "2900" else self.aujourdhui))
                if a["d"] and limite <= a["d"] <= self.aujourdhui:
                    recents.append((a["d"], art_l, chemin, src))
            recents.sort(reverse=True)
            self.flux(f"/flux/code/{code['slug']}.xml", f"Aux Voix, modifications du {code['titre']}", f"Les articles du {code['titre']} modifiés au cours des douze derniers mois.",
                      [(f"Article {n} modifié", self.url + ch, dt, f"Nouvelle rédaction en vigueur le {fd(dt)}" + (f", issue de {s[:1].lower() + s[1:]}" if s else "") + ".") for dt, n, ch, s in recents[:100]])

    # ---------------- flux, plan du site, robots ----------------
    def flux(self, chemin, titre, desc, items):
        def rfc(iso):
            try:
                return format_datetime(datetime.datetime.fromisoformat(iso[:10] + "T12:00:00+00:00"))
            except Exception:
                return ""
        def item(x):
            t, u, dt, dd = x[:4]
            guid = x[4] if len(x) > 4 else f"{u}#{dt}"   # identifiant stable : un même élément n'apparaît qu'une fois dans les lecteurs
            pub = f"<pubDate>{rfc(dt)}</pubDate>" if dt else ""
            return f'<item><title>{ESC(t)}</title><link>{ESC(u)}</link><guid isPermaLink="false">{ESC(guid)}</guid>{pub}<description>{ESC(dd)}</description></item>'
        it = "".join(item(x) for x in items)
        xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{ESC(titre)}</title><link>{ESC(self.url)}</link><description>{ESC(desc)}</description><language>fr</language>{it}</channel></rss>'
        dest = os.path.join(self.site, chemin.strip("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(xml)

    def flux_agenda(self):
        a = json.load(open(os.path.join(self.site, "agenda.json"), encoding="utf-8"))
        maj = (a.get("maj") or self.aujourdhui)[:10]
        items, vus = [], set()
        for x in a.get("s", []):
            j = x["d"][:10]
            if j < self.aujourdhui:
                continue
            for k, p in enumerate(x.get("p", [])):
                if not re.match(r"(?i)vote solennel", p[0] or "") or (j, p[1]) in vus:
                    continue
                vus.add((j, p[1]))
                objet = re.sub(r"(?i)^vote solennel (sur )?", "", p[1]).strip()
                cle = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", objet.lower()).encode("ascii", "ignore").decode()).strip("-")[:80]
                items.append((f"Vote solennel le {fd(j)} : {objet}", f"{self.url}/#/agenda", maj,
                              f"Vote solennel inscrit à l'ordre du jour de l'Assemblée nationale le {fd(j)}. L'ordre du jour peut encore changer.",
                              f"aux-voix-vote-solennel-{j}-{cle}"))
        self.flux("/flux/agenda.xml", "Aux Voix, votes solennels à venir", "Les votes solennels annoncés à l'ordre du jour de l'Assemblée nationale.", items)

    def flux_presidentielle(self):
        items = []
        try:
            C = json.load(open(os.path.join(self.site, "contenu", "candidats.json"), encoding="utf-8"))
        except Exception:
            C = []
        for c in C if isinstance(C, list) else []:
            if c.get("publie") is not True:
                continue
            nom = f"{c.get('prenom', '')} {c.get('nom', '')}".strip()
            dt = ((c.get("declaration") or {}).get("date") or "")[:10]
            src = next((x.get("url") for x in c.get("sources") or [] if isinstance(x, dict) and str(x.get("url", "")).startswith("http")), "")
            cle = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", nom.lower()).encode("ascii", "ignore").decode()).strip("-")
            items.append((f"Candidature annoncée : {nom}" + (f" ({c['soutien']})" if c.get("soutien") else ""), f"{self.url}/#/candidats",
                          dt, (c.get("note") or "Candidature déclarée publiquement.") + (f" Source : {src}" if src else ""), f"aux-voix-candidature-{cle}"))
        try:
            A = json.load(open(os.path.join(self.site, "actualites-officielles.json"), encoding="utf-8"))
        except Exception:
            A = []
        for x in A if isinstance(A, list) else []:
            if x.get("presi") and str(x.get("lien", "")).startswith("http"):
                items.append((f"{x.get('source', '')} : {x.get('titre', '')}", x["lien"], x.get("date") or "", x.get("titre", ""), x["lien"]))
        items.sort(key=lambda t: t[2] or "0000", reverse=True)
        self.flux("/flux/presidentielle.xml", "Aux Voix, présidentielle 2027", "Les candidatures annoncées et les titres de LCP, Public Sénat et vie-publique.fr sur la campagne présidentielle.", items[:60])

    def finaliser(self):
        open(os.path.join(self.site, "statique.css"), "w", encoding="utf-8").write(CSS)
        open(os.path.join(self.site, "statique.js"), "w", encoding="utf-8").write(JS)
        cartes = []
        for nom, L in self.urls.items():
            if not L:
                continue
            for k in range(0, len(L), 45000):
                fichier = f"sitemap-{nom}-{k // 45000 + 1}.xml"
                corps = "".join(f"<url><loc>{ESC(self.url + c)}</loc><lastmod>{ESC((dt or self.aujourdhui)[:10])}</lastmod></url>" for c, dt in L[k:k + 45000])
                open(os.path.join(self.site, fichier), "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{corps}</urlset>')
                cartes.append(fichier)
        index = "".join(f"<sitemap><loc>{ESC(self.url)}/{f}</loc><lastmod>{self.aujourdhui}</lastmod></sitemap>" for f in cartes)
        open(os.path.join(self.site, "sitemap.xml"), "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{index}</sitemapindex>')
        robots = f"User-agent: *\nAllow: /\nDisallow: /g/\nSitemap: {self.url}/sitemap.xml\n" if self.public else "# Site en version bêta : exploration désactivée jusqu'à l'ouverture publique.\nUser-agent: *\nDisallow: /\n"
        open(os.path.join(self.site, "robots.txt"), "w", encoding="utf-8").write(robots)
        # flux de l'ordre du jour (votes solennels annoncés) et de la présidentielle
        try:
            self.flux_agenda()
        except Exception as e:
            print(f"Flux de l'ordre du jour : {e}")
        try:
            self.flux_presidentielle()
        except Exception as e:
            print(f"Flux de la présidentielle : {e}")
        # page d'accueil des flux
        liens = "".join(f'<li><a href="/flux/{f}">{t}</a></li>' for f, t in (("votes.xml", "Votes importants de l'Assemblée"), ("lois.xml", "Étapes des lois"),
                                                                              ("agenda.xml", "Prochains votes solennels annoncés à l'Assemblée"), ("presidentielle.xml", "Présidentielle 2027 : candidatures et actualités de la campagne")))
        self.page("/flux/", "Flux de suivi", "Suivre les votes, les lois et les modifications des codes avec un lecteur de flux RSS.",
                  f"<h1>Flux de suivi</h1><p class='lede'>Un flux RSS est une adresse que l'on ne lit pas dans le navigateur : on la colle dans une application de lecture (Feedly, Inoreader, Thunderbird, NetNewsWire…), qui vous prévient à chaque nouveauté. Si vous ouvrez un flux directement, votre navigateur affiche du code : c'est normal. Ajoutez ces adresses à votre lecteur pour être prévenu automatiquement. Chaque fiche de député et chaque code a aussi son propre flux.</p><ul class='l'>{liens}</ul>")
        # l'interrupteur s'applique aussi à la page principale du site
        idx = os.path.join(self.site, "index.html")
        if self.public and os.path.exists(idx):
            s = open(idx, encoding="utf-8").read()
            s = re.sub(r'\s*<!-- Version bêta[^>]*-->\s*<meta name="robots" content="noindex, nofollow">', "", s)
            s = s.replace('<meta name="robots" content="noindex, nofollow">', "")
            open(idx, "w", encoding="utf-8").write(s)
        total = sum(len(v) for v in self.urls.values())
        print(f"Pages publiques : {total} ({', '.join(f'{k} {len(v)}' for k, v in self.urls.items())}) ; indexation {'ouverte' if self.public else 'fermée (version bêta)'}")


def chambre(c):
    return "AN" if re.match(r"^AN|^CMP-DEBATS-AN", c) else "SN" if re.match(r"^SN|^CMP-DEBATS-SN", c) else None


def lecture(c):
    for m, l in ((r"^(AN|SN)1-", "première lecture"), (r"^(AN|SN)2-", "deuxième lecture"), (r"NLEC", "nouvelle lecture"), (r"LDEF", "lecture définitive"), (r"LUNI", "lecture unique")):
        if re.search(m, c):
            return l
    return None


def i_utile(e, E):
    return E.index(e) == 0 or "DEPOT" not in e[0]


def libelle_etape(e, E):
    c, ch, lec = e[0], chambre(e[0]), lecture(e[0])
    lieu = {"AN": "à l'Assemblée", "SN": "au Sénat"}.get(ch, "")
    if c.startswith("PROM"):
        return "Promulgation"
    if c.startswith("CC"):
        return "Décision du Conseil constitutionnel"
    if c.startswith("CMP-DEC"):
        return "Conclusion de la commission mixte paritaire"
    if c.startswith("CMP-DEPOT"):
        return "Commission mixte paritaire convoquée"
    if c.startswith("CMP-DEBATS"):
        return f"Vote du texte de compromis {lieu}".strip()
    if "DEPOT" in c:
        return f"Dépôt {lieu}".strip() if E.index(e) == 0 else f"Transmission {lieu}".strip()
    if c.endswith("DEC"):
        return f"Vote en {lec or 'séance'} {lieu}".strip()
    return (e[1] or c)[:1].upper() + (e[1] or c)[1:]


def generer(site_dir):
    g = Generateur(site_dir)
    try:
        g.themes = charger_themes(site_dir)
        g.images = images_fiches(g, charger_fiches(site_dir))
    except Exception as e:
        print(f"Images de partage ignorées ({e})")
    try:
        ix = json.load(open(os.path.join(site_dir, "index.json"), encoding="utf-8"))
    except Exception:
        ix = {"legislatures": []}
    for L in sorted(ix.get("legislatures", []), key=lambda x: (x.get("au") is not None, -(int(x.get("leg", 0) or 0)))):
        try:
            d = json.load(open(os.path.join(site_dir, L["fichier"]), encoding="utf-8"))
            fv = os.path.join(site_dir, L.get("votes") or f"votes-{L['leg']}.json")
            if os.path.exists(fv) and d.get("scrutins") and "v" not in d["scrutins"][0]:
                vv = json.load(open(fv, encoding="utf-8"))
                m = dict(zip(vv.get("n", []), vv.get("v", [])))
                for x in d["scrutins"]:
                    x["v"] = m.get(x["n"], "")
            g.legislature(d, d.get("courante", False))
        except Exception as e:
            print(f"Pages : {L.get('label')} ignorée ({e})")
    g.codes()
    try:
        generer_fonds(g)
    except Exception as e:
        print(f"Pages de fond ignorées ({e})")
    g.finaliser()


if __name__ == "__main__":
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generer(os.path.join(racine, "site"))
