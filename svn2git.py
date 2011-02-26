# usage:
#
# python2.7 svn2git.py \
#           http://svn.repoze.org/repoze.catalog \
#           git@github.com:repoze/repoze.catalog.git \
#           branch1 \
#           branch2
#
# (branch specs are optional, otherwise only trunk and tags are imported)
#
# users.txt should be in /tmp/users.txt
#
# requires python 2.7

import tempfile
import shutil
import os
import subprocess
import re
import sys

tag_re = re.compile(r'tags/(\d.*)')

def do(svn, git, *branches):
    cmd = "git svn clone --stdlayout --no-metadata -A /tmp/users.txt %s tmp"
    cmd = cmd % svn
    wd = tempfile.mkdtemp() 
    try:
        os.chdir(wd)
        result = os.system(cmd)
        if result:
            raise ValueError(result)
        os.chdir('tmp')
        r = subprocess.check_output(['git', 'branch', '-r'])
        tag_branches = [ x.strip() for x in filter(None, r.split('\n'))]
        for tag_branch in tag_branches:
            matched = tag_re.match(tag_branch)
            if matched:
                tag = matched.group(1)
                print 'making tag %s' % tag
                os.system('git checkout -b tag_x remotes/%s' % tag_branch)
                os.system('git checkout master')
                os.system('git tag %s tag_x' % tag)
                os.system('git branch -D tag_x')
        for branch in branches:
            print 'creating branch %s' % branch
            os.system('git checkout -b %s remotes/%s' % (branch, branch))
        os.system('git checkout master')
        os.chdir('..')
        os.system('git clone tmp dest')
        os.chdir('dest')
        os.system('git remote add xx %s' % git)
        os.system('git push xx master')
        for branch in branches:
            print 'pushing branch %s' % branch
            os.system('git checkout -b %s remotes/origin/%s' % (branch, branch))
            os.system('git push xx %s' % branch)
        os.system('git push xx --tags')
    finally:
        shutil.rmtree(wd)
        
if __name__ == '__main__':
    do(sys.argv[1], sys.argv[2], *sys.argv[3:])
    
