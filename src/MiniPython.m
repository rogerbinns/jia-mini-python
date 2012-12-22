#import "MiniPython.h"

NSString * const MiniPythonErrorDomain=@"MiniPythonErrorDomain";

@interface MiniPythonError : NSError
@end



@interface MiniPythonContext : NSObject

@property (readonly, nonatomic) MiniPythonContext *parent;
@property (readonly, nonatomic) NSMutableDictionary *variables;
@property (readonly, nonatomic) NSMutableSet *globals;
@end

@implementation MiniPythonContext

@synthesize parent, variables, globals;

- (id)initWithParent:(MiniPythonContext*)p {
  if ( (self=[super init]) ) {
    parent=p;
  }
  return self;
}

@end

@interface MiniPython (Private)
- (NSObject*) mainLoop:(NSError**)error;
- (NSError*) internalError:(int)errcode reason:(NSString*)str;
- (NSError*) typeError:(NSObject*)val expected:(NSString*)type;
- (NSError*) binaryOpError:(NSString*)op left:(NSObject*)l right:(NSObject*)r;
- (NSError*) callClientError:(NSError*)error;
- (void) outOfMemory;
- (int) builtin_cmp:(NSObject*)left :(NSObject*)right;
@end

@implementation MiniPython
{
  int stacklimit;
  id <MiniPythonClientDelegate> client;
  __strong NSString **strings;
  __strong NSObject **stack;
  int nstrings;
  uint8_t *code;
  int codesize;
  int stacktop;
  MiniPythonContext *root;
  int pc;

}

- (id) init {
  if( (self = [super init]) ) {
    stacklimit=1024;
  }
  return self;
}

- (void) setClient:(id <MiniPythonClientDelegate>)delegate {
  client=delegate;
}

- (void) clear {
  // ::TODO:: write this
}


#define read16(v) { \
   uint8_t buf[2]; \
   res=[stream read:buf maxLength:2]; \
   if(res!=2) goto onerror; \
   v=(buf[0] | (buf[1]<<8)); }

- (BOOL) setCode:(NSInputStream*)stream error:(NSError**)error {
  NSInteger res=0, errorcode=0;
  int stringbuflen=256;
  void * stringbuf=malloc((size_t)stringbuflen);
  if(!stringbuf) stringbuflen=0;

  // reset internal state
  root=[[MiniPythonContext alloc] initWithParent:nil];
  stacktop=-1;
  pc=0;
  if(stack) {
    for(int i=0;i<stacklimit;i++)
      stack[i]=nil;
    free(stack);
    stack=NULL;
  }
  stack=(__strong NSString**)calloc((size_t)stacklimit, sizeof(NSObject*));
  if(!stack) [self outOfMemory];

  int version;
  read16(version);
  if(version!=0) {
    errorcode=MiniPythonUnknownVersionError;
    goto onerror;
  }

  // Strings
  read16(nstrings);
  strings=(__strong NSString**)calloc((size_t)nstrings, sizeof(NSString*));
  if(!strings) [self outOfMemory];

  for(int i=0; i<nstrings; i++) {
    int len;
    read16(len);
    if(len+1>stringbuflen) {
      stringbuflen=len+256;
      stringbuf=realloc(stringbuf, (size_t)stringbuflen);
      if(!stringbuf) [self outOfMemory];
    }
    res=[stream read:stringbuf maxLength:(NSUInteger)len];
    if(res!=(NSInteger)len) goto onerror;
    ((uint8_t*)stringbuf)[len]='\0';
    strings[i]=[NSString stringWithUTF8String:stringbuf];
  }

  // line number table
  int nlineno;
  read16(nlineno);
  stringbuf=realloc(stringbuf, (size_t)(nlineno*4));
  res=[stream read:stringbuf maxLength:(NSUInteger)(nlineno*4)];
  if(res!=(NSInteger)(nlineno*4))
    goto onerror;

  free(stringbuf);
  stringbuf=NULL;

  // code
  read16(codesize);
  code=malloc((size_t)codesize);
  if(!code) [self outOfMemory];
  res=[stream read:code maxLength:(NSUInteger)codesize];
  if(res!=(NSInteger)codesize)
    goto onerror;

  {
    NSError *errordash;
    [self mainLoop:&errordash];
    stacktop=-1;
    if(errordash) {
      if(error) *error=errordash;
      return NO;
    }
  }

  return YES;

 onerror:
  {
    NSError *tmperror=[NSError errorWithDomain:MiniPythonErrorDomain
                               code:(errorcode!=0)?errorcode:( (res<0)? MiniPythonStreamError:MiniPythonEndOfStreamError)
                           userInfo:(errorcode==0)?@{@"readresult": [NSNumber numberWithInteger:res]}
                                   :nil];
    [self callClientError:tmperror];
    if(error) *error=tmperror;
  }
  free(stringbuf);
  return NO;
}

- (void) dealloc {

  if(strings) {
    for(int i=0; i<nstrings; i++) {
      strings[i]=nil;
    }
    free(strings);
  }

  if(stack) {
    for(int i=0;i<stacklimit;i++)
      stack[i]=nil;
    free(stack);
  }

  free(code);
}

#define ERROR(c,s) do { *error=[self internalError:MiniPython##c reason:s]; return nil; } while(0)
#define STACKCHECK(n) do {if(stacktop+n<-1 || stacktop+n>=stacklimit) ERROR(RuntimeError, @"Exceeded stack bounds"); } while(0)
#define STRINGCHECK(v) do {if(v<0 || v>=nstrings) ERROR(InternalError, @"Invalid string index"); } while(0)
#define TYPEERROR(v,s) do { *error=[self typeError:v expected:s]; return nil; } while(0)
#define BINARYOPERROR(op,l,r) do { *error=[self binaryOpError:op left:l right:r]; return nil;} while(0)


#define ISINT(v) ([v isKindOfClass:[NSNumber class]] && 0==strcmp([N(v) objCType], @encode(int)))
#define ISBOOL(v) ([v isKindOfClass:[NSNumber class]] && 0==strcmp([N(v) objCType], @encode(BOOL)))
#define ISSTRING(v) ([v isKindOfClass:[NSString class]])
#define ISLIST(v) ([v isKindOfClass:[NSArray class]])

#define N(v) ((NSNumber*)(v))
#define S(v) ((NSString*)(v))
#define L(v) ((NSArray*)(v))

- (NSObject*) mainLoop:(NSError **)error {
  int op, val=-1;
  while(true) {
    if(pc>=codesize || pc<0) ERROR(InternalError,@"invalid pc");
    op=code[pc++];
    if(op>=128) {
      if(pc+2>=codesize) ERROR(InternalError, @"invalid pc val");
      val=code[pc] | (code[pc+1]<<8);
      pc+=2;
    }
    switch(op) {
    // -- check start : marker used by tool

    // binary operators
    case 1: // ADD
      {
        STACKCHECK(-2);
        NSObject *right=stack[stacktop--], *left=stack[stacktop--];

        if(ISINT(left) && ISINT(right)) {
          stack[++stacktop] = [NSNumber numberWithInt:[N(left) intValue] + [N(right) intValue]];
          continue;
        } else if (ISSTRING(left) && ISSTRING(right)) {
          stack[++stacktop]=[S(left) stringByAppendingString:S(right)];
          continue;
        } else if (ISLIST(left) && ISLIST(right)) {
          NSMutableArray *res=[NSMutableArray arrayWithCapacity:[L(left) count]+[L(right) count]];
          [res addObjectsFromArray:L(left)];
          [res addObjectsFromArray:L(right)];
          stack[++stacktop]=res;
          continue;
        }
        BINARYOPERROR(@"+", left, right);
      }

    case 2: // MULT
      {
        STACKCHECK(-2);
        NSObject *right=stack[stacktop--], *left=stack[stacktop--];
        if(ISINT(left) && ISINT(right)) {
          stack[++stacktop]=[NSNumber numberWithInt:[N(left) intValue]*[N(right) intValue]];
          continue;
        }
        if( (ISSTRING(left) && ISINT(right)) || (ISSTRING(right) && ISINT(left)) ) {
          // http://stackoverflow.com/a/4608137/463462
          int mult=[N(ISINT(right)?right:left) intValue];
          unsigned multdash=(mult<0)?0u:(unsigned)mult;
          NSString *base=(NSString*)(ISSTRING(left)?left:right);
          stack[++stacktop]=[@"" stringByPaddingToLength:[base length]*multdash withString:base startingAtIndex:0];
          continue;
        }
        if( (ISLIST(left) && ISINT(right)) || (ISLIST(right) && ISINT(left)) ) {
          int mult=[N(ISINT(right)?right:left) intValue];
          unsigned multdash=(mult<0)?0u:(unsigned)mult;
          NSArray *base=(NSArray*)(ISLIST(left)?left:right);
          NSMutableArray *res=[NSMutableArray arrayWithCapacity:multdash*[base count]];
          for(unsigned i=0; i<multdash; i++) {
            [res addObjectsFromArray:base];
          }
          stack[++stacktop]=res;
          continue;
        }
        BINARYOPERROR(@"*", left,right);
      }

    case 3: // DIV
      {
        STACKCHECK(-2);
        NSObject *right=stack[stacktop--], *left=stack[stacktop--];
        if(ISINT(left) && ISINT(right)) {
          int l=[N(left) intValue], r=[N(right) intValue];
          if(!r) ERROR(ArithmeticError, @"Division by zero");
          // http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
          if ((l >= 0 && r >= 0) || (l < 0 && r < 0)) {
            stack[++stacktop] = [NSNumber numberWithInt:l / r];
          } else {
            int res = l / r;
            if (l % r != 0) {
              res--;
            }
            stack[++stacktop] = [NSNumber numberWithInt:res];
          }
          continue;
        }
        BINARYOPERROR(@"/", left, right);
      }

    // comparisons
    case 4: // GT
    case 5: // LT
    case 6: // EQ
    case 26: // NOT_EQ
    case 31: // GTE
    case 32: // LTE
      {
        STACKCHECK(-2);
        NSObject *right=stack[stacktop--], *left=stack[stacktop--];

        int cmp=[self builtin_cmp:left :right];
        BOOL res=NO;
        switch (op) {
        case 5: // < LT
          res = cmp < 0;
          break;
        case 32: // <= LTE
          res = cmp <= 0;
          break;
        case 4: // > GT
          res = cmp > 0;
          break;
        case 31: // >= GTE
          res = cmp >= 0;
          break;
        case 6: // = EQ
          res = cmp == 0;
          break;
        case 26: // != NOT_EQ
          res = cmp != 0;
          break;
        }
        stack[++stacktop] = [NSNumber numberWithBool:res];
        continue;
      }

    case 11: // POP_TOP
      {
        STACKCHECK(-1);
        stacktop--;
        continue;
      }

    case 18: // PUSH_NONE
    case 21: // PUSH_TRUE
    case 22: // PUSH_FALSE
      {
        STACKCHECK(+1);
        stack[++stacktop] = (op == 18) ? [NSNull null] : [NSNumber numberWithBool:(op == 21)];
        continue;
      }

      // Codes that make the stack bigger
    case 200: // PUSH_INT
      {
        STACKCHECK(+1);
        stack[++stacktop] = [NSNumber numberWithInt:val];
        continue;
      }
    case 201: // PUSH_INT_HI
      {
        STACKCHECK(0);
        if(!ISINT(stack[stacktop])) ERROR(InternalError, @"PUSH_INT_HI expected int");
        stack[stacktop] = [NSNumber numberWithInt:[N(stack[stacktop]) intValue] | (val << 16)];
        continue;
      }


    case 162: // PUSH_STR
      {
        STACKCHECK(+1);
        STRINGCHECK(val);
        stack[++stacktop] = strings[val];
        continue;
      }


    case 23: // PRINT
      {
        STACKCHECK(-1);
        if(!ISINT(stack[stacktop])) TYPEERROR(stack[stacktop], @"int");
        if(!ISBOOL(stack[stacktop-1])) TYPEERROR(stack[stacktop-1], @"bool");

        int nargs = [N(stack[stacktop--]) intValue];
        BOOL nl = [N(stack[stacktop--]) boolValue];

        STACKCHECK(-nargs);
        stacktop -= nargs;
        NSMutableString *output=[[NSMutableString alloc] init];
        for (int i = 0; i < nargs; i++) {
          if (i != 0) {
            [output appendString:@" "];
          }
          [output appendString:[self toPyString:stack[stacktop + i + 1]]];
        }

        [output appendString:nl ? @"\n" : @" "];
        [client print:output];
        continue;
      }

    case 19: // EXIT_LOOP
      {
        return nil;
      }


    case 0: // FUNCTION_PROLOG
    case 7: // IN
    case 8: // UNARY_ADD
    case 9: // RETURN
    case 10: // CALL
    case 12: // ATTR
    case 13: // UNARY_NEG
    case 14: // SUBSCRIPT
    case 15: // SUBSCRIPT_SLICE
    case 16: // DICT
    case 17: // LIST
    case 24: // NOT
    case 25: // ITER
    case 27: // SUB
    case 28: // DEL_INDEX
    case 29: // DEL_SLICE
    case 30: // MOD
    case 33: // ASSIGN_INDEX
    case 34: // ASSERT_FAILED
    case 35: // IS
    case 128: // MAKE_METHOD
    case 129: // GOTO
    case 130: // IF_FALSE
    case 131: // NEXT
    case 132: // AND
    case 133: // OR
    case 160: // LOAD_NAME
    case 161: // STORE_NAME
    case 163: // GLOBAL
    case 164: // DEL_NAME
    case 165: // STORE_ATTR_NAME
    case 202: // POP_N
    // -- check end : marker used by tool
    default:
      ERROR(InternalError, ([NSString stringWithFormat:@"Unknown/unimplemented opcode: %d", op]));
    }


  }


}

- (NSString*) toPyString:(NSObject*)value {
  if(!value || value==[NSNull null])
    return @"None";
  if(ISSTRING(value))
    return (NSString*)value;
  if(ISINT(value))
    return [N(value) description];
  if(ISBOOL(value))
    return [N(value) boolValue]?@"True":@"False";

  return [NSString stringWithFormat:@"Need toPyString of %@: %@", [value class], value];
}

- (NSString*) toPyTypeString:(NSObject*)value {
  if(!value || value==[NSNull null])
    return @"NoneType";
  if(ISBOOL(value))
    return @"bool";
  if(ISINT(value))
    return @"int";

  return [NSString stringWithFormat:@"Need toPyTypeString of %@: %@", [value class], value];
}

- (int) builtin_cmp:(NSObject*)left :(NSObject*)right {
  if(left==right)
    return 0;
  if(ISINT(left) && ISINT(right)) {
    int l=[N(left) intValue], r=[N(right) intValue];
    if(l==r) return 0;
    return (l<r)?-1:1;
  }
  if(ISSTRING(left) && ISSTRING(right)) {
    NSString *l=(NSString*)left, *r=(NSString*)right;
    return (int)[l compare:r];
  }
  // ::TODO:: rest of comparisons
  return 0;
}

- (NSError*) internalError:(int)errcode reason:(NSString*)str {
  return [self callClientError:[NSError errorWithDomain:MiniPythonErrorDomain
                                             code:errcode
                                         userInfo:@{@"reason": str}]];

}

- (NSError*) typeError:(NSObject*)value expected:(NSString*)type {
  return [self callClientError:[NSError errorWithDomain:MiniPythonErrorDomain
                                                   code:MiniPythonTypeError
                                               userInfo:@{@"expected": type, @"got":[self toPyTypeString:value]}]];
}

- (NSError*) binaryOpError:(NSString*)op left:(NSObject*)l right:(NSObject*)r {
  return [self callClientError:[NSError errorWithDomain:MiniPythonErrorDomain
                                                   code:MiniPythonTypeError
                                               userInfo:@{@"op": op,  @"left": l, @"right": r}]];
}

- (NSError*) callClientError:(NSError*)err {
  [client onError:err];
  return err;
}

@end
