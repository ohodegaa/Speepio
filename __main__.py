from src.polygon import Polygon
from src.path_planning import find_path
from src.concave_decomposition import decompose, combine
import numpy as np
from random import randint
import matplotlib.pyplot as plt


import flask
from flask import request, jsonify
import json
app = flask.Flask(__name__)
app.config["DEBUG"] = True


def fromJson(path):
    newPath = []
    for x in path:
        newPath.append((round(x["Northing"]), round(x["Easting"])))
    return newPath

def toJson(path):
    json_path = []
    for x in range(1, len(path), 1):
        json_path.append({"Northing": path[x][0], "Easting": path[x][1]})
    return json_path

@app.route('/', methods=['POST'])
def create_task():
    if not request.json:
        abort(400)
    req = request.get_json()
    new_path = fromJson(req["path"])
    print(new_path)
    search_area = Polygon([(83, 28), (68, 0), (12, 3), (0, 58), (80, 80)])
    #search_area = Polygon([(1.0, 1.0), (2.0, 2.0), (1.2, 3.4), (4.5, 3.2), (4.0, -1.2)])
    #print([(1.0, 1.0), (2.0, 2.0), (1.2, 3.4), (4.5, 3.2), (4.0, -1.2)])
    #print(newPath)
    #search_area = Polygon(new_path)
    decompose(search_area)
    combine(search_area)  # not implemented yet...
    path = find_path(search_area, (1, -1), req["width"])
    json_path = toJson(path)
    return jsonify({'path': json_path }), 201
app.run()
