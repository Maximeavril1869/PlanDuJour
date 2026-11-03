"""Tests : envoi vers l'app Raccourcis (0.28.0).

Le bouton « Envoyer vers Raccourcis » copie un JSON {from, to, events[{title, start, end}]} dans le presse-papiers puis ouvre
shortcuts://run-shortcut?name=Plan du jour&input=clipboard (repli : input=text si la copie échoue). Même contenu que l'export .ics.
Le presse-papiers et l'ouverture du lien sont simulés ; l'heure aussi (11:30, le 3 novembre 2026).
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_raccourcis.py
Aucune donnée réelle : libellés inventés.
"""
import json
import sys
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, ponctuel
from test_regroupements import free_act

TODAY = '2026-11-03'
SPY = """
window.__opened = [];
document.addEventListener('click', (e) => { const a = e.target.closest && e.target.closest('a'); if (a && a.href.indexOf('shortcuts:') === 0) { e.preventDefault(); window.__opened.push(a.href); } }, true);
"""
CLIP_OK = "window.__clip = null; Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: (t) => { window.__clip = t; return Promise.resolve(); } } });"
CLIP_KO = "Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: () => Promise.reject(new Error('refus')) } }); document.execCommand = () => false;"


def page(browser, ponctuels, clip=CLIP_OK, segs=None, acts=None, tomorrow=None, real=None):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.add_init_script(clip)
    pg.add_init_script("window.addEventListener('DOMContentLoaded', () => {" + SPY + "});")
    pg.clock.install(time=datetime(2026, 11, 3, 11, 30))
    pg.goto(URL)
    days = {TODAY: {'real': real or {}, 'ponctuels': ponctuels, 'subtasks': {}, 'review': {}, 'profile': None, 'segs': segs or {}, 'presence': None}}
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


def send(pg, period):
    pg.select_option('#cal-period', period)
    pg.click('[data-action=cal-shortcut]')
    pg.wait_for_function("() => window.__opened.length > 0", timeout=3000)
    return pg.evaluate("() => [window.__opened[0], window.__clip]")


def test_contenu(browser):
    print('Contenu envoyé')
    ps = [ponctuel('p1', 'Bloc a venir test', 840, 60, toCal=True), ponctuel('p2', 'Bloc termine test', 540, 60, toCal=True),
          ponctuel('p4', 'Bloc non coche test', 960, 60)]
    pg = page(browser, ps, real={'p:p2': {'start': 550, 'end': 590}}, tomorrow=[ponctuel('p5', 'Bloc demain test', 600, 60, toCal=True)])
    link, clip = send(pg, 'today')
    q = urlparse(link)
    check('le lien ouvre Raccourcis avec le raccourci « Plan du jour » et le presse-papiers', q.scheme == 'shortcuts' and q.netloc == 'run-shortcut' and parse_qs(q.query) == {'name': ['Plan du jour'], 'input': ['clipboard']}, link)
    data = json.loads(clip)
    check('la période est le jour même, de 00:00 à 23:59', data['from'] == '2026-11-03T00:00:00' and data['to'] == '2026-11-03T23:59:00', data)
    ev = {e['title']: (e['start'], e['end']) for e in data['events']}
    check('seuls les blocs cochés du jour sont envoyés', sorted(ev) == ['Bloc a venir test', 'Bloc termine test'], sorted(ev))
    check('heures réelles pour un bloc terminé, heure prévue pour un bloc à venir, format ISO local', ev['Bloc termine test'] == ('2026-11-03T09:10:00', '2026-11-03T09:50:00') and ev['Bloc a venir test'] == ('2026-11-03T14:00:00', '2026-11-03T15:00:00'), ev)
    check('un toast confirme l’envoi', '2 événements envoyés' in pg.inner_text('#toast'), pg.inner_text('#toast'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_periodes(browser):
    print('Périodes')
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60, toCal=True)], tomorrow=[ponctuel('p5', 'Bloc demain test', 600, 60, toCal=True)])
    _, clip = send(pg, 'week0')
    d = json.loads(clip)
    check('7 jours à partir d’aujourd’hui : du 3 au 9, avec les deux blocs', d['from'].startswith('2026-11-03') and d['to'].startswith('2026-11-09') and len(d['events']) == 2, d)
    pg.evaluate("() => { window.__opened = []; }")
    _, clip = send(pg, 'tomorrow')
    d = json.loads(clip)
    check('demain : du 4 au 4, seulement le bloc de demain', d['from'].startswith('2026-11-04') and d['to'].startswith('2026-11-04') and [e['title'] for e in d['events']] == ['Bloc demain test'], d)
    pg.close()


def test_passages(browser):
    print('Un événement par passage')
    act = free_act('a-plain', 'Dossier test', None)
    act['toCal'] = True
    pg = page(browser, [], acts=[act], segs={'act:a-plain': [{'cid': '', 'start': 480, 'end': 510}, {'cid': '', 'start': 660, 'end': None}]})
    _, clip = send(pg, 'today')
    ev = [(e['start'][11:16], e['end'][11:16]) for e in json.loads(clip)['events']]
    check('deux passages = deux événements, le dernier jusqu’à maintenant', ev == [('08:00', '08:30'), ('11:00', '11:30')], ev)
    pg.close()


def test_vide_et_replis(browser):
    print('Rien de coché, copie impossible')
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60)])
    _, clip = send(pg, 'today')
    check('rien de coché : le raccourci reçoit une liste vide (il videra l’agenda sur la période)', json.loads(clip)['events'] == [], clip)
    check('le toast le dit', 'videra' in pg.inner_text('#toast'), pg.inner_text('#toast'))
    pg.close()
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60, toCal=True)], clip=CLIP_KO)
    pg.select_option('#cal-period', 'today')
    pg.click('[data-action=cal-shortcut]')
    pg.wait_for_function("() => window.__opened.length > 0", timeout=3000)
    link = pg.evaluate("() => window.__opened[0]")
    q = parse_qs(urlparse(link).query)
    check('copie impossible : repli par le texte dans le lien', q.get('input') == ['text'] and json.loads(q['text'][0])['events'][0]['title'] == 'Bloc test', link)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_ics_conserve(browser):
    print('Bouton .ics conservé')
    pg = page(browser, [ponctuel('p1', 'Bloc test', 840, 60, toCal=True)])
    check('les deux boutons existent', pg.locator('[data-action=cal-shortcut]').count() == 1 and pg.locator('[data-action=cal-export]').count() == 1)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_contenu(browser)
        test_periodes(browser)
        test_passages(browser)
        test_vide_et_replis(browser)
        test_ics_conserve(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
