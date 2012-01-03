#!/usr/bin/env python

import os
import sys
import tempfile
import subprocess
import unittest
import glob

opj=os.path.join

topdir=os.path.abspath(opj(os.path.dirname(__file__), ".."))
coveragedir=opj(topdir, "coverage")
jarfile=opj(topdir if not os.getenv("JMPCOVERAGE") else coveragedir, "bin", "MiniPython.jar")
testfiledir=opj(topdir, "test")
jmpcompiler=opj(topdir, "host", "jmp-compile")

covoptions=[]
if os.getenv("JMPCOVERAGE"):
    assert os.getenv("COBERTURADIR"), "$COBERTURADIR needs to be set"
    jars=[opj(os.getenv("COBERTURADIR"), "cobertura.jar")]
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

    def jmp_compile(self, infile, outfile):
        return self.run_external_command([jmpcompiler, "--asserts", infile, outfile])

    def run_jar(self, filename):
        cmd=["java"]+covoptions+["-jar", jarfile, filename]
        print ">>>", cmd
        return self.run_external_command(cmd)

    def run_external_command(self, args):
        j=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err=j.communicate()
        if j.returncode!=0:
            self.assertNotEqual(err, "")
        else:
            self.assertEqual(err, "")
        return out, err


    def run_jar_success(self, expect, code):
        files=[]
        try:
            f=tempfile.NamedTemporaryFile(prefix="runtest", dir=testfiledir)
            tn=f.name+".py"
            f.close()
            files.append(tn)
            with open(tn, "wt") as f:
                f.write(code)
            jmp=tn+".jmp"
            files.append(jmp)
            self.jmp_compile(tn, jmp)
            out, err=self.run_jar(jmp)
            self.assertEqual(err, "")
            o=out.strip()
            self.assertEqual(o, expect)
        finally:
            delfiles(files)


    def testCmp(self):
        self.jmp_compile("test/cmp.py", "test/cmp.jmp")
        self.run_jar("test/cmp.jmp")
        
def main():
    # Check the jar file is present
    if not os.path.exists(jarfile):
        raise Exception("Couldn't find built test code.  Run ant to produce "+jarfile)

    unittest.main()

if __name__=='__main__':
    main()
