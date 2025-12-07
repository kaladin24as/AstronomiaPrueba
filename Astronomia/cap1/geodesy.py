"""
geodesy.py
Herramientas para conversión geodésica: latitud geocéntrica,
radio vectorial y coordenadas rectangulares.
"""

import math


def terrestrial_radius(phi_geo, h_m,
                       a=6378.140,
                       f=1.0 / 298.257):
    """
    Elipsoide terrestre IAU 1976 por defecto.
    """
    e2 = f * (2 - f)
    sin_phi = math.sin(phi_geo)
    C = 1.0 / math.sqrt(1 - e2 * sin_phi * sin_phi)
    S = C * (1 - f) ** 2

    h_km = h_m * 0.001

    x = (a * C + h_km) * math.cos(phi_geo)
    z = (a * S + h_km) * math.sin(phi_geo)

    rho = math.sqrt(x * x + z * z)
    phi_c = math.atan2(z, x)
    return rho, phi_c, x, z
