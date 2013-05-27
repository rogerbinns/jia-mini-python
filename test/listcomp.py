# These don't add any new opcodes and are no different than writing
# out for loops with ifs and list appends.  But they do exercise lists
# and iteration nicely

# this ensures that junk left on the stack causes an error
for i in range(1500):

    assert [y+1 for y in range(4)] == [ 1,2,3,4]
    assert [y for y in range(10) if y%2==0] == [0, 2, 4, 6, 8]

    assert [x for x in range(3) if x==2] == [2]
    assert [[x,y] for x in range(3) for y in range(3) if x==2] == [[2, 0], [2, 1], [2, 2]]
    assert [[x,y,z] for x in range(3) for y in range(3) if x==2 for z in range(3)] == [[2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0], [2, 2, 1], [2, 2, 2]]

    assert [[x for x in range(2)] for x in range(3)] == [[0, 1], [0, 1], [0, 1]]

# verify name scoping
x=[[x for x in range(2)] for x in range(3)]
assert x==[[0, 1], [0, 1], [0, 1]]
assert x==[[x for x in range(2)] for x in range(3)]

func=lambda: [x for x in range(3)]
assert [func() for x in range(3)]==[[0,1,2], [0,1,2], [0,1,2]]

# multiple ifs
x=[i for i in range(20) if i%2==0 if i%3==0 for _ in range(3)]
assert x==[0,0,0,6,6,6,12,12,12,18,18,18]

# Adapted from the python test suite - test_grammar
nums = [1, 2, 3, 4, 5]
strs = ["Apple", "Banana", "Coconut"]
spcs = ["  Apple", " Banana ", "Coco  nut  "]

assert [s.strip() for s in spcs]==['Apple', 'Banana', 'Coco  nut']
assert [3 * x for x in nums]==[3, 6, 9, 12, 15]
assert [x for x in nums if x > 2]==[3, 4, 5]
assert [(i, s) for i in nums for s in strs]== (
    [(1, 'Apple'), (1, 'Banana'), (1, 'Coconut'),
     (2, 'Apple'), (2, 'Banana'), (2, 'Coconut'),
     (3, 'Apple'), (3, 'Banana'), (3, 'Coconut'),
     (4, 'Apple'), (4, 'Banana'), (4, 'Coconut'),
     (5, 'Apple'), (5, 'Banana'), (5, 'Coconut')])
assert [(i, s) for i in nums for s in [f for f in strs if "n" in f]]==(
    [(1, 'Banana'), (1, 'Coconut'), (2, 'Banana'), (2, 'Coconut'),
     (3, 'Banana'), (3, 'Coconut'), (4, 'Banana'), (4, 'Coconut'),
     (5, 'Banana'), (5, 'Coconut')])

assert [(lambda a:[a*i for i in range(a+1)])(j) for j in range(5)] == (
    [[0], [0, 1], [0, 2, 4], [0, 3, 6, 9], [0, 4, 8, 12, 16]])

# From test_iter
TRIPLETS = [(0, 0, 0), (0, 0, 1), (0, 0, 2),
            (0, 1, 0), (0, 1, 1), (0, 1, 2),
            (0, 2, 0), (0, 2, 1), (0, 2, 2),

            (1, 0, 0), (1, 0, 1), (1, 0, 2),
            (1, 1, 0), (1, 1, 1), (1, 1, 2),
            (1, 2, 0), (1, 2, 1), (1, 2, 2),

            (2, 0, 0), (2, 0, 1), (2, 0, 2),
            (2, 1, 0), (2, 1, 1), (2, 1, 2),
            (2, 2, 0), (2, 2, 1), (2, 2, 2)]

seq = range(3)
res = [(i, j, k)
       for i in seq for j in seq for k in seq]
assert res==TRIPLETS

