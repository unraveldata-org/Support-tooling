#!/usr/local/unravel/ondemand/python/bin/python2.7

#Script tests for both user and group ACL
import tagcmdSecure
import requests
import json
import time
import re
import os
import sys


#Enable debug in standalone testing mode
debug = False
USERNAME=sys.argv[1]

#GET API PASSWORD FROM UNRAVEL.PROPERTIES
separator = "="
usernameProp = 'tagcmdpy.yarn.api.user'
passwordProp = 'tagcmdpy.yarn.api.password'
ambariHostProp = 'tagcmdpy.yarn.api.host'
ambariPortProp = 'tagcmdpy.yarn.api.port'
ambariSslProp = 'tagcmdpy.yarn.api.ssl'

with open('/usr/local/unravel/etc/unravel.properties') as f:
    for line in f:
        if separator in line:
            if usernameProp in line:
                name, value = line.split(separator, 1)
                yarnApiUser = value.strip()
                yarnApiUser = yarnApiUser.replace('\n','')
            if passwordProp in line:
                name, value = line.split(separator, 1)
                yarnApiPass = value.strip()
            if ambariHostProp in line:
                name, value = line.split(separator, 1)
                yarnApiHost = value.strip()
                yarnApiHost = yarnApiHost.replace('\n','')
            if ambariPortProp in line:
                name, value = line.split(separator, 1)
                yarnApiPort = value.strip()
                yarnApiPort = yarnApiPort.replace('\n','')
            if ambariSslProp in line:
                name, value = line.split(separator, 1)
                yarnApiSsl = value.strip()
                yarnApiSsl = yarnApiSsl.replace('\n','')
                if yarnApiSsl == 'False':
                    yarnApiSsl = 'http'
                else:
                    yarnApiSsl = 'https'

DECRYPT_PASS = tagcmdSecure.decryptPassword(yarnApiPass)
DECRYPT_PASS = DECRYPT_PASS.strip('\n')
r = requests.get("%s://%s:%s/api/v1/views/CAPACITY-SCHEDULER/versions/1.0.0/instances/AUTO_CS_INSTANCE/resources/scheduler/configuration" % (yarnApiSsl, yarnApiHost, yarnApiPort), auth=(yarnApiUser, DECRYPT_PASS))


jsonObject=json.loads(r.text)
availQueues={}
for k in jsonObject['items'][0]['properties']:
    if k.endswith('acl_submit_applications'):
        v = jsonObject['items'][0]['properties'][k]
        k = k.replace('yarn.scheduler.capacity.','')
        k = k.replace('.acl_submit_applications','')
        #availQueues.append(k)
        k = k.encode('ascii')
        availQueues[k]=v

if debug == True:
    print("\n\nScript found the following queue ACLS:")
    print("=================================")
    for i in availQueues:
        print(i + " = " + availQueues[i])



idCmd = os.popen("id %s" % USERNAME ).read()
idCmdGroups = idCmd.split(" ")[2]
groupList=[]
rawGroupList = idCmdGroups.split(',')
for i in rawGroupList:
    i = re.sub(r"groups\=[0-9]{4}\(","", i)
    i = re.sub(r"\)","", i)
    i = re.sub(r"[0-9]{4}\(","", i)
    i = i.replace('\n','')
    groupList.append(i)

if debug == True:
    print("\n\nScript found the following groups for user %s:" % USERNAME)
    print("=================================")
    for i in groupList:
        print(i)

#Set place holder for final set list
aclList = set()

#TEST USERNAME QUEUE ACCESS
queueUserAccess=[]
for i in availQueues:
    x = re.findall(USERNAME, availQueues[i])
    x = re.findall('\*', availQueues[i])
    if (x):
      queueUserAccess.append(i)
      aclList.add(i)

if debug == True:
    print("\n\nScript found the following Queue access based on username or non-restricted access ACL (*):")
    print("=================================")
    for i in queueUserAccess:
        print(i)

queueGroupAccess=[]
for group in groupList:
    for i in availQueues:
        x = re.findall(group, availQueues[i])
        if (x):
          queueGroupAccess.append(i)
          aclList.add(i)


if debug == True:
    print("\n\nScript found the following Queue access based on users groups:")
    print("=================================")
    for i in queueGroupAccess:
        print(i)

if debug == True:
    print("\n\nScript found the following ACL access based on both group and username")
    print("=================================")
    for x in aclList:
        print x
    print("\n\n")

#uid=1019(benchmark-user) gid=1019(benchmark-user) groups=1019(benchmark-user),1022(test-group1),1023(test-group2),1024(test-group3)

sys.stdout.write("uid=9999(%s) " % USERNAME)
sys.stdout.write("gid=9999(%s) " % USERNAME)
sys.stdout.write("groups=")
for x in aclList:
    sys.stdout.write("9999(%s)," % x)
