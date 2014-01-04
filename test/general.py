assert 3+4<=7
assert 1+2*3==7

assert 3-4==-1
assert -1--2==1

assert 6/2==3
# see source and url for why this isn't zero
assert -2/6==-1

assert 65535+2==65537
assert 256*256-1==65535

# http://kqueue.org/blog/2012/12/31/idiv-dos/
assert -2147483648 / -1 == -2147483648

assert 6%3==0
assert 6%-3==0

assert 1%2==1
assert 1%-2==-1
assert (-11)%2==1
assert (-11)%-2==-1

assert "%d" % (3,)=="3"

assert test1.retNone()==None

assert "abc"[0]=="a"
assert "abc"[-1]=="c"

assert "abc"[:3]=="abc"
assert "abc"[1:]=="bc"
assert "abc"[-3:-1]=="ab"
assert "abc"[:89078]=="abc"
assert "abc"[43223:]==""
assert "abc"[-3:-32321]==""
assert "abc"[-333:]=="abc"

# global names are not deleted
toplevel=6
def meth():
    assert toplevel==6
    global toplevel
    assert toplevel==6
    assert toplevel==6
    del toplevel
    foo=3
    del foo
meth()
assert toplevel==6

# make sure all types can end up as dict keys
x={}
thelist=[]
x.update({
        None: 1,
        True: 2,
        {}: 3,
        []: 4,
        3: 5,
        "": 6,
        meth: 7,
        cmp: 8,
        test1.retSelf: 9,
        test1: 10,
        thelist.sort: 11
})

assert len(x)==11
assert x[None]  ==1
assert x[True]  ==2
assert x[{}]    ==3
assert x[[]]    ==4
assert x[3]     ==5
assert x[""]    ==6
assert x[meth]  ==7
assert x[cmp]   ==8
assert x[test1] ==10
assert x[test1.retSelf] ==9
assert x[thelist.sort]==11
assert [].sort not in x # different instance

#  multi globals
a=4
b=4
def meth():
    global a,b
    a=5
    b=6
meth()
assert a+b==11

assert -(3)==-3
assert -3==0-3
assert ++++3==3

assert [3,4]<[3,4,5]
assert [3,4,5]>[3,4]

assert False < True

assert str(3<4)=="True"
assert str(3>4)=="False"
assert "module" in str(test1)


d={1: 2}
d["foo"]=d
assert "..." in str(d)

l=[1,2]
l.append(l)
assert "..." in str(l)


assert type(None)=="NoneType"
assert type(True)=="bool"
assert type({})=="dict"
assert type([])=="list"
assert type(3)=="int"
assert type("")=="str"
assert "method" in type(meth)
assert "modulemethod" in type(test1.retSelf)
assert "module" in type(test1)
assert "instancemethod" in type([].sort)

def meth(a,b):
    return a+b

assert apply(meth, [3,4])==7

assert bool("")==False
assert bool("dfds")==True

assert (bool(0), bool(7)) == (False, True)

assert (bool([]), bool([0])) == (False, True)

assert (bool({}), bool({0:0})) == (False, True)

assert not {} == True
assert not [] == True

# Check or and and short circuiting

def errmeth():  # should not be called
    a=0
    1/a

if False and errmeth():
    pass

if True or errmeth():
    pass

if {}=={} or not errmeth():
    pass

if not {} or not errmeth():
    pass

assert callable(None)==False
assert callable(meth)==True
assert callable(test1.retSelf())==False
assert callable(test1.retSelf)==True

def meth2(): pass
assert meth==meth
assert meth!=meth2
assert test1.retSelf==test1.retSelf
assert test1.retSelf!=test1.retSelf()
assert test1.retSelf!=meth
assert test1.retSelf()!=3
assert test1.retSelf!=test2.retSelf
assert test1.retSelf()!=test2.retSelf()

l=[]
assert l.index==l.index
assert l.index!=[3].index
assert l.index!="".replace

assert id(meth)==id(meth)

assert int(3)==3
assert int(2+2)==4
assert int(True)==1
assert int(False)==0
assert int("7")==7
assert int("0")==0
assert int("-2345")==-2345

assert len("")==0
assert len("ddd"*3)==9

assert "abcdef".endswith("ef")
assert "abcdef".endswith("eff")==False
assert "".endswith("")
assert "sfdsfsd".endswith("")

assert "abcdef".startswith("ab")
assert "abcdef".startswith("eff")==False
assert "".startswith("")
assert "sfdsfsd".startswith("")


assert "".join(["a", "b", "c"])=="abc"
assert "1".join(["a", "b", "c"])=="a1b1c"
assert "fdsfsd".join([])==""

assert "ABC".lower()=="abc"
assert "abc".lower()=="abc"
assert "".lower()==""

assert "ABC".upper()=="ABC"
assert "abc".upper()=="ABC"
assert "".upper()==""

assert "sdfs1ffds".replace("1", "one")=="sdfsoneffds"
assert "aaaaa".replace("a", "aa")=="a"*10
assert "12345".replace("", "a")=="a1a2a3a4a5"
assert "aeiouaeiou".replace("iou", "OU")=="aeOUaeOU"

assert "fsdafdsaf".split("343")==["fsdafdsaf"]
assert "edward    is a   \nvampire   ".split()==["edward", "is", "a", "vampire"]
assert "abc.*abc.*".split(".*")==["abc", "abc", ""]
assert "abc.*abc.*".split("abc", 0)==["abc.*abc.*"]
assert "abc.*abc.*".split("abc", 1)==["", ".*abc.*"]
assert "abc.*abc.*".split("abc", 2)==["", ".*", ".*"]
assert "a1a2a3a4".split("a", 2)==['', '1', '2a3a4']
assert "1a2a3a4a".split("a", -2)==['1', '2', '3', '4', '']

assert "".strip()==""
assert "     ".strip()==""
assert "  a   ".strip()=="a"

assert test1.call("id", 7)==id(7)

used=False
def add(a,b):
    global used
    used=True
    return a+b

assert test1.add(3,4)==7
assert used

# no errors but does make sure classcastexception is handled in comparators
test1.retSelf()<test2.retSelf()
[test1.retSelf(), 2].sort()

assert None==None

# is

x={"y":3}
assert x is x
assert x is not 3

assert True is True
assert False is False
assert None is None
assert {} is not {}
assert [] is not []

# globals/locals functions - these may be removed
assert "x" in globals()
assert globals().x=={"y": 3}

def foo(opop):
    assert "opop" in locals()
    assert len(locals())==1
    assert "x" not in locals()
    x=7
    assert globals().x!=locals().x
    assert len(locals())==2

foo(1)


assert bool(test1.retSelf())
assert not bool(None)

# make sure None/null/nil is handled correctly as the underly
# list/map/array may get upset
assert len([None, test1.returnNone(), 3])==3
assert len({
        None: 3,
        test1.returnNone(): 4,
        3: None,
        4: test1.returnNone()})==3

assert test1.toPyReprString("True")=='"True"'
assert test1.toPyReprString(True)=='True'
assert test1.toPyReprString("a\n\t\"")==r'"a\n\t\""'
assert test1.toPyReprString("\\")==r'"\\"'
