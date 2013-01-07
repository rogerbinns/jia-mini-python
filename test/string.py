assert 3*"abc"=="abc"*3

assert "" in ""
assert "" in "asdas"

assert "abc" % () == "abc"
assert "abc%%d" % () == "abc%d"
assert "%%" % [] == "%"

assert "%-10s" % ('ab',) == 'ab        '
assert "%10s" % ('ab',) == '        ab'
assert "%d" % (3,) == "3"
assert "%+d" % (3,) == "+3"
assert "%05d" % (3,) == "00003"
assert "% 5d" % (3,) == "    3"
assert "%x" % (15,) == "f"
assert "%X" % (15,) == "F"

assert "%10s" % ('abcdefghijklmnop',) == 'abcdefghijklmnop'
