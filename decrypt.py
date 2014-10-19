#!/usr/bin/env python2

import simplecrypt, sqlite3, base64

user = raw_input('Enter the username: ')
password = raw_input('Their password: ')

conn = sqlite3.connect('pii.db')
row = conn.execute('SELECT * from PII WHERE Username=?', (user,)).fetchone()
conn.close()
if not row:
    print 'Failed to find a row :('
else:
    for item in row:
        try:
            print simplecrypt.decrypt(password, base64.b64decode(item))
        except:
            print 'Can\'t decrypt an item - it\'s probably plaintext (username or email)'
