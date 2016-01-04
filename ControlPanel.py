#!/usr/bin/python

import sqlite3 #debian module python-pysqlite2
import MySQLdb #debian module python-mysqldb
import ConfigParser

global config
config = ConfigParser.RawConfigParser()

def get_external_data():
	global config
	host = config.get('MySQL', 'host')
	user = config.get('MySQL', 'username')
	passwd = config.get('MySQL', 'password')
	db = config.get('MySQL', 'database')

	ext_db = MySQLdb.connect(host, user, passwd, db)
	ext_cur = ext_db.cursor()
	# Selecting label, not data, since the old access system was reading
	# too few bits from the RFID tag (but consistently), and storing the
	# wrong values.

	ext_cur.execute("SELECT label, display_name, id, phone, end_date, alarm, access FROM access_list");

        ext_rfid = ext_db.cursor()
        ext_rfid.execute("SELECT label, display_name FROM access_list");

	return ext_cur.fetchall(), dict(ext_rfid.fetchall())

def get_local_rfid():
	cur.execute("SELECT rfid, name FROM access_list")
	return dict(cur.fetchall())

def get_local_data():
    cur.execute("SELECT * FROM access_list")
    return cur.fetchall()

def sync(external, local, localrfid, externalrfid):
    # Loop through all external rfid tags, if they don't exist locally, 
    # add them to the local store
    for row in external :
        rfid = row[0]
        name = row[1]
        id = row[2]
        phone = row[3]
        end_date = row[4]
        alarm = row[5]
        access = row[6]
        if not rfid in localrfid:
            add_local(rfid, name, id, phone, end_date, alarm, access)

	# Loop through all internal rfid tags, if they don't exist externally,
	# remove the local copy
	for rfid in localrfid.keys():
		name = localrfid[rfid]
		if not rfid in externalrfid:
			remove_local(rfid, name)

    # Loop through and look for changes to other things, and update
    for x in range(6) :
        compare(x,external,local)

def compare(fieldname,external,local):
    for row in external :
        data = row[fieldname]
        rfid = row[0]
        name = row[1]
        id = row[2]
        phone = row[3]
        end_date = row[4]
        alarm = row[5]
        access = row[6]
        found = True
        for row in local:
            data2 = row[fieldname]
            rfid2 = row[0]
            if rfid == rfid2:
                if not data == data2:
                    if data is not None and data2 is not None:
                        found = False
                        print "mismatch data: %s, %s" % (data,data2)
        if found == False:
            update_local(rfid, name, id, phone, end_date, alarm, access)
    

def add_local(rfid, name, id, phone, end_date, alarm, access):
	cur.execute("INSERT INTO access_list (rfid, name, id, phone, end_date, alarm, access) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (rfid, name, id, phone, end_date, alarm, access))
	db.commit()
	print "Adding: %s, %s" % (rfid, name)

def remove_local(rfid, name):
	cur.execute("DELETE FROM access_list WHERE rfid = '%s'" % rfid)
	db.commit()
	print "Removing: %s, %s" % (rfid, name)

def update_local(rfid, name, id, phone, end_date, alarm, access):
    cur.execute("UPDATE access_list set name = '%s', id = '%s', phone = '%s', end_date = '%s', alarm = '%s', access = '%s' WHERE rfid = '%s'" % (name, id, phone, end_date, alarm, access,rfid))
    db.commit ()
    print "Updating: %s, %s" % (rfid,name)
    
config.read('/home/pi/HHSAccesControl/config.cfg')
dbName = config.get('SQLite', 'filename')
db = sqlite3.connect(dbName)
cur = db.cursor()

external_data,external_rfid = get_external_data()
local_data = get_local_data()
local_rfid = get_local_rfid()
print "External DB"
for user in  external_data:
	print user
print "Local DB"
for user in local_data:
	print user
sync(external_data, local_data, local_rfid, external_rfid)

