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

