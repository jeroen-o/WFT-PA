"""Bouwt de vaste onderdelen van PA-WFT.nl opnieuw: modulepagina's, veelgestelde vragen, privacy, over,
gebruiksvoorwaarden, klachten, 404, sitemap, robots en llms.txt, plus header en footer van index en toets.

Gebruik (vanuit de map van de repository):  python3 tools/bouw-paginas.py
Vereist Node.js om assets/js/modules.js te lezen.
"""
import re, html, os, json, subprocess
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SITE = 'https://pa-wft.nl/'
PEIL = '15 oktober 2026'

MARK = ('<svg class="mark" width="44" height="44" viewBox="0 0 120 120" aria-hidden="true"><g transform="rotate(-87 60 60)">'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#1462ad" stroke-width="14" stroke-dasharray="28.5 5.01"/>'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#0b3d73" stroke-width="14" stroke-dasharray="28.5 273.09"/></g>'
        '<text x="60" y="72" text-anchor="middle" font-family="Archivo, Arial, Helvetica, sans-serif" font-weight="800" font-size="34" fill="#1462ad">PA</text></svg>')

NAV = [('index.html#modules', 'Modules'), ('index.html#check', "Welke heb ik nodig?"), ('toets.html', 'Toets'), ('vragen.html', 'Veelgestelde vragen')]

def header(actief=''):
    links = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == actief else '', t) for h, t in NAV)
    return ('<a class="skip" href="#inhoud">Naar de inhoud</a>\n<header class="nav">\n  <a class="brand" href="index.html" aria-label="Wft Permanent Actueel — home">' + MARK +
            '<span class="brand-txt"><strong>Permanent Actueel</strong><span class="s">Wft</span><span class="d">PA-WFT.nl</span></span></a>\n'
            '  <nav aria-label="Hoofdmenu">' + links + '</nav>\n</header>')

FOOTER = '''<footer class="foot">
  <div class="foot-dfo"><img src="assets/logo/dfo-logo.png" alt="DFO — dienstverlening voor financiële ondernemers" width="170" height="40"><span>Wft Permanent Actueel is een activiteit van DFO BV</span></div>
  <div class="foot-adres">DFO BV · De Wel 14–16, 3871 MV Hoevelaken · <a href="tel:+31332580460">033 258 04 60</a> · <a href="mailto:info@dfobv.nl">info@dfobv.nl</a></div>
  <nav class="foot-links" aria-label="Voettekst"><a href="over.html">Over en verantwoording</a><a href="gebruiksvoorwaarden.html">Gebruiksvoorwaarden</a><a href="klachten.html">Klachten</a><a href="privacy.html">Privacy en cookies</a><a href="vragen.html">Veelgestelde vragen</a><a href="https://www.dfobv.nl/" target="_blank" rel="noopener">Ons team bij DFO</a></nav>
  <p class="foot-nb"><strong>Op de hoogte blijven?</strong> Schrijf je in voor de wekelijkse Nieuwsbrief Wft van DFO via de <a href="https://kennisbank.dfobv.nl/" target="_blank" rel="noopener">DFO Kennisbank</a>.</p>
  <p class="foot-disc">Oefentoets voor financieel adviseurs. Geen erkend PE-examen en geen advies. Je PE-examen leg je af bij een door het CDFD erkend examencentrum.</p>
</footer>'''

def head(titel, omschrijving, pad, extra=''):
    return f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(omschrijving)}">
<meta name="theme-color" content="#1462ad">
<link rel="canonical" href="{SITE}{pad}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta property="og:title" content="{html.escape(titel)}">
<meta property="og:description" content="{html.escape(omschrijving)}">
<meta property="og:image" content="{SITE}og-image.png">
<meta property="og:url" content="{SITE}{pad}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">{extra}
</head>
<body>'''

def pagina(pad, titel, omschrijving, kop, kicker, inhoud, actief='', extra='', ld=None):
    if ld: extra += '\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    s = (head(titel, omschrijving, pad, extra) + '\n' + header(actief) + '\n<main id="inhoud">\n<section class="block">\n  <div class="block-head">'
         f'<span class="kicker">{kicker}</span><h1 class="page-h1">{kop}</h1></div>\n  <div class="page">\n{inhoud}\n  </div>\n</section>\n</main>\n'
         + FOOTER + '\n</body>\n</html>\n')
    open(R + pad, 'w', encoding='utf-8').write(s)

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
MAANDEN = ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december']
def nl(iso): j, m, d = iso.split('-'); return f'{int(d)} {MAANDEN[int(m)-1]} {j}'

for i, mod in enumerate(MODS, 1):
    mid, naam, bij, tekst = mod['id'], mod['naam'], mod['bijgewerkt'], mod['tekst']
    d = M[mid]
    inh = (f'    <p class="lead">{html.escape(tekst)}</p>\n'
           f'    <p class="meta-regel">100 oefenvragen · laatst bijgewerkt {nl(bij)} · peildatum regelgeving {PEIL}</p>\n'
           f'    <div class="actions"><a class="btn btn-primary" href="toets.html#{mid}">Doe de toets <span>→</span></a><a class="btn btn-outline" href="index.html#modules">Alle modules</a></div>\n'
           '    <h2>Wat komt aan bod</h2>\n    <ul>' + ''.join(f'<li>{o}</li>' for o in d['onderwerpen']) + '</ul>\n'
           '    <h2>Actueel</h2>\n    <ul>' + ''.join(f'<li>{a}</li>' for a in d['actueel']) + '</ul>\n'
           '    <h2>Wijzigingen</h2>\n    <ul class="log">' + ''.join(f'<li><strong>{nl(dt)}</strong> — {html.escape(t)}</li>' for dt, t in mod['log']) + '</ul>\n'
           '    <h2>Bronnen</h2>\n    <ul class="bronnen">' + ''.join(f'<li><a href="{B[b][1]}" target="_blank" rel="noopener">{B[b][0]}</a></li>' for b in d['bronnen']) + '</ul>\n'
           f'    <p class="klein">Dit overzicht helpt je je kennis bij te houden en is geen leerstof voor een erkend PE-examen. Controleer bedragen en normen altijd in de geldende bron. Zie je een fout? Mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
    pagina(f'module-{mid}.html', f'Wft {naam} — Wft Permanent Actueel', f'Wft {naam}: wat komt aan bod, wat is actueel en de bronnen. Gratis oefentoets met 100 vragen.',
           f'Wft {html.escape(naam)}', f'Module {i:02d}', inh)

# ---------- Veelgestelde vragen ----------
FAQ = [
 ('Wat is permanente educatie (PE)?', 'Wie in de financiële dienstverlening adviseert, moet vakbekwaam zijn en blijven. Daarvoor heb je een Wft-diploma nodig en houd je je kennis bij met permanente educatie. Binnen elke PE-periode haal je de PE-examens die bij je diploma’s horen. De actuele periode en eisen vind je bij het <a href="https://www.cdfd.nl/" target="_blank" rel="noopener">CDFD</a>.'),
 ('Telt deze toets mee voor mijn PE?', 'Nee. De PA-toets is een oefentoets. Hij helpt je je kennis te testen en bij te houden, maar is geen erkend PE-examen en telt niet mee voor de registratie van je vakbekwaamheid. Je PE-examen leg je af bij een door het CDFD erkend examencentrum.'),
 ('Wat kost het?', 'Niets. Alle modules en de toets zijn gratis voor alle adviseurs, zonder abonnement en zonder account. Wft Permanent Actueel is een activiteit van DFO BV.'),
 ('Hoe werkt de toets?', 'Je kiest een module en krijgt 7 willekeurige vragen uit 100. Na elk antwoord zie je de uitleg. Heb je er 5 of meer goed, dan maak je een certificaat aan dat je naar jezelf mailt of print. Je kunt de toets zo vaak doen als je wilt; je krijgt steeds andere vragen.'),
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
    <p>Voor het certificaat vul je je naam en e-mailadres in. Die gegevens blijven in je eigen browser en worden alleen gebruikt om het certificaat op je scherm te zetten. Er wordt niets naar ons verstuurd of opgeslagen. Kies je voor mailen, dan opent je eigen mailprogramma; jij verstuurt het bericht zelf. Sluit je het tabblad, dan zijn de gegevens weg.</p>
    <h2>Cookies en meten</h2>
    <p>We gebruiken geen cookies, geen analyse- of advertentiediensten en geen trackers. Het lettertype staat op onze eigen site, zodat er geen gegevens naar externe partijen gaan.</p>
    <h2>Hosting</h2>
    <p>Deze site plaatst geen cookies, ook niet voor het onthouden van keuzes. De site wordt gehost via GitHub Pages (GitHub, Inc.). Zoals elke webserver verwerkt GitHub technische gegevens zoals je IP-adres om de pagina’s te kunnen leveren en te beveiligen. Zie de <a href="https://docs.github.com/nl/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">privacyverklaring van GitHub</a>.</p>
    <h2>Je rechten</h2>
    <p>Omdat we geen persoonsgegevens bewaren, is er niets in te zien, te wijzigen of te verwijderen. Heb je toch een vraag of klacht, mail dan <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>. Je kunt ook een klacht indienen bij de <a href="https://www.autoriteitpersoonsgegevens.nl/" target="_blank" rel="noopener">Autoriteit Persoonsgegevens</a>.</p>
    <p class="klein">Laatst bijgewerkt: {PEIL}.</p>'''
pagina('privacy.html', 'Privacy — Wft Permanent Actueel', 'Wft Permanent Actueel verzamelt en bewaart geen persoonsgegevens. Geen cookies, geen tracking.', 'Privacyverklaring', 'Privacy', inh)

# ---------- Over en verantwoording ----------
inh = f'''    <p class="lead">Wft Permanent Actueel is een gratis oefenomgeving voor financieel adviseurs: per Wft-module 100 vragen met uitleg, om je kennis te testen en bij te houden.</p>
    <h2>Wie zit erachter</h2>
    <p>Wft Permanent Actueel is een activiteit van DFO BV, dienstverlening voor financiële ondernemers. DFO BV, De Wel 14–16, 3871 MV Hoevelaken, telefoon <a href="tel:+31332580460">033 258 04 60</a>, e-mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>, <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">www.dfobv.nl</a>.</p>
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
pagina('over.html', 'Over en verantwoording — Wft Permanent Actueel', 'Wie achter Wft Permanent Actueel zit, wat de toets wel en niet is, en hoe de vragen tot stand komen.', 'Over en verantwoording', 'Over', inh)

# ---------- 404 ----------
inh = '    <p class="lead">Deze pagina bestaat niet (meer).</p>\n    <div class="actions"><a class="btn btn-primary" href="/">Naar de homepage <span>→</span></a><a class="btn btn-outline" href="/toets.html">Naar de toets</a></div>'
pagina('404.html', 'Pagina niet gevonden — Wft Permanent Actueel', 'Deze pagina bestaat niet.', 'Pagina niet gevonden', '404', inh)
s = open(R + '404.html', encoding='utf-8').read()
# 404 wordt op elk pad geserveerd: absolute paden voor assets en links
s = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|/|#)', r'\1="/', s)
s = s.replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n<meta name="theme-color"', 1)
open(R + '404.html', 'w', encoding='utf-8').write(s)

# ---------- index.html en toets.html: header, footer, fonts ----------
for f, actief in [('index.html', ''), ('toets.html', 'toets.html')]:
    s = open(R + f, encoding='utf-8').read()
    s = re.sub(r'(<a class="skip"[^>]*>[^<]*</a>\n)?<header class="nav">.*?</header>', lambda m: header(actief), s, flags=re.S)
    s = s.replace('<main>', '<main id="inhoud">')
    s = re.sub(r'<footer class="foot">.*?</footer>', lambda m: FOOTER, s, flags=re.S)
    s = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2[^"]*" rel="stylesheet">',
               '<link rel="preload" href="assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>', s)
    open(R + f, 'w', encoding='utf-8').write(s)

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

# ---------- llms.txt ----------
llms = ['# Wft Permanent Actueel (PA-WFT.nl)', '',
        '> Gratis oefenomgeving voor financieel adviseurs in Nederland: per Wft-module 100 meerkeuzevragen met uitleg, een toets van 7 vragen en een certificaat om naar jezelf te mailen. Een activiteit van DFO BV, Hoevelaken. Geen erkend PE-examen en geen advies. Peildatum regelgeving: ' + PEIL + '.', '',
        '## Toets', '', f'- [PA-toets]({SITE}toets.html): kies een module of een mix; 7 willekeurige vragen uit 100 per module, uitleg na elk antwoord, certificaat vanaf 5 van 7 goed.', '',
        '## Modules', '']
llms += [f"- [Wft {m['naam']}]({SITE}module-{m['id']}.html): {m['tekst']} Laatst bijgewerkt {nl(m['bijgewerkt'])}." for m in MODS]
llms += ['', '## Informatie', '', f'- [Veelgestelde vragen]({SITE}vragen.html)', f'- [Over en verantwoording]({SITE}over.html)', f'- [Gebruiksvoorwaarden]({SITE}gebruiksvoorwaarden.html)', f'- [Klachten]({SITE}klachten.html)', f'- [Privacy]({SITE}privacy.html)', '',
         '## Contact', '', '- DFO BV, De Wel 14–16, 3871 MV Hoevelaken, 033 258 04 60, info@dfobv.nl, https://www.dfobv.nl/']
open(R + 'llms.txt', 'w', encoding='utf-8').write('\n'.join(llms) + '\n')

# ---------- sitemap en robots ----------
paden = ['', 'toets.html'] + [f'module-{m["id"]}.html' for m in MODS] + ['vragen.html', 'over.html', 'gebruiksvoorwaarden.html', 'klachten.html', 'privacy.html']
open(R + 'sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{SITE}{p}</loc><lastmod>2026-10-15</lastmod></url>\n' for p in paden) + '</urlset>\n')
open(R + 'robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n')
print('klaar:', len(paden), 'pagina’s in sitemap')
