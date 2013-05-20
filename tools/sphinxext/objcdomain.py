'''
Created on Jul 23, 2011

@author: mathos
'''

from sphinx.locale import l_, _
from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.directives import ObjectDescription
from docutils import nodes
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from sphinxlex import SphinxLexer

class ObjCObject(ObjectDescription):
	"""Description of a ObjC language object."""


	def add_target_and_index(self, sigobj, sig, signode):
		pass
	
	def before_content(self):
		pass

	def after_content(self):
		pass
	




	def handle_signature(self, sig, signode):
		
		def p_method_parts(p):
			'''method : returnval WORD
			          | returnval WORD COLON  parameters'''
			if (len(p) == 5):
				p[0] = p[1] 
				p[0] += nodes.Text(u' ')
				p[0] += addnodes.desc_name(p[2], p[2])
				p[0] += addnodes.desc_annotation(p[3], p[3])
				p[0] += p[4]
			else:
				p[0] = p[1] 
				p[0] += nodes.Text(u' ')
				p[0] += addnodes.desc_name(p[2], p[2])
		
		def p_expression_word(p):
			'''expression : WORD
		                  | WORD STAR
		                  | VOID '''
			if (len(p) == 3):
				p[0] = addnodes.desc_type(p[1], p[1])
				p[0] += addnodes.desc_addname(p[2], p[2])
			else:
				p[0] = addnodes.desc_type(p[1], p[1])

		
			
		def p_parameter_exp(p):
			'''parameter  : methodname COLON LPAREN expression RPAREN methodname
			              | parameter parameter'''

			if (len(p) == 7):
				p[0] = p[1]
				p[0] += addnodes.desc_annotation(p[2], p[2])
				p[0] += addnodes.desc_annotation(p[3], p[3])
				p[0] += nodes.Text(u' ')
				p[0] += p[4]
				p[0] += nodes.Text(u' ')
				p[0] += addnodes.desc_annotation(p[5], p[5])
				p[0] += p[6]
		
			else:
				p[0] = p[1]
				p[0] += nodes.Text(u' ')
				p[0] += p[2]
		
		def p_parameters_exp(p):
			'''parameters : LPAREN expression RPAREN methodname
			              | LPAREN expression RPAREN methodname parameter'''
			p[0] = addnodes.desc_annotation(p[1], p[1])
			p[0] += nodes.Text(u' ')
			p[0] += p[2]
			p[0] += nodes.Text(u' ')
			p[0] += addnodes.desc_annotation(p[3], p[3])
			p[0] += p[4] 

			if (len(p) == 6):
				p[0] += nodes.Text(u' ')
				p[0] += p[5]
				
				
				
		def p_method_word(p):
			'''methodname : WORD'''
			p[0] = addnodes.desc_type(p[1], p[1])		
		
		
		def p_returnval_expr(p):
			'''returnval : MINUS LPAREN expression RPAREN
			             | PLUS LPAREN expression RPAREN'''
			p[0] = addnodes.desc_annotation(p[1], p[1]) 
			p[0] += nodes.Text(u' ')
			p[0] += addnodes.desc_annotation(p[2], p[2])
			p[0] += nodes.Text(u' ')
 			p[0] += p[3] 
			p[0] += nodes.Text(u' ')
			p[0] += addnodes.desc_annotation(p[4], p[4]) 
		
		# Error rule for syntax errors
		def p_error(p):
			print "Syntax error in input!"

		
		
		
		lex = SphinxLexer()
		lex.build()
		
		#I know this looks like this is just setting out here, but this is used
		#by yacc to find the tokens.
		tokens = lex.tokens	

		parser = yacc.yacc(write_tables=0,debug=0)
		result = parser.parse(sig)
		signode += result
		return result;	
	
class ObjCClassObject(ObjCObject):

	def get_index_text(self, name):
		return _('%s (ObjC class)') % name



class ObjectiveCDomain(Domain):
	"""ObjC language domain."""
	name = 'objc'
	label = 'ObjectiveC'
	object_types = {
		'method':	ObjType(l_('method'),	'method'),
	}

	directives = {
		'method':		 ObjCClassObject,
	}
	initial_data = {
		'objects': {},	# fullname -> docname, objtype
	}


	def clear_doc(self, docname):
		for fullname, (fn, _) in self.data['objects'].items():
			if fn == docname:
				del self.data['objects'][fullname]


	def resolve_xref(self, env, fromdocname, builder,
					 typ, target, node, contnode):
		pass
	
	def get_objects(self):
		for refname, (docname, type) in self.data['objects'].iteritems():
			yield (refname, refname, type, docname, refname, 1)


def setup(app):
	app.add_domain(ObjectiveCDomain)
