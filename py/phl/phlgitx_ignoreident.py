"""Configure repos to ignore ident strings, overrule '.gitattributes'.

For non-interactive uses of Git repositories, it can be undesirable to allow
the 'ident string' functionality as there are some edge-cases that may require
manual intervention.

Provide support for writing the repo-global '.git/info/attributes' file such
that any enabling of 'ident strings' via '.gitattributes' files will be
ignored.

Note that this should have no effect on diffs or commits, it only affects the
content of files in the work tree.  This content should not be relevant for
static inspection of the source but would be relevant for other uses, e.g.
automated builds.

"""

import os

import phlsys_fs


_REPO_ATTRIBUTES_PATH = '.git/info/attributes'
_REPO_ATTRIBUTES_CONTENT = '* -ident\n'


def is_repo_definitely_ignoring(repo_path):
    repo_attributes_path = os.path.join(repo_path, _REPO_ATTRIBUTES_PATH)
    if not os.path.exists(repo_attributes_path):
        return False
    else:
        # check the existing file
        content = phlsys_fs.read_text_file(repo_attributes_path)
        return content == _REPO_ATTRIBUTES_CONTENT


def ensure_repo_ignoring(repo_path, repo):
    if is_repo_definitely_ignoring(repo_path):
        # nothing to do
        return

    repo_attributes_path = os.path.join(repo_path, _REPO_ATTRIBUTES_PATH)
    if not os.path.exists(repo_attributes_path):
        # create the file with required content
        phlsys_fs.write_text_file(
            repo_attributes_path,
            _REPO_ATTRIBUTES_CONTENT)
        print("wrote.")
    else:
        # we won't try to do any sort of merging, just escalate
        raise Exception(
            "cannot ensure ignore ident in existing file: {}".format(
                repo_attributes_path))

    #repo('checkout', 'HEAD')
