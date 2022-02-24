

sphinx:
	cd docs && \
	make -f Makefile clean && \
	make -f Makefile html && \
	cd ..