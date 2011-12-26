Java API Reference
==================

.. You need to hava Java domain support from https://bitbucket.org/danc/sphinx-contrib/src

.. default-domain:: java

:index:`Types`
--------------

Where possible types are mapped directly from Python to Java.

+------------------------------+------------------------------+
| Python type                  | Java type                    |
+==============================+==============================+
| int                          | int/Integer - 32 bit signed  |
+------------------------------+------------------------------+
| str/unicode                  | String (unicode only)        |
+------------------------------+------------------------------+
| None                         | null                         |
+------------------------------+------------------------------+
| bool                         | boolean/Boolean              |
+------------------------------+------------------------------+
| dict                         | Map<Object, Object>          |
+------------------------------+------------------------------+
| list/tuple                   | List<Object>                 |
+------------------------------+------------------------------+

Objects in Map and List should only be ones present in the table.
Note that tuples are mutable and treated indistinguishably from lists.

Your added methods can return types other than the above without
error.  However there will be type errors if you try to operations on
them (eg use them as an `if` express, add to them).

.. _adding_methods:

:index:`Adding methods`
-----------------------

You can make methods available to the Python by calling
`MiniPython.addModule`.

.. code-block:: java

    class timeinfo {
       private void not_exposed() {}

       // using types from above
       public boolean isdst() { return false; }
       public int day_of_week(int year, int month, day) {  return 2; }
       public int sum_all(List<Object> items) { return 17; }

       // You can use other types
       public Widget get_widget() { return new Widget(); }
       public void show_widget(Widget w, boolean show) { if(show) w.show(); else w.hide(); }

       // varargs is supported
       public String printf(String fmt, Object ...items) { return String.format(fmt, items); }
    }

    // register it as a module named "example"
    MiniPython mp=new MiniPython();
    mp.addModule("example", new timeinfo());

You can then call these from Python::

    print example.isdst()
    print example.sum_all([1, 2, 3, 4])
    w=example.get_widget()
    example.show_widget(w, True)

Exposure
********

Only methods that have been declared `public` will be available.
Additionally the method has to be implemented directly in the class.
For example `toString` is not available in the above example as it is
implemented in a parent class.

If you have multiple methods with the same name, declared `public` and
implemented directly in the class (eg taking different numbers of
arguments) then the one to be used is picked at random.  No attempt is
made to try and select a method based on number or type of arguments.

No attempt is made to convert method parameters.  For example if a
method takes a `boolean` and a `list` is provided then the `list` will
not be converted to a `boolean`.

Errors
******

If your code encounters an error (for example one of the list items
not being an integer in the sum_all method above) then you should call
`MiniPython.signalError`.  Note that it will throw
ExecutionError after performing internal bookkeeping (eg tracking line
numbers) and not return.

Class
=====

.. class:: MiniPython

   This class implements the MiniPython environment.

   .. method:: void addModule(String name, Object methods)

      Makes methods on the methods Object available to the Python.
      See `Adding methods`_ for more details.

   .. method:: void setCode(InputStream stream)

      Reads the code from the supplied stream.  The stream is not
      closed and you can have additional content after the jmp.
   
      :raises EOFException: When the stream is truncated
      :raises IOException: Passed on from read() calls on the stream
      :raises ExecutionError: Any issues from executing the code

   .. method:: void setClient(Client client)

      Sets the :class:`Client` to use for specific behaviour.

   .. method:: void signalError(String exctype, String message)

      Call this method when your callbacks need to halt execution due
      to an error.

      :param exctype: Best practise is to use the name of a Python
         exception (eg "TypeError")
      :param message: Text describing the error.

      This method will do the internal bookkeeping necessary in order
      to provide diagnostics to the original caller and then throw an
      :class:`ExecutionError` which you should not catch.


   .. method:: String toPyString(Object o)

      Returns a string representing the object using Python
      nomenclature where possible.  For example `null` is returned as
      `None`, `true` as True etc.  For compound types like `dict/Map`
      and `list/List` the string returned notes their type and how
      many items are contained but does not include a string
      representation of the items.

      This method is useful for generating error messages and
      diagnostics.

   .. class:: ExecutionError
  
      This class extends :class:`Exception` encapsulating errors found while executing code.

      .. method:: String getType()

         Returns a string with the exception type.  This will usually
         match Python - eg "TypeError"

      .. method:: String toString()

         Returns "type: message" for the error

      .. method:: int linenumber()

         Returns which linenumber was being executed when the error happened.
  

   .. class:: Client

      Implement this interface to provide behaviour, and register with `MiniPython.setClient`.

      .. method:: void print(String s)

       	 Print the provided string.  Note that it will have a final
         newline if the print statement in the code did.  If the print
         statement ended in a trailing comma then it will end in a
         space.

	 Call `signalError` if there is an error in your print
	 code.
