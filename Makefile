VERSION = 1.1
DATE = "9 February 2012"

# Used for coverage
COBERTURADIR=/space/cobertura

.PHONY: doc docs publish test ant nose help javadoc coverage dist

help:
	@echo "Use \`make <target>' where target is one of"
	@echo "  test      Run tests using standard Python"
	@echo "  nose      Run tests using enhanced nosetests tool"
	@echo "  ant       Build a jar file for command line usage and testing"
	@echo "  doc       To build the documentation using sphinx"
	@echo "  coverage  Run the test suites with coverage"
	@echo "  dist      Produce final code and doc suitable for redistribution"

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


# Note that cobertura currently only works with Java 6.  You get all
# sorts of errors with Java 7.
coverage: ant
	@rm -rf coverage
	@mkdir -p coverage/bin
	bash $(COBERTURADIR)/cobertura-instrument.sh --datafile /space/java-mini-python/coverage/cobertura.ser --destination coverage bin/*.jar
	env JMPCOVERAGE=t COBERTURADIR=$(COBERTURADIR) python test/main_test.py
	bash $(COBERTURADIR)/cobertura-report.sh --datafile coverage/cobertura.ser --destination coverage src
	@echo "Report in coverage/com.rogerbinns.MiniPython.html"

BUILDDIR="build/JavaMiniPython-$(VERSION)"

dist: doc
	@rm -rf build dist
	mkdir -p "$(BUILDDIR)"
	cp host/jmp-compile "$(BUILDDIR)"
	sed -e 's/^package.*$$//' -e "s/%%VERSION%%/$(VERSION)/" < src/com/rogerbinns/MiniPython.java > "$(BUILDDIR)/MiniPython.java"
	cp -r doc/_build/html "$(BUILDDIR)/doc"
	mkdir dist
	cd build ; zip -9r "../dist/JavaMiniPython-$(VERSION).zip" *
	for f in dist/* ; do gpg --use-agent --armor --detach-sig "$$f" ; done

upload:
	@if [ -z "$(GC_USER)" ] ; then echo "Specify googlecode user by setting GC_USER environment variable" ; exit 1 ; fi
	@if [ -z "$(GC_PASSWORD)" ] ; then echo "Specify googlecode password by setting GC_PASSWORD environment variable" ; exit 1 ; fi
	test -f tools/googlecode_upload.py
	test -f dist/JavaMiniPython-$(VERSION).zip
	test -f dist/JavaMiniPython-$(VERSION).zip.asc
	python tools/googlecode_upload.py --user "$(GC_USER)" --password "$(GC_PASSWORD)" -p java-mini-python -s "$(VERSION) GPG signature" -l "Type-Signatures,OpSys-All" dist/JavaMiniPython-$(VERSION).zip.asc
	python tools/googlecode_upload.py --user "$(GC_USER)" --password "$(GC_PASSWORD)" -p java-mini-python -s "$(VERSION) (Source, includes HTML documentation)" -l "Type-Source,OpSys-All" dist/JavaMiniPython-$(VERSION).zip
