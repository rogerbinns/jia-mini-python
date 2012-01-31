# dictionary/attribute type stuff

# issue 6 

t={"a": 1}

assert t["a"]==t.a
t.b=2
assert t["a"]+t["b"]==3
assert t.a+t.b==3

# issue 7 - pseudo object orientation

foo_num=0
def Foo():
   def meth1(self, o):
       assert self is theinstance
       assert o==3

   def instance(self):
       return self.num

   res= {
       "num": foo_num,
       "meth": meth1,
       "instance": instance
       }
   global foo_num
   foo_num=foo_num+1
   return res

theinstance=Foo()
theinstance.meth(3)

assert "bound" in str(theinstance.meth)
assert "bound" not in str(theinstance["meth"])

# check self follows around
inst0=theinstance
inst1=Foo()

assert str(inst0.meth)!=str(inst1.meth)
assert inst0.instance()==0
assert inst1.instance()==1

# ensure self remains bound to method
inst0.xxx=inst1.instance

assert inst0.xxx()==1
