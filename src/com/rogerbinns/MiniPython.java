package com.rogerbinns;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class MiniPython {

	String[] strings;
	int[][] linenumbers;
	byte[] code;

	Context root;
	Context current;
	Object[] stack;
	int stacktop;

	MiniPython() {
		root=new Context(0, null);
		stack=new Object[256];
		stacktop=-1;
	}

	private enum Compare {
		DifferentTypes, // Where left and right types don't match.  Also when unorderable type such as dict doesn't match
		Less,
		Equal,
		Greater
	}

	public void setCode(InputStream is) throws IOException, ExecutionError {
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

		mainLoop(root);
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

	private static final class TModule {
		String name;
		Object o;

		TModule(Object o, String name) {
			this.o=o;
			this.name=name;
		}
		public String toString() {
			return String.format("<module %s>", name);
		}
	}

	private static final class TNativeMethod {
		TModule mod;
		String name;
		int nargs;
		Method nativeMethod;
		TNativeMethod(TModule mod, String name) {
			this.mod=mod;
			this.name=name;
			for(Method m : mod.o.getClass().getDeclaredMethods()) {
				// we only want public methods
				if((m.getModifiers()&Modifier.PUBLIC)==0) {
					continue;
				}
				if(m.getName().equals(name)) {
					nativeMethod=m;
					break;
				}
			}
			if(nativeMethod!=null) {
				nargs=nativeMethod.getParameterTypes().length;
			}
		}
		public String toString() {
			return String.format("<native method %s.%s (%d args)>", mod.name, name, nargs);
		}
	}


	// execution
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
				case 130: // IF_FALSE
				{
					if((Boolean)stack[stacktop--]==false) {
						current.pc=val;
					}
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
				case 17: // LIST
				{
					int nitems=(Integer)stack[stacktop--];
					List<Object> l=new ArrayList<Object>(nitems);
					stacktop-=nitems;
					for(int i=0; i<nitems; i++) {
						l.add(stack[stacktop+1+i]);
					}
					stack[++stacktop]=l;
					continue;
				}
				case 16: // DICT
				{
					int nitems=(Integer)stack[stacktop--];
					Map<Object,Object> m=new HashMap<Object, Object>(nitems);
					stacktop-=nitems*2;
					for(int i=0; i<nitems; i++) {
						Object k=stack[stacktop+1+i*2+1];
						Object v=stack[stacktop+1+i*2];
						m.put(k, v);
					}
					stack[++stacktop]=m;
					continue;
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
				// comparisons
				case 5: // LT
				case 4: // GT
				case 6: // EQ
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					Compare cmp=compareTo(left, right);
					boolean res=false;

					switch(op) {
					case 6: // = EQ
						res= cmp==Compare.Equal;
						break;
					case 5: // < LT
						if(cmp==Compare.DifferentTypes) {
							internalErrorBinaryOp("TypeError", "<", left, right);
						}
						res= cmp==Compare.Less;
						break;
					case 4: // > GT
						if(cmp==Compare.DifferentTypes) {
							internalErrorBinaryOp("TypeError", ">", left, right);
						}
						res= cmp==Compare.Greater;
						break;

					default:
						internalError("RuntimeError", "Unhandled comparison operator");
					}
					stack[++stacktop]=res;
					continue;
				}
				case 12: // ATTR
				{
					Object o=stack[stacktop--];
					String name=(String)stack[stacktop--];
					// we only support attributes of modules
					if(!(o instanceof TModule)) {
						internalError("AttributeError", "Can only get attributes of modules");
					}
					TNativeMethod m=new TNativeMethod((TModule)o, name);
					if(m.nativeMethod==null) {
						internalError("AtrributeError", "No method named "+name);
					}
					stack[++stacktop]=m;
					continue;
				}
				case 14: // SUBSCRIPT
				{
					Object key=stack[stacktop--];
					Object obj=stack[stacktop--];
					if(obj instanceof List) {
						if(!(key instanceof Integer)) {
							internalError("TypeError", "list indices must be integers: "+toPyString(key));
						}
						int index=(Integer)key;
						@SuppressWarnings("unchecked")
						List<Object> l=(List<Object>)obj;
						if(index<0) {
							index=l.size()+index;
						}
						if(index<0 || index>=l.size()) {
							internalError("IndexError", "list index out of range");
						}
						stack[++stacktop]=l.get(index);
						continue;
					} else if (obj instanceof Map) {
						@SuppressWarnings("unchecked")
						Map<Object,Object> m=(Map<Object, Object>) obj;
						if(m.containsKey(key)) {
							stack[++stacktop]=m.get(key);
							continue;
						}
						internalError("KeyError", toPyString(key));
					}
					internalError("TypeError","object is not subscriptable "+toPyString(obj));
				}
				case 7: // IN
				{
					Object collection=stack[stacktop--];
					Object key=stack[stacktop--];
					if(collection instanceof Map) {
						@SuppressWarnings("unchecked")
						Map<Object,Object> m=(Map<Object, Object>) collection;
						stack[++stacktop]=m.containsKey(key);
						continue;
					} else if (collection instanceof List) {
						@SuppressWarnings("unchecked")
						List<Object> l=(List<Object>) collection;
						stack[++stacktop]=l.contains(key);
						continue;
					}
					internalError("TypeError", "can't do 'in' in "+toPyString(collection));
				}

				// Unary operations
				case 13: // UNARY_NEG
				{
					if(stack[stacktop] instanceof Integer) {
						stack[stacktop]=-(Integer)stack[stacktop];
						continue;
					} else {
						internalError("TypeError", "Can only negate integers");
					}
				}
				case 24: // BOOL
				{
					Object o=stack[stacktop];
					if(o instanceof Boolean) {
						continue;
					}
					if(o instanceof String) {
						stack[stacktop]= ((String)o).length()!=0;
					} else if(o instanceof Integer) {
						stack[stacktop]= ((Integer)o)!=0;
					} else if(o==null) {
						stack[stacktop]=false;
					} else if(o instanceof List) {
						stack[stacktop]= ((List)o).size()>0;
					} else if(o instanceof Map) {
						stack[stacktop]= ((Map)o).size()>0;
					} else {
						internalError("SystemError", "Unknown type to bool "+toPyString(o));
					}
					continue;
				}

				// More heavyweight stuff
				case 20: // STR
				{
					stack[stacktop]=toPyString(stack[stacktop]);
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
					sb.append(nl?"\n":" ");
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
					if(stack[stacktop] instanceof TNativeMethod) {
						nativeCall();
						continue;
					}
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
				case 8: // UNARY_ADD
				case 15: // SUBSCRIPT_SLICE
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

	private void nativeCall() throws ExecutionError {
		TNativeMethod tm=(TNativeMethod)stack[stacktop--];
		int suppliedargs=(Integer)stack[stacktop--];
		if(suppliedargs!=tm.nargs) {
			internalError("TypeError", String.format("%s takes %d arguments (%d given)", tm.name, tm.nargs, suppliedargs));
		}
		Object[] args=new Object[suppliedargs];
		stacktop-=suppliedargs;
		for(int i=0;i<suppliedargs;i++) {
			args[i]=stack[stacktop+i+1];
		}
		Object result=null;
		try {
			result=tm.nativeMethod.invoke(tm.mod.o, args);
		} catch (IllegalArgumentException e) {
			internalError("TypeError", String.format("Call to %s: %s", tm, e));
		} catch (IllegalAccessException e) {
			// this shouldn't be possible since we checked it is public
			internalError("RuntimeError", String.format("Illegal access to native method %s: %s", tm, e));
		} catch (InvocationTargetException e) {
			Object cause=e.getCause();
			if(cause instanceof ExecutionError)
				throw (ExecutionError)cause;
			internalError(cause.getClass().getSimpleName(), String.format("%s: %s", tm, cause));
		}
		stack[++stacktop]=result;
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
		internalError(exctype, String.format("Can't %s %s %s", toPyString(left), op, toPyString(right)));
	}

	public void signalError(String exctype, String message) throws ExecutionError {
		internalError(exctype, message);
	}

	private static final Compare compareTo(Object left, Object right) {
		if(left==null || right==null) {
			if(left==right)
				return Compare.Equal;
			return Compare.DifferentTypes;
		}
		if(left.getClass()!=right.getClass())
			return Compare.DifferentTypes;
		// from here on they are the same type and neither is null
		if(left instanceof Integer) {
			int l=(Integer)left, r=(Integer)right;
			if(l==r)
				return Compare.Equal;
			if(l<r)
				return Compare.Less;
			return Compare.Greater;
		}
		if(left instanceof String) {
			int cmp=((String)left).compareTo((String)right);
			if(cmp<0) return Compare.Less;
			if(cmp==0) return Compare.Equal;
			return Compare.Greater;
		}
		if(left instanceof List) {
			@SuppressWarnings("unchecked")
			Iterator<Object> li=((List<Object>)left).iterator();
			@SuppressWarnings("unchecked")
			Iterator<Object> ri=((List<Object>)right).iterator();
			while(true) {
				// both ended at same place
				if(!li.hasNext() && !ri.hasNext()) {
					break;
				}
				// one ends before the other
				if(!li.hasNext())
					return Compare.Less;
				if(!ri.hasNext())
					return Compare.Greater;
				Compare cmp=compareTo(li.next(), ri.next());
				if(cmp!=Compare.Equal)
					return cmp;
			}
			return Compare.Equal;
		}
		if(left instanceof Map) {
			// ::TODO:: something here although we can only do equality checking
		}
		return left.equals(right)?Compare.Equal:Compare.DifferentTypes;
	}

	@SuppressWarnings("rawtypes")
	public String toPyString(Object o) {
		if(o==null)
			return "None";
		if(o instanceof Boolean)
			return ((Boolean)o)?"True":"False";
		if(o instanceof Map)
			return String.format("<dict (%d items) >", ((Map)o).size());
		if(o instanceof List)
			return String.format("<list (%d items) >", ((List)o).size());
		return o.toString();
	}

	class ExecutionError extends Exception {
		private static final long serialVersionUID = -4271385191079964823L;
		String type,message;
		Context context;
		public String toString() {
			return type+": "+message;
		}
		public String getType() {
			return type;
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

	public void addModule(String name, Object object) {
		root.names.put(name, new TModule(object, name));
	}
}
