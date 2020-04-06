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

Supported file formats:

* ``plain text``
* ``ini``
* ``json``
* ``yaml`` (basic, single document operations)

Upcoming file format support:

* ``toml``
* ``hocon``

Installation
============

Hammurabi can be installed by running ``pip install hammurabi`` and it requires
Python 3.7.0+ to run. This is the preferred method to install Hammurabi, as it
will always install the most recent stable release. If you don't have `pip`_
installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Configuration
=============

For configuration instructions, please visit the documentation_ site.

.. _documentation: https://hammurabi.readthedocs.io/en/latest/config.html

Command line options
====================

.. code-block:: bash

    hammurabi [OPTIONS] COMMAND [ARGS]...

    Hammurabi is an extensible CLI tool responsible for enforcing user-defined
    rules on a git repository.

    Find more information at: https://hammurabi.readthedocs.io/latest/

    Options:
    -c, --config PATH               Set the configuration file.  [default:
                                    pyproject.toml]
    --repository TEXT               Set the remote repository. Required format:
                                    owner/repository
    --github-token TEXT             Set github access token
    --log-level [DEBUG|INFO|WARNING|ERROR]
                                    Set logging level.
    --help                          Show this message and exit.

    Commands:
    describe  Show details of a specific resource or group of resources.
    enforce   Execute all registered Law.
    get       Show a specific resource or group of resources.
    version   Print Hammurabi version.

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

Listing available laws
----------------------

.. code-block:: bash

    $ hammurabi get laws
    - Gunicorn config set up properly

Get info about a law by its name
--------------------------------

.. code-block:: bash

    $ hammurabi get law "Gunicorn config set up properly"
    Gunicorn config set up properly

    Change the gunicorn configuration based on our learnings
    described at: https://google.com/?q=gunicorn.

    If the gunicorn configuration does not exist, create a
    new one configuration file.

Get all registered (root) rules
-------------------------------

.. code-block:: bash

    $ hammurabi get rules
    - Rule 1
    - Rule 5

Get a rule by its name
----------------------

.. code-block:: bash

    $ hammurabi get rule "Rule 1"
    Rule 1

    Ensure that a file exists. If the file does not exists,
    this :class:`hammurabi.rules.base.Rule` will create it.

    Due to the file is already created by :func:`pre_task_hook`
    there is no need to do anything just return the input parameter.

Describe a law by its name
--------------------------

.. code-block:: bash

    $ hammurabi describe law "Gunicorn config set up properly"
    Gunicorn config set up properly

    Change the gunicorn configuration based on our learnings
    described at: http://docs.gunicorn.org/en/latest/configure.html.

    If the gunicorn configuration does not exist, create a
    new one configuration file.

    Rules:
    --> Rule 1
    --> Rule 2
    --> Rule 3
    --> Rule 4
    --> Rule 5

Describe a rule by its name
---------------------------

.. code-block:: bash

    $ hammurabi describe rule "Rule 1"
    Rule 1

    Ensure that a file exists. If the file does not exists,
    this :class:`hammurabi.rules.base.Rule` will create it.

    Due to the file is already created by :func:`pre_task_hook`
    there is no need to do anything just return the input parameter.

    Chain:
    --> Rule 1
    --> Rule 2
    --> Rule 3
    --> Rule 4

Getting the execution order of laws and rules
---------------------------------------------

.. code-block:: bash

    $ hammurabi get order
    - Gunicorn config set up properly
    --> Rule 1
    --> Rule 2
    --> Rule 3
    --> Rule 4
    --> Rule 5

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

For development you will need poetry_. After poetry installed,
simply run `poetry install`. This command will both create the
virtualenv and install development dependencies for you.

.. _poetry: https://python-poetry.org/docs/#installation


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
