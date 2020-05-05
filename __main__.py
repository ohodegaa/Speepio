from src.polygon import Polygon
from src.path_planning import find_path
from src.concave_decomposition import decompose, combine
import numpy as np

import matplotlib.pyplot as plt

from random import randint

if __name__ == '__main__':
    search_area = Polygon([(1.0, 1.0), (2.0, 2.0), (1.2, 3.4), (4.5, 3.2), (4.0, -1.2)])
    search_area.draw(False)

    decompose(search_area)
    combine(search_area)

    path = find_path(search_area, (1, -1), 0.1)

    plt.plot(*zip(*path))
    plt.plot(*path[0], "go")
    plt.plot(*path[-1], "ro")

    plt.show()
