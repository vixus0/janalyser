#!/usr/bin/env bash

sqlite3 classes.db < report.sql | sed -e 's/\[\([^]]*\)\]/<\1>/g' > report.htm
