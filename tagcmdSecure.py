import sys
import os

def encryptPassword(PASSWORD):
    encryptedPW = os.popen("echo \"%s\" | openssl aes-256-cbc -e -a -K 00000000000000000000000000000000 -iv 00000000000000000000000000000000 2>/dev/null" % PASSWORD).read()
    print("\nPaste the following in unravel.properties:\n\ntagcmdpy.yarn.api.password=%s" % encryptedPW)

    return encryptedPW

def decryptPassword(PASSWORD):
    decryptedPW = os.popen("echo \"%s\" | openssl aes-256-cbc -d -a -K 00000000000000000000000000000000 -iv 00000000000000000000000000000000 2>/dev/null" % PASSWORD).read()
    #print(decryptedPW)
    return decryptedPW
