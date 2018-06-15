#/bin/bash

uwsgi setting/api_uwsgi.ini
# uwsgi --http 0.0.0.0:8080 -w api.main:app --workers 1 --honour-stdin
#8 --threads 10 --enable-threads --lazy-apps
