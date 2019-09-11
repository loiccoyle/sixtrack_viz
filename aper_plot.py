#!/usr/bin/env python3
import argparse
import numpy as np


from sixtrack_viz.aperture.profile import Profile
from sixtrack_viz.aperture.losses import Losses


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Sixtrack aperture dump file.')
    parser.add_argument('-a', '--angles', help='Number of angles.', type=int,
                        default=10)
    parser.add_argument('-c', '--cuttoff', help='Aperture radial cuttoff.',
                        type=float, default=50)
    parser.add_argument('-l', '--loss_file',
                        help='Sixtrack aperture losses dump file.',
                        default=None)
    parser.add_argument('-o', '--offset',
                        help='Include hoizontal and vertical aperture offset',
                        action='store_true')
    parser.add_argument('-s', '--style',
                        help='Plotting style, either "point", "line" or "surf".',
                        choices=['point', 'line', 'surf'],
                        default='line')
    args = parser.parse_args()

    aper = Profile(args.file)

    aper.drop_interpolated()
    aper.drop_consecutive_duplicates()

    plotter = aper.show(angles=np.linspace(0, 90, args.angles),
                        aper_cutoff=args.cuttoff,
                        with_offset=args.offset,
                        style=args.style)
    # plotter.show()
    if args.loss_file is not None:
        losses = Losses(args.loss_file)
        plotter = losses.show(plotter=plotter)

    plotter.show()
