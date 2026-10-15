(function(){
  var MODS=window.PA_MODULES.map(function(m){return [m.naam,m.tekst,m.bijgewerkt,m.id];});
  var NS='http://www.w3.org/2000/svg', sel=[5];
  var grid=document.getElementById('moduleGrid');
  MODS.forEach(function(m,i){var d=document.createElement('article');d.className='module';d.innerHTML='<span class="nr">'+String(i+1).padStart(2,'0')+'</span><h3>'+m[0]+'</h3><p>'+m[1]+'</p><p class="upd">Laatst bijgewerkt: '+window.PA_DATUM(m[2])+'</p><a class="mod-link" href="toets.html#'+m[3]+'">Doe de toets →</a>';grid.appendChild(d);});
  var chips=document.getElementById('chips');
  MODS.slice(1).forEach(function(m,j){var b=document.createElement('button');b.type='button';b.className='chip';b.textContent=m[0];b.dataset.i=j+1;b.addEventListener('click',function(){var i=+b.dataset.i,k=sel.indexOf(i);k>-1?sel.splice(k,1):sel.push(i);render();});chips.appendChild(b);});
  var segs=document.getElementById('segs'),circles=MODS.map(function(_,i){var c=document.createElementNS(NS,'circle');c.setAttribute('cx',60);c.setAttribute('cy',60);c.setAttribute('r',48);c.setAttribute('fill','none');c.setAttribute('stroke-width',14);c.setAttribute('stroke-dasharray','28.5 273.09');c.setAttribute('stroke-dashoffset',-(i*33.51));segs.appendChild(c);return c;});
  function render(){
    var on=function(i){return i===0||sel.indexOf(i)>-1;};
    circles.forEach(function(c,i){c.setAttribute('stroke',i===0?'#0b3d73':on(i)?'#1462ad':'#d6e3f2');});
    [].forEach.call(chips.children,function(b){b.setAttribute('aria-pressed',sel.indexOf(+b.dataset.i)>-1);});
    var chosen=MODS.filter(function(_,i){return on(i);});
    document.getElementById('count').textContent=chosen.length;
    document.getElementById('countLabel').textContent=chosen.length===1?'1 module':chosen.length+' modules';
    document.getElementById('chosen').innerHTML=chosen.map(function(m){return '<li>Wft '+m[0]+'</li>';}).join('');
  }
  render();
})();
