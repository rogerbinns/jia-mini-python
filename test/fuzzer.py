#!/usr/bin/env python

import array
import random
import sys
import multiprocessing, multiprocessing.queues
import time

# we skip exit loop
validops=range(19)+range(21,36)+range(128,134)+range(160,166)+range(200, 203)
# this make the stack bigger and we bias towards them. push_str is left out
# because it often has invalid index
addops=[18, 21, 22, 200, 160, 128]


seq=[]
while len(seq)<55000:
    # most operations consume the stack so we bias back in ones that add to the stack
    seq.extend(addops*200)
    seq.extend(validops)
while len(seq)<65536:
    seq.extend(range(256))

# Python on Mac is UCS-2 and mangles codepoints about U+FFFF so we work
# around that
chars="a", "b", "c", "1", "2", "3", u"\u1234", u"\ufe54", " ", u"\N{LIGHTNING}", u"\N{MUSICAL SYMBOL G CLEF}"

basestrings=["test", "foo", "int", "bool", "apply", "callable", "cmp", "filter", "map", "globals", "id", "len", "locals", "print", "range", "str", "type", "copy", "get", "update", "append", "extend", "index", "pop", "reverse", "sort", "endswith", "join", "lower", "replace", "split", "startswith", "strip", "upper", "init", "retNone", "takesAll", "retSelf", "add", "signalBatman", "badeqlist", "badeqdict"]

def get_another(seed):
    random.seed(seed)
    out=[0,0] # version
    nstrings=random.randrange(65536)
    out.extend( (nstrings%256, nstrings/256) )
    for i in range(nstrings):
        if i%5==0:
            string=random.choice(basestrings)
        else:
            string=list(chars)
            random.shuffle(string)
            string="".join(string[:random.randrange(len(string))])
        stringbytes=[ord(c) for c in string.encode("utf8")]
        out.extend( (len(stringbytes)%256, len(stringbytes)/256) )
        out.extend(  stringbytes )
    out.extend( (1,0)) # linenumbers - we encode random seed in them
    out.extend( (seed & 0xff, (seed>>8)&0xff, (seed>>16)&0xff, (seed>>24)&0xff) )
    bytecodes=seq[:random.randrange(65536)]
    random.shuffle(bytecodes)
    out.extend( (len(bytecodes)%256, len(bytecodes)/256) )
    out.extend( bytecodes )

    return array.array('B', out)

def workerloop(inq, outq):
    while True:
        outq.put(get_another(inq.get()))

def make_fuzz_file(seconds):
    workq=multiprocessing.queues.SimpleQueue()
    resultq=multiprocessing.queues.SimpleQueue()
    seed=0

    for _ in range(4):
        workq.put(seed)
        seed+=1

    for _ in range(4):
        worker=multiprocessing.Process(target=workerloop, args=(workq, resultq))
        worker.daemon=True
        worker.start()

    start=time.time()
    with open("/dev/stdout", "wb", 0) as f:
        while time.time()-start<seconds:
            workq.put(seed)
            seed+=1
            data=resultq.get()
            f.write(data)

if __name__=='__main__':
    def usage(): sys.exit("fuzzer seconds-to-run-for")

    if len(sys.argv)!=2:
        usage()

    make_fuzz_file(int(sys.argv[1]))



