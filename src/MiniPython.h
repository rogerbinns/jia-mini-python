#import "Foundation/Foundation.h"

@protocol MiniPythonClientDelegate <NSObject>
- (void) print:(NSString*)s;
- (void) onError:(NSError*)e;
@end


@interface MiniPython : NSObject
- (void) setClient:(id <MiniPythonClientDelegate>)client;
- (void) clear;
// inputstream must already be opened
- (BOOL) setCode:(NSInputStream*)code error:(NSError**)error;
+ (NSString*) toPyString:(id<NSObject>) value;
+ (NSString*) toPyTypeString:(id<NSObject>)value;
+ (NSString*) toPyReprString:(id<NSObject>)value;
- (void) setError:(NSString*)description userInfo:(NSDictionary*)userinfo;
- (void) setNSError:(NSError*)error;
- (NSError*) getError;
@end

// Error handling
extern NSString * const MiniPythonErrorDomain;

enum MiniPythonErrorCode {
  MiniPythonEndOfStreamError=1,    // unexpected end of stream reading data
  MiniPythonStreamError=2,         // error reading from stream
  MiniPythonUnknownVersionError=3, // unknown jmp bytecode version
  MiniPythonInternalError=4,       // various out of bounds and similar errors which are only
                                   // possible from malformed bytecode
  MiniPythonRuntimeError=5,        // exceeding stack bounds etc
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
