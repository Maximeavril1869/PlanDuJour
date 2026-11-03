"""Tests : demande de stockage persistant (0.25.2).

Au démarrage, l'app demande `navigator.storage.persist()` et affiche le résultat dans Réglages > Sauvegarde.
Le navigateur est simulé (aucune réponse réelle du système) : accordé, déjà accordé, refusé, en erreur, interface absente.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_stockage.py
Aucune donnée réelle.
"""
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check

STUBS = {
    'accordé': "window.__calls = { persist: 0, persisted: 0 }; Object.defineProperty(navigator, 'storage', { configurable: true, value: { persisted: () => { window.__calls.persisted++; return Promise.resolve(false); }, persist: () => { window.__calls.persist++; return Promise.resolve(true); } } });",
    'déjà accordé': "window.__calls = { persist: 0, persisted: 0 }; Object.defineProperty(navigator, 'storage', { configurable: true, value: { persisted: () => { window.__calls.persisted++; return Promise.resolve(true); }, persist: () => { window.__calls.persist++; return Promise.resolve(true); } } });",
    'refusé': "window.__calls = { persist: 0, persisted: 0 }; Object.defineProperty(navigator, 'storage', { configurable: true, value: { persisted: () => Promise.resolve(false), persist: () => { window.__calls.persist++; return Promise.resolve(false); } } });",
    'en erreur': "window.__calls = { persist: 0, persisted: 0 }; Object.defineProperty(navigator, 'storage', { configurable: true, value: { persisted: () => Promise.resolve(false), persist: () => Promise.reject(new Error('refus du système')) } });",
    'absent': "Object.defineProperty(navigator, 'storage', { configurable: true, value: undefined });",
}


def open_page(browser, stub):
    pg = browser.new_page(viewport={'width': 390, 'height': 844})
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.add_init_script(stub)
    pg.goto(URL)
    pg.click('#tab-settings')
    pg.wait_for_function("() => !document.querySelector('#persist-info').textContent.includes('vérification')", timeout=3000)
    return pg


def info(pg):
    return pg.inner_text('#persist-info')


def test_accorde(browser):
    print('Demande accordée')
    pg = open_page(browser, STUBS['accordé'])
    check('l’état affiché est « accordée »', 'accordée' in info(pg) and 'non accordée' not in info(pg), info(pg))
    check('la demande est faite une seule fois, au démarrage, sans action de l’utilisateur', pg.evaluate("() => window.__calls") == {'persist': 1, 'persisted': 1}, pg.evaluate("() => window.__calls"))
    pg.click('details[data-fid=card-cats] > summary')
    pg.fill('[data-w=target]', '07:30')
    pg.click('#save-btn')
    check('l’état affiché survit à un enregistrement de Réglages, sans nouvelle demande', 'accordée' in info(pg) and pg.evaluate("() => window.__calls.persist") == 1, (info(pg), pg.evaluate("() => window.__calls")))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_deja_accorde(browser):
    print('Déjà accordée')
    pg = open_page(browser, STUBS['déjà accordé'])
    check('affichée « accordée » sans redemander', 'accordée' in info(pg) and pg.evaluate("() => window.__calls") == {'persist': 0, 'persisted': 1}, (info(pg), pg.evaluate("() => window.__calls")))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_refuse(browser):
    print('Demande refusée')
    pg = open_page(browser, STUBS['refusé'])
    check('l’état affiché est « non accordée » avec le conseil d’exporter', 'non accordée' in info(pg) and 'exporte régulièrement' in info(pg), info(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_erreur_et_absence(browser):
    print('Erreur ou interface absente')
    for name in ('en erreur', 'absent'):
        pg = open_page(browser, STUBS[name])
        check('« %s » : « non disponible », l’app fonctionne' % name, 'non disponible' in info(pg) and pg.locator('#backup-info').count() == 1, info(pg))
        check('« %s » : aucune erreur JavaScript (pas de rejet non géré)' % name, not pg.errors, pg.errors)
        pg.click('#tab-day')
        check('« %s » : la page du jour s’affiche' % name, pg.locator('#day-search').count() == 1)
        pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_accorde(browser)
        test_deja_accorde(browser)
        test_refuse(browser)
        test_erreur_et_absence(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
