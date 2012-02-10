# Return statements inside for loops

def level3(call):
    for i in range(7):
        for i in range(7):
            for i in range(7):
                if call==3:
                    return 3
    return 0

def level2(call):
    for i in range(7):
        for i in range(7):
            if call==2:
                return 2
        return level3(call)

def level1(call):
    for i in range(7):
        if call==1:
            return 1
        return level2(call)

assert level1(1)==1
assert level1(2)==2
assert level1(3)==3
assert level1(4)==0
