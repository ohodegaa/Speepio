from src.polygon import Polygon
from src.path_planning import find_path
from src.concave_decomposition import decompose, combine
import numpy as np

import matplotlib.pyplot as plt

from random import randint

if __name__ == '__main__':
    # search_area = Polygon([(1.0, 1.0), (2.0, 2.0), (1.2, 3.4), (4.5, 3.2), (4.0, -1.2)])
    search_area = Polygon(
        [(570149, 7032824), (570058, 7032683), (569976, 7032856), (570074, 7032931), (570219, 7032822)])

    decompose(search_area)
    combine(search_area)  # not implemented yet...

    path = find_path(search_area, search_area[0], 5)
    search_area.draw(False)
    plt.plot(*zip(*path))
    plt.show()
