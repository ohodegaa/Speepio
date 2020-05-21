import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from numpy.linalg import norm
from shapely.geometry import Polygon as ShapelyPolygon, box, LineString, Point, GeometryCollection
from shapely.ops import split
import math

from .utils import *


class Polygon:
    points = []
    width = None
    support_points = None  # [edge, vertex]
    support_indices = None

    concave_vertices = None
    concave_vertex_indices = None

    sub_polygons = None

    neighbors = []

    def is_vertex_concave(self, i: int):
        if i >= len(self):
            raise IndexError("Index must be inside interval [0, len(self)) (here: [0, {})).".format(len(self)))

        vertex = self.points[i]
        left_vertex = self.points[len(self) - 1 if i == 0 else i - 1]
        right_vertex = self.points[0 if i == len(self) - 1 else i + 1]

        return np.cross(left_vertex - vertex, right_vertex - vertex) < 0

    def __init__(self, points: [(float, float)]):
        super().__init__()
        self.points = np.array(points)

    def draw(self, draw=True, color="orange"):
        xs, ys = zip(*np.concatenate((self.points, self.points[0:1])))
        plt.plot(xs, ys, color=color)
        if draw:
            plt.show()

    def get_support_points(self):
        if not self.support_points:
            self.calculate_width()
        return self.support_points

    def get_support_indices(self):
        if not self.support_indices:
            self.calculate_support_indices()
        return self.support_indices

    def get_support_edge(self):
        if not self.support_points:
            self.calculate_width()
        return self.support_points[0]

    def get_support_vertex(self):
        if not self.support_points:
            self.calculate_width()
        return self.support_points[1]

    def get_shapely_polygon(self):
        return ShapelyPolygon(self.points)

    def get_bounding_box(self):
        shapely_polygon = self.get_shapely_polygon()
        return box(*shapely_polygon.bounds)

    def get_bounds(self) -> (int, int, int, int):
        shapely_polygon = self.get_shapely_polygon()
        return shapely_polygon.bounds

    def split(self, split_line, i):
        vertex = split_line[0]

        intersection_at = None
        split_index = None

        for j in range(len(self)):
            if j == i or j == self.prev(i) or j == self.next(i):
                continue
            polygon_line = [self[j], self[j + 1]]
            
            intersects = intersects_at(polygon_line, split_line)
            if intersects is not None:
                if intersection_at is None \
                        or distance_between(intersects, vertex) < distance_between(intersection_at, vertex):
                    intersection_at = intersects
                    split_index = j

        if intersection_at is None:
            return None

        poly1 = [intersection_at]
        k_1 = i

        while k_1 != self.next(split_index):
            poly1.append(self[k_1])
            k_1 = self.next(k_1)

        poly2 = [intersection_at]
        k_2 = self.next(split_index)

        while k_2 != self.next(i):
            poly2.append(self[k_2])
            k_2 = self.next(k_2)

        poly1, poly2 = Polygon(poly1), Polygon(poly2)
        return poly1, poly2

    def get_inner_polygon(self, delta):
        shapely_polygon = self.get_shapely_polygon()
        inner_polygon = shapely_polygon.buffer(-delta, resolution=0, cap_style=3).exterior.coords[:]

        return Polygon(inner_polygon) if len(inner_polygon) > 0 else self

    def get_convex_hull(self) -> np.ndarray:
        if len(self) == 3:
            return self.points
        hull_vertex_indices = ConvexHull(self.points).vertices
        return np.array([self.points[i] for i in sorted(hull_vertex_indices)])

    def calculate_width(self):
        width = float("inf")
        hull = self.get_convex_hull()
        support_points = None
        for i in range(len(hull)):
            p1 = hull[i]
            p2 = hull[0 if i + 1 >= len(hull) else i + 1]
            max_vertex_dist = -1
            max_vertex_dist_points = None
            for vertex in [vertex for vertex in hull if not (np.array_equal(p1, vertex) or np.array_equal(p2, vertex))]:
                p3 = vertex
                dist = norm(np.cross(p2 - p1, p1 - p3)) / norm(p2 - p1)
                if dist > max_vertex_dist:
                    max_vertex_dist = dist
                    max_vertex_dist_points = [[p1, p2], p3]
            if max_vertex_dist < width:
                width = max_vertex_dist
                support_points = max_vertex_dist_points
        self.width = width
        self.support_points = support_points

    def calculate_support_indices(self):
        if not self.support_points:
            self.calculate_width()
        [[p1, p2], p3] = self.support_points
        p1_index = None
        p2_index = None
        p3_index = None

        for i in range(len(self.points)):
            if not p1_index and np.allclose(self[i], p1):
                p1_index = i
            elif not p2_index and np.allclose(self[i], p2):
                p2_index = i
            elif not p3_index and np.allclose(self[i], p3):
                p3_index = i

        if p1_index is None or p2_index is None or p3_index is None:
            raise Exception("All support indices not found...")

        self.support_indices = [[p1_index, p2_index], p3_index]

    def get_width(self):
        if not self.width:
            self.calculate_width()
        return self.width

    def get_concave_vertices(self) -> list:
        if self.concave_vertices is None:
            self.calculate_concave_vertices()
        return self.concave_vertices

    def calculate_concave_vertices(self):
        self.concave_vertices = []
        self.concave_vertex_indices = []
        if len(self) < 4:
            return
        for i in range(len(self)):
            a = self[i - 1]
            b = self[i]
            c = self[i + 1]
            bc = np.subtract(c, b)
            ab = np.subtract(b, a)
            cross_product = -np.cross(ab, bc)
            if cross_product < 0:
                self.concave_vertices.append(self[i])
                self.concave_vertex_indices.append(i)

    def get_concave_vertex_indices(self) -> list:
        if self.concave_vertex_indices is None:
            self.calculate_concave_vertices()

        return self.concave_vertex_indices

    def get_flight_direction_gradient(self):
        if not self.support_points:
            self.calculate_width()
        support_line = self.support_points[0]
        return to_gradient(support_line)

    def get_all_sub_polygons(self):
        if self.sub_polygons is None:
            return [self]
        else:
            sub_polygons = []
            for sub_poly in self.sub_polygons:
                sub_polygons.extend(sub_poly.get_all_sub_polygons())
            return sub_polygons

    @property
    def number_of_concave_vertices(self):
        return len(self.get_concave_vertices())

    @property
    def number_of_vertices(self):
        return len(self.points)

    def next(self, i):
        return (i + 1 + len(self) * 10) % self.__len__()

    def prev(self, i):
        return (i - 1 + len(self) * 10) % self.__len__()

    def __len__(self):
        return len(self.points)

    def __delitem__(self, index):
        self.points.__delitem__(index % self.__len__())

    def __setitem__(self, index, value):
        self.points[index % self.__len__()] = value

    def __getitem__(self, index):

        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else self.__len__()
            step = index.step if index.step is not None else 1
            return [self[i] for i in range(start, stop, step)]

        return self.points[(index + len(self) * 10) % self.__len__()]

    def __str__(self):
        return "Polygon(\n{}\n)".format(self.points)

    def __repr__(self):
        return "Polygon"

    def __iter__(self):
        return self.points
