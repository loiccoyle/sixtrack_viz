import pandas as pd
import numpy as np
from pathlib import Path

import pyvista as pv


class Losses:

    def __init__(self, file):
        """Handles the parsing of the losses occuring on the aperture.

        Args:
            file (str/path): Path to the sixtrack aperture losses file.
        """
        if not isinstance(file, Path):
            file = Path(file)
        self.file = file
        self.df = self.to_df()

    def to_df(self):
        '''Reads self.file to generate a DataFrame.

        Returns:
            pd.DataFrame: extracted DataFrame.
        '''
        with self.file.open('r') as fp:
            line = fp.readline()
        cols = line.rstrip().split(' ')[1:]
        df = pd.read_csv(self.file, delim_whitespace=True, names=cols,
                         skiprows=1, index_col=None)
        return df

    def show(self, plotter=None, **kwargs):
        """Computes and plots the aperture, for the given angles.

        Args:
            plotter (pyvista.Plotter, optional): If provided, will add the
            extracted losses to the Plotter.
            **kwargs: forwarded to pyvista.Plotter.add_mesh

        Returns:
            pyvista.Plotter: Plotter with the computed mesh.
        """
        if plotter is None:
            plotter = pv.Plotter()

        data = np.vstack([self.df['x'].abs()*1e3,  # [m] to [mm]
                          self.df['y'].abs()*1e3,  # [m] to [mm]
                          self.df['slos']]).T

        points = pv.PolyData(data)
        points['turn'] = self.df['turn'].values
        plotter.add_mesh(points, **kwargs)
        return plotter
