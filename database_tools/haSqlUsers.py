#!/usr/local/unravel/ondemand/python/bin/python2.7

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.exc import OperationalError
from getpass import getpass
import sys, getopt, os
import StringIO

scriptHelp = ('''
    haSetUp.py -r <role> -s <secondryhost>

        -r --role: Master or Slave
        -s --secondryhost: Hostname of the other master/Slave

        Example:

        haSetUp.py --role master --secondryhost slavehost.unravel.com
        haSetUp.py -r slave -s masterhost.unravel.com

      ''')

ops={}

#define script args
def main(argv):


   if len(argv) < 4:
       print("Missing arguments...\n")
       print(scriptHelp)
       sys.exit()
   try:
      opts, args = getopt.getopt(argv,"hr:s:",["role=","secondryhost="])
   except getopt.GetoptError:
      print(scriptHelp)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(scriptHelp)
         sys.exit()
      elif opt in ("-r", "--role"):
         ops['role'] = arg
      elif opt in ("-s", "--secondryhost"):
         ops['shost'] = arg
   return ops


if __name__ == "__main__":
   main(sys.argv[1:])

#get unravel props
def parse_unravel_properties(props_path):
    props = {}
    with open(props_path) as prop_file:
        for line in prop_file:
            key, val = line.partition("=")[::2]
            props[key.strip()] = val.strip()
    return props

unravel_props = parse_unravel_properties("/usr/local/unravel/etc/unravel.properties")
DBusername=unravel_props['unravel.jdbc.username']
DBpass=unravel_props['unravel.jdbc.password']

print("Enter the root user password for MySQL:")
#password = getpass()
password="unraveldata"
conString="mysql://root:unraveldata@127.0.0.1/unravel_mysql_prod"
engine = create_engine(conString,echo = False)
engine.execute("USE mysql")

hostname=os.popen("hostname -f").read().rstrip()

try:
    dropUsrSql="DROP USER 'unravel'@'%s'" % hostname
    delUsrData = engine.execute(dropUsrSql)
except OperationalError:
    pass

try:
    addUsrSql="CREATE USER 'unravel'@'%s' IDENTIFIED BY '%s'" % (hostname, DBpass)
    addUsrData = engine.execute(addUsrSql)
except OperationalError:
    pass

try:
    dropUsrSql="DROP USER 'unravel'@'%s'" % ops['shost']
    delUsrData = engine.execute(dropUsrSql)
except OperationalError:
    pass

try:
    addUsrSql="CREATE USER 'unravel'@'%s' IDENTIFIED BY '%s'" % (ops['shost'], DBpass)
    addUsrData = engine.execute(addUsrSql)
except OperationalError:
    pass

try:
    permissions="GRANT ALL PRIVILEGES ON unravel_mysql_prod TO 'unravel'@'%s';" % hostname
    permissions = engine.execute(addUsrSql)
except OperationalError:
    pass

try:
    permissions="GRANT ALL PRIVILEGES ON unravel_mysql_prod TO 'unravel'@'%s';" % ops['shost']
    permissions = engine.execute(addUsrSql)
except OperationalError:
    pass

try:
    updateprivs="FLUSH PRIVILEGES;"
    updateprivs = engine.execute(addUsrSql)
except OperationalError:
    pass




#
#delUsrData = engine.execute(dropUsrSql)
#addUsrData = engine.execute(addUsrSql)
