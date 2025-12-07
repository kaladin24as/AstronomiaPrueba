"""
spherical.py
Conversión entre coordenadas cartesianas y esféricas.
Incluye normalización angular y protección de dominio numérico.
"""

import math
import utils


def spherical_to_cartesian(r, theta, phi):
    """
    Esféricas → Cartesianas.
    theta: longitud (AR, acimut, longitud eclíptica…)
    phi: latitud (declinación, altura, latitud eclíptica…)
    """
    r_cosphi = r * math.cos(phi)
    return (
        r_cosphi * math.cos(theta),
        r_cosphi * math.sin(theta),
        r * math.sin(phi)
    )


def cartesian_to_spherical(x, y, z):
    """
    Cartesianas → Esféricas.
    Devuelve (r, theta_longitud, phi_latitud).
    """
    r = math.sqrt(x * x + y * y + z * z)
    if r == 0:
        return 0.0, 0.0, 0.0

    phi = math.asin(utils.clamp(z / r, -1.0, 1.0))
    theta = math.atan2(y, x)
    return r, utils.normalizar_rad(theta), phi
