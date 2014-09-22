# Correctiv Story Apps

This repository contains the applications developed by [Correctiv](https://www.correctiv.org/).

## Database for [Spendengerichte](http://spendengerichte.correctiv.org/) story

1. Setup virtualenv for project
2. Install dependencies

        pip install -r requirements.txt
3. Rename `correctiv_apps/local_settings.py.example` to `correctiv_apps/local_settings.py`
4. Sync database

        python manage.py syncdb

5. [Download the JSON file](https://apps.correctiv.org/media/justizgelder/data/bussgelder.json) or [the CSV file](https://apps.correctiv.org/media/justizgelder/data/bussgelder.csv) and load it into the database. CSV is much slower to load, but might be useful for other things.

        python manage.py loaddata bussgelder.json

    Or load the CSV file:

        python manage.py bussgelder_import bussgelder.csv

    The CSV loading can take quite some time as the loading code is not optimized (PR welcome).

6. Start ElasticSearch in another terminal and run

        python manage.py bussgelder_index

7. Start runserver

        python manage.py runserver

8. Go to [http://localhost:8000/justizgelder/](http://localhost:8000/justizgelder/)
