"""Tests : choisir un jour dans le calendrier depuis l'onglet Jour (0.34.0). Heure simulée, aucune donnée réelle.
Lancer :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_choix_date.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check

MARDI = datetime(2026, 11, 3, 8, 0)


def label(pg):
    return pg.inner_text('#panel-day .daylabel').strip()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.clock.install(time=MARDI)
        pg.goto(URL)
        print('Choix de la date')
        check('le champ date est dans le libellé du jour', pg.locator('#day-date').count() == 1)
        check('il vaut la date du jour', pg.input_value('#day-date') == '2026-11-03', pg.input_value('#day-date'))
        check('il couvre le libellé (un appui l’atteint)', pg.evaluate("() => { const a = document.querySelector('.daypick').getBoundingClientRect(), b = document.querySelector('#day-date').getBoundingClientRect(); return b.width >= a.width - 1 && b.height >= a.height - 1; }"))
        pg.fill('#day-date', '2027-03-15')
        check('choisir une date lointaine y va directement', pg.input_value('#day-date') == '2027-03-15', (label(pg), pg.input_value('#day-date')))
        check('le libellé suit', 'mars' in label(pg).lower(), label(pg))
        pg.click('[data-day-nav="1"]')
        check('les flèches repartent de ce jour', pg.input_value('#day-date') == '2027-03-16', pg.input_value('#day-date'))
        pg.click('[data-day-nav="today"]')
        check('« Aujourd’hui » revient', pg.input_value('#day-date') == '2026-11-03', pg.input_value('#day-date'))
        pg.fill('#day-date', '')
        check('un champ vidé garde le jour affiché', pg.input_value('#day-date') == '2026-11-03', pg.input_value('#day-date'))
        pg.click('#tab-recap')
        check('l’onglet Récap n’a pas de champ date', pg.locator('#panel-recap input[type=date]').count() == 0)
        check('aucune erreur JavaScript', not errs, errs)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
