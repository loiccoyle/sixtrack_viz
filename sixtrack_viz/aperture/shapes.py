import math


def Circle(angle, R):
    'angle in radians - range: [0:2pi] or [-pi:pi]'
    return R


def Ellipse(angle, a, b):
    'angle in radians - range: [0:2pi] or [-pi:pi]'
    ape = 0.0
    if (a != 0.0 and b != 0.0):
        ape = 1 / math.sqrt((math.cos(angle) / a)**2 +
                            (math.sin(angle) / b)**2)
    return ape


def Rectangle(angle, a, b):
    'angle in radians - range: [0:pi/2]'
    if (angle == 0):
        ape = a
    elif (angle == math.pi / 2):
        ape = b
    else:
        T = math.atan2(b, a)
        if (angle < T):
            ape = a / math.cos(angle)
        else:
            ape = b / math.sin(angle)
    return ape


def RectEllipse(angle, a, b, c, d):
    'angle in radians'
    return min(Rectangle(angle, a, b), Ellipse(angle, c, d))


def Line(angle, ml, ql):
    'angle in radians - range: [0:pi/2]'
    m = math.tan(angle)
    if (angle == 0):
        ape = -ql / ml
    elif (angle == math.pi / 2):
        ape = ql
    else:
        x = ql / (m - ml)
        ape = x / math.cos(angle)
    return ape


def Octagon(angle, a, b, theta1, theta2):
    'angle in radians - range: [0:pi/2]'
    mO = (b - a * math.tan(theta1)) / (b / math.tan(theta2) - a)
    qO = a * math.tan(theta1) - mO * a
    return min(Rectangle(angle, a, b), Line(angle, mO, qO))


def Racetrack(angle, aprx, apry, apex, apey):
    'angle in radians - range: [0:pi/2]'
    if (angle == 0):
        ape = aprx + apex
    elif (angle == math.pi / 2):
        ape = apry + apey
    else:
        T1 = math.atan2(apry, aprx + apex)
        T2 = math.atan2(apry + apey, aprx)
        if (angle <= T1 or angle >= T2):
            ape = Rectangle(angle, aprx + apex, apry + apey)
        else:
            # line in ref sys of rounded corner
            m = math.tan(angle)
            q = m * aprx - apry
            # intersection in ref sys of rounded corner
            x = (-apex**2 * m * q + apex * apey * math.sqrt(-q**2 + (m * apex)**2 + apey**2)) / ((m * apex)**2 + apey**2)
            # aperture is still in aperture ref sys
            ape = (x + aprx) / math.cos(angle)
    return ape


def Transition(angle, a, b, c, d, e, f, theta1, theta2):
    return min(Rectangle(angle, a, b),
               Racetrack(angle, e, f, c, d),
               Octagon(angle, a, b, theta1, theta2))
