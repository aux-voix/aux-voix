# -*- coding: utf-8 -*-
"""Mise en forme des cours : gras, surlignage et soulignement, identiques sur les pages web et dans les PDF.

Dans cours.json, on peut marquer soi-même : **gras**, ==surligné==, __souligné__.
En plus, le programme met en gras la première apparition des mots du vocabulaire du cours, souligne les renvois
« article 49-3 » et surligne les chiffres clés (5 ans, 577 députés, 60 jours…)."""
import re

# mots du vocabulaire trop courants dans une phrase pour être mis en gras tout seuls
COURANTS = {"fait", "droit", "devoir", "code", "appel", "seuil", "article", "opinion", "liberté"}
CHIFFRE = r"\d[\d   ]*\d?\s?(?:ans|an|députés|sénateurs|membres|jours|mois|heures|%|euros|€|voix|sièges|tours?)(?!\w)"
ARTICLE = r"[Aa]rticle \d+(?:-\d+)?(?: de la Constitution)?"
EXPLICITE = r"\*\*(?P<b>.+?)\*\*|==(?P<m>.+?)==|__(?P<u>.+?)__"


def _forme_terme(mot):
    return re.sub(r"\s*\(.*$", "", mot).strip()


def preparer(cours):
    """Liste des mots du vocabulaire à mettre en gras une fois dans le cours."""
    out = []
    for mot, _ in cours.get("mots", []):
        t = _forme_terme(mot)
        if t and t.lower() not in COURANTS:
            out.append(t)
    return sorted(set(out), key=len, reverse=True)


class Forme:
    """Un objet par cours : retient les mots déjà mis en gras pour ne le faire qu'une fois."""

    def __init__(self, cours, echapper, gras, souligne, surligne):
        self.vus = set()
        self.esc, self.g, self.u, self.m = echapper, gras, souligne, surligne
        termes = preparer(cours)
        self.motif = re.compile("|".join(
            [EXPLICITE]
            + ([r"(?<!\w)(?P<t>" + "|".join(re.escape(t) for t in termes) + r")(?!\w)"] if termes else [])
            + [r"(?P<a>" + ARTICLE + ")", r"(?P<n>" + CHIFFRE + ")"]), re.I)

    def __call__(self, texte, auto=True):
        sortie, pos = [], 0
        for m in self.motif.finditer(texte):
            sortie.append(self.esc(texte[pos:m.start()]))
            pos = m.end()
            if m.group("b") is not None:
                sortie.append(self.g(self.esc(m.group("b"))))
            elif m.group("m") is not None:
                sortie.append(self.m(self.esc(m.group("m"))))
            elif m.group("u") is not None:
                sortie.append(self.u(self.esc(m.group("u"))))
            elif not auto:
                sortie.append(self.esc(m.group(0)))
            elif m.groupdict().get("t"):
                cle = m.group("t").lower()
                if cle in self.vus:
                    sortie.append(self.esc(m.group(0)))
                else:
                    self.vus.add(cle)
                    sortie.append(self.g(self.esc(m.group(0))))
            elif m.groupdict().get("a"):
                sortie.append(self.u(self.esc(m.group(0))))
            else:
                sortie.append(self.m(self.esc(m.group(0))))
        sortie.append(self.esc(texte[pos:]))
        return "".join(sortie)
