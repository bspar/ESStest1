#!/usr/bin/env python2

from bottle import app, route, run, request, post, get, static_file
from beaker.middleware import SessionMiddleware
from cork import Cork
import logging

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

@get('/register')
def register():
    pass

@post('/register')
def do_register():
    aaa.register(post_get('username'), post_get('password'), post_get('email_address'))

@route('/js/<f>')
def jsres(f):
    return static_file('js/%s' % (f), root='./views')
@route('/css/<f>')
def cssres(f):
    return static_file('css/%s' % (f), root='./views')

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

# admin user: 'admin', 'soopr-secear'

if __name__ == '__main__':
    main()
