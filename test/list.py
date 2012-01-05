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

assert 3 in range(10)
assert 3 not in range(6,10)

assert filter(lambda x: x%2, range(10))==[1,3,5,7,9]

assert range(10).index(6)==6
assert range(10).index(70)==-1
assert range(10).index(None)==-1

assert len([])==0
assert len(range(100))==100

assert range(0)==[]
assert range(0,-1)==[]
assert range(3,5)==[3,4]
assert range(5, 0, -1)==[5,4,3,2,1]
assert range(5, 0, -2)==[5,3,1]
assert range(10, 20, -2)==[]

l=[1]
l.extend(range(3))
assert l==[1,0,1,2]

assert l.pop()==2
assert l==[1,0,1]
l.pop()
l.reverse()
assert l==[0,1]
l.pop()
l.reverse()
assert l==[0]
l.pop()
l.reverse()
assert l==[]

l=range(5)
l.sort()
assert l==range(5)
l.sort(None, None, True)
assert l==range(4,-1,-1)
l.sort(None, None, None)
assert l==range(5)

l=[{1: 2}, {1: 1}, {1: 3}]
l.sort(None, lambda x: x[1])
assert l==[{1: 1}, {1: 2}, {1: 3}]
l.sort(cmp, None, True)
assert l==[{1: 3}, {1: 2}, {1: 1}]
