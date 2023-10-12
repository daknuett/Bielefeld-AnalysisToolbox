import latqcdtools

from latqcdtools.statistics.jackknife import jackknife

import numpy as np

data = np.random.uniform(0, 1, 100)

f = lambda x: np.mean(x)

print(jackknife(f, data))

print(latqcdtools.metadata.get_metadata_to_export())
