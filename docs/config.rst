=============
Configuration
=============

Overview
========

Hammurabi configuration
=======================

You can set the following options in your ``pyproject.toml``
config file's `[hammurabi]` section.

+-----------------+-----------------------------------------------+-----------------+
| Config option   | Description                                   | Default value   |
+=================+===============================================+=================+
| config          | location of pyproject.toml                    | pyproject.toml  |
+-----------------+-----------------------------------------------+-----------------+
| pillar          | name of the pillar variable                   | pillar          |
+-----------------+-----------------------------------------------+-----------------+
| log_level       | logging level of the program                  | INFO            |
+-----------------+-----------------------------------------------+-----------------+
| target          | location of the target directory              | . (current dir) |
+-----------------+-----------------------------------------------+-----------------+
| repository      | github repository (owner/repo)                | None            |
+-----------------+-----------------------------------------------+-----------------+
| git_branch_name | working branch name                           | hammurabi       |
+-----------------+-----------------------------------------------+-----------------+
| dry_run         | enforce without any modification              | False           |
+-----------------+-----------------------------------------------+-----------------+
| rule_can_abort  | if a rule fails it aborts the whole execution | False           |
+-----------------+-----------------------------------------------+-----------------+

Examples
--------

Example content of the ``pyproject.toml`` file.

.. code-block:: toml

    [hammurabi]
    repository = "gabor-boros/hammurabi"
    git_branch_name = "custom-branch"
    log_level = "WARNING"
    rule_can_abort = true

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
