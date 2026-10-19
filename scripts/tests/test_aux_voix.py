"""Tests rapides, sans réseau : lancés avant chaque mise à jour (python -m unittest discover -s scripts/tests).
Si l'un échoue, la mise à jour s'arrête et le site en ligne n'est pas modifié."""
import io, json, os, sys, tempfile, unittest, zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agenda, codes, graines  # noqa: E402


class Codes(unittest.TestCase):
    def test_intitules_fusionnes_redecoupes(self):
        brut = ["Livre III : Des différentes manières dont on acquiert la propriété - Titre IV : Des engagements qui se forment "
                "sans convention - Titre IV : Du régime général des obligations - Chapitre Ier : Des quasi-contrats. - Chapitre Ier : "
                "Les modalités de l'obligation - Section 3 : L'obligation plurale", "- Sous-section 1 : La pluralité d'objets  - Paragraphe 1 : L'obligation cumulative"]
        self.assertEqual(codes.normaliser_chemins([brut])[0], [
            "Livre III : Des différentes manières dont on acquiert la propriété", "Titre IV : Du régime général des obligations",
            "Chapitre Ier : Les modalités de l'obligation", "Section 3 : L'obligation plurale",
            "Sous-section 1 : La pluralité d'objets", "Paragraphe 1 : L'obligation cumulative"])

    def test_renumerotation_garde_le_plus_grand_numero(self):
        self.assertEqual(codes.normaliser_chemins([["Titre XII : Des collectivités territoriales", "Titre XI : Des collectivités territoriales"]])[0],
                         ["Titre XII : Des collectivités territoriales"])
        self.assertEqual(codes.normaliser_chemins([["Titre XVI : De la révision", "Titre XV : De la révision", "Titre XIV : De la révision"]])[0],
                         ["Titre XVI : De la révision"])

    def test_meme_numero_ancienne_presentation_ecartee(self):
        self.assertEqual(codes.normaliser_chemins([["Titre IX : La Haute Cour", "Titre IX : La Haute Cour de Justice."]])[0], ["Titre IX : La Haute Cour"])

    def test_titre_officiel_avec_tiret_conserve(self):
        t = "Chapitre II : Des qualités requises pour succéder - De la preuve de la qualité d'héritier."
        self.assertEqual(codes.normaliser_chemins([[t]])[0], [t])

    def test_rang_numero(self):
        self.assertEqual(codes.rang_numero("Titre XI bis : Le Défenseur des droits"), (11, 1))
        self.assertEqual(codes.rang_numero("Livre Ier : Des personnes"), (1, 0))
        self.assertEqual(codes.rang_numero("Titre premier : De la souveraineté"), (1, 0))

    def test_article_legi_garde_l_intitule_en_vigueur(self):
        xml = """<ARTICLE><META><META_COMMUN><ID>LEGIARTI000000000001</ID></META_COMMUN><META_SPEC><META_ARTICLE><NUM>1</NUM>
        <ETAT>VIGUEUR</ETAT><DATE_DEBUT>2024-01-01</DATE_DEBUT><DATE_FIN>2999-01-01</DATE_FIN></META_ARTICLE></META_SPEC></META>
        <CONTEXTE><TEXTE><TM><TITRE_TM debut="1990-01-01" fin="2024-01-01">Chapitre Ier : Ancien</TITRE_TM>
        <TITRE_TM debut="2024-01-01" fin="2999-01-01">Chapitre Ier : Nouveau</TITRE_TM></TM></TEXTE></CONTEXTE>
        <BLOC_TEXTUEL><CONTENU>Texte.</CONTENU></BLOC_TEXTUEL></ARTICLE>"""
        self.assertEqual(codes.lire_article(xml.encode())["chemin"], ["Chapitre Ier : Nouveau"])


class Agenda(unittest.TestCase):
    def zip_agenda(self, reunions):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            for i, r in enumerate(reunions):
                z.writestr(f"json/reunion/R{i}.json", json.dumps({"reunion": r}))
        return b.getvalue()

    def seance(self, debut, points, etat="Confirmé"):
        return {"@xsi:type": "seance_type", "timeStampDebut": debut, "cycleDeVie": {"etat": etat}, "identifiants": {"quantieme": "Première"},
                "ODJ": {"pointsODJ": {"pointODJ": points}}}

    def point(self, typ, objet, dossier=None, etat="Confirmé"):
        return {"typePointODJ": typ, "objet": objet, "cycleDeVie": {"etat": etat},
                "dossiersLegislatifsRefs": {"dossierRef": dossier} if dossier else None}

    def test_agenda(self):
        data = self.zip_agenda([
            self.seance("2026-10-19T15:00:00.000+02:00", [self.point("Discussion", "Discussion du projet de loi de finances pour 2027 (première partie)", "DLR5L17N1")]),
            self.seance("2026-10-20T15:00:00.000+02:00", [self.point("Vote solennel", "Vote solennel sur le projet de loi de finances pour 2027 (première partie).")]),
            self.seance("2026-10-29T09:00:00.000+01:00", [self.point("Séances réservées", "Journée réservée au groupe X", etat="Supprimé"),
                                                          self.point("Discussion", "Point annulé", "DLR5L17N2", etat="Supprimé")]),
            self.seance("2026-10-01T15:00:00.000+02:00", [self.point("Discussion", "Séance passée", "DLR5L17N3")]),
            self.seance("2026-10-21T15:00:00.000+02:00", [self.point("Discussion", "Séance supprimée", "DLR5L17N4")], etat="Supprimé"),
        ])
        with tempfile.TemporaryDirectory() as d:
            nb, votes = agenda.construire_agenda(d, lambda url, requis=True: data, "17", aujourd_hui="2026-10-18")
            with open(os.path.join(d, "agenda.json"), encoding="utf-8") as f:
                a = json.load(f)
        self.assertEqual((nb, votes), (3, 1))
        self.assertEqual([s["d"] for s in a["s"]], ["2026-10-19T15:00", "2026-10-20T15:00", "2026-10-29T09:00"])
        self.assertEqual(a["s"][1]["p"][0][2], "DLR5L17N1")          # vote solennel rattaché au texte
        self.assertEqual(a["s"][2]["p"], [["Séances réservées", "Journée réservée au groupe X", None]])  # en-tête gardé, point supprimé retiré


if __name__ == "__main__":
    unittest.main()


class Graines(unittest.TestCase):
    """Petits fichiers par page : contenu attendu sur une législature fictive."""

    def construire(self):
        dossier = tempfile.mkdtemp()
        site = os.path.join(dossier, "site")
        os.makedirs(site)
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(racine, "site", "app.js"), encoding="utf-8") as f, open(os.path.join(site, "app.js"), "w", encoding="utf-8") as g:
            g.write(f.read())
        st = lambda el, part: {"el": el, "vo": 0, "elS": 0, "voS": 0, "alN": 0, "al": 0, "part": part, "partS": part, "align": part}
        deps = [{"id": f"PA{i}", "civ": "M.", "prenom": f"P{i}", "nom": f"Nom{i:02d}", "groupe": i % 2, "seg": [[1, 60, i % 2]], "actif": i < 5,
                 "dept": "Ain" if i % 2 else "Aube", "numDept": "01", "circ": 1, "commission": "Lois" if i < 3 else "Finances",
                 "st": [st(30, 0.1 * i), st(30, 0.1 * i)]} for i in range(6)]
        scr = []
        for n in range(1, 61):
            t = "SPS" if n % 10 == 0 else "SPO"
            ti = "l'ensemble du projet de loi relatif à l'agriculture" if n % 10 == 0 else f"l'amendement n° {n} du projet de loi relatif à l'agriculture"
            scr.append({"n": n, "d": f"2026-0{1 + (n - 1) // 20}-{1 + (n - 1) % 20:02d}", "t": t, "ti": ti, "so": "adopté", "po": 10, "co": 5, "ab": 0,
                        "g": [[0, 3, 1, 2, 1, 0, 0], [1, 3, 2, 1, 2, 0, 0]], "m": [], "v": "".join("1" if (k + n) % 3 else "-" for k in range(6))})
        lois = [{"id": "DLR5L17N1", "titre": "Projet de loi relatif à l'agriculture", "scrutins": [10, 20], "auteurs": ["PA1"], "rapporteurs": ["PX9"],
                 "etapes": [["AN1-DEPOT", "Dépôt", "2026-01-01"]], "prom": None},
                {"id": "DLR5L17N2", "titre": "Proposition de loi visant à tester", "scrutins": [], "auteurs": [], "rapporteurs": [],
                 "etapes": [["AN1-DEPOT", "Dépôt", "2026-02-15"]], "prom": {"date": "2026-03-01"}}]
        data = {"legislature": "17", "label": "17e législature", "du": "2026-01-01", "au": None, "courante": True, "maj": "2026-03-05T05:00Z",
                "periodes": [{"id": 0, "label": "2026", "du": "2026-01-01", "au": "2026-12-31"}], "medianes": [{}, {}],
                "groupes": [{"id": "PO1", "sigle": "A"}, {"id": "PO2", "sigle": "B"}], "lois": lois, "personnes": {"PX9": {"p": "Marie", "n": "Sénat"}},
                "deputes": deps, "scrutins": scr, "sources": {}, "amendements": {}}
        with open(os.path.join(site, "data-17.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        info, nb = graines.ecrire_graines(site, {"leg": "17", "fichier": "data-17.json"})
        def lire(nom):
            with open(os.path.join(site, "g", "17", nom + ".json"), encoding="utf-8") as f:
                return json.load(f)
        return info, nb, lire

    def test_graines(self):
        info, nb, lire = self.construire()
        self.assertEqual(info["dir"], "g/17/")
        self.assertNotIn("scrutins", info["base"])
        # médianes de groupe (députés actifs avec au moins 20 scrutins) : groupe 0 = députés 0, 2, 4
        self.assertAlmostEqual(info["base"]["ctx"]["1"]["g"]["0"]["part"], 0.2)
        self.assertAlmostEqual(info["base"]["ctx"]["1"]["c"]["Lois"]["part"], 0.1)
        # fiche d'un député : ses 25 derniers votes et ses votes solennels, son seul vote gardé, ses textes
        e = lire("elu/PA1")
        mandat = [n for n in range(1, 61) if (1 + n) % 3]
        attendus = set(mandat[-25:]) | {n for n in mandat if n % 10 == 0} | {1, 60}
        self.assertEqual({s["n"] for s in e["scrutins"]}, attendus)
        self.assertEqual(e["vi"], 1)
        self.assertTrue(all("v" not in s and s["vi"] in "1-" for s in e["scrutins"]))
        self.assertEqual([l["id"] for l in e["lois"]], ["DLR5L17N1"])
        # votes par paquets de 50, avec le texte rattaché par son titre
        p0 = lire("scrutin/0")
        self.assertEqual([s["n"] for s in p0["scrutins"]], list(range(1, 50)))
        self.assertEqual([l["id"] for l in p0["lois"]], ["DLR5L17N1"])
        self.assertEqual(len(p0["scrutins"][0]["v"]), 6)
        # loi : ses scrutins et la personne non députée citée
        l = lire("loi/DLR5L17N1")
        self.assertEqual([s["n"] for s in l["scrutins"]], [10, 20])
        self.assertIn("PX9", l["personnes"])
        # listes : ordre par défaut du site et total
        self.assertEqual([x["id"] for x in lire("lois")["lois"]], ["DLR5L17N2", "DLR5L17N1"])
        self.assertEqual(lire("votes")["scrutins"][-1]["n"], 60)
        self.assertEqual(lire("votes")["vue"], {"tot": 60, "du": "2026-01-01", "au": "2026-03-20"})
        self.assertEqual(lire("elus")["vue"]["actifs"], 5)
        # thèmes lus dans app.js : « agriculture » reconnu
        self.assertEqual(lire("themes")["vue"]["cpt"], {"agriculture": 60})
        # semaine et mois par défaut : les derniers
        self.assertEqual(lire("semaine")["graine"], "semaine")
        self.assertTrue(all(s["d"] >= "2026-03-16" for s in lire("semaine")["scrutins"]))
        self.assertEqual(lire("calendrier")["vue"]["mois"], ["2026-01", "2026-02", "2026-03"])
        self.assertTrue(all(x["maj"] == "2026-03-05T05:00Z" for x in (lire("noms"), lire("verifier"))))
