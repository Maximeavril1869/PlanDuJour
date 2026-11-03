"""Tests : nom d'un passage (0.30.0).

Au ▶ d'une tâche « sans heure », un champ « Dossier (facultatif) » donne un nom au passage (texte libre, espaces réduits, 60 caractères au plus).
Le nom apparaît dans la barre « en cours » et dans la frise, devient le titre de l'événement Calendrier (« Tâche · Nom »), se corrige dans le panneau
du bloc et se cumule dans les Stats sous la tâche. L'id envoyé à Raccourcis ne change pas.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_noms_passages.py
Aucune donnée réelle : libellés inventés (jamais de vrai SIREN).
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, stored_days
from test_passages import KEY, open_sans, seeded, segs

NOM_A = 'Dossier A-1'
NOM_B = 'Dossier B-2'


def start_named(pg, name):
    open_sans(pg)
    inp = pg.locator('details[data-fid=sans-none] input[data-passname]')
    if name is not None:
        inp.fill(name)
    pg.click('details[data-fid=sans-none] button[data-action=start]')


def stop(pg):
    pg.click('.runbar button[data-action=stop]')


def body(pg):
    return pg.evaluate("() => document.body.innerText")


def test_saisie(browser):
    print('Nom saisi au ▶')
    pg = seeded(browser)
    open_sans(pg)
    check('un champ « Dossier » est proposé sur la tâche sans heure', pg.locator('details[data-fid=sans-none] input[data-passname]').count() == 1)
    start_named(pg, NOM_A)
    check('le passage porte le nom saisi', [(g['cid'], g.get('name')) for g in segs(pg)] == [('', NOM_A)], segs(pg))
    check('la barre « en cours » affiche le nom', NOM_A in pg.inner_text('.runbar'), pg.inner_text('.runbar'))
    stop(pg)
    check('la frise affiche le nom du passage', 'Dossier test · ' + NOM_A in body(pg), body(pg)[:300])
    open_sans(pg)
    check('le champ est vide pour le passage suivant', pg.locator('details[data-fid=sans-none] input[data-passname]').input_value() == '')
    start_named(pg, None)
    check('sans nom saisi : aucun champ « name » enregistré', 'name' not in segs(pg)[1], segs(pg))
    stop(pg)
    start_named(pg, '  Dossier   B-2  ')
    check('espaces en trop réduits', segs(pg)[2].get('name') == NOM_B, segs(pg))
    stop(pg)
    start_named(pg, 'x' * 80)
    check('60 caractères au plus', len(segs(pg)[3].get('name', '')) == 60, segs(pg)[3])
    pg.reload()
    check('les noms sont conservés après rechargement', [g.get('name') for g in segs(pg)][:3] == [NOM_A, None, NOM_B], segs(pg))
    check('et relus au chargement : la frise les affiche encore', 'Dossier test · ' + NOM_A in body(pg) and 'Dossier test · ' + NOM_B in body(pg), body(pg)[:300])
    pg.close()


def test_panneau(browser):
    print('Corriger un nom dans le panneau du bloc')
    pg = seeded(browser)
    start_named(pg, NOM_A)
    stop(pg)
    open_sans(pg)
    pg.click('details[data-fid=sans-none] button[data-action=open-block]')
    field = pg.locator('input[data-seg-name="0"]')
    check('le panneau montre le nom du passage dans un champ', field.count() == 1 and field.input_value() == NOM_A)
    field.fill('Dossier C-3')
    field.dispatch_event('change')
    check('le nom corrigé est enregistré', segs(pg)[0].get('name') == 'Dossier C-3', segs(pg))
    field.fill('')
    field.dispatch_event('change')
    check('un nom vidé est retiré', 'name' not in segs(pg)[0], segs(pg))
    pg.close()


def test_stats_calendrier(browser):
    print('Stats, Calendrier et Raccourcis')
    pg = seeded(browser)
    start_named(pg, NOM_A)
    stop(pg)
    start_named(pg, NOM_B)
    stop(pg)
    start_named(pg, NOM_A)
    stop(pg)
    start_named(pg, None)
    stop(pg)
    k = day_offset(pg, 0)
    res = pg.evaluate("""(k) => {
      const s = JSON.parse(localStorage.getItem('plandujour.reglages')), d = JSON.parse(localStorage.getItem('plandujour.jours')).days;
      s.activities.forEach((a) => { a.toCal = true; });
      const st = window.PDJ.statsFor(d, s, k, k), row = st.rows.find((r) => r.name === 'Dossier test');
      const ev = window.PDJ.calendarEvents(d, s, k, k, 'plan');
      return { kids: row.children.map((c) => c.name), total: row.minutes, sum: row.children.reduce((t, c) => t + c.minutes, 0), titles: ev.map((e) => e.title), payload: JSON.parse(window.PDJ.shortcutPayload(ev, k, k)).events.map((e) => e.id) };
    }""", k)
    check('les Stats rangent le temps par nom sous la tâche, avec « Sans détail » pour le passage sans nom', sorted(res['kids']) == sorted([NOM_A, NOM_B, 'Sans détail']), res)
    check('le détail par nom retombe sur le total de la tâche', res['sum'] == res['total'], res)
    check('un passage = un événement, titre « Tâche · Nom » (le passage sans nom garde le titre de la tâche)', res['titles'] == ['Dossier test · ' + NOM_A, 'Dossier test · ' + NOM_B, 'Dossier test · ' + NOM_A, 'Dossier test'], res['titles'])
    check('les ids envoyés à Raccourcis ne contiennent pas le nom', res['payload'] == ['[PDJ-a-a-plain-%s-%d]' % (k, i) for i in range(4)], res['payload'])
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_saisie(browser)
        test_panneau(browser)
        test_stats_calendrier(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
