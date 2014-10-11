#!/usr/bin/env python2

from bottle import app, route, run, template
from beaker.middleware import SessionMiddleware

@route('/')
def index():
    return template('index.tmp')


def main():
    run(app=app, host='localhost', port=8080, debug=True)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app(), session_opts)

if __name__ == '__main__':
    main()