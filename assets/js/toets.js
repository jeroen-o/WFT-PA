/* PA-toets in de stijl van de WFT Bieb-kennistoets. Vragen: assets/js/vragen/<id>.js (nl) of assets/js/vragen-en/<id>.js (en), modules: assets/js/modules.js (nl) of modules-en.js (en), teksten: assets/js/taal.js. */
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
        s.src = '/assets/js/' + (window.PA_TAAL === 'en' ? 'vragen-en' : 'vragen') + '/' + id + '.js?v=' + ((window.PA_VRAGEN_V || {})[id] || '');
        s.onload = ok; s.onerror = function(){ delete laden[id]; s.remove(); nok(new Error('laden mislukt')); };
        document.head.appendChild(s);
      }));
    }));
  }
  var ADVIES = PA_T('advies'), DISCLAIMER = PA_T('disclaimer');
  var paneel = document.getElementById('paneel');
  var DFO_MAIL = 'info@dfobv.nl', deelnemer = null; // gegevens uit het formulier voor de uitslag; alleen in het geheugen van deze pagina
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
  function nu(){ var d = new Date(); return PA_DATUM(vandaag()) + ', ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0') + PA_T('uur'); }
  function modById(id){ return MODS.filter(function(m){ return m.id === id; })[0]; }

  // Welke modules horen bij de huidige keuze (altijd in de vaste volgorde van de modules)
  function gekozenModules(){ return MODS.filter(function(m){ return keuze.indexOf(m.id) > -1; }); }
  function keuzeLabel(){
    var ms = gekozenModules();
    if(ms.length === MODS.length) return PA_T('alleModules');
    if(ms.length > 1) return PA_T('mijnPakketLijst', ms.map(function(m){ return m.naam; }).join(', '));
    return 'Wft ' + ms[0].naam;
  }
  function bijgewerktTekst(){
    var ms = gekozenModules();
    if(ms.length === 1) return PA_T('bijgewerkt1', PA_DATUM(ms[0].bijgewerkt));
    var oudste = ms.map(function(m){ return m.bijgewerkt; }).sort()[0];
    return PA_T('bijgewerktN', ms.length, PA_DATUM(oudste));
  }

  // Logo als data-URL, zodat het certificaat ook in een nieuw venster en bij printen het logo toont
  var LOGO = window.PA_LOGO || '/assets/logo/dfo-logo.png';
  (function(){ var img = new Image(); img.onload = function(){ try{ var c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight; c.getContext('2d').drawImage(img, 0, 0); LOGO = c.toDataURL('image/png'); }catch(e){} }; img.src = LOGO; })();

  function tipBlok(){ var d = el('div', {class:'tipblok'}); if(window.PA_TIP) window.PA_TIP(d); return d; }
  function agendaBlok(){ var d = el('div', {style:'margin-top:24px'}); if(window.PA_AGENDA) window.PA_AGENDA(d); return d; }

  function startScherm(){
    var info = el('p', {class:'bijgewerkt', 'aria-live':'polite'});
    function aantalTekst(){ var n = gekozenModules().length; return n ? PA_T('aantal', n, aantalVragen(n)) : PA_T('kiesMinimaal'); }
    var uitlegAantal = el('p', {id:'aantalTekst', class:'aantal', 'aria-live':'polite'});
    var startKnop = el('button', {class:'btn', type:'button', id:'startKnop', onclick:start}, PA_T('startToets'));
    var vakjes = el('div', {class:'modkeuze', role:'group', 'aria-label':PA_T('modules')});
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
      el('button', {type:'button', class:'linkknop', id:'alleModules', onclick:function(){ keuze = MODS.map(function(m){ return m.id; }); bijwerken(); }}, PA_T('alleModules')), ' · ',
      el('button', {type:'button', class:'linkknop', onclick:function(){ keuze = []; bijwerken(); }}, PA_T('niets')), ' · ',
      el('a', {href:PA_PAGINA('index', 'check')}, PA_T('kiesKwal')));
    vul(el('div', {class:'start'},
      el('h2', null, PA_T('testKennis')),
      el('p', null, PA_T('startUitleg')),
      vakjes, snel, uitlegAantal, info, teamBlok(),
      el('p', {class:'advies'}, ADVIES),
      startKnop,
      agendaBlok()
    ));
    bijwerken();
  }

  // Link naar precies deze modulekeuze, om te delen met collega's of het hele team
  function teamLink(){
    var ids = gekozenModules().map(function(m){ return m.id; });
    return PA_URL('toets') + (ids.length === MODS.length ? '#alles' : ids.length > 1 ? '#mix=' + ids.join(',') : ids.length ? '#' + ids[0] : '');
  }
  function teamBlok(){
    var melding = el('span', {class:'klein', id:'teamStatus', 'aria-live':'polite'});
    var knop = el('button', {type:'button', class:'linkknop', id:'teamLink', onclick:function(){
      var url = teamLink();
      var klaar = function(){ melding.textContent = PA_T('teamGekopieerd', url); }, zelf = function(){ melding.textContent = PA_T('teamZelf', url); };
      try{ if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(klaar, zelf); else zelf(); }catch(e){ zelf(); }
    }}, PA_T('teamKopieer'));
    return el('p', {class:'team'}, knop, melding);
  }

  function start(){
    var ms = gekozenModules(), knop = document.getElementById('startKnop');
    if(knop){ knop.disabled = true; knop.textContent = PA_T('vragenLaden'); }
    laad(ms.map(function(m){ return m.id; })).then(function(){ begin(ms); }, function(){
      alert(PA_T('ladenMislukt'));
      if(knop){ knop.disabled = false; knop.textContent = PA_T('startToets'); }
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
        el('span', {class:'kop'}, (o.juist ? PA_T('goed') : PA_T('fout')) + o.t + (k === v.keuze ? PA_T('jouwAntwoord') : '')),
        el('span', {class:'tekst'}, o.u));
    }));
  }
  // Twijfel over een vraag: vraag, antwoorden en uitleg direct naar DFO mailen
  function meldLink(v){
    var juist = v.opties.filter(function(o){ return o.juist; })[0];
    var body = PA_T('meldModule', v.module.naam) + (v.term ? '\n' + PA_T('meldTerm', v.term) : '') + '\n\n' + PA_T('meldVraag') + '\n' + v.vraag + '\n\n' + PA_T('meldAntwoorden') + '\n'
      + v.opties.map(function(o, k){ return 'ABCD'[k] + '. ' + o.t + (o.juist ? PA_T('meldGegevenJuist') : '') + (k === v.keuze ? PA_T('meldMijnAntwoord') : ''); }).join('\n')
      + '\n\n' + PA_T('meldUitleg') + '\n' + juist.u + '\n\n' + PA_T('meldTwijfel') + '\n';
    var href = 'mailto:info@dfobv.nl?subject=' + encodeURIComponent(PA_T('meldOnderwerp')) + '&body=' + encodeURIComponent(body);
    return el('p', {class:'meld'}, el('a', {href:href, id:'meldVraag'}, PA_T('meldLink')));
  }

  function toonVraag(){
    var v = toets[stap];
    var titel = el('h2', {id:'vraagtitel', tabindex:'-1'}, v.vraag);
    var opties = el('div', {class:'opties', role:'group', 'aria-labelledby':'vraagtitel'});
    var uitlegVak = el('div');
    var volgende = el('button', {class:'btn', type:'button', id:'volgende', disabled:''}, stap < toets.length - 1 ? PA_T('volgende') : PA_T('bekijkResultaat'));
    volgende.addEventListener('click', function(){ if(stap < toets.length - 1){ stap++; toonVraag(); } else if(oefenen) oefenKlaar(); else gegevensScherm(); });
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
          el('strong', null, o.juist ? PA_T('juistKop') : PA_T('onjuistKop')), uitlegLijst(v), meldLink(v)));
        volgende.disabled = false;
        volgende.focus();
      });
      opties.append(b);
    });
    var pct = Math.round(stap / toets.length * 100);
    vul(el('div', {class:'vraag'},
      el('div', {class:'voortgang'}, el('span', {id:'vraagKop'}, PA_T(oefenen ? 'oefenVraag' : 'vraagVan', stap + 1, toets.length)), el('span', {class:'badge'}, 'Wft ' + v.module.naam + (v.term ? PA_T('badgeTerm', v.term) : ''))),
      el('div', {class:'balk', role:'progressbar', 'aria-label':PA_T('voortgang'), 'aria-valuemin':'0', 'aria-valuemax':'100', 'aria-valuenow':String(pct)}, el('span', {style:'width:' + pct + '%'})),
      titel, opties, uitlegVak,
      el('div', {class:'acties'}, el('button', {class:'btn ghost', type:'button', onclick:function(){ if(confirm(PA_T('stoppenVraag'))) startScherm(); }}, PA_T('stoppen')), volgende)
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
      el('div', {class:'score'}, kop, el('p', null, PA_T(nogFout.length ? 'oefenKlaarFout' : 'oefenKlaarGoed')),
        el('p', {class:'klein'}, PA_T('oefenTelt'))),
      el('div', {class:'acties', style:'justify-content:center'},
        nogFout.length ? oefenKnop(nogFout, PA_T('oefenDeze', nogFout.length)) : null,
        hoofdtoets ? el('button', {class:'btn ghost', type:'button', id:'terugResultaat', onclick:function(){ oefenen = false; toets = hoofdtoets; resultaat(true); }}, PA_T('terugResultaat')) : null,
        el('button', {class:'btn ghost', type:'button', onclick:start}, PA_T('nieuweToets'))));
    kop.focus();
  }

  // Uitslag pas na het invullen van je gegevens; een kopie van het certificaat gaat naar DFO BV (via het mailconcept dat jij verstuurt)
  function gegevensScherm(){
    var d = deelnemer || {};
    var naam = el('input', {type:'text', id:'gatenaam', autocomplete:'name', required:'', maxlength:'80', value:d.naam || ''});
    var mail = el('input', {type:'email', id:'gatemail', autocomplete:'email', required:'', maxlength:'120', value:d.mail || ''});
    var geb = el('input', {type:'date', id:'gategeb', autocomplete:'bday', max:vandaag(), min:'1925-01-01', value:d.geb || ''});
    var bedrijf = el('input', {type:'text', id:'gatebedrijf', autocomplete:'organization', maxlength:'100', value:d.bedrijf || ''});
    var werkgever = el('input', {type:'email', id:'gatewerkgever', maxlength:'120', value:d.werkgever || ''});
    var akkoord = el('input', {type:'checkbox', id:'gateakkoord', required:''});
    var status = el('div', {class:'certstatus', id:'gateStatus', 'aria-live':'polite'});
    var geldig = function(m){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(m); };
    var form = el('form', {class:'certform gate', id:'gateForm', novalidate:''},
      el('h2', null, PA_T('gateTitel')),
      el('p', null, PA_T('gateUitleg')),
      el('div', {class:'veld'}, el('label', {for:'gatenaam'}, PA_T('labelNaam')), naam),
      el('div', {class:'veld'}, el('label', {for:'gatemail'}, PA_T('labelMail')), mail),
      el('div', {class:'veld'}, el('label', {for:'gategeb'}, PA_T('labelGeb')), geb),
      el('div', {class:'veld'}, el('label', {for:'gatebedrijf'}, PA_T('labelBedrijf')), bedrijf),
      el('div', {class:'veld'}, el('label', {for:'gatewerkgever'}, PA_T('labelWerkgever')), werkgever),
      el('label', {class:'vink', for:'gateakkoord'}, akkoord, el('span', null, PA_T('gateAkkoord') + ' ', el('a', {href:PA_PAGINA('privacy'), target:'_blank', rel:'noopener'}, PA_T('gatePrivacy')))),
      el('div', {class:'acties', style:'margin-top:12px'}, el('button', {class:'btn', type:'submit', id:'gateKnop'}, PA_T('gateKnop'))),
      el('p', {class:'klein'}, PA_T('gateNoot')),
      status);
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var g = {naam:naam.value.trim(), mail:mail.value.trim(), geb:geb.value, bedrijf:bedrijf.value.trim(), werkgever:werkgever.value.trim()};
      if(!g.naam){ status.textContent = PA_T('vulNaam'); naam.focus(); return; }
      if(!geldig(g.mail)){ status.textContent = PA_T('geldigMail'); mail.focus(); return; }
      if(g.geb && (!/^\d{4}-\d{2}-\d{2}$/.test(g.geb) || g.geb > vandaag() || g.geb < '1925-01-01')){ status.textContent = PA_T('geldigGeb'); geb.focus(); return; }
      if(g.werkgever && !geldig(g.werkgever)){ status.textContent = PA_T('geldigWerkgever'); werkgever.focus(); return; }
      if(!akkoord.checked){ status.textContent = PA_T('gateAkkoordFout'); akkoord.focus(); return; }
      deelnemer = g;
      resultaat(false);
    });
    hoofdtoets = toets;
    vul(form);
    naam.focus();
  }

  function resultaat(terug){
    var goed = toets.filter(function(v){ return v.opties[v.keuze].juist; }).length, n = toets.length;
    var ms = gekozenModules();
    hoofdtoets = toets;
    if(!terug || !laatste) laatste = {goed:goed, n:n, pct:Math.round(goed / n * 100), thema:keuzeLabel(), themaKort:ms.length > 1 && ms.length < MODS.length ? PA_T('mijnPakket') : keuzeLabel(), datum:PA_DATUM(vandaag()), nummer:certificaatnummer(),
      bijgewerkt:PA_DATUM(ms.map(function(m){ return m.bijgewerkt; }).sort()[0]),
      modules:ms.map(function(m){ return 'Wft ' + m.naam; }),
      vanMods:MODS.map(function(m){ var n = toets.filter(function(v){ return v.module.id === m.id; }).length; return n ? m.naam + ' (' + n + ')' : null; }).filter(Boolean),
      vragen:toets.map(function(v){ var j = v.opties.filter(function(o){ return o.juist; })[0]; return {vraag:v.vraag, jouw:v.opties[v.keuze].t, juist:j.t, goed:v.opties[v.keuze].juist}; })};
    var geslaagd = goed / n >= 0.7; // geslaagd vanaf 70% goed
    var oordeel = PA_T(goed === n ? 'oordeel1' : goed / n >= 0.7 ? 'oordeel2' : goed / n >= 0.5 ? 'oordeel3' : 'oordeel4');
    var lijst = el('ol', {class:'overzicht'});
    toets.forEach(function(v){ lijst.append(el('li', {class:v.opties[v.keuze].juist ? 'ok' : 'nok'}, el('span', {class:'v'}, v.vraag), uitlegLijst(v), meldLink(v))); });
    vul(
      el('div', {class:'score' + (geslaagd ? ' geslaagd' : '')}, geslaagd ? el('p', {class:'hoera', role:'status'}, PA_T('hoera')) : null, el('div', {class:'getal', id:'score', tabindex:'-1'}, goed + '/' + n), el('p', null, oordeel)),
      goed < n ? el('div', {class:'acties', style:'justify-content:center'}, oefenKnop(fouten(toets), PA_T('oefenFoute', n - goed))) : null,
      certificaatFormulier(deelnemer),
      agendaBlok(),
      tipBlok(),
      el('div', {class:'acties', style:'justify-content:center'},
        el('button', {class:'btn ghost', type:'button', onclick:start}, PA_T('nieuweZelfde')),
        el('button', {class:'btn ghost', type:'button', onclick:startScherm}, PA_T('andereModule')),
        el('button', {class:'btn ghost', type:'button', id:'printAntwoorden', onclick:printAntwoorden}, PA_T('printAntwoorden'))),
      el('h3', {style:'margin-top:24px;font-size:17px'}, PA_T('overzichtUitleg')),
      lijst);
    var sc = document.getElementById('score'); sc.focus({preventScroll:true}); sc.parentNode.scrollIntoView({block:'start'});
    if(geslaagd && !terug) feest();
    // Certificaat meteen klaarzetten: pdf als bijlage in een mail aan jezelf, met een kopie aan DFO BV
    var cf = document.getElementById('certForm');
    if(cf && !terug && deelnemer) setTimeout(function(){ if(cf.requestSubmit) cf.requestSubmit(); else cf.dispatchEvent(new Event('submit', {cancelable:true})); }, 400);
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

  function kopieAdressen(g){ return [g.werkgever, DFO_MAIL].filter(Boolean).join(', '); } // werkgever (optioneel) en DFO BV

  function certificaatFormulier(vooraf){
    vooraf = vooraf || {};
    var naam = el('input', {type:'text', id:'certnaam', autocomplete:'name', required:'', maxlength:'80', value:vooraf.naam || ''});
    var mail = el('input', {type:'email', id:'certmail', autocomplete:'email', required:'', maxlength:'120', value:vooraf.mail || ''});
    var geb = el('input', {type:'date', id:'certgeb', autocomplete:'bday', max:vandaag(), min:'1925-01-01', value:vooraf.geb || ''});
    var bedrijf = el('input', {type:'text', id:'certbedrijf', autocomplete:'organization', maxlength:'100', value:vooraf.bedrijf || ''});
    var werkgever = el('input', {type:'email', id:'certwerkgever', maxlength:'120', value:vooraf.werkgever || ''});
    function gegevens(){ return {naam:naam.value.trim(), mail:mail.value.trim(), geb:geb.value, bedrijf:bedrijf.value.trim(), werkgever:werkgever.value.trim()}; }
    function controleer(metMail){
      var g = gegevens();
      if(!g.naam){ status.textContent = PA_T('vulNaam'); naam.focus(); return null; }
      if(g.geb && (!/^\d{4}-\d{2}-\d{2}$/.test(g.geb) || g.geb > vandaag() || g.geb < '1925-01-01')){ status.textContent = PA_T('geldigGeb'); geb.focus(); return null; }
      if(metMail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(g.mail)){ status.textContent = PA_T('geldigMail'); mail.focus(); return null; }
      if(g.werkgever && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(g.werkgever)){ status.textContent = PA_T('geldigWerkgever'); werkgever.focus(); return null; }
      return g;
    }
    var status = el('div', {class:'certstatus', id:'certStatus', 'aria-live':'polite'});
    var form = el('form', {class:'certform', id:'certForm', novalidate:''},
      el('h3', null, PA_T('ontvangCert')),
      el('p', {class:'advies'}, ADVIES),
      el('p', null, PA_T('certUitleg')),
      el('div', {class:'veld'}, el('label', {for:'certnaam'}, PA_T('labelNaam')), naam),
      el('div', {class:'veld'}, el('label', {for:'certgeb'}, PA_T('labelGeb')), geb),
      el('div', {class:'veld'}, el('label', {for:'certmail'}, PA_T('labelMail')), mail),
      el('div', {class:'veld'}, el('label', {for:'certbedrijf'}, PA_T('labelBedrijf')), bedrijf),
      el('div', {class:'veld'}, el('label', {for:'certwerkgever'}, PA_T('labelWerkgever')), werkgever),
      el('div', {class:'acties', style:'margin-top:12px'},
        el('button', {class:'btn', type:'submit', id:'mailPdfKnop'}, PA_T('mailPdf')),
        el('button', {class:'btn ghost', type:'button', id:'pdfKnop', onclick:function(){ status.className = 'certstatus'; var g = controleer(false); if(!g) return; g.uitgegeven = nu(); g.verstuurd = false; maakPdf(g).then(function(doc){ PA_PDF.download(doc.output('blob'), pdfNaam(), 'application/pdf'); status.className = 'certstatus klaar'; status.textContent = PA_T('pdfGedownload', pdfNaam()); }); }}, PA_T('downloadPdf')),
        el('button', {class:'btn ghost', type:'button', id:'printKnop', onclick:function(){ status.className = 'certstatus'; var g = controleer(false); if(!g) return; g.uitgegeven = nu(); g.verstuurd = false; printCertificaat(g); }}, PA_T('bekijkPrint'))),
      el('p', {class:'klein', style:'margin-top:10px'}, el('a', {href:'#', id:'mailTekstLink', onclick:function(e){ e.preventDefault(); status.className = 'certstatus'; var g = controleer(true); if(!g) return; g.uitgegeven = nu(); g.verstuurd = true; var href = mailHref(g); form.setAttribute('data-mailto', href); window.location.href = href; }}, PA_T('mailTekstLink'))),
      status);
    form.addEventListener('submit', function(e){
      e.preventDefault(); status.className = 'certstatus';
      var g = controleer(true); if(!g) return;
      g.uitgegeven = nu(); g.verstuurd = true;
      form.setAttribute('data-mailto', mailHref(g));
      status.textContent = PA_T('certMaken');
      maakPdf(g).then(function(doc){
        var blob = doc.output('blob'), naamPdf = pdfNaam(), onderwerp = mailOnderwerp(g), tekst = certTekst(g, false);
        var bestand = null; try{ bestand = new File([blob], naamPdf, {type:'application/pdf'}); }catch(e){}
        if(bestand && navigator.canShare && navigator.canShare({files:[bestand]})){
          // Mobiel en browsers met delen: de pdf gaat als bijlage naar de gekozen mail-app
          navigator.share({files:[bestand], title:onderwerp, text:PA_T('deelBericht', g.mail) + PA_T('deelKopie', kopieAdressen(g)) + '\n\n' + tekst}).then(function(){
            status.className = 'certstatus klaar'; status.textContent = PA_T('deelKlaar', g.mail, kopieAdressen(g));
          }).catch(function(){ emlDownload(doc, g, onderwerp, tekst, naamPdf); });
        } else emlDownload(doc, g, onderwerp, tekst, naamPdf);
      });
    });
    return form;
  }


  function certTekst(g, metVragen){
    var r = laatste;
    return PA_T('mailTitel') + '\n\n' + PA_T('mNaam') + g.naam + (g.geb ? '\n' + PA_T('mGeb') + PA_DATUM(g.geb) : '') + '\n' + PA_T('mMail') + g.mail + (g.bedrijf ? '\n' + PA_T('mBedrijf') + g.bedrijf : '') + '\n' + PA_T('mVerstuurd') + g.uitgegeven + '\n' + PA_T('mResultaat', r.goed, r.n, r.pct) + '\n' + PA_T('mModule') + r.thema + (r.modules.length > 1 ? '\n' + PA_T('mModules') + r.modules.join(', ') + '\n' + PA_T('mVragenUit') + r.vanMods.join(', ') : '') + '\n' + PA_T('mDatum') + r.datum + '\n' + PA_T('mBank') + r.bijgewerkt + '\n' + PA_T('mNummer') + r.nummer + '\n\n'
      + ADVIES + '\n\n' + PA_T('mOpnieuw') + PA_URL('toets') + '\nWft Permanent Actueel: ' + PA_SITE + '\n\n' + DISCLAIMER + '\n';
  }
  function mailOnderwerp(g){ return PA_T('mOnderwerp', laatste.nummer, g.naam, laatste.goed, laatste.n); }
  function pdfNaam(){ return PA_T('pdfNaam', laatste.nummer); }
  function maakPdf(g){ return window.PA_PDF ? PA_PDF.maak(laatste, g, LOGO, STEMPEL, ADVIES, DISCLAIMER) : Promise.reject(new Error('pdf niet geladen')); }
  function emlDownload(doc, g, onderwerp, tekst, naamPdf){
    var naamEml = PA_T('emlNaam', laatste.nummer);
    PA_PDF.download(PA_PDF.eml(doc, g.mail, kopieAdressen(g), onderwerp, tekst, naamPdf), naamEml, 'message/rfc822');
    var st = document.getElementById('certStatus');
    st.className = 'certstatus klaar';
    st.textContent = PA_T('emlKlaar', naamEml, g.mail, PA_T('emlKopie', kopieAdressen(g)));
  }
  function mailHref(g){
    var onderwerp = mailOnderwerp(g);
    var basis = 'mailto:' + encodeURIComponent(g.mail) + '?' + 'cc=' + encodeURIComponent(kopieAdressen(g)) + '&' + 'subject=' + encodeURIComponent(onderwerp) + '&body=';
    return basis + encodeURIComponent(certTekst(g, false));
  }

  var STEMPEL = '<svg class="stempel" viewBox="0 0 200 200" aria-label="' + PA_T('stempelLabel') + '" role="img"><defs><path id="cirkel" d="M100,100 m-72,0 a72,72 0 1,1 144,0 a72,72 0 1,1 -144,0"/></defs>'
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
      + '<div class="kop"><img src="' + LOGO + '" alt="' + PA_T('cLogoAlt') + '"><div class="nr">' + PA_T('cNummer') + '<br><strong>' + r.nummer + '</strong><br>' + r.datum + '<br><a href="' + PA_SITE + '" style="color:#0E5AA7;font-weight:700;text-decoration:none">PA-WFT.nl</a></div></div>'
      + '<h1>' + PA_T('cTitel') + '</h1><p class="sub">' + PA_T('cSub') + '</p>'
      + '<div>' + PA_T('cEigenVerklaring') + '</div><div class="naam">' + esc(g.naam) + '</div>'
      + '<dl class="pers">' + (g.geb ? '<dt>' + PA_T('cGeb') + '</dt><dd>' + esc(PA_DATUM(g.geb)) + '</dd>' : '') + (g.mail ? '<dt>' + PA_T('cMail') + '</dt><dd>' + esc(g.mail) + '</dd>' : '') + (g.bedrijf ? '<dt>' + PA_T('cBedrijf') + '</dt><dd>' + esc(g.bedrijf) + '</dd>' : '')
      + '<dt>' + PA_T(g.verstuurd ? 'cVerstuurd' : 'cAangemaakt') + '</dt><dd>' + esc(g.uitgegeven) + '</dd></dl>'
      + '<div>' + PA_T('cAfgelegd') + '</div>'
      + '<div class="res"><div><strong>' + r.goed + ' / ' + r.n + '</strong>' + PA_T('cGoed') + '</div><div><strong>' + r.pct + '%</strong>' + PA_T('cScore') + '</div><div><strong>' + esc(r.themaKort) + '</strong>' + PA_T(r.modules.length > 1 ? 'cModulesMv' : 'cModule') + '</div><div><strong>' + esc(r.bijgewerkt) + '</strong>' + PA_T('cBank') + '</div></div>'
      + (r.modules.length > 1 ? '<dl class="pers mods"><dt>' + PA_T('cModulesLabel') + '</dt><dd>' + esc(r.modules.join(', ')) + '</dd><dt>' + PA_T('cVragenUit') + '</dt><dd>' + esc(r.vanMods.join(', ')) + '</dd></dl>' : '')
      + '<p class="advies">' + ADVIES + PA_T('cOpnieuw') + '<a href="' + PA_URL('toets') + '">' + PA_URL('toets').replace('https://', '') + '</a>.</p>'
      + '<div class="voet"><p>' + DISCLAIMER + '<br><a href="' + PA_SITE + '" style="color:#0E5AA7;font-weight:700">PA-WFT.nl — ' + PA_SITE + '</a></p>' + STEMPEL + '</div>'
      + '</div></div>';
    return '<!doctype html><html lang="' + PA_TAAL + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>' + esc(PA_T('cDocTitel', g.naam)) + '</title><style>' + css + '</style></head><body>' + body
      + '<script>window.onload=function(){setTimeout(function(){window.focus();window.print();},300);}<\/script></body></html>';
  }

  // Overzicht van alle beantwoorde vragen met uitleg, om te printen of als pdf op te slaan
  function printAntwoorden(){
    var r = laatste, w = window.open('', '_blank');
    if(!w){ alert(PA_T('popupAntw')); return; }
    var items = toets.map(function(v, i){
      var ok = v.opties[v.keuze].juist;
      return '<li class="' + (ok ? 'ok' : 'nok') + '"><p class="kop"><span>' + esc(PA_T('aVraagNr', i + 1, v.module.naam)) + (v.term ? esc(PA_T('aTermCdfd', v.term)) : '') + '</span><strong>' + PA_T(ok ? 'aGoed' : 'aFout') + '</strong></p><p class="v">' + esc(v.vraag) + '</p><ul>'
        + v.opties.map(function(o, k){ return '<li class="' + (o.juist ? 'j' : 'f') + (k === v.keuze ? ' g' : '') + '"><b>' + 'ABCD'[k] + '. ' + esc(o.t) + (o.juist ? PA_T('aJuist') : '') + (k === v.keuze ? PA_T('aJouw') : '') + '</b><br>' + esc(o.u) + '</li>'; }).join('') + '</ul></li>';
    }).join('');
    var css = 'body{font-family:"Segoe UI",Arial,sans-serif;color:#2C3A47;margin:24px;font-size:12.5px;line-height:1.45}h1{font-size:22px;color:#0E5AA7;margin:0 0 4px}.meta{color:#4A4A4A;margin:0 0 18px}'
      + 'ol{list-style:none;padding:0;margin:0}ol>li{border:1px solid #BBD3EA;border-left:5px solid #1B6B3A;padding:10px 14px;margin:0 0 12px;page-break-inside:avoid}ol>li.nok{border-left-color:#A52A21}'
      + '.kop{display:flex;justify-content:space-between;margin:0;font-size:11px;color:#4A4A4A}.kop strong{color:#1B6B3A}li.nok .kop strong{color:#A52A21}.v{font-weight:700;font-size:13.5px;margin:4px 0 8px}'
      + 'ul{margin:0;padding:0;list-style:none}ul li{padding:4px 0 4px 10px;border-left:3px solid #E3C7C4;margin:0 0 4px}ul li.j{border-left-color:#1B6B3A}ul li.g{background:#F4F7FB}a{color:#0E5AA7}'
      + '@media print{body{margin:0}@page{size:A4;margin:14mm}}';
    w.document.open();
    w.document.write('<!doctype html><html lang="' + PA_TAAL + '"><head><meta charset="utf-8"><title>' + PA_T('aDocTitel', r.nummer) + '</title><style>' + css + '</style></head><body>'
      + '<h1>' + PA_T('aKop') + '</h1><p class="meta">' + esc(PA_T('aMeta', r.thema, r.goed, r.n, r.pct, r.datum, r.nummer)) + '<a href="' + PA_SITE + '">PA-WFT.nl</a></p>'
      + '<ol>' + items + '</ol><p class="meta">' + PA_T('aVoet', PA_URL('toets')) + '</p>'
      + '<script>window.onload=function(){setTimeout(function(){window.focus();window.print();},300);}<\/script></body></html>');
    w.document.close();
  }

  // Printen via een nieuw venster: window.print() wordt in een iframe (bijvoorbeeld Google Sites) geblokkeerd
  function printCertificaat(g){
    var w = window.open('', '_blank');
    if(!w){ alert(PA_T('popupCert')); return; }
    w.document.open(); w.document.write(certificaatHTML(g)); w.document.close();
  }

  // Voorkeuze via de link: toets.html#hypothecair-krediet of toets.html#mix=basis,pensioen
  // Oefenronde met alle vragen van één toetsterm (telt niet mee voor het certificaat)
  function oefenTerm(mid, term){
    var m = modById(mid);
    if(!m) return false;
    vul(el('p', {class:'laden'}, PA_T('vragenLaden')));
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
