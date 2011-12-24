Java API Reference
==================

.. You need to hava Java domain support from https://bitbucket.org/danc/sphinx-contrib/src

.. default-domain:: java

.. class:: MiniPython

   This class implements the MiniPython environment.

   .. method:: void setCode(InputStream stream)

      Reads the code from the supplied stream.  The stream is not
      closed and you can have additional content after the jmp.
   
      :raises EOFException: When the stream is truncated
      :raises IOException: Passed on from read() calls on stream
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

      Implement this interface to provide behaviour.

      .. method:: void print(String s)

       	 Print the provided string.  Note that it will have a final
         newline if the print statement in the code did.  If the print
         statement ended in a trailing comma then it will end in a
         space.

	 Call `signalError` if there is an error in your print
	 code.
