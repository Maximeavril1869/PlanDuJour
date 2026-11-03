"""Tests : statuts des catégories (0.23.1) et arbre en menus imbriqués dans Réglages.

Statut = Travail / Perso / Hors, choisi sur la catégorie de niveau supérieur et hérité par ses sous-catégories (aucun mélange possible).
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_statuts.py
Aucune donnée réelle : libellés inventés.
"""
import sys

from playwright.sync_api import sync_playwright

from test_arborescence import open_cats, page_with, stored_cats
from test_calendrier import RESULTS, check, new_page

# Pro (travail) > RH ; Maison (perso) > Bricolage ; Trajets (hors). La sous-catégorie « RH » porte un statut contradictoire exprès : il doit être ignoré.
CATS = [
    {'id': 'w', 'name': 'Pro', 'kind': 'work', 'parent': None},
    {'id': 'w1', 'name': 'RH', 'kind': 'perso', 'parent': 'w'},
    {'id': 'p', 'name': 'Maison', 'kind': 'perso', 'parent': None},
    {'id': 'p1', 'name': 'Bricolage', 'kind': 'perso', 'parent': 'p'},
    {'id': 'h', 'name': 'Trajets', 'kind': 'hors', 'parent': None},
]
GROUP = '#cats-list details.grp[data-fid=grp-kind-%s]'


def open_cats_card(pg):
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-cats] > summary')


def titles(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#cats-list > details.grp')].map((g) => g.querySelector(':scope > summary').textContent)")


def kind_select(pg, cid):
    return pg.evaluate("(id) => { const s = document.querySelector('#cats-list .cat-row[data-id=\"' + id + '\"] select[data-k=kind]'); return [s.value, s.disabled]; }", cid)


def test_donnees(browser):
    print('Statut : lecture et héritage')
    pg = new_page(browser)
    res = pg.evaluate("""() => { const l = window.PDJ.cleanCats([
        { id: 'a', name: 'A', work: true }, { id: 'b', name: 'B', work: false }, { id: 'cat-trajets', name: 'Trajets', work: false },
        { id: 'c', name: 'C', kind: 'hors' }, { id: 'd', name: 'D', kind: 'work', parent: 'b' }, { id: 'e', name: 'E', kind: 'zzz', work: true }]);
      const o = {}; l.forEach((c) => { o[c.id] = [c.kind, c.work]; }); return o; }""")
    check('ancien réglage : case Travail cochée = travail, sinon perso', res['a'] == ['work', True] and res['b'] == ['perso', False], res)
    check('la catégorie de départ « Trajets » devient hors', res['cat-trajets'] == ['hors', False], res)
    check('un statut explicite est gardé, un statut invalide est repris de l’ancienne case', res['c'][0] == 'hors' and res['e'][0] == 'work', res)
    check('une sous-catégorie prend le statut de sa racine, pas le sien', res['d'] == ['perso', False], res)
    check('une catégorie absente (activité sans catégorie) est hors', pg.evaluate("() => window.PDJ.catKind(window.PDJ.cleanCats([{ id: 'a', name: 'A' }]), 'inconnue')") == 'hors')
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_structure(browser):
    print('Réglages : trois menus de statut, un menu par catégorie')
    pg = page_with(browser, CATS)
    open_cats_card(pg)
    check('trois menus Travail, Perso, Hors avec leur nombre de catégories', titles(pg) == ['Travail · 2', 'Perso · 2', 'Hors · 1'], titles(pg))
    check('tout est fermé au départ', pg.evaluate("() => [...document.querySelectorAll('#cats-list details')].every((d) => !d.open)"))
    check('les menus portent leur statut (couleur)', pg.evaluate("() => [...document.querySelectorAll('#cats-list > details.grp')].map((g) => g.dataset.status).join()") == 'work,perso,hors')
    check('une sous-catégorie est imbriquée dans le menu de sa catégorie', pg.locator(GROUP % 'work' + ' details[data-fid=catnode-w] details[data-fid=catnode-w1]').count() == 1)
    check('le titre d’une catégorie donne son nombre de sous-catégories', pg.evaluate("() => document.querySelector('details[data-fid=catnode-w] > summary').textContent") == 'Pro · 1')
    pg.evaluate("() => document.querySelectorAll('#cats-list details').forEach((d) => { d.open = true; })")
    check('la racine choisit son statut, la sous-catégorie l’hérite', kind_select(pg, 'w') == ['work', False] and kind_select(pg, 'w1') == ['work', True], (kind_select(pg, 'w'), kind_select(pg, 'w1')))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_changer_statut(browser):
    print('Changer le statut d’une racine')
    pg = page_with(browser, CATS)
    open_cats_card(pg)
    open_cats(pg)
    pg.select_option('#cats-list .cat-row[data-id=p] select[data-k=kind]', 'hors')
    check('la sous-catégorie suit tout de suite', kind_select(pg, 'p1') == ['hors', True], kind_select(pg, 'p1'))
    check('la ligne reste en place jusqu’à l’enregistrement', pg.locator(GROUP % 'perso' + ' .cat-row[data-id=p]').count() == 1)
    pg.click('#save-btn')
    cs = stored_cats(pg)
    check('enregistré : racine et sous-catégorie sont hors', cs['p']['kind'] == 'hors' and cs['p1']['kind'] == 'hors' and cs['p1']['work'] is False, cs)
    check('après l’enregistrement, les lignes se rangent dans le bon menu', titles(pg) == ['Travail · 2', 'Perso · 0', 'Hors · 3'], titles(pg))
    check('la sous-catégorie reste sous sa catégorie dans le nouveau menu', pg.locator(GROUP % 'hors' + ' details[data-fid=catnode-p] details[data-fid=catnode-p1]').count() == 1)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_ranger_sous(browser):
    print('Ranger une catégorie sous une autre')
    pg = page_with(browser, CATS)
    open_cats_card(pg)
    open_cats(pg)
    pg.select_option('#cats-list .cat-row[data-id=h] select[data-k=parent]', 'w')
    check('elle prend le statut du nouveau parent et ne peut plus le changer', kind_select(pg, 'h') == ['work', True], kind_select(pg, 'h'))
    pg.click('#save-btn')
    cs = stored_cats(pg)
    check('enregistré : parent et statut', cs['h']['parent'] == 'w' and cs['h']['kind'] == 'work' and cs['h']['work'] is True, cs['h'])
    check('elle apparaît sous Pro dans le menu Travail', pg.locator(GROUP % 'work' + ' details[data-fid=catnode-w] details[data-fid=catnode-h]').count() == 1)
    open_cats(pg)
    pg.select_option('#cats-list .cat-row[data-id=h] select[data-k=parent]', '')
    check('remise au niveau supérieur : le statut redevient modifiable, sans changer', kind_select(pg, 'h') == ['work', False], kind_select(pg, 'h'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_ajout_suppression(browser):
    print('Ajouter et supprimer')
    pg = page_with(browser, CATS)
    open_cats_card(pg)
    pg.click('[data-action=add-cat]')
    info = pg.evaluate("() => { const a = document.activeElement; return [!!a.closest('details.grp[data-fid=grp-kind-perso]'), a.dataset.k, document.querySelector('details.grp[data-fid=grp-kind-perso]').open]; }")
    check('« + Catégorie » ouvre le menu Perso et place le curseur sur le nom', info == [True, 'name', True], info)
    pg.keyboard.type('Nouvelle racine')
    check('le titre et le compteur suivent la saisie', titles(pg) == ['Travail · 2', 'Perso · 3', 'Hors · 1'], titles(pg))
    nid = pg.evaluate("() => [...document.querySelectorAll('#cats-list .cat-row')].find((r) => r.querySelector('[data-k=name]').value === 'Nouvelle racine').dataset.id")
    pg.select_option('#cats-list .cat-row[data-id="%s"] select[data-k=kind]' % nid, 'work')
    pg.click('#save-btn')
    check('enregistrée au niveau supérieur avec le statut choisi', stored_cats(pg)[nid]['kind'] == 'work' and stored_cats(pg)[nid]['parent'] is None, stored_cats(pg).get(nid))
    check('elle se range dans le menu Travail', pg.locator(GROUP % 'work' + ' > .grpbody > details[data-fid="catnode-%s"]' % nid).count() == 1)
    open_cats(pg)
    pg.click('#cats-list .cat-row[data-id=w] [data-action=del-cat]')
    state = pg.evaluate("""() => [!document.querySelector('#cats-list .cat-row[data-id=w]'),
        !!document.querySelector('#cats-list details.grp[data-fid=grp-kind-work] > .grpbody > details[data-fid=catnode-w1]'),
        document.querySelector('#cats-list .cat-row[data-id=w1] select[data-k=parent]').value,
        document.querySelector('#cats-list .cat-row[data-id=w1] select[data-k=kind]').disabled]""")
    check('supprimer une catégorie : ses sous-catégories restent là, un niveau plus haut, statut modifiable', state == [True, True, '', False], state)
    pg.click('#save-btn')
    cs = stored_cats(pg)
    check('enregistré : la sous-catégorie remonte et garde son statut', 'w' not in cs and cs['w1']['parent'] is None and cs['w1']['kind'] == 'work', cs.get('w1'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_anciens_reglages(browser):
    print('Anciens réglages sans statut')
    pg = page_with(browser, [{'id': 'cat-trajets', 'name': 'Trajets', 'work': False}, {'id': 'x', 'name': 'Ancienne', 'work': True}, {'id': 'y', 'name': 'Autre', 'work': False}])
    open_cats_card(pg)
    check('rangées par statut déduit de l’ancienne case', titles(pg) == ['Travail · 1', 'Perso · 1', 'Hors · 1'], titles(pg))
    check('« Trajets » est dans Hors', pg.locator(GROUP % 'hors' + ' .cat-row[data-id=cat-trajets]').count() == 1)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_donnees(browser)
        test_structure(browser)
        test_changer_statut(browser)
        test_ranger_sous(browser)
        test_ajout_suppression(browser)
        test_anciens_reglages(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
