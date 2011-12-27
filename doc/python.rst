Python reference
================

See :doc:`lang` for an overview of what types and operations are
supported.  Java Mini Python does not have an internal object model -
instead Java types are :doc:`used directly <java>`.  This keeps the
code considerably smaller.  But it also means that most Python
attributes (eg functions) do not exist.  For example in Python
integers have 64 different attributes.

list type
---------

.. method:: append(item)

   Adds item to end of list (modify in place)

str type
--------

.. method:: upper()

   Returns upper case version of string.

Global functions
----------------

.. function:: bool(item)

   Returns a boolean for the item.  For example it is True for
   non-zero integers and strings/list/dict that contain at least one item.

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

   Returns the string corresponding to item.  Note that if the item is
   a dict or list then it will not include the members, just a note of
   how many members there are.  (Turning a dict/list into a string
   including members robustly takes lots of code and memory as members
   could be other containers that then contain the root collection
   leading to infinite items.)

   For :doc:`non basic types <java>` their :jdoc:`toString()
   <java/lang/Object.html#toString()>` method is called.

.. function:: type(item)

   Unlike regular Python this returns a string.  For the basic types
   it will be the expected name.  For others it will be their
   :jdoc:`Class.getSimpleName()
   <java/lang/Class.html#getSimpleName()>`.
