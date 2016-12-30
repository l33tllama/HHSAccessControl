#!/bin/sh
sqlite3 ControlPanel.py < init.sql
python ControlPanel.py