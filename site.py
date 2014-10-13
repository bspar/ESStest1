#!/usr/bin/env python2

from bottle import app, route, run, template, static_file
from beaker.middleware import SessionMiddleware

@route('/')
def index():
    return static_file('index.html', root='./views')


def main():
    run(app=app, host='0.0.0.0', port=8080, debug=True)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app(), session_opts)

if __name__ == '__main__':
    main()
