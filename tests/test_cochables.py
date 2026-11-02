"""Tests : sous-activités cochables (0.22.0).

Une case « fait » par sous-activité et par jour : cochée d'office quand le chrono s'arrête ou qu'un temps est saisi,
cochable et décochable à la main (le temps reste), affichée en progression « n/4 ».
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_cochables.py
Aucune donnée réelle : libellés inventés.
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, new_page, stored_days
from test_regroupements import free_act

KEY = 'act:a-matin'
KIDS = [{'id': 'k-rep', 'name': 'Mission A'}, {'id': 'k-enc', 'name': 'Mission B'}, {'id': 'k-trait', 'name': 'Mission C'}, {'id': 'k-exp', 'name': 'Mission D'}]


def seeded_page(browser, days=None):
    """Une activité sans heure « Routine test » à quatre sous-activités, tous les jours."""
    pg = new_page(browser)
    act = free_act('a-matin', 'Routine test', None)
    act['children'] = KIDS
    settings = pg.evaluate("(a) => { const s = window.PDJ.defaultSettings(); s.categories = []; s.activities = [a]; s.templates = []; return s; }", act)
    pg.evaluate("([s, d]) => { localStorage.setItem('plandujour.reglages', JSON.stringify(s)); if (d) localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", [settings, days])
    pg.reload()
    return pg


def open_sans(pg):
    """Ouvre la carte « Sans heure » puis son menu « Sans catégorie » (tout est fermé au départ)."""
    if not pg.evaluate("() => document.querySelector('details[data-fid=card-sansheure]').open"):
        pg.click('details[data-fid=card-sansheure] > summary')
    if not pg.evaluate("() => document.querySelector('details[data-fid=sans-none]').open"):
        pg.click('details[data-fid=sans-none] > summary')


def done_ids(pg, date):
    d = stored_days(pg).get(date, {})
    return sorted((d.get('kidsDone') or {}).get(KEY, {}).keys())


def checked(pg):
    return pg.evaluate("() => [...document.querySelectorAll('details[data-fid=sans-none] input[data-kid-done]')].filter((i) => i.checked).map((i) => i.dataset.kidDone)")


def progress(pg):
    return pg.inner_text('details[data-fid=sans-none] li').split('\n')[0]


def test_cases_a_la_main(browser):
    print('Cases cochées à la main')
    pg = seeded_page(browser)
    today = day_offset(pg, 0)
    open_sans(pg)
    check('quatre cases, aucune cochée au départ', pg.locator('details[data-fid=sans-none] input[data-kid-done]').count() == 4 and checked(pg) == [])
    check('la progression affiche 0/4', '0/4' in progress(pg), progress(pg))
    pg.check('details[data-fid=sans-none] input[data-kid-done=k-rep]')
    check('cocher une case l’enregistre', done_ids(pg, today) == ['k-rep'], done_ids(pg, today))
    check('la progression passe à 1/4 et le menu reste ouvert', '1/4' in progress(pg) and pg.evaluate("() => document.querySelector('details[data-fid=sans-none]').open"), progress(pg))
    pg.reload()
    open_sans(pg)
    check('la case reste cochée après fermeture et réouverture', checked(pg) == ['k-rep'], checked(pg))
    pg.uncheck('details[data-fid=sans-none] input[data-kid-done=k-rep]')
    check('décocher retire la marque', done_ids(pg, today) == [] and checked(pg) == [], done_ids(pg, today))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_chrono_coche(browser):
    print('Le chrono coche d’office')
    pg = seeded_page(browser)
    today = day_offset(pg, 0)
    open_sans(pg)
    pg.click('details[data-fid=sans-none] button[data-action=child-go][data-cid=k-enc]')
    check('démarrer un chrono ne coche rien encore', done_ids(pg, today) == [], done_ids(pg, today))
    pg.click('.childbtns button[data-cid=k-exp]')
    check('passer à une autre sous-activité coche la précédente', done_ids(pg, today) == ['k-enc'], done_ids(pg, today))
    pg.click('.runbar button[data-action=stop]')
    check('arrêter le chrono coche la sous-activité en cours', done_ids(pg, today) == ['k-enc', 'k-exp'], done_ids(pg, today))
    open_sans(pg)
    check('les deux cases sont cochées dans « Sans heure » et la progression est 2/4', checked(pg) == ['k-enc', 'k-exp'] and '2/4' in progress(pg), (checked(pg), progress(pg)))
    pg.uncheck('details[data-fid=sans-none] input[data-kid-done=k-enc]')
    segs = stored_days(pg)[today]['segs'].get(KEY, [])
    check('décocher une case laisse son temps enregistré', len(segs) == 2 and done_ids(pg, today) == ['k-exp'], (len(segs), done_ids(pg, today)))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_panneau(browser):
    print('Panneau du bloc')
    pg = seeded_page(browser)
    today = day_offset(pg, 0)
    open_sans(pg)
    pg.click('details[data-fid=sans-none] button[data-action=open-block]')
    check('le panneau montre une case par sous-activité', pg.locator('#bp-child-btns input[data-kid-done]').count() == 4)
    pg.check('#bp-child-btns input[data-kid-done=k-trait]')
    check('cocher dans le panneau l’enregistre', done_ids(pg, today) == ['k-trait'], done_ids(pg, today))
    pg.select_option('#seg-child', 'k-rep')
    pg.fill('#seg-start', '0800')
    pg.fill('#seg-end', '0830')
    pg.click('[data-bp=add-seg]')
    check('saisir un temps à la main coche la sous-activité', done_ids(pg, today) == ['k-rep', 'k-trait'], done_ids(pg, today))
    check('la case cochée apparaît dans le panneau', pg.evaluate("() => document.querySelector('#bp-child-btns input[data-kid-done=k-rep]').checked"))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_jour_passe(browser):
    print('Jour passé')
    pg = seeded_page(browser)
    past = day_offset(pg, -1)
    pg.click('[data-day-nav="-1"]')
    pg.wait_for_timeout(200)
    open_sans(pg)
    check('un jour passé affiche aussi les cases, sans chrono', pg.locator('details[data-fid=sans-none] label.kidlbl input[data-kid-done]').count() == 4 and pg.locator('details[data-fid=sans-none] button[data-action=child-go]').count() == 0)
    pg.check('details[data-fid=sans-none] input[data-kid-done=k-exp]')
    check('la case est enregistrée sur ce jour-là', done_ids(pg, past) == ['k-exp'], done_ids(pg, past))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_donnees_propres(browser):
    print('Lecture des données')
    pg = new_page(browser)
    today = day_offset(pg, 0)
    pg.close()
    day = {'real': {}, 'ponctuels': [], 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None,
           'kidsDone': {KEY: {'k-rep': True, 'k-enc': False, 'k-trait': 'oui'}, 'act:autre': 'x'}}
    pg = seeded_page(browser, {'version': 2, 'days': {today: day}})
    open_sans(pg)
    check('seules les marques valides sont lues (true uniquement)', checked(pg) == ['k-rep'], checked(pg))
    check('un ancien jour sans le champ se lit sans erreur', pg.errors == [], pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_cases_a_la_main(browser)
        test_chrono_coche(browser)
        test_panneau(browser)
        test_jour_passe(browser)
        test_donnees_propres(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
