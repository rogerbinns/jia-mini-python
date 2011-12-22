package com.rogerbinns;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;

public class MiniPython {

	String[] strings;
	int[] integers;
	int[][] linenumbers;
	byte[] code;

	public void setCode(InputStream is) throws IOException {
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
		if(is.read(b)!=byteslen)
			throw new EOFException();
		return new String(b, "UTF8");
	}
}
