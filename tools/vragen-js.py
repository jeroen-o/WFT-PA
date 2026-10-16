"""Schrijft de vragenbank per module naar assets/js/vragen/<id>.js (Engels: assets/js/vragen-en/<id>.js).

Gebruik:
  python3 tools/vragen-js.py <map-met-json> [en]   # bestanden <id>-def.json of <id>.json met {"vragen":[{"v","a","t"}]}
Elke vraag wordt [vraag, [[antwoord, uitleg] x4], toetsterm]; het EERSTE antwoord is steeds het juiste (de toets husselt zelf).
Pas na een inhoudelijke wijziging de datum "bijgewerkt" en het log aan in assets/js/modules.js en draai tools/bouw-paginas.py.
"""
import json, os, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
DOEL = R + 'assets/js/vragen/'
TAAL = 'en' if sys.argv[-1:] == ['en'] else 'nl'
if TAAL == 'en': DOEL = R + 'assets/js/vragen-en/'
MODS = json.loads(subprocess.check_output(['node', '-e', "global.window={};eval(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(JSON.stringify(window.PA_MODULES))", R + 'assets/js/modules.js']))

def controleer(mid, vs):
    for i, q in enumerate(vs):
        assert isinstance(q[0], str) and q[0].strip(), (mid, i, 'lege vraag')
        assert len(q[1]) == 4 and all(len(a) == 2 and a[0].strip() and a[1].strip() for a in q[1]), (mid, i, 'antwoorden')
        assert len({a[0] for a in q[1]}) == 4, (mid, i, 'dubbele antwoorden')

def schrijf(mid, vs):
    controleer(mid, vs)
    naam = next(m['naam'] for m in MODS if m['id'] == mid)
    if TAAL == 'en':
        naam = {'basis': 'Basic', 'consumptief-krediet': 'Consumer Credit', 'hypothecair-krediet': 'Mortgage Credit', 'schade-particulier': 'Non-life Insurance (Personal)', 'schade-zakelijk': 'Non-life Insurance (Commercial)', 'vermogen': 'Wealth', 'inkomen': 'Income', 'pensioen': 'Pensions', 'zorgverzekering': 'Health Insurance'}[mid]
    regels = ',\n'.join(json.dumps(q, ensure_ascii=False) for q in vs)
    os.makedirs(DOEL, exist_ok=True)
    with open(DOEL + mid + '.js', 'w', encoding='utf-8') as f:
        f.write(f'/* {"Question bank PA test (English convenience translation), Wft " if TAAL == "en" else "Vragenbank PA-toets, Wft "}{naam}. Vorm: [vraag, [[antwoord, uitleg] x4], toetsterm CDFD]; het EERSTE antwoord is steeds het juiste.\n'
                '   Gegenereerd met tools/vragen-js.py. */\n'
                f'(window.PA_VRAGEN = window.PA_VRAGEN || {{}})[{json.dumps(mid)}] = [\n{regels}\n];\n')
    print(f'{mid}: {len(vs)} vragen')

if __name__ == '__main__':
    bron = sys.argv[1]
    for m in MODS:
        for naam in (m['id'] + '-def.json', m['id'] + '.json'):
            if os.path.exists(os.path.join(bron, naam)):
                d = json.load(open(os.path.join(bron, naam), encoding='utf-8'))
                schrijf(m['id'], [[q['v'], q['a']] + ([q['t']] if q.get('t') else []) for q in d['vragen']])
                break
        else:
            print(f'{m["id"]}: geen bestand, ongewijzigd')
