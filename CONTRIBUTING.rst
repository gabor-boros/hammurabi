.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/gabor-boros/hammurabi/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it. In case you added a
new Rule or Precondition, do not forget to add them to the docs as well.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Hammurabi could always use more documentation, whether as part of the
official Hammurabi docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/gabor-boros/hammurabi/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `hammurabi` for local development.

As `step 0` make sure you have python 3.7+ and [https://pre-commit.com/](pre-commit) installed.

1. Fork the `hammurabi` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/hammurabi.git

3. Install your local copy. Assuming you have poetry installed, this is how you set up your fork for local development::

    $ cd hammurabi/
    $ poetry install -E all

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass linters and the tests::

    $ poetry shell
    $ make lint
    $ make test
    $ pre-commit run --all-files

   You will need make not just for executing the command, but to build (and test) the
   documentations page as well.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.7 and 3.8.

Releasing
---------

A reminder for the maintainers on how to release.
Make sure all your changes are committed (including an entry in CHANGELOG.rst).

After all, create a tag and a release on GitHub. The rest will be handled by
Travis.

Please follow this checklist for the release:

1. Make sure that formatters are not complaining (``make format`` returns 0)
2. Make sure that linters are not complaining (``make lint`` returns 0)
3. Update CHANGELOG.rst - do not forget to update the unreleased link comparison
4. Update version in ``pyproject.toml``, ``CHANGELOG.rst`` and ``hammurabi/__init__.py``
5. Compare the external and generated documentation
6. Create a new Release on GitHub with a detailed release description based on
   the previous releases.
