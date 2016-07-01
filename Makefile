all:
	python run.py

install:
	sudo pip install -r requirements.txt

docs: .FORCE

.FORCE:
	touch docs/index.rst
	sphinx-build -b html docs build

clean:
	find . -type f -name "*.pyc" -delete

zip: docs
	zip -r build.zip ./build/*
