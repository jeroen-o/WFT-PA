# -*- coding: utf-8 -*-
"""Engelse versie van PA-WFT.nl in /en/. Wordt via exec geladen door tools/bouw-paginas.py (zelfde namespace: R, SITE, MODS, M, ...).
De Engelse versie is een hulpmiddel en geen officiële vertaling; examens en wetgeving zijn Nederlands.
Inhoud: tools/en-data.py. Vragenbank: assets/js/vragen-en/<id>.js. Modules: assets/js/modules-en.js."""
exec(open(R + 'tools/en-data.py', encoding='utf-8').read())
os.makedirs(R + 'en', exist_ok=True)

MAANDEN_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
def en_datum(iso): j, m, d = iso.split('-'); return f'{int(d)} {MAANDEN_EN[int(m) - 1]} {j}'
PEIL_EN = en_datum(PEIL_ISO)
E_ABS = '/'  # Engelse pagina's staan in /en/: alle assets absoluut vanaf de siteroot

def node_json(code, *args):
    return json.loads(subprocess.check_output(['node', '-e', code] + list(args)))

# ---------- Engelse modules en vragenbank ----------
MODS_EN = {}
if os.path.exists(R + 'assets/js/modules-en.js'):
    try: MODS_EN = {m['id']: m for m in node_json("global.window={};eval(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(JSON.stringify(window.PA_MODULES))", R + 'assets/js/modules-en.js')}
    except Exception as e: print('modules-en.js niet gelezen:', e)
def mod_en(m):
    e = MODS_EN.get(m['id'], {})
    return {'id': m['id'], 'naam': EN_NAAM[m['id']], 'tekst': e.get('tekst', m['tekst']), 'bijgewerkt': m['bijgewerkt'], 'log': e.get('log', m['log'])}
MODS_E = [mod_en(m) for m in MODS]
NAAM_E = {m['id']: m['naam'] for m in MODS_E}

_bestaand = [f'assets/js/vragen-en/{m["id"]}.js' for m in MODS if os.path.exists(R + f'assets/js/vragen-en/{m["id"]}.js')]
VRAGEN_EN = node_json("global.window={};for(const f of process.argv.slice(1))eval(require('fs').readFileSync(f,'utf8'));process.stdout.write(JSON.stringify(window.PA_VRAGEN))", *[R + f for f in _bestaand]) if _bestaand else {}
VRAGEN_V_EN = {m['id']: hashlib.sha1(open(R + f'assets/js/vragen-en/{m["id"]}.js', 'rb').read()).hexdigest()[:8] for m in MODS if m['id'] in VRAGEN_EN}

# ---------- kader: header, footer, head ----------
NAV_E = [('index.html', 'Home'), ('quiz.html', 'Quiz'), ('index.html#modules', 'Modules'), ('pe-explained.html', 'PE explained'), ('whats-new.html', 'What’s new'),
         ('glossary.html', 'Glossary'), ('about.html', 'About DFO BV'), ('search.html', 'Search')]

def header_e(actief='', pad=''):
    loep = '<svg class="loep" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'
    links = ''.join('<a href="%s"%s>%s%s</a>' % (h, ' aria-current="page"' if h == actief else '', loep if h == 'search.html' else '', t) for h, t in NAV_E)
    nl_pad = next((k for k, v in EN_PAD.items() if v == pad), '')
    return ('<a class="skip" href="#inhoud">Skip to content</a>\n<div class="topbar">\n  <div class="wrap">\n'
            '    <a class="logo" href="index.html" aria-label="Wft Permanent Actueel — home"' + (' aria-current="page"' if actief == 'index.html' else '') + '><img src="/assets/logo/pa-wft-logo-horizontal.png" width="144" height="60" alt="Wft Permanent Actueel — PA-WFT.nl" fetchpriority="high"></a>\n'
            '    <a class="taalknop" href="/' + ('' if nl_pad in ('', 'index.html') else nl_pad) + '" hreflang="nl" lang="nl" title="Lees deze pagina in het Nederlands">NL</a>\n'
            '    <a class="zoekknop" href="search.html" aria-label="Search the site">' + loep.replace('width="16" height="16"', 'width="24" height="24"') + '</a>\n'
            '    <nav class="topnav" aria-label="Main menu">' + links + '</nav>\n'
            '  </div>\n</div>')

def masthead_e(kicker, kop, intro='', extra='', datum=''):
    return ('<header class="masthead">\n  <div class="wrap">\n' + (f'    <p class="bijgewerkt-kop"><time datetime="{datum}" title="Last updated">{en_datum(datum)}</time></p>\n' if datum else '') + (f'    <p class="kicker">{kicker}</p>\n' if kicker else '') + f'    <h1>{kop}</h1>\n'
            + (f'    <p class="intro">{intro}</p>\n' if intro else '') + extra + '  </div>\n</header>')

MELDING_E = ('<div class="melding" role="note"><strong>Please note.</strong> The PA test is a practice test and does not count as a Wft exam, PE exam or PE evidence. '
             'DFO BV is not responsible for the accuracy and completeness of all questions and answers; rules change. This English version is a convenience translation: legislation, exams and official sources are in Dutch. Want to be sure? '
             'Contact <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">DFO BV</a> on <a href="tel:+31332580460">+31 33 258 04 60</a> or <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</div>')

FOOTER_E = (partnerband('Our partners', '/') + '<footer class="foot">\n  <div class="wrap">\n    <div class="foot-kolommen">\n'
    '      <div class="foot-merk"><p class="foot-titel">Wft Permanent Actueel</p><p>Free practice test for advisers and client-facing employees. Knowledge up to date, every quarter again.</p>'
    '<p><a class="btn btn-white" href="quiz.html">Start the quiz</a></p></div>\n'
    '      <nav aria-label="Quiz and knowledge"><p class="foot-kop">Quiz and knowledge</p><ul><li><a href="quiz.html">Quiz</a></li><li><a href="index.html#modules">Modules</a></li>'
    '<li><a href="whats-new.html">What’s new</a></li><li><a href="glossary.html">Glossary</a></li><li><a href="index.html#tip">Tip your colleagues</a></li><li><a href="index.html#check">Which modules do I need?</a></li><li><a href="pe-explained.html">PE explained</a></li><li><a href="/wetgeving.html" hreflang="nl" lang="nl">Legislation (Dutch)</a></li><li><a href="faq.html">FAQ</a></li></ul></nav>\n'
    '      <nav aria-label="DFO"><p class="foot-kop">DFO</p><ul><li><a href="/compliance.html" hreflang="nl" lang="nl">DFO Compliance (Dutch)</a></li><li><a href="/opleidingen.html" hreflang="nl" lang="nl">DFO Training (Dutch)</a></li>'
    '<li><a href="https://www.dfobv.nl/ons-team/"' + EXT + '>Our team</a></li><li><a href="https://www.dfosignalen.nl/"' + EXT + '>DFO Signalen</a></li><li><a href="https://www.dfobv.nl/product/nieuwsbrief-wft/"' + EXT + '>Nieuwsbrief Wft</a></li><li><a href="https://kennisbank.dfobv.nl/"' + EXT + '>DFO Knowledge base</a></li></ul></nav>\n'
    '      <div><p class="foot-kop">Contact</p><address>DFO BV<br>De Wel 14–16<br>3871 MV Hoevelaken, the Netherlands<br><a href="tel:+31332580460">+31 33 258 04 60</a><br><a href="mailto:info@dfobv.nl">info@dfobv.nl</a><br>'
    '<a href="https://www.dfobv.nl/contact/"' + EXT + '>Contact page</a></address><p class="foot-klein">KvK 32068727 · VAT NL806480828B01</p></div>\n'
    '    </div>\n  </div>\n'
    '  <div class="foot-balk"><div class="wrap">'
    '<div class="foot-balk-tekst"><nav class="foot-links" aria-label="Terms"><a href="about.html">About and accountability</a><a href="terms.html">Terms of use</a><a href="complaints.html">Complaints</a><a href="privacy.html">Privacy and cookies</a></nav>'
    '<p class="foot-disc">© 2026 DFO BV. Wft Permanent Actueel is an activity of DFO BV. Practice test for financial advisers; not a recognised PE exam and not advice. This English version is a convenience translation.</p></div>'
    '<a class="foot-logo" href="https://www.dfobv.nl/"' + EXT + ' aria-label="DFO BV — go to dfobv.nl"><img src="/assets/logo/dfo-logo.png" width="186" height="44" loading="lazy" decoding="async" alt="DFO — services for financial entrepreneurs"></a>'
    '</div></div>\n</footer>\n'
    '<script>(function(){function o(){var h=location.hash.slice(1),e=h&&document.getElementById(decodeURIComponent(h));if(e&&e.tagName==="DETAILS"){e.open=true;e.scrollIntoView();}}o();addEventListener("hashchange",o);})();</script>')

NIEUWSBRIEVEN_E = ('<section class="nieuwsbrieven" id="newsletters" aria-labelledby="nb-kop">\n'
    '    <h2 id="nb-kop">Stay up to date</h2>\n'
    '    <p class="lead">Stay up to date with the latest news. Subscribe to the newsletters of DFO (in Dutch).</p>\n'
    '    <div class="nb-kaarten">\n'
    '      <article class="nb-kaart"><h3>DFO Signalen</h3><p>Weekly signals from the market, model texts and practical analyses for the advisory firm, with an archive going back years. In Dutch.</p>'
    '<a class="btn" href="https://www.dfosignalen.nl/"' + EXT + '>Subscribe to DFO Signalen</a></article>\n'
    '      <article class="nb-kaart"><h3>Nieuwsbrief Wft</h3><p>On average once a week, the latest developments in legislation and supervision, explained briefly and practically for financial service providers. In Dutch.</p>'
    '<a class="btn" href="https://www.dfobv.nl/product/nieuwsbrief-wft/"' + EXT + '>Subscribe to the Nieuwsbrief Wft</a></article>\n'
    '    </div>\n'
    '    <p class="klein">Subscribing is done on the DFO website. Wft Permanent Actueel does not store any data itself.</p>\n'
    '  </section>\n')

def canon_e(pad): return SITE + 'en/' + ('' if pad == 'index.html' else pad)
NL_VAN_EN = {v: k for k, v in EN_PAD.items()}
def head_e(titel, omschrijving, pad, extra='', og_beeld='og-image.png', og_type='website'):
    t, o, u = html.escape(titel), html.escape(omschrijving), canon_e(pad)
    nlpad = NL_VAN_EN.get(pad)
    nl_u = canon(nlpad) if nlpad else SITE
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{t}</title>\n<meta name="description" content="{o}">\n'
            + ('<meta name="robots" content="noindex, follow">\n' if pad == 'search.html' else '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">\n')
            + '<meta name="theme-color" content="#1462ad">\n<meta name="author" content="DFO BV">\n'
            f'<link rel="canonical" href="{u}">\n<link rel="alternate" hreflang="en" href="{u}">\n<link rel="alternate" hreflang="nl" href="{nl_u}">\n<link rel="alternate" hreflang="x-default" href="{nl_u}">\n'
            '<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n'
            f'<meta property="og:type" content="{og_type}">\n<meta property="og:site_name" content="Wft Permanent Actueel">\n<meta property="og:locale" content="en_GB">\n<meta property="og:locale:alternate" content="nl_NL">\n'
            f'<meta property="og:title" content="{t}">\n<meta property="og:description" content="{o}">\n<meta property="og:url" content="{u}">\n'
            f'<meta property="og:image" content="{SITE}{og_beeld}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{t}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{t}">\n<meta name="twitter:description" content="{o}">\n<meta name="twitter:image" content="{SITE}{og_beeld}">\n'
            '<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
            '<link rel="stylesheet" href="/assets/css/style.css">' + extra + '\n</head>\n<body>')

def ld_aanvullen_e(ld, pad, titel, omschrijving, datum, kruimel, beeld):
    ld = ld or {'@context': 'https://schema.org', '@graph': []}
    if '@graph' not in ld: ld = {'@context': 'https://schema.org', '@graph': [{k: v for k, v in ld.items() if k != '@context'}]}
    g = ld['@graph']; typen = {n.get('@type') for n in g}; ids = {n.get('@id') for n in g}
    org = dict(ORG, contactPoint=dict(ORG['contactPoint'], availableLanguage=['nl', 'en']))
    web = dict(WEBSITE, inLanguage='en', url=SITE + 'en/', **{'@id': SITE + 'en/#site'}, description='Free practice environment for financial advisers in the Netherlands: per Wft module practice questions with explanations, a quiz of 7 questions per module (5 extra per added module) and a certificate. Dutch legislation; English convenience translation.',
               potentialAction={'@type': 'SearchAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': SITE + 'en/search.html?q={search_term_string}'}, 'query-input': 'required name=search_term_string'})
    if org['@id'] not in ids: g.insert(0, org)
    if web['@id'] not in ids: g.insert(1, web)
    u = canon_e(pad)
    g.append({'@type': 'WebPage', '@id': u + '#page', 'url': u, 'name': re.sub(r'\s*\|.*$', '', titel), 'description': omschrijving, 'inLanguage': 'en', 'dateModified': datum,
              'isPartOf': {'@id': SITE + 'en/#site'}, 'publisher': {'@id': SITE + '#dfo'}, 'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + beeld, 'width': 1200, 'height': 630}})
    if 'BreadcrumbList' not in typen and pad != 'index.html':
        g.append({'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Wft Permanent Actueel', 'item': SITE + 'en/'}, {'@type': 'ListItem', 'position': 2, 'name': kruimel, 'item': u}]})
    return ld

ZOEK_EN = []
def pagina_e(pad, titel, omschrijving, kop, kicker, inhoud, actief='', extra='', ld=None, intro='', scripts='', mast_extra='', datum=None, og_type='website', kruimel=None):
    global ZOEK
    datum = datum or BIJGEWERKT.get(NL_VAN_EN.get(pad, ''), PEIL_ISO)
    og_beeld = 'og-image.png'
    if os.path.exists(R + 'og/en/' + pad.replace('.html', '.png')): og_beeld = 'og/en/' + pad.replace('.html', '.png')
    if pad != 'search.html': ld = ld_aanvullen_e(ld, pad, titel, omschrijving, datum, kruimel or re.sub(r'<[^>]+>', '', kop), og_beeld)
    if ld: extra += '\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    inhoud = wrap_tabellen(inhoud)
    if not inhoud.lstrip().startswith('<div class="paneel'): inhoud = '<div class="paneel page">\n' + inhoud + '\n</div>'
    s = (head_e(titel, omschrijving, pad, extra, og_beeld, og_type) + '\n' + header_e(actief, pad) + '\n' + masthead_e(kicker, kop, intro, mast_extra, datum)
         + '\n<main id="inhoud">\n  <div class="wrap">\n' + inhoud + '\n' + MELDING_E + '\n  </div>\n</main>\n' + FOOTER_E + scripts + '\n</body>\n</html>\n')
    s = kop_ids(s)
    if pad != 'search.html':
        opgeslagen = ZOEK; ZOEK = ZOEK_EN
        try: zoek_indexeer(pad, titel, omschrijving, s.replace(MELDING_E, ''))
        finally: ZOEK = opgeslagen
    open(R + 'en/' + pad, 'w', encoding='utf-8').write(versie(link_cdfd(s)))
    BIJGEWERKT_E[pad] = datum
BIJGEWERKT_E = {}

# ---------- hulpfuncties voor de Engelse modulepagina's ----------
KWAL_E = [('Mortgage Credit Adviser', ['basis', 'vermogen', 'hypothecair-krediet']), ('Wealth Adviser', ['basis', 'vermogen']), ('Pensions Adviser', ['basis', 'vermogen', 'pensioen']),
          ('Consumer Credit Adviser', ['basis', 'consumptief-krediet']), ('Commercial Non-life Insurance Adviser', ['basis', 'schade-particulier', 'schade-zakelijk']),
          ('Personal Non-life Insurance Adviser', ['basis', 'schade-particulier']), ('Income Adviser', ['basis', 'inkomen']), ('Health Insurance Adviser', ['zorgverzekering'])]

def kort_e(mid, naam, bij, nieuw):
    kw = [k for k, ms in KWAL_E if mid in ms]
    m = re.match(r'<strong>(.*?)\.?</strong>\s*(.*)', nieuw[0], re.S)
    zin = lambda t: t[:1].lower() + t[1:] if len(t) > 1 and not t[1].isupper() else t
    eerste = (m.group(1) + ': ' + zin(re.sub(r'<[^>]+>', '', m.group(2)).split('. ')[0])).rstrip('.') if m else re.sub(r'<[^>]+>', '', nieuw[0]).split('. ')[0].rstrip('.')
    items = [f'<strong>Who needs it:</strong> required for {len(kw)} professional qualification{"s" if len(kw) != 1 else ""}: ' + ', '.join(kw) + '.',
             '<strong>PE:</strong> you take one PE exam per professional qualification within the PE period, which runs until 31 March 2028 inclusive.',
             '<strong>Exam terms:</strong> the final objectives and exam terms of the CDFD have been renewed for exams from 1 April 2026.' + (' One exam term for this module was changed.' if mid in EN_WIJZ else ''),
             f'<strong>Current:</strong> {html.escape(eerste)}.',
             f'<strong>Practise:</strong> 7 multiple-choice questions with an explanation for every answer, free and without an account. Last updated {en_datum(bij)}.']
    return '    <div class="kort"><h2>Wft ' + html.escape(naam) + ' at a glance</h2><ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul></div>\n'

def verwant_e(mid):
    ids = []
    for k, ms in KWAL_E:
        if mid in ms: ids += [m for m in ms if m != mid and m not in ids]
    if not ids: return ''
    return ('    <h2>Related modules</h2>\n    <p>These modules belong to the same professional qualifications. Practise them together in one quiz: '
            + f'<a href="quiz.html#mix={",".join([mid] + ids)}">quiz with all {len(ids) + 1} modules</a>.</p>\n    <ul>'
            + ''.join(f'<li><a href="module-{i}.html">Wft {html.escape(NAAM_E[i])}</a></li>' for i in ids) + '</ul>\n')

def termen_e(mid):
    tel = {}
    for q in VRAGEN.get(mid, []):
        if len(q) > 2 and q[2]: tel[q[2]] = tel.get(q[2], 0) + 1
    if not tel: return ''
    sleutel = lambda t: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', t)]
    return ('    <h2>Practise per exam term</h2>\n    <p>Practise only the questions about one exam term of the CDFD, for example a topic you find difficult. A practice round does not count towards the certificate.</p>\n'
            '    <ul class="termen">' + ''.join(f'<li><a href="quiz.html#term={mid}:{t}">{t}</a></li>' for t in sorted(tel, key=sleutel)) + '</ul>\n')

def meld_e(q):
    body = (f'Module: see question text\n' + (f'CDFD exam term: {q[2]}\n' if len(q) > 2 and q[2] else '') + f'\nQuestion:\n{q[0]}\n\nAnswers:\n' + '\n'.join(f'- {a[0]}' + ('  [given as correct]' if k == 0 else '') for k, a in enumerate(q[1]))
            + f'\n\nExplanation of the correct answer:\n{q[1][0][1]}\n\nMy doubt:\n')
    return 'mailto:info@dfobv.nl?subject=' + urllib.parse.quote('check this question on PA-WFT.nl') + '&body=' + urllib.parse.quote(body)

def voorbeeld_e(q, nr):
    term = f' <span class="term">exam term {html.escape(q[2])}</span>' if len(q) > 2 and q[2] else ''
    return (f'    <article class="voorbeeld"><h3>Example question {nr}{term}</h3>\n      <p>{html.escape(q[0])}</p>\n      <ul>'
            + ''.join(f'<li>{html.escape(a[0])}</li>' for a in sorted(q[1], key=lambda a: a[0].lower())) + '</ul>\n'
            f'      <details><summary>Show the answer and explanation</summary><p><strong>Correct: {html.escape(q[1][0][0])}.</strong> {html.escape(q[1][0][1])}</p>'
            '<ul class="uitleg">' + ''.join(f'<li><strong>{html.escape(a[0])}</strong>: {html.escape(a[1])}</li>' for a in q[1][1:]) + '</ul>'
            + f'<p class="meld"><a href="{html.escape(meld_e(q))}">Doubt about this question or answer? Email it straight to DFO</a></p></details></article>\n')

def voorbeelden_e(mid, n=3):
    """Dezelfde voorbeeldvragen als op de Nederlandse pagina (zelfde index), maar in het Engels."""
    nlv = VRAGEN.get(mid, []); env = VRAGEN_EN.get(mid)
    if not env or len(env) != len(nlv): return []
    return [env[nlv.index(q)] for q in voorbeelden(mid, n)]

def quiz_ld_e(naam, qs):
    return {'@type': 'Quiz', 'name': f'Example questions Wft {naam}', 'inLanguage': 'en', 'isAccessibleForFree': True, 'educationalLevel': 'Professional level',
            'about': {'@type': 'Thing', 'name': f'Wft {naam}'},
            'hasPart': [{'@type': 'Question', 'eduQuestionType': 'Multiple choice', 'learningResourceType': 'Practice problem', 'text': q[0],
                         'acceptedAnswer': {'@type': 'Answer', 'text': q[1][0][0], 'answerExplanation': {'@type': 'Comment', 'text': q[1][0][1]}},
                         'suggestedAnswer': [{'@type': 'Answer', 'text': a[0]} for a in q[1][1:]]} for q in qs]}

def datums_e(mid=None, kop='h2'):
    rij = [d for d in DATUMS if mid is None or mid in d[3]]
    if not rij: return ''
    def mods(d): return '' if mid or len(d[3]) == len(ALLE) else ' <span class="datums-mods">' + ', '.join('Wft ' + NAAM_E[x] for x in d[3]) + '</span>'
    def li(d): return f'<li><time datetime="{d[0]}">{en_datum(d[0])}</time><span><strong>{html.escape(EN_DATUMS[d[0]][0])}.</strong> {html.escape(EN_DATUMS[d[0]][1])}{mods(d)}</span></li>'
    komend = [d for d in rij if d[0] > PEIL_ISO]; recent = [d for d in rij if d[0] <= PEIL_ISO]
    uit = f'    <{kop}>Important dates</{kop}>\n'
    if komend: uit += '    <p class="datums-kop">Coming up</p>\n    <ul class="datums">' + ''.join(li(d) for d in komend) + '</ul>\n'
    if recent: uit += '    <p class="datums-kop">Recently took effect</p>\n    <ul class="datums recent">' + ''.join(li(d) for d in reversed(recent)) + '</ul>\n'
    return uit

# ---------- modulepagina's ----------
NIEUW_E = {}
SCRIPTS_E = {}  # wordt na de definitie van de scripts hieronder gevuld
def js(*namen): return ''.join(f'\n<script src="/assets/js/{n}"></script>' for n in namen)
def js_vragen_v(): return '\n<script>window.PA_VRAGEN_V=' + json.dumps(VRAGEN_V_EN, separators=(',', ':')) + ';</script>'
S_BASIS = ('taal.js', 'modules-en.js')

for i, mod in enumerate(MODS_E, 1):
    mid, naam, bij, tekst = mod['id'], mod['naam'], mod['bijgewerkt'], mod['tekst']
    d = M[mid]; vb = voorbeelden_e(mid)
    nieuw = (['<strong>New CDFD exam terms from 1 April 2026.</strong> The final objectives and exam terms for this module have been renewed and apply to exams from 1 April 2026. The quiz questions are aligned with them.']
             + ([f'<strong>Changed exam term.</strong> {EN_WIJZ[mid]}'] if mid in EN_WIJZ else []) + EN_ACTUEEL[mid])
    NIEUW_E[mid] = nieuw
    inh = (f'    <p class="lead">{html.escape(tekst)} Practise for free with PE practice questions for Wft {html.escape(naam)}, with an explanation for every answer.</p>\n'
           f'    <p class="meta-regel">Last updated {en_datum(bij)} · legislation as at {PEIL_EN}</p>\n'
           f'    <div class="acties"><a class="btn" href="quiz.html#{mid}">Take the quiz</a><a class="btn ghost" href="index.html#modules">All modules</a></div>\n'
           + kort_e(mid, naam, bij, EN_ACTUEEL[mid]) +
           '    <h2>What is covered</h2>\n    <ul>' + ''.join(f'<li>{o}</li>' for o in EN_ONDERWERPEN[mid]) + '</ul>\n'
           '    <h2>What’s new in 2026</h2>\n    <ul>' + ''.join(f'<li>{a}</li>' for a in nieuw) + '</ul>\n'
           + datums_e(mid)
           + '    <h2>CDFD exam terms from 1 April 2026</h2>\n    <p>The final objectives and exam terms of the CDFD for this module are divided into tasks:</p>\n    <ol>' + ''.join(f'<li>{html.escape(t)}</li>' for t in EN_TAKEN[mid]) + '</ol>\n'
           + '    <p class="klein">Source: final objectives and exam terms per module of the CDFD, applicable to exams from 1 April 2026 (in Dutch). The full documents are in the <a href="https://cdfd.nl/downloads/" target="_blank" rel="noopener">CDFD downloads</a>.</p>\n'
           + (f'    <h2>Example questions Wft {html.escape(naam)}</h2>\n    <p>This is what the quiz questions look like. In the quiz the answers appear in random order.</p>\n' + ''.join(voorbeeld_e(q, k) for k, q in enumerate(vb, 1)) if vb else '')
           + f'    <div class="acties"><a class="btn" href="quiz.html#{mid}">Keep practising in the quiz</a></div>\n'
           + termen_e(mid)
           + verwant_e(mid)
           + ('    <h2>Terms for this module</h2>\n    <p>' + ' · '.join(f'<a href="glossary.html#begrip-{slug(b[0])}">{html.escape(EN_BEGRIPPEN[b[0]][0])}</a>' for b in BEGRIPPEN if mid in b[2]) + '</p>\n' if any(mid in b[2] for b in BEGRIPPEN) else '')
           + '    <h2>Changes</h2>\n    <ul class="log">' + ''.join(f'<li><strong>{en_datum(dt)}</strong> — {html.escape(t)}</li>' for dt, t in mod['log']) + '</ul>\n'
           '    <h2>Sources</h2>\n    <ul class="bronnen">' + ''.join(f'<li><a href="{B[b][1]}" target="_blank" rel="noopener">{EN_B[b]}</a></li>' for b in d['bronnen']) + '</ul>\n'
           + '  ' + NIEUWSBRIEVEN_E +
           '    <p class="klein">This overview helps you keep your knowledge up to date and is not study material for a recognised PE exam. Always check amounts and standards in the applicable source. Spot an error? Email <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Course', 'name': f'Wft {naam} — Permanent Actueel', 'description': f'Free PE practice questions Wft {naam}: multiple-choice questions with explanations, a quiz of 7 questions (5 extra per added module) and a certificate. {tekst}',
         'url': f'{SITE}en/module-{mid}.html', 'inLanguage': 'en', 'isAccessibleForFree': True, 'educationalLevel': 'Professional level', 'teaches': EN_ONDERWERPEN[mid][:6],
         'dateModified': bij, 'provider': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'},
         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR', 'category': 'Free'}, 'hasCourseInstance': {'@type': 'CourseInstance', 'courseMode': 'online', 'courseWorkload': 'PT10M'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Wft Permanent Actueel', 'item': SITE + 'en/'},
                                                        {'@type': 'ListItem', 'position': 2, 'name': f'Wft {naam}', 'item': f'{SITE}en/module-{mid}.html'}]}]
          + ([quiz_ld_e(naam, vb)] if vb else [])}
    titel = f'Wft {naam} 2026: free PE practice questions'
    if len(titel) > 60: titel = f'Wft {naam} 2026: free practice questions'
    if len(titel) > 60: titel = f'Wft {naam}: free practice questions'
    oms = f'Wft {naam}: free practice questions with real-life cases and explanations, what’s new in 2026, important dates and exam terms. Practice test for advisers.'
    if len(oms) > 160: oms = f'Wft {naam}: free practice questions with explanations, what’s new in 2026 and important dates. Practice test for advisers.'
    pagina_e(f'module-{mid}.html', titel, oms, f'Wft {html.escape(naam)}', f'Module {i:02d} · Permanent Actueel', inh, ld=ld, kruimel=f'Wft {naam}')

# ---------- What's new ----------
KWARTAAL_E = f'Q{(int(PEIL_ISO[5:7]) - 1) // 3 + 1} {PEIL_ISO[:4]}'
inh = (f'    <p class="lead">What’s new for financial advisers in {KWARTAAL_E}? Per Wft module the changes in legislation, exam terms and the market that you need to know to stay permanently up to date.</p>\n'
       f'    <p class="meta-regel">Legislation as at {PEIL_EN}</p>\n'
       '    <div class="acties"><a class="btn" href="quiz.html">Take the knowledge quiz</a></div>\n'
       + datums_e()
       + ''.join(f'    <h2 id="{m["id"]}"><a href="module-{m["id"]}.html">Wft {html.escape(m["naam"])}</a></h2>\n    <ul>' + ''.join(f'<li>{x}</li>' for x in NIEUW_E[m['id']]) + f'</ul>\n    <p><a href="quiz.html#{m["id"]}">Test your knowledge of Wft {html.escape(m["naam"])} →</a></p>\n' for m in MODS_E)
       + '  ' + NIEUWSBRIEVEN_E
       + '    <p class="klein">This overview helps you keep your knowledge up to date and is not advice. Always check amounts and standards in the applicable source. Spot an error? Email <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')
ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': f'What’s new in the Wft: {KWARTAAL_E}', 'inLanguage': 'en', 'dateModified': LAATSTE,
      'author': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'}, 'publisher': {'@type': 'Organization', 'name': 'DFO BV'},
      'mainEntityOfPage': f'{SITE}en/whats-new.html', 'about': [f'Wft {m["naam"]}' for m in MODS_E]}
pagina_e('whats-new.html', f'What’s new in the Wft: {KWARTAAL_E}', f'What’s new for financial advisers in {KWARTAAL_E}: per Wft module the changes in legislation, exam terms and the market.',
         f'What’s new: {KWARTAAL_E}', 'Permanent Actueel', inh, ld=ld, og_type='article', datum=LAATSTE)

# ---------- Glossary ----------
inh = ('    <p class="lead">The most important terms from the Wft, permanent education and the Wft modules, briefly explained. A handy memory aid while practising. Dutch terms are given in brackets.</p>\n'
       f'    <p class="meta-regel">Legislation as at {PEIL_EN}</p>\n'
       '    <nav class="abc" aria-label="Terms by letter">' + ' '.join(f'<a href="#letter-{l.lower()}">{l}</a>' for l in sorted({EN_BEGRIPPEN[b[0]][0][0].upper() for b in BEGRIPPEN})) + '</nav>\n'
       '    <dl class="begrippen">\n')
vorige = ''
for b in sorted(BEGRIPPEN, key=lambda x: EN_BEGRIPPEN[x[0]][0].lower()):
    term, uitleg = EN_BEGRIPPEN[b[0]]
    l = term[0].upper(); anker = f' id="letter-{l.lower()}"' if l != vorige else ''; vorige = l
    inh += (f'      <div class="begrip"{anker}><dt id="begrip-{slug(b[0])}">{html.escape(term)}</dt><dd>{html.escape(uitleg)} '
            + '<span class="begrip-mods">' + ' · '.join(f'<a href="module-{m}.html">Wft {html.escape(NAAM_E[m])}</a>' for m in b[2]) + '</span></dd></div>\n')
inh += ('    </dl>\n    <div class="acties"><a class="btn" href="quiz.html">Test your knowledge in the quiz</a><a class="btn ghost" href="search.html">Search the site</a></div>\n'
        '    <p class="klein">This explanation is simplified and is not advice. Amounts and limits change every year; always check the applicable source.</p>')
ld = {'@context': 'https://schema.org', '@graph': [{'@type': 'DefinedTermSet', '@id': SITE + 'en/glossary.html#terms', 'name': 'Glossary Wft — Permanent Actueel', 'inLanguage': 'en',
       'hasDefinedTerm': [{'@type': 'DefinedTerm', '@id': SITE + 'en/glossary.html#begrip-' + slug(b[0]), 'name': EN_BEGRIPPEN[b[0]][0], 'description': EN_BEGRIPPEN[b[0]][1], 'inDefinedTermSet': SITE + 'en/glossary.html#terms',
                           'url': SITE + 'en/glossary.html#begrip-' + slug(b[0])} for b in BEGRIPPEN]}]}
pagina_e('glossary.html', 'Wft glossary: PE, exam terms and Wft modules explained', 'What is a PE exam, a professional qualification, OVI or the Wtp? The most important Wft terms briefly and clearly explained for financial advisers.',
         'Wft glossary', 'Briefly explained', inh, ld=ld, kruimel='Wft glossary', datum=LAATSTE)

# ---------- FAQ ----------
inh = '\n'.join(f'    <details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in EN_FAQ)
ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in EN_FAQ]}
pagina_e('faq.html', 'Frequently asked questions — Wft Permanent Actueel', 'Answers to frequently asked questions about the free Wft knowledge quiz, PE exams, PE points, staying permanently up to date and the certificate.',
         'Frequently asked questions', 'Questions', inh, actief='faq.html', ld=ld)

# ---------- PE explained ----------
inh = ('    <p class="lead antwoord"><strong>Short answer:</strong> under the Wft there are no PE points any more. Since 1 January 2014 you keep your advising authority valid with one PE exam per professional qualification within each PE period; the current period runs until 31 March 2028 inclusive. '
       'Wft Permanent Actueel helps you practise for free; the quiz itself earns no PE points or PE exam.</p>\n'
       '    <div class="acties"><a class="btn" href="quiz.html">Practise for free</a><a class="btn ghost" href="index.html#check">Which modules do I need?</a></div>\n'
       + '\n'.join(f'    <h2>{q}</h2>\n    <p>{a}</p>' for q, a in EN_PE) +
       '\n    <h2>Practise per Wft module</h2>\n    <ul>' + ''.join(f'<li><a href="module-{m["id"]}.html">Wft {m["naam"]}</a>: PE practice questions</li>' for m in MODS_E) + '</ul>\n'
       '    <h2>Sources</h2>\n    <ul class="bronnen"><li><a href="https://cdfd.nl/" target="_blank" rel="noopener">CDFD — Dutch Financial Services Competence Board</a></li><li><a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">CDFD — advising authorities (in Dutch)</a></li><li><a href="https://cdfd.nl/wanneer-moet-ik-pe-examen-doen/" target="_blank" rel="noopener">CDFD — when do I have to take the PE exam? (in Dutch)</a></li><li><a href="https://cdfd.nl/mijn-wft/" target="_blank" rel="noopener">CDFD — Mijn Wft</a></li><li><a href="https://cdfd.nl/downloads/" target="_blank" rel="noopener">CDFD — downloads: final objectives and exam terms per module (in Dutch)</a></li>'
       '<li><a href="https://wetten.overheid.nl/BWBR0035213" target="_blank" rel="noopener">Establishment and mandate decree of the Dutch Financial Services Competence Board (Wft, in Dutch)</a></li>'
       '<li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">AFM — professional competence requirements (in Dutch)</a></li><li><a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/doorlopende-eisen-en-bedrijfsvoering/diplomaplicht-waar-moet-je-als-dienstverlener-aan-voldoen" target="_blank" rel="noopener">AFM — diploma requirement (in Dutch)</a></li>'
       f'<li><a href="{B["eind"][1]}" target="_blank" rel="noopener">{EN_B["eind"]}</a></li><li><a href="{B["wft"][1]}" target="_blank" rel="noopener">{EN_B["wft"]}</a></li></ul>\n'
       f'    <p class="klein">Reference date {PEIL_EN}. General information, not advice. The requirements that apply to you exactly can be found at the CDFD.</p>')
ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in EN_PE]}
pagina_e('pe-explained.html', 'PE points Wft and Permanent Actueel: how PE works in 2026', 'Do PE points still exist? How does PE work under the Wft and what is Wft Permanent Actueel? Explanation for financial advisers, plus free PE practice questions per module.',
         'PE points, PE exams and Wft Permanent Actueel', 'PE explained', inh, actief='pe-explained.html', ld=ld, kruimel='PE explained')

# ---------- Privacy, About, Terms, Complaints ----------
inh = f'''    <p class="lead">Wft Permanent Actueel uses no cookies and no trackers. We only use your details to create your result and certificate; a copy of the certificate goes to DFO BV.</p>
    <h2>Who is responsible</h2>
    <p>DFO BV, De Wel 14–16, 3871 MV Hoevelaken, the Netherlands. Privacy questions: <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>
    <h2>The quiz and the certificate</h2>
    <p>To see your result you enter your name and email address and, if you wish, your date of birth, the company you work for and your employer’s email address for an extra copy. In doing so you agree to a copy of your certificate going to DFO BV. Your browser uses that data to create the certificate; PA-WFT.nl does not store it itself and does not send it to a server automatically. The certificate is prepared as a pdf in an email to yourself, with a copy to DFO BV (info@dfobv.nl). You send that message yourself from your email programme: if you do not send it, DFO BV receives nothing and you do not get the certificate in your mailbox. Practice rounds, such as practising your wrong questions again or practising per exam term, do not ask for any details. If you close the tab, the data is gone from your browser.</p>
    <h2>What DFO BV does with the copy</h2>
    <p>DFO BV receives the copy in the mailbox info@dfobv.nl. That is the data on the certificate: your name, email address, the result, the modules and the date, plus your date of birth, company and your employer’s email address if you entered them. The legal basis is your consent: you tick the box to agree to the copy. DFO BV does not keep the email longer than necessary and does not use the data for purposes other than confirming your participation in the practice test.</p>
    <h2>Cookies and measuring</h2>
    <p>We do not use cookies, analytics or advertising services, or trackers. The font is hosted on our own site, so no data goes to external parties.</p>
    <h2>Hosting</h2>
    <p>This site does not place cookies, not even to remember choices. The site is hosted via GitHub Pages (GitHub, Inc.). Like any web server, GitHub processes technical data such as your IP address to deliver and secure the pages. See the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">GitHub privacy statement</a>.</p>
    <h2>Your rights</h2>
    <p>You can ask DFO BV to let you view, correct or delete the copy it has received from you: email <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>. If you have a question or complaint, email the same address. You can also file a complaint with the <a href="https://www.autoriteitpersoonsgegevens.nl/en" target="_blank" rel="noopener">Dutch Data Protection Authority</a>.</p>
    <p class="klein">Last updated: {PEIL_EN}.</p>'''
pagina_e('privacy.html', 'Privacy — Wft Permanent Actueel', 'How Wft Permanent Actueel handles your data: no cookies, no tracking, and a copy of your certificate goes to DFO BV.', 'Privacy statement', 'Privacy', inh)

inh = f'''    <p class="lead">Wft Permanent Actueel is a free practice environment for financial advisers: per Wft module practice questions with explanations, to test and maintain your knowledge.</p>
    <h2>Who is behind it</h2>
    <p>Wft Permanent Actueel is an activity of DFO BV, services for financial entrepreneurs. DFO BV, De Wel 14–16, 3871 MV Hoevelaken, the Netherlands, telephone <a href="tel:+31332580460">+31 33 258 04 60</a>, email <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>, <a href="https://www.dfobv.nl/contact/" target="_blank" rel="noopener">contact page</a>. KvK (Dutch Chamber of Commerce) 32068727, VAT number NL806480828B01. Get to know <a href="https://www.dfobv.nl/ons-team/" target="_blank" rel="noopener">our team</a>.</p>
    <h2>What it is and is not</h2>
    <ul>
      <li>It is a practice test. It is not a recognised PE exam and does not count towards the registration of your professional competence.</li>
      <li>The certificate confirms your result on the practice test. A copy goes to DFO BV when you send the email message.</li>
      <li>The content is general information and not advice. Always check legislation in the applicable source.</li>
      <li>This English version is a convenience translation of the Dutch site. Dutch legislation and the exams of the CDFD are in Dutch; where the translation differs, the Dutch text and the official sources prevail.</li>
    </ul>
    <h2>How the questions are made</h2>
    <p>The questions were drawn up with the help of AI, based on public legislation and the final objectives and exam terms of the Wft exams. Reference date: {PEIL_EN}. Amounts and percentages that change every year are deliberately not in the questions; the quiz is about principles and fixed concepts. For each module you can see the date on which the questions were last updated.</p>
    <h2>Spotted an error?</h2>
    <p>Email the question and what you think is wrong to <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>. We will adjust the question and update the date of the module.</p>'''
pagina_e('about.html', 'DFO BV and Wft Permanent Actueel: about and accountability', 'Who is behind Wft Permanent Actueel, what the quiz is and is not, and how the questions are made.', 'About and accountability', 'DFO BV', inh, actief='about.html')

inh = f'''    <p class="lead">These terms apply to the use of PA-WFT.nl. By using the site you agree to them.</p>
    <h2>Free and without an account</h2>
    <p>Wft Permanent Actueel is an activity of DFO BV. Use of the modules, the quiz and the certificate is free for all advisers. You do not need an account or a subscription. To see your result you enter your details; see the <a href="privacy.html">privacy statement</a>.</p>
    <h2>What the quiz is</h2>
    <p>The PA test is a practice test. It is not a recognised PE exam and does not count towards the registration of your professional competence. The certificate only confirms your result on the practice test; a copy goes to DFO BV when you send the email message. Do not use it as evidence of professional competence.</p>
    <h2>No advice, no guarantee</h2>
    <p>The content is general information, with {PEIL_EN} as the reference date. Despite our care, a question or explanation may be incorrect or outdated. Always check legislation in the applicable source before relying on it in your practice. DFO BV is not liable for damage arising from the use of this site, to the extent the law allows. The English version is a convenience translation; the Dutch version prevails.</p>
    <h2>Rights to the content</h2>
    <p>The questions, explanations, texts and design belong to DFO BV. You may use them for your own knowledge. Copying or distributing them, including in part, is only allowed with the permission of DFO BV.</p>
    <h2>Changes</h2>
    <p>DFO BV may change these terms and the content of the site. The version on this page applies.</p>
    <h2>Other services of DFO</h2>
    <p>The paid services of DFO BV are subject to DFO’s general terms of delivery; see <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">www.dfobv.nl</a>.</p>
    <p class="klein">Last updated: {PEIL_EN}.</p>'''
pagina_e('terms.html', 'Terms of use — Wft Permanent Actueel', 'Terms for the free use of PA-WFT.nl: practice test, no advice, rights to the content.', 'Terms of use', 'Terms', inh)

inh = f'''    <p class="lead">Not satisfied with Wft Permanent Actueel? Let us know and we will look for a solution together.</p>
    <h2>How to file a complaint</h2>
    <ol>
      <li>Email your complaint to <a href="mailto:info@dfobv.nl">info@dfobv.nl</a> or call <a href="tel:+31332580460">+31 33 258 04 60</a>.</li>
      <li>State your name, your email address and what your complaint is about. If it is about a quiz question, state the module and the question.</li>
      <li>We will confirm that we have received your complaint, investigate it and let you know what we do with it.</li>
    </ol>
    <h2>Error in a question</h2>
    <p>An error in a question is not a complaint but a report, and it is welcome. In the quiz, every question has the link “Doubt about this question? Email it straight to DFO”.</p>
    <h2>Can’t work it out together?</h2>
    <p>See the complaints procedure of DFO BV at <a href="https://www.dfobv.nl/" target="_blank" rel="noopener">www.dfobv.nl</a>.</p>
    <p class="klein">Last updated: {PEIL_EN}.</p>'''
pagina_e('complaints.html', 'Complaints — Wft Permanent Actueel', 'Not satisfied with Wft Permanent Actueel or the knowledge quiz? How to file a complaint with DFO BV and how we handle it.', 'Complaints procedure', 'Complaints', inh)

# ---------- Home ----------
inh = f'''<div class="paneel page" id="uitleg">
    <h2>Free for all advisers</h2>
    <p class="lead">Wft Permanent Actueel helps you keep your professional knowledge up to date. Practise with PE practice questions for exactly the Wft modules that match your diplomas and client contact, with an explanation for every answer. Free, without a subscription and without an account.</p>
    <p class="antwoord"><strong>Take the quiz every quarter</strong>, so you stay permanently up to date. Keep the certificate in your personnel file and also hand it to your employer.</p>
    <p class="klein">This English version is a convenience translation. Dutch legislation and the exams of the CDFD are in Dutch.</p>
    <div class="acties"><a class="btn" href="quiz.html">Start the knowledge quiz</a><a class="btn ghost" href="#modules">View the 9 modules</a></div>
    <div data-agenda><p><a href="quiz.html">Put the quiz in your calendar every quarter for the next 5 years</a></p></div>
    <form class="zoekform homezoek" action="search.html" method="get" role="search"><label for="homezoek">Search the site</label><div class="zoekrij"><input type="search" id="homezoek" name="q" placeholder="For example: CCD II, PE exam, box 3" maxlength="80"><button class="btn" type="submit">Search</button></div></form>
    <h2>Wft, PE and Permanent Actueel</h2>
    <p>As a financial adviser in the Netherlands you must remain professionally competent: you hold a Wft diploma and keep your knowledge up to date with permanent education (PE). PE points no longer exist under the Wft; since 1 January 2014 you take one PE exam per professional qualification within each PE period, at an exam institute recognised by the CDFD. The current PE period runs until 31 March 2028 inclusive. The PA test is a practice test and earns no PE points or PE exam.</p>
    <p>According to the AFM, staying permanently up to date applies to all employees with substantive client contact, including back office and support staff. Record which knowledge you have gained: keep your certificates in your competence or personnel file.</p>
    <p><a href="pe-explained.html">Read how PE, PE points and Permanent Actueel work</a> · <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">AFM professional competence requirements (in Dutch)</a></p>
</div>
<div class="paneel" id="modules">
    <h2>The 9 modules</h2>
    <p>Per module practice questions with explanations, with the date on which the questions were last updated.</p>
    <div class="modules" id="moduleGrid"></div>
</div>
<div class="paneel" id="check">
    <h2>Which modules do I need?</h2>
    <div class="check">
      <div><p>Choose your professional qualifications. You see which modules belong to them and take a quiz on exactly those modules. Within each PE period you take one PE exam per professional qualification.</p><div class="chips" id="chips"></div><p class="klein" id="checkNoot" aria-live="polite"></p><p class="klein">Source: <a href="https://www.afm.nl/nl-nl/sector/adviseurs-bemiddelaars-en-gevolmachtigde-agenten/themas/vakbekwaamheidseisen" target="_blank" rel="noopener">AFM professional competence requirements</a> and the CDFD, consulted October 2026. A tool, not advice.</p></div>
      <div class="result"><div class="ring-wrap">{RING}<div class="ring-count" id="count">0</div></div>
        <div class="pkg"><span class="label">Your PA package</span><span class="pkg-n" id="countLabel"></span><ul id="chosen"></ul><a class="btn" id="startToets" href="quiz.html">Quiz on my package</a></div></div>
    </div>
</div>
<div class="paneel" id="werkwijze">
    <h2>How it works</h2>
    <div class="steps">
      <div class="step"><span class="num">01</span><h3>Choose your modules</h3><p>Per professional qualification, or all modules mixed.</p></div>
      <div class="step"><span class="num">02</span><h3>Practise and learn</h3><p>7 questions per module, 5 extra per module you add, with an explanation for all four answers.</p></div>
      <div class="step"><span class="num">03</span><h3>Certificate</h3><p>Keep it in your personnel file and hand it to your employer.</p></div>
      <div class="step"><span class="num">04</span><h3>Every quarter</h3><p>Take the quiz every quarter, so you stay permanently up to date.</p></div>
    </div>
</div>
<div class="paneel" id="tip">
    <div data-tip><h3>Tip your colleagues</h3><p>Send your colleagues an invitation to the free knowledge quiz: <a href="mailto:?subject=Tip%3A%20test%20your%20Wft%20knowledge%20for%20free%20on%20PA-WFT.nl&amp;body=https%3A%2F%2Fpa-wft.nl%2Fen%2Fquiz.html">email a colleague</a>.</p></div>
</div>
<div class="paneel">
  ''' + NIEUWSBRIEVEN_E + f'''</div>
</div>
<section class="poster"><div class="wrap"><h2>Practise all modules in your package this year. Free.</h2><a class="btn btn-white" href="quiz.html">Start the knowledge quiz</a></div></section>
<div class="wrap">'''
pagina_e('index.html', 'Wft Permanent Actueel: free PE practice test for advisers',
         'Wft Permanent Actueel: free for all advisers. PE practice questions with explanations for all 9 Wft modules, from Basic to Pensions. With certificate.',
         'Wft Permanent Actueel', 'An activity of DFO BV', inh, actief='index.html', ld={'@context': 'https://schema.org', '@graph': []},
         intro='Knowledge up to date, every quarter again. Practise per Wft module with questions about what is current, with an explanation for every answer.',
         mast_extra='    <p class="gratis"><strong>Free for all advisers.</strong> All modules and the knowledge quiz, at no cost.</p>\n    ' + MARK.replace('<svg ', '<svg class="hero-mark" ', 1) + '\n',
         scripts=js(*S_BASIS, 'main.js', 'agenda.js', 'tip.js'), datum=LAATSTE)

# ---------- Quiz ----------
inh = ('<div class="paneel" id="paneel" aria-live="polite">\n      <noscript><p>Please enable JavaScript to take the quiz.</p></noscript>\n</div>\n'
       '<div class="paneel page">\n    <h2>How the Wft knowledge quiz works</h2>\n'
       '    <ol><li>Choose one or more Wft modules, or your whole package per professional qualification.</li><li>Answer the multiple-choice questions: many are real-life cases, aligned with the exam terms of the CDFD from 1 April 2026.</li>'
       '<li>After each answer you read why each of the four answers is right or wrong.</li><li>Afterwards you receive a certificate as a pdf, and you can practise your wrong questions again.</li></ol>\n'
       '    <h2>Modules in the quiz</h2>\n    <ul class="kolommen">' + ''.join(f'<li><a href="module-{m["id"]}.html">Wft {html.escape(m["naam"])}</a></li>' for m in MODS_E) + '</ul>\n'
       '    <h2>Frequently asked questions about the quiz</h2>\n'
       + ''.join(f'    <details class="faq"><summary>{v}</summary><p>{a}</p></details>\n' for v, a in EN_TOETS_FAQ)
       + '    <p>Want to know more? Read <a href="pe-explained.html">how PE works</a>, see the <a href="glossary.html">glossary</a> or <a href="whats-new.html">what’s new</a>. The questions are about Dutch legislation; this English version is a convenience translation.</p>\n</div>')
ld_toets = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'LearningResource', 'name': 'Wft knowledge quiz — Permanent Actueel', 'url': SITE + 'en/quiz.html', 'inLanguage': 'en', 'isAccessibleForFree': True,
     'learningResourceType': 'Practice test', 'educationalLevel': 'Professional level', 'audience': {'@type': 'Audience', 'audienceType': 'Financial advisers and client-facing employees'},
     'teaches': [f'Wft {m["naam"]}' for m in MODS_E], 'provider': {'@id': SITE + '#dfo'}},
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': v, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for v, a in EN_TOETS_FAQ]}]}
pagina_e('quiz.html', 'Free Wft knowledge quiz with explanations', 'Free Wft knowledge quiz for advisers: 7 questions per module, 5 extra per added module, different every time. With explanations and certificate.',
         'Wft knowledge quiz', 'Wft Permanent Actueel', inh, actief='quiz.html', ld=ld_toets, kruimel='Wft knowledge quiz',
         intro=f'Seven questions for one module, five extra for every module you add, different every time, across the {len(MODS_E)} Wft modules. For each answer you read why it is right or wrong, and afterwards you receive a certificate.',
         extra='\n<link rel="stylesheet" href="/assets/css/toets.css">',
         scripts=js_vragen_v() + js(*S_BASIS, 'agenda.js', 'tip.js', 'vendor/jspdf.umd.min.js', 'certpdf.js', 'toets.js'), datum=LAATSTE)

# ---------- Search ----------
inh = ('    <form class="zoekform" action="search.html" method="get" role="search">\n'
       '      <label for="zoekterm">Search the site</label>\n'
       '      <div class="zoekrij"><input type="search" id="zoekterm" name="q" autocomplete="off" placeholder="For example: CCD II, PE exam, box 3, OVI" maxlength="80">'
       '<button class="btn" type="submit">Search</button></div>\n    </form>\n'
       '    <p id="zoekstatus" class="zoekstatus" aria-live="polite"></p>\n    <ol id="zoekresultaten" class="zoekresultaten"></ol>\n'
       '    <noscript><p>Search needs JavaScript. See the <a href="/sitemap.xml">sitemap</a> instead.</p></noscript>\n'
       '    <h2>Popular topics</h2>\n    <p class="zoektips">' + ' '.join(f'<a href="search.html?q={urllib.parse.quote(t)}">{t}</a>' for t in ['PE exam', 'CCD II', 'exam terms', 'box 3', 'Wwft', 'Pension Transition Act', 'certificate', 'OVI']) + '</p>\n')
# (de zoekindex voor Engels wordt na het bouwen van alle pagina's geschreven)
pagina_e('search.html', 'Search — Wft Permanent Actueel', 'Search Wft Permanent Actueel: modules, current changes, PE, glossary and frequently asked questions.', 'Search', 'Search the site', inh, actief='search.html',
         scripts=js('taal.js', 'zoekindex-en.js', 'zoek.js'), datum=LAATSTE)
open(R + 'assets/js/zoekindex-en.js', 'w', encoding='utf-8').write('/* English search index, generated by tools/bouw-paginas.py. Do not edit by hand. */\nwindow.PA_ZOEK=' + json.dumps(ZOEK_EN, ensure_ascii=False, separators=(',', ':')) + ';\n')

# ---------- llms-full (Engels) ----------
volledig = ['# Wft Permanent Actueel (PA-WFT.nl) — full text (English)', '',
            f'> Free practice environment for financial advisers in the Netherlands by DFO BV. Reference date: {PEIL_EN}. Practice test, not a recognised PE exam and not advice. English convenience translation of the Dutch site; legislation and exams are in Dutch. Source: {SITE}en/', '']
huidige = None
for dd in ZOEK_EN:
    if dd['p'] != huidige:
        volledig += ['', f"## {dd['p']}", f"Source: {SITE}en/{dd['u'].split('#')[0]}", '']; huidige = dd['p']
    if dd['h']: volledig += [f"### {dd['h']}", '']
    volledig += [dd['x'], '']
open(R + 'llms-full-en.txt', 'w', encoding='utf-8').write('\n'.join(volledig) + '\n')
print('Engelse versie:', len(BIJGEWERKT_E), 'pagina’s,', len(ZOEK_EN), 'zoekrecords')
