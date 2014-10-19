#!/usr/bin/env python2

from bottle import app, route, run, request, post, static_file, template
from beaker.middleware import SessionMiddleware
from cork import Cork
from simplecrypt import encrypt, decrypt
import logging, sqlite3, gnupg, base64

admin_email = 'bspar@bspar.org'

# Home page
@route('/')
def index():
    return static_file('index.html', root='./views')

# Login action
@post('/login')
def do_login():
    username = post_get('username')
    password = post_get('password')
    session = request.environ['beaker.session'] # Implement session storage
    conn = sqlite3.connect('pii.db')
    row = conn.execute('SELECT Username, Name, StudentID from PII WHERE Username=?', (username,)).fetchone()
    conn.close()
    if not row:     # Make sure the user exists - if not, say 'Nope. Tey again.'
        return 'Nope. Try again.'
    # Add some PII to the session (server side)
    session['username'] = row[0]
    session['name'] = decrypt(password, base64.b64decode(row[1]))
    session['studentid'] = decrypt(password, base64.b64decode(row[2]))
    session.save()
    # Attempt login - success brings the user to services, failure (disabled account or bad password) brings them back home
    aaa.login(username, password, success_redirect='/services', fail_redirect='/')

# A sample services page that shows some random PII
@route('/services')
def services():
    session = request.environ['beaker.session']
    return template('''
        <p>Look at all these services! The more services listed here, the more you can tell how much we care about you. Yes, we care /that/ much!
        <p>User: {{username}}
        <p>Name: {{name}}
        <p>StudentID: {{studentid}}
    ''', username=session['username'], name=session['name'], studentid=session['studentid'])

# logout
@route('/logout')
def logout():
    aaa.logout(success_redirect='/')

# User registration
@post('/register')
def do_register():
    password = post_get('password')
    username = post_get('username')
    # Encrypt (and base64-encode) PII before putting it into the database
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
    conn = sqlite3.connect('pii.db')
    cur = conn.cursor()
    print 'User: ' + str(user)
    # schema: PII(Username TEXT PRIMARY KEY, Name TEXT, StudentID TEXT, SSN TEXT, CCN TEXT, CCV TEXT, Phone TEXT, Cell TEXT, Address TEXT, City TEXT, State TEXT, Zip TEXT, Email TEXT)
    cur.execute('INSERT INTO PII VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', user)  # add user to database
    conn.commit()
    conn.close()
    # Send user verification email to admin
    aaa.register(post_get('username'), post_get('password'), admin_email)
    # Send encrypted email with user's password to the administrator
    aaa.mailer.send_email(admin_email, username, str(gpg.encrypt(password, admin_email, always_trust=True)))
    return 'Thanks, an admin will soon activate your account.'

# User validation page
@route('/validate/:reg_code')
def validate(reg_code):
    # Get the username of the registration code
    user = aaa._store.pending_registrations[reg_code]['username']
    # Get the user's email from the database
    conn = sqlite3.connect('pii.db')
    email = conn.execute('SELECT Email from PII WHERE Username=?', (user,)).fetchone()[0]
    conn.close()
    # Send notification email to user
    aaa.mailer.send_email(email, 'Your STUPIDCOMP account has been approved!', 'Your STUPIDCOMP account has been approved! You may now use the services.')
    # Do the actual validation
    aaa.validate_registration(reg_code)
    return 'Yay. Now the user can enjoy all them services'

# A few routes for static stuff
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

def getapp():
    return app

def main():
    run(app=app, host='0.0.0.0', port=8080, debug=True)

# 'aaa' is the instance of cork, the user management module
aaa = Cork('cork_conf', email_sender='bspar@bspar.org', smtp_url='smtp://smtp.bspar.org')
# 'gpg' is the GPG module
gpg = gnupg.GPG(gnupghome='./gnupg')

# Logging module (append only)
logging.basicConfig(filename='website.log', format='localhost - - [%(asctime)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

# Enable use of session data
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app(), session_opts)

# admin user: 'admin', 'soopr-secear'

if __name__ == '__main__':
    main()
