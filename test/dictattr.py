# dictionary/attribute type stuff

# issues 6 & 7

t={"a": 1}

assert t["a"]==t.a
t.b=2
assert t["a"]+t["b"]==3
assert t.a+t.b==3
