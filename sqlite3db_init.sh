#!/bin/sh
echo "CREATE TABLE access_list(rfid INTEGER PRIMARY KEY,name TEXT,id INTEGER,phone INTEGER,end_date DATE NOT NULL,alarm INTEGER,access INTEGER);" | sqlite3 ControlPanel.db
python ControlPanel.py
