all:
	python run.py

install:
	sudo pip install -r requirements.txt

clean:
	find . -type f -name "*.pyc" -delete
