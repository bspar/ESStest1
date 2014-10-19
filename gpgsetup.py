#!/usr/bin/env python2

import gnupg

gpg = gnupg.GPG(gnupghome='./gnupg')
key_data = open('bspar.key').read()
result = gpg.import_keys(key_data)
print result.results
print '---'
print result
