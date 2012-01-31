assert 3+4<=7
assert 1+2*3==7

assert 3-4==-1
assert -1--2==1

assert 6/2==3
# see source and url for why this isn't zero
assert -2/6==-1

assert 65535+2==65537

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

assert map(type, [None, True, {}, [], 3, "", meth, test1.retSelf, test1, [].sort])  \
                  ==["NoneType", "bool", "dict", "list", "int", "str", "method", "modulemethod", "module", "instancemethod"]

def meth(a,b):
    return a+b

assert apply(meth, [3,4])==7

assert bool("")==False
assert bool("dfds")==True

assert (bool(0), bool(7)) == (False, True)

assert (bool([]), bool([0])) == (False, True)

assert (bool({}), bool({0:0})) == (False, True)

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
assert id(test1.retSelf)!=id(test1.retSelf)

assert int(3)==3
assert int(2+2)==4
assert int(True)==1
assert int(False)==0
assert int("7")==7
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
assert "abc.*abc.*".split(".*")==["abc", "abc"]
assert "a1a2a3a4".split("a", 2)==['', '1', '2a3a4']

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
