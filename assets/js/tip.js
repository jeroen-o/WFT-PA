/* Tip een collega: zet in het eigen mailprogramma een mail klaar met een wervende tekst over PA-WFT.nl.
   Er gaat niets via de site: de adressen blijven in de browser en in je eigen mail.
   Gebruik: <div data-tip></div>; window.PA_TIP(element) vult een element ook later (de toets). */
(function(){
  var SITE = 'https://pa-wft.nl/', TOETS = 'https://pa-wft.nl/toets.html';
  var ONDERWERP = 'Tip: test gratis je Wft-kennis op PA-WFT.nl';
  var MAX = 50;
  var GELDIG = /^[^\s@,;<>"]+@[^\s@,;<>"]+\.[^\s@,;<>"]+$/;

  function tekst(naam){
    return 'Hoi,\n\n'
      + 'Ik test mijn Wft-kennis op PA-WFT.nl en dacht meteen aan jou. In een paar minuten weet je hoe actueel je kennis is, en het kost niets.\n\n'
      + 'Wat je krijgt:\n'
      + '- Praktijkcasussen uit alle 9 Wft-modules, van Basis tot Pensioen. Kies één module of je hele pakket.\n'
      + '- Bij elk antwoord uitleg waarom het goed of fout is.\n'
      + '- Vragen afgestemd op de toetstermen van het CDFD per 1 april 2026.\n'
      + '- Na afloop een certificaat voor je personeelsdossier.\n'
      + '- Gratis voor alle adviseurs, zonder account en zonder abonnement.\n\n'
      + 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Zullen we kijken wie de hoogste score haalt?\n\n'
      + 'Start hier: ' + TOETS + '\n\n'
      + 'Groet,\n' + (naam || '') + '\n\n'
      + '--\nWft Permanent Actueel (' + SITE + ') is een activiteit van DFO BV. Oefentoets, geen PE-examen.\n';
  }
  function adressen(invoer){
    return invoer.split(/[\s,;]+/).map(function(a){ return a.replace(/^<|>$/g, '').trim(); }).filter(Boolean)
      .filter(function(a, i, l){ return l.map(function(x){ return x.toLowerCase(); }).indexOf(a.toLowerCase()) === i; });
  }
  function mk(tag, attr, inhoud){
    var e = document.createElement(tag);
    Object.keys(attr || {}).forEach(function(k){ e.setAttribute(k, attr[k]); });
    if(inhoud) e.textContent = inhoud;
    return e;
  }

  var teller = 0;
  window.PA_TIP = function(doel){
    var n = ++teller, id = function(s){ return 'tip' + s + n; };
    doel.className = (doel.className ? doel.className + ' ' : '') + 'tip';
    doel.innerHTML = '';
    var kop = mk('h3', null, 'Tip je collega’s');
    var uitleg = mk('p', null, 'Ken je collega’s die hun Wft-kennis ook actueel willen houden? Vul hun e-mailadressen in. We zetten een mail met een korte uitnodiging klaar in je eigen mailprogramma; jij kijkt hem na en verstuurt hem zelf. De adressen gaan niet naar DFO en worden nergens bewaard.');
    var lMail = mk('label', {'for':id('aan')}, 'E-mailadressen van je collega’s');
    var hulp = mk('span', {'class':'hulp', id:id('hulp')}, 'Eén of meer adressen, gescheiden door een komma, puntkomma of nieuwe regel.');
    var aan = mk('textarea', {id:id('aan'), rows:'3', autocomplete:'off', spellcheck:'false', 'aria-describedby':id('hulp'), placeholder:'collega@kantoor.nl, collega2@kantoor.nl'});
    var lNaam = mk('label', {'for':id('naam')}, 'Je naam (onder de mail, optioneel)');
    var naam = mk('input', {type:'text', id:id('naam'), autocomplete:'name', maxlength:'80'});
    var bccL = mk('label', {'class':'vink'});
    var bcc = mk('input', {type:'checkbox', id:id('bcc')});
    bccL.append(bcc, document.createTextNode(' Verstuur als bcc, zodat collega’s elkaars adres niet zien'));
    var status = mk('p', {'class':'tipstatus', 'aria-live':'polite'});
    var knop = mk('button', {type:'button', 'class':'btn'}, 'Zet de mail klaar');
    var kopie = mk('button', {type:'button', 'class':'btn ghost'}, 'Kopieer de tekst');
    var rij = mk('div', {'class':'acties'}); rij.append(knop, kopie);

    knop.addEventListener('click', function(){
      var lijst = adressen(aan.value), fout = lijst.filter(function(a){ return !GELDIG.test(a); });
      if(!lijst.length){ status.textContent = 'Vul minimaal één e-mailadres in.'; aan.focus(); return; }
      if(fout.length){ status.textContent = 'Controleer ' + (fout.length === 1 ? 'dit adres' : 'deze adressen') + ': ' + fout.join(', '); aan.focus(); return; }
      if(lijst.length > MAX){ status.textContent = 'Maximaal ' + MAX + ' adressen per keer.'; aan.focus(); return; }
      var ontvangers = lijst.join(',');
      var href = 'mailto:' + (bcc.checked ? '' : ontvangers) + '?' + (bcc.checked ? 'bcc=' + encodeURIComponent(ontvangers) + '&' : '')
        + 'subject=' + encodeURIComponent(ONDERWERP) + '&body=' + encodeURIComponent(tekst(naam.value.trim()));
      window.location.href = href;
      status.textContent = 'Je mailprogramma opent met de uitnodiging aan ' + (lijst.length === 1 ? '1 collega' : lijst.length + ' collega’s') + '. Opent er niets, of gebruik je webmail? Kies dan "Kopieer de tekst".';
    });
    kopie.addEventListener('click', function(){
      var t = 'Onderwerp: ' + ONDERWERP + '\n\n' + tekst(naam.value.trim());
      var klaar = function(){ status.textContent = 'De tekst staat op je klembord. Plak hem in een nieuwe mail.'; };
      var zelf = function(){ status.textContent = 'Kopiëren lukte niet. Selecteer de tekst hieronder en kopieer hem zelf.'; voorbeeld.open = true; };
      try{ if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(klaar, zelf); else zelf(); }catch(e){ zelf(); }
    });

    var voorbeeld = mk('details', {'class':'tipvoorbeeld'});
    var sv = mk('summary', null, 'Bekijk de tekst van de mail');
    var pre = mk('pre');
    function ververs(){ pre.textContent = 'Onderwerp: ' + ONDERWERP + '\n\n' + tekst(naam.value.trim()); }
    naam.addEventListener('input', ververs); ververs();
    voorbeeld.append(sv, pre);

    doel.append(kop, uitleg, lMail, hulp, aan, lNaam, naam, bccL, rij, status, voorbeeld);
  };
  document.querySelectorAll('[data-tip]').forEach(function(el){ window.PA_TIP(el); });
})();
