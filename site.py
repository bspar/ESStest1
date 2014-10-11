#!/usr/bin/env python2

from bottle import route, run, template

@route('/')
def index():
    return template('index.tmp')


def main():
    run(host='localhost', port=8080, debug=True)

if __name__ == '__main__':
    main()