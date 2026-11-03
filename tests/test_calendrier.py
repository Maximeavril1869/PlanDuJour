"""Tests de l'app en navigateur automatisé (Chromium via Playwright) : export Calendrier et démarrage.

Lancer depuis la racine du dépôt :  python3 tests/test_calendrier.py
Voir tests/README.md pour l'installation. Aucune donnée réelle : tous les libellés sont inventés.
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

URL = (pathlib.Path(__file__).resolve().parent.parent / 'index.html').as_uri()
DAYS_KEY = 'plandujour.jours'

RESULTS = []


def check(name, cond, detail=''):
    RESULTS.append((name, bool(cond)))
    print(('  OK   ' if cond else '  ECHEC ') + name + ('' if cond else '  -> ' + str(detail)))


def new_page(browser, seed_days=None):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.goto(URL)
    if seed_days is not None:
        pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify(d))", seed_days)
        pg.reload()
    return pg


def seed_defaults(pg):
    """Enregistre les anciennes valeurs d'origine (fixture de test) : depuis la 0.31.1 l'app démarre vierge."""
    pg.evaluate("() => localStorage.setItem('plandujour.reglages', JSON.stringify(window.PDJ.defaultSettings()))")
    pg.reload()


def day_offset(pg, n):
    return pg.evaluate("""(n) => { const d = new Date(); d.setDate(d.getDate() + n); const z = (x) => String(x).padStart(2, '0');
      return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate()); }""", n)


def stored_days(pg):
    return json.loads(pg.evaluate("() => localStorage.getItem('plandujour.jours')") or '{"days":{}}')['days']


def all_ponctuels(pg):
    out = []
    for date, d in stored_days(pg).items():
        for p in d.get('ponctuels', []):
            out.append((date, p))
    return out


def ponctuel(id_, name, start, duration=60, **extra):
    p = {'id': id_, 'name': name, 'mode': 'fixed', 'entry': 'duration', 'start': start, 'duration': duration,
         'confirm': False, 'carry': False, 'cat': None, 'alarm': None, 'parallel': False, 'toCal': False}
    p.update(extra)
    return p


def seed(date, *ponctuels, real=None):
    return {'version': 2, 'days': {date: {'real': real or {}, 'ponctuels': list(ponctuels), 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None}}}


def test_demarrage(browser):
    print('Démarrage')
    pg = new_page(browser)
    check('aucune erreur JavaScript au chargement', not pg.errors, pg.errors)
    check('les quatre onglets existent', all(pg.locator(s).count() == 1 for s in ('#tab-day', '#tab-recap', '#tab-stats', '#tab-settings')))
    pg.close()


def test_export(browser):
    print('Export vers Calendrier')
    pg = new_page(browser)
    d = day_offset(pg, 1)
    res = pg.evaluate("""(d) => {
      const P = window.PDJ, s = P.defaultSettings(), day = P.emptyDay();
      const mk = (id, name, st, toCal, alarm) => ({ id, name, mode: 'fixed', entry: 'duration', start: st, duration: 60, confirm: false, carry: false, cat: null, alarm: alarm, parallel: false, toCal });
      day.ponctuels = [mk('idA', 'Coche sans rappel', 600, true, null), mk('idB', 'Coche avec rappel', 720, true, 10), mk('idC', 'Non coche', 800, false, 10), mk('idD', 'Rappel heure', 900, true, 0)];
      s.activities.forEach((a) => { a.days = [1, 2, 3, 4, 5, 6, 7]; a.toCal = false; a.alarm = 15; });   // aucune activité cochée, même avec un rappel...
      s.activities.find((a) => a.id === 'act-sax').toCal = true;                                        // ...sauf le saxophone
      const ev = P.calendarEvents({ [d]: day }, s, d, d, 'plan');
      return { ev: ev, ics: P.buildIcs(ev) };
    }""", d)
    titles = [e['title'] for e in res['ev']]
    check('un bloc coché est exporté, avec ou sans rappel', 'Coche sans rappel' in titles and 'Coche avec rappel' in titles, titles)
    check('un bloc non coché n’est pas exporté, même avec un rappel', 'Non coche' not in titles, titles)
    check('seuls les blocs cochés sortent (activités comprises)', sorted(titles) == ['Coche avec rappel', 'Coche sans rappel', 'Rappel heure', 'Saxophone'], titles)
    sans = [e for e in res['ev'] if e['title'] == 'Coche sans rappel'][0]
    check('un bloc coché sans rappel n’a pas d’alarme', sans['alarm'] is None, sans)
    mine = [e for e in res['ev'] if e['title'] == 'Coche avec rappel'][0]
    check('le bloc ponctuel a un UID et un code sans date', mine['uid'] == 'pdj-p-idB' and mine['code'] == 'PDJ-p-idB', mine)
    check('le code part dans les Notes (DESCRIPTION) du .ics', 'DESCRIPTION:PDJ-p-idB' in res['ics'])
    check('le rappel part dans le .ics', 'TRIGGER:-PT10M' in res['ics'] and 'TRIGGER:PT0S' in res['ics'])
    others = [e for e in res['ev'] if e['title'] == 'Saxophone']
    check('l’occurrence d’activité porte un code PDJ-a avec son jour', all(e['code'].startswith('PDJ-a-') and e['code'].endswith(d) for e in others), others)
    pg.close()


def test_par_defaut(browser):
    print('Premier lancement vierge (0.31.1)')
    pg = new_page(browser)
    d = day_offset(pg, 1)
    n = pg.evaluate("(d) => { const P = window.PDJ; return P.calendarEvents({}, P.defaultSettings(), d, d, 'plan').length; }", d)
    check('rien n’est exporté tant que rien n’est coché', n == 0, n)
    check('l’app vierge le dit sur la page du jour', 'App vierge' in pg.inner_text('#panel-day'), pg.inner_text('#panel-day')[:200])
    pg.click('#tab-recap')
    check('l’app vierge le dit dans le Récap', 'App vierge' in pg.inner_text('#panel-recap'), pg.inner_text('#panel-recap')[:200])
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-acts] > summary')
    check('aucune activité au premier lancement', pg.locator('[data-action=add-act]').count() == 1 and pg.locator('input[data-a=toCal]').count() == 0, pg.locator('input[data-a=toCal]').count())
    stored = pg.evaluate("() => localStorage.getItem('plandujour.reglages')")
    check('rien n’est enregistré tant que tu n’as pas enregistré', stored is None, stored)
    check('plus d’import dans Réglages', pg.locator('#cal-text').count() == 0 and pg.locator('[data-action=cal-import]').count() == 0)
    check('le bouton d’export est là', pg.locator('[data-action=cal-export]').count() == 1)
    pg.click('[data-action=add-act]')
    check('la case « Exporter vers Calendrier » existe dans une activité ajoutée', pg.locator('input[data-a=toCal]').count() >= 1)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.evaluate("() => localStorage.setItem('plandujour.reglages', '{pas du json')")
    pg.reload()
    pg.click('#tab-recap')
    check('réglages illisibles : app vierge et message d’avertissement', 'illisibles' in pg.inner_text('#panel-recap') and 'une app vierge' in pg.inner_text('#panel-recap'), pg.inner_text('#panel-recap')[:200])
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-acts] > summary')
    check('réglages illisibles : aucune activité (pas de valeurs d’origine)', pg.locator('input[data-a=toCal]').count() == 0, pg.locator('input[data-a=toCal]').count())
    pg.close()


def test_case_enregistree(browser):
    print('Case à cocher d’un bloc ponctuel')
    pg = new_page(browser)
    d = day_offset(pg, 1)
    pg.evaluate("""([d]) => { const P = window.PDJ; const day = P.emptyDay();
      day.ponctuels = [{ id: 'idZ', name: 'Dentiste', mode: 'fixed', entry: 'duration', start: 600, duration: 30, confirm: false, carry: false, cat: null, alarm: null, parallel: false, toCal: true }];
      localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: { [d]: day } })); }""", [d])
    pg.reload()
    ps = all_ponctuels(pg)
    check('la case cochée survit au rechargement', len(ps) == 1 and ps[0][1].get('toCal') is True, ps)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for t in (test_demarrage, test_export, test_par_defaut, test_case_enregistree):
            t(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
