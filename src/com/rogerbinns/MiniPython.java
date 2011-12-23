package com.rogerbinns;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;

public class MiniPython {

	String[] strings;
	int[] integers;
	int[][] linenumbers;
	byte[] code;
	boolean hasRun;

	Context root;
	Object[] stack;
	int stacktop;

	public void setCode(InputStream is) throws IOException {
		hasRun=false;

		// string table
		int stablen=get16(is);
		strings=new String[stablen];
		for(int i=0; i<stablen; i++) {
			strings[i]=getUTF(is, get16(is));
		}
		// integer table
		int itablen=get16(is);
		integers=new int[itablen];
		for(int i=0; i<itablen; i++) {
			integers[i]=get32(is);
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

	private static final int get32(InputStream is) throws IOException {
		int a=is.read(),
				b=is.read(),
				c=is.read(),
				d=is.read();
		if(a<0 || b<0 || c<0 || d<0)
			throw new EOFException();
		return a+(b<<8)+(c<<16)+(d<<24);
	}

	private static final String getUTF(InputStream is, int byteslen) throws IOException {
		byte[] b=new byte[byteslen];
		// ::TODO:: while loop dealing with incomplete reads
		if(is.read(b)!=byteslen)
			throw new EOFException();
		return new String(b, "UTF8");
	}

	private final void firstRun() {
		root=new Context(0);
		stack=new Object[256];
		stacktop=-1;
		mainLoop(root);
	}

	private final class Context {
		Context parent;
		int pc;
		Context(int pc) {
			this.pc=pc;
		}
	}

	private final void mainLoop(Context context) throws ExecutionError {
		int op, val=-1;
		while(true) {
			op=code[context.pc] & 0xff;
			context.pc++;
			if(op>=128) {
				val=(code[context.pc]&0xff)+((code[context.pc+1]&0xff)<<8);
				context.pc+=2;
			}
			switch(op) {
			// -- check start : marker used by tool
			case 200: // PUSH_INT
				try {
					stack[++stacktop]=integers[val];
				} catch(ArrayIndexOutOfBoundsException e) {
					extendStack();
					context.pc-=3;
					stacktop--;
				}
				continue;
			case 162: // PUSH_STR
				try {
					stack[++stacktop]=strings[val];
				} catch(ArrayIndexOutOfBoundsException e) {
					extendStack();
					context.pc-=3;
					stacktop--;
				}
				continue;
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
				internalErrorBinaryOp("multiply", left, right);
			}
			case 11: // POP_TOP
				stacktop--;
				continue;
			case 0: // FUNCTION_PROLOG
			case 1: // ADD
			case 3: // DIV
			case 4: // GT
			case 5: // LT
			case 6: // EQ
			case 7: // IN
			case 8: // UNARY_ADD
			case 9: // RETURN
			case 10: // CALL
			case 12: // ATTR
			case 13: // UNARY_NEG
			case 14: // SUBSCRIPT
			case 15: // SUBSCRIPT_SLICE
			case 16: // DICT
			case 17: // LIST
			case 18: // PUSH_NONE
			case 128: // SET_METHOD
			case 129: // GOTO
			case 130: // IF_FALSE
			case 160: // LOAD_NAME
			case 161: // STORE_NAME
				// -- check end : marker used by tool
			default:
				internalError(String.format("Unknown/unimplemented opcode: %d", op));
				break;
			}
		}
	}

	private void extendStack() throws ExecutionError {
		int newsize=stack.length+512;
		if(newsize>8192) {
			internalError("Maximum stack depth exceeded");
		}
		Object[] newstack=new Object[newsize];
		System.arraycopy(stack, 0, newstack, 0, stack.length);
		stack=newstack;
	}

	private void internalError(String message) throws ExecutionError {
		// need to know current context
		throw new ExecutionError();
	}

	private void internalErrorBinaryOp(String op, Object left, Object right) throws ExecutionError {
		internalError(String.format("Can't %s %s %s", left.getClass().getSimpleName(), op, right.getClass().getSimpleName()));
	}

	public void signalError(String message) throws ExecutionError {
		internalError(message);
	}

	class ExecutionError extends Exception {

	}
}
