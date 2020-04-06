CHANGELOG
=========

All notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog`_, and this project adheres to
`Semantic Versioning`_.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. Hyperlinks for releases

.. _Unreleased: https://github.com/gabor-boros/hammurabi/compare/v0.5.0...master
.. _0.1.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.0
.. _0.1.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.1
.. _0.1.2: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.2
.. _0.2.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.2.0
.. _0.3.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.3.0
.. _0.3.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.3.1
.. _0.4.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.4.0
.. _0.5.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.5.0

Unreleased
----------

Added
~~~~~

* New precondition ``IsOwnedBy`` / ``IsNotOwnedBy``
* New precondition ``HasMode`` / ``HasNoMode``
* New precondition ``IsDirectoryExists`` / ``IsDirectoryNotExists``
* New precondition ``IsFileExists`` / ``IsFileNotExists``
* New precondition ``IsLineExists`` / ``IsLineNotExists``
* Add preconditions for ``Law`` class

Changed
~~~~~~~

* Added return value type hint to ``pre_task_hook``
* ``_get_by_selector`` / ``_set_by_selector`` became public methods (``get_by_selector`` / ``set_by_selector``)

0.5.0_ - 2020-03-31
-------------------

Fixed
~~~~~

* Add untracked files as well to the index

Removed
~~~~~~~

* Remove lock file creation since it is useless

0.4.0_ - 2020-03-31
-------------------

Added
~~~~~

* Added ``Reporter`` and ``JSONReporter`` classes to be able to expose execution results
* Add new config option ``report_name`` to the available settings
* New exception type ``PreconditionFailedError`` indicating that the precondition failed and no need to raise an error

Changed
~~~~~~~

* Make sure children and pipe can be set at the same time
* Simplify yaml key rename logic
* ``SectionRenamed`` not raises error if old section name is not represented but the new one
* ``OptionRenamed`` not raises error if old option name is not represented but the new one
* ``LineReplaced`` not raises error if old line is not represented but the new one
* Remove redundant way of getting rules of a law (https://github.com/gabor-boros/hammurabi/issues/45)
* GitHub mixin now returns the URL of the open PR's URL; if an existing PR found, that PR's URL will be returned
* Pillar prepare its Reporter for report generation
* Pillar has a new argument to set the pillar's reporter easily
* CLI's enforce command now calls the Pillar's prepared Reporter to do the report
* "No changes made by" messages now info logs instead of warnings
* Commit changes only if the Law has passing rules
* If ``PreconditionFailedError`` raised, do not log error messages, log a warning instead
* ``LineExists`` will not raise an exception if multiple targets found, instead it will select the last match as target
* Have better PR description formatting

Fixed
~~~~~

* Fixed a dictionary traversal issue regarding yaml file support
* Fixed "Failed Rules" formatting of PR description by removing ``\xa0`` character
* Fixed no Rule name in PR description if the Law did not change anything issue
* Fixed nested rule indentation PR description markup
* Fixed an issue with ``LineReplaced``, if the input file is empty, raise an exception

0.3.1_ - 2020-03-26
-------------------

Fixed
~~~~~

* Make sure the lost ini file fix is back lost by merge conflict resolution

0.3.0_ - 2020-03-25
-------------------

Added
~~~~~

* Add Yaml file support (https://github.com/gabor-boros/hammurabi/pull/24)

Changed
~~~~~~~

* Make sure ``SectionExists`` adds the section even if no target given (https://github.com/gabor-boros/hammurabi/pull/21)
* Apply PEP-561 (https://github.com/gabor-boros/hammurabi/pull/19)

Fixed
~~~~~

* Fixed an ini section rename issue (https://github.com/gabor-boros/hammurabi/pull/24)

Removed
~~~~~~~

* Updated CONTRIBUTING.rst to remove the outdated stub generation

0.2.0_ - 2020-03-23
--------------------

Added
~~~~~

* Render files from Jinja2 templates (``TemplateRendered`` rule)
* Add new ``Precondition`` base class (https://github.com/gabor-boros/hammurabi/pull/9)
* Add Code of Conduct to meet community requirements (https://github.com/gabor-boros/hammurabi/pull/10)
* New section in the documentations for ``Rules`` and ``Preconditions`` (https://github.com/gabor-boros/hammurabi/pull/11)
* Collect failed rules for every law (``Law.failed_rules``) (https://github.com/gabor-boros/hammurabi/pull/13)
* Add chained rules to PR body (https://github.com/gabor-boros/hammurabi/pull/13)
* Add failed rules to PR body (https://github.com/gabor-boros/hammurabi/pull/13)
* Throw a warning when no GitHub client is initialized (https://github.com/gabor-boros/hammurabi/pull/13)
* Raise runtime error when no GitHub client is initialized, but PR creation called (https://github.com/gabor-boros/hammurabi/pull/13)
* Guess owner/repository based on the origin url of the working directory (https://github.com/gabor-boros/hammurabi/pull/13)

Changed
~~~~~~~

* Add stub formatting to Makefile's `stubs` command
* Extract common methods of ``Precondition`` and ``Rule`` to a new ``AbstractRule`` class (https://github.com/gabor-boros/hammurabi/pull/9)
* Extended CONTRIBUTING guidelines to include a notice for adding ``Rules`` and ``Preconditions`` (https://github.com/gabor-boros/hammurabi/pull/11)
* Refactor package structure and extract preconditions to separate submodule (https://github.com/gabor-boros/hammurabi/pull/11)
* Pull request body generation moved to the common ``GitMixin`` class (https://github.com/gabor-boros/hammurabi/pull/13)
* Pillar will always create lock file in the working directory (https://github.com/gabor-boros/hammurabi/pull/13)
* Call expandvar and expanduser of configuration files (https://github.com/gabor-boros/hammurabi/pull/13)
* Hammurabi only works in the current working directory (https://github.com/gabor-boros/hammurabi/pull/13)
* Read settings (pyproject.toml) path from ``HAMMURABI_SETTINGS_PATH`` environment variable (https://github.com/gabor-boros/hammurabi/pull/13)
* Fix version handling in docs

Fixed
~~~~~

* Remove faulty author of git committing (https://github.com/gabor-boros/hammurabi/pull/13)
* Only attempt to create a PR if there is no PR from Hammurabi (https://github.com/gabor-boros/hammurabi/pull/13)
* Fix double committing issue (https://github.com/gabor-boros/hammurabi/pull/13)
* Fix committing of laws when nothing changed (https://github.com/gabor-boros/hammurabi/pull/13)
* Fixed several CLI arguments related issues (https://github.com/gabor-boros/hammurabi/pull/13)
* Fixed a typo in the Bug issue template of GitHub (https://github.com/gabor-boros/hammurabi/pull/13)

Removed
~~~~~~~

* Removed target directory setting from config and CLI (https://github.com/gabor-boros/hammurabi/pull/13)

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
