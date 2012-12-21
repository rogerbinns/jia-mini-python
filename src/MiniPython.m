#import "MiniPython.h"

NSString const *MiniPythonErrorDomain=@"MiniPythonErrorDomain";

@interface MiniPython (Private)

@end

@implementation MiniPython
{
  size_t stacklimit;
}

- (id) init {
  if( (self = [super init]) ) {
    stacklimit=1024;
  }
  return self;
}

@end
