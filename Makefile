.PHONY: doc docs publish


docs: doc

doc:
	make -C doc html

publish: doc
	rsync -av --delete --exclude=.git doc/_build/html/ ../jmp-doc/
	cd ../jmp-doc && git status