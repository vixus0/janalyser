#!/usr/bin/env python

import sys
import os
import fnmatch
import sqlite3 as sql


def recursive_glob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results


def insert_class(con, name, pkg, repo):
    con.execute(
        'insert into classes (name, package, repo) values (?, ?, ?)',
        (name, pkg, repo)
        )


def insert_import(con, id, import_name, import_pkg):
    con.execute(
        'insert into imports \
            (class_id, imports_name, imports_package) \
            values (?, ?, ?)',
        (id, import_name, import_pkg)
        )


def parse_java(repo, fn, con):
    name = os.path.split(fn)[-1].replace('.java', '')
    pkg = None
    last_class_id = -1

    with open(fn) as f:
        for line in f.readlines():
            tk = line.split()
            if line.startswith('package'):
                pkg = tk[-1].replace(';', '')
                insert_class(con, name, pkg, repo)
                last_class_id = con.lastrowid
            elif line.startswith('import static'):
                # should split <pkg>.<class>.<static thing>
                stuff = tk[-1].rsplit('.', 2)
                import_pkg = stuff[0]
                import_class = stuff[1]
                insert_import(con, last_class_id, import_class, import_pkg)


if __name__ == '__main__':
    os.remove('classes.db')
    con = sql.connect('classes.db')
    con.execute('''create table classes (
                name text,
                package text,
                repo text,
                unique (name, package, repo)
                )''')

    con.execute('''create table imports (
                class_id integer,
                imports_name text,
                imports_package text,
                foreign key (class_id) references classes(rowid)
                )''')

    with con:
        for repo in sys.argv[1:]:
            repo_path = os.path.expanduser(repo)
            repo_name = os.path.basename(repo)
            print('Scanning repo '+repo_path)
            for fn in recursive_glob(repo_path, '*.java'):
                print(' - '+fn)
                parse_java(repo_name, fn, con.cursor())
