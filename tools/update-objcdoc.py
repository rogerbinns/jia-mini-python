#!/usr/bin/env python

import os
import textwrap
import re

opj=os.path.join
topdir=os.path.abspath(opj(os.path.dirname(__file__), ".."))


def update_file(name, content):
    res=[]
    found=False
    with open(name, "rtU") as f:
        for line in f:
            if line.strip()==".. Rest of file is generated from MiniPython.h - do not edit":
                res.append(line+"\n")
                res.append(content)
                res="".join(res)
                found=True
                break
            res.append(line)

    if not found:
        raise Exception("Comment marker not found in file")
    with open(name, "rtU") as f:
        existing=f.read()
    if existing!=res:
        print "Updating",name,"from MiniPython.h"
        with open(name, "wt") as f:
            f.write(res)

def get_doc(ifile):
    res=[]
    initem=False
    incomment=False
    comment=""
    for line in open(ifile, "rtU"):
        if line.strip().startswith("/**"):
            assert not incomment
            incomment=True
            comment=""
            continue
        if incomment and line.strip().startswith("*/"):
            incomment=False
            comment=textwrap.dedent(comment)
            continue
        if initem and line.startswith("@end"):
            initem=False
            res.append("")
            continue
        if line.startswith("@"):
            assert not initem
            initem=True
            x=line.split()[1]
            res.append(":index:`%s <%s (Objective C)>`" % (x,x))
            res.append("-"*len(res[-1]))
            res.append("")
            res.extend("  "+c for c in comment.split("\n"))
            comment=""
            continue
        if incomment:
            comment+=line
            continue
        if initem and line.strip():
            meth=line.replace(";", "").strip()
            if ":" in meth:
                idx=":".join(re.findall(r"\b(\w+)\b\s*:\s*\([^)]+\)\s*\w+\s*", meth))+":"
            else:
                idx=re.match(r"\s*[\+\-]\s*\([^)]+\)\s*\b(?P<name>\w+)\b\s*", meth).group("name")
            res.append("  .. index:: "+idx+" (Objective C method)")
            res.append("")
            res.append("  .. method:: "+meth)
            res.append("")
            res.extend("     "+c for c in comment.split("\n"))
            comment=""
    return "\n".join(res)

if __name__=='__main__':
    res=get_doc(opj(topdir, "src", "MiniPython.h"))
    update_file(opj(topdir, "doc", "objc.rst"), res)
