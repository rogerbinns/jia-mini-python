# Note that Python 2 gives different answers when the types don't match
# and that Python 3 gives exceptions
assert ( 'a string' + 'a string' )=='a stringa string'
assert ( 'a string' * 6 )=='a stringa stringa stringa stringa stringa string'
assert ( 'a string' * -2 )==''
assert ( 'a string' and 'a string' )=='a string'
assert ( 'a string' and 6 )==6
assert ( 'a string' and -2 )==-2
assert ( 'a string' and False )==False
assert ( 'a string' and True )
assert ( 'a string' and None )==None
assert ( 'a string' and [1, 2, 3] )==[1, 2, 3]
assert ( 'a string' and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( 'a string' and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( 'a string' and {} )=={}
assert ( 'a string' and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( 'a string' and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( 'a string' and [True, False] )==[True, False]
assert ( 'a string' and [False, True] )==[False, True]
assert ( 'a string' and {1: 'one'} )=={1: 'one'}
assert ( 'a string' and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( 'a string' or 'a string' )=='a string'
assert ( 'a string' or 6 )=='a string'
assert ( 'a string' or -2 )=='a string'
assert ( 'a string' or False )=='a string'
assert ( 'a string' or True )=='a string'
assert ( 'a string' or None )=='a string'
assert ( 'a string' or [1, 2, 3] )=='a string'
assert ( 'a string' or ['one', 'two', 'three'] )=='a string'
assert ( 'a string' or ['one', 'three', 'too'] )=='a string'
assert ( 'a string' or {} )=='a string'
assert ( 'a string' or {(1, 2, 3): []} )=='a string'
assert ( 'a string' or {(1, 't', '3'): []} )=='a string'
assert ( 'a string' or [True, False] )=='a string'
assert ( 'a string' or [False, True] )=='a string'
assert ( 'a string' or {1: 'one'} )=='a string'
assert ( 'a string' or {0: 'zero', 1: 'pne'} )=='a string'
assert ( 'a string' < 'a string' )==False
assert ( 'a string' < 6 )==False
assert ( 'a string' < -2 )==False
assert ( 'a string' < False )==False
assert ( 'a string' < True )==False
assert ( 'a string' < None )==False
assert ( 'a string' < [1, 2, 3] )==False
assert ( 'a string' < ['one', 'two', 'three'] )==False
assert ( 'a string' < ['one', 'three', 'too'] )==False
assert ( 'a string' < {} )==False
assert ( 'a string' < {(1, 2, 3): []} )==False
assert ( 'a string' < {(1, 't', '3'): []} )==False
assert ( 'a string' < [True, False] )==False
assert ( 'a string' < [False, True] )==False
assert ( 'a string' < {1: 'one'} )==False
assert ( 'a string' < {0: 'zero', 1: 'pne'} )==False
assert ( 'a string' > 'a string' )==False
assert ( 'a string' > 6 )
assert ( 'a string' > -2 )
assert ( 'a string' > False )
assert ( 'a string' > True )
assert ( 'a string' > None )
assert ( 'a string' > [1, 2, 3] )
assert ( 'a string' > ['one', 'two', 'three'] )
assert ( 'a string' > ['one', 'three', 'too'] )
assert ( 'a string' > {} )
assert ( 'a string' > {(1, 2, 3): []} )
assert ( 'a string' > {(1, 't', '3'): []} )
assert ( 'a string' > [True, False] )
assert ( 'a string' > [False, True] )
assert ( 'a string' > {1: 'one'} )
assert ( 'a string' > {0: 'zero', 1: 'pne'} )
assert ( 'a string' == 'a string' )
assert ( 'a string' == 6 )==False
assert ( 'a string' == -2 )==False
assert ( 'a string' == False )==False
assert ( 'a string' == True )==False
assert ( 'a string' == None )==False
assert ( 'a string' == [1, 2, 3] )==False
assert ( 'a string' == ['one', 'two', 'three'] )==False
assert ( 'a string' == ['one', 'three', 'too'] )==False
assert ( 'a string' == {} )==False
assert ( 'a string' == {(1, 2, 3): []} )==False
assert ( 'a string' == {(1, 't', '3'): []} )==False
assert ( 'a string' == [True, False] )==False
assert ( 'a string' == [False, True] )==False
assert ( 'a string' == {1: 'one'} )==False
assert ( 'a string' == {0: 'zero', 1: 'pne'} )==False
assert ( 'a string' <= 'a string' )
assert ( 'a string' <= 6 )==False
assert ( 'a string' <= -2 )==False
assert ( 'a string' <= False )==False
assert ( 'a string' <= True )==False
assert ( 'a string' <= None )==False
assert ( 'a string' <= [1, 2, 3] )==False
assert ( 'a string' <= ['one', 'two', 'three'] )==False
assert ( 'a string' <= ['one', 'three', 'too'] )==False
assert ( 'a string' <= {} )==False
assert ( 'a string' <= {(1, 2, 3): []} )==False
assert ( 'a string' <= {(1, 't', '3'): []} )==False
assert ( 'a string' <= [True, False] )==False
assert ( 'a string' <= [False, True] )==False
assert ( 'a string' <= {1: 'one'} )==False
assert ( 'a string' <= {0: 'zero', 1: 'pne'} )==False
assert ( 'a string' >= 'a string' )
assert ( 'a string' >= 6 )
assert ( 'a string' >= -2 )
assert ( 'a string' >= False )
assert ( 'a string' >= True )
assert ( 'a string' >= None )
assert ( 'a string' >= [1, 2, 3] )
assert ( 'a string' >= ['one', 'two', 'three'] )
assert ( 'a string' >= ['one', 'three', 'too'] )
assert ( 'a string' >= {} )
assert ( 'a string' >= {(1, 2, 3): []} )
assert ( 'a string' >= {(1, 't', '3'): []} )
assert ( 'a string' >= [True, False] )
assert ( 'a string' >= [False, True] )
assert ( 'a string' >= {1: 'one'} )
assert ( 'a string' >= {0: 'zero', 1: 'pne'} )
assert ( 'a string' != 'a string' )==False
assert ( 'a string' != 6 )
assert ( 'a string' != -2 )
assert ( 'a string' != False )
assert ( 'a string' != True )
assert ( 'a string' != None )
assert ( 'a string' != [1, 2, 3] )
assert ( 'a string' != ['one', 'two', 'three'] )
assert ( 'a string' != ['one', 'three', 'too'] )
assert ( 'a string' != {} )
assert ( 'a string' != {(1, 2, 3): []} )
assert ( 'a string' != {(1, 't', '3'): []} )
assert ( 'a string' != [True, False] )
assert ( 'a string' != [False, True] )
assert ( 'a string' != {1: 'one'} )
assert ( 'a string' != {0: 'zero', 1: 'pne'} )
assert ( 6 + 6 )==12
assert ( 6 + -2 )==4
assert ( 6 - 6 )==0
assert ( 6 - -2 )==8
assert ( 6 * 'a string' )=='a stringa stringa stringa stringa stringa string'
assert ( 6 * 6 )==36
assert ( 6 * -2 )==-12
assert ( 6 * [1, 2, 3] )==[1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
assert ( 6 * ['one', 'two', 'three'] )==['one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three']
assert ( 6 * ['one', 'three', 'too'] )==['one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too']
assert ( 6 * [True, False] )==[True, False, True, False, True, False, True, False, True, False, True, False]
assert ( 6 * [False, True] )==[False, True, False, True, False, True, False, True, False, True, False, True]
assert ( 6 / 6 )==1
assert ( 6 / -2 )==-3
assert ( 6 and 'a string' )=='a string'
assert ( 6 and 6 )==6
assert ( 6 and -2 )==-2
assert ( 6 and False )==False
assert ( 6 and True )
assert ( 6 and None )==None
assert ( 6 and [1, 2, 3] )==[1, 2, 3]
assert ( 6 and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( 6 and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( 6 and {} )=={}
assert ( 6 and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( 6 and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( 6 and [True, False] )==[True, False]
assert ( 6 and [False, True] )==[False, True]
assert ( 6 and {1: 'one'} )=={1: 'one'}
assert ( 6 and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( 6 or 'a string' )==6
assert ( 6 or 6 )==6
assert ( 6 or -2 )==6
assert ( 6 or False )==6
assert ( 6 or True )==6
assert ( 6 or None )==6
assert ( 6 or [1, 2, 3] )==6
assert ( 6 or ['one', 'two', 'three'] )==6
assert ( 6 or ['one', 'three', 'too'] )==6
assert ( 6 or {} )==6
assert ( 6 or {(1, 2, 3): []} )==6
assert ( 6 or {(1, 't', '3'): []} )==6
assert ( 6 or [True, False] )==6
assert ( 6 or [False, True] )==6
assert ( 6 or {1: 'one'} )==6
assert ( 6 or {0: 'zero', 1: 'pne'} )==6
assert ( 6 < 'a string' )
assert ( 6 < 6 )==False
assert ( 6 < -2 )==False
assert ( 6 < False )==False
assert ( 6 < True )==False
assert ( 6 < None )==False
assert ( 6 < [1, 2, 3] )
assert ( 6 < ['one', 'two', 'three'] )
assert ( 6 < ['one', 'three', 'too'] )
assert ( 6 < {} )==False
assert ( 6 < {(1, 2, 3): []} )==False
assert ( 6 < {(1, 't', '3'): []} )==False
assert ( 6 < [True, False] )
assert ( 6 < [False, True] )
assert ( 6 < {1: 'one'} )==False
assert ( 6 < {0: 'zero', 1: 'pne'} )==False
assert ( 6 > 'a string' )==False
assert ( 6 > 6 )==False
assert ( 6 > -2 )
assert ( 6 > False )
assert ( 6 > True )
assert ( 6 > None )
assert ( 6 > [1, 2, 3] )==False
assert ( 6 > ['one', 'two', 'three'] )==False
assert ( 6 > ['one', 'three', 'too'] )==False
assert ( 6 > {} )
assert ( 6 > {(1, 2, 3): []} )
assert ( 6 > {(1, 't', '3'): []} )
assert ( 6 > [True, False] )==False
assert ( 6 > [False, True] )==False
assert ( 6 > {1: 'one'} )
assert ( 6 > {0: 'zero', 1: 'pne'} )
assert ( 6 == 'a string' )==False
assert ( 6 == 6 )
assert ( 6 == -2 )==False
assert ( 6 == False )==False
assert ( 6 == True )==False
assert ( 6 == None )==False
assert ( 6 == [1, 2, 3] )==False
assert ( 6 == ['one', 'two', 'three'] )==False
assert ( 6 == ['one', 'three', 'too'] )==False
assert ( 6 == {} )==False
assert ( 6 == {(1, 2, 3): []} )==False
assert ( 6 == {(1, 't', '3'): []} )==False
assert ( 6 == [True, False] )==False
assert ( 6 == [False, True] )==False
assert ( 6 == {1: 'one'} )==False
assert ( 6 == {0: 'zero', 1: 'pne'} )==False
assert ( 6 <= 'a string' )
assert ( 6 <= 6 )
assert ( 6 <= -2 )==False
assert ( 6 <= False )==False
assert ( 6 <= True )==False
assert ( 6 <= None )==False
assert ( 6 <= [1, 2, 3] )
assert ( 6 <= ['one', 'two', 'three'] )
assert ( 6 <= ['one', 'three', 'too'] )
assert ( 6 <= {} )==False
assert ( 6 <= {(1, 2, 3): []} )==False
assert ( 6 <= {(1, 't', '3'): []} )==False
assert ( 6 <= [True, False] )
assert ( 6 <= [False, True] )
assert ( 6 <= {1: 'one'} )==False
assert ( 6 <= {0: 'zero', 1: 'pne'} )==False
assert ( 6 >= 'a string' )==False
assert ( 6 >= 6 )
assert ( 6 >= -2 )
assert ( 6 >= False )
assert ( 6 >= True )
assert ( 6 >= None )
assert ( 6 >= [1, 2, 3] )==False
assert ( 6 >= ['one', 'two', 'three'] )==False
assert ( 6 >= ['one', 'three', 'too'] )==False
assert ( 6 >= {} )
assert ( 6 >= {(1, 2, 3): []} )
assert ( 6 >= {(1, 't', '3'): []} )
assert ( 6 >= [True, False] )==False
assert ( 6 >= [False, True] )==False
assert ( 6 >= {1: 'one'} )
assert ( 6 >= {0: 'zero', 1: 'pne'} )
assert ( 6 != 'a string' )
assert ( 6 != 6 )==False
assert ( 6 != -2 )
assert ( 6 != False )
assert ( 6 != True )
assert ( 6 != None )
assert ( 6 != [1, 2, 3] )
assert ( 6 != ['one', 'two', 'three'] )
assert ( 6 != ['one', 'three', 'too'] )
assert ( 6 != {} )
assert ( 6 != {(1, 2, 3): []} )
assert ( 6 != {(1, 't', '3'): []} )
assert ( 6 != [True, False] )
assert ( 6 != [False, True] )
assert ( 6 != {1: 'one'} )
assert ( 6 != {0: 'zero', 1: 'pne'} )
assert ( -2 + 6 )==4
assert ( -2 + -2 )==-4
assert ( -2 - 6 )==-8
assert ( -2 - -2 )==0
assert ( -2 * 'a string' )==''
assert ( -2 * 6 )==-12
assert ( -2 * -2 )==4
assert ( -2 * [1, 2, 3] )==[]
assert ( -2 * ['one', 'two', 'three'] )==[]
assert ( -2 * ['one', 'three', 'too'] )==[]
assert ( -2 * [True, False] )==[]
assert ( -2 * [False, True] )==[]
assert ( -2 / 6 )==-1
assert ( -2 / -2 )==1
assert ( -2 and 'a string' )=='a string'
assert ( -2 and 6 )==6
assert ( -2 and -2 )==-2
assert ( -2 and False )==False
assert ( -2 and True )
assert ( -2 and None )==None
assert ( -2 and [1, 2, 3] )==[1, 2, 3]
assert ( -2 and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( -2 and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( -2 and {} )=={}
assert ( -2 and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( -2 and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( -2 and [True, False] )==[True, False]
assert ( -2 and [False, True] )==[False, True]
assert ( -2 and {1: 'one'} )=={1: 'one'}
assert ( -2 and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( -2 or 'a string' )==-2
assert ( -2 or 6 )==-2
assert ( -2 or -2 )==-2
assert ( -2 or False )==-2
assert ( -2 or True )==-2
assert ( -2 or None )==-2
assert ( -2 or [1, 2, 3] )==-2
assert ( -2 or ['one', 'two', 'three'] )==-2
assert ( -2 or ['one', 'three', 'too'] )==-2
assert ( -2 or {} )==-2
assert ( -2 or {(1, 2, 3): []} )==-2
assert ( -2 or {(1, 't', '3'): []} )==-2
assert ( -2 or [True, False] )==-2
assert ( -2 or [False, True] )==-2
assert ( -2 or {1: 'one'} )==-2
assert ( -2 or {0: 'zero', 1: 'pne'} )==-2
assert ( -2 < 'a string' )
assert ( -2 < 6 )
assert ( -2 < -2 )==False
assert ( -2 < False )==False
assert ( -2 < True )==False
assert ( -2 < None )==False
assert ( -2 < [1, 2, 3] )
assert ( -2 < ['one', 'two', 'three'] )
assert ( -2 < ['one', 'three', 'too'] )
assert ( -2 < {} )==False
assert ( -2 < {(1, 2, 3): []} )==False
assert ( -2 < {(1, 't', '3'): []} )==False
assert ( -2 < [True, False] )
assert ( -2 < [False, True] )
assert ( -2 < {1: 'one'} )==False
assert ( -2 < {0: 'zero', 1: 'pne'} )==False
assert ( -2 > 'a string' )==False
assert ( -2 > 6 )==False
assert ( -2 > -2 )==False
assert ( -2 > False )
assert ( -2 > True )
assert ( -2 > None )
assert ( -2 > [1, 2, 3] )==False
assert ( -2 > ['one', 'two', 'three'] )==False
assert ( -2 > ['one', 'three', 'too'] )==False
assert ( -2 > {} )
assert ( -2 > {(1, 2, 3): []} )
assert ( -2 > {(1, 't', '3'): []} )
assert ( -2 > [True, False] )==False
assert ( -2 > [False, True] )==False
assert ( -2 > {1: 'one'} )
assert ( -2 > {0: 'zero', 1: 'pne'} )
assert ( -2 == 'a string' )==False
assert ( -2 == 6 )==False
assert ( -2 == -2 )
assert ( -2 == False )==False
assert ( -2 == True )==False
assert ( -2 == None )==False
assert ( -2 == [1, 2, 3] )==False
assert ( -2 == ['one', 'two', 'three'] )==False
assert ( -2 == ['one', 'three', 'too'] )==False
assert ( -2 == {} )==False
assert ( -2 == {(1, 2, 3): []} )==False
assert ( -2 == {(1, 't', '3'): []} )==False
assert ( -2 == [True, False] )==False
assert ( -2 == [False, True] )==False
assert ( -2 == {1: 'one'} )==False
assert ( -2 == {0: 'zero', 1: 'pne'} )==False
assert ( -2 <= 'a string' )
assert ( -2 <= 6 )
assert ( -2 <= -2 )
assert ( -2 <= False )==False
assert ( -2 <= True )==False
assert ( -2 <= None )==False
assert ( -2 <= [1, 2, 3] )
assert ( -2 <= ['one', 'two', 'three'] )
assert ( -2 <= ['one', 'three', 'too'] )
assert ( -2 <= {} )==False
assert ( -2 <= {(1, 2, 3): []} )==False
assert ( -2 <= {(1, 't', '3'): []} )==False
assert ( -2 <= [True, False] )
assert ( -2 <= [False, True] )
assert ( -2 <= {1: 'one'} )==False
assert ( -2 <= {0: 'zero', 1: 'pne'} )==False
assert ( -2 >= 'a string' )==False
assert ( -2 >= 6 )==False
assert ( -2 >= -2 )
assert ( -2 >= False )
assert ( -2 >= True )
assert ( -2 >= None )
assert ( -2 >= [1, 2, 3] )==False
assert ( -2 >= ['one', 'two', 'three'] )==False
assert ( -2 >= ['one', 'three', 'too'] )==False
assert ( -2 >= {} )
assert ( -2 >= {(1, 2, 3): []} )
assert ( -2 >= {(1, 't', '3'): []} )
assert ( -2 >= [True, False] )==False
assert ( -2 >= [False, True] )==False
assert ( -2 >= {1: 'one'} )
assert ( -2 >= {0: 'zero', 1: 'pne'} )
assert ( -2 != 'a string' )
assert ( -2 != 6 )
assert ( -2 != -2 )==False
assert ( -2 != False )
assert ( -2 != True )
assert ( -2 != None )
assert ( -2 != [1, 2, 3] )
assert ( -2 != ['one', 'two', 'three'] )
assert ( -2 != ['one', 'three', 'too'] )
assert ( -2 != {} )
assert ( -2 != {(1, 2, 3): []} )
assert ( -2 != {(1, 't', '3'): []} )
assert ( -2 != [True, False] )
assert ( -2 != [False, True] )
assert ( -2 != {1: 'one'} )
assert ( -2 != {0: 'zero', 1: 'pne'} )
assert ( False and 'a string' )==False
assert ( False and 6 )==False
assert ( False and -2 )==False
assert ( False and False )==False
assert ( False and True )==False
assert ( False and None )==False
assert ( False and [1, 2, 3] )==False
assert ( False and ['one', 'two', 'three'] )==False
assert ( False and ['one', 'three', 'too'] )==False
assert ( False and {} )==False
assert ( False and {(1, 2, 3): []} )==False
assert ( False and {(1, 't', '3'): []} )==False
assert ( False and [True, False] )==False
assert ( False and [False, True] )==False
assert ( False and {1: 'one'} )==False
assert ( False and {0: 'zero', 1: 'pne'} )==False
assert ( False or 'a string' )=='a string'
assert ( False or 6 )==6
assert ( False or -2 )==-2
assert ( False or False )==False
assert ( False or True )
assert ( False or None )==None
assert ( False or [1, 2, 3] )==[1, 2, 3]
assert ( False or ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( False or ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( False or {} )=={}
assert ( False or {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( False or {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( False or [True, False] )==[True, False]
assert ( False or [False, True] )==[False, True]
assert ( False or {1: 'one'} )=={1: 'one'}
assert ( False or {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( False < 'a string' )
assert ( False < 6 )
assert ( False < -2 )
assert ( False < False )==False
assert ( False < True )
assert ( False < None )==False
assert ( False < [1, 2, 3] )
assert ( False < ['one', 'two', 'three'] )
assert ( False < ['one', 'three', 'too'] )
assert ( False < {} )
assert ( False < {(1, 2, 3): []} )
assert ( False < {(1, 't', '3'): []} )
assert ( False < [True, False] )
assert ( False < [False, True] )
assert ( False < {1: 'one'} )
assert ( False < {0: 'zero', 1: 'pne'} )
assert ( False > 'a string' )==False
assert ( False > 6 )==False
assert ( False > -2 )==False
assert ( False > False )==False
assert ( False > True )==False
assert ( False > None )
assert ( False > [1, 2, 3] )==False
assert ( False > ['one', 'two', 'three'] )==False
assert ( False > ['one', 'three', 'too'] )==False
assert ( False > {} )==False
assert ( False > {(1, 2, 3): []} )==False
assert ( False > {(1, 't', '3'): []} )==False
assert ( False > [True, False] )==False
assert ( False > [False, True] )==False
assert ( False > {1: 'one'} )==False
assert ( False > {0: 'zero', 1: 'pne'} )==False
assert ( False == 'a string' )==False
assert ( False == 6 )==False
assert ( False == -2 )==False
assert ( False == False )
assert ( False == True )==False
assert ( False == None )==False
assert ( False == [1, 2, 3] )==False
assert ( False == ['one', 'two', 'three'] )==False
assert ( False == ['one', 'three', 'too'] )==False
assert ( False == {} )==False
assert ( False == {(1, 2, 3): []} )==False
assert ( False == {(1, 't', '3'): []} )==False
assert ( False == [True, False] )==False
assert ( False == [False, True] )==False
assert ( False == {1: 'one'} )==False
assert ( False == {0: 'zero', 1: 'pne'} )==False
assert ( False <= 'a string' )
assert ( False <= 6 )
assert ( False <= -2 )
assert ( False <= False )
assert ( False <= True )
assert ( False <= None )==False
assert ( False <= [1, 2, 3] )
assert ( False <= ['one', 'two', 'three'] )
assert ( False <= ['one', 'three', 'too'] )
assert ( False <= {} )
assert ( False <= {(1, 2, 3): []} )
assert ( False <= {(1, 't', '3'): []} )
assert ( False <= [True, False] )
assert ( False <= [False, True] )
assert ( False <= {1: 'one'} )
assert ( False <= {0: 'zero', 1: 'pne'} )
assert ( False >= 'a string' )==False
assert ( False >= 6 )==False
assert ( False >= -2 )==False
assert ( False >= False )
assert ( False >= True )==False
assert ( False >= None )
assert ( False >= [1, 2, 3] )==False
assert ( False >= ['one', 'two', 'three'] )==False
assert ( False >= ['one', 'three', 'too'] )==False
assert ( False >= {} )==False
assert ( False >= {(1, 2, 3): []} )==False
assert ( False >= {(1, 't', '3'): []} )==False
assert ( False >= [True, False] )==False
assert ( False >= [False, True] )==False
assert ( False >= {1: 'one'} )==False
assert ( False >= {0: 'zero', 1: 'pne'} )==False
assert ( False != 'a string' )
assert ( False != 6 )
assert ( False != -2 )
assert ( False != False )==False
assert ( False != True )
assert ( False != None )
assert ( False != [1, 2, 3] )
assert ( False != ['one', 'two', 'three'] )
assert ( False != ['one', 'three', 'too'] )
assert ( False != {} )
assert ( False != {(1, 2, 3): []} )
assert ( False != {(1, 't', '3'): []} )
assert ( False != [True, False] )
assert ( False != [False, True] )
assert ( False != {1: 'one'} )
assert ( False != {0: 'zero', 1: 'pne'} )
assert ( True and 'a string' )=='a string'
assert ( True and 6 )==6
assert ( True and -2 )==-2
assert ( True and False )==False
assert ( True and True )
assert ( True and None )==None
assert ( True and [1, 2, 3] )==[1, 2, 3]
assert ( True and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( True and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( True and {} )=={}
assert ( True and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( True and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( True and [True, False] )==[True, False]
assert ( True and [False, True] )==[False, True]
assert ( True and {1: 'one'} )=={1: 'one'}
assert ( True and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( True or 'a string' )
assert ( True or 6 )
assert ( True or -2 )
assert ( True or False )
assert ( True or True )
assert ( True or None )
assert ( True or [1, 2, 3] )
assert ( True or ['one', 'two', 'three'] )
assert ( True or ['one', 'three', 'too'] )
assert ( True or {} )
assert ( True or {(1, 2, 3): []} )
assert ( True or {(1, 't', '3'): []} )
assert ( True or [True, False] )
assert ( True or [False, True] )
assert ( True or {1: 'one'} )
assert ( True or {0: 'zero', 1: 'pne'} )
assert ( True < 'a string' )
assert ( True < 6 )
assert ( True < -2 )
assert ( True < False )==False
assert ( True < True )==False
assert ( True < None )==False
assert ( True < [1, 2, 3] )
assert ( True < ['one', 'two', 'three'] )
assert ( True < ['one', 'three', 'too'] )
assert ( True < {} )
assert ( True < {(1, 2, 3): []} )
assert ( True < {(1, 't', '3'): []} )
assert ( True < [True, False] )
assert ( True < [False, True] )
assert ( True < {1: 'one'} )
assert ( True < {0: 'zero', 1: 'pne'} )
assert ( True > 'a string' )==False
assert ( True > 6 )==False
assert ( True > -2 )==False
assert ( True > False )
assert ( True > True )==False
assert ( True > None )
assert ( True > [1, 2, 3] )==False
assert ( True > ['one', 'two', 'three'] )==False
assert ( True > ['one', 'three', 'too'] )==False
assert ( True > {} )==False
assert ( True > {(1, 2, 3): []} )==False
assert ( True > {(1, 't', '3'): []} )==False
assert ( True > [True, False] )==False
assert ( True > [False, True] )==False
assert ( True > {1: 'one'} )==False
assert ( True > {0: 'zero', 1: 'pne'} )==False
assert ( True == 'a string' )==False
assert ( True == 6 )==False
assert ( True == -2 )==False
assert ( True == False )==False
assert ( True == True )
assert ( True == None )==False
assert ( True == [1, 2, 3] )==False
assert ( True == ['one', 'two', 'three'] )==False
assert ( True == ['one', 'three', 'too'] )==False
assert ( True == {} )==False
assert ( True == {(1, 2, 3): []} )==False
assert ( True == {(1, 't', '3'): []} )==False
assert ( True == [True, False] )==False
assert ( True == [False, True] )==False
assert ( True == {1: 'one'} )==False
assert ( True == {0: 'zero', 1: 'pne'} )==False
assert ( True <= 'a string' )
assert ( True <= 6 )
assert ( True <= -2 )
assert ( True <= False )==False
assert ( True <= True )
assert ( True <= None )==False
assert ( True <= [1, 2, 3] )
assert ( True <= ['one', 'two', 'three'] )
assert ( True <= ['one', 'three', 'too'] )
assert ( True <= {} )
assert ( True <= {(1, 2, 3): []} )
assert ( True <= {(1, 't', '3'): []} )
assert ( True <= [True, False] )
assert ( True <= [False, True] )
assert ( True <= {1: 'one'} )
assert ( True <= {0: 'zero', 1: 'pne'} )
assert ( True >= 'a string' )==False
assert ( True >= 6 )==False
assert ( True >= -2 )==False
assert ( True >= False )
assert ( True >= True )
assert ( True >= None )
assert ( True >= [1, 2, 3] )==False
assert ( True >= ['one', 'two', 'three'] )==False
assert ( True >= ['one', 'three', 'too'] )==False
assert ( True >= {} )==False
assert ( True >= {(1, 2, 3): []} )==False
assert ( True >= {(1, 't', '3'): []} )==False
assert ( True >= [True, False] )==False
assert ( True >= [False, True] )==False
assert ( True >= {1: 'one'} )==False
assert ( True >= {0: 'zero', 1: 'pne'} )==False
assert ( True != 'a string' )
assert ( True != 6 )
assert ( True != -2 )
assert ( True != False )
assert ( True != True )==False
assert ( True != None )
assert ( True != [1, 2, 3] )
assert ( True != ['one', 'two', 'three'] )
assert ( True != ['one', 'three', 'too'] )
assert ( True != {} )
assert ( True != {(1, 2, 3): []} )
assert ( True != {(1, 't', '3'): []} )
assert ( True != [True, False] )
assert ( True != [False, True] )
assert ( True != {1: 'one'} )
assert ( True != {0: 'zero', 1: 'pne'} )
assert ( None and 'a string' )==None
assert ( None and 6 )==None
assert ( None and -2 )==None
assert ( None and False )==None
assert ( None and True )==None
assert ( None and None )==None
assert ( None and [1, 2, 3] )==None
assert ( None and ['one', 'two', 'three'] )==None
assert ( None and ['one', 'three', 'too'] )==None
assert ( None and {} )==None
assert ( None and {(1, 2, 3): []} )==None
assert ( None and {(1, 't', '3'): []} )==None
assert ( None and [True, False] )==None
assert ( None and [False, True] )==None
assert ( None and {1: 'one'} )==None
assert ( None and {0: 'zero', 1: 'pne'} )==None
assert ( None or 'a string' )=='a string'
assert ( None or 6 )==6
assert ( None or -2 )==-2
assert ( None or False )==False
assert ( None or True )
assert ( None or None )==None
assert ( None or [1, 2, 3] )==[1, 2, 3]
assert ( None or ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( None or ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( None or {} )=={}
assert ( None or {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( None or {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( None or [True, False] )==[True, False]
assert ( None or [False, True] )==[False, True]
assert ( None or {1: 'one'} )=={1: 'one'}
assert ( None or {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( None < 'a string' )
assert ( None < 6 )
assert ( None < -2 )
assert ( None < False )
assert ( None < True )
assert ( None < None )==False
assert ( None < [1, 2, 3] )
assert ( None < ['one', 'two', 'three'] )
assert ( None < ['one', 'three', 'too'] )
assert ( None < {} )
assert ( None < {(1, 2, 3): []} )
assert ( None < {(1, 't', '3'): []} )
assert ( None < [True, False] )
assert ( None < [False, True] )
assert ( None < {1: 'one'} )
assert ( None < {0: 'zero', 1: 'pne'} )
assert ( None > 'a string' )==False
assert ( None > 6 )==False
assert ( None > -2 )==False
assert ( None > False )==False
assert ( None > True )==False
assert ( None > None )==False
assert ( None > [1, 2, 3] )==False
assert ( None > ['one', 'two', 'three'] )==False
assert ( None > ['one', 'three', 'too'] )==False
assert ( None > {} )==False
assert ( None > {(1, 2, 3): []} )==False
assert ( None > {(1, 't', '3'): []} )==False
assert ( None > [True, False] )==False
assert ( None > [False, True] )==False
assert ( None > {1: 'one'} )==False
assert ( None > {0: 'zero', 1: 'pne'} )==False
assert ( None == 'a string' )==False
assert ( None == 6 )==False
assert ( None == -2 )==False
assert ( None == False )==False
assert ( None == True )==False
assert ( None == None )
assert ( None == [1, 2, 3] )==False
assert ( None == ['one', 'two', 'three'] )==False
assert ( None == ['one', 'three', 'too'] )==False
assert ( None == {} )==False
assert ( None == {(1, 2, 3): []} )==False
assert ( None == {(1, 't', '3'): []} )==False
assert ( None == [True, False] )==False
assert ( None == [False, True] )==False
assert ( None == {1: 'one'} )==False
assert ( None == {0: 'zero', 1: 'pne'} )==False
assert ( None <= 'a string' )
assert ( None <= 6 )
assert ( None <= -2 )
assert ( None <= False )
assert ( None <= True )
assert ( None <= None )
assert ( None <= [1, 2, 3] )
assert ( None <= ['one', 'two', 'three'] )
assert ( None <= ['one', 'three', 'too'] )
assert ( None <= {} )
assert ( None <= {(1, 2, 3): []} )
assert ( None <= {(1, 't', '3'): []} )
assert ( None <= [True, False] )
assert ( None <= [False, True] )
assert ( None <= {1: 'one'} )
assert ( None <= {0: 'zero', 1: 'pne'} )
assert ( None >= 'a string' )==False
assert ( None >= 6 )==False
assert ( None >= -2 )==False
assert ( None >= False )==False
assert ( None >= True )==False
assert ( None >= None )
assert ( None >= [1, 2, 3] )==False
assert ( None >= ['one', 'two', 'three'] )==False
assert ( None >= ['one', 'three', 'too'] )==False
assert ( None >= {} )==False
assert ( None >= {(1, 2, 3): []} )==False
assert ( None >= {(1, 't', '3'): []} )==False
assert ( None >= [True, False] )==False
assert ( None >= [False, True] )==False
assert ( None >= {1: 'one'} )==False
assert ( None >= {0: 'zero', 1: 'pne'} )==False
assert ( None != 'a string' )
assert ( None != 6 )
assert ( None != -2 )
assert ( None != False )
assert ( None != True )
assert ( None != None )==False
assert ( None != [1, 2, 3] )
assert ( None != ['one', 'two', 'three'] )
assert ( None != ['one', 'three', 'too'] )
assert ( None != {} )
assert ( None != {(1, 2, 3): []} )
assert ( None != {(1, 't', '3'): []} )
assert ( None != [True, False] )
assert ( None != [False, True] )
assert ( None != {1: 'one'} )
assert ( None != {0: 'zero', 1: 'pne'} )
assert ( [1, 2, 3] + [1, 2, 3] )==[1, 2, 3, 1, 2, 3]
assert ( [1, 2, 3] + ['one', 'two', 'three'] )==[1, 2, 3, 'one', 'two', 'three']
assert ( [1, 2, 3] + ['one', 'three', 'too'] )==[1, 2, 3, 'one', 'three', 'too']
assert ( [1, 2, 3] + [True, False] )==[1, 2, 3, True, False]
assert ( [1, 2, 3] + [False, True] )==[1, 2, 3, False, True]
assert ( [1, 2, 3] * 6 )==[1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
assert ( [1, 2, 3] * -2 )==[]
assert ( [1, 2, 3] and 'a string' )=='a string'
assert ( [1, 2, 3] and 6 )==6
assert ( [1, 2, 3] and -2 )==-2
assert ( [1, 2, 3] and False )==False
assert ( [1, 2, 3] and True )
assert ( [1, 2, 3] and None )==None
assert ( [1, 2, 3] and [1, 2, 3] )==[1, 2, 3]
assert ( [1, 2, 3] and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( [1, 2, 3] and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( [1, 2, 3] and {} )=={}
assert ( [1, 2, 3] and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( [1, 2, 3] and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( [1, 2, 3] and [True, False] )==[True, False]
assert ( [1, 2, 3] and [False, True] )==[False, True]
assert ( [1, 2, 3] and {1: 'one'} )=={1: 'one'}
assert ( [1, 2, 3] and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( [1, 2, 3] or 'a string' )==[1, 2, 3]
assert ( [1, 2, 3] or 6 )==[1, 2, 3]
assert ( [1, 2, 3] or -2 )==[1, 2, 3]
assert ( [1, 2, 3] or False )==[1, 2, 3]
assert ( [1, 2, 3] or True )==[1, 2, 3]
assert ( [1, 2, 3] or None )==[1, 2, 3]
assert ( [1, 2, 3] or [1, 2, 3] )==[1, 2, 3]
assert ( [1, 2, 3] or ['one', 'two', 'three'] )==[1, 2, 3]
assert ( [1, 2, 3] or ['one', 'three', 'too'] )==[1, 2, 3]
assert ( [1, 2, 3] or {} )==[1, 2, 3]
assert ( [1, 2, 3] or {(1, 2, 3): []} )==[1, 2, 3]
assert ( [1, 2, 3] or {(1, 't', '3'): []} )==[1, 2, 3]
assert ( [1, 2, 3] or [True, False] )==[1, 2, 3]
assert ( [1, 2, 3] or [False, True] )==[1, 2, 3]
assert ( [1, 2, 3] or {1: 'one'} )==[1, 2, 3]
assert ( [1, 2, 3] or {0: 'zero', 1: 'pne'} )==[1, 2, 3]
assert ( [1, 2, 3] < 'a string' )
assert ( [1, 2, 3] < 6 )==False
assert ( [1, 2, 3] < -2 )==False
assert ( [1, 2, 3] < False )==False
assert ( [1, 2, 3] < True )==False
assert ( [1, 2, 3] < None )==False
assert ( [1, 2, 3] < [1, 2, 3] )==False
assert ( [1, 2, 3] < ['one', 'two', 'three'] )
assert ( [1, 2, 3] < ['one', 'three', 'too'] )
assert ( [1, 2, 3] < {} )==False
assert ( [1, 2, 3] < {(1, 2, 3): []} )==False
assert ( [1, 2, 3] < {(1, 't', '3'): []} )==False
assert ( [1, 2, 3] < [True, False] )==False
assert ( [1, 2, 3] < [False, True] )==False
assert ( [1, 2, 3] < {1: 'one'} )==False
assert ( [1, 2, 3] < {0: 'zero', 1: 'pne'} )==False
assert ( [1, 2, 3] > 'a string' )==False
assert ( [1, 2, 3] > 6 )
assert ( [1, 2, 3] > -2 )
assert ( [1, 2, 3] > False )
assert ( [1, 2, 3] > True )
assert ( [1, 2, 3] > None )
assert ( [1, 2, 3] > [1, 2, 3] )==False
assert ( [1, 2, 3] > ['one', 'two', 'three'] )==False
assert ( [1, 2, 3] > ['one', 'three', 'too'] )==False
assert ( [1, 2, 3] > {} )
assert ( [1, 2, 3] > {(1, 2, 3): []} )
assert ( [1, 2, 3] > {(1, 't', '3'): []} )
assert ( [1, 2, 3] > [True, False] )
assert ( [1, 2, 3] > [False, True] )
assert ( [1, 2, 3] > {1: 'one'} )
assert ( [1, 2, 3] > {0: 'zero', 1: 'pne'} )
assert ( [1, 2, 3] == 'a string' )==False
assert ( [1, 2, 3] == 6 )==False
assert ( [1, 2, 3] == -2 )==False
assert ( [1, 2, 3] == False )==False
assert ( [1, 2, 3] == True )==False
assert ( [1, 2, 3] == None )==False
assert ( [1, 2, 3] == [1, 2, 3] )
assert ( [1, 2, 3] == ['one', 'two', 'three'] )==False
assert ( [1, 2, 3] == ['one', 'three', 'too'] )==False
assert ( [1, 2, 3] == {} )==False
assert ( [1, 2, 3] == {(1, 2, 3): []} )==False
assert ( [1, 2, 3] == {(1, 't', '3'): []} )==False
assert ( [1, 2, 3] == [True, False] )==False
assert ( [1, 2, 3] == [False, True] )==False
assert ( [1, 2, 3] == {1: 'one'} )==False
assert ( [1, 2, 3] == {0: 'zero', 1: 'pne'} )==False
assert ( [1, 2, 3] <= 'a string' )
assert ( [1, 2, 3] <= 6 )==False
assert ( [1, 2, 3] <= -2 )==False
assert ( [1, 2, 3] <= False )==False
assert ( [1, 2, 3] <= True )==False
assert ( [1, 2, 3] <= None )==False
assert ( [1, 2, 3] <= [1, 2, 3] )
assert ( [1, 2, 3] <= ['one', 'two', 'three'] )
assert ( [1, 2, 3] <= ['one', 'three', 'too'] )
assert ( [1, 2, 3] <= {} )==False
assert ( [1, 2, 3] <= {(1, 2, 3): []} )==False
assert ( [1, 2, 3] <= {(1, 't', '3'): []} )==False
assert ( [1, 2, 3] <= [True, False] )==False
assert ( [1, 2, 3] <= [False, True] )==False
assert ( [1, 2, 3] <= {1: 'one'} )==False
assert ( [1, 2, 3] <= {0: 'zero', 1: 'pne'} )==False
assert ( [1, 2, 3] >= 'a string' )==False
assert ( [1, 2, 3] >= 6 )
assert ( [1, 2, 3] >= -2 )
assert ( [1, 2, 3] >= False )
assert ( [1, 2, 3] >= True )
assert ( [1, 2, 3] >= None )
assert ( [1, 2, 3] >= [1, 2, 3] )
assert ( [1, 2, 3] >= ['one', 'two', 'three'] )==False
assert ( [1, 2, 3] >= ['one', 'three', 'too'] )==False
assert ( [1, 2, 3] >= {} )
assert ( [1, 2, 3] >= {(1, 2, 3): []} )
assert ( [1, 2, 3] >= {(1, 't', '3'): []} )
assert ( [1, 2, 3] >= [True, False] )
assert ( [1, 2, 3] >= [False, True] )
assert ( [1, 2, 3] >= {1: 'one'} )
assert ( [1, 2, 3] >= {0: 'zero', 1: 'pne'} )
assert ( [1, 2, 3] != 'a string' )
assert ( [1, 2, 3] != 6 )
assert ( [1, 2, 3] != -2 )
assert ( [1, 2, 3] != False )
assert ( [1, 2, 3] != True )
assert ( [1, 2, 3] != None )
assert ( [1, 2, 3] != [1, 2, 3] )==False
assert ( [1, 2, 3] != ['one', 'two', 'three'] )
assert ( [1, 2, 3] != ['one', 'three', 'too'] )
assert ( [1, 2, 3] != {} )
assert ( [1, 2, 3] != {(1, 2, 3): []} )
assert ( [1, 2, 3] != {(1, 't', '3'): []} )
assert ( [1, 2, 3] != [True, False] )
assert ( [1, 2, 3] != [False, True] )
assert ( [1, 2, 3] != {1: 'one'} )
assert ( [1, 2, 3] != {0: 'zero', 1: 'pne'} )
assert ( ['one', 'two', 'three'] + [1, 2, 3] )==['one', 'two', 'three', 1, 2, 3]
assert ( ['one', 'two', 'three'] + ['one', 'two', 'three'] )==['one', 'two', 'three', 'one', 'two', 'three']
assert ( ['one', 'two', 'three'] + ['one', 'three', 'too'] )==['one', 'two', 'three', 'one', 'three', 'too']
assert ( ['one', 'two', 'three'] + [True, False] )==['one', 'two', 'three', True, False]
assert ( ['one', 'two', 'three'] + [False, True] )==['one', 'two', 'three', False, True]
assert ( ['one', 'two', 'three'] * 6 )==['one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three', 'one', 'two', 'three']
assert ( ['one', 'two', 'three'] * -2 )==[]
assert ( ['one', 'two', 'three'] and 'a string' )=='a string'
assert ( ['one', 'two', 'three'] and 6 )==6
assert ( ['one', 'two', 'three'] and -2 )==-2
assert ( ['one', 'two', 'three'] and False )==False
assert ( ['one', 'two', 'three'] and True )
assert ( ['one', 'two', 'three'] and None )==None
assert ( ['one', 'two', 'three'] and [1, 2, 3] )==[1, 2, 3]
assert ( ['one', 'two', 'three'] and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( ['one', 'two', 'three'] and {} )=={}
assert ( ['one', 'two', 'three'] and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( ['one', 'two', 'three'] and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( ['one', 'two', 'three'] and [True, False] )==[True, False]
assert ( ['one', 'two', 'three'] and [False, True] )==[False, True]
assert ( ['one', 'two', 'three'] and {1: 'one'} )=={1: 'one'}
assert ( ['one', 'two', 'three'] and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( ['one', 'two', 'three'] or 'a string' )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or 6 )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or -2 )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or False )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or True )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or None )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or [1, 2, 3] )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or ['one', 'three', 'too'] )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or {} )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or {(1, 2, 3): []} )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or {(1, 't', '3'): []} )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or [True, False] )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or [False, True] )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or {1: 'one'} )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] or {0: 'zero', 1: 'pne'} )==['one', 'two', 'three']
assert ( ['one', 'two', 'three'] < 'a string' )
assert ( ['one', 'two', 'three'] < 6 )==False
assert ( ['one', 'two', 'three'] < -2 )==False
assert ( ['one', 'two', 'three'] < False )==False
assert ( ['one', 'two', 'three'] < True )==False
assert ( ['one', 'two', 'three'] < None )==False
assert ( ['one', 'two', 'three'] < [1, 2, 3] )==False
assert ( ['one', 'two', 'three'] < ['one', 'two', 'three'] )==False
assert ( ['one', 'two', 'three'] < ['one', 'three', 'too'] )==False
assert ( ['one', 'two', 'three'] < {} )==False
assert ( ['one', 'two', 'three'] < {(1, 2, 3): []} )==False
assert ( ['one', 'two', 'three'] < {(1, 't', '3'): []} )==False
assert ( ['one', 'two', 'three'] < [True, False] )==False
assert ( ['one', 'two', 'three'] < [False, True] )==False
assert ( ['one', 'two', 'three'] < {1: 'one'} )==False
assert ( ['one', 'two', 'three'] < {0: 'zero', 1: 'pne'} )==False
assert ( ['one', 'two', 'three'] > 'a string' )==False
assert ( ['one', 'two', 'three'] > 6 )
assert ( ['one', 'two', 'three'] > -2 )
assert ( ['one', 'two', 'three'] > False )
assert ( ['one', 'two', 'three'] > True )
assert ( ['one', 'two', 'three'] > None )
assert ( ['one', 'two', 'three'] > [1, 2, 3] )
assert ( ['one', 'two', 'three'] > ['one', 'two', 'three'] )==False
assert ( ['one', 'two', 'three'] > ['one', 'three', 'too'] )
assert ( ['one', 'two', 'three'] > {} )
assert ( ['one', 'two', 'three'] > {(1, 2, 3): []} )
assert ( ['one', 'two', 'three'] > {(1, 't', '3'): []} )
assert ( ['one', 'two', 'three'] > [True, False] )
assert ( ['one', 'two', 'three'] > [False, True] )
assert ( ['one', 'two', 'three'] > {1: 'one'} )
assert ( ['one', 'two', 'three'] > {0: 'zero', 1: 'pne'} )
assert ( ['one', 'two', 'three'] == 'a string' )==False
assert ( ['one', 'two', 'three'] == 6 )==False
assert ( ['one', 'two', 'three'] == -2 )==False
assert ( ['one', 'two', 'three'] == False )==False
assert ( ['one', 'two', 'three'] == True )==False
assert ( ['one', 'two', 'three'] == None )==False
assert ( ['one', 'two', 'three'] == [1, 2, 3] )==False
assert ( ['one', 'two', 'three'] == ['one', 'two', 'three'] )
assert ( ['one', 'two', 'three'] == ['one', 'three', 'too'] )==False
assert ( ['one', 'two', 'three'] == {} )==False
assert ( ['one', 'two', 'three'] == {(1, 2, 3): []} )==False
assert ( ['one', 'two', 'three'] == {(1, 't', '3'): []} )==False
assert ( ['one', 'two', 'three'] == [True, False] )==False
assert ( ['one', 'two', 'three'] == [False, True] )==False
assert ( ['one', 'two', 'three'] == {1: 'one'} )==False
assert ( ['one', 'two', 'three'] == {0: 'zero', 1: 'pne'} )==False
assert ( ['one', 'two', 'three'] <= 'a string' )
assert ( ['one', 'two', 'three'] <= 6 )==False
assert ( ['one', 'two', 'three'] <= -2 )==False
assert ( ['one', 'two', 'three'] <= False )==False
assert ( ['one', 'two', 'three'] <= True )==False
assert ( ['one', 'two', 'three'] <= None )==False
assert ( ['one', 'two', 'three'] <= [1, 2, 3] )==False
assert ( ['one', 'two', 'three'] <= ['one', 'two', 'three'] )
assert ( ['one', 'two', 'three'] <= ['one', 'three', 'too'] )==False
assert ( ['one', 'two', 'three'] <= {} )==False
assert ( ['one', 'two', 'three'] <= {(1, 2, 3): []} )==False
assert ( ['one', 'two', 'three'] <= {(1, 't', '3'): []} )==False
assert ( ['one', 'two', 'three'] <= [True, False] )==False
assert ( ['one', 'two', 'three'] <= [False, True] )==False
assert ( ['one', 'two', 'three'] <= {1: 'one'} )==False
assert ( ['one', 'two', 'three'] <= {0: 'zero', 1: 'pne'} )==False
assert ( ['one', 'two', 'three'] >= 'a string' )==False
assert ( ['one', 'two', 'three'] >= 6 )
assert ( ['one', 'two', 'three'] >= -2 )
assert ( ['one', 'two', 'three'] >= False )
assert ( ['one', 'two', 'three'] >= True )
assert ( ['one', 'two', 'three'] >= None )
assert ( ['one', 'two', 'three'] >= [1, 2, 3] )
assert ( ['one', 'two', 'three'] >= ['one', 'two', 'three'] )
assert ( ['one', 'two', 'three'] >= ['one', 'three', 'too'] )
assert ( ['one', 'two', 'three'] >= {} )
assert ( ['one', 'two', 'three'] >= {(1, 2, 3): []} )
assert ( ['one', 'two', 'three'] >= {(1, 't', '3'): []} )
assert ( ['one', 'two', 'three'] >= [True, False] )
assert ( ['one', 'two', 'three'] >= [False, True] )
assert ( ['one', 'two', 'three'] >= {1: 'one'} )
assert ( ['one', 'two', 'three'] >= {0: 'zero', 1: 'pne'} )
assert ( ['one', 'two', 'three'] != 'a string' )
assert ( ['one', 'two', 'three'] != 6 )
assert ( ['one', 'two', 'three'] != -2 )
assert ( ['one', 'two', 'three'] != False )
assert ( ['one', 'two', 'three'] != True )
assert ( ['one', 'two', 'three'] != None )
assert ( ['one', 'two', 'three'] != [1, 2, 3] )
assert ( ['one', 'two', 'three'] != ['one', 'two', 'three'] )==False
assert ( ['one', 'two', 'three'] != ['one', 'three', 'too'] )
assert ( ['one', 'two', 'three'] != {} )
assert ( ['one', 'two', 'three'] != {(1, 2, 3): []} )
assert ( ['one', 'two', 'three'] != {(1, 't', '3'): []} )
assert ( ['one', 'two', 'three'] != [True, False] )
assert ( ['one', 'two', 'three'] != [False, True] )
assert ( ['one', 'two', 'three'] != {1: 'one'} )
assert ( ['one', 'two', 'three'] != {0: 'zero', 1: 'pne'} )
assert ( ['one', 'three', 'too'] + [1, 2, 3] )==['one', 'three', 'too', 1, 2, 3]
assert ( ['one', 'three', 'too'] + ['one', 'two', 'three'] )==['one', 'three', 'too', 'one', 'two', 'three']
assert ( ['one', 'three', 'too'] + ['one', 'three', 'too'] )==['one', 'three', 'too', 'one', 'three', 'too']
assert ( ['one', 'three', 'too'] + [True, False] )==['one', 'three', 'too', True, False]
assert ( ['one', 'three', 'too'] + [False, True] )==['one', 'three', 'too', False, True]
assert ( ['one', 'three', 'too'] * 6 )==['one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too', 'one', 'three', 'too']
assert ( ['one', 'three', 'too'] * -2 )==[]
assert ( ['one', 'three', 'too'] and 'a string' )=='a string'
assert ( ['one', 'three', 'too'] and 6 )==6
assert ( ['one', 'three', 'too'] and -2 )==-2
assert ( ['one', 'three', 'too'] and False )==False
assert ( ['one', 'three', 'too'] and True )
assert ( ['one', 'three', 'too'] and None )==None
assert ( ['one', 'three', 'too'] and [1, 2, 3] )==[1, 2, 3]
assert ( ['one', 'three', 'too'] and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( ['one', 'three', 'too'] and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] and {} )=={}
assert ( ['one', 'three', 'too'] and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( ['one', 'three', 'too'] and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( ['one', 'three', 'too'] and [True, False] )==[True, False]
assert ( ['one', 'three', 'too'] and [False, True] )==[False, True]
assert ( ['one', 'three', 'too'] and {1: 'one'} )=={1: 'one'}
assert ( ['one', 'three', 'too'] and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( ['one', 'three', 'too'] or 'a string' )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or 6 )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or -2 )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or False )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or True )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or None )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or [1, 2, 3] )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or ['one', 'two', 'three'] )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or {} )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or {(1, 2, 3): []} )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or {(1, 't', '3'): []} )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or [True, False] )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or [False, True] )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or {1: 'one'} )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] or {0: 'zero', 1: 'pne'} )==['one', 'three', 'too']
assert ( ['one', 'three', 'too'] < 'a string' )
assert ( ['one', 'three', 'too'] < 6 )==False
assert ( ['one', 'three', 'too'] < -2 )==False
assert ( ['one', 'three', 'too'] < False )==False
assert ( ['one', 'three', 'too'] < True )==False
assert ( ['one', 'three', 'too'] < None )==False
assert ( ['one', 'three', 'too'] < [1, 2, 3] )==False
assert ( ['one', 'three', 'too'] < ['one', 'two', 'three'] )
assert ( ['one', 'three', 'too'] < ['one', 'three', 'too'] )==False
assert ( ['one', 'three', 'too'] < {} )==False
assert ( ['one', 'three', 'too'] < {(1, 2, 3): []} )==False
assert ( ['one', 'three', 'too'] < {(1, 't', '3'): []} )==False
assert ( ['one', 'three', 'too'] < [True, False] )==False
assert ( ['one', 'three', 'too'] < [False, True] )==False
assert ( ['one', 'three', 'too'] < {1: 'one'} )==False
assert ( ['one', 'three', 'too'] < {0: 'zero', 1: 'pne'} )==False
assert ( ['one', 'three', 'too'] > 'a string' )==False
assert ( ['one', 'three', 'too'] > 6 )
assert ( ['one', 'three', 'too'] > -2 )
assert ( ['one', 'three', 'too'] > False )
assert ( ['one', 'three', 'too'] > True )
assert ( ['one', 'three', 'too'] > None )
assert ( ['one', 'three', 'too'] > [1, 2, 3] )
assert ( ['one', 'three', 'too'] > ['one', 'two', 'three'] )==False
assert ( ['one', 'three', 'too'] > ['one', 'three', 'too'] )==False
assert ( ['one', 'three', 'too'] > {} )
assert ( ['one', 'three', 'too'] > {(1, 2, 3): []} )
assert ( ['one', 'three', 'too'] > {(1, 't', '3'): []} )
assert ( ['one', 'three', 'too'] > [True, False] )
assert ( ['one', 'three', 'too'] > [False, True] )
assert ( ['one', 'three', 'too'] > {1: 'one'} )
assert ( ['one', 'three', 'too'] > {0: 'zero', 1: 'pne'} )
assert ( ['one', 'three', 'too'] == 'a string' )==False
assert ( ['one', 'three', 'too'] == 6 )==False
assert ( ['one', 'three', 'too'] == -2 )==False
assert ( ['one', 'three', 'too'] == False )==False
assert ( ['one', 'three', 'too'] == True )==False
assert ( ['one', 'three', 'too'] == None )==False
assert ( ['one', 'three', 'too'] == [1, 2, 3] )==False
assert ( ['one', 'three', 'too'] == ['one', 'two', 'three'] )==False
assert ( ['one', 'three', 'too'] == ['one', 'three', 'too'] )
assert ( ['one', 'three', 'too'] == {} )==False
assert ( ['one', 'three', 'too'] == {(1, 2, 3): []} )==False
assert ( ['one', 'three', 'too'] == {(1, 't', '3'): []} )==False
assert ( ['one', 'three', 'too'] == [True, False] )==False
assert ( ['one', 'three', 'too'] == [False, True] )==False
assert ( ['one', 'three', 'too'] == {1: 'one'} )==False
assert ( ['one', 'three', 'too'] == {0: 'zero', 1: 'pne'} )==False
assert ( ['one', 'three', 'too'] <= 'a string' )
assert ( ['one', 'three', 'too'] <= 6 )==False
assert ( ['one', 'three', 'too'] <= -2 )==False
assert ( ['one', 'three', 'too'] <= False )==False
assert ( ['one', 'three', 'too'] <= True )==False
assert ( ['one', 'three', 'too'] <= None )==False
assert ( ['one', 'three', 'too'] <= [1, 2, 3] )==False
assert ( ['one', 'three', 'too'] <= ['one', 'two', 'three'] )
assert ( ['one', 'three', 'too'] <= ['one', 'three', 'too'] )
assert ( ['one', 'three', 'too'] <= {} )==False
assert ( ['one', 'three', 'too'] <= {(1, 2, 3): []} )==False
assert ( ['one', 'three', 'too'] <= {(1, 't', '3'): []} )==False
assert ( ['one', 'three', 'too'] <= [True, False] )==False
assert ( ['one', 'three', 'too'] <= [False, True] )==False
assert ( ['one', 'three', 'too'] <= {1: 'one'} )==False
assert ( ['one', 'three', 'too'] <= {0: 'zero', 1: 'pne'} )==False
assert ( ['one', 'three', 'too'] >= 'a string' )==False
assert ( ['one', 'three', 'too'] >= 6 )
assert ( ['one', 'three', 'too'] >= -2 )
assert ( ['one', 'three', 'too'] >= False )
assert ( ['one', 'three', 'too'] >= True )
assert ( ['one', 'three', 'too'] >= None )
assert ( ['one', 'three', 'too'] >= [1, 2, 3] )
assert ( ['one', 'three', 'too'] >= ['one', 'two', 'three'] )==False
assert ( ['one', 'three', 'too'] >= ['one', 'three', 'too'] )
assert ( ['one', 'three', 'too'] >= {} )
assert ( ['one', 'three', 'too'] >= {(1, 2, 3): []} )
assert ( ['one', 'three', 'too'] >= {(1, 't', '3'): []} )
assert ( ['one', 'three', 'too'] >= [True, False] )
assert ( ['one', 'three', 'too'] >= [False, True] )
assert ( ['one', 'three', 'too'] >= {1: 'one'} )
assert ( ['one', 'three', 'too'] >= {0: 'zero', 1: 'pne'} )
assert ( ['one', 'three', 'too'] != 'a string' )
assert ( ['one', 'three', 'too'] != 6 )
assert ( ['one', 'three', 'too'] != -2 )
assert ( ['one', 'three', 'too'] != False )
assert ( ['one', 'three', 'too'] != True )
assert ( ['one', 'three', 'too'] != None )
assert ( ['one', 'three', 'too'] != [1, 2, 3] )
assert ( ['one', 'three', 'too'] != ['one', 'two', 'three'] )
assert ( ['one', 'three', 'too'] != ['one', 'three', 'too'] )==False
assert ( ['one', 'three', 'too'] != {} )
assert ( ['one', 'three', 'too'] != {(1, 2, 3): []} )
assert ( ['one', 'three', 'too'] != {(1, 't', '3'): []} )
assert ( ['one', 'three', 'too'] != [True, False] )
assert ( ['one', 'three', 'too'] != [False, True] )
assert ( ['one', 'three', 'too'] != {1: 'one'} )
assert ( ['one', 'three', 'too'] != {0: 'zero', 1: 'pne'} )
assert ( {} and 'a string' )=={}
assert ( {} and 6 )=={}
assert ( {} and -2 )=={}
assert ( {} and False )=={}
assert ( {} and True )=={}
assert ( {} and None )=={}
assert ( {} and [1, 2, 3] )=={}
assert ( {} and ['one', 'two', 'three'] )=={}
assert ( {} and ['one', 'three', 'too'] )=={}
assert ( {} and {} )=={}
assert ( {} and {(1, 2, 3): []} )=={}
assert ( {} and {(1, 't', '3'): []} )=={}
assert ( {} and [True, False] )=={}
assert ( {} and [False, True] )=={}
assert ( {} and {1: 'one'} )=={}
assert ( {} and {0: 'zero', 1: 'pne'} )=={}
assert ( {} or 'a string' )=='a string'
assert ( {} or 6 )==6
assert ( {} or -2 )==-2
assert ( {} or False )==False
assert ( {} or True )
assert ( {} or None )==None
assert ( {} or [1, 2, 3] )==[1, 2, 3]
assert ( {} or ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( {} or ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( {} or {} )=={}
assert ( {} or {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( {} or {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( {} or [True, False] )==[True, False]
assert ( {} or [False, True] )==[False, True]
assert ( {} or {1: 'one'} )=={1: 'one'}
assert ( {} or {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( {} < 'a string' )
assert ( {} < 6 )
assert ( {} < -2 )
assert ( {} < False )==False
assert ( {} < True )==False
assert ( {} < None )==False
assert ( {} < [1, 2, 3] )
assert ( {} < ['one', 'two', 'three'] )
assert ( {} < ['one', 'three', 'too'] )
assert ( {} < {} )==False
assert ( {} < {(1, 2, 3): []} )
assert ( {} < {(1, 't', '3'): []} )
assert ( {} < [True, False] )
assert ( {} < [False, True] )
assert ( {} < {1: 'one'} )
assert ( {} < {0: 'zero', 1: 'pne'} )
assert ( {} > 'a string' )==False
assert ( {} > 6 )==False
assert ( {} > -2 )==False
assert ( {} > False )
assert ( {} > True )
assert ( {} > None )
assert ( {} > [1, 2, 3] )==False
assert ( {} > ['one', 'two', 'three'] )==False
assert ( {} > ['one', 'three', 'too'] )==False
assert ( {} > {} )==False
assert ( {} > {(1, 2, 3): []} )==False
assert ( {} > {(1, 't', '3'): []} )==False
assert ( {} > [True, False] )==False
assert ( {} > [False, True] )==False
assert ( {} > {1: 'one'} )==False
assert ( {} > {0: 'zero', 1: 'pne'} )==False
assert ( {} == 'a string' )==False
assert ( {} == 6 )==False
assert ( {} == -2 )==False
assert ( {} == False )==False
assert ( {} == True )==False
assert ( {} == None )==False
assert ( {} == [1, 2, 3] )==False
assert ( {} == ['one', 'two', 'three'] )==False
assert ( {} == ['one', 'three', 'too'] )==False
assert ( {} == {} )
assert ( {} == {(1, 2, 3): []} )==False
assert ( {} == {(1, 't', '3'): []} )==False
assert ( {} == [True, False] )==False
assert ( {} == [False, True] )==False
assert ( {} == {1: 'one'} )==False
assert ( {} == {0: 'zero', 1: 'pne'} )==False
assert ( {} <= 'a string' )
assert ( {} <= 6 )
assert ( {} <= -2 )
assert ( {} <= False )==False
assert ( {} <= True )==False
assert ( {} <= None )==False
assert ( {} <= [1, 2, 3] )
assert ( {} <= ['one', 'two', 'three'] )
assert ( {} <= ['one', 'three', 'too'] )
assert ( {} <= {} )
assert ( {} <= {(1, 2, 3): []} )
assert ( {} <= {(1, 't', '3'): []} )
assert ( {} <= [True, False] )
assert ( {} <= [False, True] )
assert ( {} <= {1: 'one'} )
assert ( {} <= {0: 'zero', 1: 'pne'} )
assert ( {} >= 'a string' )==False
assert ( {} >= 6 )==False
assert ( {} >= -2 )==False
assert ( {} >= False )
assert ( {} >= True )
assert ( {} >= None )
assert ( {} >= [1, 2, 3] )==False
assert ( {} >= ['one', 'two', 'three'] )==False
assert ( {} >= ['one', 'three', 'too'] )==False
assert ( {} >= {} )
assert ( {} >= {(1, 2, 3): []} )==False
assert ( {} >= {(1, 't', '3'): []} )==False
assert ( {} >= [True, False] )==False
assert ( {} >= [False, True] )==False
assert ( {} >= {1: 'one'} )==False
assert ( {} >= {0: 'zero', 1: 'pne'} )==False
assert ( {} != 'a string' )
assert ( {} != 6 )
assert ( {} != -2 )
assert ( {} != False )
assert ( {} != True )
assert ( {} != None )
assert ( {} != [1, 2, 3] )
assert ( {} != ['one', 'two', 'three'] )
assert ( {} != ['one', 'three', 'too'] )
assert ( {} != {} )==False
assert ( {} != {(1, 2, 3): []} )
assert ( {} != {(1, 't', '3'): []} )
assert ( {} != [True, False] )
assert ( {} != [False, True] )
assert ( {} != {1: 'one'} )
assert ( {} != {0: 'zero', 1: 'pne'} )
assert ( {(1, 2, 3): []} and 'a string' )=='a string'
assert ( {(1, 2, 3): []} and 6 )==6
assert ( {(1, 2, 3): []} and -2 )==-2
assert ( {(1, 2, 3): []} and False )==False
assert ( {(1, 2, 3): []} and True )
assert ( {(1, 2, 3): []} and None )==None
assert ( {(1, 2, 3): []} and [1, 2, 3] )==[1, 2, 3]
assert ( {(1, 2, 3): []} and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( {(1, 2, 3): []} and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( {(1, 2, 3): []} and {} )=={}
assert ( {(1, 2, 3): []} and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( {(1, 2, 3): []} and [True, False] )==[True, False]
assert ( {(1, 2, 3): []} and [False, True] )==[False, True]
assert ( {(1, 2, 3): []} and {1: 'one'} )=={1: 'one'}
assert ( {(1, 2, 3): []} and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( {(1, 2, 3): []} or 'a string' )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or 6 )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or -2 )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or False )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or True )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or None )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or [1, 2, 3] )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or ['one', 'two', 'three'] )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or ['one', 'three', 'too'] )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or {} )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or {(1, 't', '3'): []} )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or [True, False] )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or [False, True] )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or {1: 'one'} )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} or {0: 'zero', 1: 'pne'} )=={(1, 2, 3): []}
assert ( {(1, 2, 3): []} < 'a string' )
assert ( {(1, 2, 3): []} < 6 )
assert ( {(1, 2, 3): []} < -2 )
assert ( {(1, 2, 3): []} < False )==False
assert ( {(1, 2, 3): []} < True )==False
assert ( {(1, 2, 3): []} < None )==False
assert ( {(1, 2, 3): []} < [1, 2, 3] )
assert ( {(1, 2, 3): []} < ['one', 'two', 'three'] )
assert ( {(1, 2, 3): []} < ['one', 'three', 'too'] )
assert ( {(1, 2, 3): []} < {} )==False
assert ( {(1, 2, 3): []} < {(1, 2, 3): []} )==False
assert ( {(1, 2, 3): []} < {(1, 't', '3'): []} )
assert ( {(1, 2, 3): []} < [True, False] )
assert ( {(1, 2, 3): []} < [False, True] )
assert ( {(1, 2, 3): []} < {1: 'one'} )==False
assert ( {(1, 2, 3): []} < {0: 'zero', 1: 'pne'} )
assert ( {(1, 2, 3): []} > 'a string' )==False
assert ( {(1, 2, 3): []} > 6 )==False
assert ( {(1, 2, 3): []} > -2 )==False
assert ( {(1, 2, 3): []} > False )
assert ( {(1, 2, 3): []} > True )
assert ( {(1, 2, 3): []} > None )
assert ( {(1, 2, 3): []} > [1, 2, 3] )==False
assert ( {(1, 2, 3): []} > ['one', 'two', 'three'] )==False
assert ( {(1, 2, 3): []} > ['one', 'three', 'too'] )==False
assert ( {(1, 2, 3): []} > {} )
assert ( {(1, 2, 3): []} > {(1, 2, 3): []} )==False
assert ( {(1, 2, 3): []} > {(1, 't', '3'): []} )==False
assert ( {(1, 2, 3): []} > [True, False] )==False
assert ( {(1, 2, 3): []} > [False, True] )==False
assert ( {(1, 2, 3): []} > {1: 'one'} )
assert ( {(1, 2, 3): []} > {0: 'zero', 1: 'pne'} )==False
assert ( {(1, 2, 3): []} == 'a string' )==False
assert ( {(1, 2, 3): []} == 6 )==False
assert ( {(1, 2, 3): []} == -2 )==False
assert ( {(1, 2, 3): []} == False )==False
assert ( {(1, 2, 3): []} == True )==False
assert ( {(1, 2, 3): []} == None )==False
assert ( {(1, 2, 3): []} == [1, 2, 3] )==False
assert ( {(1, 2, 3): []} == ['one', 'two', 'three'] )==False
assert ( {(1, 2, 3): []} == ['one', 'three', 'too'] )==False
assert ( {(1, 2, 3): []} == {} )==False
assert ( {(1, 2, 3): []} == {(1, 2, 3): []} )
assert ( {(1, 2, 3): []} == {(1, 't', '3'): []} )==False
assert ( {(1, 2, 3): []} == [True, False] )==False
assert ( {(1, 2, 3): []} == [False, True] )==False
assert ( {(1, 2, 3): []} == {1: 'one'} )==False
assert ( {(1, 2, 3): []} == {0: 'zero', 1: 'pne'} )==False
assert ( {(1, 2, 3): []} <= 'a string' )
assert ( {(1, 2, 3): []} <= 6 )
assert ( {(1, 2, 3): []} <= -2 )
assert ( {(1, 2, 3): []} <= False )==False
assert ( {(1, 2, 3): []} <= True )==False
assert ( {(1, 2, 3): []} <= None )==False
assert ( {(1, 2, 3): []} <= [1, 2, 3] )
assert ( {(1, 2, 3): []} <= ['one', 'two', 'three'] )
assert ( {(1, 2, 3): []} <= ['one', 'three', 'too'] )
assert ( {(1, 2, 3): []} <= {} )==False
assert ( {(1, 2, 3): []} <= {(1, 2, 3): []} )
assert ( {(1, 2, 3): []} <= {(1, 't', '3'): []} )
assert ( {(1, 2, 3): []} <= [True, False] )
assert ( {(1, 2, 3): []} <= [False, True] )
assert ( {(1, 2, 3): []} <= {1: 'one'} )==False
assert ( {(1, 2, 3): []} <= {0: 'zero', 1: 'pne'} )
assert ( {(1, 2, 3): []} >= 'a string' )==False
assert ( {(1, 2, 3): []} >= 6 )==False
assert ( {(1, 2, 3): []} >= -2 )==False
assert ( {(1, 2, 3): []} >= False )
assert ( {(1, 2, 3): []} >= True )
assert ( {(1, 2, 3): []} >= None )
assert ( {(1, 2, 3): []} >= [1, 2, 3] )==False
assert ( {(1, 2, 3): []} >= ['one', 'two', 'three'] )==False
assert ( {(1, 2, 3): []} >= ['one', 'three', 'too'] )==False
assert ( {(1, 2, 3): []} >= {} )
assert ( {(1, 2, 3): []} >= {(1, 2, 3): []} )
assert ( {(1, 2, 3): []} >= {(1, 't', '3'): []} )==False
assert ( {(1, 2, 3): []} >= [True, False] )==False
assert ( {(1, 2, 3): []} >= [False, True] )==False
assert ( {(1, 2, 3): []} >= {1: 'one'} )
assert ( {(1, 2, 3): []} >= {0: 'zero', 1: 'pne'} )==False
assert ( {(1, 2, 3): []} != 'a string' )
assert ( {(1, 2, 3): []} != 6 )
assert ( {(1, 2, 3): []} != -2 )
assert ( {(1, 2, 3): []} != False )
assert ( {(1, 2, 3): []} != True )
assert ( {(1, 2, 3): []} != None )
assert ( {(1, 2, 3): []} != [1, 2, 3] )
assert ( {(1, 2, 3): []} != ['one', 'two', 'three'] )
assert ( {(1, 2, 3): []} != ['one', 'three', 'too'] )
assert ( {(1, 2, 3): []} != {} )
assert ( {(1, 2, 3): []} != {(1, 2, 3): []} )==False
assert ( {(1, 2, 3): []} != {(1, 't', '3'): []} )
assert ( {(1, 2, 3): []} != [True, False] )
assert ( {(1, 2, 3): []} != [False, True] )
assert ( {(1, 2, 3): []} != {1: 'one'} )
assert ( {(1, 2, 3): []} != {0: 'zero', 1: 'pne'} )
assert ( {(1, 't', '3'): []} and 'a string' )=='a string'
assert ( {(1, 't', '3'): []} and 6 )==6
assert ( {(1, 't', '3'): []} and -2 )==-2
assert ( {(1, 't', '3'): []} and False )==False
assert ( {(1, 't', '3'): []} and True )
assert ( {(1, 't', '3'): []} and None )==None
assert ( {(1, 't', '3'): []} and [1, 2, 3] )==[1, 2, 3]
assert ( {(1, 't', '3'): []} and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( {(1, 't', '3'): []} and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( {(1, 't', '3'): []} and {} )=={}
assert ( {(1, 't', '3'): []} and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( {(1, 't', '3'): []} and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} and [True, False] )==[True, False]
assert ( {(1, 't', '3'): []} and [False, True] )==[False, True]
assert ( {(1, 't', '3'): []} and {1: 'one'} )=={1: 'one'}
assert ( {(1, 't', '3'): []} and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( {(1, 't', '3'): []} or 'a string' )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or 6 )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or -2 )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or False )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or True )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or None )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or [1, 2, 3] )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or ['one', 'two', 'three'] )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or ['one', 'three', 'too'] )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or {} )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or {(1, 2, 3): []} )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or [True, False] )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or [False, True] )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or {1: 'one'} )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} or {0: 'zero', 1: 'pne'} )=={(1, 't', '3'): []}
assert ( {(1, 't', '3'): []} < 'a string' )
assert ( {(1, 't', '3'): []} < 6 )
assert ( {(1, 't', '3'): []} < -2 )
assert ( {(1, 't', '3'): []} < False )==False
assert ( {(1, 't', '3'): []} < True )==False
assert ( {(1, 't', '3'): []} < None )==False
assert ( {(1, 't', '3'): []} < [1, 2, 3] )
assert ( {(1, 't', '3'): []} < ['one', 'two', 'three'] )
assert ( {(1, 't', '3'): []} < ['one', 'three', 'too'] )
assert ( {(1, 't', '3'): []} < {} )==False
assert ( {(1, 't', '3'): []} < {(1, 2, 3): []} )==False
assert ( {(1, 't', '3'): []} < {(1, 't', '3'): []} )==False
assert ( {(1, 't', '3'): []} < [True, False] )
assert ( {(1, 't', '3'): []} < [False, True] )
assert ( {(1, 't', '3'): []} < {1: 'one'} )==False
assert ( {(1, 't', '3'): []} < {0: 'zero', 1: 'pne'} )
assert ( {(1, 't', '3'): []} > 'a string' )==False
assert ( {(1, 't', '3'): []} > 6 )==False
assert ( {(1, 't', '3'): []} > -2 )==False
assert ( {(1, 't', '3'): []} > False )
assert ( {(1, 't', '3'): []} > True )
assert ( {(1, 't', '3'): []} > None )
assert ( {(1, 't', '3'): []} > [1, 2, 3] )==False
assert ( {(1, 't', '3'): []} > ['one', 'two', 'three'] )==False
assert ( {(1, 't', '3'): []} > ['one', 'three', 'too'] )==False
assert ( {(1, 't', '3'): []} > {} )
assert ( {(1, 't', '3'): []} > {(1, 2, 3): []} )
assert ( {(1, 't', '3'): []} > {(1, 't', '3'): []} )==False
assert ( {(1, 't', '3'): []} > [True, False] )==False
assert ( {(1, 't', '3'): []} > [False, True] )==False
assert ( {(1, 't', '3'): []} > {1: 'one'} )
assert ( {(1, 't', '3'): []} > {0: 'zero', 1: 'pne'} )==False
assert ( {(1, 't', '3'): []} == 'a string' )==False
assert ( {(1, 't', '3'): []} == 6 )==False
assert ( {(1, 't', '3'): []} == -2 )==False
assert ( {(1, 't', '3'): []} == False )==False
assert ( {(1, 't', '3'): []} == True )==False
assert ( {(1, 't', '3'): []} == None )==False
assert ( {(1, 't', '3'): []} == [1, 2, 3] )==False
assert ( {(1, 't', '3'): []} == ['one', 'two', 'three'] )==False
assert ( {(1, 't', '3'): []} == ['one', 'three', 'too'] )==False
assert ( {(1, 't', '3'): []} == {} )==False
assert ( {(1, 't', '3'): []} == {(1, 2, 3): []} )==False
assert ( {(1, 't', '3'): []} == {(1, 't', '3'): []} )
assert ( {(1, 't', '3'): []} == [True, False] )==False
assert ( {(1, 't', '3'): []} == [False, True] )==False
assert ( {(1, 't', '3'): []} == {1: 'one'} )==False
assert ( {(1, 't', '3'): []} == {0: 'zero', 1: 'pne'} )==False
assert ( {(1, 't', '3'): []} <= 'a string' )
assert ( {(1, 't', '3'): []} <= 6 )
assert ( {(1, 't', '3'): []} <= -2 )
assert ( {(1, 't', '3'): []} <= False )==False
assert ( {(1, 't', '3'): []} <= True )==False
assert ( {(1, 't', '3'): []} <= None )==False
assert ( {(1, 't', '3'): []} <= [1, 2, 3] )
assert ( {(1, 't', '3'): []} <= ['one', 'two', 'three'] )
assert ( {(1, 't', '3'): []} <= ['one', 'three', 'too'] )
assert ( {(1, 't', '3'): []} <= {} )==False
assert ( {(1, 't', '3'): []} <= {(1, 2, 3): []} )==False
assert ( {(1, 't', '3'): []} <= {(1, 't', '3'): []} )
assert ( {(1, 't', '3'): []} <= [True, False] )
assert ( {(1, 't', '3'): []} <= [False, True] )
assert ( {(1, 't', '3'): []} <= {1: 'one'} )==False
assert ( {(1, 't', '3'): []} <= {0: 'zero', 1: 'pne'} )
assert ( {(1, 't', '3'): []} >= 'a string' )==False
assert ( {(1, 't', '3'): []} >= 6 )==False
assert ( {(1, 't', '3'): []} >= -2 )==False
assert ( {(1, 't', '3'): []} >= False )
assert ( {(1, 't', '3'): []} >= True )
assert ( {(1, 't', '3'): []} >= None )
assert ( {(1, 't', '3'): []} >= [1, 2, 3] )==False
assert ( {(1, 't', '3'): []} >= ['one', 'two', 'three'] )==False
assert ( {(1, 't', '3'): []} >= ['one', 'three', 'too'] )==False
assert ( {(1, 't', '3'): []} >= {} )
assert ( {(1, 't', '3'): []} >= {(1, 2, 3): []} )
assert ( {(1, 't', '3'): []} >= {(1, 't', '3'): []} )
assert ( {(1, 't', '3'): []} >= [True, False] )==False
assert ( {(1, 't', '3'): []} >= [False, True] )==False
assert ( {(1, 't', '3'): []} >= {1: 'one'} )
assert ( {(1, 't', '3'): []} >= {0: 'zero', 1: 'pne'} )==False
assert ( {(1, 't', '3'): []} != 'a string' )
assert ( {(1, 't', '3'): []} != 6 )
assert ( {(1, 't', '3'): []} != -2 )
assert ( {(1, 't', '3'): []} != False )
assert ( {(1, 't', '3'): []} != True )
assert ( {(1, 't', '3'): []} != None )
assert ( {(1, 't', '3'): []} != [1, 2, 3] )
assert ( {(1, 't', '3'): []} != ['one', 'two', 'three'] )
assert ( {(1, 't', '3'): []} != ['one', 'three', 'too'] )
assert ( {(1, 't', '3'): []} != {} )
assert ( {(1, 't', '3'): []} != {(1, 2, 3): []} )
assert ( {(1, 't', '3'): []} != {(1, 't', '3'): []} )==False
assert ( {(1, 't', '3'): []} != [True, False] )
assert ( {(1, 't', '3'): []} != [False, True] )
assert ( {(1, 't', '3'): []} != {1: 'one'} )
assert ( {(1, 't', '3'): []} != {0: 'zero', 1: 'pne'} )
assert ( [True, False] + [1, 2, 3] )==[True, False, 1, 2, 3]
assert ( [True, False] + ['one', 'two', 'three'] )==[True, False, 'one', 'two', 'three']
assert ( [True, False] + ['one', 'three', 'too'] )==[True, False, 'one', 'three', 'too']
assert ( [True, False] + [True, False] )==[True, False, True, False]
assert ( [True, False] + [False, True] )==[True, False, False, True]
assert ( [True, False] * 6 )==[True, False, True, False, True, False, True, False, True, False, True, False]
assert ( [True, False] * -2 )==[]
assert ( [True, False] and 'a string' )=='a string'
assert ( [True, False] and 6 )==6
assert ( [True, False] and -2 )==-2
assert ( [True, False] and False )==False
assert ( [True, False] and True )
assert ( [True, False] and None )==None
assert ( [True, False] and [1, 2, 3] )==[1, 2, 3]
assert ( [True, False] and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( [True, False] and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( [True, False] and {} )=={}
assert ( [True, False] and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( [True, False] and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( [True, False] and [True, False] )==[True, False]
assert ( [True, False] and [False, True] )==[False, True]
assert ( [True, False] and {1: 'one'} )=={1: 'one'}
assert ( [True, False] and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( [True, False] or 'a string' )==[True, False]
assert ( [True, False] or 6 )==[True, False]
assert ( [True, False] or -2 )==[True, False]
assert ( [True, False] or False )==[True, False]
assert ( [True, False] or True )==[True, False]
assert ( [True, False] or None )==[True, False]
assert ( [True, False] or [1, 2, 3] )==[True, False]
assert ( [True, False] or ['one', 'two', 'three'] )==[True, False]
assert ( [True, False] or ['one', 'three', 'too'] )==[True, False]
assert ( [True, False] or {} )==[True, False]
assert ( [True, False] or {(1, 2, 3): []} )==[True, False]
assert ( [True, False] or {(1, 't', '3'): []} )==[True, False]
assert ( [True, False] or [True, False] )==[True, False]
assert ( [True, False] or [False, True] )==[True, False]
assert ( [True, False] or {1: 'one'} )==[True, False]
assert ( [True, False] or {0: 'zero', 1: 'pne'} )==[True, False]
assert ( [True, False] < 'a string' )
assert ( [True, False] < 6 )==False
assert ( [True, False] < -2 )==False
assert ( [True, False] < False )==False
assert ( [True, False] < True )==False
assert ( [True, False] < None )==False
assert ( [True, False] < [1, 2, 3] )
assert ( [True, False] < ['one', 'two', 'three'] )
assert ( [True, False] < ['one', 'three', 'too'] )
assert ( [True, False] < {} )==False
assert ( [True, False] < {(1, 2, 3): []} )==False
assert ( [True, False] < {(1, 't', '3'): []} )==False
assert ( [True, False] < [True, False] )==False
assert ( [True, False] < [False, True] )==False
assert ( [True, False] < {1: 'one'} )==False
assert ( [True, False] < {0: 'zero', 1: 'pne'} )==False
assert ( [True, False] > 'a string' )==False
assert ( [True, False] > 6 )
assert ( [True, False] > -2 )
assert ( [True, False] > False )
assert ( [True, False] > True )
assert ( [True, False] > None )
assert ( [True, False] > [1, 2, 3] )==False
assert ( [True, False] > ['one', 'two', 'three'] )==False
assert ( [True, False] > ['one', 'three', 'too'] )==False
assert ( [True, False] > {} )
assert ( [True, False] > {(1, 2, 3): []} )
assert ( [True, False] > {(1, 't', '3'): []} )
assert ( [True, False] > [True, False] )==False
assert ( [True, False] > [False, True] )
assert ( [True, False] > {1: 'one'} )
assert ( [True, False] > {0: 'zero', 1: 'pne'} )
assert ( [True, False] == 'a string' )==False
assert ( [True, False] == 6 )==False
assert ( [True, False] == -2 )==False
assert ( [True, False] == False )==False
assert ( [True, False] == True )==False
assert ( [True, False] == None )==False
assert ( [True, False] == [1, 2, 3] )==False
assert ( [True, False] == ['one', 'two', 'three'] )==False
assert ( [True, False] == ['one', 'three', 'too'] )==False
assert ( [True, False] == {} )==False
assert ( [True, False] == {(1, 2, 3): []} )==False
assert ( [True, False] == {(1, 't', '3'): []} )==False
assert ( [True, False] == [True, False] )
assert ( [True, False] == [False, True] )==False
assert ( [True, False] == {1: 'one'} )==False
assert ( [True, False] == {0: 'zero', 1: 'pne'} )==False
assert ( [True, False] <= 'a string' )
assert ( [True, False] <= 6 )==False
assert ( [True, False] <= -2 )==False
assert ( [True, False] <= False )==False
assert ( [True, False] <= True )==False
assert ( [True, False] <= None )==False
assert ( [True, False] <= [1, 2, 3] )
assert ( [True, False] <= ['one', 'two', 'three'] )
assert ( [True, False] <= ['one', 'three', 'too'] )
assert ( [True, False] <= {} )==False
assert ( [True, False] <= {(1, 2, 3): []} )==False
assert ( [True, False] <= {(1, 't', '3'): []} )==False
assert ( [True, False] <= [True, False] )
assert ( [True, False] <= [False, True] )==False
assert ( [True, False] <= {1: 'one'} )==False
assert ( [True, False] <= {0: 'zero', 1: 'pne'} )==False
assert ( [True, False] >= 'a string' )==False
assert ( [True, False] >= 6 )
assert ( [True, False] >= -2 )
assert ( [True, False] >= False )
assert ( [True, False] >= True )
assert ( [True, False] >= None )
assert ( [True, False] >= [1, 2, 3] )==False
assert ( [True, False] >= ['one', 'two', 'three'] )==False
assert ( [True, False] >= ['one', 'three', 'too'] )==False
assert ( [True, False] >= {} )
assert ( [True, False] >= {(1, 2, 3): []} )
assert ( [True, False] >= {(1, 't', '3'): []} )
assert ( [True, False] >= [True, False] )
assert ( [True, False] >= [False, True] )
assert ( [True, False] >= {1: 'one'} )
assert ( [True, False] >= {0: 'zero', 1: 'pne'} )
assert ( [True, False] != 'a string' )
assert ( [True, False] != 6 )
assert ( [True, False] != -2 )
assert ( [True, False] != False )
assert ( [True, False] != True )
assert ( [True, False] != None )
assert ( [True, False] != [1, 2, 3] )
assert ( [True, False] != ['one', 'two', 'three'] )
assert ( [True, False] != ['one', 'three', 'too'] )
assert ( [True, False] != {} )
assert ( [True, False] != {(1, 2, 3): []} )
assert ( [True, False] != {(1, 't', '3'): []} )
assert ( [True, False] != [True, False] )==False
assert ( [True, False] != [False, True] )
assert ( [True, False] != {1: 'one'} )
assert ( [True, False] != {0: 'zero', 1: 'pne'} )
assert ( [False, True] + [1, 2, 3] )==[False, True, 1, 2, 3]
assert ( [False, True] + ['one', 'two', 'three'] )==[False, True, 'one', 'two', 'three']
assert ( [False, True] + ['one', 'three', 'too'] )==[False, True, 'one', 'three', 'too']
assert ( [False, True] + [True, False] )==[False, True, True, False]
assert ( [False, True] + [False, True] )==[False, True, False, True]
assert ( [False, True] * 6 )==[False, True, False, True, False, True, False, True, False, True, False, True]
assert ( [False, True] * -2 )==[]
assert ( [False, True] and 'a string' )=='a string'
assert ( [False, True] and 6 )==6
assert ( [False, True] and -2 )==-2
assert ( [False, True] and False )==False
assert ( [False, True] and True )
assert ( [False, True] and None )==None
assert ( [False, True] and [1, 2, 3] )==[1, 2, 3]
assert ( [False, True] and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( [False, True] and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( [False, True] and {} )=={}
assert ( [False, True] and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( [False, True] and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( [False, True] and [True, False] )==[True, False]
assert ( [False, True] and [False, True] )==[False, True]
assert ( [False, True] and {1: 'one'} )=={1: 'one'}
assert ( [False, True] and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( [False, True] or 'a string' )==[False, True]
assert ( [False, True] or 6 )==[False, True]
assert ( [False, True] or -2 )==[False, True]
assert ( [False, True] or False )==[False, True]
assert ( [False, True] or True )==[False, True]
assert ( [False, True] or None )==[False, True]
assert ( [False, True] or [1, 2, 3] )==[False, True]
assert ( [False, True] or ['one', 'two', 'three'] )==[False, True]
assert ( [False, True] or ['one', 'three', 'too'] )==[False, True]
assert ( [False, True] or {} )==[False, True]
assert ( [False, True] or {(1, 2, 3): []} )==[False, True]
assert ( [False, True] or {(1, 't', '3'): []} )==[False, True]
assert ( [False, True] or [True, False] )==[False, True]
assert ( [False, True] or [False, True] )==[False, True]
assert ( [False, True] or {1: 'one'} )==[False, True]
assert ( [False, True] or {0: 'zero', 1: 'pne'} )==[False, True]
assert ( [False, True] < 'a string' )
assert ( [False, True] < 6 )==False
assert ( [False, True] < -2 )==False
assert ( [False, True] < False )==False
assert ( [False, True] < True )==False
assert ( [False, True] < None )==False
assert ( [False, True] < [1, 2, 3] )
assert ( [False, True] < ['one', 'two', 'three'] )
assert ( [False, True] < ['one', 'three', 'too'] )
assert ( [False, True] < {} )==False
assert ( [False, True] < {(1, 2, 3): []} )==False
assert ( [False, True] < {(1, 't', '3'): []} )==False
assert ( [False, True] < [True, False] )
assert ( [False, True] < [False, True] )==False
assert ( [False, True] < {1: 'one'} )==False
assert ( [False, True] < {0: 'zero', 1: 'pne'} )==False
assert ( [False, True] > 'a string' )==False
assert ( [False, True] > 6 )
assert ( [False, True] > -2 )
assert ( [False, True] > False )
assert ( [False, True] > True )
assert ( [False, True] > None )
assert ( [False, True] > [1, 2, 3] )==False
assert ( [False, True] > ['one', 'two', 'three'] )==False
assert ( [False, True] > ['one', 'three', 'too'] )==False
assert ( [False, True] > {} )
assert ( [False, True] > {(1, 2, 3): []} )
assert ( [False, True] > {(1, 't', '3'): []} )
assert ( [False, True] > [True, False] )==False
assert ( [False, True] > [False, True] )==False
assert ( [False, True] > {1: 'one'} )
assert ( [False, True] > {0: 'zero', 1: 'pne'} )
assert ( [False, True] == 'a string' )==False
assert ( [False, True] == 6 )==False
assert ( [False, True] == -2 )==False
assert ( [False, True] == False )==False
assert ( [False, True] == True )==False
assert ( [False, True] == None )==False
assert ( [False, True] == [1, 2, 3] )==False
assert ( [False, True] == ['one', 'two', 'three'] )==False
assert ( [False, True] == ['one', 'three', 'too'] )==False
assert ( [False, True] == {} )==False
assert ( [False, True] == {(1, 2, 3): []} )==False
assert ( [False, True] == {(1, 't', '3'): []} )==False
assert ( [False, True] == [True, False] )==False
assert ( [False, True] == [False, True] )
assert ( [False, True] == {1: 'one'} )==False
assert ( [False, True] == {0: 'zero', 1: 'pne'} )==False
assert ( [False, True] <= 'a string' )
assert ( [False, True] <= 6 )==False
assert ( [False, True] <= -2 )==False
assert ( [False, True] <= False )==False
assert ( [False, True] <= True )==False
assert ( [False, True] <= None )==False
assert ( [False, True] <= [1, 2, 3] )
assert ( [False, True] <= ['one', 'two', 'three'] )
assert ( [False, True] <= ['one', 'three', 'too'] )
assert ( [False, True] <= {} )==False
assert ( [False, True] <= {(1, 2, 3): []} )==False
assert ( [False, True] <= {(1, 't', '3'): []} )==False
assert ( [False, True] <= [True, False] )
assert ( [False, True] <= [False, True] )
assert ( [False, True] <= {1: 'one'} )==False
assert ( [False, True] <= {0: 'zero', 1: 'pne'} )==False
assert ( [False, True] >= 'a string' )==False
assert ( [False, True] >= 6 )
assert ( [False, True] >= -2 )
assert ( [False, True] >= False )
assert ( [False, True] >= True )
assert ( [False, True] >= None )
assert ( [False, True] >= [1, 2, 3] )==False
assert ( [False, True] >= ['one', 'two', 'three'] )==False
assert ( [False, True] >= ['one', 'three', 'too'] )==False
assert ( [False, True] >= {} )
assert ( [False, True] >= {(1, 2, 3): []} )
assert ( [False, True] >= {(1, 't', '3'): []} )
assert ( [False, True] >= [True, False] )==False
assert ( [False, True] >= [False, True] )
assert ( [False, True] >= {1: 'one'} )
assert ( [False, True] >= {0: 'zero', 1: 'pne'} )
assert ( [False, True] != 'a string' )
assert ( [False, True] != 6 )
assert ( [False, True] != -2 )
assert ( [False, True] != False )
assert ( [False, True] != True )
assert ( [False, True] != None )
assert ( [False, True] != [1, 2, 3] )
assert ( [False, True] != ['one', 'two', 'three'] )
assert ( [False, True] != ['one', 'three', 'too'] )
assert ( [False, True] != {} )
assert ( [False, True] != {(1, 2, 3): []} )
assert ( [False, True] != {(1, 't', '3'): []} )
assert ( [False, True] != [True, False] )
assert ( [False, True] != [False, True] )==False
assert ( [False, True] != {1: 'one'} )
assert ( [False, True] != {0: 'zero', 1: 'pne'} )
assert ( {1: 'one'} and 'a string' )=='a string'
assert ( {1: 'one'} and 6 )==6
assert ( {1: 'one'} and -2 )==-2
assert ( {1: 'one'} and False )==False
assert ( {1: 'one'} and True )
assert ( {1: 'one'} and None )==None
assert ( {1: 'one'} and [1, 2, 3] )==[1, 2, 3]
assert ( {1: 'one'} and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( {1: 'one'} and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( {1: 'one'} and {} )=={}
assert ( {1: 'one'} and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( {1: 'one'} and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( {1: 'one'} and [True, False] )==[True, False]
assert ( {1: 'one'} and [False, True] )==[False, True]
assert ( {1: 'one'} and {1: 'one'} )=={1: 'one'}
assert ( {1: 'one'} and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( {1: 'one'} or 'a string' )=={1: 'one'}
assert ( {1: 'one'} or 6 )=={1: 'one'}
assert ( {1: 'one'} or -2 )=={1: 'one'}
assert ( {1: 'one'} or False )=={1: 'one'}
assert ( {1: 'one'} or True )=={1: 'one'}
assert ( {1: 'one'} or None )=={1: 'one'}
assert ( {1: 'one'} or [1, 2, 3] )=={1: 'one'}
assert ( {1: 'one'} or ['one', 'two', 'three'] )=={1: 'one'}
assert ( {1: 'one'} or ['one', 'three', 'too'] )=={1: 'one'}
assert ( {1: 'one'} or {} )=={1: 'one'}
assert ( {1: 'one'} or {(1, 2, 3): []} )=={1: 'one'}
assert ( {1: 'one'} or {(1, 't', '3'): []} )=={1: 'one'}
assert ( {1: 'one'} or [True, False] )=={1: 'one'}
assert ( {1: 'one'} or [False, True] )=={1: 'one'}
assert ( {1: 'one'} or {1: 'one'} )=={1: 'one'}
assert ( {1: 'one'} or {0: 'zero', 1: 'pne'} )=={1: 'one'}
assert ( {1: 'one'} < 'a string' )
assert ( {1: 'one'} < 6 )
assert ( {1: 'one'} < -2 )
assert ( {1: 'one'} < False )==False
assert ( {1: 'one'} < True )==False
assert ( {1: 'one'} < None )==False
assert ( {1: 'one'} < [1, 2, 3] )
assert ( {1: 'one'} < ['one', 'two', 'three'] )
assert ( {1: 'one'} < ['one', 'three', 'too'] )
assert ( {1: 'one'} < {} )==False
assert ( {1: 'one'} < {(1, 2, 3): []} )
assert ( {1: 'one'} < {(1, 't', '3'): []} )
assert ( {1: 'one'} < [True, False] )
assert ( {1: 'one'} < [False, True] )
assert ( {1: 'one'} < {1: 'one'} )==False
assert ( {1: 'one'} < {0: 'zero', 1: 'pne'} )
assert ( {1: 'one'} > 'a string' )==False
assert ( {1: 'one'} > 6 )==False
assert ( {1: 'one'} > -2 )==False
assert ( {1: 'one'} > False )
assert ( {1: 'one'} > True )
assert ( {1: 'one'} > None )
assert ( {1: 'one'} > [1, 2, 3] )==False
assert ( {1: 'one'} > ['one', 'two', 'three'] )==False
assert ( {1: 'one'} > ['one', 'three', 'too'] )==False
assert ( {1: 'one'} > {} )
assert ( {1: 'one'} > {(1, 2, 3): []} )==False
assert ( {1: 'one'} > {(1, 't', '3'): []} )==False
assert ( {1: 'one'} > [True, False] )==False
assert ( {1: 'one'} > [False, True] )==False
assert ( {1: 'one'} > {1: 'one'} )==False
assert ( {1: 'one'} > {0: 'zero', 1: 'pne'} )==False
assert ( {1: 'one'} == 'a string' )==False
assert ( {1: 'one'} == 6 )==False
assert ( {1: 'one'} == -2 )==False
assert ( {1: 'one'} == False )==False
assert ( {1: 'one'} == True )==False
assert ( {1: 'one'} == None )==False
assert ( {1: 'one'} == [1, 2, 3] )==False
assert ( {1: 'one'} == ['one', 'two', 'three'] )==False
assert ( {1: 'one'} == ['one', 'three', 'too'] )==False
assert ( {1: 'one'} == {} )==False
assert ( {1: 'one'} == {(1, 2, 3): []} )==False
assert ( {1: 'one'} == {(1, 't', '3'): []} )==False
assert ( {1: 'one'} == [True, False] )==False
assert ( {1: 'one'} == [False, True] )==False
assert ( {1: 'one'} == {1: 'one'} )
assert ( {1: 'one'} == {0: 'zero', 1: 'pne'} )==False
assert ( {1: 'one'} <= 'a string' )
assert ( {1: 'one'} <= 6 )
assert ( {1: 'one'} <= -2 )
assert ( {1: 'one'} <= False )==False
assert ( {1: 'one'} <= True )==False
assert ( {1: 'one'} <= None )==False
assert ( {1: 'one'} <= [1, 2, 3] )
assert ( {1: 'one'} <= ['one', 'two', 'three'] )
assert ( {1: 'one'} <= ['one', 'three', 'too'] )
assert ( {1: 'one'} <= {} )==False
assert ( {1: 'one'} <= {(1, 2, 3): []} )
assert ( {1: 'one'} <= {(1, 't', '3'): []} )
assert ( {1: 'one'} <= [True, False] )
assert ( {1: 'one'} <= [False, True] )
assert ( {1: 'one'} <= {1: 'one'} )
assert ( {1: 'one'} <= {0: 'zero', 1: 'pne'} )
assert ( {1: 'one'} >= 'a string' )==False
assert ( {1: 'one'} >= 6 )==False
assert ( {1: 'one'} >= -2 )==False
assert ( {1: 'one'} >= False )
assert ( {1: 'one'} >= True )
assert ( {1: 'one'} >= None )
assert ( {1: 'one'} >= [1, 2, 3] )==False
assert ( {1: 'one'} >= ['one', 'two', 'three'] )==False
assert ( {1: 'one'} >= ['one', 'three', 'too'] )==False
assert ( {1: 'one'} >= {} )
assert ( {1: 'one'} >= {(1, 2, 3): []} )==False
assert ( {1: 'one'} >= {(1, 't', '3'): []} )==False
assert ( {1: 'one'} >= [True, False] )==False
assert ( {1: 'one'} >= [False, True] )==False
assert ( {1: 'one'} >= {1: 'one'} )
assert ( {1: 'one'} >= {0: 'zero', 1: 'pne'} )==False
assert ( {1: 'one'} != 'a string' )
assert ( {1: 'one'} != 6 )
assert ( {1: 'one'} != -2 )
assert ( {1: 'one'} != False )
assert ( {1: 'one'} != True )
assert ( {1: 'one'} != None )
assert ( {1: 'one'} != [1, 2, 3] )
assert ( {1: 'one'} != ['one', 'two', 'three'] )
assert ( {1: 'one'} != ['one', 'three', 'too'] )
assert ( {1: 'one'} != {} )
assert ( {1: 'one'} != {(1, 2, 3): []} )
assert ( {1: 'one'} != {(1, 't', '3'): []} )
assert ( {1: 'one'} != [True, False] )
assert ( {1: 'one'} != [False, True] )
assert ( {1: 'one'} != {1: 'one'} )==False
assert ( {1: 'one'} != {0: 'zero', 1: 'pne'} )
assert ( {0: 'zero', 1: 'pne'} and 'a string' )=='a string'
assert ( {0: 'zero', 1: 'pne'} and 6 )==6
assert ( {0: 'zero', 1: 'pne'} and -2 )==-2
assert ( {0: 'zero', 1: 'pne'} and False )==False
assert ( {0: 'zero', 1: 'pne'} and True )
assert ( {0: 'zero', 1: 'pne'} and None )==None
assert ( {0: 'zero', 1: 'pne'} and [1, 2, 3] )==[1, 2, 3]
assert ( {0: 'zero', 1: 'pne'} and ['one', 'two', 'three'] )==['one', 'two', 'three']
assert ( {0: 'zero', 1: 'pne'} and ['one', 'three', 'too'] )==['one', 'three', 'too']
assert ( {0: 'zero', 1: 'pne'} and {} )=={}
assert ( {0: 'zero', 1: 'pne'} and {(1, 2, 3): []} )=={(1, 2, 3): []}
assert ( {0: 'zero', 1: 'pne'} and {(1, 't', '3'): []} )=={(1, 't', '3'): []}
assert ( {0: 'zero', 1: 'pne'} and [True, False] )==[True, False]
assert ( {0: 'zero', 1: 'pne'} and [False, True] )==[False, True]
assert ( {0: 'zero', 1: 'pne'} and {1: 'one'} )=={1: 'one'}
assert ( {0: 'zero', 1: 'pne'} and {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or 'a string' )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or 6 )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or -2 )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or False )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or True )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or None )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or [1, 2, 3] )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or ['one', 'two', 'three'] )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or ['one', 'three', 'too'] )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or {} )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or {(1, 2, 3): []} )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or {(1, 't', '3'): []} )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or [True, False] )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or [False, True] )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or {1: 'one'} )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} or {0: 'zero', 1: 'pne'} )=={0: 'zero', 1: 'pne'}
assert ( {0: 'zero', 1: 'pne'} < 'a string' )
assert ( {0: 'zero', 1: 'pne'} < 6 )
assert ( {0: 'zero', 1: 'pne'} < -2 )
assert ( {0: 'zero', 1: 'pne'} < False )==False
assert ( {0: 'zero', 1: 'pne'} < True )==False
assert ( {0: 'zero', 1: 'pne'} < None )==False
assert ( {0: 'zero', 1: 'pne'} < [1, 2, 3] )
assert ( {0: 'zero', 1: 'pne'} < ['one', 'two', 'three'] )
assert ( {0: 'zero', 1: 'pne'} < ['one', 'three', 'too'] )
assert ( {0: 'zero', 1: 'pne'} < {} )==False
assert ( {0: 'zero', 1: 'pne'} < {(1, 2, 3): []} )==False
assert ( {0: 'zero', 1: 'pne'} < {(1, 't', '3'): []} )==False
assert ( {0: 'zero', 1: 'pne'} < [True, False] )
assert ( {0: 'zero', 1: 'pne'} < [False, True] )
assert ( {0: 'zero', 1: 'pne'} < {1: 'one'} )==False
assert ( {0: 'zero', 1: 'pne'} < {0: 'zero', 1: 'pne'} )==False
assert ( {0: 'zero', 1: 'pne'} > 'a string' )==False
assert ( {0: 'zero', 1: 'pne'} > 6 )==False
assert ( {0: 'zero', 1: 'pne'} > -2 )==False
assert ( {0: 'zero', 1: 'pne'} > False )
assert ( {0: 'zero', 1: 'pne'} > True )
assert ( {0: 'zero', 1: 'pne'} > None )
assert ( {0: 'zero', 1: 'pne'} > [1, 2, 3] )==False
assert ( {0: 'zero', 1: 'pne'} > ['one', 'two', 'three'] )==False
assert ( {0: 'zero', 1: 'pne'} > ['one', 'three', 'too'] )==False
assert ( {0: 'zero', 1: 'pne'} > {} )
assert ( {0: 'zero', 1: 'pne'} > {(1, 2, 3): []} )
assert ( {0: 'zero', 1: 'pne'} > {(1, 't', '3'): []} )
assert ( {0: 'zero', 1: 'pne'} > [True, False] )==False
assert ( {0: 'zero', 1: 'pne'} > [False, True] )==False
assert ( {0: 'zero', 1: 'pne'} > {1: 'one'} )
assert ( {0: 'zero', 1: 'pne'} > {0: 'zero', 1: 'pne'} )==False
assert ( {0: 'zero', 1: 'pne'} == 'a string' )==False
assert ( {0: 'zero', 1: 'pne'} == 6 )==False
assert ( {0: 'zero', 1: 'pne'} == -2 )==False
assert ( {0: 'zero', 1: 'pne'} == False )==False
assert ( {0: 'zero', 1: 'pne'} == True )==False
assert ( {0: 'zero', 1: 'pne'} == None )==False
assert ( {0: 'zero', 1: 'pne'} == [1, 2, 3] )==False
assert ( {0: 'zero', 1: 'pne'} == ['one', 'two', 'three'] )==False
assert ( {0: 'zero', 1: 'pne'} == ['one', 'three', 'too'] )==False
assert ( {0: 'zero', 1: 'pne'} == {} )==False
assert ( {0: 'zero', 1: 'pne'} == {(1, 2, 3): []} )==False
assert ( {0: 'zero', 1: 'pne'} == {(1, 't', '3'): []} )==False
assert ( {0: 'zero', 1: 'pne'} == [True, False] )==False
assert ( {0: 'zero', 1: 'pne'} == [False, True] )==False
assert ( {0: 'zero', 1: 'pne'} == {1: 'one'} )==False
assert ( {0: 'zero', 1: 'pne'} == {0: 'zero', 1: 'pne'} )
assert ( {0: 'zero', 1: 'pne'} <= 'a string' )
assert ( {0: 'zero', 1: 'pne'} <= 6 )
assert ( {0: 'zero', 1: 'pne'} <= -2 )
assert ( {0: 'zero', 1: 'pne'} <= False )==False
assert ( {0: 'zero', 1: 'pne'} <= True )==False
assert ( {0: 'zero', 1: 'pne'} <= None )==False
assert ( {0: 'zero', 1: 'pne'} <= [1, 2, 3] )
assert ( {0: 'zero', 1: 'pne'} <= ['one', 'two', 'three'] )
assert ( {0: 'zero', 1: 'pne'} <= ['one', 'three', 'too'] )
assert ( {0: 'zero', 1: 'pne'} <= {} )==False
assert ( {0: 'zero', 1: 'pne'} <= {(1, 2, 3): []} )==False
assert ( {0: 'zero', 1: 'pne'} <= {(1, 't', '3'): []} )==False
assert ( {0: 'zero', 1: 'pne'} <= [True, False] )
assert ( {0: 'zero', 1: 'pne'} <= [False, True] )
assert ( {0: 'zero', 1: 'pne'} <= {1: 'one'} )==False
assert ( {0: 'zero', 1: 'pne'} <= {0: 'zero', 1: 'pne'} )
assert ( {0: 'zero', 1: 'pne'} >= 'a string' )==False
assert ( {0: 'zero', 1: 'pne'} >= 6 )==False
assert ( {0: 'zero', 1: 'pne'} >= -2 )==False
assert ( {0: 'zero', 1: 'pne'} >= False )
assert ( {0: 'zero', 1: 'pne'} >= True )
assert ( {0: 'zero', 1: 'pne'} >= None )
assert ( {0: 'zero', 1: 'pne'} >= [1, 2, 3] )==False
assert ( {0: 'zero', 1: 'pne'} >= ['one', 'two', 'three'] )==False
assert ( {0: 'zero', 1: 'pne'} >= ['one', 'three', 'too'] )==False
assert ( {0: 'zero', 1: 'pne'} >= {} )
assert ( {0: 'zero', 1: 'pne'} >= {(1, 2, 3): []} )
assert ( {0: 'zero', 1: 'pne'} >= {(1, 't', '3'): []} )
assert ( {0: 'zero', 1: 'pne'} >= [True, False] )==False
assert ( {0: 'zero', 1: 'pne'} >= [False, True] )==False
assert ( {0: 'zero', 1: 'pne'} >= {1: 'one'} )
assert ( {0: 'zero', 1: 'pne'} >= {0: 'zero', 1: 'pne'} )
assert ( {0: 'zero', 1: 'pne'} != 'a string' )
assert ( {0: 'zero', 1: 'pne'} != 6 )
assert ( {0: 'zero', 1: 'pne'} != -2 )
assert ( {0: 'zero', 1: 'pne'} != False )
assert ( {0: 'zero', 1: 'pne'} != True )
assert ( {0: 'zero', 1: 'pne'} != None )
assert ( {0: 'zero', 1: 'pne'} != [1, 2, 3] )
assert ( {0: 'zero', 1: 'pne'} != ['one', 'two', 'three'] )
assert ( {0: 'zero', 1: 'pne'} != ['one', 'three', 'too'] )
assert ( {0: 'zero', 1: 'pne'} != {} )
assert ( {0: 'zero', 1: 'pne'} != {(1, 2, 3): []} )
assert ( {0: 'zero', 1: 'pne'} != {(1, 't', '3'): []} )
assert ( {0: 'zero', 1: 'pne'} != [True, False] )
assert ( {0: 'zero', 1: 'pne'} != [False, True] )
assert ( {0: 'zero', 1: 'pne'} != {1: 'one'} )
assert ( {0: 'zero', 1: 'pne'} != {0: 'zero', 1: 'pne'} )==False
