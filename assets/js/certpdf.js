/* Certificaat als pdf (jsPDF, lokaal in assets/js/vendor) en als mailconcept met pdf-bijlage.
   Alles gebeurt in de browser: er gaat niets naar een server. */
(function(){
  var BLAUW = [14, 90, 167], INKT = [44, 58, 71], GRIJS = [74, 74, 74], VLAK = [237, 243, 250], LIJN = [187, 211, 234];
  var SITE = 'https://pa-wft.nl/';

  // Stempel (SVG) via een canvas omzetten naar een png, licht gedraaid zoals op het certificaat
  function stempelPng(svg){
    return new Promise(function(klaar){
      var img = new Image();
      img.onload = function(){
        var c = document.createElement('canvas'); c.width = c.height = 300;
        var x = c.getContext('2d'); x.globalAlpha = .88; x.translate(150, 150); x.rotate(-12 * Math.PI / 180); x.drawImage(img, -142, -142, 284, 284);
        try{ klaar(c.toDataURL('image/png')); }catch(e){ klaar(null); }
      };
      img.onerror = function(){ klaar(null); };
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" '));
    });
  }

  function maak(r, g, logo, stempelSvg, advies, disclaimer){
    return stempelPng(stempelSvg).then(function(stempel){
      var doc = new window.jspdf.jsPDF({unit:'mm', format:'a4'});
      var W = 210, L = 22, R = W - 22, y;
      doc.setProperties({title:'Certificaat PA-toets ' + r.nummer + ' — ' + g.naam, author:'DFO BV — Wft Permanent Actueel', subject:'PA-toets', creator:'PA-WFT.nl'});
      // kader
      doc.setDrawColor.apply(doc, BLAUW); doc.setLineWidth(1.1); doc.rect(10, 10, W - 20, 277);
      doc.setLineWidth(.35); doc.rect(13.5, 13.5, W - 27, 270);
      // kop: logo links, nummer, datum en website rechts
      if(logo && logo.indexOf('data:image/png') === 0) doc.addImage(logo, 'PNG', L, 22, 56, 13.2, 'logo', 'FAST');
      doc.setFont('helvetica', 'normal'); doc.setFontSize(9); doc.setTextColor.apply(doc, GRIJS);
      doc.text('Certificaatnummer', R, 24, {align:'right'});
      doc.setFont('helvetica', 'bold'); doc.setTextColor.apply(doc, INKT); doc.text(r.nummer, R, 28.5, {align:'right'});
      doc.setFont('helvetica', 'normal'); doc.setTextColor.apply(doc, GRIJS); doc.text(r.datum, R, 33, {align:'right'});
      doc.setTextColor.apply(doc, BLAUW); doc.setFont('helvetica', 'bold'); doc.textWithLink('PA-WFT.nl', R - doc.getTextWidth('PA-WFT.nl'), 37.5, {url:SITE});
      // titel
      y = 58;
      doc.setFont('helvetica', 'bold'); doc.setFontSize(30); doc.setTextColor.apply(doc, BLAUW); doc.text('Certificaat', L, y);
      doc.setFont('helvetica', 'normal'); doc.setFontSize(9.5); doc.setTextColor.apply(doc, GRIJS); doc.setCharSpace(1.1); doc.text('PA-TOETS · WFT PERMANENT ACTUEEL', L, y + 7); doc.setCharSpace(0);
      y += 22;
      doc.setFontSize(11.5); doc.setTextColor.apply(doc, INKT); doc.text('Hierbij verklaart DFO BV dat', L, y);
      y += 11; doc.setFont('helvetica', 'bold'); doc.setFontSize(24); doc.text(doc.splitTextToSize(g.naam, R - L)[0], L, y);
      doc.setDrawColor.apply(doc, LIJN); doc.setLineWidth(.6); doc.line(L, y + 3, L + 110, y + 3);
      // persoonsgegevens
      y += 11; doc.setFontSize(9.5);
      var rij = function(label, waarde){ doc.setFont('helvetica', 'normal'); doc.setTextColor.apply(doc, GRIJS); doc.text(label, L, y); doc.setFont('helvetica', 'bold'); doc.setTextColor.apply(doc, INKT); var t = doc.splitTextToSize(waarde, R - L - 34); doc.text(t, L + 34, y); y += 4.8 * t.length; };
      rij('Geboortedatum', PA_DATUM(g.geb));
      if(g.mail) rij('E-mailadres', g.mail);
      if(g.bedrijf) rij('Bedrijf', g.bedrijf);
      rij(g.verstuurd ? 'Verstuurd op' : 'Aangemaakt op', g.uitgegeven);
      y += 5; doc.setFont('helvetica', 'normal'); doc.setFontSize(11.5); doc.setTextColor.apply(doc, INKT); doc.text('de PA-toets heeft afgelegd met het volgende resultaat:', L, y);
      // tegels
      y += 5;
      var tegels = [[r.goed + ' / ' + r.n, 'vragen goed'], [r.pct + '%', 'score'], [r.modules.length > 1 ? (r.thema.indexOf('Mijn pakket') === 0 ? 'Mijn pakket' : r.thema) : r.thema, r.modules.length > 1 ? 'modules' : 'module'], [r.bijgewerkt, 'vragenbank bijgewerkt']], x = L;
      tegels.forEach(function(t){
        doc.setFont('helvetica', 'bold'); doc.setFontSize(14); var tekst = doc.splitTextToSize(t[0], 70)[0];
        var bw = Math.max(doc.getTextWidth(tekst), 22) + 9;
        if(x + bw > R){ x = L; y += 19; }
        doc.setFillColor.apply(doc, VLAK); doc.rect(x, y, bw, 16, 'F');
        doc.setTextColor.apply(doc, BLAUW); doc.text(tekst, x + 4.5, y + 7.2);
        doc.setFont('helvetica', 'normal'); doc.setFontSize(8.5); doc.setTextColor.apply(doc, INKT); doc.text(t[1], x + 4.5, y + 12.6);
        x += bw + 4;
      });
      y += 24;
      if(r.modules.length > 1){ doc.setFontSize(9.5); rij('Modules', r.modules.join(', ')); rij('Vragen uit', r.vanMods.join(', ')); y += 3; }
      // advies met link
      doc.setFontSize(9.5); doc.setFont('helvetica', 'normal');
      var at = doc.splitTextToSize(advies + ' Doe de toets opnieuw op pa-wft.nl/toets.html.', R - L - 10);
      doc.setFillColor.apply(doc, VLAK); doc.rect(L, y, R - L, 6 + 4.6 * at.length, 'F');
      doc.setFillColor.apply(doc, BLAUW); doc.rect(L, y, 1.2, 6 + 4.6 * at.length, 'F');
      doc.setTextColor.apply(doc, INKT); doc.text(at, L + 5, y + 5.2);
      doc.link(L, y, R - L, 6 + 4.6 * at.length, {url:SITE + 'toets.html'});
      // voet: disclaimer en stempel
      doc.setFontSize(7.8); doc.setTextColor.apply(doc, GRIJS);
      var dt = doc.splitTextToSize(disclaimer, 112); doc.text(dt, L, 262 - 3.4 * dt.length);
      doc.setTextColor.apply(doc, BLAUW); doc.setFont('helvetica', 'bold'); doc.textWithLink('PA-WFT.nl — ' + SITE, L, 267, {url:SITE});
      if(stempel) doc.addImage(stempel, 'PNG', R - 44, 224, 44, 44, 'stempel', 'FAST');
      return doc;
    });
  }

  function b64utf8(t){ return btoa(unescape(encodeURIComponent(t))).replace(/.{76}/g, '$&\r\n'); }
  function kopUtf8(t){ return '=?UTF-8?B?' + btoa(unescape(encodeURIComponent(t))) + '?='; }

  // Mailconcept (.eml) met de pdf als bijlage; X-Unsent zorgt dat Outlook het als concept opent
  function eml(doc, aan, cc, onderwerp, tekst, bestandsnaam){
    var pdf = doc.output('datauristring').split(',')[1].replace(/.{76}/g, '$&\r\n');
    var grens = 'pawft-' + Date.now().toString(36);
    return ['To: ' + aan, cc ? 'Cc: ' + cc : null, 'Subject: ' + kopUtf8(onderwerp), 'X-Unsent: 1', 'MIME-Version: 1.0',
      'Content-Type: multipart/mixed; boundary="' + grens + '"', '',
      '--' + grens, 'Content-Type: text/plain; charset=UTF-8', 'Content-Transfer-Encoding: base64', '', b64utf8(tekst), '',
      '--' + grens, 'Content-Type: application/pdf; name="' + bestandsnaam + '"', 'Content-Transfer-Encoding: base64',
      'Content-Disposition: attachment; filename="' + bestandsnaam + '"', '', pdf, '', '--' + grens + '--', ''].filter(function(l){ return l !== null; }).join('\r\n');
  }

  function download(inhoud, naam, type){
    var blob = inhoud instanceof Blob ? inhoud : new Blob([inhoud], {type:type});
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = naam;
    document.body.appendChild(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  window.PA_PDF = {maak:maak, eml:eml, download:download};
})();
