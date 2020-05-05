from .polygon import Polygon
import numpy as np
import math
from numpy.linalg import norm
import matplotlib.pyplot as plt

from time import sleep
from .utils import *

ZERO = 1e-8


class PathFinder:
    polygon = None
    footprint_width = None
    start_side = None
    point_first = False

    support_gradient = None
    sweep_gradient = None

    right_vertex = None
    right_i = None

    left_vertex = None
    left_i = None

    path = []

    def __init__(self, polygon: Polygon, footprint_width, side="left", point_first=False):
        self.polygon = polygon
        self.footprint_width = footprint_width
        self.start_side = side
        self.point_first = point_first

        support_edge = self.polygon.get_support_edge()

        self.support_gradient = to_gradient(support_edge)

        self.sweep_gradient = np.array([self.support_gradient[1], -self.support_gradient[0]])

        self.right_vertex = support_edge[0]
        self.left_vertex = support_edge[1]

        [[p1_index, p2_index], p3_index] = self.polygon.get_support_indices()

        self.left_i = p2_index
        self.right_i = p1_index

        start_vertices = \
            [self.left_vertex,
             self.right_vertex] if self.start_side == "left" \
                else [self.right_vertex,
                      self.left_vertex]

        self.path = start_vertices

    def find_path(self):

        done = False
        current_side = "left" if self.start_side == "right" else "right"
        self.generate_side_edge(current_side, True)
        while not done:
            current_side = "left" if current_side == "right" else "right"
            for forward_edge in [0, 1]:
                done = self.generate_side_edge(current_side, bool(forward_edge))
                if done:
                    break

        current_side = "left" if current_side == "right" else "right"
        self.generate_side_edge(current_side, True)

        return self.path[::-1] if self.point_first else self.path

    def set_vertex(self, side, new_vertex):
        if side == "left":
            self.left_vertex = new_vertex
        elif side == "right":
            self.right_vertex = new_vertex

    def get_vertex(self, side):
        if side == "left":
            return self.left_vertex
        elif side == "right":
            return self.right_vertex
        else:
            return None

    def set_vertex_index(self, side, new_index):
        if side == "left":
            self.left_i = new_index
        elif side == "right":
            self.right_i = new_index

    def get_vertex_index(self, side):
        if side == "left":
            return self.left_i
        elif side == "right":
            return self.right_i

    def get_next_vertex_index(self, side):
        if side == "left":
            return self.left_i + 1
        elif side == "right":
            return self.right_i - 1

    def is_done(self, vertex):
        [p1, p2] = self.polygon.get_support_edge()

        dist = norm(np.cross(vertex - p1, p2 - p1)) / norm(p2 - p1)
        return self.polygon.get_width() - dist < ZERO

    def generate_side_edge(self, side, forward_edge=False):

        traveled_up = 0.0
        while self.footprint_width - traveled_up > ZERO:
            current_edge = [self.polygon[self.get_vertex_index(side)],
                            self.polygon[self.get_next_vertex_index(side)]]
            gradient = to_gradient(current_edge)

            inner_cos = np.dot(self.sweep_gradient, gradient) / (1 * 1)
            required_dist = (self.footprint_width - traveled_up) / inner_cos \
                if inner_cos > ZERO else float("inf")
            max_allowed_dist = distance_between(self.get_vertex(side), current_edge[1])
            dist = min(required_dist, max_allowed_dist)

            if required_dist >= max_allowed_dist:
                self.set_vertex_index(side, self.get_next_vertex_index(side))
            self.set_vertex(side, self.get_vertex(side) + np.multiply(gradient, dist))
            traveled_up += dist * inner_cos
            if forward_edge or self.footprint_width - traveled_up <= ZERO:
                self.path.append(self.get_vertex(side))

            if self.is_done(self.get_vertex(side)):
                return True

        return False


def find_path(polygon: Polygon, start_point, footprint_width):
    sub_polygons = polygon.get_all_sub_polygons()

    print(len(sub_polygons))

    adjacent_matrix = [
        [0 for i in range(len(sub_polygons))]
        for j in range(len(sub_polygons))
    ]

    start_index = 0
    distance_from_start = float("inf")

    for i in range(len(sub_polygons)):
        for j in range(len(sub_polygons)):
            if i == j or adjacent_matrix[i][j] or adjacent_matrix[j][i]:
                continue
            intersection_vertices = intersection(sub_polygons[i], sub_polygons[j])
            if len(intersection_vertices) > 0:
                adjacent_matrix[i][j] = 1
                adjacent_matrix[j][i] = 1
                sub_polygons[i].neighbors.append(sub_polygons[j])

        [[p1, p2], p3] = sub_polygons[i].support_points

        for support_point in [p1, p2, p3]:
            dist = distance_between(support_point, start_point)
            if dist < distance_from_start:
                start_index = i
                distance_from_start = dist

    path_indices = find_path_indices(adjacent_matrix, start_index)
    return find_final_path(sub_polygons, path_indices, start_point, footprint_width)


def find_final_path(polygons, path_indices, start_point, footprint_width):
    current_pos = start_point
    final_path = [start_point]

    for path_i in path_indices:
        polygon = polygons[path_i]

        inner_polygon = polygon.get_inner_polygon(footprint_width/2)
        if inner_polygon is None:
            continue

        [[p1, p2], p3] = polygon.support_points
        shortest_dist = float("inf")
        direction = "left"
        point_first = False

        dist1 = distance_between(p1, current_pos)
        dist2 = distance_between(p2, current_pos)
        dist3 = distance_between(p3, current_pos)

        if dist1 < shortest_dist:
            shortest_dist = dist1
            direction = "right"

        if dist2 < shortest_dist:
            shortest_dist = dist2
            direction = "left"

        if dist3 < shortest_dist:
            point_first = True

        path_finder = PathFinder(inner_polygon, footprint_width, direction, point_first)
        path = path_finder.find_path()

        final_path.extend(path)
        current_pos = path[-1]

    return final_path


class Node:
    children = None
    parent = None
    i = None

    def __init__(self, i, parent=None, children=None):
        self.i = i
        self.parent = parent
        self.children = children

    def is_path_found(self, N):
        found_nodes = [0 for i in range(N)]
        path = [self.i]
        found_nodes[self.i] = 1
        node = self
        while node.parent is not None:
            parent = node.parent
            found_nodes[parent.i] = 1
            path.append(parent.i)
            node = parent
        return path[::-1] if all(found_nodes) else None


def find_path_indices(adjacent_matrix, start_i):
    root_node = Node(start_i)
    N = len(adjacent_matrix)

    level_nodes = [root_node]

    found_path = None

    while found_path is None:
        next_level_nodes = []
        for ln in level_nodes:

            for i, is_neighbor in enumerate(adjacent_matrix[ln.i]):
                if is_neighbor:
                    node = Node(i, parent=ln)
                    path = node.is_path_found(N)
                    if path is not None:
                        return path
                    next_level_nodes.append(node)

        level_nodes = next_level_nodes

    return None
