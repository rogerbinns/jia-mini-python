#if !__has_feature(objc_arc)
#error "ARC: Automatic reference counting must be enabled for this file"
#endif

#pragma clang diagnostic ignored "-Wunknown-pragmas"
#pragma clang diagnostic ignored "-Wdirect-ivar-access"
#pragma clang diagnostic ignored "-Wreceiver-is-weak"
#pragma clang diagnostic ignored "-Warc-repeated-use-of-weak"

#import "MiniPython.h"

#include <stdio.h>

static void usage() {
  fprintf(stderr, "Usage: tester [--multi] [--clear] inputfile\n");
}

@interface Test1 : NSObject
@end

@interface ListBadEquals : NSMutableArray
@end

@interface MapBadEquals : NSMutableDictionary
@end

// it also records
@interface BlockingInputStream : NSInputStream
- (void) clear;
- (void) writeTo:(const char*)filename;
@end

@implementation Test1
{
  MiniPython* __weak mp;
}
- (id) init:(MiniPython*)mp_ {if((self=[super init])) { mp=mp_;} return self;}
- (void) retNone {}
- (NSObject*) returnNone { return nil; }
- (void) takesAll:(BOOL)b :(BOOL)b2 :(NSDictionary*)dict :(NSArray*)list :(NSNumber*)int1 :(int)int2 :(Test1*)t1 {
  (void)b; (void)b2; (void)int2;
  if(![dict isKindOfClass:[NSDictionary class]]) [mp setError:MiniPythonTypeError reason:@"Expected dict" userInfo:nil];
  else if(![list isKindOfClass:[NSArray class]]) [mp setError:MiniPythonTypeError reason:@"Expected list" userInfo:nil];
  else if(![int1 isKindOfClass:[NSNumber class]] || strcmp([(NSNumber*)int1 objCType], @encode(int)))
    [mp setError:MiniPythonTypeError reason:@"Expected int" userInfo:nil];
  else if(![t1 isKindOfClass:[Test1 class]]) [mp setError:MiniPythonTypeError reason:@"Expected Test1" userInfo:nil];
}
- (NSObject*) retSelf { return self; }
- (NSObject*) _call:(NSString*)name args:(NSArray*)args {
  NSError *error;
  NSObject *ret=[mp callMethod:name args:args error:&error];
  if(error) [mp setNSError:error];
  return ret;
}
- (NSObject*) call:(NSString*)name { return [self _call:name args:nil];}
- (NSObject*) call:(NSString*)name :(id)a0 { return [self _call:name args:@[a0]];}
- (NSObject*) call:(NSString*)name :(id)a0 :(id)a1 { return [self _call:name args:@[a0, a1]];}
- (NSObject*) call:(NSString*)name :(id)a0 :(id)a1 :(id)a2 { return [self _call:name args:@[a0, a1, a2]];}

- (void) vacall:(NSString*)a0 {
  [self vacall:a0 :@""];
}

- (void) vacall:(NSString*)a0 :(NSString*)a1 {
  if(![a0 isKindOfClass:[NSString class]] || ![a1 isKindOfClass:[NSString class]])
    [mp setError:MiniPythonTypeError reason:@"expected str" userInfo:nil];
}

- (int) add:(int)l :(int)r { (void)l;(void)r; return [(NSNumber*)[self _call:@"add" args:@[@3, @4]] intValue]; }
- (void) signalBatman { [mp setError:MiniPythonGeneralError reason:@"Batman" userInfo:nil]; }
- (id) badeqlist { return [[ListBadEquals alloc] init]; }
- (id) badeqDict { return [[MapBadEquals alloc] init]; }
- (void) foo {}
- (void) foo:(int)i {(void)i;}
- (void) foo:(int)i :(int)j {(void)i;(void)j;}
- (void) takesFloat:(float)v { (void)v; }
- (float) returnsFloat { return 3.14f; }
- (NSString*) toPyReprString:(id)o { return [MiniPython toPyReprString:o]; }
@end

@implementation ListBadEquals
// we only need append support
{
  id items[10];
  NSUInteger count;
}

- (BOOL) isEqual:(id)other { (void)other; return NO;}
- (NSUInteger) count { return count; }
- (id) objectAtIndex:(NSUInteger)c { return (c<count)?items[c]:nil;}
- (void) insertObject:(id)obj atIndex:(NSUInteger)c {
  items[c]=obj;
  count++;
}
@end

@implementation MapBadEquals
{
  NSMutableDictionary *underlying;
}
- (id) init { if((self=[super init])) {underlying=[[NSMutableDictionary alloc] init];} return self;}
- (BOOL) isEqual:(id)other { (void)other; return NO;}
- (void) setObject:(id)v forKey:(id<NSCopying>)k { [underlying setObject:v forKey:k];}
@end


@interface Client : NSObject <MiniPythonClientDelegate>
@end

@implementation Client {
  NSMutableString *out, *err;
}

- (id) init:(NSMutableString*)out_ :(NSMutableString*)err_ {
  if( (self=[super init]) ) {
    out=out_;
    err=err_;
  }
  return self;
}

- (void) print:(NSString*)s {
  if(out)
    [out appendString:s];
  else
    printf("%s", [s UTF8String]);
}
- (void) onError:(NSError*)error {
  if(err) {
    [err appendString:[error description]];
    [err appendString:@"\n"];
  } else
    fprintf(stderr, "%s\n", [[error description] UTF8String]);
}
@end

// This is so that the debugger can get access to it easily and we can
// dump out any crashing jmp
static BlockingInputStream *currentstream;

// This needs to have the same semantics as Tester.java and has been
// translated from the Java
static int main2(int argc, char *argv[]) {

  @autoreleasepool {

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

    NSString *fname=[[NSString alloc] initWithUTF8String:argv[0]];

    if (![[NSFileManager defaultManager] fileExistsAtPath:fname]) {
      fprintf(stderr, "No file at %s\n", argv[0]);
      return 1;
    }

    BlockingInputStream *is=[[BlockingInputStream alloc] initWithFileAtPath:[[NSString alloc] initWithUTF8String:argv[0]]];
    [is open];

    NSMutableString *out=nil, *err=nil;
    if(multimode) {
      out=[[NSMutableString alloc] init];
      err=[[NSMutableString alloc] init];
    }
    MiniPython *mp=[[MiniPython alloc] init];

    // sadly the weaks are not enough
#define EXIT(x) do { [mp clear]; return (x); } while(0)

    if(!clear) {
      [mp setClient:[[Client alloc] init:out :err]];
    }


    if(multimode)
      printf("[");

    BOOL first=true;
    for(;;)
      {
        [mp clear];
        if(!clear) {
          [mp addModule:[[Test1 alloc] init:mp] named:@"test1"];
          [mp addModule:[[Test1 alloc] init:mp] named:@"test2"];
        }

        NSError *error=nil;
        [is clear];
        currentstream=is;
        BOOL res=[mp setCode:is error:&error];
        currentstream=nil;
        NSCAssert( (res==NO && error) || res==YES, @"Failed return %d", res);
        if(error) {
          NSCAssert( [[error domain] isEqual:MiniPythonErrorDomain], @"Invalid error domain returned %@", [error domain]);
          switch([error code]) {
          case MiniPythonEndOfStreamError:
            if(multimode) {
              printf("]\n");
              EXIT(0);
            }
            fprintf(stderr, "Unexpected end of file\n");
            EXIT(1);
          default:
            if(clear)
              fprintf(stderr, "%s\n", [[error description] UTF8String]);
            if(!multimode)
              EXIT(7);
            break;
          }
        }

        if(!multimode)
          EXIT(0);

        if(first)
          first=NO;
        else
          printf(",\n");

        // stupid amounts of code to print json data to stdout
        NSOutputStream *thisisridiculous=[NSOutputStream outputStreamToMemory];
        [thisisridiculous open];
        [NSJSONSerialization writeJSONObject:@[out, err]
                                    toStream:thisisridiculous options:(NSJSONWritingOptions)0 error:nil];
        NSData *noreally=[thisisridiculous propertyForKey:NSStreamDataWrittenToMemoryStreamKey];
        fwrite([noreally bytes], [noreally length], 1, stdout);
        fflush(stdout);
        [out setString:@""];
        [err setString:@""];
      }
  }
}

int main(int argc, char *argv[]) {
  int res;
  @autoreleasepool {
    res=main2(argc, argv);
  }
  return res;
}

@implementation BlockingInputStream
{
  NSInputStream *in;
  uint8_t *savedbuf;
  NSUInteger bufused;
}

- (id) initWithFileAtPath:(NSString*) name {
  if( (self=[super init]) ) {
    in=[[NSInputStream alloc] initWithFileAtPath:name];
  }
  return self;
}

- (BOOL) getBuffer:(uint8_t **)buffer length:(NSUInteger *)len {
  (void)buffer;
  (void)len;
  return NO;
}

- (NSInteger)read:(uint8_t *)buffer maxLength:(NSUInteger)len {
  NSUInteger sofar=0;
  while(sofar<len) {
    NSInteger res=[in read:buffer maxLength:len-sofar];
    if(res==0) return (NSInteger)sofar;
    if(res<0) return res;
    // we let the OS figure growing this at a reasonable rate
    savedbuf=realloc(savedbuf, bufused+(NSUInteger)res);
    memcpy(savedbuf+bufused, buffer, (NSUInteger)res);
    bufused+=(NSUInteger)res;
    // advance
    buffer+=res;
    sofar+=(NSUInteger)res;
  }
  return (NSInteger)sofar;
}

- (void) writeTo:(const char*)filename {
  printf("Writing out saved data %d bytes to %s\n", (int)bufused, filename);
  FILE *f=fopen(filename, "wb");
  fwrite(savedbuf, bufused, 1, f);
  fclose(f);
  printf("Done\n");
}

- (void) open {
  [in open];
}

- (void) clear {
  free(savedbuf);
  savedbuf=NULL;
  bufused=0;
}

- (void) close {
  [in close];
}


@end
