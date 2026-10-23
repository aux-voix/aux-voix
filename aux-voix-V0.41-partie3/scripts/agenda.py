#!/usr/bin/env python3
"""Aux Voix : l'ordre du jour à venir de l'Assemblée nationale (séances publiques), depuis le jeu « Agenda » des
données ouvertes de l'Assemblée (Licence Ouverte). Écrit site/agenda.json. Facultatif : en cas d'échec, le fichier
précédent est conservé."""
import datetime, io, json, os, re, unicodedata, zipfile

URL = "https://data.assemblee-nationale.fr/static/openData/repository/{leg}/vp/reunions/Agenda.json.zip"
SUPPRIMES = ("supprim", "annul", "report")


def liste(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


SANS_VOTE = re.compile(r"^vote solennel (?:sur )?(?:l ensemble )?(?:du |de la |des |de l |le |la |les )?", re.I)
PREFIXE = re.compile(r"^(?:suite de la )?discussion,? (?:en [^,]+ lecture,? )?(?:de la |du |des |de l['’]|d['’]|de )?", re.I)


def points_seance(r):
    odj = (r.get("ODJ") or {}).get("pointsODJ") or {}
    sortie, vus = [], set()
    for p in liste(odj.get("pointODJ")):
        etat = ((p.get("cycleDeVie") or {}).get("etat") or "").lower()
        objet = re.sub(r"\s+", " ", (p.get("objet") or "")).strip().rstrip(".")
        # l'intitulé « Journée réservée au groupe… » est publié comme un point « supprimé » qui sert d'en-tête : on le garde
        if any(x in etat for x in SUPPRIMES) and not re.match(r"(?i)journ[ée]e r[ée]serv", objet):
            continue
        if not objet:
            continue
        dossier = (p.get("dossiersLegislatifsRefs") or {}).get("dossierRef")
        if isinstance(dossier, list):
            dossier = dossier[0] if dossier else None
        typ = (p.get("typePointODJ") or "").strip()
        cle = (typ, norm(PREFIXE.sub("", objet)), dossier)
        if cle in vus:
            continue
        vus.add(cle)
        sortie.append([typ, objet, dossier])
    return sortie


def construire_agenda(site_dir, telecharger, leg="17", aujourd_hui=None):
    aujourd_hui = aujourd_hui or datetime.date.today().isoformat()
    data = telecharger(URL.format(leg=leg), requis=False)
    if not data:
        raise RuntimeError("jeu « Agenda » indisponible")
    seances = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for nom in z.namelist():
            if not nom.endswith(".json"):
                continue
            try:
                r = json.loads(z.read(nom).decode("utf-8")).get("reunion") or {}
            except Exception:
                continue
            if r.get("@xsi:type") != "seance_type":
                continue
            debut = r.get("timeStampDebut") or ""
            if debut[:10] < aujourd_hui:
                continue
            etat = ((r.get("cycleDeVie") or {}).get("etat") or "").lower()
            if any(x in etat for x in SUPPRIMES):
                continue
            P = points_seance(r)
            if not P:
                continue
            seances.append({"d": debut[:16], "q": ((r.get("identifiants") or {}).get("quantieme") or ""), "e": etat, "p": P})
    seances.sort(key=lambda s: s["d"])
    # un vote solennel ne porte pas de référence de dossier : on la retrouve par le titre du texte discuté
    titres = {}
    for s in seances:
        for typ, objet, dossier in s["p"]:
            if dossier:
                titres.setdefault(norm(PREFIXE.sub("", objet)).split(" premiere partie")[0].split(" seconde partie")[0], dossier)
    for s in seances:
        for p in s["p"]:
            if p[2] is None and norm(p[0]).startswith("vote solennel"):
                cible = norm(SANS_VOTE.sub("", norm(p[1])))
                for t, d in titres.items():
                    if t and (cible.startswith(t) or t.startswith(cible)):
                        p[2] = d
                        break
    sortie = {"maj": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "leg": leg,
              "source": URL.format(leg=leg), "s": seances}
    with open(os.path.join(site_dir, "agenda.json"), "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, separators=(",", ":"))
    votes = sum(1 for s in seances for p in s["p"] if norm(p[0]).startswith("vote solennel"))
    return len(seances), votes


if __name__ == "__main__":
    import sys
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fichier = sys.argv[1] if len(sys.argv) > 1 else None
    tel = (lambda url, requis=True: open(fichier, "rb").read()) if fichier else None
    if tel is None:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from construire_donnees import telecharger as tel
    print(construire_agenda(os.path.join(racine, "site"), tel, aujourd_hui=(sys.argv[2] if len(sys.argv) > 2 else None)))
