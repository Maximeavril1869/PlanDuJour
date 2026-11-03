"""Tests : ligne « maintenant » (0.26.0).

Une ligne horizontale suit l'heure sur la frise du jour (et une ligne « Maintenant » dans le Récap de la journée courante) ;
rien avant le lever, après le coucher ni sur un autre jour ; la page se place sur la ligne à l'ouverture puis on défile librement.
L'heure est simulée (horloge du navigateur) : aucune dépendance à l'heure réelle.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_maintenant.py
Aucune donnée réelle : libellés inventés.
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, ponctuel

TODAY = datetime(2026, 11, 3)


def page(browser, h, m=0):
    pg = browser.new_page(viewport={'width': 390, 'height': 700})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.clock.install(time=TODAY.replace(hour=h, minute=m))
    pg.goto(URL)
    day = {'real': {}, 'ponctuels': [ponctuel('p1', 'Bloc matin test', 540, 60), ponctuel('p2', 'Bloc soir test', 840, 60)],
           'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None}
    pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify(d))", {'version': 2, 'days': {'2026-11-03': day}})
    pg.reload()
    return pg


def top(pg, sel):
    return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.getBoundingClientRect().top + window.scrollY : null; }", sel)


def block_top(pg, name):
    return pg.evaluate("(n) => { const e = [...document.querySelectorAll('.blk')].find((b) => b.textContent.includes(n)); return e.getBoundingClientRect().top + window.scrollY; }", name)


def test_frise(browser):
    print('Ligne sur la frise du jour')
    pg = page(browser, 11, 30)
    check('une ligne « maintenant » est affichée avec l’heure', pg.locator('.nowline').count() == 1 and pg.inner_text('.nowline') == '11:30', pg.locator('.nowline').count())
    t = top(pg, '.nowline')
    check('elle est entre le bloc du matin et le bloc du soir', block_top(pg, 'Bloc matin test') + 80 < t < block_top(pg, 'Bloc soir test'), (t, block_top(pg, 'Bloc matin test'), block_top(pg, 'Bloc soir test')))
    h11 = pg.evaluate("() => { const s = [...document.querySelectorAll('.hline')].find((h) => h.textContent.includes('11:00')); return s.getBoundingClientRect().top + window.scrollY; }")
    check('la position est proportionnelle au temps (11 h 30 = 45 px sous 11 h 00)', abs(t - h11 - 45) <= 2, (t, h11))
    pg.clock.run_for(5 * 60 * 1000)
    pg.wait_for_function("() => document.querySelector('.nowline') && document.querySelector('.nowline').textContent === '11:35'", timeout=3000)
    check('elle avance seule avec l’heure (11:35, plus bas)', top(pg, '.nowline') > t, (t, top(pg, '.nowline')))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_hors_plage(browser):
    print('Aucune ligne hors de la journée')
    for h, m, why in ((3, 0, 'avant le lever'), (5, 30, 'juste avant le lever (05:45)'), (23, 50, 'après le coucher')):
        pg = page(browser, h, m)
        check('pas de ligne ' + why, pg.locator('.nowline').count() == 0, pg.locator('.nowline').count())
        check('aucune erreur JavaScript (' + why + ')', not pg.errors, pg.errors)
        pg.close()
    pg = page(browser, 11, 30)
    pg.click('[data-day-nav="-1"]')
    check('pas de ligne sur un autre jour (la veille)', pg.locator('.nowline').count() == 0)
    pg.click('[data-day-nav="today"]')
    check('la ligne revient sur aujourd’hui', pg.locator('.nowline').count() == 1)
    pg.close()


def test_defilement(browser):
    print('Défilement')
    pg = page(browser, 14, 30)
    pg.wait_for_timeout(100)
    y = pg.evaluate("() => window.scrollY")
    r = pg.evaluate("() => document.querySelector('.nowline').getBoundingClientRect().top")
    check('à l’ouverture la page est placée sur la ligne (visible dans l’écran)', y > 0 and 0 <= r <= 700, (y, r))
    pg.evaluate("() => window.scrollTo(0, 0)")
    pg.clock.run_for(60 * 1000)
    pg.wait_for_timeout(100)
    check('ensuite on défile librement : le rafraîchissement ne ramène pas la page', pg.evaluate("() => window.scrollY") == 0)
    pg.click('[data-day-nav="-1"]')
    pg.click('[data-day-nav="today"]')
    r = pg.evaluate("() => document.querySelector('.nowline').getBoundingClientRect().top")
    check('revenir sur aujourd’hui replace la page sur la ligne', 0 <= r <= 700, r)
    pg.evaluate("() => window.scrollTo(0, 0)")
    pg.click('#tab-stats')
    pg.click('#tab-day')
    r = pg.evaluate("() => document.querySelector('.nowline').getBoundingClientRect().top")
    check('toucher l’onglet « Jour » (depuis un autre onglet) recentre sur la ligne', 0 <= r <= 700, r)
    pg.evaluate("() => window.scrollTo(0, 0)")
    pg.click('#tab-day')
    r = pg.evaluate("() => document.querySelector('.nowline').getBoundingClientRect().top")
    check('toucher « Jour » alors qu’on y est déjà recentre aussi', 0 <= r <= 700, r)
    pg.click('[data-day-nav="-1"]')
    pg.click('#tab-day')
    check('sur un jour passé, « Jour » ne cherche pas de ligne (pas d’erreur, en haut de page)', pg.evaluate("() => window.scrollY") == 0 and not pg.errors, pg.errors)
    pg.close()


def test_recap(browser):
    print('Ligne dans le Récap')
    pg = page(browser, 11, 30)
    pg.click('#tab-recap')
    check('« Maintenant 11:30 » apparaît dans le Récap de la journée courante', pg.locator('#panel-recap li.nowli').count() == 1 and '11:30' in pg.inner_text('#panel-recap li.nowli'))
    order = pg.evaluate("() => [...document.querySelectorAll('#panel-recap .tl li')].map((l) => l.textContent)")
    i = [k for k, t in enumerate(order) if 'Maintenant' in t][0]
    check('elle est placée entre les deux blocs', any('Bloc matin test' in t for t in order[:i]) and any('Bloc soir test' in t for t in order[i + 1:]), order)
    pg.clock.run_for(5 * 60 * 1000)
    pg.wait_for_function("() => document.querySelector('#panel-recap li.nowli') && document.querySelector('#panel-recap li.nowli').textContent.includes('11:35')", timeout=3000)
    check('elle avance avec l’heure (11:35)', '11:35' in pg.inner_text('#panel-recap li.nowli'))
    pg.click('[data-recap-mode=type]')
    check('pas de ligne en semaine type', pg.locator('#panel-recap li.nowli').count() == 0)
    pg.click('[data-recap-mode=reel]')
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()
    pg = page(browser, 23, 50)
    pg.click('#tab-recap')
    check('pas de ligne dans le Récap après le coucher', pg.locator('#panel-recap li.nowli').count() == 0)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_frise(browser)
        test_hors_plage(browser)
        test_defilement(browser)
        test_recap(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
