=================
Development tools
=================

MUSCLE 3 is a fairly complex piece of software, being a coupling library
designed to link together independent bits of software written in different
languages. To help us develop MUSCLE 3, we use a variety of tools that check our
work and build software and documentation where required. This page describes
the development tools we use, what they do, and how they are configured.


Building and installation
=========================

The main language for MUSCLE 3 is Python 3. To help install and publish the
Python parts of MUSCLE 3, we use `setuptools`_. Setuptools reads information
from the file `setup.py` in the root of the repository. This file contains a
description of MUSCLE 3 which is used on PyPI (the standard online Python
package repository), information used by PIP when installing MUSCLE 3, and
information about required libraries.

The dependencies in `setup.py` are specified with an exact version number,
rather than an at-least version number. This way, we can be sure that no
incompatible changes are introduced that break MUSCLE 3. However, it also means
that the dependencies get out of date, as new versions are released. To keep
up-to-date on this, we use `Requires.io`_, a web service that scans our
`setup.py` and checks our versions against the latest releases. It produces a
button, which we embed in our README.rst, that shows whether we are up-to-date.

We will most likely have outdated dependencies quite often, as rapid updates are
a fact of life in today's Open Source world. This is not an immediate problem, as
the older versions will still be available and MUSCLE 3 will work with them, but
we should update regularly to stay current and avoid potential security issues.


Quality Control
===============

MUSCLE 3 is infrastructure used for building infrastructure (models) for doing
scientific experiments. As such, it is important that it is reliable, easy to
use, and easy to develop. Furthermore, it will frequently be used by
inexperienced programmers, who will look at MUSCLE 3 as an example of how to
write good code. It is therefore important that MUSCLE 3 is a well-implemented,
high quality program. To make sure that this happens, we use static checking
(linting), unit tests, and integration tests.

Static checking
---------------

The quality control system uses several tools, which are called from the central
Makefile. In our standard development environment, the command `make test` in
the top directory will run them all.

Python has a standard coding standard known as PEP8, which specifies how Python
code should be formatted. Consistently writing our code according to PEP8 makes
it easier to read, and makes it easier for new developers to get started. We use
the `PEP8 plug-in`_ for Pytest (see below) to check the formatting.

Although Python is a dynamically-typed language, it supports type annotations,
and using those for static type checking. While writing code with type
annotations sometimes takes a bit more thinking than doing without them, it
increases the reliability of the program a lot, as type checking can detect
mistakes that unit tests don't. So we use type annotations, and use `mypy`_ to
check them as part of the set of quality control software.

Finally, we use `Codacy`_, which is an online tool that runs various static
checking tools against our repository. It is run automatically for the main
branches, as well as for every pull request. Codacy tends to give false
positives fairly often, but the settings can be tuned and specific warnings can
be set to be ignored. So having some Codacy warnings on a pull request is not
necessarily a problem, but they should be reviewed and either fixed or disabled
as appropriate.

Tests
-----

MUSCLE 3 has a suite of tests, both unit tests (which test small bits of the
code one piece at a time) and integration tests (which test whether it all goes
together correctly). We run these tests, measure test coverage, and have
continuous integration just in case we forget to run the tests manually.

The main test framework for the Python part of the code is `PyTest`_. This
Python library provides a library with functions that make it easier to write
test cases, and a runner that automatically detects tests and runs them. Tests
are located in `test/` subdirectories in the code, and in the `integration_test`
directory in the root of the repository. In various places in the code, files
named `conftest.py` are located, which contain test fixtures. These files are
picked up automatically by PyTest. Having such a file in the root directory
causes PyTest to add that path to the PYTHONPATH, so that Python can find the
module under test if you import it from the test case. This doesn't work for the
integration tests, so there's a separate `include_libmuscle.py` there that sets
the path correctly.

We use a code coverage plug-in for PyTest, which measures which lines of the
code are executed during testing, and more importantly, which lines aren't.
Ideally, all code is covered, but in practice there will be things that are
difficult to test and not important enough to warrant testing. 90% coverage is a
nice (but sometimes challenging) target to aim for. This plug-in uses the
Python coverage library, which is configured in `.coveragerc`, where e.g.
generated code is excluded from testing.

Tests can be run locally using `make test`, but are also run in the cloud via
`Travis-CI`_ on every push to the Github repository. After Travis has run the
tests, it reports the code coverage to `Codacy`_, which integrates it with the
linting results into its dashboard. It also reports back to GitHub, adding an
icon to e.g. a pull request to signal whether the tests have passed or not.


Documentation
=============

The MUSCLE 3 documentation lives in the repository together with the code. This
is a much preferable arrangement to a separate wiki, as previous MUSCLEs had,
because wikis tend to get lost.

The source for the documentation is in `docs/source`, and it is written in
`ReStructuredText`_. It is processed into HTML by the `Sphinx`_ program, which
uses the `sphinx-autodoc`_ plug-in for extracting docstrings from the Python
source code and converting that into API documentation. Sphinx is configured
via `docs/source/conf.py`. This file contains a hook to automatically run
`sphinx-autodoc` whenever Sphinx is run, so that is does not have to be run
separately first.

The `ReadTheDocs`_ online service is configured to automatically render the
documentation and display it online. This uses Sphinx, but does not support
`sphinx-autodoc`, which is why we use the aforementioned hook.


.. _`setuptools`: https://setuptools.readthedocs.io
.. _`Requires.io`: https://requires.io/
.. _`PEP8 plug-in`: https://pypi.python.org/pypi/pytest-pep8
.. _`mypy`: https://mypy.readthedocs.io
.. _`Codacy`: https://support.codacy.com
.. _`PyTest`: https://pytest.org
.. _`Travis-CI`: https://docs.travis-ci.com
.. _`ReStructuredText`: http://docutils.sourceforge.net/rst.html
.. _`Sphinx`: http://www.sphinx-doc.org
.. _`sphinx-autodoc`: http://www.sphinx-doc.org/en/master/ext/autodoc.html
.. _`ReadTheDocs`: https://readthedocs.org
