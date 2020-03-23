#!/usr/bin/env python

import flask
import flask_restful
import webbrowser


app = flask.Flask(__name__, template_folder='flask')
api = flask_restful.Api(app)

objs = [
    {
        'name': 'my_object',
        'description': 'description of my object'
    },
    {
        'name': 'another_object',
        'description': 'this is another object'
    }
]

class MyObject(flask_restful.Resource):
    def get(self, name):
        for obj in objs:
            if obj['name'] == name:
                print(obj)
                return obj
        return {'error': 'Resource not found'}

api.add_resource(MyObject, '/object/<string:name>')


if __name__ == "__main__":
    webbrowser.open_new('http://127.0.0.1:5000/object/another_object')
    app.run(host='0.0.0.0', port=5000, debug=True)

