export FLASK_APP=server
flask db migrate
flask db upgrade