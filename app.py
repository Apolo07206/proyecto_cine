from flask import Flask , render_template , request, url_for , flash ,redirect
from flask_mysqldb import MySQL


app=Flask(__name__)
mysql=MySQL(app)


app.secret_key='eicwiemcumaehfppiwgqkvr'
@app.route('/')
def home():
    return 'hola mundo '

if __name__ == '__main__':
    app.run(debug=True)