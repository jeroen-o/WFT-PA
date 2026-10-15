/* PA-toets in de stijl van de WFT Bieb-kennistoets. Vragen: assets/js/vragen.js, modules: assets/js/modules.js. */
(function(){
  // 7 vragen bij één module, 5 extra per module die je toevoegt: 1 → 7, 2 → 12, 3 → 17, 9 → 47
  function aantalVragen(n){ return 7 + 5 * (Math.max(1, n) - 1); }
  var MODS = window.PA_MODULES, laden = {};
  // Vragen per module laden (assets/js/vragen/<id>.js), alleen voor de gekozen modules
  function vragenVan(id){ return (window.PA_VRAGEN || {})[id]; }
  function laad(ids){
    return Promise.all(ids.filter(function(id){ return !vragenVan(id); }).map(function(id){
      return laden[id] || (laden[id] = new Promise(function(ok, nok){
        var s = document.createElement('script');
        s.src = 'assets/js/vragen/' + id + '.js?v=' + ((window.PA_VRAGEN_V || {})[id] || '');
        s.onload = ok; s.onerror = function(){ delete laden[id]; s.remove(); nok(new Error('laden mislukt')); };
        document.head.appendChild(s);
      }));
    }));
  }
  var paneel = document.getElementById('paneel');
  var keuze = ['basis'], toets = [], stap = 0, laatste = null, gehad = {}, hoofdtoets = null, oefenen = false; // keuze: id's van de gekozen modules

  function el(tag, props){
    var e = document.createElement(tag);
    if(props) Object.keys(props).forEach(function(k){
      var v = props[k];
      if(v === null || v === undefined) return;
      if(k === 'class') e.className = v;
      else if(k.indexOf('on') === 0) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v);
    });
    for(var i = 2; i < arguments.length; i++){
      [].concat(arguments[i]).forEach(function(k){ if(k !== null && k !== undefined) e.append(k); });
    }
    return e;
  }
  function vul(){ paneel.replaceChildren.apply(paneel, [].filter.call(arguments, function(k){ return k !== null && k !== undefined; })); }
  function esc(s){ return String(s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function rnd(n){ var a = new Uint32Array(1); crypto.getRandomValues(a); return a[0] % n; }
  function hussel(a){ a = a.slice(); for(var i = a.length - 1; i > 0; i--){ var j = rnd(i + 1), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function vandaag(){ var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function nu(){ var d = new Date(); return PA_DATUM(vandaag()) + ', ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0') + ' uur'; }
  function modById(id){ return MODS.filter(function(m){ return m.id === id; })[0]; }

  // Welke modules horen bij de huidige keuze (altijd in de vaste volgorde van de modules)
  function gekozenModules(){ return MODS.filter(function(m){ return keuze.indexOf(m.id) > -1; }); }
  function keuzeLabel(){
    var ms = gekozenModules();
    if(ms.length === MODS.length) return 'Alle modules';
    if(ms.length > 1) return 'Mijn pakket: ' + ms.map(function(m){ return m.naam; }).join(', ');
    return 'Wft ' + ms[0].naam;
  }
  function bijgewerktTekst(){
    var ms = gekozenModules();
    if(ms.length === 1) return 'Vragen van deze module laatst bijgewerkt op ' + PA_DATUM(ms[0].bijgewerkt) + '.';
    var oudste = ms.map(function(m){ return m.bijgewerkt; }).sort()[0];
    return ms.length + ' modules. Oudste bijwerkdatum: ' + PA_DATUM(oudste) + '.';
  }

  // Logo als data-URL, zodat het certificaat ook in een nieuw venster en bij printen het logo toont
  var LOGO = 'assets/logo/dfo-logo.png';
  (function(){ var img = new Image(); img.onload = function(){ try{ var c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight; c.getContext('2d').drawImage(img, 0, 0); LOGO = c.toDataURL('image/png'); }catch(e){} }; img.src = LOGO; })();

  function agendaBlok(){ var d = el('div', {style:'margin-top:24px'}); if(window.PA_AGENDA) window.PA_AGENDA(d); return d; }

  function startScherm(){
    var info = el('p', {class:'bijgewerkt', 'aria-live':'polite'});
    function aantalTekst(){ var n = gekozenModules().length; return n ? 'Met deze keuze: ' + n + (n === 1 ? ' module, ' : ' modules, ') + aantalVragen(n) + ' vragen.' : 'Kies minimaal één module.'; }
    var uitlegAantal = el('p', {id:'aantalTekst', class:'aantal', 'aria-live':'polite'});
    var startKnop = el('button', {class:'btn', type:'button', id:'startKnop', onclick:start}, 'Start de toets');
    var vakjes = el('div', {class:'modkeuze', role:'group', 'aria-label':'Modules'});
    function bijwerken(){
      [].forEach.call(vakjes.querySelectorAll('input'), function(i){ i.checked = keuze.indexOf(i.value) > -1; });
      var ms = gekozenModules();
      uitlegAantal.textContent = aantalTekst();
      info.textContent = ms.length ? bijgewerktTekst() : '';
      startKnop.disabled = !ms.length;
      laad(keuze).catch(function(){});
    }
    MODS.forEach(function(m){
      var i = el('input', {type:'checkbox', value:m.id, id:'mod-' + m.id});
      i.addEventListener('change', function(){ keuze = MODS.map(function(x){ return x.id; }).filter(function(id){ return id === m.id ? i.checked : keuze.indexOf(id) > -1; }); bijwerken(); });
      vakjes.append(el('label', {class:'modvak', for:'mod-' + m.id}, i, el('span', null, 'Wft ' + m.naam)));
    });
    var snel = el('p', {class:'snel'},
      el('button', {type:'button', class:'linkknop', id:'alleModules', onclick:function(){ keuze = MODS.map(function(m){ return m.id; }); bijwerken(); }}, 'Alle modules'), ' · ',
      el('button', {type:'button', class:'linkknop', onclick:function(){ keuze = []; bijwerken(); }}, 'Niets'), ' · ',
      el('a', {href:'index.html#check'}, 'Kies op beroepskwalificatie'));
    vul(el('div', {class:'start'},
      el('h2', null, 'Test je kennis'),
      el('p', null, 'Kies een of meer modules. Bij één module krijg je 7 willekeurige meerkeuzevragen, en voor elke module die je toevoegt 5 extra (2 modules: 12 vragen, 3 modules: 17). Na elk antwoord zie je bij alle vier de antwoorden waarom ze goed of fout zijn. Na afloop ontvang je een certificaat met je resultaat.'),
      vakjes, snel, uitlegAantal, info, teamBlok(),
      el('p', {class:'advies'}, 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het ook in bij je werkgever.'),
      startKnop,
      agendaBlok()
    ));
    bijwerken();
  }

  // Link naar precies deze modulekeuze, om te delen met collega's of het hele team
  function teamLink(){
    var ids = gekozenModules().map(function(m){ return m.id; });
    return 'https://pa-wft.nl/toets.html' + (ids.length === MODS.length ? '#alles' : ids.length > 1 ? '#mix=' + ids.join(',') : ids.length ? '#' + ids[0] : '');
  }
  function teamBlok(){
    var melding = el('span', {class:'klein', id:'teamStatus', 'aria-live':'polite'});
    var knop = el('button', {type:'button', class:'linkknop', id:'teamLink', onclick:function(){
      var url = teamLink();
      var klaar = function(){ melding.textContent = ' Gekopieerd: ' + url; }, zelf = function(){ melding.textContent = ' Kopieer deze link: ' + url; };
      try{ if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(klaar, zelf); else zelf(); }catch(e){ zelf(); }
    }}, 'Kopieer de link naar deze toets voor je team');
    return el('p', {class:'team'}, knop, melding);
  }

  function start(){
    var ms = gekozenModules(), knop = document.getElementById('startKnop');
    if(knop){ knop.disabled = true; knop.textContent = 'Vragen laden…'; }
    laad(ms.map(function(m){ return m.id; })).then(function(){ begin(ms); }, function(){
      alert('De vragen konden niet worden geladen. Controleer je internetverbinding en probeer het opnieuw.');
      if(knop){ knop.disabled = false; knop.textContent = 'Start de toets'; }
    });
  }

  function begin(ms){
    var totaal = aantalVragen(ms.length);
    oefenen = false;
    // Per module 5 vragen (bij één module 7); de rest gaat naar willekeurige modules, zodat elke module meedoet
    var basis = ms.length === 1 ? totaal : 5, quota = {};
    ms.forEach(function(m){ quota[m.id] = basis; });
    hussel(ms).slice(0, totaal - basis * ms.length).forEach(function(m){ quota[m.id]++; });
    var gekozen = [];
    ms.forEach(function(m){
      var bank = (vragenVan(m.id) || []).map(function(q, i){ return {q:q, module:m, sleutel:m.id + ':' + i}; });
      var nieuw = hussel(bank.filter(function(x){ return !gehad[x.sleutel]; }));
      if(nieuw.length < quota[m.id]){ bank.forEach(function(x){ delete gehad[x.sleutel]; }); nieuw = hussel(bank); }
      gekozen = gekozen.concat(nieuw.slice(0, quota[m.id]));
    });
    toets = hussel(gekozen).map(function(x){
      gehad[x.sleutel] = 1;
      return {module:x.module, vraag:x.q[0], term:x.q[2] || '', opties:hussel(x.q[1].map(function(a, k){ return {t:a[0], u:a[1], juist:k === 0}; })), keuze:null};
    });
    stap = 0;
    toonVraag();
  }

  function uitlegLijst(v){
    return el('ul', {class:'uitleglijst'}, v.opties.map(function(o, k){
      return el('li', {class:(o.juist ? 'ok' : 'nok') + (k === v.keuze ? ' gekozen' : '')},
        el('span', {class:'kop'}, (o.juist ? '✓ Goed: ' : '✗ Fout: ') + o.t + (k === v.keuze ? ' (jouw antwoord)' : '')),
        el('span', {class:'tekst'}, o.u));
    }));
  }
  // Twijfel over een vraag: vraag, antwoorden en uitleg direct naar DFO mailen
  function meldLink(v){
    var juist = v.opties.filter(function(o){ return o.juist; })[0];
    var body = 'Module: Wft ' + v.module.naam + (v.term ? '\nToetsterm CDFD: ' + v.term : '') + '\n\nVraag:\n' + v.vraag + '\n\nAntwoorden:\n'
      + v.opties.map(function(o, k){ return 'ABCD'[k] + '. ' + o.t + (o.juist ? '  [gegeven als juist]' : '') + (k === v.keuze ? '  [mijn antwoord]' : ''); }).join('\n')
      + '\n\nUitleg bij het juiste antwoord:\n' + juist.u + '\n\nMijn twijfel:\n';
    var href = 'mailto:info@dfobv.nl?subject=' + encodeURIComponent('check deze vraag op PA-WFT.nl') + '&body=' + encodeURIComponent(body);
    return el('p', {class:'meld'}, el('a', {href:href, id:'meldVraag'}, 'Twijfel je over deze vraag of het antwoord? Mail hem direct naar DFO'));
  }

  function toonVraag(){
    var v = toets[stap];
    var titel = el('h2', {id:'vraagtitel', tabindex:'-1'}, v.vraag);
    var opties = el('div', {class:'opties', role:'group', 'aria-labelledby':'vraagtitel'});
    var uitlegVak = el('div');
    var volgende = el('button', {class:'btn', type:'button', id:'volgende', disabled:''}, stap < toets.length - 1 ? 'Volgende vraag' : 'Bekijk resultaat');
    volgende.addEventListener('click', function(){ if(stap < toets.length - 1){ stap++; toonVraag(); } else if(oefenen) oefenKlaar(); else resultaat(); });
    v.opties.forEach(function(o, k){
      var b = el('button', {class:'optie', type:'button'}, el('span', {class:'l', 'aria-hidden':'true'}, 'ABCD'[k]), el('span', null, o.t));
      b.addEventListener('click', function(){
        if(v.keuze !== null) return;
        v.keuze = k;
        [].forEach.call(opties.children, function(c, ci){
          c.disabled = true;
          if(v.opties[ci].juist) c.classList.add('goed'); else if(ci === k) c.classList.add('fout');
        });
        uitlegVak.replaceChildren(el('div', {class:'uitleg ' + (o.juist ? 'ok' : 'nok'), role:'status'},
          el('strong', null, o.juist ? 'Goed!' : 'Helaas, dat is niet juist.'), uitlegLijst(v), meldLink(v)));
        volgende.disabled = false;
        volgende.focus();
      });
      opties.append(b);
    });
    var pct = Math.round(stap / toets.length * 100);
    vul(el('div', {class:'vraag'},
      el('div', {class:'voortgang'}, el('span', {id:'vraagKop'}, (oefenen ? 'Oefenronde · vraag ' : 'Vraag ') + (stap + 1) + ' van ' + toets.length), el('span', {class:'badge'}, 'Wft ' + v.module.naam + (v.term ? ' · toetsterm ' + v.term : ''))),
      el('div', {class:'balk', role:'progressbar', 'aria-label':'Voortgang', 'aria-valuemin':'0', 'aria-valuemax':'100', 'aria-valuenow':String(pct)}, el('span', {style:'width:' + pct + '%'})),
      titel, opties, uitlegVak,
      el('div', {class:'acties'}, el('button', {class:'btn ghost', type:'button', onclick:function(){ if(confirm('Toets stoppen? Je antwoorden gaan verloren.')) startScherm(); }}, 'Stoppen'), volgende)
    ));
    titel.focus();
  }

  function certificaatnummer(){
    var t = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', s = '';
    for(var i = 0; i < 6; i++) s += t[rnd(t.length)];
    return 'PA-' + new Date().getFullYear() + '-' + s;
  }

  // Oefenronde met de fout beantwoorde vragen; telt niet mee voor het certificaat
  function fouten(lijst){ return lijst.filter(function(v){ return !v.opties[v.keuze].juist; }); }
  function oefenFout(lijst){
    oefenen = true;
    toets = hussel(lijst).map(function(v){ return {module:v.module, vraag:v.vraag, term:v.term, opties:hussel(v.opties.map(function(o){ return {t:o.t, u:o.u, juist:o.juist}; })), keuze:null}; });
    stap = 0; toonVraag();
  }
  function oefenKnop(lijst, tekst){
    return el('button', {class:'btn', type:'button', id:'oefenFout', onclick:function(){ oefenFout(lijst); }}, tekst);
  }
  function oefenKlaar(){
    var nogFout = fouten(toets), goed = toets.length - nogFout.length;
    var kop = el('div', {class:'getal', id:'score', tabindex:'-1'}, goed + '/' + toets.length);
    vul(
      el('div', {class:'score'}, kop, el('p', null, nogFout.length ? 'Oefenronde klaar. Een paar vragen zijn nog lastig: lees de uitleg en oefen ze nog een keer.' : 'Oefenronde klaar: nu alles goed.'),
        el('p', {class:'klein'}, 'Een oefenronde telt niet mee voor je certificaat.')),
      el('div', {class:'acties', style:'justify-content:center'},
        nogFout.length ? oefenKnop(nogFout, 'Oefen deze ' + (nogFout.length === 1 ? 'vraag' : nogFout.length + ' vragen') + ' nog een keer') : null,
        hoofdtoets ? el('button', {class:'btn ghost', type:'button', id:'terugResultaat', onclick:function(){ oefenen = false; toets = hoofdtoets; resultaat(true); }}, 'Terug naar je resultaat en certificaat') : null,
        el('button', {class:'btn ghost', type:'button', onclick:start}, 'Nieuwe toets')));
    kop.focus();
  }

  function resultaat(terug){
    var goed = toets.filter(function(v){ return v.opties[v.keuze].juist; }).length, n = toets.length;
    var ms = gekozenModules();
    hoofdtoets = toets;
    if(!terug || !laatste) laatste = {goed:goed, n:n, pct:Math.round(goed / n * 100), thema:keuzeLabel(), datum:PA_DATUM(vandaag()), nummer:certificaatnummer(),
      bijgewerkt:PA_DATUM(ms.map(function(m){ return m.bijgewerkt; }).sort()[0]),
      modules:ms.map(function(m){ return 'Wft ' + m.naam; }),
      vanMods:MODS.map(function(m){ var n = toets.filter(function(v){ return v.module.id === m.id; }).length; return n ? m.naam + ' (' + n + ')' : null; }).filter(Boolean),
      vragen:toets.map(function(v){ var j = v.opties.filter(function(o){ return o.juist; })[0]; return {vraag:v.vraag, jouw:v.opties[v.keuze].t, juist:j.t, goed:v.opties[v.keuze].juist}; })};
    var geslaagd = goed / n >= 0.7; // geslaagd vanaf 70% goed
    var oordeel = goed === n ? 'Foutloos. Uitstekend!' : goed / n >= 0.7 ? 'Goed gedaan, ruim voldoende.' : goed / n >= 0.5 ? 'Redelijk, maar er is ruimte voor verbetering.' : 'Dat kan beter. Lees de uitleg hieronder en probeer het opnieuw.';
    var lijst = el('ol', {class:'overzicht'});
    toets.forEach(function(v){ lijst.append(el('li', {class:v.opties[v.keuze].juist ? 'ok' : 'nok'}, el('span', {class:'v'}, v.vraag), uitlegLijst(v), meldLink(v))); });
    vul(
      el('div', {class:'score' + (geslaagd ? ' geslaagd' : '')}, geslaagd ? el('p', {class:'hoera', role:'status'}, 'HOERA, gefeliciteerd!') : null, el('div', {class:'getal', id:'score', tabindex:'-1'}, goed + '/' + n), el('p', null, oordeel)),
      goed < n ? el('div', {class:'acties', style:'justify-content:center'}, oefenKnop(fouten(toets), 'Oefen je ' + (n - goed === 1 ? 'foute vraag' : (n - goed) + ' foute vragen') + ' opnieuw')) : null,
      certificaatFormulier(),
      agendaBlok(),
      el('div', {class:'acties', style:'justify-content:center'},
        el('button', {class:'btn ghost', type:'button', onclick:start}, 'Nieuwe toets, zelfde module'),
        el('button', {class:'btn ghost', type:'button', onclick:startScherm}, 'Andere module kiezen'),
        el('button', {class:'btn ghost', type:'button', id:'printAntwoorden', onclick:printAntwoorden}, 'Print beantwoorde vragen')),
      el('h3', {style:'margin-top:24px;font-size:17px'}, 'Overzicht met uitleg'),
      lijst);
    var sc = document.getElementById('score'); sc.focus({preventScroll:true}); sc.parentNode.scrollIntoView({block:'start'});
    if(geslaagd && !terug) feest();
  }

  // Confetti bij geslaagd; niet bij "beperk beweging" in de systeeminstellingen
  function feest(){
    if(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var c = document.createElement('canvas'), x = c.getContext('2d');
    if(!x) return;
    c.className = 'confetti'; c.setAttribute('aria-hidden', 'true');
    document.body.appendChild(c);
    var dpr = Math.min(window.devicePixelRatio || 1, 2), W, H;
    function maat(){ W = innerWidth; H = innerHeight; c.width = W * dpr; c.height = H * dpr; x.setTransform(dpr, 0, 0, dpr, 0, 0); }
    maat(); addEventListener('resize', maat);
    var kleuren = ['#1462ad', '#0b3d73', '#8db8e3', '#f2b705', '#e4572e', '#2a9d5c', '#ffffff'];
    var deeltjes = [], n = W < 600 ? 120 : 220;
    for(var i = 0; i < n; i++){
      var links = i % 2 === 0;
      deeltjes.push({x:links ? -10 : W + 10, y:H * (.55 + Math.random() * .35), vx:(links ? 1 : -1) * (4 + Math.random() * 9), vy:-(9 + Math.random() * 11),
        w:6 + Math.random() * 7, h:8 + Math.random() * 10, r:Math.random() * 6.28, vr:(Math.random() - .5) * .35, k:kleuren[i % kleuren.length], z:Math.random() * 6.28, rond:Math.random() < .25});
    }
    var start = performance.now(), duur = 4200;
    function stap(t){
      var oud = t - start;
      x.clearRect(0, 0, W, H);
      x.globalAlpha = oud > duur - 900 ? Math.max(0, (duur - oud) / 900) : 1;
      deeltjes.forEach(function(d){
        d.vy += .28; d.vx *= .985; d.vy *= .985; d.z += .12;
        d.x += d.vx + Math.sin(d.z) * 1.2; d.y += d.vy; d.r += d.vr;
        x.save(); x.translate(d.x, d.y); x.rotate(d.r); x.scale(1, Math.cos(d.z));
        x.fillStyle = d.k;
        if(d.rond){ x.beginPath(); x.arc(0, 0, d.w / 2, 0, 6.28); x.fill(); } else x.fillRect(-d.w / 2, -d.h / 2, d.w, d.h);
        x.restore();
      });
      if(oud < duur) requestAnimationFrame(stap); else { removeEventListener('resize', maat); c.remove(); }
    }
    requestAnimationFrame(stap);
  }

  function certificaatFormulier(){
    var naam = el('input', {type:'text', id:'certnaam', autocomplete:'name', required:'', maxlength:'80'});
    var mail = el('input', {type:'email', id:'certmail', autocomplete:'email', required:'', maxlength:'120'});
    var geb = el('input', {type:'date', id:'certgeb', autocomplete:'bday', max:vandaag(), min:'1925-01-01'});
    var bedrijf = el('input', {type:'text', id:'certbedrijf', autocomplete:'organization', maxlength:'100'});
    var werkgever = el('input', {type:'email', id:'certwerkgever', maxlength:'120'});
    function gegevens(){ return {naam:naam.value.trim(), mail:mail.value.trim(), geb:geb.value, bedrijf:bedrijf.value.trim(), werkgever:werkgever.value.trim()}; }
    function controleer(metMail){
      var g = gegevens();
      if(!g.naam){ status.textContent = 'Vul je naam in.'; naam.focus(); return null; }
      if(g.geb && (!/^\d{4}-\d{2}-\d{2}$/.test(g.geb) || g.geb > vandaag() || g.geb < '1925-01-01')){ status.textContent = 'Vul een geldige geboortedatum in, of laat het veld leeg.'; geb.focus(); return null; }
      if(metMail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(g.mail)){ status.textContent = 'Vul een geldig e-mailadres in.'; mail.focus(); return null; }
      if(g.werkgever && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(g.werkgever)){ status.textContent = 'Vul een geldig e-mailadres van je werkgever in, of laat het veld leeg.'; werkgever.focus(); return null; }
      return g;
    }
    var status = el('div', {class:'certstatus', id:'certStatus', 'aria-live':'polite'});
    var form = el('form', {class:'certform', id:'certForm', novalidate:''},
      el('h3', null, 'Ontvang je certificaat'),
      el('p', {class:'advies'}, 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het ook in bij je werkgever.'),
      el('p', null, 'Vul je gegevens in. Ze komen op het certificaat en blijven in je eigen browser: er gaat niets naar DFO en er wordt niets bewaard. Met "Mail met pdf-bijlage" maak je het certificaat als pdf en zet je het als bijlage in een mail aan jezelf.'),
      el('div', {class:'veld'}, el('label', {for:'certnaam'}, 'Naam op het certificaat'), naam),
      el('div', {class:'veld'}, el('label', {for:'certgeb'}, 'Geboortedatum (optioneel)'), geb),
      el('div', {class:'veld'}, el('label', {for:'certmail'}, 'Je e-mailadres'), mail),
      el('div', {class:'veld'}, el('label', {for:'certbedrijf'}, 'Bedrijf waar je werkt (optioneel)'), bedrijf),
      el('div', {class:'veld'}, el('label', {for:'certwerkgever'}, 'E-mailadres werkgever, voor een kopie (optioneel)'), werkgever),
      el('div', {class:'acties', style:'margin-top:12px'},
        el('button', {class:'btn', type:'submit', id:'mailPdfKnop'}, 'Mail met pdf-bijlage'),
        el('button', {class:'btn ghost', type:'button', id:'pdfKnop', onclick:function(){ status.className = 'certstatus'; var g = controleer(false); if(!g) return; g.uitgegeven = nu(); g.verstuurd = false; maakPdf(g).then(function(doc){ PA_PDF.download(doc.output('blob'), pdfNaam(), 'application/pdf'); status.className = 'certstatus klaar'; status.textContent = 'De pdf is gedownload: ' + pdfNaam() + '.'; }); }}, 'Download pdf'),
        el('button', {class:'btn ghost', type:'button', id:'printKnop', onclick:function(){ status.className = 'certstatus'; var g = controleer(false); if(!g) return; g.uitgegeven = nu(); g.verstuurd = false; printCertificaat(g); }}, 'Bekijken of printen')),
      el('p', {class:'klein', style:'margin-top:10px'}, el('a', {href:'#', id:'mailTekstLink', onclick:function(e){ e.preventDefault(); status.className = 'certstatus'; var g = controleer(true); if(!g) return; g.uitgegeven = nu(); g.verstuurd = true; var href = mailHref(g); form.setAttribute('data-mailto', href); window.location.href = href; }}, 'Of mail het certificaat als tekst, zonder bijlage')),
      status);
    form.addEventListener('submit', function(e){
      e.preventDefault(); status.className = 'certstatus';
      var g = controleer(true); if(!g) return;
      g.uitgegeven = nu(); g.verstuurd = true;
      form.setAttribute('data-mailto', mailHref(g));
      status.textContent = 'Het certificaat wordt gemaakt…';
      maakPdf(g).then(function(doc){
        var blob = doc.output('blob'), naamPdf = pdfNaam(), onderwerp = mailOnderwerp(g), tekst = certTekst(g, false);
        var bestand = null; try{ bestand = new File([blob], naamPdf, {type:'application/pdf'}); }catch(e){}
        if(bestand && navigator.canShare && navigator.canShare({files:[bestand]})){
          // Mobiel en browsers met delen: de pdf gaat als bijlage naar de gekozen mail-app
          navigator.share({files:[bestand], title:onderwerp, text:'Aan: ' + g.mail + (g.werkgever ? ' (kopie: ' + g.werkgever + ')' : '') + '\n\n' + tekst}).then(function(){
            status.className = 'certstatus klaar'; status.textContent = 'Kies je mail-app; de pdf zit als bijlage in het bericht. Vul zo nodig ' + g.mail + (g.werkgever ? ' en ' + g.werkgever : '') + ' in als ontvanger.';
          }).catch(function(){ emlDownload(doc, g, onderwerp, tekst, naamPdf); });
        } else emlDownload(doc, g, onderwerp, tekst, naamPdf);
      });
    });
    return form;
  }

  var ADVIES = 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het ook in bij je werkgever.';
  var DISCLAIMER = 'Eigen verklaring van de deelnemer. De deelnemer heeft de oefentoets van Wft Permanent Actueel (PA-WFT.nl), een activiteit van DFO BV (KvK 32068727), De Wel 14–16, 3871 MV Hoevelaken, zelf gemaakt en de gegevens zelf ingevuld. DFO BV heeft identiteit en resultaat niet gecontroleerd en registreert niets. Het certificaat is geen Wft-diploma, geen PE-examen en levert geen PE-punten op.';

  function certTekst(g, metVragen){
    var r = laatste;
    return 'Certificaat PA-toets — Wft Permanent Actueel\n\nNaam: ' + g.naam + (g.geb ? '\nGeboortedatum: ' + PA_DATUM(g.geb) : '') + '\nE-mailadres: ' + g.mail + (g.bedrijf ? '\nBedrijf: ' + g.bedrijf : '') + '\nVerstuurd op: ' + g.uitgegeven + '\nResultaat: ' + r.goed + ' van ' + r.n + ' goed (' + r.pct + '%)\nModule: ' + r.thema + (r.modules.length > 1 ? '\nModules: ' + r.modules.join(', ') + '\nVragen uit: ' + r.vanMods.join(', ') : '') + '\nDatum: ' + r.datum + '\nVragenbank bijgewerkt: ' + r.bijgewerkt + '\nCertificaatnummer: ' + r.nummer + '\n\n'
      + ADVIES + '\n\nDoe de toets opnieuw: https://pa-wft.nl/toets.html\nWft Permanent Actueel: https://pa-wft.nl/\n\n' + DISCLAIMER + '\n';
  }
  function mailOnderwerp(g){ return 'Certificaat PA-toets ' + laatste.nummer + ' — ' + g.naam + ' (' + laatste.goed + '/' + laatste.n + ')'; }
  function pdfNaam(){ return 'Certificaat-PA-toets-' + laatste.nummer + '.pdf'; }
  function maakPdf(g){ return window.PA_PDF ? PA_PDF.maak(laatste, g, LOGO, STEMPEL, ADVIES, DISCLAIMER) : Promise.reject(new Error('pdf niet geladen')); }
  function emlDownload(doc, g, onderwerp, tekst, naamPdf){
    var naamEml = 'Mail-certificaat-PA-toets-' + laatste.nummer + '.eml';
    PA_PDF.download(PA_PDF.eml(doc, g.mail, g.werkgever, onderwerp, tekst, naamPdf), naamEml, 'message/rfc822');
    var st = document.getElementById('certStatus');
    st.className = 'certstatus klaar';
    st.textContent = 'Er is een mailconcept gedownload: ' + naamEml + '. Open het bestand: Outlook en Windows Mail openen een concept aan ' + g.mail + (g.werkgever ? ' met een kopie aan ' + g.werkgever : '') + ', met de pdf al als bijlage. Klik op Verzenden. Opent jouw mailprogramma het niet als concept? Gebruik dan "Download pdf" en voeg de pdf zelf toe.';
  }
  function mailHref(g){
    var onderwerp = mailOnderwerp(g);
    var basis = 'mailto:' + encodeURIComponent(g.mail) + '?' + (g.werkgever ? 'cc=' + encodeURIComponent(g.werkgever) + '&' : '') + 'subject=' + encodeURIComponent(onderwerp) + '&body=';
    return basis + encodeURIComponent(certTekst(g, false));
  }

  var STEMPEL = '<svg class="stempel" viewBox="0 0 200 200" aria-label="Stempel DFO BV" role="img"><defs><path id="cirkel" d="M100,100 m-72,0 a72,72 0 1,1 144,0 a72,72 0 1,1 -144,0"/></defs>'
    + '<g fill="none" stroke="#0E5AA7"><circle cx="100" cy="100" r="94" stroke-width="5"/><circle cx="100" cy="100" r="84" stroke-width="1.5"/><circle cx="100" cy="100" r="52" stroke-width="1.5"/></g>'
    + '<text font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#0E5AA7" letter-spacing="1.6"><textPath href="#cirkel" startOffset="0" textLength="440" lengthAdjust="spacing">DFO BV • HOEVELAKEN • PERMANENT ACTUEEL •</textPath></text>'
    + '<text x="100" y="98" text-anchor="middle" font-family="Arial,sans-serif" font-size="30" font-weight="700" fill="#0E5AA7">DFO</text>'
    + '<text x="100" y="118" text-anchor="middle" font-family="Arial,sans-serif" font-size="10.5" font-weight="700" fill="#0E5AA7" letter-spacing="1.5">PA-WFT</text></svg>';

  function certificaatHTML(g){
    var r = laatste;
    var css = 'body{margin:0;font-family:"Segoe UI",Arial,sans-serif;color:#2C3A47;background:#fff}'
      + '.cert{max-width:900px;margin:0 auto;padding:28px}'
      + '.kader{border:3px solid #0E5AA7;outline:1px solid #0E5AA7;outline-offset:-10px;padding:40px 44px;position:relative}'
      + '.kop{display:flex;justify-content:space-between;align-items:center;gap:20px}.kop img{height:50px}'
      + '.kop .nr{font-size:12px;color:#4A4A4A;text-align:right}'
      + 'h1{font-size:34px;color:#0E5AA7;margin:34px 0 4px;font-weight:700;letter-spacing:.02em}'
      + '.sub{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#4A4A4A;margin:0 0 28px}'
      + '.pers.mods{margin:-8px 0 0}.pers.mods dd{font-weight:500}'
      + '.pers{display:grid;grid-template-columns:max-content 1fr;gap:2px 14px;font-size:13px;margin:-8px 0 18px}.pers dt{color:#4A4A4A}.pers dd{margin:0;font-weight:600}'
      + '.naam{font-size:30px;font-weight:700;border-bottom:2px solid #BBD3EA;padding-bottom:6px;margin:6px 0 18px;display:inline-block;min-width:60%}'
      + '.res{display:flex;gap:16px;flex-wrap:wrap;margin:8px 0 24px}.res div{background:#EDF3FA;border-radius:4px;padding:10px 16px;font-size:13px}.res strong{display:block;font-size:22px;color:#0E5AA7}'
      + '.voet{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-top:40px}.voet p{font-size:11px;color:#4A4A4A;max-width:60ch;margin:0}'
      + '.advies{margin:28px 0 0;background:#EDF3FA;border-left:4px solid #0E5AA7;padding:10px 14px;font-size:13px}'
      + '.stempel{width:140px;height:140px;transform:rotate(-12deg);opacity:.88;flex:0 0 auto}'
      + '@media (max-width:600px){.cert{padding:12px}.kader{padding:24px 18px}.voet{flex-direction:column;align-items:flex-start}}'
      + '@media print{.cert{padding:0}@page{size:A4;margin:12mm}.res div{-webkit-print-color-adjust:exact;print-color-adjust:exact}}';
    var body = '<div class="cert"><div class="kader">'
      + '<div class="kop"><img src="' + LOGO + '" alt="DFO — dienstverlening voor financiële ondernemers"><div class="nr">Certificaatnummer<br><strong>' + r.nummer + '</strong><br>' + r.datum + '<br><a href="https://pa-wft.nl/" style="color:#0E5AA7;font-weight:700;text-decoration:none">PA-WFT.nl</a></div></div>'
      + '<h1>Certificaat</h1><p class="sub">PA-toets · Wft Permanent Actueel</p>'
      + '<div>Eigen verklaring van</div><div class="naam">' + esc(g.naam) + '</div>'
      + '<dl class="pers">' + (g.geb ? '<dt>Geboortedatum</dt><dd>' + esc(PA_DATUM(g.geb)) + '</dd>' : '') + (g.mail ? '<dt>E-mailadres</dt><dd>' + esc(g.mail) + '</dd>' : '') + (g.bedrijf ? '<dt>Bedrijf</dt><dd>' + esc(g.bedrijf) + '</dd>' : '')
      + '<dt>' + (g.verstuurd ? 'Verstuurd op' : 'Aangemaakt op') + '</dt><dd>' + esc(g.uitgegeven) + '</dd></dl>'
      + '<div>de PA-toets heeft afgelegd met het volgende resultaat:</div>'
      + '<div class="res"><div><strong>' + r.goed + ' / ' + r.n + '</strong>vragen goed</div><div><strong>' + r.pct + '%</strong>score</div><div><strong>' + esc(r.modules.length > 1 && r.thema.indexOf('Mijn pakket') === 0 ? 'Mijn pakket' : r.thema) + '</strong>' + (r.modules.length > 1 ? 'modules' : 'module') + '</div><div><strong>' + esc(r.bijgewerkt) + '</strong>vragenbank bijgewerkt</div></div>'
      + (r.modules.length > 1 ? '<dl class="pers mods"><dt>Modules</dt><dd>' + esc(r.modules.join(', ')) + '</dd><dt>Vragen uit</dt><dd>' + esc(r.vanMods.join(', ')) + '</dd></dl>' : '')
      + '<p class="advies">' + ADVIES + ' Doe de toets opnieuw op <a href="https://pa-wft.nl/toets.html">pa-wft.nl/toets.html</a>.</p>'
      + '<div class="voet"><p>' + DISCLAIMER + '<br><a href="https://pa-wft.nl/" style="color:#0E5AA7;font-weight:700">PA-WFT.nl — https://pa-wft.nl/</a></p>' + STEMPEL + '</div>'
      + '</div></div>';
    return '<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Certificaat PA-toets — ' + esc(g.naam) + '</title><style>' + css + '</style></head><body>' + body
      + '<script>window.onload=function(){setTimeout(function(){window.focus();window.print();},300);}<\/script></body></html>';
  }

  // Overzicht van alle beantwoorde vragen met uitleg, om te printen of als pdf op te slaan
  function printAntwoorden(){
    var r = laatste, w = window.open('', '_blank');
    if(!w){ alert('Pop-up geblokkeerd. Sta pop-ups toe om de antwoorden te printen.'); return; }
    var items = toets.map(function(v, i){
      var ok = v.opties[v.keuze].juist;
      return '<li class="' + (ok ? 'ok' : 'nok') + '"><p class="kop"><span>Vraag ' + (i + 1) + ' · Wft ' + esc(v.module.naam) + (v.term ? ' · toetsterm CDFD ' + esc(v.term) : '') + '</span><strong>' + (ok ? '✓ Goed' : '✗ Fout') + '</strong></p><p class="v">' + esc(v.vraag) + '</p><ul>'
        + v.opties.map(function(o, k){ return '<li class="' + (o.juist ? 'j' : 'f') + (k === v.keuze ? ' g' : '') + '"><b>' + 'ABCD'[k] + '. ' + esc(o.t) + (o.juist ? ' — juist antwoord' : '') + (k === v.keuze ? ' — jouw antwoord' : '') + '</b><br>' + esc(o.u) + '</li>'; }).join('') + '</ul></li>';
    }).join('');
    var css = 'body{font-family:"Segoe UI",Arial,sans-serif;color:#2C3A47;margin:24px;font-size:12.5px;line-height:1.45}h1{font-size:22px;color:#0E5AA7;margin:0 0 4px}.meta{color:#4A4A4A;margin:0 0 18px}'
      + 'ol{list-style:none;padding:0;margin:0}ol>li{border:1px solid #BBD3EA;border-left:5px solid #1B6B3A;padding:10px 14px;margin:0 0 12px;page-break-inside:avoid}ol>li.nok{border-left-color:#A52A21}'
      + '.kop{display:flex;justify-content:space-between;margin:0;font-size:11px;color:#4A4A4A}.kop strong{color:#1B6B3A}li.nok .kop strong{color:#A52A21}.v{font-weight:700;font-size:13.5px;margin:4px 0 8px}'
      + 'ul{margin:0;padding:0;list-style:none}ul li{padding:4px 0 4px 10px;border-left:3px solid #E3C7C4;margin:0 0 4px}ul li.j{border-left-color:#1B6B3A}ul li.g{background:#F4F7FB}a{color:#0E5AA7}'
      + '@media print{body{margin:0}@page{size:A4;margin:14mm}}';
    w.document.open();
    w.document.write('<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Beantwoorde vragen PA-toets ' + r.nummer + '</title><style>' + css + '</style></head><body>'
      + '<h1>Beantwoorde vragen — PA-toets</h1><p class="meta">' + esc(r.thema) + ' · ' + r.goed + ' van ' + r.n + ' goed (' + r.pct + '%) · ' + r.datum + ' · certificaatnummer ' + r.nummer + ' · <a href="https://pa-wft.nl/">PA-WFT.nl</a></p>'
      + '<ol>' + items + '</ol><p class="meta">Wft Permanent Actueel is een activiteit van DFO BV. Oefentoets, geen PE-examen. Doe de toets opnieuw op https://pa-wft.nl/toets.html</p>'
      + '<script>window.onload=function(){setTimeout(function(){window.focus();window.print();},300);}<\/script></body></html>');
    w.document.close();
  }

  // Printen via een nieuw venster: window.print() wordt in een iframe (bijvoorbeeld Google Sites) geblokkeerd
  function printCertificaat(g){
    var w = window.open('', '_blank');
    if(!w){ alert('Pop-up geblokkeerd. Sta pop-ups toe om het certificaat te openen.'); return; }
    w.document.open(); w.document.write(certificaatHTML(g)); w.document.close();
  }

  // Voorkeuze via de link: toets.html#hypothecair-krediet of toets.html#mix=basis,pensioen
  // Oefenronde met alle vragen van één toetsterm (telt niet mee voor het certificaat)
  function oefenTerm(mid, term){
    var m = modById(mid);
    if(!m) return false;
    vul(el('p', {class:'laden'}, 'Vragen laden…'));
    laad([mid]).then(function(){
      var lijst = (vragenVan(mid) || []).filter(function(q){ return q[2] === term; });
      if(!lijst.length){ keuze = [mid]; startScherm(); return; }
      keuze = [mid];
      oefenen = true; hoofdtoets = null;
      toets = hussel(lijst).map(function(q){ return {module:m, vraag:q[0], term:q[2], opties:hussel(q[1].map(function(a, k){ return {t:a[0], u:a[1], juist:k === 0}; })), keuze:null}; });
      stap = 0; toonVraag();
    }, function(){ startScherm(); });
    return true;
  }

  function leesHash(){
    var h = decodeURIComponent(location.hash.slice(1));
    var tm = /^term=([a-z-]+):([0-9]+[a-z]\.[0-9]+)$/.exec(h);
    if(tm && oefenTerm(tm[1], tm[2])) return;
    var ids = (h.indexOf('mix=') === 0 ? h.slice(4).split(',') : [h]).filter(modById);
    if(h === 'alles') ids = MODS.map(function(m){ return m.id; });
    if(ids.length) keuze = MODS.map(function(m){ return m.id; }).filter(function(id){ return ids.indexOf(id) > -1; });
    startScherm();
  }
  window.addEventListener('hashchange', leesHash);
  leesHash();
})();
