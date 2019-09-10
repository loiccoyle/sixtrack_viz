import math
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iter, *args, **kwargs):
        return iter

from mayavi import mlab
# from collections import OrderedDict

from . import shapes


class aperture:

    def __init__(self, line, invertSigns=[]):
        self.name = None  # string
        self.atyp = None  # RT, CR, etc...
        self.s = None    # [m]
        self.specs = []
        self._fromLine(line, invertSigns=invertSigns)

    def isEmpty(self):
        return sum(self.specs) == 0.0

    def _fromLine(self, line, invertSigns=[]):
        data = line.strip().split()
        self.name = data[0]
        self.atyp = data[1]
        self.s = float(data[2])
        for ii in range(11):
            self.specs.append(float(data[ii + 3]))
        for ii in invertSigns:
            self.specs[ii] *= -1

    def getAperture(self, angle):
        ape = 0.0
        if (self.atyp == 'CR'):
            ape = shapes.Circle(angle,
                                self.specs[0])
        elif (self.atyp == 'RE'):
            ape = shapes.Rectangle(angle,
                                   self.specs[0],
                                   self.specs[1])
        elif (self.atyp == 'EL'):
            ape = shapes.Ellipse(angle,
                                 self.specs[0],
                                 self.specs[1])
        elif (self.atyp == 'RL'):
            ape = shapes.RectEllipse(angle,
                                     self.specs[0],
                                     self.specs[1],
                                     self.specs[2],
                                     self.specs[3])
        elif (self.atyp == 'OC'):
            ape = shapes.Octagon(angle,
                                 self.specs[0],
                                 self.specs[1],
                                 self.specs[2],
                                 self.specs[3])
        elif (self.atyp == 'RT'):
            # wrong!
            ape = shapes.Racetrack(angle,
                                   self.specs[0],
                                   self.specs[1],
                                   self.specs[2],
                                   self.specs[3])
        elif (self.atyp == 'TR'):
            ape = shapes.Transition(angle,
                                    self.specs[0],
                                    self.specs[1],
                                    self.specs[2],
                                    self.specs[3],
                                    self.specs[4],
                                    self.specs[5],
                                    self.specs[6],
                                    self.specs[7])
        else:
            print(self.atyp)
        return self.s, ape

    def getHOffset(self):
        return self.s, self.specs[9]

    def getVOffset(self):
        return self.s, self.specs[10]


class Profile:

    def __init__(self, file, invertSigns=[]):
        self.apertures = []
        self.fileName = None
        self._parseApeDump(file, invertSigns=invertSigns)

    def __len__(self):
        return len(self.apertures)

    def _parseApeDump(self, file, invertSigns=[]):
        with open(file, 'r') as iFile:
            print(' loading %s file...' % (file))
            for line in iFile.readlines():
                if (not line.startswith('#')):
                    tmpApe = aperture(line, invertSigns=invertSigns)
                    if (tmpApe.isEmpty()):
                        print(f' ...aperture {tmpApe.name} at {tmpApe.s} is NULL!')
                    self.apertures.append(tmpApe)
            if (len(self) == 0):
                print(' ...no aperture markers found!')
            else:
                self.fileName = file

# undefined tag variable 
    # def filterOutTransitions(self):
    #     print(" filtering out interpolated values from profile...")
    #     apeProfile = Profile()
    #     apeProfile.fileName = self.fileName
    #     apeProfile.apertures = [
    #         k for k in self.apertures[tag] if (k.name != 'interpolated')]
    #     return apeProfile

    def getApeVsS(self, angle):
        # print(' aperture at %g degs...' % (angle))
        Ss = []
        apes = []
        if (angle < 0.0 or angle > 90.0):
            print(' invalid angle - allowed range: [0:90] degs')
            return Ss, apes
        angle_rad = math.radians(angle)
        for aper in self.apertures:
            tmpS, tmpApe = aper.getAperture(angle_rad)
            Ss.append(tmpS)
            apes.append(tmpApe)
        return np.array(Ss), np.array(apes)

    def getHOffset(self):
        Ss = []
        offsets = []
        for aper in self.apertures:
            tmpS, tmpOff = aper.getHOffset()
            Ss.append(tmpS)
            offsets.append(tmpOff)
        return Ss, offsets

    def getVOffset(self):
        Ss = []
        offsets = []
        for aper in self.apertures:
            tmpS, tmpOff = aper.getVOffset()
            Ss.append(tmpS)
            offsets.append(tmpOff)
        return Ss, offsets

    def show(self, angles=np.linspace(0, 90, 20), aper_cutoff=50, **kwargs):
        # 3d render
        Ss = []
        Ape_x = []
        Ape_y = []
        for a in tqdm(angles, desc='Calculating aperture for angles'):
            tmpSs, tmpApe = self.getApeVsS(a)
            # if Ss == []:
            # cutoff to remove large apertures
            if aper_cutoff is not None:
                filter_ar = tmpApe < aper_cutoff
                tmpSs = tmpSs[filter_ar]
                tmpApe = tmpApe[filter_ar]
            Ss.append(tmpSs)
            Ape_x.append(tmpApe*np.cos(np.radians(a)))
            Ape_y.append(tmpApe*np.sin(np.radians(a)))

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
        # mlab.show()

        # 2d offset plot
        # fig = plt.figure()
        # ax_2d = fig.add_subplot(1, 1, 1)
        # # offsets
        # ax_2d.grid()
        # ax_2d.set_xlabel('s [m]')
        # ax_2d.set_ylabel('offset [mm]')
        # ax_2d.set_xlim(sMin, sMax)
        # # cm = plt.get_cmap('gist_rainbow')
        # tmpSs, tmpOff = self.getHOffset()
        # ax_2d.plot(tmpSs, tmpOff, '.-', label='H offset')
        # tmpSs, tmpOff = self.getVOffset()
        # ax_2d.plot(tmpSs, tmpOff, '.-', label='V offset')
        # ax_2d.legend(loc='best')
        # plt.show()
