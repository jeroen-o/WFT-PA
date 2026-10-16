/* Zoeken op PA-WFT.nl: doorzoekt de zoekindex (assets/js/zoekindex.js) in de browser. Geen server, geen database. */
(function(){
  var INDEX = window.PA_ZOEK || [];
  var veld = document.getElementById('zoekterm'), lijst = document.getElementById('zoekresultaten'), status = document.getElementById('zoekstatus');
  if(!veld || !lijst) return;

  function norm(t){ return String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  // Genormaliseerde velden één keer voorbereiden
  var DATA = INDEX.map(function(d){ return {d:d, p:norm(d.p), h:norm(d.h), x:norm(d.x)}; });

  function termen(q){ return norm(q).replace(/[^a-z0-9€.,'\- ]+/g, ' ').split(/\s+/).filter(function(t){ return t.length > 1 || /\d/.test(t); }).slice(0, 8); }
  function telt(tekst, t){ var n = 0, i = tekst.indexOf(t); while(i > -1 && n < 20){ n++; i = tekst.indexOf(t, i + t.length); } return n; }

  function zoek(q){
    var ts = termen(q);
    if(!ts.length) return [];
    var zin = norm(q).trim();
    return DATA.map(function(r){
      var score = 0;
      for(var i = 0; i < ts.length; i++){
        var t = ts[i], a = telt(r.p, t), b = telt(r.h, t), c = telt(r.x, t);
        if(!a && !b && !c) return null; // alle zoekwoorden moeten voorkomen
        score += a * 6 + b * 4 + Math.min(c, 8);
      }
      if(ts.length > 1 && (r.h + ' ' + r.x).indexOf(zin) > -1) score += 10; // hele zoekterm als zinsdeel
      return {r:r, score:score};
    }).filter(Boolean).sort(function(a, b){ return b.score - a.score; }).slice(0, 30);
  }

  // Fragment rond de eerste treffer, met <mark> rond de zoekwoorden (via DOM-nodes, dus veilig)
  function fragment(tekst, ts){
    var n = norm(tekst), pos = -1;
    ts.forEach(function(t){ var i = n.indexOf(t); if(i > -1 && (pos < 0 || i < pos)) pos = i; });
    var start = Math.max(0, pos - 80), eind = Math.min(tekst.length, start + 240);
    if(start > 0){ var sp = tekst.indexOf(' ', start); if(sp > -1 && sp < pos) start = sp + 1; }
    var stuk = tekst.slice(start, eind), nstuk = n.slice(start, eind);
    var p = document.createElement('p'); p.className = 'fragment';
    if(start > 0) p.append('… ');
    var i = 0;
    while(i < stuk.length){
      var best = -1, len = 0;
      ts.forEach(function(t){ var j = nstuk.indexOf(t, i); if(j > -1 && (best < 0 || j < best)){ best = j; len = t.length; } });
      if(best < 0){ p.append(stuk.slice(i)); break; }
      p.append(stuk.slice(i, best));
      var m = document.createElement('mark'); m.textContent = stuk.slice(best, best + len); p.append(m);
      i = best + len;
    }
    if(eind < tekst.length) p.append(' …');
    return p;
  }

  function toon(q, bijwerkenUrl){
    var ts = termen(q), res = zoek(q);
    lijst.replaceChildren();
    if(bijwerkenUrl){ try{ history.replaceState(null, '', q ? 'zoeken.html?q=' + encodeURIComponent(q) : 'zoeken.html'); }catch(e){} }
    if(!q.trim()){ status.textContent = ''; return; }
    if(!ts.length){ status.textContent = 'Typ minimaal twee letters.'; return; }
    status.textContent = res.length ? res.length + (res.length === 30 ? '+ resultaten' : res.length === 1 ? ' resultaat' : ' resultaten') + ' voor "' + q.trim() + '".' : 'Geen resultaten voor "' + q.trim() + '". Probeer een ander of korter zoekwoord.';
    res.forEach(function(o){
      var d = o.r.d, li = document.createElement('li'), a = document.createElement('a');
      a.href = d.u || 'index.html';
      a.textContent = d.h ? d.h : d.p;
      var waar = document.createElement('span'); waar.className = 'waar'; waar.textContent = d.h ? d.p : 'Pagina';
      var h = document.createElement('h3'); h.append(a);
      li.append(waar, h, fragment(d.x, ts));
      lijst.append(li);
    });
  }

  var q = new URLSearchParams(location.search).get('q') || '';
  veld.value = q;
  toon(q, false);
  var wacht;
  veld.addEventListener('input', function(){ clearTimeout(wacht); wacht = setTimeout(function(){ toon(veld.value, true); }, 150); });
  veld.form.addEventListener('submit', function(e){ e.preventDefault(); toon(veld.value, true); });
  if(!q) veld.focus();
})();
