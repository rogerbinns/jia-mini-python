package com.rogerbinns;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Array;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IllegalFormatException;
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

	// If true then the stack is resized on every instruction to be as short as possible.
	// This catches code that doesn't extend the stack as necessary.
	boolean PARANOIDSTACK=true;

	MiniPython() {
		root=current=new Context(0, null);
		stack=new Object[PARANOIDSTACK?0:256];
		stacktop=-1;
		addBuiltins();
	}

	private enum Compare {
		NotComparable, // Types don't match, unorderable etc
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
			// ::TODO:: remove once thoroughly tested
			if(stacktop!=-1) {
				internalError("StackLeak", "Buggy code has led to a leak on the stack");
			}
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

	// this encapsulates the current stack frame
	private static final class Context {
		Context parent;
		Map<String,Object> variables;
		Set<String> globals; // only initialized if needed
		int pc;
		boolean return_on_return=false;
		Context(int pc, Context parent) {
			this.pc=pc;
			this.parent=parent;
			variables=new HashMap<String,Object>();
		}
		void addGlobal(String s) {
			if(globals==null) {
				globals=new HashSet<String>(1);
			}
			globals.add(s);
		}
	}

	// Our internal types.  We use Java native types wherever possible

	private static interface Callable {}

	private static final class TMethod implements Callable{
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

	private interface TNativeMethod extends Callable {
		Method getMethod();
		Object getThis();
		Object[] getPrefixArgs();
	}

	private final class TBuiltinInstanceMethod implements TNativeMethod, Callable {
		Object[] prefixargs;
		String prettyname;
		Method method;

		TBuiltinInstanceMethod(Object[] prefixargs, Method m, String prettyname) {
			this.prefixargs=prefixargs;
			this.prettyname=prettyname;
			method=m;
		}
		@Override
		public Object getThis() { return MiniPython.this; }

		@Override
		public Method getMethod() { return method; }

		@Override
		public Object[] getPrefixArgs() { return prefixargs; }

		public String toString() { return String.format("<instance method %s.%s>", toPyTypeString(prefixargs[0]), prettyname); }
	}

	private final class TModuleNativeMethod implements TNativeMethod, Callable {
		TModule mod;
		String name;
		Method nativeMethod;

		TModuleNativeMethod(TModule mod, String name) throws ExecutionError {
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
			if(nativeMethod==null) {
				internalError("AttributeError", "No method named "+name);
			}
		}

		TModuleNativeMethod(TModule mod, Method meth, String name) {
			this.mod=mod;
			this.nativeMethod=meth;
			this.name=name;
		}

		public String toString() {
			return String.format("<native method %s.%s>", mod.name, name);
		}

		@Override
		public Method getMethod() {
			return nativeMethod;
		}

		@Override
		public Object getThis() {
			return mod.o;
		}

		@Override
		public Object[] getPrefixArgs() {
			return null;
		}
	}

	private final void addBuiltins() {
		TModule tm=new TModule(this, "__builtins__");
		for(Method m : this.getClass().getDeclaredMethods()) {
			if(m.getName().startsWith("builtin_")) {
				String name=m.getName().substring("builtin_".length());
				TModuleNativeMethod tn=new TModuleNativeMethod(tm, m, name);
				root.variables.put(name, tn);
			}
		}
	}


	public Object callMethod(String name, Object ...args) throws ExecutionError {
		Object meth=root.variables.get(name);
		if(meth==null) {
			internalError("NameError", name+" is not defined");
		}
		if(!(meth instanceof Callable)) {
			internalError("TypeError", toPyString(meth)+" is not callable");
		}
		return call((Callable)meth, args);
	}

	Object call(Callable meth, Object ...args) throws ExecutionError {
		int savedsp=stacktop;
		try {
			int sp=stacktop;
			while(sp+3+args.length>=stack.length) {
				extendStack();
			}
			for(int i=0; i<args.length; i++) {
				stack[++stacktop]=args[i];
			}
			stack[++stacktop]=args.length;
			if(meth instanceof TMethod) {
				Context c=new Context(((TMethod)meth).addr, current);
				c.return_on_return=true;
				Object retval=mainLoop(c);
				if(PARANOIDSTACK) {
					if(stacktop!=savedsp) {
						internalError("StackLeak", "Buggy code has led to a leak on the stack");
					}
				}
				return retval;
			} else if (meth instanceof TNativeMethod) {
				stack[++stacktop]=meth;
				nativeCall();
				Object retval=stack[stacktop--];
				if(PARANOIDSTACK) {
					if(stacktop!=savedsp) {
						internalError("StackLeak", "Buggy code has led to a leak on the stack");
					}
				}
				return retval;
			} else {
				internalError("RuntimeError", "callable failed to be callable");
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
				if(PARANOIDSTACK) {
					if(stacktop+1<stack.length)
					{
						Object[] newstack=new Object[stacktop+1];
						System.arraycopy(stack, 0, newstack, 0, newstack.length);
						stack=newstack;
					}
				}
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
					if(builtin_bool(stack[stacktop--])==false) {
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
						current.pc=val;
					}
					continue;
				}
				case 132: // AND
				case 133: // OR
				{
					if(builtin_bool(stack[stacktop])==(op==133)) {
						// on true (OR) or false (AND), goto end
						current.pc=val;
					} else {
						// clear top value so next one can be tested
						stacktop--;
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
					while(true) {
						try {
							stack[++stacktop]=val;
							continue opcodeswitch;
						} catch(ArrayIndexOutOfBoundsException e) {
							extendStack();
							stacktop--;
						}
					}
				}
				case 201: // PUSH_INT_HI
				{
					stack[stacktop]=((Integer)stack[stacktop])|(val<<16);
					continue;
				}
				case 162: // PUSH_STR
				{
					while(true) {
						try {
							stack[++stacktop]=strings[val];
							continue opcodeswitch;
						} catch(ArrayIndexOutOfBoundsException e) {
							extendStack();
							stacktop--;
						}
					}
				}
				case 18: // PUSH_NONE
				case 21: // PUSH_TRUE
				case 22: // PUSH_FALSE
				{
					while(true) {
						try {
							stack[++stacktop]=(op==18)?null:(op==21);
							continue opcodeswitch;
						} catch(ArrayIndexOutOfBoundsException e) {
							extendStack();
							stacktop--;
						}
					}
				}
				case 160: // LOAD_NAME
				{
					while(true) {
						try {
							Context c=current;
							String key=strings[val];
							while(c!=null) {
								if(c.variables.containsKey(key)) {
									stack[++stacktop]=c.variables.get(key);
									continue opcodeswitch;
								}
								c=c.parent;
							}
							internalError("NameError", String.format("name '%s' is not defined", key));
						} catch(ArrayIndexOutOfBoundsException e) {
							extendStack();
							stacktop--;
						}
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
					if((left instanceof String && right instanceof Integer) ||
							(right instanceof String && left instanceof Integer)) {
						String s=(left instanceof String)?(String)left:(String)right;
						Integer ii=(left instanceof Integer)?(Integer)left:(Integer)right;
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
				case 27: // SUB
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					if(left instanceof Integer && right instanceof Integer) {
						stack[++stacktop]=(Integer)left-(Integer)right;
					} else {
						internalErrorBinaryOp("TypeError", "+", left, right);
					}
					continue;
				}
				case 30: // MOD
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					if(left instanceof Integer && right instanceof Integer) {
						stack[++stacktop]=(Integer)left % (Integer)right;
					} else if (left instanceof String && right instanceof List) {
						try {
							stack[++stacktop]=String.format((String) left, ((List)right).toArray());
						} catch(IllegalFormatException e) {
							internalError("TypeError", "String.format - "+e.toString());
						}
					} else {
						internalErrorBinaryOp("TypeError", "%", left, right);
					}
					continue;
				}
				// comparisons
				case 6: // EQ
				case 26: // NOT_EQ
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];
					Compare cmp=compareTo(left, right);
					stack[++stacktop]=(op==6) ? (cmp==Compare.Equal): (cmp!=Compare.Equal);
					continue;
				}

				case 5: // LT
				case 4: // GT
				{
					Object right=stack[stacktop--],
							left=stack[stacktop--];

					int cmp=builtin_cmp(left, right);
					boolean res=false;

					switch(op) {
					case 5: // < LT
						res= cmp<0;	break;
					case 4: // > GT
						res= cmp>0; break;
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
					stack[++stacktop]=getAttr(o, name);
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
				case 15: // SUBSCRIPT_SLICE
				{
					Object to=stack[stacktop--];
					Object from=stack[stacktop--];
					Object inlist=stack[stacktop--];
					if(!(inlist instanceof List)) {
						internalError("TypeError", "you can only slice lists not "+toPyTypeString(inlist));
					}
					if(to instanceof Integer && from instanceof Integer) {
						int ifrom=(Integer)from;
						int ito=(Integer)to;
						List thelist=(List)inlist;
						if(ifrom<0) {
							ifrom=thelist.size()+ifrom;
						}
						if(ito<0) {
							ito=thelist.size()+ito;
						}
						List result=new ArrayList();
						for(int i=ifrom; i<ito && i<thelist.size(); i++) {
							result.add(thelist.get(i));
						}
						stack[++stacktop]=result;
					} else {
						internalError("TypeError", String.format("slice indices must both be integers: supplied %s and %s", toPyTypeString(from), toPyTypeString(to)));
					}
					continue;
				}
				case 28: // DEL_INDEX
				{
					Object item=stack[stacktop--];
					Object container=stack[stacktop--];
					if(container instanceof List) {
						if(!(item instanceof Integer)) {
							internalError("TypeError", "Can only use integers to index list not "+toPyTypeString(item));
						}
						int i=(Integer)item;
						if(i<0) {
							i=((List)container).size()+i;
						}
						if(i<0 || i>= ((List)container).size()) {
							internalError("IndexError", "list index out of bounds");
						}
						((List)container).remove(i);
					} else if (container instanceof Map) {
						Object found=((Map)container).remove(item);
						if(item!=null && found==null) {
							internalError("KeyError", toPyString(item));
						}
					} else {
						internalError("TypeError", "Can't delete item of "+toPyTypeString(container));
					}
					continue;
				}
				case 29: // DEL_SLICE
				{
					Object to=stack[stacktop--];
					Object from=stack[stacktop--];
					Object inlist=stack[stacktop--];
					if(!(inlist instanceof List)) {
						internalError("TypeError", "you can only slice lists not "+toPyTypeString(inlist));
					}
					if(to instanceof Integer && from instanceof Integer) {
						int ifrom=(Integer)from;
						int ito=(Integer)to;
						List thelist=(List)inlist;
						if(ifrom<0) {
							ifrom=thelist.size()+ifrom;
						}
						if(ito<0) {
							ito=thelist.size()+ito;
						}
						// List only lets you delete one item at a time.  We have to start from the end so we don't
						// peturb index values while deleting
						if(ito>ifrom) {
							for(int i=ito-1; i>=0 && i>=ifrom; i--) {
								// python allows out of range list indices
								if(i<thelist.size()) {
									thelist.remove(i);
								}
							}
						}
					} else {
						internalError("TypeError", String.format("slice indices must both be integers: supplied %s and %s", toPyTypeString(from), toPyTypeString(to)));
					}
					continue;
				}
				case 164: // DEL_NAME
				{
					String name=strings[val];
					// Python allows del of globals but ignores the del!
					if(current.globals!=null && current.globals.contains(name)) {
						continue;
					}
					// we have to test for membership since we can't tell from remove if the
					// key existed or had a null value
					if(current.variables.containsKey(name)) {
						current.variables.remove(name);
					} else {
						internalError("NameError", String.format("name '%s' is not defined", name));
					}
					continue;
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
					c.variables.put(strings[val], stack[stacktop--]);
					continue;
				}
				case 163: // GLOBAL
				{
					if(current!=root && current.variables.containsKey(strings[val])) {
						internalError("SyntaxError", String.format("Name '%s' is assigned to before 'global' declaration", strings[val]));
					}
					current.addGlobal(strings[val]);
					continue;
				}

				// Function call related
				case 128: // SET_METHOD
				{
					String name=(String)stack[stacktop--];
					current.variables.put(name, new TMethod(val));
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

					boolean ror=current.return_on_return;
					current=current.parent;
					if(ror)
						return stack[stacktop--];
					continue;
				}

				case 3: // DIV
				case 8: // UNARY_ADD
					// -- check end : marker used by tool
				default:
					internalError("RuntimeError", String.format("Unknown/unimplemented opcode: %d", op));
				}
			}
	}

	private void extendStack() throws ExecutionError {
		int newsize=stack.length+(PARANOIDSTACK?1:512);
		if(newsize>8192) {
			internalError("RuntimeError", "Maximum stack depth exceeded");
		}
		Object[] newstack=new Object[newsize];
		System.arraycopy(stack, 0, newstack, 0, stack.length);
		stack=newstack;
	}


	static final private boolean checkTypeCompatible(Class<?> type, Object val) {
		if(val==null)
			return !type.isPrimitive();
		if(type.isAssignableFrom(val.getClass()))
			return true;
		if(!type.isPrimitive())
			return false;

		// type could be 'int' while val is 'Integer' - work out if that is the case
		// as autoboxing will make them compatible
		Class<?>vc=val.getClass();
		return (vc==Integer.class && type==Integer.TYPE) ||
				(vc==Boolean.class && type==Boolean.TYPE);

	}


	private void nativeCall() throws ExecutionError {
		// It requires a heroic amount of code to call the single invoke method, and get decent error message
		// such as wrong parameter types.  Varargs is even more comical.
		TNativeMethod tm=(TNativeMethod)stack[stacktop--];

		int suppliedargs=(Integer)stack[stacktop--];
		stacktop-=suppliedargs;
		Object[] args;
		Object[] prefixargs=tm.getPrefixArgs();
		int lpargs=(prefixargs!=null)?prefixargs.length:0;
		suppliedargs+=lpargs;

		Method method=tm.getMethod();
		Class<?>[] parameterTypes=method.getParameterTypes();

		int badarg=-1;
		Object badval=null;

		boolean varargs=method.isVarArgs();
		if(varargs) {
			int varargsindex=method.getGenericParameterTypes().length-1;
			Class<?> vatype=parameterTypes[varargsindex].getComponentType();
			Object varargsdata=Array.newInstance(vatype, suppliedargs-varargsindex);
			args=new Object[varargsindex+1];

			args[varargsindex]=varargsdata;

			for(int i=0;i<suppliedargs;i++) {
				Object val=(i<lpargs) ? prefixargs[i] : stack[stacktop+i-lpargs+1];

				if(i<varargsindex) {
					if(!checkTypeCompatible(parameterTypes[i], val)) {
						badarg=i; badval=val;
						break;
					}
					args[i]=val;
				} else {
					if(!checkTypeCompatible(vatype, val)) {
						badarg=i; badval=val;
						break;
					}
					Array.set(varargsdata, i-varargsindex, val);
				}
			}
		} else {
			args=new Object[suppliedargs];
			for(int i=0;i<suppliedargs;i++) {
				Object val=(i<lpargs) ? prefixargs[i] : stack[stacktop+i-lpargs+1];

				if(!checkTypeCompatible(parameterTypes[i], val)) {
					badarg=i; badval=val;
					break;
				}
				args[i]=val;
			}
		}

		if(badarg>=0) {
			Class<?> expecting=null;
			if(varargs && badarg>=parameterTypes.length-1) {
				expecting=parameterTypes[parameterTypes.length-1].getComponentType();
			} else {
				expecting=parameterTypes[badarg];
			}

			internalError("TypeError", String.format("Calling %s - bad argument #%d - got %s, expecting %s",
					tm,
					badarg+1-lpargs,
					toPyTypeString(badval),
					toPyTypeString(expecting)));
		}

		if(args.length!=parameterTypes.length) {
			String msg=String.format("Call to %s.  Takes %d%s args, %d provided", tm,
					method.getGenericParameterTypes().length+(varargs?-1:0)-lpargs,
					varargs?"+":"", suppliedargs-lpargs);
			internalError("TypeError", msg);
		}

		Object result=null;
		try {
			result=method.invoke(tm.getThis(), args);
		} catch (IllegalArgumentException e) {
			// this shouldn't be possible since we checked arg typing
			internalError("RuntimeError", String.format("Illegal arguments to native method %s: %s", tm, e));
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

	Object getAttr(Object o, String name) throws ExecutionError {
		if(o instanceof TModule)
			return new TModuleNativeMethod((TModule)o, name);

		// find an instance method
		String target="instance_"+toPyTypeString(o)+"_"+name;
		for(Method meth : this.getClass().getDeclaredMethods()) {
			if(meth.getName().equals(target))
				return new TBuiltinInstanceMethod(new Object[]{o}, meth, name);
		}

		internalError("AttributeError", String.format("No attribute '%s' of %s", name, toPyString(o)));
		return null;
	}

	private static final Compare compareTo(Object left, Object right) {
		if(left==null || right==null) {
			if(left==right)
				return Compare.Equal;
			return Compare.NotComparable;
		}
		if(left.equals(right))
			return Compare.Equal;

		if(left.getClass()!=right.getClass())
			return Compare.NotComparable;
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
			assert false;
		}
		return left.equals(right)?Compare.Equal:Compare.NotComparable;
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	private String _toPyString(Object o, boolean quotestrings, Set<Integer> seencontainers) {
		if(o==null)
			return "None";
		if(o instanceof Boolean)
			return ((Boolean)o)?"True":"False";
		if(o instanceof String) {
			String s=(String)o;
			if(quotestrings)
				return "\""+s.replace("\\", "\\\\").replace("\"", "\\\"")+"\"";
			return s;
		}
		if(o instanceof Map || o instanceof List) {
			if(seencontainers==null) {
				seencontainers=new HashSet<Integer>();
			}

			Integer id=System.identityHashCode(o);
			StringBuilder sb=new StringBuilder();
			if(o instanceof List) {
				sb.append("[");
				if(seencontainers.contains(id)) {
					sb.append("...");
				} else {
					seencontainers.add(id);
					boolean first=true;
					for(Object item : (List)o) {
						if(first) {
							first=false;
						} else {
							sb.append(", ");
						}
						sb.append(_toPyString(item, true, seencontainers));
					}
				}
				sb.append("]");
			} else {
				sb.append("{");
				if(seencontainers.contains(id)) {
					sb.append("...");
				} else {
					seencontainers.add(id);
					boolean first=true;
					Set<Map.Entry> items=((Map)o).entrySet();
					for(Map.Entry item : items) {
						if(first) {
							first=false;
						} else {
							sb.append(", ");
						}
						// it would rather silly to use a container as the key, but go ahead (hence null passed in)
						sb.append(_toPyString(item.getKey(), true, null));
						sb.append(": ");
						sb.append(_toPyString(item.getValue(), true, seencontainers));
					}
				}
				sb.append("}");
			}
			return sb.toString();
		}
		return o.toString();
	}

	public String toPyString(Object o) {
		return _toPyString(o, false, null);
	}

	public static String toPyTypeString(Object o) {
		if(o==null)
			return "NoneType";
		if(o instanceof Boolean || o==Boolean.TYPE || o==Boolean.class)
			return "bool";
		if(o instanceof Map || o==Map.class)
			return "dict";
		if(o instanceof List || o==List.class)
			return "list";
		if(o instanceof Integer || o==Integer.TYPE || o==Integer.class)
			return "int";
		if(o instanceof String)
			return "str";
		if(o instanceof Callable)
			return "callable";
		if(o instanceof Class<?>)
			return ((Class<?>)o).getSimpleName();
		return toPyTypeString(o.getClass());
	}

	public class ExecutionError extends Exception {
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

	public interface Client {
		public void print(String s) throws ExecutionError;
	}

	Client mTheClient;
	public void setClient(Client client) {
		mTheClient=client;
	}

	public void addModule(String name, Object object) {
		root.variables.put(name, new TModule(object, name));
	}

	// builtin methods
	Object builtin_apply(Callable meth, List<Object> args) throws ExecutionError {
		return call(meth, args.toArray());
	}

	@SuppressWarnings("rawtypes")
	boolean builtin_bool(Object o) throws ExecutionError {
		if(o instanceof Boolean)
			return (Boolean)o;
		if(o instanceof String)
			return ((String)o).length()!=0;
		if(o instanceof Integer)
			return ((Integer)o)!=0;
		if(o==null)
			return false;
		if(o instanceof List)
			return ((List)o).size()>0;

			// Eclipse is retarded and screws up indentation from here on
			if(o instanceof Map)
				return ((Map)o).size()>0;

				internalError("TypeError", "Can't 'bool' "+toPyString(o));
				return false;
	}

	boolean builtin_callable(Object o) {
		return o!=null && o instanceof Callable;
	}

	int builtin_cmp(Object left, Object right) throws ExecutionError {
		Compare cmp=compareTo(left, right);
		switch(cmp) {
		case Less: return -1;
		case Equal: return 0;
		case Greater: return 1;
		default:
		case NotComparable:
			internalError("TypeError", String.format("Can't compare %s against %s", toPyTypeString(left), toPyTypeString(right)));
			// not reachable
			return -100;
		}
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	List builtin_filter(Callable function, List items) throws ExecutionError {
		List res=new ArrayList();
		for(Object item : items) {
			if(builtin_bool(call(function, item))) {
				res.add(item);
			}
		}
		return res;
	}

	int builtin_id(Object o) {
		return System.identityHashCode(o);
	}

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

	List<Object> builtin_range(int start, int... constraints) throws ExecutionError {
		if(constraints.length>2) {
			internalError("TypeError", "Expected at most 3 arguments");
		}
		int step=1;
		int stop=1;
		switch(constraints.length) {
		case 0:
			stop=start;
			start=0;
			break;
		case 1:
			stop=constraints[0];
			break;
		case 2:
			stop=constraints[0];
			step=constraints[1];
			break;
		}
		if(step==0) {
			internalError("ValueError", "step argument must not be zero");
		}
		List<Object> res=new ArrayList<Object>();

		if(step<0 && stop<start) {
			for(int i=start; i>stop; i+=step) {
				res.add(i);
			}
		} else {
			for(int i=start; i<stop; i+=step) {
				res.add(i);
			}
		}
		return res;
	}

	String builtin_str(Object o) {
		return toPyString(o);
	}

	String builtin_type(Object o) {
		return toPyTypeString(o);
	}

	// instance methods
	String instance_str_upper(String s) {
		return s.toUpperCase();
	}

	@SuppressWarnings({ "unchecked", "rawtypes" })
	void instance_list_append(List list, Object item) {
		list.add(item);
	}

	@SuppressWarnings({ "unchecked", "rawtypes" })
	void instance_list_sort(List list, Object... args) throws ExecutionError {
		Callable cmp=null;
		Callable key=null;
		boolean reverse=false;

		switch(args.length) {
		default:
			internalError("TypeError", String.format("list.sort() takes most 3 arguments (%d given)", args.length));
		case 3:
			if(args[2]!=null) {
				if(!(args[2] instanceof Boolean)) {
					internalError("TypeError", "list.sort reverse parameter should be boolean not "+toPyTypeString(args[2]));
				}
				reverse=(Boolean)args[2];
			}
		case 2:
		{
			if(args[1]!=null) {
				if(!builtin_callable(args[1])) {
					internalError("ValueError", "list.sort key parameter must be callable");
				}
				key=(Callable)args[1];
			}
		}
		case 1:
		{
			if(args[0]!=null) {
				if(!builtin_callable(args[0])) {
					internalError("ValueError", "list.sort cmp parameter must be callable");
				}
				cmp=(Callable)args[0];
			}
		}
		case 0:
			break;
		}

		// and this is why we like using real programming languages ...
		final Callable javasucks=cmp;
		final Callable javareallysucks=key;
		final ExecutionError[] didimentionsuckage=new ExecutionError[1];

		Comparator comparator=new Comparator() {
			@Override
			public int compare(Object left, Object right) {
				try {
					if(javareallysucks!=null)
					{
						left=call(javareallysucks, left);
						right=call(javareallysucks, right);
					}

					return (javasucks==null)?builtin_cmp(left, right):(Integer)call(javasucks, left, right);
				} catch (ExecutionError e) {
					didimentionsuckage[0]=e;
					throw new ClassCastException();
				}
			}
		};
		if(reverse) {
			comparator=Collections.reverseOrder(comparator);
		}
		try {
			Collections.sort(list, comparator);
		} catch(ClassCastException e) {
			if(didimentionsuckage[0]!=null)
				throw didimentionsuckage[0];
			throw e;
		}
	}

}
