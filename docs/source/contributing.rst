=======================
Contributing to MUSCLE3
=======================

MUSCLE3 is developed by a community of contributors, and we welcome anyone and
everyone to help us build it. Maybe you've found a mistake in the code (it
happens, we're only human!) that you would like to fix, want to add a new
feature, or improve the documentation. That's great!

However, because MUSCLE3 is worked on by different people simultaneously, we do
need some system to keep track of all the changes, so that it doesn't become an
unintelligible mess. We use the Git version control system for this, together
with the Github hosting platform.

Describing all of Git and Github here would be too much (both have their own
documentation), but we do describe the process of contributing a change to
MUSCLE3 in some detail. We're assuming that you already have Git installed, and
have a Github account that you're logged in with. Once that's done, please
proceed as below.


Make an Issue
=============

`Issues`_ are found in a tab at the top of `the repository home page`_. Please check
to see that the bug you want to fix or the feature you want to add does not
already have an issue dedicated to it. If it does, feel free to add to the
discussion. If not, please make a new issue.

If you have discovered an error in MUSCLE3, please describe

* What you were trying to achieve
* What you did to achieve this
* What result you expected
* What happened instead

With that information, it should be possible for someone else to reproduce the
problem, or to check that a proposed fix has really solved the issue.

If you would like a new feature (or would like to add it yourself), please
describe

* The context in which you're using MUSCLE3
* What you are trying to achieve
* How the new feature would help you do that
* What the new feature should do and how it should work

If you want to fix the bug or implement the feature yourself, you'll have to set
up a development environment.

.. _Issues: https://github.com/multiscale/muscle3/issues
.. _the repository home page: https://github.com/multiscale/muscle3/


Get a local repository
======================

First, you'll need a public Git repository that you have write access to, and which
contains MUSCLE3. If you have write access to the main MUSCLE3 repository,
then you're set already. If not, click the Fork button at the top right of the
main MUSCLE3 repository page. This will make a copy of the repository that you
can write to, under your own account.

Next, you need a copy of this public repository on your local computer, so that
you can easily edit files. This is done by cloning the repository::

  git clone git@github.com:/multiscale/muscle3.git

for the original repository, of if you've forked it, probably something like::

  git clone git@github.com:/UserName/muscle3.git

You can use the ``Clone or download`` button to copy the location into your
clipboard.

This will create a local directory named ``muscle3`` containing a Git
repository that you can work in.


Install the tools
=================

Inside this directory, first check out the ``develop`` branch::

  cd muscle3
  git checkout develop

Next, you'll need a virtual environment to install the development tool in::

  virtualenv -p python3 ~/Envs/muscle3

The path is arbitrary, a virtualenv is just a directory with software in it, so
you can put it anywhere you want. An ``Envs`` subdirectory in your home
directory is somewhat standard though.  Do note that once created, a virtualenv
cannot be moved around without breaking (but it's easy to make a new one in a
new location instead).

Then, activate the environment, and install the development tools
into it::

  source ~/Envs/muscle3/bin/activate
  pip install -e .[dev]

and run the test suite, just to make sure that you have everything in working
order::

  make test


Make changes
============

Changes should be made on a fresh branch, dedicated to the issue you are
addressing. That way, multiple people can work at the same time, and multiple
issues can be addressed simultaneously, without everyone getting confused. So to
start, make a new branch, starting from the `develop` branch::

  git checkout develop
  git checkout -b issue-123

where, instead of 123, you put the number of the issue you're addressing.

For a simple bug, the whole issue can probably be fixed with a single change. (A
single change may affect different functions or files, but those changes should
be related, so that it doesn't make sense to do one and not the other.)

First, make a test that detects the bug you're going to fix, and make sure it
fails by running the test suite::

  make test

Then, fix the bug, and run the tests again, now to make sure that they pass.
When everything is in order, you can commit the change::

  git add changed_file.py some_dir/other_changed_file.py
  git commit -m "Made x configurable"
  git push

The last command pushes your changes back to the server, so that other
developers can see them. Do this after every commit! It makes it much easier to
collaborate.

Note that commits should be as small as possible. Please do not hack away for
several days and then commit a whole giant bunch of changes in a single commit,
as that makes it impossible to figure out later what was changed when, and which
change introduced that bug we are trying to find.

If you are solving a more complex problem, then a single commit will not be
enough, and you'll have to make a series of them, repeating the above steps,
until the issue is solved. Starting with a test is often the best way of going
about adding a new feature as well. You'll find that you'll need to think about
what your new feature should do and how it should work to create the test(s),
and once you've done that implementing it is a lot easier!

One last note: **Never copy-paste code from another program!**. It's fine to
have external dependencies (although we do try to limit them, to try to keep
installation simple), but those should be kept separate. Copy-pasting code leads
to complicated legal issues that we would really like to avoid. So please, only
contribute code that you wrote yourself. Thanks!


Make a pull request
===================

Once you've made all the changes needed to resolve the issue, the next step is
to make a pull request. Your changes so far are on a branch, either in the main
repository, or in a fork of the main repository. A pull request is a request to
the maintainers of MUSCLE3 to take the changes on your branch, and incorporate
them into the main version of the software.

To make a pull request, make sure that you have committed and pushed all your
changes, and that the tests pass. Then, go to the Github homepage of your fork,
if you have one, or the main MUSCLE3 repository. If you've just pushed, then
Github will show a "Compare & pull request" button. Otherwise, look up your
branch using the top left drop-down button, and then click the "New pull
request" button next to it.

This gives you a page describing your pull request. You will want to request a
merge from your issue branch, to the develop branch in the main MUSCLE3
repository. Add a description of the changes you've made, and click "Create pull
request", and you're all set.


Interact
========

Like issues, pull requests on Github are a kind of discussion forum, in which
the proposed changes can be discussed. We may ask you to make some improvements
before we accept your pull request. While the pull request is open, any
additional commits pushed to your public branch will automatically show up
there.

Once we're all satisfied with the change, the pull request will be accepted, and
your code will become part of MUSCLE3. Thank you!
