serviceregistry: gunicorn --access-logfile - --capture-output -p $PORT serviceregistry:__hug_wsgi__
userprofile: gunicorn --access-logfile - --capture-output -p $PORT userprofile:__hug_wsgi__
timeline: gunicorn --access-logfile - --capture-output -p $PORT timeline:__hug_wsgi__
likeservice: gunicorn --access-logfile - --capture-output -p $PORT likeservice:__hug_wsgi__
pollservice: gunicorn --access-logfile - --capture-output -p $PORT pollservice:__hug_wsgi__
postworker: python3 postworker.py
likesworker: python3 likesworker.py
pollworker: python3 pollworker.py
emailserveron: python3 emailserveron.py
emailnotifyworker: python3 emailnotifyworker.py
