Objective C API Reference
=========================

.. default-domain:: objc

:index:`Types <single:Types; Objective C>`
------------------------------------------

Where possible types are mapped directly from Python to Objective C

+------------+--------------------------------------+
|Python type |Objective-C type                      |
+============+======================================+
|int         |int/:adoc:`NSNumber` (32 bit signed)  |
+------------+--------------------------------------+
|str         |:adoc:`NSString` (Unicode only)       |
+------------+--------------------------------------+
|None        |nil/:adoc:`NSNull` in collections     |
+------------+--------------------------------------+
|bool        |BOOL/:adoc:`NSNumber`                 |
+------------+--------------------------------------+
|dict        |:adoc:`NSMutableDictionary`           |
+------------+--------------------------------------+
|list        |:adoc:`NSMutableArray`                |
+------------+--------------------------------------+

.. note::

   The mutable forms of NSDictionary and NSArray (but not NSString)
   are always created by the MiniPython code.  When they come from
   outside attempts are made to detect that they are the mutable
   versions before performing mutating operations, but in general that
   doesn't work (eg isKindOfClass will return true even when it
   isn't).  Consequently you will get Objective C level exceptions
   performing mutating operations on NSDictionary/Array that came from
   outside of MiniPython.

.. _objc_adding_methods:

:index:`Adding methods <single:Adding methods; Objective C>`
------------------------------------------------------------

You can make methods available to the Python by calling `MiniPython
addModule:named:`.  Supply a delegate instance and what its name
inside MiniPython should be.

Only a first method name part should be present, with the number of
colons matching the number of parameters.  For example `ameth:(id)arg1
:(id)arg2` is fine while `ameth:(id)arg1 foo:(id)arg2` is not.  You
can supply methods with the same name but differing numbers of
arguments.  Only methods directly implemented in the delegate are
callable - those in parent classes are not.

.. code-block:: objc

   @implementation timeinfo
   {
     // Weak ensures we don't have a reference cycle
     MiniPython* __weak mp;
   }

   // not callable due to multiple name parts
   - (void) init:(MiniPython*)mp_ withName:(NSString*)name {
     if((self=[super init])) {
       // save a copy so we can set errors
       mp=mp_;
       [mp addModule:mp_ named:name];
     }
     return self;
   }

   // using regular types from table above
   - (BOOL) isdst { return NO; }
   - (int) day_of_week:(int)year :(int)month :(int)day { return 2; }
   - (int) sum_all:(NSArray*)items {
       // Note: item's type is not guaranteed beyond being an id.  You should check.
       if(![items isKindOfClass:[NSArray class]]) {
         [mp setError:MiniPythonTypeError reason:
             [NSString stringWithFormat:@"Expected list not %@", [mp toPyTypeString:items]]
             userInfo:nil];
         // return value is ignored
         return 0;
       }
       // dummy code
       return 17;
     }

   // You can use other types
   - (Widget*) get_widget { return [[Widget alloc] init]; }
   - (void) show_widget:(Widget*)w :(BOOL)show {
       if(show) [w show]; else [w hide];
     }

   @end

   MiniPython *mp=[[MiniPython alloc] init];
   [[timeinfo alloc] init:mp withName:@"example"];

You can then call these from Python.

.. code-block:: python

   print example.isdst()
   print example.sum_all([1,2,3,4])
   w=example.get_widget()
   example.show_widget(w, True)

.. _objcerror:

:index:`Errors <single:Errors; Objective C>`
--------------------------------------------

To report an error you need to invoke `setError: reason: userInfo:` on
the MiniPython instance.  The code above has an example of issuing a
TypeError.

`setCode: error:` and `callObject: args: error:` both take an in
parameter of `NSError**`.  If an error occurs it will point to an
:adoc:`NSError`.  The domain will have the value as pointed to by
`MiniPythonErrorDomain` and the code will be from the
`MiniPythonErrorCode` enumeration.


.. Rest of file is generated from MiniPython.h - do not edit

MiniPython
----------

.. class:: MiniPython

   .. method:: - (void)clear

      Blah blah
