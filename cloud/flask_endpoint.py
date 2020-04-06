#!/usr/bin/env python

import flask
import webbrowser


app = flask.Flask(__name__, template_folder="flask")


@app.route('/')
def home():
    return flask.render_template('index.html')


if __name__ == '__main__':
    webbrowser.open_new('http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
