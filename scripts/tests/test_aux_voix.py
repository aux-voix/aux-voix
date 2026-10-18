"""Tests rapides, sans réseau : lancés avant chaque mise à jour (python -m unittest discover -s scripts/tests).
Si l'un échoue, la mise à jour s'arrête et le site en ligne n'est pas modifié."""
import io, json, os, sys, tempfile, unittest, zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agenda, codes  # noqa: E402


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
