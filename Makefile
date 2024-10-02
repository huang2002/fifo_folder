.PHONY: test doc build pub

test:
	pytest

doc:
	if [ ! -d ./wiki/ ]; then mkdir ./wiki/; fi
	pydoc-markdown && cp ./build/docs/content/*.md ./wiki/

build:
	hatch build

pub:
	hatch publish
