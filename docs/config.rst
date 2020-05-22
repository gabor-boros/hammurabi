=============
Configuration
=============

Overview
========

Hammurabi configuration
=======================

You can set the following options in your ``pyproject.toml``
config file's `[hammurabi]` section. Config option marked with ``*`` (asterisk)
is mandatory (set by CLI argument or project config). Hammurabi can be configured
through environment variables too. To use an environment variable based config option
set the ``HAMMURABI_<CONFIG_OPTION>`` where ``<CONFIG_OPTION>`` is in uppercase and
matches one of the options below.

+-----------------+-----------------------------------------------+-----------------------+
| Config option   | Description                                   | Default value         |
+=================+===============================================+=======================+
| pillar_config * | location of pillar config                     | None                  |
+-----------------+-----------------------------------------------+-----------------------+
| pillar_name     | name of the pillar variable                   | pillar                |
+-----------------+-----------------------------------------------+-----------------------+
| log_level       | logging level of the program                  | INFO                  |
+-----------------+-----------------------------------------------+-----------------------+
| log_path        | path to the log file or None                  | ./hammurabi.log       |
+-----------------+-----------------------------------------------+-----------------------+
| log_format      | format of the log lines                       | BASIC_FORMAT          |
+-----------------+-----------------------------------------------+-----------------------+
| repository      | git repository (owner/repo)                   | None                  |
+-----------------+-----------------------------------------------+-----------------------+
| git_branch_name | working branch name                           | hammurabi             |
+-----------------+-----------------------------------------------+-----------------------+
| dry_run         | enforce without any modification              | False                 |
+-----------------+-----------------------------------------------+-----------------------+
| rule_can_abort  | if a rule fails it aborts the whole execution | False                 |
+-----------------+-----------------------------------------------+-----------------------+
| report_name     | report file's name to generate                | hammurabi_report.json |
+-----------------+-----------------------------------------------+-----------------------+

For HTTPS git remotes do not forget to set the ``GIT_USERNAME`` and ``GIT_PASSWORD``
environment variables. For SSH git remotes please add your ssh key before using
Hammurabi.

Examples
--------

Example content of the ``pyproject.toml`` file.

.. code-block:: toml

    [hammurabi]
    pillar_config = "/tmp/config/global_config.py"
    working_dir = "/tmp/clones/hammurabi"
    repository = "gabor-boros/hammurabi"
    git_branch_name = "custom-branch-name"
    log_level = "WARNING"
    log_file = "/var/log/hammurabi.log"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    rule_can_abort = true
    report_name = "hammurabi_report.json"

Pillar configuration
====================

The pillar needs no configuration. All the thing the developer
must do is creating a :class:`hammurabi.pillar.Pillar` object
and registering the laws to it.

Using custom rules
------------------

Custom rules are not different from built-in one. In case
of a custom rule, just import and use it.

Examples
--------

.. code-block:: python

    >>> from hammurabi import Law, Pillar
    >>> from mycompany.rules import MyCustomRule
    >>>
    >>> meaning_of_life = Law(
    >>>     name="...",
    >>>     description="...",
    >>>     rules=[MyCustomRule]
    >>> )
    >>>
    >>> pillar = Pillar()
    >>> pillar.register(meaning_of_life)
