"""Tests de l'app en navigateur automatisé (Chromium via Playwright) : calendrier et démarrage.

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


def day_offset(pg, n):
    return pg.evaluate("""(n) => { const d = new Date(); d.setDate(d.getDate() + n); const z = (x) => String(x).padStart(2, '0');
      return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate()); }""", n)


def import_text(pg, text):
    pg.click('#tab-settings')
    pg.evaluate("""(t) => { document.querySelectorAll('details').forEach((d) => { d.open = true; });
      document.querySelector('#cal-text').value = t; document.querySelector('[data-action=cal-import]').click(); }""", text)
    return pg.inner_text('#cal-result')


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
         'confirm': False, 'carry': False, 'cat': None, 'alarm': None, 'parallel': False, 'noCal': False}
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
      const mk = (id, name, st, fromCal, alarm) => ({ id, name, mode: 'fixed', entry: 'duration', start: st, duration: 60, confirm: false, carry: false, cat: null, alarm: alarm, parallel: false, noCal: false, fromCal });
      day.ponctuels = [mk('idA', 'Venu cal', 600, true, 10), mk('idB', 'Cree app', 720, false, 10), mk('idC', 'Sans rappel', 800, false, null), mk('idD', 'Rappel heure', 900, false, 0)];
      s.activities.forEach((a) => { a.days = [1, 2, 3, 4, 5, 6, 7]; a.alarm = null; });    // aucune activité n'a de rappel...
      s.activities.find((a) => a.id === 'act-sax').alarm = 5;                              // ...sauf le saxophone
      const ev = P.calendarEvents({ [d]: day }, s, d, d, 'plan');
      return { ev: ev, ics: P.buildIcs(ev) };
    }""", d)
    titles = [e['title'] for e in res['ev']]
    check('un rendez-vous venu du calendrier n’est pas exporté, même avec un rappel', 'Venu cal' not in titles, titles)
    check('un bloc avec rappel est exporté', 'Cree app' in titles)
    check('un rappel « à l’heure » (0 minute) compte', 'Rappel heure' in titles)
    check('un bloc sans rappel n’est pas exporté', 'Sans rappel' not in titles, titles)
    check('seuls les blocs avec rappel sortent (une activité sans rappel reste chez elle)', sorted(titles) == ['Cree app', 'Rappel heure', 'Saxophone'], titles)
    mine = [e for e in res['ev'] if e['title'] == 'Cree app'][0]
    check('le bloc ponctuel a un UID et un code sans date', mine['uid'] == 'pdj-p-idB' and mine['code'] == 'PDJ-p-idB', mine)
    check('le code part dans les Notes (DESCRIPTION) du .ics', 'DESCRIPTION:PDJ-p-idB' in res['ics'])
    check('le rappel part dans le .ics', 'TRIGGER:-PT10M' in res['ics'] and 'TRIGGER:PT0S' in res['ics'])
    others = [e for e in res['ev'] if e['title'] == 'Saxophone']
    check('l’occurrence d’activité porte un code PDJ-a avec son jour', all(e['code'].startswith('PDJ-a-') and e['code'].endswith(d) for e in others), others)
    pg.close()


def test_lecture(browser):
    print('Lecture des lignes et des .ics')
    pg = new_page(browser)
    ev = pg.evaluate("""() => window.PDJ.parseCalendarText([
      '2026-11-10 09:00 10:00 Ancien format',
      '2026-11-10 09:00 10:00 Complet | Perso | 20261102153012 | PDJ-p-idX',
      '2026-11-10 11:00 12:00 Sans notes | Travail | 20261102153013 | ',
      '2026-11-10 13:00 14:00 Création invalide | Travail | 2026 | note libre'
    ].join('\\n'))""")
    check('ancien format toujours lu', ev[0]['title'] == 'Ancien format' and ev[0]['code'] is None and ev[0]['created'] is None, ev[0])
    check('code, calendrier et création lus', ev[1]['code'] == 'PDJ-p-idX' and ev[1]['cal'] == 'Perso' and ev[1]['created'] == '20261102153012', ev[1])
    check('notes vides acceptées', ev[2]['code'] is None and ev[2]['created'] == '20261102153013', ev[2])
    check('date de création invalide ignorée', ev[3]['created'] is None, ev[3])
    ics = pg.evaluate("""() => window.PDJ.parseCalendarText('BEGIN:VCALENDAR\\r\\nBEGIN:VEVENT\\r\\nDTSTART:20261110T090000\\r\\nDTEND:20261110T100000\\r\\nSUMMARY:Test ics\\r\\nCREATED:20261102T153012Z\\r\\nDESCRIPTION:PDJ-p-idY\\r\\nEND:VEVENT\\r\\nEND:VCALENDAR')""")
    check('.ics : code et création lus', ics[0]['code'] == 'PDJ-p-idY' and ics[0]['created'] == '20261102153012', ics)
    pg.close()


def test_import_par_code(browser):
    print('Import : mise à jour par code')
    pg = new_page(browser)
    d1, d2 = day_offset(pg, 3), day_offset(pg, 5)
    pg.close()
    pg = new_page(browser, seed(d1, ponctuel('idP', 'Rdv app', 600), real={'p:idP': {'start': 601, 'end': 650}}))
    r = import_text(pg, d2 + ' 14:00 15:30 Rdv déplacé | Plan du jour | 20261102153012 | PDJ-p-idP')
    ps = all_ponctuels(pg)
    check('un seul bloc après mise à jour (pas de doublon)', len(ps) == 1, ps)
    date, p = ps[0]
    check('titre, jour, début et durée mis à jour', date == d2 and p['name'] == 'Rdv déplacé' and p['start'] == 840 and p['duration'] == 90, ps)
    check('le bloc garde son identifiant', p['id'] == 'idP')
    check('les heures réelles suivent le bloc', stored_days(pg)[d2]['real'].get('p:idP') == {'start': 601, 'end': 650}, stored_days(pg)[d2])
    check('le message annonce la mise à jour', '1 rendez-vous mis à jour' in r and '1 par code' in r, r)
    r2 = import_text(pg, d2 + ' 14:00 15:30 Rdv déplacé | Plan du jour | 20261102153012 | PDJ-p-idP')
    check('un second import identique ne change rien', len(all_ponctuels(pg)) == 1 and 'mis à jour' not in r2, r2)
    import_text(pg, d2 + ' 10:00 11:00 Bloc supprimé | Plan du jour | 20261102153012 | PDJ-p-inconnu')
    check('un code dont le bloc n’existe plus ne recrée rien', len(all_ponctuels(pg)) == 1)
    import_text(pg, d2 + ' 10:00 11:00 Occurrence | Plan du jour | 20261102153012 | PDJ-a-act-sax-' + d2)
    check('une occurrence d’activité exportée est ignorée', len(all_ponctuels(pg)) == 1)
    import_text(pg, d2 + ' 16:00 17:00 Ancien export | Plan du jour | 20261102153012 | ')
    check('un événement du calendrier dédié sans code est ignoré', len(all_ponctuels(pg)) == 1)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_import_par_creation(browser):
    print('Import : retrouver un événement par sa date de création')
    pg = new_page(browser)
    d1, d2 = day_offset(pg, 2), day_offset(pg, 4)
    import_text(pg, d1 + ' 09:00 10:00 Réunion test | Perso | 20261102153012 | ')
    ps = all_ponctuels(pg)
    check('ajouté, marqué « vient du calendrier » et relié à sa date de création', len(ps) == 1 and ps[0][1]['fromCal'] is True and ps[0][1]['calKey'] == '20261102153012', ps)
    r = import_text(pg, d2 + ' 15:00 16:30 Réunion renommée | Perso | 20261102153012 | ')
    ps = all_ponctuels(pg)
    check('titre, jour et heures changés : mis à jour sans doublon', len(ps) == 1 and ps[0][0] == d2 and ps[0][1]['name'] == 'Réunion renommée' and ps[0][1]['start'] == 900 and ps[0][1]['duration'] == 90, ps)
    check('le message annonce « par date de création »', '1 par date de création' in r, r)
    check('toujours marqué « vient du calendrier »', ps[0][1]['fromCal'] is True)
    pg.close()

    pg = new_page(browser)
    d1 = day_offset(pg, 2)
    import_text(pg, d1 + ' 09:00 10:00 Série A | Perso | 20261102153012 | \n' + d1 + ' 11:00 12:00 Série B | Perso | 20261102153012 | ')
    ps = all_ponctuels(pg)
    check('deux événements de même date de création : ajoutés sans code de reconnaissance', len(ps) == 2 and all(p['calKey'] is None for _, p in ps), ps)
    pg.close()

    pg = new_page(browser)
    d1 = day_offset(pg, 2)
    import_text(pg, d1 + ' 09:00 10:00 Sans création | Perso | | ')
    import_text(pg, d1 + ' 09:00 10:00 Sans création | Perso | | ')
    check('sans date de création : le doublon exact reste évité', len(all_ponctuels(pg)) == 1)
    pg.close()


def test_import_relie_ancien(browser):
    print('Import : relier un rendez-vous déjà importé')
    pg = new_page(browser)
    d1, d2 = day_offset(pg, 2), day_offset(pg, 3)
    pg.close()
    pg = new_page(browser, seed(d1, ponctuel('idOld', 'Ancien rdv', 600, fromCal=True)))
    r = import_text(pg, d1 + ' 10:00 11:00 Ancien rdv | Perso | 20261102153012 | ')
    ps = all_ponctuels(pg)
    check('l’ancien bloc reçoit la date de création, sans doublon', len(ps) == 1 and ps[0][1]['calKey'] == '20261102153012' and 'relié' in r, (ps, r))
    import_text(pg, d2 + ' 10:00 11:00 Ancien rdv décalé | Perso | 20261102153012 | ')
    ps = all_ponctuels(pg)
    check('il est ensuite retrouvé après changement', len(ps) == 1 and ps[0][0] == d2 and ps[0][1]['name'] == 'Ancien rdv décalé', ps)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_edition_garde_le_lien(browser):
    print('Éditeur : le lien est conservé')
    pg = new_page(browser)
    today = day_offset(pg, 0)
    import_text(pg, today + ' 09:00 10:00 Réunion test | Perso | 20261102153012 | ')
    pg.click('#tab-day')
    pg.get_by_text('Réunion test').first.click()
    pg.wait_for_timeout(200)
    check('la case « Vient de mon calendrier » est cochée', pg.evaluate("() => document.querySelector('#bp-edit [data-a=fromCal]').checked"))
    pg.fill('#bp-edit [data-a=name]', 'Réunion modifiée')
    pg.click('#bp-save')
    pg.wait_for_timeout(200)
    ps = all_ponctuels(pg)
    check('après modification dans l’app, la date de création est conservée', ps[0][1]['name'] == 'Réunion modifiée' and ps[0][1]['calKey'] == '20261102153012', ps)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for t in (test_demarrage, test_export, test_lecture, test_import_par_code, test_import_par_creation, test_import_relie_ancien, test_edition_garde_le_lien):
            t(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
