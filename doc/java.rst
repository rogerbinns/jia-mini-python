Java API Reference
==================

.. You need to hava Java domain support from https://bitbucket.org/danc/sphinx-contrib/src

.. default-domain:: java

:index:`Types`
--------------

Where possible types are mapped directly from Python to Java.

+--------------+---------------------------------------------------+
| Python type  | Java type                                         |
+==============+===================================================+
| int          | int/Integer - 32 bit signed                       |
+--------------+---------------------------------------------------+
| str          | String (unicode only)                             |
+--------------+---------------------------------------------------+
| None         | null                                              |
+--------------+---------------------------------------------------+
| bool         | boolean/Boolean                                   |
+--------------+---------------------------------------------------+
| dict         | :jdoc:`Map <java/util/Map.html>` <Object, Object> |
+--------------+---------------------------------------------------+
| list         | :jdoc:`List <java/util/List.html>` <Object>       |
+--------------+---------------------------------------------------+

Note that tuples are mutable and treated as lists.

Your added methods can return types other than the above without
error.  However there will be type errors if you try to perform
operations on them (eg use them as an `if` expression or add them).

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
method takes a `boolean` and an `int` is provided then the `int` will
not be converted to a `boolean`.

Errors
******

If your code encounters an error (for example one of the list items
not being an integer in the sum_all method above) then you should call
`MiniPython.signalError`.  Note that it will throw
ExecutionError after performing internal bookkeeping (eg tracking line
numbers) and not return.

.. Rest of file is generated from Javadoc - do not edit

.. _MiniPython:

class MiniPython
----------------

.. class:: MiniPython

   (`javadoc <_static/javadoc/com/rogerbinns/MiniPython.html>`__)
   Encapsulates running a Python syntax file.

   The source should have been transformed using jmp-compile. The class is not
   threadsafe and calls should only be made in the same thread. There is no
   shared state between instances.

   .. method:: void addModule(String name, Object object)

      Makes methods on the methods Object available to the Python

      :param name:  Module name in the Python environment
      :param object:  Object to introspect looking for methods

      .. seealso:: `Adding methods <java.html#id1>`__

   .. method:: Object callMethod(String name, Object... args)

      Calls a method in Python and returns the result

      :param name:  Global method name
      :param args:  Variable list of arguments that it takes
      :raises ExecutionError:  On any issues encountered

   .. method:: void clear()

      Removes all internal state.

      This ensures that garbage collection is easier. You can reuse this
      instance by calling addModule to reregister modules and setCode to run
      new code.

   .. method:: void setClient(Client client)

      Callbacks to use for specific behaviour

      :param client:  Replaces existing client with this one

   .. method:: void setCode(InputStream stream)

      Reads and executes code from the supplied stream

      The stream provided must satisfy reads completely (eg if 27 bytes is
      asked for then that number should be returned in the read() call unless
      end of file is reached.)

      :param stream:  The stream is not closed and you can have additional content
                 after the jmp.
      :raises IOException:  Passed on from read() calls on the stream
      :raises EOFException:  When the stream is truncated
      :raises ExecutionError:  Any issues from executing the code

   .. method:: void signalError(String exctype, String message)

      Call this method when your callbacks need to halt execution due to an
      error

      This method will do the internal bookkeeping necessary in order to
      provide diagnostics to the original caller and then throw an
      ExecutionError which you should not catch.

      :param exctype:  Best practise is to use the name of a Python exception (eg
                 "TypeError")
      :param message:  Text describing the error.
      :raises ExecutionError:  Always thrown

   .. method:: String toPyString(Object o)

      Returns a string representing the object using Python nomenclature where
      possible

      For example `null` is returned as `None`, `true` as `True` etc. Container
      types like dict/Map and list/List will include the items.

      :param o:  Object to stringify. Can be null.

   .. method:: static String toPyTypeString(Object o)

      Returns a string representing the type of the object using Python
      nomenclature where possible

      For example `null` is returned as `NoneType`, `true` as `bool`, `Map` as
      `dict` etc. You can also pass in Class objects as well as instances. Note
      that primitives (eg `int`) and the corresponding boxed type (eg
      `Integer`) will both be returned as the same string (`int` in this case).

      :param o:  Object whose type to stringify, or a Class or null

.. _Client:

interface MiniPython.Client
---------------------------

.. class:: MiniPython.Client

   (`javadoc <_static/javadoc/com/rogerbinns/MiniPython.Client.html>`__)
   Provide platform behaviour

   .. method:: void onError(ExecutionError error);

      Called whenever there is an ExecutionError.

      This provides one spot where you can perform logging and other
      diagnostics.

      :param error:  The instance that is about to be thrown

   .. method:: void print(String s)

      Request to print a string

      :param s:  String to print. May or may not contain a trailing newline
                 depending on code
      :raises ExecutionError:  Throw this if you experience any issues

.. _ExecutionError:

class MiniPython.ExecutionError
-------------------------------

.. class:: MiniPython.ExecutionError

   (`javadoc <_static/javadoc/com/rogerbinns/MiniPython.ExecutionError.html>`__)
   Encapsulates what would be an Exception in Python.

   Do not instantiate one directly - call signalError instead.


   .. method:: String getType()

      Returns the type of the error.

      This typically corresponds to a Python exception (eg `TypeError` or
      `IndexError`)

   .. method:: int linenumber()

      Returns the line number which was being executed when the error
      happened.

      If you omitted line numbers then -1 is returned.

   .. method:: int pc()

      Returns program counter when error occurred.

      Note that due to internal implementation details this is the next
      instruction to be executed, not the currently executing one.

   .. method:: String toString()

      Returns "type: message" for the error
