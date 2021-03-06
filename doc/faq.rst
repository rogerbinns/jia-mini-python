Frequently Asked Questions
==========================

Why was this project done?
--------------------------

There was a need for controlling behaviour in a Java library project
that fell between a JSON configuration file and full blown code.

While Jython, Lua or some similar library could be used it would
require version coordination if the app already used those libraries.
Additionally those libraries are orders of magnitude larger than the
original project which is very undesirable.

|project| is just over 800 lines of code (Java)/1,000 (Objective C),
and a single source file which you are encouraged to put into your own
packages thereby avoiding having to coordinate versions.

Is it used in the real world?
-----------------------------

Yes.  It is used to implement the `Appington
<http://www.appington.com>`__ SDK.  The same Python code is used to
control audio downloads and playback.  For example when playing an
audio prompt the locale, time since last audio, caps, and other
criteria need to be taken into account.

The SDK is used in several different Android and iOS applications,
covering millions of users all over the world.

What about hostile code?
------------------------

Code run by |project| is restricted in what it can do.  For
example it can only access modules you explicitly make available, and
then only public methods implemented directly in the module.

You can return and accept any objects, but the code cannot access them
other than passing them around.  This means you could expose instances
but do not have to worry about methods being called on the instances
that would put them into undesirable states.

Code can perform denial of service attacks::

    # infinite loop
    while True:
        pass

    # huge list
    l=[]
    while True:
        l.append(l)

    # huge string
    s="a"
    while True:
        s=s+s

Consequently you should not use "untrusted" code.

What about bugs?
----------------

There is a comprehensive test suite.  Since Python already exists it
provides something to verify answers against.  The test harness is
written in Python.

There is over 99% line coverage and similar branch coverage in the
code.  While this doesn't guarantee the absence of bugs, it at least
assures that the vast majority of code is tested.  (The remaining
lines/branches are generally defensive coding.)

The scope being limited (note "Mini" in the name!) there is also less
functionality and less to go wrong.

Please use the discussion group
https://groups.google.com/forum/#!forum/jia-mini-python and bug
tracker at https://github.com/rogerbinns/jia-mini-python/issues if you
encounter any issues.

What about bugs in my code?
---------------------------

There is no debugger provided or any similar notion of interactivity.
It is easiest/quickest to develop your code using print statements.
On a host computer you can use normal Python `mocking
<http://en.wikipedia.org/wiki/Mock_object>`__ the modules.

When there are errors you get a line number that can be looked up, as
well as a program counter which can be used with an :doc:`annotated
listing <jmp-compile>` to find the exact issue.

Use asserts to verify operation of your code.  By default they are
ignored but you can turn them on passing :option:`--asserts` to
:doc:`jmp-compile`.  A large portion of the test suite is implemented
using asserts.
