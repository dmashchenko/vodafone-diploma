from flask import Flask
from flask import render_template
import json

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/data')
def data():
    d = [{'long': 30.083, 'lat': 50.149, 'group': "A", 'size': 60},
         {'long': 31.26, 'lat': 47.71, 'group': "C", 'size': 20},
         {'long': 29.349, 'lat': 48.864, 'group': "B", 'size': 87}]
    return json.dumps(d)


@app.route('/ukraine.geo.json')
def map():
    return app.send_static_file('ukraine.geo.json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
