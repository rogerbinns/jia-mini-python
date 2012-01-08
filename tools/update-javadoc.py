#!/usr/bin/env python

import os
import sys
import glob
import tempfile
import json
import shutil
import subprocess
import re

opj=os.path.join
topdir=os.path.abspath(opj(os.path.dirname(__file__), ".."))

# I did try using a program to provide javadoc information in JSON
# format but unfortunately it had far too many bugs.

def genjson(filename):
    incomment=False
    content=None
    thejson={"packages": {}}
    package=None
    state={}
    with open(filename, "rtU") as f:
        for line in f:
            if line.strip().startswith("package"):
                line=line.strip().strip(";")
                package=line.split()[1]
                thejson["packages"][package]={"classes": {}}
                continue
            if line.strip().startswith("/**"):
                # process comment and whatever follows
                assert incomment==False
                content=[]
                incomment=True
                continue
            if incomment:
                if line.strip().startswith("*/"):
                    incomment=False
                    continue
                content.append(line)
                continue
            if content:
                if line.strip():
                    update(thejson, package, content, line, state)
                else:
                    assert False, "Comment followed by blank "+"".join(content)
                content=None
            continue
    return thejson

# this should really be a nested function in genjson
def update(thejson, package, content, line, state):
    # Fixup the line
    line=line.replace("{", " ").replace(",", ", ")
    line=re.sub(r"\bpublic\b", "", line)
    line=re.sub(r"\s+", " ", line)
    line=line.strip()
    # fixup content
    content=[re.sub(r"^\s*\*\s?", "", unhtml(c.strip())).rstrip() for c in content]
    # massage into right place
    if line.split()[0] in ("interface", "class"):
        name=line.split()[1]
        if not name.startswith("MiniPython"):
            name="MiniPython."+name
        thejson["packages"][package]["classes"][name]={"type": line.split()[0], "methods": {}, "comment-text": "\n".join(content)}
        state["curmeth"]=thejson["packages"][package]["classes"][name]["methods"]
    else:
        line=re.sub(r"\bthrows\b.*", "", line).strip()
        name=re.match(r".*?(?P<name>\b\w+\b)\(.*", line).group("name")
        state["curmeth"][name]={"signature": line, "comment-text": "\n".join(content)}

def update_doc(data):
    res=[]
    indentlevel=0
    def indent():
        return indentlevel*"   "

    for klass,doc in sorted(data["packages"]["com.rogerbinns"]["classes"].items()):
        res.append(".. _"+klass.split(".")[-1]+":")
        res.append("")
        res.append("%s %s" % (doc["type"], klass))
        res.append("-"*len(res[-1]))
        res.append("")
        savedindent=indentlevel
        res.append(indent()+".. class:: "+klass)
        res.append("")
        indentlevel+=1
        res.append(indent()+"(`javadoc <_static/javadoc/com/rogerbinns/%s.html>`__)" % (klass,))
        for line in doc["comment-text"].split("\n"):
            if(line):
                res.append(indent()+line)
            else:
                res.append("")
        for name, meth in sorted(doc["methods"].items()):
            res.append("")
            res.append(indent()+".. method:: "+meth["signature"])
            res.append("")
            indentlevel+=1
            lines=meth["comment-text"].split("\n")
            pos=0
            while pos<len(lines):
                line=lines[pos]
                if line.strip():
                    line=fixup(line) 
                if not isinstance(line, tuple):
                    line=(line,)
                for l in line:
                    if(l.strip()):
                        res.append(indent()+l)
                    else:
                        res.append("")
                if res[-1].rstrip().endswith(":"):
                    # append next line to it
                    res[-1]=res[-1]+" "+lines[pos+1].strip()
                    pos+=1
                pos+=1
            indentlevel-=1
              
        res.append("")
        indentlevel=savedindent

    return "\n".join(res)

def unhtml(line):
    # strip/replace html tags we use with rst
    line=line.replace("<p>", "").replace("</p>", "") 
    
    line=re.sub(r'<a.*?\bhref="(?P<addr>[^"]+?)".*?>(?P<text>.*?)</a>', 
                r'`\g<text> <\g<addr>>`__',
                line)

    assert "/>" not in line
    return line

def fixup(line):
    # turn javadoc @stuff into sphinx
    x=line.split(None, 2)
    while len(x)<3:
        x.append("")
    if x[0]=="@param":
        return ":param %s: %s" % (x[1], x[2])
    elif x[0]=="@throws":
        return ":raises %s: %s" % (x[1], x[2])
    elif x[0]=="@see":
        x=line.split(None, 1)[1]
        # strip leading ../
        x=re.sub(r"<(../)+", "<", x)
        return ("", ".. seealso:: "+x)
    elif x[0].startswith("@"):
        import pdb ; pdb.set_trace()
        pass
    if "@" in line:
        import pdb ; pdb.set_trace()
        pass
    return line

def update_file(name, content):
    res=[]
    found=False
    with open(name, "rtU") as f:
        for line in f:
            if line.strip()==".. Rest of file is generated from Javadoc - do not edit":
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
        print "Updating",name,"from Javadoc"
        with open(name, "wt") as f:
            f.write(res)

if __name__=='__main__':
    data=genjson(opj(topdir, "src", "com", "rogerbinns", "MiniPython.java"))
    res=update_doc(data)
    update_file(opj(topdir, "doc", "java.rst"), res)
    
