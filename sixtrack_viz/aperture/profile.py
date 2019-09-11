import math
import pandas as pd
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iter, *args, **kwargs):
        return iter
from pathlib import Path
from mayavi import mlab
# from collections import OrderedDict

from . import shapes


class Profile:

    def __init__(self, file):
        if not isinstance(file, Path):
            file = Path(file)
        self.file = file
        self.df = self.to_df()

    @staticmethod
    def _col_parsing(string):
        string = string.strip().replace('[m]', '').replace('[mm]', '').replace('[rad]', '')
        return string.split()[1:]

    def to_df(self):
        with self.file.open('r') as fp:
            line = fp.readline()
        cols = self._col_parsing(line)
        df = pd.read_csv(self.file, delim_whitespace=True, names=cols,
                         skiprows=1, index_col=None)
        return df

    def get_aperture(self, angle):
        rad_angle = math.radians(angle)
        if rad_angle != angle:
            angle = rad_angle

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

    def show(self, angles=np.linspace(0, 90, 20), aper_cutoff=50,
             with_offset=False, **kwargs):
        # 3d render
        Ss = []
        Ape_x = []
        Ape_y = []
        for a in tqdm(angles, desc='Calculating aperture for angles'):
            a = math.radians(a)
            tmpSs = self.df['s'].values
            tmpApe = self.get_aperture(a)
            if with_offset:
                tmpHoff = self.df['xoff'].values
                tmpVoff = self.df['yoff'].values
                tmpApe_x = tmpApe*np.cos(a) + tmpHoff
                tmpApe_y = tmpApe*np.sin(a) + tmpVoff
            else:
                tmpApe_x = tmpApe*np.cos(a)
                tmpApe_y = tmpApe*np.sin(a)

            # cutoff to remove large apertures
            if aper_cutoff is not None and aper_cutoff > 0:
                filter_ar = np.sqrt(tmpApe_x**2 + tmpApe_y**2) < aper_cutoff
                tmpSs = tmpSs[filter_ar]
                tmpApe_x = tmpApe_x[filter_ar]
                tmpApe_y = tmpApe_y[filter_ar]

            Ss.append(tmpSs)
            Ape_x.append(tmpApe_x)
            Ape_y.append(tmpApe_y)

        Ss = np.hstack(Ss)
        Ape_x = np.hstack(Ape_x)
        Ape_y = np.hstack(Ape_y)

        if 'figure' not in kwargs.keys():
            fig = mlab.figure(bgcolor=(0, 0, 0), size=(1920, 1080))
            kwargs['figure'] = fig
        else:
            fig = kwargs['figure']
        aperture = mlab.points3d(Ss,
                                 Ape_x,
                                 Ape_y,
                                 mode='point',
                                 **kwargs
                                 )
        return fig, aperture
