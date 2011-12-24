#!/usr/bin/env python

import os
import sys
import tempfile
import subprocess
import unittest

opj=os.path.join

topdir=os.path.abspath(opj(os.path.dirname(__file__), ".."))
jarfile=opj(topdir, "bin", "MiniPython.jar")
testfiledir=opj(topdir, "test")
jmpcompiler=opj(topdir, "host", "jmp-compile")

def delfiles(files):
    for f in files:
        try:
            os.remove(f)
        except:
            pass


class JavaMiniPython(unittest.TestCase):

    def jmp_compile(self, infile, outfile):
        return self.run_external_command([jmpcompiler, infile, outfile])

    def run_jar(self, filename):
        return self.run_external_command(["java", "-jar", jarfile, filename])

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


    def testSanityCheck(self):
        "Verify basic operations work/fail as expected"
        # we try all operations against all types that should succeed
        testvals=[
            "a string",
            3423,
            False, 
            True,
            None]

        testops=[
            "+", "-", "*", "/", "and", "or", "not", "<", ">", "==", "<=", ">=", "!="
            ]

        workingcombos=[]
        failcombos=[]

        for left in testvals:
            for op in testops:
                for right in testvals:
                    testcase="%r %s %r" % (left, op, right)
                    try:
                        res=eval(testcase)
                        workingcombos.append( (res, testcase) )
                    except Exception,e:
                        failcombos.append( (e, testcase) )

        for res, case in workingcombos:
            self.run_jar_success(res, "print "+case)

        for res, case in failcombos:
            self.run_jar_fail(res, "print "+case)

def main():
    # Check the jar file is present
    if not os.path.exists(jarfile):
        raise Exception("Couldn't find built test code.  Run ant to produce "+jarfile)

    unittest.main()

if __name__=='__main__':
    main()
