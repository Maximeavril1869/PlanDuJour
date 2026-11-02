"""Tests : les cartes repliables sont fermées au départ (Réglages, page du jour).

Lancer depuis la racine du dépôt :  python3 tests/test_pliage.py
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, new_page, ponctuel, seed


def merged_seed(pg, today, past):
    """Aujourd'hui : un bloc sans heure. Hier : un bloc « à reporter » non fait (apparaît dans la revue)."""
    days = {'version': 2, 'days': {}}
    base = {'real': {}, 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None}
    days['days'][today] = dict(base, ponctuels=[ponctuel('idFree', 'Tâche libre test', None, 1, mode='free')])
    days['days'][past] = dict(base, ponctuels=[ponctuel('idPast', 'Bloc hier test', 600, 60, carry=True)])
    return days


def test_pliage(browser):
    print('Cartes repliées au départ')
    pg = new_page(browser)
    today, past = day_offset(pg, 0), day_offset(pg, -1)
    pg.close()
    pg = new_page(browser, merged_seed(None, today, past))

    check('page du jour : « Présence au travail » fermée', pg.evaluate("() => document.querySelector('details[data-fid=card-pres]').open") is False)
    sans = pg.locator('details[data-fid=card-sansheure]')
    check('page du jour : la carte « Sans heure » existe, repliable', sans.count() == 1)
    check('page du jour : « Sans heure » fermée au départ', pg.evaluate("() => document.querySelector('details[data-fid=card-sansheure]').open") is False)
    nb = pg.evaluate("() => document.querySelectorAll('details[data-fid=card-sansheure] li').length")
    check('le titre indique le nombre de tâches sans heure de la liste', nb >= 1 and ('Sans heure · %d' % nb) in pg.inner_text('details[data-fid=card-sansheure] summary'), nb)
    pg.click('details[data-fid=card-sansheure] summary')
    check('un tap sur le titre déplie la carte', pg.evaluate("() => document.querySelector('details[data-fid=card-sansheure]').open") is True)
    pg.click('[data-day-nav=today]')
    check('l’état déplié est conservé quand la page se réaffiche', pg.evaluate("() => document.querySelector('details[data-fid=card-sansheure]').open") is True)

    pg.click('[data-day-nav="-1"]')
    pg.wait_for_timeout(200)
    head = pg.locator('.rv-head')
    check('jour passé : la « Revue du jour » est repliée', head.count() == 1 and head.get_attribute('aria-expanded') == 'false')
    head.click()
    check('un tap sur la revue la déplie', pg.locator('.rv-head').get_attribute('aria-expanded') == 'true')

    pg.click('#tab-settings')
    opened = pg.evaluate("() => [...document.querySelectorAll('#panel-settings details')].filter((d) => d.open).map((d) => d.dataset.fid)")
    check('Réglages : aucune carte ni ligne dépliée au départ', opened == [], opened)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_pliage(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
