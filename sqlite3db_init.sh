#!/bin/sh
cd "${0%/*}"
sqlite3 ControlPanel.py < init.sql
python ControlPanel.py