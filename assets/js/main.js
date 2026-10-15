(function(){
  var MODS=window.PA_MODULES.map(function(m){return [m.naam,m.tekst,m.bijgewerkt,m.id];});
  var NS='http://www.w3.org/2000/svg';
  var grid=document.getElementById('moduleGrid');
  MODS.forEach(function(m,i){var d=document.createElement('article');d.className='module';d.innerHTML='<span class="nr">'+String(i+1).padStart(2,'0')+'</span><h3><a href="module-'+m[3]+'.html">'+m[0]+'</a></h3><p>'+m[1]+'</p><p class="upd">Laatst bijgewerkt: '+window.PA_DATUM(m[2])+'</p><a class="mod-link" href="toets.html#'+m[3]+'">Doe de toets →</a>';grid.appendChild(d);});

  /* Beroepskwalificaties met de modules waaruit ze bestaan. Bron: CDFD (adviesbevoegdheden), geraadpleegd oktober 2026.
     'controle': de volledige samenstelling stond niet in de bron; de check toont alleen de eigen module en verwijst naar het CDFD. */
  var KWAL=[
    {naam:'Adviseur Hypothecair krediet',mods:['basis','vermogen','hypothecair-krediet']},
    {naam:'Adviseur Vermogen',mods:['basis','vermogen']},
    {naam:'Adviseur Pensioen',mods:['basis','vermogen','pensioen']},
    {naam:'Adviseur Consumptief krediet',mods:['basis','consumptief-krediet']},
    {naam:'Adviseur Schadeverzekering zakelijk',mods:['basis','schade-particulier','schade-zakelijk']},
    {naam:'Adviseur Schadeverzekering particulier',mods:['schade-particulier'],controle:true},
    {naam:'Adviseur Inkomen',mods:['inkomen'],controle:true},
    {naam:'Adviseur Zorgverzekering',mods:['zorgverzekering'],controle:true}
  ];
  var sel=[0];
  var chips=document.getElementById('chips');
  if(!chips) return;
  KWAL.forEach(function(k,i){var b=document.createElement('button');b.type='button';b.className='chip';b.textContent=k.naam;b.addEventListener('click',function(){var j=sel.indexOf(i);j>-1?sel.splice(j,1):sel.push(i);render();});chips.appendChild(b);});
  var segs=document.getElementById('segs'),circles=MODS.map(function(_,i){var c=document.createElementNS(NS,'circle');c.setAttribute('cx',60);c.setAttribute('cy',60);c.setAttribute('r',48);c.setAttribute('fill','none');c.setAttribute('stroke-width',14);c.setAttribute('stroke-dasharray','28.5 273.09');c.setAttribute('stroke-dashoffset',-(i*33.51));segs.appendChild(c);return c;});
  function render(){
    var ids={};sel.forEach(function(i){KWAL[i].mods.forEach(function(m){ids[m]=1;});});
    var chosen=MODS.filter(function(m){return ids[m[3]];});
    var controle=sel.some(function(i){return KWAL[i].controle;});
    circles.forEach(function(c,i){c.setAttribute('stroke',ids[MODS[i][3]]?(i===0?'#0b3d73':'#1462ad'):'#d6e3f2');});
    [].forEach.call(chips.children,function(b,i){b.setAttribute('aria-pressed',sel.indexOf(i)>-1);});
    document.getElementById('count').textContent=chosen.length;
    document.getElementById('countLabel').textContent=chosen.length===1?'1 module':chosen.length+' modules';
    var start=document.getElementById('startToets');
    if(start){start.hidden=!chosen.length;if(chosen.length)start.href='toets.html#'+(chosen.length>1?'mix='+chosen.map(function(m){return m[3];}).join(','):chosen[0][3]);}
    document.getElementById('chosen').innerHTML=chosen.length?chosen.map(function(m){return '<li>Wft '+m[0]+'</li>';}).join(''):'<li>Kies een of meer beroepskwalificaties</li>';
    var n=document.getElementById('checkNoot');
    if(n)n.innerHTML=controle?'Van deze kwalificatie toont de check alleen de eigen module. Controleer de volledige samenstelling bij de <a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">adviesbevoegdheden van het CDFD</a>.':'';
  }
  render();
})();
