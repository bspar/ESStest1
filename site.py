#!/usr/bin/env python2

from bottle import app, route, run, request, post, static_file
from beaker.middleware import SessionMiddleware
from cork import Cork
from simplecrypt import encrypt
import logging, sqlite3

@route('/')
def index():
    return static_file('index.html', root='./views')

@post('/login')
def do_login():
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')

@route('/logout')
def logout():
    aaa.logout(success_redirect='/login')

@post('/register')
def do_register():
    password = post_get('password')
    user = (
        encrypt(password, post_get('username')),
        encrypt(password, post_get('name')),
        encrypt(password, post_get('studentid')),
        encrypt(password, post_get('ssn')),
        encrypt(password, post_get('ccn')),
        encrypt(password, post_get('ccv')),
        encrypt(password, post_get('phone')),
        encrypt(password, post_get('cell')),
        encrypt(password, post_get('address')),
        encrypt(password, post_get('city')),
        encrypt(password, post_get('state')),
        encrypt(password, post_get('zip')),
        encrypt(password, post_get('email')),
        0,
    )
    cur = conn.cursor()
    cur.execute('INSERT INTO PII VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', user)
    aaa.register(post_get('username'), post_get('password'), post_get('email_address'))

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

aaa = Cork('cork_conf', email_sender='bspar@bspar.org', smtp_url='smtp://smtp.magnet.ie')

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
# schema: PII(Username TEXT, Name TEXT, StudentID TEXT, SSN TEXT, CCN TEXT, CCV TEXT, Phone TEXT, Cell TEXT, Address TEXT, City TEXT, State TEXT, Zip TEXT, Email TEXT, Enabled INTEGER)

# admin user: 'admin', 'soopr-secear'

if __name__ == '__main__':
    if not conn:
        raise Exception('Cannot connect to pii.db')
    main()
