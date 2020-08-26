CHANGELOG
=========

All notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog`_, and this project adheres to
`Semantic Versioning`_.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. Hyperlinks for releases

.. _Unreleased: https://github.com/gabor-boros/hammurabi/compare/v0.10.0...master
.. _0.1.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.0
.. _0.1.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.1
.. _0.1.2: https://github.com/gabor-boros/hammurabi/releases/tag/v0.1.2
.. _0.2.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.2.0
.. _0.3.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.3.0
.. _0.3.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.3.1
.. _0.4.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.4.0
.. _0.5.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.5.0
.. _0.6.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.6.0
.. _0.7.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.7.0
.. _0.7.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.7.1
.. _0.7.2: https://github.com/gabor-boros/hammurabi/releases/tag/v0.7.2
.. _0.7.3: https://github.com/gabor-boros/hammurabi/releases/tag/v0.7.3
.. _0.7.4: https://github.com/gabor-boros/hammurabi/releases/tag/v0.7.4
.. _0.8.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.8.0
.. _0.8.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.8.1
.. _0.8.2: https://github.com/gabor-boros/hammurabi/releases/tag/v0.8.2
.. _0.9.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.9.0
.. _0.9.1: https://github.com/gabor-boros/hammurabi/releases/tag/v0.9.1
.. _0.10.0: https://github.com/gabor-boros/hammurabi/releases/tag/v0.10.0

Unreleased_
-----------

Added
~~~~~

* Add references to external documentation site

Fixed
~~~~~

* Allow documentation generation for rules which are depending on extra packages
* Update enforce command description
* Fix failing pylint error W0707 in slack notification

Changed
~~~~~~~

* Rename all `target` to `match` as it shows the intention better
* Remove trailing "s" from preconditions starting with "Is"
* Extend the documentation of `DirectoryNotExists`
* Mention in the docs that `match` will use partial match if the regex is not specific enough
* Add László Üveges to maintainers
* Replace Travis CI with GitHub Actions
* Update the release process with the external documentation site

0.10.0_ - 2020-08-14
--------------------

Added
~~~~~

* Extended the the development installation instruction by adding pre-commit
* Add more tests for pillar

Fixed
~~~~~

* Set `__version__` to the latest tag to fix documentation generation

Changed
~~~~~~~

* CI/CD now executes `pre-commit run --all-files`
* Rename `LineReplaced`'s `target` parameter to `match` to reduce confusion
* Finetune pytest configuration by using classes named `*TestCase` instead of `Test*`
* Replace click based CLI with a Typer based one
* Use `latest` for local documentation generation
* Update CONTRIBUTING.md regarding documentation config version bump
* Include `main.py` in test reports and add tests

Removed
~~~~~~~

* `--rule-can-abort` is not an option anymore for enforce command
* Drop `get order` command since it is not used at all
* Drop `get laws` command since it is not used at all
* Drop `get law` command since it is not used at all
* Drop `get rules` command since it is not used at all
* Drop `get rule` command since it is not used at all
* Drop `describe law` command since it is not used at all
* Drop `describe rule` command since it is not used at all
* Remove hypothesis test reporting statistics generation

0.9.1_ - 2020-08-08
-------------------

Fixed
~~~~~

* Quick fix for a flipped condition when using allow_push

0.9.0_ - 2020-08-07
-------------------

Added
~~~~~

* Add new `allow_push` option to config to be able to turn on/off pushing to remote
* Extend the documentation with the new `allow_push` option
* Add `--push/--no-push` option to `enforce` command to control `allow_push` from CLI

Changed
~~~~~~~

* Pull request won't be opened if no changes were pushed to remote
* Bump ujson to 3.1.0
* Bump configupdater to 1.1.2

Fixed
~~~~~

* Fixed changelog hyperlinks

0.8.2_ - 2020-07-31
-------------------

Fixed
~~~~~

* GitHub API url is transformed to Pull Request URLs
* Fix import issues when importing a Rule which has a missing extras dependency

Changed
~~~~~~~

* Bump pydantic to 1.6.1
* Bump configupdater to 1.1.1
* Bump coverage to 5.2.1
* Bump pytest to 6.0.1
* Bump hypothesis to 5.21.0

0.8.1_ - 2020-07-20
-------------------

Fixed
~~~~~

* Fix GitHub API change caused issues when filtering opened PRs

0.8.0_ - 2020-07-15
-------------------

Added
~~~~~

* Extended the documentation with the new optional dependency install guide

Changed
~~~~~~~

* Make extra dependencies optional (introducing breaking changes)
* Simplify Slack notification sending and change its formatting to allow better customization

0.7.4_ - 2020-07-14
-------------------

Added
~~~~~

* Add ``git push`` notification hooks
* Add Slack notification

Changed
~~~~~~~

* Bump pydantic to 1.6
* Bump gitpython to 3.1.7
* Bump hypothesis to 5.19.2
* Bump coverage to 5.2
* Bump sphinx-rtd-theme to 0.5.0
* Bump mypy to 0.782
* Bump flake8 to 3.8.3
* Bump pylint to 2.5.3
* Bump ujson to 3.0.0
* Bump pyhocon to 0.3.55

0.7.3_ - 2020-05-25
-------------------

Fixed
~~~~~

* Fix updating existing pull request issue pt. 3

0.7.2_ - 2020-05-25
-------------------

Fixed
~~~~~

* Fix updating existing pull request issue pt. 2

0.7.1_ - 2020-05-22
-------------------

Fixed
~~~~~

* Fix recursive directory removal issue
* Fix updating existing pull request issue
* Fix wrong default value in config documentation

Changed
~~~~~~~

* Bump hypothesis to 5.15.1
* Bump toml to 0.10.1
* Bump flake8 to 3.8.1
* Bump pylint to 2.5.2

0.7.0_ - 2020-04-28
-------------------

Added
~~~~~

* Implement ``__repr`` and ``__str__`` for ``Law``, ``Rule`` and ``Precondition`` objects
* Add logging related configuration options to customize logging
* Add dictionary parsed rules as a base for YAML and JSON rules
* Extend the documentations by the new dictionary rules
* Add community discord link

Changed
~~~~~~~

* Unify log message styles
* Adjust logging levels
* Use dictionary parsed rules as a base for YAML and JSON rules
* Reduced the method complexity of ``DictValueExists`` and ``DictValueNotExists`` rules
* Reduced the method complexity of ``Rule`` execution
* Reduced the method complexity of ``Law`` execution
* Reduced the method complexity of ``LineExists`` task execution
* Reduced the method complexity of ``SectionExists`` task execution
* Improve ``LineExists`` rule to make sure text can be added at the end of file even the file has no trailing newline
* Bump click to 7.1.2
* Bump pylint to 2.5.0
* Bump pydantic to 1.5.1
* Bump hypothesis to 5.10.4
* Bump jinja2 to 2.11.2
* Bump coverage to 5.1
* Bump gitpython to 3.1.1

Removed
~~~~~~~

* Remove ``criteria`` fields since Hammurabi now supports preconditions and it breaks the API uniformity

0.6.0_ - 2020-04-06
-------------------

Added
~~~~~

* New precondition ``IsOwnedBy`` / ``IsNotOwnedBy``
* New precondition ``HasMode`` / ``HasNoMode``
* New precondition ``IsDirectoryExists`` / ``IsDirectoryNotExists``
* New precondition ``IsFileExists`` / ``IsFileNotExists``
* New precondition ``IsLineExists`` / ``IsLineNotExists``
* Add preconditions for ``Law`` class
* Add JSON file support

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
