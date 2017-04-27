#!/usr/bin/env python

import os
import fnmatch
import sqlite3 as sql

from argparse import ArgumentParser


def recursive_glob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results


def insert_class(con, name, pkg, repo):
    print(' - Adding class {}.{} from {}'.format(pkg, name, repo))
    con.execute(
        'insert into classes (name, package, repo) values (?, ?, ?)',
        (name, pkg, repo)
        )


def insert_import(con, id, cls_name, import_name, import_pkg):
    print('   * Class {}:{} imports {}.{}'.format(id, cls_name, import_pkg, import_name))
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
            tk = line.replace(';', '').split()
            if line.startswith('package'):
                pkg = tk[-1]
                insert_class(con, name, pkg, repo)
                last_class_id = con.lastrowid
            elif line.startswith('import static'):
                # split into <pkg>.<class>.<static thing>
                stuff = tk[-1].rsplit('.', 2)
                insert_import(con, last_class_id, name, stuff[1], stuff[0])
            elif line.startswith('import'):
                # split into <pkg>.<class>
                stuff = tk[-1].rsplit('.', 1)
                insert_import(con, last_class_id, name, stuff[1], stuff[0])


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('dirs', help='Directories to scan', nargs='+')
    ap.add_argument('-o', '--out', help='Output sqlite DB file', default='classes.db')
    args = ap.parse_args()

    if os.path.exists(args.out):
        os.remove(args.out)

    con = sql.connect(args.out)
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
        for repo in args.dirs:
            repo_path = os.path.expanduser(repo).rstrip('/')
            repo_name = os.path.split(repo_path)[-1]
            print('\nScanning repo {} ({})'.format(repo_path, repo_name))
            for fn in recursive_glob(repo_path, '*.java'):
                parse_java(repo_name, fn, con.cursor())
