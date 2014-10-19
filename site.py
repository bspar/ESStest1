#!/usr/bin/env python2

from bottle import app, route, run, request, post, static_file, template
from beaker.middleware import SessionMiddleware
from cork import Cork
from simplecrypt import encrypt, decrypt
import logging, sqlite3, gnupg, base64

admin_email = 'bspar@bspar.org'

@route('/')
def index():
    return static_file('index.html', root='./views')

@post('/login')
def do_login():
    username = post_get('username')
    password = post_get('password')
    session = request.environ['beaker.session']
    row = conn.execute('SELECT Username, Name, StudentID from PII WHERE Username=?', (username,)).fetchone()
    if not row:
        return 'Nope. Try again.'
    session['username'] = row[0]
    session['name'] = decrypt(password, base64.b64decode(row[1]))
    session['studentid'] = decrypt(password, base64.b64decode(row[2]))
    session.save()
    aaa.login(username, password, success_redirect='/services', fail_redirect='/')

@route('/services')
def services():
    session = request.environ['beaker.session']
    return template('''
        <p>Look at all these services! The more services listed here, the more you can tell how much we care about you. Yes, we care /that/ much!
        <p>User: {{username}}
        <p>Name: {{name}}
        <p>StudentID: {{studentid}}
    ''', username=session['username'], name=session['name'], studentid=session['studentid'])

@route('/logout')
def logout():
    aaa.logout(success_redirect='/')

@post('/register')
def do_register():
    password = post_get('password')
    username = post_get('username')
    user = (
        username,
        base64.b64encode(encrypt(password, post_get('name'))),
        base64.b64encode(encrypt(password, post_get('studentid'))),
        base64.b64encode(encrypt(password, post_get('ssn'))),
        base64.b64encode(encrypt(password, post_get('ccn'))),
        base64.b64encode(encrypt(password, post_get('ccv'))),
        base64.b64encode(encrypt(password, post_get('phone'))),
        base64.b64encode(encrypt(password, post_get('cell'))),
        base64.b64encode(encrypt(password, post_get('address'))),
        base64.b64encode(encrypt(password, post_get('city'))),
        base64.b64encode(encrypt(password, post_get('state'))),
        base64.b64encode(encrypt(password, post_get('zip'))),
        post_get('email'),
    )
    cur = conn.cursor()
    print 'User: ' + str(user)
    # schema: PII(Username TEXT PRIMARY KEY, Name TEXT, StudentID TEXT, SSN TEXT, CCN TEXT, CCV TEXT, Phone TEXT, Cell TEXT, Address TEXT, City TEXT, State TEXT, Zip TEXT, Email TEXT)
    cur.execute('INSERT INTO PII VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', user)
    conn.commit()
    # Send user verification email to admin
    aaa.register(post_get('username'), post_get('password'), admin_email)
    # Send encrypted email with user's password to the administrator
    aaa.mailer.send_email(admin_email, username, str(gpg.encrypt(password, admin_email, always_trust=True)))
    return 'Thanks, an admin will soon activate your account.'

@route('/validate/:reg_code')
def validate(reg_code):
    user = aaa._store.pending_registrations[reg_code]['username']
    email = base64.b64decode(conn.execute('SELECT Email from PII WHERE Username=?', (user,)).fetchone())
    aaa.mailer.send_email(email, 'Your STUPIDCOMP account has been approved!', 'Your STUPIDCOMP account has been approved! You may now use the services.')
    aaa.validate_registration(reg_code)
    return 'Yay. Now the user can enjoy all them services'

@route('/js/<f>')
def jsres(f):
    return static_file('js/%s' % (f), root='./views')
@route('/css/<f>')
def cssres(f):
    return static_file('css/%s' % (f), root='./views')
@route('/font-awesome-4.1.0/<d>/<f>')
def fawesomeres(d, f):
    return static_file('%s' % (f), root='./views/font-awesome-4.1.0/%s' % (d))
@route('/img/<f>')
def imgres(f):
    return static_file('img/%s' % (f), root='./views')

def postd():
    return request.forms

def post_get(name, default=''):
    return request.POST.get(name, default).strip()

def main():
    run(app=app, host='0.0.0.0', port=8080, debug=True)

aaa = Cork('cork_conf', email_sender='bspar@bspar.org', smtp_url='smtp://smtp.bspar.org')
gpg = gnupg.GPG(gnupghome='./gnupg')

logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app(), session_opts)
conn = sqlite3.connect('pii.db')

# admin user: 'admin', 'soopr-secear'

if __name__ == '__main__':
    if not conn:
        raise Exception('Cannot connect to pii.db')
    main()
