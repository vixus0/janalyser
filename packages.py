#!/usr/bin/env python

import fileinput
import sys
import os
import fnmatch
from collections import defaultdict
from argparse import ArgumentParser
from tempfile import mkdtemp
from subprocess import check_output


def java_sources(dir):
    for root, _, filenames in os.walk(dir):
        files = (os.path.join(root, filename) for filename in fnmatch.filter(filenames, '*.java'))
        for filename in files:
            for line in open(filename).readlines():
                yield (filename, line)


def xcls(line):
    return line.split()[-1].replace(';', '').replace(',', '')


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--saml', help='List of SAML repos')
    ap.add_argument('repos', help='Repos to investigate', nargs='+')
    args = ap.parse_args()

    tmpd = mkdtemp(prefix='saml_pain_')
    sys.stderr.write('Working in {}\n'.format(tmpd))

    classes_in_repo = defaultdict(list)
    repo_containing_class = defaultdict(list)

    for repo in fileinput.input([args.saml]):
        # Clone the SAML repo
        repo = repo.strip()
        print('Cloning SAML repo: '+repo)
        repo_dir = os.path.join(tmpd, os.path.basename(repo))
        git_args = [
            'git', 'clone', '--depth', '1', 'git@github.gds:{}.git'.format(repo),
            repo_dir
            ]
        check_output(git_args)
        # Find the unique package names
        for filename, line in java_sources(repo_dir):
            if line.startswith('package'):
                cls = os.path.basename(filename).replace('.java', '')
                full_class = '.'.join([xcls(line), cls])
                classes_in_repo[repo].append(full_class)
                repo_containing_class[full_class].append(repo)

    dependencies = defaultdict(lambda: defaultdict(list))
    gradle_deps = defaultdict(list)

    for repo_dir in args.repos:
        gradle_file = os.path.join(repo_dir, 'build.gradle')
        if os.path.exists(gradle_file):
            repo = os.path.basename(repo_dir)
            for filename, line in java_sources(repo_dir):
                if line.startswith('import'):
                    cls = xcls(line)
                    if cls in repo_containing_class.keys():
                        dependencies[repo][filename].append((repo_containing_class[cls], cls))
            with open(gradle_file) as f:
                lines = f.readlines()
                for saml_repo in classes_in_repo.keys():
                    saml_lib = os.path.basename(saml_repo)
                    for l in lines:
                        if saml_lib in l:
                            gradle_deps[repo].append(saml_repo)

    with open('./out/classes_in_repo', 'wb') as f:
        for saml_repo in sorted(classes_in_repo.keys()):
            f.write('{}:\n'.format(saml_repo))
            for cls in classes_in_repo[saml_repo]:
                f.write('- {}\n'.format(cls))
            f.write('\n')

    with open('./out/dependencies', 'wb') as f:
        for repo in sorted(dependencies):
            if len(dependencies[repo]) == 0:
                continue
            f.write('{}:\n'.format(repo))
            for filename in sorted(dependencies[repo]):
                f.write('  {}:\n'.format(os.path.basename(filename).replace('.java', '')))
                for dep in sorted(dependencies[repo][filename], key=lambda t: t[0]):
                    saml_repos = ', '.join(d+('*' if d in gradle_deps[repo] else '') for d in dep[0])
                    saml_cls = dep[1]
                    f.write('  - [{}] {}\n'.format(saml_repos, saml_cls))
            f.write('\n')
