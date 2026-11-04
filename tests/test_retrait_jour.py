"""Tests : retirer une activité récurrente pour un seul jour (0.33.0).

Bouton « Retirer pour ce jour » dans le panneau d'une activité récurrente ; ligne « Retiré ce jour : … · Rétablir » sur le Jour ;
seul ce jour change (frise, Récap, export Calendrier) ; refus si le bloc a déjà des heures réelles ; données jamais perdues (rétablir remet tout).
Les anciennes activités d'origine servent de fixture (seed_defaults) : l'app démarre vierge depuis la 0.31.1. Heure simulée. Aucune donnée réelle.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_retrait_jour.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, seed_defaults, stored_days

MARDI = datetime(2026, 11, 3)
KEY = 'act:act-trajet-aller'


def page(browser, h=7, m=0):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.clock.install(time=MARDI.replace(hour=h, minute=m))
    pg.goto(URL)
    seed_defaults(pg)
    return pg


def blocks(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#day-timeline .blk .bn')].map((b) => b.textContent.replace('✓ ', '').trim())")


def removed(pg, date='2026-11-03'):
    return stored_days(pg).get(date, {}).get('removed')


def toast(pg):
    return pg.evaluate("() => { const t = document.querySelector('#toast'); return t.hidden ? '' : t.textContent; }")


def test_retrait_et_retablissement(browser):
    print('Retirer un jour, rétablir')
    pg = page(browser)
    check('au départ, le trajet aller est sur la frise', 'Trajet aller' in blocks(pg), blocks(pg))
    pg.click('[data-key="%s"]' % KEY)
    check('le bouton « Retirer pour ce jour » est dans le panneau d’une activité récurrente', pg.locator('#bp-remove').is_visible() and not pg.locator('#bp-del').is_visible())
    pg.click('#bp-remove')
    check('le bloc disparaît de la frise', 'Trajet aller' not in blocks(pg), blocks(pg))
    check('les autres blocs restent', 'Trajet retour' in blocks(pg), blocks(pg))
    check('le jour enregistre l’activité retirée', removed(pg) == ['act-trajet-aller'], removed(pg))
    check('une ligne « Retiré ce jour » propose de rétablir', 'Retiré ce jour' in pg.inner_text('#day-head') and 'Trajet aller · Rétablir' in pg.inner_text('#day-head'), pg.inner_text('#day-head')[:300])
    check('un message confirme', 'retiré pour ce jour' in toast(pg), toast(pg))
    pg.reload()
    check('le retrait survit au rechargement', 'Trajet aller' not in blocks(pg) and removed(pg) == ['act-trajet-aller'])
    pg.click('[data-day-nav="1"]')
    check('le lendemain, le trajet aller est toujours là (un seul jour)', 'Trajet aller' in blocks(pg), blocks(pg))
    check('le lendemain, pas de ligne « Retiré ce jour »', 'Retiré ce jour' not in pg.inner_text('#day-head'))
    pg.click('[data-day-nav="-1"]')
    pg.click('[data-action=restore-act]')
    check('« Rétablir » remet le bloc', 'Trajet aller' in blocks(pg) and removed(pg) == [], (blocks(pg), removed(pg)))
    check('la ligne « Retiré ce jour » disparaît', 'Retiré ce jour' not in pg.inner_text('#day-head'))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_effets(browser):
    print('Effets : Récap, calendrier, jours voisins')
    pg = page(browser)
    pg.evaluate("""() => { const st = JSON.parse(localStorage.getItem('plandujour.reglages')); st.activities.forEach((a) => { a.toCal = true; });
      localStorage.setItem('plandujour.reglages', JSON.stringify(st)); }""")
    pg.reload()
    n_avant = pg.evaluate("() => { const P = window.PDJ, st = JSON.parse(localStorage.getItem('plandujour.reglages')); return P.calendarEvents({}, st, '2026-11-03', '2026-11-03', 'plan').map((e) => e.title); }")
    pg.click('[data-key="%s"]' % KEY)
    pg.click('#bp-remove')
    n_apres = pg.evaluate("() => { const P = window.PDJ, st = JSON.parse(localStorage.getItem('plandujour.reglages')), d = JSON.parse(localStorage.getItem('plandujour.jours')).days; return P.calendarEvents(d, st, '2026-11-03', '2026-11-03', 'plan').map((e) => e.title); }")
    check('avant, l’export du jour contient le trajet aller', any('Trajet aller' in t for t in n_avant), n_avant)
    check('après, l’export du jour ne le contient plus (les autres restent)', not any('Trajet aller' in t for t in n_apres) and any('Trajet retour' in t for t in n_apres), n_apres)
    pg.click('#tab-recap')
    rows = pg.evaluate("() => [...document.querySelectorAll('#panel-recap li .what')].map((s) => s.textContent)")
    check('le Récap du jour retiré n’affiche plus le trajet aller', not any('Trajet aller' in t for t in rows) and any('Trajet retour' in t for t in rows), rows)
    pg.click('[data-recap-date="2026-11-04"]')
    rows = pg.evaluate("() => [...document.querySelectorAll('#panel-recap li .what')].map((s) => s.textContent)")
    check('le Récap d’un autre jour l’affiche toujours', any('Trajet aller' in t for t in rows), rows)
    pg.click('#tab-stats')
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_refus_et_limites(browser):
    print('Refus si heures réelles, blocs ponctuels, données invalides')
    pg = page(browser, 9, 0)
    pg.evaluate("""() => { const d = { real: { 'act:act-trajet-aller': { start: 390, end: 450 } }, ponctuels: [{ id: 'p1', name: 'Réunion test', mode: 'fixed', entry: 'duration', start: 600, duration: 60, confirm: false, carry: false, cat: null, alarm: null, parallel: false, toCal: false }], subtasks: {}, review: {}, profile: null, segs: {}, kidsDone: {}, presence: null, trip: null, removed: [] };
      localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: { '2026-11-03': d } })); }""")
    pg.reload()
    pg.click('[data-key="%s"]' % KEY)
    pg.click('#bp-remove')
    check('un bloc avec des heures réelles ne peut pas être retiré', removed(pg) == [] and 'Trajet aller' in blocks(pg), (removed(pg), blocks(pg)))
    check('le message dit quoi faire', 'Efface d’abord' in toast(pg), toast(pg))
    pg.click('#bp-clear')
    pg.click('[data-key="%s"]' % KEY)
    pg.click('#bp-remove')
    check('une fois les heures effacées, le retrait marche', removed(pg) == ['act-trajet-aller'] and 'Trajet aller' not in blocks(pg), (removed(pg), blocks(pg)))
    pg.click('[data-action=restore-act]')
    pg.click('[data-key="p:p1"]')
    check('un bloc ponctuel garde « Supprimer » et n’a pas « Retirer pour ce jour »', pg.locator('#bp-del').is_visible() and not pg.locator('#bp-remove').is_visible())
    pg.click('[data-bp=close]')
    pg.evaluate("() => localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: { '2026-11-03': { real: {}, ponctuels: [], subtasks: {}, review: {}, profile: null, segs: {}, kidsDone: {}, presence: null, trip: null, removed: [1, '', null, 'act-trajet-aller', 'act-trajet-aller', 'inconnue', {}] } } }))")
    pg.reload()
    pg.click('[data-key="act:act-trajet-retour"]')
    pg.click('#bp-remove')      # un enregistrement force l'écriture de la version nettoyée
    check('données invalides nettoyées : seuls les identifiants texte, sans doublon, sont gardés', removed(pg) == ['act-trajet-aller', 'inconnue', 'act-trajet-retour'], removed(pg))
    check('une activité inconnue retirée ne produit ni ligne ni erreur', 'inconnue' not in pg.inner_text('#day-head') and 'Trajet aller' not in blocks(pg), (blocks(pg), pg.inner_text('#day-head')[:200]))
    pg.evaluate("() => localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: { '2026-11-03': { real: {}, ponctuels: [], subtasks: {}, review: {}, profile: null, segs: {}, kidsDone: {}, presence: null, trip: null } } }))")
    pg.reload()
    check('un ancien jour sans champ « removed » s’ouvre normalement', 'Trajet aller' in blocks(pg), blocks(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_retrait_et_retablissement(browser)
        test_effets(browser)
        test_refus_et_limites(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
