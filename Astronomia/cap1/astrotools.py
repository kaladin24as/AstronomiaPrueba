"""
astrotools.py
Herramientas astronómicas independientes:
distancia angular, visibilidad, orto/ocaso.
"""

import math
import utils


def angular_distance(a1, d1, a2, d2):
    """Distancia angular por el coseno esférico."""
    cos_th = (
        math.sin(d1) * math.sin(d2)
        + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2)
    )
    return math.acos(utils.clamp(cos_th, -1, 1))


def visibility(phi, delta):
    """
    Determina visibilidad:
        - Siempre visible
        - Nunca visible
        - Normal (con H0 válido)
    """
    cos_H0 = -math.tan(phi) * math.tan(delta)

    if cos_H0 >= 1:
        return "NUNCA_VISIBLE", 0.0
    if cos_H0 <= -1:
        return "SIEMPRE_VISIBLE", 0.0

    return "NORMAL", math.acos(cos_H0)
