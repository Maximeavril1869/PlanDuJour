"""Tests : Stats en arbre (0.24.0).

Un menu par statut (Travail, Perso, Hors), puis un menu par catégorie, avec un total à chaque niveau ; le temps est compté au niveau le plus fin
(activité, sous-activité). Aucun temps n'est compté deux fois : la somme des trois statuts égale le total des activités.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_stats_arbre.py
Aucune donnée réelle : libellés inventés.
"""
import sys

from playwright.sync_api import sync_playwright

from test_arborescence import page_with
from test_calendrier import RESULTS, check, day_offset
from test_regroupements import free_act

# Pro (travail) > Dossiers, Réunions ; Maison (perso) > Bricolage ; Trajets (hors) ; Vide (perso, aucune activité).
CATS = [
    {'id': 'w', 'name': 'Pro', 'kind': 'work', 'parent': None}, {'id': 'w1', 'name': 'Dossiers', 'parent': 'w'}, {'id': 'w2', 'name': 'Réunions', 'parent': 'w'},
    {'id': 'p', 'name': 'Maison', 'kind': 'perso', 'parent': None}, {'id': 'p1', 'name': 'Bricolage', 'parent': 'p'},
    {'id': 'h', 'name': 'Trajets', 'kind': 'hors', 'parent': None},
    {'id': 'v', 'name': 'Vide', 'kind': 'perso', 'parent': None},
]


def act(id_, name, cat, children=None):
    a = free_act(id_, name, cat)
    a['children'] = children or []
    return a


ACTS = [act('a1', 'Dossier test', 'w1'), act('a2', 'Réunion test', 'w2'), act('a3', 'Direct test', 'w'),
        act('a4', 'Courrier test', 'w1', [{'id': 'k1', 'name': 'Canal A'}, {'id': 'k2', 'name': 'Canal B'}]),
        act('a5', 'Bricolage test', 'p1'), act('a6', 'Train test', 'h'), act('a7', 'Libre test', None)]
# minutes : Dossier 60, Réunion 30, Direct 15, Courrier 35 (20 + 15), Bricolage 60, Train 60, Libre 20 ; total 280 (Travail 140, Perso 60, Hors 80)
REAL = {'act:a1': (480, 540), 'act:a2': (600, 630), 'act:a3': (660, 675), 'act:a5': (800, 860), 'act:a6': (900, 960), 'act:a7': (1000, 1020)}
SEGS = {'act:a4': [{'cid': 'k1', 'start': 700, 'end': 720}, {'cid': 'k2', 'start': 720, 'end': 735}]}


def seeded(browser, cats=CATS, acts=ACTS, real=REAL, segs=SEGS):
    pg = page_with(browser, cats, acts)
    today = day_offset(pg, 0)
    day = {'real': {k: {'start': v[0], 'end': v[1]} for k, v in real.items()}, 'ponctuels': [], 'subtasks': {}, 'review': {}, 'profile': None, 'segs': segs, 'presence': None}
    pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify(d))", {'version': 2, 'days': {today: day}})
    pg.reload()
    pg.click('#tab-stats')
    return pg


def kinds(pg):
    return pg.evaluate("() => [...document.querySelectorAll('.stree > details.grp')].map((g) => [g.dataset.status, g.querySelector(':scope > summary strong').textContent])")


def open_all(pg):
    pg.evaluate("() => document.querySelectorAll('.stree details').forEach((d) => { d.open = true; })")


def node_totals(pg):
    return pg.evaluate("() => Object.fromEntries([...document.querySelectorAll('.stree details.catnode')].map((d) => [d.dataset.fid, d.querySelector(':scope > summary strong').textContent]))")


def test_totaux(browser):
    print('Un total à chaque niveau')
    pg = seeded(browser)
    check('trois menus de statut avec leur total', kinds(pg) == [['work', '2 h 20'], ['perso', '1 h'], ['hors', '1 h 20']], kinds(pg))
    check('tout est fermé au départ', pg.evaluate("() => [...document.querySelectorAll('.stree details')].every((d) => !d.open)"))
    open_all(pg)
    t = node_totals(pg)
    check('Pro porte le total de ses activités et de ses sous-catégories (140 min)', t.get('stn-w') == '2 h 20', t)
    check('Dossiers (60 + 35) et Réunions (30)', t.get('stn-w1') == '1 h 35' and t.get('stn-w2') == '30 min', t)
    check('Maison et Bricolage (60)', t.get('stn-p') == '1 h' and t.get('stn-p1') == '1 h', t)
    check('une catégorie sans temps sur la période n’apparaît pas', 'stn-v' not in t, t)
    check('Trajets est dans Hors, « Sans catégorie » aussi, en dernier', pg.evaluate("() => [...document.querySelectorAll('.stree details.grp[data-status=hors] > .grpbody > details.catnode > summary span')].map((e) => e.textContent)") == ['Trajets', 'Sans catégorie'])
    check('l’arbre est imbriqué : Dossiers est dans Pro', pg.locator('details[data-fid=stn-w] details[data-fid=stn-w1]').count() == 1)
    check('une activité posée directement sur Pro est listée dans Pro', pg.evaluate("() => [...document.querySelectorAll('details[data-fid=stn-w] > .catbody > ul.rows > li .stline span')].map((e) => e.textContent)") == ['Direct test'])
    sub = pg.evaluate("() => [...document.querySelectorAll('details[data-fid=stn-w1] > .catbody > ul.rows > li')].find((li) => li.textContent.includes('Courrier test')).querySelector('.stsub').textContent")
    check('les sous-activités sont détaillées sous leur activité', 'Canal A' in sub and '20 min' in sub and 'Canal B' in sub and '15 min' in sub, sub)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_pas_de_double_compte(browser):
    print('Aucun double compte')
    pg = seeded(browser)
    res = pg.evaluate("""() => { const d = JSON.parse(localStorage.getItem('plandujour.jours')).days, s = JSON.parse(localStorage.getItem('plandujour.reglages'));
        const k = Object.keys(d)[0], st = window.PDJ.statsFor(d, s, k, k), sum = ['work', 'perso', 'hors'].reduce((t, x) => t + st.kinds[x].minutes, 0);
        const check = (n) => n.minutes === n.acts.reduce((t, a) => t + a.minutes, 0) + n.kids.reduce((t, c) => t + c.minutes, 0) && n.kids.every(check);
        const ok = ['work', 'perso', 'hors'].every((x) => st.kinds[x].nodes.every(check));
        return [sum, st.total, ok]; }""")
    check('la somme Travail + Perso + Hors égale le total des activités (140 + 60 + 80 = 280 min)', res[0] == res[1] and res[0] == 280, res)
    check('chaque catégorie vaut ses activités plus ses sous-catégories', res[2] is True, res)
    check('le total affiché en bas (Par activité) est le même', '4 h 40' in pg.inner_text('#panel-stats'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_orpheline_et_vide(browser):
    print('Catégorie supprimée, période sans temps')
    pg = seeded(browser)
    res = pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('plandujour.reglages'));
        const t = window.PDJ.statsTree([{ date: 'x', key: 'k', name: 'Orpheline test', cat: 'disparue', child: null, minutes: 25 }], s);
        return [t.hors.minutes, t.hors.nodes.map((n) => n.name), t.work.minutes, t.perso.minutes]; }""")
    check('une activité dont la catégorie n’existe plus est comptée « Hors », « Sans catégorie »', res == [25, ['Sans catégorie'], 0, 0], res)
    pg.click('[data-stats-nav="1"]')
    check('une période sans temps : pas de carte « Par catégorie »', pg.locator('.stree').count() == 0)
    pg.close()
    pg = seeded(browser, real={'act:a1': (480, 540)}, segs={})
    check('seul Travail a du temps : Perso et Hors restent affichés à 0 min', kinds(pg) == [['work', '1 h'], ['perso', '0 min'], ['hors', '0 min']], kinds(pg))
    check('un statut sans temps n’a rien à déplier', pg.evaluate("() => [...document.querySelectorAll('.stree > details.grp')].map((g) => g.classList.contains('nokids')).join()") == 'false,true,true')
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_pliage(browser):
    print('Pliage conservé tant que l’app reste ouverte')
    pg = seeded(browser)
    pg.click('.stree details[data-fid=stk-work] > summary')
    pg.click('details[data-fid=stn-w] > summary')
    check('un tap déplie le statut puis la catégorie', pg.evaluate("() => document.querySelector('details[data-fid=stn-w]').open"))
    pg.click('[data-stats-mode="month"]')
    pg.click('[data-stats-mode="week"]')
    state = pg.evaluate("() => [document.querySelector('details[data-fid=stk-work]').open, document.querySelector('details[data-fid=stn-w]').open, document.querySelector('details[data-fid=stk-perso]').open]")
    check('l’état déplié survit à un changement de période', state == [True, True, False], state)
    pg.click('.stree details[data-fid=stk-work] > summary')
    check('un second tap replie', not pg.evaluate("() => document.querySelector('details[data-fid=stk-work]').open"))
    pg.reload()
    pg.click('#tab-stats')
    check('après fermeture de l’app, tout est de nouveau fermé', pg.evaluate("() => [...document.querySelectorAll('.stree details')].every((d) => !d.open)"))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_totaux(browser)
        test_pas_de_double_compte(browser)
        test_orpheline_et_vide(browser)
        test_pliage(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
