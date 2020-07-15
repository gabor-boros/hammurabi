.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Hammurabi, run this command in your terminal:

.. code-block:: console

    $ pip install hammurabi

This is the preferred method to install Hammurabi, as it will always install
the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
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
list the extra names separated by comma as described in pip_'s example section point
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

.. _pip: https://pip.pypa.io/en/stable/reference/pip_install/#examples

From sources
------------

The sources for Hammurabi can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/gabor-boros/hammurabi

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/gabor-boros/hammurabi/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/gabor-boros/hammurabi
.. _tarball: https://github.com/gabor-boros/hammurabi/tarball/master
