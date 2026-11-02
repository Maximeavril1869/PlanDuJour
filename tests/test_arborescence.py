"""Tests : catégories en arbre (0.23.0).

Chaque catégorie a au plus un parent ; profondeur limitée à 8 ; chemin « A › B » affiché ; réparation des données invalides.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_arborescence.py
Aucune donnée réelle : libellés inventés.
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, new_page
from test_regroupements import free_act


def cats_tree(n=3):
    return [{'id': 'c0', 'name': 'Racine A', 'work': True}] + \
           [{'id': 'c%d' % i, 'name': 'Niveau %d' % i, 'work': False, 'parent': 'c%d' % (i - 1)} for i in range(1, n)]


def page_with(browser, cats, acts=None):
    pg = new_page(browser)
    s = pg.evaluate("([c, a]) => { const s = window.PDJ.defaultSettings(); s.categories = c; s.activities = a; s.templates = []; return s; }", [cats, acts or []])
    pg.evaluate("(s) => localStorage.setItem('plandujour.reglages', JSON.stringify(s))", s)
    pg.reload()
    return pg


def open_cats(pg):
    """Déplie tous les menus de l'arbre des catégories (ils sont fermés au départ depuis la 0.23.1)."""
    pg.evaluate("() => document.querySelectorAll('#cats-list details').forEach((d) => { d.open = true; })")


def stored_cats(pg):
    return {c['id']: c for c in pg.evaluate("() => JSON.parse(localStorage.getItem('plandujour.reglages')).categories")}


def test_chemin_et_options(browser):
    print('Chemin et listes')
    pg = page_with(browser, cats_tree(3), [free_act('a1', 'Activité test', 'c2')])
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-cats] > summary')
    opts = pg.evaluate("() => [...document.querySelectorAll('#acts-list select[data-a=cat] option')].map((o) => o.textContent)")
    check('la liste des catégories d’une activité montre le chemin', any('Racine A › Niveau 1 › Niveau 2' in o for o in opts), opts)
    par = pg.evaluate("() => [...document.querySelectorAll('#cats-list .cat-row[data-id=c1] select[data-k=parent] option')].map((o) => o.textContent)")
    check('une catégorie ne peut pas être rangée sous elle-même ni sous sa descendante', not any(o.startswith('Racine A › Niveau 1') for o in par) and any(o == 'Racine A' for o in par), par)
    pg.click('#tab-day')
    pg.click('details[data-fid=card-sansheure] > summary')
    names = pg.evaluate("() => [...document.querySelectorAll('details[data-fid=card-sansheure] details.grp')].map((d) => d.dataset.gname)")
    check('« Sans heure » titre le groupe avec le chemin', names == ['Racine A › Niveau 1 › Niveau 2'], names)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_edition(browser):
    print('Édition dans Réglages')
    pg = page_with(browser, cats_tree(3))
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-cats] > summary')
    open_cats(pg)
    pg.select_option('#cats-list .cat-row[data-id=c2] select[data-k=parent]', 'c0')
    pg.click('#save-btn')
    check('changer le parent s’enregistre', stored_cats(pg)['c2'].get('parent') == 'c0', stored_cats(pg))
    open_cats(pg)
    pg.click('[data-action=add-cat]')
    new_id = pg.evaluate("() => [...document.querySelectorAll('#cats-list .cat-row')].find((r) => r.querySelector('[data-k=name]').value === '').dataset.id")
    last = pg.locator('#cats-list .cat-row[data-id="%s"]' % new_id)
    last.locator('[data-k=name]').fill('Nouvelle branche')
    last.locator('[data-k=parent]').select_option('c1')
    pg.click('#save-btn')
    new = [c for c in stored_cats(pg).values() if c['name'] == 'Nouvelle branche']
    check('une nouvelle catégorie peut être rangée sous une autre', len(new) == 1 and new[0]['parent'] == 'c1', new)
    open_cats(pg)
    pg.click('#cats-list .cat-row[data-id=c1] [data-action=del-cat]')
    pg.click('#save-btn')
    cs = stored_cats(pg)
    check('supprimer une catégorie remonte ses enfants d’un niveau', 'c1' not in cs and cs['c2']['parent'] == 'c0' and [c for c in cs.values() if c['name'] == 'Nouvelle branche'][0]['parent'] == 'c0', cs)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_profondeur_et_reparation(browser):
    print('Profondeur et données invalides')
    pg = new_page(browser)
    bad = [{'id': 'x', 'name': 'Boucle X', 'work': False, 'parent': 'y'}, {'id': 'y', 'name': 'Boucle Y', 'work': False, 'parent': 'x'},
           {'id': 'z', 'name': 'Orpheline', 'work': False, 'parent': 'absent'}, {'id': 's', 'name': 'Soi-même', 'work': False, 'parent': 's'}]
    res = pg.evaluate("(b) => window.PDJ.cleanCats(b).map((c) => [c.id, c.parent])", bad)
    d = dict((a, b) for a, b in res)
    check('parent inexistant ou soi-même : niveau supérieur', d['z'] is None and d['s'] is None, d)
    check('une boucle est cassée (au moins une des deux passe au niveau supérieur)', d['x'] is None or d['y'] is None, d)
    deep = pg.evaluate("(n) => { const l = []; for (let i = 0; i < n; i++) l.push({ id: 'd' + i, name: 'N' + i, parent: i ? 'd' + (i - 1) : null }); const out = window.PDJ.cleanCats(l); const depth = (id) => { let k = 1, c = out.find((x) => x.id === id); while (c && c.parent) { k++; c = out.find((x) => x.id === c.parent); } return k; }; return Math.max.apply(null, out.map((c) => depth(c.id))); }", 12)
    check('la profondeur ne dépasse jamais 8', deep <= 8, deep)
    check('d’anciennes catégories sans champ parent restent au niveau supérieur', pg.evaluate("() => window.PDJ.cleanCats([{ id: 'o', name: 'Ancienne', work: true }])[0].parent === null"))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_chemin_et_options(browser)
        test_edition(browser)
        test_profondeur_et_reparation(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
