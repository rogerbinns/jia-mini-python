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


