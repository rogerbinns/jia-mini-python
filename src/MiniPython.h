#import "Foundation/Foundation.h"

@interface MiniPython : NSObject
- (void) setClient:(id)client;
- (void) clear;
- (BOOL) setCode:(NSInputStream*)code withError:(NSError**)error;
@end

// Error handling
extern NSString const *MiniPythonErrorDomain;

enum {
  MiniPythonEndOfStreamError=1, // unexpected end of stream reading data
  MiniPythonExecutionError=2    // issue encountered executing bytecode
};
