Welcome to Java Mini Python's documentation
===========================================

.. centered::  Version |version| released |today|

Java Mini Python provides an implementation of a useful subset of
Python syntax and types in Java.  The sweet spot is where you need a
`DSL <http://en.wikipedia.org/wiki/Domain-specific_language>`__ (eg
expressions, variables, conditionals, methods/macros, callbacks) and
would like to use Python's syntax and types (eg heterogeneous lists
and dicts).

It was originally written in order to have a richer configuration file
for an Android app library. For example you could make the brightness
setting have a value of 7 except on Thursday afternoons, unless the
program has been running for 24 hours.

If you are looking for a fuller implementation of Python then try the
`Jython Project <http://www.jython.org/>`__

Java Mini Python is hosted at http://code.google.com/p/java-mini-python/

Works with `Java 1.5+
<http://en.wikipedia.org/wiki/Java_version_history#J2SE_5.0_.28September_30.2C_2004.29>`__
and `Python 2.6+/3.1+
<http://en.wikipedia.org/wiki/History_of_Python#Version_release_dates>`__.

As a JAR file Java Mini Python comes in at 32kb, `Rhino
<http://www.mozilla.org/rhino/>`__ (Javascript interpreter) comes in
at 1.1MB or more and various Lua implementations are at least ½ MB.
Java Mini Python doesn't include a language parser or `REPL
<http://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop>`__
as you use :doc:`jmp-compile` to do the parsing.  This keeps things
small - just the way we like it.

Contents:

.. toctree::
   :maxdepth: 2

   example
   lang   
   java
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

