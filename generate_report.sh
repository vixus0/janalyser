#!/usr/bin/env bash

sqlite3 classes.db < report.sql > docs/report.htm
