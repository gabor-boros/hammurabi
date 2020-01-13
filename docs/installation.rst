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

To work with parsed files, you need to install the required
extras.

+-----------------+----------------------------------------+----------------------------------+
| Name            | Description                            | Install example                  |
+=================+========================================+==================================+
| ini             | Parse ini/cfg files                    | `pip install hammurabi[ini]`     |
+-----------------+----------------------------------------+----------------------------------+

To install multiple extras at once, you can run
``pip install hammurabi[extra1,extra2,...]``.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


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
