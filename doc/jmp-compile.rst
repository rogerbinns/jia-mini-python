jmp-compile
===========

This is the tool used to turn your Python syntax source into the
internal representation used.  It can also dump the internal
representation.

You can use Python 2.6+ or 3.1+ to run `jmp-compile`.

.. program:: jmp-compile

Compiling
---------

`jmp-compile [options] input.py [output.jmp]`

Produces an internal representation from `input.py`.  By default the
output is alongside the input with a `.jmp` extension.

.. option:: --print-function

    If you run under Python 2 then `print` will be treated as a
    statement.  Supplying this flag will treat it is as a function.
    If you run `jmp-compile` under Python 3 then `print` is always
    treated as a function.

.. option:: --asserts

    By default asserts are ignored.  If you supply this flag then
    asserts will be evaluated and an exception to be thrown if it does
    not evaluate to a true value.

.. option:: --omit-line-table

    Normally a table that maps between internal program counter value
    and the corresponding source line number is included in the
    output.  This allows line numbers to be given in exceptions.
    However it consumes 4 bytes per line of executable code so you can
    save space by specifying this flag.  You can always work out the
    line number from a program counter using annotated output.

.. option:: --annotate

    Places a file alongside the output with an extension of `.i` that
    has the source lines intermingled with the internal representation
    like :option:`--dump` output.  It is recommended you use this
    option if omitting the line table so that later you can map the
    program counter to the corresponding line as this output always
    includes the line information.  You can see an example annotated
    file below.

.. option:: --syntax

    Does not produce an output file.  This checks the syntax and that
    various limits (eg string length, jmp size) are not exceeded.  The
    exit code will be non-zero on any error.

.. option:: --no-optimization

    Turns off optimizations such as constant expressions (replacing
    ``3+4`` with ``7`` and ``True or 7`` with ``True``) and omitting
    unreachable code (eg ``if False``).

.. option:: --constant name=value

   Can be supplied multiple times.  value must be in Python syntax and
   can be any expression.  For example ``--constant DEBUG=True``,
   ``--constant VERSION="2alpha1"``, ``--constant mapping={3: "Three",
   4: "a"*7, 5: func(1,2,3)}``.  Be careful of the shell altering what
   you provide on the command line.


Dumping
-------

`jmp-compile --dump [options] file.jmp`

This prints the internal representation from a `.jmp` file.

.. option:: --dump

    Turns on dump mode

.. option:: --dump-source <input.py>

    Optional input file the `.jmp` was produced from.  The source
    lines are intermingled with the output.  By default a `.py` file
    alongside the `.jmp` file is looked for.

Dumping Example
***************

This is an example of :option:`--dump` or :option:`--annotate`
output.  :doc:`internals` describes what is going on in more detail.

.. literalinclude:: dumpexample.i
