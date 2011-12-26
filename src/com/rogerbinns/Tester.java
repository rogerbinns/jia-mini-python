package com.rogerbinns;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

import com.rogerbinns.MiniPython.ExecutionError;

public class Tester {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (args.length!=1) {
			System.err.print("Expected exactly one argument - .jmp file to read\n");
			System.exit(2);
		}
		InputStream is = null;
		try {
			is=new FileInputStream(args[0]);
		} catch (Exception e) {
			System.err.printf("Failed to open input file: %s\n", e);
			System.exit(3);
		}
		MiniPython mp=new MiniPython();
		mp.setClient(new MiniPython.Client() {
			@Override
			public void print(String s) throws ExecutionError {
				System.out.print(s);
				System.out.flush();
			}
		});

		@SuppressWarnings("unused") // used via reflection, why does it whine?
		class TimeWrapper {
			public int time() {
				return (int) (System.currentTimeMillis()/1000);
			}
			public int add(int x, int y) {
				return x+y;
			}
			private int veryprivate() {
				return 3;
			}
			public void returnsvoid() {

			}
			public String vatest(String s, int... ints) {
				return s+ints.toString();
			}
		}

		mp.addModule("time", new TimeWrapper());
		try {
			mp.setCode(is);
			System.exit(0);
		} catch (ExecutionError e) {
			System.err.println(e);
			System.err.printf("Line %d.  pc=%d\n", e.linenumber(), e.pc());
			System.exit(5);
		} catch (IOException e) {
			System.err.printf("Failure: %s\n", e);
			System.exit(1);
		}
	}

}
