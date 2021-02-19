import os
from pathlib import Path
import configparser
from flask import Flask
from flask import render_template
import mysql.connector
from mysql.connector import errorcode
import json

config = configparser.ConfigParser()
abspath_of_this_script = os.path.abspath(os.path.realpath(__file__))
PROJECT_ROOT = Path(os.path.split(abspath_of_this_script)[0]).resolve()
config.read(PROJECT_ROOT / './infra.cfg')
host = config["default"]["warehouse_host"]

try:
    cnx = mysql.connector.connect(
        host=host,
        port=3306,
        user="admin",
        password="admin1234",
        database="traffic")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/data')
def data():
    cursor = cnx.cursor()
    res = []
    cursor.execute("SELECT lon ,lat FROM traffic_prediction")
    for (lon, lat) in cursor:
        res.append({'long': lon, 'lat': lat, 'group': "B", 'size': 60})
    return json.dumps(res)


@app.route('/ukraine.geo.json')
def map():
    return app.send_static_file('ukraine.geo.json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
