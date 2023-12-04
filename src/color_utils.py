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

def DEGREES_TO_RADIANS(deg):
    return 2 * np.pi * deg / 360.0

def RADIANS_TO_DEGREES(rad):
    return rad * 360.0 / (2 * np.pi)

def srgb_to_xyz(srgb):
    def gamma_expansion(value255):
        if(value255 <= 10):
            return float(value255) / 3294.6
        else :
            return ((float(value255) + 14.025) / 269.025) ** 2.4
        
    R = gamma_expansion(srgb[0])
    G = gamma_expansion(srgb[1])
    B = gamma_expansion(srgb[2])

    return np.matmul(SRGB_XYZ_TRANSFORMATION_MATRIX, [R, G, B])

def xyz_to_lab(xyz):
    def f(v):
        if(v > EPSILON):
            return v ** (1.0 / 3.0)
        else:
            return (KAPPA * v + 16.0) / 116.0
    
    fx = f(xyz[0] / X_W)
    fy = f(xyz[1]) # Y / Y_W is simply Y / 1
    fz = f(xyz[2] / Z_W)

    return [
        116.0 * fy - 16.0,
        500.0 * (fx - fy),
        200.0 * (fy - fz),
    ]

def srgb_to_lab(srgb):
    return xyz_to_lab(srgb_to_xyz(srgb))

def lab_to_lch(lab):
    h = RADIANS_TO_DEGREES(np.arctan2(lab[2], lab[1]))
    if(h < 0.0):
        h = 360.0 + h

    return [
        lab[0],
        np.hypot(lab[1], lab[2]),
        h
    ]

def compute_color_distance(lab1, lab2):
    lch1 = lab_to_lch(lab1)
    lch2 = lab_to_lch(lab2)
    L_BAR = (lab1[0] + lab2[0]) / 2.0
    DELTA_L = lab1[0] - lab2[0]

    def calc_a_prime(a, cbar):
        return a * (1 + 0.5 * (1 - np.sqrt(cbar ** 7 / (cbar ** 7 + 25.0 ** 7))))

    C1 = lch1[1]
    C2 = lch2[1]
    C_BAR = (C1 + C2) / 2.0
    a1_prime = calc_a_prime(lab1[1], C_BAR)
    a2_prime = calc_a_prime(lab2[1], C_BAR)
    C1_PRIME = np.hypot(a1_prime, lab1[2])
    C2_PRIME = np.hypot(a2_prime, lab2[2])
    C_BAR_PRIME = (C1_PRIME + C2_PRIME) / 2.0
    DELTA_C = C2_PRIME - C1_PRIME

    h1_prime = RADIANS_TO_DEGREES(np.arctan2(lab1[2], a1_prime)) % 360.0
    h2_prime = RADIANS_TO_DEGREES(np.arctan2(lab2[2], a2_prime)) % 360.0
    def calc_delta_h_prime(h1_prime, h2_prime):
        abs_diff = np.abs(h1_prime - h2_prime)

        if(abs_diff <= 180.0):
            return h2_prime - h1_prime
        elif(abs_diff > 180.0 and h2_prime <= h1_prime):
            return h2_prime - h1_prime + 360.0
        else:
            return h2_prime - h1_prime - 360.0
        
    delta_h_prime = calc_delta_h_prime(h1_prime, h2_prime)
    DELTA_H = 2 * np.sqrt(C1_PRIME * C2_PRIME) * np.sin(DEGREES_TO_RADIANS(delta_h_prime / 2.0))
    
    H_BAR_PRIME = 0.0
    abs_diff = np.abs(h1_prime - h2_prime)

    if(abs_diff <= 180.0):
        H_BAR_PRIME = (h1_prime + h2_prime) / 2.0
    elif(abs_diff > 180.0 and h1_prime + h2_prime < 360.0):
        H_BAR_PRIME = (h1_prime + h2_prime + 360.0) / 2.0
    else:
        H_BAR_PRIME = (h1_prime + h2_prime - 360.0) / 2.0

    T = 1 \
        - 0.17 * np.cos(DEGREES_TO_RADIANS(H_BAR_PRIME - 30.0)) \
        + 0.24 * np.cos(DEGREES_TO_RADIANS(2 * H_BAR_PRIME)) \
        + 0.32 * np.cos(DEGREES_TO_RADIANS(3 * H_BAR_PRIME + 6.0)) \
        - 0.20 * np.cos(DEGREES_TO_RADIANS(4 * H_BAR_PRIME - 63.0))

    S_L = 1 + (0.015 * (L_BAR - 50.0) ** 2) / (np.sqrt(20.0 + (L_BAR - 50) ** 2))
    S_C = 1 + 0.045 * C_BAR_PRIME
    S_H = 1 + 0.015 * C_BAR_PRIME * T
    R_T = -2 * np.sqrt(C_BAR_PRIME ** 7 / (C_BAR_PRIME ** 7 + 25.0 ** 7)) * np.sin(DEGREES_TO_RADIANS(60 * np.exp(-1 * ((H_BAR_PRIME - 275) / 25) ** 2)))

    return np.sqrt(\
        (DELTA_L / S_L) ** 2 \
        + (DELTA_C / S_C) ** 2 \
        + (DELTA_H / S_H) ** 2 \
        + R_T * (DELTA_C / S_C) * (DELTA_H / S_H)
    )