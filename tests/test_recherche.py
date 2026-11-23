"""Tests : la recherche distingue le prévu du fait (0.40.0). Heure simulée, aucune donnée réelle.
Lancer :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_recherche.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, seed_defaults

MARDI = datetime(2026, 11, 3, 18, 0)
DAYS = """() => { const d = (real) => ({ real: real, ponctuels: [], subtasks: {}, review: {}, profile: null, segs: {}, kidsDone: {}, presence: null, trip: null, removed: [] });
  localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: {
    '2026-11-02': d({ 'act:act-trajet-aller': { start: 395, end: 450 }, 'act:act-trajet-retour': { start: null, end: null, missed: true } }),
    '2026-11-03': d({ 'act:act-trajet-aller': { start: 390, end: 440 } }) } })); }"""
GROUPS = "() => [...document.querySelectorAll('#panel-recap .card')].filter((c) => c.querySelector('h2') && /^(Prévu|Fait ou passé)/.test(c.querySelector('h2').textContent)).map((c) => ({ title: c.querySelector('h2').textContent, rows: [...c.querySelectorAll('li')].map((l) => l.innerText.replace(/\\s+/g, ' ').trim()) }))"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.clock.install(time=MARDI)
        pg.goto(URL)
        seed_defaults(pg)
        pg.evaluate(DAYS)
        pg.reload()
        print('Recherche : prévu et fait (dans le Récap depuis la 0.41.0)')
        check('la page du jour n’a plus de barre de recherche', pg.locator('#day-head input[type=search]').count() == 0 and pg.locator('#day-search').count() == 0)
        pg.click('#tab-recap')
        check('le Récap a la barre de recherche', pg.locator('#recap-search').count() == 1)
        pg.fill('#recap-search', 'trajet aller')
        pg.wait_for_timeout(200)
        g = pg.evaluate(GROUPS)
        titles = [x['title'] for x in g]
        check('deux groupes : Prévu puis Fait ou passé', len(g) == 2 and titles[0].startswith('Prévu') and titles[1].startswith('Fait ou passé'), titles)
        plan, past = g[0]['rows'], g[1]['rows']
        check('le groupe Prévu ne contient que du prévu', plan and all('prévu' in r for r in plan), plan[:3])
        check('le prévu garde l’heure prévue', all('06:30' in r for r in plan), plan[:2])
        check('le groupe passé contient le fait d’aujourd’hui et celui d’hier', len(past) == 2 and all('fait' in r for r in past), past)
        check('un fait montre l’heure réelle (hier 06:35–07:30, aujourd’hui 06:30–07:20)', '06:30–07:20' in past[0] and '06:35–07:30' in past[1], past)
        check('le plus récent d’abord (aujourd’hui avant hier)', 'mar 03/11' in past[0] and 'lun 02/11' in past[1], past)
        pg.fill('#recap-search', 'trajet retour')
        pg.wait_for_timeout(200)
        g = pg.evaluate(GROUPS)
        check('un raté est classé dans « Fait ou passé » avec son statut', any(x['title'].startswith('Fait ou passé') and any('raté' in r for r in x['rows']) for x in g), g)
        pg.fill('#recap-search', 'zzzz')
        pg.wait_for_timeout(200)
        check('aucun résultat : message', 'Aucune tâche trouvée' in pg.inner_text('#panel-recap'))
        pg.fill('#recap-search', 'a')
        pg.wait_for_timeout(200)
        check('une seule lettre : message', 'au moins 2 lettres' in pg.inner_text('#panel-recap'))
        pg.fill('#recap-search', 'trajet aller')
        pg.wait_for_timeout(200)
        pg.locator('[data-search-go="2026-11-03"]').first.click()
        pg.wait_for_timeout(200)
        check('« Ouvrir » revient sur la page du jour, à la date trouvée', pg.locator('#panel-day').is_visible() and pg.locator('#panel-recap').is_hidden() and 'Mardi 3 novembre' in pg.inner_text('#day-head'), pg.inner_text('#day-head')[:80])
        pg.click('#tab-recap')
        check('la recherche est vidée après « Ouvrir »', pg.input_value('#recap-search') == '')
        check('aucune erreur JavaScript', not errs, errs)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
