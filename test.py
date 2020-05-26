from src.polygon import Polygon
from src.path_planning import find_path
from src.concave_decomposition import decompose, combine
import numpy as np

import matplotlib.pyplot as plt

from random import randint

if __name__ == '__main__':
    # search_area = Polygon([(1.0, 1.0), (2.0, 2.0), (1.2, 3.4), (4.5, 3.2), (4.0, -1.2)])
    search_area = Polygon(
        [(569902, 7032834), (570036, 7032830), (570192, 7032921), (570216, 7032726), (570063, 7032751), (569965, 7032646)])

    plt.plot(*search_area[0], "ro")
    search_area.draw()
    decompose(search_area, search_area)
    combine(search_area)  # not implemented yet...

    path = find_path(search_area, search_area[0], 4)
    search_area.draw(False)
    plt.plot(*zip(*path))
    plt.show()
