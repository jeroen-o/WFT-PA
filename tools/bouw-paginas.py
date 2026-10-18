"""Bouwt de vaste onderdelen van PA-WFT.nl opnieuw: modulepagina's, veelgestelde vragen, privacy, over,
gebruiksvoorwaarden, klachten, 404, sitemap, robots en llms.txt, plus header en footer van index en toets.

Gebruik (vanuit de map van de repository):  python3 tools/bouw-paginas.py
Vereist Node.js om assets/js/modules.js te lezen.
"""
import re, html, os, json, subprocess, urllib.parse, unicodedata
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SITE = 'https://pa-wft.nl/'
PEIL = '15 oktober 2026'

# Tweetaligheid: Nederlandse pagina -> Engelse pagina (in /en/). Pagina's zonder Engelse tegenhanger linken naar de Engelse homepage.
EN_PAD = {'index.html': 'index.html', 'toets.html': 'quiz.html', 'nieuw.html': 'whats-new.html', 'begrippen.html': 'glossary.html', 'pe-punten-wft.html': 'pe-explained.html',
          'vragen.html': 'faq.html', 'over.html': 'about.html', 'privacy.html': 'privacy.html', 'gebruiksvoorwaarden.html': 'terms.html', 'klachten.html': 'complaints.html', 'zoeken.html': 'search.html'}
for _m in ['basis', 'consumptief-krediet', 'hypothecair-krediet', 'schade-particulier', 'schade-zakelijk', 'vermogen', 'inkomen', 'pensioen', 'zorgverzekering']:
    EN_PAD[f'module-{_m}.html'] = f'module-{_m}.html'
def en_url(pad): return SITE + 'en/' + ('' if EN_PAD[pad] == 'index.html' else EN_PAD[pad])

MARK = ('<svg viewBox="0 0 120 120" aria-hidden="true"><g transform="rotate(-87 60 60)">'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#1462ad" stroke-width="14" stroke-dasharray="28.5 5.01"/>'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#0b3d73" stroke-width="14" stroke-dasharray="28.5 273.09"/></g>'
        '<text x="60" y="72" text-anchor="middle" font-family="Archivo, Arial, sans-serif" font-weight="800" font-size="34" fill="#1462ad">PA</text></svg>')

NAV = [('index.html', 'Home'), ('toets.html', 'Kennistoets'), ('index.html#modules', 'Modules'), ('pe-punten-wft.html', 'PE uitgelegd'), ('wetgeving.html', 'Wet- en regelgeving'),
       ('compliance.html', 'DFO Compliance'), ('opleidingen.html', 'DFO Opleidingen'), ('over.html', 'DFO BV'), ('zoeken.html', 'Zoeken')]

def header(actief='', pad=''):
    loep = '<svg class="loep" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'
    links = ''.join('<a href="%s"%s>%s%s</a>' % (h, ' aria-current="page"' if h == actief else '', loep if h == 'zoeken.html' else '', t) for h, t in NAV)
    return ('<a class="skip" href="#inhoud">Naar de inhoud</a>\n<div class="topbar">\n  <div class="wrap">\n'
            '    <a class="logo" href="index.html" aria-label="Wft Permanent Actueel — home"' + (' aria-current="page"' if actief == 'index.html' else '') + '><img src="assets/logo/pa-wft-logo-horizontal.png" width="144" height="60" alt="Wft Permanent Actueel — PA-WFT.nl" fetchpriority="high"></a>\n'
            '    <a class="taalknop" href="' + ('en/' + ('' if EN_PAD.get(pad, 'index.html') == 'index.html' else EN_PAD[pad]) if pad != '404.html' else 'en/') + '" hreflang="en" lang="en" title="Read this page in English">EN</a>\n'
            '    <a class="zoekknop" href="zoeken.html" aria-label="Zoeken op de site">' + loep.replace('width="16" height="16"', 'width="24" height="24"') + '</a>\n'
            '    <nav class="topnav" aria-label="Hoofdmenu">' + links + '</nav>\n'
            '  </div>\n</div>')

def masthead(kicker, kop, intro='', extra='', datum=''):
    return ('<header class="masthead">\n  <div class="wrap">\n' + (f'    <p class="bijgewerkt-kop"><time datetime="{datum}" title="Laatst bijgewerkt">{nl(datum)}</time></p>\n' if datum else '') + (f'    <p class="kicker">{kicker}</p>\n' if kicker else '') + f'    <h1>{kop}</h1>\n'
            + (f'    <p class="intro">{intro}</p>\n' if intro else '') + extra + '  </div>\n</header>')

MELDING = ('<div class="melding" role="note"><strong>Let op.</strong> De PA-toets is een oefentoets en geldt niet als Wft-examen, PE-examen of PE-bewijs. '
           'DFO BV is niet verantwoordelijk voor de juistheid en volledigheid van alle vragen en antwoorden; regels wijzigen. Wil je het zeker weten? '
           'Neem contact op met <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">DFO BV</a> via <a href="tel:+31332580460">033 258 04 60</a> of <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</div>')

EXT = ' target="_blank" rel="noopener"'
FOOTER = ('<footer class="foot">\n  <div class="wrap">\n    <div class="foot-kolommen">\n'
    '      <div class="foot-merk"><p class="foot-titel">Wft Permanent Actueel</p><p>Gratis oefentoets voor adviseurs en klantmedewerkers. Kennis actueel, elk kwartaal weer.</p>'
    '<p><a class="btn btn-white" href="toets.html">Start de kennistoets</a></p></div>\n'
    '      <nav aria-label="Toets en kennis"><p class="foot-kop">Toets en kennis</p><ul><li><a href="toets.html">Kennistoets</a></li><li><a href="index.html#modules">Modules</a></li>'
    '<li><a href="nieuw.html">Wat is er nieuw</a></li><li><a href="begrippen.html">Begrippenlijst</a></li><li><a href="index.html#tip">Tip je collega’s</a></li><li><a href="index.html#check">Welke modules heb ik nodig?</a></li><li><a href="pe-punten-wft.html">PE uitgelegd</a></li><li><a href="wetgeving.html">Wet- en regelgeving</a></li><li><a href="vragen.html">Veelgestelde vragen</a></li></ul></nav>\n'
    '      <nav aria-label="DFO"><p class="foot-kop">DFO</p><ul><li><a href="compliance.html">DFO Compliance</a></li><li><a href="opleidingen.html">DFO Opleidingen</a></li>'
    '<li><a href="https://www.dfobv.nl/ons-team/"' + EXT + '>Ons team</a></li><li><a href="https://www.dfosignalen.nl/"' + EXT + '>DFO Signalen</a></li><li><a href="https://www.dfobv.nl/product/nieuwsbrief-wft/"' + EXT + '>Nieuwsbrief Wft</a></li><li><a href="https://kennisbank.dfobv.nl/"' + EXT + '>DFO Kennisbank</a></li></ul></nav>\n'
    '      <div><p class="foot-kop">Contact</p><address>DFO BV<br>De Wel 14–16<br>3871 MV Hoevelaken<br><a href="tel:+31332580460">033 258 04 60</a><br><a href="mailto:info@dfobv.nl">info@dfobv.nl</a><br>'
    '<a href="https://www.dfobv.nl/contact/"' + EXT + '>Contactpagina</a></address><p class="foot-klein">KvK 32068727 · btw NL806480828B01</p></div>\n'
    '    </div>\n  </div>\n'
    '  <div class="foot-balk"><div class="wrap">'
    '<div class="foot-balk-tekst"><nav class="foot-links" aria-label="Voorwaarden"><a href="over.html">Over en verantwoording</a><a href="gebruiksvoorwaarden.html">Gebruiksvoorwaarden</a><a href="klachten.html">Klachten</a><a href="privacy.html">Privacy en cookies</a></nav>'
    '<p class="foot-disc">© 2026 DFO BV. Wft Permanent Actueel is een activiteit van DFO BV. Oefentoets voor financieel adviseurs; geen erkend PE-examen en geen advies.</p></div>'
    '<a class="foot-logo" href="https://www.dfobv.nl/"' + EXT + ' aria-label="DFO BV — naar dfobv.nl"><img src="assets/logo/dfo-logo.png" width="186" height="44" loading="lazy" decoding="async" alt="DFO — dienstverlening voor financiële ondernemers"></a>'
    '</div></div>\n</footer>\n'
    '<script>(function(){function o(){var h=location.hash.slice(1),e=h&&document.getElementById(decodeURIComponent(h));if(e&&e.tagName==="DETAILS"){e.open=true;e.scrollIntoView();}}o();addEventListener("hashchange",o);})();</script>')

GEEN_INDEX = {'404.html', 'zoeken.html'}
def canon(pad): return SITE + ('' if pad == 'index.html' else pad)
def head(titel, omschrijving, pad, extra='', og_beeld='og-image.png', og_type='website'):
    t, o, u = html.escape(titel), html.escape(omschrijving), canon(pad)
    return ('<!doctype html>\n<html lang="nl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{t}</title>\n<meta name="description" content="{o}">\n'
            + ('<meta name="robots" content="noindex, follow">\n' if pad in GEEN_INDEX else '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">\n')
            + '<meta name="theme-color" content="#1462ad">\n<meta name="author" content="DFO BV">\n'
            f'<link rel="canonical" href="{u}">\n<link rel="alternate" hreflang="nl" href="{u}">\n'
            + (f'<link rel="alternate" hreflang="en" href="{en_url(pad)}">\n' if pad in EN_PAD else '') + f'<link rel="alternate" hreflang="x-default" href="{u}">\n'
            '<link rel="icon" href="favicon.ico" sizes="any">\n<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<link rel="manifest" href="site.webmanifest">\n'
            f'<meta property="og:type" content="{og_type}">\n<meta property="og:site_name" content="Wft Permanent Actueel">\n<meta property="og:locale" content="nl_NL">\n'
            f'<meta property="og:title" content="{t}">\n<meta property="og:description" content="{o}">\n<meta property="og:url" content="{u}">\n'
            f'<meta property="og:image" content="{SITE}{og_beeld}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{t}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{t}">\n<meta name="twitter:description" content="{o}">\n<meta name="twitter:image" content="{SITE}{og_beeld}">\n'
            '<link rel="preload" href="assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
            '<link rel="stylesheet" href="assets/css/style.css">' + extra + '\n</head>\n<body>')

import hashlib
def versie(html_tekst):
    """Zet achter elke lokale CSS- en JS-link een versiecode op basis van de inhoud, zodat browsers na een wijziging het nieuwe bestand laden."""
    def code(m):
        pad = m.group(2)
        try: h = hashlib.sha1(open(R + pad.lstrip('/'), 'rb').read()).hexdigest()[:8]
        except OSError: return m.group(0)
        return f'{m.group(1)}{pad}?v={h}"'
    return re.sub(r'((?:href|src)=")(/?assets/(?:css|js)/[^"?]+\.(?:css|js))"', code, html_tekst)

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

# Blok "Blijf op de hoogte": aanmelden gaat via de sites van DFO zelf; PA-WFT.nl bewaart geen gegevens
NIEUWSBRIEVEN = ('<section class="nieuwsbrieven" id="nieuwsbrief" aria-labelledby="nb-kop">\n'
    '    <h2 id="nb-kop">Blijf op de hoogte</h2>\n'
    '    <p class="lead">Zo blijf je op de hoogte van het actuele nieuws. Meld je aan voor de nieuwsbrieven van DFO.</p>\n'
    '    <div class="nb-kaarten">\n'
    '      <article class="nb-kaart"><h3>DFO Signalen</h3><p>Wekelijks signalen uit de markt, modelteksten en praktijkanalyses voor het advieskantoor, met een archief dat jaren teruggaat.</p>'
    '<a class="btn" href="https://www.dfosignalen.nl/"' + EXT + '>Meld je aan voor DFO Signalen</a></article>\n'
    '      <article class="nb-kaart"><h3>Nieuwsbrief Wft</h3><p>Gemiddeld één keer per week de actuele ontwikkelingen in wet- en regelgeving en toezicht, kort en praktisch uitgelegd voor financieel dienstverleners.</p>'
    '<a class="btn" href="https://www.dfobv.nl/product/nieuwsbrief-wft/"' + EXT + '>Meld je aan voor de Nieuwsbrief Wft</a></article>\n'
    '    </div>\n'
    '    <p class="klein">Aanmelden gaat via de website van DFO. Wft Permanent Actueel slaat zelf geen gegevens op.</p>\n'
    '  </section>\n')

def pagina(pad, titel, omschrijving, kop, kicker, inhoud, actief='', extra='', ld=None, intro='', scripts='', mast_extra='', datum=None, kaal=False, og_beeld='og-image.png', og_type='website', kruimel=None):
    datum = datum or BIJGEWERKT.get(pad, PEIL_ISO)
    if og_beeld == 'og-image.png' and os.path.exists(R + 'og/' + pad.replace('.html', '.png')): og_beeld = 'og/' + pad.replace('.html', '.png')
    if pad not in GEEN_INDEX:
        ld = ld_aanvullen(ld, pad, titel, omschrijving, datum, kruimel or re.sub(r'<[^>]+>', '', kop), og_beeld)
    if ld: extra += '\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    if not kaal and not inhoud.lstrip().startswith('<div class="paneel'):
        inhoud = '<div class="paneel page">\n' + inhoud + '\n</div>'
    s = (head(titel, omschrijving, pad, extra, og_beeld, og_type) + '\n' + header(actief, pad) + '\n' + masthead(kicker, kop, intro, mast_extra, datum)
         + ('\n<main id="inhoud" class="kaal">\n' + inhoud + '\n<div class="wrap">' + MELDING + '</div>\n</main>\n' if kaal else
            '\n<main id="inhoud">\n  <div class="wrap">\n' + inhoud + '\n' + MELDING + '\n  </div>\n</main>\n') + FOOTER + scripts + '\n</body>\n</html>\n')
    if kaal: s = s.replace('<body>', '<body class="breed">', 1)
    s = kop_ids(s)
    if pad not in ('404.html', 'zoeken.html'): zoek_indexeer(pad, titel, omschrijving, s)
    open(R + pad, 'w', encoding='utf-8').write(versie(link_cdfd(s)))

# ---------- gestructureerde data: elke pagina krijgt Organization, WebSite, WebPage en een broodkruimelpad ----------
ORG = {'@type': 'Organization', '@id': SITE + '#dfo', 'name': 'DFO BV', 'alternateName': 'DFO — dienstverlening voor financiële ondernemers', 'url': 'https://www.dfobv.nl/',
       'logo': {'@type': 'ImageObject', 'url': SITE + 'assets/logo/dfo-logo.png'}, 'email': 'info@dfobv.nl', 'telephone': '+31332580460',
       'vatID': 'NL806480828B01', 'identifier': {'@type': 'PropertyValue', 'propertyID': 'KvK', 'value': '32068727'},
       'address': {'@type': 'PostalAddress', 'streetAddress': 'De Wel 14-16', 'postalCode': '3871 MV', 'addressLocality': 'Hoevelaken', 'addressCountry': 'NL'},
       'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer service', 'telephone': '+31332580460', 'email': 'info@dfobv.nl', 'availableLanguage': 'nl', 'url': 'https://www.dfobv.nl/contact/'},
       'sameAs': ['https://www.dfobv.nl/', 'https://www.linkedin.com/company/bureaudfo/', 'https://kennisbank.dfobv.nl/', 'https://www.dfosignalen.nl/']}
WEBSITE = {'@type': 'WebSite', '@id': SITE + '#site', 'name': 'Wft Permanent Actueel', 'alternateName': 'PA-WFT.nl', 'url': SITE, 'inLanguage': 'nl', 'publisher': {'@id': SITE + '#dfo'},
           'description': 'Gratis oefenomgeving voor financieel adviseurs: per Wft-module PE-oefenvragen met uitleg, een kennistoets van 7 vragen per module (5 extra per toegevoegde module) en een certificaat.',
           'potentialAction': {'@type': 'SearchAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': SITE + 'zoeken.html?q={search_term_string}'}, 'query-input': 'required name=search_term_string'}}
def ld_aanvullen(ld, pad, titel, omschrijving, datum, kruimel, beeld='og-image.png'):
    ld = ld or {'@context': 'https://schema.org', '@graph': []}
    if '@graph' not in ld:
        ld = {'@context': 'https://schema.org', '@graph': [{k: v for k, v in ld.items() if k != '@context'}]}
    g = ld['@graph']
    typen = {n.get('@type') for n in g}
    ids = {n.get('@id') for n in g}
    if ORG['@id'] not in ids: g.insert(0, ORG)
    if WEBSITE['@id'] not in ids: g.insert(1, WEBSITE)
    u = canon(pad)
    g.append({'@type': 'WebPage', '@id': u + '#pagina', 'url': u, 'name': re.sub(r'\s*\|.*$', '', titel), 'description': omschrijving, 'inLanguage': 'nl',
              'dateModified': datum, 'isPartOf': {'@id': SITE + '#site'}, 'publisher': {'@id': SITE + '#dfo'},
              'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + beeld, 'width': 1200, 'height': 630}})
    if 'BreadcrumbList' not in typen and pad != 'index.html':
        g.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Wft Permanent Actueel', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': kruimel, 'item': u}]})
    return ld

# ---------- zoeken: ids op tussenkoppen en een zoekindex per sectie (alles in de browser, geen database) ----------
ZOEK = []
def slug(t):
    t = re.sub(r'<[^>]+>', '', html.unescape(t)).lower()
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:60] or 'sectie'
def kop_ids(s):
    gezien = set(re.findall(r'\sid="([^"]+)"', s))
    def zet(m):
        if ' id=' in m.group(1): return m.group(0)
        b = slug(m.group(2)); i = b; n = 2
        while i in gezien: i = f'{b}-{n}'; n += 1
        gezien.add(i)
        return f'<h2{m.group(1)} id="{i}">{m.group(2)}</h2>'
    s = re.sub(r'<h2([^>]*)>(.*?)</h2>', zet, s, flags=re.S)
    def faq(m):
        b = 'vraag-' + slug(m.group(1)); i = b; n = 2
        while i in gezien: i = f'{b}-{n}'; n += 1
        gezien.add(i)
        return f'<details class="faq" id="{i}"><summary>{m.group(1)}</summary>'
    return re.sub(r'<details class="faq"><summary>(.*?)</summary>', faq, s, flags=re.S)
def platte_tekst(h):
    h = re.sub(r'(?is)<(script|style|svg|nav|form|button)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?i)<br\s*/?>|</(p|li|h[1-6]|div|dt|dd|tr)>', ' ', h)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())
def zoek_indexeer(pad, titel, omschrijving, s):
    m = re.search(r'(?s)<main id="inhoud"[^>]*>(.*)</main>', s)
    if not m: return
    main = m.group(1).replace(MELDING, '')
    paginatitel = re.sub(r'\s*[|—].*$', '', titel).strip()
    url = '' if pad == 'index.html' else pad
    # losse veelgestelde vragen als eigen zoekresultaat
    for fid, vraag, antw in re.findall(r'<details class="faq" id="([^"]+)"><summary>(.*?)</summary>(.*?)</details>', main, flags=re.S):
        ZOEK.append({'u': f'{url}#{fid}', 'p': paginatitel, 'h': platte_tekst(vraag), 'x': platte_tekst(antw)[:3000]})
    main = re.sub(r'<details class="faq".*?</details>', ' ', main, flags=re.S)
    for bid, term, uitleg in re.findall(r'<dt id="([^"]+)">(.*?)</dt><dd>(.*?)</dd>', main, flags=re.S):
        ZOEK.append({'u': f'{url}#{bid}', 'p': paginatitel, 'h': platte_tekst(term), 'x': platte_tekst(uitleg)})
    main = re.sub(r'<dl class="begrippen">.*?</dl>', ' ', main, flags=re.S)
    delen = re.split(r'(<h2[^>]*>.*?</h2>)', main, flags=re.S)
    ZOEK.append({'u': url, 'p': paginatitel, 'h': '', 'x': (omschrijving + ' ' + platte_tekst(delen[0]))[:3000]})
    for i in range(1, len(delen), 2):
        km = re.match(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', delen[i], re.S)
        if not km: continue
        tekst = platte_tekst(delen[i + 1] if i + 1 < len(delen) else '')
        if tekst: ZOEK.append({'u': f'{url}#{km.group(1)}', 'p': paginatitel, 'h': platte_tekst(km.group(2)), 'x': tekst[:8000]})

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
            '<strong>EU-witwasverordening (AMLR) vanaf 10 juli 2027.</strong> De kernregels voor cliëntenonderzoek komen dan in een rechtstreeks werkende EU-verordening. De nieuwe Europese witwasautoriteit AMLA is opgericht en gaat direct toezicht houden op een beperkt aantal grote instellingen; voor advieskantoren blijft de nationale toezichthouder het aanspreekpunt.',
            '<strong>DORA geldt sinds 17 januari 2025.</strong> De Europese regels voor digitale operationele weerbaarheid gelden voor onder meer banken en verzekeraars. Verzekeringstussenpersonen die een micro-, kleine of middelgrote onderneming zijn, vallen erbuiten; via hun leveranciers en volmachtgevers merken ze er wel iets van. De Wft-eis van een beheerste bedrijfsvoering blijft voor ICT-risico’s gelden.',
            '<strong>AI-verordening.</strong> Gefaseerde toepassing raakt advieskantoren via software, modellen en uitbesteding.'],
   bronnen=['wft', 'bgfo', 'eind', 'wwft', 'amlr', 'avg', 'idd', 'kifid', 'ai']),
 'consumptief-krediet': dict(
   onderwerpen=['Soorten krediet: doorlopend krediet, persoonlijke lening, private lease, BNPL, roodstand', 'Kredietwaardigheidstoets, leennormen en BKR-registratie',
                'Informatie: Europese standaardinformatie en JKP', 'Herroepingsrecht, vervroegd aflossen en opzeggen', 'Maximale kredietvergoeding (principe)',
                'Wft- en Wck-kader', 'Schuldhulp en betalingsproblemen', 'Zorgplicht, provisie en oversluiten', 'Wwft en AVG bij krediet'],
   actueel=['<strong>CCD II per 20 november 2026.</strong> De herziene richtlijn consumentenkrediet gaat gelden; de Nederlandse implementatiewet is nog in voorbereiding. Onder meer BNPL en huur of lease met koopoptie komen onder het kredietregime.',
            '<strong>Strengere kredietwaardigheidstoets onder CCD II.</strong> Krediet mag alleen worden verstrekt als uit de kredietwaardigheidsbeoordeling blijkt dat de consument waarschijnlijk aan zijn verplichtingen kan voldoen. Daarnaast komen er strengere eisen aan reclame en aan de informatie vooraf.'],
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
            '<strong>Nieuwe richtlijn productaansprakelijkheid.</strong> De EU-richtlijn 2024/2853 moet uiterlijk 9 december 2026 in Nederlandse wet zijn omgezet en geldt voor producten die daarna op de markt komen. Software, ook AI-systemen, telt dan als product. Bespreek met klanten die software maken of gebruiken in hun producten of de aansprakelijkheidsdekking daarop aansluit.',
            '<strong>Sanctiewetgeving.</strong> Blijft een vast aandachtspunt bij zakelijke klanten en buitenlandse belangen.'],
   bronnen=['bw7', 'wft', 'bgfo', 'idd', 'wwft', 'dora', 'ai']),
 'vermogen': dict(
   onderwerpen=['Vermogensopbouw en financiële planning', 'Sparen en het depositogarantiestelsel', 'Beleggen: aandelen, obligaties, fondsen, risico en spreiding',
                'Beleggingsverzekeringen, banksparen en lijfrente', 'Box 3 op hoofdlijnen', 'Schenken en erven', 'MiFID II: geschiktheid, klantclassificatie, kostentransparantie',
                'PRIIPs en essentiële-informatiedocument', 'SFDR en duurzaamheidsvoorkeuren', 'Zorgplicht en beleggersprofiel'],
   actueel=['<strong>Box 3.</strong> De Overbruggingswet box 3 geldt tot een nieuw stelsel in werking treedt; daarnaast loopt het rechtsherstel na het Kerstarrest. Werk met de regels van het betreffende belastingjaar.',
            '<strong>Crypto: MiCA en DAC8.</strong> Sinds 30 december 2024 hebben aanbieders van cryptodiensten in de EU een vergunning nodig onder de MiCA-verordening; in Nederland verleent de AFM die. Een vergunning beschermt niet tegen koersverlies en er is geen beleggerscompensatiestelsel voor crypto. Sinds 1 januari 2026 geven cryptodienstverleners in de EU gegevens over hun klanten door aan de belastingdienst (DAC8).',
            '<strong>EU-witwasverordening (AMLR) vanaf 10 juli 2027.</strong> De regels voor cliëntenonderzoek komen in een rechtstreeks werkende EU-verordening.'],
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
   actueel=['<strong>Arbeidsongeschiktheidsverzekering voor zelfstandigen.</strong> Een verplichte basisverzekering is in voorbereiding. Volg de stand van het wetsvoorstel; de huidige regels blijven gelden tot invoering.',
            '<strong>Handhaving schijnzelfstandigheid sinds 1 januari 2025.</strong> De Belastingdienst handhaaft weer op de beoordeling van arbeidsrelaties. Is een zzp’er in werkelijkheid werknemer, dan gelden de werknemersverzekeringen. Bespreek bij zzp-klanten hoe zeker hun status is; dat raakt hun inkomensrisico en de keuze voor een arbeidsongeschiktheidsverzekering.'],
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

TAKEN = {'basis': ['Informeren en doorverwijzen van de klant, het aangaan van de financiële relatie', 'Beheren van de relatie en het verlenen van service met betrekking tot financiële diensten'], 'consumptief-krediet': ['Inventariseren van de gegevens van de klant', 'Opstellen van de risicoanalyse ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing', 'Beheren en actueel houden van het advies'], 'hypothecair-krediet': ['Inventariseren van de gegevens van de klant', 'Opstellen van de risicoanalyse ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing, zowel financieel als organisatorisch', 'Beheren en actueel houden van het advies'], 'inkomen': ['Inventariseren van de gegevens van de klant', 'Analyseren van de gegevens van de klant ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing, zowel financieel als organisatorisch', 'Beheren en actueel houden van het advies', 'Begeleiden bij de schadebehandeling/claim'], 'pensioen': ['Inventariseren van de gegevens van de klant', 'Analyseren van de gegevens van de klant ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing, zowel financieel als organisatorisch', 'Beheren en actueel houden van het advies'], 'schade-particulier': ['Inventariseren van de gegevens van de klant', 'Opstellen van de risicoanalyse ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing, zowel financieel als organisatorisch', 'Beheren en actueel houden van het advies', 'Begeleiden bij de schadebehandeling/claim'], 'schade-zakelijk': ['Inventariseren van de gegevens van de klant', 'Opstellen van de risicoanalyse ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing, zowel financieel als organisatorisch', 'Beheren en actueel houden van het advies', 'Begeleiden bij de schadebehandeling/claim'], 'vermogen': ['Inventariseren van de gegevens van de klant', 'Opstellen van de risicoanalyse ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing, zowel financieel als organisatorisch', 'Beheren en actueel houden van het advies'], 'zorgverzekering': ['Inventariseren van de gegevens van de klant', 'Opstellen van de risicoanalyse ten behoeve van het advies', 'Adviseren (en eventueel bemiddelen) van een passende oplossing', 'Begeleiden bij het beheer van de zorg- en/of ziektekostenverzekering(en)', 'Begeleiden bij de schadebehandeling/claim']}
WIJZ = {'schade-particulier': 'Toetsterm 1d.9 is per 1 april 2026 aangepast: meer ruimte voor vragen over de ongevallenverzekering inzittenden (OVI) en de schadeverzekering inzittenden (SVI), de verschillen tussen beide en welke vorm bij de behoefte van de klant past.', 'inkomen': 'Toetsterm 1h.8 is per 1 april 2026 van kennis- naar begripsniveau gegaan: de wettelijke kaders voor het uitvragen van medische informatie, keuringsgrenzen en medische acceptatie moet je niet alleen kunnen beschrijven maar ook kunnen uitleggen en toepassen in een concrete situatie, zoals erfelijke aandoeningen en gezondheidsverklaring of keuring.'}
# lees modulegegevens uit modules.js
MODS = json.loads(subprocess.check_output(['node', '-e', "global.window={};eval(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(JSON.stringify(window.PA_MODULES))", R + 'assets/js/modules.js']))
PEIL_ISO = '2026-10-15'
# vragenbank per module (assets/js/vragen/<id>.js); de toets laadt alleen de gekozen modules
VRAGEN = json.loads(subprocess.check_output(['node', '-e', "global.window={};for(const f of process.argv.slice(1))eval(require('fs').readFileSync(f,'utf8'));process.stdout.write(JSON.stringify(window.PA_VRAGEN))"]
                                            + [R + f'assets/js/vragen/{m["id"]}.js' for m in MODS]))
VRAGEN_V = {m['id']: hashlib.sha1(open(R + f'assets/js/vragen/{m["id"]}.js', 'rb').read()).hexdigest()[:8] for m in MODS}

def voorbeelden(mid, n=3):
    """Vaste voorbeeldvragen per module voor de modulepagina: bij voorkeur casussen, verspreid over de vragenbank."""
    vs = VRAGEN.get(mid, [])
    kand = [q for q in vs if len(q[0]) > 220]
    if len(kand) < n * 3: kand = sorted(vs, key=lambda q: -len(q[0]))[:max(n * 3, len(kand))]
    stap = max(1, len(kand) // n)
    return [kand[(i * stap + stap // 2) % len(kand)] for i in range(min(n, len(kand)))]

def voorbeeld_html(q, nr):
    term = f' <span class="term">toetsterm CDFD {html.escape(q[2])}</span>' if len(q) > 2 and q[2] else ''
    opties = sorted(q[1], key=lambda a: a[0].lower())
    return (f'    <article class="voorbeeld"><h3>Voorbeeldvraag {nr}{term}</h3>\n      <p>{html.escape(q[0])}</p>\n      <ul>'
            + ''.join(f'<li>{html.escape(a[0])}</li>' for a in opties) + '</ul>\n'
            f'      <details><summary>Bekijk het antwoord en de uitleg</summary><p><strong>Juist: {html.escape(q[1][0][0])}.</strong> {html.escape(q[1][0][1])}</p>'
            '<ul class="uitleg">' + ''.join(f'<li><strong>{html.escape(a[0])}</strong>: {html.escape(a[1])}</li>' for a in q[1][1:]) + '</ul>'
            + f'<p class="meld"><a href="{html.escape(meld_href(q))}">Twijfel je over deze vraag of het antwoord? Mail hem direct naar DFO</a></p></details></article>\n')

def meld_href(q):
    body = (f'Vraag:\n{q[0]}\n\nAntwoorden:\n' + '\n'.join(f'- {a[0]}' + ('  [gegeven als juist]' if k == 0 else '') for k, a in enumerate(q[1]))
            + f'\n\nUitleg bij het juiste antwoord:\n{q[1][0][1]}\n\nMijn twijfel:\n')
    if len(q) > 2 and q[2]: body = f'Toetsterm CDFD: {q[2]}\n\n' + body
    return 'mailto:info@dfobv.nl?subject=' + urllib.parse.quote('check deze vraag op PA-WFT.nl') + '&body=' + urllib.parse.quote(body)

def termen_html(mid):
    """Oefenlinks per CDFD-toetsterm (alleen als de vragen een toetsterm hebben)."""
    tel = {}
    for q in VRAGEN.get(mid, []):
        if len(q) > 2 and q[2]: tel[q[2]] = tel.get(q[2], 0) + 1
    if not tel: return ''
    sleutel = lambda t: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', t)]
    return ('    <h2>Oefen per toetsterm</h2>\n    <p>Oefen alleen de vragen bij één toetsterm van het CDFD, bijvoorbeeld een onderwerp dat je lastig vindt. Een oefenronde telt niet mee voor het certificaat.</p>\n'
            '    <ul class="termen">' + ''.join(f'<li><a href="toets.html#term={mid}:{t}">{t}</a></li>' for t in sorted(tel, key=sleutel)) + '</ul>\n')

def quiz_ld(naam, qs):
    return {'@type': 'Quiz', 'name': f'Voorbeeldvragen Wft {naam}', 'inLanguage': 'nl', 'isAccessibleForFree': True, 'educationalLevel': 'Beroepsniveau',
            'about': {'@type': 'Thing', 'name': f'Wft {naam}'},
            'hasPart': [{'@type': 'Question', 'eduQuestionType': 'Multiple choice', 'learningResourceType': 'Practice problem', 'text': q[0],
                         'acceptedAnswer': {'@type': 'Answer', 'text': q[1][0][0], 'answerExplanation': {'@type': 'Comment', 'text': q[1][0][1]}},
                         'suggestedAnswer': [{'@type': 'Answer', 'text': a[0]} for a in q[1][1:]]} for q in qs]}
BIJGEWERKT = {}
MAANDEN = ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december']
def nl(iso): j, m, d = iso.split('-'); return f'{int(d)} {MAANDEN[int(m)-1]} {j}'

LAATSTE = max(m['bijgewerkt'] for m in MODS)
BIJGEWERKT.update({'index.html': LAATSTE, 'toets.html': LAATSTE})
BEGRIPPEN = [
 ('AFM', 'Autoriteit Financiële Markten: de gedragstoezichthouder. De AFM houdt toezicht op hoe financiële ondernemingen zich gedragen tegenover klanten, verleent vergunningen aan adviseurs en bemiddelaars en ziet toe op de vakbekwaamheid.', ['basis']),
 ('DNB', 'De Nederlandsche Bank: de prudentiële toezichthouder. DNB let op de financiële soliditeit van banken, verzekeraars en pensioenfondsen.', ['basis', 'pensioen']),
 ('CDFD', 'College Deskundigheid Financiële Dienstverlening. Het CDFD stelt de eind- en toetstermen van de Wft-examens vast en erkent de examen-instituten die Wft- en PE-examens afnemen.', ['basis']),
 ('Wft', 'Wet op het financieel toezicht: de hoofdwet voor het toezicht op de financiële sector, met onder meer regels voor vergunningen, vakbekwaamheid, informatieverstrekking en zorgplicht.', ['basis']),
 ('Beroepskwalificatie', 'De combinatie van Wft-modules die je nodig hebt om in een bepaald domein te adviseren, bijvoorbeeld Adviseur Hypothecair krediet (Basis, Vermogen en Hypothecair krediet).', ['basis']),
 ('PE-examen', 'Examen voor permanente educatie. Wie adviseert, haalt binnen elke PE-periode per beroepskwalificatie één PE-examen bij een door het CDFD erkend examen-instituut. Het toetst vooral de actuele ontwikkelingen.', ['basis']),
 ('PE-periode', 'De periode waarbinnen je je PE-examens haalt. De lopende PE-periode loopt van 1 april 2025 tot en met 31 maart 2028.', ['basis']),
 ('PE-punten', 'Een systeem van punten voor permanente educatie dat onder de Wft niet meer bestaat. Sinds 1 januari 2014 houd je je adviesbevoegdheid geldig met PE-examens.', ['basis']),
 ('Permanent actueel', 'De eis dat medewerkers met inhoudelijk klantcontact hun vakkennis bijhouden en kunnen toepassen. Het is een open norm: de onderneming bepaalt zelf hoe ze die invult en is ervoor verantwoordelijk.', ['basis']),
 ('Eindterm en toetsterm', 'Eindtermen beschrijven wat een kandidaat moet kunnen; toetstermen werken dat uit in toetsbare kennis en vaardigheden. Het CDFD stelt ze vast; de huidige gelden voor examens vanaf 1 april 2026.', ['basis']),
 ('Zorgplicht', 'De plicht van een financiële dienstverlener om zorgvuldig te handelen en rekening te houden met de belangen van de klant, onder meer door passend te adviseren.', ['basis']),
 ('Klantprofiel', 'Het beeld van de klant dat de adviseur vastlegt: financiële positie, kennis en ervaring, doelstellingen en risicobereidheid. Het is de basis voor een passend advies.', ['basis']),
 ('Provisieverbod', 'Het verbod om voor bepaalde producten, zoals hypotheken en complexe producten, provisie van de aanbieder te ontvangen. De klant betaalt de adviseur dan zelf.', ['basis', 'hypothecair-krediet']),
 ('Kifid', 'Klachteninstituut Financiële Dienstverlening: behandelt klachten van consumenten over financiële dienstverleners als die er met de dienstverlener zelf niet uitkomen.', ['basis']),
 ('Wwft', 'Wet ter voorkoming van witwassen en financieren van terrorisme. De wet verplicht onder meer tot cliëntenonderzoek en het melden van ongebruikelijke transacties.', ['basis', 'vermogen']),
 ('AMLR', 'De EU-anti-witwasverordening. Vanaf 10 juli 2027 staan de kernregels voor cliëntenonderzoek in deze rechtstreeks werkende verordening.', ['basis', 'vermogen']),
 ('DORA', 'Digital Operational Resilience Act: Europese regels voor de digitale weerbaarheid van financiële instellingen, van toepassing sinds 17 januari 2025. Kleine en middelgrote verzekeringstussenpersonen vallen erbuiten.', ['basis']),
 ('IDD', 'Insurance Distribution Directive: de Europese richtlijn voor de distributie van verzekeringen, met onder meer eisen aan informatie, belangenconflicten en vakbekwaamheid.', ['basis', 'schade-particulier', 'schade-zakelijk']),
 ('CCD II', 'De herziene Europese richtlijn consumentenkrediet (2023/2225). Hij geldt vanaf 20 november 2026 en brengt onder meer achteraf betalen via een externe aanbieder en lease met koopoptie onder het kredietregime.', ['consumptief-krediet']),
 ('BKR', 'Bureau Krediet Registratie: registreert kredieten van consumenten. Kredietgevers raadplegen het register bij een aanvraag.', ['consumptief-krediet', 'hypothecair-krediet']),
 ('NHG', 'Nationale Hypotheek Garantie: een borgstelling voor hypotheken tot een jaarlijks vastgestelde grens. Bij gedwongen verkoop met restschuld kan de borgstelling die schuld onder voorwaarden overnemen.', ['hypothecair-krediet']),
 ('Leennormen', 'De regels die bepalen hoeveel iemand maximaal mag lenen voor een eigen woning: de financieringslast als deel van het inkomen en de lening ten opzichte van de woningwaarde. Ze worden jaarlijks vastgesteld.', ['hypothecair-krediet']),
 ('Aflossingseis', 'Voor renteaftrek op een hypotheek die na 2012 is afgesloten, moet de lening in maximaal 30 jaar ten minste annuïtair worden afgelost.', ['hypothecair-krediet']),
 ('OVI', 'Ongevallenverzekering inzittenden: keert een vast bedrag uit bij overlijden of blijvende invaliditeit van inzittenden door een verkeersongeval, ongeacht wie schuld heeft.', ['schade-particulier']),
 ('SVI', 'Schadeverzekering inzittenden: vergoedt de werkelijke schade van inzittenden bij een verkeersongeval, zoals letselschade en schade aan spullen, ongeacht wie schuld heeft.', ['schade-particulier']),
 ('Onderverzekering', 'Als het verzekerde bedrag lager is dan de werkelijke waarde, vergoedt de verzekeraar de schade naar evenredigheid, tenzij de polis een garantie tegen onderverzekering geeft.', ['schade-particulier', 'schade-zakelijk']),
 ('Mededelingsplicht', 'De wettelijke plicht van de verzekeringnemer om vóór het sluiten van een verzekering alle feiten te melden die hij kent en die van belang zijn voor de beslissing van de verzekeraar.', ['schade-particulier', 'schade-zakelijk', 'inkomen']),
 ('AVB', 'Aansprakelijkheidsverzekering voor bedrijven: dekt schade aan personen of zaken van anderen waarvoor een bedrijf aansprakelijk is.', ['schade-zakelijk']),
 ('Bedrijfsschadeverzekering', 'Vergoedt het verlies aan brutowinst en doorlopende vaste kosten als het bedrijf na een gedekte gebeurtenis, zoals brand, stil komt te liggen, gedurende de uitkeringstermijn.', ['schade-zakelijk']),
 ('Productaansprakelijkheid', 'De aansprakelijkheid van een producent voor schade door een gebrekkig product, zonder dat schuld hoeft te worden bewezen. Onder de nieuwe EU-richtlijn telt ook software als product.', ['schade-zakelijk']),
 ('Box 3', 'De box in de inkomstenbelasting voor inkomen uit sparen en beleggen. Belast wordt een rendement over het vermogen op de peildatum.', ['vermogen']),
 ('MiCA', 'Markets in Crypto-Assets: de Europese verordening voor cryptodiensten. Sinds 30 december 2024 hebben aanbieders van cryptodiensten in de EU een vergunning nodig.', ['vermogen']),
 ('DAC8', 'Europese regels waardoor cryptodienstverleners sinds 1 januari 2026 gegevens over hun klanten doorgeven aan de belastingdienst.', ['vermogen']),
 ('Risicoprofiel', 'De mate waarin een klant risico wil en kan lopen met beleggen. De adviseur stelt het vast op basis van doelstellingen, financiële positie, kennis en ervaring.', ['vermogen']),
 ('WIA', 'Wet werk en inkomen naar arbeidsvermogen: de regeling voor werknemers die na twee jaar ziekte arbeidsongeschikt zijn, met de IVA en de WGA.', ['inkomen']),
 ('IVA', 'Inkomensvoorziening volledig arbeidsongeschikten: de WIA-uitkering voor wie volledig en duurzaam arbeidsongeschikt is.', ['inkomen']),
 ('WGA', 'Werkhervatting gedeeltelijk arbeidsgeschikten: de WIA-regeling voor wie gedeeltelijk of niet duurzaam arbeidsongeschikt is.', ['inkomen']),
 ('AOV', 'Arbeidsongeschiktheidsverzekering: een particuliere verzekering waarmee een zelfstandige zijn inkomen verzekert bij arbeidsongeschiktheid.', ['inkomen']),
 ('Schijnzelfstandigheid', 'Als iemand formeel als zzp’er werkt, maar de arbeidsrelatie in werkelijkheid een dienstbetrekking is. De Belastingdienst handhaaft hier sinds 1 januari 2025 weer op.', ['inkomen']),
 ('Wtp', 'Wet toekomst pensioenen: het nieuwe pensioenstelsel met premieregelingen. Pensioenregelingen moeten uiterlijk op 1 januari 2028 zijn overgegaan.', ['pensioen']),
 ('Invaren', 'Het omzetten van opgebouwde pensioenaanspraken naar het nieuwe pensioenstelsel van de Wtp.', ['pensioen']),
 ('UPO', 'Uniform Pensioenoverzicht: het jaarlijkse overzicht van de pensioenuitvoerder met de opgebouwde en te bereiken pensioenaanspraken.', ['pensioen']),
 ('AOW', 'Algemene Ouderdomswet: het basispensioen van de overheid vanaf de AOW-leeftijd.', ['pensioen']),
 ('Eigen risico (Zvw)', 'Het verplichte bedrag per kalenderjaar dat een verzekerde van 18 jaar of ouder zelf betaalt voor zorg uit het basispakket, met uitzonderingen zoals de huisarts. De hoogte wordt jaarlijks vastgesteld.', ['zorgverzekering']),
 ('Naturapolis', 'Een zorgverzekering waarbij de verzekeraar afspraken maakt met zorgaanbieders. Bij een niet-gecontracteerde zorgaanbieder kan de vergoeding lager zijn.', ['zorgverzekering']),
 ('Restitutiepolis', 'Een zorgverzekering waarbij de verzekerde zelf de zorgaanbieder kiest en de kosten worden vergoed, tot maximaal een marktconform tarief.', ['zorgverzekering']),
 ('Acceptatieplicht', 'De plicht van een zorgverzekeraar om iedereen te accepteren voor de basisverzekering, zonder premieverschil op basis van gezondheid.', ['zorgverzekering']),
]

NIEUW = {}
# Beroepskwalificaties en de modules die erbij horen (AFM, vakbekwaamheidseisen); gelijk aan KWAL in assets/js/main.js
KWAL = [('Adviseur Hypothecair krediet', ['basis', 'vermogen', 'hypothecair-krediet']), ('Adviseur Vermogen', ['basis', 'vermogen']),
        ('Adviseur Pensioen', ['basis', 'vermogen', 'pensioen']), ('Adviseur Consumptief krediet', ['basis', 'consumptief-krediet']),
        ('Adviseur Schadeverzekering zakelijk', ['basis', 'schade-particulier', 'schade-zakelijk']), ('Adviseur Schadeverzekering particulier', ['basis', 'schade-particulier']),
        ('Adviseur Inkomen', ['basis', 'inkomen']), ('Adviseur Zorgverzekering', ['zorgverzekering'])]

def kort_html(mid, naam, bij, nieuw):
    kw = [k for k, ms in KWAL if mid in ms]
    m = re.match(r'<strong>(.*?)\.?</strong>\s*(.*)', nieuw[0], re.S)
    zin = lambda t: t[:1].lower() + t[1:] if len(t) > 1 and not t[1].isupper() else t
    eerste = (m.group(1) + ': ' + zin(re.sub(r'<[^>]+>', '', m.group(2)).split('. ')[0])).rstrip('.') if m else re.sub(r'<[^>]+>', '', nieuw[0]).split('. ')[0].rstrip('.')
    items = [f'<strong>Voor wie:</strong> nodig voor {len(kw)} beroepskwalificatie{"s" if len(kw) != 1 else ""}: ' + ', '.join(kw) + '.',
             '<strong>PE:</strong> je haalt per beroepskwalificatie één PE-examen binnen de PE-periode, die loopt tot en met 31 maart 2028.',
             '<strong>Toetstermen:</strong> de eind- en toetstermen van het CDFD zijn vernieuwd voor examens vanaf 1 april 2026.' + (' Daarbij is een toetsterm voor deze module gewijzigd.' if mid in WIJZ else ''),
             f'<strong>Actueel:</strong> {html.escape(eerste)}.',
             f'<strong>Oefenen:</strong> 7 meerkeuzevragen met uitleg bij alle antwoorden, gratis en zonder account. Laatst bijgewerkt {nl(bij)}.']
    return '    <div class="kort"><h2>Wft ' + html.escape(naam) + ' in het kort</h2><ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul></div>\n'

def verwant_html(mid):
    ids = []
    for k, ms in KWAL:
        if mid in ms: ids += [m for m in ms if m != mid and m not in ids]
    if not ids: return ''
    naam = {m['id']: m['naam'] for m in MODS}
    return ('    <h2>Verwante modules</h2>\n    <p>Deze modules horen bij dezelfde beroepskwalificaties. Oefen ze samen in één toets: '
            + f'<a href="toets.html#mix={",".join([mid] + ids)}">toets met alle {len(ids) + 1} modules</a>.</p>\n    <ul>'
            + ''.join(f'<li><a href="module-{i}.html">Wft {html.escape(naam[i])}</a></li>' for i in ids) + '</ul>\n')
# Belangrijke datums (alleen vaststaande datums uit wet- en regelgeving); modules waarvoor ze gelden
ALLE = ['basis', 'consumptief-krediet', 'hypothecair-krediet', 'schade-particulier', 'schade-zakelijk', 'vermogen', 'inkomen', 'pensioen', 'zorgverzekering']
DATUMS = [
    ('2024-12-30', 'MiCA volledig van toepassing', 'Aanbieders van cryptodiensten in de EU hebben een vergunning nodig.', ['vermogen']),
    ('2025-01-01', 'Handhaving schijnzelfstandigheid', 'De Belastingdienst handhaaft weer op de beoordeling van arbeidsrelaties.', ['inkomen']),
    ('2025-01-17', 'DORA van toepassing', 'Europese regels voor digitale operationele weerbaarheid van financiële instellingen.', ['basis']),
    ('2025-04-01', 'Start PE-periode 2025–2028', 'Binnen deze periode haal je per beroepskwalificatie één PE-examen.', ALLE),
    ('2026-01-01', 'DAC8 van toepassing', 'Cryptodienstverleners in de EU geven klantgegevens door aan de belastingdienst.', ['vermogen']),
    ('2026-04-01', 'Nieuwe toetstermen CDFD', 'Vernieuwde eind- en toetstermen voor alle Wft-modules.', ALLE),
    ('2026-11-20', 'CCD II gaat gelden', 'De herziene richtlijn consumentenkrediet: strengere kredietwaardigheidstoets, ook BNPL en lease met koopoptie.', ['consumptief-krediet']),
    ('2026-12-09', 'Omzetting nieuwe richtlijn productaansprakelijkheid', 'Uiterste datum voor de Nederlandse wet; software telt als product.', ['schade-zakelijk', 'schade-particulier']),
    ('2027-01-01', 'Jaarlijkse wijzigingen', 'Nieuwe jaarversies van onder meer de leennormen, NHG-normen, zorgpremies en eigen risico, en fiscale bedragen.', ['hypothecair-krediet', 'zorgverzekering', 'vermogen', 'inkomen', 'pensioen']),
    ('2027-04-01', 'PE-examens opnieuw geactualiseerd', 'Het CDFD actualiseert de PE-examens elk jaar per 1 april en liet ontwikkelingen voor de examens vanaf 1 april 2027 aanmelden.', ALLE),
    ('2027-07-10', 'EU-witwasverordening (AMLR) gaat gelden', 'De kernregels voor cliëntenonderzoek komen in een rechtstreeks werkende EU-verordening.', ['basis', 'vermogen', 'hypothecair-krediet', 'consumptief-krediet']),
    ('2028-01-01', 'Uiterste datum overgang nieuw pensioenstelsel', 'Pensioenregelingen moeten zijn overgegaan naar het stelsel van de Wet toekomst pensioenen.', ['pensioen']),
    ('2028-03-31', 'Einde PE-periode 2025–2028', 'Uiterste datum om je PE-examen per beroepskwalificatie te halen.', ALLE),
]

def datums_html(mid=None, kop='h2'):
    rij = [d for d in DATUMS if mid is None or mid in d[3]]
    if not rij: return ''
    naam = {m['id']: m['naam'] for m in MODS}
    def mods(d): return '' if mid or len(d[3]) == len(ALLE) else ' <span class="datums-mods">' + ', '.join('Wft ' + naam[x] for x in d[3]) + '</span>'
    def li(d): return f'<li><time datetime="{d[0]}">{nl(d[0])}</time><span><strong>{html.escape(d[1])}.</strong> {html.escape(d[2])}{mods(d)}</span></li>'
    komend = [d for d in rij if d[0] > PEIL_ISO]; recent = [d for d in rij if d[0] <= PEIL_ISO]
    uit = f'    <{kop}>Belangrijke datums</{kop}>\n'
    if komend: uit += '    <p class="datums-kop">Binnenkort</p>\n    <ul class="datums">' + ''.join(li(d) for d in komend) + '</ul>\n'
    if recent: uit += '    <p class="datums-kop">Recent ingegaan</p>\n    <ul class="datums recent">' + ''.join(li(d) for d in reversed(recent)) + '</ul>\n'
    return uit
for i, mod in enumerate(MODS, 1):
    BIJGEWERKT[f"module-{mod['id']}.html"] = mod['bijgewerkt']
    mid, naam, bij, tekst = mod['id'], mod['naam'], mod['bijgewerkt'], mod['tekst']
    d = M[mid]
    vb = voorbeelden(mid)
    nieuw = (['<strong>Nieuwe toetstermen CDFD per 1 april 2026.</strong> De eind- en toetstermen voor deze module zijn vernieuwd en gelden voor examens vanaf 1 april 2026. De vragen in de toets zijn erop afgestemd.']
             + ([f'<strong>Gewijzigde toetsterm.</strong> {WIJZ[mid]}'] if mid in WIJZ else []) + d['actueel'])
    NIEUW[mid] = nieuw
    inh = (f'    <p class="lead">{html.escape(tekst)} Oefen gratis met PE-oefenvragen voor Wft {html.escape(naam)}, met uitleg bij elk antwoord.</p>\n'
           f'    <p class="meta-regel">Laatst bijgewerkt {nl(bij)} · peildatum regelgeving {PEIL}</p>\n'
           f'    <div class="acties"><a class="btn" href="toets.html#{mid}">Doe de toets</a><a class="btn ghost" href="index.html#modules">Alle modules</a></div>\n'
           + kort_html(mid, naam, bij, d['actueel']) +
           '    <h2>Wat komt aan bod</h2>\n    <ul>' + ''.join(f'<li>{o}</li>' for o in d['onderwerpen']) + '</ul>\n'
           '    <h2>Wat is er nieuw in 2026</h2>\n    <ul>' + ''.join(f'<li>{a}</li>' for a in nieuw) + '</ul>\n'
           + datums_html(mid)
           + '    <h2>Toetstermen CDFD per 1 april 2026</h2>\n    <p>De eind- en toetstermen van het CDFD voor deze module zijn ingedeeld in taken:</p>\n    <ol>' + ''.join(f'<li>{html.escape(t)}</li>' for t in TAKEN[mid]) + '</ol>\n'

           + '    <p class="klein">Bron: eind- en toetstermen per module van het CDFD, geldend voor examens vanaf 1 april 2026. De volledige documenten staan bij de <a href="https://cdfd.nl/downloads/" target="_blank" rel="noopener">downloads van het CDFD</a>.</p>\n'
           f'    <h2>Voorbeeldvragen Wft {html.escape(naam)}</h2>\n    <p>Zo zien de vragen in de toets eruit. In de toets staan de antwoorden in willekeurige volgorde.</p>\n'
           + ''.join(voorbeeld_html(q, k) for k, q in enumerate(vb, 1))
           + f'    <div class="acties"><a class="btn" href="toets.html#{mid}">Oefen verder in de toets</a></div>\n'
           + termen_html(mid)
           + verwant_html(mid)
           + ('    <h2>Begrippen bij deze module</h2>\n    <p>' + ' · '.join(f'<a href="begrippen.html#begrip-{slug(b[0])}">{html.escape(b[0])}</a>' for b in BEGRIPPEN if mid in b[2]) + '</p>\n' if any(mid in b[2] for b in BEGRIPPEN) else '')
           + '    <h2>Wijzigingen</h2>\n    <ul class="log">' + ''.join(f'<li><strong>{nl(dt)}</strong> — {html.escape(t)}</li>' for dt, t in mod['log']) + '</ul>\n'
           '    <h2>Bronnen</h2>\n    <ul class="bronnen">' + ''.join(f'<li><a href="{B[b][1]}" target="_blank" rel="noopener">{B[b][0]}</a></li>' for b in d['bronnen']) + '</ul>\n'
           + '  ' + NIEUWSBRIEVEN +
           f'    <p class="klein">Dit overzicht helpt je je kennis bij te houden en is geen leerstof voor een erkend PE-examen. Controleer bedragen en normen altijd in de geldende bron. Zie je een fout? Mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Course', 'name': f'Wft {naam} — Permanent Actueel', 'description': f'Gratis PE-oefenvragen Wft {naam}: meerkeuzevragen met uitleg, een toets van 7 vragen (5 extra per toegevoegde module) en een certificaat. {tekst}',
         'url': f'{SITE}module-{mid}.html', 'inLanguage': 'nl', 'isAccessibleForFree': True, 'educationalLevel': 'Beroepsniveau', 'teaches': d['onderwerpen'][:6],
         'dateModified': bij, 'provider': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'},
         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR', 'category': 'Gratis'},
         'hasCourseInstance': {'@type': 'CourseInstance', 'courseMode': 'online', 'courseWorkload': 'PT10M'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Wft Permanent Actueel', 'item': SITE},
                                                        {'@type': 'ListItem', 'position': 2, 'name': f'Wft {naam}', 'item': f'{SITE}module-{mid}.html'}]},
        quiz_ld(naam, vb)]}
    titel = f'Wft {naam} 2026: gratis PE-oefenvragen en actualiteit'
    if len(titel) > 60: titel = f'Wft {naam} 2026: gratis PE-oefenvragen'
    if len(titel) > 60: titel = f'Wft {naam} 2026: gratis oefenvragen'
    oms = f'Wft {naam}: gratis oefenvragen met praktijkcasussen en uitleg, wat er nieuw is in 2026, belangrijke datums en toetstermen. Oefentoets voor adviseurs.'
    if len(oms) > 160: oms = f'Wft {naam}: gratis oefenvragen met uitleg, wat er nieuw is in 2026 en belangrijke datums. Oefentoets voor adviseurs.'
    pagina(f'module-{mid}.html', titel, oms,
           f'Wft {html.escape(naam)}', f'Module {i:02d} · Permanent Actueel', inh, ld=ld)

# ---------- Veelgestelde vragen ----------
# ---------- wat is er nieuw (kwartaaloverzicht) ----------
KWARTAAL = f'{(int(PEIL_ISO[5:7]) - 1) // 3 + 1}e kwartaal {PEIL_ISO[:4]}'
inh = (f'    <p class="lead">Wat is er nieuw voor financieel adviseurs in het {KWARTAAL}? Per Wft-module de wijzigingen in wet- en regelgeving, toetstermen en markt die je moet kennen om permanent actueel te blijven.</p>\n'
       f'    <p class="meta-regel">Peildatum regelgeving {PEIL}</p>\n'
       '    <div class="acties"><a class="btn" href="toets.html">Doe de kennistoets</a></div>\n'
       + datums_html()
       + ''.join(f'    <h2 id="{m["id"]}"><a href="module-{m["id"]}.html">Wft {html.escape(m["naam"])}</a></h2>\n    <ul>' + ''.join(f'<li>{x}</li>' for x in NIEUW[m['id']]) + f'</ul>\n    <p><a href="toets.html#{m["id"]}">Test je kennis van Wft {html.escape(m["naam"])} →</a></p>\n' for m in MODS)
       + '  ' + NIEUWSBRIEVEN
       + '    <p class="klein">Dit overzicht helpt je je kennis bij te houden en is geen advies. Controleer bedragen en normen altijd in de geldende bron. Zie je een fout? Mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': f'Wat is er nieuw in de Wft: {KWARTAAL}', 'inLanguage': 'nl', 'dateModified': LAATSTE,
      'author': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'}, 'publisher': {'@type': 'Organization', 'name': 'DFO BV'},
      'mainEntityOfPage': f'{SITE}nieuw.html', 'about': [f'Wft {m["naam"]}' for m in MODS]}
BIJGEWERKT['nieuw.html'] = LAATSTE
pagina('nieuw.html', f'Wat is er nieuw in de Wft: {KWARTAAL}', f'Wat is er nieuw voor financieel adviseurs in het {KWARTAAL}: per Wft-module de wijzigingen in regelgeving, toetstermen en markt.',
       f'Wat is er nieuw: {KWARTAAL}', 'Permanent Actueel', inh, ld=ld, og_type='article')

FAQ = [
 ('Wat is permanente educatie (PE)?', 'Wie in de financiële dienstverlening adviseert, moet vakbekwaam zijn en blijven. Daarvoor heb je een Wft-diploma nodig en houd je je kennis bij met permanente educatie. Binnen elke PE-periode haal je één PE-examen per beroepskwalificatie; de lopende periode loopt van 1 april 2025 tot en met 31 maart 2028. De actuele periode en eisen vind je bij het <a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD</a>.'),
 ('Telt deze toets mee voor mijn PE?', 'Nee. De PA-toets is een oefentoets. Hij helpt je je kennis te testen en bij te houden, maar is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid. Je PE-examen leg je af bij een door het CDFD erkend examencentrum.'),
 ('Levert de toets PE-punten op?', 'Nee. Onder de Wft bestaan geen PE-punten meer: je houdt je diploma’s geldig met PE-examens. De PA-toets is een gratis oefentoets en levert geen PE-punten of PE-examen op. Lees meer in <a href="pe-punten-wft.html">PE-punten en Wft Permanent Actueel</a>.'),
 ('Wat kost het?', 'Niets. Alle modules en de toets zijn gratis voor alle adviseurs, zonder abonnement en zonder account. Wft Permanent Actueel is een activiteit van DFO BV.'),
 ('Hoe werkt de toets?', 'Je kiest een of meer modules. Bij één module krijg je 7 willekeurige vragen, en voor elke module die je toevoegt 5 extra: 2 modules geven 12 vragen, 3 modules 17, alle 9 modules 47. Na elk antwoord zie je de uitleg. Daarna ontvang je een certificaat met je resultaat, als pdf in je mail of om te printen. Je kunt de toets zo vaak doen als je wilt; je krijgt steeds andere vragen.'),
 ('Hoe vaak doe ik de toets?', 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Op de homepage en in de toets zet je met één klik een herinnering in je agenda: elk kwartaal, de komende 5 jaar, met een link naar de toets. Bewaar elk certificaat in je personeelsdossier en lever het ook in bij je werkgever. Zo laat je zien dat je je kennis bijhoudt. Het certificaat vervangt je PE-examen niet.'),
 ('Wat staat er op het certificaat?', 'Je naam, de module, je resultaat, de datum, de datum waarop de vragen van die module voor het laatst zijn bijgewerkt en een certificaatnummer. Een kopie van het certificaat gaat naar DFO BV (info@dfobv.nl) zodra jij het mailbericht verstuurt.'),
 ('Waarom moet ik mijn gegevens invullen om mijn uitslag te zien?', 'Zo zetten we je certificaat als pdf klaar in een mail aan jezelf, met een kopie aan DFO BV (info@dfobv.nl). Je vult je naam en e-mailadres in en gaat akkoord met die kopie; geboortedatum, bedrijf en e-mailadres van je werkgever zijn optioneel. Oefenrondes, zoals je foute vragen opnieuw oefenen of oefenen per toetsterm, vragen geen gegevens.'),
 ('Wat gebeurt er met mijn gegevens?', 'PA-WFT.nl zelf slaat niets op en stuurt niets automatisch naar een server: je browser maakt het certificaat. Het certificaat staat klaar in een mail aan jezelf met een kopie aan DFO BV (info@dfobv.nl); jij verstuurt dat bericht zelf vanuit je mailprogramma. Zie de <a href="privacy.html">privacyverklaring</a>.'),
 ('Welke modules heb ik nodig?', 'Dat hangt af van je beroepskwalificaties. Een beroepskwalificatie bestaat uit een combinatie van modules, bijvoorbeeld Adviseur Hypothecair krediet: Basis, Vermogen en Hypothecair krediet. Kies je kwalificaties in de <a href="index.html#check">pakketcheck</a> op de homepage en controleer de eisen die voor jou gelden bij het CDFD.'),
 ('Hoe actueel zijn de vragen?', 'Per module zie je wanneer de vragen voor het laatst zijn bijgewerkt. De peildatum van de regelgeving is ' + PEIL + '. Bedragen en percentages die elk jaar wijzigen, zitten bewust niet in de vragen.'),
 ('Ik zie een fout in een vraag. Wat nu?', 'Graag horen we het. Mail de vraag en wat er volgens jou niet klopt naar <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.'),
]
inh = '\n'.join(f'    <details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)
ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}
pagina('vragen.html', 'Veelgestelde vragen — Wft Permanent Actueel', 'Antwoorden op veelgestelde vragen over de gratis Wft-kennistoets, PE-examens, PE-punten, permanent actueel blijven en het certificaat.',
       'Veelgestelde vragen', 'Vragen', inh, actief='vragen.html', ld=ld)

# ---------- Privacy ----------
inh = f'''    <p class="lead">Wft Permanent Actueel gebruikt geen cookies en geen trackers. Je gegevens gebruiken we alleen om je uitslag en certificaat te maken; een kopie van het certificaat gaat naar DFO BV.</p>
    <h2>Wie is verantwoordelijk</h2>
    <p>DFO BV, De Wel 14–16, 3871 MV Hoevelaken. Vragen over privacy: <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>
    <h2>De toets en het certificaat</h2>
    <p>Om je uitslag te zien vul je je naam en e-mailadres in, en desgewenst je geboortedatum, het bedrijf waar je werkt en het e-mailadres van je werkgever voor een extra kopie. Je gaat daarbij akkoord met een kopie van je certificaat aan DFO BV. Je browser gebruikt die gegevens om het certificaat te maken; PA-WFT.nl slaat ze niet zelf op en stuurt ze niet automatisch naar een server. Het certificaat wordt als pdf klaargezet in een mail aan jezelf, met een kopie aan DFO BV (info@dfobv.nl). Jij verstuurt dat bericht zelf vanuit je mailprogramma: verstuur je het niet, dan ontvangt DFO BV niets en krijg je het certificaat niet in je mailbox. Oefenrondes, zoals je foute vragen opnieuw oefenen of oefenen per toetsterm, vragen geen gegevens. Sluit je het tabblad, dan zijn de gegevens uit je browser weg.</p>
    <h2>Wat DFO BV met de kopie doet</h2>
    <p>DFO BV ontvangt de kopie in de mailbox info@dfobv.nl. Dat zijn de gegevens op het certificaat: je naam, e-mailadres, het resultaat, de modules en de datum, plus je geboortedatum, bedrijf en e-mailadres van je werkgever als je die hebt ingevuld. De grondslag is je toestemming: je vinkt aan dat je akkoord gaat met de kopie. DFO BV bewaart de mail niet langer dan nodig en gebruikt de gegevens niet voor andere doeleinden dan het bevestigen van je deelname aan de oefentoets.</p>
    <h2>Cookies en meten</h2>
    <p>We gebruiken geen cookies, geen analyse- of advertentiediensten en geen trackers. Het lettertype staat op onze eigen site, zodat er geen gegevens naar externe partijen gaan.</p>
    <h2>Hosting</h2>
    <p>Deze site plaatst geen cookies, ook niet voor het onthouden van keuzes. De site wordt gehost via GitHub Pages (GitHub, Inc.). Zoals elke webserver verwerkt GitHub technische gegevens zoals je IP-adres om de pagina’s te kunnen leveren en te beveiligen. Zie de <a href="https://docs.github.com/nl/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">privacyverklaring van GitHub</a>.</p>
    <h2>Je rechten</h2>
    <p>Je kunt DFO BV vragen de kopie die het van je heeft ontvangen in te zien, te verbeteren of te verwijderen: mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>. Heb je een vraag of klacht, mail dan hetzelfde adres. Je kunt ook een klacht indienen bij de <a href="https://www.autoriteitpersoonsgegevens.nl/" target="_blank" rel="noopener">Autoriteit Persoonsgegevens</a>.</p>
    <p class="klein">Laatst bijgewerkt: {PEIL}.</p>'''
pagina('privacy.html', 'Privacy — Wft Permanent Actueel', 'Hoe Wft Permanent Actueel met je gegevens omgaat: geen cookies, geen tracking, en een kopie van je certificaat gaat naar DFO BV.', 'Privacyverklaring', 'Privacy', inh)

# ---------- Over en verantwoording ----------
inh = f'''    <p class="lead">Wft Permanent Actueel is een gratis oefenomgeving voor financieel adviseurs: per Wft-module oefenvragen met uitleg, om je kennis te testen en bij te houden.</p>
    <h2>Wie zit erachter</h2>
    <p>Wft Permanent Actueel is een activiteit van DFO BV, dienstverlening voor financiële ondernemers. DFO BV, De Wel 14–16, 3871 MV Hoevelaken, telefoon <a href="tel:+31332580460">033 258 04 60</a>, e-mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>, <a href="https://www.dfobv.nl/contact/" target="_blank" rel="noopener">contactpagina</a>. KvK 32068727, btw-nummer NL806480828B01. Maak kennis met <a href="https://www.dfobv.nl/ons-team/" target="_blank" rel="noopener">ons team</a>.</p>
    <h2>Wat het wel en niet is</h2>
    <ul>
      <li>Het is een oefentoets. Het is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid.</li>
      <li>Het certificaat bevestigt je resultaat op de oefentoets. Een kopie gaat naar DFO BV als je het mailbericht verstuurt.</li>
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
    <p>Wft Permanent Actueel is een activiteit van DFO BV. Het gebruik van de modules, de toets en het certificaat is gratis voor alle adviseurs. Je hebt geen account of abonnement nodig. Om je uitslag te zien vul je je gegevens in; zie de <a href="privacy.html">privacyverklaring</a>.</p>
    <h2>Wat de toets is</h2>
    <p>De PA-toets is een oefentoets. Hij is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid. Het certificaat bevestigt alleen je resultaat op de oefentoets; een kopie gaat naar DFO BV als je het mailbericht verstuurt. Gebruik het niet als bewijs van vakbekwaamheid.</p>
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
pagina('klachten.html', 'Klachten — Wft Permanent Actueel', 'Niet tevreden over Wft Permanent Actueel of de kennistoets? Zo dien je een klacht in bij DFO BV en zo handelen we die af.', 'Klachtenprocedure', 'Klachten', inh)

# ---------- PE uitgelegd (SEO/GEO) ----------
PE = [
 ('Bestaan PE-punten nog onder de Wft?', 'Nee. Sinds 1 januari 2014 werkt permanente educatie onder de Wft niet meer met PE-punten. Je houdt je adviesbevoegdheid geldig door binnen elke PE-periode het PE-examen te halen voor elke beroepskwalificatie die je hebt. PE-punten kom je nog wel tegen bij vrijwillige beroepsregisters; welke activiteiten daar meetellen, bepaalt elk register zelf.'),
 ('Wat is PE onder de Wft?', 'PE staat voor permanente educatie. Wie adviseert over financiële producten, moet aantoonbaar vakbekwaam zijn: het juiste Wft-diploma voor elke product-dienstcombinatie waarin je adviseert, en dat diploma geldig houden met PE-examens. Je legt de examens af bij een door het CDFD erkend examen-instituut. De AFM houdt toezicht op de naleving van de diplomaplicht door de onderneming.'),
 ('Wat doet het CDFD?', 'Het College Deskundigheid Financiële Dienstverlening (CDFD) ondersteunt de minister van Financiën bij de vakbekwaamheidseisen in de Wft. Het heeft drie kerntaken: (1) elk jaar de relevante ontwikkelingen in het vakgebied in kaart brengen en de minister adviseren over de eind- en toetstermen, die de minister na consultatie bij ministeriële regeling vaststelt; (2) het inhoudelijk beheer van de centrale examenbank voor de initiële examens, de PE-examens en de bijzondere examens, inclusief het opstellen en onderhouden van examenvragen; en (3) de erkenning van en het toezicht op exameninstituten, die pas examens mogen afnemen na erkenning. Daarnaast erkent het CDFD buitenlandse beroepskwalificaties uit andere EU-lidstaten en Zwitserland. Via <a href="https://cdfd.nl/mijn-wft/" target="_blank" rel="noopener">Mijn Wft</a> (met DigiD) zie je welke beroepskwalificaties je hebt en download je je diploma’s en certificaten. Volgens de AFM zie je op de website van DUO welke diploma’s geregistreerd zijn en tot welke datum ze geldig zijn.'),
 ('Hoe lang duurt de PE-periode?', 'Volgens het CDFD loopt de lopende PE-periode van 1 april 2025 tot en met 31 maart 2028; de volgende loopt van 1 april 2028 tot en met 31 maart 2031. Per beroepskwalificatie haal je binnen de periode één PE-examen. Wanneer je dat doet, bepaal je zelf, zolang het voor de einddatum is. Zie <a href="https://cdfd.nl/wanneer-moet-ik-pe-examen-doen/" target="_blank" rel="noopener">Wanneer moet ik PE-examen doen?</a>'),
 ('Wat toetst een PE-examen?', 'Het PE-examen toetst recente ontwikkelingen in het vakgebied. De toetstermen worden jaarlijks per 1 april geactualiseerd; per 1 april 2026 zijn de PE-examens vernieuwd. Volgens het CDFD gaat het om ontwikkelingen die passen bij de module, relevant zijn voor het klantbelang en tijdig definitief bekend zijn. Zie het <a href="https://cdfd.nl/nieuws/wft-pe-examens-vernieuwd-vanaf-1-april-2026-cdfd-vraagt-nieuwe-ontwikkelingen/" target="_blank" rel="noopener">nieuwsbericht van het CDFD</a>.'),
 ('Welke ontwikkelingen komen in het PE-examen?', 'Volgens het CDFD kan een ontwikkeling in de PE-examens komen als die past bij de reikwijdte van de Wft-module, relevant is vanuit het klantbelang en impact heeft op de adviespraktijk, niet ouder is dan circa drie jaar op 1 januari 2026 (of opnieuw relevant is) en definitief bekend is op 1 januari 2026; de ingangsdatum mag later liggen. Grondslagen zijn onder meer nationale wet- en regelgeving, Europese verordeningen, beleid van ministeries, officiële richtlijnen of gedragscodes (bijvoorbeeld van de AFM of het Verbond van Verzekeraars), bedrijfsregelingen van algemene aard en jurisprudentie of uitspraken van Kifid. Bij een Europese richtlijn waarvan de nationale regels nog niet definitief zijn, wordt alleen de inhoud van de richtlijn getoetst.'),
 ('Geldt permanent actueel ook voor medewerkers zonder adviesdiploma?', 'Ja. De AFM onderscheidt twee lagen. Alle klantmedewerkers met inhoudelijk klantcontact moeten permanent actueel vakbekwaam zijn: ze kennen de actuele ontwikkelingen in hun vakgebied en kunnen die toepassen. Dat geldt ook voor binnendienst en ondersteuners die met klanten over producten spreken. Wie adviseert, heeft daarnaast een geldige beroepskwalificatie nodig en houdt die geldig met PE-examens (de diplomaplicht). De verplichting om permanent actueel vakbekwaam te zijn is een open norm: de onderneming bepaalt zelf hoe ze die invult, en de vergunninghouder is ervoor verantwoordelijk. Voor medewerkers zonder diplomaplicht regelt de onderneming de vakbekwaamheid via de bedrijfsvoering, bijvoorbeeld met trainingen die passen bij hun werk. Zie de <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">vakbekwaamheidseisen van de AFM</a>.'),
 ('Hoe toon je aan dat je permanent actueel bent?', 'De onderneming beschrijft in haar bedrijfsprocessen (AO/IC) hoe vakbekwaamheid is geregeld. Volgens de AFM helpt het om per medewerker vast te leggen welke kennis die heeft opgedaan en of die de kennis in de praktijk toepast. Een vakbekwaamheidsdossier per medewerker bevat bijvoorbeeld de functie, de beroepskwalificaties en PE-examens, gevolgde trainingen met datum en onderwerp, en een jaarlijkse evaluatie. Het certificaat van de PA-toets kun je daarin bewaren als bewijs dat je je kennis bijhoudt; het vervangt het PE-examen niet. De AFM kan bij een onderzoek vragen naar de AO/IC-beschrijving, het overzicht van diploma’s en PE en het bewijs van permanent actueel blijven.'),
 ('Is ontheffing van de diplomaplicht mogelijk?', 'De AFM kent een ontheffingsbeleid voor de diplomaplicht in specifieke situaties. Lees dat beleid bij de AFM voordat je erop rekent.'),
 ('Wat betekent Wft Permanent Actueel (PA)?', 'Permanent Actueel betekent dat je vakkennis na je Wft-diploma bij de tijd blijft. PE-examens toetsen vooral wat er is veranderd in wet- en regelgeving en in de markt. Wft Permanent Actueel (PA-WFT.nl) is een gratis oefenomgeving van DFO BV waarmee je per Wft-module oefent.'),
 ('Welke PE-examens heb ik nodig?', 'Dat hangt af van je beroepskwalificaties. Het stelsel is modulair: per module haal je een initieel examen, en een combinatie van modules levert een beroepskwalificatie op. Volgens de AFM zijn dat: Adviseur Zorgverzekering (Zorgverzekeringen), Adviseur Consumptief krediet (Basis, Consumptief krediet), Adviseur Schadeverzekering particulier (Basis, Schadeverzekering particulier), Adviseur Vermogen (Basis, Vermogen), Adviseur Inkomen (Basis, Inkomen), Adviseur Schadeverzekering zakelijk (Basis, Schadeverzekering zakelijk, Schadeverzekering particulier), Adviseur Hypothecair krediet (Basis, Hypothecair krediet, Vermogen) en Adviseur Pensioen (Basis, Pensioenverzekeringen, Vermogen). Zie de <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">vakbekwaamheidseisen van de AFM</a> en de <a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">adviesbevoegdheden van het CDFD</a>; de <a href="index.html#check">pakketcheck</a> rekent het voor je uit.'),
 ('Wat gebeurt er als ik mijn PE niet op tijd haal?', 'Dan vervalt je adviesbevoegdheid voor die beroepskwalificatie. Je herstelt die door een bijzonder examen te halen of door de initiële module-examens opnieuw te doen. Tot dat moment mag je in dat domein niet zelfstandig adviseren. Plan je PE-examen dus niet op het laatste moment: richting het einde van een periode is het druk bij de examen-instituten.'),
 ('Telt een PE-training mee?', 'Voor de wettelijke adviesbevoegdheid telt alleen het gehaalde PE-examen; een training zonder examen houdt je diploma niet geldig. Trainingen kunnen wel helpen om permanent actueel te blijven en tellen soms mee voor registertitels.'),
 ('Levert de PA-toets PE-punten of een PE-examen op?', 'Nee. De PA-toets is een oefentoets. Je krijgt een certificaat met je resultaat, maar dat is geen bewijs van vakbekwaamheid en telt niet mee voor je PE.'),
 ('Hoe oefen ik gratis voor mijn PE-examen?', 'Op PA-WFT.nl staan per Wft-module meerkeuzevragen met uitleg. Een toets over één module heeft 7 vragen; elke extra module voegt er 5 toe. Je kunt ook een mix maken van alle modules uit je eigen pakket. Gratis voor alle adviseurs, zonder account.'),
]
inh = ('    <p class="lead antwoord"><strong>Kort antwoord:</strong> onder de Wft bestaan geen PE-punten meer. Sinds 1 januari 2014 houd je je adviesbevoegdheid geldig met één PE-examen per beroepskwalificatie binnen elke PE-periode; de lopende periode loopt tot en met 31 maart 2028. '
       'Wft Permanent Actueel helpt je daar gratis mee te oefenen; de toets zelf levert geen PE-punten of PE-examen op.</p>\n'
       '    <div class="acties"><a class="btn" href="toets.html">Oefen gratis</a><a class="btn ghost" href="index.html#check">Welke modules heb ik nodig?</a></div>\n'
       + '\n'.join(f'    <h2>{q}</h2>\n    <p>{a}</p>' for q, a in PE) +
       '\n    <h2>Oefenen per Wft-module</h2>\n    <ul>' + ''.join(f'<li><a href="module-{m["id"]}.html">Wft {m["naam"]}</a>: PE-oefenvragen</li>' for m in MODS) + '</ul>\n'
       '    <h2>Bronnen</h2>\n    <ul class="bronnen"><li><a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD — College Deskundigheid Financiële Dienstverlening</a></li><li><a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">CDFD — adviesbevoegdheden</a></li><li><a href="https://cdfd.nl/wanneer-moet-ik-pe-examen-doen/" target="_blank" rel="noopener">CDFD — wanneer moet ik PE-examen doen?</a></li><li><a href="https://cdfd.nl/mijn-wft/" target="_blank" rel="noopener">CDFD — Mijn Wft</a></li><li><a href="https://cdfd.nl/downloads/" target="_blank" rel="noopener">CDFD — downloads: eind- en toetstermen per module, kenmerken PE-ontwikkelingen</a></li>'
       '<li><a href="https://wetten.overheid.nl/BWBR0035213" target="_blank" rel="noopener">Instellings- en mandaatbesluit College Deskundigheid Financiële Dienstverlening Wft</a></li>'
       '<li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">AFM — vakbekwaamheidseisen</a></li><li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/doorlopende-eisen-en-bedrijfsvoering/diplomaplicht-waar-moet-je-als-dienstverlener-aan-voldoen" target="_blank" rel="noopener">AFM — diplomaplicht</a></li>'
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
    <form class="zoekform homezoek" action="zoeken.html" method="get" role="search"><label for="homezoek">Zoek op de site</label><div class="zoekrij"><input type="search" id="homezoek" name="q" placeholder="Bijvoorbeeld: CCD II, PE-examen, box 3" maxlength="80"><button class="btn" type="submit">Zoeken</button></div></form>
    <h2>Wft, PE en Permanent Actueel</h2>
    <p>Als financieel adviseur moet je vakbekwaam blijven: je hebt een Wft-diploma en houdt je kennis bij met permanente educatie (PE). PE-punten bestaan onder de Wft niet meer; sinds 1 januari 2014 haal je binnen elke PE-periode één PE-examen per beroepskwalificatie, bij een door het CDFD erkend examen-instituut. De lopende PE-periode loopt tot en met 31 maart 2028. De PA-toets is een oefentoets en levert geen PE-punten of PE-examen op.</p>
    <p>Permanent actueel zijn geldt volgens de AFM voor alle medewerkers met inhoudelijk klantcontact, dus ook voor binnendienst en ondersteuners. Leg vast welke kennis je hebt opgedaan: bewaar je certificaten in je vakbekwaamheids- of personeelsdossier.</p>
    <p><a href="pe-punten-wft.html">Lees hoe PE, PE-punten en Permanent Actueel werken</a> · <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">Vakbekwaamheidseisen van de AFM</a></p>
</div>
<div class="paneel" id="modules">
    <h2>De 9 modules</h2>
    <p>Per module oefenvragen met uitleg, met de datum waarop de vragen voor het laatst zijn bijgewerkt.</p>
    <div class="modules" id="moduleGrid"></div>
</div>
<div class="paneel" id="check">
    <h2>Welke modules heb ik nodig?</h2>
    <div class="check">
      <div><p>Kies je beroepskwalificaties. Je ziet welke modules daarbij horen en maakt een toets over precies die modules. Binnen elke PE-periode haal je één PE-examen per beroepskwalificatie.</p><div class="chips" id="chips"></div><p class="klein" id="checkNoot" aria-live="polite"></p><p class="klein">Bron: <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">vakbekwaamheidseisen van de AFM</a> en het CDFD, geraadpleegd oktober 2026. Een hulpmiddel, geen advies.</p></div>
      <div class="result"><div class="ring-wrap">{RING}<div class="ring-count" id="count">0</div></div>
        <div class="pkg"><span class="label">Jouw PA-pakket</span><span class="pkg-n" id="countLabel"></span><ul id="chosen"></ul><a class="btn" id="startToets" href="toets.html">Toets over mijn pakket</a></div></div>
    </div>
</div>
<div class="paneel" id="werkwijze">
    <h2>Zo werkt het</h2>
    <div class="steps">
      <div class="step"><span class="num">01</span><h3>Kies je modules</h3><p>Per beroepskwalificatie, of alle modules door elkaar.</p></div>
      <div class="step"><span class="num">02</span><h3>Oefen en leer</h3><p>7 vragen per module, 5 extra per module die je toevoegt, met uitleg bij alle vier de antwoorden.</p></div>
      <div class="step"><span class="num">03</span><h3>Certificaat</h3><p>Bewaar het in je personeelsdossier en lever het in bij je werkgever.</p></div>
      <div class="step"><span class="num">04</span><h3>Elk kwartaal</h3><p>Doe de toets elk kwartaal, zo blijf je permanent actueel.</p></div>
    </div>
</div>
<div class="paneel" id="tip">
    <div data-tip><h3>Tip je collega’s</h3><p>Stuur je collega’s een uitnodiging voor de gratis kennistoets: <a href="mailto:?subject=Tip%3A%20test%20gratis%20je%20Wft-kennis%20op%20PA-WFT.nl&amp;body=https%3A%2F%2Fpa-wft.nl%2Ftoets.html">mail een collega</a>.</p></div>
</div>
<div class="paneel">
  ''' + NIEUWSBRIEVEN + f'''</div>
</div>
<section class="poster"><div class="wrap"><h2>Oefen dit jaar alle modules uit je pakket. Gratis.</h2><a class="btn btn-white" href="toets.html">Start de kennistoets</a></div></section>
<div class="wrap">'''
ld_home = {'@context': 'https://schema.org', '@graph': []}  # Organization en WebSite komen via ld_aanvullen op elke pagina
pagina('index.html', 'Wft Permanent Actueel: gratis PE-oefentoets voor adviseurs',
       'Wft Permanent Actueel: gratis voor alle adviseurs. PE-oefenvragen met uitleg voor alle 9 Wft-modules, van Basis tot Pensioen. Met certificaat.',
       'Wft Permanent Actueel', 'Een activiteit van DFO BV', inh, actief='index.html', ld=ld_home,
       intro='Kennis actueel, elk kwartaal weer. Oefen per Wft-module met vragen over wat er actueel is, met uitleg bij elk antwoord.',
       mast_extra='    <p class="gratis"><strong>Gratis voor alle adviseurs.</strong> Alle modules en de kennistoets, zonder kosten.</p>\n    ' + MARK.replace('<svg ', '<svg class="hero-mark" ', 1) + '\n',
       scripts='\n<script src="assets/js/taal.js"></script>\n<script src="assets/js/modules.js"></script>\n<script src="assets/js/main.js"></script>\n<script src="assets/js/agenda.js"></script>\n<script src="assets/js/tip.js"></script>')
s = open(R + 'index.html', encoding='utf-8').read()
s = s.replace('<meta name="theme-color" content="#1462ad">', '<meta name="google-site-verification" content="3JKf334ow3hOt0pa1YDk1TUvE6EaKzWpUMmtlkBD6fo">\n<meta name="theme-color" content="#1462ad">', 1)
open(R + 'index.html', 'w', encoding='utf-8').write(s)

# ---------- Kennistoets ----------
TOETS_FAQ = [
 ('Hoeveel vragen krijg ik?', 'Bij één module krijg je 7 meerkeuzevragen. Voor elke module die je toevoegt komen er 5 bij: 2 modules geven 12 vragen, 3 modules 17. De vragen worden elke keer opnieuw gekozen.'),
 ('Is de toets gratis?', 'Ja. De toets en alle modules zijn gratis voor alle adviseurs, zonder account en zonder abonnement.'),
 ('Telt de toets mee voor mijn PE?', 'Nee. Het is een oefentoets. Hij levert geen PE-punten of PE-examen op. Je adviesbevoegdheid houd je geldig met een PE-examen per beroepskwalificatie bij een erkend examen-instituut.'),
 ('Wat staat er op het certificaat?', 'Je naam, de modules, je score en de datum, met de vermelding dat het een eigen verklaring is bij een oefentoets. Bewaar het in je personeelsdossier en lever het in bij je werkgever.'),
 ('Kan ik oefenen op een onderwerp?', 'Ja. Op elke modulepagina kies je een toetsterm van het CDFD en oefen je alleen de vragen daarover. Na de toets kun je ook je foute vragen opnieuw oefenen.'),
 ('Hoe vaak moet ik de toets doen?', 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Zet met één klik een herinnering in je agenda.'),
]
inh = ('<div class="paneel" id="paneel" aria-live="polite">\n      <noscript><p>Schakel JavaScript in om de toets te maken.</p></noscript>\n</div>\n'
       '<div class="paneel page">\n    <h2>Zo werkt de Wft-kennistoets</h2>\n'
       '    <ol><li>Kies een of meer Wft-modules, of je hele pakket per beroepskwalificatie.</li><li>Beantwoord de meerkeuzevragen: veel vragen zijn praktijkcasussen, afgestemd op de toetstermen van het CDFD per 1 april 2026.</li>'
       '<li>Na elk antwoord lees je bij alle vier de antwoorden waarom ze goed of fout zijn.</li><li>Na afloop ontvang je een certificaat als pdf, en je kunt je foute vragen opnieuw oefenen.</li></ol>\n'
       '    <h2>Modules in de toets</h2>\n    <ul class="kolommen">' + ''.join(f'<li><a href="module-{m["id"]}.html">Wft {html.escape(m["naam"])}</a></li>' for m in MODS) + '</ul>\n'
       '    <h2>Veelgestelde vragen over de toets</h2>\n'
       + ''.join(f'    <details class="faq"><summary>{v}</summary><p>{a}</p></details>\n' for v, a in TOETS_FAQ)
       + '    <p>Meer weten? Lees <a href="pe-punten-wft.html">hoe PE werkt</a>, bekijk de <a href="begrippen.html">begrippenlijst</a> of <a href="nieuw.html">wat er nieuw is</a>.</p>\n</div>')
ld_toets = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'LearningResource', 'name': 'Wft-kennistoets — Permanent Actueel', 'url': SITE + 'toets.html', 'inLanguage': 'nl', 'isAccessibleForFree': True,
     'learningResourceType': 'Practice test', 'educationalLevel': 'Beroepsniveau', 'audience': {'@type': 'Audience', 'audienceType': 'Financieel adviseurs en klantmedewerkers'},
     'teaches': [f'Wft {m["naam"]}' for m in MODS], 'provider': {'@id': SITE + '#dfo'}},
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': v, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for v, a in TOETS_FAQ]}]}
pagina('toets.html', 'Gratis Wft-kennistoets met uitleg | Permanent Actueel',
       'Gratis Wft-kennistoets voor adviseurs: 7 vragen per module, 5 extra per toegevoegde module, elke keer anders. Met uitleg en certificaat.',
       'Wft-kennistoets', 'Wft Permanent Actueel', inh, actief='toets.html', ld=ld_toets, kruimel='Wft-kennistoets',
       intro=f'Zeven vragen bij één module, vijf extra voor elke module die je toevoegt, elke keer anders, over de {len(MODS)} Wft-modules. Bij elk antwoord lees je waarom het goed of fout is, en na afloop ontvang je een certificaat.',
       extra='\n<link rel="stylesheet" href="assets/css/toets.css">',
       scripts='\n<script src="assets/js/taal.js"></script>\n<script src="assets/js/modules.js"></script>\n<script>window.PA_VRAGEN_V=' + json.dumps(VRAGEN_V, separators=(',', ':')) + ';</script>\n<script src="assets/js/agenda.js"></script>\n<script src="assets/js/tip.js"></script>\n<script src="assets/js/vendor/jspdf.umd.min.js"></script>\n<script src="assets/js/certpdf.js"></script>\n<script src="assets/js/toets.js"></script>')

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
pagina('wetgeving.html', 'Wet- en regelgeving voor adviseurs: Wft, Wwft en meer',
       'Overzicht van wet- en regelgeving voor financieel adviseurs: Wft, Wwft, krediet, fiscaal, pensioen en sociale zekerheid, met links naar de officiële tekst.',
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
pagina('opleidingen.html', 'DFO Opleidingen voor financieel adviseurs',
       'Opleidingen, bijeenkomsten en kennisproducten van DFO voor medewerkers van financiële advieskantoren, plus gratis oefenen met de Wft-kennistoets.',
       'DFO Opleidingen', 'DFO BV', inh, actief='opleidingen.html',
       intro='Opleidingen en bijeenkomsten voor medewerkers van het advieskantoor, en kennis om je vak bij te houden.')

# ---------- llms.txt ----------
llms = ['# Wft Permanent Actueel (PA-WFT.nl)', '',
        '> Gratis oefenomgeving voor financieel adviseurs in Nederland: per Wft-module meerkeuzevragen met uitleg, een toets van 7 vragen (5 extra per toegevoegde module) en een certificaat om naar jezelf te mailen. Een activiteit van DFO BV, Hoevelaken. Geen erkend PE-examen en geen advies. Peildatum regelgeving: ' + PEIL + '.', '',
        '## PE en Permanent Actueel', '', f'- [PE-punten, PE-examens en Wft Permanent Actueel]({SITE}pe-punten-wft.html): onder de Wft bestaan geen PE-punten meer; sinds 1 januari 2014 houd je je adviesbevoegdheid geldig met één PE-examen per beroepskwalificatie binnen elke PE-periode (lopende periode: 1 april 2025 tot en met 31 maart 2028, volgens het CDFD). De PA-toets is een gratis oefentoets en levert geen PE-punten of PE-examen op.', '',
        '## Toets', '', f'- [PA-toets]({SITE}toets.html): kies een module of een mix; 7 vragen bij één module en 5 extra per toegevoegde module, uitleg bij alle vier de antwoorden, na afloop een certificaat (eigen verklaring, geen PE-bewijs), foute vragen opnieuw oefenen en oefenen per CDFD-toetsterm.', '',
        '## Modules', '']
llms += [f"- [Wft {m['naam']}]({SITE}module-{m['id']}.html): {m['tekst']} Laatst bijgewerkt {nl(m['bijgewerkt'])}." for m in MODS]
llms += ['', '## Belangrijke datums', ''] + [f'- {nl(d[0])}: {d[1]}. {d[2]}' for d in DATUMS]
llms += ['', '## English version', '', f'- [English home]({SITE}en/): free Wft practice test for advisers, English convenience translation', f'- [Quiz]({SITE}en/quiz.html)', f'- [PE explained]({SITE}en/pe-explained.html)', f'- [What’s new]({SITE}en/whats-new.html)', f'- [Glossary]({SITE}en/glossary.html)', f'- [Full text in English]({SITE}llms-full-en.txt)']
llms += ['', '## Informatie', '', f'- [Begrippenlijst Wft]({SITE}begrippen.html): korte uitleg van de belangrijkste begrippen uit de Wft en permanente educatie', f'- [Zoeken]({SITE}zoeken.html?q=): doorzoek de site', f'- [Volledige tekst voor taalmodellen]({SITE}llms-full.txt)', f'- [Wat is er nieuw]({SITE}nieuw.html): per Wft-module de actuele wijzigingen van dit kwartaal', f'- [Wet- en regelgeving]({SITE}wetgeving.html): overzicht van Wft, Wwft, krediet, fiscaal, pensioen en sociale zekerheid met links naar de officiële tekst', f'- [DFO Compliance]({SITE}compliance.html)', f'- [DFO Opleidingen]({SITE}opleidingen.html)', f'- [Veelgestelde vragen]({SITE}vragen.html)', f'- [Over en verantwoording]({SITE}over.html)', f'- [Gebruiksvoorwaarden]({SITE}gebruiksvoorwaarden.html)', f'- [Klachten]({SITE}klachten.html)', f'- [Privacy]({SITE}privacy.html)', '',
         '## Contact', '', '- DFO BV, De Wel 14–16, 3871 MV Hoevelaken, 033 258 04 60, info@dfobv.nl, https://www.dfobv.nl/contact/ — KvK 32068727, btw NL806480828B01']
open(R + 'llms.txt', 'w', encoding='utf-8').write('\n'.join(llms) + '\n')


# ---------- begrippenlijst (DefinedTermSet) ----------
naam_van = {m['id']: m['naam'] for m in MODS}
BIJGEWERKT['begrippen.html'] = LAATSTE
inh = ('    <p class="lead">De belangrijkste begrippen uit de Wft, permanente educatie en de Wft-modules, kort uitgelegd. Handig als geheugensteun bij het oefenen.</p>\n'
       '    <p class="meta-regel">Peildatum regelgeving ' + PEIL + '</p>\n'
       '    <nav class="abc" aria-label="Begrippen op letter">' + ' '.join(f'<a href="#letter-{l.lower()}">{l}</a>' for l in sorted({b[0][0].upper() for b in BEGRIPPEN})) + '</nav>\n'
       '    <dl class="begrippen">\n')
vorige = ''
for b in sorted(BEGRIPPEN, key=lambda x: x[0].lower()):
    l = b[0][0].upper(); bid = 'begrip-' + slug(b[0])
    anker = f' id="letter-{l.lower()}"' if l != vorige else ''; vorige = l
    inh += (f'      <div class="begrip"{anker}><dt id="{bid}">{html.escape(b[0])}</dt><dd>{html.escape(b[1])} '
            + '<span class="begrip-mods">' + ' · '.join(f'<a href="module-{m}.html">Wft {html.escape(naam_van[m])}</a>' for m in b[2]) + '</span></dd></div>\n')
inh += ('    </dl>\n    <div class="acties"><a class="btn" href="toets.html">Test je kennis in de toets</a><a class="btn ghost" href="zoeken.html">Zoek op de site</a></div>\n'
        '    <p class="klein">Deze uitleg is vereenvoudigd en geen advies. Bedragen en grenzen wijzigen per jaar; controleer altijd de geldende bron.</p>')
ld = {'@context': 'https://schema.org', '@graph': [{'@type': 'DefinedTermSet', '@id': SITE + 'begrippen.html#begrippen', 'name': 'Begrippenlijst Wft — Permanent Actueel', 'inLanguage': 'nl',
       'hasDefinedTerm': [{'@type': 'DefinedTerm', '@id': SITE + 'begrippen.html#begrip-' + slug(b[0]), 'name': b[0], 'description': b[1], 'inDefinedTermSet': SITE + 'begrippen.html#begrippen',
                           'url': SITE + 'begrippen.html#begrip-' + slug(b[0])} for b in BEGRIPPEN]}]}
pagina('begrippen.html', 'Begrippenlijst Wft: PE, toetstermen en Wft-modules uitgelegd', 'Wat is een PE-examen, een beroepskwalificatie, OVI of de Wtp? De belangrijkste Wft-begrippen kort en helder uitgelegd voor financieel adviseurs.',
       'Begrippenlijst Wft', 'Kort uitgelegd', inh, ld=ld, kruimel='Begrippenlijst Wft')

# ---------- zoekindex en zoekpagina (als laatste, zodat de index compleet is) ----------
open(R + 'assets/js/zoekindex.js', 'w', encoding='utf-8').write('/* Zoekindex, gegenereerd door tools/bouw-paginas.py. Niet met de hand bewerken. */\nwindow.PA_ZOEK=' + json.dumps(ZOEK, ensure_ascii=False, separators=(',', ':')) + ';\n')
inh = ('    <form class="zoekform" action="zoeken.html" method="get" role="search">\n'
       '      <label for="zoekterm">Zoek op de site</label>\n'
       '      <div class="zoekrij"><input type="search" id="zoekterm" name="q" autocomplete="off" placeholder="Bijvoorbeeld: CCD II, PE-examen, box 3, OVI" maxlength="80">'
       '<button class="btn" type="submit">Zoeken</button></div>\n    </form>\n'
       '    <p id="zoekstatus" class="zoekstatus" aria-live="polite"></p>\n    <ol id="zoekresultaten" class="zoekresultaten"></ol>\n'
       '    <noscript><p>Zoeken werkt met JavaScript. Bekijk anders de <a href="sitemap.xml">sitemap</a>.</p></noscript>\n'
       '    <h2>Populaire onderwerpen</h2>\n    <p class="zoektips">' + ' '.join(f'<a href="zoeken.html?q={urllib.parse.quote(t)}">{t}</a>' for t in ['PE-examen', 'CCD II', 'toetstermen', 'box 3', 'Wwft', 'Wet toekomst pensioenen', 'certificaat', 'OVI']) + '</p>\n')
pagina('zoeken.html', 'Zoeken — Wft Permanent Actueel', 'Doorzoek Wft Permanent Actueel: modules, actuele wijzigingen, PE, wet- en regelgeving en veelgestelde vragen.',
       'Zoeken', 'Doorzoek de site', inh, actief='zoeken.html', scripts='\n<script src="assets/js/taal.js"></script>\n<script src="assets/js/zoekindex.js"></script>\n<script src="assets/js/zoek.js"></script>')

# ---------- llms-full.txt: de volledige tekst van de site in Markdown, voor AI-assistenten ----------
volledig = ['# Wft Permanent Actueel (PA-WFT.nl) — volledige tekst', '',
            f'> Gratis oefenomgeving voor financieel adviseurs van DFO BV. Peildatum regelgeving: {PEIL}. Oefentoets, geen erkend PE-examen en geen advies. Bron: {SITE}', '']
huidige = None
for d in ZOEK:
    pagina_url = SITE + d['u'].split('#')[0]
    if d['p'] != huidige:
        volledig += ['', f"## {d['p']}", f'Bron: {pagina_url}', '']; huidige = d['p']
    if d['h']: volledig += [f"### {d['h']}", '']
    volledig += [d['x'], '']
open(R + 'llms-full.txt', 'w', encoding='utf-8').write('\n'.join(volledig) + '\n')

# ---------- Engelse versie (/en/) ----------
exec(open(R + 'tools/bouw-engels.py', encoding='utf-8').read())

# ---------- sitemap en robots ----------
paden = ['', 'toets.html', 'nieuw.html', 'begrippen.html', 'pe-punten-wft.html', 'wetgeving.html', 'compliance.html', 'opleidingen.html'] + [f'module-{m["id"]}.html' for m in MODS] + ['vragen.html', 'over.html', 'gebruiksvoorwaarden.html', 'klachten.html', 'privacy.html']
def sm_url(loc, lastmod, alt):
    x = f'  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>'
    for taal, u in alt: x += f'<xhtml:link rel="alternate" hreflang="{taal}" href="{u}"/>'
    return x + '</url>\n'
sm = ''
for p_ in paden:
    key = p_ or 'index.html'
    alt = [('nl', SITE + p_), ('en', en_url(key)), ('x-default', SITE + p_)] if key in EN_PAD else []
    sm += sm_url(SITE + p_, BIJGEWERKT.get(key, PEIL_ISO), alt)
for nlp, enp in EN_PAD.items():
    if enp == 'search.html': continue
    sm += sm_url(en_url(nlp), BIJGEWERKT_E.get(enp, PEIL_ISO), [('nl', SITE + ('' if nlp == 'index.html' else nlp)), ('en', en_url(nlp)), ('x-default', SITE + ('' if nlp == 'index.html' else nlp))])
open(R + 'sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + sm + '</urlset>\n')
ROBOTS_AI = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'Bingbot', 'CCBot']
NIET = ['/tools/', '/assets/js/vragen/', '/assets/js/vragen-en/']
open(R + 'robots.txt', 'w').write('# PA-WFT.nl: vrij te lezen door zoekmachines en AI-assistenten. De vragenbank van de toets is uitgesloten.\n'
    + ''.join(f'User-agent: {b}\n' for b in ['*'] + ROBOTS_AI) + 'Allow: /\n' + ''.join(f'Disallow: {d}\n' for d in NIET)
    + f'\nSitemap: {SITE}sitemap.xml\n')
print('klaar:', len(paden) + len(EN_PAD) - 1, 'pagina’s in sitemap')
