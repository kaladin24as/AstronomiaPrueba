"""Utilidades matemáticas y de conversión."""
import numpy as np

def to_rad(d, m=0, s=0, sign=1):
    """Convierte GMS a radianes. Soporta arrays."""
    deg = np.abs(d) + m/60.0 + s/3600.0
    return np.radians(deg) * np.sign(sign if sign != 0 else 1) * np.sign(d if d != 0 else 1)

def to_hms(rad):
    """Radianes -> (Horas, Minutos, Segundos)."""
    # Normalizar a [0, 2pi]
    rad = rad % (2 * np.pi)
    hours_dec = np.degrees(rad) / 15.0
    h = int(hours_dec)
    rem = (hours_dec - h) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    return h, m, s

def to_dms(rad):
    """Radianes -> (Grados, Minutos, Segundos)."""
    # Manejo de signo
    deg_dec = np.degrees(rad)
    sign = 1 if deg_dec >= 0 else -1
    deg_dec = np.abs(deg_dec)
    d = int(deg_dec)
    rem = (deg_dec - d) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    return sign * d, m, s

def normalize_pi(angle):
    """Normaliza ángulos entre [-pi, pi]."""
    return (angle + np.pi) % (2 * np.pi) - np.pi