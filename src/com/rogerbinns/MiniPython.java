package com.rogerbinns;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class MiniPython {

	String[] strings;
	int[][] linenumbers;
	byte[] code;
	boolean hasRun;

	Context root;
	Context current;
	Object[] stack;
	int stacktop;

	public void setCode(InputStream is) throws IOException, ExecutionError {
		hasRun=false;

		// string table
		int stablen=get16(is);
		strings=new String[stablen];
		for(int i=0; i<stablen; i++) {
			strings[i]=getUTF(is, get16(is));
		}
		// line numbers
		int ltablen=get16(is);
		linenumbers=new int[ltablen][2];
		for(int i=0; i<ltablen; i++) {
			linenumbers[i][0]=get16(is);
			linenumbers[i][1]=get16(is);
		}
		// code
		int codelen=get16(is);
		code=new byte[codelen];
		if(is.read(code)!=codelen)
			throw new EOFException();

		firstRun();
	}

	private static final int get16(InputStream is) throws IOException {
		int a=is.read(),
				b=is.read();
		if(a<0 || b<0)
			throw new EOFException();
		return a+(b<<8);
	}

	private static final String getUTF(InputStream is, int byteslen) throws IOException {
		byte[] b=new byte[byteslen];
		// ::TODO:: while loop dealing with incomplete reads
		if(is.read(b)!=byteslen)
			throw new EOFException();
		return new String(b, "UTF8");
	}

	private final void firstRun() throws ExecutionError {
		root=new Context(0, null);
		stack=new Object[256];
		stacktop=-1;
		mainLoop(root);
	}

	private final class Context {
		Context parent;
		Map<String,Object> names;
		Set<String> globals; // only initialized if needed
		int pc;
		Context(int pc, Context parent) {
			this.pc=pc;
			this.parent=parent;
			names=new HashMap<String,Object>();
		}
		void addGlobal(String s) {
			if(globals==null) {
				globals=new HashSet<String>();
			}
			globals.add(s);
		}
	}

	// Our internal types.  We use Java native types wherever possible
	private static final class TMethod {
		// address of method in bytecode
		int addr;
		TMethod(int addr) {
			this.addr=addr;
		}
		public String toString() {
			return String.format("<method at %d>", addr);
		}
	}

	private final Object mainLoop(Context context) throws ExecutionError {
		if(true) {
			current=context;
			return _mainLoop();
		} else {
			int savedstacktop=stacktop;
			Context savedcontext=current;
			current=context;
			try {
				return _mainLoop();
			} finally {
				stacktop=savedstacktop;
				current=savedcontext;
			}
		}
	}

	private final Object _mainLoop() throws ExecutionError {
		int op, val=-1;
		opcodeswitch:
			while(true) {
				op=code[current.pc] & 0xff;
				current.pc++;
				if(op>=128) {
					val=(code[current.pc]&0xff)+((code[current.pc+1]&0xff)<<8);
					current.pc+=2;
				}
				switch(op) {
				// -- check start : marker used by tool

				// Control flow codes
				case 19: // EXIT_LOOP
				{
					return null;
				}
				case 129: // GOTO
				{
					current.pc=val;
					continue;
				}
				// Mostly harmless/lightweight codes
				case 11: // POP_TOP
				{
					stacktop--;
					continue;
				}
				// Codes that make the stack bigger
				case 200: // PUSH_INT
				{
					try {
						stack[++stacktop]=val;
					} catch(ArrayIndexOutOfBoundsException e) {
						extendStack();
						current.pc-=3;
						stacktop--;
					}
					continue;
				}
				case 201: // PUSH_INT_HI
				{
					stack[stacktop]=((Integer)stack[stacktop])|(val<<16);
					continue;
				}
				case 162: // PUSH_STR
				{
					try {
						stack[++stacktop]=strings[val];
					} catch(ArrayIndexOutOfBoundsException e) {
						extendStack();
						current.pc-=3;
						stacktop--;
					}
					continue;
				}
				case 18: // PUSH_NONE
				case 21: // PUSH_TRUE
				case 22: // PUSH_FALSE
				{
					try {
						stack[++stacktop]=(op==18)?null:(op==21);
					} catch(ArrayIndexOutOfBoundsException e) {
						extendStack();
						current.pc-=3;
						stacktop--;
					}
					continue;
				}
				case 160: // LOAD_NAME
				{
					try {
						Context c=current;
						String key=strings[val];
						while(c!=null) {
							if(c.names.containsKey(key)) {
								stack[++stacktop]=c.names.get(key);
								continue opcodeswitch;
							}
							c=c.parent;
						}
						internalError("NameError", String.format("name '%s' is not defined", key));
					} catch(ArrayIndexOutOfBoundsException e) {
						extendStack();
						current.pc-=3;
						stacktop--;
						continue;
					}
				}

				// Binary operations
				case 2: // MULT
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					if(left instanceof Integer && right instanceof Integer) {
						stack[++stacktop]=(Integer)left*(Integer)right;
						continue;
					}
					if(left instanceof String && right instanceof Integer) {
						String s=(String)left;
						Integer ii=(Integer)right;
						StringBuilder sb=new StringBuilder(s.length()*ii);
						for(int i=0; i<ii; i++) {
							sb.append(s);
						}
						stack[++stacktop]=sb.toString();
						continue;
					}
					internalErrorBinaryOp("TypeError", "multiply", left, right);
				}
				case 13: // UNARY_NEG
					if(stack[stacktop] instanceof Integer) {
						stack[stacktop]=-(Integer)stack[stacktop];
						continue;
					} else {
						internalError("TypeError", "Can only negate integers");
					}

					// More heavyweight stuff
				case 20: // STR
				{
					if(!(stack[stacktop] instanceof String)) {
						Object o=stack[stacktop];
						if (o instanceof Boolean) {
							stack[stacktop]=((Boolean)o)?"True":"False";
						} else if (o==null) {
							stack[stacktop]="None";
						} else {
							stack[stacktop]=stack[stacktop].toString();
						}
					}
					continue;
				}
				case 23: // PRINT
				{
					StringBuilder sb=new StringBuilder();
					int nargs=(Integer)stack[stacktop--];
					boolean nl=(Boolean)stack[stacktop--];
					stacktop-=nargs;
					for(int i=0; i<nargs; i++) {
						if(i!=0) {
							sb.append(" ");
						}
						sb.append((String)stack[stacktop+i+1]);
					}
					if(nl) {
						sb.append("\n");
					}
					if(mTheClient!=null) {
						mTheClient.print(sb.toString());
					}
					continue;
				}
				case 161: // STORE_NAME
				{
					// is it a global?
					Context c=current;
					if(current.globals!=null && current.globals.contains(strings[val])) {
						c=root;
					}
					c.names.put(strings[val], stack[stacktop--]);
					continue;
				}
				case 163: // GLOBAL
				{
					current.addGlobal(strings[val]);
					continue;
				}

				// Function call related
				case 128: // SET_METHOD
				{
					String name=(String)stack[stacktop--];
					current.names.put(name, new TMethod(val));
					continue;
				}
				case 10: // CALL
				{
					if(!(stack[stacktop] instanceof TMethod)) {
						internalError("TypeError", "object is not callable");
					}
					TMethod meth=(TMethod)stack[stacktop--];
					current=new Context(meth.addr, current);
					continue;
				}
				case 0: // FUNCTION_PROLOG
				{
					int argsexpected=(Integer)stack[stacktop--];
					int argsprovided=(Integer)stack[stacktop--];
					if(argsexpected!=argsprovided) {
						internalError("TypeError", String.format("Takes exactly %d arguments (%d given)", argsexpected, argsprovided));
					}
					continue;
				}
				case 9: // RETURN
				{
					if(current.parent==null) {
						internalError("SyntaxError", "'return' outside function");
					}
					current=current.parent;
					continue;
				}
				case 1: // ADD
				case 3: // DIV
				case 4: // GT
				case 5: // LT
				case 6: // EQ
				case 7: // IN
				case 8: // UNARY_ADD
				case 12: // ATTR
				case 14: // SUBSCRIPT
				case 15: // SUBSCRIPT_SLICE
				case 16: // DICT
				case 17: // LIST
				case 130: // IF_FALSE
					// -- check end : marker used by tool
				default:
					internalError("RuntimeError", String.format("Unknown/unimplemented opcode: %d", op));
				}
			}
	}

	private void extendStack() throws ExecutionError {
		int newsize=stack.length+512;
		if(newsize>8192) {
			internalError("RuntimeError", "Maximum stack depth exceeded");
		}
		Object[] newstack=new Object[newsize];
		System.arraycopy(stack, 0, newstack, 0, stack.length);
		stack=newstack;
	}

	private void internalError(String exctype, String message) throws ExecutionError {
		// need to know current context
		ExecutionError e=new ExecutionError();
		e.type=exctype;
		e.message=message;
		e.context=current;
		throw e;
	}

	private void internalErrorBinaryOp(String exctype, String op, Object left, Object right) throws ExecutionError {
		internalError(exctype, String.format("Can't %s %s %s", left.getClass().getSimpleName(), op, right.getClass().getSimpleName()));
	}

	public void signalError(String exctype, String message) throws ExecutionError {
		internalError(exctype, message);
	}

	class ExecutionError extends Exception {
		private static final long serialVersionUID = -4271385191079964823L;
		String type,message;
		Context context;
		public String toString() {
			return type+": "+message;
		}
		public int linenumber() {
			// note that context.pc points to the instruction after the one being executed
			int lastline=-1;
			for(int i=0;i<linenumbers.length;i++) {
				if(linenumbers[i][0]>=context.pc) {
					break;
				}
				lastline=linenumbers[i][1];
			}
			return lastline;
		}
		public int pc() {
			return context.pc;
		}
	}

	interface Client {
		public void print(String s) throws ExecutionError;
	}

	Client mTheClient;
	public void setClient(Client client) {
		mTheClient=client;
	}
}
