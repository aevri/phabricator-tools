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

...

Inspection
----------

### Log files
### Special branches
### Special refs
### Phabricator user
