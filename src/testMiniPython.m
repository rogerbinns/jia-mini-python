#import "MiniPython.h"

#include <stdio.h>

static void usage() {
  fprintf(stderr, "Usage: tester [--multi] [--clear] inputfile\n");
}

// This needs to have the same semantics as Tester.java and has been
// translated from the Java
int main(int argc, char *argv[]) {

  BOOL multimode=NO;
  BOOL clear=NO;

  // skip app name
  argc--; argv++;

  while(argc && argv[0][0]=='-') {
    if(strcmp(argv[0], "--multi")==0) {
      multimode=YES;
    } else if (strcmp(argv[0], "--clear")==0) {
      clear=YES;
    } else {
      usage();
      return 1;
    }
    argc--;
    argv++;
  }
  if(argc!=1) {
    usage();
    return 1;
  }

  @autoreleasepool {

    NSString *fname=[[NSString alloc] initWithUTF8String:argv[0]];

    if (![[NSFileManager defaultManager] fileExistsAtPath:fname]) {
      fprintf(stderr, "No file at %s\n", argv[0]);
      return 1;
    }

    NSInputStream *is=[[NSInputStream alloc] initWithFileAtPath:[[NSString alloc] initWithUTF8String:argv[0]]];

    NSOutputStream *out=nil, *err=nil;
    MiniPython *mp=[[MiniPython alloc] init];

    if(!clear) {
      // needs print and onError
      [mp setClient:nil];
    }

    if(multimode)
      printf("[");

    BOOL first=true;
    do {
      out=[NSOutputStream outputStreamToMemory];
      err=[NSOutputStream outputStreamToMemory];
      if(clear) [mp clear];
      NSError *error=nil;
      BOOL res=[mp setCode:is withError:&error];
      NSCAssert( (res==NO && error) || res==YES, @"Failed return %d", res);
      if(error) {
        NSCAssert( [[error domain] isEqual:MiniPythonErrorDomain], @"Invalid error domain returned %@", [error domain]);
        switch([error code]) {
        case MiniPythonEndOfStreamError:
          if(multimode) {
            printf("]\n");
            return 0;
          }
          fprintf(stderr, "Unexpected end of file\n");
          return 1;
        case MiniPythonExecutionError:
          if(clear)
            fprintf(stderr, "%s\n", [[error description] UTF8String]);
          if(multimode)
            return 7;
          break;
        default:
          fprintf(stderr, "Failure: %s\n", [[error description] UTF8String]);
          return 1;
        }
      }

      if(!multimode)
        return 0;

      if(first)
        first=NO;
      else
        printf(",");

      //::TODO:: output contents of out and err as json
    } while(multimode);
  }

  return 0;
}
