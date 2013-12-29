Internals
=========

Overview
--------

Executing a language is a multi step process:

* Tokenize the input (keywords, numbers, strings, etc)
* Parse into pieces according to the grammar (eg an if statement would
  be composed of a test, a true arm and an optional else arm)
* Output some sort of code to represent that.  For example `3+4*5`
  would need to multiply 4 by 5 and then add 3.
* Execute that code - it could be `machine code
  <http://en.wikipedia.org/wiki/Machine_code>`__ executed directly by
  the processor, or something higher level `interpreted by a program
  <http://en.wikipedia.org/wiki/Interpreter_(computing)>`__.  (It gets
  lots more complicated than that with combinations of the two,
  translating dynamically from the latter to the former.  This is
  outside the scope of a `mini` implementation.)

Fortunately Python already has code that performs the tokenizing and
parsing in the `ast module <http://docs.python.org/library/ast>`__::

 >>> ast.dump(ast.parse("3+4*5"))
 'Module(body=[Expr(value=BinOp(left=Num(n=3), op=Add(), right=BinOp(left=Num(n=4), op=Mult(), right=Num(n=5))))])'
 >>> ast.dump(ast.parse("if 3+4>6: print x"))
 "Module(body=[If(test=Compare(left=BinOp(left=Num(n=3), op=Add(), right=Num(n=4)), ops=[Gt()], comparators=[Num(n=6)]), body=[Print(dest=None, values=[Name(id='x', ctx=Load())], nl=True)], orelse=[])])"
 >>> 

The code representation used is custom `bytecode
<http://en.wikipedia.org/wiki/Bytecode>`__ with about 40 different
operations.  These encompass control flow (if, for, goto), comparisons
(> <= != etc), operators (* + - / etc), subscripts (eg x[y]),
variables etc.  Data is stored on a stack with operations acting on
the stack.  For example `ADD` takes the top two items off the stack,
adds them and then puts the result back on the stack.
:doc:`jmp-compile` contains the code that visits the hierarchy from
ast and turns it into this bytecode.

The MiniPython Java code is what interprets the bytecode.  It
maintains the virtual stack, a context mapping variable names to
values and the virtual `program counter
<http://en.wikipedia.org/wiki/Program_counter>`__.  The actual
bytecode execution is done in the internal `mainLoop` method which is
essentially a large `switch statement
<http://en.wikipedia.org/wiki/Switch_statement>`__ on whatever the
bytecode is at the program counter.

Bytecode Format
---------------

Instructions
************

Instructions take one of two forms.  If their value is less than 128
then they are a single byte.  If 128 or greater then they are followed
by an additional 2 bytes making up an unsigned 16 bit integer (`little
endian <http://en.wikipedia.org/wiki/Endianness#Little-endian>`__).

For control flow instructions the number is a relevant program counter
address.  For string instructions it is an index into the string
table.  For integer instructions it is used as is.

JMP file
********

Numbers are always two bytes little endian and should be sufficient
for anticpated usage (note `Mini` in the name).  However if there is a
need to expand in the future then the version header allows for the
representation to be updated.

+--------------+-------------------------------------------------------+
| Size (bytes) | Description                                           |
+==============+=======================================================+
|      2       |Version header.  Currently only 0 is supported.        |
+--------------+-------------------------------------------------------+
|      2       |Number of strings in the string table                  |
+--------------+-------------------------------------------------------+
|  variable    |Each string is two bytes of size information followed  |
|              |by the UTF8 bytes making up the string.  There is no   |
|              |null terminator or similar.                            |
+--------------+-------------------------------------------------------+
|      2       |Number of entries in the line number table             |
+--------------+-------------------------------------------------------+
| entries*4    |Each entry in the table is four bytes consisting of two|
|              |numbers mapping a program counter to a line number.    |
|              |When subsequent program counters map to the same line  |
|              |number they are omitted from the table so there will be|
|              |one entry per line of executable code in the source    |
+--------------+-------------------------------------------------------+
|     2        | Size of the code                                      |
+--------------+-------------------------------------------------------+
| code size    | The raw bytes making up the code                      |
+--------------+-------------------------------------------------------+
						      
Anatomy of MiniPython.java
--------------------------

The main data structure is a stack of Objects, a stack pointer and a
context.  The stack holds the data to be operated on.  The context
holds a mapping of variable names to their values.  :doc:`Java <java>`
types are used wherever possible.

The function `mainLoop` contains the switch statement on the current
instruction.  Each instruction examines its data, throws exceptions if
unsuitable or performs the operation.  Since existing Java types are
used they don't know about Python semantics and the code uses lots of
`instanceof`.

Calling Java code is very complicated and implemented in the
`nativeCall` function.  It should just be a simple call to
`Method.invoke
<http://docs.oracle.com/javase/7/docs/api/java/lang/reflect/Method.html#invoke(java.lang.Object, java.lang.Object...)>`__ 
but that has several short comings.  It doesn't handle `variable arguments
<http://en.wikipedia.org/wiki/Variable_argument_list#Variadic_functions_in_C.23.2C_C.2B.2B.2FCLI.2C_VB.net.2C_and_Java>`__
requiring that `nativeCall` has to do the packing from variable
arguments to the final parameter array.  Additionally when types are
not correct you get an `IllegalArgumentException
<http://docs.oracle.com/javase/7/docs/api/java/lang/IllegalArgumentException.html>`__
with no further detail.  This is extremely unhelpful since you
wouldn't know which parameter is the problem or which types should
have been used.  Consequently `nativeCall` does the type checking
itself so that useful error messages can be given.

:ref:`global_functions` are implemented by finding class member methods with
an appropriate name prefix and added to the root context.
`nativeCall` ensures they are called correctly.

:doc:`Instance methods <python>` are implemented in a substantially
similar manner except they are looked for when the code does a name
lookup on an item.

There are a few other nested classes to hold various pieces of data
(eg "modules").

Example
-------

The listing shows :option:`--dump` output.  The first numeric column
is the code offset.  This is followed by the name of the instruction.
Near the bottom of :doc:`jmp-compile` is the list of name to byte
value mappings.  For instructions that reference strings the relevant
string table entry is shown as a comment.

The `MiniPython.java` contains the exact implementation for each
instruction.  This is a brief explanation of some of the ones you see
in the listing.

.. describe:: PUSH_INT

    Puts the number on the stack.  (There is a separate PUSH_INT_HI
    used for numbers that don't fit in two bytes.)
.. describe:: ADD

    Adds top two items on stack, pushes result.  (Note that items
    could be numbers, strings, lists etc)
.. describe:: STORE_NAME

    Takes the top item off the stack and saves it in a variable with
    the specified name
.. describe:: LOAD_NAME

    Puts contents of the named variable onto the stack
.. describe:: GT

    Removes top two stack items pushing True or False depending on if
    greater than
.. describe:: IF_FALSE

    Take the top item off the stack and if it evaluates to False then
    go to the instruction number specified.  False itself as well as
    empty strings/list/dicts, the number 0 and None are all considered false.
.. describe:: PUSH_TRUE

    Pushes True onto the stack
.. describe:: PRINT

    Print statement builtin which needs to know if a newline should be
    emitted (the True or False pushed beforehand) as well as how many
    items it should print.

.. describe:: FUNCTION_PROLOG

    Takes top item off the stack which is how many parameters the
    function takes.  It ensures that number were provided plus various
    other housekeeping operations.

.. literalinclude:: dumpexample.i
