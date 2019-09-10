import pandas as pd
from pathlib import Path

from mayavi import mlab


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

    def show(self, **kwargs):
        if 'figure' not in kwargs.keys():
            fig = mlab.figure()
            kwargs['figure'] = fig
        else:
            fig = kwargs['figure']
        losses = mlab.points3d(self.df['slos'],
                               self.df['x'].abs()*1e3,
                               self.df['y'].abs()*1e3,
                               mode='sphere',
                               colormap='viridis',
                               scale_factor=0.7,
                               **kwargs
                               )
        losses.glyph.scale_mode = 'scale_by_vector'
        losses.mlab_source.dataset.point_data.scalars = self.df['turn'].values / self.df['turn'].max()
        return fig, losses
