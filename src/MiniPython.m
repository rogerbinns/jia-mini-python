#if !__has_feature(objc_arc)
#error "ARC: Automatic reference counting must be enabled for this file"
#endif

#pragma clang diagnostic ignored "-Wunknown-pragmas"
#pragma clang diagnostic ignored "-Wdirect-ivar-access"
#pragma clang diagnostic ignored "-Wreceiver-is-weak"
#pragma clang diagnostic ignored "-Warc-repeated-use-of-weak"

#import "MiniPython.h"
#import <objc/runtime.h>

NSString *const MiniPythonErrorDomain = @"MiniPythonErrorDomain";

@interface MiniPythonError : NSError
+ (NSError *)withMiniPython:(MiniPython *)mp code:(NSInteger)code userInfo:(NSDictionary *)userinfo;
@end

@interface MiniPythonModule : NSObject <NSCopying>
- (NSObject *)initWithDelegate:(NSObject *)delegate name:(NSString *)name;

- (BOOL)hasMethod:(NSString *)name;

- (NSObject *)delegate;

- (BOOL)isEqual:(id)other;

- (NSUInteger)hash;
@end

@interface MiniPythonContext : NSObject <NSCopying>
- (id)initWithParent:(MiniPythonContext *)p;

- (void)setValue:(NSObject *)v forName:(NSString *)n;

- (NSObject *)getName:(NSString *)n;

- (MiniPythonContext *)parent;

- (BOOL)hasLocal:(NSString *)name;

- (void)markGlobal:(NSString *)name;

- (BOOL)delName:(NSString *)name;

- (NSObject *)getGlobalName:(NSString *)name;

- (NSDictionary *)globals;

- (NSDictionary *)locals;
@end

@interface MiniPythonNativeMethod : NSObject <NSCopying>
// regular global method
- (NSObject *)init:(MiniPython *)mp name:(NSString *)name target:(NSObject *)object;

// method on an instance of something (dict, list etc)
- (NSObject *)init:(MiniPython *)mp name:(NSString *)name target:(NSObject *)object instance:(NSObject *)instance;

- (NSObject *)call:(NSArray *)args;

- (BOOL)isEqual:(id)other;

- (NSUInteger)hash;

- (BOOL)hasInstance;
@end

@interface MiniPythonMethod : NSObject <NSCopying>
- (NSObject *)initWithPC:(int)pc context:(MiniPythonContext *)context;

- (NSObject *)instance;

- (void)setInstance:(NSObject *)instance;

- (int)pc;

- (MiniPythonContext *)context;

- (void)setName:(NSString *)name;

- (BOOL)isEqual:(id)other;

- (NSUInteger)hash;
@end

@implementation MiniPython {
    int stacklimit;
    id <MiniPythonClientDelegate> client;
    __strong NSString **strings;
    __strong NSObject **stack;
    uint16_t *linenotab;
    int nlineno;
    int nstrings;
    uint8_t *code;
    int codesize;
    int stacktop;
    MiniPythonContext *context;
    NSString *currentmethod;
    int pc;
    NSError *errorindicator;
    NSSet *instance_methods;
    NSRecursiveLock *theLock;

}

- (id)init {
    if ((self = [super init])) {
        theLock = [[NSRecursiveLock alloc] init];
        stacklimit = 1024;
        // build up list of known instance methods
        instance_methods = [[NSMutableSet alloc] init];
        Method *methods = class_copyMethodList([self class], NULL);
        Method *m = methods;
        while (*m) {
            SEL sel = method_getName(*m);
            if (strncmp(sel_getName(sel), "instance_", 9) == 0) {
                const char *name = sel_getName(sel) + 9;
                unsigned i;
                for (i = 0; name[i] && name[i] != ':'; i++) {}
                NSString *funcname = [[NSString alloc] initWithBytes:name length:i encoding:NSASCIIStringEncoding];
                [(NSMutableSet *) instance_methods addObject:funcname];
            }
            m++;
        }
        free(methods);
    }

    return self;
}

// alternative is @synchronized(self) { / }
#define LOCKMP [theLock lock];
#define UNLOCKMP [theLock unlock];

- (void)setClient:(id <MiniPythonClientDelegate>)delegate {
    client = delegate;
}

- (void)clear {
    LOCKMP;
    context = nil;
    if (strings) {
        for (int i = 0; i < nstrings; i++) {
            strings[i] = nil;
        }
        free(strings);
        strings = NULL;
    }

    if (stack) {
        for (int i = 0; i < stacklimit; i++) {
            stack[i] = nil;
        }
        free(stack);
        stack = NULL;
    }

    free(linenotab);
    linenotab = NULL;

    free(code);
    code = NULL;

    errorindicator = nil;
    UNLOCKMP;
}

- (BOOL)setCode:(NSInputStream *)stream error:(NSError * __autoreleasing *)error {
    LOCKMP;
    BOOL ret = [self setCodeLocked:stream error:error];
    UNLOCKMP;
    return ret;
}

#define ERRORNOMEM(x) do { free(stringbuf); [self clear]; [self internalError:MiniPythonOutOfMemory reason:x]; if(error) *error=[self getError]; return NO; } while(0)

#define read16(v) { \
   uint8_t buf[2]; \
   res=[stream read:buf maxLength:2]; \
   if(res!=2) goto onerror; \
   v=(buf[0] | (buf[1]<<8)); }

- (BOOL)setCodeLocked:(NSInputStream *)stream error:(NSError * __autoreleasing *)error {
    NSInteger res = 0, errorcode = 0;
    int stringbuflen = 256;
    void *stringbuf = malloc((size_t) stringbuflen);
    if (!stringbuf) {stringbuflen = 0;}

    // check clear was called
    if (stack) {
        [self internalError:MiniPythonNeedsClear reason:@"You must clear to reuse this instance"];
        if (error) {*error = [self getError];}
        free(stringbuf);
        return NO;
    }
    [self addBuiltins];

    stack = (__strong NSObject **) calloc((size_t) stacklimit, sizeof(NSObject *));
    if (!stack) ERRORNOMEM(@"allocating stack");

    int version;
    read16(version);
    if (version != 0) {
        errorcode = MiniPythonUnknownVersionError;
        goto onerror;
    }

    // Strings
    read16(nstrings);
    strings = (__strong NSString **) calloc((size_t) nstrings, sizeof(NSString *));
    if (!strings) ERRORNOMEM(@"allocating string table");

    for (int i = 0; i < nstrings; i++) {
        int len;
        read16(len);
        if (len > stringbuflen) {
            stringbuflen = len + 256;
            stringbuf = realloc(stringbuf, (size_t) stringbuflen);
            if (!stringbuf) ERRORNOMEM(@"allocating string");
        }
        if (len) {
            res = [stream read:stringbuf maxLength:(NSUInteger) len];
            if (res != (NSInteger) len) {goto onerror;}
        }
        strings[i] = [[NSString alloc] initWithBytes:stringbuf length:(NSUInteger) len encoding:NSUTF8StringEncoding];
        if (!strings[i]) {
            [self clear];
            [self internalError:MiniPythonInternalError reason:[NSString stringWithFormat:@"Unable to read string #%d as utf8", i]];
            if (error) {*error = [self getError];}
            free(stringbuf);
            return NO;
        }
    }

    // line number table
    read16(nlineno);
    if (nlineno) {
        linenotab = malloc((size_t) (nlineno * 4));
        if (linenotab) {
            res = [stream read:(uint8_t *) linenotab maxLength:(NSUInteger) (nlineno * 4)];
        }
        if (res != (NSInteger) (nlineno * 4)) {
            goto onerror;
        }
    }

    free(stringbuf);
    stringbuf = NULL;

    // code
    read16(codesize);
    code = malloc((size_t) codesize);
    if (!code) ERRORNOMEM(@"allocating code");
    res = [stream read:code maxLength:(NSUInteger) codesize];
    if (res != (NSInteger) codesize) {
        goto onerror;
    }

    {
        pc = 0;
        stacktop = -1;
        @autoreleasepool {
            [self mainLoop];
        }
        stacktop = -1;
        pc = 0;
        if (errorindicator) {
            if (error) {*error = errorindicator;}
            return NO;
        }
    }

    return YES;

    onerror:
    [self setNSError:[MiniPythonError withMiniPython:self
                                                code:(errorcode != 0) ? errorcode : ((res < 0) ? MiniPythonStreamError : MiniPythonEndOfStreamError)
                                            userInfo:(errorcode == 0) ? @{@"readresult" : [NSNumber numberWithInteger:res]}
                                                : nil]];
    if (error) {*error = errorindicator;}
    free(stringbuf);
    return NO;
}

- (void)dealloc {
    [self clear];
}

#define ERROR(c,s) do { [self internalError:MiniPython##c reason:(s)]; return nil; } while(0)
#define STRINGCHECK(v) do {if((v)<0 || (v)>=nstrings) ERROR(InternalError, @"Invalid string index"); } while(0)
#define TYPEERROR(v,s) do { [self typeError:(v) expected:(s)]; return nil; } while(0)
#define BINARYOPERROR(op,l,r) do { [self binaryOpError:(op) left:(l) right:(r)]; return nil;} while(0)

#define ISNONE(v) ((v)==[NSNull null])
#define ISINT(v) ([(v) isKindOfClass:[NSNumber class]] && 0==strcmp([N(v) objCType], @encode(int)))
#define ISBOOL(v) ([(v) isKindOfClass:[NSNumber class]] && 0==strcmp([N(v) objCType], @encode(BOOL)))
#define ISSTRING(v) ([(v) isKindOfClass:[NSString class]])
#define ISLIST(v) ([(v) isKindOfClass:[NSArray class]])
#define ISLISTM(v) ([(v) isKindOfClass:[NSMutableArray class]])
#define ISDICT(v) ([(v) isKindOfClass:[NSDictionary class]])
#define ISDICTM(v) ([(v) isKindOfClass:[NSMutableDictionary class]])

#define N(v) ((NSNumber*)(v))
#define S(v) ((NSString*)(v))
#define L(v) ((NSArray*)(v))
#define D(v) ((NSDictionary*)(v))

- (NSObject *)mainLoop {
    int op, val = -1;
    BOOL stackerror = NO;
    while (1) {
        if (!code || pc >= codesize || pc < 0) ERROR(InternalError, @"invalid pc");
        op = code[pc++];
        if (op >= 128) {
            if (pc + 1 >= codesize) ERROR(InternalError, @"invalid pc supplemental");
            val = code[pc] | (code[pc + 1] << 8);
            pc += 2;
        }

        // this does stack bounds checking
        switch (op) {
            // -- check start : marker used by tool

            // does not use stack
            case 19: // EXIT_LOOP
            case 129: // GOTO
            case 163: // GLOBAL
            case 164: // DEL_NAME
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
            case 25: // ITER
            case 161: // STORE_NAME
            case 11: // POP_TOP
            case 9: // RETURN (further checking in implementation)
                if (stacktop < 0 || stacktop >= stacklimit) {stackerror = YES;}
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
            case 35: // IS
            case 31: // GTE
            case 32: // LTE
            case 26: // NOT_EQ
            case 27: // SUB
            case 14: // SUBSCRIPT
            case 12: // ATTR
            case 28: // DEL_INDEX
            case 165: // STORE_ATTR_NAME
            case 23: // PRINT  (further checking in implementation)
            case 10: // CALL (further checking in implementation)
                if (stacktop - 1 < 0 || stacktop >= stacklimit) {stackerror = YES;}
                break;

                // use top 3 items
            case 15: // SUBSCRIPT_SLICE
            case 33: // ASSIGN_INDEX
            case 29: // DEL_SLICE

                if (stacktop - 2 < 0 || stacktop >= stacklimit) {stackerror = YES;}
                break;

                // and the winner with 4 items
            case 0: // FUNCTION_PROLOG
                if (stacktop - 3 < 0 || stacktop >= stacklimit) {stackerror = YES;}
                break;

                // uses top and adds one
            case 131: // NEXT
                if (stacktop < 0 || stacktop + 1 >= stacklimit) {stackerror = YES;}
                break;

                // no use - adds item
            case 162: // PUSH_STR
            case 18: // PUSH_NONE
            case 21: // PUSH_TRUE
            case 22: // PUSH_FALSE
            case 200: // PUSH_INT
            case 160: // LOAD_NAME
            case 128: // MAKE_METHOD
                if (stacktop + 1 >= stacklimit) {stackerror = YES;}
                break;

                // N items
            case 202: // POP_N
                if (stacktop + 1 - val < 0) {stackerror = YES;}
                break;

                // -- check end : marker used by tool
            default:
                ERROR(InternalError, ([NSString stringWithFormat:@"Unknown/unimplemented opcode: %d", op]));
        }

        if (!stack || stackerror)
        ERROR(RuntimeError, @"Exceeded stack bounds");

        // this does the bytecode instruction
        switch (op) {
            // -- check start : marker used by tool

            // unary operators
            case 24: // NOT
            {
                stack[stacktop] = [NSNumber numberWithBool:![self builtin_bool:stack[stacktop]]];
                continue;
            }

            case 8: // UNARY_ADD
            {
                if (!ISINT(stack[stacktop])) TYPEERROR(stack[stacktop], @"int");
                continue;
            }

            case 13: // UNARY_NEG
            {
                if (ISINT(stack[stacktop])) {
                    stack[stacktop] = [NSNumber numberWithInt:-[N(stack[stacktop]) intValue]];
                } else TYPEERROR(stack[stacktop], @"int");
                continue;
            }

                // binary operators
            case 1: // ADD
            {
                NSObject *right = stack[stacktop--], *left = stack[stacktop--];

                if (ISINT(left) && ISINT(right)) {
                    stack[++stacktop] = [NSNumber numberWithInt:[N(left) intValue] + [N(right) intValue]];
                    continue;
                } else if (ISSTRING(left) && ISSTRING(right)) {
                    stack[++stacktop] = [S(left) stringByAppendingString:S(right)];
                    continue;
                } else if (ISLIST(left) && ISLIST(right)) {
                    NSMutableArray *res = [NSMutableArray arrayWithCapacity:[L(left) count] + [L(right) count]];
                    [res addObjectsFromArray:L(left)];
                    [res addObjectsFromArray:L(right)];
                    stack[++stacktop] = res;
                    continue;
                }
                BINARYOPERROR(@"+", left, right);
            }

            case 27: // SUB
            {
                NSObject *right = stack[stacktop--], *left = stack[stacktop--];
                if (ISINT(left) && ISINT(right)) {
                    stack[++stacktop] = [NSNumber numberWithInt:[N(left) intValue] - [N(right) intValue]];
                    continue;
                }
                BINARYOPERROR(@"-", left, right);
            }

            case 2: // MULT
            {
                NSObject *right = stack[stacktop--], *left = stack[stacktop--];
                if (ISINT(left) && ISINT(right)) {
                    stack[++stacktop] = [NSNumber numberWithInt:[N(left) intValue] * [N(right) intValue]];
                    continue;
                }
                if ((ISSTRING(left) && ISINT(right)) || (ISSTRING(right) && ISINT(left))) {
                    // http://stackoverflow.com/a/4608137/463462
                    int mult = [N(ISINT(right) ? right : left) intValue];
                    unsigned multdash = (mult < 0) ? 0u : (unsigned) mult;
                    NSString *base = (NSString *) (ISSTRING(left)? left : right);
                    stack[++stacktop] = [@"" stringByPaddingToLength:[base length] * multdash withString:base startingAtIndex:0];
                    continue;
                }
                if ((ISLIST(left) && ISINT(right)) || (ISLIST(right) && ISINT(left))) {
                    int mult = [N(ISINT(right) ? right : left) intValue];
                    unsigned multdash = (mult < 0) ? 0u : (unsigned) mult;
                    NSArray *base = (NSArray *) (ISLIST(left)? left : right);
                    NSMutableArray *res = [NSMutableArray arrayWithCapacity:multdash * [base count]];
                    for (unsigned i = 0; i < multdash; i++) {
                        [res addObjectsFromArray:base];
                    }
                    stack[++stacktop] = res;
                    continue;
                }
                BINARYOPERROR(@"*", left, right);
            }

            case 3: // DIV
            {
                NSObject *right = stack[stacktop--], *left = stack[stacktop--];
                if (ISINT(left) && ISINT(right)) {
                    int l = [N(left) intValue], r = [N(right) intValue];
                    if (!r) ERROR(ArithmeticError, @"Division by zero");
                    int res;
                    if (l == -2147483648 && r == -1) {
                        res = -2147483648;
                    } else {
                        res = l / r;
                        // http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
                        if (!(l >= 0 && r >= 0) && !(l < 0 && r < 0) && l % r != 0) {
                            res--;
                        }

                    }
                    stack[++stacktop] = [NSNumber numberWithInt:res];
                    continue;
                }
                BINARYOPERROR(@"/", left, right);
            }

            case 30: // MOD
            {
                NSObject *right = stack[stacktop--], *left = stack[stacktop--];
                if (ISINT(left) && ISINT(right)) {
                    int l = [N(left) intValue], r = [N(right) intValue];
                    if (!r) ERROR(ArithmeticError, @"Modulo by zero");
                    int res = l % r;
                    // in Python the result sign is same as sign of right
                    if ((res < 0 && r >= 0) || (res >= 0 && r < 0)) {
                        res = -res;
                    }
                    stack[++stacktop] = [NSNumber numberWithInt:res];
                    continue;
                } else if (ISSTRING(left) && ISLIST(right)) {
                    NSString *fmt = [self format:S(left) with:L(right)];
                    if (!fmt) {return nil;}
                    stack[++stacktop] = fmt;
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
                NSObject *right = stack[stacktop--], *left = stack[stacktop--];

                int cmp = [self builtin_cmp:left :right];
                BOOL res = NO;
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

            case 35: // IS
            {
                NSObject *l = stack[stacktop--], *r = stack[stacktop--];
                stack[++stacktop] = [NSNumber numberWithBool:l == r];
                continue;
            }

                // lists, dicts, complex operations
            case 16: // DICT
            {
                if (!ISINT(stack[stacktop])) ERROR(InternalError, @"DICT expected int");
                int nitems = [N(stack[stacktop--]) intValue];
                stacktop -= nitems * 2;
                if (nitems < 0 || (nitems && (stacktop + 1 < 0 || nitems > stacklimit || stacktop + nitems * 2 >= stacklimit)))
                ERROR(RuntimeError, @"Exceeded stack bounds in dict");
                NSMutableDictionary *res = [NSMutableDictionary dictionaryWithCapacity:(NSUInteger) nitems];
                for (int i = 0; i < nitems; i++) {
                    [res setObject:stack[stacktop + 1 + i * 2] forKey:(id <NSCopying>) stack[stacktop + 1 + i * 2 + 1]];
                }
                stack[++stacktop] = res;
                continue;
            }

            case 17: // LIST
            {
                if (!ISINT(stack[stacktop])) ERROR(InternalError, @"LIST expected int");
                int nitems = [N(stack[stacktop--]) intValue];
                stacktop -= nitems;
                if (nitems < 0 || (nitems && (stacktop + 1 < 0 || nitems > stacklimit || stacktop + nitems >= stacklimit)))
                ERROR(RuntimeError, @"Exceeded stack bounds in list");
                NSMutableArray *res = [NSMutableArray arrayWithCapacity:(NSUInteger) nitems];
                for (int i = 0; i < nitems; i++) {
                    [res addObject:stack[stacktop + 1 + i]];
                }
                stack[++stacktop] = res;
                continue;
            }

            case 7: // IN
            {
                NSObject *collection = stack[stacktop--];
                NSObject *key = stack[stacktop--];
                BOOL res;
                if (ISDICT(collection)) {
                    res = !![D(collection) objectForKey:key];
                } else if (ISLIST(collection)) {
                    res = [L(collection) containsObject:key];
                } else if (ISSTRING(collection) && ISSTRING(key)) {
                    res = [S(key) length] == 0 || [S(collection) rangeOfString:S(key)].location != NSNotFound;
                } else  BINARYOPERROR(@"in", key, collection);

                stack[++stacktop] = [NSNumber numberWithBool:res];
                continue;
            }

            case 25: // ITER
            {
                NSObject *object = stack[stacktop--];
                if (ISLIST(object)) {
                    stack[++stacktop] = [L(object) objectEnumerator];
                } else if (ISDICT(object)) {
                    stack[++stacktop] = [D(object) keyEnumerator];
                } else TYPEERROR(object, @"iterable");
                continue;
            }

            case 131: // NEXT
            {
                NSObject *iter = stack[stacktop];
                if (![iter isKindOfClass:[NSEnumerator class]])
                ERROR(InternalError, @"Non-iterator for next");
                NSObject *v = [(NSEnumerator *) iter nextObject];
                if (v) {
                    stack[++stacktop] = v;
                } else {pc = val;}
                continue;
            }

            case 14: // SUBSCRIPT
            {
                NSObject *key = stack[stacktop--], *object = stack[stacktop--];
                if (ISLIST(object)) {
                    if (!ISINT(key)) ERROR(TypeError, [@"list indices must be int not "
                        stringByAppendingString:[MiniPython toPyTypeString:key]]);
                    int index = [N(key) intValue];
                    NSArray *list = L(object);
                    int length = (int) [list count];
                    if (index < 0) {index += length;}
                    if (index < 0 || index >= length) ERROR(IndexError, @"list index out of range");
                    stack[++stacktop] = [list objectAtIndex:(NSUInteger) index];
                    continue;
                } else if (ISDICT(object)) {
                    NSObject *v = [D(object) objectForKey:key];
                    if (!v) ERROR(KeyError, [MiniPython toPyReprString:key]);
                    stack[++stacktop] = v;
                    continue;
                } else if (ISSTRING(object)) {
                    if (!ISINT(key)) ERROR(TypeError, [@"str indices must be int not "
                        stringByAppendingString:[MiniPython toPyTypeString:key]]);
                    int index = [N(key) intValue];
                    int length = (int) [S(object) length];
                    if (index < 0) {index += length;}
                    if (index < 0 || index >= length) ERROR(IndexError, @"str index out of range");
                    stack[++stacktop] = [S(object) substringWithRange:NSMakeRange((NSUInteger) index, 1)];
                    continue;
                }
                TYPEERROR(object, @"object is not subscriptable");
            }

            case 15: // SUBSCRIPT_SLICE
            {
                NSObject *to = stack[stacktop--], *from = stack[stacktop--], *object = stack[stacktop--];
                if (!(ISLIST(object) || ISSTRING(object)))
                ERROR(TypeError, ([NSString stringWithFormat:@"you can only slice lists and strings, not %@",
                                                             [MiniPython toPyTypeString:object]]));
                if (!((ISNONE(to) || ISINT(to)) && (ISNONE(from) || ISINT(from))))
                ERROR(TypeError, ([NSString stringWithFormat:@"slice indices must both be integers (or None): supplied %@ and %@",
                                                             [MiniPython toPyTypeString:from], [MiniPython toPyTypeString:to]]));
                int length = ISSTRING(object)? (int) [S(object) length] : (int) [L(object) count];
                int ifrom = ISNONE(from)? 0 : [N(from) intValue];
                int ito = ISNONE(to)? length : [N(to) intValue];
                // NB: slices are allowed to supply out of bounds ranges
                if (ifrom < 0) {ifrom += length;}
                if (ifrom < 0) {ifrom = 0;}
                if (ifrom >= length) {
                    ifrom = 0;
                    ito = 0;
                }
                if (ito < 0) {ito += length;}
                if (ito < 0) {ito = 0;}
                if (ito > length) {ito = length;}
                if (ito < ifrom) {ito = ifrom;}
                if (ISLIST(object)) {
                    // subarraywithrange on mutablelist returns a non-mutablelist so we have to do this the long way
                    NSArray *sub = [L(object) subarrayWithRange:NSMakeRange((NSUInteger) ifrom, (NSUInteger) (ito - ifrom))];
                    NSMutableArray *res = [NSMutableArray arrayWithCapacity:[sub count]];
                    [res addObjectsFromArray:sub];
                    stack[++stacktop] = res;
                } else {
                    stack[++stacktop] = [S(object) substringWithRange:NSMakeRange((NSUInteger) ifrom, (NSUInteger) (ito - ifrom))];
                }
                continue;
            }

            case 29: // DEL_SLICE
            {
                if (!ISINT(stack[stacktop]) || !ISINT(stack[stacktop - 1]) || !ISLIST(stack[stacktop - 2]))
                ERROR(TypeError, [NSString stringWithFormat:@"You can only delete slices of lists using integer indices"]);
                int to = [N(stack[stacktop--]) intValue];
                int from = [N(stack[stacktop--]) intValue];
                NSMutableArray *list = (NSMutableArray *) stack[stacktop--];
                if (!ISLISTM(list)) TYPEERROR(list, @"NSMutableArray");
                NSUInteger length = [list count];
                if (from < 0) {from += (int) length;}
                if (to < 0) {to += (int) length;}
                if (from < 0) {from = 0;}
                if ((NSUInteger) to > length) {to = (int) length;}
                if (to > from) {
                    [list removeObjectsInRange:NSMakeRange((NSUInteger) from, (NSUInteger) (to - from))];
                }
                continue;
            }

            case 33: // ASSIGN_INDEX
            {
                NSObject *value = stack[stacktop--], *index = stack[stacktop--], *collection = stack[stacktop--];
                if (ISDICT(collection)) {
                    if (!ISDICTM(collection)) TYPEERROR(collection, @"NSMutableDictionary");
                    [(NSMutableDictionary *) collection setObject:value forKey:(id <NSCopying>) index];
                } else if (ISLIST(collection)) {
                    if (!ISLISTM(collection)) TYPEERROR(collection, @"NSMutableArray");
                    if (!ISINT(index)) TYPEERROR(index, @"int");
                    int iindex = [N(index) intValue];
                    NSUInteger length = [L(collection) count];
                    if (iindex < 0) {iindex += (int) length;}
                    if ((NSUInteger) iindex >= length) ERROR(IndexError,
                    ([NSString stringWithFormat:@"list assignment index out of range: %d", iindex]));
                    [(NSMutableArray *) collection replaceObjectAtIndex:(NSUInteger) iindex withObject:value];
                } else TYPEERROR(collection, @"object supporting item assignment");
                continue;
            }

            case 28: // DEL_INDEX
            {
                NSObject *item = stack[stacktop--], *container = stack[stacktop--];
                if (ISDICT(container)) {
                    if (!ISDICTM(container)) TYPEERROR(container, @"NSMutableDictionary");
                    if (![D(container) objectForKey:item]) ERROR(KeyError, [MiniPython toPyReprString:item]);
                    [(NSMutableDictionary *) container removeObjectForKey:item];
                } else if (ISLIST(container)) {
                    if (!ISLISTM(container)) TYPEERROR(container, @"NSMutableArray");
                    if (!ISINT(item)) TYPEERROR(item, @"int");
                    int iindex = [N(item) intValue];
                    NSUInteger length = [L(container) count];
                    if (iindex < 0) {iindex += (int) length;}
                    if ((NSUInteger) iindex >= length) ERROR(IndexError,
                    ([NSString stringWithFormat:@"list deletion index out of range: %d", iindex]));
                    [(NSMutableArray *) container removeObjectAtIndex:(NSUInteger) iindex];
                } else TYPEERROR(container, @"object supporting item deletion");
                continue;
            }

            case 12: // ATTR
            {
                NSObject *o = stack[stacktop--], *key = stack[stacktop--];
                if (!ISSTRING(key)) TYPEERROR(key, @"str");

                if ([o isKindOfClass:[MiniPythonModule class]]) {
                    if ([(MiniPythonModule *) o hasMethod:(NSString *) key]) {
                        stack[++stacktop] = [[MiniPythonNativeMethod alloc] init:self name:(NSString *) key target:[(MiniPythonModule *) o delegate]];
                        continue;
                    }
                } else if (ISDICT(o)) {
                    // instance value or method?
                    NSObject *v = [(NSDictionary *) o objectForKey:key];
                    if (v) {
                        if ([v isKindOfClass:[MiniPythonMethod class]]) {
                            v = [(MiniPythonMethod *) v copy];
                            [(MiniPythonMethod *) v setInstance:D(o)];
                        }
                        stack[++stacktop] = v;
                        continue;
                    }
                }

                // Find a native instance method
                NSString *name = [NSString stringWithFormat:@"%@_%@", [MiniPython toPyTypeString:o], S(key)];
                if ([instance_methods containsObject:name]) {
                    stack[++stacktop] = [[MiniPythonNativeMethod alloc] init:self name:name target:self instance:o];
                    continue;
                }

                ERROR(AttributeError, ([NSString stringWithFormat:@"No attribute '%@' of %@ %@",
                                                                  [MiniPython toPyString:key], [MiniPython toPyTypeString:o],
                                                                  [MiniPython toPyReprString:o]]));
            }

            case 165: // STORE_ATTR_NAME
            {
                STRINGCHECK(val);
                NSObject *o = stack[stacktop--], *v = stack[stacktop--];

                if (ISDICTM(o)) {
                    [(NSMutableDictionary *) o setObject:v forKey:strings[val]];
                    continue;
                }
                TYPEERROR(o, @"dict");
            }

                // stack things
            case 11: // POP_TOP
            {
                stacktop--;
                continue;
            }
            case 202: // POP_N
            {
                stacktop -= val;
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
                if (!ISINT(stack[stacktop])) ERROR(InternalError, @"PUSH_INT_HI expected int");
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
                if (!ISINT(stack[stacktop])) TYPEERROR(stack[stacktop], @"int");
                if (!ISBOOL(stack[stacktop - 1])) TYPEERROR(stack[stacktop - 1], @"bool");

                int nargs = [N(stack[stacktop--]) intValue];
                BOOL nl = [N(stack[stacktop--]) boolValue];

                if (nargs < 0 || nargs > stacklimit)
                ERROR(RuntimeError, @"Exceeded stack bounds in print");

                stacktop -= nargs;
                if (nargs && (stacktop + 1 < 0 || stacktop + nargs >= stacklimit))
                ERROR(RuntimeError, @"Exceeded stack bounds in print");
                NSMutableString *output = [[NSMutableString alloc] init];
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
                ERROR(AssertionError, ISNONE(o) ? @"assertion failed" : [MiniPython toPyString:o]);
            }

                // control flow

            case 19: // EXIT_LOOP
            {
                return nil;
            }

            case 130: // IF_FALSE
            {
                if (![self builtin_bool:stack[stacktop--]]) {
                    pc = val; // checked at top of switch
                }
                continue;
            }

            case 132: // AND
            case 133: // OR
            {
                if ([self builtin_bool:stack[stacktop]] == (op == 133)) {
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
                NSObject *item = stack[stacktop--];
                if ([item isKindOfClass:[MiniPythonMethod class]]) {
                    [(MiniPythonMethod *) item setName:strings[val]];
                }
                [context setValue:item forName:strings[val]];
                continue;
            }
            case 160: // LOAD_NAME
            {
                STRINGCHECK(val);
                NSObject *v = [context getName:strings[val]];
                if (v) {
                    stack[++stacktop] = v;
                    continue;
                }
                ERROR(NameError, ([NSString stringWithFormat:@"name '%@' is not defined", strings[val]]));
            }

            case 163: // GLOBAL
            {
                STRINGCHECK(val);
                if ([context parent]) {
                    if ([context hasLocal:strings[val]])
                    ERROR(SyntaxError, ([NSString stringWithFormat:@"Name '%@' is assigned to before 'global' declaration",
                                                                   strings[val]]));
                    [context markGlobal:strings[val]];
                }
                continue;
            }

            case 164: // DEL_NAME
            {
                STRINGCHECK(val);
                if (![context delName:strings[val]]) ERROR(NameError, ([NSString stringWithFormat:@"Name '%@' is not defined", strings[val]]));
                continue;
            }

                // function calls
            case 10: // CALL
            {
                NSObject *func = stack[stacktop--];
                if (![self builtin_callable:func])
                TYPEERROR(func, @"method");


                if (!ISINT(stack[stacktop])) ERROR(InternalError, @"bad method call sequence");
                int nargs = [N(stack[stacktop]) intValue];
                if (nargs < 0 || nargs > stacklimit)
                ERROR(RuntimeError, @"Exceeded stack bounds in call");

                if ([func isKindOfClass:[MiniPythonNativeMethod class]]) {
                    stacktop--;
                    stacktop -= nargs;
                    if (nargs && (stacktop + 1 < 0 || stacktop + nargs + 1 >= stacklimit))
                    ERROR(RuntimeError, @"Exceeded stack bounds in call");

                    NSMutableArray *args = [NSMutableArray arrayWithCapacity:(NSUInteger) nargs];
                    for (int i = 0; i < nargs; i++) {
                        [args addObject:stack[stacktop + i + 1]];
                    }

                    NSString *origmethod = currentmethod;
                    currentmethod = [func description];
                    NSObject *res = [(MiniPythonNativeMethod *) func call:args];
                    currentmethod = origmethod;
                    if (errorindicator) {return nil;}
                    stack[++stacktop] = res;
                    continue;
                }
                // ::TODO:: we can look at instruction at pc which should be a push_int of
                // how many args the function takes and compare against current stacktop.  we have to
                // do that here because function prolog has no idea

                // regular python method
                MiniPythonMethod *method = (MiniPythonMethod *) func;
                if ([method instance]) {[self adjustArgsForBoundMethod:[method instance]];}
                stack[++stacktop] = context;
                stack[++stacktop] = [NSNumber numberWithInt:pc];
                pc = [method pc];
                context = [[MiniPythonContext alloc] initWithParent:[method context]];
                continue;
            }

            case 0: // FUNCTION_PROLOG
            {
                if (!ISINT(stack[stacktop]) || !ISINT(stack[stacktop - 1]) || ![stack[stacktop - 2] isKindOfClass:[MiniPythonContext class]]
                    || !ISINT(stack[stacktop - 3])) ERROR(InternalError, @"Bad call sequence at method prolog");
                int argsexpected = [N(stack[stacktop--]) intValue];
                NSObject *returnpc = stack[stacktop--];
                NSObject *returncontext = stack[stacktop--];
                int argsprovided = [N(stack[stacktop--]) intValue];
                if (argsexpected < 0 || argsexpected > stacklimit || argsprovided < 0 || argsprovided > stacklimit)
                ERROR(InternalError, @"Bad call nargs provision");
                if (argsexpected != argsprovided) ERROR(TypeError, ([NSString stringWithFormat:@"method takes %d args (%d provided)",
                                                                                               argsexpected, argsprovided]));
                // the stack contents need to be rotated - we currently have the args present
                // and need to shuffle the returnpc/context before them
                if (stacktop - argsprovided < -1) ERROR(InternalError, @"Incorrect nargs provision");
                // memcpy is not used as it would mess up ARC
                for (int i = 0; i < argsprovided; i++) {
                    stack[stacktop - i + 2] = stack[stacktop - i];
                }
                stacktop += 2;
                stack[stacktop - argsprovided] = returnpc;
                stack[stacktop - argsprovided - 1] = returncontext;
                continue;
            }

            case 9: // RETURN
            {
                if (![context parent]) ERROR(SyntaxError, @"'return' outside method");
                if (stacktop - 2 < 0 || stacktop >= stacklimit) ERROR(InternalError, @"incomplete stack for return");
                NSObject *retval = stack[stacktop--];
                if (!ISINT(stack[stacktop]) || ![stack[stacktop - 1] isKindOfClass:[MiniPythonContext class]])
                ERROR(InternalError, @"bad return sequence");
                int returnpc = [N(stack[stacktop--]) intValue];
                context = (MiniPythonContext *) stack[stacktop--];
                if (returnpc < 0) {return retval;}
                pc = returnpc;
                stack[++stacktop] = retval;
                continue;
            }

            case 128: // MAKE_METHOD
            {
                stack[++stacktop] = [[MiniPythonMethod alloc] initWithPC:val context:context];
                continue;
            }

            case 129: // GOTO
            {
                if (val < 0 || val >= codesize) ERROR(InternalError, @"goto pc out of bounds");
                pc = val;
                continue;
            }

                // -- check end : marker used by tool
            default:
                ERROR(InternalError, ([NSString stringWithFormat:@"Unknown/unimplemented opcode: %d", op]));
        }
    }
}

- (void)adjustArgsForBoundMethod:(NSObject *)instance {
    // we need to insert instance at the beginning of arg list and
    // increase number of args by one
    int nargs = [(NSNumber *) stack[stacktop] intValue];
    stack[stacktop] = [NSNumber numberWithInt:1 + nargs];
    stacktop++;
    for (int i = 0; i < nargs + 1; i++) {
        stack[stacktop - i] = stack[stacktop - i - 1];
    }
    stack[stacktop - nargs - 1] = instance;
}

- (NSObject *)call:(NSObject *)callable args:(NSArray *)args {
    int savedsp = stacktop;
    NSObject *res = nil;

    if ([callable isKindOfClass:[MiniPythonNativeMethod class]]) {
        NSString *origmethod = currentmethod;
        currentmethod = [callable description];
        res = [(MiniPythonNativeMethod *) callable call:args];
        currentmethod = origmethod;
        stacktop = savedsp;
        return res;
    }

    if ((NSUInteger) stacktop + [args count] + 4 >= (NSUInteger) stacklimit) ERROR(RuntimeError, @"Call would exceed stack bounds");

    for (NSUInteger i = 0; i < [args count]; i++) {
        stack[++stacktop] = [args objectAtIndex:i];
    }
    stack[++stacktop] = [NSNumber numberWithInt:(int) [args count]];

    MiniPythonContext *savedcontext = context;
    MiniPythonMethod *method = (MiniPythonMethod *) callable;
    if ([method instance]) {[self adjustArgsForBoundMethod:[method instance]];}

    int savedpc = pc;
    stack[++stacktop] = context;
    stack[++stacktop] = [NSNumber numberWithInt:-1];
    pc = [method pc];
    context = [[MiniPythonContext alloc] initWithParent:[method context]];
    @autoreleasepool {
        res = [self mainLoop];
    }
    pc = savedpc;
    stacktop = savedsp;
    context = savedcontext;
    return res;
}

+ (NSString *)_toPyString:(NSObject *)value quote:(BOOL)quote seen:(NSMutableSet *)seen {
    if (!value || ISNONE(value)) {
        return @"None";
    }
    if (ISSTRING(value)) {
        if (!quote) {
            return (NSString *) value;
        }
        return [NSString stringWithFormat:@"\"%@\"", [[S(value) stringByReplacingOccurrencesOfString:@"\\" withString:@"\\\\"]
            stringByReplacingOccurrencesOfString:@"\"" withString:@"\\\""]];
    }
    if (ISINT(value)) {
        return [N(value) description];
    }
    if (ISBOOL(value)) {
        return [N(value) boolValue] ? @"True" : @"False";
    }
    if (ISDICT(value) || ISLIST(value)) {
        if (!seen) {seen = [[NSMutableSet alloc] init];}
        NSMutableString *res = [[NSMutableString alloc] init];
        assert(sizeof(NSUInteger) == sizeof(id));
        NSNumber *objectid = [NSNumber numberWithUnsignedInteger:(NSUInteger) value];
        [res appendString:ISLIST(value)? @"[" : @"{"];
        if ([seen containsObject:objectid]) {
            [res appendString:@"..."];
        } else {
            [seen addObject:objectid];
            BOOL first = YES;
            for (NSObject *item in ISDICT(value) ? D(value) : L(value)) {
                if (first) {
                    first = NO;
                } else {[res appendString:@", "];}
                [res appendString:[self _toPyString:item quote:YES seen:seen]];
                if (ISDICT(value)) {
                    [res appendString:@": "];
                    [res appendString:[self _toPyString:[D(value) objectForKey:item] quote:YES seen:seen]];
                }
            }
        }
        [res appendString:ISLIST(value)? @"]" : @"}"];
        return res;
    }

    return [value description];
}

+ (NSString *)toPyString:(NSObject *)value {
    return [self _toPyString:value quote:NO seen:nil];
}

+ (NSString *)toPyReprString:(NSObject *)value {
    return [self _toPyString:value quote:YES seen:nil];
}

+ (NSString *)toPyTypeString:(NSObject *)value {
    if (!value || ISNONE(value)) {return @"NoneType";}
    if (ISSTRING(value)) {return @"str";}
    if (ISBOOL(value)) {return @"bool";}
    if (ISINT(value)) {return @"int";}
    if (ISLIST(value)) {return @"list";}
    if (ISDICT(value)) {return @"dict";}

    if ([value isKindOfClass:[MiniPythonNativeMethod class]]) {
        return [(MiniPythonNativeMethod *) value hasInstance] ? @"instancemethod" : @"modulemethod";
    }
    if ([value isKindOfClass:[MiniPythonMethod class]]) {return @"method";}
    if ([value isKindOfClass:[MiniPythonModule class]]) {return @"module";}
    if ([value isKindOfClass:[NSNumber class]]) {
        return [NSString stringWithFormat:@"NSNumber(%s)", [(NSNumber *) value objCType]];
    }

    return [[value class] description];
}

- (NSString *)format:(NSString *)format with:(NSArray *)args {
    NSMutableString *res = [[NSMutableString alloc] init];
    NSUInteger pos = 0;
    NSUInteger argpos = 0;

#define ADDCHAR(x) do { [res appendFormat:@"%C", (x)]; } while(0)
    while (pos < [format length]) {
        unichar c = [format characterAtIndex:pos];
        pos++;
        if (c != '%') {
            ADDCHAR(c);
            continue;
        }

        if (pos < [format length] && [format characterAtIndex:pos] == '%') {
            pos++;
            ADDCHAR((unichar) '%');
            continue;
        }

        BOOL flag_left = NO, flag_plus = NO, flag_space = NO, flag_zero = NO, flag_done = NO;
        do {
            if (pos >= [format length])
            ERROR(TypeError, @"incomplete format specifier");
            c = [format characterAtIndex:pos];
            switch (c) {
                case '-':
                    flag_left = YES;
                    break;
                case '+':
                    flag_plus = YES;
                    break;
                case ' ':
                    flag_space = YES;
                    break;
                case '0':
                    flag_zero = YES;
                    break;
                default:
                    flag_done = YES;
            }
            if (!flag_done) {pos++;}
        } while (!flag_done);

        NSUInteger width = 0;
        while (pos < [format length] && (c = [format characterAtIndex:pos]) && c >= '0' && c <= '9') {
            width = width * 10 + (c - '0');
            pos++;
        }

        if (pos >= [format length])
        ERROR(TypeError, @"incomplete format specifier");
        c = [format characterAtIndex:pos];
        pos++;

        if (argpos >= [args count])
        ERROR(TypeError, @"insufficient arguments for format string");
        NSObject *arg = [args objectAtIndex:argpos];
        argpos++;
        switch (c) {
            case 's': {
                NSString *s = [MiniPython toPyString:arg];
                if ([s length] >= width) {
                    [res appendString:s];
                    continue;
                }
                if (flag_left) {
                    [res appendString:s];
                    for (NSUInteger i = 0; i < width - [s length]; i++)
                        ADDCHAR((unichar) ' ');
                    continue;
                }
                for (NSUInteger i = 0; i < width - [s length]; i++)
                    ADDCHAR((unichar) ' ');
                [res appendString:s];
                continue;
            }
            case 'X':
            case 'x':
            case 'd':
                if (!ISINT(arg)) TYPEERROR(arg, @"int for formatting");
                int i = [N(arg) intValue];

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wformat-nonliteral"
                [res appendFormat:[NSString stringWithFormat:@"%%%@%@%@%@%@%C",
                                                             flag_left ? @"-" : @"",
                                                             flag_plus ? @"+" : @"",
                                                             flag_space ? @" " : @"",
                                                             flag_zero ? @"0" : @"",
                                                             width ? [NSNumber numberWithInt:(int) width] : @"",
                                                             c], i];
#pragma clang diagnostic pop

                continue;
            default:
                ERROR(TypeError, ([NSString stringWithFormat:@"Unknown format '%C'", c]));
        }
    }


    return res;
#undef ADDCHAR
}

// From here on are methods that are invoked indirectly via NSInvocation (aka reflection).  Static analysis tools will
// declare them unused.  Consequently they are marked as __unused which means that they are actually used!

- (NSObject *)builtin_apply:(NSObject *)func :(NSArray *)args __unused {
    if (![self builtin_callable:func]) TYPEERROR(func, @"method");
    if (!ISLIST(args)) TYPEERROR(args, @"list");
    if (stacktop + (int) [args count] >= stacklimit)
    ERROR(InternalError, @"stack overflow in call");
    return [self call:func args:args];
}

- (BOOL)builtin_bool:(NSObject *)value {
    if (ISBOOL(value)) {
        return [N(value) boolValue];
    } else if (!value || ISNONE(value)) {
        return NO;
    } else if (ISINT(value)) {
        return 0 != [N(value) intValue];
    } else if (ISSTRING(value)) {
        return 0 != [S(value) length];
    } else if (ISLIST(value)) {
        return 0 != [L(value) count];
    } else if (ISDICT(value)) {
        return 0 != [D(value) count];
    }

    // treat unknown objects as true
    return YES;
}

- (BOOL)builtin_callable:(NSObject *)value {
    return [value isKindOfClass:[MiniPythonNativeMethod class]]
        || [value isKindOfClass:[MiniPythonMethod class]];
}

- (int)builtin_cmp:(NSObject *)left :(NSObject *)right {
    if (left == right) {
        return 0;
    }
    if ((ISINT(left) && ISINT(right)) || (ISBOOL(left) && ISBOOL(right))) {
        int l = [N(left) intValue], r = [N(right) intValue];
        if (l == r) {return 0;}
        return (l < r) ? -1 : 1;
    }
    if ([left isEqual:right]) {return 0;}
    if (ISSTRING(left) && ISSTRING(right)) {
        NSString *l = (NSString *) left, *r = (NSString *) right;
        return (int) [l compare:r];
    }
    if (ISLIST(left) && ISLIST(right)) {
        // compare item by item with python semantics
        NSEnumerator *li = [L(left) objectEnumerator],
            *ri = [L(right) objectEnumerator];
        for (; ;) {
            NSObject *l = [li nextObject],
                *r = [ri nextObject];
            // both ended at same place?
            if (!l && !r) {return 0;}
            if (!l) {return -1;}
            if (!r) {return 1;}
            int cmp = [self builtin_cmp:l :r];
            if (cmp != 0) {return cmp;}
        }
    }
    if (ISDICT(left) && ISDICT(right)) {
        uintptr_t l = (uintptr_t) left, r = (uintptr_t) right;
        return (l < r) ? -1 : 1;
    }
    // different types compare as their type strings
    if ([left class] != [right class]) {
        return [self builtin_cmp:[MiniPython toPyTypeString:left] :[MiniPython toPyTypeString:right]];
    }
    // just compare as strings then
    NSString *ls = [MiniPython toPyString:left], *rs = [MiniPython toPyString:right];
    // we know they aren't equal so use address if strings are equal
    if ([ls isEqual:rs]) {
        uintptr_t l = (uintptr_t) left, r = (uintptr_t) right;
        return (l < r) ? -1 : 1;
    }

    return [self builtin_cmp:ls :rs];
}

- (NSArray *)builtin_filter:(NSObject *)func :(NSArray *)list __unused {
    if (![self builtin_callable:func])
    TYPEERROR(func, @"method");
    if (!ISLIST(list))
    TYPEERROR(list, @"list");

    NSObject *bvalue = nil;

    NSMutableArray *res = [[NSMutableArray alloc] init];
    for (NSObject *v in list) {
        bvalue = [self call:func args:@[v]];
        if ([self getError]) {return NULL;}
        if ([self builtin_bool:bvalue]) {
            [res addObject:v];
        }
    }
    return res;
}

- (NSDictionary *)builtin_globals __unused {
    return [context globals];
}

- (int)builtin_id:(NSObject *)value __unused {
    return (int) (value ? value : [NSNull null]);
}

- (int)builtin_int:(NSObject *)value __unused {
    if (ISINT(value)) {return [N(value) intValue];}
    if (ISBOOL(value)) {return !![N(value) boolValue];}
    if (ISSTRING(value)) {
        int ival = [S(value) intValue];
        if (ival == 0) {
            if (![value isEqual:@"0"]) {
                [self internalError:MiniPythonValueError reason:[NSString stringWithFormat:@"'%@' could not be converted to int", value]];
                return 0;
            }
        }
        return ival;
    }
    [self typeError:value expected:@"int, bool or string"];
    return 0;
}

- (int)builtin_len:(NSObject *)value __unused {
    if (ISDICT(value)) {return (int) [D(value) count];}
    if (ISLIST(value)) {return (int) [L(value) count];}
    if (ISSTRING(value)) {return (int) [S(value) length];}
    [self typeError:value expected:@"dict, list or str" details:nil];
    return 0;
}

- (NSDictionary *)builtin_locals __unused {
    return [context locals];
}

- (NSObject *)builtin_map:(NSObject *)func :(NSArray *)list __unused {
    if (![self builtin_callable:func])
    TYPEERROR(func, @"method");
    if (!ISLIST(list))
    TYPEERROR(list, @"list");

    NSMutableArray *res = [[NSMutableArray alloc] init];
    for (NSObject *v in list) {
        NSObject *value = [self call:func args:@[v]];
        if ([self getError]) {return NULL;}
        [res addObject:value];
    }
    return res;
}

// We don't have varargs support so everything gets routed to this guy
- (void)print_helper:(NSArray *)args {
    NSMutableString *output = [[NSMutableString alloc] init];
    BOOL first = YES;
    for (NSObject *item in args) {
        if (first) {
            first = NO;
        } else {[output appendString:@" "];}
        [output appendString:[MiniPython toPyString:item]];
    }
    [output appendString:@"\n"];
    [client print:output];
}

- (void)builtin_print __unused {
    [self print_helper:@[]];
}

- (void)builtin_print:(NSObject *)one __unused {
    [self print_helper:@[one]];
}

- (void)builtin_print:(NSObject *)one :(NSObject *)two __unused {
    [self print_helper:@[one, two]];
}

- (void)builtin_print:(NSObject *)one :(NSObject *)two :(NSObject *)three __unused {
    [self print_helper:@[one, two, three]];
}

- (void)builtin_print:(NSObject *)one :(NSObject *)two :(NSObject *)three :(NSObject *)four __unused {
    [self print_helper:@[one, two, three, four]];
}

- (void)builtin_print:(NSObject *)one :(NSObject *)two :(NSObject *)three :(NSObject *)four :(NSObject *)five __unused {
    [self print_helper:@[one, two, three, four, five]];
}

- (void)builtin_print:(NSObject *)one :(NSObject *)two :(NSObject *)three :(NSObject *)four :(NSObject *)five
    :(NSObject *)six __unused {
    [self print_helper:@[one, two, three, four, five, six]];
}

- (void)builtin_print:(NSObject *)one :(NSObject *)two :(NSObject *)three :(NSObject *)four :(NSObject *)five
    :(NSObject *)six :(NSObject *)seven __unused {
    [self print_helper:@[one, two, three, four, five, six, seven]];
}

// should be enough ....
- (void)builtin_print:(NSObject *)one :(NSObject *)two :(NSObject *)three :(NSObject *)four :(NSObject *)five
    :(NSObject *)six :(NSObject *)seven :(NSObject *)eight __unused {
    [self print_helper:@[one, two, three, four, five, six, seven, eight]];
}


- (NSArray *)builtin_range:(int)end __unused {
    return [self builtin_range:0 :end :1];
}

- (NSArray *)builtin_range:(int)start :(int)end __unused {
    return [self builtin_range:start :end :1];
}

- (NSArray *)builtin_range:(int)start :(int)stop :(int)step {
    NSMutableArray *res = [[NSMutableArray alloc] init];
    if (step == 0) ERROR(ValueError, @"step argument must not be zero");
    if (step < 0 && stop < start) {
        for (int i = start; i > stop; i += step) {
            [res addObject:[NSNumber numberWithInt:i]];
        }
    } else if (step > 0) {
        for (int i = start; i < stop; i += step) {
            [res addObject:[NSNumber numberWithInt:i]];
        }
    }

    return res;
}


- (NSString *)builtin_str:(NSObject *)value __unused {
    return [MiniPython toPyString:value];
}

- (NSString *)builtin_type:(NSObject *)value __unused {
    return [MiniPython toPyTypeString:value];
}

- (NSObject *)instance_dict_copy:(NSDictionary *)dict __unused {
    return [[NSMutableDictionary alloc] initWithDictionary:dict];
}

- (NSObject *)instance_dict_get:(NSDictionary *)dict :(NSObject *)key :(NSObject *)defvalue __unused {
    NSObject *v = [dict objectForKey:key ? key : [NSNull null]];
    return v ? v : defvalue;
}

- (void)instance_dict_update:(NSMutableDictionary *)dict :(NSObject *)other __unused {
    if (!ISDICTM(dict)) {
        [self typeError:dict expected:@"NSMutableDictionary"];
        return;
    }
    if (!ISDICT(other)) {
        [self typeError:other expected:@"dict"];
        return;
    }
    [dict addEntriesFromDictionary:D(other)];
}

- (void)instance_list_append:(NSMutableArray *)list :(NSObject *)item __unused {
    if (!ISLISTM(list)) {
        [self typeError:list expected:@"NSMutableArray"];
        return;
    }
    [list addObject:item];
}

- (void)instance_list_extend:(NSMutableArray *)list :(NSArray *)items __unused {
    if (!ISLISTM(list)) {
        [self typeError:list expected:@"NSMutableArray"];
        return;
    }
    if (!ISLIST(items)) {
        [self typeError:items expected:@"list"];
        return;
    }
    [list addObjectsFromArray:items];
}

- (int)instance_list_index:(NSArray *)list :(NSObject *)item __unused {
    NSUInteger location = [list indexOfObject:item];
    if (location == NSNotFound) {return -1;}
    return (int) location;
}

- (NSObject *)instance_list_pop:(NSMutableArray *)list __unused {
    if (!ISLISTM(list)) TYPEERROR(list, @"NSMutableArray");
    NSObject *res = [list lastObject];
    if (!res) ERROR(IndexError, @"pop from empty list");
    [list removeLastObject];
    return res;
}

- (void)instance_list_reverse:(NSMutableArray *)list __unused {
    if (!ISLISTM(list)) {
        [self typeError:list expected:@"NSMutableArray"];
        return;
    }

    if (![list count]) {return;}
    NSUInteger i = 0;
    NSUInteger j = [list count] - 1;
    while (i < j) {
        [list exchangeObjectAtIndex:i withObjectAtIndex:j];
        i++;
        j--;
    }
}


- (void)instance_list_sort:(NSMutableArray *)list __unused {
    [self instance_list_sort:list :[NSNull null] :[NSNull null] :NO];
}

- (void)instance_list_sort:(NSMutableArray *)list :(NSObject *)cmp __unused {
    [self instance_list_sort:list :cmp :[NSNull null] :NO];
}

- (void)instance_list_sort:(NSMutableArray *)list :(NSObject *)cmp :(NSObject *)key __unused {
    [self instance_list_sort:list :cmp :key :NO];
}

- (void)instance_list_sort:(NSMutableArray *)list :(NSObject *)cmp :(NSObject *)key :(BOOL)reverse {
    if (!ISLISTM(list)) {
        [self typeError:list expected:@"NSMutableArray"];
        return;
    }
    if (!(!cmp || ISNONE(cmp) || [self builtin_callable:cmp])) {
        [self typeError:cmp expected:@"callable or None"];
        return;
    }
    if (!(!key || ISNONE(key) || [self builtin_callable:key])) {
        [self typeError:key expected:@"callable or None"];
        return;
    }

    if (ISNONE(key)) {key = nil;}
    if (ISNONE(cmp)) {cmp = nil;}

    [list sortUsingComparator:^(id left, id right) {
        if ([self getError]) {return (NSComparisonResult) NSOrderedSame;}

        if (key) {
            left = [self call:key args:@[left]];
            right = [self call:key args:@[right]];
        }

        int cmpresult;

        if (cmp) {
            NSObject *res = [self call:cmp args:@[left, right]];
            if ([self getError]) {return (NSComparisonResult) NSOrderedSame;}
            if (!ISINT(res)) {
                [self typeError:res expected:@"int"];
                return (NSComparisonResult) NSOrderedSame;
            }
            cmpresult = [N(res) intValue];
        } else {
            cmpresult = [self builtin_cmp:left :right];
        }

        if (reverse) {cmpresult = -cmpresult;}

        if (cmpresult < 0) {return (NSComparisonResult) NSOrderedAscending;}
        if (cmpresult > 0) {return (NSComparisonResult) NSOrderedDescending;}
        return (NSComparisonResult) NSOrderedSame;
    }];
}

- (BOOL)instance_str_endswith:(NSString *)str :(NSString *)suffix __unused {
    if (!ISSTRING(suffix)) {
        [self typeError:suffix expected:@"str"];
        return NO;
    }
    return [suffix length] ? [str hasSuffix:suffix] : YES;
}

- (NSString *)instance_str_join:(NSString *)str :(NSObject *)with __unused {
    if (!ISLIST(with)) TYPEERROR(with, @"list");
    NSArray *list = L(with);
    NSMutableString *res = [[NSMutableString alloc] init];
    BOOL first = YES;
    for (NSObject *item in list) {
        if (!ISSTRING(item)) TYPEERROR(item, @"all list items must be str");
        if (first) {
            first = NO;
        } else {[res appendString:str];}
        [res appendString:S(item)];
    }
    return res;
}

- (NSString *)instance_str_lower:(NSString *)str __unused {
    return [str lowercaseString];
}

- (NSString *)instance_str_replace:(NSString *)str :(NSString *)find :(NSString *)replacement __unused {
    if (!ISSTRING(find)) TYPEERROR(find, @"str");
    if (!ISSTRING(replacement)) TYPEERROR(find, @"replacement");
    if ([find length]) {
        return [str stringByReplacingOccurrencesOfString:find withString:replacement];
    }
    NSMutableString *res = [[NSMutableString alloc] init];
    for (NSUInteger pos = 0; pos < [str length]; pos++) {
        [res appendFormat:@"%@%C", replacement, [str characterAtIndex:pos]];
    }
    return res;
}

- (NSArray *)internal_str_split:(NSString *)str sep:(NSString *)sep maxCount:(int)maxcount {
    NSMutableArray *res = [[NSMutableArray alloc] init];
    NSUInteger pos = 0;

    if (!sep) {
        // any whitespace and different semantics
        unichar c;
        for (; ;) {
            while (pos < [str length] && (c = [str characterAtIndex:pos], c == ' ' || c == '\t' || c == '\r' || c == '\n')) {
                pos++;
            }
            if (pos == [str length]) {return res;}
            NSUInteger pos2 = pos;
            while (pos2 < [str length] && (c = [str characterAtIndex:pos2], c != ' ' && c != '\t' && c != '\r' && c != '\n')) {
                pos2++;
            }
            [res addObject:[str substringWithRange:NSMakeRange(pos, pos2 - pos)]];
            pos = pos2;
        }
    }


    while (pos < [str length]) {
        if (maxcount >= 0 && [res count] >= (NSUInteger) maxcount) {
            [res addObject:[str substringWithRange:NSMakeRange(pos, [str length] - pos)]];
            return res;
        }

        NSRange found = [str rangeOfString:sep options:NSLiteralSearch range:NSMakeRange(pos, [str length] - pos)];
        if (found.location == NSNotFound) {
            [res addObject:[str substringWithRange:NSMakeRange(pos, [str length] - pos)]];
            return res;
        }

        [res addObject:[str substringWithRange:NSMakeRange(pos, found.location - pos)]];
        pos = found.location + found.length;
    }

    if ([str hasSuffix:sep]) {
        [res addObject:@""];
    }

    return res;
}

- (NSArray *)instance_str_split:(NSString *)str __unused {
    return [self internal_str_split:str sep:nil maxCount:-1];
}

- (NSArray *)instance_str_split:(NSString *)str :(NSString *)sep __unused {
    return [self instance_str_split:str :sep :-1];
}

- (NSArray *)instance_str_split:(NSString *)str :(NSString *)sep :(int)maxsep {
    if (!ISSTRING(sep)) TYPEERROR(sep, @"str");
    if (![sep length]) ERROR(ValueError, @"empty separator");
    return [self internal_str_split:str sep:sep maxCount:maxsep];
}

- (BOOL)instance_str_startswith:(NSString *)str :(NSString *)prefix __unused {
    if (!ISSTRING(prefix)) {
        [self typeError:prefix expected:@"str"];
        return NO;
    }
    return [prefix length] ? [str hasPrefix:prefix] : YES;
}

- (NSString *)instance_str_strip:(NSString *)str __unused {
    // builtin objc whitespace set includes U+0085 which python doesn't
    return [str stringByTrimmingCharactersInSet:[NSCharacterSet characterSetWithCharactersInString:@" \t\r\n"]];
}

- (NSString *)instance_str_upper:(NSString *)str __unused {
    return [str uppercaseString];
}

- (void)internalError:(int)errcode reason:(NSString *)str {
    [self setNSError:[MiniPythonError withMiniPython:self
                                                code:errcode
                                            userInfo:@{@"reason" : str}]];
}

- (void)typeError:(NSObject *)value expected:(NSString *)type {
    [self setNSError:[MiniPythonError withMiniPython:self
                                                code:MiniPythonTypeError
                                            userInfo:@{@"expected" : type, @"got" : [MiniPython toPyTypeString:value]}]];
}

- (void)typeError:(NSObject *)value expected:(NSString *)type details:(NSDictionary *)more {
    NSMutableDictionary *d = [[NSMutableDictionary alloc] init];
    [d addEntriesFromDictionary:more];
    [d setObject:type forKey:@"expected"];
    [d setObject:[MiniPython toPyTypeString:value] forKey:@"got"];
    [self setNSError:[MiniPythonError withMiniPython:self
                                                code:MiniPythonTypeError
                                            userInfo:d]];
}

- (void)binaryOpError:(NSString *)op left:(NSObject *)l right:(NSObject *)r {
    [self setNSError:[MiniPythonError withMiniPython:self
                                                code:MiniPythonTypeError
                                            userInfo:@{@"op" : op, @"left" : l, @"right" : r}]];
}

- (void)setNSError:(NSError *)error {
    LOCKMP;
    errorindicator = error;
    [client onError:errorindicator];
    UNLOCKMP;
}

- (void)setError:(enum MiniPythonErrorCode)code_ reason:(NSString *)reason userInfo:(NSDictionary *)userinfo {
    LOCKMP;
    NSMutableDictionary *d = [[NSMutableDictionary alloc] init];
    [d setObject:reason forKey:@"reason"];
    if (userinfo) {
        [d addEntriesFromDictionary:userinfo];
    }
    [self setNSError:[MiniPythonError withMiniPython:self
                                                code:code_
                                            userInfo:d]];
    UNLOCKMP;
}

- (NSError *)getError {
    return errorindicator;
}

- (NSDictionary *)stateForError {
    NSMutableDictionary *d = [[NSMutableDictionary alloc] init];
    [d setObject:[NSNumber numberWithInt:pc] forKey:@"pc"];
    [d setObject:[NSNumber numberWithInt:stacktop] forKey:@"stacktop"];
    if (nlineno && linenotab) {
        int line = 0;
        // linear search for first pc gte our pc (remember pc points to
        // next instruction to be executed)
        for (int i = 0; i < nlineno; i++) {
            if (linenotab[i * 2] >= pc) {
                break;
            }
            line = linenotab[i * 2 + 1];
        }
        [d setObject:[NSNumber numberWithInt:line] forKey:@"lineno"];
        if (currentmethod) {
            [d setObject:currentmethod forKey:@"currentmethod"];
        }
    }
    return d;
}

- (void)addBuiltins {
    if (!context) {
        context = [[MiniPythonContext alloc] initWithParent:nil];
    }

    Method *methods = class_copyMethodList([self class], NULL);
    Method *m = methods;
    while (*m) {
        SEL sel = method_getName(*m);
        if (strncmp(sel_getName(sel), "builtin_", 8) == 0) {
            const char *name = sel_getName(sel) + 8;
            unsigned i;
            for (i = 0; name[i] && name[i] != ':'; i++) {}
            NSString *funcname = [[NSString alloc] initWithBytes:name length:i encoding:NSASCIIStringEncoding];
            [context setValue:[[MiniPythonNativeMethod alloc] init:self name:funcname target:self] forName:funcname];
        }
        m++;
    }

    free(methods);
}


- (void)addModule:(NSObject *)module named:(NSString *)name {
    LOCKMP;
    if (!context) {
        context = [[MiniPythonContext alloc] initWithParent:nil];
    }
    MiniPythonModule *mod = [[MiniPythonModule alloc] initWithDelegate:module name:name];
    [context setValue:mod forName:name];
    UNLOCKMP;
}

- (NSObject *)callMethod:(NSString *)name args:(NSArray *)args error:(NSError * __autoreleasing *)error {
    LOCKMP;
    NSObject *retval = nil;

    NSObject *meth = [context getGlobalName:name];
    if (!meth) {
        [self internalError:MiniPythonNameError reason:[NSString stringWithFormat:@"No name '%@' found", name]];
    } else {
        retval = [self callObject:meth args:args error:error];
    }
    UNLOCKMP;
    return retval;
}

- (NSObject *)callObject:(NSObject *)meth args:(NSArray *)args error:(NSError * __autoreleasing *)error {
    LOCKMP;

    int savedsp = stacktop, savedpc = pc;
    MiniPythonContext *savedcontext = context;
    NSObject *retval = nil;

    if ([self builtin_callable:meth]) {
        retval = [self call:meth args:args];
    } else {
        [self typeError:meth expected:@"method"];
    }

    if ([self getError]) {
        if (error) {
            *error = [self getError];
        }
        errorindicator = nil;
        retval = nil;
    }
    pc = savedpc;
    stacktop = savedsp;
    context = savedcontext;
    UNLOCKMP;
    return retval;
}

- (BOOL)isCallable:(NSObject *)object {
    return [self builtin_callable:object];
}

@end

@implementation MiniPythonContext {
    MiniPythonContext *parent;
    NSMutableDictionary *variables;
    NSMutableSet *globals;
}


- (id)initWithParent:(MiniPythonContext *)p {
    if ((self = [super init])) {
        parent = p;
    }
    return self;
}

- (void)setValue:(NSObject *)v forName:(NSString *)n {
    MiniPythonContext *use = self;

    if (use->parent && globals && [globals containsObject:n]) {
        while (use->parent) {
            use = use->parent;
        }
    }
    if (!use->variables) {
        use->variables = [[NSMutableDictionary alloc] init];
    }
    [use->variables setObject:v forKey:n];
}

- (NSObject *)getName:(NSString *)n {
    MiniPythonContext *use = self;

    if (use->parent && globals && [globals containsObject:n]) {
        while (use->parent) {
            use = use->parent;
        }
    }

    NSObject *v = nil;
    do {
        v = (use->variables) ? [use->variables objectForKey:n] : nil;
        if (v) {return v;}
        use = use->parent;
    } while (use);
    return v;
}

- (NSObject *)getGlobalName:(NSString *)n {
    return [[self globals] objectForKey:n];
}

- (NSDictionary *)globals {
    MiniPythonContext *use = self;
    while (use->parent) {
        use = use->parent;
    }
    if (!use->variables) {
        use->variables = [[NSMutableDictionary alloc] init];
    }
    return use->variables;
}

- (NSDictionary *)locals {
    if (!variables) {
        variables = [[NSMutableDictionary alloc] init];
    }
    return variables;
}

- (MiniPythonContext *)parent {
    return parent;
}

- (BOOL)hasLocal:(NSString *)name {
    return variables && !![variables objectForKey:name];
}

- (void)markGlobal:(NSString *)name {
    if (!globals) {
        globals = [[NSMutableSet alloc] init];
    }
    [globals addObject:name];
}

- (id)copyWithZone:(NSZone *)zone {
    MiniPythonContext *new = [[[self class] allocWithZone:zone] init];
    if (new) {
        new->parent = parent;
        new->variables = variables;
        new->globals = globals;
    }
    return new;
}

- (BOOL)delName:(NSString *)name {
    // note this has to provide python semantics, not what you consider sensible!
    if (globals && [globals containsObject:name]) {return YES;}
    if (!variables || ![variables objectForKey:name]) {return NO;}
    [variables removeObjectForKey:name];
    return YES;
}

@end

@implementation MiniPythonError

+ (NSError *)withMiniPython:(MiniPython *)mp code:(NSInteger)code userInfo:(NSDictionary *)userinfo {
    NSMutableDictionary *d = [[NSMutableDictionary alloc] init];
    [d addEntriesFromDictionary:[mp stateForError]];
    if (userinfo) {
        [d addEntriesFromDictionary:userinfo];
    }
    return [super errorWithDomain:MiniPythonErrorDomain
                             code:code
                         userInfo:d];
}

- (NSString *)description {
    NSMutableString *res = [[NSMutableString alloc] init];
    NSDictionary *ue = [self userInfo];

    switch ((enum MiniPythonErrorCode) [self code]) {
        case MiniPythonOutOfMemory:
            [res appendString:@"Out of memory:"];
            break;
        case MiniPythonNeedsClear:
            [res appendString:@"Needs clear:"];
            break;
        case MiniPythonEndOfStreamError:
            [res appendString:@"Unexpected end of file"];
            break;
        case MiniPythonStreamError:
            [res appendString:@"StreamError: error reading code stream"];
            break;
        case MiniPythonUnknownVersionError:
            [res appendString:@"UnknownVersionError: unknown jmp version"];
            break;
        case MiniPythonInternalError:
            [res appendString:@"InternalError:"];
            break;
        case MiniPythonRuntimeError:
            [res appendString:@"RuntimeError:"];
            break;

        case MiniPythonTypeError:
            [res appendString:@"TypeError:"];
            if ([ue objectForKey:@"got"]) {
                if ([ue objectForKey:@"returntypesig"]) {
                    [res appendFormat:@" Unknown return format \"%@\"", [ue objectForKey:@"returntypesig"]];
                } else {
                    [res appendFormat:@" Got %@ expected %@", [ue objectForKey:@"got"], [ue objectForKey:@"expected"]];
                    if ([ue objectForKey:@"arg"]) {
                        [res appendFormat:@" (argument #%@", [ue objectForKey:@"arg"]];
                        if ([ue objectForKey:@"typesig"]) {
                            [res appendFormat:@" with signature \"%@\"", [ue objectForKey:@"typesig"]];
                        }
                        [res appendString:@")"];
                    }
                }
            }
            if ([ue objectForKey:@"op"]) {
                [res appendFormat:@"can't perform %@ on %@ and %@", [ue objectForKey:@"op"],
                                  [MiniPython toPyTypeString:[ue objectForKey:@"left"]],
                                  [MiniPython toPyTypeString:[ue objectForKey:@"right"]]];
            }
            break;
        case MiniPythonArithmeticError:
            [res appendString:@"ArithmeticException:"];
            break;
        case MiniPythonAssertionError:
            [res appendString:@"AssertionError:"];
            break;
        case MiniPythonNameError:
            [res appendString:@"NameError:"];
            break;
        case MiniPythonGeneralError:
            [res appendString:@"GeneralError:"];
            break;
        case MiniPythonIndexError:
            [res appendString:@"IndexError:"];
            break;
        case MiniPythonKeyError:
            [res appendString:@"KeyError:"];
            break;
        case MiniPythonAttributeError:
            [res appendString:@"AttributeError:"];
            break;
        case MiniPythonSyntaxError:
            [res appendString:@"SyntaxError:"];
            break;
        case MiniPythonValueError:
            [res appendString:@"ValueError:"];
            break;
    }

    if (![res length]) {
        return [@"Unhandled stringification of " stringByAppendingString:[super description]];
    }

    if ([ue objectForKey:@"reason"]) {
        [res appendFormat:@" %@", [ue objectForKey:@"reason"]];
    }

    if ([ue objectForKey:@"currentmethod"]) {
        [res appendFormat:@" in call to %@()", [ue objectForKey:@"currentmethod"]];
    }

    // line number and pc
    if ([ue objectForKey:@"pc"]) {
        [res appendFormat:@"\npc = %d", [[ue objectForKey:@"pc"] intValue]];
        if ([ue objectForKey:@"lineno"]) {
            [res appendFormat:@" line = %d", [[ue objectForKey:@"lineno"] intValue]];
        }
    }

    return res;
}
@end

@implementation MiniPythonMethod {
    int pc;
    MiniPythonContext *context;
    NSString *name;
    NSObject *instance;
}

- (BOOL)isEqual:(id)other {
    if ([other isMemberOfClass:[self class]]) {
        MiniPythonMethod *o = other;
        return pc == o->pc && instance == o->instance;
    }
    return NO;
}

- (NSUInteger)hash {
    return 0;
}

- (NSObject *)initWithPC:(int)pc_ context:(MiniPythonContext *)context_ {
    if ((self = [super init])) {
        pc = pc_;
        context = context_;
    }
    return self;
}

- (NSString *)description {
    return [NSString stringWithFormat:@"<%@method%@%@%@%@>",
                                      instance ? @"bound " : @"",
                                      name ? @" " : @"",
                                      name ? name : @"",
                                      instance ? @" of id " : @"",
                                      instance ? [NSNumber numberWithInt:(int) instance] : @""];
}

- (NSObject *)instance {
    return instance;
}

- (void)setName:(NSString *)name_ {
    if (!name) {
        name = name_;
    }
}

- (void)setInstance:(NSObject *)instance_ {
    if (!instance) {
        instance = instance_;
    }
}

- (int)pc {
    return pc;
}

- (MiniPythonContext *)context {
    return context;
}

- (id)copyWithZone:(NSZone *)zone {
    MiniPythonMethod *new = [[[self class] allocWithZone:zone] init];
    if (new) {
        new->pc = pc;
        new->context = context;
        new->name = name;
        new->instance = instance;
    }
    return new;
}
@end


@implementation MiniPythonNativeMethod {
    MiniPython *__weak mp;
    NSString *name;
    NSObject *object;
    NSObject *instance;
    // We cache the most recently used invocation.  There can be
    // multiple methods of the same name but taking different numbers of
    // args
    NSInvocation *invocation;
    NSUInteger nargsininvocation;
}

- (BOOL)hasInstance {
    return !!instance;
}

- (BOOL)isEqual:(id)other {
    if ([other isMemberOfClass:[self class]]) {
        MiniPythonNativeMethod *o = other;
        return mp == o->mp && object == o->object && instance == o->instance;
    }
    return NO;
}

- (NSUInteger)hash {
    return 1;
}

- (id)copyWithZone:(NSZone *)zone {
    MiniPythonNativeMethod *new = [[[self class] allocWithZone:zone] init];
    if (new) {
        new->mp = mp;
        new->name = name;
        new->object = object;
        new->instance = instance;
    }
    return new;
}


- (NSObject *)init:(MiniPython *)mp_ name:(NSString *)name_ target:(NSObject *)object_ {
    return [self init:mp_ name:name_ target:object_ instance:nil];
}

- (NSObject *)init:(MiniPython *)mp_ name:(NSString *)name_ target:(NSObject *)object_ instance:(NSObject *)instance_ {
    if ((self = [super init])) {
        mp = mp_;
        name = name_;
        object = object_;
        instance = instance_;
    }
    return self;
}

- (NSString *)description {
    return [NSString stringWithFormat:@"<%@method %@%@%@>",
                                      instance ? @"bound " : @"",
                                      name,
                                      instance ? @" of id " : @"",
                                      instance ? [NSNumber numberWithInt:(int) instance] : @""];
}

- (void)wrongNumberOfArguments:(NSUInteger)provided {
    NSMutableString *res = [NSMutableString stringWithFormat:@"Incorrect number of arguments supplied. Given %d, expected",
                                                             (int) provided];

    const char *prefix;
    if (instance) {
        prefix = "instance_";
    } else if (mp == object) {
        prefix = "builtin_";
    } else {prefix = "";}
    size_t prefixlen = strlen(prefix);

    Method *methods = class_copyMethodList([object class], NULL);
    Method *m = methods;

    const char *methname = [name UTF8String];
    size_t methnamelen = strlen(methname);

    BOOL first = YES;

    for (; *m; m++) {
        SEL sel = method_getName(*m);
        if (prefixlen == 0 || strncmp(sel_getName(sel), prefix, prefixlen) == 0) {
            const char *curname = sel_getName(sel) + prefixlen;
            if (strncmp(curname, methname, methnamelen)) {continue;}
            curname += methnamelen;
            if (!*curname) {
                // zero args
                if (first) {
                    first = NO;
                } else {[res appendString:@"or"];}
                [res appendString:@" zero "];
                continue;
            }
            // right prefix but wrong method
            if (*curname != ':') {continue;}
            int nargs = 0;
            while (*curname == ':') {
                nargs++;
                curname++;
            }
            if (*curname) {continue;}
            if (first) {
                first = NO;
            } else {[res appendString:@"or"];}
            [res appendFormat:@" %d ", nargs - !!instance];
            continue;
        }
    }
    [mp setNSError:[MiniPythonError withMiniPython:mp
                                              code:MiniPythonTypeError
                                          userInfo:@{@"reason" : res}]];
}

- (NSObject *)call:(NSArray *)args {
    // This adds one if we are supplying an instance argument later as
    // all args have to be shifted to leave space for it
#define INST(x) ((x)+(instance!=nil))
    if (!invocation || INST([args count]) != nargsininvocation) {
        NSMutableString *selname;
        if (instance) {
            selname = [NSMutableString stringWithString:@"instance_"];
            [selname appendString:name];
        } else if (object == mp) {
            selname = [NSMutableString stringWithString:@"builtin_"];
            [selname appendString:name];
        }
        else {
            selname = [NSMutableString stringWithString:name];
        }
        for (unsigned i = 0; i < INST([args count]); i++) {
            [selname appendString:@":"];
        }
        SEL sel = NSSelectorFromString(selname);
        if (![object respondsToSelector:sel]) {
            [self wrongNumberOfArguments:[args count]];
            return NULL;
        }
        invocation = [NSInvocation invocationWithMethodSignature:[object methodSignatureForSelector:sel]];
        [invocation setSelector:sel];
        [invocation setTarget:object];
        nargsininvocation = INST([args count]);
    }

    // check/set parameters
    for (NSUInteger i = 0; i < [args count]; i++) {
        NSObject *v = [args objectAtIndex:i];
        const char *type = [[invocation methodSignature] getArgumentTypeAtIndex:2 + INST(i)];
        if (strcmp(type, "i") == 0) {
            int ival;
            if (!ISINT(v)) {
                [mp typeError:v expected:@"int" details:@{@"method" : name, @"arg" : [NSNumber numberWithInt:(int) i + 1]}];
                return NULL;
            }
            ival = [N(v) intValue];
            [invocation setArgument:&ival atIndex:INST((NSInteger) i + 2)];
        } else if (strcmp(type, "c") == 0) {
            BOOL bval;
            if (!ISBOOL(v)) {
                [mp typeError:v expected:@"bool" details:@{@"method" : name, @"arg" : [NSNumber numberWithInt:(int) i + 1]}];
                return NULL;
            }
            bval = [N(v) boolValue];
            [invocation setArgument:&bval atIndex:INST((NSInteger) i + 2)];
        } else if (strcmp(type, "@") == 0) {
            // always works but we pass nil instead of NSNull
            if (v == [NSNull null]) {v = nil;}
            [invocation setArgument:&v atIndex:INST((NSInteger) i + 2)];
        } else {
            [mp typeError:v expected:@"supported type" details:@{@"method" : name, @"arg" : [NSNumber numberWithInt:(int) i + 1], @"typesig" : [NSString stringWithUTF8String:type]}];
            return NULL;
        }
    }
    if (instance) {[invocation setArgument:&instance atIndex:2];}

    // make the call
    [invocation invoke];

    // check error flag
    if ([mp getError]) {
        return NULL;
    }

    // now deal with return
    const char *returntype = [[invocation methodSignature] methodReturnType];
    if (strcmp(returntype, "i") == 0) {
        int ival;
        [invocation getReturnValue:&ival];
        return [NSNumber numberWithInt:ival];
    } else if (strcmp(returntype, "c") == 0) {
        BOOL bval;
        [invocation getReturnValue:&bval];
        return [NSNumber numberWithBool:bval];
    } else if (strcmp(returntype, "@") == 0) {
        /*
      The return value from the invocation is not retained so
      reference count ends up wrong.  We need to ensure it is retained
      but can't just call retain due to ARC, hence the following.

      http://stackoverflow.com/a/11874258/463462

      This solution also works: http://stackoverflow.com/a/11569236/463462
    */
        __unsafe_unretained NSObject *result;
        [invocation getReturnValue:&result];
        return result ? result : [NSNull null];
    } else if (strcmp(returntype, "v") == 0) {
        return [NSNull null];
    } else {
        [mp typeError:self expected:@"known return type" details:@{@"method" : name, @"returntypesig" : [NSString stringWithUTF8String:returntype]}];
        return NULL;
    }
}

@end

@implementation MiniPythonModule {
    NSObject *delegate;
    NSString *modname;
    NSSet *available;
}

- (id)initWithDelegate:(NSObject *)delegate_  name:(NSString *)name_ {
    if ((self = [super init])) {
        delegate = delegate_;
        modname = name_;

        available = [[NSMutableSet alloc] init];
        Method *methods = class_copyMethodList([delegate class], NULL);
        Method *m = methods;
        while (*m) {
            SEL sel = method_getName(*m);
            const char *name = sel_getName(sel);
            unsigned i;
            for (i = 0; name[i] && name[i] != ':'; i++) {}
            NSString *funcname = [[NSString alloc] initWithBytes:name length:i encoding:NSASCIIStringEncoding];
            [(NSMutableSet *) available addObject:funcname];
            m++;
        }
        free(methods);
    }
    return self;
}

- (NSString *)description {
    return [NSString stringWithFormat:@"<module %@>", modname];
}

- (BOOL)hasMethod:(NSString *)name {
    return [available containsObject:name];
}

- (NSObject *)delegate {
    return delegate;
}

- (BOOL)isEqual:(id)other {
    if ([other isMemberOfClass:[self class]]) {
        MiniPythonModule *o = other;
        return delegate == o->delegate && [modname isEqual:o->modname];
    }
    return NO;
}

- (NSUInteger)hash {
    return 2;
}

- (id)copyWithZone:(NSZone *)zone {
    MiniPythonModule *new = [[[self class] allocWithZone:zone] init];
    if (new) {
        new->delegate = delegate;
        new->modname = modname;
        new->available = available;
    }
    return new;
}

@end
