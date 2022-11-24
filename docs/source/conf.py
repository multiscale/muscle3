#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# cerise documentation build configuration file, created by
# sphinx-quickstart on Wed Apr 19 10:25:17 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import pathlib
import sys

_rootpath = pathlib.Path(__file__).parents[2]
print('Project root path: {}'.format(_rootpath))

sys.path.insert(0, str(_rootpath))
sys.path.insert(0, str(_rootpath / 'libmuscle/python/'))
sys.path.append(str(_rootpath / 'docs/ext/breathe'))

# create a libmuscle/version.py if needed (which it is on RTD)
version_path = os.path.join(os.path.dirname(__file__), '../../libmuscle/python/libmuscle/version.py')
if not os.path.exists(version_path):
    with open(version_path, 'w') as f:
        f.write("__version__ = '0.0.0'")

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
        'breathe',
        'sphinx.ext.autodoc',
        'sphinx.ext.autosectionlabel',
        'sphinx.ext.intersphinx',
        'sphinx.ext.napoleon',
        'sphinx.ext.todo',
        'sphinx.ext.viewcode',
        'sphinxfortran.fortran_domain',
        'sphinx_tabs.tabs']

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'muscle3'
copyright = '2018-2022 University of Amsterdam and Netherlands eScience Center, 2022 The ITER Organization'
author = 'Lourens Veen'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

_version_file = '../../VERSION'
with open(_version_file, 'r') as f:
    # The full version, including alpha/beta/rc tags.
    release = f.read()
    # The short X.Y version.
    version = release.split('-')[0]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'examples/python/build/venv']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Also document constructors.
autoclass_content = 'both'

# Configure breathe (Doxygen plug-in)
breathe_projects = { 'libmuscle': str(_rootpath / 'docs' / 'doxygen' / 'xml') }

breathe_default_project = 'libmuscle'

breathe_default_members = ('members',)

# Configuration of sphinx.ext.intersphinx
# See https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "ymmsl": ("https://ymmsl-python.readthedocs.io/en/stable", None),
}


# -- Patch version into installation instructions --
def patch_installation_version():
    with open('installing.rst', 'w') as out_file:
        with open('installing.rst.in', 'r') as in_file:
            in_text = in_file.read()
            out_text = in_text.replace('%%VERSION%%', release.strip())
            out_file.write(out_text)

patch_installation_version()


# -- Run doxygen manually, as readthedocs doesn't support it --
import subprocess
subprocess.call('cd ../.. ; doxygen', shell=True)

# -- Run apidoc plug-in manually, as readthedocs doesn't support it -------
# See https://github.com/rtfd/readthedocs.org/issues/1139
def run_apidoc(_):
    here = os.path.dirname(__file__)
    out = os.path.abspath(os.path.join(here, 'apidocs'))
    src = os.path.abspath(os.path.join(here, '..', '..', 'libmuscle', 'python'))

    ignore_paths = [
            '*/test',
            'muscle_manager/protocol/*',
            'libmuscle/python/libmuscle/managere_protocol/*']

    argv = ['-f', '-T', '-e', '-M', '-o', out, src] + ignore_paths

    try:
        # Sphinx 1.7+
        from sphinx.ext import apidoc
        apidoc.main(argv)
    except ImportError:
        # Sphinx 1.6 (and earlier)
        from sphinx import apidoc
        argv.insert(0, apidoc.__file__)
        apidoc.main(argv)

def setup(app):
    app.connect('builder-inited', run_apidoc)

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'muscle3_doc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'muscle3.tex', 'MUSCLE3 Documentation',
     'MUSCLE3 contributors', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'muscle3', 'MUSCLE3 Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'muscle3', 'MUSCLE3 Documentation',
     author, 'muscle3',
     'The MUSCLE3 multiscale coupling library and environment.',
     'Miscellaneous'),
]


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']
