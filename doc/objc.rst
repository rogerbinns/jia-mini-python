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

:index:`MiniPythonClientDelegate <MiniPythonClientDelegate (Objective C)>`
--------------------------------------------------------------------------

  A place to handle platform behaviour
  
  .. index:: onError: (Objective C method)

  .. method:: - (void)onError:(NSError *)e

     Called whenever there is an error.
     
     This provides one spot where you can perform logging and other
     diagnostics.
     
  .. index:: print: (Objective C method)

  .. method:: - (void)print:(NSString *)s

     Called with a complete string from a print call/statement.  It will
     be newline terminated, unless the print statement had a trailing
     comma.
     

:index:`MiniPython <MiniPython (Objective C)>`
----------------------------------------------

  
  .. index:: setClient: (Objective C method)

  .. method:: - (void)setClient:(id <MiniPythonClientDelegate>)client

     Delegate to use for platform behaviour.
     
     :param client: Replaces existing client with this one.
     
  .. index:: setCode:error: (Objective C method)

  .. method:: - (BOOL)setCode:(NSInputStream *)code error:(NSError **)error

     Loads and executes byte code
     
     :param code: The inputstream must already be opened
     
  .. index:: clear (Objective C method)

  .. method:: - (void)clear

     Removes all internal state.
     
     This ensures that garbage collection is easier. You can reuse this
     instance by calling addModule:named: to reregister modules and
     setCode:error: to run new code.
     
     
  .. index:: addModule:named: (Objective C method)

  .. method:: - (void)addModule:(NSObject*)module named:(NSString *)name

     Makes methods implemented in `module` available within Python
     code as module `name`.
     
     See :ref:`adding methods <objc_adding_methods>` for details on
     which methods are made available.
     
  .. index:: callMethod:args:error: (Objective C method)

  .. method:: - (NSObject *)callMethod:(NSString *)name args:(NSArray *)args error:(NSError **)error

     Calls a method in Python and returns the result
     
     :param name:  Global method name
     :param args:  list of arguments that it takes
     
     If an error occurs then nil will be returned and error (if
     supplied) will point to the :adoc:`NSError`.
     
  .. index:: isCallable: (Objective C method)

  .. method:: - (BOOL)isCallable:(NSObject *)object

     Returns YES if the `object` is a MiniPython object and can be
     called.  This is useful if you need to do type checking.
     
  .. index:: callObject:args:error: (Objective C method)

  .. method:: - (NSObject *)callObject:(NSObject *)object args:(NSArray *)args error:(NSError **)error

     Calls a method in Python and returns the result
     
     :param name:  Global method name
     :param args:  list of arguments that it takes
     
     If an error occurs then nil will be returned and error (if
     supplied) will point to the error.
     
  .. index:: toPyString: (Objective C method)

  .. method:: + (NSString *)toPyString:(NSObject *)value

     Returns a string representing the object using Python nomenclature where
     possible
     
     For example `nil` is returned as `None`, `YES` as `True`
     etc. Container types like dict/NSDictionary and list/NSArray will
     include the items.
     
  .. index:: toPyTypeString: (Objective C method)

  .. method:: + (NSString *)toPyTypeString:(NSObject *)value

     Returns a string representing the type of the object using Python
     nomenclature where possible
     
     For example `nil` is returned as `NoneType`, `YES` as `bool`,
     `NSDictionary` as `dict` etc.
     
     :param value:  Object whose type to stringify
     
  .. index:: toPyReprString: (Objective C method)

  .. method:: + (NSString *)toPyReprString:(NSObject *)value

     Same as toPyString except strings are quoted and backslash
     escaped. If you emit an error message this is preferable as it
     makes it clear a value is a string.
     
  .. index:: setError:reason:userInfo: (Objective C method)

  .. method:: - (void)setError:(enum MiniPythonErrorCode)code reason:(NSString *)reason userInfo:(NSDictionary *)userinfo

     Use this function to indicate an error has occurred, for example in
     a :ref:`module method <objc_adding_methods>`.  See also
     :ref:`objcerror`.
     
  .. index:: setNSError: (Objective C method)

  .. method:: - (void)setNSError:(NSError *)error

     Similar to setError:readon:userInfo: except supplying a generic
     :adoc:`NSError`.
     
  .. index:: getError (Objective C method)

  .. method:: - (NSError *)getError

     Returns the most recent error
     
