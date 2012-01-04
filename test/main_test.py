#!/usr/bin/env python

import os
import sys
import tempfile
import subprocess
import unittest
import glob
import re
import json

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
    

def delfiles(files):
    for f in files:
        try:
            os.remove(f)
        except:
            pass


class JavaMiniPython(unittest.TestCase):

    def jmp_compile(self, infile, *outfile):
        out,err=self.run_external_command([jmpcompiler, "--asserts", infile]+list(outfile))
        self.assertEqual(err, "")

    def run_jar(self, filename, multi=False):
        cmd=["java"]+covoptions+["com.rogerbinns.Tester"]
        if multi:
            cmd.append("--multi")
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
            if line.startswith("#>"):
                if code:
                    tests.append( (linestart, pat, "".join(code)) )
                    code=[]
                linestart=lineno
                pat=line[2:].strip()
                continue
            code.append(line)
        if code:
            tests.append( (linestart, pat, "".join(code)) )

        with open("test/errors.jmp", "wb") as jmp:
            for _,_, code in tests:
                with tempfile.NamedTemporaryFile(prefix="runtest") as tmppyf, \
                        tempfile.NamedTemporaryFile(prefix="runtest") as tmpjmpf:
                    tmppyf.write(code)
                    tmppyf.flush()
                    self.jmp_compile(tmppyf.name, tmpjmpf.name)
                    jmp.write(tmpjmpf.read())
        
        out,err=self.run_jar("test/errors.jmp", multi=True)
        self.assertEqual(err, "")
        results=json.loads(out)
        self.assertEqual(len(results), len(tests))
        for num, (lineno, pat, _) in enumerate(tests):
            out,err=results[num]
            if "*" in pat:
                self.assert_(re.match(pat, err, re.DOTALL|re.IGNORECASE), "Failed to match at line %d of errors.py\nerr = %s" % (lineno, err))
            else:
                self.assert_(err.startswith(pat), "Failed to prefix at line %d of errors.py\nerr = %s" % (lineno,err))

    def testSource(self):
        "Source checks"
        for lineno,line in enumerate(open("src/com/rogerbinns/MiniPython.java", "rtU")):
            if "internalError" in line and "private" not in line:
                self.assert_("throw internalError" in line, "Line %d doesn't throw internalError" % (lineno+1,))

def main():
    # Check the jar file is present
    if not os.path.exists(jarfile):
        raise Exception("Couldn't find built test code.  Run ant to produce "+jarfile)

    unittest.main()

if __name__=='__main__':
    main()
