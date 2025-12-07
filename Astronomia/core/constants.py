"""Constantes fundamentales (IAU 1976 / WGS84)."""
import numpy as np

# Física y Sistema Solar
C_LIGHT = 299792.458      # km/s
AU_KM = 149597870.0       # km (Unidad Astronómica)

# Tierra (Elipsoide IAU 1976 / Libro Sec 1.8)
R_EARTH_EQ = 6378.140     # km (Radio ecuatorial, a)
F_EARTH = 1.0 / 298.257   # Achatamiento (f)
E_EARTH_SQ = F_EARTH * (2 - F_EARTH) # Excentricidad al cuadrado (e^2)

# Oblicuidad de la eclíptica (J2000.0 estándar aproximado para ejercicios)
EPSILON_J2000 = np.radians(23 + 26/60 + 21.448/3600)