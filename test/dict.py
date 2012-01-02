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
assert one<two
assert one<=two
assert one!=two
assert (one>=two)==False
assert (one>two)==False
assert (one==two)==False

assert ("a" in empty) ==False
assert (() in empty) ==False
assert (() in one)==False

assert "a" not in empty
assert () not in empty
assert () not in one

assert 1 in one and 3 in two
assert one[1]==two[1]

assert len(two)==2
