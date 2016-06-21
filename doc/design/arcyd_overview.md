Arcyd overview
==============

Arcyd is a daemon to watch git repos, create and land Phabricator revisions
automatically.

The intention is to make it easy for large teams to start using Differential
without individual contributors needing to install and configure Arcanist -
they only need to interact with Git.

Individual contributors are still free to use Arcanist, Arcyd provides a
zero-config layer over Git to get them started.

Arcyd does the following:
- Watches for specially named branches and automatically creates revisions
- Automatically updates revisions when the branch changes
- Automatically lands revisions when they are approved

Minimal user workflow:

```
$ git checkout mywork
~ commit some work on the branch ~
$ git push origin feature/mywork:r/master/mywork

.. Arcyd see's the 'r/master/mywork' branch and creates a review ..
.. Reviewer accepts the change ..
.. Arcyd squashes the 'r/master/mywork' branch onto master and deletes it ..
```

Interactions
------------

In the following diagram you can see that the author of a revision interacts
with Phabricator indirectly first, pushing to the Git server which Arcyd is
watching.  Arcyd will create a new Phabricator revision if a new review branch
is observed on the Git server. It will update the same Phabricator revision if
the review branch is updated.

```
Author (Git client) <--> Git server <--> Arcyd <--> Phabricator <-- Reviewer (web)
                                                        ^
                                                        `Author (web)
```

The author also interacts with Phabricator directly via the web interface. If
the author sets the review to be 'abandoned' then Arcyd will archive the Git
branch after a reasonable grace period.

The reviewer interacts with Phabricator directly via the web interface. If the
reviewer accepts the revision then Arcyd will land it by squashing the review
branch onto the destination branch, removing the review branch and closing the
review.

If there are merge conflicts when squashing onto the destination branch then
Arcyd will set the Phabricator revision to 'Needs Revision' and prompt the
author to update the review such that it will merge cleanly. The reviewer will
then need to accept the changes again.

Setup
-----

### Pre-requisites

To start an Arcyd instance, you will need the following software installed:

- Linux / UNIX
- Git client
- Python 2.7

You will of course also need to be able to reach these services:

- Your Git server (e.g. Phabricator, Gitolite, local fs, ...)
- Your Phabricator instance

You will also need a Phabricator user for Arcyd to run as, probably called
'arcyd' or similar.

### Optional dependencies

As an administrator, it can be useful to get email notifications from Arcyd.
For example in the case where Phabricator or Git become unavailable. In this
case you will need 'sendmail' configured on the machine.

### Installation

At the time of writing, the phabricator-tools repository does not provide any
Python packages. Instead you can simply get a local clone and add the
`proto/arcyd` binary to your `$PATH`.

### Configuration

Arcyd insists on storing it's configuration in a Git repository, the aim is to
make replication possible using the existing dependencies (Git client and
server), and also to encourage versioning of configuration changes.

Use the [`arcyd init`](../man/arcyd/arcyd_init.generated.txt) command to start
a new repository with some basic configuration.

...

Disaster recovery
-----------------

In the event of the loss of the Arcyd machine ... Arcyd only caches
repositories locally, all state is stored on the Git Server and in Phabricator
...

Inspection
----------

### Log files
### Special branches
### Special refs
### Phabricator user
