#!/usr/bin/env python3
"""Aux Voix : « graines », un petit fichier par page, pour la législature en cours.

Quand quelqu'un ouvre directement la fiche d'un député, un vote, une loi ou une liste (lien partagé, favori), le site
lit d'abord la graine de cette page : quelques kilo-octets au lieu des 9 Mo de data-17.json et votes-17.json.
Le fichier complet n'est téléchargé que si la personne fait ensuite quelque chose qui en a besoin (filtrer une liste,
ouvrir une page sans graine). Chaque graine a le même format que data-17.json, réduit aux éléments affichés : la page
s'affiche exactement comme avec les données complètes (vérifié par scripts/tests et par la comparaison des pages).

Les règles de choix (25 derniers votes d'un député, 20 derniers votes d'un groupe, etc.) recopient celles du site
(site/app.js) : si l'une change là-bas, il faut la changer ici. La liste des thèmes est lue directement dans app.js."""
import datetime, functools, json, os, re, shutil

from accueil import norm, texte_de, queue_titre

PAR_PAQUET = 50          # scrutins regroupés par 50 : un seul fichier pour 50 pages de vote
MARGE = {"lois": 80, "votes": 60, "elus": 100}   # premières lignes des listes, avec une marge sur ce qu'affiche le site


def ti_propre(ti):
    return re.sub(r"\s*\.\s*$", "", str(ti or ""))          # comme prepare() dans le site


def est_sol(s):
    return s.get("t") == "SPS"


def est_moc(s):
    return s.get("t") == "MOC" or bool(re.search("motion de censure", ti_propre(s.get("ti")), re.I))


def est_ensemble(s):
    return bool(re.match(r"l.ensemble|(la|le) (proposition|projet) de loi|l.article unique (du|de la|de l.) (projet|proposition) de loi", norm(ti_propre(s.get("ti")))))


def lundi_de(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def themes_du_site(app_js):
    """Les thèmes et leurs mots-clés, lus dans app.js (une seule source de vérité)."""
    with open(app_js, encoding="utf-8") as f:
        src = f.read()
    bloc = re.search(r"const THEMES=\[(.*?)\n\];", src, re.S)
    if not bloc:
        raise RuntimeError("liste THEMES introuvable dans app.js")
    out = []
    for cle, lib, motif in re.findall(r'\["(\w+)","([^"]+)",RX\("((?:[^"\\]|\\.)*)"\)\]', bloc.group(1)):
        motif = re.sub(r"\\(.)", r"\1", motif)              # chaîne JavaScript -> expression régulière
        out.append((cle, lib, re.compile(r"\b(?:" + motif + ")", re.ASCII)))   # \b du JavaScript : lettres ASCII
    if len(out) < 5:
        raise RuntimeError("liste THEMES incomplète")
    return out


def theme_de(s, themes):
    t = norm(texte_de(ti_propre(s.get("ti"))) or ti_propre(s.get("ti")))
    for cle, _, rx in themes:
        if rx.search(t):
            return cle
    return None


def mediane(vals):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return None
    m = len(v) // 2
    return v[m] if len(v) % 2 else (v[m - 1] + v[m]) / 2


def contextes(deputes, nb_periodes):
    """Médianes par groupe et par commission (fonction contexte() du site), pour chaque période."""
    out = {}
    for k in range(nb_periodes + 1):
        g, c = {}, {}
        for d in deputes:
            st = d["st"][k]
            if not d.get("actif") or st["el"] < 20:
                continue
            g.setdefault(d["groupe"], []).append(st)
            if d.get("commission"):
                c.setdefault(d["commission"], []).append(st)
        out[str(k)] = {"g": {str(gi): {x: mediane(s[x] for s in L) for x in ("partS", "part", "align")} for gi, L in g.items()},
                       "c": {cm: {x: mediane(s[x] for s in L) for x in ("partS", "part", "align")} for cm, L in c.items()}}
    return out


def cmp_val(a, b):
    """cmpVal() du site, pour des nombres et des dates au format AAAA-MM-JJ."""
    if a is None and b is None:
        return 0
    if a is None:
        return 1
    if b is None:
        return -1
    return (a > b) - (a < b)


def trier(rows, get, sens):
    """sortRows() du site : les valeurs absentes en dernier, tri stable."""
    def c(x, y):
        va, vb = get(x), get(y)
        if va is None or vb is None:
            return cmp_val(va, vb)
        return sens * cmp_val(va, vb)
    return sorted(rows, key=functools.cmp_to_key(c))


def cle_nom(d):
    """Approximation de l'ordre alphabétique français (le site trie lui-même : la marge couvre les écarts)."""
    return norm(d["nom"] + " " + d["prenom"])


def sans(s, *champs):
    return {k: v for k, v in s.items() if k not in champs}


def ecrire_graines(site_dir, entree):
    """entree : la ligne de index.json de la législature en cours. Renvoie le tronc commun à placer dans
    demarrage.json, et un petit bilan."""
    leg = entree["leg"]
    with open(os.path.join(site_dir, entree["fichier"]), encoding="utf-8") as f:
        d = json.load(f)
    S, L, D = d.get("scrutins") or [], d.get("lois") or [], d.get("deputes") or []
    P = d.get("personnes") or {}
    if not S or not D:
        raise RuntimeError("données incomplètes")
    # vote de chaque député : dans data-17.json (ancien format) ou dans votes-17.json
    if not isinstance(S[0].get("v"), str):
        with open(os.path.join(site_dir, entree.get("votes") or f"votes-{leg}.json"), encoding="utf-8") as f:
            vx = json.load(f)
        vm = dict(zip(vx["n"], vx["v"]))
        vide = "-" * len(D)
        for s in S:
            s["v"] = vm.get(s["n"], vide)
    maj = d["maj"]
    SCN = {s["n"]: s for s in S}
    racine = os.path.join(site_dir, "g", leg)
    if os.path.isdir(racine):
        shutil.rmtree(racine)
    nb = {"fichiers": 0, "octets": 0}

    def ecrire(nom, contenu):
        chemin = os.path.join(racine, nom + ".json")
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        contenu = dict({"maj": maj}, **contenu)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(contenu, f, ensure_ascii=False, separators=(",", ":"))
        nb["fichiers"] += 1
        nb["octets"] += os.path.getsize(chemin)

    def ordre(nums):
        """Les scrutins retenus, dans l'ordre des données complètes."""
        return [s for s in S if s["n"] in nums]

    base = {k: v for k, v in d.items() if k not in ("scrutins", "lois", "deputes", "personnes")}
    base["ctx"] = contextes(D, len(d.get("periodes") or []))

    # Liste des députés réduite au nécessaire pour nommer chacun (vote par vote, auteurs d'un texte, membres d'un groupe)
    noms = [{k: x.get(k) for k in ("id", "civ", "prenom", "nom", "groupe", "seg", "actif", "dept", "numDept", "circ")} for x in D]
    ecrire("noms", {"deputes": noms})

    # Le texte d'un scrutin (loiDe() du site) : le lien officiel, sinon le seul dossier de même titre
    scr2loi = {}
    for l in L:
        for k in l.get("scrutins") or []:
            scr2loi[k] = l
    motif = re.compile(f"L{leg}N")
    par_titre = {}
    for l in L:
        if motif.search(l["id"]):
            q = queue_titre(l["titre"])
            par_titre[q] = None if q in par_titre else l

    def loi_de(s):
        if s["n"] in scr2loi:
            return scr2loi[s["n"]]
        tx = texte_de(ti_propre(s["ti"]))
        if not tx:
            return None
        k = queue_titre(tx)
        return par_titre.get(k) if len(k.split(" ")) >= 4 else None

    # Fiche d'un député : ses 25 derniers votes (et ses 25 derniers votes solennels), les dates de ses changements de
    # groupe, les textes qu'il a déposés ou rapportés. Son vote seul est gardé (« vi ») : le site recompose le reste.
    for i, dp in enumerate(D):
        mandat = [s for s in S if s["v"][i] != "-"]
        nums = {s["n"] for s in mandat[-25:]} | {s["n"] for s in [x for x in mandat if est_sol(x)][-25:]}
        for a, b, _ in dp.get("seg") or []:
            nums |= {a, b}
        scr = [dict(sans(s, "v"), vi=s["v"][i]) for s in ordre(nums)]
        lois = [l for l in L if dp["id"] in (l.get("auteurs") or []) or dp["id"] in (l.get("rapporteurs") or [])]
        ecrire(f"elu/{dp['id']}", {"graine": f"elu/{dp['id']}", "noms": 1, "vi": i, "dep": [dp], "lois": lois, "scrutins": scr})

    # Pages de vote, par paquets de 50 : le scrutin, le vote de chaque député, le texte examiné
    paquets = {}
    for s in S:
        paquets.setdefault(s["n"] // PAR_PAQUET, []).append(s)
    # les dossiers de même titre voyagent ensemble : le site voit ainsi, comme avec les données complètes, que le titre
    # ne suffit pas à choisir entre eux
    meme_titre = {}
    for l in L:
        if motif.search(l["id"]):
            meme_titre.setdefault(queue_titre(l["titre"]), []).append(l)
    for p, scr in paquets.items():
        lois = []
        for s in scr:
            l = loi_de(s)
            if l is None:
                continue
            for x in [l] + (meme_titre.get(queue_titre(l["titre"]), []) if motif.search(l["id"]) else []):
                if all(x is not y for y in lois):
                    lois.append(x)
        lois.sort(key=lambda l: L.index(l))
        ecrire(f"scrutin/{p}", {"graine": f"scrutin/{p}", "noms": 1, "scrutins": scr, "lois": lois})

    # Page d'une loi : le dossier, ses scrutins, ses auteurs et rapporteurs
    for l in L:
        nums = set(l.get("scrutins") or [])
        ids = list(l.get("auteurs") or []) + list(l.get("rapporteurs") or [])
        ecrire(f"loi/{l['id']}", {"graine": f"loi/{l['id']}", "noms": 1, "lois": [l],
                                  "scrutins": [sans(s, "v") for s in ordre(nums)], "personnes": {x: P[x] for x in ids if x in P}})

    # Page d'un groupe : ses 20 derniers votes (et 20 derniers votes solennels), tous les votes sur l'ensemble d'un texte
    ens = {s["n"] for s in S if est_ensemble(s)}
    for gi, g in enumerate(d.get("groupes") or []):
        avec = [s for s in S if any(b[0] == gi for b in s.get("g") or [])]
        nums = ens | {s["n"] for s in avec[-20:]} | {s["n"] for s in [x for x in avec if est_sol(x)][-20:]}
        ecrire(f"groupe/{g['id']}", {"graine": f"groupe/{g['id']}", "noms": 1, "scrutins": [sans(s, "v") for s in ordre(nums)]})

    # Listes : les premières lignes dans l'ordre par défaut, et le total
    def date_loi(l):
        if l.get("prom"):
            return l["prom"].get("date")
        e = (l.get("etapes") or [])
        return (e[-1][2] if e and len(e[-1]) > 2 else None) or ""
    ecrire("lois", {"graine": "lois", "lois": trier(L, date_loi, -1)[:MARGE["lois"]], "vue": {"tot": len(L)}})
    ecrire("votes", {"graine": "votes", "scrutins": [sans(s, "v") for s in ordre({x["n"] for x in trier(S, lambda s: s["n"], -1)[:MARGE["votes"]]})],
                     "vue": {"tot": len(S), "du": S[0]["d"], "au": S[-1]["d"]}})
    actifs = [x for x in D if x.get("actif")] or D
    garde = {x["id"] for x in sorted(actifs, key=cle_nom)[:MARGE["elus"]]}
    ecrire("elus", {"graine": "elus", "deputes": [x for x in D if x["id"] in garde],
                    "vue": {"actifs": len(actifs), "depts": sorted({x["dept"] for x in D if x.get("dept")})}})

    # Actualités : lois promulguées, votes solennels et motions de censure de toute la législature
    ecrire("actualites", {"graine": "actualites", "lois": [l for l in L if l.get("prom")],
                          "scrutins": [sans(s, "v") for s in S if est_sol(s) or est_moc(s)]})

    # La semaine : chaque semaine de la législature, et la dernière semaine de vote par défaut
    du = d.get("du") or S[0]["d"][:10]
    aujourdhui = datetime.date.today().isoformat()
    lundi, fin = lundi_de(du), lundi_de(max(aujourdhui, S[-1]["d"][:10]))
    while lundi <= fin:
        dimanche = (datetime.date.fromisoformat(lundi) + datetime.timedelta(days=6)).isoformat()
        dans = lambda x: bool(x) and lundi <= x[:10] <= dimanche
        contenu = {"scrutins": [sans(s, "v", "g", "m") for s in S if dans(s["d"])],
                   "lois": [l for l in L if (l.get("prom") and dans(l["prom"].get("date")))
                            or ((l.get("etapes") or [[]])[0][:1] and "DEPOT" in l["etapes"][0][0] and dans(l["etapes"][0][2]))]}
        ecrire(f"semaine/{lundi}", dict({"graine": f"semaine/{lundi}"}, **contenu))
        if lundi == lundi_de(S[-1]["d"][:10]):
            ecrire("semaine", dict({"graine": "semaine"}, **contenu))
        lundi = (datetime.date.fromisoformat(lundi) + datetime.timedelta(days=7)).isoformat()

    # Le mois à l'Assemblée : chaque mois, et le dernier par défaut
    mois = sorted({s["d"][:7] for s in S} | {l["prom"]["date"][:7] for l in L
                                              if l.get("prom") and l["prom"].get("date") and l["prom"]["date"] >= du})
    for m in mois:
        scr = [s for s in S if s["d"].startswith(m)]
        nums = {s["n"] for s in scr}
        lois = [l for l in L if (l.get("prom") and (l["prom"].get("date") or "").startswith(m))
                or any((e[2] if len(e) > 2 else "") and e[2].startswith(m) for e in l.get("etapes") or [])
                or nums & set(l.get("scrutins") or [])]
        contenu = {"scrutins": [sans(s, "v", "g", "m") for s in scr], "lois": lois, "vue": {"mois": mois}}
        ecrire(f"calendrier/{m}", dict({"graine": f"calendrier/{m}"}, **contenu))
        if m == mois[-1]:
            ecrire("calendrier", dict({"graine": "calendrier"}, **contenu))

    # Thèmes : le nombre de scrutins par thème, et les 30 derniers votes importants de chacun
    try:
        themes = themes_du_site(os.path.join(site_dir, "app.js"))
        th = {s["n"]: theme_de(s, themes) for s in S}
        cpt = {}
        for t in th.values():
            if t:
                cpt[t] = cpt.get(t, 0) + 1
        dispo = [t for t, _, _ in themes if cpt.get(t)]
        defaut = sorted(dispo, key=lambda t: -cpt[t])[0] if dispo else None
        for t in dispo:
            L30 = [s for s in S if th[s["n"]] == t and (est_ensemble(s) or est_sol(s))][-30:]
            contenu = {"scrutins": [sans(s, "v") for s in L30], "vue": {"cpt": cpt}}
            ecrire(f"themes/{t}", dict({"graine": f"themes/{t}"}, **contenu))
            if t == defaut:
                ecrire("themes", dict({"graine": "themes"}, **contenu))
    except Exception as e:
        print(f"Graines : thèmes non écrits ({e})")

    # « Comment on vérifie » : le dernier scrutin solennel
    sols = [s for s in S if est_sol(s) and not est_moc(s)] or [s for s in S if not est_moc(s)]
    if sols:
        ecrire("verifier", {"graine": "verifier", "noms": 1, "scrutins": [sols[-1]]})

    # Comparateur : tous les scrutins sans leur détail, la position de chaque groupe à chaque scrutin (« gp », un caractère
    # par scrutin), et le vote de chaque député dans un fichier à part (v/PA….json), lu seulement pour les deux comparés
    colonnes = {dp["id"]: "".join(s["v"][i] for s in S) for i, dp in enumerate(D)}
    for ident, col in colonnes.items():
        ecrire(f"v/{ident}", {"v": col})
    gp = ["".join(str(next((b[2] for b in s.get("g") or [] if b[0] == gi and 1 <= b[2] <= 3), 0)) for s in S)
          for gi in range(len(d.get("groupes") or []))]
    # paire affichée par défaut (pageCmp) : le premier député en exercice, et le premier d'un autre groupe
    a = actifs[0]
    b = next((x for x in actifs if x["groupe"] != a["groupe"]), None)
    ecrire("cmp", {"graine": "cmp", "noms": 1, "scrutins": [{k: s[k] for k in ("n", "d", "t", "ti")} for s in S], "gp": gp,
                   "cols": {x["id"]: colonnes[x["id"]] for x in (a, b) if x}})

    return {"dir": f"g/{leg}/", "maj": maj, "base": base}, nb
