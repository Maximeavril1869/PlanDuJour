"""Tests : ordre de la page du jour et libellés (0.41.0). Heure simulée, aucune donnée réelle.
- « Présence du jour » est juste sous « Profil de la journée », avant la carte « Présence au travail » ;
- la carte « Sans heure » s'appelle « Tâches » (page du jour et Récap, semaine type).
Lancer :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_ordre_jour.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, seed_defaults

MARDI = datetime(2026, 11, 3, 9, 0)
ORDER = "() => { const h = document.querySelector('#day-head'); const pos = (sel) => { const e = h.querySelector(sel); return e ? [...h.children].indexOf(e.closest('#day-head > *')) : -1; };" \
        " return { prof: pos('#day-profile'), bar: pos('.workbar'), pres: pos('details[data-fid=card-pres]'), trip: pos('details[data-fid=card-trip]') }; }"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.clock.install(time=MARDI)
        pg.goto(URL)
        seed_defaults(pg)
        pg.click('details[data-fid=card-pres] summary')
        pg.click('[data-action=pres-in]')           # une présence enregistrée : la barre « Présence du jour » s'affiche
        pg.wait_for_timeout(200)
        print('Page du jour : ordre')
        o = pg.evaluate(ORDER)
        check('« Présence du jour » est affichée', o['bar'] >= 0, o)
        check('« Présence du jour » est juste après le profil de la journée', o['bar'] > o['prof'] >= 0 and o['bar'] - o['prof'] <= 2, o)
        check('« Présence du jour » est avant la carte « Présence au travail »', o['bar'] < o['pres'], o)
        check('« Présence du jour » est avant « Départ et retour »', o['bar'] < o['trip'], o)
        print('Libellés « Tâches »')
        titles = pg.evaluate("() => [...document.querySelectorAll('#day-head summary h2')].map((h) => h.textContent)")
        check('la carte de la page du jour s’appelle « Tâches · n »', any(t.startswith('Tâches · ') for t in titles) and not any(t.startswith('Sans heure') for t in titles), titles)
        pg.click('#tab-recap')
        pg.click('[data-recap-mode=type]')
        h2 = pg.evaluate("() => [...document.querySelectorAll('#panel-recap .card h2')].map((h) => h.textContent)")
        check('le Récap (semaine type) a une carte « Tâches », plus « Sans heure »', 'Tâches' in h2 and 'Sans heure' not in h2, h2)
        check('aucune erreur JavaScript', not errs, errs)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
