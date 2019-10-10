#!/usr/bin/python

import os

confFile='/etc/my.cnf'

os.popen('clear')
print "Placing a backup of /etc/my.cnf in /tmp/"
#Copy command below argument "-n" ensures the original my.cnf is not backed up more than max_connect_errors
#This ensures that the original my.cnf is preserved if multipul runs of this script occur
os.popen('cp -n /etc/my.cnf /tmp/my-cnf-$(date +"%Y-%m-%d").bak')
import ConfigParser

#Parse original config into dictionary
class MyParser(ConfigParser.ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

if __name__ == "__main__":
    f = MyParser()
    f.read(confFile)
    defaultConfig = f.as_dict()
    #print defaultConfig['mysqld']['innodb_lock_wait_timeout']

#Reccommended conf derived from:
# https://unraveldata.atlassian.net/wiki/spaces/UN43/pages/437682525/Installing+MySQL+or+Compatible+Database+for+Unravel

desiredConfig={
'key_buffer_size' : '123M',
'max_allowed_packet' : '32M',
'sort_buffer_size' : '32M',
'query_cache_size' : '64M',
'thread_concurrency' : '6',
'max_connections' : '500',
'max_connect_errors' : '2000000000',
'open_files_limit' : '10000',
'port-open-timeout' : '121',
'expire-logs-days' : '2',
'character_set_server' : 'utf8',
'collation_server' : 'utf8_unicode_ci',
'innodb_open_files' : '2000',
'innodb_file_per_table' : '1',
'innodb_data_file_path' : 'ibdata1:100M:autoextend',
'innodb_buffer_pool_size' : '1G',
'innodb_flush_method' : 'O_DIRECT',
'innodb_log_file_size' : '256M',
'innodb_log_buffer_size' : '64M',
'innodb_flush_log_at_trx_commit' : '2',
'innodb_lock_wait_timeout' : '50',
'innodb_thread_concurrency' : '20',
'innodb_read_io_threads' : '16',
'innodb_write_io_threads' : '4',
'binlog_format' : 'mixed'
}

addValues={}
updateValues={}

for k,v in desiredConfig.iteritems():
    if k in defaultConfig['mysqld']:
        #print defaultConfig['mysqld'][k]
        #If the config value is different change it
        if v == defaultConfig['mysqld'][k]:
            #print("Correct value")
            continue
        else:
            updateValues[k] = v
            f.set('mysqld', k, v)
    else:
        #If no config present add it
        #print ("No key found for %s" % k)
        addValues[k] = v
        f.set('mysqld', k, v)

if bool(addValues) != False:
    print "\n\nThe following config is not present and will be added:\n"
    for k,v in addValues.iteritems():
        print("%s=%s" % (k,v))
if bool(updateValues) != False:
        print "\n\nThe following configs will be updated to Unravel reccomended values:\n"
        for k,v in updateValues.iteritems():
            print("%s=%s" % (k,v))

if bool(addValues) == False and bool(updateValues) == False:
    print("No config changes required")
else:
    write=raw_input("Write config changes to file? (Y/N)")
    write=write.upper()
    if write == "Y":
        with open(confFile, 'w') as g:
            f.write(g)
    else:
        print("Aborting write file, unknown keyboard response: \"%s\" % write")
        
