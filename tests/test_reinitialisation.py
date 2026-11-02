"""Tests : réinitialisation de l'app (Réglages > Réinitialiser…).

Lancer depuis la racine du dépôt :  python3 tests/test_reinitialisation.py
"""
import json
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, new_page, ponctuel, seed


def store(pg, key, value):
    pg.evaluate("([k, v]) => localStorage.setItem(k, JSON.stringify(v))", [key, value])


def read(pg, key):
    raw = pg.evaluate("(k) => localStorage.getItem(k)", key)
    return None if raw is None else json.loads(raw)


def prepare(browser):
    """Page avec des réglages personnalisés, des jours, et d'anciennes copies de sécurité."""
    pg = new_page(browser)
    today = day_offset(pg, 0)
    custom = pg.evaluate("() => { const s = window.PDJ.defaultSettings(); s.activities[0].name = 'Activité perso test'; s.workTarget = 400; return s; }")
    store(pg, 'plandujour.reglages', custom)
    store(pg, 'plandujour.jours', seed(today, ponctuel('idR', 'Bloc test', 600)))
    store(pg, 'plandujour.avant-import.jours', {'old': 1})
    store(pg, 'plandujour.avant-import.reglages', {'old': 1})
    store(pg, 'plandujour.jours.sauvegarde', {'old': 1})
    pg.reload()
    pg.click('#tab-settings')
    return pg, today


def open_reset(pg):
    pg.evaluate("() => document.querySelector('[data-action=reset]').click()")
    pg.wait_for_selector('#reset-word')


def test_confirmation(browser):
    print('Confirmation')
    pg, today = prepare(browser)
    check('le panneau est fermé au départ', pg.locator('#reset-word').count() == 0)
    open_reset(pg)
    check('le bouton ouvre le panneau avec les deux choix', pg.locator('input[name=reset-mode]').count() == 2)
    pg.fill('#reset-word', 'oups')
    pg.evaluate("() => document.querySelector('[data-action=reset-go]').click()")
    check('un mot incorrect affiche une erreur', pg.is_visible('#reset-err'))
    check('un mot incorrect n’efface rien', read(pg, 'plandujour.jours')['days'] and read(pg, 'plandujour.reglages')['activities'][0]['name'] == 'Activité perso test')
    pg.evaluate("() => document.querySelector('[data-action=reset-cancel]').click()")
    check('« Annuler » ferme le panneau', pg.locator('#reset-word').count() == 0)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_tout_effacer(browser):
    print('Tout effacer')
    pg, today = prepare(browser)
    open_reset(pg)
    pg.fill('#reset-word', 'effacer')                      # la casse n'a pas d'importance
    pg.evaluate("() => document.querySelector('[data-action=reset-go]').click()")
    pg.wait_for_timeout(200)
    s = read(pg, 'plandujour.reglages')
    check('réglages vierges : aucune activité, catégorie, tâche', s['activities'] == [] and s['categories'] == [] and s['templates'] == [], s)
    check('un seul profil « Journée », à heures libres, tous les jours', len(s['profiles']) == 1 and s['profiles'][0]['name'] == 'Journée' and s['profiles'][0]['wake'] is None and s['profiles'][0]['bedtime'] is None and len(s['profiles'][0]['days']) == 7, s['profiles'])
    check('aucun congé', s['leave']['periods'] == [])
    check('tous les jours sont effacés', read(pg, 'plandujour.jours')['days'] == {})
    check('les anciennes copies de sécurité sont effacées', all(pg.evaluate("(k) => localStorage.getItem(k)", k) is None for k in ('plandujour.avant-import.jours', 'plandujour.avant-import.reglages', 'plandujour.jours.sauvegarde')))
    check('le panneau se referme', pg.locator('#reset-word').count() == 0)
    check('pas de bandeau « valeurs de départ » (les réglages sont enregistrés)', 'valeurs de départ' not in pg.evaluate("() => document.querySelector('#panel-day').innerText"))
    pg.reload()
    s2 = read(pg, 'plandujour.reglages')
    check('après rechargement, l’app reste vierge (les valeurs de départ ne reviennent pas)', s2['activities'] == [] and len(s2['profiles']) == 1, s2)
    for tab in ('#tab-day', '#tab-recap', '#tab-stats', '#tab-settings'):
        pg.click(tab)
    check('les quatre onglets s’affichent sans erreur', not pg.errors, pg.errors)
    pg.click('#tab-day')
    pg.click('[data-action=add-block]')
    pg.fill('#bp-edit [data-a=name]', 'Premier bloc test')
    pg.fill('#bp-edit [data-a=start]', '10:00')
    pg.fill('#bp-edit [data-a=second]', '30')
    pg.click('#bp-save')
    pg.wait_for_timeout(200)
    ps = [p for d in read(pg, 'plandujour.jours')['days'].values() for p in d['ponctuels']]
    check('on peut ajouter un bloc ponctuel dans l’app vierge', len(ps) == 1 and ps[0]['name'] == 'Premier bloc test' and ps[0]['duration'] == 30, ps)
    check('aucune erreur JavaScript après l’ajout', not pg.errors, pg.errors)
    pg.close()


def test_jours_seulement(browser):
    print('Effacer seulement les jours')
    pg, today = prepare(browser)
    before = read(pg, 'plandujour.reglages')
    open_reset(pg)
    pg.evaluate("() => document.querySelector('input[name=reset-mode][value=days]').click()")
    pg.fill('#reset-word', 'EFFACER')
    pg.evaluate("() => document.querySelector('[data-action=reset-go]').click()")
    pg.wait_for_timeout(200)
    check('les jours sont effacés', read(pg, 'plandujour.jours')['days'] == {})
    after = read(pg, 'plandujour.reglages')
    check('les réglages sont intacts', after['activities'][0]['name'] == 'Activité perso test' and len(after['activities']) == len(before['activities']), after)
    check('la copie des jours est effacée, celle des réglages conservée', pg.evaluate("() => localStorage.getItem('plandujour.avant-import.jours')") is None and pg.evaluate("() => localStorage.getItem('plandujour.avant-import.reglages')") is not None)
    check('le panneau se referme', pg.locator('#reset-word').count() == 0)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for t in (test_confirmation, test_tout_effacer, test_jours_seulement):
            t(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
