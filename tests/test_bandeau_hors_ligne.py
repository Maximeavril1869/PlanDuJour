"""Tests : bannière « Hors ligne » (0.36.0, CONVENTIONS §55).

Réutilise le faux serveur Supabase de test_sync.py (aucun réseau réel, aucun vrai compte). Aucune donnée réelle : libellés et identifiants inventés.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_bandeau_hors_ligne.py
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check
from test_sync import DAY1, FauxSupabase, day_with, device, login, names, seed, sync, wait, wait_remote

TABS = ['day', 'recap', 'stats', 'settings']


def barre(pg):
    return pg.evaluate("""() => { const e = document.getElementById('offbar'), n = document.querySelector('.tabbar');
        const r = e.getBoundingClientRect(), nr = n.getBoundingClientRect(), s = document.querySelector('.savebar');
        const sr = s ? s.getBoundingClientRect() : null;
        return { hidden: e.hidden, shown: r.height > 0, bottom: r.bottom, top: r.top, navTop: nr.top, h: r.height, pe: getComputedStyle(e).pointerEvents, text: e.textContent,
                 saveBottom: sr && sr.height > 0 ? sr.bottom : null }; }""")


def test_bandeau(browser):
    print('Bannière « Hors ligne » (compte connecté)')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Avant coupure')})
    login(a)
    wait_remote(fake, lambda: ('jour:' + DAY1) in fake.rows)
    wait(a, "() => document.querySelector('#sync-status').textContent.startsWith('Synchronisé')")
    check('en ligne : pas de bannière', barre(a)['shown'] is False, barre(a))
    a.context.set_offline(True)
    check('réseau coupé : la bannière apparaît tout de suite', wait(a, "() => !document.getElementById('offbar').hidden", None, 3000))
    s = barre(a)
    check('elle dit « Hors ligne »', s['text'].startswith('Hors ligne'), s)
    check('elle est juste au-dessus des onglets', abs(s['bottom'] - s['navTop']) <= 1.5 and s['h'] >= 20, s)
    check('elle n’intercepte aucun toucher (pointer-events: none)', s['pe'] == 'none', s)
    for t in TABS:
        a.click('#tab-' + t)
        s = barre(a)
        check('onglet « %s » : bannière visible' % t, s['shown'] is True, s)
        if s['saveBottom'] is not None:
            check('onglet « %s » : la barre d’enregistrement est au-dessus de la bannière, sans la recouvrir' % t, s['saveBottom'] <= s['top'] + 1.5, s)
    a.click('#tab-day')
    # l'app reste utilisable : modification pendant la coupure
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Pendant coupure'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    check('hors ligne : la donnée locale est modifiable et gardée', names(a, DAY1) == ['Pendant coupure'])
    a.context.set_offline(False)
    sync(a)
    check('réseau revenu : la bannière disparaît après la synchronisation', wait(a, "() => document.getElementById('offbar').hidden", None, 9000), barre(a))
    check('la modification faite hors ligne est partie', wait_remote(fake, lambda: bool(fake.rows.get('jour:' + DAY1)) and fake.rows['jour:' + DAY1]['valeur'] is not None))
    # Wi-Fi sans internet : le navigateur se croit en ligne, le serveur ne répond pas
    fake.offline = True
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Panne serveur'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    sync(a)
    check('Wi-Fi sans internet : bannière après l’échec de la synchro', wait(a, "() => !document.getElementById('offbar').hidden", None, 6000))
    fake.offline = False
    sync(a)
    check('… et elle disparaît au retour', wait(a, "() => document.getElementById('offbar').hidden", None, 9000))
    check('aucune erreur JavaScript', not a.errors, a.errors)


def test_sans_compte(browser):
    print('Bannière « Hors ligne » : rien à signaler sans compte connecté')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Local seulement')})
    a.context.set_offline(True)
    a.wait_for_timeout(500)
    check('sans compte : pas de bannière (l’app est locale)', barre(a)['shown'] is False, barre(a))
    check('aucune erreur JavaScript', not a.errors, a.errors)


def test_deconnexion(browser):
    print('Bannière « Hors ligne » : se déconnecter la retire')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Avant coupure')})
    login(a)
    wait_remote(fake, lambda: ('jour:' + DAY1) in fake.rows)
    a.context.set_offline(True)
    wait(a, "() => !document.getElementById('offbar').hidden", None, 3000)
    a.click('[data-action=sync-logout]')
    check('déconnecté : la bannière disparaît', wait(a, "() => document.getElementById('offbar').hidden", None, 4000), barre(a))
    check('aucune erreur JavaScript', not a.errors, a.errors)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_bandeau(browser)
        test_sans_compte(browser)
        test_deconnexion(browser)
        browser.close()
    failed = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(failed)))
    for n in failed:
        print('  ECHEC : ' + n)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
