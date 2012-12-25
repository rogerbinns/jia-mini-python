#import "MiniPython.h"
// #import <Foundation/NSObjCRuntime.h>
#import <objc/runtime.h>

NSString * const MiniPythonErrorDomain=@"MiniPythonErrorDomain";

@interface MiniPythonError : NSError
+ (NSError*) withMiniPython:(MiniPython*)mp code:(NSInteger)code userInfo:(NSDictionary*)userinfo;
@end

@interface MiniPythonContext : NSObject
- (void) setValue:(id<NSObject>)v forName:(NSString*)n;
- (id<NSObject>) getName:(NSString*)n;
@end

@implementation MiniPythonContext
{
  MiniPythonContext *parent;
  NSMutableDictionary *variables;
  NSMutableSet *globals;
}


- (id)initWithParent:(MiniPythonContext*)p {
  if ( (self=[super init]) ) {
    parent=p;
  }
  return self;
}

- (void) setValue:(id<NSObject>)v forName:(NSString*)n {
  MiniPythonContext *use=self;

  if(use->parent && globals && [globals containsObject:n]) {
    while(use->parent)
      use=use->parent;
  }
  if(!use->variables)
    use->variables=[[NSMutableDictionary alloc] init];
  [use->variables setObject:v forKey:n];
}

- (id<NSObject>) getName:(NSString*)n {
  MiniPythonContext *use=self;

  if(use->parent && globals && [globals containsObject:n]) {
    while(use->parent)
      use=use->parent;
  }

  return (use->variables)?[use->variables objectForKey:n]:nil;
}

@end

@interface MiniPythonNativeMethod : NSObject
- (id) init:(MiniPython*)mp name:(NSString*)name target:(id)object;
- (id<NSObject>) call:(NSArray*)args;
@end

@interface MiniPython (Private)
- (id<NSObject>) mainLoop;
- (void) internalError:(int)errcode reason:(NSString*)str;
- (void) typeError:(id<NSObject>)val expected:(NSString*)type;
- (void) binaryOpError:(NSString*)op left:(id<NSObject>)l right:(id<NSObject>)r;
- (void) outOfMemory;
- (NSDictionary*) stateForError;
- (void) addBuiltins;
- (NSString*) format:(NSString*)format with:(NSArray*)args;
- (int) builtin_cmp:(id<NSObject>)left :(id<NSObject>)right;
- (BOOL) builtin_bool:(id<NSObject>)value;
@end

@implementation MiniPython
{
  int stacklimit;
  id <MiniPythonClientDelegate> client;
  __strong NSString **strings;
  __strong id<NSObject> *stack;
  uint16_t *linenotab;
  int nlineno;
  int nstrings;
  uint8_t *code;
  int codesize;
  int stacktop;
  MiniPythonContext *context;
  int pc;
  NSError *errorindicator;
}

- (id) init {
  if( (self = [super init]) ) {
    stacklimit=1024;
  }
  context=[[MiniPythonContext alloc] initWithParent:nil];
  return self;
}

- (void) setClient:(id <MiniPythonClientDelegate>)delegate {
  client=delegate;
}

- (void) clear {
  // ::TODO:: write this
  context=[[MiniPythonContext alloc] initWithParent:nil];
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
  [self addBuiltins];
  stacktop=-1;
  pc=-1;
  free(linenotab);
  linenotab=NULL;
  free(code);
  code=NULL;
  errorindicator=nil;
  if(stack) {
    for(int i=0;i<stacklimit;i++)
      stack[i]=nil;
    free(stack);
    stack=NULL;
  }
  stack=(__strong id<NSObject>*) calloc((size_t)stacklimit, sizeof(id<NSObject>));
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
    if(len>stringbuflen) {
      stringbuflen=len+256;
      stringbuf=realloc(stringbuf, (size_t)stringbuflen);
      if(!stringbuf) [self outOfMemory];
    }
    if(len) {
      res=[stream read:stringbuf maxLength:(NSUInteger)len];
      if(res!=(NSInteger)len) goto onerror;
    }
    strings[i]=[[NSString alloc] initWithBytes:stringbuf length:(NSUInteger)len encoding:NSUTF8StringEncoding];
  }

  // line number table
  read16(nlineno);
  if(nlineno) {
    linenotab=malloc((size_t)(nlineno*4));
    if(linenotab)
      res=[stream read:(uint8_t*)linenotab maxLength:(NSUInteger)(nlineno*4)];
    if(res!=(NSInteger)(nlineno*4))
      goto onerror;
  }

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
    pc=0;
    [self mainLoop];
    stacktop=-1;
    if(errorindicator) {
      if(error) *error=errorindicator;
      return NO;
    }
  }

  return YES;

 onerror:
  [self setNSError:[NSError errorWithDomain:MiniPythonErrorDomain
                                       code:(errorcode!=0)?errorcode:( (res<0)? MiniPythonStreamError:MiniPythonEndOfStreamError)
                                   userInfo:(errorcode==0)?@{@"readresult": [NSNumber numberWithInteger:res]}
                                           :nil]];
  if(error) *error=errorindicator;
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

#define ERROR(c,s) do { [self internalError:MiniPython##c reason:(s)]; return nil; } while(0)
#define STRINGCHECK(v) do {if((v)<0 || (v)>=nstrings) ERROR(InternalError, @"Invalid string index"); } while(0)
#define TYPEERROR(v,s) do { [self typeError:(v) expected:(s)]; return nil; } while(0)
#define BINARYOPERROR(op,l,r) do { [self binaryOpError:(op) left:(l) right:(r)]; return nil;} while(0)

#define ISNONE(v) (!(v) || (v)==[NSNull null])
#define ISINT(v) ([(v) isKindOfClass:[NSNumber class]] && 0==strcmp([N(v) objCType], @encode(int)))
#define ISBOOL(v) ([(v) isKindOfClass:[NSNumber class]] && 0==strcmp([N(v) objCType], @encode(BOOL)))
#define ISSTRING(v) ([(v) isKindOfClass:[NSString class]])
#define ISLIST(v) ([(v) isKindOfClass:[NSArray class]])
#define ISDICT(v) ([(v) isKindOfClass:[NSDictionary class]])

#define N(v) ((NSNumber*)(v))
#define S(v) ((NSString*)(v))
#define L(v) ((NSArray*)(v))
#define D(v) ((NSDictionary*)(v))

- (id<NSObject>) mainLoop {
  int op, val=-1;
  BOOL stackerror=NO;
  while(true) {
    if(pc>=codesize || pc<0) ERROR(InternalError,@"invalid pc");
    op=code[pc++];
    if(op>=128) {
      if(pc+2>=codesize) ERROR(InternalError, @"invalid pc val");
      val=code[pc] | (code[pc+1]<<8);
      pc+=2;
    }

    // this does stack bounds checking
    switch(op) {
    // -- check start : marker used by tool

    // does not use stack
    case 19: // EXIT_LOOP
      break;

    // Use top item
    case 8: // UNARY_ADD
    case 24: // NOT
    case 13: // UNARY_NEG
    case 201: // PUSH_INT_HI  (alters top item - bad opcode name)
    case 130: // IF_FALSE
    case 34: // ASSERT_FAILED
    case 132: // AND
    case 133: // OR
    case 17: // LIST
    case 16: // DICT
    case 161: // STORE_NAME
      if(stacktop<0 || stacktop>=stacklimit) stackerror=YES;
      break;

    // Use top two items
    case 1: // ADD
    case 2: // MULT
    case 3: // DIV
    case 30: // MOD
    case 4: // GT
    case 5: // LT
    case 6: // EQ
    case 7: // IN
    case 31: // GTE
    case 32: // LTE
    case 26: // NOT_EQ
    case 27: // SUB
    case 23: // PRINT  (further checking in implementation)
    case 10: // CALL (further checking in implementation)
      if(stacktop-1<0 || stacktop>=stacklimit) stackerror=YES;
      break;

    // no use - adds item
    case 162: // PUSH_STR
    case 18: // PUSH_NONE
    case 21: // PUSH_TRUE
    case 22: // PUSH_FALSE
    case 200: // PUSH_INT
    case 160: // LOAD_NAME
      if(stacktop+1>=stacklimit) stackerror=YES;
      break;


    case 0: // FUNCTION_PROLOG
    case 9: // RETURN
    case 11: // POP_TOP
    case 12: // ATTR
    case 14: // SUBSCRIPT
    case 15: // SUBSCRIPT_SLICE
    case 25: // ITER
    case 28: // DEL_INDEX
    case 29: // DEL_SLICE
    case 33: // ASSIGN_INDEX
    case 35: // IS
    case 128: // MAKE_METHOD
    case 129: // GOTO
    case 131: // NEXT
    case 163: // GLOBAL
    case 164: // DEL_NAME
    case 165: // STORE_ATTR_NAME
    case 202: // POP_N
    // -- check end : marker used by tool
    default:
      ERROR(InternalError, ([NSString stringWithFormat:@"Unknown/unimplemented opcode check: %d", op]));
    }

    if(stackerror)
      ERROR(RuntimeError, @"Exceeded stack bounds");

    // this does the bytecode instruction
    switch(op) {
    // -- check start : marker used by tool

    // unary operators
    case 24: // NOT
      {
        stack[stacktop]=[NSNumber numberWithBool:![self builtin_bool:stack[stacktop]]];
        continue;
      }

    case 13: // UNARY_NEG
      {
        if(ISINT(stack[stacktop])) {
          stack[stacktop]=[NSNumber numberWithInt:-[N(stack[stacktop]) intValue]];
        } else TYPEERROR(stack[stacktop], @"int");
        continue;
      }

    // binary operators
    case 1: // ADD
      {
        id<NSObject> right=stack[stacktop--], left=stack[stacktop--];

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

    case 27: // SUB
      {
        id<NSObject> right=stack[stacktop--], left=stack[stacktop--];
        if(ISINT(left) && ISINT(right)) {
          stack[++stacktop]=[NSNumber numberWithInt:[N(left) intValue]-[N(right) intValue]];
          continue;
        }
        BINARYOPERROR(@"-", left, right);
      }

    case 2: // MULT
      {
        id<NSObject> right=stack[stacktop--], left=stack[stacktop--];
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
        id<NSObject> right=stack[stacktop--], left=stack[stacktop--];
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

    case 30: // MOD
      {
        id<NSObject> right=stack[stacktop--], left=stack[stacktop--];
        if(ISINT(left) && ISINT(right)) {
          int l=[N(left) intValue], r=[N(right) intValue];
          if(!r) ERROR(ArithmeticError, @"Modulo by zero");
          int res= l % r;
          // in Python the result sign is same as sign of right
          if ((res < 0 && r >= 0) || (res >= 0 && r < 0)) {
            res = -res;
          }
          stack[++stacktop] = [NSNumber numberWithInt:res];
          continue;
        } else if(ISSTRING(left) && ISLIST(right)) {
          stack[++stacktop] = [self format:S(left) with:L(right)];
          continue;
        }
        BINARYOPERROR(@"%", left, right);
      }

    // comparisons
    case 4: // GT
    case 5: // LT
    case 6: // EQ
    case 26: // NOT_EQ
    case 31: // GTE
    case 32: // LTE
      {
        id<NSObject> right=stack[stacktop--], left=stack[stacktop--];

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


    // constructors
    case 16: // DICT
      {
        if(!ISINT(stack[stacktop])) ERROR(InternalError, @"DICT expected int");
        int nitems=[N(stack[stacktop--]) intValue];
        stacktop-=nitems*2;
        if(nitems && (stacktop+1<0 || stacktop+nitems*2>=stacklimit))
          ERROR(RuntimeError, @"Exceeded stack bounds in dict");
        NSMutableDictionary *res=[NSMutableDictionary dictionaryWithCapacity:(NSUInteger)nitems];
        for(int i=0; i<nitems; i++) {
          [res setObject:stack[stacktop+1+i*2] forKey:stack[stacktop+1+i*2+1]];
        }
        stack[++stacktop]=res;
        continue;
      }

    case 17: // LIST
      {
        if(!ISINT(stack[stacktop])) ERROR(InternalError, @"LIST expected int");
        int nitems=[N(stack[stacktop--]) intValue];
        stacktop-=nitems;
        if(nitems && (stacktop+1<0 || stacktop+nitems>=stacklimit))
          ERROR(RuntimeError, @"Exceeded stack bounds in list");
        NSMutableArray *res=[NSMutableArray arrayWithCapacity:(NSUInteger)nitems];
        for(int i=0; i<nitems; i++)
          [res addObject:stack[stacktop+1+i]];
        stack[++stacktop]=res;
        continue;
      }

    // stack things
    case 11: // POP_TOP
      {
        stacktop--;
        continue;
      }

    case 18: // PUSH_NONE
    case 21: // PUSH_TRUE
    case 22: // PUSH_FALSE
      {
        stack[++stacktop] = (op == 18) ? [NSNull null] : [NSNumber numberWithBool:(op == 21)];
        continue;
      }

      // Codes that make the stack bigger
    case 200: // PUSH_INT
      {
        stack[++stacktop] = [NSNumber numberWithInt:val];
        continue;
      }
    case 201: // PUSH_INT_HI
      {
        if(!ISINT(stack[stacktop])) ERROR(InternalError, @"PUSH_INT_HI expected int");
        stack[stacktop] = [NSNumber numberWithInt:[N(stack[stacktop]) intValue] | (val << 16)];
        continue;
      }


    case 162: // PUSH_STR
      {
        STRINGCHECK(val);
        stack[++stacktop] = strings[val];
        continue;
      }


    case 23: // PRINT
      {
        if(!ISINT(stack[stacktop])) TYPEERROR(stack[stacktop], @"int");
        if(!ISBOOL(stack[stacktop-1])) TYPEERROR(stack[stacktop-1], @"bool");

        int nargs = [N(stack[stacktop--]) intValue];
        BOOL nl = [N(stack[stacktop--]) boolValue];

        stacktop -= nargs;
        if(nargs && (stacktop+1<0 || stacktop+nargs>=stacklimit))
          ERROR(RuntimeError, @"Exceeded stack bounds in print");
        NSMutableString *output=[[NSMutableString alloc] init];
        for (int i = 0; i < nargs; i++) {
          if (i != 0) {
            [output appendString:@" "];
          }
          [output appendString:[MiniPython toPyString:stack[stacktop + i + 1]]];
        }

        [output appendString:nl ? @"\n" : @" "];
        [client print:output];
        continue;
      }

    case 34: // ASSERT_FAILED
      {
        id<NSObject> o = stack[stacktop--];
        ERROR(AssertionError, ISNONE(o)?@"assertion failed":[MiniPython toPyString:o]);
      }

    // control flow

    case 19: // EXIT_LOOP
      {
        return nil;
      }

    case 130: // IF_FALSE
      {
        if(![self builtin_bool:stack[stacktop--]]) {
          pc=val; // checked at top of switch
        }
        continue;
      }

    case 132: // AND
    case 133: // OR
      {
        if([self builtin_bool:stack[stacktop]] == (op==133)) {
          // on true (OR) or false (AND), goto end
          pc = val;
        } else {
          // clear top value so next one can be tested
          stacktop--;
        }
        continue;
      }

    // names
    case 161: // STORE_NAME
      {
        STRINGCHECK(val);
        [context setValue:stack[stacktop--] forName:strings[val]];
        continue;
      }
    case 160: // LOAD_NAME
      {
        STRINGCHECK(val);
        id<NSObject> v=[context getName:strings[val]];
        if(v) {
          stack[++stacktop]=v;
          continue;
        }
        ERROR(NameError, ([NSString stringWithFormat:@"name '%@' is not defined", strings[val]]));
      }

    case 10: // CALL
      {
        id<NSObject> func=stack[stacktop--];
        if(![func isKindOfClass:[MiniPythonNativeMethod class]]) TYPEERROR(func, @"function");
        if(!ISINT(stack[stacktop])) ERROR(InternalError, @"bad function call sequence");
        int nargs = [N(stack[stacktop--]) intValue];

        stacktop -= nargs;
        if(nargs && (stacktop+1<0 || stacktop+nargs>=stacklimit))
          ERROR(RuntimeError, @"Exceeded stack bounds in call");

        NSMutableArray *args=[NSMutableArray arrayWithCapacity:(NSUInteger)nargs];
        for (int i = 0; i < nargs; i++) {
          [args addObject:stack[stacktop+i+1]];
        }

        id<NSObject> res=[(MiniPythonNativeMethod*)func call:args];
        if(errorindicator) return nil;
        stack[++stacktop]=res;
        continue;
      }

    case 0: // FUNCTION_PROLOG
    case 7: // IN
    case 8: // UNARY_ADD
    case 9: // RETURN
    case 12: // ATTR
    case 14: // SUBSCRIPT
    case 15: // SUBSCRIPT_SLICE
    case 25: // ITER
    case 28: // DEL_INDEX
    case 29: // DEL_SLICE
    case 33: // ASSIGN_INDEX
    case 35: // IS
    case 128: // MAKE_METHOD
    case 129: // GOTO
    case 131: // NEXT
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

+ (NSString*) toPyString:(id<NSObject>)value {
  if(ISNONE(value))
    return @"None";
  if(ISSTRING(value))
    return (NSString*)value;
  if(ISINT(value))
    return [N(value) description];
  if(ISBOOL(value))
    return [N(value) boolValue]?@"True":@"False";

  return [NSString stringWithFormat:@"Need toPyString of %@: %@", [value class], value];
}

+ (NSString*) toPyTypeString:(id<NSObject>)value {
  if(ISNONE(value)) return @"NoneType";
  if(ISSTRING(value)) return @"str";
  if(ISBOOL(value)) return @"bool";
  if(ISINT(value))  return @"int";
  if(ISLIST(value)) return @"list";
  if(ISDICT(value)) return @"dict";

  if([value isKindOfClass:[MiniPythonNativeMethod class]]) return @"modulemethod";

  // ::TODO:: more type strings
  return [NSString stringWithFormat:@"Need toPyTypeString of %@: %@", [value class], value];
}

- (NSString*) format:(NSString*)format with:(NSArray*)args {
  // ::TODO:: write a printf equivalent
  return [NSString stringWithFormat:@"fmt \"%@\" with %@", format, [MiniPython toPyString:args]];
}

- (int) builtin_cmp:(id<NSObject>)left :(id<NSObject>)right {
  if(left==right)
    return 0;
  if( (ISINT(left) && ISINT(right)) || (ISBOOL(left) && ISBOOL(right))) {
    int l=[N(left) intValue], r=[N(right) intValue];
    if(l==r) return 0;
    return (l<r)?-1:1;
  }
  if([left isEqual:right]) return 0;
  if(ISSTRING(left) && ISSTRING(right)) {
    NSString *l=(NSString*)left, *r=(NSString*)right;
    return (int)[l compare:r];
  }
  if(ISLIST(left) && ISLIST(right)) {
    // compare item by item with python semantics
    NSEnumerator *li=[L(left) objectEnumerator],
      *ri=[L(right) objectEnumerator];
    for(;;) {
      id<NSObject> l=[li nextObject],
        r=[ri nextObject];
      // both ended at same place?
      if(!l && !r) return 0;
      if(!l) return -1;
      if(!r) return 1;
      int cmp=[self builtin_cmp:l :r];
      if(cmp!=0) return cmp;
    }
  }
  if(ISDICT(left) && ISDICT(right)) {
    uintptr_t l=(uintptr_t)left, r=(uintptr_t)right;
    return (l<r)?-1:1;
  }
  // different types compare as their type strings
  if([left class] != [right class]) {
    return [self builtin_cmp:[MiniPython toPyTypeString:left] :[MiniPython toPyTypeString:right]];
  }
  // just compare as strings then
  return [self builtin_cmp:[MiniPython toPyString:left] :[MiniPython toPyString:right]];
}

- (BOOL) builtin_bool:(id<NSObject>)value {
  if(ISBOOL(value)) {
    return [N(value) boolValue];
  } else if(ISNONE(value)) {
    return NO;
  } else if(ISINT(value)) {
    return 0!=[N(value) intValue];
  } else if(ISSTRING(value)) {
    return 0!=[S(value) length];
  } else if(ISLIST(value)) {
    return 0!=[L(value) count];
  } else if(ISDICT(value)) {
    return 0!=[D(value) count];
  }

  // treat unknown objects as true
  return YES;
}

- (NSString*)builtin_type:(NSObject*)value {
  return [MiniPython toPyTypeString:value];
}

- (NSString*)builtin_str:(NSObject*)value {
  return [MiniPython toPyString:value];
}

- (void) internalError:(int)errcode reason:(NSString*)str {
  [self setNSError:[MiniPythonError withMiniPython:self
                                              code:errcode
                                          userInfo:@{@"reason": str}]];
}

- (void) typeError:(id<NSObject>)value expected:(NSString*)type {
  [self setNSError:[MiniPythonError withMiniPython:self
                                              code:MiniPythonTypeError
                                          userInfo:@{@"expected": type, @"got":[MiniPython toPyTypeString:value]}]];
}

- (void) typeError:(id<NSObject>)value expected:(NSString*)type details:(NSDictionary*)more {
  NSMutableDictionary *d=[[NSMutableDictionary alloc] init];
  [d addEntriesFromDictionary:more];
  [d setObject:type forKey:@"expected"];
  [d setObject:[MiniPython toPyTypeString:value] forKey:@"got"];
  [self setNSError:[MiniPythonError withMiniPython:self
                                              code:MiniPythonTypeError
                                          userInfo:d]];
}

- (void) binaryOpError:(NSString*)op left:(id<NSObject>)l right:(id<NSObject>)r {
  [self setNSError:[MiniPythonError withMiniPython:self
                                              code:MiniPythonTypeError
                                          userInfo:@{@"op": op,  @"left": l, @"right": r}]];
}

- (void) setNSError:(NSError*)error {
  errorindicator=error;
  [client onError:errorindicator];
}

- (void) setError:(NSString*)description userInfo:(NSDictionary*)userinfo {
  NSMutableDictionary *d=[[NSMutableDictionary alloc] init];
  [d setObject:description forKey:@"description"];
  [d addEntriesFromDictionary:userinfo];
  [self setNSError:[MiniPythonError withMiniPython:self
                                              code:MiniPythonGeneralError
                                          userInfo:d]];
}

- (NSError*) getError {
  return errorindicator;
}

- (NSDictionary*) stateForError {
  NSMutableDictionary *d=[[NSMutableDictionary alloc] init];
  [d setObject:[NSNumber numberWithInt:pc] forKey:@"pc"];
  [d setObject:[NSNumber numberWithInt:stacktop] forKey:@"stacktop"];
  if(nlineno && linenotab) {
    int line=0;
    // linear search for first pc gte our pc (remember pc points to
    // next instruction to be executed)
    for(int i=0; i<nlineno; i++) {
      if(linenotab[i*2]>=pc)
        break;
      line=linenotab[i*2+1];
    }
    [d setObject:[NSNumber numberWithInt:line] forKey:@"lineno"];
  }
  return d;
}

- (void) addBuiltins {
  Method *methods=class_copyMethodList([self class], NULL);
  Method *m=methods;
  while(*m) {
    SEL sel=method_getName(*m);
    if(strncmp(sel_getName(sel), "builtin_", 8)==0) {
      const char*name=sel_getName(sel)+8;
      unsigned i;
      for(i=0; name[i] && name[i]!=':' ; i++);
      NSString *funcname=[[NSString alloc] initWithBytes:name length:i encoding:NSASCIIStringEncoding];
      [context setValue:[[MiniPythonNativeMethod alloc] init:self name:funcname target:self] forName:funcname];
    }
    m++;
  }

  free(methods);
}


- (int) builtin_banana:(id) left :(id)right {
  return [self builtin_cmp:left :right];
}

@end

@implementation MiniPythonError

+ (NSError*) withMiniPython:(MiniPython*)mp code:(NSInteger)code userInfo:(NSDictionary*)userinfo {
  NSMutableDictionary *d=[[NSMutableDictionary alloc] init];
  [d addEntriesFromDictionary:[mp stateForError]];
  [d addEntriesFromDictionary:userinfo];
  return [super errorWithDomain:MiniPythonErrorDomain
                           code:code
                       userInfo:d];
}

- (NSString*) description {
  NSMutableString *res=[[NSMutableString alloc] init];
  NSMutableSet *set=[[NSMutableSet alloc] init];
  NSDictionary *ue=[self userInfo];

  switch((enum MiniPythonErrorCode)[self code]) {
  case MiniPythonEndOfStreamError:
    [res appendString:@"EndOfStreamError: Unexpected end of stream reading code"];
    break;
  case MiniPythonAssertionError:
    [res appendFormat:@"AssertionError: %@", [ue objectForKey:@"reason"]];
    [set addObject:@"reason"];
    break;
  }

  if(![res length]) {
    return [@"Unhandled stringification of " stringByAppendingString:[super description]];
  }

  // line number and pc
  if([ue objectForKey:@"pc"]) {
    [res appendFormat:@"\npc = %d", [[ue objectForKey:@"pc"] intValue]];
    [set addObject:@"pc"];
    if([ue objectForKey:@"lineno"]) {
      [res appendFormat:@" line = %d", [[ue objectForKey:@"lineno"] intValue]];
      [set addObject:@"lineno"];
    }
  }

  // stacktop will go away
  if([ue objectForKey:@"stacktop"]) {
      [res appendFormat:@" stacktop = %d", [[ue objectForKey:@"stacktop"] intValue]];
      [set addObject:@"stacktop"];
  }

  if([set count]!=[ue count]) {
    NSLog(@"Did not use all keys of %@\nUsed %@", ue, set);
  }
  return res;
}
@end

@implementation MiniPythonNativeMethod
{
  MiniPython *mp;
  NSString *name;
  id object;
  // We cache the most recently used invocation.  There are multiple
  // methods of the same name but taking different numbers of args
  NSInvocation *invocation;
  NSUInteger nargsininvocation;
}

- (id) init:(MiniPython*)mp_ name:(NSString*)name_ target:(id)object_ {
  if ( (self=[super init]) ) {
    mp=mp_;
    name=name_;
    object=object_;
  }
  return self;
}

- (id<NSObject>) call:(NSArray*)args {
  if(!invocation || [args count]!=nargsininvocation) {
    NSMutableString *selname;
    if (object==mp) {
      selname=[NSMutableString stringWithString:@"builtin_"];
      [selname appendString:name];
    }
    else
      selname=[NSMutableString stringWithString:name];
    for(unsigned i=0;i<[args count];i++)
      [selname appendString:@":"];
    SEL sel=NSSelectorFromString(selname);
    if(![object respondsToSelector:sel]) {
      [mp typeError:self expected:@"Correct number of arguments"];
      return NULL;
    }
    invocation=[NSInvocation invocationWithMethodSignature:[object methodSignatureForSelector:sel]];
    [invocation setSelector:sel];
    [invocation setTarget:object];
    nargsininvocation=[args count];
  }

  // check/set parameters
  for(NSUInteger i=0; i<[args count]; i++) {
    id<NSObject> v=[args objectAtIndex:i];
    const char *type=[[invocation methodSignature] getArgumentTypeAtIndex:2+i];
    if(strcmp(type, "i")==0) {
      int ival;
      if(!ISINT(v)) {
        [mp typeError:v expected:@"int" details:@{@"function": name, @"arg":[NSNumber numberWithInt:(int)i]}];
        return NULL;
      }
      ival=[N(v) intValue];
      [invocation setArgument:&ival atIndex:(NSInteger)i+2];
    } else if (strcmp(type, "c")==0) {
      BOOL bval;
      if(!ISBOOL(v)) {
        [mp typeError:v expected:@"bool" details:@{@"function": name, @"arg":[NSNumber numberWithInt:(int)i]}];
        return NULL;
      }
      bval=[N(v) boolValue];
      [invocation setArgument:&bval atIndex:(NSInteger)i+2];
    } else if (strcmp(type, "@")==0) {
      // always works but we pass nil instead of NSNUll
      if(v==[NSNull null]) v=nil;
      [invocation setArgument:&v atIndex:(NSInteger)i+2];
    } else {
      [mp typeError:v expected:@"known type" details:@{@"function": name, @"arg":[NSNumber numberWithInt:(int)i], @"typesig":[NSString stringWithUTF8String:type]}];
      return NULL;
    }
  }

  // make the call
  [invocation invoke];

  // check error flag
  if([mp getError])
    return NULL;

  // now deal with return
  const char *returntype=[[invocation methodSignature] methodReturnType];
  if(strcmp(returntype, "i")==0) {
    int ival;
    [invocation getReturnValue:&ival];
    return [NSNumber numberWithInt:ival];
  } else if(strcmp(returntype, "c")==0) {
    BOOL bval;
    [invocation getReturnValue:&bval];
    return [NSNumber numberWithBool:bval];
  } else if(strcmp(returntype, "@")==0) {
    id oval;
    [invocation getReturnValue:&oval];
    return oval;
  } else if(strcmp(returntype, "v")==0) {
    return [NSNull null];
  } else {
    [mp typeError:self expected:@"known type" details:@{@"function": name, @"returntypesig":[NSString stringWithUTF8String:returntype]}];
    return NULL;
  }
}

@end
