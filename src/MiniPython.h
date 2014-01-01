#import "Foundation/Foundation.h"

// Points to the string constant for errors from MiniPython
extern NSString *const MiniPythonErrorDomain;

/**
   A place to handle platform behaviour
*/
@protocol MiniPythonClientDelegate <NSObject>
/**
   Called whenever there is an error.

   This provides one spot where you can perform logging and other
   diagnostics.
 */
- (void)onError:(NSError *)e;
/**
   Called with a complete string from a print call/statement.  It will
   be newline terminated, unless the print statement had a trailing
   comma.
*/
- (void)print:(NSString *)s;

@end


enum MiniPythonErrorCode {
    // these errors occur during loading
    MiniPythonOutOfMemory = 0,
    MiniPythonNeedsClear = 1,          // you need to call clear to reuse the instance
    MiniPythonEndOfStreamError = 2,    // unexpected end of stream reading data
    MiniPythonStreamError = 3,         // error reading from stream
    MiniPythonUnknownVersionError = 4, // unknown jmp bytecode version

    // not because of well formed code
    MiniPythonInternalError = 10,       // various out of bounds and similar errors which are only
                                        // possible from malformed bytecode
    MiniPythonRuntimeError = 11,        // exceeding stack bounds etc

    // various things
    MiniPythonTypeError = 100,         // incorrect types
    MiniPythonArithmeticError = 101,   // division/mod by zero etc
    MiniPythonAssertionError = 102,    // assertion failed
    MiniPythonNameError = 103,         // name doesn't exist
    MiniPythonGeneralError = 104,      // Non specific via setError:userInfo:
    MiniPythonIndexError = 105,        // array bounds
    MiniPythonKeyError = 106,          // key not in dict
    MiniPythonAttributeError = 107,    // no such attribute of an object
    MiniPythonSyntaxError = 108,       // eg: return outside a function
    MiniPythonValueError = 109         // correct type, wrong contents
};

@interface MiniPython : NSObject
/**
   Delegate to use for platform behaviour.

   :param client: Replaces existing client with this one.
 */
- (void)setClient:(id <MiniPythonClientDelegate>)client;

/**
   Loads and executes byte code

   :param code: The inputstream must already be opened
*/
- (BOOL)setCode:(NSInputStream *)code error:(NSError **)error;

/**
   Removes all internal state.

   This ensures that garbage collection is easier. You can reuse this
   instance by calling addModule:named: to reregister modules and
   setCode:error: to run new code.

 */
- (void)clear;

/**
   Makes methods implemented in `module` available within Python
   code as module `name`.

   See :ref:`adding methods <objc_adding_methods>` for details on
   which methods are made available.
*/
- (void)addModule:(NSObject*)module named:(NSString *)name;

/**
   Calls a method in Python and returns the result

   :param name:  Global method name
   :param args:  list of arguments that it takes

   If an error occurs then nil will be returned and error (if
   supplied) will point to the :adoc:`NSError`.
 */
- (NSObject *)callMethod:(NSString *)name args:(NSArray *)args error:(NSError **)error;

/**
   Returns YES if the `object` is a MiniPython object and can be
   called.  This is useful if you need to do type checking.
*/
- (BOOL)isCallable:(NSObject *)object;
/**
   Calls a method in Python and returns the result

   :param name:  Global method name
   :param args:  list of arguments that it takes

   If an error occurs then nil will be returned and error (if
   supplied) will point to the error.
 */
- (NSObject *)callObject:(NSObject *)object args:(NSArray *)args error:(NSError **)error;

/**
   Returns a string representing the object using Python nomenclature where
   possible

   For example `nil` is returned as `None`, `YES` as `True`
   etc. Container types like dict/NSDictionary and list/NSArray will
   include the items.
*/
+ (NSString *)toPyString:(NSObject *)value;

/**
   Returns a string representing the type of the object using Python
   nomenclature where possible

   For example `nil` is returned as `NoneType`, `YES` as `bool`,
   `NSDictionary` as `dict` etc.

   :param value:  Object whose type to stringify
*/
+ (NSString *)toPyTypeString:(NSObject *)value;

/**
   Same as toPyString except strings are quoted and backslash
   escaped. If you emit an error message this is preferable as it
   makes it clear a value is a string.
*/
+ (NSString *)toPyReprString:(NSObject *)value;

/**
   Use this function to indicate an error has occurred, for example in
   a :ref:`module method <objc_adding_methods>`.  See also
   :ref:`objcerror`.
*/
- (void)setError:(enum MiniPythonErrorCode)code reason:(NSString *)reason userInfo:(NSDictionary *)userinfo;

/**
   Similar to setError:readon:userInfo: except supplying a generic
   :adoc:`NSError`.
*/
- (void)setNSError:(NSError *)error;

/**
   Returns the most recent error
*/
- (NSError *)getError;
@end
