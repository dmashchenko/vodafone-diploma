from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')

@app.route('/ukraine.geo.json')
def json():
    return app.send_static_file('ukraine.geo.json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
