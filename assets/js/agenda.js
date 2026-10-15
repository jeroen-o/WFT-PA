/* Agendaherinnering: elk kwartaal de PA-toets, 5 jaar lang (20 keer), met een link naar de toets.
   Gebruik: <div data-agenda></div>; window.PA_AGENDA(element) vult een element ook later (de toets). */
(function(){
  var URL_TOETS = 'https://pa-wft.nl/toets.html';
  var TITEL = 'PA-toets Wft Permanent Actueel';
  var KEER = 20; // elk kwartaal, 5 jaar lang
  var REGEL = 'RRULE:FREQ=MONTHLY;INTERVAL=3;COUNT=' + KEER;
  var TEKST = 'Doe de PA-toets, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het in bij je werkgever. ' + URL_TOETS;

  function pad(n){ return String(n).padStart(2, '0'); }
  function dag(d){ return d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()); }
  // Eerste afspraak over drie maanden; daarna elke drie maanden
  // Dag maximaal 28, zodat elke maand die dag heeft en er geen kwartaal wordt overgeslagen
  function eerste(){ var d = new Date(); d.setDate(Math.min(d.getDate(), 28)); d.setMonth(d.getMonth() + 3); return d; }

  function ics(){
    var s = eerste(), e = new Date(s); e.setDate(e.getDate() + 1);
    var nu = new Date(), stamp = nu.getUTCFullYear() + pad(nu.getUTCMonth() + 1) + pad(nu.getUTCDate()) + 'T' + pad(nu.getUTCHours()) + pad(nu.getUTCMinutes()) + '00Z';
    var regels = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//DFO BV//PA-WFT.nl//NL', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT', 'UID:pa-toets-' + stamp + '@pa-wft.nl', 'DTSTAMP:' + stamp,
      'DTSTART;VALUE=DATE:' + dag(s), 'DTEND;VALUE=DATE:' + dag(e), REGEL,
      'SUMMARY:' + TITEL, 'DESCRIPTION:' + TEKST.replace(/,/g, '\\,'), 'URL:' + URL_TOETS, 'TRANSP:TRANSPARENT',
      'BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + TITEL, 'TRIGGER:PT9H', 'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR'];
    return regels.join('\r\n') + '\r\n';
  }
  function google(){
    var s = eerste(), e = new Date(s); e.setDate(e.getDate() + 1);
    return 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + encodeURIComponent(TITEL)
      + '&dates=' + dag(s) + '/' + dag(e) + '&details=' + encodeURIComponent(TEKST)
      + '&recur=' + encodeURIComponent(REGEL);
  }

  window.PA_AGENDA = function(doel){
    doel.className = (doel.className ? doel.className + ' ' : '') + 'agenda';
    doel.innerHTML = '';
    var p = document.createElement('p');
    p.textContent = 'Zet een herinnering in je agenda: elk kwartaal, de komende 5 jaar, met een link naar de toets.';
    var a1 = document.createElement('a');
    a1.className = 'btn ghost'; a1.href = 'data:text/calendar;charset=utf-8,' + encodeURIComponent(ics());
    a1.download = 'pa-toets-elk-kwartaal.ics'; a1.textContent = 'Zet in mijn agenda (Outlook, Apple)';
    var a2 = document.createElement('a');
    a2.className = 'btn ghost'; a2.href = google(); a2.target = '_blank'; a2.rel = 'noopener'; a2.textContent = 'Google Agenda';
    var rij = document.createElement('div'); rij.className = 'acties'; rij.append(a1, a2);
    doel.append(p, rij);
  };
  document.querySelectorAll('[data-agenda]').forEach(function(el){ window.PA_AGENDA(el); });
})();
