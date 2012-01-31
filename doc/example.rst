:index:`Example`
****************

Write your Python code::

  launches=0

  def get_brightness(base):
    if time.day_of_week() == 4 and launches < 3:
       return base+10
    return base+7

Turn that into the bytecode that Java Mini Python uses.  This checks
the syntax, tokenizes and produces a smaller file.  The output is by
default the same filename as the input but with an extension of .jmp::

  jmp-compile settings.py

Add the Java Mini Python java source file to your project.  It is one
.java file and you can put it anywhere.  Using your own namespace is
recommended.  This means you do not have to worry about anyone else
using it as well, having version clashes etc.

.. code-block:: java

  // make new instance
  MiniPython mp=new MiniPython();

  // make methods available
  class timestuff { 
       int day_of_week() { return 4; } 
  };
  mp.addModule("time", new timestuff());

  // provide print and other Client behaviour
  mp.setClient(new MiniPython.Client() {
      @Override
      void print(String s) {
           System.out.print(s);
      }
      @Override
      void onError(Execution error) {
        // a single location to log, dissect or otherwise deal
	// with any error
      }     
  });

  // give it code to run in an inputstream from a file, network etc
  mp.setCode(new FileInputStream("settings.jmp"));

  // Call a method 
  int brightness=(Integer)mp.callMethod("get_brightness", 2);
