"""Bouwt de vaste onderdelen van PA-WFT.nl opnieuw: modulepagina's, veelgestelde vragen, privacy, over,
gebruiksvoorwaarden, klachten, 404, sitemap, robots en llms.txt, plus header en footer van index en toets.

Gebruik (vanuit de map van de repository):  python3 tools/bouw-paginas.py
Vereist Node.js om assets/js/modules.js te lezen.
"""
import re, html, os, json, subprocess
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SITE = 'https://pa-wft.nl/'
PEIL = '15 oktober 2026'

MARK = ('<svg viewBox="0 0 120 120" aria-hidden="true"><g transform="rotate(-87 60 60)">'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#1462ad" stroke-width="14" stroke-dasharray="28.5 5.01"/>'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#0b3d73" stroke-width="14" stroke-dasharray="28.5 273.09"/></g>'
        '<text x="60" y="72" text-anchor="middle" font-family="Archivo, Arial, sans-serif" font-weight="800" font-size="34" fill="#1462ad">PA</text></svg>')

NAV = [('toets.html', 'Kennistoets'), ('index.html#modules', 'Modules'), ('pe-punten-wft.html', 'PE uitgelegd'), ('wetgeving.html', 'Wet- en regelgeving'),
       ('compliance.html', 'DFO Compliance'), ('opleidingen.html', 'DFO Opleidingen'), ('over.html', 'DFO BV')]

def header(actief=''):
    links = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == actief else '', t) for h, t in NAV)
    return ('<a class="skip" href="#inhoud">Naar de inhoud</a>\n<div class="topbar">\n  <div class="wrap">\n'
            '    <a class="logo" href="index.html" aria-label="Wft Permanent Actueel — home"' + (' aria-current="page"' if actief == 'index.html' else '') + '><img src="assets/logo/pa-wft-logo-horizontal.png" width="144" height="60" alt="Wft Permanent Actueel — PA-WFT.nl"></a>\n'
            '    <nav class="topnav" aria-label="Hoofdmenu">' + links + '</nav>\n'
            '  </div>\n</div>')

def masthead(kicker, kop, intro='', extra='', datum=''):
    return ('<header class="masthead">\n  <div class="wrap">\n' + (f'    <p class="bijgewerkt-kop"><time datetime="{datum}" title="Laatst bijgewerkt">{nl(datum)}</time></p>\n' if datum else '') + (f'    <p class="kicker">{kicker}</p>\n' if kicker else '') + f'    <h1>{kop}</h1>\n'
            + (f'    <p class="intro">{intro}</p>\n' if intro else '') + extra + '  </div>\n</header>')

MELDING = ('<div class="melding" role="note"><strong>Let op.</strong> De PA-toets is een oefentoets en geldt niet als Wft-examen, PE-examen of PE-bewijs. '
           'DFO BV is niet verantwoordelijk voor de juistheid en volledigheid van alle vragen en antwoorden; regels wijzigen. Wil je het zeker weten? '
           'Neem contact op met <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">DFO BV</a> via <a href="tel:+31332580460">033 258 04 60</a> of <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</div>')

FOOTER = ('<footer>\n  <div class="wrap foot-grid">\n  <div class="foot-tekst">\n'
    '    <div>Wft Permanent Actueel is een activiteit van DFO BV · De Wel 14–16, 3871 MV Hoevelaken · <a href="tel:+31332580460">033 258 04 60</a> · <a href="mailto:info@dfobv.nl">info@dfobv.nl</a></div>\n'
    '    <nav class="foot-links" aria-label="Voettekst"><a href="over.html">Over en verantwoording</a><a href="gebruiksvoorwaarden.html">Gebruiksvoorwaarden</a><a href="klachten.html">Klachten</a>'
    '<a href="privacy.html">Privacy en cookies</a><a href="vragen.html">Veelgestelde vragen</a><a href="https://www.dfobv.nl/ons-team/" target="_blank" rel="noopener">Ons team</a>'
    '<a href="https://www.dfobv.nl/product/nieuwsbrief-wft/" target="_blank" rel="noopener">Nieuwsbrief Wft</a></nav>\n'
    '    <p class="foot-disc">Op de hoogte blijven? Schrijf je in voor de wekelijkse <a href="https://www.dfobv.nl/product/nieuwsbrief-wft/" target="_blank" rel="noopener">Nieuwsbrief Wft</a> van DFO. '
    'Oefentoets voor financieel adviseurs; geen erkend PE-examen en geen advies.</p>\n  </div>\n'
    '  <a class="foot-logo" href="https://www.dfobv.nl/" target="_blank" rel="noopener" aria-label="DFO BV — naar dfobv.nl"><img src="assets/logo/dfo-logo.png" width="186" height="44" alt="DFO — dienstverlening voor financiële ondernemers"></a>\n'
    '  </div>\n</footer>')

def head(titel, omschrijving, pad, extra=''):
    return ('<!doctype html>\n<html lang="nl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{html.escape(titel)}</title>\n<meta name="description" content="{html.escape(omschrijving)}">\n<meta name="theme-color" content="#1462ad">\n'
            f'<link rel="canonical" href="{SITE}{pad}">\n<link rel="icon" href="favicon.ico" sizes="any">\n<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<link rel="manifest" href="site.webmanifest">\n'
            f'<meta property="og:title" content="{html.escape(titel)}">\n<meta property="og:description" content="{html.escape(omschrijving)}">\n'
            f'<meta property="og:image" content="{SITE}og-image.png">\n<meta property="og:url" content="{SITE}{pad}">\n<meta name="twitter:card" content="summary_large_image">\n'
            '<link rel="preload" href="assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
            '<link rel="stylesheet" href="assets/css/style.css">' + extra + '\n</head>\n<body>')

def link_cdfd(html_tekst):
    kop, sep, romp = html_tekst.partition('<body')
    delen = re.split(r'(<[^>]+>)', romp)
    in_a = in_script = 0
    for i, d in enumerate(delen):
        if d.startswith('<'):
            t = d[1:].split(None, 1)[0].lower().rstrip('>') if len(d) > 2 else ''
            if t == 'a': in_a += 1
            elif t == '/a': in_a -= 1
            elif t in ('script', 'style', 'title'): in_script += 1
            elif t in ('/script', '/style', '/title'): in_script -= 1
        elif not in_a and not in_script and 'CDFD' in d:
            delen[i] = re.sub(r'\bCDFD\b', '<a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD</a>', d)
    return kop + sep + ''.join(delen)

def pagina(pad, titel, omschrijving, kop, kicker, inhoud, actief='', extra='', ld=None, intro='', scripts='', mast_extra='', datum=None, kaal=False):
    datum = datum or BIJGEWERKT.get(pad, PEIL_ISO)
    if ld: extra += '\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    if not kaal and not inhoud.lstrip().startswith('<div class="paneel'):
        inhoud = '<div class="paneel page">\n' + inhoud + '\n</div>'
    s = (head(titel, omschrijving, pad, extra) + '\n' + header(actief) + '\n' + masthead(kicker, kop, intro, mast_extra, datum)
         + ('\n<main id="inhoud" class="kaal">\n' + inhoud + '\n<div class="wrap">' + MELDING + '</div>\n</main>\n' if kaal else
            '\n<main id="inhoud">\n  <div class="wrap">\n' + inhoud + '\n' + MELDING + '\n  </div>\n</main>\n') + FOOTER + scripts + '\n</body>\n</html>\n')
    if kaal: s = s.replace('<body>', '<body class="breed">', 1)
    open(R + pad, 'w', encoding='utf-8').write(link_cdfd(s))

# ---------- Modules ----------
WT = 'https://wetten.overheid.nl/'
EU = 'https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX%3A'
B = {
 'wft': ('Wet op het financieel toezicht (Wft)', WT + 'BWBR0020368'),
 'bgfo': ('Besluit Gedragstoezicht financiële ondernemingen Wft (BGfo)', WT + 'BWBR0020421'),
 'eind': ('Regeling eindtermen en toetstermen examens financiële dienstverlening Wft', WT + 'BWBR0032957'),
 'wwft': ('Wet ter voorkoming van witwassen en financieren van terrorisme (Wwft)', WT + 'BWBR0024281'),
 'avg': ('Algemene verordening gegevensbescherming (AVG)', EU + '32016R0679'),
 'idd': ('Richtlijn verzekeringsdistributie (IDD)', EU + '32016L0097'),
 'kifid': ('Kifid-reglementen', 'https://www.kifid.nl/reglementen/'),
 'bw7': ('Burgerlijk Wetboek Boek 7 (o.a. verzekeringsovereenkomst)', WT + 'BWBR0005290'),
 'wck': ('Wet op het consumentenkrediet (WCK)', WT + 'BWBR0004815'),
 'ccd2': ('Herziene richtlijn consumentenkrediet (CCD II)', EU + '32023L2225'),
 'mifid': ('Richtlijn markten voor financiële instrumenten (MiFID II)', EU + '32014L0065'),
 'sfdr': ('Verordening duurzaamheidsinformatie (SFDR)', EU + '32019R2088'),
 'priips': ('PRIIPs-verordening', EU + '32014R1286'),
 'ib': ('Wet inkomstenbelasting 2001', WT + 'BWBR0011353'),
 'obw3': ('Overbruggingswet box 3', WT + 'BWBR0047702'),
 'sw': ('Successiewet 1956', WT + 'BWBR0002226'),
 'trhk': ('Tijdelijke regeling hypothecair krediet (TRHK)', WT + 'BWBR0032503'),
 'mcd': ('Hypothekenrichtlijn (MCD)', EU + '32014L0017'),
 'nhg': ('NHG Voorwaarden & Normen', 'https://www.nhg.nl/'),
 'wia': ('Wet werk en inkomen naar arbeidsvermogen (WIA)', WT + 'BWBR0019057'),
 'zw': ('Ziektewet', WT + 'BWBR0001888'),
 'ww': ('Werkloosheidswet', WT + 'BWBR0004045'),
 'anw': ('Algemene nabestaandenwet (Anw)', WT + 'BWBR0007795'),
 'pw': ('Pensioenwet', WT + 'BWBR0020809'),
 'wtp': ('Wet toekomst pensioenen', WT + 'BWBR0048328'),
 'aow': ('Algemene Ouderdomswet (AOW)', WT + 'BWBR0002221'),
 'wvps': ('Wet verevening pensioenrechten bij scheiding', WT + 'BWBR0006641'),
 'zvw': ('Zorgverzekeringswet', WT + 'BWBR0018450'),
 'zt': ('Wet op de zorgtoeslag', WT + 'BWBR0018451'),
 'awir': ('Algemene wet inkomensafhankelijke regelingen (AWIR)', WT + 'BWBR0018472'),
 'amlr': ('EU-witwasverordening (AMLR)', EU + '32024R1624'),
 'ai': ('AI-verordening', EU + '32024R1689'),
 'dora': ('Digital Operational Resilience Act (DORA)', EU + '32022R2554'),
}
M = {
 'basis': dict(
   onderwerpen=['Wft-kader en toezicht door AFM en DNB', 'Vergunningplicht en vrijstellingen', 'Vakbekwaamheid en permanente educatie', 'Zorgplicht en klantbelang centraal',
                'Informatieverstrekking en het dienstverleningsdocument', 'Beloning, provisieverbod en belangenconflicten', 'Kifid en klachtafhandeling',
                'Wwft: cliëntenonderzoek en melden', 'AVG en integriteit, eed of belofte', 'Financiële basisbegrippen, consumentenrecht en sociale zekerheid op hoofdlijnen', 'Duurzaamheidsvoorkeuren'],
   actueel=['<strong>EU-witwaspakket (AMLR en AMLD6).</strong> Komt boven op de huidige Wwft; de Wwft wordt op termijn vervangen door een implementatiewet. De poortwachtersrol van adviseurs verandert mee.',
            '<strong>AI-verordening en DORA.</strong> Gefaseerde toepassing raakt advieskantoren via software, modellen en uitbesteding.'],
   bronnen=['wft', 'bgfo', 'eind', 'wwft', 'amlr', 'avg', 'idd', 'kifid', 'ai']),
 'consumptief-krediet': dict(
   onderwerpen=['Soorten krediet: doorlopend krediet, persoonlijke lening, private lease, BNPL, roodstand', 'Kredietwaardigheidstoets, leennormen en BKR-registratie',
                'Informatie: Europese standaardinformatie en JKP', 'Herroepingsrecht, vervroegd aflossen en opzeggen', 'Maximale kredietvergoeding (principe)',
                'Wft- en Wck-kader', 'Schuldhulp en betalingsproblemen', 'Zorgplicht, provisie en oversluiten', 'Wwft en AVG bij krediet'],
   actueel=['<strong>CCD II per 20 november 2026.</strong> De herziene richtlijn consumentenkrediet gaat gelden; de Nederlandse implementatiewet is nog in voorbereiding. Onder meer BNPL en huur of lease met koopoptie komen onder het kredietregime.'],
   bronnen=['wft', 'bgfo', 'wck', 'ccd2', 'wwft', 'avg']),
 'schade-particulier': dict(
   onderwerpen=['Verzekeringsrecht: mededelingsplicht, premie, schadevergoeding, onderverzekering, verjaring', 'Motorrijtuigen: WAM, WA, casco, bonus-malus',
                'Woonhuis en inboedel: herbouwwaarde, nieuwwaarde, gevaren en uitsluitingen', 'Aansprakelijkheid particulieren (AVP)', 'Rechtsbijstand, reis en annulering',
                'Schadebehandeling en expertise', 'Terrorismerisico, natuurrampen en overstroming', 'Zorgplicht, IDD en Kifid'],
   actueel=['<strong>Geen grote wetswijziging gesignaleerd.</strong> Het kader blijft Boek 7 BW (verzekeringsovereenkomst), de IDD en de Wft-gedragsregels. Polisvoorwaarden verschillen per verzekeraar; toets altijd de actuele voorwaarden.'],
   bronnen=['bw7', 'wft', 'bgfo', 'idd', 'kifid', 'avg']),
 'schade-zakelijk': dict(
   onderwerpen=['Zakelijke risico-inventarisatie', 'Brand, opstal, inventaris en goederen', 'Bedrijfsschade en uitkeringstermijn', 'Aansprakelijkheid: AVB, product, werkgever, beroep',
                'Bestuurdersaansprakelijkheid (D&amp;O) en CAR', 'Transport, wagenpark en cyber', 'Collectieve contracten, volmachten, beurspolissen en coassurantie',
                'Verzekeringsrecht: mededelingsplicht, eerste en tweede risico', 'IDD, Wwft en sanctiewetgeving'],
   actueel=['<strong>AI-verordening en DORA.</strong> Raken zakelijke klanten en hun verzekeringsbehoefte, onder meer bij cyber- en IT-risico’s.',
            '<strong>Sanctiewetgeving.</strong> Blijft een vast aandachtspunt bij zakelijke klanten en buitenlandse belangen.'],
   bronnen=['bw7', 'wft', 'bgfo', 'idd', 'wwft', 'dora', 'ai']),
 'vermogen': dict(
   onderwerpen=['Vermogensopbouw en financiële planning', 'Sparen en het depositogarantiestelsel', 'Beleggen: aandelen, obligaties, fondsen, risico en spreiding',
                'Beleggingsverzekeringen, banksparen en lijfrente', 'Box 3 op hoofdlijnen', 'Schenken en erven', 'MiFID II: geschiktheid, klantclassificatie, kostentransparantie',
                'PRIIPs en essentiële-informatiedocument', 'SFDR en duurzaamheidsvoorkeuren', 'Zorgplicht en beleggersprofiel'],
   actueel=['<strong>Box 3.</strong> De Overbruggingswet box 3 geldt tot een nieuw stelsel in werking treedt; daarnaast loopt het rechtsherstel na het Kerstarrest. Werk met de regels van het betreffende belastingjaar.'],
   bronnen=['wft', 'bgfo', 'mifid', 'priips', 'sfdr', 'ib', 'obw3', 'sw', 'wwft']),
 'hypothecair-krediet': dict(
   onderwerpen=['Leennormen: financieringslast en verhouding lening-waarde', 'Hypotheekvormen en rentevormen', 'Eigenwoningregeling: aflossingseis, bijleenregeling, eigenwoningreserve',
                'Nationale Hypotheek Garantie', 'Taxatie, notaris en hypotheekakte', 'Vergoeding bij vervroegd aflossen', 'ESIS en informatieverstrekking',
                'Inkomen en kredietwaardigheid', 'Risico’s in het advies: overlijden, arbeidsongeschiktheid, werkloosheid, relatie-einde, pensioen', 'Duurzaamheid en energielabel'],
   actueel=['<strong>TRHK en NHG Voorwaarden &amp; Normen.</strong> Wijzigen jaarlijks per 1 januari. Werk altijd met de jaarversie.',
            '<strong>Hypotheekacceptatie 2026.</strong> De NHG-kostengrens is € 470.000. Meerdere geldverstrekkers beperken het aflossingsvrije deel bij nieuwe aanvragen tot 30% van de woningwaarde, en taxatierapporten moeten ingaan op funderingsrisico. Check de actuele criteria per geldverstrekker.'],
   bronnen=['trhk', 'mcd', 'nhg', 'wft', 'bgfo', 'ib', 'wwft']),
 'inkomen': dict(
   onderwerpen=['Loondoorbetaling bij ziekte en de Wet verbetering poortwachter', 'Ziektewet, WIA (WGA en IVA) en Wajong', 'WW en Anw op hoofdlijnen',
                'Arbeidsongeschiktheidsverzekering voor zelfstandigen', 'WGA-hiaat, WIA-excedent en verzuimverzekering', 'Woonlastenverzekering en overlijdensrisicoverzekering',
                'Fiscale behandeling van premies en uitkeringen', 'Inkomensanalyse en zorgplicht', 'AVG en gezondheidsgegevens'],
   actueel=['<strong>Arbeidsongeschiktheidsverzekering voor zelfstandigen.</strong> Een verplichte basisverzekering is in voorbereiding. Volg de stand van het wetsvoorstel; de huidige regels blijven gelden tot invoering.'],
   bronnen=['wia', 'zw', 'ww', 'anw', 'wft', 'bgfo', 'idd', 'avg']),
 'pensioen': dict(
   onderwerpen=['De drie pijlers en de AOW', 'Pensioenwet: pensioenovereenkomst, uitvoerders, informatie en waardeoverdracht', 'Wet toekomst pensioenen: premieregelingen, transitie en invaren',
                'Partner- en wezenpensioen, Anw-hiaat', 'Fiscaal kader (Witteveen) en lijfrente', 'Pensioen bij scheiding', 'Dga-pensioen en pensioen in eigen beheer', 'Zorgplicht en advies bij keuzes'],
   actueel=['<strong>Wet toekomst pensioenen.</strong> Pensioenregelingen moeten uiterlijk op 1 januari 2028 zijn overgegaan naar het nieuwe stelsel. Let op transitiemomenten, nabestaandendekking en communicatie aan deelnemers.'],
   bronnen=['pw', 'wtp', 'aow', 'anw', 'wvps', 'ib', 'wft', 'idd']),
 'zorgverzekering': dict(
   onderwerpen=['Zorgverzekeringswet: verzekeringsplicht, acceptatieplicht, verbod op premiedifferentiatie', 'Basispakket en eigen risico', 'Polisvormen: natura, restitutie, combinatie, budget',
                'Overstappen en aanvullende verzekeringen', 'Inkomensafhankelijke bijdrage en zorgtoeslag', 'Wlz en Wmo naast de Zvw', 'Zorg in het buitenland', 'Wanbetalersregeling en geschillen', 'AVG en informatieverstrekking'],
   actueel=['<strong>Jaarlijkse wijzigingen per 1 januari.</strong> Premies, het verplicht eigen risico, het basispakket en de zorgtoeslag worden elk jaar opnieuw vastgesteld. Gebruik de bedragen van het betreffende jaar.'],
   bronnen=['zvw', 'zt', 'awir', 'wft', 'bgfo', 'idd', 'avg']),
}

# lees modulegegevens uit modules.js
MODS = json.loads(subprocess.check_output(['node', '-e', "global.window={};eval(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(JSON.stringify(window.PA_MODULES))", R + 'assets/js/modules.js']))
PEIL_ISO = '2026-10-15'
BIJGEWERKT = {}
MAANDEN = ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december']
def nl(iso): j, m, d = iso.split('-'); return f'{int(d)} {MAANDEN[int(m)-1]} {j}'

LAATSTE = max(m['bijgewerkt'] for m in MODS)
BIJGEWERKT.update({'index.html': LAATSTE, 'toets.html': LAATSTE})
for i, mod in enumerate(MODS, 1):
    BIJGEWERKT[f"module-{mod['id']}.html"] = mod['bijgewerkt']
    mid, naam, bij, tekst = mod['id'], mod['naam'], mod['bijgewerkt'], mod['tekst']
    d = M[mid]
    inh = (f'    <p class="lead">{html.escape(tekst)} Oefen gratis met PE-oefenvragen voor Wft {html.escape(naam)}, met uitleg bij elk antwoord.</p>\n'
           f'    <p class="meta-regel">Laatst bijgewerkt {nl(bij)} · peildatum regelgeving {PEIL}</p>\n'
           f'    <div class="acties"><a class="btn" href="toets.html#{mid}">Doe de toets</a><a class="btn ghost" href="index.html#modules">Alle modules</a></div>\n'
           '    <h2>Wat komt aan bod</h2>\n    <ul>' + ''.join(f'<li>{o}</li>' for o in d['onderwerpen']) + '</ul>\n'
           '    <h2>Actueel</h2>\n    <ul>' + ''.join(f'<li>{a}</li>' for a in d['actueel']) + '</ul>\n'
           '    <h2>Wijzigingen</h2>\n    <ul class="log">' + ''.join(f'<li><strong>{nl(dt)}</strong> — {html.escape(t)}</li>' for dt, t in mod['log']) + '</ul>\n'
           '    <h2>Bronnen</h2>\n    <ul class="bronnen">' + ''.join(f'<li><a href="{B[b][1]}" target="_blank" rel="noopener">{B[b][0]}</a></li>' for b in d['bronnen']) + '</ul>\n'
           f'    <p class="klein">Dit overzicht helpt je je kennis bij te houden en is geen leerstof voor een erkend PE-examen. Controleer bedragen en normen altijd in de geldende bron. Zie je een fout? Mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Course', 'name': f'Wft {naam} — Permanent Actueel', 'description': f'Gratis PE-oefenvragen Wft {naam}: meerkeuzevragen met uitleg, een toets van 7 vragen en een certificaat. {tekst}',
         'url': f'{SITE}module-{mid}.html', 'inLanguage': 'nl', 'isAccessibleForFree': True, 'educationalLevel': 'Beroepsniveau', 'teaches': d['onderwerpen'][:6],
         'dateModified': bij, 'provider': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'},
         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR', 'category': 'Gratis'},
         'hasCourseInstance': {'@type': 'CourseInstance', 'courseMode': 'online', 'courseWorkload': 'PT10M'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Wft Permanent Actueel', 'item': SITE},
                                                        {'@type': 'ListItem', 'position': 2, 'name': f'Wft {naam}', 'item': f'{SITE}module-{mid}.html'}]}]}
    titel = f'Wft {naam}: gratis PE-oefenvragen | Permanent Actueel'
    if len(titel) > 62: titel = f'Wft {naam}: gratis PE-oefenvragen'
    pagina(f'module-{mid}.html', titel, f'Wft {naam} Permanent Actueel: gratis PE-oefenvragen met uitleg, wat er actueel is en de bronnen. Oefentoets voor adviseurs, geen PE-examen.',
           f'Wft {html.escape(naam)}', f'Module {i:02d} · Permanent Actueel', inh, ld=ld)

# ---------- Veelgestelde vragen ----------
FAQ = [
 ('Wat is permanente educatie (PE)?', 'Wie in de financiële dienstverlening adviseert, moet vakbekwaam zijn en blijven. Daarvoor heb je een Wft-diploma nodig en houd je je kennis bij met permanente educatie. Binnen elke PE-periode haal je één PE-examen per beroepskwalificatie; de lopende periode loopt van 1 april 2025 tot en met 31 maart 2028. De actuele periode en eisen vind je bij het <a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD</a>.'),
 ('Telt deze toets mee voor mijn PE?', 'Nee. De PA-toets is een oefentoets. Hij helpt je je kennis te testen en bij te houden, maar is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid. Je PE-examen leg je af bij een door het CDFD erkend examencentrum.'),
 ('Levert de toets PE-punten op?', 'Nee. Onder de Wft bestaan geen PE-punten meer: je houdt je diploma’s geldig met PE-examens. De PA-toets is een gratis oefentoets en levert geen PE-punten of PE-examen op. Lees meer in <a href="pe-punten-wft.html">PE-punten en Wft Permanent Actueel</a>.'),
 ('Wat kost het?', 'Niets. Alle modules en de toets zijn gratis voor alle adviseurs, zonder abonnement en zonder account. Wft Permanent Actueel is een activiteit van DFO BV.'),
 ('Hoe werkt de toets?', 'Je kiest een module en krijgt 7 willekeurige vragen. Na elk antwoord zie je de uitleg. Daarna maak je een certificaat met je resultaat, dat je naar jezelf mailt of print. Je kunt de toets zo vaak doen als je wilt; je krijgt steeds andere vragen.'),
 ('Hoe vaak doe ik de toets?', 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Op de homepage en in de toets zet je met één klik een herinnering in je agenda: elk kwartaal, de komende 5 jaar, met een link naar de toets. Bewaar elk certificaat in je personeelsdossier en lever het ook in bij je werkgever. Zo laat je zien dat je je kennis bijhoudt. Het certificaat vervangt je PE-examen niet.'),
 ('Wat staat er op het certificaat?', 'Je naam, de module, je resultaat, de datum, de datum waarop de vragen van die module voor het laatst zijn bijgewerkt en een certificaatnummer. Het certificaat wordt nergens centraal geregistreerd.'),
 ('Wordt er iets van mij bewaard?', 'Nee. Je naam en e-mailadres blijven in je eigen browser en worden alleen gebruikt om het certificaat te maken. Mailen gaat via je eigen mailprogramma. Zie de <a href="privacy.html">privacyverklaring</a>.'),
 ('Welke modules heb ik nodig?', 'Dat hangt af van je diploma’s en het soort klantcontact. Gebruik de <a href="index.html#check">pakketcheck</a> op de homepage als hulpmiddel. Voor de precieze eisen die voor jou gelden, kijk je bij het CDFD of de AFM.'),
 ('Hoe actueel zijn de vragen?', 'Per module zie je wanneer de vragen voor het laatst zijn bijgewerkt. De peildatum van de regelgeving is ' + PEIL + '. Bedragen en percentages die elk jaar wijzigen, zitten bewust niet in de vragen.'),
 ('Ik zie een fout in een vraag. Wat nu?', 'Graag horen we het. Mail de vraag en wat er volgens jou niet klopt naar <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.'),
]
inh = '\n'.join(f'    <details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)
ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}
pagina('vragen.html', 'Veelgestelde vragen — Wft Permanent Actueel', 'Antwoorden op vragen over de gratis PA-toets, permanente educatie en het certificaat.',
       'Veelgestelde vragen', 'Vragen', inh, actief='vragen.html', ld=ld)

# ---------- Privacy ----------
inh = f'''    <p class="lead">Wft Permanent Actueel verzamelt en bewaart geen persoonsgegevens.</p>
    <h2>Wie is verantwoordelijk</h2>
    <p>DFO BV, De Wel 14–16, 3871 MV Hoevelaken. Vragen over privacy: <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>
    <h2>De toets en het certificaat</h2>
    <p>Voor het certificaat vul je je naam, geboortedatum en e-mailadres in, en desgewenst het bedrijf waar je werkt. Die gegevens blijven in je eigen browser en worden alleen gebruikt om het certificaat op je scherm te zetten. Er wordt niets naar ons verstuurd of opgeslagen. Kies je voor mailen, dan opent je eigen mailprogramma; jij verstuurt het bericht zelf. Sluit je het tabblad, dan zijn de gegevens weg.</p>
    <h2>Cookies en meten</h2>
    <p>We gebruiken geen cookies, geen analyse- of advertentiediensten en geen trackers. Het lettertype staat op onze eigen site, zodat er geen gegevens naar externe partijen gaan.</p>
    <h2>Hosting</h2>
    <p>Deze site plaatst geen cookies, ook niet voor het onthouden van keuzes. De site wordt gehost via GitHub Pages (GitHub, Inc.). Zoals elke webserver verwerkt GitHub technische gegevens zoals je IP-adres om de pagina’s te kunnen leveren en te beveiligen. Zie de <a href="https://docs.github.com/nl/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">privacyverklaring van GitHub</a>.</p>
    <h2>Je rechten</h2>
    <p>Omdat we geen persoonsgegevens bewaren, is er niets in te zien, te wijzigen of te verwijderen. Heb je toch een vraag of klacht, mail dan <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>. Je kunt ook een klacht indienen bij de <a href="https://www.autoriteitpersoonsgegevens.nl/" target="_blank" rel="noopener">Autoriteit Persoonsgegevens</a>.</p>
    <p class="klein">Laatst bijgewerkt: {PEIL}.</p>'''
pagina('privacy.html', 'Privacy — Wft Permanent Actueel', 'Wft Permanent Actueel verzamelt en bewaart geen persoonsgegevens. Geen cookies, geen tracking.', 'Privacyverklaring', 'Privacy', inh)

# ---------- Over en verantwoording ----------
inh = f'''    <p class="lead">Wft Permanent Actueel is een gratis oefenomgeving voor financieel adviseurs: per Wft-module oefenvragen met uitleg, om je kennis te testen en bij te houden.</p>
    <h2>Wie zit erachter</h2>
    <p>Wft Permanent Actueel is een activiteit van DFO BV, dienstverlening voor financiële ondernemers. DFO BV, De Wel 14–16, 3871 MV Hoevelaken, telefoon <a href="tel:+31332580460">033 258 04 60</a>, e-mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>, <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">www.dfobv.nl</a>. Maak kennis met <a href="https://www.dfobv.nl/ons-team/" target="_blank" rel="noopener">ons team</a>.</p>
    <h2>Wat het wel en niet is</h2>
    <ul>
      <li>Het is een oefentoets. Het is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid.</li>
      <li>Het certificaat bevestigt je resultaat op de oefentoets en wordt niet centraal geregistreerd.</li>
      <li>De inhoud is algemene informatie en geen advies. Controleer wet- en regelgeving altijd in de geldende bron.</li>
    </ul>
    <h2>Hoe de vragen tot stand komen</h2>
    <p>De vragen zijn opgesteld met behulp van AI, op basis van openbare wet- en regelgeving en de eind- en toetstermen van de Wft-examens. Peildatum: {PEIL}. Bedragen en percentages die elk jaar wijzigen, zitten bewust niet in de vragen; de toets gaat over principes en vaste begrippen. Per module staat de datum waarop de vragen voor het laatst zijn bijgewerkt.</p>
    <h2>Fout gezien?</h2>
    <p>Mail de vraag en wat er volgens jou niet klopt naar <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>. We passen de vraag aan en werken de datum van de module bij.</p>'''
pagina('over.html', 'DFO BV en Wft Permanent Actueel: over en verantwoording', 'Wie achter Wft Permanent Actueel zit, wat de toets wel en niet is, en hoe de vragen tot stand komen.', 'Over en verantwoording', 'DFO BV', inh, actief='over.html')

# ---------- 404 ----------
inh = '    <p class="lead">Deze pagina bestaat niet (meer).</p>\n    <div class="acties"><a class="btn" href="/">Naar de homepage</a><a class="btn ghost" href="/toets.html">Naar de toets</a></div>'
pagina('404.html', 'Pagina niet gevonden — Wft Permanent Actueel', 'Deze pagina bestaat niet.', 'Pagina niet gevonden', '404', inh)
s = open(R + '404.html', encoding='utf-8').read()
# 404 wordt op elk pad geserveerd: absolute paden voor assets en links
s = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|/|#)', r'\1="/', s)
s = s.replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n<meta name="theme-color"', 1)
open(R + '404.html', 'w', encoding='utf-8').write(s)

# ---------- Gebruiksvoorwaarden ----------
inh = f'''    <p class="lead">Deze voorwaarden gelden voor het gebruik van PA-WFT.nl. Door de site te gebruiken, ga je ermee akkoord.</p>
    <h2>Gratis en zonder account</h2>
    <p>Wft Permanent Actueel is een activiteit van DFO BV. Het gebruik van de modules, de toets en het certificaat is gratis voor alle adviseurs. Je hebt geen account of abonnement nodig.</p>
    <h2>Wat de toets is</h2>
    <p>De PA-toets is een oefentoets. Hij is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid. Het certificaat bevestigt alleen je resultaat op de oefentoets en wordt niet centraal geregistreerd. Gebruik het niet als bewijs van vakbekwaamheid.</p>
    <h2>Geen advies, geen garantie</h2>
    <p>De inhoud is algemene informatie, met als peildatum {PEIL}. Ondanks de zorg die we eraan besteden, kan een vraag of uitleg onjuist of verouderd zijn. Controleer wet- en regelgeving altijd in de geldende bron voordat je erop vertrouwt in je praktijk. DFO BV is niet aansprakelijk voor schade die ontstaat door het gebruik van deze site, voor zover de wet dat toelaat.</p>
    <h2>Rechten op de inhoud</h2>
    <p>De vragen, uitleg, teksten en vormgeving zijn van DFO BV. Je mag ze gebruiken voor je eigen kennis. Overnemen of verspreiden, ook in delen, mag alleen met toestemming van DFO BV.</p>
    <h2>Wijzigingen</h2>
    <p>DFO BV kan deze voorwaarden en de inhoud van de site aanpassen. De versie op deze pagina geldt.</p>
    <h2>Andere diensten van DFO</h2>
    <p>Voor de betaalde diensten van DFO BV gelden de algemene leveringsvoorwaarden van DFO; zie <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">www.dfobv.nl</a>.</p>
    <p class="klein">Laatst bijgewerkt: {PEIL}.</p>'''
pagina('gebruiksvoorwaarden.html', 'Gebruiksvoorwaarden — Wft Permanent Actueel', 'Voorwaarden voor het gratis gebruik van PA-WFT.nl: oefentoets, geen advies, rechten op de inhoud.', 'Gebruiksvoorwaarden', 'Voorwaarden', inh)

# ---------- Klachten ----------
inh = f'''    <p class="lead">Niet tevreden over Wft Permanent Actueel? Laat het ons weten, dan zoeken we samen naar een oplossing.</p>
    <h2>Zo dien je een klacht in</h2>
    <ol>
      <li>Mail je klacht naar <a href="mailto:info@dfobv.nl">info@dfobv.nl</a> of bel <a href="tel:+31332580460">033 258 04 60</a>.</li>
      <li>Vermeld je naam, je e-mailadres en waar je klacht over gaat. Gaat het over een toetsvraag, noem dan de module en de vraag.</li>
      <li>We bevestigen dat we je klacht hebben ontvangen, onderzoeken hem en laten je weten wat we ermee doen.</li>
    </ol>
    <h2>Fout in een vraag</h2>
    <p>Een fout in een vraag is geen klacht maar een melding, en die is welkom. In de toets staat bij elke vraag de link “Klopt deze vraag niet? Meld het”.</p>
    <h2>Komen we er samen niet uit?</h2>
    <p>Zie de klachtenprocedure van DFO BV op <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">www.dfobv.nl</a>.</p>
    <p class="klein">Laatst bijgewerkt: {PEIL}.</p>'''
pagina('klachten.html', 'Klachten — Wft Permanent Actueel', 'Zo dien je een klacht in over Wft Permanent Actueel.', 'Klachtenprocedure', 'Klachten', inh)

# ---------- PE uitgelegd (SEO/GEO) ----------
PE = [
 ('Bestaan PE-punten nog onder de Wft?', 'Nee. Sinds 1 januari 2014 werkt permanente educatie onder de Wft niet meer met PE-punten. Je houdt je adviesbevoegdheid geldig door binnen elke PE-periode het PE-examen te halen voor elke beroepskwalificatie die je hebt. PE-punten kom je nog wel tegen bij vrijwillige beroepsregisters; welke activiteiten daar meetellen, bepaalt elk register zelf.'),
 ('Wat is PE onder de Wft?', 'PE staat voor permanente educatie. Wie adviseert over financiële producten, moet aantoonbaar vakbekwaam zijn: het juiste Wft-diploma voor elke product-dienstcombinatie waarin je adviseert, en dat diploma geldig houden met PE-examens. Je legt de examens af bij een door het CDFD erkend examen-instituut. De AFM houdt toezicht op de naleving van de diplomaplicht door de onderneming.'),
 ('Wat doet het CDFD?', 'Het College Deskundigheid Financiële Dienstverlening (CDFD) adviseert de minister van Financiën over de eind- en toetstermen van de Wft-examens en erkent de examen-instituten. Via <a href="https://cdfd.nl/mijn-wft/" target="_blank" rel="noopener">Mijn Wft</a> (met DigiD) zie je welke beroepskwalificaties je hebt en download je je diploma’s en certificaten.'),
 ('Hoe lang duurt de PE-periode?', 'Volgens het CDFD loopt de lopende PE-periode van 1 april 2025 tot en met 31 maart 2028; de volgende loopt van 1 april 2028 tot en met 31 maart 2031. Per beroepskwalificatie haal je binnen de periode één PE-examen. Wanneer je dat doet, bepaal je zelf, zolang het voor de einddatum is. Zie <a href="https://cdfd.nl/wanneer-moet-ik-pe-examen-doen/" target="_blank" rel="noopener">Wanneer moet ik PE-examen doen?</a>'),
 ('Wat toetst een PE-examen?', 'Het PE-examen toetst recente ontwikkelingen in het vakgebied. De toetstermen worden jaarlijks per 1 april geactualiseerd; per 1 april 2026 zijn de PE-examens vernieuwd. Volgens het CDFD gaat het om ontwikkelingen die passen bij de module, relevant zijn voor het klantbelang en tijdig definitief bekend zijn. Zie het <a href="https://cdfd.nl/nieuws/wft-pe-examens-vernieuwd-vanaf-1-april-2026-cdfd-vraagt-nieuwe-ontwikkelingen/" target="_blank" rel="noopener">nieuwsbericht van het CDFD</a>.'),
 ('Wat betekent Wft Permanent Actueel (PA)?', 'Permanent Actueel betekent dat je vakkennis na je Wft-diploma bij de tijd blijft. PE-examens toetsen vooral wat er is veranderd in wet- en regelgeving en in de markt. Wft Permanent Actueel (PA-WFT.nl) is een gratis oefenomgeving van DFO BV waarmee je per Wft-module oefent.'),
 ('Welke PE-examens heb ik nodig?', 'Dat hangt af van je beroepskwalificaties. Het stelsel is modulair: per module haal je een initieel examen, en een combinatie van modules levert een beroepskwalificatie op. Zo bestaat Adviseur Hypothecair krediet volgens het CDFD uit Basis, Vermogen en Hypothecair krediet, en Adviseur Vermogen uit Basis en Vermogen. Controleer de exacte samenstelling bij de <a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">adviesbevoegdheden van het CDFD</a>; de <a href="index.html#check">pakketcheck</a> is alleen een hulpmiddel.'),
 ('Wat gebeurt er als ik mijn PE niet op tijd haal?', 'Dan vervalt je adviesbevoegdheid voor die beroepskwalificatie. Je herstelt die door een bijzonder examen te halen of door de initiële module-examens opnieuw te doen. Tot dat moment mag je in dat domein niet zelfstandig adviseren. Plan je PE-examen dus niet op het laatste moment: richting het einde van een periode is het druk bij de examen-instituten.'),
 ('Telt een PE-training mee?', 'Voor de wettelijke adviesbevoegdheid telt alleen het gehaalde PE-examen; een training zonder examen houdt je diploma niet geldig. Trainingen kunnen wel helpen om permanent actueel te blijven en tellen soms mee voor registertitels.'),
 ('Levert de PA-toets PE-punten of een PE-examen op?', 'Nee. De PA-toets is een oefentoets. Je krijgt een certificaat met je resultaat, maar dat is geen bewijs van vakbekwaamheid en telt niet mee voor je PE.'),
 ('Hoe oefen ik gratis voor mijn PE-examen?', 'Op PA-WFT.nl staan per Wft-module meerkeuzevragen met uitleg. Elke toets bevat 7 willekeurige vragen. Je kunt ook een mix maken van alle modules uit je eigen pakket. Gratis voor alle adviseurs, zonder account.'),
]
inh = ('    <p class="lead antwoord"><strong>Kort antwoord:</strong> onder de Wft bestaan geen PE-punten meer. Sinds 1 januari 2014 houd je je adviesbevoegdheid geldig met één PE-examen per beroepskwalificatie binnen elke PE-periode; de lopende periode loopt tot en met 31 maart 2028. '
       'Wft Permanent Actueel helpt je daar gratis mee te oefenen; de toets zelf levert geen PE-punten of PE-examen op.</p>\n'
       '    <div class="acties"><a class="btn" href="toets.html">Oefen gratis</a><a class="btn ghost" href="index.html#check">Welke modules heb ik nodig?</a></div>\n'
       + '\n'.join(f'    <h2>{q}</h2>\n    <p>{a}</p>' for q, a in PE) +
       '\n    <h2>Oefenen per Wft-module</h2>\n    <ul>' + ''.join(f'<li><a href="module-{m["id"]}.html">Wft {m["naam"]}</a>: PE-oefenvragen</li>' for m in MODS) + '</ul>\n'
       '    <h2>Bronnen</h2>\n    <ul class="bronnen"><li><a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD — College Deskundigheid Financiële Dienstverlening</a></li><li><a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">CDFD — adviesbevoegdheden</a></li><li><a href="https://cdfd.nl/wanneer-moet-ik-pe-examen-doen/" target="_blank" rel="noopener">CDFD — wanneer moet ik PE-examen doen?</a></li><li><a href="https://cdfd.nl/mijn-wft/" target="_blank" rel="noopener">CDFD — Mijn Wft</a></li>'
       '<li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars" target="_blank" rel="noopener">AFM — adviseurs en bemiddelaars</a></li>'
       f'<li><a href="{B["eind"][1]}" target="_blank" rel="noopener">{B["eind"][0]}</a></li><li><a href="{B["wft"][1]}" target="_blank" rel="noopener">{B["wft"][0]}</a></li></ul>\n'
       f'    <p class="klein">Peildatum {PEIL}. Algemene informatie, geen advies. De eisen die precies voor jou gelden, vind je bij het CDFD.</p>')
ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in PE]}
pagina('pe-punten-wft.html', 'PE-punten Wft en Permanent Actueel: zo werkt PE in 2026', 'Bestaan PE-punten nog? Hoe werkt PE onder de Wft en wat is Wft Permanent Actueel? Uitleg voor financieel adviseurs, plus gratis PE-oefenvragen per module.',
       'PE-punten, PE-examens en Wft Permanent Actueel', 'PE uitgelegd', inh, actief='pe-punten-wft.html', ld=ld)

# ---------- Homepage ----------
RING = ('<svg viewBox="0 0 120 120" aria-hidden="true"><g transform="rotate(-87 60 60)" id="segs"></g></svg>')
inh = f'''<div class="paneel page" id="uitleg">
    <h2>Gratis voor alle adviseurs</h2>
    <p class="lead">Wft Permanent Actueel helpt je je vakkennis bij te houden. Oefen met PE-oefenvragen precies de Wft-modules die bij jouw diploma's en klantcontact horen, met uitleg bij elk antwoord. Zonder kosten, zonder abonnement en zonder account.</p>
    <p class="antwoord"><strong>Doe de toets elk kwartaal</strong>, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het ook in bij je werkgever.</p>
    <div class="acties"><a class="btn" href="toets.html">Start de kennistoets</a><a class="btn ghost" href="#modules">Bekijk de 9 modules</a></div>
    <div data-agenda><p><a href="toets.html">Zet de toets de komende 5 jaar elk kwartaal in je agenda</a></p></div>
    <h2>Wft, PE en Permanent Actueel</h2>
    <p>Als financieel adviseur moet je vakbekwaam blijven: je hebt een Wft-diploma en houdt je kennis bij met permanente educatie (PE). PE-punten bestaan onder de Wft niet meer; sinds 1 januari 2014 haal je binnen elke PE-periode één PE-examen per beroepskwalificatie, bij een door het CDFD erkend examen-instituut. De lopende PE-periode loopt tot en met 31 maart 2028. De PA-toets is een oefentoets en levert geen PE-punten of PE-examen op.</p>
    <p><a href="pe-punten-wft.html">Lees hoe PE, PE-punten en Permanent Actueel werken</a></p>
</div>
<div class="paneel" id="modules">
    <h2>De 9 modules</h2>
    <p>Per module oefenvragen met uitleg, met de datum waarop de vragen voor het laatst zijn bijgewerkt.</p>
    <div class="modules" id="moduleGrid"></div>
</div>
<div class="paneel" id="check">
    <h2>Welke modules heb ik nodig?</h2>
    <div class="check">
      <div><p>Selecteer de diploma's die je bezit. Basis staat standaard aan. Voor de eisen die precies voor jou gelden, kijk je bij het CDFD.</p><div class="chips" id="chips"></div></div>
      <div class="result"><div class="ring-wrap">{RING}<div class="ring-count" id="count">0</div></div>
        <div class="pkg"><span class="label">Jouw PA-pakket</span><span class="pkg-n" id="countLabel"></span><ul id="chosen"></ul><a class="btn" id="startToets" href="toets.html">Toets over mijn pakket</a></div></div>
    </div>
</div>
<div class="paneel" id="werkwijze">
    <h2>Zo werkt het</h2>
    <div class="steps">
      <div class="step"><span class="num">01</span><h3>Kies je modules</h3><p>Op basis van je diploma's en type klantcontact.</p></div>
      <div class="step"><span class="num">02</span><h3>Oefen en leer</h3><p>7 vragen per toets, met uitleg bij alle vier de antwoorden.</p></div>
      <div class="step"><span class="num">03</span><h3>Certificaat</h3><p>Bewaar het in je personeelsdossier en lever het in bij je werkgever.</p></div>
      <div class="step"><span class="num">04</span><h3>Elk kwartaal</h3><p>Doe de toets elk kwartaal, zo blijf je permanent actueel.</p></div>
    </div>
</div>
</div>
<section class="poster"><h2>Oefen dit jaar alle modules uit je pakket. Gratis.</h2><a class="btn btn-white" href="toets.html">Start de kennistoets</a></section>
<div class="wrap">'''
ld_home = {'@context': 'https://schema.org', '@graph': [
 {'@type': 'Organization', '@id': SITE + '#dfo', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/', 'email': 'info@dfobv.nl', 'telephone': '+31332580460',
  'address': {'@type': 'PostalAddress', 'streetAddress': 'De Wel 14-16', 'postalCode': '3871 MV', 'addressLocality': 'Hoevelaken', 'addressCountry': 'NL'}},
 {'@type': 'WebSite', '@id': SITE + '#site', 'name': 'Wft Permanent Actueel', 'url': SITE, 'inLanguage': 'nl', 'publisher': {'@id': SITE + '#dfo'},
  'description': 'Gratis oefenomgeving voor financieel adviseurs: per Wft-module PE-oefenvragen met uitleg, een kennistoets van 7 vragen en een certificaat.'}]}
pagina('index.html', 'Wft Permanent Actueel: gratis PE-oefentoets voor adviseurs',
       'Wft Permanent Actueel: gratis voor alle adviseurs. PE-oefenvragen met uitleg voor alle 9 Wft-modules, van Basis tot Pensioen. Met certificaat.',
       'Wft Permanent Actueel', 'Een activiteit van DFO BV', inh, actief='index.html', ld=ld_home,
       intro='Kennis actueel, elk jaar weer. Oefen per Wft-module met vragen over wat er actueel is, met uitleg bij elk antwoord.',
       mast_extra='    <p class="gratis"><strong>Gratis voor alle adviseurs.</strong> Alle modules en de kennistoets, zonder kosten.</p>\n    ' + MARK.replace('<svg ', '<svg class="hero-mark" ', 1) + '\n',
       scripts='\n<script src="assets/js/modules.js"></script>\n<script src="assets/js/main.js"></script>\n<script src="assets/js/agenda.js"></script>')
s = open(R + 'index.html', encoding='utf-8').read()
s = s.replace('<meta name="theme-color" content="#1462ad">', '<meta name="google-site-verification" content="3JKf334ow3hOt0pa1YDk1TUvE6EaKzWpUMmtlkBD6fo">\n<meta name="theme-color" content="#1462ad">', 1)
open(R + 'index.html', 'w', encoding='utf-8').write(s)

# ---------- Kennistoets ----------
inh = '<div class="paneel" id="paneel" aria-live="polite">\n      <noscript><p>Schakel JavaScript in om de toets te maken.</p></noscript>\n</div>'
pagina('toets.html', 'Gratis Wft-kennistoets: 7 PE-oefenvragen met uitleg | Permanent Actueel',
       'Gratis Wft-kennistoets voor adviseurs: 7 vragen, elke keer anders, over de 9 Wft-modules. Met uitleg en certificaat.',
       'Wft-kennistoets', 'Wft Permanent Actueel', inh, actief='toets.html',
       intro=f'Zeven vragen, elke keer anders, over de {len(MODS)} Wft-modules. Bij elk antwoord lees je waarom het goed of fout is, en na afloop maak je een certificaat.',
       extra='\n<link rel="stylesheet" href="assets/css/toets.css">',
       scripts='\n<script src="assets/js/modules.js"></script>\n<script src="assets/js/vragen.js"></script>\n<script src="assets/js/agenda.js"></script>\n<script src="assets/js/toets.js"></script>')

# ---------- Wet- en regelgeving ----------
bron = open(R + 'tools/wetgeving-bron.md', encoding='utf-8').read()
cats, huidig = [], None
for regel in bron.split('\n'):
    if regel.startswith('## '):
        naam_c = regel[3:].strip()
        if naam_c in ('Veelgestelde vragen', 'Bronnen'): break
        huidig = None if naam_c in ('Wft-kennistoets', 'DFO Compliance') else (naam_c, [])
        if huidig: cats.append(huidig)
    elif huidig and regel.startswith('- '):
        m = re.match(r'- \[(.+?)\]\((.+?)\): (.*)', regel)
        if m: huidig[1].append((m.group(1), m.group(2), m.group(3), False))
        else:
            m = re.match(r'- (.+?): (.*?) \(directe verwijzing nog te verifiëren\)', regel)
            if m: huidig[1].append((m.group(1), 'https://wetten.overheid.nl/zoeken?keyword=' + m.group(1).split(' (')[0].replace(' ', '+'), m.group(2), True))
VERANDERT = [
 '<strong>CCD II — 20 november 2026.</strong> De herziene richtlijn consumentenkrediet gaat gelden; de Nederlandse implementatiewet is nog in voorbereiding. Aanbieders van BNPL, uitgestelde-betaalkaarten en huur of lease met koopoptie moeten toetsen of zij vergunningplichtig worden.',
 '<strong>EU-witwaspakket (AMLR en AMLD6).</strong> Komt boven op de huidige Wwft; de Wwft wordt op termijn vervangen door een implementatiewet bij het Europese pakket. De poortwachtersrol van adviseurs verandert mee.',
 '<strong>Hypotheekacceptatie 2026.</strong> De NHG-kostengrens is € 470.000. Meerdere geldverstrekkers beperken het aflossingsvrije deel bij nieuwe aanvragen tot 30% van de woningwaarde, en taxatierapporten moeten ingaan op funderingsrisico.',
 '<strong>AI-verordening en DORA.</strong> Gefaseerde toepassing raakt advieskantoren via software, modellen en uitbesteding.',
 '<strong>TRHK en NHG Voorwaarden &amp; Normen.</strong> Wijzigen jaarlijks per 1 januari. Werk met de jaarversie.']
inh = ('<div class="paneel page">\n    <h2>Wat er dit jaar verandert</h2>\n    <ul>' + ''.join(f'<li>{v}</li>' for v in VERANDERT) + '</ul>\n</div>\n'
       '<div class="paneel page">\n    <h2>Overzicht per thema</h2>\n    <p>Nationale regels verwijzen naar de geldende tekst op wetten.overheid.nl, Europese regels naar EUR-Lex. Controleer bij normen die per jaar wijzigen altijd de versiedatum van de wettekst.</p>\n'
       + '\n'.join(f'    <p class="groep" id="{re.sub("[^a-z]+", "-", c.lower()).strip("-")}">{html.escape(c)}</p>\n    <ul class="linklijst">'
                   + ''.join(f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(n)}</a>' + ('<span class="tag">verwijzing te verifiëren</span>' if t else '') + f'<span>{html.escape(d)}</span></li>' for n, u, d, t in items) + '</ul>'
                   for c, items in cats)
       + f'\n    <p class="klein">Peildatum {PEIL}. Bron: WFT Bieb van DFO. Algemene informatie, geen advies.</p>\n</div>')
secties = open(R + 'tools/wetgeving-secties.html', encoding='utf-8').read()
pagina('wetgeving.html', 'Wet- en regelgeving voor financieel adviseurs: Wft, Wwft en meer',
       'Doorzoekbaar overzicht van wet- en regelgeving voor financieel adviseurs: Wft, Wwft, hypothecair en consumptief krediet, fiscaal, pensioen, sociale zekerheid en toeslagen, met links naar de officiële tekst.',
       'Wet- en regelgeving', 'Wft Permanent Actueel', secties, actief='wetgeving.html', kaal=True,
       intro=f'Doorzoekbare bibliotheek van wet- en regelgeving voor financiële dienstverleners. Elke regeling linkt naar de officiële tekst op wetten.overheid.nl of EUR-Lex. <span id="peildatum">Peildatum {PEIL}</span>.',
       extra='\n<link rel="stylesheet" href="assets/css/wetgeving.css">\n<link rel="stylesheet" href="assets/css/style.css">',
       scripts='\n<script src="assets/js/wetgeving.js"></script>')

# ---------- DFO Compliance ----------
def lijst(items): return '<ul class="linklijst">' + ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a>' + (f'<span>{d}</span>' if d else '') + '</li>' for n, u, d in items) + '</ul>'
inh = ('<div class="paneel page">\n    <h2>Waar DFO je bij helpt</h2>\n    <ul><li>Begeleiding bij het aanvragen van een Wft-vergunning bij de AFM.</li>'
       '<li>Antwoord op je Wft- en compliancevragen via de e-mailhelpdesk van het serviceabonnement.</li>'
       '<li>Modeldocumenten voor de verplichte vastleggingen, zoals klachtenprocedure, incidentenregeling, Wwft-beleid en dienstenwijzer.</li>'
       '<li>De wekelijkse Nieuwsbrief Wft met actuele ontwikkelingen uit wet- en regelgeving en toezicht.</li>'
       '<li>Opleidingen en bijeenkomsten voor medewerkers van het advieskantoor.</li></ul>\n'
       '    <div class="acties"><a class="btn" href="https://www.dfobv.nl/product/bureau-dfo-servicepakket/" target="_blank" rel="noopener">Wft Serviceabonnement</a><a class="btn ghost" href="https://kennisbank.dfobv.nl/" target="_blank" rel="noopener">DFO Kennisbank</a></div>\n</div>\n'
       '<div class="paneel page">\n    <h2>Modeldocumenten Wft en Wwft</h2>\n    ' + lijst([
         ('Overzicht documenten Wft en Wwft', 'https://www2.dfobv.nl/documenten-contracten/wft-wwft/', 'Klachtenprocedure, archiveringsregeling, cliëntovereenkomst en andere verplichte vastleggingen.'),
         ('Klachtenprocedure', 'https://www.dfobv.nl/product/klachtenprocedure/', 'De Wft verplicht een vastgelegde interne klachtenprocedure die bij medewerkers bekend is.'),
         ('Incidentenregeling', 'https://www.dfobv.nl/product/incidentenregeling/', 'Vastlegging en melding van incidenten, onder meer richting de AFM.'),
         ('Model Wwft-beleid financiële dienstverlener', 'https://www.dfobv.nl/product/model-wwft-beleid-financiele-dienstverlener/', 'Beleid voor cliëntenonderzoek, risicobeoordeling en melden van ongebruikelijke transacties.'),
         ('Model dienstenwijzer incl. privacyparagraaf', 'https://www.dfobv.nl/product/model-dienstenwijzer-met-privacy/', 'Precontractuele klantinformatie volgens de Wft, gecombineerd met de AVG-informatieplicht.'),
         ('Model opdrachtbevestiging zakelijk krediet', 'https://www.dfobv.nl/product/model-opdrachtbevestiging-advies-en-bemiddeling-zakelijk-krediet/', 'Opdrachtbevestiging voor advies en bemiddeling in zakelijk krediet.')]) +
       '\n    <h2>Bedrijfsvoering en samenwerking</h2>\n    ' + lijst([
         ('Documenten bedrijfsvoering', 'https://www2.dfobv.nl/documenten-contracten/bedrijfsvoering/', 'Modellen voor de inrichting van het kantoor.'),
         ('Modelovereenkomst freelancer financiële dienstverlening', 'https://www.dfobv.nl/product/modelovereenkomst-freelancer-financiele-dienstverlening/', 'De Wft legt voor freelancers dezelfde eisen op als voor vaste medewerkers, onder meer op vakbekwaamheid en beheerste bedrijfsvoering.'),
         ('Overzicht samenwerkingsvormen financiële dienstverlening', 'https://www.dfobv.nl/product/overzicht-samenwerkingsvormen-financiele-dienstverlening/', 'Aangesloten onderneming, collectieve vergunning en andere constructies naast elkaar.')]) +
       '\n</div>\n<div class="paneel page">\n    <h2>Wil je het zeker weten?</h2>\n    <p>Twijfel je over de toepassing van een regel in jouw situatie? Neem contact op met DFO: telefoon <a href="tel:+31332580460">033 258 04 60</a>, e-mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>\n'
       '    <div class="acties"><a class="btn ghost" href="https://www.dfobv.nl/" target="_blank" rel="noopener">Naar dfobv.nl</a><a class="btn ghost" href="https://www.dfobv.nl/ons-team/" target="_blank" rel="noopener">Ons team</a></div>\n</div>')
pagina('compliance.html', 'DFO Compliance: Wft-vergunning, helpdesk en modeldocumenten',
       'DFO ondersteunt financiële dienstverleners bij Wft-vergunningaanvragen, Wft- en compliancevragen, modeldocumenten Wft en Wwft en de Nieuwsbrief Wft.',
       'DFO Compliance', 'DFO BV', inh, actief='compliance.html',
       intro='Voor verdieping en ondersteuning bij Wft- en Wwft-vraagstukken kun je terecht bij DFO: actuele informatie, modeldocumenten en persoonlijke hulp.')

# ---------- DFO Opleidingen ----------
inh = ('<div class="paneel page">\n    <h2>Opleidingen en bijeenkomsten</h2>\n    <p>DFO organiseert opleidingen en bijeenkomsten voor medewerkers van het advieskantoor. Kijk in de agenda voor de actuele data.</p>\n    ' + lijst([
         ('Agenda opleidingen en bijeenkomsten', 'https://www.dfobv.nl/agenda/', 'Actuele opleidingen, cursussen en bijeenkomsten van DFO.'),
         ('Opleiding schadebehandelaar financieel advieskantoor', 'https://www.dfobv.nl/product/opleiding-schadebehandelaar-financieel-advieskantoor/', None)]) +
       '\n    <h2>Kennis bijhouden</h2>\n    ' + lijst([
         ('Wft Serviceabonnement kennis en praktijk', 'https://www.dfobv.nl/product/bureau-dfo-servicepakket/', 'Nieuwsbrief Wft plus e-mailhelpdesk voor Wft-vragen.'),
         ('Nieuwsbrief Wft', 'https://www.dfobv.nl/product/nieuwsbrief-wft/', 'Gemiddeld één nieuwsbrief per week over actuele Wft-ontwikkelingen.'),
         ('DFO Kennisbank', 'https://kennisbank.dfobv.nl/', 'Artikelen uit de Nieuwsbrief Wft, doorzoekbaar.')]) +
       '\n    <h2>Gratis oefenen</h2>\n    <p>Met de <a href="toets.html">Wft-kennistoets</a> van Wft Permanent Actueel oefen je per module met vragen met uitleg. Gratis voor alle adviseurs. De toets is een oefentoets en geen erkend PE-examen.</p>\n</div>')
pagina('opleidingen.html', 'DFO Opleidingen: opleidingen en kennis voor financieel adviseurs',
       'Opleidingen, bijeenkomsten en kennisproducten van DFO voor medewerkers van financiële advieskantoren, plus gratis oefenen met de Wft-kennistoets.',
       'DFO Opleidingen', 'DFO BV', inh, actief='opleidingen.html',
       intro='Opleidingen en bijeenkomsten voor medewerkers van het advieskantoor, en kennis om je vak bij te houden.')

# ---------- llms.txt ----------
llms = ['# Wft Permanent Actueel (PA-WFT.nl)', '',
        '> Gratis oefenomgeving voor financieel adviseurs in Nederland: per Wft-module meerkeuzevragen met uitleg, een toets van 7 vragen en een certificaat om naar jezelf te mailen. Een activiteit van DFO BV, Hoevelaken. Geen erkend PE-examen en geen advies. Peildatum regelgeving: ' + PEIL + '.', '',
        '## PE en Permanent Actueel', '', f'- [PE-punten, PE-examens en Wft Permanent Actueel]({SITE}pe-punten-wft.html): onder de Wft bestaan geen PE-punten meer; sinds 1 januari 2014 houd je je adviesbevoegdheid geldig met één PE-examen per beroepskwalificatie binnen elke PE-periode (lopende periode: 1 april 2025 tot en met 31 maart 2028, volgens het CDFD). De PA-toets is een gratis oefentoets en levert geen PE-punten of PE-examen op.', '',
        '## Toets', '', f'- [PA-toets]({SITE}toets.html): kies een module of een mix; 7 willekeurige vragen, uitleg na elk antwoord, certificaat vanaf 5 van 7 goed.', '',
        '## Modules', '']
llms += [f"- [Wft {m['naam']}]({SITE}module-{m['id']}.html): {m['tekst']} Laatst bijgewerkt {nl(m['bijgewerkt'])}." for m in MODS]
llms += ['', '## Informatie', '', f'- [Wet- en regelgeving]({SITE}wetgeving.html): overzicht van Wft, Wwft, krediet, fiscaal, pensioen en sociale zekerheid met links naar de officiële tekst', f'- [DFO Compliance]({SITE}compliance.html)', f'- [DFO Opleidingen]({SITE}opleidingen.html)', f'- [Veelgestelde vragen]({SITE}vragen.html)', f'- [Over en verantwoording]({SITE}over.html)', f'- [Gebruiksvoorwaarden]({SITE}gebruiksvoorwaarden.html)', f'- [Klachten]({SITE}klachten.html)', f'- [Privacy]({SITE}privacy.html)', '',
         '## Contact', '', '- DFO BV, De Wel 14–16, 3871 MV Hoevelaken, 033 258 04 60, info@dfobv.nl, https://www.dfobv.nl/']
open(R + 'llms.txt', 'w', encoding='utf-8').write('\n'.join(llms) + '\n')

# ---------- sitemap en robots ----------
paden = ['', 'toets.html', 'pe-punten-wft.html', 'wetgeving.html', 'compliance.html', 'opleidingen.html'] + [f'module-{m["id"]}.html' for m in MODS] + ['vragen.html', 'over.html', 'gebruiksvoorwaarden.html', 'klachten.html', 'privacy.html']
open(R + 'sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{SITE}{p}</loc><lastmod>2026-10-15</lastmod></url>\n' for p in paden) + '</urlset>\n')
open(R + 'robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n')
print('klaar:', len(paden), 'pagina’s in sitemap')
