VERSION = 0.1


.PHONY: doc docs publish test ant nose help

help:
	@echo "Use \`make <target>' where target is one of"
	@echo "  test      Run tests using standard Python"
	@echo "  nose      Run tests using enhanced nosetests tool"
	@echo "  ant       Build a jar file for command line usage and testing"
	@echo "  doc       To build the documentation using sphinx"

docs: doc

doc:
	make -C doc html VERSION=$(VERSION)

publish: doc
	rsync -av --delete --exclude=.hg doc/_build/html/ ../jmp-doc/
	cd ../jmp-doc && hg status

ant:
	ant

test: ant
	python test/main_test.py

nose: ant
	nosetests test/