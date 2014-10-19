ESStest1
========

Embedded System Security test 1 project


To run:
========

+ Install the following python2 modules:

    bottle, cork, simplecrypt, sqlite3, python-gnupg, base64

+ Use the apache esstest1.conf file to enable the website in apache (requires mod-ssl) (the website shall be located in /var/www/ESStest1/)

+ As of now, the only PGP key is for bspar@bspar.org. Use the provided "gpgsetup.py" script to import any other keys