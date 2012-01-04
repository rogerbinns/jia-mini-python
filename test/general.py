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

assert "%d" % [3]=="3"

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
