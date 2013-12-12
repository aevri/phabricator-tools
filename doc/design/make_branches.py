#! /usr/bin/env python
import subprocess
commit_list = subprocess.check_output(['git', 'rev-list', 'master..'])
branch = 'master'
for commit in reversed(commit_list.splitlines()):
    print subprocess.check_output(['git', 'log', '-n', '1', commit])
    description = raw_input('one word description: ')
    branch = "r/{}/{}".format(branch, description)
    print subprocess.check_output(['git', 'branch', branch, commit])
