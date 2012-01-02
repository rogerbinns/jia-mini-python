#!/usr/bin/env python

# Generate tests file 

testvals=[
    "a string",
    6,
    -2,
    False, 
    True,
    None,
    [1,2,3],
    ["one", "two", "three"],
    ["one", "three", "too"],
    {},
    {(1,2,3): []},
    {(1,"t","3"): []},
    [True, False],
    [False, True],
    {1: "one"},
    {1: "pne", 0: "zero"}
]

testops=[
    "+", "-", "*", "/", "and", "or", "<", ">", "==", "<=", ">=", "!="
    ]

print "# Note that Python 2 gives different answers when the types don't match"
print "# and that Python 3 gives exceptions"

for left in testvals:
    for op in testops:
        for right in testvals:
            toeval=code="%r %s %r" % (left, op, right)
            try:
                if op in ("+", "-", "*", "/") and (isinstance(right, bool) or isinstance(left, bool)):
                    raise Exception("bools are not ints")
                if ("<" in op or ">" in op) and type(left)!=type(right):
                    toeval="%r %s %r" % (type(left).__name__, op, type(right).__name__)
                res=eval(toeval)
                print "assert (", code, ")" + ( ("=="+ repr(res)) if res is not True else "")
            except:
                pass
