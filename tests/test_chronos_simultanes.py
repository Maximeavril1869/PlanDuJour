"""Tests : plusieurs tâches « sans heure » peuvent tourner en même temps (0.42.0).

Démarrer une tâche sans heure (ou une de ses sous-activités) n'arrête plus les autres tâches sans heure ; une barre « en cours » par tâche ;
pas d'alerte de chevauchement entre deux tâches sans heure ; un bloc à heure fixe en cours est toujours coupé au démarrage d'une tâche sans heure ;
Pause et « Je pars » coupent tous les chronos sans heure. Heure simulée, aucune donnée réelle : libellés inventés.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chronos_simultanes.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, stored_days
from test_coupure_presence import base, fixed_act, open_pres
from test_regroupements import free_act

MARDI = datetime(2026, 11, 3)
DATE = '2026-11-03'


def page(browser, h, m, days):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.clock.install(time=MARDI.replace(hour=h, minute=m))
    pg.goto(URL)
    kids = free_act('a-kids', 'Courrier test', None)
    kids['children'] = [{'id': 'k1', 'name': 'Canal A'}, {'id': 'k2', 'name': 'Canal B'}]
    acts = [free_act('a-dossier', 'Dossier test', None), free_act('a-code', 'Code test', None), kids, fixed_act('a-fixe', 'Réunion test')]
    settings = pg.evaluate("(a) => { const s = window.PDJ.defaultSettings(); s.categories = []; s.activities = a; s.templates = []; return s; }", acts)
    pg.evaluate("([s, d]) => { localStorage.setItem('plandujour.reglages', JSON.stringify(s)); localStorage.setItem('plandujour.jours', JSON.stringify(d)); }",
                [settings, {'version': 2, 'days': {DATE: days}}])
    pg.reload()
    return pg


def day(pg):
    return stored_days(pg).get(DATE, {})


def seg(pg, key):
    return day(pg).get('segs', {}).get(key, [])


def open_taches(pg):
    if pg.locator('details[data-fid=card-sansheure]').get_attribute('open') is None:
        pg.click('details[data-fid=card-sansheure] > summary')
    if pg.locator('details[data-fid=sans-none]').get_attribute('open') is None:
        pg.click('details[data-fid=sans-none] > summary')


def start(pg, key):
    open_taches(pg)
    pg.click('[data-action=start][data-key="%s"]' % key)


def test_deux_taches(browser):
    print('Deux tâches sans heure en même temps')
    pg = page(browser, 9, 0, base())
    start(pg, 'act:a-dossier')
    pg.clock.set_system_time(MARDI.replace(hour=9, minute=40))
    start(pg, 'act:a-code')
    a, b = seg(pg, 'act:a-dossier'), seg(pg, 'act:a-code')
    check('la première tâche reste en cours', len(a) == 1 and a[0]['start'] == 540 and a[0]['end'] is None, a)
    check('la seconde démarre à 9:40 (580) sans couper la première', len(b) == 1 and b[0]['start'] == 580 and b[0]['end'] is None, b)
    check('deux barres « en cours » sont affichées', pg.locator('.runbar').count() == 2, pg.locator('.runbar').count())
    check('aucune alerte de chevauchement entre les deux', pg.locator('.banner.warn').count() == 0, pg.locator('.banner.warn').all_inner_texts())
    pg.clock.set_system_time(MARDI.replace(hour=10, minute=0))
    pg.locator('.runbar [data-action=stop][data-key="act:a-dossier"]').click()
    a, b = seg(pg, 'act:a-dossier'), seg(pg, 'act:a-code')
    check('arrêter la première (10:00) garde son temps complet : 9:00 à 10:00', a[0]['end'] == 600, a)
    check('la seconde continue', b[0]['end'] is None and pg.locator('.runbar').count() == 1, b)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_bloc_fixe(browser):
    print('Bloc à heure fixe en cours')
    pg = page(browser, 10, 30, base({'segs': {'act:a-dossier': [{'cid': '', 'start': 540, 'end': None}]}, 'real': {'act:a-fixe': {'start': 600, 'end': None}}}))
    start(pg, 'act:a-code')
    check('le bloc à heure fixe en cours est coupé à 10:30 (630) comme avant', day(pg)['real']['act:a-fixe']['end'] == 630, day(pg)['real'])
    check('la tâche sans heure déjà en cours continue', seg(pg, 'act:a-dossier')[0]['end'] is None, seg(pg, 'act:a-dossier'))
    check('la nouvelle tâche est en cours', seg(pg, 'act:a-code')[0]['end'] is None, seg(pg, 'act:a-code'))
    pg.close()


def test_sous_activites(browser):
    print('Sous-activités')
    pg = page(browser, 9, 0, base({'segs': {'act:a-dossier': [{'cid': '', 'start': 500, 'end': None}]}}))
    open_taches(pg)
    pg.click('[data-action=child-go][data-key="act:a-kids"][data-cid=k1]')
    check('une sous-activité démarre sans couper la tâche en cours', seg(pg, 'act:a-dossier')[0]['end'] is None and seg(pg, 'act:a-kids')[0]['end'] is None,
          (seg(pg, 'act:a-dossier'), seg(pg, 'act:a-kids')))
    pg.clock.set_system_time(MARDI.replace(hour=9, minute=20))
    pg.click('[data-action=child-go][data-key="act:a-kids"][data-cid=k2]')
    k = seg(pg, 'act:a-kids')
    check('changer de sous-activité coupe la précédente de la même tâche (9:20 = 560)', len(k) == 2 and k[0]['end'] == 560 and k[1]['cid'] == 'k2' and k[1]['end'] is None, k)
    check('la tâche « Dossier » tourne toujours', seg(pg, 'act:a-dossier')[0]['end'] is None, seg(pg, 'act:a-dossier'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_pause(browser):
    print('Pause avec deux chronos')
    pg = page(browser, 10, 30, base({'segs': {'act:a-dossier': [{'cid': '', 'start': 540, 'end': None}], 'act:a-code': [{'cid': '', 'start': 570, 'end': None}]}}))
    open_pres(pg)
    pg.click('[data-action=pres-pause]')
    check('Pause coupe les deux chronos à 10:30 (630)', seg(pg, 'act:a-dossier')[0]['end'] == 630 and seg(pg, 'act:a-code')[0]['end'] == 630,
          (seg(pg, 'act:a-dossier'), seg(pg, 'act:a-code')))
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for t in (test_deux_taches, test_bloc_fixe, test_sous_activites, test_pause):
            t(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
