Example
*******

Write your Python code::

  def get_brightness():
    if time.day_of_week() == 4 and launches < 3:
       return 10
    return 7

Turn that into the bytecode that Java Mini Python uses.  This checks
the syntax, tokenizes and produces a smaller file.  The output is by
default the same filename as the input but with an extension of .jmp::

  jmp-compile settings.py

Add the Java Mini Python java source to your project.  It is one .java
file and you can put it anywhere.  Using your own namespace is
recommended.  This means you do not have to worry about anyone else
using it as well, having version clashes etc.

.. code-block:: java

  // make new instance
  JMP jmp=new JMP();
  // make methods available
  class timestuff { 
       int day_of_week() { return 4; } 
  };
  jmp.addModule("time", new timestuff());
  // give it code to run
  jmp.setCode(inputStream);
  // Call a method 
  int brightness=jmp.callInt("get_brightness");
