.. _development:

Releasing
***********

MUSCLE3 uses Git on GitHub for version management, using the `Git Flow`_
branching model. Making a release involves quite a few steps, so they're listed
here to help make the process more reliable; this information is really only
useful for the maintainers.

Check online documentation
--------------------------

Online documentation rendering on ReadTheDoc works a bit differently than local
builds, as a result of which checking a local documentation build only partially
ensures we get working online documentation. So this needs to be checked:

- Check develop branch documentation is there
- Specifically, check the Python API documentation page
- Check the other languages too

If the Python API docs are missing, then it's likely to be a dependency problem.
Sphinx needs dependencies installed, and that's now done via tox so that the
dependencies come from ``setup.py`` and local builds should match what RTD does,
but it's still not the same process, so it's best to check.

Check metadata
--------------

- Check the metadata in ``setup.py``, and update as necessary
- Check the dependencies, and fix them to an appropriate range of versions
- Check the copyright date and owners in ``README.rst`` and ``docs/source/conf.py``
  and update as necessary.

Update the changelog
--------------------

Each release should have an entry in the CHANGELOG.rst describing the new
features and fixed problems. Use the git log to get a list of the changes, and
switch to the development branch:

.. code-block:: bash

  git log <your favourite options>
  git switch develop

and then edit CHANGELOG.rst and commit.

.. code-block:: bash

  git add CHANGELOG.rst
  git commit -m 'Add version x.y.z to the change log'

Make a release branch
---------------------

To start the release process, make a release branch

.. code-block:: bash

  git switch -c release-x.y.z develop

MUSCLE3 uses `Semantic Versioning`_, so name the new version accordingly.

Update version
--------------

Next, the version should be updated. There is a single version tag in the
``VERSION`` file in the root of the repository. On the development branch, the
version should be set to ``x.y.z-dev``, where ``x.y.z`` is the next expected
version (it's fine if that changes later, e.g. because you end up releasing
2.0.0 rather than 1.4.0).  On the release branch, it should be set to the number
of this release of course.

Check documentation
-------------------

Next, we should build the documentation to ensure that the new version number
shows up:

.. code-block:: bash

  make docs

It may give some warnings about missing references, that's a known issue and
normally harmless. Next, point your web browser to
``docs/build/html/index.html`` and verify that the documentation built
correctly. In particular, the new version number should be in the browser's
title bar as well as in the blue box on the top left of the page.

Run tests
---------

Before we make a commit, the tests should be run, and this is a good idea anyway
if we're making a release. So run ``make test`` and check that everything is in
order.

Commit the version update
-------------------------

This is the usual Git poem:

.. code-block:: bash

  git add VERSION
  git commit -m 'Set release version to x.y.z'
  git push --set-upstream origin release-x.y.z

This will trigger the Continuous Integration, so check that that's not giving
any errors while we're at it.

Fix badges
----------

The badges in the README.rst normally point to the development branch versions
of everything. For the master branch, they should point to the master version.

.. code-block:: bash

  # edit README.rst
  git add README.rst
  git commit -m 'Update badges to point to master'
  git push

Merge into the master branch
----------------------------

If all seems to be well, then we can merge the release branch into the master
branch and tag it, thus making a release, at least as far as Git Flow is
concerned. We use the ``-X theirs`` option here to resolve the merge conflict
caused by the version update that was done for the previous release, which we
don't have on this branch. The last command is to push the tag, which is
important for GitHub and GitHub integrations.

.. code-block:: bash

  git switch master
  git merge --no-ff -X theirs release-x.y.z
  git tag -a x.y.z -m 'Release x.y.z'
  git push
  git push origin x.y.z


Make a GitHub release
---------------------

In order to get a DOI for this release, we need to make a release on GitHub. Go
to the `MUSCLE3 GitHub repository`_ and click 'Releases'. Select 'Draft a new
release', select the x.y.z. tag that we just uploaded, and use 'Release x.y.z'
as the title.

The main text ends up as the description on Zenodo, so start with the first
three paragraphs from the Introduction section of the documentation to give
people an idea of what they're looking at. Then copy-paste the description of
the current release from the change log, and convert it from ReStructuredText
to MarkDown.

Optionally select 'This is a pre-release' if it's not a final version, ensure
'Set as the latest release' is checked, then publish it.

Build and release to PyPI
-------------------------

Finally, the new version needs to be built and uploaded to PyPI, so that people
can start using it. To build, use:

.. code-block:: bash

  rm -r ./build
  python3 setup.py sdist bdist_wheel

Note that we remove ``./build``, which is the build directory setuptools uses,
to ensure that we're doing a clean build, I've seen some weird mixes of versions
on occasion so it's better to be safe than sorry.

We can then check to see if everything is okay using

.. code-block:: bash

  twine check dist/muscle3-x.y.z*

and if all seems well, we can upload to PyPI:

.. code-block:: bash

  twine upload dist/muscle3-x.y.z*

Announce release
----------------

Announce the release in the usual places, so that people know it exists. There
should be a short release message listing new features and fixed bugs, and don't
forget to thank everyone who contributed!

Merge the release branch back into develop
------------------------------------------

The above concludes the release, but we need to do one more thing to be able to
continue developing. The release branch contains some changes to the change log
that we want to have back on the develop branch. So we'll merge it back in:

.. code-block:: bash

  git switch develop
  git merge --no-commit release-x.y.z


We use --no-commit to give ourselves a chance to edit the changes before
committing them. Make sure that README.rst is taken from the develop side,
CHANGELOG.rst comes from the release branch, and VERSION is given a new number,
probably x.y.{z+1}-dev unless you have big plans. When done, commit the merge
and continue developing.

Update issues
-------------

Go through the issues on GitHub and close tho ones for which a fix was
released. Or if they were created by someone else, ask the user to check that
the new version solves their problem and close the issue if it does.


.. _`Git Flow`: http://nvie.com/posts/a-successful-git-branching-model/
.. _`Semantic Versioning`: http://www.semver.org
.. _`MUSCLE3 GitHub repository`: https://github.com/multiscale/muscle3
