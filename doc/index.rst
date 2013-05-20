Welcome to |project| documentation
==================================

.. centered::  Version |version| released |today|

.. note::

  Due to a lack of foresight, this project used to be named Java Mini
  Python. It also has an Objective C implmentation that works on iOS
  and MacOS, and may see other platforms in the future, hence the
  current name.

|project| provides an implementation of a useful subset of
Python syntax and types in Java and Objective C.  The sweet spot is
where you need a `DSL
<http://en.wikipedia.org/wiki/Domain-specific_language>`__ (eg
expressions, variables, conditionals, methods/macros, callbacks) and
would like to use Python's syntax and types (eg heterogeneous lists
and dicts).  Think of it as adding those things to `JSON
<http://json.org>`__ rather than cutting down Python.

It was originally written in order to have a richer configuration file
for an Android app library. For example you could make the brightness
setting have a value of 7 except on Thursday afternoons, unless the
program has been running for 24 hours.

If you are looking for a fuller implementation of Python then try the
`Jython Project <http://www.jython.org/>`__ for Java, or regular
`CPython <http://www.python.org/download>`__.

|project| is hosted at http://code.google.com/p/java-mini-python/

Works with `Java 1.5+
<http://en.wikipedia.org/wiki/Java_version_history#J2SE_5.0_.28September_30.2C_2004.29>`__,
iOS/MacOS with Clang and `ARC
<http://developer.apple.com/library/mac/#releasenotes/ObjectiveC/RN-TransitioningToARC/Introduction/Introduction.html>`__,
and `Python 2.6+/3.1+
<http://en.wikipedia.org/wiki/History_of_Python#Version_release_dates>`__.

As a JAR file |project| comes in at 32kb, `Rhino
<http://www.mozilla.org/rhino/>`__ (Javascript interpreter) comes in
at 1.1MB or more and various Lua implementations are at least ½ MB.
x86 CPython is over 1½ MB (plus numerous extra files), while Objective
C |project| is under 100kb.  |project| doesn't include a language
parser or `REPL
<http://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop>`__
as you use :doc:`jmp-compile` to do the parsing.  This keeps things
small - just the way we like it.

Contents:

.. toctree::
   :maxdepth: 2

   example
   lang
   java
   objc
   python
   jmp-compile
   quirks
   internals
   faq
   changes
   copyright




Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

