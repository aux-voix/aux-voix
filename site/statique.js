document.addEventListener("click",function(e){var b=e.target.closest("[data-copie]");if(!b)return;var t=document.getElementById(b.getAttribute("data-copie")).textContent;
function ok(){var x=b.textContent;b.textContent="Copié";setTimeout(function(){b.textContent=x;},1500);}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok);}else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy");ok();}catch(_){}a.remove();}});
/* Visites comptées par GoatCounter, sans cookie ni script tiers (voir app.js) : seulement si le site l'active, sur sa propre adresse */
(function(){var m=document.querySelector('meta[name="av-mesure"]'),c=document.querySelector('link[rel="canonical"]');if(!m||!c)return;
var r=false;try{r=localStorage.getItem("skipgc")==="t";}catch(_){}if(r||navigator.globalPrivacyControl===true||navigator.doNotTrack==="1"||navigator.webdriver)return;
var h=function(x){return x.replace(/^www\./,"");};if(location.protocol!=="https:"||h(location.hostname)!==h(new URL(c.href).hostname))return;
var q={p:location.pathname,t:document.title,r:document.referrer,s:screen.width,rnd:Math.random().toString(36).slice(2,7)},u=m.content+"?";
for(var k in q)if(q[k]!=="")u+=k+"="+encodeURIComponent(q[k])+"&";
var go=function(){try{if(navigator.sendBeacon&&navigator.sendBeacon(u))return;}catch(_){}new Image().src=u;};
if(window.requestIdleCallback)requestIdleCallback(go,{timeout:4000});else setTimeout(go,1500);})();