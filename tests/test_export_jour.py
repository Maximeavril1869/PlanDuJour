"""Tests : export vers Calendrier du jour même (0.27.0).

« Aujourd'hui » et « 7 jours à partir d'aujourd'hui » s'ajoutent à « Demain » et « 7 jours à partir de demain » ; le plan exporté est celui de l'app
à l'instant (heures réelles, bloc en cours jusqu'à maintenant, blocs recalés) ; une tâche sans heure à passages donne un événement par passage.
L'heure est simulée (11:30, le 3 novembre 2026). Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_export_jour.py
Aucune donnée réelle : libellés inventés.
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, ponctuel
from test_regroupements import free_act

TODAY = '2026-11-03'


def page(browser, ponctuels, real=None, segs=None, tomorrow=None, acts=None):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.add_init_script("Object.defineProperty(navigator, 'canShare', { configurable: true, value: undefined });")   # force le téléchargement
    pg.clock.install(time=datetime(2026, 11, 3, 11, 30))
    pg.goto(URL)
    day = {'real': real or {}, 'ponctuels': ponctuels, 'subtasks': {}, 'review': {}, 'profile': None, 'segs': segs or {}, 'presence': None}
    days = {TODAY: day}
    if tomorrow:
        days['2026-11-04'] = {'real': {}, 'ponctuels': tomorrow, 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None}
    if acts is not None:
        settings = pg.evaluate("(a) => { const s = window.PDJ.defaultSettings(); s.categories = []; s.activities = a; s.templates = []; return s; }", acts)
        pg.evaluate("(s) => localStorage.setItem('plandujour.reglages', JSON.stringify(s))", settings)
    pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify(d))", {'version': 2, 'days': days})
    pg.reload()
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-cal] > summary')
    return pg


def export(pg, period):
    pg.select_option('#cal-period', period)
    with pg.expect_download(timeout=5000) as dl:
        pg.click('[data-action=cal-export]')
    d = dl.value
    return d.suggested_filename, open(d.path(), encoding='utf-8').read()


def starts(ics):
    return [l[8:] for l in ics.splitlines() if l.startswith('DTSTART:')]


def ends(ics):
    return [l[6:] for l in ics.splitlines() if l.startswith('DTEND:')]


def titles(ics):
    return [l[8:] for l in ics.splitlines() if l.startswith('SUMMARY:')]


def test_options(browser):
    print('Choix de période')
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60, toCal=True)])
    opts = pg.evaluate("() => [...document.querySelectorAll('#cal-period option')].map((o) => [o.value, o.textContent])")
    check('quatre périodes dont « Aujourd’hui » et « 7 jours à partir d’aujourd’hui »', [o[0] for o in opts] == ['today', 'tomorrow', 'week0', 'week'] and opts[0][1] == 'Aujourd’hui', opts)
    pg.close()


def test_aujourdhui(browser):
    print('Export d’aujourd’hui')
    ps = [ponctuel('p1', 'Bloc a venir test', 840, 60, toCal=True),
          ponctuel('p2', 'Bloc termine test', 540, 60, toCal=True),
          ponctuel('p3', 'Bloc en cours test', 600, 30, toCal=True),
          ponctuel('p4', 'Bloc non coche test', 960, 60)]
    real = {'p:p2': {'start': 550, 'end': 590}, 'p:p3': {'start': 600, 'end': None}}
    pg = page(browser, ps, real=real, tomorrow=[ponctuel('p5', 'Bloc demain test', 600, 60, toCal=True)])
    name, ics = export(pg, 'today')
    check('le fichier porte la date du jour', name == 'plandujour-2026-11-03.ics', name)
    check('les trois blocs cochés sont exportés, pas le non coché ni celui de demain', sorted(titles(ics)) == ['Bloc a venir test', 'Bloc en cours test', 'Bloc termine test'], titles(ics))
    pairs = dict(zip(titles(ics), zip(starts(ics), ends(ics))))
    check('un bloc terminé garde ses heures réelles (09:10–09:50)', pairs['Bloc termine test'] == ('20261103T091000', '20261103T095000'), pairs)
    check('un bloc en cours va jusqu’à maintenant (10:00–11:30)', pairs['Bloc en cours test'] == ('20261103T100000', '20261103T113000'), pairs)
    check('un bloc à venir garde son heure prévue (14:00–15:00)', pairs['Bloc a venir test'] == ('20261103T140000', '20261103T150000'), pairs)
    uids = [l for l in ics.splitlines() if l.startswith('UID:')]
    check('les identifiants sont stables d’un export à l’autre', sorted(uids) == sorted(l for l in export(pg, 'today')[1].splitlines() if l.startswith('UID:')), uids)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_semaines(browser):
    print('Périodes de 7 jours')
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60, toCal=True)], tomorrow=[ponctuel('p5', 'Bloc demain test', 600, 60, toCal=True)])
    n0, ics0 = export(pg, 'week0')
    check('« 7 jours à partir d’aujourd’hui » : du 3 au 9 novembre, aujourd’hui compris', n0 == 'plandujour-2026-11-03_2026-11-09.ics' and 'Bloc test' in titles(ics0) and 'Bloc demain test' in titles(ics0), (n0, titles(ics0)))
    n1, ics1 = export(pg, 'week')
    check('« 7 jours à partir de demain » : du 4 au 10 novembre, sans aujourd’hui', n1 == 'plandujour-2026-11-04_2026-11-10.ics' and 'Bloc test' not in titles(ics1) and 'Bloc demain test' in titles(ics1), (n1, titles(ics1)))
    n2, ics2 = export(pg, 'tomorrow')
    check('« Demain » inchangé : seulement demain', n2 == 'plandujour-2026-11-04.ics' and titles(ics2) == ['Bloc demain test'], (n2, titles(ics2)))
    pg.close()


def test_passages(browser):
    print('Un événement par passage')
    act = free_act('a-plain', 'Dossier test', None)
    act['toCal'] = True
    segs = {'act:a-plain': [{'cid': '', 'start': 480, 'end': 510}, {'cid': '', 'start': 600, 'end': 645}, {'cid': '', 'start': 660, 'end': None}],
            'p:p9': [{'cid': '', 'start': 700, 'end': 720}]}
    p9 = ponctuel('p9', 'Tache ponctuelle test', None, mode='free', toCal=True)
    pg = page(browser, [p9], segs=segs, acts=[act])
    name, ics = export(pg, 'today')
    dossier = [(s, e) for t, s, e in zip(titles(ics), starts(ics), ends(ics)) if t == 'Dossier test']
    check('trois passages = trois événements (le dernier, en cours, jusqu’à 11:30)', dossier == [('20261103T080000', '20261103T083000'), ('20261103T100000', '20261103T104500'), ('20261103T110000', '20261103T113000')], dossier)
    check('un bloc ponctuel sans heure est exporté de la même façon', titles(ics).count('Tache ponctuelle test') == 1, titles(ics))
    uids = [l for l in ics.splitlines() if l.startswith('UID:')]
    check('chaque événement a un identifiant distinct', len(uids) == len(set(uids)) == 4, uids)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_rien_a_exporter(browser):
    print('Rien de coché')
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60)])
    pg.select_option('#cal-period', 'today')
    pg.click('[data-action=cal-export]')
    check('un message explique qu’il n’y a rien à exporter', 'Aucun bloc' in pg.inner_text('#toast'), pg.inner_text('#toast'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_options(browser)
        test_aujourdhui(browser)
        test_semaines(browser)
        test_passages(browser)
        test_rien_a_exporter(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
