# -*- coding: utf-8 -*-
"""Génère les PDF des cours (cours, TD élève, corrigé enseignant) dans site/cours/pdf/.
À lancer en local après toute modification de site/contenu/cours.json :  python3 scripts/pdf_cours.py"""
import json, os, sys
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, KeepTogether

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEU = colors.HexColor("#123B6D")
GRIS = colors.HexColor("#5A6169")


def t(s):
    s = s.replace("−", "-").replace(" ", " ").replace("≥", "au moins ")
    return escape(s.encode("cp1252", "replace").decode("cp1252"))


ST = {
    "titre": ParagraphStyle("titre", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=BLEU, spaceAfter=4),
    "sous": ParagraphStyle("sous", fontName="Helvetica", fontSize=10.5, leading=14, textColor=GRIS, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17, textColor=BLEU, spaceBefore=14, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11.5, leading=15, spaceBefore=9, spaceAfter=3),
    "p": ParagraphStyle("p", fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=5),
    "q": ParagraphStyle("q", fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=2),
    "c": ParagraphStyle("c", fontName="Helvetica", fontSize=10, leading=14, textColor=GRIS, leftIndent=0),
    "doc": ParagraphStyle("doc", fontName="Helvetica", fontSize=10.5, leading=15, backColor=colors.HexColor("#F5F7F9"), borderColor=BLEU, borderWidth=0, borderPadding=8, spaceBefore=6, spaceAfter=12),
}


def pied(titre):
    def f(c, d):
        c.saveState()
        c.setFont("Helvetica", 8.5)
        c.setFillColor(GRIS)
        c.drawString(2 * cm, 1.1 * cm, t("Aux Voix · auxvoix.fr · supports neutres, rédigés avec l'aide d'une IA, à vérifier avec les sources officielles"))
        c.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"{d.page}")
        c.restoreState()
    return f


def liste(items, style="q"):
    return ListFlowable([ListItem(Paragraph(t(x), ST[style]), leftIndent=14) for x in items], bulletType="1", bulletFontName="Helvetica-Bold", bulletFontSize=10.5, leftIndent=18)


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
    if genre == "cours":
        S += [Paragraph(t("Objectif : " + c["objectif"]), ST["p"]), Paragraph(t(c["intro"]), ST["p"])]
        for p in c["parties"]:
            S.append(Paragraph(t(p["h"]), ST["h3"]))
            S += [Paragraph(t(x), ST["p"]) for x in p["p"]]
        S.append(Paragraph("À retenir", ST["h2"]))
        S.append(ListFlowable([ListItem(Paragraph(t(x), ST["p"]), leftIndent=14) for x in c["retenir"]], bulletType="bullet", start="•", leftIndent=16))
        S.append(Paragraph("Vocabulaire", ST["h2"]))
        tab = Table([[Paragraph(f"<b>{t(m)}</b>", ST["q"]), Paragraph(t(d), ST["q"])] for m, d in c["mots"]], colWidths=[4.3 * cm, 12.7 * cm])
        tab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE1E5")), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        S.append(tab)
        if c.get("liens"):
            S.append(Paragraph("Pour aller plus loin", ST["h2"]))
            S += [Paragraph(f"{t(a)} : {escape(u)}", ST["q"]) for a, u in c["liens"]]
    elif genre == "td":
        S.append(Paragraph("Nom : ______________________________   Date : ______________", ST["p"]))
        S.append(Paragraph(t(td["consigne"]), ST["p"]))
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
