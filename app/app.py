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


@app.route('/data/<float:threshold>')
def data(threshold):
    cursor = cnx.cursor()
    res = []
    query = f"SELECT * FROM " \
            f"(SELECT lon, lat, SUM(value) AS traffic FROM traffic_prediction " \
            f"WHERE month = '2020-07-01' GROUP BY lon, lat) AS stations WHERE traffic > {threshold}"

    cursor.execute(query)
    for (lon, lat, value) in cursor:
        res.append({'long': lon, 'lat': lat, 'group': "B", 'size': value})

    return json.dumps(res)


@app.route('/ukraine.geo.json')
def ukraine_map():
    return app.send_static_file('ukraine.geo.json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
