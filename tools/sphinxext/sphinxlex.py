'''
Created on Jul 22, 2011

@author: mathos
'''
import ply.lex as lex

reserved = { 'void' : 'VOID' }

class SphinxLexer:
	# List of token names.   This is always required
	
	tokens = list(reserved.values()) + [
		'WORD',
	   'PLUS',
	   'MINUS',
	   'STAR',
	   'LPAREN',
	   'RPAREN',
	   'COLON',
	] 

	# Regular expression rules for simple tokens
#	t_LITER =r'[a-zA-Z_]?(\.|[^\"])*'
#	t_CONST = r"[a-zA-Z_]?(\.|[^\'])+"
	#t_L = r'[a-zA-Z_]'
#	t_CONST = r"[a-zA-Z_]?'(\\.|[^'])+'"
#	t_STRING_LITERAL = '[a-zA-Z_]?"(\\.|[^"])*"'
	#t_WORD = r"[LuU8]?('([^'\\]*(?:\\.[^'\\]*)*)'" r'|"([^"\\]*(?:\\.[^"\\]*)*)")'

	
	t_PLUS	= r'\+'
	t_MINUS   = r'-'
	t_STAR   = r'\*'
	t_LPAREN  = r'\('
	t_RPAREN  = r'\)'
	t_COLON = r':'
	
	def t_WORD(self,t):
		r'(~?\b[a-zA-Z_][a-zA-Z0-9_]*)\b'
		t.type = reserved.get(t.value.lower(),'WORD')	# Check for reserved words
		return t

	# A regular expression rule with some action code
	# Note addition of self parameter since we're in a class
#	def t_NUMBER(self,t):
#		r'\d+'
#		t.value = int(t.value)	
#		return t

	# Define a rule so we can track line numbers
	def t_newline(self,t):
		r'\n+'
		t.lexer.lineno += len(t.value)

	# A string containing ignored characters (spaces and tabs)
	t_ignore  = ' \t'

	# Error handling rule
	def t_error(self,t):
		print "Illegal character '%s'" % t.value[0]
		t.lexer.skip(1)

	# Build the lexer
	def build(self,**kwargs):
		self.lexer = lex.lex(module=self, **kwargs)
	
	# Test it output
	def test(self,data):
		self.lexer.input(data)
		while True:
			tok = self.lexer.token()
			if not tok: break
			print tok