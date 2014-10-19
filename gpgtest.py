#!/usr/bin/env python2

import gnupg

gpg = gnupg.GPG(gnupghome='./gnupg')
print '---'
string = 'yoyoyo'
print '---'
encrypted = str(gpg.encrypt(string, 'bspar@bspar.org', always_trust=True))
print '---'
print encrypted
