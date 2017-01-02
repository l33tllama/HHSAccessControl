#!/bin/sh

# Just in case
rm ControlPanel.db.old
mv ControlPanel.db ControlPanel.db.old

cat init.sql | sqlite3 ControlPanel.db
python ControlPanel.py

