package com.rogerbinns;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Array;
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
		root=current=new Context(0, null);
		stack=new Object[256];
		stacktop=-1;
		addBuiltins();
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
		// ::TODO:: read in chunks
		if(is.read(code)!=codelen)
			throw new EOFException();

		try {
			stacktop=-1;
			mainLoop(root);
		} finally {
			stacktop=-1;
		}
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
				globals=new HashSet<String>(1);
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
		Method nativeMethod;
		TNativeMethod(TModule mod) {
			this.mod=mod;
		}
		void Lookup(String name) {
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
		}
		public String toString() {
			return String.format("<native method %s.%s>", mod.name, name);
		}
	}

	private final void addBuiltins() {
		TModule tm=new TModule(this, "__builtins__");
		for(Method m : this.getClass().getDeclaredMethods()) {
			if(m.getName().startsWith("builtin_")) {
				TNativeMethod tn=new TNativeMethod(tm);
				tn.nativeMethod=m;
				String name=m.getName().substring("builtin_".length());
				tn.name=name;
				root.names.put(name, tn);
			}
		}
	}


	public Object callMethod(String name, Object ...args) throws ExecutionError {
		int savedsp=stacktop;
		try {
			Object meth=root.names.get(name);
			if(meth==null) {
				internalError("NameError", name+" is not defined");
			}
			int sp=stacktop;
			while(sp+2+args.length>=stack.length) {
				extendStack();
			}
			for(int i=0; i<args.length; i++) {
				stack[++stacktop]=args[i];
			}
			stack[++stacktop]=args.length;
			stack[++stacktop]=meth;
			if(meth instanceof TMethod) {
				Context c=new Context(((TMethod)meth).addr, current);
				return mainLoop(c);
			} else if (meth instanceof TNativeMethod) {
				nativeCall();
				return stack[--stacktop];
			} else {
				internalError("TypeError", toPyString(meth)+" is not callable");
				return null;
			}
		} finally {
			stacktop=savedsp;
		}
	}

	// execution
	private final Object mainLoop(Context context) throws ExecutionError {
		Context savedcontext=current;
		current=context;
		try {
			return _mainLoop();
		} finally {
			current=savedcontext;
		}
	}

	// The virtual cpu execution loop.
	// Java's generics are poor and it whines about conversions even when the generic types are Object
	// so this turns off the whining as there is nothing we can do about it.
	@SuppressWarnings({ "rawtypes", "unchecked" })
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
				case 131: // NEXT
				{
					Iterator it=(Iterator)stack[stacktop];
					if(it.hasNext()) {
						if(stacktop+1==stack.length) {
							extendStack();
						}
						stack[++stacktop]=it.next();
					} else {
						// take iterator off stack
						stacktop--;
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
					internalErrorBinaryOp("TypeError", "*", left, right);
				}
				case 1: // ADD
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					if ((left==null || right==null) || !right.getClass().equals(left.getClass())) {
						internalErrorBinaryOp("TypeError", "+", left, right);
					}
					// both are the same type
					if(left instanceof Integer) {
						stack[++stacktop]=(Integer)left+(Integer)right;
					} else 	if(left instanceof String) {
						stack[++stacktop]=(String)left+(String)right;
					} else if(left instanceof List) {
						List<Object> m=new ArrayList<Object>(((List)left).size()+((List)right).size());
						m.addAll((List)left);
						m.addAll((List)right);
						stack[++stacktop]=m;
					} else {
						internalErrorBinaryOp("TypeError", "+", left, right);
					}
					continue;
				}

				// comparisons
				case 5: // LT
				case 4: // GT
				case 6: // EQ
				case 26: // NOT_EQ
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					Compare cmp=compareTo(left, right);
					boolean res=false;

					switch(op) {
					case 6:  // == EQ
					case 26: // != NOT_EQ
						res=(op==6) ? (cmp==Compare.Equal): (cmp!=Compare.Equal);
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
					TNativeMethod m=new TNativeMethod((TModule)o);
					m.Lookup(name);
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
						stack[++stacktop]=((Map)collection).containsKey(key);
						continue;
					} else if (collection instanceof List) {
						stack[++stacktop]=((List)collection).contains(key);
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
						internalError("TypeError", "Can't 'bool' "+toPyString(o));
					}
					continue;
				}
				case 20: // STR
				{
					stack[stacktop]=toPyString(stack[stacktop]);
					continue;
				}
				case 25: // ITER
				{
					Object o=stack[stacktop];
					if(o instanceof List) {
						stack[stacktop]=((List)o).iterator();
					} else if (o instanceof Map) {
						stack[stacktop]=((Map)o).keySet().iterator();
					} else {
						internalError("TypeError", toPyString(o)+" is not iterable");
					}
					continue;
				}

				// More heavyweight stuff
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
						sb.append(toPyString(stack[stacktop+i+1]));
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
					if(current!=root && current.names.containsKey(strings[val])) {
						internalError("SyntaxError", String.format("Name '%s' is assigned to before 'global' declaration", strings[val]));
					}
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
						internalError("TypeError", toPyString(stack[stacktop])+" is not callable");
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
		// It requires a heroic amount of code to call the single invoke method, and get decent error message
		// such as wrong parameter types.  Varargs is even more comical.
		TNativeMethod tm=(TNativeMethod)stack[stacktop--];

		int suppliedargs=(Integer)stack[stacktop--];
		stacktop-=suppliedargs;
		Object[] args;

		@SuppressWarnings("rawtypes")
		Class[] parameterTypes=tm.nativeMethod.getParameterTypes();

		int badarg=-1;

		boolean varargs=tm.nativeMethod.isVarArgs();
		if(varargs) {
			int varargsindex=tm.nativeMethod.getGenericParameterTypes().length-1;

			Object varargsdata=Array.newInstance(
					parameterTypes[varargsindex].getComponentType(),
					suppliedargs-varargsindex);
			args=new Object[varargsindex+1];

			args[varargsindex]=varargsdata;

			for(int i=0;i<suppliedargs;i++) {
				try {
					if(i<varargsindex) {
						args[i]=parameterTypes[i].cast(stack[stacktop+i+1]);
					} else {
						Array.set(varargsdata, i-varargsindex, stack[stacktop+i+1]);
					}
				} catch (IllegalArgumentException e) {
					badarg=i; break;
				} catch (ClassCastException e) {
					badarg=i; break;
				}
			}
		} else {
			args=new Object[suppliedargs];
			for(int i=0;i<suppliedargs;i++) {
				try {
					args[i]=parameterTypes[i].cast(stack[stacktop+i+1]);
				} catch (ClassCastException e) {
					badarg=i; break;
				}
			}
		}

		if(badarg>=0) {
			Class expecting=null;
			if(varargs) {
				expecting=parameterTypes[parameterTypes.length-1].getComponentType();
			} else {
				expecting=parameterTypes[badarg];
			}

			internalError("TypeError", String.format("Calling %s - bad argument #%d - got %s, expecting %s",
					tm,
					badarg+1,
					toPyString(stack[stacktop+badarg+1].getClass().getSimpleName()),
					toPyString(expecting.getSimpleName())));
		}

		Object result=null;
		try {
			result=tm.nativeMethod.invoke(tm.mod.o, args);
		} catch (IllegalArgumentException e) {
			String msg=String.format("Call to %s: %s.  Takes %d%s args, %d provided", tm, e,
					tm.nativeMethod.getGenericParameterTypes().length+(varargs?-1:0),
					varargs?"+":"", suppliedargs);
			internalError("TypeError", msg);
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

	// builtin methods
	@SuppressWarnings("rawtypes")
	int builtin_len(Object item) throws ExecutionError {
		if(item instanceof Map) return ((Map)item).size();
		if(item instanceof List) return ((List)item).size();
		if(item instanceof String) return ((String)item).length();
		internalError("TypeError", "Can't get length of "+toPyString(item));
		// unreachable code
		return -1;
	}

	void builtin_print(Object ...items) throws ExecutionError {
		StringBuilder sb=new StringBuilder();
		for(int i=0; i<items.length; i++) {
			if(i!=0) {
				sb.append(" ");
			}
			sb.append(toPyString(items[i]));
		}
		sb.append("\n");
		if(mTheClient!=null) {
			mTheClient.print(sb.toString());
		}
	}
}
