sphinx:
	cd docs && \
	make -f Makefile clean && \
	make -f Makefile html && \
	cd ..

ghpages:
	git checkout -b gh-pages && \
	cp -r docs/_build/html/* . && \
	touch .nojekyll && \
	git add -u && \
	git add -A && \
	git commit -m "Jenkins Autocommit - Update Docs"