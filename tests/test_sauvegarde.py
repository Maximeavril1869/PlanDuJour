"""Tests : rappel de sauvegarde (0.25.0).

Un bandeau sur la page Jour apparaît quand des modifications ne sont pas sauvegardées depuis au moins N jours (réglable dans Réglages > Sauvegarde,
7 par défaut, 0 = jamais). L'état est propre à l'appareil (clé `plandujour.sauvegarde`) et n'entre pas dans l'export.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_sauvegarde.py
Aucune donnée réelle : libellés inventés.
"""
import json
import sys

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, check, day_offset, new_page, ponctuel, seed

KEY = 'plandujour.sauvegarde'


def stored(pg):
    raw = pg.evaluate("(k) => localStorage.getItem(k)", KEY)
    return json.loads(raw) if raw else None


def set_backup(pg, since=None, last=None, every=None, snooze=None):
    """Écrit l'état de sauvegarde (décalages en jours par rapport à aujourd'hui) puis recharge."""
    st = {}
    if since is not None:
        st['since'] = day_offset(pg, since)
    if last is not None:
        st['last'] = day_offset(pg, last)
    if every is not None:
        st['every'] = every
    if snooze is not None:
        st['snooze'] = day_offset(pg, snooze)
    pg.evaluate("([k, v]) => localStorage.setItem(k, JSON.stringify(v))", [KEY, st])
    pg.reload()


def banner(pg):
    return pg.locator('#backup-banner').count() == 1


def no_download(pg):
    """Sans feuille de partage (comme sur un ordinateur) : l'export passe par un téléchargement."""
    pg.evaluate("() => { Object.defineProperty(navigator, 'canShare', { value: undefined, configurable: true }); }")


def test_affichage(browser):
    print('Quand le bandeau apparaît')
    pg = new_page(browser)
    check('une app neuve : pas de bandeau', not banner(pg))
    pg.click('#tab-settings')
    info = pg.inner_text('#backup-info')
    check('Réglages : aucune sauvegarde, aucune modification', 'Aucune sauvegarde faite depuis cet appareil' in info and 'Aucune modification depuis la dernière sauvegarde' in info, info)
    check('le délai par défaut est de 7 jours', pg.input_value('#backup-every') == '7')
    pg.click('#tab-day')
    set_backup(pg, since=-8)
    check('modifications non sauvegardées depuis 8 jours (délai 7) : bandeau', banner(pg))
    txt = pg.inner_text('#backup-banner')
    check('le bandeau dit depuis combien de jours et qu’aucune sauvegarde n’existe', '8 jours' in txt and 'Aucune sauvegarde faite depuis cet appareil' in txt, txt)
    set_backup(pg, since=-8, last=-9)
    check('avec une sauvegarde passée, il la rappelle', 'Dernière sauvegarde' in pg.inner_text('#backup-banner'))
    set_backup(pg, since=-7)
    check('exactement 7 jours : bandeau', banner(pg))
    set_backup(pg, since=-6)
    check('6 jours : pas encore', not banner(pg))
    set_backup(pg, since=-3, every=3)
    check('délai de 3 jours, 3 jours écoulés : bandeau', banner(pg))
    set_backup(pg, since=-60, every=0)
    check('délai « jamais » : jamais de bandeau', not banner(pg))
    set_backup(pg, last=-40)
    check('aucune modification depuis une vieille sauvegarde : pas de bandeau', not banner(pg))
    set_backup(pg, since=-8, snooze=1)
    check('rappel reporté à demain : caché aujourd’hui', not banner(pg))
    set_backup(pg, since=-8, snooze=0)
    check('rappel reporté jusqu’à aujourd’hui : de retour', banner(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_donnees_invalides(browser):
    print('État illisible')
    pg = new_page(browser)
    for raw in ('{"since":"2026-13-45","last":"n’importe quoi","every":99,"snooze":5}', 'pas du json', '[]', 'null'):
        pg.evaluate("([k, v]) => localStorage.setItem(k, v)", [KEY, raw])
        pg.reload()
        pg.click('#tab-settings')
        check('« %s » : valeurs par défaut, pas de bandeau' % raw[:24], not banner(pg) and pg.input_value('#backup-every') == '7' and not pg.errors, pg.errors)
    pg.close()


def test_plus_tard(browser):
    print('Plus tard')
    pg = new_page(browser)
    set_backup(pg, since=-8)
    pg.click('[data-action=backup-later]')
    check('le bandeau disparaît', not banner(pg))
    check('le rappel est reporté à demain, les modifications restent signalées', stored(pg)['snooze'] == day_offset(pg, 1) and stored(pg)['since'] == day_offset(pg, -8), stored(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_export(browser):
    print('Exporter maintenant')
    pg = new_page(browser)
    set_backup(pg, since=-8)
    no_download(pg)
    with pg.expect_download() as dl:
        pg.click('[data-action=backup-now]')
    check('un fichier JSON est téléchargé', dl.value.suggested_filename.startswith('plandujour-') and dl.value.suggested_filename.endswith('.json'), dl.value.suggested_filename)
    st = stored(pg)
    check('dernière sauvegarde = aujourd’hui, plus de modification en attente', st['last'] == day_offset(pg, 0) and st['since'] is None, st)
    check('le bandeau disparaît', not banner(pg))
    pg.click('#tab-settings')
    info = pg.inner_text('#backup-info')
    check('Réglages : sauvegardé aujourd’hui, aucune modification depuis', 'aujourd’hui' in info and 'Aucune modification depuis la dernière sauvegarde' in info, info)
    exported = json.load(open(dl.value.path(), encoding='utf-8'))
    check('l’état de sauvegarde n’entre pas dans le fichier exporté', sorted(exported) == ['app', 'appVersion', 'days', 'exportedAt', 'format', 'settings'] and 'since' not in json.dumps(exported), sorted(exported))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_feuille_de_partage(browser):
    print('Feuille de partage (iPhone, iPad)')
    pg = new_page(browser)
    set_backup(pg, since=-8)
    pg.evaluate("() => { Object.defineProperty(navigator, 'canShare', { value: () => true, configurable: true }); navigator.share = () => Promise.reject(Object.assign(new Error('annulé'), { name: 'AbortError' })); }")
    pg.click('[data-action=backup-now]')
    pg.wait_for_timeout(300)
    check('annuler la feuille de partage ne compte pas comme une sauvegarde', banner(pg) and stored(pg)['since'] == day_offset(pg, -8) and stored(pg).get('last') is None, stored(pg))
    pg.evaluate("() => { navigator.share = () => Promise.resolve(); }")
    pg.click('[data-action=backup-now]')
    pg.wait_for_timeout(300)
    check('l’enregistrer dans Fichiers compte comme une sauvegarde', not banner(pg) and stored(pg)['last'] == day_offset(pg, 0) and stored(pg)['since'] is None, stored(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def test_modifications(browser):
    print('Ce qui compte comme une modification')
    pg = new_page(browser)
    check('ouvrir l’app ne marque rien', stored(pg) is None)
    pg.click('details[data-fid=card-pres] > summary')
    pg.click('[data-action=pres-in]')
    check('une saisie sur la page du jour marque la première modification', stored(pg) and stored(pg)['since'] == day_offset(pg, 0), stored(pg))
    pg.close()
    pg = new_page(browser)
    pg.click('#tab-settings')
    pg.click('details[data-fid=card-cats] > summary')
    pg.fill('[data-w=target]', '07:30')
    pg.click('#save-btn')
    check('enregistrer les réglages marque aussi la modification', stored(pg) and stored(pg)['since'] == day_offset(pg, 0), stored(pg))
    pg.close()
    pg = new_page(browser)
    set_backup(pg, since=-8)
    pg.click('details[data-fid=card-pres] > summary')
    pg.click('[data-action=pres-in]')
    check('une nouvelle modification ne repousse pas la date de la première', stored(pg)['since'] == day_offset(pg, -8), stored(pg))
    pg.close()
    pg = new_page(browser, seed('2026-10-01', ponctuel('idS', 'Bloc test', 600)))
    check('une app déjà utilisée avant la 0.25.0 : le compte commence à la première ouverture', stored(pg) and stored(pg)['since'] == day_offset(pg, 0) and stored(pg).get('last') is None, stored(pg))
    pg.close()
    pg = new_page(browser, seed('2026-10-01', ponctuel('idS', 'Bloc test', 600)))
    set_backup(pg, last=-2)
    check('mais pas si une sauvegarde a déjà été faite', stored(pg).get('since') is None and not banner(pg), stored(pg))
    pg.close()


def test_delai(browser):
    print('Régler le délai')
    pg = new_page(browser)
    set_backup(pg, since=-8)
    pg.click('#tab-settings')
    for value, expected in (('14', False), ('3', True), ('0', False), ('7', True)):
        pg.select_option('#backup-every', value)
        pg.click('#tab-day')
        check('délai %s : bandeau %s' % (value, 'affiché' if expected else 'caché'), banner(pg) == expected, banner(pg))
        pg.click('#tab-settings')
    check('le délai choisi est conservé', stored(pg)['every'] == 7)
    check('changer le délai n’exige pas « Enregistrer »', pg.inner_text('#dirty-msg') == 'Aucune modification')
    pg.reload()
    pg.click('#tab-settings')
    check('et il survit à la fermeture de l’app', pg.input_value('#backup-every') == '7')
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def import_file(pg, mode):
    payload = pg.evaluate("() => JSON.stringify({ app: 'plandujour', format: 1, settings: window.PDJ.defaultSettings(), days: { version: 2, days: {} } })")
    pg.click('#tab-settings')
    pg.set_input_files('#import-file', files=[{'name': 'test.json', 'mimeType': 'application/json', 'buffer': payload.encode('utf-8')}])
    pg.click('[data-action=%s]' % mode)


def test_import_et_reinitialisation(browser):
    print('Import et réinitialisation')
    pg = new_page(browser)
    set_backup(pg, since=-8)
    import_file(pg, 'imp-all')
    check('tout remplacer par un fichier : l’appareil est identique au fichier, plus de modification en attente', stored(pg)['since'] is None, stored(pg))
    pg.close()
    pg = new_page(browser)
    set_backup(pg, last=-3)
    import_file(pg, 'imp-settings')
    check('remplacer les réglages seulement : mes jours ne sont dans aucun fichier, modification en attente', stored(pg)['since'] == day_offset(pg, 0), stored(pg))
    pg.close()
    pg = new_page(browser)
    set_backup(pg, since=-8, last=-9, every=14)
    pg.click('#tab-settings')
    pg.evaluate("() => document.querySelector('[data-action=reset]').click()")
    pg.wait_for_selector('#reset-word')
    pg.fill('#reset-word', 'effacer')
    pg.click('[data-action=reset-go]')
    check('tout effacer : l’état de sauvegarde est effacé aussi', stored(pg) is None, stored(pg))
    check('et l’app vierge ne réclame rien', not banner(pg))
    pg.close()
    pg = new_page(browser)
    set_backup(pg, last=-2, every=14)
    pg.click('#tab-settings')
    pg.evaluate("() => document.querySelector('[data-action=reset]').click()")
    pg.wait_for_selector('#reset-word')
    pg.check('input[name=reset-mode][value=days]')
    pg.fill('#reset-word', 'EFFACER')
    pg.click('[data-action=reset-go]')
    check('effacer les jours : modification en attente, délai conservé', stored(pg)['since'] == day_offset(pg, 0) and stored(pg)['every'] == 14, stored(pg))
    check('aucune erreur JavaScript', not pg.errors, pg.errors)
    pg.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_affichage(browser)
        test_donnees_invalides(browser)
        test_plus_tard(browser)
        test_export(browser)
        test_feuille_de_partage(browser)
        test_modifications(browser)
        test_delai(browser)
        test_import_et_reinitialisation(browser)
        browser.close()
    bad = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
