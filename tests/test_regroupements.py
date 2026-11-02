"""Tests : regroupements par catégorie en menus repliables (0.21.0).

Page du jour, carte « Sans heure » ; Réglages, cartes « Activités » et « Tâches habituelles ».
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_regroupements.py
Aucune donnée réelle : libellés inventés.
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, new_page, ponctuel

CATS = [{'id': 'cat-admin', 'name': 'Admin', 'work': False}, {'id': 'cat-bureau', 'name': 'Bureau', 'work': True}]


def free_act(id_, name, cat):
    return {'id': id_, 'name': name, 'days': [1, 2, 3, 4, 5, 6, 7], 'mode': 'free', 'entry': 'duration', 'start': None, 'duration': 1,
            'confirm': False, 'carry': False, 'children': [], 'cat': cat, 'parallel': False, 'toCal': False, 'alarm': None}


def tpl(id_, name, cat):
    return {'id': id_, 'name': name, 'cat': cat, 'mode': 'free', 'duration': 30, 'confirm': False, 'carry': False, 'parallel': False, 'toCal': False, 'alarm': None}


def seeded_page(browser):
    """Réglages : deux catégories, quatre activités sans heure, trois tâches habituelles. Jour : un bloc ponctuel sans heure en catégorie Bureau."""
    pg = new_page(browser)
    today = day_offset(pg, 0)
    settings = pg.evaluate("""([cats, acts, tpls]) => { const s = window.PDJ.defaultSettings(); s.categories = cats; s.activities = acts; s.templates = tpls; return s; }""",
                           [CATS,
                            [free_act('a-zebre', 'Zèbre dossier', 'cat-bureau'), free_act('a-archives', 'Archives', 'cat-admin'),
                             free_act('a-agenda', 'Agenda', 'cat-admin'), free_act('a-divers', 'Divers libre', None)],
                            [tpl('t-mail', 'Mail', 'cat-bureau'), tpl('t-impots', 'Impôts', 'cat-admin'), tpl('t-courses', 'Courses', None)]])
    days = {'version': 2, 'days': {today: {'real': {}, 'ponctuels': [ponctuel('idP', 'Appel client', None, 1, mode='free', cat='cat-bureau')],
                                           'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None}}}
    pg.evaluate("([s, d]) => { localStorage.setItem('plandujour.reglages', JSON.stringify(s)); localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", [settings, days])
    pg.reload()
    return pg


def opened(pg, sel):
    return pg.evaluate("(s) => [...document.querySelectorAll(s)].map((d) => d.open)", sel)


def test_sans_heure(browser):
    print('Page du jour : « Sans heure » par catégorie')
    pg = seeded_page(browser)
    fids = pg.evaluate("() => [...document.querySelectorAll('details[data-fid=card-sansheure] details.grp')].map((d) => d.dataset.fid)")
    check('un menu par catégorie, dans l’ordre des catégories, « Sans catégorie » en dernier', fids == ['sans-cat-admin', 'sans-cat-bureau', 'sans-none'], fids)
    check('la carte « Sans heure » est fermée au départ', pg.evaluate("() => document.querySelector('details[data-fid=card-sansheure]').open") is False)
    pg.click('details[data-fid=card-sansheure] > summary')
    check('toutes les catégories sont fermées au départ', opened(pg, 'details[data-fid=card-sansheure] details.grp') == [False, False, False])
    titres = pg.evaluate("() => [...document.querySelectorAll('details[data-fid=card-sansheure] details.grp > summary')].map((s) => s.textContent.trim())")
    check('chaque titre indique le nombre de tâches', titres == ['Admin · 2', 'Bureau · 2', 'Sans catégorie · 1'], titres)
    noms = pg.evaluate("() => [...document.querySelectorAll('details[data-fid=sans-cat-admin] li > span:first-child')].map((s) => s.textContent)")
    check('dans un menu, les tâches sont triées par nom', len(noms) == 2 and noms[0].startswith('Agenda') and noms[1].startswith('Archives'), noms)
    check('le bloc ponctuel apparaît dans sa catégorie', pg.locator('details[data-fid=sans-cat-bureau] li', has_text='Appel client').count() == 1)
    pg.click('details[data-fid=sans-cat-admin] > summary')
    check('un tap sur une catégorie la déplie', opened(pg, 'details[data-fid=card-sansheure] details.grp') == [True, False, False])
    pg.click('[data-day-nav=today]')
    check('l’état déplié est conservé quand la page se réaffiche', opened(pg, 'details[data-fid=card-sansheure] details.grp') == [True, False, False])
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_reglages_activites(browser):
    print('Réglages : Activités par catégorie')
    pg = seeded_page(browser)
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-acts] > summary')
    fids = pg.evaluate("() => [...document.querySelectorAll('#acts-list details.grp')].map((d) => d.dataset.fid)")
    check('un menu par catégorie, « Sans catégorie » en dernier', fids == ['grp-acts-cat-admin', 'grp-acts-cat-bureau', 'grp-acts-none'], fids)
    check('tous les menus sont fermés au départ', opened(pg, '#acts-list details.grp') == [False, False, False])
    titres = pg.evaluate("() => [...document.querySelectorAll('#acts-list details.grp > summary')].map((s) => s.textContent.trim())")
    check('chaque titre indique le nombre d’activités', titres == ['Admin · 2', 'Bureau · 1', 'Sans catégorie · 1'], titres)
    pg.click('details[data-fid=grp-acts-cat-admin] > summary')
    check('un tap déplie le menu et montre ses lignes', pg.locator('details[data-fid=grp-acts-cat-admin] .rowfold > summary').first.is_visible())
    pg.click('[data-action=add-act]')
    check('« + Ajouter une activité » ouvre le menu « Sans catégorie » et montre la nouvelle ligne',
          opened(pg, '#acts-list details.grp') == [True, False, True] and pg.locator('#acts-list [data-a=name]').last.is_visible(), opened(pg, '#acts-list details.grp'))
    check('le menu « Admin » reste ouvert après l’ajout', opened(pg, '#acts-list details.grp')[0] is True)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_reglages_taches(browser):
    print('Réglages : Tâches habituelles par catégorie')
    pg = seeded_page(browser)
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-tpl] > summary')
    fids = pg.evaluate("() => [...document.querySelectorAll('#tpls-list details.grp')].map((d) => d.dataset.fid)")
    check('un menu par catégorie, « Sans catégorie » en dernier', fids == ['grp-tpl-cat-admin', 'grp-tpl-cat-bureau', 'grp-tpl-none'], fids)
    check('tous les menus sont fermés au départ', opened(pg, '#tpls-list details.grp') == [False, False, False])
    pg.click('[data-action=add-tpl]')
    titres = pg.evaluate("() => [...document.querySelectorAll('#tpls-list details.grp > summary')].map((s) => s.textContent.trim())")
    check('« + Ajouter » range la nouvelle tâche dans « Sans catégorie », ouvert, compteur à jour',
          opened(pg, '#tpls-list details.grp') == [False, False, True] and titres[2] == 'Sans catégorie · 2' and pg.locator('#tpls-list [data-t=name]').last.is_visible(), (titres, opened(pg, '#tpls-list details.grp')))
    pg.evaluate("() => document.querySelector('details[data-fid=grp-tpl-none] [data-action=del-tpl]').click()")
    titres = pg.evaluate("() => [...document.querySelectorAll('#tpls-list details.grp > summary')].map((s) => s.textContent.trim())")
    check('supprimer une tâche met le compteur à jour', titres[2] == 'Sans catégorie · 1', titres)
    pg.evaluate("() => document.querySelector('details[data-fid=grp-tpl-none] [data-action=del-tpl]').click()")
    check('supprimer la dernière tâche d’un menu supprime le menu', pg.locator('#tpls-list details.grp').count() == 2)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_erreur_ouvre_le_menu(browser):
    print('Réglages : une erreur de saisie ouvre le menu concerné')
    pg = seeded_page(browser)
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-tpl] > summary')
    check('le menu « Bureau » est fermé avant l’erreur', opened(pg, 'details[data-fid=grp-tpl-cat-bureau]') == [False])
    pg.evaluate("""() => { const i = document.querySelector('details[data-fid=grp-tpl-cat-bureau] [data-t=name]'); i.value = ''; i.dispatchEvent(new Event('input', { bubbles: true })); }""")
    pg.click('#save-btn')
    check('le menu et la ligne en erreur s’ouvrent', opened(pg, 'details[data-fid=grp-tpl-cat-bureau]') == [True] and pg.locator('details[data-fid=grp-tpl-cat-bureau] [data-t=name]').is_visible())
    pg.fill('details[data-fid=grp-tpl-cat-bureau] [data-t=name]', 'Mail test')
    pg.click('#save-btn')
    check('après correction, l’enregistrement passe et les menus gardent leur état', pg.locator('details[data-fid=grp-tpl-cat-bureau]').count() == 1 and opened(pg, 'details[data-fid=grp-tpl-cat-bureau]') == [True])
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_sans_heure(browser)
        test_reglages_activites(browser)
        test_reglages_taches(browser)
        test_erreur_ouvre_le_menu(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
