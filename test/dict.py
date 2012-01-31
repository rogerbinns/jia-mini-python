empty={}
assert len(empty)==0
assert str(empty)=="{}"

order=0

def next():
    global order
    res=order
    order=order+1
    return res

# note that Python evaluates value before key
one={next(): next()}
assert one=={1:0}

order=0
two={next(): next(), next(): next()}
assert two=={1:0, 3:2}

# Python 3 doesn't allow ordering of dictionaries
if one<two:
    assert two>one
else:
    assert one>two
assert ("a" in empty) ==False
assert (() in empty) ==False
assert (() in one)==False

assert "a" not in empty
assert () not in empty
assert () not in one

assert 1 in one and 3 in two
assert one[1]==two[1]

assert len(two)==2

# check assignment & nulls
for i in "fred", 22, None, [1,"two"]:
    two[i]=None
    assert len(two)==3
    assert two[i]==None
    two[i]=1
    assert two[i]+1==2

    assert i in two
    del two[i]
    assert len(two)==2
    assert i not in two

# update
two.update(one)
two.update(empty)
two.update({None: "x", "423432": 43324, None: "y", "fred": next, next: 77})
assert two[None]=="y"
assert two["fred"]==next
assert two[next]+1==78

# iterators
another={}
for i in two:
    another[i]=two[i]

assert another==two

# string

stringed=str(two)
for k in another:
    assert str(k) in stringed
    assert str(another[k]) in stringed

# a dict that can't do equals well
d=test1.badeqDict()
d2=test2.badeqDict()

for k in another:
    d[k]=another[k]
    d2[k]=another[k]

assert d!=d2

# get
d={}
assert d.get("foo", 3)==3
d["foo"]=4
assert d.get("foo", 3)==4
d[None]=5
assert d.get(None, 3)==5
