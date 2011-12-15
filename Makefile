VERSION = 0.1


.PHONY: doc docs publish


docs: doc

doc:
	make -C doc html VERSION=$(VERSION)

publish: doc
	rsync -av --delete --exclude=.hg doc/_build/html/ ../jmp-doc/
	cd ../jmp-doc && hg status
