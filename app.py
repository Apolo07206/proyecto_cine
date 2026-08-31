from flask import Flask , render_template , request, url_for , flash ,redirect
from flask_mysqldb import MySQL
from config import Config


app=Flask(__name__)
app.config.from_object(Config)
mysql=MySQL(app)


app.secret_key='eicwiemcumaehfppiwgqkvr'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] ='proyecto_cine'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'


@app.route('/')
def home():
    return 'hola mundo '

if __name__ == '__main__':
    app.run(debug=True)