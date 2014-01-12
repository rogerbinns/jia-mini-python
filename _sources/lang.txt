Syntax/type support
*******************

The goal is to support a useful subset of Python syntax and keep the
resulting files small.

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
  invoke, closures, :func:`apply`)

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
* Augmented assignments += -= /= etc (:ref:`note <augassign>`)
* List comprehensions

What is not supported
=====================

* docstrings are seen but ignored.  You cannot retrieve them.  They do
  not end up in the output jmp file.
* Variable arguments and keyword arguments (`*args` and `**kwargs`).
  Note that methods added in :ref:`Java
  <java_adding_methods>`/:ref:`ObjC <objc_adding_methods>` can take
  variable numbers of arguments.  You can call :func:`apply` to call a
  function with a list of arguments.
* Default arguments
* Bitwise operators (<< >> & | ^)
* Classes - note however that there is a useful :ref:`approximation <pyobject>`
* Decorators
* Threads (mutexes ensure only one call at a time into |project| can happen)
* Exceptions
* More than one source file/module
* Generators
* Import
* With
* Tuple unpacking.  For example::

    for x,y in z:
        pass
* Floating point
* Bytes type
* Assignment to False/True/None (allowed in some Python versions to
  change value).

Exceptions
==========

Exceptions are not supported nor is try/except.  If you do something
that results in an exception (eg adding a number to a string) then a
:ref:`Java level exception <ExecutionError>` will be thrown, or
:ref:`Objective C error <ObjCError>` returned.

If you do need to be highly dynamic then consider using the `Look
Before You Leap <http://docs.python.org/glossary.html#term-lbyl>`__
style where you make checks before performing operations that can
fail.  Note that multi-threading is not supported (serialised) so
there are no race conditions.
