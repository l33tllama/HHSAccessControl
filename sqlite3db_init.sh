#!/bin/sh
sqlite3 ControlPanel.py 'CREATE TABLE access_list(
rfid INTEGER PRIMARY KEY,
name TEXT,
id INTEGER,
phone INTEGER,
end_date DATE NOT NULL,
alarm INTEGER,
access INTEGER);'
python ControlPanel.py