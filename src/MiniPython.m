#import "MiniPython.h"

NSString * const MiniPythonErrorDomain=@"MiniPythonErrorDomain";

@interface MiniPythonError : NSError
+ (NSError*) withMiniPython:(MiniPython*)mp code:(NSInteger)code userInfo:(NSDictionary*)userinfo;
@end

@interface MiniPythonContext : NSObject
- (void) setValue:(NSObject*)v forName:(NSString*)n;
- (NSObject*) getName:(NSString*)n;
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

- (void) setValue:(NSObject*)v forName:(NSString*)n {
  MiniPythonContext *use=self;

  if(use->parent && globals && [globals containsObject:n]) {
    while(use->parent)
      use=use->parent;
  }
  if(!use->variables)
    use->variables=[[NSMutableDictionary alloc] init];
  [use->variables setObject:v forKey:n];
}

- (NSObject*) getName:(NSString*)n {
  MiniPythonContext *use=self;

  if(use->parent && globals && [globals containsObject:n]) {
    while(use->parent)
      use=use->parent;
  }

  return (use->variables)?[use->variables objectForKey:n]:nil;
}

@end

@interface MiniPython (Private)
- (NSObject*) mainLoop:(NSError**)error;
- (NSError*) internalError:(int)errcode reason:(NSString*)str;
- (NSError*) typeError:(NSObject*)val expected:(NSString*)type;
- (NSError*) binaryOpError:(NSString*)op left:(NSObject*)l right:(NSObject*)r;
- (NSError*) callClientError:(NSError*)error;
- (void) outOfMemory;
- (NSDictionary*) stateForError;
- (int) builtin_cmp:(NSObject*)left :(NSObject*)right;
- (NSNumber*) builtin_bool:(NSObject*)value;
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
  MiniPythonContext *context;
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
  context=[[MiniPythonContext alloc] initWithParent:nil];
  stacktop=-1;
  pc=-1;
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
    pc=0;
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

#define ERROR(c,s) do { *error=[self internalError:MiniPython##c reason:(s)]; return nil; } while(0)
#define STRINGCHECK(v) do {if((v)<0 || (v)>=nstrings) ERROR(InternalError, @"Invalid string index"); } while(0)
#define TYPEERROR(v,s) do { *error=[self typeError:(v) expected:(s)]; return nil; } while(0)
#define BINARYOPERROR(op,l,r) do { *error=[self binaryOpError:(op) left:(l) right:(r)]; return nil;} while(0)

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

- (NSObject*) mainLoop:(NSError **)error {
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
    case 4: // GT
    case 5: // LT
    case 6: // EQ
    case 7: // IN
    case 31: // GTE
    case 32: // LTE
    case 26: // NOT_EQ
    case 27: // SUB
    case 23: // PRINT  (further checking in implementation)
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
    case 10: // CALL
    case 11: // POP_TOP
    case 12: // ATTR
    case 14: // SUBSCRIPT
    case 15: // SUBSCRIPT_SLICE
    case 25: // ITER
    case 28: // DEL_INDEX
    case 29: // DEL_SLICE
    case 30: // MOD
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
        stack[stacktop]=[NSNumber numberWithBool:![[self builtin_bool:stack[stacktop]] boolValue]];
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

    case 27: // SUB
      {
        NSObject *right=stack[stacktop--], *left=stack[stacktop--];
        if(ISINT(left) && ISINT(right)) {
          stack[++stacktop]=[NSNumber numberWithInt:[N(left) intValue]-[N(right) intValue]];
          continue;
        }
        BINARYOPERROR(@"-", left, right);
      }

    case 2: // MULT
      {
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
        if(stacktop+1<0 || stacktop+nargs>=stacklimit)
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
        NSObject *o = stack[stacktop--];
        ERROR(AssertionError, ISNONE(o)?@"assertion failed":[MiniPython toPyString:o]);
      }

    // control flow

    case 19: // EXIT_LOOP
      {
        return nil;
      }

    case 130: // IF_FALSE
      {
        if(![[self builtin_bool:stack[stacktop--]] boolValue]) {
          pc=val; // checked at top of switch
        }
        continue;
      }

    case 132: // AND
    case 133: // OR
      {
        if([[self builtin_bool:stack[stacktop]] boolValue] == (op==133)) {
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
        NSObject *v=[context getName:strings[val]];
        if(v) {
          stack[++stacktop]=v;
          continue;
        }
        ERROR(NameError, ([NSString stringWithFormat:@"name '%@' is not defined", strings[val]]));
      }

    case 0: // FUNCTION_PROLOG
    case 7: // IN
    case 8: // UNARY_ADD
    case 9: // RETURN
    case 10: // CALL
    case 12: // ATTR
    case 14: // SUBSCRIPT
    case 15: // SUBSCRIPT_SLICE
    case 25: // ITER
    case 28: // DEL_INDEX
    case 29: // DEL_SLICE
    case 30: // MOD
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

+ (NSString*) toPyString:(NSObject*)value {
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

+ (NSString*) toPyTypeString:(NSObject*)value {
  if(ISNONE(value)) return @"NoneType";
  if(ISSTRING(value)) return @"str";
  if(ISBOOL(value)) return @"bool";
  if(ISINT(value))  return @"int";
  if(ISLIST(value)) return @"list";
  if(ISDICT(value)) return @"dict";

  // ::TODO:: more type strings
  return [NSString stringWithFormat:@"Need toPyTypeString of %@: %@", [value class], value];
}

- (int) builtin_cmp:(NSObject*)left :(NSObject*)right {
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
      NSObject *l=[li nextObject],
        *r=[ri nextObject];
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

- (NSNumber*) builtin_bool:(NSObject*)value {
  BOOL res=NO;

  if(ISBOOL(value)) {
    return N(value);
  } else if(ISNONE(value)) {
    // always false
  } else if(ISINT(value)) {
    res= 0!=[N(value) intValue];
  } else if(ISSTRING(value)) {
    res= 0!=[S(value) length];
  } else if(ISLIST(value)) {
    res= 0!=[L(value) count];
  } else if(ISDICT(value)) {
    res= 0!=[D(value) count];
  } else // treat unknown objects as true
    res=YES;

  return [NSNumber numberWithBool:res];
}

- (NSError*) internalError:(int)errcode reason:(NSString*)str {
  return [self callClientError:[MiniPythonError
                                 withMiniPython:self
                                           code:errcode
                                       userInfo:@{@"reason": str}]];

}

- (NSError*) typeError:(NSObject*)value expected:(NSString*)type {
  return [self callClientError:[NSError errorWithDomain:MiniPythonErrorDomain
                                                   code:MiniPythonTypeError
                                               userInfo:@{@"expected": type, @"got":[MiniPython toPyTypeString:value]}]];
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

- (NSDictionary*) stateForError {
  return @{
    @"pc":[NSNumber numberWithInt:pc],
      @"stacktop":[NSNumber numberWithInt:stacktop]
      };
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
@end
