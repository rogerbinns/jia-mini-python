:index:`Example`
****************

Python Source
=============

Write your Python code::

  launches=0

  def get_brightness(base):
    if time.day_of_week() == 4 and launches < 3:
       return base+10
    return base+7

Turn that into the bytecode that |project| uses with
:doc:`jmp-compile`.  This checks the syntax, tokenizes and produces a
smaller file.  The output is by default the same filename as the input
but with an extension of .jmp::

  jmp-compile settings.py

Java
====

Add the |project| java source file to your project.  It is one .java
file and you can put it anywhere.  Using your own namespace is
recommended.  This means you do not have to worry about anyone else
using it as well, having version clashes etc.

.. code-block:: java

  // make new instance
  MiniPython mp=new MiniPython();

  // make methods available
  class timestuff {
       int day_of_week() { return 4; }
  }

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

  // give it code to run in an inputStream from a file, network etc
  mp.setCode(new FileInputStream("settings.jmp"));

  // Call a method passing in one parameter
  int brightness=(Integer)mp.callMethod("get_brightness", 2);

Objective C
===========

Add :file:`MiniPython.h` to relevant files, and :file:`MiniPython.m`
to your project.  Use it like this.

.. code-block:: objc

   // the module we want to add
   @interface timestuff
   @end

   @implementation timestuf
   - (int) day_of_week {
     return 4;
   }
   @end

   // MiniPythonClientDelegate methods
   - (void)print:(NSString *)s {
       NSLog(@"MiniPython: %@", s);
   }

   - (void)onError:(NSError *)e {
        // a single location to log, dissect or otherwise deal
	// with any error
   }

   // make new instance
   MiniPython *mp=[[MiniPython alloc] init];

   [mp addModule:[[timestuff alloc] init] named:@"time"];
   [mp setClient:self];

   // give it code to run
   NSInputStream *in=[NSInputStream inputStreamWithFileAtPath:filename];
   [in open];

   NSError *error;
   BOOL success=[mp setCode:in error:&error];

   // call a method passing in one parameter
   int brightness=[(NSNumber*)[mp callMethod:@"get_brightness" args:@[@2] error:&error] intValue];
