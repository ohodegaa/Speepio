import math
import numpy as np
import matplotlib.pyplot as plt

ZERO = 1e-1


def to_gradient(line):
    dy = line[1][1] - line[0][1]
    dx = line[1][0] - line[0][0]
    gradient = [0.0, 0.0] if abs(dx) < ZERO and abs(dy) < ZERO else (np.array([dx, dy]) / np.sqrt(
        dx ** 2 + dy ** 2))
    return gradient


def distance_between(a, b):
    dy = b[1] - a[1]
    dx = b[0] - a[0]
    return math.sqrt(dx ** 2 + dy ** 2)


def line(p1, p2):
    a = (p1[1] - p2[1])
    b = (p2[0] - p1[0])
    c = (p1[0] * p2[1] - p2[0] * p1[1])
    return a, b, -c

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def intersects_at(line1, line2):
    plt.plot(*zip(*line1))
    plt.plot(*zip(*line2))
    plt.show()

    L1, L2 = line(*line1), line(*line2)
    
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if abs(D) > 0.0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return None


def intersection(polygon1, polygon2):
    points1, points2 = polygon1.points, polygon2.points
    intersections = []

    for p1 in points1:
        for p2 in points2:
            if distance_between(p1, p2) < ZERO:
                intersections.append(p1)
                break

    return intersections
