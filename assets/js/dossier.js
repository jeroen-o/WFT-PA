/* Vakbekwaamheidsdossier: een invulformulier voor het vastleggen van vakbekwaamheid per medewerker.
   Alles gebeurt in de browser; er wordt niets opgeslagen of verzonden. Afdrukken via een nieuw venster (werkt ook in een iframe). */
(function(){
  var vorm = document.getElementById('dossierForm');
  if(!vorm) return;
  var KWAL = ['Adviseur Hypothecair krediet', 'Adviseur Vermogen', 'Adviseur Pensioen', 'Adviseur Consumptief krediet', 'Adviseur Schadeverzekering zakelijk', 'Adviseur Schadeverzekering particulier', 'Adviseur Inkomen', 'Adviseur Zorgverzekering'];
  var SOORTEN = ['Training of cursus', 'Zelfstudie', 'PA-toets (oefentoets)', 'Teamoverleg of casusbespreking', 'Nieuwsbrief of vakpublicatie', 'Overig'];

  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function el(tag, attr, inhoud){
    var e = document.createElement(tag);
    Object.keys(attr || {}).forEach(function(k){ e.setAttribute(k, attr[k]); });
    if(inhoud != null) e.append(typeof inhoud === 'string' ? document.createTextNode(inhoud) : inhoud);
    return e;
  }
  function datumNl(iso){
    if(!/^\d{4}-\d{2}-\d{2}$/.test(iso || '')) return iso || '';
    var m = ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'], d = iso.split('-');
    return parseInt(d[2], 10) + ' ' + m[parseInt(d[1], 10) - 1] + ' ' + d[0];
  }

  // Dynamische rijen
  function rijTabel(id, kolommen, maakRij){
    var tabel = document.getElementById(id), body = tabel.querySelector('tbody');
    function voegToe(){ body.append(maakRij(function(tr){ tr.remove(); })); }
    voegToe();
    document.querySelector('[data-voegtoe="' + id + '"]').addEventListener('click', function(){ voegToe(); body.lastChild.querySelector('input,select').focus(); });
    return body;
  }
  function cel(label, veld){ var td = el('td', {'data-label': label}); td.append(veld); return td; }
  function verwijderKnop(klaar){ var b = el('button', {type:'button', 'class':'linkknop', 'aria-label':'Verwijder deze rij'}, 'Verwijder'); b.addEventListener('click', klaar); return b; }
  function invoer(type, naam, label){ return el('input', {type:type, 'data-veld':naam, 'aria-label':label}); }
  function keuze(naam, label, opties){ var s = el('select', {'data-veld':naam, 'aria-label':label}); s.append(el('option', {value:''}, '— kies —')); opties.forEach(function(o){ s.append(el('option', {value:o}, o)); }); return s; }

  var kwalLijst = document.getElementById('kwalLijst');
  KWAL.forEach(function(k, i){
    var id = 'kwal' + i, l = el('label', {'for':id, 'class':'vink'}), c = el('input', {type:'checkbox', id:id, value:k});
    l.append(c, document.createTextNode(' ' + k)); kwalLijst.append(l);
  });

  var peBody = rijTabel('peTabel', 3, function(weg){
    var tr = el('tr');
    tr.append(cel('Beroepskwalificatie', keuze('kwal', 'Beroepskwalificatie', KWAL)), cel('PE-examen behaald op', invoer('date', 'datum', 'Datum PE-examen')), cel('PE-periode tot en met', invoer('date', 'tot', 'Einde PE-periode')), cel('', verwijderKnop(weg)));
    return tr;
  });
  var trBody = rijTabel('actTabel', 4, function(weg){
    var tr = el('tr');
    tr.append(cel('Datum', invoer('date', 'datum', 'Datum')), cel('Soort', keuze('soort', 'Soort activiteit', SOORTEN)), cel('Onderwerp', invoer('text', 'onderwerp', 'Onderwerp')), cel('Uren', (function(){ var i = invoer('text', 'uren', 'Aantal uren'); i.setAttribute('inputmode', 'decimal'); return i; })()), cel('', verwijderKnop(weg)));
    return tr;
  });

  function rijen(body){
    return [].map.call(body.querySelectorAll('tr'), function(tr){
      var r = {}; [].forEach.call(tr.querySelectorAll('[data-veld]'), function(v){ r[v.getAttribute('data-veld')] = v.value.trim(); });
      return r;
    }).filter(function(r){ return Object.keys(r).some(function(k){ return r[k]; }); });
  }
  function waarde(id){ return (document.getElementById(id).value || '').trim(); }

  function dossierHTML(){
    var kw = [].filter.call(kwalLijst.querySelectorAll('input'), function(c){ return c.checked; }).map(function(c){ return c.value; });
    var pe = rijen(peBody), act = rijen(trBody);
    var css = 'body{font-family:"Segoe UI",Arial,sans-serif;color:#2C3A47;margin:24px;font-size:12.5px;line-height:1.45}h1{font-size:22px;color:#0E5AA7;margin:0 0 4px}h2{font-size:14px;color:#0E5AA7;border-bottom:2px solid #BBD3EA;padding-bottom:3px;margin:20px 0 8px}'
      + '.meta{color:#4A4A4A;margin:0 0 14px}dl{display:grid;grid-template-columns:max-content 1fr;gap:3px 14px;margin:0}dt{color:#4A4A4A}dd{margin:0;font-weight:600}'
      + 'table{border-collapse:collapse;width:100%}th,td{border:1px solid #BBD3EA;padding:5px 8px;text-align:left;vertical-align:top}th{background:#EDF3FA}.leeg{color:#777;font-style:italic}.hand{margin-top:34px;display:flex;gap:40px}.hand div{flex:1;border-top:1px solid #2C3A47;padding-top:4px;color:#4A4A4A}'
      + '@media print{body{margin:0}@page{size:A4;margin:14mm}}';
    function tab(kop, koppen, regels, leeg){
      if(!regels.length) return '<p class="leeg">' + esc(leeg) + '</p>';
      return '<table><thead><tr>' + koppen.map(function(k){ return '<th>' + esc(k) + '</th>'; }).join('') + '</tr></thead><tbody>' + regels.join('') + '</tbody></table>';
    }
    var uren = act.reduce(function(s, r){ return s + (parseFloat(String(r.uren).replace(',', '.')) || 0); }, 0);
    return '<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Vakbekwaamheidsdossier ' + esc(waarde('dNaam')) + '</title><style>' + css + '</style></head><body>'
      + '<h1>Vakbekwaamheidsdossier</h1><p class="meta">Aangemaakt op ' + esc(datumNl(new Date().toISOString().slice(0, 10))) + ' met het hulpmiddel van PA-WFT.nl (Wft Permanent Actueel, een activiteit van DFO BV). Dit is een eigen vastlegging; het vervangt geen diploma of PE-examen.</p>'
      + '<h2>Medewerker</h2><dl><dt>Naam</dt><dd>' + esc(waarde('dNaam')) + '</dd><dt>Functie</dt><dd>' + esc(waarde('dFunctie')) + '</dd><dt>Onderneming</dt><dd>' + esc(waarde('dOnderneming')) + '</dd><dt>Verslagperiode</dt><dd>' + esc(waarde('dPeriode')) + '</dd></dl>'
      + '<h2>Beroepskwalificaties</h2>' + (kw.length ? '<ul>' + kw.map(function(k){ return '<li>' + esc(k) + '</li>'; }).join('') + '</ul>' : '<p class="leeg">Geen ingevuld (bijvoorbeeld bij een medewerker zonder diplomaplicht).</p>')
      + '<h2>PE-examens</h2>' + tab('', ['Beroepskwalificatie', 'PE-examen behaald op', 'PE-periode tot en met'], pe.map(function(r){ return '<tr><td>' + esc(r.kwal) + '</td><td>' + esc(datumNl(r.datum)) + '</td><td>' + esc(datumNl(r.tot)) + '</td></tr>'; }), 'Nog geen PE-examens vastgelegd.')
      + '<h2>Kennisactiviteiten</h2>' + tab('', ['Datum', 'Soort', 'Onderwerp', 'Uren'], act.map(function(r){ return '<tr><td>' + esc(datumNl(r.datum)) + '</td><td>' + esc(r.soort) + '</td><td>' + esc(r.onderwerp) + '</td><td>' + esc(r.uren) + '</td></tr>'; }), 'Nog geen activiteiten vastgelegd.')
      + (act.length && uren ? '<p>Totaal vastgelegd: ' + esc(String(uren).replace('.', ',')) + ' uur.</p>' : '')
      + '<h2>Toepassing in de praktijk</h2><p>' + (esc(waarde('dPraktijk')).replace(/\n/g, '<br>') || '<span class="leeg">Niet ingevuld.</span>') + '</p>'
      + '<h2>Evaluatie</h2><dl><dt>Datum evaluatie</dt><dd>' + esc(datumNl(waarde('dEvalDatum'))) + '</dd><dt>Evaluatie door</dt><dd>' + esc(waarde('dEvalDoor')) + '</dd></dl><p>' + (esc(waarde('dEvaluatie')).replace(/\n/g, '<br>') || '<span class="leeg">Niet ingevuld.</span>') + '</p>'
      + '<div class="hand"><div>Handtekening medewerker</div><div>Handtekening leidinggevende of compliance</div></div>'
      + '<script>window.onload=function(){setTimeout(function(){window.focus();window.print();},300);}<\/script></body></html>';
  }

  var status = document.getElementById('dossierStatus');
  function melding(t){ status.textContent = t; }
  function print(){
    if(!waarde('dNaam')){ melding('Vul minimaal de naam van de medewerker in.'); document.getElementById('dNaam').focus(); return; }
    var w = window.open('', '_blank');
    if(!w){ melding('Pop-up geblokkeerd. Sta pop-ups toe om het dossier te printen.'); return; }
    w.document.open(); w.document.write(dossierHTML()); w.document.close(); melding('Het dossier is geopend om te printen of als pdf te bewaren.');
  }
  function download(){
    if(!waarde('dNaam')){ melding('Vul minimaal de naam van de medewerker in.'); document.getElementById('dNaam').focus(); return; }
    var html = dossierHTML().replace(/<script>[\s\S]*?<\/script>/, '');
    var a = el('a', {href: URL.createObjectURL(new Blob([html], {type:'text/html'})), download: 'vakbekwaamheidsdossier-' + waarde('dNaam').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '.html'});
    document.body.append(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    melding('Het dossier is gedownload als html-bestand. Bewaar het in je personeelsdossier.');
  }
  document.getElementById('dossierPrint').addEventListener('click', print);
  document.getElementById('dossierDownload').addEventListener('click', download);
  document.getElementById('dossierWis').addEventListener('click', function(){ if(confirm('Alles wissen? De ingevulde gegevens gaan verloren.')){ vorm.reset(); [peBody, trBody].forEach(function(b){ while(b.children.length > 1) b.lastChild.remove(); }); melding('Alles is gewist.'); } });
  vorm.addEventListener('submit', function(e){ e.preventDefault(); print(); });

  // Checklist: afdrukken
  var cp = document.getElementById('checklistPrint');
  if(cp) cp.addEventListener('click', function(){
    var w = window.open('', '_blank'); if(!w){ alert('Pop-up geblokkeerd. Sta pop-ups toe om de checklist te printen.'); return; }
    var items = [].map.call(document.querySelectorAll('#checklist label'), function(l){ return '<li><span class="v">' + (l.querySelector('input').checked ? '&#9745;' : '&#9744;') + '</span> ' + esc(l.textContent.trim()) + '</li>'; }).join('');
    w.document.open(); w.document.write('<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Checklist permanent actueel</title><style>body{font-family:"Segoe UI",Arial,sans-serif;color:#2C3A47;margin:24px;font-size:13px;line-height:1.6}h1{font-size:20px;color:#0E5AA7}ul{list-style:none;padding:0}li{margin:0 0 6px}.v{font-size:16px}@media print{body{margin:0}@page{size:A4;margin:14mm}}</style></head><body><h1>Checklist permanent actueel</h1><ul>' + items + '</ul><p>Bron: PA-WFT.nl (Wft Permanent Actueel, een activiteit van DFO BV). Algemene informatie, geen advies.</p><script>window.onload=function(){setTimeout(function(){window.focus();window.print();},300);}<\/script></body></html>');
    w.document.close();
  });
})();
