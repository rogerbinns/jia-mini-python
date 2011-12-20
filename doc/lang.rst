Syntax/type support
*******************

The goal is to support a useful subset of Python syntax and keep the
resulting files small.  If you want fuller Python support then
consider using `Jython <http://www.jython.org>`__ instead.

What is supported
=================

Types
-----

* int
* string (unicode only)
* list
* dict
* bool
* None

Keywords
--------

* def (new methods)
* if
* while

Operators
---------

* and & or
* \+ - * / (where applicable)
* len (as applicable)
* [] (list and dict indexing)

What is not supported
=====================

* Classes
* Decorators
* Threads
* Exceptions
* More than one source file/module
* Generators
* List comprehensions
