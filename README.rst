Hammurabi
*********

.. image:: https://img.shields.io/pypi/v/hammurabi.svg
    :target: https://pypi.python.org/pypi/hammurabi
    :alt: PyPi Package

.. image:: https://travis-ci.org/gabor-boros/hammurabi.svg?branch=master
    :target: https://travis-ci.org/gabor-boros/hammurabi
    :alt: Build Status

.. image:: https://readthedocs.org/projects/hammurabi/badge/?version=latest
    :target: https://hammurabi.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://api.codeclimate.com/v1/badges/bcebab7105dfd82f358b/maintainability
   :target: https://codeclimate.com/github/gabor-boros/hammurabi/maintainability
   :alt: Maintainability

.. image:: https://api.codeclimate.com/v1/badges/bcebab7105dfd82f358b/test_coverage
    :target: https://codeclimate.com/github/gabor-boros/hammurabi/test_coverage
    :alt: Test Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
    :alt: Black Formatted

.. image:: https://bestpractices.coreinfrastructure.org/projects/3587/badge
    :target: https://bestpractices.coreinfrastructure.org/projects/3587
    :alt: CII Best Practices


Mass changes made easy.

Hammurabi is an extensible CLI tool responsible for enforcing user-defined rules
on a git repository.

Features
========

Hammurabi integrates well with both git and Github to make sure that the
execution happens on a separate branch and the committed changes are pushed
to the target repository. After pushing to the target repository, a pull
request will be opened.

Hammurabi supports several operations (Rules) by default. These Rules can do

* file and directory operations like copy, move, create or delete
* manipulation of attributes like ownership or access permissions change
* file and directory manipulations
* piped rule execution (output of a rule is the input of the next rule)
* children rule execution (output of a rule is the input of the upcoming rules)
* creating files from Jinja2 templates
* send notification on git push

Supported file formats:

* ``plain text``
* ``ini``
* ``json``
* ``yaml`` (basic, single document operations)
* ``toml``

Upcoming file format support:

* ``hocon``

Community
=========

If you need help or you would like to be part of the Hammurabi community, join us on discord_.

.. _discord: https://discord.gg/dj8Myk5

Installation
============

Hammurabi can be installed by running ``pip install hammurabi`` and it requires
Python 3.7.0+ to run. This is the preferred method to install Hammurabi, as it
will always install the most recent stable release. If you don't have `pip`_
installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Installing extras
-----------------

Hammurabi tries to be as tiny as its possible, hence some rules are requiring extra
dependencies to be installed. Please check the documentation of the Rules to know
which dependency is required to use the specific rule.

To install hammurabi with an extra package run ``pip install hammurabi[<EXTRA>]``,
where ``<EXTRA>`` is the name of the extra option. To install multiple extra packages
list the extra names separated by comma as described in `pip's examples`_ section point
number six.

+---------------------+--------------------------------------------+
| Extra               | Description                                |
+=====================+============================================+
| all                 | alias to install all the extras available  |
+---------------------+--------------------------------------------+
| ini                 | needed for ini/cfg based rules             |
+---------------------+--------------------------------------------+
| ujson               | install if you need faster json manipulat  |
+---------------------+--------------------------------------------+
| yaml                | needed for yaml based rules                |
+---------------------+--------------------------------------------+
| templating          | needed for rules which are using templates |
+---------------------+--------------------------------------------+
| slack-notifications | needed for slack webhook notifications     |
+---------------------+--------------------------------------------+

.. _`pip's examples`: https://pip.pypa.io/en/stable/reference/pip_install/#examples

Configuration
=============

For configuration instructions, please visit the documentation_ site.

.. _documentation: https://hammurabi.readthedocs.io/en/latest/config.html

Usage examples
==============

In every case, make sure that you clone the target repository prior using Hammurabi.
After cloning the repository, always set the current working directory to the target's
path. Hammurabi will not clone the target repository or change its execution directory.

Enforce registered laws
-----------------------

.. code-block:: bash

    $ hammurabi enforce
    [INFO]  2020-14-07 16:31 - Checkout branch "hammurabi"
    [INFO]  2020-14-07 16:31 - Executing law "L001"
    [INFO]  2020-14-07 16:31 - Running task for "configure file exists"
    [INFO]  2020-14-07 16:31 - Rule "configure file exists" finished successfully
    [INFO]  2020-14-07 16:31 - Running task for "Minimum clang version is set"
    [INFO]  2020-14-07 16:31 - Rule "Minimum clang version is set" finished successfully
    [INFO]  2020-14-07 16:31 - Running task for "Minimum icc version is set"
    [INFO]  2020-14-07 16:31 - Rule "Minimum icc version is set" finished successfully
    [INFO]  2020-14-07 16:31 - Running task for "Minimum lessc version is set"
    [INFO]  2020-14-07 16:31 - Rule "Minimum lessc version is set" finished successfully
    [INFO]  2020-14-07 16:31 - Running task for "Maximum lessc version is set"
    [INFO]  2020-14-07 16:31 - Rule "Maximum lessc version is set" finished successfully
    [INFO]  2020-14-07 16:31 - Pushing changes
    [INFO]  2020-14-07 16:35 - Checking for opened pull request
    [INFO]  2020-14-07 16:35 - Opening pull request

Custom Rules
============

Although the project aims to support as many general operations as it can,
the need for adding custom rules may arise.

To extend Hammurabi with custom rules, you will need to inherit a class
from ``Rule`` and define its abstract methods.

The following example will show you how to create and use a custom rule.
For more reference please check how the existing rules are implemented.

.. code-block:: python

    # custom.py
    import shutil
    import logging
    from hammurabi.mixins import GitMixin
    from hammurabi.rules.base import Rule


    class CustomOwnerChanged(Rule, GitMixin):
        """
        Change the ownership of a file or directory to <original user>:admin.
        """

        def __init__(self, name: str, path: Optional[Path] = None, **kwargs):
            super().__init__(name, path, **kwargs)

        def post_task_hook(self):
            self.git_add(self.param)

        def task(self) -> Path:
            # Since ``Rule`` is setting its 2nd parameter to ``self.param``,
            # we can use ``self.param`` to access the target file's path.
            logging.debug('Changing group of "%s" to admin', str(self.param))
            shutil.chown(self.param, group="admin")
            return self.param

Custom Preconditions
====================

Rule execution supports preconditions. The logic is simple: if all preconditions
pass, the rule is executed. Otherwise it will be skipped.

.. code-block:: python

    # custom.py
    from hammurabi import IsLineExists


    class IsPackage(IsLineExists):
        def __init__(self, **kwargs):
            super().__init__(path=Path("Jenkinsfile"), criteria="package", **kwargs)

Command line options
====================

.. code-block:: bash

    Usage: hammurabi [OPTIONS] COMMAND [ARGS]...

    Hammurabi is an extensible CLI tool responsible for enforcing user-defined
    rules on a git repository.

    Find more information at: https://hammurabi.readthedocs.io/latest/

    Options:
    -c, --config PATH               Set the configuration file.  [default:
                                    pyproject.toml]

    --repository TEXT               Set the remote repository. Required format:
                                    owner/repository.  [default: ]

    --token TEXT                    Set github access token.  [default: ]
    --log-level [DEBUG|INFO|WARNING|ERROR]
                                    Set logging level.  [default: INFO]
    --install-completion [bash|zsh|fish|powershell|pwsh]
                                    Install completion for the specified shell.
    --show-completion [bash|zsh|fish|powershell|pwsh]
                                    Show completion for the specified shell, to
                                    copy it or customize the installation.

    --help                          Show this message and exit.

    Commands:
    enforce  Execute registered laws.
    version  Print hammurabi version.

Contributing
============

Hurray, You reached this section, which means you are ready
to contribute.

Please read our contibuting guideline_. This guideline will
walk you through how can you successfully contribute to
Hammurabi.

.. _guideline: https://github.com/gabor-boros/hammurabi/blob/master/CONTRIBUTING.rst

Installation
------------

For development you will need poetry_ and pre-commit_. After poetry installed,
simply run `poetry install -E all`. This command will both create the virtualenv
and install all development dependencies for you.

.. _poetry: https://python-poetry.org/docs/#installation
.. _pre-commit: https://pre-commit.com/#install


Useful make Commands
--------------------

+------------------+-------------------------------------+
| Command          | Description                         |
+==================+=====================================+
| help             | Print available make commands       |
+------------------+-------------------------------------+
| clean            | Remove all artifacts                |
+------------------+-------------------------------------+
| clean-build      | Remove build artifacts              |
+------------------+-------------------------------------+
| clean-mypy       | Remove mypy artifacts               |
+------------------+-------------------------------------+
| clean-pyc        | Remove Python artifacts             |
+------------------+-------------------------------------+
| clean-test       | Remove test artifacts               |
+------------------+-------------------------------------+
| docs             | Generate Sphinx documentation       |
+------------------+-------------------------------------+
| format           | Run several formatters              |
+------------------+-------------------------------------+
| lint             | Run several linters after format    |
+------------------+-------------------------------------+
| test             | Run all tests with coverage         |
+------------------+-------------------------------------+
| test-unit        | Run unit tests with coverage        |
+------------------+-------------------------------------+
| test-integration | Run integration tests with coverage |
+------------------+-------------------------------------+

Why Hammurabi?
==============

Hammurabi was the sixth king in the Babylonian dynasty,
which ruled in central Mesopotamia from c. 1894 to 1595 B.C.

The Code of Hammurabi was one of the earliest and most
complete written legal codes and was proclaimed by the
Babylonian king Hammurabi, who reigned from 1792 to 1750 B.C.
Hammurabi expanded the city-state of Babylon along the Euphrates
River to unite all of southern Mesopotamia. The Hammurabi code
of laws, a collection of 282 rules, established standards for
commercial interactions and set fines and punishments to meet
the requirements of justice. Hammurabi’s Code was carved onto
a massive, finger-shaped black stone stele (pillar) that was
looted by invaders and finally rediscovered in 1901.
