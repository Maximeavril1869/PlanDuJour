"""Tests : « À confirmer » et bloc en cours fixés au-dessus des onglets (0.39.0), aujourd'hui seulement. Heure simulée, aucune donnée réelle.
Lancer :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_bas_ecran.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, seed_defaults

MARDI_SOIR = datetime(2026, 11, 3, 18, 0)
BOXES = "() => { const q = (s) => { const e = document.querySelector(s); if (!e || e.getClientRects().length === 0) return null; const r = e.getBoundingClientRect(); return { pos: getComputedStyle(e).position, top: r.top, bottom: r.bottom }; }; return { conf: q('.confbar'), run: q('.runbar'), tab: q('.tabbar'), dock: q('#day-dock'), inline: document.querySelectorAll('#day-head .card:not(.confbar)').length }; }"


PONCT = "[{ id: 'p1', name: 'Réunion test', mode: 'fixed', entry: 'duration', start: 600, duration: 30, confirm: true, carry: false, cat: null, alarm: null, parallel: false, toCal: false }]"


def day(real):
    return ("() => localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: { '2026-11-03': { real: REAL, ponctuels: " + PONCT + ", subtasks: {}, review: {}, profile: null, segs: {}, kidsDone: {}, presence: null, trip: null, removed: [] } } }))").replace('REAL', real)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.clock.install(time=MARDI_SOIR)
        pg.goto(URL)
        seed_defaults(pg)
        pg.evaluate(day('{}'))
        pg.reload()
        print('À confirmer en bas de l’écran')
        b = pg.evaluate(BOXES)
        check('un bloc passé à confirmer affiche le cadre « À confirmer »', b['conf'] is not None, b)
        check('le cadre est fixé', b['conf'] and b['dock']['pos'] == 'fixed', b)
        check('il est juste au-dessus des onglets', b['conf'] and 0 <= b['tab']['top'] - b['conf']['bottom'] <= 12, b)
        check('le menu reste visible', b['tab']['bottom'] <= 844 + 1)
        check('il contient le bloc et Fait / Raté', pg.locator('.confbar [data-action=confirm-done]').count() >= 1 and pg.locator('.confbar [data-action=confirm-missed]').count() >= 1)
        check('pas de doublon dans la page', pg.locator('#day-head > .card:has(h2:text("À confirmer"))').count() == 0)
        pg.mouse.wheel(0, 3000)
        pg.wait_for_timeout(100)
        b2 = pg.evaluate(BOXES)
        check('il reste en bas au défilement', b2['conf'] and abs(b2['conf']['bottom'] - b['conf']['bottom']) < 1, (b, b2))
        pg.evaluate(day("{ 'act:act-trajet-aller': { start: 390, end: null } }"))
        pg.reload()
        b = pg.evaluate(BOXES)
        check('avec un bloc en cours : les deux sont là', b['conf'] and b['run'], b)
        check('« À confirmer » est au-dessus du bloc en cours', b['conf'] and b['run'] and b['conf']['bottom'] <= b['run']['top'] + 1, b)
        check('le bloc en cours reste collé aux onglets', b['run'] and 0 <= b['tab']['top'] - b['run']['bottom'] <= 12, b)
        pg.screenshot(path='/tmp/claude-0/-home-claude/bb7425f0-ad10-5ec0-878f-57ac7ab3e28e/scratchpad/shots/bas.png')
        pg.click('.confbar [data-action=confirm-done]')
        b = pg.evaluate(BOXES)
        check('« Fait » retire le bloc du cadre', b['conf'] is None or pg.locator('.confbar [data-action=confirm-done]').count() == 0, b)
        pg.click('[data-day-nav="-1"]')
        b = pg.evaluate(BOXES)
        check('un jour passé : pas de bas fixé', b['dock'] is None, b)
        check('un jour passé : « À confirmer » reste dans la page', pg.locator('#day-head > .card:has(h2:text("À confirmer"))').count() == 1)
        pg.click('[data-day-nav="today"]')
        pg.click('#tab-recap')
        check('autre onglet : rien de fixé visible', pg.evaluate(BOXES)['dock'] is None)
        check('aucune erreur JavaScript', not errs, errs)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
