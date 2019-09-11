import pandas as pd
import numpy as np
from pathlib import Path

import pyvista as pv


class Losses:

    def __init__(self, file):
        if not isinstance(file, Path):
            file = Path(file)
        self.file = file
        self.df = self.to_df()

    def to_df(self):
        with self.file.open('r') as fp:
            line = fp.readline()
        cols = line.rstrip().split(' ')[1:]
        df = pd.read_csv(self.file, delim_whitespace=True, names=cols,
                         skiprows=1, index_col=None)
        return df

    def show(self, plotter=None, **kwargs):
        if plotter is None:
            plotter = pv.Plotter()

        data = np.vstack([self.df['slos'],
                          self.df['x'].abs()*1e3,  # [m] to [mm]
                          self.df['y'].abs()*1e3]).T  # [m] to [mm]
        points = pv.PolyData(data)
        points['turn'] = self.df['turn'].values
        plotter.add_mesh(points)
        return plotter
