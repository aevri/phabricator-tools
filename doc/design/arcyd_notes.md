# Arcyd Quickstart

Arcyd removes the need for using the 'arc' command-line tool to interact with Phabricator.

Arcyd only works with Git.  It relies on efficient branching to enhance your workflow.
## Project Objectives

* Remove the need for setting up, configuring and learning 'Arcanist'
* Automate landing of changes when they pass review
* Configure linters for everyone in one place

## Basic Workflow

Here is an example of what a typical workflow might look like:

   ```
$ git checkout -b feature/mywork HEAD
# ~ do your work ~
# ~ commit (use Phabricator message format, see below) ~
$ git push origin feature/mywork:r/master/mywork
 
# .. daemon creates review ..
# .. reviewer asks for changes ..
 
$ git checkout r/master/mywork
# ~ make requested changes ~
$ git commit ...  # use appropriate message
$ git push origin r/master/mywork  # arcyd will figure out the review to update
 
# .. reviewer accepts revision ..
# .. daemon automatically lands revision (squash) ..
# .. daemon removes r/master/mywork ..
```
__NOTES:__
* Squashing

   Arcyd currently squashes review branches when landing, this behavior doesn't suit all use cases.
   Support for other integration strategies is planned but not yet implemented.
   Please see jevr.git_integration_strategies for examples of other integration strategies.
* Auto-archiving abandoned reviews

   If you abandon a review, arcyd will archive the review branch for you "after a while" (roughly a day at time of writing). 
   See the 'advanced' sections below for details of where it gets archived to.
   
## Branch naming

Arcyd relies on a special branch naming convention in order to discover which branches to create reviews from and where they should land.

e.g. __r/base/branch/description__

Where:

__r__ Always starts with 'r/'.

__base/branch__ The branch we'll diff against and land onto if the review is accepted.
Note that this can be many 'sections', e.g. 'release / 2013_Apr'

__description__ You get one 'section' to describe your change.
Please use '_' or '-' or camelCase to join multiple words.

## Commit messages

In order to fill out the review page correctly, Arcyd expects your commit messages to be in the same format that Arcanist uses.
(Arcyd sends the commit messages to Phabricator to parse and receives the fields back)

There are a number of 'fields' that Arcyd will recognize in the commit messages:

|field|mandatory?|
|-----|----------|
|title|mandatory|
|summary|optional|
|test plan|mandatory|
|reviewers|optional|
|maniphest tasks|optional|

The 'title' field of the message is automatically taken from the first line of a commit.
The 'summary' field of the message is automatically taken from the 'body' of the commit.

For example:
```
This is the title
 
This is the summary / body, note that the second line is always blank.
 
This is also taken as part of the summary as it is considered as part of the 'body' of
the message.
 
Test Plan: this can be all on one line if you want
Reviewers: one-or-many-unix-names separated-by-spaces
```

__Notes:__

* Please see Tim Pope's 'A note about git commit messages' for some background on the 'subject / body' distinction.
* Reviewers must be already registered in your Phabricator instance. To register, they simply need to log in.

Only the last commit on a branch is used to determine the fields to create a review. You might find ```git commit --allow-empty``` useful for tacking an empty commit with a well-formed message on the end of your branch.

## Advanced: Cleaning up local branches

Arcyd maintains a 'landed archive' which preserves your original branches before they landed, you can use this to clean your local copies of landed branches.
 

```
# Fetch the 'landed archive' (do this each time)
$ git fetch origin refs/arcyd/landed:refs/arcyd/landed 
 
# List the local branches which are merged into the landed archive
$ git branch --merged refs/arcyd/landed
 
# If that list looks good, forcibly remove the branches
$ git branch --merged refs/arcyd/landed | xargs git branch -D
```
 
Note that similarly for abandoned branches, you may fetch 'refs/arcyd/abandoned' and operate on it in the same way as 'refs/arcyd/landed'.

## Advanced: Arcyd's personal page

You can see Arcyd's recent activities on Phabricator by visiting it's
'/p/arcyd' page, this can be pretty handy for tracking down stray reviews.  For
example, to see Arcyd's activity on the 'all.phab' instance, you can go here:
https://myphab.example/p/arcyd/ 

## Advanced: Arcyd's 'reserve' branch

Arcyd stores the state of your reviews under 'dev/arcyd/*' so that only Arcyd
and the CREATOR used in Gitolite may edit what's there. Before it stores any
state it first creates a a branch 'dev/arcyd/reserve'. This is to ensure that
attempts to push branches to 'dev/arcyd/*' will succeed.

This means that if the 'dev/arcyd/reserve' branch exists then the repository
was added to Arcyd at some point. The branch is not currently removed if the
repository was removed from Arcyd's control, at the time of writing only a
handful of repositories have been removed so it's not likely that this is the
case for you.

## Advanced: Arcyd's tracker branches

The point of Arcyd is that reviews should be magically created, updated and
closed without you needing to think about how.

Rarely, things can go wrong. Knowing about Arcyd's tracker branches can help
you work out what's happening.

When you push a branch 'r/master/myfeature' to your repository, Arcyd will push
a branch like 'dev/arcyd/trackers/rbranch/--/-/ok/r/master/myfeature/7992' to
your repo to track it. This branch name stores the entire state of the review
from Arcyd's point of view.

Here's how that tracker branch name breaks down:
dev/arcyd/trackers/rbranch/--/-
ok
r/master/myfeature
7992
All 'r/branch' trackers
start with this prefix	status	your branch name	the review id or 'none'

See here for implementation details:

https://github.com/bloomberg/phabricator-tools/blob/master/py/abd/abdt_rbranchnaming.py#L28 

Note that the old-style 'arcyd-review/myfeature/master' tracker branches have a
difference format, which is not covered here.

Some things to note:
* Make sure you "git fetch --prune" before looking at trackers to ensure you have the latest versions. The '--prune' is important for removing branches already deleted remotely.
* You can get the review ID from the tracker branch name
* If the tracker does not exist then you know Arcyd has not created a review
* If the tracker does not point to the same revision as the 'r/master/myfeature' branch then Arcyd knows it must update the review
* The tracker is stored under 'dev/arcyd/*' so that only Arcyd and the CREATOR used in Gitolite may edit what's there. Generally you should not interfere with those!

There's a command-line tool 'barc' for analyzing a repositories tracker branches:

```
$ ~phab/bin/barc list --help
usage: barc list [-h]
                 [--format-summary | --format-json | --format-python | --format-string STR]
List the reviews and corresponding branches in the current repository.
optional arguments:
  -h, --help           show this help message and exit
 
... snip ...
```

Arcyd knows who the author of a branch is by looking at the author of the most
recent commit on the branch. If this email is not registered with the
Phabricator instance then Arcyd has no way of knowing who they are.

You can diagnose this by viewing the tracker branches

### Common problems: pushing a branch with no new commits

Sometimes people push a branch before they have made new commits on it, in this
case Arcyd does not know who the author should be.

It will assume that the previous author on the branch will be able to assist,
so it assigns the review to them and writes an explanatory note in there.

This is by far the biggest hole in the workflow, there are plans to improve it
by automatically commandeering reviews when a 'new' author pushes to a branch.

This means that if you push a branch before committing, someone else may get
assigned the review. If you push to the branch again with commits to review,
the review will be re-assigned to you automatically.

##  Troubleshooting: review not created after pushing r/ branch

## Addendum: What's with the name?

'Arcyd' breaks down like this:

|Arc|y|d|
|---|---|---|
|After `Arcanist`|It's basically Arcanist but in pYthon|It's a daemon (almost)|

You can pronounce it like 'orchid' but starting with an 'a' - 'archid'.
