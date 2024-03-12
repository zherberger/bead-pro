import numpy as np

SRGB_XYZ_TRANSFORMATION_MATRIX = [
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041]
]

EPSILON = 216.0 / 24839.0
KAPPA = 24839.0 / 27.0

# Standard illuminant D65
X_W = 0.950489
Y_W = 1.0
Z_W = 1.088840

# Standard illuminant D50
X_D50 = 0.96422
Y_D50 = 1.0
Z_D50 = 0.82521


def degrees_to_radians(deg):
    return 2 * np.pi * deg / 360.0


def radians_to_degrees(rad):
    return rad * 360.0 / (2 * np.pi)


def srgb_to_xyz(srgb):
    def gamma_expansion(value255):
        if value255 <= 10:
            return float(value255) / 3294.6
        else:
            return ((float(value255) + 14.025) / 269.025) ** 2.4

    r = gamma_expansion(srgb[0])
    g = gamma_expansion(srgb[1])
    b = gamma_expansion(srgb[2])

    return np.matmul(SRGB_XYZ_TRANSFORMATION_MATRIX, [r, g, b])


def xyz_to_lab(xyz):
    def f(v):
        if v > EPSILON:
            return v ** (1.0 / 3.0)
        else:
            return (KAPPA * v + 16.0) / 116.0

    fx = f(xyz[0] / X_W)
    fy = f(xyz[1])  # Y / Y_W is simply Y / 1
    fz = f(xyz[2] / Z_W)

    return [
        116.0 * fy - 16.0,
        500.0 * (fx - fy),
        200.0 * (fy - fz),
    ]


def srgb_to_lab(srgb):
    return xyz_to_lab(srgb_to_xyz(srgb))


def lab_to_lch(lab):
    h = radians_to_degrees(np.arctan2(lab[2], lab[1]))
    if h < 0.0:
        h = 360.0 + h

    return [
        lab[0],
        np.hypot(lab[1], lab[2]),
        h
    ]


def calc_delta_h_prime(h1_prime, h2_prime):
    abs_diff = np.abs(h1_prime - h2_prime)

    if abs_diff <= 180.0:
        return h2_prime - h1_prime
    elif abs_diff > 180.0 and h2_prime <= h1_prime:
        return h2_prime - h1_prime + 360.0
    else:
        return h2_prime - h1_prime - 360.0


def compute_color_distance(lab1, lab2):
    lch1 = lab_to_lch(lab1)
    lch2 = lab_to_lch(lab2)
    l_bar = (lab1[0] + lab2[0]) / 2.0
    delta_l = lab1[0] - lab2[0]

    def calc_a_prime(a, cbar):
        return a * (1 + 0.5 * (1 - np.sqrt(cbar ** 7 / (cbar ** 7 + 25.0 ** 7))))

    c1 = lch1[1]
    c2 = lch2[1]
    c_bar = (c1 + c2) / 2.0
    a1_prime = calc_a_prime(lab1[1], c_bar)
    a2_prime = calc_a_prime(lab2[1], c_bar)
    c1_prime = np.hypot(a1_prime, lab1[2])
    c2_prime = np.hypot(a2_prime, lab2[2])
    c_bar_prime = (c1_prime + c2_prime) / 2.0
    delta_c = c2_prime - c1_prime

    h1_prime = radians_to_degrees(np.arctan2(lab1[2], a1_prime)) % 360.0
    h2_prime = radians_to_degrees(np.arctan2(lab2[2], a2_prime)) % 360.0

    delta_h_prime = calc_delta_h_prime(h1_prime, h2_prime)
    delta_h = 2 * np.sqrt(c1_prime * c2_prime) * np.sin(degrees_to_radians(delta_h_prime / 2.0))

    h_bar_prime = 0.0
    abs_diff = np.abs(h1_prime - h2_prime)

    if abs_diff <= 180.0:
        h_bar_prime = (h1_prime + h2_prime) / 2.0
    elif abs_diff > 180.0 and h1_prime + h2_prime < 360.0:
        h_bar_prime = (h1_prime + h2_prime + 360.0) / 2.0
    else:
        h_bar_prime = (h1_prime + h2_prime - 360.0) / 2.0

    t = 1 \
        - 0.17 * np.cos(degrees_to_radians(h_bar_prime - 30.0)) \
        + 0.24 * np.cos(degrees_to_radians(2 * h_bar_prime)) \
        + 0.32 * np.cos(degrees_to_radians(3 * h_bar_prime + 6.0)) \
        - 0.20 * np.cos(degrees_to_radians(4 * h_bar_prime - 63.0))

    s_l = 1 + (0.015 * (l_bar - 50.0) ** 2) / (np.sqrt(20.0 + (l_bar - 50) ** 2))
    s_c = 1 + 0.045 * c_bar_prime
    s_h = 1 + 0.015 * c_bar_prime * t
    r_t = -2 * np.sqrt(c_bar_prime ** 7 / (c_bar_prime ** 7 + 25.0 ** 7)) * np.sin(
        degrees_to_radians(60 * np.exp(-1 * ((h_bar_prime - 275) / 25) ** 2)))

    return np.sqrt(
        (delta_l / s_l) ** 2
        + (delta_c / s_c) ** 2
        + (delta_h / s_h) ** 2
        + r_t * (delta_c / s_c) * (delta_h / s_h)
    )
