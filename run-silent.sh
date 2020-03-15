export FLASK_ENV=development
export FLASK_APP=www
(flask run --host=0.0.0.0 --port=8100 &) > server.log 2>&1