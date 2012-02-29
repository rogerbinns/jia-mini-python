Syntax/type support
*******************

The goal is to support a useful subset of Python syntax and keep the
resulting files small.  If you want fuller Python support then
consider using `Jython <http://www.jython.org>`__ instead.

:doc:`python` details more about specific types and global functions.

What is supported
=================

Types
-----

* int
* string (unicode only)
* list
* dict
* bool (:ref:`note <booleans>`)
* None
* tuple (note: :ref:`treated as list and mutable <tuples>`)
* functions (you can nest them, assign to variables, pass then around,
  invoke, :func:`apply`)

Keywords
--------

* def (new methods)
* if
* while
* for (iterate over list members and dict keys)
* return
* del
* lambda

Operators
---------

* boolean: and, or
* \+ - * / // % (Where applicable for types. Division is always floor division.)
* < <= == != >= > (:ref:`note <comparisons>`)
* in / not in (list/dict membership)
* is / is not (same object checking)
* len (as applicable)
* [] (list and dict indexing)
* [from:to] list slicing (step not supported)
* x if y else z (ternary)


What is not supported
=====================

* docstrings are seen but ignored.  You cannot retrieve them.  They do
  not end up in the output jmp file.
* Variable arguments and keyword arguments (`*args` and `**kwargs`).
  Note that methods :ref:`added via Java <adding_methods>` can take
  variable numbers of arguments.  You can call :func:`apply` to call
  a function with a list of arguments.
* Default arguments
* Augmented assignments (+= -= /= etc)
* Bitwise operators (<< >> & | ^)
* Classes - note however that there is some :ref:`pyobject`
* Decorators
* Threads
* Exceptions
* More than one source file/module
* Generators
* Import
* With
* List comprehensions (see :func:`map`)
* Tuple unpacking.  For example::

    for x,y in z:
        pass
* Floating point
* Bytes type
* Assignment to False/True/None (allowed in some Python versions to
  change value).  Has no effect.

Use Jython if you want more than mini-Python

Exceptions
==========

Exceptions are not supported nor is try/except.  If you do something
that results in an exception (eg adding a number to a string) then a
:ref:`Java level exception <ExecutionError>` will be thrown.

If you do need to be highly dynamic then consider using the `Look
Before You Leap <http://docs.python.org/glossary.html#term-lbyl>`__
style where you make checks before performing operations that can
fail.  Note that multi-threading is not supported so there are no race
conditions.
