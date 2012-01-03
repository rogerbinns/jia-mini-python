VERSION = 0.3
DATE = "31 December 2011"

# Used for coverage
COBERTURADIR=/space/cobertura

.PHONY: doc docs publish test ant nose help javadoc coverage

help:
	@echo "Use \`make <target>' where target is one of"
	@echo "  test      Run tests using standard Python"
	@echo "  nose      Run tests using enhanced nosetests tool"
	@echo "  ant       Build a jar file for command line usage and testing"
	@echo "  doc       To build the documentation using sphinx"
	@echo "  coverage  Run the test suites with coverage"

docs: doc

doc: javadoc
	make -C doc html VERSION=$(VERSION) DATE=$(DATE)

linkcheck:
	make -C doc linkcheck VERSION=$(VERSION) DATE=$(DATE)

publish: doc
	rsync -av --delete --exclude=.hg doc/_build/html/ ../jmp-doc/
	cd ../jmp-doc && hg status

ant:
	ant

test: ant
	python test/main_test.py

nose: ant
	nosetests test/

JAVADOCDIR="doc/_build/javadoc"

javadoc:
	@rm -rf $(JAVADOCDIR)
	@mkdir -p $(JAVADOCDIR)
	javadoc -notimestamp -quiet -nodeprecatedlist -use -notree -nohelp -sourcepath src -d $(JAVADOCDIR)/javadoc -link http://docs.oracle.com/javase/7/docs/api/  src/com/rogerbinns/MiniPython.java
	tools/update-javadoc.py


coverage: ant
	@rm -rf coverage
	@mkdir -p coverage/bin
	bash $(COBERTURADIR)/cobertura-instrument.sh --datafile /space/java-mini-python/coverage/cobertura.ser --destination coverage bin/*.jar
	env JMPCOVERAGE=t COBERTURADIR=$(COBERTURADIR) python test/main_test.py
	bash $(COBERTURADIR)/cobertura-report.sh --datafile coverage/cobertura.ser --destination coverage src