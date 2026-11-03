"""Tests : tâches « sans heure » refaisables plusieurs fois par jour (0.25.3).

Une tâche sans heure et sans sous-activité reste dans « Sans heure » après ■ ; chaque ▶ ouvre un nouveau passage (un temps chronométré
dont l'identifiant de sous-activité est vide). Chaque passage a son créneau dans la journée et compte dans les Stats ; pas de case « fait ».
Une tâche à sous-activités garde son fonctionnement. Un ancien temps réel unique devient le premier passage.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_passages.py
Aucune donnée réelle : libellés inventés.
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, new_page, ponctuel, stored_days
from test_regroupements import free_act

KEY = 'act:a-plain'


def seeded(browser, days=None, with_kids=False):
    pg = new_page(browser)
    plain = free_act('a-plain', 'Dossier test', None)
    acts = [plain]
    if with_kids:
        k = free_act('a-kids', 'Courrier test', None)
        k['children'] = [{'id': 'k1', 'name': 'Canal A'}, {'id': 'k2', 'name': 'Canal B'}]
        acts.append(k)
    settings = pg.evaluate("(a) => { const s = window.PDJ.defaultSettings(); s.categories = []; s.activities = a; s.templates = []; return s; }", acts)
    pg.evaluate("([s, d]) => { localStorage.setItem('plandujour.reglages', JSON.stringify(s)); if (d) localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", [settings, days])
    pg.reload()
    return pg


def open_sans(pg):
    if not pg.evaluate("() => document.querySelector('details[data-fid=card-sansheure]').open"):
        pg.click('details[data-fid=card-sansheure] > summary')
    if not pg.evaluate("() => document.querySelector('details[data-fid=sans-none]').open"):
        pg.click('details[data-fid=sans-none] > summary')


def segs(pg, key=KEY):
    return stored_days(pg).get(day_offset(pg, 0), {}).get('segs', {}).get(key, [])


def row(pg, name):
    return pg.evaluate("(n) => { const li = [...document.querySelectorAll('details[data-fid=card-sansheure] li')].find((l) => l.textContent.includes(n)); return li ? li.textContent : null; }", name)


def test_chrono(browser):
    print('Plusieurs passages au chrono')
    pg = seeded(browser)
    open_sans(pg)
    pg.click('details[data-fid=sans-none] button[data-action=start]')
    check('▶ ouvre un passage sans sous-activité', [(g['cid'], g['end']) for g in segs(pg)] == [('', None)], segs(pg))
    check('pas de temps réel unique enregistré', KEY not in stored_days(pg)[day_offset(pg, 0)]['real'])
    pg.click('.runbar button[data-action=stop]')
    check('■ ferme le passage', len(segs(pg)) == 1 and segs(pg)[0]['end'] is not None, segs(pg))
    open_sans(pg)
    check('la tâche reste dans « Sans heure » avec son temps du jour', row(pg, 'Dossier test') is not None and 'min' in row(pg, 'Dossier test'), row(pg, 'Dossier test'))
    check('aucune case « fait » pour cette tâche', pg.locator('details[data-fid=sans-none] input[type=checkbox]').count() == 0)
    check('▶ Démarrer est de nouveau proposé', pg.locator('details[data-fid=sans-none] button[data-action=start]').count() == 1)
    pg.click('details[data-fid=sans-none] button[data-action=start]')
    pg.click('.runbar button[data-action=stop]')
    check('un second ▶ ajoute un second passage', len(segs(pg)) == 2 and all(g['cid'] == '' and g['end'] is not None for g in segs(pg)), segs(pg))
    check('aucune sous-activité cochée par un passage', 'kidsDone' not in stored_days(pg)[day_offset(pg, 0)] or not stored_days(pg)[day_offset(pg, 0)]['kidsDone'].get(KEY))
    pg.reload()
    open_sans(pg)
    check('après fermeture de l’app, les deux passages sont là et la tâche reste proposée', len(segs(pg)) == 2 and row(pg, 'Dossier test') is not None)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_creneaux_et_stats(browser):
    print('Créneaux de la journée et Stats')
    today = None
    pg = seeded(browser)
    today = day_offset(pg, 0)
    day = {'real': {}, 'ponctuels': [], 'subtasks': {}, 'review': {}, 'profile': None, 'presence': None,
           'segs': {KEY: [{'cid': '', 'start': 480, 'end': 510}, {'cid': '', 'start': 600, 'end': 645}]}}
    pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify(d))", {'version': 2, 'days': {today: day}})
    pg.reload()
    spans = pg.evaluate("() => window.PDJ.buildDay(JSON.parse(localStorage.getItem('plandujour.reglages')), JSON.parse(localStorage.getItem('plandujour.jours')).days['%s'], 1, null, false, '%s').spans.map((s) => [s.name, s.start, s.end])" % (today, today))
    check('chaque passage a son créneau dans la journée', spans == [['Dossier test', 480, 510], ['Dossier test', 600, 645]], spans)
    open_sans(pg)
    check('« Sans heure » indique 2 passages et la durée totale (1 h 15)', '2 passages' in row(pg, 'Dossier test') and '1 h 15' in row(pg, 'Dossier test'), row(pg, 'Dossier test'))
    pg.click('#tab-stats')
    txt = pg.inner_text('#panel-stats')
    check('les Stats additionnent les passages (1 h 15)', 'Dossier test' in txt and '1 h 15' in txt, txt[:300])
    check('aucune sous-activité inventée dans les Stats', 'Sous-activité supprimée' not in txt)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_panneau(browser):
    print('Panneau : passages à la main')
    pg = seeded(browser)
    today = day_offset(pg, 0)
    open_sans(pg)
    pg.click('details[data-fid=sans-none] button[data-action=open-block]')
    check('le panneau parle de passages, sans choix de sous-activité ni début/fin uniques', pg.inner_text('#bp-children-h') == 'Passages' and not pg.is_visible('#seg-child') and not pg.is_visible('#bp-real'))
    pg.fill('#seg-start', '0800'); pg.fill('#seg-end', '0830'); pg.click('[data-bp=add-seg]')
    pg.fill('#seg-start', '1400'); pg.fill('#seg-end', '1415'); pg.click('[data-bp=add-seg]')
    check('deux passages saisis à la main sont enregistrés et triés', [(g['cid'], g['start'], g['end']) for g in segs(pg)] == [('', 480, 510), ('', 840, 855)], segs(pg))
    check('la liste du panneau les numérote', pg.locator('#bp-seg-list li').count() == 2 and 'Passage 2' in pg.inner_text('#bp-seg-list'))
    pg.click('#bp-seg-list li >> nth=0 >> button')
    check('on peut supprimer un passage', [(g['start'], g['end']) for g in segs(pg)] == [(840, 855)], segs(pg))
    pg.click('#bp-save')
    check('enregistrer le panneau ne crée pas de temps réel unique', KEY not in stored_days(pg)[today]['real'], stored_days(pg)[today]['real'])
    pg.click('details[data-fid=sans-none] button[data-action=open-block]')
    pg.click('#bp-clear')
    check('« Effacer les passages » vide la journée de cette tâche', segs(pg) == [] and KEY not in stored_days(pg)[today]['real'])
    open_sans(pg)
    check('la tâche est de nouveau « à faire » (sans durée)', row(pg, 'Dossier test') is not None and 'passage' not in row(pg, 'Dossier test'), row(pg, 'Dossier test'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_ancien_temps_et_ponctuel(browser):
    print('Ancien temps réel et bloc ponctuel')
    pg = seeded(browser)
    today = day_offset(pg, 0)
    p = ponctuel('p1', 'Tâche ponctuelle test', None, mode='free', entry='duration')
    day = {'real': {KEY: {'start': 480, 'end': 510}}, 'ponctuels': [p], 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None}
    pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify(d))", {'version': 2, 'days': {today: day}})
    pg.reload()
    open_sans(pg)
    check('une tâche terminée à l’ancienne reste proposée', row(pg, 'Dossier test') is not None)
    pg.click('details[data-fid=sans-none] li:has-text("Dossier test") button[data-action=start]')
    pg.click('.runbar button[data-action=stop]')
    d = stored_days(pg)[today]
    check('l’ancien temps devient le premier passage, le nouveau le suit', len(d['segs'][KEY]) == 2 and d['segs'][KEY][0] == {'cid': '', 'start': 480, 'end': 510} and KEY not in d['real'], d)
    open_sans(pg)
    pg.click('details[data-fid=sans-none] li:has-text("Tâche ponctuelle test") button[data-action=start]')
    pg.click('.runbar button[data-action=stop]')
    pg.click('details[data-fid=sans-none] li:has-text("Tâche ponctuelle test") button[data-action=start]')
    pg.click('.runbar button[data-action=stop]')
    check('un bloc ponctuel sans heure se refait aussi', len(stored_days(pg)[today]['segs'].get('p:p1', [])) == 2, stored_days(pg)[today]['segs'])
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_sous_activites_inchangees(browser):
    print('Tâche à sous-activités : comportement inchangé')
    pg = seeded(browser, with_kids=True)
    today = day_offset(pg, 0)
    open_sans(pg)
    li = pg.locator('details[data-fid=sans-none] li:has-text("Courrier test")')
    check('pas de ▶ global, des ▶ par sous-activité et des cases', li.locator('button[data-action=start]').count() == 0 and li.locator('input[data-kid-done]').count() == 2)
    pg.click('details[data-fid=sans-none] li:has-text("Courrier test") button[data-action=child-go][data-cid=k1]')
    pg.click('.runbar button[data-action=stop]')
    d = stored_days(pg)[today]
    check('le chrono coche toujours la sous-activité', d['segs']['act:a-kids'][0]['cid'] == 'k1' and d['kidsDone']['act:a-kids'] == {'k1': True}, d)
    open_sans(pg)
    check('« faites » est toujours affiché', 'faites' in row(pg, 'Courrier test'), row(pg, 'Courrier test'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_chrono(browser)
        test_creneaux_et_stats(browser)
        test_panneau(browser)
        test_ancien_temps_et_ponctuel(browser)
        test_sous_activites_inchangees(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
