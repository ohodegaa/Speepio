from src.polygon import Polygon
from src.path_planning import find_path
from src.concave_decomposition import decompose, combine
import numpy as np

import matplotlib.pyplot as plt

from random import randint

if __name__ == '__main__':
    # search_area = Polygon([(1.0, 1.0), (2.0, 2.0), (0.2, 3.2), (4.5, 3.2), (4.0, 1.2)])
    search_area = Polygon(
        [(569902, 7033834), (570036, 7033180), (570202, 7034921), (570502, 7033521), (570306, 7032626),
         (570163, 7033151), (569965, 7032646)])

    plt.plot(*search_area[0], "ro")
    search_area.draw()
    decompose(search_area, search_area)
    combine(search_area)  # not implemented yet...

    path = find_path(search_area, search_area[0], 10)
    search_area.draw(False)
    plt.plot(*zip(*path))
    plt.show()
