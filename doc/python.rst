Python reference
================

See :doc:`lang` for an overview of what types and operations are
supported.  Java Mini Python does not have an internal object model -
instead Java types are :doc:`used directly <java>`.  This keeps the
code considerably smaller.  But it also means that most Python
attributes (eg functions) do not exist.  For example in Python
integers have 64 different attributes while they have none in this
implementation.

list type
---------

.. method:: append(item)

   Adds item to end of list (modify in place)

.. method:: sort(cmp=None, key=None, reverse=False)
 
   You can omit some or all of the arguments.  Since keyword arguments
   are not supported you will need to supply preceding arguments.

   :param callable cmp: A function returning less than zero, zero or
      positive when supplied with two items to compare.  If None is
      provided then :func:`cmp` is used.
   :param callable key: A function taking a list member as argument
      returning a derived value to use for the comparison.
   :param bool reverse: Should the list be sorted greatest first

   Unlike Python's implementation this does require that cmp and key
   are callables if supplied.

   Java's :jdoc:`Collections.sort <java/util/Collections.html#sort(java.util.List, java.util.Comparator)>` is used whose implementation is derived
   from Python's `sort <http://en.wikipedia.org/wiki/Timsort>`__.

str type
--------

.. method:: upper()

   Returns upper case version of string.

Global functions
----------------

.. function:: apply(callable, args)

   :param callable: A callable object
   :param list args: The arguments to call with

   Since `*args` is not supported, this is how to call something when
   you have built up the arguments in a list.

.. function:: bool(item)

   Returns a boolean for the item.  For example it is True for
   non-zero integers and strings/list/dict that contain at least one item.

.. function:: callable(item)

   Returns a boolean indicating if the item can be called as a function.

.. function:: cmp(left, right)

   Compares left against right depending on if they are less, equal or
   greater.  Note that an exception is raised if they are not of
   comparable types.

.. function:: filter(function, list)

   Returns a new list consisting of members when `function(member)`
   returned true.

.. function:: id(item):

   Returns a numeric code uniquely representing this instance.  Behind
   the scenes it returns the result of
   :jdoc:`System.getIdentityHashcode()
   <java/lang/System.html#identityHashCode(java.lang.Object)>`.

.. function:: len(item)

   Returns length of item such as number of characters for a str,
   members in a list/dict.

.. function:: print(*items)

   Prints the items after converting them to strings and separating
   with a space.  A newline is always emitted.  You will only be able
   to call this function if you ran :doc:`jmp-compile <jmp-compile>`
   under Python 3 or supplied the `--print-function` argument.

.. function:: range([start], stop[, step])

   Returns a list of integers between start (inclusive) and stop
   (exclusive) each incrementing by step.  Step can be negative.

.. function:: str(item)

   Returns the string corresponding to item.

   For :doc:`non basic types <java>` their :jdoc:`toString()
   <java/lang/Object.html#toString()>` method is called.

.. function:: type(item)

   Unlike regular Python this returns a string.  For the basic types
   it will be the expected name.  For others it will be their
   :jdoc:`Class.getSimpleName()
   <java/lang/Class.html#getSimpleName()>`.
