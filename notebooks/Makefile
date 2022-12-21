NOTEBOOKS := $(wildcard *.ipynb)

all: run

pdf: $(NOTEBOOKS:%.ipynb=%.pdf)

py: $(NOTEBOOKS:%.ipynb=%.py)

html: $(NOTEBOOKS:%.ipynb=%.html)

run: $(NOTEBOOKS:%.ipynb=%.run)


%.py: %.ipynb
	jupyter nbconvert --to=python $<

%.pdf: %.ipynb
	jupyter nbconvert --to=pdf $<

%.html: %.ipynb
	jupyter nbconvert --to=html $<

%.run: %.ipynb
	jupyter nbconvert --to notebook --execute --inplace $<

clean:
	@rm -rf *.pdf *.html *.py *.run