assert []+[]==[]
assert [1]+[]==[1]
assert [1]+[2]==[1,2]
assert [1]+[2]!=[1, "two"]
assert [1][0]==1
assert [1][-1]==1

assert [1][:1]==[1]
assert [1][1:]==[]
assert [1][-1:]==[1]
assert [1,2,3][-3:-1]==[1,2]
assert [1,2,3][-3:-2222]==[]
assert [1,2,3][-432432:]==[1,2,3]
assert [1,2,3][1:4243242]==[2,3]

l=[0,1,2,3]
l[3]=3
assert l==[0,1,2,3]
l[3]=4
assert l==[0,1,2,4]
l[-1]=5
assert l==[0,1,2,5]

del l[0]
assert l==[1,2,5]

del l[1]
assert l==[1,5]

l=range(10)
del l[1:9]
assert l==[0,9]

del l[-432423:432423]
assert l==[]

l=range(5)

del l[-4:-2]
assert l==[0,3,4]

l=range(5)
del l[2:2]
assert l==range(5)
del l[4:1]
assert l==range(5)
