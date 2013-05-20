'''
Created on Jul 22, 2011

@author: mathos
'''
# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from sphinxcontrib.sphinxlex import SphinxLexer

def p_method_parts(p):
	'''method : returnval methodname
	          | returnval methodname COLON  parameters'''
	if (len(p) == 5):
		p[0] = p[1] +' ' + p[2]+p[3]+p[4]

	else:
		p[0] = p[1] +' ' + p[2]

def p_expression_word(p):
	'''expression : WORD
                  | WORD STAR
                  | VOID '''
	print p[1]
	if (len(p) == 3):
		p[0] = p[1] +' '+p[2]
	else:
		p[0] = p[1]

	
def p_parameter_exp(p):
	'''parameter  : WORD COLON LPAREN expression RPAREN WORD
	              | parameter parameter'''
	print "param1 "+p[1] +' '+p[2]+' '+p[3]+' '+p[4]
	if (len(p) == 7):
		p[0] = p[1] + p[2]+p[3]+' '+p[4]+' '+p[5]+p[6]

	else:
		p[0] = p[1] +' ' + p[2]

def p_parameters_exp(p):
	'''parameters : LPAREN expression RPAREN WORD
	              | LPAREN expression RPAREN WORD parameter'''
	print "param"+p[1] +' '+p[2]+' '+p[3]+' '+p[4]
	if (len(p) == 6):
		p[0] = p[1] +' '+p[2]+' '+p[3]+p[4] +' '+p[5]

	else :
		p[0] = p[1] +' '+p[2]+' '+p[3]+p[4]


def p_method_word(p):
	'''methodname : WORD'''
	
	print "Method: "+p[1]
	p[0] = p[1]


def p_factor_num(p):
	'''factor : NUMBER'''
	p[0] = p[1]



def p_returnval_expr(p):
	'''returnval : MINUS LPAREN expression RPAREN
	             | PLUS LPAREN expression RPAREN'''
	print "HERE "+p[3]

	p[0] = p[1] + ' '+ p[2] + ' '+ p[3] + ' '+p[4] 

# Error rule for syntax errors
def p_error(p):
	print "Syntax error in input!"

# Build the parser
lex = SphinxLexer()
lex.build()

tokens = lex.tokens	

	
parser = yacc.yacc()

while True:
	try:
		s = raw_input('calc > ')
	except EOFError:
		break
	if not s: continue
	result = parser.parse(s)
	print result