#> AssertionError:.*message.*
# This is to ensure assertions are working
assert False, "a message"
#> TypeError
[] * True
#> TypeError:.*bool.*list.*
False*[False]
#> NameError:.*varname.*
return 3+varname-7
#> TypeError
"fdsf" * []
#> TypeError
[] * "fdsfds"
#> TypeError
None + 3
#> TypeError
3 + None
#> TypeError:.*bool.*
3 + True
#> TypeError:.*list.*
[]+4
#> TypeError:.*dict.*dict.*
{}+{}
#> TypeError:.*bool.*
3-True
#> TypeError:.*dict.*
{}-5
#> TypeError:.*dict.*
3/{}
#> TypeError:.*bool.*
True/3
#> ArithmeticException
1/0
#> TypeError:
True % False
#> TypeError
3 % True
#> TypeError
{} % 7
#> TypeError
"%{" % []
#> TypeError
"324324" % 432
#> AttributeError
(3).foo
#> TypeError
[1][True]
#> IndexError
[1][-2]
#> IndexError
[1][1]
#> KeyError
{}[1]
#> TypeError
"fdsfsda"[[]]
#> IndexError
"dsgdf"[1000]
#> IndexError
"fdsfsd"[-17]
#> TypeError:.*subscriptable.*
3423[3]
#> TypeError
21312[3:{}]
#> TypeError
21312[{}:{}]
#> TypeError.*slice.*
21312[:{}]
#> TypeError.*slice.*
21312[{}:]
#> TypeError.*slice.*
{}[1:2]
#> TypeError
[]["ttt"]=3
#> IndexError.*range.*
[1,2,3][-213]=4
#> IndexError.*range.*
[1,2,3][213]=4
#> TypeError.*item assignment.*
f=True
f[3]=3
#> TypeError
del []["fdsfsd"]
#> TypeError
f=True
del f[3]
#> IndexError
del [1,2,3][-4343]
#> IndexError
del [1,2,3][4343]
#> KeyError
del {1:2}["ff"]
#> TypeError
del [1,2,3][1:{}]
#> TypeError
del [1,2,3][{}:]
#> TypeError
f=True
del f[1:2]
#> TypeError
# python does support this, we don't
del [][:2]
#> TypeError
# see above
del [1,2,3][2:]

#> NameError
name=3
assert 3+name==6
del name
assert 3+name==77
#> NameError
del foo
#> NameError
def meth():
    foo=3
    assert foo==3
    del foo
    assert foo==88
meth()

#> TypeError
"sdffds" in 3
#> TypeError
3 in 3
#> TypeError
-True
#> TypeError
+True

#> TypeError
for x in 3: pass
#> AssertionError
assert False, None # for coverage

#. foo.*\n
print "foobar"
#. .*foobar[^\n]$
print "foobar",
#. .*foo bar\n
print "foo","bar"

#> SyntaxError

global foo # for coverage
def meth():
    foo=3
    global foo

meth()

#> TypeError
d={}
d()

#> TypeError.*takes.*arg.*
def meth(a,b,c):
    pass

meth(1)
#> SyntaxError
return 3
#> RuntimeError
def meth():
    return 3+meth()
meth()

### Exercise the toPyTypeString code
#> TypeError.*bool.*
test1.takesAll(3, 0, 0, 0, 0, 0, 0)
#> TypeError.*bool.*
test1.takesAll(True, 3, 0, 0, 0, 0, 0)
#> TypeError.*dict.*
test1.takesAll(False, True, 4, 0, 0, 0, 0)
#> TypeError.*list.*
test1.takesAll(False, True, {}, {}, 0, 0, 0)
#> TypeError.*int.*
test1.takesAll(False, True, {}, [], "fff", 0, 0)
#> TypeError.*int.*
test1.takesAll(False, True, {}, [], 3, "", 0)
#> TypeError.*Test1.*
test1.takesAll(False, True, {}, [], 3, 3, "")
#> TypeError.*(Test1|takesAll).*
test1.takesAll(test1.retSelf())

#> ValueError
int("fred")
#> TypeError
int({})
#> TypeError
len(True)
#> TypeError
"fdsfdsa"[3]="5"

#> ValueError
range(0,10,0)

#> TypeError
range(1,2,3,4,5,6)

#> .*(java.lang.NullPointerException|NoneType).*
"fdasfdsa".endswith(None)

#> TypeError
"".join(["sfds", "sas", 1])

#> TypeError.*(too many|incorrect number).*
"".split(1,2,3,4,5)

#> TypeError
"".split("", "foo")

#> TypeError
"".split(1,2)

#> ValueError
"afdsfads".split("")

#> .*(java.lang.NullPointerException|NoneType).*
[].extend(None)

#> TypeError
[].extend()

#> IndexError
[].pop()

#> TypeError
[].sort(1,2,3,4,5,6)

#> TypeError
[].sort(None, None, 1)

#> TypeError.*callable.*
[].sort(None, True)

#> TypeError.*callable.*
[].sort(True)

#> AssertionError
def meth(a,b):
    assert False
[1,2].sort(meth)

#> AttributeError
test1.privatemethod

#> TypeError
notcallable=7
test1.call("notcallable")

#> NameError
test1.call("doesn't exist")

#> TypeError
apply(None, [])

#> (RuntimeError|.*stack overflow).*
x=test1.call
apply(test1.call, ["x"]*65536)

#> TypeError
test1.vacall(3)
#> TypeError
test1.vacall("foo", 4)
#> TypeError.*(takes.*args|number of arguments).*
test1.vacall()

#> .*Batman.*
test1.signalBatman()

#> .*Batman.*
test2.signalBatman()

#> TypeError
x=3
x.foo=4
#> TypeError
range(10)[{}:]
#> TypeError
range(10)[3:""]
#>TypeError
"%" % []
#>TypeError
"%d" % ("foo",)
#>TypeError
"% 5" % ("foo",)
#>TypeError
"%Q" % ("abc",)
#>TypeError
filter(3, [1,2])
#>TypeError
filter(lambda :1, "aaa")
#>TypeError
map(3, [])
#>TypeError
map(lambda :3, 3)

#.\n
# these are needed because of no varargs in objc
print()
#.1\n
print(1)
#.1 2\n
print(1,2)
#.1 2 3\n
print(1,2,3)
#.1 2 3 4\n
print(1,2,3,4)
#.1 2 3 4 5\n
print(1,2,3,4,5)
#.1 2 3 4 5 6\n
print(1,2,3,4,5,6)
#.1 2 3 4 5 6 7\n
print(1,2,3,4,5,6,7)
#.1 2 3 4 5 6 7 8\n
print(1,2,3,4,5,6,7,8)

#>TypeError
locals(3)

#>TypeError.* or .* (objc)
test1.foo(1,2,3,4)

#>TypeError.*signature "f".* (objc)
test1.takesFloat(1)

#>TypeError.*return format "f".* (objc)
test1.returnsFloat()
