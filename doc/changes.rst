Change History
**************

2.0
===

There is now a compatible Objective C solution that works on iOS and Mac

Added :jdoc:`toPyReprString` for Java

``bool`` now always returns a value.  Before it would give TypeError
for unknown types, which now give True.

Correct Java string.split for various corner cases.

1.2
===

Filled in the :jdoc:`cause <java/lang/Throwable.html#getCause()>` for
:ref:`ExecutionError <ExecutionError>` and added toDetailedString()
method.

Added several annotations that help when the file is compiled with
very strict warnings.

Minor documentation tweaks and updates.

Added toDetailedString() on the Exception which provides additional
useful detail for logging and analytics.

1.1
===

All Java non-public items marked private to avoid them showing up in
completions if you copied the code to your own package.  (:issue:`1`)

Do not use `String.isEmpty()` as it doesn't exist on Android (:issue:`2`)

Public entry points are synchronized to prevent concurrent usage (:issue:`3`)

Added `dict.get(key, default)` (:issue:`5`)

Dictionary members can be obtained and set via attribute style access
too (:issue:`6`)::

   a={"foo": 3}
   # Get
   print a["foo"], a.foo
   # Set
   a.bar=7
   print a["bar"], a.bar

Added *is/is not* operator.  Behind the scenes this translates *x is
y* into *id(x) == id(y)*.

It is possible to do a form of object orientation keeping data and the
functions that operate on it together in the same dictionary as
:ref:`documented here <pyobject>` (:issue:`7`)

Code that attempted to do a rich compare of dictionaries was removed
and their :func:`id` is used instead.  (:ref:`comparisons`).

Added dict.copy (:issue:`8`)

Added :doc:`jmp-compile` option to only do a syntax check

Fixed returns within for loops (:issue:`10`)
