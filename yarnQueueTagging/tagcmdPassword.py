#!/usr/local/unravel/ondemand/python/bin/python2.7

import tagcmdSecure
import sys
from getpass import getpass

if sys.argv[1] == "encrypt":
    pswd = getpass('Password to encrypt:')
    tagcmdSecure.encryptPassword(pswd)

if sys.argv[1] == "decrypt":
    decryptedPass = tagcmdSecure.decryptPassword(sys.argv[2])
    print(decryptedPass)
