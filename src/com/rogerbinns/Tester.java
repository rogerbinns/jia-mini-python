package com.rogerbinns;

import java.io.EOFException;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import com.rogerbinns.MiniPython.ExecutionError;

public class Tester {

	public static void main(String[] args) {
		boolean multimode=false;

		if(args.length<1) {
			usage();
		}

		while(args.length>0 && args[0].startsWith("--")) {
			int nargs=0;
			if(args[0].equals("--multi")) {
				multimode=true;
				nargs=1;
			} else {
				usage();
			}
			// yes this awful - prune args
			List<String> l = new ArrayList<String>(Arrays.asList(args));
			for(int i=0; i<nargs; i++) {
				l.remove(0);
			}
			args = l.toArray(new String[0]);
		}

		if (args.length!=1) {
			usage();
		}

		InputStream is = null;
		try {
			is=new FileInputStream(args[0]);
		} catch (Exception e) {
			System.err.printf("Failed to open input file: %s\n", e);
			System.exit(3);
		}
		final MiniPython mp=new MiniPython();
		final StringBuilder out=new StringBuilder(), err=new StringBuilder();
		final boolean fmultimode=multimode;

		mp.setClient(new MiniPython.Client() {
			@Override
			public void print(String s) throws ExecutionError {
				if(fmultimode) {
					out.append(s);
				} else {
					System.out.print(s);
				}
			}

			@Override
			public void onError(ExecutionError error) {
				if(fmultimode) {
					err.append(error.toString()+"\n");
					err.append(String.format("Line %d.  pc=%d\n", error.linenumber(), error.pc()));
				} else {
					System.err.println(error);
					System.err.printf("Line %d.  pc=%d\n", error.linenumber(), error.pc());
					System.err.flush();
				}
			}
		});

		mp.addModule("test1", new Test1());

		if(multimode) {
			System.out.print("[");
		}
		boolean first=true;
		do {
			out.setLength(0);
			err.setLength(0);

			try {
				mp.setCode(is);
				if(!multimode) {
					System.exit(0);
				}
			} catch(EOFException e) {
				if(multimode) {
					System.out.println("]");
					System.exit(0);
				}
				System.err.println("Unexpected end of file");
			} catch (IOException e) {
				System.err.printf("Failure: %s\n", e);
				System.exit(1);
			} catch (ExecutionError e) {
				// we printed in the client
				if(!multimode) {
					System.exit(7);
				}
			}
			if(first) {
				first=false;
			} else {
				System.out.println(",");
			}
			if(multimode) {
				System.out.print("["+toJSON(out.toString())+", "+toJSON(err.toString())+"]");
			}
		} while(multimode);
	}

	static void usage() {
		System.err.println("Usage: Tester [--multi] inputfile");
	}

	static String toJSON(String s) {
		return '"'+s.replace("\\", "\\\\")
				.replace("\"", "\\\"")
				.replace("\n", "\\n")
				.replace("/", "\\/")
				+'"';
	}

	static class Test1
	{
		public void retNone() {}
		@SuppressWarnings("rawtypes")
		public void takesAll(Boolean b, boolean b2, Map m, List l, Integer i, int i2, Test1 t1) {}
		public Test1 retSelf() { return this; }
	}
}
