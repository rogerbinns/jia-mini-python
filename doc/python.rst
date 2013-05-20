Python reference
================

See :doc:`lang` for an overview of what types and operations are
supported.  |project| does not have an internal object model -
instead Java types are :doc:`used directly <java>`.  This keeps the
code considerably smaller.  But it also means that most Python
attributes (eg functions) do not exist.  For example in Python
integers have 64 different attributes while they have none in this
implementation.

dict type
---------

.. method:: copy()  -> dict

   Returns a new dictionary with the same contents, but changes to the
   new one do not affect the original.

.. method:: get(key, default)

   Returns value associated with key, and if it doesn't exist then `default`.

.. method:: update(other)

   Copies all items from other into this dict.

list type
---------

.. method:: append(item)

   Adds item to end of this list

.. method:: extend(list)

   Appends every member of list to this list

.. method:: index(item)

   Returns position of item in list or -1 if not found.  Calls
   :jdoc:`List.indexOf <java/util/List.html#indexOf(java.lang.Object)>`

.. method:: reverse()

   Reverses the order of the elements in the list by calling
   :jdoc:`Collections.reverse <java/util/Collections.html#reverse(java.util.List)>`.

.. method:: pop()

   Removes the last item in the list and returns it

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

.. method:: endswith(suffix)

   Returns True if the string ends with the specified suffix.  Calls
   :jdoc:`String.endsWith <java/lang/String.html#endsWith(java.lang.String)>`.

.. method:: join(list)

   Return a string which is the concatenation of the strings in the
   list, separated by this string.

.. method:: lower()

   Returns lower case version of string by calling
   :jdoc:`String.toLowerCase <java/lang/String.html#toLowerCase()>`.

.. method:: replace(target, replacement)

   Returns a new string replacing all occurrences of `target` with
   `replacement` by calling :jdoc:`String.replace
   <java/lang/String.html#replace(java.lang.CharSequence,
   java.lang.CharSequence)>`.

.. method:: split(sep, maxsplits)

   :param str sep: Separator to use.  If not specified then whitespace
      is used.
   :param int maxsplits: Stop splitting when this many have been found
      with the last item being the remainder of the string.  If not
      specified then all possible splits are found.
   :returns: List of substrings (each not including the separator)

   Splits string into a list of substrings around `sep` stopping when
   maxsplits have been found.

.. method:: startswith(prefix)

   Returns True is the string starts with prefix.  Calls
   :jdoc:`String.startsWith <java/lang/String.html#startsWith(java.lang.String)>`.

.. method:: strip()

   Returns new string omitting leading and trailing whitespace.  Calls
   :jdoc:`String.trim <java/lang/String.html#trim()>`.

.. method:: upper()

   Returns upper case version of string by calling
   :jdoc:`String.toUpperCase <java/lang/String.html#toUpperCase()>`.

.. _global_functions:

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
   greater.  (:ref:`Note <comparisons>`)

.. function:: filter(function, list)

   Returns a new list consisting of members when `function(member)`
   returned true.

.. function:: id(item)

   Returns a numeric code uniquely representing this instance.  Behind
   the scenes it returns the result of
   :jdoc:`System.getIdentityHashcode()
   <java/lang/System.html#identityHashCode(java.lang.Object)>`.

.. function: int(item)

   Returns integer of item.  int items are returned as is, bools as
   0/1 for False/True and strings are parsed.  Note that this
   implementation does not take a base/radix argument.

.. function:: len(item)

   Returns length of item such as number of characters for a str,
   members in a list/dict.

.. function:: map(function, list)

   Returns a new list consisting of function applied to each list
   member.  Use this an alternate to list comprehensions.

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

.. _pyobject:

Object orientation
------------------

You can do a form of object oriented programming where you keep data
and the methods that operate on it together in the same dictionary.
This is because of two features on dictionaries - attribute access and
implicit *self* if attribute access returns a method.

|project| lets you access dictionaries the regular Python way
and as attribute access::

    d={"a": 3}
    # normal way
    d["a"]
    # attribute access
    d.a

If you add a method to a dictionary and then access the method via
attribute access then the dictionary will be added as an implicit
first parameter in calls, which you traditionally call *self*.::

    def meth(self, a):
    	pass

    d={"meth": meth}

    # This call
    d.meth(3)
    # becomes this behind the scenes
    meth(d, 3)

    # Dictionary access won't and this will complain about not enough
    # parameters
    d["meth"](3)

Here is an example of being somewhat object oriented by using
dictionaries with methods.  (Technically this is substantially similar
to `prototype based programming
<http://en.wikipedia.org/wiki/Prototype-based_programming>`__ and
similar to how Javascript works.)::

    # How we make new ones
    def Circle(x, y, radius):

       def area(self):
       	   return radius*radius*31415/10000

       def draw(self, graphics):
       	   graphics.plot(...)

       return {
          # data members
	  "x": x,
	  "y": y,
	  "radius": radius,
	  # method members
	  "area": area,
	  "draw": draw}

    # This is how we make a new instance
    circ=Circle(25, 3, 12)
    print circ.area()
