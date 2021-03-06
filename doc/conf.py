# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "sphinxext")))

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo', 'sphinx.ext.extlinks', 'javadomain', "objcdomain"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

extlinks={
    "jdoc": ("http://docs.oracle.com/javase/7/docs/api/%s", "javadoc"),
    "issue": ("https://github.com/rogerbinns/jia-mini-python/issues/%s", "Issue "),
    "adoc": ("https://developer.apple.com/library/ios/documentation/Cocoa/Reference/Foundation/Classes/%s_Class/Reference/Reference.html", ""),
    "aref": ("https://developer.apple.com/library/ios/documentation/Cocoa/Reference/Foundation/Classes/NSString_Class/Reference/%s", ""),
}

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Jia Mini Python'
copyright = u'2011-2014, Roger Binns <rogerb@rogerbinns.com>'

rst_prolog="""
.. |project| replace:: %s

""" % (project,)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = os.getenv("VERSION")
# The full version, including alpha/beta/rc tags.
release = version
assert version
today = os.getenv("DATE")

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', "_build/javadoc" ]

# Output file base name for HTML help builder.
htmlhelp_basename = 'JiaMiniPythondoc'

html_theme_options = {'stickysidebar': True}



# -- Options for LaTeX output --------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'JiaMiniPython.tex', u'Jia Mini Python Documentation',
   u'Roger Binns', 'manual'),
]

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'jiaminipython', u'Jia Mini Python Documentation',
     [u'Roger Binns'], 1)
]

# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = u'Roger Binns'
epub_publisher = u'Roger Binns'
epub_copyright = copyright

add_module_names=False
