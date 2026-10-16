(function(){
  var MODS=window.PA_MODULES.map(function(m){return [m.naam,m.tekst,m.bijgewerkt,m.id];});
  var NS='http://www.w3.org/2000/svg';
  var grid=document.getElementById('moduleGrid');
  MODS.forEach(function(m,i){var d=document.createElement('article');d.className='module';d.innerHTML='<span class="nr">'+String(i+1).padStart(2,'0')+'</span><h3><a href="'+PA_PAGINA('module-'+m[3])+'">'+m[0]+'</a></h3><p>'+m[1]+'</p><p class="upd">'+PA_T('laatstBijgewerkt',window.PA_DATUM(m[2]))+'</p><a class="mod-link" href="'+PA_PAGINA('toets',m[3])+'">'+PA_T('doeToets')+'</a>';grid.appendChild(d);});

  /* Beroepskwalificaties met de benodigde diploma's. Bron: AFM, Vakbekwaamheidseisen (tabel beroep en producten), en CDFD, geraadpleegd oktober 2026. */
  var KWAL=[
    {naam:PA_T('kwal0'),mods:['basis','vermogen','hypothecair-krediet']},
    {naam:PA_T('kwal1'),mods:['basis','vermogen']},
    {naam:PA_T('kwal2'),mods:['basis','vermogen','pensioen']},
    {naam:PA_T('kwal3'),mods:['basis','consumptief-krediet']},
    {naam:PA_T('kwal4'),mods:['basis','schade-particulier','schade-zakelijk']},
    {naam:PA_T('kwal5'),mods:['basis','schade-particulier']},
    {naam:PA_T('kwal6'),mods:['basis','inkomen']},
    {naam:PA_T('kwal7'),mods:['zorgverzekering']}
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
    document.getElementById('countLabel').textContent=PA_T('modTeller',chosen.length);
    var start=document.getElementById('startToets');
    if(start){start.hidden=!chosen.length;if(chosen.length)start.href=PA_PAGINA('toets')+'#'+(chosen.length>1?'mix='+chosen.map(function(m){return m[3];}).join(','):chosen[0][3]);}
    document.getElementById('chosen').innerHTML=chosen.length?chosen.map(function(m){return '<li>Wft '+m[0]+'</li>';}).join(''):'<li>'+PA_T('kiesKwalLijst')+'</li>';
    var n=document.getElementById('checkNoot');
    if(n)n.innerHTML=controle?PA_T('checkNoot'):'';
  }
  render();
})();
