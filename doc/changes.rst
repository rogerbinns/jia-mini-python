Change History
**************

1.1
===

All non-public items marked private to avoid them showing up in
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
