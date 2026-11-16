"""Tests : départ en pause et départ du travail coupent les actions « sans heure » en cours (0.37.0).

Boutons Pause et « Je pars » (heure du moment) : un passage ou une sous-activité chronométré(e) d'un bloc sans heure est arrêté(e) à cette heure ;
un bloc à heure fixe dont le chrono tourne n'est pas touché. La reprise ne relance rien.
Saisie à la main (champs de la carte Présence) : coupe à l'heure saisie une action démarrée avant ; une action démarrée après est laissée telle quelle.
L'heure est simulée (horloge du navigateur). Aucune donnée réelle : libellés inventés.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_coupure_presence.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, stored_days
from test_regroupements import free_act

MARDI = datetime(2026, 11, 3)
DATE = '2026-11-03'


def fixed_act(id_, name):
    a = free_act(id_, name, None)
    a.update({'mode': 'fixed', 'entry': 'duration', 'start': 600, 'duration': 120})
    return a


def page(browser, h, m, days):
    """Page à l'heure h:m, avec une activité sans heure, une à sous-activités (sans heure) et une à heure fixe ; jours préremplis."""
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.clock.install(time=MARDI.replace(hour=h, minute=m))
    pg.goto(URL)
    kids = free_act('a-kids', 'Courrier test', None)
    kids['children'] = [{'id': 'k1', 'name': 'Canal A'}, {'id': 'k2', 'name': 'Canal B'}]
    acts = [free_act('a-plain', 'Dossier test', None), kids, fixed_act('a-fixe', 'Réunion test')]
    settings = pg.evaluate("(a) => { const s = window.PDJ.defaultSettings(); s.categories = []; s.activities = a; s.templates = []; return s; }", acts)
    pg.evaluate("([s, d]) => { localStorage.setItem('plandujour.reglages', JSON.stringify(s)); localStorage.setItem('plandujour.jours', JSON.stringify(d)); }",
                [settings, {'version': 2, 'days': {DATE: days}}])
    pg.reload()
    return pg


def day(pg):
    return stored_days(pg).get(DATE, {})


def open_pres(pg):
    if pg.locator('details[data-fid=card-pres]').get_attribute('open') is None:
        pg.click('details[data-fid=card-pres] > summary')


def seg(pg, key):
    return day(pg).get('segs', {}).get(key, [])


def base(extra=None):
    d = {'real': {}, 'ponctuels': [], 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': {'start': 480, 'end': None, 'pauses': []},
         'kidsDone': {}, 'trip': None, 'removed': []}
    d.update(extra or {})
    return d


def test_pause_bouton(browser):
    print('Bouton Pause')
    pg = page(browser, 10, 30, base({'segs': {'act:a-plain': [{'cid': '', 'start': 540, 'end': None}],
                                              'act:a-kids': [{'cid': 'k1', 'start': 500, 'end': None}]},
                                      'real': {'act:a-fixe': {'start': 600, 'end': None}}}))
    open_pres(pg)
    pg.click('[data-action=pres-pause]')
    check('le passage « sans heure » est coupé à 10:30 (630)', seg(pg, 'act:a-plain')[0]['end'] == 630, seg(pg, 'act:a-plain'))
    check('la sous-activité en cours est coupée à 10:30 et cochée faite', seg(pg, 'act:a-kids')[0]['end'] == 630 and day(pg)['kidsDone'].get('act:a-kids', {}).get('k1') is True,
          (seg(pg, 'act:a-kids'), day(pg).get('kidsDone')))
    check('le bloc à heure fixe garde son chrono ouvert', day(pg)['real']['act:a-fixe']['end'] is None, day(pg)['real'])
    check('la pause est bien ouverte à 10:30', day(pg)['presence']['pauses'] == [{'start': 630, 'end': None}], day(pg)['presence'])
    pg.clock.set_system_time(MARDI.replace(hour=10, minute=50))
    open_pres(pg)
    pg.click('[data-action=pres-resume]')
    check('la reprise ne relance rien', all(g['end'] is not None for k in ('act:a-plain', 'act:a-kids') for g in seg(pg, k)) and len(seg(pg, 'act:a-plain')) == 1,
          day(pg)['segs'])
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_depart_bouton(browser):
    print('Bouton « Je pars »')
    pg = page(browser, 17, 0, base({'segs': {'act:a-plain': [{'cid': '', 'start': 960, 'end': None}]}}))
    open_pres(pg)
    pg.click('[data-action=pres-out]')
    check('le départ du travail coupe le passage à 17:00 (1020)', seg(pg, 'act:a-plain')[0]['end'] == 1020, seg(pg, 'act:a-plain'))
    check('le départ est enregistré à 17:00', day(pg)['presence']['end'] == 1020, day(pg)['presence'])
    pg.close()


def test_meme_minute(browser):
    print('Action démarrée à la minute même')
    pg = page(browser, 11, 0, base({'segs': {'act:a-plain': [{'cid': '', 'start': 660, 'end': None}]}}))
    open_pres(pg)
    pg.click('[data-action=pres-pause]')
    g = seg(pg, 'act:a-plain')[0]
    check('coupée quand même (durée minimale d’une minute)', g['end'] == 661, g)
    pg.close()


def test_saisie_main(browser):
    print('Saisie à la main')
    pg = page(browser, 16, 0, base({'segs': {'act:a-plain': [{'cid': '', 'start': 780, 'end': None}],
                                              'act:a-kids': [{'cid': 'k1', 'start': 900, 'end': None}]}}))
    open_pres(pg)
    pg.fill('[data-pres=pstart]', '14:00')
    pg.fill('[data-pres=pend]', '14:30')
    pg.click('[data-action=pres-addpause]')
    check('pause saisie 14:00 : le passage commencé à 13:00 est coupé à 14:00 (840)', seg(pg, 'act:a-plain')[0]['end'] == 840, seg(pg, 'act:a-plain'))
    check('la sous-activité commencée à 15:00 (après la pause) est laissée ouverte', seg(pg, 'act:a-kids')[0]['end'] is None, seg(pg, 'act:a-kids'))
    check('la pause est enregistrée', {'start': 840, 'end': 870} in day(pg)['presence']['pauses'], day(pg)['presence'])
    open_pres(pg)
    pg.fill('[data-pres=end]', '15:30')
    pg.press('[data-pres=end]', 'Tab')
    check('départ saisi 15:30 : la sous-activité commencée à 15:00 est coupée à 15:30 (930)', seg(pg, 'act:a-kids')[0]['end'] == 930, seg(pg, 'act:a-kids'))
    check('le départ est enregistré', day(pg)['presence']['end'] == 930, day(pg)['presence'])
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_rien_en_cours(browser):
    print('Rien en cours')
    pg = page(browser, 12, 0, base({'segs': {'act:a-plain': [{'cid': '', 'start': 540, 'end': 600}]}}))
    open_pres(pg)
    pg.click('[data-action=pres-pause]')
    check('un temps déjà terminé n’est pas modifié', seg(pg, 'act:a-plain') == [{'cid': '', 'start': 540, 'end': 600}], seg(pg, 'act:a-plain'))
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for t in (test_pause_bouton, test_depart_bouton, test_meme_minute, test_saisie_main, test_rien_en_cours):
            t(browser)
        browser.close()
    echecs = [r for r in RESULTS if not r[0]]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(echecs)))
    sys.exit(1 if echecs else 0)


if __name__ == '__main__':
    main()
