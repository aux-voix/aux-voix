# -*- coding: utf-8 -*-
"""Page « Donner mon avis » (/avis/) : formulaire Google Forms chargé seulement au clic, plus un lien de secours.
Le lien du formulaire se règle dans site/contenu/site.json : "avis": {"form_url": "GOOGLE_FORM_URL"}."""
import json, os, re
from html import escape as ESC

MOTIF = re.compile(r"^https://docs\.google\.com/forms/d/e/([A-Za-z0-9_-]+)/viewform(?:[?#].*)?$")


def lien_form(valeur):
    """(lien à ouvrir, lien d'intégration), ou (None, None) tant que GOOGLE_FORM_URL n'est pas remplacé."""
    m = MOTIF.match((valeur or "").strip())
    if not m:
        return None, None
    i = m.group(1)
    return f"https://docs.google.com/forms/d/e/{i}/viewform", f"https://docs.google.com/forms/d/e/{i}/viewform?embedded=true"


def pages_avis(g):
    cfg = json.load(open(os.path.join(g.site, "contenu", "site.json"), encoding="utf-8"))
    contact = (cfg.get("mentions") or {}).get("contact") or "contact@auxvoix.fr"
    delai = int((cfg.get("signalement") or {}).get("delai_jours") or 7)
    ouvrir, integrer = lien_form((cfg.get("avis") or {}).get("form_url"))
    if ouvrir:
        formulaire = f"""<div class="avis-act">
<button type="button" class="cta" id="avis-bouton" aria-expanded="false" aria-controls="avis-cadre">Afficher le formulaire sur cette page</button>
<a class="cta s" href="{ESC(ouvrir)}" target="_blank" rel="noopener noreferrer">Ouvrir le formulaire dans un nouvel onglet<span class="sr"> (s'ouvre dans un nouvel onglet, sur Google Forms)</span></a>
</div>
<p class="meta">Tant que tu n'affiches pas le formulaire, rien n'est chargé depuis Google. Si l'affichage ne fonctionne pas, utilise le lien « Ouvrir le formulaire dans un nouvel onglet ».</p>
<div id="avis-cadre" hidden>
<iframe id="avis-iframe" title="Formulaire « Donner mon avis » (Google Forms)" data-src="{ESC(integrer)}" width="100%" height="760" loading="lazy"></iframe>
</div>
<noscript><p class="encart">JavaScript est désactivé : utilise le lien « Ouvrir le formulaire dans un nouvel onglet ».</p></noscript>
<script>
(function(){{var b=document.getElementById("avis-bouton"),c=document.getElementById("avis-cadre"),f=document.getElementById("avis-iframe");
if(!b||!c||!f)return;
b.addEventListener("click",function(){{var ouvert=!c.hidden;
if(ouvert){{c.hidden=true;b.setAttribute("aria-expanded","false");b.textContent="Afficher le formulaire sur cette page";return;}}
if(!f.src)f.src=f.getAttribute("data-src");
c.hidden=false;b.setAttribute("aria-expanded","true");b.textContent="Masquer le formulaire";}});}})();
</script>"""
    else:
        formulaire = """<p class="encart att"><strong>Formulaire pas encore branché.</strong> Remplacer <code>GOOGLE_FORM_URL</code> par le lien du formulaire Google dans <code>site/contenu/site.json</code> (clé <code>avis</code>, <code>form_url</code>).</p>"""
    corps = f"""<h1>Donner mon avis</h1>
<p class="lede">Aux Voix est en version bêta : le site n'est pas encore ouvert à tout le monde. Ton avis nous aide à l'améliorer, et le formulaire est anonyme.</p>
<h2 id="form">Le formulaire</h2>
<p>Il y a 5 questions, la plupart facultatives. Tu peux répondre en 2 minutes.</p>
<ol class="q"><li>Clarté du site, de 1 à 5.</li><li>Ce qui t'a manqué ou paru confus.</li><li>Ton profil : lycéen, étudiant, actif, enseignant ou autre (facultatif).</li><li>Un contenu qui t'a paru orienté, et lequel.</li><li>Ton e-mail, seulement si tu veux une réponse (facultatif).</li></ol>
{formulaire}
<h2 id="reponse">Notre réponse</h2>
<p>Si tu laisses ton e-mail, nous te répondons sous {delai} jours, comme pour le signalement d'une erreur. Pour une erreur précise sur une page, utilise plutôt <a href="/#/signaler">Signaler une erreur</a> : elle est corrigée et notée dans le <a href="/#/methode/corrections">journal des corrections</a>.</p>
<h2 id="donnees">Tes données</h2>
<div class="encart" role="note" aria-labelledby="donnees">
<ul>
<li><strong>Collectées :</strong> tes réponses, et ton e-mail seulement si tu le donnes. Le formulaire ne demande ni nom, ni connexion à un compte Google.</li>
<li><strong>Pourquoi :</strong> améliorer le site avant son ouverture. Rien n'est revendu, aucune publicité.</li>
<li><strong>Combien de temps :</strong> 6 mois au maximum, puis suppression.</li>
<li><strong>Où :</strong> le formulaire est fourni par Google Forms. Google traite les réponses et peut le faire en dehors de l'Union européenne. Quand tu affiches ou ouvres le formulaire, Google peut aussi déposer des cookies.</li>
<li><strong>Tes droits :</strong> accéder à tes réponses, les corriger ou les faire supprimer en écrivant à <a href="mailto:{ESC(contact)}">{ESC(contact)}</a>. Tu peux aussi saisir la <a href="https://www.cnil.fr/" rel="noopener">CNIL</a>.</li>
</ul></div>"""
    titre = "Donner mon avis sur Aux Voix : formulaire anonyme"
    desc = "Aux Voix est en version bêta. Dis-nous ce qui est clair, confus ou orienté grâce à un court formulaire anonyme. Réponse sous 7 jours si tu laisses ton e-mail."
    g.page("/avis/", titre, desc, corps, jsonld=[{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Donner mon avis", "item": g.url + "/avis/"}]}])
    g.urls.setdefault("fonds", []).append(("/avis/", g.aujourdhui))
