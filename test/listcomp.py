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
