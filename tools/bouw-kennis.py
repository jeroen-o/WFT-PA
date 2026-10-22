# -*- coding: utf-8 -*-
"""Kennispagina's van PA-WFT.nl: Wft, TRHK, BGfo, EBA GLOM (uit tools/kennis/<naam>.json), de gids Permanent actueel,
het vakbekwaamheidsdossier en het kennisoverzicht. Wordt via exec geladen door tools/bouw-paginas.py (zelfde namespace)."""

KENNIS_JSON = {
    'wft.html': ('wft', 'Wft uitgelegd'),
    'trhk.html': ('trhk', 'TRHK uitgelegd'),
    'bgfo.html': ('bgfo', 'BGfo uitgelegd'),
    'eba-glom.html': ('eba-glom', 'EBA-richtsnoeren leningverstrekking (GLOM)'),
}
KENNIS_BESCHRIJVING = {
    'wft.html': 'De Wet op het financieel toezicht: opbouw, toezicht door AFM en DNB, vergunning, vakbekwaamheid en gedragsregels.',
    'trhk.html': 'De wettelijke leennormen voor hypotheken: financieringslast, loan-to-value en de jaarlijkse wijzigingen.',
    'bgfo.html': 'De gedragsregels voor adviseurs en aanbieders: zorgplicht, informatie, beloning en bedrijfsvoering.',
    'eba-glom.html': 'De Europese richtsnoeren voor kredietverlening en -monitoring en wat ze betekenen voor hypotheek- en kredietadviseurs.',
    'permanent-actueel.html': 'De complete gids: wat de AFM verwacht, een stappenplan, een kwartaalritme en wat je vastlegt.',
    'vakbekwaamheidsdossier.html': 'Hulpmiddel: leg per medewerker kwalificaties, PE-examens en kennisactiviteiten vast en print of bewaar het dossier.',
    'pe-punten-wft.html': 'Hoe PE onder de Wft werkt: PE-examens, de PE-periode en wat de PA-toets wel en niet is.',
    'nieuws.html': 'Elke maand het actuele nieuws over Wft, BGfo, TRHK, PE en examens, met officiële bron.',
    'nieuw.html': 'Per Wft-module de wijzigingen van dit kwartaal en de belangrijke datums.',
    'begrippen.html': 'De belangrijkste Wft-begrippen kort en helder uitgelegd.',
    'wetgeving.html': 'Doorzoekbare bibliotheek van wet- en regelgeving met links naar de officiële tekst.',
}
KENNIS_TITEL = {'wft.html': 'De Wft uitgelegd', 'trhk.html': 'TRHK: de leennormen', 'bgfo.html': 'BGfo: de gedragsregels', 'eba-glom.html': 'EBA-richtsnoeren leningverstrekking (GLOM)',
                'permanent-actueel.html': 'Permanent actueel: de gids', 'vakbekwaamheidsdossier.html': 'Vakbekwaamheidsdossier (hulpmiddel)', 'pe-punten-wft.html': 'PE uitgelegd',
                'nieuws.html': 'Wft-nieuws per maand', 'nieuw.html': 'Wat is er nieuw', 'begrippen.html': 'Begrippenlijst', 'wetgeving.html': 'Wet- en regelgeving'}

def kennis_kaarten(paden, h='h3'):
    return '<div class="kaarten">' + ''.join(f'<article class="kaart"><{h}><a href="{p}">{html.escape(KENNIS_TITEL[p])}</a></{h}><p>{html.escape(KENNIS_BESCHRIJVING[p])}</p></article>' for p in paden) + '</div>\n'

def verder_lezen(eigen):
    rest = [p for p in ['wft.html', 'bgfo.html', 'trhk.html', 'eba-glom.html', 'permanent-actueel.html', 'pe-punten-wft.html', 'begrippen.html'] if p != eigen]
    return '    <h2>Verder lezen</h2>\n    ' + kennis_kaarten(rest[:6])

def ld_article(pad, titel, omschrijving, datum, faq=None, begrippen=None):
    g = [{'@type': 'Article', 'headline': titel, 'description': omschrijving, 'inLanguage': 'nl', 'datePublished': '2026-10-20', 'dateModified': datum,
          'author': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'}, 'publisher': {'@id': SITE + '#dfo'}, 'mainEntityOfPage': SITE + pad,
          'about': [{'@type': 'Thing', 'name': b} for b in (begrippen or [])]}]
    if faq: g.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in faq]})
    return {'@context': 'https://schema.org', '@graph': g}

PE_KENNIS_DATUM = '2026-10-20'
KENNIS_PAGINAS = []

# ---------- pagina's uit JSON ----------
for pad, (naam, kruimel) in KENNIS_JSON.items():
    bron = R + f'tools/kennis/{naam}.json'
    if not os.path.exists(bron):
        print(f'WAARSCHUWING: {bron} ontbreekt, pagina {pad} niet gebouwd'); continue
    d = json.load(open(bron, encoding='utf-8'))
    BIJGEWERKT[pad] = PE_KENNIS_DATUM
    toc = '    <nav class="inhoud" aria-label="Op deze pagina"><p class="inhoud-kop">Op deze pagina</p><ol>' + ''.join(f'<li><a href="#{slug(s["h2"])}">{html.escape(s["h2"])}</a></li>' for s in d['secties']) + '<li><a href="#veelgestelde-vragen">Veelgestelde vragen</a></li><li><a href="#bronnen">Bronnen</a></li></ol></nav>\n'
    inh = (f'    <p class="lead antwoord"><strong>Kort antwoord:</strong> {html.escape(d["kort"])}</p>\n'
           f'    <p class="meta-regel">Laatst bijgewerkt {nl(PE_KENNIS_DATUM)} · peildatum regelgeving {PEIL}</p>\n'
           '    <div class="acties"><a class="btn" href="toets.html">Test je kennis</a><a class="btn ghost" href="pe-punten-wft.html">PE uitgelegd</a></div>\n' + toc
           + ''.join(f'    <h2 id="{slug(s["h2"])}">{html.escape(s["h2"])}</h2>\n    {s["html"]}\n' for s in d['secties'])
           + '    <h2 id="veelgestelde-vragen">Veelgestelde vragen</h2>\n' + ''.join(f'    <details class="faq"><summary>{html.escape(q)}</summary><p>{a}</p></details>\n' for q, a in d['faq'])
           + '    <h2 id="bronnen">Bronnen</h2>\n    <ul class="bronnen">' + ''.join(f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in d['bronnen']) + '</ul>\n'
           + verder_lezen(pad) + '  ' + NIEUWSBRIEVEN
           + '    <p class="klein">Algemene informatie, geen advies. Controleer regels en bedragen altijd in de geldende bron. Zie je een fout? Mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
    pagina(pad, d['titel'], d['omschrijving'], html.escape(d['h1']), html.escape(d['kicker']), inh, ld=ld_article(pad, d['titel'], d['omschrijving'], PE_KENNIS_DATUM, d['faq'], d.get('begrippen')), kruimel=kruimel, og_type='article')
    KENNIS_PAGINAS.append(pad)

# ---------- Permanent actueel: de gids ----------
PA_FAQ = [
 ('Wat is permanent actueel?', 'Permanent actueel zijn betekent dat je de actuele ontwikkelingen in je vakgebied kent en kunt toepassen in je werk. Volgens de AFM geldt dit voor alle medewerkers met inhoudelijk klantcontact. Het is een open norm: de onderneming bepaalt zelf hoe ze het invult en de vergunninghouder is er verantwoordelijk voor.'),
 ('Is permanent actueel hetzelfde als een PE-examen?', 'Nee. Het PE-examen is de diplomaplicht voor wie adviseert: per beroepskwalificatie haal je binnen de PE-periode één PE-examen. Permanent actueel zijn is breder en geldt ook voor medewerkers zonder diplomaplicht. Een training of een oefentoets vervangt het PE-examen niet.'),
 ('Hoe vaak moet ik mijn kennis bijhouden?', 'Er is geen wettelijk aantal uren of moment vastgelegd: het is een open norm. Veel ondernemingen kiezen een vast ritme, bijvoorbeeld elk kwartaal een toets of een teamoverleg, aangevuld met een jaarlijkse evaluatie. Leg je keuze vast in je bedrijfsprocessen (AO/IC).'),
 ('Wat moet ik vastleggen?', 'De AFM noemt dat het helpt om per medewerker vast te leggen welke kennis die heeft opgedaan en of die in de praktijk wordt toegepast. Denk aan functie, beroepskwalificaties en PE-examens, gevolgde trainingen met datum en onderwerp, en een jaarlijkse evaluatie. Met het <a href="vakbekwaamheidsdossier.html">vakbekwaamheidsdossier</a> van PA-WFT.nl maak je dat dossier zelf.'),
 ('Levert het certificaat van de PA-toets PE-punten of een PE-examen op?', 'Nee. De PA-toets is een gratis oefentoets. Het certificaat is een eigen verklaring en geen bewijs van vakbekwaamheid; je kunt het wel in het dossier bewaren als aanvullend bewijs dat je je kennis bijhoudt.'),
 ('Wat gebeurt er als ik mijn PE-examen niet op tijd haal?', 'Dan vervalt je adviesbevoegdheid voor die beroepskwalificatie. Je herstelt die met een bijzonder examen of door de initiële module-examens opnieuw te doen. De lopende PE-periode loopt van 1 april 2025 tot en met 31 maart 2028.'),
]
PA_STAPPEN = [
 ('Breng de functies in kaart', 'Zet per functie op een rij wie inhoudelijk klantcontact heeft: adviseurs, maar ook binnendienst en ondersteuners die met klanten over producten spreken.'),
 ('Leg kwalificaties en einddata vast', 'Noteer per adviseur de beroepskwalificaties en de einddatum van de PE-periode (de lopende periode eindigt op 31 maart 2028). Bewaak de einddatum, want de examen-instituten zijn richting het einde druk.'),
 ('Bepaal de onderwerpen per functie', 'Gebruik de Wft-modules en de toetstermen van het CDFD als houvast voor welke kennis bij welke functie hoort. Medewerkers zonder diplomaplicht kiezen onderwerpen die passen bij hun werk.'),
 ('Kies een vast ritme', 'Bijvoorbeeld elk kwartaal een toets of casusbespreking, en jaarlijks een evaluatie. Een vast moment maakt het vol te houden en laat zien dat het structureel gebeurt.'),
 ('Leg het vast', 'Bewaar per medewerker wat er is gedaan, met datum en onderwerp, in een dossier. Gebruik het hulpmiddel op deze site of je eigen systeem.'),
 ('Evalueer en pas toe', 'Bespreek jaarlijks of de kennis in de praktijk wordt toegepast en pas het plan aan. Beschrijf de werkwijze in je bedrijfsprocessen (AO/IC).'),
]
PA_CHECK = ['Alle medewerkers met inhoudelijk klantcontact zijn in kaart gebracht', 'Per adviseur staan beroepskwalificaties en einddatum PE-periode vast', 'De werkwijze voor permanent actueel staat beschreven in de bedrijfsprocessen (AO/IC)',
            'Er is een vast ritme (bijvoorbeeld elk kwartaal) met een eigenaar', 'Per medewerker is een vakbekwaamheidsdossier met datum en onderwerp van de kennisactiviteiten',
            'Er is een jaarlijkse evaluatie waarin staat of de kennis in de praktijk wordt toegepast', 'Nieuwe ontwikkelingen (bijvoorbeeld uit "Wat is er nieuw") worden besproken in het team',
            'Medewerkers zonder diplomaplicht hebben passende onderwerpen en bewijs', 'De PE-examens zijn ruim voor de einddatum gepland']
inh = ('    <p class="lead antwoord"><strong>Kort antwoord:</strong> permanent actueel betekent dat iedereen met inhoudelijk klantcontact de actuele ontwikkelingen in het vakgebied kent en kan toepassen. Het is een open norm: de onderneming bepaalt hoe, en de vergunninghouder is verantwoordelijk. Wie adviseert, houdt daarnaast de beroepskwalificatie geldig met PE-examens.</p>\n'
       f'    <p class="meta-regel">Laatst bijgewerkt {nl(PE_KENNIS_DATUM)} · volgens de AFM en het CDFD, geraadpleegd oktober 2026</p>\n'
       '    <div class="acties"><a class="btn" href="vakbekwaamheidsdossier.html">Maak een vakbekwaamheidsdossier</a><a class="btn ghost" href="toets.html">Doe de kennistoets</a></div>\n'
       '    <h2>Wat betekent permanent actueel?</h2>\n    <p>Volgens de <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">vakbekwaamheidseisen van de AFM</a> moeten medewerkers met inhoudelijk klantcontact permanent actueel vakbekwaam zijn: ze kennen de actuele ontwikkelingen in hun vakgebied en kunnen die toepassen. Dat gaat verder dan een diploma. Het is een <strong>open norm</strong>: de wet schrijft geen aantal uren of vaste opleidingen voor. De onderneming bepaalt zelf hoe ze dit invult, en de vergunninghouder is ervoor verantwoordelijk.</p>\n'
       '    <h2>Permanent actueel en PE-examens: twee lagen</h2>\n    <table><thead><tr><th></th><th>Permanent actueel</th><th>PE-examen (diplomaplicht)</th></tr></thead><tbody>'
       '<tr><th>Voor wie</th><td>Alle medewerkers met inhoudelijk klantcontact, ook binnendienst en ondersteuners</td><td>Wie adviseert en een beroepskwalificatie heeft</td></tr>'
       '<tr><th>Wat</th><td>Actuele ontwikkelingen kennen en toepassen</td><td>Eén PE-examen per beroepskwalificatie binnen de PE-periode</td></tr>'
       '<tr><th>Hoe</th><td>Open norm; de onderneming kiest de invulling</td><td>Examen bij een door het CDFD erkend examen-instituut</td></tr>'
       '<tr><th>Bewijs</th><td>Eigen vastlegging, bijvoorbeeld een dossier</td><td>Het behaalde PE-examen (zichtbaar bij DUO en Mijn Wft)</td></tr></tbody></table>\n'
       '    <p>Lees meer in <a href="pe-punten-wft.html">PE-punten, PE-examens en Wft Permanent Actueel</a>.</p>\n'
       '    <h2>Wat verwacht de AFM?</h2>\n    <p>De onderneming beschrijft in haar bedrijfsprocessen (AO/IC) hoe vakbekwaamheid is geregeld. Volgens de AFM helpt het om per medewerker vast te leggen welke kennis die heeft opgedaan en of die de kennis in de praktijk toepast. Bij een onderzoek kan de AFM vragen naar de AO/IC-beschrijving, het overzicht van diploma’s en PE, en het bewijs van permanent actueel blijven. Een vakbekwaamheidsdossier per medewerker is daarvoor een praktische vorm.</p>\n'
       '    <h2>Stappenplan: zo richt je het in</h2>\n    <ol class="stappen">' + ''.join(f'<li><strong>{html.escape(k)}.</strong> {html.escape(t)}</li>' for k, t in PA_STAPPEN) + '</ol>\n'
       '    <h2>Voorbeeld van een kwartaalritme</h2>\n    <p>Dit is een voorbeeld en geen wettelijke eis; kies wat bij je kantoor past.</p>\n    <ul>'
       '<li><strong>Elk kwartaal:</strong> doe de <a href="toets.html">kennistoets</a> over je modules, bespreek de ontwikkelingen uit <a href="nieuw.html">Wat is er nieuw</a> en leg het vast.</li>'
       '<li><strong>Elk jaar rond 1 januari:</strong> controleer de jaarlijkse wijzigingen, zoals leennormen (<a href="trhk.html">TRHK</a>), NHG-normen en zorgpremies.</li>'
       '<li><strong>Elk jaar rond 1 april:</strong> het CDFD actualiseert de PE-examens en toetstermen per 1 april; neem de wijzigingen door.</li>'
       '<li><strong>Jaarlijks:</strong> evalueer per medewerker en werk het dossier en de AO/IC-beschrijving bij.</li>'
       '<li><strong>Ruim voor 31 maart 2028:</strong> plan de PE-examens van de lopende PE-periode.</li></ul>\n'
       '    <h2>Wat leg je vast?</h2>\n    <ul><li>Naam, functie en beroepskwalificaties</li><li>PE-examens met datum en einde van de PE-periode</li><li>Kennisactiviteiten: datum, soort, onderwerp en uren</li><li>Certificaten van oefentoetsen, als aanvullend bewijs</li><li>De jaarlijkse evaluatie: is de kennis toegepast?</li></ul>\n'
       '    <p><a href="vakbekwaamheidsdossier.html">Open het hulpmiddel voor het vakbekwaamheidsdossier</a>: je vult het in, print het of bewaart het als bestand. Er wordt niets opgeslagen op onze site.</p>\n'
       '    <h2>Checklist voor je kantoor</h2>\n    <div id="checklist" class="checklist">' + ''.join(f'<label class="vink"><input type="checkbox"> {html.escape(c)}</label>' for c in PA_CHECK) + '</div>\n'
       '    <div class="acties"><button class="btn ghost" type="button" id="checklistPrint">Print de checklist</button></div>\n'
       '    <h2>Veelgemaakte fouten</h2>\n    <ul><li>Een training zien als vervanging van het PE-examen. Voor de adviesbevoegdheid telt alleen het behaalde PE-examen.</li><li>Binnendienst en ondersteuners vergeten, terwijl zij ook met klanten over producten spreken.</li>'
       '<li>De einddatum van de PE-periode niet bewaken en te laat een examen plannen.</li><li>Alleen opleidingen noteren, en niet vastleggen of de kennis in de praktijk wordt toegepast.</li><li>Het certificaat van een oefentoets presenteren als bewijs van vakbekwaamheid.</li></ul>\n'
       '    <h2>Veelgestelde vragen</h2>\n' + ''.join(f'    <details class="faq"><summary>{q}</summary><p>{a}</p></details>\n' for q, a in PA_FAQ)
       + '    <h2>Bronnen</h2>\n    <ul class="bronnen"><li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">AFM — vakbekwaamheidseisen</a></li><li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/doorlopende-eisen-en-bedrijfsvoering/diplomaplicht-waar-moet-je-als-dienstverlener-aan-voldoen" target="_blank" rel="noopener">AFM — diplomaplicht</a></li><li><a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD</a></li><li><a href="https://cdfd.nl/wanneer-moet-ik-pe-examen-doen/" target="_blank" rel="noopener">CDFD — wanneer moet ik PE-examen doen?</a></li></ul>\n'
       + verder_lezen('permanent-actueel.html') + '  ' + NIEUWSBRIEVEN
       + '    <p class="klein">Algemene informatie, geen advies. De eisen die precies voor jouw onderneming gelden, vind je bij de AFM en het CDFD.</p>')
BIJGEWERKT['permanent-actueel.html'] = PE_KENNIS_DATUM
pagina('permanent-actueel.html', 'Permanent actueel: de complete gids voor adviseurs', 'Wat betekent permanent actueel voor adviseurs en klantmedewerkers? Wat verwacht de AFM, een stappenplan, kwartaalritme, checklist en vakbekwaamheidsdossier.',
       'Permanent actueel: de complete gids', 'Gids', inh, ld=ld_article('permanent-actueel.html', 'Permanent actueel: de complete gids voor adviseurs', 'Wat betekent permanent actueel?', PE_KENNIS_DATUM, PA_FAQ, ['Permanent actueel', 'PE-examen', 'AO/IC', 'Vakbekwaamheid']),
       kruimel='Permanent actueel', og_type='article', scripts='\n<script src="assets/js/dossier.js"></script>')
KENNIS_PAGINAS.append('permanent-actueel.html')

# ---------- Vakbekwaamheidsdossier (hulpmiddel) ----------
inh = ('    <p class="lead">Leg per medewerker vast welke kennis is opgedaan en of die wordt toegepast. Vul het formulier in, print het of bewaar het als bestand voor het personeelsdossier. <strong>Er wordt niets opgeslagen of verzonden</strong>: alles blijft in je browser.</p>\n'
       '    <p class="klein">Dit is een eigen vastlegging en vervangt geen diploma of PE-examen. Lees eerst <a href="permanent-actueel.html">Permanent actueel: de gids</a>.</p>\n'
       '    <form id="dossierForm" class="dossier" novalidate>\n'
       '      <h2>Medewerker</h2>\n'
       '      <div class="veld"><label for="dNaam">Naam</label><input type="text" id="dNaam" autocomplete="off" maxlength="80"></div>\n'
       '      <div class="veld"><label for="dFunctie">Functie</label><input type="text" id="dFunctie" autocomplete="off" maxlength="80"></div>\n'
       '      <div class="veld"><label for="dOnderneming">Onderneming</label><input type="text" id="dOnderneming" autocomplete="off" maxlength="100"></div>\n'
       '      <div class="veld"><label for="dPeriode">Verslagperiode (bijvoorbeeld 2026)</label><input type="text" id="dPeriode" autocomplete="off" maxlength="40"></div>\n'
       '      <h2>Beroepskwalificaties</h2>\n      <div id="kwalLijst" class="kwallijst"></div>\n'
       '      <h2>PE-examens</h2>\n      <p class="klein">De lopende PE-periode loopt van 1 april 2025 tot en met 31 maart 2028.</p>\n'
       '      <div class="tabelwrap"><table class="invul" id="peTabel"><thead><tr><th>Beroepskwalificatie</th><th>PE-examen behaald op</th><th>PE-periode tot en met</th><th></th></tr></thead><tbody></tbody></table></div>\n'
       '      <p><button type="button" class="btn ghost" data-voegtoe="peTabel">Rij toevoegen</button></p>\n'
       '      <h2>Kennisactiviteiten</h2>\n'
       '      <div class="tabelwrap"><table class="invul" id="actTabel"><thead><tr><th>Datum</th><th>Soort</th><th>Onderwerp</th><th>Uren</th><th></th></tr></thead><tbody></tbody></table></div>\n'
       '      <p><button type="button" class="btn ghost" data-voegtoe="actTabel">Rij toevoegen</button></p>\n'
       '      <h2>Toepassing in de praktijk</h2>\n'
       '      <div class="veld"><label for="dPraktijk">Hoe is de opgedane kennis toegepast in het werk?</label><textarea id="dPraktijk" rows="4" maxlength="2000"></textarea></div>\n'
       '      <h2>Evaluatie</h2>\n'
       '      <div class="veld"><label for="dEvalDatum">Datum evaluatie</label><input type="date" id="dEvalDatum"></div>\n'
       '      <div class="veld"><label for="dEvalDoor">Evaluatie door</label><input type="text" id="dEvalDoor" autocomplete="off" maxlength="80"></div>\n'
       '      <div class="veld"><label for="dEvaluatie">Conclusie en afspraken</label><textarea id="dEvaluatie" rows="4" maxlength="2000"></textarea></div>\n'
       '      <div class="acties"><button class="btn" type="submit" id="dossierPrint">Print of bewaar als pdf</button><button class="btn ghost" type="button" id="dossierDownload">Download als bestand</button><button class="btn ghost" type="button" id="dossierWis">Alles wissen</button></div>\n'
       '      <p id="dossierStatus" class="certstatus" aria-live="polite"></p>\n'
       '    </form>\n'
       '    <noscript><p>Dit hulpmiddel werkt met JavaScript.</p></noscript>')
BIJGEWERKT['vakbekwaamheidsdossier.html'] = PE_KENNIS_DATUM
pagina('vakbekwaamheidsdossier.html', 'Vakbekwaamheidsdossier maken: gratis hulpmiddel', 'Gratis hulpmiddel om per medewerker kwalificaties, PE-examens en kennisactiviteiten vast te leggen. Print of bewaar het dossier; er wordt niets opgeslagen.',
       'Vakbekwaamheidsdossier', 'Hulpmiddel', inh, kruimel='Vakbekwaamheidsdossier', og_type='website',
       ld={'@context': 'https://schema.org', '@graph': [{'@type': 'WebApplication', 'name': 'Vakbekwaamheidsdossier — Wft Permanent Actueel', 'url': SITE + 'vakbekwaamheidsdossier.html', 'inLanguage': 'nl', 'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Web',
                                         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'provider': {'@id': SITE + '#dfo'}}]},
       scripts='\n<script src="assets/js/dossier.js"></script>')
KENNIS_PAGINAS.append('vakbekwaamheidsdossier.html')

# ---------- Kennisoverzicht ----------
inh = ('    <p class="lead">Alles wat je nodig hebt om permanent actueel te blijven op het gebied van de Wft: uitleg van de wet en de regelingen eronder, de gids voor permanent actueel, hulpmiddelen en de actuele ontwikkelingen. Gratis voor alle adviseurs.</p>\n'
       '    <h2>De regelgeving uitgelegd</h2>\n    ' + kennis_kaarten(['wft.html', 'bgfo.html', 'trhk.html', 'eba-glom.html', 'wetgeving.html', 'begrippen.html'])
       + '    <h2>Permanent actueel en PE</h2>\n    ' + kennis_kaarten(['permanent-actueel.html', 'vakbekwaamheidsdossier.html', 'pe-punten-wft.html', 'nieuws.html', 'nieuw.html'])
       + '    <h2>Oefenen per module</h2>\n    <ul class="kolommen">' + ''.join(f'<li><a href="module-{m["id"]}.html">Wft {html.escape(m["naam"])}</a></li>' for m in MODS) + '</ul>\n'
       + '  ' + NIEUWSBRIEVEN)
BIJGEWERKT['kennis.html'] = PE_KENNIS_DATUM
pagina('kennis.html', 'Kennis: Wft, BGfo, TRHK en permanent actueel', 'Kennisbank voor adviseurs: de Wft, het BGfo, de TRHK en de EBA-richtsnoeren uitgelegd, plus de gids permanent actueel en hulpmiddelen.',
       'Kennis', 'Wft Permanent Actueel', inh, actief='kennis.html', kruimel='Kennis')
