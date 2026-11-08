# -*- coding: utf-8 -*-
"""Génère les PDF des cours (cours, TD élève, corrigé enseignant) dans site/cours/pdf/.
À lancer en local après toute modification de site/contenu/cours.json :  python3 scripts/pdf_cours.py"""
import json, os, sys
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mise_en_forme import Forme
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, KeepTogether

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEU = colors.HexColor("#123B6D")
GRIS = colors.HexColor("#5A6169")


def polices():
    """Lexend (titres) et Source Sans 3 (texte), incorporées au PDF. Repli sur Helvetica si les fichiers manquent.
    Les polices variables (.ttf) sont cherchées dans $AUXVOIX_POLICES ou dans le dossier fonts/ ; on en tire des instances fixes."""
    dossier = os.environ.get("AUXVOIX_POLICES") or os.path.join(RACINE, "fonts")
    try:
        from fontTools.ttLib import TTFont as FT
        from fontTools.varLib.instancer import instantiateVariableFont
        tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "auxvoix_polices")
        os.makedirs(tmp, exist_ok=True)

        def inst(src, poids, nom):
            sortie = os.path.join(tmp, nom + ".ttf")
            if not os.path.exists(sortie):
                f = FT(os.path.join(dossier, src))
                if "fvar" in f:
                    instantiateVariableFont(f, {"wght": poids}, inplace=True)
                for rec in f["name"].names:   # nom PostScript distinct, sinon reportlab fusionne les graisses
                    if rec.nameID in (1, 4, 6):
                        rec.string = nom if rec.nameID == 6 else nom.replace("-", " ")
                f.save(sortie)
            pdfmetrics.registerFont(TTFont(nom, sortie))
        inst("Lexend.ttf", 700, "AV-Titre")
        inst("SS3.ttf", 400, "AV-Texte")
        inst("SS3.ttf", 700, "AV-Gras")
        inst("SS3i.ttf", 400, "AV-Ital")
        pdfmetrics.registerFontFamily("AV-Texte", normal="AV-Texte", bold="AV-Gras", italic="AV-Ital", boldItalic="AV-Gras")
        return "AV-Titre", "AV-Texte", "AV-Gras"
    except Exception as e:
        print("Polices non trouvées, repli Helvetica :", e)
        return "Helvetica-Bold", "Helvetica", "Helvetica-Bold"


FT_TITRE, FT_TEXTE, FT_GRAS = polices()
JAUNE = colors.HexColor("#F3C24F")


def t(s):
    s = s.replace("\u2212", "-").replace("\u202f", "\u00a0").replace("\u2265", "au moins ")
    return escape(s)


def fmt(c):
    """Mise en forme riche (gras, souligné, surligné) identique à celle du site."""
    return Forme(c, lambda x: escape(x), lambda x: f"<b>{x}</b>", lambda x: f"<u>{x}</u>", lambda x: f'<font backColor="#FFF1BF">{x}</font>')


ST = {
    "titre": ParagraphStyle("titre", fontName=FT_TITRE, fontSize=22, leading=27, textColor=BLEU, alignment=TA_CENTER, spaceAfter=6),
    "sous": ParagraphStyle("sous", fontName=FT_TEXTE, fontSize=11, leading=15, textColor=GRIS, alignment=TA_CENTER, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName=FT_TITRE, fontSize=14, leading=18, textColor=BLEU, alignment=TA_CENTER, spaceBefore=16, spaceAfter=3),
    "h3": ParagraphStyle("h3", fontName=FT_TITRE, fontSize=11.5, leading=15, textColor=BLEU, spaceBefore=10, spaceAfter=3, leftIndent=8, borderPadding=(0, 0, 0, 0)),
    "p": ParagraphStyle("p", fontName=FT_TEXTE, fontSize=11, leading=16, spaceAfter=6),
    "q": ParagraphStyle("q", fontName=FT_TEXTE, fontSize=11, leading=15.5, spaceAfter=2),
    "c": ParagraphStyle("c", fontName=FT_TEXTE, fontSize=10.5, leading=14.5, textColor=GRIS, leftIndent=0),
    "doc": ParagraphStyle("doc", fontName=FT_TEXTE, fontSize=11, leading=16, backColor=colors.HexColor("#F5F7F9"), borderColor=BLEU, borderWidth=0, borderPadding=9, spaceBefore=8, spaceAfter=14),
    "ret": ParagraphStyle("ret", fontName=FT_TEXTE, fontSize=11, leading=15.5, leftIndent=0),
}


def pied(titre):
    def f(c, d):
        c.saveState()
        c.setFont(FT_TEXTE, 8.5)
        c.setFillColor(GRIS)
        c.drawString(2 * cm, 1.1 * cm, t("Aux Voix · auxvoix.fr · supports neutres, rédigés avec l'aide d'une IA, à vérifier avec les sources officielles"))
        c.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"{d.page}")
        c.restoreState()
    return f


def titre2(texte):
    from reportlab.platypus import HRFlowable
    return [Paragraph(texte, ST["h2"]), HRFlowable(width=1.6 * cm, thickness=2.2, color=JAUNE, spaceAfter=7, hAlign="CENTER")]


def liste(items, style="q"):
    return ListFlowable([ListItem(Paragraph(t(x), ST[style]), leftIndent=14) for x in items], bulletType="1", bulletFontName=FT_GRAS, bulletFontSize=10.5, leftIndent=18)


def questions(td):
    out = []
    for i, q in enumerate(td["questions"], 1):
        bloc = [Paragraph(f"<b>{i}.</b> {t(q['q'])}", ST["q"])]
        for k, ch in enumerate(q.get("choix", [])):
            bloc.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{'abc'[k]}) {t(ch)}", ST["c"]))
        if not q.get("choix"):
            bloc.append(Spacer(1, 1.3 * cm))   # place pour répondre
        else:
            bloc.append(Spacer(1, 0.3 * cm))
        out.append(KeepTogether(bloc))
    return out


def construire(c, genre, dossier):
    nom = {"cours": "cours", "td": "td", "corrige": "corrige"}[genre]
    fichier = os.path.join(dossier, f"{c['slug']}-{nom}.pdf")
    doc = SimpleDocTemplate(fichier, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                            title=f"{c['titre']} ({ {'cours': 'cours', 'td': 'TD', 'corrige': 'corrigé'}[genre] })", author="Rédaction Aux Voix")
    S = []
    suffixe = {"cours": "Cours", "td": "TD, version élève", "corrige": "Corrigé, version enseignant"}[genre]
    S += [Paragraph(t(c["titre"]), ST["titre"]), Paragraph(t(f"{suffixe} · {c['niveau']} · {c['duree']}"), ST["sous"])]
    td = c["td"]
    F = fmt(c)
    if genre == "cours":
        S += [Paragraph("<b>Objectif :</b> " + t(c["objectif"]), ST["p"])]
        S += titre2("Le cours")
        S.append(Paragraph(F(c["intro"]), ST["p"]))
        for p in c["parties"]:
            S.append(Paragraph(t(p["h"]), ST["h3"]))
            S += [Paragraph(F(x), ST["p"]) for x in p["p"]]
        ret = [Paragraph("À retenir", ParagraphStyle("rh", parent=ST["h2"], spaceBefore=0, spaceAfter=6))]
        ret += [Paragraph("• " + F(x, auto=False), ST["ret"]) for x in c["retenir"]]
        boite = Table([[ret]], colWidths=[17 * cm])
        boite.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")), ("LINEBEFORE", (0, 0), (0, -1), 3, JAUNE),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        S += [Spacer(1, 10), boite]
        S += titre2("Vocabulaire")
        tab = Table([[Paragraph(f"<b>{t(m)}</b>", ST["q"]), Paragraph(t(d), ST["q"])] for m, d in c["mots"]], colWidths=[4.3 * cm, 12.7 * cm])
        tab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE1E5")), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        S.append(tab)
        if c.get("liens"):
            S += titre2("Pour aller plus loin")
            S += [Paragraph(f"{t(a)} : {escape(u)}", ST["q"]) for a, u in c["liens"]]
    elif genre == "td":
        S.append(Paragraph("Nom : ______________________________   Date : ______________", ST["p"]))
        S.append(Paragraph("<b>Consigne.</b> " + F(td["consigne"], auto=False), ST["p"]))
        if td.get("doc"):
            S.append(Paragraph(t(td["doc"]), ST["doc"]))
        S += questions(td)
    else:
        S.append(Paragraph(t("Éléments de réponse. Pour les questions à réponse libre, on valorise l'exactitude des faits et la reformulation fidèle, jamais l'opinion personnelle."), ST["p"]))
        for i, q in enumerate(td["questions"], 1):
            S.append(KeepTogether([Paragraph(f"<b>{i}.</b> {t(q['q'])}", ST["c"]), Paragraph(f"<b>Réponse :</b> {t(q['rep'])}", ST["p"]), Spacer(1, 4)]))
    f = pied(c["titre"])
    doc.build(S, onFirstPage=f, onLaterPages=f)
    return fichier


def main():
    C = json.load(open(os.path.join(RACINE, "site", "contenu", "cours.json"), encoding="utf-8"))["cours"]
    dossier = os.path.join(RACINE, "site", "cours", "pdf")
    os.makedirs(dossier, exist_ok=True)
    n = 0
    for c in C:
        for g in ("cours", "td", "corrige"):
            construire(c, g, dossier)
            n += 1
    print(n, "PDF dans", dossier)


if __name__ == "__main__":
    main()
