package com.rogerbinns;

/* Java Mini Python - version %%VERSION%%
 * See http://code.google.com/p/java-mini-python/ for the project page,
 * bug tracker, mailing lists, support, documentation and license information
 */

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
import java.util.regex.Pattern;

/**
 * Encapsulates running a Python syntax file.
 * 
 * The source should have been transformed using jmp-compile. The class cannot
 * be used concurrently. There is no shared state between instances.
 */
public class MiniPython {

	private String[] strings;
	private int[][] linenumbers;
	private byte[] code;

	private Context root;
	private Context current;
	private Object[] stack; // stack of values
	private int stacktop; // top occupied slot on stack
	private int pc;

	private static int STACK_SIZE;

	public MiniPython() {
		STACK_SIZE = 1024;
	}

	/**
	 * Removes all internal state.
	 * 
	 * This ensures that garbage collection is easier. You can reuse this
	 * instance by calling addModule to reregister modules and setCode to run
	 * new code.
	 */
	public synchronized void clear() {
		root = current = null;
		stack = null;
		strings = null;
		linenumbers = null;
		code = null;
		mTheClient = null;
	}

	/**
	 * Reads and executes code from the supplied stream
	 * 
	 * The stream provided must satisfy reads completely (eg if 27 bytes is
	 * asked for then that number should be returned in the read() call unless
	 * end of file is reached.)
	 * 
	 * @param stream
	 *            The stream is not closed and you can have additional content
	 *            after the jmp.
	 * @throws IOException
	 *             Passed on from read() calls on the stream
	 * @throws EOFException
	 *             When the stream is truncated
	 * @throws ExecutionError
	 *             Any issues from executing the code
	 */
	public synchronized void setCode(InputStream stream) throws IOException,
	ExecutionError {
		if (root == null) {
			root = new Context(null);
		}
		current = root;
		stack = new Object[STACK_SIZE];
		stacktop = -1;
		pc = 0;
		addBuiltins();

		// version
		int version = get16(stream);
		if (version != 0)
			throw new IOException(String.format(
					"Unknown JMP version number %d", version));

		// string table
		int stablen = get16(stream);
		strings = new String[stablen];
		for (int i = 0; i < stablen; i++) {
			strings[i] = getUTF(stream, get16(stream));
		}
		// line numbers
		int ltablen = get16(stream);
		linenumbers = new int[ltablen][2];
		for (int i = 0; i < ltablen; i++) {
			linenumbers[i][0] = get16(stream);
			linenumbers[i][1] = get16(stream);
		}
		// code
		int codelen = get16(stream);
		code = new byte[codelen];
		if (stream.read(code) != codelen)
			throw new EOFException();

		try {
			stacktop = -1;
			mainLoop();
		} catch (ExecutionError e) {
			throw e;
		} catch (Exception e) {
			throw internalError(e);
		} finally {
			stacktop = -1;
		}
	}

	private static final int get16(InputStream is) throws IOException {
		int a = is.read(), b = is.read();
		if (a < 0 || b < 0)
			throw new EOFException();
		return a + (b << 8);
	}

	private static final String getUTF(InputStream is, int byteslen)
			throws IOException {
		byte[] b = new byte[byteslen];
		if (is.read(b) != byteslen)
			throw new EOFException();
		return new String(b, "UTF8");
	}

	// this encapsulates the current stack frame
	private static final class Context {
		Context parent; // used for variable lookups
		Map<String, Object> variables;
		Set<String> globals; // only initialized if needed

		Context(Context parent) {
			this.parent = parent;
			variables = new HashMap<String, Object>();
		}

		void addGlobal(String s) {
			if (globals == null) {
				globals = new HashSet<String>(1);
			}
			globals.add(s);
		}
	}

	// Our internal types. We use Java native types wherever possible

	private static interface Callable {
	}

	private static final class TMethod implements Callable {
		// address of method in bytecode
		int addr;
		Context context;
		Object self; // set if a bound method

		TMethod(int addr, Context context) {
			this.addr = addr;
			this.context = context;
			this.self=null;
		}

		public String toString() {
			if (self!=null)
				return String.format("<bound method of id %d at %d>", builtin_id(self), addr);
			return String.format("<method at %d>", addr);
		}

		@Override
		public boolean equals(Object other) {
			return other instanceof TMethod
					&& this.self == ((TMethod) other).self
					&& this.addr == ((TMethod) other).addr;
		}
	}

	private static final class TModule {
		String name;
		Object o;

		TModule(Object o, String name) {
			this.o = o;
			this.name = name;
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

	private final class TBuiltinInstanceMethod implements TNativeMethod {
		Object[] prefixargs;
		String prettyname;
		Method method;

		TBuiltinInstanceMethod(Object[] prefixargs, Method m, String prettyname) {
			this.prefixargs = prefixargs;
			this.prettyname = prettyname;
			method = m;
		}

		@Override
		public Object getThis() {
			return MiniPython.this;
		}

		@Override
		public Method getMethod() {
			return method;
		}

		@Override
		public Object[] getPrefixArgs() {
			return prefixargs;
		}

		@Override
		public boolean equals(Object other) {
			return other instanceof TBuiltinInstanceMethod
					&& this.prettyname
					.equals(((TBuiltinInstanceMethod) other).prettyname)
					&& this.prefixargs
					.equals(((TBuiltinInstanceMethod) other).prefixargs);
		}

		@Override
		public String toString() {
			return String.format("<instance method %s.%s for %d>",
					toPyTypeString(prefixargs[0]), prettyname,
					builtin_id(prefixargs[0]));
		}
	}

	private final class TModuleNativeMethod implements TNativeMethod {
		TModule mod;
		String name;
		Method nativeMethod;

		TModuleNativeMethod(TModule mod, String name) throws ExecutionError {
			this.mod = mod;
			this.name = name;
			for (Method m : mod.o.getClass().getDeclaredMethods()) {
				// we only want public methods
				if ((m.getModifiers() & Modifier.PUBLIC) == 0) {
					continue;
				}
				if (m.getName().equals(name)) {
					nativeMethod = m;
					break;
				}
			}
			if (nativeMethod == null)
				throw internalError("AttributeError", "No method named " + name);
		}

		TModuleNativeMethod(TModule mod, Method meth, String name) {
			this.mod = mod;
			this.nativeMethod = meth;
			this.name = name;
		}

		@Override
		public boolean equals(Object other) {
			return other instanceof TModuleNativeMethod
					&& this.name.equals(((TModuleNativeMethod) other).name)
					&& this.mod.o.equals(((TModuleNativeMethod) other).mod.o);
		}

		@Override
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
		TModule tm = new TModule(this, "__builtins__");
		for (Method m : this.getClass().getDeclaredMethods()) {
			if (m.getName().startsWith("builtin_")) {
				String name = m.getName().substring("builtin_".length());
				TModuleNativeMethod tn = new TModuleNativeMethod(tm, m, name);
				root.variables.put(name, tn);
			}
		}
	}

	/**
	 * Calls a method in Python and returns the result
	 * 
	 * @param name
	 *            Global method name
	 * @param args
	 *            Variable list of arguments that it takes
	 * @throws ExecutionError
	 *             On any issues encountered
	 */
	public synchronized Object callMethod(String name, Object... args)
			throws ExecutionError {
		Object meth = root.variables.get(name);
		if (meth == null)
			throw internalError("NameError", name + " is not defined");
		if (!(meth instanceof Callable))
			throw internalError("TypeError", toPyString(meth)
					+ " is not callable");
		return call((Callable) meth, args);
	}

	private Object call(Callable meth, Object... args) throws ExecutionError {
		int savedsp = stacktop;
		int savedpc = pc;
		Context savedcontext = current;
		try {
			for (int i = 0; i < args.length; i++) {
				stack[++stacktop] = args[i];
			}
			stack[++stacktop] = args.length;
			if (meth instanceof TMethod) {
				TMethod tmeth = (TMethod) meth;
				adjustArgsForBoundMethod(tmeth);
				Context c = new Context(tmeth.context);
				stack[++stacktop] = current; // return context
				stack[++stacktop] = -1; // returnpc
				pc = tmeth.addr;
				current = c;
				return mainLoop();
			} else if (meth instanceof TNativeMethod) {
				stack[++stacktop] = meth;
				nativeCall();
				return stack[stacktop--];
			} else
				throw internalError("TypeError", toPyTypeString(meth)
						+ " is not callable");
		} catch (ExecutionError e) {
			throw e;
		} catch (Exception e) {
			throw internalError(e);
		} finally {
			stacktop = savedsp;
			pc = savedpc;
			current = savedcontext;
		}
	}

	// futzes the stack to insert the self argument if needed
	private void adjustArgsForBoundMethod(TMethod meth) {
		if(meth.self==null) return;
		int nargs=(Integer)stack[stacktop];
		System.arraycopy(stack, stacktop-nargs, stack, stacktop-nargs+1, nargs+1);
		stack[stacktop-nargs]=meth.self;
		stack[++stacktop]=nargs+1;
	}

	// The virtual cpu execution loop.
	// Java's generics are poor and it whines about conversions even when the
	// generic types are Object
	// so this turns off the whining as there is nothing we can do about it.
	@SuppressWarnings({ "rawtypes", "unchecked" })
	private final Object mainLoop() throws ExecutionError {
		int op, val = -1;
		opcodeswitch: while (true) {
			op = code[pc++] & 0xff;
			if (op >= 128) {
				val = (code[pc] & 0xff) + ((code[pc + 1] & 0xff) << 8);
				pc += 2;
			}
			switch (op) {
			// -- check start : marker used by tool

			// Control flow codes
			case 19: // EXIT_LOOP
			{
				return null;
			}
			case 129: // GOTO
			{
				pc = val;
				continue;
			}
			case 130: // IF_FALSE
			{
				if (builtin_bool(stack[stacktop--]) == false) {
					pc = val;
				}
				continue;
			}
			case 131: // NEXT
			{
				Iterator it = (Iterator) stack[stacktop];
				if (it.hasNext()) {
					stack[++stacktop] = it.next();
				} else {
					pc = val;
				}
				continue;
			}
			case 132: // AND
			case 133: // OR
			{
				if (builtin_bool(stack[stacktop]) == (op == 133)) {
					// on true (OR) or false (AND), goto end
					pc = val;
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
			case 202: // POP_N
			{
				stacktop-=val;
				continue;
			}
			// Codes that make the stack bigger
			case 200: // PUSH_INT
			{
				stack[++stacktop] = val;
				continue;
			}
			case 201: // PUSH_INT_HI
			{
				stack[stacktop] = ((Integer) stack[stacktop]) | (val << 16);
				continue;
			}
			case 162: // PUSH_STR
			{
				stack[++stacktop] = strings[val];
				continue;
			}
			case 18: // PUSH_NONE
			case 21: // PUSH_TRUE
			case 22: // PUSH_FALSE
			{
				stack[++stacktop] = (op == 18) ? null : (op == 21);
				continue;
			}
			case 160: // LOAD_NAME
			{
				Context c = current;
				String key = strings[val];
				while (c != null) {
					if (c.variables.containsKey(key)) {
						stack[++stacktop] = c.variables.get(key);
						continue opcodeswitch;
					}
					c = c.parent;
				}
				throw internalError("NameError",
						String.format("name '%s' is not defined", key));
			}
			case 17: // LIST
			{
				int nitems = (Integer) stack[stacktop--];
				List l = new ArrayList(nitems);
				stacktop -= nitems;
				for (int i = 0; i < nitems; i++) {
					l.add(stack[stacktop + 1 + i]);
				}
				stack[++stacktop] = l;
				continue;
			}
			case 16: // DICT
			{
				int nitems = (Integer) stack[stacktop--];
				Map m = new HashMap(nitems);
				stacktop -= nitems * 2;
				for (int i = 0; i < nitems; i++) {
					Object k = stack[stacktop + 1 + i * 2 + 1];
					Object v = stack[stacktop + 1 + i * 2];
					m.put(k, v);
				}
				stack[++stacktop] = m;
				continue;
			}

			// Binary operations
			case 35: // IS
			{
				Object right = stack[stacktop--], left = stack[stacktop--];
				stack[++stacktop]= builtin_id(left)==builtin_id(right);
				continue;
			}
			case 2: // MULT
			{
				Object right = stack[stacktop--], left = stack[stacktop--];
				if (left instanceof Integer && right instanceof Integer) {
					stack[++stacktop] = (Integer) left * (Integer) right;
					continue;
				}
				if ((left instanceof String && right instanceof Integer)
						|| (right instanceof String && left instanceof Integer)) {
					String s = (left instanceof String) ? (String) left
							: (String) right;
					int ii = (left instanceof Integer) ? (Integer) left
							: (Integer) right;
					// python is happy with negative multiplier
					if (ii < 0) {
						ii = 0;
					}
					StringBuilder sb = new StringBuilder(s.length() * ii);
					for (int i = 0; i < ii; i++) {
						sb.append(s);
					}
					stack[++stacktop] = sb.toString();
					continue;
				}
				if ((left instanceof List && right instanceof Integer)
						|| (right instanceof List && left instanceof Integer)) {
					List l = (left instanceof List) ? (List) left
							: (List) right;
					int ii = (left instanceof Integer) ? (Integer) left
							: (Integer) right;
					// Python is happy with negative multiplier
					if (ii < 0) {
						ii = 0;
					}
					List res = new ArrayList(ii * l.size());
					for (int i = 0; i < ii; i++) {
						res.addAll(l);
					}
					stack[++stacktop] = res;
					continue;
				}
				throw internalErrorBinaryOp("TypeError", "*", left, right);
			}
			case 1: // ADD
			{
				Object right = stack[stacktop--], left = stack[stacktop--];
				if ((left == null || right == null)
						|| !right.getClass().equals(left.getClass()))
					throw internalErrorBinaryOp("TypeError", "+", left, right);
				// both are the same type
				if (left instanceof Integer) {
					stack[++stacktop] = (Integer) left + (Integer) right;
				} else if (left instanceof String) {
					stack[++stacktop] = (String) left + (String) right;
				} else if (left instanceof List) {
					List m = new ArrayList(((List) left).size()
							+ ((List) right).size());
					m.addAll((List) left);
					m.addAll((List) right);
					stack[++stacktop] = m;
				} else
					throw internalErrorBinaryOp("TypeError", "+", left, right);
				continue;
			}
			case 27: // SUB
			{
				Object right = stack[stacktop--], left = stack[stacktop--];
				if (left instanceof Integer && right instanceof Integer) {
					stack[++stacktop] = (Integer) left - (Integer) right;
				} else
					throw internalErrorBinaryOp("TypeError", "-", left, right);
				continue;
			}
			case 3: // DIV
			{
				Object right = stack[stacktop--], left = stack[stacktop--];
				if (left instanceof Integer && right instanceof Integer) {
					// If one operand is negative then the answer isn't quite
					// what you expect
					// http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
					int l = (Integer) left, r = (Integer) right;
					if ((l >= 0 && r >= 0) || (l < 0 && r < 0)) {
						stack[++stacktop] = l / r;
					} else {
						int res = l / r;
						if (l % r != 0) {
							res--;
						}
						stack[++stacktop] = res;
					}
				} else
					throw internalErrorBinaryOp("TypeError", "/", left, right);
				continue;
			}
			case 30: // MOD
			{
				Object right = stack[stacktop--], left = stack[stacktop--];
				if (left instanceof Integer && right instanceof Integer) {
					int l = (Integer) left, r = (Integer) right;
					int res = l % r;
					// in Python the result sign is same as sign of right
					if ((res < 0 && r >= 0) || (res >= 0 && r < 0)) {
						res = -res;
					}
					stack[++stacktop] = res;
				} else if (left instanceof String && right instanceof List) {
					try {
						stack[++stacktop] = String.format((String) left,
								((List) right).toArray());
					} catch (IllegalFormatException e) {
						throw internalError("TypeError",
								"String.format - " + e.toString());
					}
				} else
					throw internalErrorBinaryOp("TypeError", "%", left, right);
				continue;
			}
			// comparisons
			case 5: // LT
			case 4: // GT
			case 31: // GTE
			case 32: // LTE
			case 6: // EQ
			case 26: // NOT_EQ
			{
				Object right = stack[stacktop--], left = stack[stacktop--];

				int cmp = builtin_cmp(left, right);
				boolean res = false;

				switch (op) {
				case 5: // < LT
					res = cmp < 0;
					break;
				case 32: // <= LTE
					res = cmp <= 0;
					break;
				case 4: // > GT
					res = cmp > 0;
					break;
				case 31: // >= GTE
					res = cmp >= 0;
					break;
				case 6: // = EQ
					res = cmp == 0;
					break;
				case 26: // != NOT_EQ
					res = cmp != 0;
					break;
				}
				stack[++stacktop] = res;
				continue;
			}
			case 12: // ATTR
			{
				Object o = stack[stacktop--];
				String name = (String) stack[stacktop--];
				stack[++stacktop] = getAttr(o, name);
				continue;
			}
			case 165: // STORE_ATTR_NAME
			{
				Object o = stack[stacktop--];
				Object v = stack[stacktop--];
				String name = strings[val];
				setAttr(o, name, v);
				continue;
			}
			case 14: // SUBSCRIPT
			{
				Object key = stack[stacktop--];
				Object obj = stack[stacktop--];
				if (obj instanceof List) {
					if (!(key instanceof Integer))
						throw internalError("TypeError",
								"list indices must be integers: "
										+ toPyString(key));
					int index = (Integer) key;
					List l = (List) obj;
					if (index < 0) {
						index = l.size() + index;
					}
					if (index < 0 || index >= l.size())
						throw internalError("IndexError",
								"list index out of range");
					stack[++stacktop] = l.get(index);
					continue;
				} else if (obj instanceof Map) {
					Map m = (Map) obj;
					if (m.containsKey(key)) {
						stack[++stacktop] = m.get(key);
						continue;
					}
					throw internalError("KeyError", toPyString(key));
				} else if (obj instanceof String) {
					if (!(key instanceof Integer))
						throw internalError("TypeError",
								"str indices must be integers: "
										+ toPyString(key));
					int ikey = (Integer) key;
					if (ikey < 0) {
						ikey += ((String) obj).length();
					}
					try {
						stack[++stacktop] = ((String) obj).substring(ikey,
								ikey + 1);
						continue;
					} catch (IndexOutOfBoundsException e) {
						throw internalError("IndexError",
								"string index out of range");
					}
				}
				throw internalError("TypeError", "object is not subscriptable "
						+ toPyString(obj));
			}
			case 15: // SUBSCRIPT_SLICE
			{
				Object to = stack[stacktop--];
				Object from = stack[stacktop--];
				Object obj = stack[stacktop--];
				if (!((to == null || to instanceof Integer) && (from == null || from instanceof Integer)))
					throw internalError(
							"TypeError",
							String.format(
									"slice indices must both be integers: supplied %s and %s",
									toPyTypeString(from), toPyTypeString(to)));
				if (obj instanceof List) {
					List thelist = (List) obj;
					int ifrom = (from == null) ? 0 : (Integer) from;
					int ito = (to == null) ? thelist.size() : (Integer) to;
					if (ifrom < 0) {
						ifrom += thelist.size();
						if (ifrom < 0) {
							ifrom = 0;
						}
					}
					if (ito < 0) {
						ito += thelist.size();
					}
					List result = new ArrayList();
					for (int i = ifrom; i < ito && i < thelist.size(); i++) {
						result.add(thelist.get(i));
					}
					stack[++stacktop] = result;
					continue;
				} else if (obj instanceof String) {
					String str = (String) obj;
					int ifrom = (from == null) ? 0 : (Integer) from;
					int ito = (to == null) ? str.length() : (Integer) to;
					if (ifrom < 0) {
						ifrom += str.length();
					}
					if (ito < 0) {
						ito += str.length();
					}
					// python allows the indices to be out of range
					if ((ifrom >= str.length()) || ito <= ifrom) {
						stack[++stacktop] = "";
					} else {
						if (ito > str.length()) {
							ito = str.length();
						}
						if (ifrom < 0) {
							ifrom = 0;
						}
						stack[++stacktop] = str.substring(ifrom, ito);
					}
					continue;
				}
				throw internalError("TypeError",
						"you can only slice lists and strings, not "
								+ toPyTypeString(obj));
			}
			case 33: // ASSIGN_INDEX
			{
				Object value = stack[stacktop--];
				Object index = stack[stacktop--];
				Object obj = stack[stacktop--];
				if (obj instanceof Map) {
					((Map) obj).put(index, value);
				} else if (obj instanceof List) {
					if (!(index instanceof Integer))
						throw internalError("TypeError",
								"list indices must be integers, not "
										+ toPyTypeString(index));
					int iindex = (Integer) index;
					List list = (List) obj;
					if (iindex < 0) {
						iindex += list.size();
					}
					if (iindex < 0 || iindex >= list.size())
						throw internalError("IndexError", String.format(
								"list assignment index out of range: %d",
								iindex));
					list.set(iindex, value);
				} else
					throw internalError("TypeError", toPyTypeString(obj)
							+ " does not support item assignment");
				continue;
			}
			case 28: // DEL_INDEX
			{
				Object item = stack[stacktop--];
				Object container = stack[stacktop--];
				if (container instanceof List) {
					if (!(item instanceof Integer))
						throw internalError("TypeError",
								"Can only use integers to index list not "
										+ toPyTypeString(item));
					int i = (Integer) item;
					if (i < 0) {
						i = ((List) container).size() + i;
					}
					if (i < 0 || i >= ((List) container).size())
						throw internalError("IndexError",
								"list index out of bounds");
					((List) container).remove(i);
				} else if (container instanceof Map) {
					Object found = ((Map) container).remove(item);
					if (item != null && found == null)
						throw internalError("KeyError", toPyString(item));
				} else
					throw internalError("TypeError", "Can't delete item of "
							+ toPyTypeString(container));
				continue;
			}
			case 29: // DEL_SLICE
			{
				Object to = stack[stacktop--];
				Object from = stack[stacktop--];
				Object inlist = stack[stacktop--];
				if (!(inlist instanceof List))
					throw internalError("TypeError",
							"you can only slice lists not "
									+ toPyTypeString(inlist));
				if (to instanceof Integer && from instanceof Integer) {
					int ifrom = (Integer) from;
					int ito = (Integer) to;
					List thelist = (List) inlist;
					if (ifrom < 0) {
						ifrom = thelist.size() + ifrom;
					}
					if (ito < 0) {
						ito = thelist.size() + ito;
					}
					// List only lets you delete one item at a time. We have to
					// start from the end so we don't
					// peturb index values while deleting
					if (ito > ifrom) {
						for (int i = ito - 1; i >= 0 && i >= ifrom; i--) {
							// python allows out of range list indices
							if (i < thelist.size()) {
								thelist.remove(i);
							}
						}
					}
				} else
					throw internalError(
							"TypeError",
							String.format(
									"slice indices must both be integers: supplied %s and %s",
									toPyTypeString(from), toPyTypeString(to)));
				continue;
			}
			case 164: // DEL_NAME
			{
				String name = strings[val];
				// Python allows del of globals but ignores the del!
				if (current.globals != null && current.globals.contains(name)) {
					continue;
				}
				// we have to test for membership since we can't tell from
				// remove if the
				// key existed or had a null value
				if (current.variables.containsKey(name)) {
					current.variables.remove(name);
				} else
					throw internalError("NameError",
							String.format("name '%s' is not defined", name));
				continue;
			}
			case 7: // IN
			{
				Object collection = stack[stacktop--];
				Object key = stack[stacktop--];
				if (collection instanceof Map) {
					stack[++stacktop] = ((Map) collection).containsKey(key);
				} else if (collection instanceof List) {
					stack[++stacktop] = ((List) collection).contains(key);
				} else if (key instanceof String
						&& collection instanceof String) {
					stack[++stacktop] = ((String) collection)
							.contains((String) key);
				} else
					throw internalError("TypeError", "can't do 'in' in "
							+ toPyString(collection));
				continue;
			}

			// Unary operations
			case 13: // UNARY_NEG
			{
				if (stack[stacktop] instanceof Integer) {
					stack[stacktop] = -(Integer) stack[stacktop];
				} else
					throw internalError("TypeError", "Can't negate "
							+ toPyTypeString(stack[stacktop]));
				continue;
			}
			case 8: // UNARY_ADD
			{
				if (stack[stacktop] instanceof Integer) {
				} else
					throw internalError("TypeError", "Can't unary plus "
							+ toPyTypeString(stack[stacktop]));
				continue;
			}
			case 24: // NOT
			{
				stack[stacktop] = !builtin_bool(stack[stacktop]);
				continue;
			}
			case 25: // ITER
			{
				Object o = stack[stacktop];
				if (o instanceof List) {
					stack[stacktop] = ((List) o).iterator();
				} else if (o instanceof Map) {
					stack[stacktop] = ((Map) o).keySet().iterator();
				} else
					throw internalError("TypeError", toPyString(o)
							+ " is not iterable");
				continue;
			}

			// More heavyweight stuff
			case 34: // ASSERT_FAILED
			{
				Object o = stack[stacktop--];
				throw internalError("AssertionError",
						toPyString((o != null) ? o : "assertion failed"));
			}
			case 23: // PRINT
			{
				StringBuilder sb = new StringBuilder();
				int nargs = (Integer) stack[stacktop--];
				boolean nl = (Boolean) stack[stacktop--];
				stacktop -= nargs;
				for (int i = 0; i < nargs; i++) {
					if (i != 0) {
						sb.append(" ");
					}
					sb.append(toPyString(stack[stacktop + i + 1]));
				}
				sb.append(nl ? "\n" : " ");
				if (mTheClient != null) {
					mTheClient.print(sb.toString());
				}
				continue;
			}
			case 161: // STORE_NAME
			{
				// is it a global?
				Context c = current;
				if (current.globals != null
						&& current.globals.contains(strings[val])) {
					c = root;
				}
				c.variables.put(strings[val], stack[stacktop--]);
				continue;
			}
			case 163: // GLOBAL
			{
				if (current != root) {
					if (current.variables.containsKey(strings[val]))
						throw internalError(
								"SyntaxError",
								String.format(
										"Name '%s' is assigned to before 'global' declaration",
										strings[val]));
					current.addGlobal(strings[val]);
				}
				continue;
			}

			// Function call related
			case 128: // MAKE_METHOD
			{
				stack[++stacktop] = new TMethod(val, current);
				continue;
			}
			case 10: // CALL
			{
				if (stack[stacktop] instanceof TNativeMethod) {
					nativeCall();
					continue;
				}
				if (!(stack[stacktop] instanceof TMethod))
					throw internalError("TypeError",
							toPyTypeString(stack[stacktop])
							+ " is not callable");
				TMethod meth = (TMethod) stack[stacktop--];
				adjustArgsForBoundMethod(meth);
				stack[++stacktop] = current; // return context
				stack[++stacktop] = pc; // return address
				current = new Context(meth.context);
				pc = meth.addr;
				continue;
			}
			case 0: // FUNCTION_PROLOG
			{
				int argsexpected = (Integer) stack[stacktop--];
				int returnpc = (Integer) stack[stacktop--];
				Context returncontext = (Context) stack[stacktop--];
				int argsprovided = (Integer) stack[stacktop--];
				if (argsexpected != argsprovided)
					throw internalError("TypeError", String.format(
							"Method takes exactly %d arguments (%d given)",
							argsexpected, argsprovided));
				// we need to insert the returncontext/pc before the args
				stacktop += 2;
				System.arraycopy(stack, stacktop - argsprovided - 1, stack,
						stacktop - argsprovided + 1, argsprovided);
				stack[stacktop - argsprovided - 1] = returncontext;
				stack[stacktop - argsprovided] = returnpc;
				continue;
			}
			case 9: // RETURN
			{
				if (current.parent == null)
					throw internalError("SyntaxError",
							"'return' outside function");

				Object retval = stack[stacktop--];
				int returnpc = (Integer) stack[stacktop--];
				current = (Context) stack[stacktop--];
				if (returnpc < 0)
					return retval;
				pc = returnpc;
				stack[++stacktop] = retval;
				continue;
			}
			// -- check end : marker used by tool
			default:
				throw internalError("RuntimeError",
						String.format("Unknown/unimplemented opcode: %d", op));
			}
		}
	}

	static final private boolean checkTypeCompatible(Class<?> type, Object val) {
		if (val == null)
			return !type.isPrimitive();
		if (type.isAssignableFrom(val.getClass()))
			return true;
		if (!type.isPrimitive())
			return false;

		// type could be 'int' while val is 'Integer' - work out if that is the
		// case
		// as autoboxing will make them compatible
		Class<?> vc = val.getClass();
		return (vc == Integer.class && type == Integer.TYPE)
				|| (vc == Boolean.class && type == Boolean.TYPE);

	}

	private void nativeCall() throws ExecutionError {
		// It requires a heroic amount of code to call the single invoke method,
		// and get decent error message
		// such as wrong parameter types. Varargs is even more comical.
		TNativeMethod tm = (TNativeMethod) stack[stacktop--];

		int suppliedargs = (Integer) stack[stacktop--];
		stacktop -= suppliedargs;
		Object[] args;
		Object[] prefixargs = tm.getPrefixArgs();
		int lpargs = (prefixargs != null) ? prefixargs.length : 0;
		suppliedargs += lpargs;

		Method method = tm.getMethod();
		Class<?>[] parameterTypes = method.getParameterTypes();

		int badarg = -1;
		Object badval = null;

		boolean varargs = method.isVarArgs();
		if (varargs
				&& suppliedargs >= method.getGenericParameterTypes().length - 1) {
			int varargsindex = method.getGenericParameterTypes().length - 1;
			Class<?> vatype = parameterTypes[varargsindex].getComponentType();
			Object varargsdata = Array.newInstance(vatype, suppliedargs
					- varargsindex);
			args = new Object[varargsindex + 1];
			args[varargsindex] = varargsdata;

			for (int i = 0; i < suppliedargs; i++) {
				Object val = (i < lpargs) ? prefixargs[i] : stack[stacktop + i
				                                                  - lpargs + 1];

				if (i < varargsindex) {
					if (!checkTypeCompatible(parameterTypes[i], val)) {
						badarg = i;
						badval = val;
						break;
					}
					args[i] = val;
				} else {
					if (!checkTypeCompatible(vatype, val)) {
						badarg = i;
						badval = val;
						break;
					}
					Array.set(varargsdata, i - varargsindex, val);
				}
			}
		} else {
			args = new Object[suppliedargs];
			for (int i = 0; i < suppliedargs; i++) {
				Object val = (i < lpargs) ? prefixargs[i] : stack[stacktop + i
				                                                  - lpargs + 1];

				if (!checkTypeCompatible(parameterTypes[i], val)) {
					badarg = i;
					badval = val;
					break;
				}
				args[i] = val;
			}
		}

		if (badarg >= 0) {
			Class<?> expecting = null;
			if (varargs && badarg >= parameterTypes.length - 1) {
				expecting = parameterTypes[parameterTypes.length - 1]
						.getComponentType();
			} else {
				expecting = parameterTypes[badarg];
			}

			throw internalError("TypeError", String.format(
					"Calling %s - bad argument #%d - got %s, expecting %s", tm,
					badarg + 1 - lpargs, toPyTypeString(badval),
					toPyTypeString(expecting)));
		}

		if (args.length != parameterTypes.length) {
			String msg = String.format(
					"Call to %s.  Takes %d%s args, %d provided", tm,
					method.getGenericParameterTypes().length
					+ (varargs ? -1 : 0) - lpargs, varargs ? "+" : "",
							suppliedargs - lpargs);
			throw internalError("TypeError", msg);
		}

		Object result = null;
		try {
			result = method.invoke(tm.getThis(), args);
		} catch (IllegalArgumentException e) {
			// this shouldn't be possible since we checked arg typing
			throw internalError("RuntimeError", String.format(
					"Illegal arguments to native method %s: %s", tm, e));
		} catch (IllegalAccessException e) {
			// this shouldn't be possible since we checked it is public
			throw internalError("RuntimeError", String.format(
					"Illegal access to native method %s: %s", tm, e));
		} catch (InvocationTargetException e) {
			Object cause = e.getCause();
			if (cause instanceof ExecutionError)
				throw (ExecutionError) cause;
			throw internalError(cause.getClass().getSimpleName(),
					String.format("%s: %s", tm, cause));
		}
		stack[++stacktop] = result;
	}

	private ExecutionError internalError(String exctype, String message) {
		// need to know current context
		ExecutionError e = new ExecutionError();
		e.type = exctype;
		e.message = message;
		e.pc = pc;
		if (mTheClient != null) {
			mTheClient.onError(e);
		}
		return e;
	}

	private ExecutionError internalError(Exception e) {
		if (e instanceof ArrayIndexOutOfBoundsException
				&& stacktop >= stack.length)
			return internalError("RuntimeError", "Maximum stack depth exceeded"); /* SOURCECHECKOK */
		return internalError(e.getClass().getSimpleName(), /* SOURCECHECKOK */
				e.toString());
	}

	private ExecutionError internalErrorBinaryOp(String exctype, String op,
			Object left, Object right) {
		return internalError(exctype, /* SOURCECHECKOK */
				String.format("Can't do binary op: %s %s %s",
						toPyTypeString(left), op, toPyTypeString(right)));
	}

	/**
	 * Call this method when your callbacks need to halt execution due to an
	 * error
	 * 
	 * This method will do the internal bookkeeping necessary in order to
	 * provide diagnostics to the original caller and then throw an
	 * ExecutionError which you should not catch.
	 * 
	 * @param exctype
	 *            Best practise is to use the name of a Python exception (eg
	 *            "TypeError")
	 * @param message
	 *            Text describing the error.
	 * @throws ExecutionError
	 *             Always thrown
	 */
	public void signalError(String exctype, String message)
			throws ExecutionError {
		throw internalError(exctype, message);
	}

	@SuppressWarnings("rawtypes")
	private Object getAttr(Object o, String name) throws ExecutionError {
		if (o instanceof TModule)
			return new TModuleNativeMethod((TModule) o, name);

		if(o instanceof Map) {
			Map m=(Map)o;
			if(m.containsKey(name)) {
				Object retval=m.get(name);
				if(retval instanceof TMethod) {
					TMethod t=(TMethod)retval;
					if (t.self == null) {
						t=new TMethod(t.addr, t.context);
						t.self=o;
						retval=t;
					}
				}
				return retval;
			}
		}

		// find an instance method
		String target = "instance_" + toPyTypeString(o) + "_" + name;
		for (Method meth : this.getClass().getDeclaredMethods()) {
			if (meth.getName().equals(target))
				return new TBuiltinInstanceMethod(new Object[] { o }, meth,
						name);
		}

		throw internalError("AttributeError",
				String.format("No attribute '%s' of %s", name, toPyString(o)));
	}

	@SuppressWarnings({ "unchecked", "rawtypes" })
	private void setAttr(Object o, String name, Object value)
			throws ExecutionError {
		if (o instanceof Map) {
			((Map) o).put(name, value);
			return;
		}
		throw internalError("TypeError", "Can't set attributes on "
				+ toPyTypeString(o));
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	private final int compareTo(Object left, Object right)
			throws ExecutionError {
		if (left == right)
			return 0;

		if (left == null || right == null)
			return compareTo(toPyTypeString(left), toPyTypeString(right));
		try {
			// ignore any exceptions this throws
			if (left.equals(right))
				return 0;
		} catch (ClassCastException e) {
		}

		if (left.getClass() != right.getClass())
			return compareTo(toPyTypeString(left), toPyTypeString(right));

		// from here on they are the same type and neither is null
		if (left instanceof Integer) {
			int l = (Integer) left, r = (Integer) right;
			// equals handled above
			if (l < r)
				return -1;
			return +1;
		}

		if (left instanceof String) {
			int cmp = ((String) left).compareTo((String) right);
			// equals handled above
			if (cmp < 0)
				return -1;
			return +1;
		}
		if (left instanceof List) {
			Iterator li = ((List) left).iterator();
			Iterator ri = ((List) right).iterator();
			while (true) {
				// both ended at same place
				if (!li.hasNext() && !ri.hasNext()) {
					break;
				}
				// one ends before the other
				if (!li.hasNext())
					return -1;
				if (!ri.hasNext())
					return +1;
				int cmp = compareTo(li.next(), ri.next());
				if (cmp != 0)
					return cmp;
			}
			return 0;
		}
		if (left instanceof Map)
			return compareTo(builtin_id(left), builtin_id(right));
		if (left instanceof Boolean)
			return compareTo(builtin_int(left), builtin_int(right));
		return compareTo(left.toString(), right.toString());
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	private String _toPyString(Object o, boolean quotestrings,
			Set<Integer> seencontainers) {
		if (o == null)
			return "None";
		if (o instanceof Boolean)
			return ((Boolean) o) ? "True" : "False";
		if (o instanceof String) {
			String s = (String) o;
			if (quotestrings)
				return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"")
						+ "\"";
			return s;
		}
		if (o instanceof Map || o instanceof List) {
			if (seencontainers == null) {
				seencontainers = new HashSet<Integer>();
			}

			Integer id = System.identityHashCode(o);
			StringBuilder sb = new StringBuilder();
			if (o instanceof List) {
				sb.append("[");
				if (seencontainers.contains(id)) {
					sb.append("...");
				} else {
					seencontainers.add(id);
					boolean first = true;
					for (Object item : (List) o) {
						if (first) {
							first = false;
						} else {
							sb.append(", ");
						}
						sb.append(_toPyString(item, true, seencontainers));
					}
				}
				sb.append("]");
			} else {
				sb.append("{");
				if (seencontainers.contains(id)) {
					sb.append("...");
				} else {
					seencontainers.add(id);
					boolean first = true;
					Set<Map.Entry> items = ((Map) o).entrySet();
					for (Map.Entry item : items) {
						if (first) {
							first = false;
						} else {
							sb.append(", ");
						}
						// it would rather silly to use a container as the key,
						// but go ahead (hence null passed in)
						sb.append(_toPyString(item.getKey(), true, null));
						sb.append(": ");
						sb.append(_toPyString(item.getValue(), true,
								seencontainers));
					}
				}
				sb.append("}");
			}
			return sb.toString();
		}
		return o.toString();
	}

	/**
	 * Returns a string representing the object using Python nomenclature where
	 * possible
	 * 
	 * For example `null` is returned as `None`, `true` as `True` etc. Container
	 * types like dict/Map and list/List will include the items.
	 * 
	 * @param o
	 *            Object to stringify. Can be null.
	 */
	public String toPyString(Object o) {
		return _toPyString(o, false, null);
	}

	/**
	 * Returns a string representing the type of the object using Python
	 * nomenclature where possible
	 * 
	 * For example `null` is returned as `NoneType`, `true` as `bool`, `Map` as
	 * `dict` etc. You can also pass in Class objects as well as instances. Note
	 * that primitives (eg `int`) and the corresponding boxed type (eg
	 * `Integer`) will both be returned as the same string (`int` in this case).
	 * 
	 * @param o
	 *            Object whose type to stringify, or a Class or null
	 */
	public static String toPyTypeString(Object o) {
		if (o == null)
			return "NoneType";
		if (o instanceof Boolean || o == Boolean.TYPE || o == Boolean.class)
			return "bool";
		if (o instanceof Map || o == Map.class)
			return "dict";
		if (o instanceof List || o == List.class)
			return "list";
		if (o instanceof Integer || o == Integer.TYPE || o == Integer.class)
			return "int";
		if (o instanceof String)
			return "str";
		if (o instanceof TMethod)
			return "method";
		if (o instanceof TModule)
			return "module";
		if (o instanceof TModuleNativeMethod)
			return "modulemethod";
		if (o instanceof TBuiltinInstanceMethod)
			return "instancemethod";
		if (o instanceof Class<?>)
			return ((Class<?>) o).getSimpleName();
		return toPyTypeString(o.getClass());
	}

	private Client mTheClient;

	/**
	 * Callbacks to use for specific behaviour
	 * 
	 * @param client
	 *            Replaces existing client with this one
	 */
	public void setClient(Client client) {
		mTheClient = client;
	}

	/**
	 * Makes methods on the methods Object available to the Python
	 * 
	 * @param name
	 *            Module name in the Python environment
	 * @param object
	 *            Object to introspect looking for methods
	 * @see <a href="../../../../java.html#id1">Adding methods</a>
	 */
	public void addModule(String name, Object object) {
		if (root == null) {
			root = new Context(null);
		}
		root.variables.put(name, new TModule(object, name));
	}

	// builtin methods
	@SuppressWarnings("unused")
	private Object builtin_apply(Callable meth, List<Object> args)
			throws ExecutionError {
		return call(meth, args.toArray());
	}

	@SuppressWarnings("rawtypes")
	private boolean builtin_bool(Object o) throws ExecutionError {
		if (o instanceof Boolean)
			return (Boolean) o;
		if (o instanceof String)
			return ((String) o).length() != 0;
		if (o instanceof Integer)
			return ((Integer) o) != 0;
		if (o == null)
			return false;
		if (o instanceof List)
			return ((List) o).size() > 0;

			// Eclipse is retarded and screws up indentation from here on
			if (o instanceof Map)
				return ((Map) o).size() > 0;

				throw internalError("TypeError", "Can't 'bool' " + toPyString(o));
	}

	private boolean builtin_callable(Object o) {
		return o instanceof Callable;
	}

	private int builtin_cmp(Object left, Object right) throws ExecutionError {
		return compareTo(left, right);
	}

	@SuppressWarnings({ "rawtypes", "unchecked", "unused" })
	private List builtin_filter(Callable function, List items)
			throws ExecutionError {
		List res = new ArrayList();
		for (Object item : items) {
			if (builtin_bool(call(function, item))) {
				res.add(item);
			}
		}
		return res;
	}

	@SuppressWarnings({ "unused", "rawtypes" })
	private Map builtin_globals() {
		return root.variables;
	}

	private static int builtin_id(Object o) {
		return System.identityHashCode(o);
	}

	private int builtin_int(Object o) throws ExecutionError {
		if (o instanceof Integer)
			return (Integer) o;
		if (o instanceof Boolean)
			return ((Boolean) o) ? 1 : 0;
		if (o instanceof String) {
			try {
				return Integer.parseInt((String) o);
			} catch (NumberFormatException e) {
				throw internalError("ValueError", e.toString());
			}
		}
		throw internalError("TypeError",
				"int argument must be bool, string or int not "
						+ toPyTypeString(o));
	}

	@SuppressWarnings({ "rawtypes", "unused" })
	private int builtin_len(Object item) throws ExecutionError {
		if (item instanceof Map)
			return ((Map) item).size();
		if (item instanceof List)
			return ((List) item).size();
		if (item instanceof String)
			return ((String) item).length();
		throw internalError("TypeError", "Can't get length of "
				+ toPyString(item));
	}

	@SuppressWarnings({ "unused", "rawtypes" })
	private Map builtin_locals() {
		return current.variables;
	}
	@SuppressWarnings({ "rawtypes", "unchecked", "unused" })
	private List builtin_map(Callable function, List items)
			throws ExecutionError {
		List res = new ArrayList(items.size());
		for (Object item : items) {
			res.add(call(function, item));
		}
		return res;
	}

	@SuppressWarnings("unused")
	private void builtin_print(Object... items) throws ExecutionError {
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < items.length; i++) {
			if (i != 0) {
				sb.append(" ");
			}
			sb.append(toPyString(items[i]));
		}
		sb.append("\n");
		if (mTheClient != null) {
			mTheClient.print(sb.toString());
		}
	}

	@SuppressWarnings("unused")
	private List<Object> builtin_range(int start, int... constraints)
			throws ExecutionError {
		if (constraints.length > 2)
			throw internalError("TypeError", "Expected at most 3 arguments");
		int step = 1;
		int stop = 1;
		switch (constraints.length) {
		case 0:
			stop = start;
			start = 0;
			break;
		case 1:
			stop = constraints[0];
			break;
		case 2:
			stop = constraints[0];
			step = constraints[1];
			break;
		}
		if (step == 0)
			throw internalError("ValueError", "step argument must not be zero");
		List<Object> res = new ArrayList<Object>();

		if (step < 0 && stop < start) {
			for (int i = start; i > stop; i += step) {
				res.add(i);
			}
		} else if (step > 0) {
			for (int i = start; i < stop; i += step) {
				res.add(i);
			}
		}
		return res;
	}

	@SuppressWarnings("unused")
	private String builtin_str(Object o) {
		return toPyString(o);
	}

	@SuppressWarnings("unused")
	private String builtin_type(Object o) {
		return toPyTypeString(o);
	}

	// instance methods
	@SuppressWarnings("unused")
	private boolean instance_str_endswith(String s, String suffix) {
		return s.endsWith(suffix);
	}

	@SuppressWarnings({ "rawtypes", "unused" })
	private String instance_str_join(String s, List items)
			throws ExecutionError {
		StringBuilder sb = new StringBuilder();
		for (Object item : items) {
			if (sb.length() > 0) {
				sb.append(s);
			}
			if (!(item instanceof String))
				throw internalError("TypeError", "Can only join string items");
			sb.append((String) item);
		}
		return sb.toString();
	}

	@SuppressWarnings("unused")
	private String instance_str_lower(String s) {
		return s.toLowerCase();
	}

	@SuppressWarnings("unused")
	private String instance_str_replace(String s, String target,
			String replacement) {
		String res = s.replace(target, replacement);
		if (target.length() == 0)
			// Python precedes each character with replacement
			// Java also adds one more on the end which we undo here
			return res.substring(0, res.length() - replacement.length());
		return res;
	}

	@SuppressWarnings({ "unused", "fallthrough" })
	private List<String> instance_str_split(String s, Object... args)
			throws ExecutionError {
		int maxsplit = 0;
		String sep = null;

		switch (args.length) {
		default:
			throw internalError("TypeError",
					"Too many arguments to str.split (at most 2 taken)");
		case 2:
			if (!(args[1] instanceof Integer))
				throw internalError("TypeError",
						"maxsplit should be an integer");
			maxsplit = (Integer) args[1];
			maxsplit++; // Java and Python count differently
		case 1:
			if (!(args[0] instanceof String))
				throw internalError("TypeError", "sep should be an integer");
			sep = (String) args[0];
			if (sep.length() == 0)
				throw internalError("ValueError", "empty separator");
		case 0:
		}
		String[] splits = s.split((sep != null) ? Pattern.quote(sep) : "\\s+",
				maxsplit);
		ArrayList<String> res = new ArrayList<String>(splits.length);
		for (String str : splits) {
			res.add(str);
		}
		return res;
	}

	@SuppressWarnings("unused")
	private boolean instance_str_startswith(String s, String prefix) {
		return s.startsWith(prefix);
	}

	@SuppressWarnings("unused")
	private String instance_str_strip(String s) {
		return s.trim();
	}

	@SuppressWarnings("unused")
	private String instance_str_upper(String s) {
		return s.toUpperCase();
	}

	@SuppressWarnings({ "unchecked", "unused", "rawtypes" })
	private Map instance_dict_copy(Map map) {
		return new HashMap(map);
	}

	@SuppressWarnings({ "unused", "rawtypes" })
	private Object instance_dict_get(Map map, Object key, Object defValue) {
		return map.containsKey(key) ? map.get(key) : defValue;
	}

	@SuppressWarnings({ "unchecked", "rawtypes", "unused" })
	private void instance_dict_update(Map map, Map other) {
		Iterator<Map.Entry> it = other.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry m = it.next();
			map.put(m.getKey(), m.getValue());
		}
	}

	@SuppressWarnings({ "unchecked", "rawtypes", "unused" })
	private void instance_list_append(List list, Object item) {
		list.add(item);
	}

	@SuppressWarnings({ "unchecked", "rawtypes", "unused" })
	private void instance_list_extend(List list, List other) {
		for (Object i : other) {
			list.add(i);
		}
	}

	@SuppressWarnings({ "rawtypes", "unused" })
	private int instance_list_index(List list, Object item) {
		return list.indexOf(item);
	}

	@SuppressWarnings({ "rawtypes", "unused" })
	private Object instance_list_pop(List list) throws ExecutionError {
		if (list.size() == 0)
			throw internalError("IndexError", "pop from empty list");
		Object res = list.get(list.size() - 1);
		list.remove(list.size() - 1);
		return res;
	}

	@SuppressWarnings({ "rawtypes", "unused" })
	private void instance_list_reverse(List list) {
		Collections.reverse(list);
	}

	@SuppressWarnings({ "unchecked", "rawtypes", "unused", "fallthrough" })
	private void instance_list_sort(List list, Object... args)
			throws ExecutionError {
		Callable cmp = null;
		Callable key = null;
		boolean reverse = false;

		switch (args.length) {
		default:
			throw internalError("TypeError", String.format(
					"list.sort() takes most 3 arguments (%d given)",
					args.length));
		case 3:
			if (args[2] != null) {
				if (!(args[2] instanceof Boolean))
					throw internalError("TypeError",
							"list.sort reverse parameter should be boolean not "
									+ toPyTypeString(args[2]));
				reverse = (Boolean) args[2];
			}
		case 2: {
			if (args[1] != null) {
				if (!builtin_callable(args[1]))
					throw internalError("ValueError",
							"list.sort key parameter must be callable");
				key = (Callable) args[1];
			}
		}
		case 1: {
			if (args[0] != null) {
				if (!builtin_callable(args[0]))
					throw internalError("ValueError",
							"list.sort cmp parameter must be callable");
				cmp = (Callable) args[0];
			}
		}
		case 0:
			break;
		}

		// and this is why we like using real programming languages ...
		final Callable javasucks = cmp;
		final Callable javareallysucks = key;
		final ExecutionError[] didimentionsuckage = new ExecutionError[1];

		Comparator comparator = new Comparator() {
			@Override
			public int compare(Object left, Object right) {
				try {
					if (javareallysucks != null) {
						left = call(javareallysucks, left);
						right = call(javareallysucks, right);
					}

					return (javasucks == null) ? builtin_cmp(left, right)
							: (Integer) call(javasucks, left, right);
				} catch (ExecutionError e) {
					didimentionsuckage[0] = e;
					throw new ClassCastException();
				}
			}
		};
		if (reverse) {
			comparator = Collections.reverseOrder(comparator);
		}
		try {
			Collections.sort(list, comparator);
		} catch (ClassCastException e) {
			if (didimentionsuckage[0] != null)
				throw didimentionsuckage[0];
			throw e;
		}
	}

	/**
	 * Provide platform behaviour
	 */
	public interface Client {
		/**
		 * Request to print a string
		 * 
		 * @param s
		 *            String to print. May or may not contain a trailing newline
		 *            depending on code
		 * @throws ExecutionError
		 *             Throw this if you experience any issues
		 */
		public void print(String s) throws ExecutionError;

		/**
		 * Called whenever there is an ExecutionError.
		 * 
		 * This provides one spot where you can perform logging and other
		 * diagnostics.
		 * 
		 * @param error
		 *            The instance that is about to be thrown
		 */
		public void onError(ExecutionError error);
	}

	/**
	 * Encapsulates what would be an Exception in Python.
	 * 
	 * Do not instantiate one directly - call signalError instead.
	 * 
	 */
	public class ExecutionError extends Exception {
		static final long serialVersionUID = -4271385191079964823L;
		private String type, message;
		private int pc;

		private ExecutionError() {
		}

		@Override
		/**
		 * Returns "type: message" for the error
		 */
		public String toString() {
			return getType() + ": " + message;
		}

		/**
		 * Returns the type of the error.
		 * 
		 * This typically corresponds to a Python exception (eg `TypeError` or
		 * `IndexError`)
		 */
		public String getType() {
			return type;
		}

		/**
		 * Returns the line number which was being executed when the error
		 * happened.
		 * 
		 * If you omitted line numbers then -1 is returned.
		 */
		public int linenumber() {
			// note that context.pc points to the instruction after the one
			// being executed
			int lastline = -1;
			for (int i = 0; i < linenumbers.length; i++) {
				if (linenumbers[i][0] >= pc) {
					break;
				}
				lastline = linenumbers[i][1];
			}
			return lastline;
		}

		/**
		 * Returns program counter when error occurred.
		 * 
		 * Note that due to internal implementation details this is the next
		 * instruction to be executed, not the currently executing one.
		 */
		public int pc() {
			return this.pc;
		}
	}
}
