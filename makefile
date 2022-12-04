migrate:
	rm -rf db.sqlite3
	python3 manage.py makemigrations nwsAPI
	python3 manage.py migrate
celery:
	celery -A dwnpptool worker -l info
run:
	python3 manage.py runserver 8888