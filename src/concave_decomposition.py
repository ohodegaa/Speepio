from .polygon import Polygon
from .utils import to_gradient
import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiLineString, GeometryCollection, box, Point
import numpy as np


def decompose(polygon: Polygon, root_poly=None):
    number_of_vertices = len(polygon)
    if polygon.number_of_concave_vertices == 0:
        return

    sub_polygon_pairs = []
    for i in polygon.get_concave_vertex_indices():
        for j in range(number_of_vertices):
            vertex_i = polygon[i]
            if i == j:
                continue
            gradient = to_gradient([polygon[j], polygon[j + 1]])
            split_line = [vertex_i, np.add(vertex_i, gradient)]
            split_result = polygon.split(split_line, i)
            if split_result is not None:
                sub_polygon_pairs.append(split_result)

    min_sum_of_widths_pair = find_min_sum_of_widths_pair(sub_polygon_pairs)
    polygon.sub_polygons = min_sum_of_widths_pair

    for poly in min_sum_of_widths_pair:
        decompose(poly, root_poly)


def find_min_sum_of_widths_pair(sub_polygon_pairs):
    min_sum_of_widths = float("inf")
    min_sum_of_widths_pair = None
    for sub_polygon_pair in sub_polygon_pairs:
        width = sum([sub_polygon.get_width() for sub_polygon in sub_polygon_pair])
        if width < min_sum_of_widths:
            min_sum_of_widths_pair = sub_polygon_pair
            min_sum_of_widths = width

    return min_sum_of_widths_pair


def combine(polygon: Polygon):
    return
