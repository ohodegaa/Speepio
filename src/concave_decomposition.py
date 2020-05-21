from .polygon import Polygon
from .utils import to_gradient
import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiLineString, GeometryCollection, box, Point
import numpy as np


def decompose(polygon: Polygon):
    print("runs")
    number_of_vertices = len(polygon)
    number_of_concave_vertices = polygon.number_of_concave_vertices
    print(number_of_concave_vertices)
    print(number_of_vertices)
    polygon.draw(False)
    if number_of_concave_vertices == 0:
        return

    sub_polygon_pairs = []
    for i in polygon.get_concave_vertex_indices():
        for j in range(number_of_vertices):
            vertex_i = polygon[i]
            if np.allclose(vertex_i, polygon[j]) \
                    or np.allclose(vertex_i, polygon[j + 1]):
                continue
            gradient = to_gradient([polygon[j], polygon[j + 1]])
            print(gradient)
            split_line = np.array([vertex_i, np.add(vertex_i, gradient * 1000)])
            print(split_line)
            plt.plot(*zip(*split_line))
            plt.show()
            split_result = polygon.split(split_line, i)
            print(split_result)
            if split_result is not None:
                sub_polygon_pairs.append(split_result)

    min_sum_of_widths = float("inf")
    min_sum_of_widths_pair = None
    for sub_polygon_pair in sub_polygon_pairs:
        width = sum([sub_polygon.get_width() for sub_polygon in sub_polygon_pair])
        if width < min_sum_of_widths:
            min_sum_of_widths_pair = sub_polygon_pair
            min_sum_of_widths = width

    polygon.sub_polygons = min_sum_of_widths_pair
    print(min_sum_of_widths_pair)
    for poly in min_sum_of_widths_pair:
        decompose(poly)


def combine(polygon: Polygon):
    return
