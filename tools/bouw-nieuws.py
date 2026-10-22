# -*- coding: utf-8 -*-
"""Nieuwsrubriek van PA-WFT.nl: overzicht (nieuws.html), een pagina per maand (nieuws-<jjjj-mm>.html) en een Atom-feed (nieuws.xml).
Data: tools/nieuws.json. Elk bericht heeft een officiële bron. Wordt via exec geladen door tools/bouw-paginas.py (zelfde namespace)."""

NIEUWS = json.load(open(R + 'tools/nieuws.json', encoding='utf-8'))['maanden']
NIEUWS.sort(key=lambda m: m['maand'], reverse=True)
for _m in NIEUWS: _m['items'].sort(key=lambda i: i['datum'], reverse=True)
NIEUWS_LAATSTE = max(i['datum'] for m in NIEUWS for i in m['items'])
NAAM_MOD = {m['id']: m['naam'] for m in MODS}

def maandnaam(mm):
    j, m = mm.split('-'); return f'{MAANDEN[int(m)-1]} {j}'
def maandpad(mm): return f'nieuws-{mm}.html'
def item_id(i): return i['datum'] + '-' + slug(i['titel'])[:60].rstrip('-')

def item_html(i, kop='h3'):
    mods = ' · '.join(f'<a href="module-{m}.html">Wft {html.escape(NAAM_MOD[m])}</a>' for m in i.get('modules', [])) if len(i.get('modules', [])) < 9 else 'Alle modules'
    return (f'    <article class="nb-item" id="{item_id(i)}">\n'
            f'      <p class="nb-meta"><span class="nb-label">{html.escape(i["label"])}</span> <time datetime="{i["datum"]}">{nl(i["datum"])}</time></p>\n'
            f'      <{kop}>{html.escape(i["titel"])}</{kop}>\n      <p>{html.escape(i["tekst"])}</p>\n'
            + (f'      <p class="nb-praktijk"><strong>Wat betekent dit voor jou?</strong> {html.escape(i["praktijk"])}</p>\n' if i.get('praktijk') else '')
            + ('      <p class="nb-bron"><strong>Bron:</strong> ' + ' · '.join(f'<a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(t)}</a>' for t, u in i['bron']) + '</p>\n')
            + (f'      <p class="nb-mods"><strong>Relevant voor:</strong> {mods}</p>\n' if mods else '')
            + '    </article>\n')

NB_NOOT = ('    <p class="klein">Algemene informatie, geen advies. Elk bericht is gebaseerd op een officiële bron en naar eigen inzicht samengevat; raadpleeg voor besluiten altijd de bron zelf. '
           'Zie je een fout of mis je iets? Mail <a href="mailto:info@dfobv.nl">info@dfobv.nl</a>.</p>')

def ld_nieuws(pad, titel, omschrijving, items, datum):
    return {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': titel, 'description': omschrijving, 'inLanguage': 'nl', 'dateModified': datum, 'url': SITE + pad,
         'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': n + 1, 'url': f'{SITE}{maandpad(i["datum"][:7])}#{item_id(i)}', 'name': i['titel']} for n, i in enumerate(items)]}},
        *[{'@type': 'NewsArticle', '@id': f'{SITE}{maandpad(i["datum"][:7])}#{item_id(i)}', 'headline': i['titel'], 'description': i['tekst'][:300], 'datePublished': i['datum'], 'dateModified': i['datum'],
           'inLanguage': 'nl', 'author': {'@type': 'Organization', 'name': 'DFO BV', 'url': 'https://www.dfobv.nl/'}, 'publisher': {'@id': SITE + '#dfo'},
           'mainEntityOfPage': f'{SITE}{maandpad(i["datum"][:7])}#{item_id(i)}', 'isBasedOn': [u for _, u in i['bron']]} for i in items]]}

# ---------- maandpagina's ----------
for n, m in enumerate(NIEUWS):
    pad = maandpad(m['maand']); naam = maandnaam(m['maand'])
    nieuwer = NIEUWS[n - 1] if n > 0 else None; ouder = NIEUWS[n + 1] if n + 1 < len(NIEUWS) else None
    BIJGEWERKT[pad] = max(i['datum'] for i in m['items'])
    inh = (f'    <p class="lead">{html.escape(m["samenvatting"])}</p>\n'
           f'    <p class="meta-regel">{len(m["items"])} {"bericht" if len(m["items"]) == 1 else "berichten"} · peildatum regelgeving {PEIL}</p>\n'
           + ''.join(item_html(i, 'h2') for i in m['items'])
           + '    <nav class="nb-blader" aria-label="Andere maanden">' + (f'<a href="{maandpad(ouder["maand"])}">← {maandnaam(ouder["maand"])}</a>' if ouder else '<span></span>')
           + '<a href="nieuws.html">Alle maanden</a>' + (f'<a href="{maandpad(nieuwer["maand"])}">{maandnaam(nieuwer["maand"])} →</a>' if nieuwer else '<span></span>') + '</nav>\n'
           + '  ' + NIEUWSBRIEVEN + NB_NOOT)
    t = f'Wft-nieuws {naam}: wat is er veranderd voor adviseurs'
    o = f'Het actuele Wft-nieuws van {naam}: {m["samenvatting"]}'
    pagina(pad, t, o, f'Wft-nieuws {naam}', 'Nieuws per maand', inh, actief='nieuws.html', ld=ld_nieuws(pad, t, o, m['items'], BIJGEWERKT[pad]), kruimel=f'Nieuws {naam}', og_type='article')

# ---------- overzicht ----------
laatste = [i for m in NIEUWS for i in m['items']][:3]
inh = ('    <p class="lead">Elke maand het actuele nieuws voor financieel adviseurs: wetgeving, toezicht, permanente educatie en examens. Alleen berichten met een officiële bron, kort samengevat en met wat het voor jou betekent.</p>\n'
       f'    <p class="meta-regel">Laatst bijgewerkt {nl(NIEUWS_LAATSTE)} · <a href="nieuws.xml">Volg via feed (Atom)</a></p>\n'
       '    <h2>Laatste berichten</h2>\n' + ''.join(item_html(i) for i in laatste)
       + '    <h2>Nieuws per maand</h2>\n    <div class="kaarten">'
       + ''.join(f'<article class="kaart"><h3><a href="{maandpad(m["maand"])}">{maandnaam(m["maand"]).capitalize()}</a></h3><p>{html.escape(m["samenvatting"])}</p></article>' for m in NIEUWS)
       + '</div>\n    <p class="klein">Maanden zonder bevestigd nieuws staan er niet tussen. Voor het kwartaaloverzicht per module: <a href="nieuw.html">Wat is er nieuw</a>.</p>\n'
       + '  ' + NIEUWSBRIEVEN + NB_NOOT)
alle = [i for m in NIEUWS for i in m['items']]
BIJGEWERKT['nieuws.html'] = NIEUWS_LAATSTE
pagina('nieuws.html', 'Wft-nieuws per maand voor financieel adviseurs', 'Elke maand het actuele nieuws over de Wft, BGfo, TRHK, PE en examens, met officiële bron en wat het voor jou betekent.',
       'Wft-nieuws', 'Per maand actueel', inh, actief='nieuws.html', ld=ld_nieuws('nieuws.html', 'Wft-nieuws per maand', 'Het actuele Wft-nieuws per maand.', alle, NIEUWS_LAATSTE), kruimel='Nieuws')

# ---------- Atom-feed ----------
def esc(t): return html.escape(t, quote=True)
feed = ('<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="nl">\n'
        f'  <title>Wft-nieuws — Wft Permanent Actueel</title>\n  <subtitle>Het actuele Wft-nieuws per maand voor financieel adviseurs</subtitle>\n'
        f'  <link rel="self" href="{SITE}nieuws.xml"/>\n  <link href="{SITE}nieuws.html"/>\n  <id>{SITE}nieuws.html</id>\n  <updated>{NIEUWS_LAATSTE}T00:00:00Z</updated>\n'
        '  <author><name>DFO BV</name><uri>https://www.dfobv.nl/</uri></author>\n')
for i in alle:
    u = f'{SITE}{maandpad(i["datum"][:7])}#{item_id(i)}'
    feed += (f'  <entry><title>{esc(i["titel"])}</title><link href="{u}"/><id>{u}</id><updated>{i["datum"]}T00:00:00Z</updated>'
             f'<category term="{esc(i["label"])}"/><summary>{esc(i["tekst"][:400])}</summary></entry>\n')
open(R + 'nieuws.xml', 'w', encoding='utf-8').write(feed + '</feed>\n')

# ---------- blok op de homepage, vóór de nieuwsbrieven ----------
blok = ('<section class="nb-home" aria-labelledby="nbh-kop"><h2 id="nbh-kop">Wft-nieuws</h2><ul>'
        + ''.join(f'<li><time datetime="{i["datum"]}">{nl(i["datum"])}</time> <a href="{maandpad(i["datum"][:7])}#{item_id(i)}">{html.escape(i["titel"])}</a></li>' for i in laatste)
        + '</ul><p><a href="nieuws.html">Alle nieuws per maand →</a></p></section>\n')
_s = open(R + 'index.html', encoding='utf-8').read()
_a = '<section class="nieuwsbrieven"'
if _a in _s and 'nb-home' not in _s: open(R + 'index.html', 'w', encoding='utf-8').write(_s.replace(_a, blok + _a, 1))
KENNIS_PAGINAS.append('nieuws.html')
