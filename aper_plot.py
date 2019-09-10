#!/usr/bin/env python3
import argparse
import numpy as np

from mayavi import mlab

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
    args = parser.parse_args()

    aper = Profile(args.file)
    fig, aper = aper.show(angles=np.linspace(0, 90, args.angles),
                          aper_cutoff=args.cuttoff,
                          mask_points=10)
    if args.loss_file is not None:
        losses = Losses(args.loss_file)
        fig, los = losses.show(figure=fig)

    mlab.show()
