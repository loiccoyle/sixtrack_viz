import math
import pandas as pd
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iter, *args, **kwargs):
        return iter
from pathlib import Path
import pyvista as pv

from . import shapes


class Profile:

    def __init__(self, file):
        """Handles the parsing of the aperture profile.

        Args:
            file (str/path): Path to sixtrack aperture dump file.
        """
        if not isinstance(file, Path):
            file = Path(file)
        self.file = file
        self.df = self.to_df()

    @staticmethod
    def _col_parsing(string):
        '''
        Parses the first line to get columns names.
        '''
        string = string.strip().replace('[m]', '').replace('[mm]', '').replace('[rad]', '')
        return string.split()[1:]

    def to_df(self):
        '''Reads self.file to generate a DataFrame.

        Returns:
            pd.DataFrame: extracted DataFrame.
        '''
        with self.file.open('r') as fp:
            line = fp.readline()
        cols = self._col_parsing(line)
        df = pd.read_csv(self.file, delim_whitespace=True, names=cols,
                         skiprows=1, index_col=None)
        return df

    def drop_interpolated(self):
        '''
        Removes any row with name "interpolated".
        '''
        self.df = self.df[self.df['name'] != 'interpolated']

    def drop_consecutive_duplicates(self):
        '''
        Drops any consecutive duplicates.
        '''
        cols = ['aptype', 'aper1', 'aper2', 'aper3', 'aper4',
                'aper5', 'aper6', 'aper7', 'aper8', 'xoff', 'yoff']
        mask1 = (self.df[cols].shift() != self.df[cols]).any(axis=1)
        mask2 = (self.df[cols].shift(-1) != self.df[cols]).any(axis=1)
        self.df = self.df.loc[np.logical_or(mask1, mask2)]

    def get_aperture(self, angle):
        '''Computes the aperture for a given angle.

        Args:
            angle (float): Angle at which to ocmpute the aperture, in degrees.

        Returns:
            np.array: 1d array containing the computed aperture.
        '''
        # rad_angle = math.radians(angle)
        # if rad_angle != angle:
        #     angle = rad_angle

        funcs = {
                 'CR': shapes.Circle,
                 'RE': shapes.Rectangle,
                 'EL': shapes.Ellipse,
                 'RL': shapes.RectEllipse,
                 'OC': shapes.Octagon,
                 'RT': shapes.Racetrack,
                 'TR': shapes.Transition,
                }
        indices = {
                   'CR': [3],
                   'RE': [3, 4],
                   'EL': [3, 4],
                   'RL': [3, 4, 5, 6],
                   'OC': [3, 4, 5, 6],
                   'RT': [3, 4, 5, 6],
                   'TR': [3, 4, 5, 6, 7, 8, 9, 10],
                   }

        def calc_ape(row, angle):
            func = funcs[row[1]]
            args = row[indices[row[1]]]
            return func(angle, *args)
        return np.apply_along_axis(calc_ape, 1, self.df.values, angle=angle)

    @staticmethod
    def polyline_from_points(points):
        """Creates a line from points.

        Args:
            points (np.array): (n, 3) shaped array.

        Returns:
            pv.PolyData: generated line.
        """
        poly = pv.PolyData()
        poly.points = points
        the_cell = np.arange(0, len(points), dtype=np.int)
        the_cell = np.insert(the_cell, 0, len(points))
        poly.lines = the_cell
        return poly

    def show(self, angles=np.linspace(0, 90, 20), aper_cutoff=100,
             with_offset=False, plotter=None, style='line', mirror=None,
             **kwargs):
        """Computes and plots the aperture, for the given angles.

        Args:
            angles (iterable, optional): Angles at which to compute the
            apertures.
            aper_cutoff (int, optional): Aperture radial cuttoff for plotting,
            set to 0 or None to disable.
            with_offset (bool, optional): Take into account the offset.
            plotter (pyvista.Plotter, optional): If provided, will add the
            computed mesh to the given pyvista.Plotter.
            style (str, optional): either "point", "line" or "surf", controls
            the style of the plotted aperture. "surf" requires additional
            computation.
            mirror (str, optional): mirrors the apperture, either 'H', 'V' or
            'HV'.
            **kwargs: forwarded to pyvista.Plotter.add_mesh

        Returns:
            pyvista.Plotter: Plotter with the computed mesh.

        Raises:
            ValueError: When "style" is incorrect.
        """
        if style not in ['line', 'surf', 'point']:
            cntnt = '"style" must be either "line", "surf" or "point".'
            raise ValueError(cntnt)
        if mirror is not None and not set(mirror) <= set('HV'):
            raise ValueError('"mirror" must be "H", "V" or "HV".')

        if plotter is None:
            plotter = pv.Plotter()

        Ss = []
        Ape_x = []
        Ape_y = []
        for a in tqdm(angles, desc='Computing aperture'):
            a = math.radians(a)
            tmpSs = self.df['s'].values
            tmpApe = self.get_aperture(a)
            tmpApe_x = tmpApe * np.cos(a)
            tmpApe_y = tmpApe * np.sin(a)
            if with_offset:
                tmpApe_x = tmpApe_x + self.df['xoff'].values
                tmpApe_y = tmpApe_y + self.df['yoff'].values

            # cutoff to remove large apertures
            if aper_cutoff is not None and aper_cutoff > 0:
                cutt_off_mask = np.sqrt(tmpApe_x**2 + tmpApe_y**2) < aper_cutoff
                tmpSs = tmpSs[cutt_off_mask]
                tmpApe_x = tmpApe_x[cutt_off_mask]
                tmpApe_y = tmpApe_y[cutt_off_mask]

            Ss.append(tmpSs)
            Ape_x.append(tmpApe_x)
            Ape_y.append(tmpApe_y)

        if 'H' in mirror:
            Ss.extend(Ss)
            Ape_x.extend([-x for x in Ape_x])
            Ape_y.extend(Ape_y)

        if 'V' in mirror:
            Ss.extend(Ss)
            Ape_x.extend(Ape_x)
            Ape_y.extend([-y for y in Ape_y])

        if style == 'line':
            for i, (s, x, y) in enumerate(zip(Ss, Ape_x, Ape_y)):
                data = np.vstack([x, y, s]).T
                lines = self.polyline_from_points(data)
                plotter.add_mesh(lines, name=f'angle {i}', **kwargs)

        elif style in ['point', 'surf']:
            Ss = np.hstack(Ss)
            Ape_x = np.hstack(Ape_x)
            Ape_y = np.hstack(Ape_y)
            points = pv.PolyData(np.vstack([Ape_x, Ape_y, Ss]).T)
            if style == 'point':
                plotter.add_mesh(points, **kwargs)
            elif style == 'surf':
                surf = points.delaunay_2d()
                plotter.add_mesh(surf, **kwargs)

        return plotter
