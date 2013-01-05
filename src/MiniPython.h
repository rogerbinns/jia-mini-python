#import "Foundation/Foundation.h"

@protocol MiniPythonClientDelegate <NSObject>
- (void) print:(NSString*)s;
- (void) onError:(NSError*)e;
@end


enum MiniPythonErrorCode {
  // these errors occur during loading
  MiniPythonOutOfMemory=0,
  MiniPythonNeedsClear=1,          // you need to call clear to reuse the instance
  MiniPythonEndOfStreamError=2,    // unexpected end of stream reading data
  MiniPythonStreamError=3,         // error reading from stream
  MiniPythonUnknownVersionError=4, // unknown jmp bytecode version

  // not because of well formed code
  MiniPythonInternalError=10,       // various out of bounds and similar errors which are only
                                    // possible from malformed bytecode
  MiniPythonRuntimeError=11,        // exceeding stack bounds etc

  /// various things
  MiniPythonTypeError=100,         // incorrect types
  MiniPythonArithmeticError=101,   // division/mod by zero etc
  MiniPythonAssertionError=102,    // assertion failed
  MiniPythonNameError=103,         // name doesn't exist
  MiniPythonGeneralError=104,      // Non specific via setError:userInfo:
  MiniPythonIndexError=105,        // array bounds
  MiniPythonKeyError=106,          // key not in dict
  MiniPythonAttributeError=107,    // no such attribute of an object
  MiniPythonSyntaxError=108,       // return outside a function
  MiniPythonValueError=109         // correct type, wrong contents
};

@interface MiniPython : NSObject
- (void) setClient:(id <MiniPythonClientDelegate>)client;
- (void) clear;
// inputstream must already be opened
- (BOOL) setCode:(NSInputStream*)code error:(NSError**)error;
+ (NSString*) toPyString:(NSObject*) value;
+ (NSString*) toPyTypeString:(NSObject*)value;
+ (NSString*) toPyReprString:(NSObject*)value;
- (void) setError:(enum MiniPythonErrorCode)code reason:(NSString*)reason userInfo:(NSDictionary*)userinfo;
- (void) setNSError:(NSError*)error;
- (NSError*) getError;
- (void) addModule:(NSObject*)module named:(NSString*)name;
- (NSObject*) callMethod:(NSString*)name args:(NSArray*)args error:(NSError**)error;
@end

// Error handling
extern NSString * const MiniPythonErrorDomain;

