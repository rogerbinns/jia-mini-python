VERSION = 2.1
DATE = "31 July 2014"

# use python3 for python3
PYTHON=python

# Used for coverage
COBERTURADIR=/space/cobertura

.PHONY: doc docs publish test ant help javadoc coverage dist obin valgrind ocoverage clean

help:
	@echo "Use \`make <target>' where target is one of"
	@echo "  test      Run tests using standard Python (java based)"
	@echo "  otest     Run tests for Objective C implementation"
	@echo "  ant       Build a jar file for command line usage and testing"
	@echo "  doc       To build the documentation using sphinx"
	@echo "  coverage  Run the test suites with coverage"
	@echo "  ocoverage Coverage for objective C"
	@echo "  dist      Produce final code and doc suitable for redistribution"

docs: doc

doc: javadoc objdoc
	make -C doc html VERSION=$(VERSION) DATE=$(DATE)

linkcheck:
	make -C doc linkcheck VERSION=$(VERSION) DATE=$(DATE)

clean:
	rm -rf bin/* doc/_build *.gcov *.gcda *.gcno coverage build dist

publish: doc
	rsync -av --delete --exclude=.git --exclude=.nojekyll doc/_build/html/ ../jmp-doc/
	cd ../jmp-doc && git status

ant:
	ant -q

test: ant
	$(PYTHON) test/main_test.py

otest: obin
	$(PYTHON) test/main_test.py objc

obin: bin/testminipython

bin/testminipython: src/MiniPython.h src/MiniPython.m src/testMiniPython.m Makefile
	$(CC) -g -Weverything -fobjc-arc \
	src/MiniPython.m src/testMiniPython.m -framework Foundation -lobjc  -o $@

# Requires minimum clang/llvm3.2 http://stackoverflow.com/questions/8826682/
# use -a with gcov to get each block
COVERAGECC=clang
ocoverage:
	-rm -rf *.gcda *.gcno *.gcov coverage
	$(COVERAGECC) --coverage -fsanitize -g -Weverything -fobjc-arc src/MiniPython.m src/testMiniPython.m -framework Foundation -lobjc  -o bin/testminipython
	python test/main_test.py objc
	gcov -bc src/MiniPython.m

valgrind: obin
	valgrind --dsymutil=yes --redzone-size=4096 --track-origins=yes --freelist-vol=1000000000 --leak-check=full --show-reachable=yes bin/testminipython $(TEST)

JAVADOCDIR="doc/_build/javadoc"

javadoc:
	@rm -rf $(JAVADOCDIR)
	@mkdir -p $(JAVADOCDIR)
	javadoc -notimestamp -quiet -nodeprecatedlist -use -notree -nohelp -sourcepath src -d $(JAVADOCDIR)/javadoc -link http://docs.oracle.com/javase/7/docs/api/  src/com/rogerbinns/MiniPython.java
	tools/update-javadoc.py

objdoc:
	tools/update-objcdoc.py

# The cobertura-instrument script shipped by them is completely borken
# hence taking matters into our own hands
coverage:
	@rm -rf coverage bin
	@mkdir -p coverage/bin
	ant -q
	java -classpath "$(COBERTURADIR)/cobertura.jar:$(COBERTURADIR)/lib/*:bin/MiniPython.jar" net.sourceforge.cobertura.instrument.Main --datafile `pwd`/coverage/cobertura.ser --destination coverage bin/MiniPython.jar
	env JMPCOVERAGE=t COBERTURADIR=$(COBERTURADIR) python test/main_test.py
	bash $(COBERTURADIR)/cobertura-report.sh --datafile coverage/cobertura.ser --destination coverage src
	@echo "Report in coverage/com.rogerbinns.MiniPython.html"

BUILDDIR="build/JiaMiniPython-$(VERSION)"

dist: clean doc
	@rm -rf build dist
	mkdir -p "$(BUILDDIR)"
	cp host/jmp-compile "$(BUILDDIR)"
	sed -e 's/^package.*$$//' -e "s/%%VERSION%%/$(VERSION)/" < src/com/rogerbinns/MiniPython.java > "$(BUILDDIR)/MiniPython.java"
	cp src/MiniPython.[mh] "$(BUILDDIR)"
	cp -r doc/_build/html "$(BUILDDIR)/doc"
	mkdir dist
	cd build ; zip -9r "../dist/JiaMiniPython-$(VERSION).zip" *
	for f in dist/* ; do gpg --use-agent --armor --detach-sig "$$f" ; done
