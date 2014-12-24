"""Abstraction for Arcyd's git operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_git
#
# Public Classes:
#   Repo
#    .is_identical
#    .get_remote_branches
#    .checkout_forced_new_branch
#    .raw_diff_range
#    .get_range_hashes
#    .make_revisions_from_hashes
#    .squash_merge
#    .archive_to_landed
#    .push_landed
#    .archive_to_abandoned
#    .push_abandoned
#    .push_asymmetrical
#    .push
#    .push_delete
#    .checkout_master_fetch_prune
#    .hash_ref_pairs
#    .checkout_make_raw_diff
#    .get_remote
#   DifferResultCache
#    .get_cache
#    .set_cache
#    .checkout_make_raw_diff
#
# Public Functions:
#   get_managed_branches
#   checkout_master_fetch_special_refs
#
# Public Assignments:
#   ARCYD_LANDED_REF
#   ARCYD_LANDED_BRANCH_FQ
#   ARCYD_ABANDONED_REF
#   ARCYD_ABANDONED_BRANCH_FQ
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import

import phlgit_branch
import phlgit_checkout
import phlgit_commit
import phlgit_diff
import phlgit_fetch
import phlgit_log
import phlgit_merge
import phlgit_push
import phlgit_showref
import phlgitu_ref

import abdt_branch
import abdt_differ
import abdt_lander
import abdt_logging
import abdt_naming

_ARCYD_REFSPACE = 'refs/arcyd'
_PRIVATE_ARCYD_BRANCHSPACE = '__private_arcyd'

_LANDED_ARCHIVE_BRANCH_MESSAGE = """
Create an archive branch for landed branches

Landed branches will be automatically merged here by Arcyd for your
reference.

This branch is useful for:

  o: cleaning up branches contained by the landed branch
     (see 'git branch --merged')

  o: finding the pre-landed version of a commit
     (see 'git log --grep' - you can search for the landed sha1)

  o: keeping track of Arcyd's landing activity
     (see 'git log --first-parent')

""".strip()

ARCYD_LANDED_REF = "{}/landed".format(_ARCYD_REFSPACE)
_ARCYD_LANDED_BRANCH = "{}/landed".format(_PRIVATE_ARCYD_BRANCHSPACE)
ARCYD_LANDED_BRANCH_FQ = "refs/heads/" + _ARCYD_LANDED_BRANCH

_ABANDONED_ARCHIVE_BRANCH_MESSAGE = """
Create an archive branch for abandoned branches

Abandoned branches will be automatically merged here by Arcyd for your
reference.

This branch is useful for:

  o: keeping track of Arcyd's abandoning activity
     (see 'git log --first-parent')

  o: recovering abandoned branches
     (use 'git branch <branch name> <commit hash>')

""".strip()

ARCYD_ABANDONED_REF = "{}/abandoned".format(_ARCYD_REFSPACE)
_ARCYD_ABANDONED_BRANCH = "{}/abandoned".format(_PRIVATE_ARCYD_BRANCHSPACE)
ARCYD_ABANDONED_BRANCH_FQ = "refs/heads/" + _ARCYD_ABANDONED_BRANCH


class Repo(object):

    def __init__(
            self, refcache_repo, differ_cache, remote, description):
        """Initialise a new Repo.

        :repo: a callable supporting git commands, e.g. repo("status")
        :remote: name of the remote to use
        :description: short identification of the repo for humans
        :returns: None

        """
        super(Repo, self).__init__()
        self._repo = refcache_repo
        self._remote = remote
        self._description = description
        self._is_landing_archive_enabled = None
        self._differ_cache = differ_cache

    def is_identical(self, branch1, branch2):
        """Return True if the branches point to the same commit.

        :branch1: string name of branch
        :branch2: string name of branch
        :returns: True if the branches point to the same commit

        """
        return phlgit_branch.is_identical(self, branch1, branch2)

    def _is_ref(self, ref):
        """Return True if the specified ref exists, otherwise False.

        :ref: the string name of the ref to look up
        :return: True if the specified ref exists, otherwise False

        """
        ref_names = phlgit_showref.names(self)
        return ref in ref_names

    def get_remote_branches(self):
        """Return a list of string names of remote branches.

        :returns: list of string names

        """
        return phlgit_branch.get_remote(self, self._remote)

    def checkout_forced_new_branch(self, new_name, based_on):
        """Overwrite and checkout 'new_name' as a new branch from 'based_on'.

        :new_name: the string name of the branch to create and overwrite
        :based_on: the string name of the branch to copy
        :returns: None

        """
        phlgit_checkout.new_branch_force_based_on(
            self, new_name, based_on)

    # TODO: split this into more functions with varying context
    def raw_diff_range(self, base, to, context=None):
        """Return a string of the unified diff between 'base' and 'to'.

        Note that the output is based on 'git diff base...to', so the commits
        are diff'ed via thier common ancestry.

        :base: the commit or branch name to start from
        :to: the commit or branch name to end with
        :context: integer amount of surrounding context to include
        :returns: string of the unified diff

        """
        return phlgit_diff.raw_diff_range(self, base, to, context)

    def get_range_hashes(self, start, end):
        """Return a list of strings of commit hashes from 'start' to 'end'.

        The list begins with the revision closest to but not including
        'start'.  Raise a ValueError if any of the returned values are not
        valid hexadecimal.

        :start: a reference that log will understand
        :end: a reference that log will understand
        :returns: a list of strings of commit hashes from 'start' to 'end'.

        """
        return phlgit_log.get_range_hashes(self, start, end)

    def make_revisions_from_hashes(self, hashes):
        """Return a list of 'phlgit_log__Revision' from 'hashes'.

        Raise an exception if the repo does not return a valid FullMessage
        from any of 'hashes'.

        :hashes: a list of commit hash strings
        :returns: a list of 'phlgit_log__Revision'

        """
        return phlgit_log.make_revisions_from_hashes(self, hashes)

    def squash_merge(self, branch, message, author_name, author_email):
        """Return output from Git performing a squash merge.

        :branch: string name of branch to merge into HEAD
        :message: string message for the merge commit
        :author_name: string name of author for the merge commit
        :author_email: string email of author for the merge commit
        :returns: string of Git output

        """
        # TODO: test that the author is set correctly
        return phlgit_merge.squash(
            self,
            branch,
            message,
            author_name + " <" + author_email + ">")

    def _checkout_archive_ref_branch(
            self, short_branch_name, fq_branch_name, initial_message):

        if self._is_ref(fq_branch_name):
            phlgit_checkout.branch(self, short_branch_name)
        else:
            phlgit_checkout.orphan_clean(self, short_branch_name)
            phlgit_commit.allow_empty(self, initial_message)

    def archive_to_landed(
            self, review_hash, review_branch, base_branch, land_hash, message):
        """Merge the specified review branch to the 'landed' archive branch.

        :review_hash: the string of the commit hash to archive
        :review_branch: the string name of the branch to archive
        :base_branch: the string name of the branch the review is branched off
        :land_hash: the string of the commit hash the branch landed with
        :message: the string commit message the the branch landed with
        :returns: None

        """
        self._checkout_archive_ref_branch(
            _ARCYD_LANDED_BRANCH,
            ARCYD_LANDED_BRANCH_FQ,
            _LANDED_ARCHIVE_BRANCH_MESSAGE)

        new_message = "landed {} on {} as {}\n\nwith message:\n{}".format(
            review_branch, base_branch, land_hash, message)

        phlgit_merge.ours(self, review_hash, new_message)

    def push_landed(self):
        """Push the 'landed' archive branch to the remote.

        :returns: None

        """
        self.push_asymmetrical(ARCYD_LANDED_BRANCH_FQ, ARCYD_LANDED_REF)

    def archive_to_abandoned(
            self, review_hash, review_branch, base_branch):
        """Merge the specified review branch to the 'abandoned' archive branch.

        :review_hash: the string of the commit hash to archive
        :review_branch: the string name of the branch to archive
        :base_branch: the string name of the branch the review is branched off
        :returns: None

        """
        # get on the archive branch, create new orphan if necessary
        self._checkout_archive_ref_branch(
            _ARCYD_ABANDONED_BRANCH,
            ARCYD_ABANDONED_BRANCH_FQ,
            _ABANDONED_ARCHIVE_BRANCH_MESSAGE)

        new_message = "abandoned {}, branched from {}".format(
            review_branch, base_branch)

        phlgit_merge.ours(self, review_hash, new_message)

    def push_abandoned(self):
        """Push the 'abandoned' archive branch to the remote.

        :returns: None

        """
        self.push_asymmetrical(
            ARCYD_ABANDONED_BRANCH_FQ, ARCYD_ABANDONED_REF)

    def push_asymmetrical(self, local_branch, remote_branch):
        """Push 'local_branch' as 'remote_branch' to the remote.

        :local_branch: string name of the branch to push
        :remote_branch: string name of the branch on the remote
        :returns: None

        """
        phlgit_push.push_asymmetrical(
            self, local_branch, remote_branch, self._remote)

    def push(self, branch):
        """Push 'branch' to the remote.

        :branch: string name of the branch to push
        :returns: None

        """
        phlgit_push.push(self, branch, self._remote)

    def push_delete(self, branch, *args):
        """Delete 'branch' from the remote.

        :branch: string name of the branch
        :*args: (optional) more string names of branches
        :returns: None

        """
        phlgit_push.delete(self, self._remote, branch, *args)

    def checkout_master_fetch_prune(self):
        """Checkout master, fetch from the remote and prune branches.

        Please see checkout_master_fetch_special_refs() for why we must
        checkout master first.

        :returns: None

        """
        checkout_master_fetch_special_refs(self, self._remote)

    @property
    def hash_ref_pairs(self):
        """Return a list of (sha1, name) tuples from the repo's list of refs.

        :repo: a callable supporting git commands, e.g. repo("status")
        :returns: a list of (sha1, name)

        """
        return self._repo.hash_ref_pairs

    def checkout_make_raw_diff(
            self, from_branch, to_branch, max_diff_size_utf8_bytes):
        """Return an abdt_differ.DiffResult of the changes on the branch.

        If the diff would exceed the pre-specified max diff size then take
        measures to reduce the diff.

        Potentially checkout onto the 'to_branch' so that changes to
        .gitattributes files will be considered.

        :from_branch: string name of the merge-base of 'branch'
        :to_branch: string name of the branch to diff
        :max_diff_size_utf8_bytes: the maximum allowed size of the diff as utf8
        :returns: the string diff of the changes on the branch

        """
        return self._differ_cache.checkout_make_raw_diff(
            from_branch, to_branch, max_diff_size_utf8_bytes)

    def _log_read_call(self, args, kwargs):
        with abdt_logging.remote_io_read_event_context(
                'git-{}'.format(args[0]),
                '{}: {} {}'.format(
                    self._description, ' '.join(args), kwargs)):
            return self._repo(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if args:
            if args[0] == 'push':
                with abdt_logging.remote_io_write_event_context(
                        'git-push',
                        '{}: {} {}'.format(
                            self._description, ' '.join(args), kwargs)):
                    return self._repo(*args, **kwargs)
            elif args[0] in ('fetch', 'pull', 'ls-remote'):
                # N.B. git-archive may also read but we're not using it
                return self._log_read_call(args, kwargs)
            elif len(args) >= 2 and args[:2] == ('remote', 'prune'):
                return self._log_read_call(args, kwargs)

        return self._repo(*args, **kwargs)

    def get_remote(self):
        return self._remote


class DifferResultCache(object):

    def __init__(self, refcache_repo):
        super(DifferResultCache, self).__init__()
        self._diff_results = {}
        self._repo = refcache_repo

    def get_cache(self):
        return self._diff_results

    def set_cache(self, cache):
        self._diff_results = cache

    def checkout_make_raw_diff(
            self, from_branch, to_branch, max_diff_size_utf8_bytes):
        """Return an abdt_differ.DiffResult of the changes on the branch.

        If the diff would exceed the pre-specified max diff size then take
        measures to reduce the diff.

        Potentially checkout onto the 'to_branch' so that changes to
        .gitattributes files will be considered.

        :from_branch: string name of the merge-base of 'branch'
        :to_branch: string name of the branch to diff
        :max_diff_size_utf8_bytes: the maximum allowed size of the diff as utf8
        :returns: the string diff of the changes on the branch

        """
        # checkout the 'to' branch, otherwise we won't take into account any
        # changes to .gitattributes files
        from_ref, to_ref = self._refs_to_hashes((from_branch, to_branch))
        phlgit_checkout.branch(self._repo, to_ref)
        return abdt_differ.make_raw_diff(
            self._repo,
            from_branch,
            to_branch,
            max_diff_size_utf8_bytes)

    def _refs_to_hashes(self, ref_list):
        hash_ref_pairs = self._repo.hash_ref_pairs
        ref_to_hash = dict(((r, h) for h, r in hash_ref_pairs))
        return (ref_to_hash[ref] for ref in ref_list)


def _get_branch_to_hash(repo):

    remote = repo.get_remote()
    hash_ref_list = repo.hash_ref_pairs

    def is_remote(ref):
        return phlgitu_ref.is_under_remote(ref, remote)

    # XXX: can't use dictionary comprehensions until the linters don't complain
    full_to_short = phlgitu_ref.fq_remote_to_short_local
    branch_to_hash = dict([
        (full_to_short(r), h) for h, r in hash_ref_list if is_remote(r)
    ])

    return branch_to_hash


def get_managed_branches(repo, repo_desc, naming, branch_link_callable=None):
    branch_to_hash = _get_branch_to_hash(repo)
    branch_pairs = abdt_naming.get_branch_pairs(branch_to_hash.keys(), naming)

    managed_branches = []
    lander = abdt_lander.squash

    for b in branch_pairs:
        branch_url = None
        review_branch = b.review
        tracker_branch = b.tracker
        assert review_branch is not None or tracker_branch is not None

        review_hash = None
        tracker_hash = None

        if review_branch is not None:
            review_hash = branch_to_hash[review_branch.branch]
            if branch_link_callable:
                branch_url = branch_link_callable(review_branch.branch)

        if tracker_branch is not None:
            tracker_hash = branch_to_hash[tracker_branch.branch]

        managed_branches.append(
            abdt_branch.Branch(
                repo,
                review_branch,
                review_hash,
                tracker_branch,
                tracker_hash,
                lander,
                repo_desc,
                branch_url))

    return managed_branches


def checkout_master_fetch_special_refs(repo, remote):
    # fetch the 'landed' and 'abandoned' refs, if they exist

    # We must checkout master before fetching the special refs to the
    # local branches. Otherwise we might be attempting to overwrite the
    # current branch with fetch, which would fail.
    phlgit_checkout.branch(repo, 'master')

    branch_refspec = '+refs/heads/*:refs/remotes/origin/*'
    arcyd_refspec = '+{refspace}/*:refs/heads/{branchspace}/*'.format(
        refspace=_ARCYD_REFSPACE, branchspace=_PRIVATE_ARCYD_BRANCHSPACE)
    refspec_list = [branch_refspec, arcyd_refspec]

    phlgit_fetch.prune_safe(repo, remote, refspec_list)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
