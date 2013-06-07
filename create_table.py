#!/usr/bin/python

# Author: Dainius Jocas
# This script create table 'rpi' if it does not exist already in the database 'monitor.db'
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

con = None

try:
    con = lite.connect('monitor.db')

    cur = con.cursor()
    cur.execute("CREATE TABLE if not exists rpi(piID INT, piHostname TEXT, piActivity TEXT, piCPULoad TEXT, piGateway TEXT, piStorageState TEXT, piIP TEXT, piNetmask TEXT, piProce$


except lite.Error, e:

    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:

    if con:
        con.close()
