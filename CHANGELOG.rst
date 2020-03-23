CHANGELOG
=========

All notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog`_, and this project adheres to
`Semantic Versioning`_.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

Unreleased_
--------------------

Added
~~~~~

* Render files from Jinja2 templates (``TemplateRendered`` rule)
* Add new ``Precondition`` base class (https://github.com/gabor-boros/hammurabi/pull/9)
* Add Code of Conduct to meet community requirements (https://github.com/gabor-boros/hammurabi/pull/10)
* New section in the documentations for ``Rules`` and ``Preconditions`` (https://github.com/gabor-boros/hammurabi/pull/11)
* Collect failed rules for every law (``Law.failed_rules``) (https://github.com/gabor-boros/hammurabi/pull/12)
* Add chained rules to PR body (https://github.com/gabor-boros/hammurabi/pull/12)
* Add failed rules to PR body (https://github.com/gabor-boros/hammurabi/pull/12)

Changed
~~~~~~~

* Add stub formatting to Makefile's `stubs` command
* Extract common methods of ``Precondition`` and ``Rule`` to a new ``AbstractRule`` class (https://github.com/gabor-boros/hammurabi/pull/9)
* Extended CONTRIBUTING guidelines to include a notice for adding ``Rules`` and ``Preconditions`` (https://github.com/gabor-boros/hammurabi/pull/11)
* Refactor package structure and extract preconditions to separate submodule (https://github.com/gabor-boros/hammurabi/pull/11)
* Pull request body generation moved to the common ``GitMixin`` class (https://github.com/gabor-boros/hammurabi/pull/12)
* Pillar will always create lock file in the working directory (https://github.com/gabor-boros/hammurabi/pull/12)

Fixed
~~~~~

* Remove faulty author of git committing (https://github.com/gabor-boros/hammurabi/pull/12)
* Only attempt to create a PR if there is no PR from Hammurabi (https://github.com/gabor-boros/hammurabi/pull/12)
* Fix double committing issue (https://github.com/gabor-boros/hammurabi/pull/12)

0.1.2_ - 2020-03-18
--------------------

Changed
~~~~~~~

* Extended Makefile to generate stubs
* Extend documentation how to generate and update stubs
* Update how to release section of CONTRIBUTING.rst

0.1.1_ - 2020-03-17
--------------------

Changed
~~~~~~~

* Moved unreleased section of CHANGELOG to the top
* Updated changelog entries to contain links for release versions
* Updated CONTRIBUTING document to mention changelog links
* Refactored configuration handling (https://github.com/gabor-boros/hammurabi/pull/5)

Fixed
~~~~~

* Fixed wrong custom rule example in the README
* Smaller issues around git committing and pushing (https://github.com/gabor-boros/hammurabi/pull/5)

0.1.0_ - 2020-03-12
--------------------

Added
~~~~~

* Basic file manipulations
    * Create file
    * Create files
    * Remove file
    * Remove files
    * Empty file

* Basic directory manipulations
    * Create directory
    * Remove directory
    * Empty directory

* Basic file and directory operations
    * Change owner
    * Change mode
    * Move file or directory
    * Copy file or directory
    * Rename file or directory

* Plain text/general file manipulations
    * Add line
    * Remove line
    * Replace line

* INI file specific manipulations
    * Add section
    * Remove section
    * Rename section
    * Add option
    * Remove option
    * Rename option

* Miscellaneous
    * Initial documentation
    * CI/CD integration

.. Hyperlinks for releases

.. _Unreleased: https://github.com/gabor-boros/hammurabi/compare/v0.1.2...master
.. _0.1.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.0
.. _0.1.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.1
.. _0.1.2: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.2

.. EXAMPLE CHANGELOG ENTRY

    0.1.0_ - 2020-01-xx
    --------------------

    Added
    ~~~~~

    * TODO.

    Changed
    ~~~~~~~

    * TODO.

    Fixed
    ~~~~~

    * TODO.

    Removed
    ~~~~~~~

    * TODO
