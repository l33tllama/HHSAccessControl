#!/bin/sh
qlite3 ControlPanel.py < init.sql
python ControlPanel.py