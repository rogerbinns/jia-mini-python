VERSION = 0.2
DATE = "28 December 2011"


.PHONY: doc docs publish test ant nose help javadoc

help:
	@echo "Use \`make <target>' where target is one of"
	@echo "  test      Run tests using standard Python"
	@echo "  nose      Run tests using enhanced nosetests tool"
	@echo "  ant       Build a jar file for command line usage and testing"
	@echo "  doc       To build the documentation using sphinx"

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
	javadoc -notimestamp -quiet -nodeprecatedlist -use -notree -nohelp -sourcepath src -d $(JAVADOCDIR)/javadoc -link http://docs.oracle.com/javase/6/docs/api/  src/com/rogerbinns/MiniPython.java
