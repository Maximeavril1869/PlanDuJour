"""Tests : départ et retour de chez soi, et lignes de repère sur la frise et dans le Récap (0.32.0).

Deux boutons « Je pars de chez moi » / « Je rentre chez moi » (heure du moment, aujourd'hui) et deux champs pour corriger.
Les lignes viennent de heures réellement enregistrées : départ de chez soi, arrivée au travail (présence), début et fin de pause,
départ du travail (présence), retour chez soi. Frise du Jour et Récap (semaine réelle) ; rien n'est prévu à l'avance.
L'heure est simulée (horloge du navigateur). Aucune donnée réelle.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_reperes.py
"""
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, stored_days

MARDI = datetime(2026, 11, 3)


def page(browser, h, m=0, day=MARDI):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.clock.install(time=day.replace(hour=h, minute=m))
    pg.goto(URL)
    return pg


def at(pg, h, m, day=MARDI):
    pg.clock.set_system_time(day.replace(hour=h, minute=m))


def open_card(pg, fid):
    if pg.locator('details[data-fid=%s]' % fid).get_attribute('open') is None:
        pg.click('details[data-fid=%s] > summary' % fid)


def frise(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#day-timeline .marker.mk-day span')].map((s) => s.textContent.trim())")


def recap_marks(pg):
    pg.click('#tab-recap')
    return pg.evaluate("() => [...document.querySelectorAll('#panel-recap li.mark .what')].map((s) => s.textContent.trim())")


def trip(pg, date=None):
    d = stored_days(pg).get(date or '2026-11-03', {})
    return d.get('trip')


def test_boutons(browser):
    print('Boutons Je pars / Je rentre')
    pg = page(browser, 7, 0)
    check('la carte « Départ et retour » existe et est fermée au départ', pg.locator('details[data-fid=card-trip]').count() == 1 and pg.locator('details[data-fid=card-trip]').get_attribute('open') is None)
    open_card(pg, 'card-trip')
    check('les deux boutons sont là (aujourd’hui)', pg.locator('[data-action=trip-leave]').count() == 1 and pg.locator('[data-action=trip-home]').count() == 1)
    check('rien sur la frise avant le moindre enregistrement', frise(pg) == [], frise(pg))
    pg.click('[data-action=trip-leave]')
    check('« Je pars » enregistre l’heure du moment (07:00 = 420)', trip(pg) == {'leave': 420, 'home': None}, trip(pg))
    check('la ligne « Départ de chez moi 07:00 » apparaît sur la frise', frise(pg) == ['Départ de chez moi 07:00'], frise(pg))
    open_card(pg, 'card-trip')
    check('la carte reste dépliée après l’action et le bouton « Je pars » disparaît', pg.locator('[data-action=trip-leave]').count() == 0 and pg.locator('[data-action=trip-home]').count() == 1)
    at(pg, 16, 30)
    pg.click('[data-action=trip-home]')
    check('« Je rentre » enregistre 16:30 (990)', trip(pg) == {'leave': 420, 'home': 990}, trip(pg))
    check('les deux lignes sont sur la frise, dans l’ordre', frise(pg) == ['Départ de chez moi 07:00', 'Retour chez moi 16:30'], frise(pg))
    check('plus aucun bouton une fois les deux heures prises', pg.locator('[data-action=trip-leave]').count() == 0 and pg.locator('[data-action=trip-home]').count() == 0)
    pg.reload()
    check('les lignes survivent au rechargement', frise(pg) == ['Départ de chez moi 07:00', 'Retour chez moi 16:30'], frise(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_presence_en_lignes(browser):
    print('Présence au travail : arrivée, pauses, départ en lignes')
    pg = page(browser, 7, 0)
    open_card(pg, 'card-trip')
    pg.click('[data-action=trip-leave]')
    at(pg, 7, 30)
    open_card(pg, 'card-pres')
    pg.click('[data-action=pres-in]')
    check('l’arrivée au travail devient une ligne', 'Arrivée au travail 07:30' in frise(pg), frise(pg))
    check('une présence encore ouverte n’a pas de ligne de départ', not any('Départ du travail' in x for x in frise(pg)), frise(pg))
    at(pg, 12, 0)
    pg.click('[data-action=pres-pause]')
    check('une pause ouverte donne seulement « Début de pause »', 'Début de pause 12:00' in frise(pg) and not any('Fin de pause' in x for x in frise(pg)), frise(pg))
    at(pg, 12, 30)
    pg.click('[data-action=pres-resume]')
    at(pg, 16, 0)
    pg.click('[data-action=pres-out]')
    at(pg, 16, 30)
    open_card(pg, 'card-trip')
    pg.click('[data-action=trip-home]')
    attendu = ['Départ de chez moi 07:00', 'Arrivée au travail 07:30', 'Début de pause 12:00', 'Fin de pause 12:30', 'Départ du travail 16:00', 'Retour chez moi 16:30']
    check('la journée complète : six lignes, triées par heure', frise(pg) == attendu, frise(pg))
    rm = recap_marks(pg)
    check('le Récap (semaine réelle) montre les mêmes six lignes', [x for x in rm if x in [a[:-6] for a in attendu]] == [a[:-6] for a in attendu], rm)
    check('les lignes du Récap portent l’heure', pg.evaluate("() => [...document.querySelectorAll('#panel-recap li.mark .t')].map((s) => s.textContent.trim())").count('07:30') == 1)
    pg.click('[data-recap-mode=type]')
    check('en semaine type, aucune ligne de repère (rien n’est prévu)', not any(x in [a[:-6] for a in attendu] for x in [s for s in pg.evaluate("() => [...document.querySelectorAll('#panel-recap li.mark .what')].map((s) => s.textContent.trim())")]))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_correction(browser):
    print('Correction à la main')
    pg = page(browser, 8, 0)
    open_card(pg, 'card-trip')
    pg.fill('[data-trip=leave]', '0650'); pg.dispatch_event('[data-trip=leave]', 'change')
    check('un départ saisi à la main (0650 → 06:50 = 410) est enregistré et dessiné', trip(pg) == {'leave': 410, 'home': None} and frise(pg) == ['Départ de chez moi 06:50'], (trip(pg), frise(pg)))
    open_card(pg, 'card-trip')
    pg.fill('[data-trip=home]', '1715'); pg.dispatch_event('[data-trip=home]', 'change')
    check('un retour saisi à la main (17:15 = 1035)', trip(pg) == {'leave': 410, 'home': 1035}, trip(pg))
    open_card(pg, 'card-trip')
    pg.fill('[data-trip=home]', '0600'); pg.dispatch_event('[data-trip=home]', 'change')
    check('un retour avant le départ est refusé, rien ne change', trip(pg) == {'leave': 410, 'home': 1035}, trip(pg))
    open_card(pg, 'card-trip')
    pg.fill('[data-trip=leave]', '2599'); pg.dispatch_event('[data-trip=leave]', 'change')
    check('une heure invalide est refusée, rien ne change', trip(pg) == {'leave': 410, 'home': 1035}, trip(pg))
    open_card(pg, 'card-trip')
    pg.fill('[data-trip=leave]', ''); pg.dispatch_event('[data-trip=leave]', 'change')
    check('un champ vidé retire la ligne (le retour reste)', trip(pg) == {'leave': None, 'home': 1035} and frise(pg) == ['Retour chez moi 17:15'], (trip(pg), frise(pg)))
    open_card(pg, 'card-trip')
    pg.fill('[data-trip=home]', ''); pg.dispatch_event('[data-trip=home]', 'change')
    check('les deux champs vides : plus rien d’enregistré pour le jour', trip(pg) is None and frise(pg) == [], (trip(pg), frise(pg)))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_jour_passe(browser):
    print('Jour passé et lecture de données')
    pg = page(browser, 9, 0)
    pg.evaluate("""() => { const d = (t, pr) => ({ real: {}, ponctuels: [], subtasks: {}, review: {}, profile: null, segs: {}, presence: pr, kidsDone: {}, trip: t });
      localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: {
        '2026-11-02': d({ leave: 400, home: 1000 }, { start: 450, end: 960, pauses: [{ start: 720, end: 750 }] }),
        '2026-11-01': d({ leave: 1000, home: 500 }, null),
        '2026-10-31': d('n’importe quoi', null) } })); }""")
    pg.reload()
    d = stored_days(pg)
    check('les données valides sont relues', d['2026-11-02'].get('trip') == {'leave': 400, 'home': 1000}, d['2026-11-02'].get('trip'))
    pg.click('#tab-recap')
    pg.click('[data-recap-date="2026-11-02"]')
    rm = pg.evaluate("() => [...document.querySelectorAll('#panel-recap li.mark .what')].map((s) => s.textContent.trim())")
    check('le Récap d’un jour passé montre ses six lignes', [x for x in rm if x != 'Lever' and x != 'Coucher'] == ['Départ de chez moi', 'Arrivée au travail', 'Début de pause', 'Fin de pause', 'Départ du travail', 'Retour chez moi'], rm)
    r = pg.evaluate("() => [window.PDJ.cleanTrip({ leave: 600, home: 500 }), window.PDJ.cleanTrip({ leave: null, home: null }), window.PDJ.cleanTrip({}), window.PDJ.cleanTrip('x'), window.PDJ.cleanTrip({ leave: 'a', home: 700 })]")
    check('cleanTrip : retour avant le départ écarté, rien → null, valeurs invalides ignorées', r == [{'leave': 600, 'home': None}, None, None, None, {'leave': None, 'home': 700}], r)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_frise(browser):
    print('Frise : plage et lisibilité')
    pg = page(browser, 7, 0)
    open_card(pg, 'card-trip')
    pg.click('[data-action=trip-leave]')
    at(pg, 7, 5)
    open_card(pg, 'card-pres')
    pg.click('[data-action=pres-in]')
    box = pg.evaluate("() => { const a = document.querySelector('#day-timeline .tlarea').getBoundingClientRect(); return [a.top, a.bottom, [...document.querySelectorAll('#day-timeline .marker.mk-day span')].map((s) => { const r = s.getBoundingClientRect(); return [r.top, r.bottom]; })]; }")
    top, bottom, spans = box
    check('les lignes sont dans la zone de la frise, même sans lever ni coucher', all(top - 1 <= a and b <= bottom + 20 for a, b in spans), box)
    check('deux repères à 5 minutes d’écart : les libellés ne se chevauchent pas', len(spans) == 2 and spans[0][1] <= spans[1][0] + 0.5, spans)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_boutons(browser)
        test_presence_en_lignes(browser)
        test_correction(browser)
        test_jour_passe(browser)
        test_frise(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
