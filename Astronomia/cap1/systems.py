"""
systems.py
Transformaciones generales entre sistemas de coordenadas astronómicos:
Horizontal, Horarias, Ecuatoriales, Eclípticas y Galácticas.
"""

import math
import utils


# ============================================================================
# ---- Horizontal ↔ Horarias
# ============================================================================

def horizontal_to_horary(phi_lat, A, z):
    """
    Horizontal (A, z) → Horarias (H, δ).
    """
    sin_delta = (
        -math.sin(z) * math.cos(A) * math.cos(phi_lat)
        + math.cos(z) * math.sin(phi_lat)
    )
    delta = math.asin(utils.clamp(sin_delta, -1, 1))

    y = math.sin(z) * math.sin(A)
    x = (
        math.sin(z) * math.cos(A) * math.sin(phi_lat)
        + math.cos(z) * math.cos(phi_lat)
    )
    H = math.atan2(y, x)

    return utils.normalizar_rad(H), delta


def horary_to_horizontal(phi_lat, H, delta):
    """
    Horarias (H, δ) → Horizontal (A, z).
    """
    cos_z = (
        math.cos(delta) * math.cos(H) * math.cos(phi_lat)
        + math.sin(delta) * math.sin(phi_lat)
    )
    z = math.acos(utils.clamp(cos_z, -1, 1))

    y = math.cos(delta) * math.sin(H)
    x = (
        math.cos(delta) * math.cos(H) * math.sin(phi_lat)
        - math.sin(delta) * math.cos(phi_lat)
    )
    A = math.atan2(y, x)

    return utils.normalizar_rad(A), z


# ============================================================================
# ---- Horarias ↔ Absolutas
# ============================================================================

def horary_to_absolute(H, TS):
    """Ascensión Recta = TS − H."""
    return utils.normalizar_rad(TS - H)


def absolute_to_horary(alpha, TS):
    """Ángulo Horario = TS − α."""
    return utils.normalizar_rad(TS - alpha)


# ============================================================================
# ---- Absolutas ↔ Eclípticas
# ============================================================================

def absolute_to_ecliptic(alpha, delta, eps):
    """
    Coordenadas ecuatoriales → eclípticas.
    """
    sin_beta = (
        -math.cos(delta) * math.sin(alpha) * math.sin(eps)
        + math.sin(delta) * math.cos(eps)
    )
    beta = math.asin(utils.clamp(sin_beta, -1, 1))

    y = (
        math.cos(delta) * math.sin(alpha) * math.cos(eps)
        + math.sin(delta) * math.sin(eps)
    )
    x = math.cos(delta) * math.cos(alpha)

    lamb = math.atan2(y, x)
    return utils.normalizar_rad(lamb), beta


def ecliptic_to_absolute(lamb, beta, eps):
    """
    Coordenadas eclípticas → ecuatoriales.
    """
    sin_delta = (
        math.cos(beta) * math.sin(lamb) * math.sin(eps)
        + math.sin(beta) * math.cos(eps)
    )
    delta = math.asin(utils.clamp(sin_delta, -1, 1))

    y = (
        math.cos(beta) * math.sin(lamb) * math.cos(eps)
        - math.sin(beta) * math.sin(eps)
    )
    x = math.cos(beta) * math.cos(lamb)

    alpha = math.atan2(y, x)
    return utils.normalizar_rad(alpha), delta


# ============================================================================
# ---- Absolutas ↔ Galácticas (J2000)
# ============================================================================

_AP = math.radians(192.85948)
_DP = math.radians(27.12825)
_LNODE = math.radians(32.93192)


def absolute_to_galactic(alpha, delta):
    """
    Ecuatoriales (J2000) → Galácticas.
    """
    sin_b = (
        math.sin(delta) * math.sin(_DP)
        + math.cos(delta) * math.cos(_DP) * math.cos(alpha - _AP)
    )
    b = math.asin(utils.clamp(sin_b, -1, 1))

    y = math.cos(delta) * math.sin(alpha - _AP)
    x = (
        math.sin(delta) * math.cos(_DP)
        - math.cos(delta) * math.sin(_DP) * math.cos(alpha - _AP)
    )

    diff = math.atan2(y, x)
    l = _LNODE - diff
    return utils.normalizar_rad(l), b


def galactic_to_absolute(l, b):
    """
    Galácticas (J2000) → Ecuatoriales.
    """
    sin_delta = (
        math.sin(b) * math.sin(_DP)
        + math.cos(b) * math.cos(_DP) * math.sin(_LNODE - l)
    )
    delta = math.asin(utils.clamp(sin_delta, -1, 1))

    y = math.cos(b) * math.cos(_LNODE - l)
    x = (
        math.sin(b) * math.cos(_DP)
        - math.cos(b) * math.sin(_DP) * math.sin(_LNODE - l)
    )

    diff = math.atan2(y, x)
    alpha = _AP + diff
    return utils.normalizar_rad(alpha), delta
