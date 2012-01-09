
#    1 x=3+4

    0 PUSH_INT 3
    3 PUSH_INT 4
    6 ADD
    7 STORE_NAME 0   	# string 0 = 'x'

#    2 if x>5:

   10 LOAD_NAME 0   	# string 0 = 'x'
   13 PUSH_INT 5
   16 GT
   17 IF_FALSE 28

#    3   print "greater"

   20 PUSH_STR 1   	# string 1 = 'greater'
   23 PUSH_TRUE
   24 PUSH_INT 1
   27 PRINT

#    5 def fact(n):

   28 MAKE_METHOD 37
   31 STORE_NAME 2   	# string 2 = 'fact'
   34 GOTO 77
   37 PUSH_INT 1
   40 FUNCTION_PROLOG
   41 STORE_NAME 3   	# string 3 = 'n'

#    6   if n<=1:

   44 LOAD_NAME 3   	# string 3 = 'n'
   47 PUSH_INT 1
   50 LTE
   51 IF_FALSE 58

#    7      return 1

   54 PUSH_INT 1
   57 RETURN

#    8   return n*fact(n-1)

   58 LOAD_NAME 3   	# string 3 = 'n'
   61 LOAD_NAME 3   	# string 3 = 'n'
   64 PUSH_INT 1
   67 SUB
   68 PUSH_INT 1
   71 LOAD_NAME 2   	# string 2 = 'fact'
   74 CALL
   75 MULT
   76 RETURN

#   10 print fact(10)

   77 PUSH_INT 10
   80 PUSH_INT 1
   83 LOAD_NAME 2   	# string 2 = 'fact'
   86 CALL
   87 PUSH_TRUE
   88 PUSH_INT 1
   91 PRINT
   92 EXIT_LOOP
