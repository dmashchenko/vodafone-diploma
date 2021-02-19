from flask import Flask
from flask import render_template
import mysql.connector
from mysql.connector import errorcode
import json

try:
    cnx = mysql.connector.connect(
        host="terraform-20210218095209829200000001.cfi5l15buuvj.us-east-1.rds.amazonaws.com",
        port=3306,
        user="admin",
        password="admin1234",
        database="base_station")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
# else:
#     cnx.close()

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/data')
def data():
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM traffic")
    for (first_name, last_name, hire_date, x, xx) in cursor:
        app.logger.info(f"{first_name}, {last_name} , {hire_date}, {x}, {xx}")
    d = [{'long': 30.083, 'lat': 50.149, 'group': "A", 'size': 60},
         {'long': 31.26, 'lat': 47.71, 'group': "C", 'size': 20},
         {'long': 29.349, 'lat': 48.864, 'group': "B", 'size': 87}]
    return json.dumps(d)


@app.route('/ukraine.geo.json')
def map():
    return app.send_static_file('ukraine.geo.json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
