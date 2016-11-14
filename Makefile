build:
	docker-compose build sha_api

run:
	docker-compose run -p "8080:8080" sha_api

test:
	python setup.py nosetests --cover-branches --cover-html --cover-html-dir ./cover --cover-package sha_api -d -s -v --with-coverage
