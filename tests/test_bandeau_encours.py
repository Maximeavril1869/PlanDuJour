"""Tests : bandeau « en cours » fixé au-dessus des onglets, jour d'aujourd'hui seulement (0.38.0). Heure simulée, aucune donnée réelle.
Lancer :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_bandeau_encours.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, seed_defaults

MARDI = datetime(2026, 11, 3, 7, 0)
R = "() => { const r = document.querySelector('.runbar'); if (!r) return null; const a = r.getBoundingClientRect(), t = document.querySelector('.tabbar').getBoundingClientRect(); return { pos: getComputedStyle(r.parentElement).position, bottom: a.bottom, tabTop: t.top, vis: a.height > 0 && a.bottom <= innerHeight, tabVis: t.bottom <= innerHeight + 1 && t.height > 0 }; }"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.clock.install(time=MARDI)
        pg.goto(URL)
        seed_defaults(pg)
        pg.evaluate("() => localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: { '2026-11-03': { real: { 'act:act-trajet-aller': { start: 390, end: null } }, ponctuels: [], subtasks: {}, review: {}, profile: null, segs: {}, kidsDone: {}, presence: null, trip: null, removed: [] } } }))")
        pg.reload()
        print('Bandeau en cours')
        r = pg.evaluate(R)
        check('un bloc en cours affiche le bandeau', r is not None)
        check('le bandeau est fixé', r and r['pos'] == 'fixed', r)
        check('il est juste au-dessus des onglets', r and 0 <= r['tabTop'] - r['bottom'] <= 12, r)
        check('le menu reste visible', r and r['tabVis'] and r['vis'], r)
        pg.mouse.wheel(0, 3000)
        pg.wait_for_timeout(100)
        r2 = pg.evaluate(R)
        check('il reste en bas quand on fait défiler', r2 and r2['pos'] == 'fixed' and abs(r2['bottom'] - r['bottom']) < 1, (r, r2))
        check('le bouton Arrêter est cliquable', pg.locator('.runbar [data-action=stop]').is_visible())
        pg.screenshot(path='/tmp/claude-0/-home-claude/bb7425f0-ad10-5ec0-878f-57ac7ab3e28e/scratchpad/shots/encours.png')
        pg.click('[data-day-nav="1"]')
        check('un autre jour : pas de bandeau', pg.evaluate(R) is None)
        pg.click('[data-day-nav="today"]')
        check('retour à aujourd’hui : le bandeau revient', pg.evaluate(R) is not None)
        pg.click('#tab-recap')
        check('autre onglet : pas de bandeau visible', not pg.locator('.runbar').is_visible())
        check('autre onglet : le menu est visible', pg.evaluate(R.replace("document.querySelector('.runbar')", "document.querySelector('.tabbar')")) is not None)
        pg.click('#tab-day')
        pg.click('.runbar [data-action=stop]')
        check('« Arrêter » fait disparaître le bandeau', pg.evaluate(R) is None)
        check('aucune erreur JavaScript', not errs, errs)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
