# abd
* `abdcmd_addphabricator.py` -
Make a new phabricator instance known to the Arcyd instance.
* `abdcmd_addrepo.py` -
Add a new repository for the Arcyd instance to manage.
* `abdcmd_arcyd.py` -
Arcyd - daemon to watch git repos, create and land reviews automatically.
* `abdcmd_arcydstatushtml.py` -
Render arcyd status file as meaningful html to present to users.
* `abdcmd_devstatushtml.py` -
Help develop status pages by providing simulating various statuses.
* `abdcmd_init.py` -
Create a new arcyd instance in working dir, with backing git repository.
* `abdcmd_instaweb.py` -
Start a local webserver to report the status of an arcyd instance.
* `abdcmd_processrepos.py` -
Command to process multiple repos.
* `abdcmd_repostatushtml.py` -
Render status files as meaningful html to present to users.
* `abdcmd_start.py` -
Start the arcyd instance for the current directory, if not already going.
* `abdcmd_stop.py` -
Stop the arcyd instance for the current directory.
* `abdcmnt_commenter.py` -
Make pre-defined comments on Differential revisions.
* `abdi_processargs.py` -
Process the arguments for a single repository and execute.
* `abdi_processrepo.py` -
abd automates the creation and landing of reviews from branches.
* `abdmail_mailer.py` -
Send mails to interested parties about pre-specified conditions.
* `abdt_arcydreporter.py` -
Report the state of arcyd as it updates repositories.
* `abdt_branch.py` -
Implement operations for branch-based reviews.
* `abdt_branchmock.py` -
Implement mocked operations for branch-based reviews.
* `abdt_branchtester.py` -
Test suite for abdt_branch-like things.
* `abdt_classicnaming.py` -
Branch naming conventions for 'arcyd-review/description/base' style.
* `abdt_compositenaming.py` -
Composite multiple naming schemes by chaining them together.
* `abdt_conduit.py` -
Abstraction for Arcyd's conduit operations.
* `abdt_conduitgit.py` -
Operations combining conduit with git.
* `abdt_conduitmock.py` -
Abstraction for Arcyd's conduit operations.
* `abdt_differ.py` -
Generate git diffs between branches suitable for Differential reviews.
* `abdt_errident.py` -
"A global list of error identifiers that may be used.
* `abdt_exception.py` -
Exception hierarchy for abd user and system errors.
* `abdt_fs.py` -
Arcyd-specific interactions with the filesystem.
* `abdt_git.py` -
Abstraction for Arcyd's git operations.
* `abdt_lander.py` -
Callables for re-integrating branches upstream.
* `abdt_landinglog.py` -
Operations for maintaining a list of landed branches in upstream repo.
* `abdt_logging.py` -
Log important events appropriately from anywhere in Arcyd.
* `abdt_naming.py` -
Naming conventions for abd.
* `abdt_namingtester.py` -
Test suite for abdt naming convention classes.
* `abdt_rbranchnaming.py` -
Branch naming conventions for 'r/base/description' style.
* `abdt_repoconfig.py` -
Per-repository configuration.
* `abdt_repooptions.py` -
Per-repository configuration options.
* `abdt_reporeporter.py` -
Report the state of a repository.
* `abdt_shareddictoutput.py` -
Provide equivalent classes that write dictionaries to shared resources.
* `abdt_tryloop.py` -
Retry operations that may intermittently fail, log each failure.
* `abdt_userwarning.py` -
Hierarchy of warnings to feed back to users.
* `abdweb_arcydcontent.py` -
Render html to report the state of a running instance of Arcyd.
* `abdweb_htmlformatter.py` -
Provide useful utilities for formatting html.
* `abdweb_page.py` -
Render the outline of an Arcyd report page, with inline CSS, JS etc.
* `abdweb_repocontent.py` -
Render html to report the state of a repository watched by Arcyd.

-----
*please note: this file is generated, edits will be lost*
