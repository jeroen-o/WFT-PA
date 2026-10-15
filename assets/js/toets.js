(function(){
  var AANTAL=7, GESLAAGD=5;
  var MODS=window.PA_MODULES, VRAGEN=window.PA_VRAGEN||{};
  var $=function(id){return document.getElementById(id);};
  var stappen=['stap-kies','stap-vraag','stap-uitslag','stap-cert'];
  var mod=null, reeks=[], nr=0, antwoorden=[], cert=null;

  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function rnd(n){var a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]%n;}
  function hussel(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=rnd(i+1),t=a[i];a[i]=a[j];a[j]=t;}return a;}
  function toon(id,focus){stappen.forEach(function(s){$(s).hidden=s!==id;});window.scrollTo(0,0);if(focus)$(focus).focus();}

  // Stap 1: module kiezen
  var grid=$('toetsModules');
  MODS.forEach(function(m,i){
    var n=(VRAGEN[m.id]||[]).length;
    var b=document.createElement('button');
    b.type='button';b.className='module kies';
    b.innerHTML='<span class="nr">'+String(i+1).padStart(2,'0')+'</span><h3>Wft '+esc(m.naam)+'</h3><p>'+esc(m.tekst)+'</p><p class="meta">'+n+' vragen · laatst bijgewerkt '+PA_DATUM(m.bijgewerkt)+'</p>';
    b.disabled=n<AANTAL;
    b.addEventListener('click',function(){start(m);});
    grid.appendChild(b);
  });

  function start(m){
    mod=m;nr=0;antwoorden=[];
    reeks=hussel(VRAGEN[m.id]).slice(0,AANTAL).map(function(q){
      var opties=hussel(q[1].map(function(a,i){return {tekst:a[0],uitleg:a[1],juist:i===0};}));
      return {vraag:q[0],opties:opties};
    });
    if(location.hash!=='#'+m.id)history.replaceState(null,'','#'+m.id);
    vraag();
  }

  // Stap 2: vragen
  function vraag(){
    var q=reeks[nr];
    $('vraagKop').textContent='Wft '+mod.naam+' · vraag '+(nr+1)+' van '+AANTAL;
    $('voortgangBalk').style.width=(nr/AANTAL*100)+'%';
    $('vraagTekst').textContent=q.vraag;
    $('uitleg').innerHTML='';$('volgende').hidden=true;
    var box=$('opties');box.innerHTML='';
    q.opties.forEach(function(o,i){
      var b=document.createElement('button');
      b.type='button';b.className='optie';
      b.textContent=String.fromCharCode(65+i)+'. '+o.tekst;
      b.addEventListener('click',function(){kies(i);});
      box.appendChild(b);
    });
    toon('stap-vraag','vraagTekst');
  }
  function kies(i){
    var q=reeks[nr],gekozen=q.opties[i],juist=q.opties.filter(function(o){return o.juist;})[0];
    antwoorden.push({vraag:q.vraag,gekozen:gekozen,juist:juist});
    [].forEach.call($('opties').children,function(b,j){b.disabled=true;if(q.opties[j].juist)b.classList.add('goed');else if(j===i)b.classList.add('fout');});
    $('uitleg').innerHTML=(gekozen.juist?'<p><strong>Goed.</strong> '+esc(gekozen.uitleg)+'</p>':'<p><strong>Niet goed.</strong> '+esc(gekozen.uitleg)+'</p><p><strong>Juist antwoord:</strong> '+esc(juist.tekst)+'. '+esc(juist.uitleg)+'</p>');
    var v=$('volgende');v.hidden=false;v.innerHTML=(nr+1<AANTAL?'Volgende vraag':'Bekijk je uitslag')+' <span>→</span>';v.focus();
  }
  $('volgende').addEventListener('click',function(){nr++;nr<AANTAL?vraag():uitslag();});

  // Stap 3: uitslag
  function score(){return antwoorden.filter(function(a){return a.gekozen.juist;}).length;}
  function uitslag(){
    var s=score(),ok=s>=GESLAAGD;
    $('uitslagKop').textContent='Wft '+mod.naam;
    $('uitslagTitel').textContent=s+' van '+AANTAL+' goed';
    $('uitslagTekst').textContent=ok?'Geslaagd. Vul je naam en e-mailadres in om je certificaat te maken.':'Voor een certificaat heb je er minimaal '+GESLAAGD+' van de '+AANTAL+' goed nodig. Probeer het nog eens; je krijgt nieuwe vragen.';
    $('certForm').hidden=!ok;$('formFout').textContent='';
    $('overzicht').innerHTML=antwoorden.map(function(a){
      return '<li><span class="'+(a.gekozen.juist?'ok">Goed':'nok">Fout')+'</span> — '+esc(a.vraag)+(a.gekozen.juist?'':'<br>Juist: '+esc(a.juist.tekst))+'</li>';
    }).join('');
    toon('stap-uitslag','uitslagTitel');
  }
  $('opnieuw').addEventListener('click',function(){start(mod);});
  $('andereModule').addEventListener('click',kiesOpnieuw);
  $('terug').addEventListener('click',function(){start(mod);});
  function kiesOpnieuw(){history.replaceState(null,'',location.pathname);toon('stap-kies');}

  // Stap 4: certificaat
  $('certForm').addEventListener('submit',function(e){
    e.preventDefault();
    var naam=$('naam').value.trim(),email=$('email').value.trim();
    if(!naam){$('formFout').textContent='Vul je naam in.';$('naam').focus();return;}
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){$('formFout').textContent='Vul een geldig e-mailadres in.';$('email').focus();return;}
    var d=new Date(),iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
    var code='';for(var i=0;i<6;i++)code+='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'[rnd(32)];
    cert={naam:naam,email:email,module:'Wft '+mod.naam,bijgewerkt:PA_DATUM(mod.bijgewerkt),score:score(),datum:PA_DATUM(iso),nummer:'PA-'+iso.replace(/-/g,'')+'-'+code};
    $('certVoorbeeld').innerHTML=certHtml(cert,'assets/logo/dfo-logo.png');
    $('mailKnop').href='mailto:'+encodeURIComponent(email)+'?subject='+encodeURIComponent('Certificaat PA-toets '+cert.module+' — '+cert.nummer)+'&body='+encodeURIComponent(certTekst(cert));
    toon('stap-cert','certTitel');
  });

  var DISCLAIMER='Dit certificaat bevestigt het resultaat van een oefentoets van Wft Permanent Actueel. Het is geen PE-examen en telt niet mee voor de registratie van je vakbekwaamheid. Het certificaat is niet centraal geregistreerd.';
  function certHtml(c,logo){
    return '<article class="cert">'+
      '<div class="cert-top"><span class="kicker">Wft Permanent Actueel · PA-WFT.nl</span><img src="'+esc(logo)+'" alt="DFO — dienstverlening voor financiële ondernemers"></div>'+
      '<span class="kicker ink">Certificaat PA-toets</span>'+
      '<h3>'+esc(c.naam)+'</h3>'+
      '<p>heeft de PA-toets <strong>'+esc(c.module)+'</strong> met goed gevolg afgelegd.</p>'+
      '<dl><dt>Resultaat</dt><dd>'+c.score+' van '+AANTAL+' vragen goed</dd>'+
      '<dt>Datum</dt><dd>'+esc(c.datum)+'</dd>'+
      '<dt>Vragenbank bijgewerkt</dt><dd>'+esc(c.bijgewerkt)+'</dd>'+
      '<dt>Certificaatnummer</dt><dd>'+esc(c.nummer)+'</dd></dl>'+
      '<p class="klein">Wft Permanent Actueel is een activiteit van DFO BV, De Wel 14–16, 3871 MV Hoevelaken. '+DISCLAIMER+'</p>'+
    '</article>';
  }
  function certTekst(c){
    return 'CERTIFICAAT PA-TOETS\nWft Permanent Actueel (PA-WFT.nl), een activiteit van DFO BV\n\n'+
      c.naam+' heeft de PA-toets '+c.module+' met goed gevolg afgelegd.\n\n'+
      'Resultaat: '+c.score+' van '+AANTAL+' vragen goed\nDatum: '+c.datum+'\nVragenbank bijgewerkt: '+c.bijgewerkt+'\nCertificaatnummer: '+c.nummer+'\n\n'+DISCLAIMER+'\n';
  }
  $('printKnop').addEventListener('click',function(){
    // window.open in plaats van window.print: werkt ook als de pagina in een iframe staat
    var w=window.open('','_blank');
    if(!w){alert('Sta pop-ups toe om het certificaat te openen.');return;}
    var basis=location.href.replace(/[#?].*$/,'').replace(/[^\/]*$/,'');
    var css=[].map.call(document.styleSheets,function(s){try{return [].map.call(s.cssRules,function(r){return r.cssText;}).join('\n');}catch(e){return '';}}).join('\n');
    var logo=basis+'assets/logo/dfo-logo.png',img=document.querySelector('#certVoorbeeld img');
    // Logo als data-URL meegeven, zodat het ook in het nieuwe venster direct zichtbaar en printbaar is
    try{var c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;c.getContext('2d').drawImage(img,0,0);logo=c.toDataURL('image/png');}catch(e){}
    w.document.write('<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Certificaat '+esc(cert.nummer)+'</title><style>'+css+'body{padding:24px}@media print{body{padding:0}.cert{border:2px solid #201e1d}}</style></head><body>'+certHtml(cert,logo)+'<script>window.onload=function(){window.print();};<\/script></body></html>');
    w.document.close();
  });

  // Direct naar een module via toets.html#hypothecair-krediet
  var h=location.hash.slice(1),m=MODS.filter(function(x){return x.id===h;})[0];
  if(m&&(VRAGEN[m.id]||[]).length>=AANTAL)start(m);
})();
