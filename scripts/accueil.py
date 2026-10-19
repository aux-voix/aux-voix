#!/usr/bin/env python3
"""Aux Voix : fichier léger de l'accueil (accueil-17.json).

L'accueil n'a besoin que des derniers jours de vote, des groupes et de quelques textes. Ce fichier, une centaine de
fois plus léger que data-17.json, permet d'afficher l'accueil tout de suite ; le fichier complet n'est téléchargé que
lorsqu'on ouvre une autre page (ou qu'on s'apprête à le faire). Même structure que data-17.json, avec "lite": true."""
import datetime, json, os, re, unicodedata

JOURS = 10   # jours de vote gardés : de quoi retrouver la dernière séance et ses votes


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if not "̀" <= c <= "ͯ").lower()


def texte_de(ti):
    """Même règle que texteDe() dans le site."""
    m = re.search(r"((?:du |de la |de l')?(?:projet|proposition) de loi[^()]*)", str(ti), re.I)
    return re.sub(r"^(du |de la |de l')", "", m.group(1), flags=re.I).strip() if m else None


def queue_titre(x):
    """Même règle que queueTitre() dans le site."""
    t = norm(x).replace("’", "'").strip()
    t = re.sub(r"^(projet|proposition) de loi (organique |constitutionnelle )?", "", t)
    t = re.sub(r"^\S+\s+", "", t)
    t = re.sub(r"[\s,.;:]+$", "", t)
    return re.sub(r"\s+", " ", t)


def ecrire_accueil(site_dir, entree):
    """entree : la ligne de index.json de la législature en cours. Renvoie le nom du fichier écrit."""
    leg = entree["leg"]
    d = json.load(open(os.path.join(site_dir, entree["fichier"]), encoding="utf-8"))
    S = d.get("scrutins") or []
    if not S:
        raise RuntimeError("aucun scrutin")
    dernier = max(s["d"][:10] for s in S)
    debut = (datetime.date.fromisoformat(dernier) - datetime.timedelta(days=JOURS)).isoformat()
    garde = [s for s in S if s["d"][:10] >= debut]
    nums = {s["n"] for s in garde}
    lois = d.get("lois") or []
    retenues = {l["id"] for l in lois if nums & set(l.get("scrutins") or [])}
    # votes sans lien direct vers leur texte : même rattachement par le titre que le site (loiDe)
    lies = {k for l in lois for k in l.get("scrutins") or []}
    motif = re.compile(f"L{leg}N")
    par_titre = {}
    for l in lois:
        if motif.search(l["id"]):
            q = queue_titre(l["titre"])
            par_titre[q] = None if q in par_titre else l["id"]
    for s in garde:
        if s["n"] in lies:
            continue
        tx = texte_de(s.get("ti", ""))
        if tx:
            k = queue_titre(tx)
            if len(k.split(" ")) >= 4 and par_titre.get(k):
                retenues.add(par_titre[k])
    # textes cités par l'ordre du jour à venir (carte « Prochain vote solennel »)
    try:
        ag = json.load(open(os.path.join(site_dir, "agenda.json"), encoding="utf-8"))
        retenues |= {p[2] for x in ag.get("s", []) for p in x.get("p", []) if p[2]}
    except Exception:
        pass
    lite = {k: v for k, v in d.items() if k not in ("scrutins", "lois", "deputes", "personnes")}
    lite.update({"lite": True, "scrutins": [{k: v for k, v in s.items() if k != "v"} for s in garde],
                 "lois": [l for l in lois if l["id"] in retenues], "deputes": [], "personnes": {}})
    nom = f"accueil-{leg}.json"
    with open(os.path.join(site_dir, nom), "w", encoding="utf-8") as f:
        json.dump(lite, f, ensure_ascii=False, separators=(",", ":"))
    return nom, len(garde), len(lite["lois"]), os.path.getsize(os.path.join(site_dir, nom))
