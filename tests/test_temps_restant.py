"""Tests : temps restant avant le coucher sur la ligne « maintenant » et rafraîchissement du Récap (0.31.0).

Sur la page du jour, la ligne « maintenant » porte, avec l'heure, le temps qui reste jusqu'au coucher (rien si le coucher est libre).
Le Récap rattrape l'heure dès qu'on ouvre l'onglet ou qu'on revient dans l'app (il restait sur l'heure du dernier affichage).
L'heure est simulée (horloge du navigateur) : aucune dépendance à l'heure réelle.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_temps_restant.py
Aucune donnée réelle : libellés inventés.
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check

MARDI = datetime(2026, 11, 3)       # profil Semaine : lever 05:45, coucher 22:00
VENDREDI = datetime(2026, 11, 6)    # profil Vendredi : coucher libre


def page(browser, day, h, m=0):
    pg = browser.new_page(viewport={'width': 390, 'height': 700})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.clock.install(time=day.replace(hour=h, minute=m))
    pg.goto(URL)
    return pg


def test_temps_restant(browser):
    print('Temps restant avant le coucher')
    pg = page(browser, MARDI, 11, 30)
    em = pg.locator('.nowline em')
    check('la ligne porte le temps restant jusqu’au coucher (22:00 − 11:30)', em.count() == 1 and em.inner_text() == '10 h 30 avant le coucher', em.inner_text() if em.count() else None)
    check('l’heure reste affichée', pg.inner_text('.nowline span') == '11:30')
    pg.clock.run_for(5 * 60 * 1000)
    pg.wait_for_function("() => document.querySelector('.nowline span') && document.querySelector('.nowline span').textContent === '11:35'", timeout=3000)
    check('le temps restant diminue avec l’heure (11:35 : 10 h 25)', pg.inner_text('.nowline em') == '10 h 25 avant le coucher', pg.inner_text('.nowline em'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()
    pg = page(browser, MARDI, 21, 15)
    check('à 21:15 : 45 min avant le coucher', '45' in pg.inner_text('.nowline em') and 'avant le coucher' in pg.inner_text('.nowline em'), pg.inner_text('.nowline em'))
    pg.close()
    pg = page(browser, VENDREDI, 11, 30)
    check('coucher libre (vendredi) : la ligne n’affiche que l’heure', pg.locator('.nowline').count() == 1 and pg.locator('.nowline em').count() == 0, pg.locator('.nowline em').count())
    pg.close()


def test_recap_rattrape(browser):
    print('Récap : l’heure est rattrapée')
    pg = page(browser, MARDI, 11, 30)
    pg.click('#tab-recap')
    check('le Récap montre 11:30', '11:30' in pg.inner_text('#panel-recap li.nowli'))
    pg.click('#tab-day')
    pg.clock.set_system_time(MARDI.replace(hour=16, minute=52))     # l'heure passe sans qu'aucune minuterie ne tourne (app en veille)
    pg.click('#tab-recap')
    check('en ouvrant l’onglet, le Récap affiche tout de suite la nouvelle heure (16:52)', '16:52' in pg.inner_text('#panel-recap li.nowli'), pg.inner_text('#panel-recap li.nowli'))
    pg.clock.set_system_time(MARDI.replace(hour=17, minute=3))
    pg.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
    check('au retour dans l’app (visibilitychange), le Récap ouvert est rattrapé (17:03)', '17:03' in pg.inner_text('#panel-recap li.nowli'), pg.inner_text('#panel-recap li.nowli'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_temps_restant(browser)
        test_recap_rattrape(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
