#!/usr/bin/env python

import os
import sys
import tempfile
import subprocess
import unittest
import glob
import re
import json
import time
import imp
import array

opj=os.path.join

topdir=os.path.abspath(opj(os.path.dirname(__file__), ".."))
coveragedir=opj(topdir, "coverage")
jarfile=opj(topdir if not os.getenv("JMPCOVERAGE") else coveragedir, "bin", "MiniPython.jar")
testfiledir=opj(topdir, "test")
jmpcompiler=opj(topdir, "host", "jmp-compile")

covoptions=["-cp", jarfile]
if os.getenv("JMPCOVERAGE"):
    assert os.getenv("COBERTURADIR"), "$COBERTURADIR needs to be set"
    jars=[jarfile, opj(os.getenv("COBERTURADIR"), "cobertura.jar")]
    for f in glob.glob(opj(os.getenv("COBERTURADIR"), "lib", "*.jar")):
        jars.append(f)
    covoptions=["-cp", os.pathsep.join(jars),
                "-Dnet.sourceforge.cobertura.datafile="+os.path.abspath(opj(coveragedir, "cobertura.ser"))]

with open(opj(topdir, "host", "jmp-compile"), "rtU") as f:
    jmpcompilemod=imp.new_module("jmp_compile")
    exec f in jmpcompilemod.__dict__, jmpcompilemod.__dict__
    jmpcompilerobject=jmpcompilemod.Compiler()

def jmp_compile_internal(infile, outfile=None):
    class options:
        print_function=False
        asserts=True
    if outfile is None:
        outfile=os.path.splitext(infile)[1]+".jmp"
    jmpcompilerobject.compile(options, infile, outfile)

def delfiles(files):
    for f in files:
        try:
            os.remove(f)
        except:
            pass


class JavaMiniPython(unittest.TestCase):

    def jmp_compile(self, infile, outfile=None, print_function=False):
        outfile=[outfile] if outfile else []
        out,err=self.run_external_command([jmpcompiler]+(["--print-function"] if print_function else [])+["--asserts", infile]+outfile)
        self.assertEqual(err, "")

    def run_jar(self, filename, args=[]):
        cmd=["java"]+covoptions+["com.rogerbinns.Tester"]
        cmd.extend(args)
        cmd.append(filename)
        return self.run_external_command(cmd)

    def run_external_command(self, args):
        j=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err=j.communicate()
        if j.returncode!=0:
            self.assertNotEqual(err, "")
        else:
            self.assertEqual(err, "")
        return out, err

    def testCmp(self):
        "Test comparisons"
        self.run_py("test/cmp.py")
        
    def testDict(self):
        "Test dictionaries"
        self.run_py("test/dict.py")

    def testString(self):
        "Test strings"
        self.run_py("test/string.py")

    def testList(self):
        "Test lists"
        self.run_py("test/list.py")

    def testGeneral(self):
        "Test various operations"
        self.run_py("test/general.py")

    def run_py(self, name):
        self.jmp_compile(name)
        out,err=self.run_jar(os.path.splitext(name)[0]+".jmp")
        self.assertEqual("", err)

    def testErrors(self):
        "Test various operations that should result in errors"
        # we read errors.py which has multiple stanzas starting with
        # #> followed by a prefix or regex and then some code that
        # should raise that error
        tests=[]
        code=[]
        for lineno,line in enumerate(open("test/errors.py")):
            lineno+=1 # we count from one for files
            if line.startswith("#>") or line.startswith("#."):
                if code:
                    tests.append( (linestart, pattype, pat, "".join(code)) )
                    code=[]
                linestart=lineno
                pat=line[2:].strip()
                pattype=["out","err"][line[1]==">"]
                continue
            code.append(line)
        if code:
            tests.append( (linestart, pattype, pat, "".join(code)) )

        with open("test/errors.jmp", "wb") as jmp:
            for _,_,_, code in tests:
                with tempfile.NamedTemporaryFile(prefix="runtest") as tmppyf, \
                        tempfile.NamedTemporaryFile(prefix="runtest") as tmpjmpf:
                    tmppyf.write(code)
                    tmppyf.flush()
                    jmp_compile_internal(tmppyf.name, tmpjmpf.name)
                    jmp.write(tmpjmpf.read())
        out,err=self.run_jar("test/errors.jmp", args=["--multi"])
        self.assertEqual(err, "")
        results=json.loads(out)
        self.assertEqual(len(results), len(tests))
        for num, (lineno, pattype, pat, _) in enumerate(tests):
            out,err=results[num]
            against=[out,err][pattype=="err"]
            if "*" in pat:
                self.assert_(re.match(pat, against, re.DOTALL|re.IGNORECASE), "Failed to match at line %d of errors.py\n%s = %s" % (lineno, pattype, against))
            else:
                self.assert_(against.startswith(pat), "Failed to prefix at line %d of errors.py\n%s = %s" % (lineno,pattype, against))

    def testPrintFunction(self):
        "Test print function"
        for expect, code in (
            ('\n', 'print()'),
            ('1 2\n', 'print(1,2)'),
            ):
            with tempfile.NamedTemporaryFile() as tmpf, tempfile.NamedTemporaryFile() as jmp:
                tmpf.write(code)
                tmpf.flush()
                self.jmp_compile(tmpf.name, jmp.name, print_function=True)
                out,err=self.run_jar(jmp.name)
                self.assertEqual(err, "")
                self.assertEqual(out, expect)
                
    def testCorrupt(self):
        "Corrupted input"

        testpats=[]
        t=array.array('B', [0,0, 0,0, 0,0, 10,0, 0, 1, 2, 3])
        for i in range(1, len(t)+1):
            testpats.append( ("Unexpected end of file", t[:i]) )

        if False:
            # Cobertura bug: doesn't see these so no point running them
            for i in [20]+range(35,128)+range(134,160)+range(165,200)+range(202,56):
                testpats.append(("RuntimeError: Unknown/unimplemented opcode: "+str(i),
                                 array.array('B', [0,0,0,0, 0,0, 3,0, i,0,0])))

        testpats.append(("RuntimeError: Unknown/unimplemented opcode: 245",
                         array.array('B', [0,0,0,0, 0,0, 3,0, 245,0,0])))

        testpats.append(("Failure: java.io.IOException: Unknown JMP version number 1",
                         array.array('B', [1,0])))

        testpats.append(("Unexpected end of file",
                         array.array('B', [0,0,1,0, 245,0,0])))
        # This is invalid utf8 but java is happy to accept it
        testpats.append(("",
                         array.array('B', [0,0,1,0, 4,0, 0xf0, 0x28, 0x8c, 0x28, 0, 0, 1, 0, 19])))
        for expect, code in testpats:
            with tempfile.NamedTemporaryFile() as tmpf:
                # array decides tempfiles are not open files
                code.tofile(open(tmpf.name, "wb"))
                out,err=self.run_jar(tmpf.name)
                self.assert_(err.startswith(expect), "Expected: %r, Got: %r" % (expect,err))

    def testSource(self):
        "Source checks"
        for lineno,line in enumerate(open("src/com/rogerbinns/MiniPython.java", "rtU")):
            if "internalError" in line and "private" not in line and "SOURCECHECKOK" not in line:
                self.assert_("throw internalError" in line, "Line %d doesn't throw internalError" % (lineno+1,))

    def testClear(self):
        "Test clear()"
        for pf in False, True:
            with tempfile.NamedTemporaryFile() as tmpf, tempfile.NamedTemporaryFile() as jmp:
                tmpf.write("print(3)\ntest1\n")
                tmpf.flush()
                self.jmp_compile(tmpf.name, jmp.name, print_function=pf)
                out,err=self.run_jar(jmp.name, args=["--clear"])
                self.assertEqual(out, "")
                self.assertNotEqual(err, "")
                self.assert_(err.startswith("NameError"))
        

def main():
    # Check the jar file is present
    if not os.path.exists(jarfile):
        raise Exception("Couldn't find built test code.  Run ant to produce "+jarfile)

    unittest.main()

if __name__=='__main__':
    main()
