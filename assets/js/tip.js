/* Tip een collega: zet in het eigen mailprogramma een mail klaar met een wervende tekst over PA-WFT.nl.
   Er gaat niets via de site: de adressen blijven in de browser en in je eigen mail.
   Gebruik: <div data-tip></div>; window.PA_TIP(element) vult een element ook later (de toets). */
(function(){
  var ONDERWERP = PA_T('tipOnderwerp');
  var MAX = 50;
  var GELDIG = /^[^\s@,;<>"]+@[^\s@,;<>"]+\.[^\s@,;<>"]+$/;

  function tekst(naam){ return PA_T('tipTekst', naam); }
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
    var kop = mk('h3', null, PA_T('tipKop'));
    var uitleg = mk('p', null, PA_T('tipUitleg'));
    var lMail = mk('label', {'for':id('aan')}, PA_T('tipLabelMail'));
    var hulp = mk('span', {'class':'hulp', id:id('hulp')}, PA_T('tipHulp'));
    var aan = mk('textarea', {id:id('aan'), rows:'3', autocomplete:'off', spellcheck:'false', 'aria-describedby':id('hulp'), placeholder:PA_T('tipPlaceholder')});
    var lNaam = mk('label', {'for':id('naam')}, PA_T('tipLabelNaam'));
    var naam = mk('input', {type:'text', id:id('naam'), autocomplete:'name', maxlength:'80'});
    var bccL = mk('label', {'class':'vink'});
    var bcc = mk('input', {type:'checkbox', id:id('bcc')});
    bccL.append(bcc, document.createTextNode(PA_T('tipBcc')));
    var status = mk('p', {'class':'tipstatus', 'aria-live':'polite'});
    var knop = mk('button', {type:'button', 'class':'btn'}, PA_T('tipKnop'));
    var kopie = mk('button', {type:'button', 'class':'btn ghost'}, PA_T('tipKopieer'));
    var rij = mk('div', {'class':'acties'}); rij.append(knop, kopie);

    knop.addEventListener('click', function(){
      var lijst = adressen(aan.value), fout = lijst.filter(function(a){ return !GELDIG.test(a); });
      if(!lijst.length){ status.textContent = PA_T('tipMinimaal'); aan.focus(); return; }
      if(fout.length){ status.textContent = PA_T('tipControleer', fout.length, fout.join(', ')); aan.focus(); return; }
      if(lijst.length > MAX){ status.textContent = PA_T('tipMax', MAX); aan.focus(); return; }
      var ontvangers = lijst.join(',');
      var href = 'mailto:' + (bcc.checked ? '' : ontvangers) + '?' + (bcc.checked ? 'bcc=' + encodeURIComponent(ontvangers) + '&' : '')
        + 'subject=' + encodeURIComponent(ONDERWERP) + '&body=' + encodeURIComponent(tekst(naam.value.trim()));
      window.location.href = href;
      status.textContent = PA_T('tipOpent', lijst.length);
    });
    kopie.addEventListener('click', function(){
      var t = PA_T('tipOnderwerpLabel') + ONDERWERP + '\n\n' + tekst(naam.value.trim());
      var klaar = function(){ status.textContent = PA_T('tipOpKlembord'); };
      var zelf = function(){ status.textContent = PA_T('tipKopieerMislukt'); voorbeeld.open = true; };
      try{ if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(klaar, zelf); else zelf(); }catch(e){ zelf(); }
    });

    var voorbeeld = mk('details', {'class':'tipvoorbeeld'});
    var sv = mk('summary', null, PA_T('tipBekijk'));
    var pre = mk('pre');
    function ververs(){ pre.textContent = PA_T('tipOnderwerpLabel') + ONDERWERP + '\n\n' + tekst(naam.value.trim()); }
    naam.addEventListener('input', ververs); ververs();
    voorbeeld.append(sv, pre);

    doel.append(kop, uitleg, lMail, hulp, aan, lNaam, naam, bccL, rij, status, voorbeeld);
  };
  document.querySelectorAll('[data-tip]').forEach(function(el){ window.PA_TIP(el); });
})();
