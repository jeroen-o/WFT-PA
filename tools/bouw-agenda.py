# -*- coding: utf-8 -*-
"""DFO-agenda (dfo-agenda.html) en partnerlogo's. Data: tools/dfo-agenda.json (overgenomen van https://www.dfobv.nl/agenda/).
Wordt via exec geladen door tools/bouw-paginas.py (zelfde namespace). Verlopen activiteiten worden in de browser verborgen (assets/js/dfo-agenda.js)."""
import datetime
AGENDA = json.load(open(R + 'tools/dfo-agenda.json', encoding='utf-8'))
AGENDA.sort(key=lambda e: (e['datum'], e['start']))
DAGEN = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']
AGENDA_BRON = 'https://www.dfobv.nl/agenda/'
AGENDA_STAND = '2026-10-22'

def ag_rij(e):
    d = datetime.date.fromisoformat(e['datum'])
    plaats = 'Online' if e['locatie'].upper() == 'ONLINE' else e['locatie']
    return (f'<li class="ag-item" data-datum="{e["datum"]}"><div class="ag-datum"><span class="ag-dag">{d.day}</span><span class="ag-mnd">{MAANDEN[d.month-1][:3]}</span></div>'
            f'<div class="ag-info"><a href="{AGENDA_BRON}" target="_blank" rel="noopener">{html.escape(e["titel"])}</a>'
            f'<span class="ag-meta">{DAGEN[d.weekday()]} {nl(e["datum"])} · {e["start"]}–{e["eind"]} · {html.escape(plaats)}</span></div></li>\n')

def ag_lijst(evs):
    return '<ul class="ag-lijst">\n' + ''.join(ag_rij(e) for e in evs) + '</ul>\n'

inh = ('    <p class="lead">Trainingen, workshops, webinars en opleidingen van DFO voor medewerkers van financiële advieskantoren. Meld je aan via de website van DFO.</p>\n'
       f'    <p class="meta-regel">Overgenomen van <a href="{AGENDA_BRON}" target="_blank" rel="noopener">dfobv.nl/agenda</a> · stand {nl(AGENDA_STAND)} · verlopen activiteiten verdwijnen vanzelf</p>\n'
       '    <div id="ag-wrap">\n    ' + ag_lijst(AGENDA) + '    </div>\n'
       '    <p id="ag-leeg" hidden>Er staan op dit moment geen activiteiten in de agenda. Kijk op <a href="' + AGENDA_BRON + '" target="_blank" rel="noopener">dfobv.nl/agenda</a> voor de nieuwste stand.</p>\n'
       '    <div class="acties"><a class="btn" href="' + AGENDA_BRON + '" target="_blank" rel="noopener">Aanmelden en meer informatie</a><a class="btn ghost" href="opleidingen.html">DFO Opleidingen</a></div>\n'
       '    <p class="klein">Programma, tijden en locaties kunnen wijzigen; de agenda op dfobv.nl is leidend. Vragen? Bel <a href="tel:+31332580460">033 258 04 60</a> of mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
ld_ag = {'@context': 'https://schema.org', '@graph': [{'@type': 'Event', 'name': e['titel'], 'startDate': f'{e["datum"]}T{e["start"]}:00+01:00', 'eventAttendanceMode': 'https://schema.org/OnlineEventAttendanceMode' if e['locatie'].upper() == 'ONLINE' else 'https://schema.org/OfflineEventAttendanceMode',
         'eventStatus': 'https://schema.org/EventScheduled', 'url': AGENDA_BRON, 'inLanguage': 'nl', 'organizer': {'@id': SITE + '#dfo'},
         'location': ({'@type': 'VirtualLocation', 'url': AGENDA_BRON} if e['locatie'].upper() == 'ONLINE' else {'@type': 'Place', 'name': e['locatie'], 'address': e['locatie']})} for e in AGENDA]}
BIJGEWERKT['dfo-agenda.html'] = AGENDA_STAND
pagina('dfo-agenda.html', 'Agenda DFO: trainingen, workshops en webinars voor adviseurs', 'De agenda van DFO met trainingen, workshops, webinars en opleidingen voor medewerkers van financiële advieskantoren.',
       'Agenda DFO', 'Activiteiten van DFO BV', inh, actief='opleidingen.html', ld=ld_ag, kruimel='Agenda DFO', scripts='\n<script src="assets/js/dfo-agenda.js"></script>')

# volgende activiteiten op de homepage en op DFO Opleidingen
_vol = [e for e in AGENDA if e['datum'] >= AGENDA_STAND][:4]
_blok = ('<section class="ag-home" aria-labelledby="agh-kop"><h2 id="agh-kop">Agenda DFO</h2>' + ag_lijst(_vol)
         + '<p><a href="dfo-agenda.html">De hele agenda met activiteiten →</a></p></section>\n')
for _f, _a in (('index.html', '<section class="nieuwsbrieven"'), ('opleidingen.html', '<h2')):
    _s = open(R + _f, encoding='utf-8').read()
    if 'ag-home' in _s: continue
    _i = _s.find(_a, _s.find('<main'))
    if _i > 0: open(R + _f, 'w', encoding='utf-8').write(_s[:_i] + _blok + _s[_i:])

# partners
PARTNERS = [('Blinqx Verzekering & Hypotheek', 'assets/partners/blinqx.png', 471, 160), ('Turien & Co Assuradeuren', 'assets/partners/turien.png', 409, 160), ('Lloyds', 'assets/partners/lloyds.png', 558, 160)]
_pb = ('<section class="partners" aria-labelledby="partners-kop"><h2 id="partners-kop">Partners</h2><ul class="partner-logos">'
       + ''.join(f'<li><img src="{p}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{html.escape(n)}"></li>' for n, p, w, h in PARTNERS) + '</ul></section>\n')
_s = open(R + 'index.html', encoding='utf-8').read()
if 'class="partners"' not in _s:
    _i = _s.find('<section class="nieuwsbrieven"'); open(R + 'index.html', 'w', encoding='utf-8').write(_s[:_i] + _pb + _s[_i:])
KENNIS_PAGINAS.append('dfo-agenda.html')
KENNIS_TITEL['dfo-agenda.html'] = 'Agenda DFO'
KENNIS_BESCHRIJVING['dfo-agenda.html'] = 'Trainingen, workshops, webinars en opleidingen van DFO voor adviseurs.'
