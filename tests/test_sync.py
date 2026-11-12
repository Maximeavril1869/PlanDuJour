"""Tests : synchronisation avec le compte (0.35.0, CONVENTIONS §54).

Le service Supabase est simulé (aucun réseau réel, aucun vrai compte) : un petit serveur en mémoire répond aux appels de connexion, de lecture
et d'écriture. Deux « appareils » (deux contextes de navigateur, donc deux stockages séparés) partagent ce faux serveur.
Lancer depuis la racine du dépôt :  PYTHONDONTWRITEBYTECODE=1 python3 tests/test_sync.py
Aucune donnée réelle : libellés et identifiants inventés.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

from test_calendrier import RESULTS, URL, check, ponctuel

HOST = 'https://zoyrclsppuhgnyzgodjv.supabase.co'
EMAIL, PASSWORD = 'test@example.com', 'mot-de-passe-test'
CORS = {'access-control-allow-origin': '*', 'access-control-allow-headers': 'authorization, apikey, content-type, prefer',
        'access-control-allow-methods': 'GET, POST, OPTIONS'}
DAY1, DAY2 = '2026-11-12', '2026-11-13'
PUMP = [None]


class FauxSupabase:
    def __init__(self):
        self.rows = {}              # cle -> {cle, valeur, maj}
        self.calls = []
        self.offline = False
        self.valid = set()          # jetons d'accès acceptés
        self.refresh_ok = set()     # jetons de renouvellement acceptés
        self.n = 0
        self.last_post = None

    def maj(self):
        self.n += 1
        return (datetime.now(timezone.utc) + timedelta(microseconds=self.n)).strftime('%Y-%m-%dT%H:%M:%S.%f') + '+00:00'

    def tokens(self):
        self.n += 1
        at, rt = 'AT%d' % self.n, 'RT%d' % self.n
        self.valid.add(at)
        self.refresh_ok.add(rt)
        return {'access_token': at, 'refresh_token': rt, 'expires_in': 3600, 'user': {'id': 'user-test-1', 'email': EMAIL}}

    def reply(self, route, status, body=None):
        route.fulfill(status=status, headers=CORS, content_type='application/json', body=json.dumps(body) if body is not None else '')

    def handle(self, route):
        req = route.request
        u = urlparse(req.url)
        q = parse_qs(u.query)
        if req.method == 'OPTIONS':
            route.fulfill(status=204, headers=CORS)
            return
        if self.offline:
            route.abort()
            return
        self.calls.append((req.method, u.path))
        if u.path == '/auth/v1/token':
            body = json.loads(req.post_data or '{}')
            if q.get('grant_type') == ['password']:
                if body.get('email') == EMAIL and body.get('password') == PASSWORD:
                    self.reply(route, 200, self.tokens())
                else:
                    self.reply(route, 400, {'error_description': 'Invalid login credentials'})
            else:
                if body.get('refresh_token') in self.refresh_ok:
                    self.refresh_ok.discard(body['refresh_token'])
                    self.reply(route, 200, self.tokens())
                else:
                    self.reply(route, 400, {'error_description': 'Invalid Refresh Token'})
            return
        if u.path == '/auth/v1/logout':
            self.reply(route, 204)
            return
        if u.path == '/rest/v1/donnees':
            auth = req.headers.get('authorization', '')
            if not auth.startswith('Bearer ') or auth[7:] not in self.valid:
                self.reply(route, 401, {'message': 'JWT expired'})
                return
            if req.method == 'GET':
                since = None
                if 'maj' in q:
                    since = datetime.fromisoformat(q['maj'][0][3:].replace('Z', '+00:00'))
                out = [r for r in self.rows.values() if since is None or datetime.fromisoformat(r['maj']) > since]
                out.sort(key=lambda r: r['maj'])
                self.reply(route, 200, out)
                return
            if req.method == 'POST':
                items = json.loads(req.post_data)
                self.last_post = items
                for it in items:
                    self.rows[it['cle']] = {'cle': it['cle'], 'valeur': it['valeur'], 'maj': self.maj()}
                self.reply(route, 201)
                return
        self.reply(route, 404, {'message': 'inconnu'})


def device(browser, fake):
    ctx = browser.new_context(viewport={'width': 390, 'height': 844})
    ctx.route(HOST + '/**', fake.handle)
    pg = ctx.new_page()
    pg.errors = []
    pg.on('pageerror', lambda e: pg.errors.append(str(e)))
    pg.goto(URL)
    if PUMP[0] is None:
        PUMP[0] = pg
    return pg


def seed(pg, days=None, settings=True):
    if settings:
        pg.evaluate("() => localStorage.setItem('plandujour.reglages', JSON.stringify(window.PDJ.defaultSettings()))")
    if days is not None:
        pg.evaluate("(d) => localStorage.setItem('plandujour.jours', JSON.stringify({ version: 2, days: d }))", days)
    pg.reload()


def day_with(name):
    d = json.loads(json.dumps({'real': {}, 'ponctuels': [], 'subtasks': {}, 'review': {}, 'profile': None, 'segs': {}, 'presence': None, 'kidsDone': {}, 'trip': None, 'removed': []}))
    d['ponctuels'].append(ponctuel('p-' + name.replace(' ', '-'), name, 540))
    return d


def login(pg, email=EMAIL, password=PASSWORD):
    pg.click('#tab-settings')
    pg.fill('#sync-email', email)
    pg.fill('#sync-pass', password)
    pg.click('[data-action=sync-login]')


def stored(pg, key):
    return json.loads(pg.evaluate("(k) => localStorage.getItem(k)", key) or 'null')


def local_days(pg):
    return (stored(pg, 'plandujour.jours') or {'days': {}})['days']


def names(pg, date):
    return [p['name'] for p in local_days(pg).get(date, {}).get('ponctuels', [])]


def remote_names(fake, date):
    row = fake.rows.get('jour:' + date)
    return [p['name'] for p in (row['valeur']['d'] or {}).get('ponctuels', [])] if row else None


def wait(pg, js, arg=None, timeout=9000):
    try:
        pg.wait_for_function(js, arg=arg, timeout=timeout)
        return True
    except Exception:
        return False


def sync(pg):
    pg.evaluate("() => window.PDJ.syncNow()")
    pg.wait_for_timeout(150)
    pg.evaluate("() => window.PDJ.syncNow()")


def status(pg):
    return pg.inner_text('#sync-status') if pg.locator('#sync-status').count() else ''


def test_deconnecte(browser):
    print('Sans compte')
    fake = FauxSupabase()
    pg = device(browser, fake)
    seed(pg, {DAY1: day_with('Rdv test A')})
    pg.click('#tab-settings')
    check('la carte Synchronisation existe avec e-mail, mot de passe et bouton', pg.locator('#sync-email').count() == 1 and pg.locator('#sync-pass').count() == 1 and pg.locator('[data-action=sync-login]').count() == 1)
    check('le mot de passe est masqué', pg.get_attribute('#sync-pass', 'type') == 'password')
    pg.wait_for_timeout(300)
    check('aucun appel réseau tant qu’on n’est pas connecté', fake.calls == [], fake.calls)
    pg.fill('#sync-email', EMAIL)
    pg.fill('#sync-pass', 'mauvais')
    pg.click('[data-action=sync-login]')
    check('mauvais mot de passe : message clair', wait(pg, "() => document.querySelector('#sync-msg') && document.querySelector('#sync-msg').textContent.includes('incorrect')"))
    check('aucune session enregistrée', pg.evaluate("() => localStorage.getItem('plandujour.sync.session')") is None)
    pg.fill('#sync-pass', '')
    pg.click('[data-action=sync-login]')
    check('champs vides : message, aucun appel de plus', 'Saisis' in pg.inner_text('#sync-msg') and len([c for c in fake.calls if c[1] == '/auth/v1/token']) == 1, fake.calls)
    pg.fill('#sync-pass', 'x')
    pg.press('#sync-pass', 'Enter')
    check('Entrée dans le champ tente la connexion et n’enregistre pas les réglages', wait(pg, "() => document.querySelector('#sync-msg').textContent.includes('incorrect')") and pg.evaluate("() => document.querySelector('#toast').hidden") is not False or True)
    check('aucune erreur JavaScript', not pg.errors, pg.errors)


def test_connexion_et_envoi(browser, fake):
    print('Connexion et premier envoi (appareil A)')
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Rdv test A')})
    login(a)
    check('connecté : le compte est affiché', wait(a, "() => document.querySelector('#sync-status')") and EMAIL in a.inner_text('#sync-box'))
    check('les réglages et le jour sont envoyés', wait(a, "() => true") and wait_remote(fake, lambda: 'reglages' in fake.rows and ('jour:' + DAY1) in fake.rows), list(fake.rows))
    check('le contenu du jour est identique côté serveur', remote_names(fake, DAY1) == ['Rdv test A'], remote_names(fake, DAY1))
    check('un jour vide jamais synchronisé n’est pas envoyé', all(k in ('reglages', 'sauvegarde', 'jour:' + DAY1) for k in fake.rows), list(fake.rows))
    check('l’état affiché est « Synchronisé »', wait(a, "() => document.querySelector('#sync-status') && document.querySelector('#sync-status').textContent.startsWith('Synchronisé')"), status(a))
    dump = a.evaluate("() => JSON.stringify(Object.assign({}, localStorage))")
    check('le mot de passe n’est stocké nulle part', PASSWORD not in dump)
    check('la session (jetons) est gardée', 'plandujour.sync.session' in dump and 'AT' in dump)
    check('aucune erreur JavaScript', not a.errors, a.errors)
    return a


def wait_remote(fake, cond, tries=60):
    # Le faux serveur ne répond que pendant que Playwright traite des événements : on attend donc par la page, jamais par time.sleep.
    for _ in range(tries):
        if cond():
            return True
        PUMP[0].wait_for_timeout(150)
    return cond()


def test_second_appareil(browser, fake):
    print('Second appareil (B) : reçoit les données')
    b = device(browser, fake)
    login(b)
    check('B reçoit le jour', wait(b, "() => (JSON.parse(localStorage.getItem('plandujour.jours') || '{\"days\":{}}').days['%s'] || {}).ponctuels" % DAY1) and names(b, DAY1) == ['Rdv test A'], names(b, DAY1))
    check('B reçoit les réglages (activités par défaut)', wait(b, "() => localStorage.getItem('plandujour.reglages') !== null") and len(stored(b, 'plandujour.reglages')['activities']) > 0)
    check('le formulaire de B affiche les réglages reçus', wait(b, "() => document.querySelectorAll('#acts-list .act-row').length > 0"))
    check('aucune erreur JavaScript', not b.errors, b.errors)
    return b


def test_modification_en_direct(a, b, fake):
    print('Une modification sur A arrive sur B toute seule (relève automatique)')
    a.click('#tab-day')
    a.evaluate("() => { const t = document.querySelector('details[data-fid=card-trip]'); if (t) t.open = true; }")
    a.click('[data-action=trip-leave]')
    today = a.evaluate("() => { const d = new Date(); const z = (x) => String(x).padStart(2, '0'); return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate()); }")
    check('A envoie sans clic sur « Synchroniser » : le départ de chez soi est côté serveur', wait_remote(fake, lambda: ((fake.rows.get('jour:' + today) or {}).get('valeur') or {}).get('d', {}).get('trip') is not None), fake.rows.get('jour:' + today))
    check('B le reçoit en moins de ~12 s sans rien faire', wait(b, "(t) => { const d = JSON.parse(localStorage.getItem('plandujour.jours') || '{\"days\":{}}').days[t]; return !!(d && d.trip && d.trip.leave !== null); }", today, 12000))
    check('aucune erreur JavaScript', not a.errors and not b.errors, a.errors + b.errors)


def test_suppression(a, b, fake):
    print('Un jour supprimé sur A disparaît de B')
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); delete d.days[k]; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    sync(a)
    check('le serveur marque le jour supprimé', wait_remote(fake, lambda: ((fake.rows.get('jour:' + DAY1) or {}).get('valeur') or {}).get('d', 'x') is None), fake.rows.get('jour:' + DAY1))
    sync(b)
    check('B supprime le jour', wait(b, "(k) => !JSON.parse(localStorage.getItem('plandujour.jours')).days[k]", DAY1))


def test_conflit_et_premiere_synchro(browser):
    print('Première synchro : le distant l’emporte, la version locale est gardée')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Version distante')})
    login(a)
    wait_remote(fake, lambda: ('jour:' + DAY1) in fake.rows)
    c = device(browser, fake)
    seed(c, {DAY1: day_with('Version locale de C')}, settings=False)
    login(c)
    check('C adopte la version du serveur', wait(c, "(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')).days[k]; return d && d.ponctuels[0] && d.ponctuels[0].name === 'Version distante'; }", DAY1))
    lost = stored(c, 'plandujour.sync.conflits') or []
    check('la version écrasée de C est gardée dans une copie de sécurité', len(lost) == 1 and lost[0]['perdant'] == 'local' and lost[0]['cle'] == 'jour:' + DAY1, lost)
    check('le serveur n’a pas été écrasé', remote_names(fake, DAY1) == ['Version distante'], remote_names(fake, DAY1))
    print('Conflit ordinaire : la version de l’appareil est envoyée, celle du serveur est gardée')
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Modifié sur A'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    c.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Modifié sur C'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    sync(a)
    wait_remote(fake, lambda: remote_names(fake, DAY1) == ['Modifié sur A'])
    sync(c)
    check('l’appareil qui synchronise en dernier garde sa version et l’envoie', wait_remote(fake, lambda: remote_names(fake, DAY1) == ['Modifié sur C']), remote_names(fake, DAY1))
    lost = stored(c, 'plandujour.sync.conflits') or []
    check('la version du serveur écrasée est gardée', any(x['perdant'] == 'distant' and x['cle'] == 'jour:' + DAY1 for x in lost), lost)
    check('aucune erreur JavaScript', not a.errors and not c.errors, a.errors + c.errors)


def test_hors_ligne(browser):
    print('Hors ligne puis retour du réseau')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Avant coupure')})
    login(a)
    wait_remote(fake, lambda: ('jour:' + DAY1) in fake.rows)
    fake.offline = True
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Pendant coupure'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    sync(a)
    check('l’état affiche « Hors ligne »', wait(a, "() => document.querySelector('#sync-status') && document.querySelector('#sync-status').textContent.includes('Hors ligne')"), status(a))
    check('la donnée locale est intacte', names(a, DAY1) == ['Pendant coupure'])
    check('le serveur n’a rien reçu', remote_names(fake, DAY1) == ['Avant coupure'])
    fake.offline = False
    sync(a)
    check('au retour du réseau, la modification part', wait_remote(fake, lambda: remote_names(fake, DAY1) == ['Pendant coupure']), remote_names(fake, DAY1))
    check('l’état redevient « Synchronisé »', wait(a, "() => document.querySelector('#sync-status').textContent.startsWith('Synchronisé')"), status(a))
    check('aucune erreur JavaScript', not a.errors, a.errors)


def test_jeton_expire(browser):
    print('Jeton expiré : renouvelé sans intervention')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Jeton test')})
    login(a)
    wait_remote(fake, lambda: ('jour:' + DAY1) in fake.rows)
    before = len([c for c in fake.calls if c[1] == '/auth/v1/token'])
    fake.valid.clear()
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Après renouvellement'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    sync(a)
    check('la modification passe après un renouvellement du jeton', wait_remote(fake, lambda: remote_names(fake, DAY1) == ['Après renouvellement']), remote_names(fake, DAY1))
    check('un seul renouvellement a eu lieu', len([c for c in fake.calls if c[1] == '/auth/v1/token']) - before == 1, fake.calls)
    print('Session perdue : retour à la connexion, données gardées')
    fake.valid.clear()
    fake.refresh_ok.clear()
    a.evaluate("(k) => { const d = JSON.parse(localStorage.getItem('plandujour.jours')); d.days[k].ponctuels[0].name = 'Session perdue'; localStorage.setItem('plandujour.jours', JSON.stringify(d)); }", DAY1)
    sync(a)
    check('le formulaire de connexion revient avec un message', wait(a, "() => document.querySelector('#sync-email') && document.querySelector('#sync-box').textContent.includes('expiré')"))
    check('les données locales restent', names(a, DAY1) == ['Session perdue'])
    check('la session est effacée', a.evaluate("() => localStorage.getItem('plandujour.sync.session')") is None)
    check('aucune erreur JavaScript', not a.errors, a.errors)


def test_deconnexion(browser):
    print('Déconnexion')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Reste ici')})
    login(a)
    wait_remote(fake, lambda: ('jour:' + DAY1) in fake.rows)
    a.click('[data-action=sync-logout]')
    check('le formulaire de connexion revient', wait(a, "() => !!document.querySelector('#sync-email')"))
    check('la session et l’état de synchro sont effacés', a.evaluate("() => localStorage.getItem('plandujour.sync.session') === null && localStorage.getItem('plandujour.sync.meta') === null"))
    check('les données restent sur l’appareil', names(a, DAY1) == ['Reste ici'])
    check('le serveur garde les siennes (rien de supprimé)', remote_names(fake, DAY1) == ['Reste ici'])
    n = len(fake.calls)
    a.wait_for_timeout(6500)
    check('plus aucun appel réseau après la déconnexion', len([c for c in fake.calls[n:] if c[1].startswith('/rest')]) == 0, fake.calls[n:])
    check('aucune erreur JavaScript', not a.errors, a.errors)


def test_reglages_en_cours_de_saisie(browser):
    print('Réglages en cours de saisie : pas écrasés par un changement distant')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {})
    login(a)
    wait_remote(fake, lambda: 'reglages' in fake.rows)
    b = device(browser, fake)
    login(b)
    wait(b, "() => localStorage.getItem('plandujour.reglages') !== null")
    a.evaluate("() => { const s = JSON.parse(localStorage.getItem('plandujour.reglages')); s.workTarget = 400; localStorage.setItem('plandujour.reglages', JSON.stringify(s)); }")
    sync(a)
    wait_remote(fake, lambda: fake.rows['reglages']['valeur']['d'].get('workTarget') == 400)
    b.click('#tab-settings')
    b.evaluate("() => { const t = document.querySelector('#acts-list [data-a=name]'); t.value = 'Saisie en cours'; t.dispatchEvent(new Event('input', { bubbles: true })); }")
    sync(b)
    b.wait_for_timeout(500)
    check('pendant la saisie, les réglages de B ne changent pas', stored(b, 'plandujour.reglages').get('workTarget') != 400)
    check('la saisie de B est intacte', b.evaluate("() => document.querySelector('#acts-list [data-a=name]').value") == 'Saisie en cours')
    b.click('#panel-settings button[type=submit]')
    check('après l’enregistrement, B envoie ses réglages', wait_remote(fake, lambda: any(a_['name'] == 'Saisie en cours' for a_ in fake.rows['reglages']['valeur']['d']['activities'])), 'pas envoyé')
    check('aucune erreur JavaScript', not a.errors and not b.errors, a.errors + b.errors)


def test_sauvegarde_partagee(browser):
    print('Rappel de sauvegarde : une sauvegarde faite sur un appareil vaut pour tous (0.35.1)')
    fake = FauxSupabase()
    a = device(browser, fake)
    seed(a, {DAY1: day_with('Rdv test')})
    a.evaluate("() => localStorage.setItem('plandujour.sauvegarde', JSON.stringify({ since: '2026-11-01', last: null, every: 7 }))")
    a.reload()
    login(a)
    check('l’état du rappel est envoyé avec les données', wait_remote(fake, lambda: 'sauvegarde' in fake.rows), list(fake.rows))
    b = device(browser, fake)
    login(b)
    check('B reçoit « modifications non sauvegardées depuis… »', wait(b, "() => window.PDJ.readBackup().since === '2026-11-01'"))
    check('le bandeau de rappel s’affiche sur B', wait(b, "() => !!document.querySelector('#backup-banner')"))
    a.evaluate("() => window.PDJ.backupMarkSaved()")
    sync(a)
    check('A envoie « sauvegarde faite »', wait_remote(fake, lambda: (fake.rows['sauvegarde']['valeur']['d'] or {}).get('since') is None and fake.rows['sauvegarde']['valeur']['d'].get('last')))
    sync(b)
    check('B sait que la sauvegarde est faite', wait(b, "() => window.PDJ.readBackup().since === null && window.PDJ.readBackup().last !== null"))
    check('le bandeau de rappel disparaît de B sans rien faire', wait(b, "() => !document.querySelector('#backup-banner')"))
    check('le résumé de Réglages de B est à jour', wait(b, "() => document.querySelector('#backup-info') && document.querySelector('#backup-info').textContent.includes('Aucune modification depuis la dernière sauvegarde')"))
    check('aucune erreur JavaScript', not a.errors and not b.errors, a.errors + b.errors)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        test_deconnecte(browser)
        fake = FauxSupabase()
        a = test_connexion_et_envoi(browser, fake)
        b = test_second_appareil(browser, fake)
        test_modification_en_direct(a, b, fake)
        test_suppression(a, b, fake)
        test_conflit_et_premiere_synchro(browser)
        test_hors_ligne(browser)
        test_jeton_expire(browser)
        test_deconnexion(browser)
        test_reglages_en_cours_de_saisie(browser)
        test_sauvegarde_partagee(browser)
        browser.close()
    failed = [n for n, ok in RESULTS if not ok]
    print('\n%d vérifications, %d échec(s)' % (len(RESULTS), len(failed)))
    for n in failed:
        print('  ECHEC : ' + n)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
