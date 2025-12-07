"""
Capítulo 1: Coordenadas Astronómicas (Versión Genérica).

Módulo de transformación universal. Permite convertir entre sistemas de coordenadas
manejando automáticamente las unidades de entrada y salida (Grados, Horas, Radianes, GMS, HMS).

Sistemas:
    - HORIZONTAL (Azimut, Altura/Distancia Cenital)
    - HORARIO (Ángulo Horario, Declinación)
    - ECUATORIAL (Ascensión Recta, Declinación)
    - ECLIPTICO (Longitud, Latitud)
    - GALACTICO (Longitud, Latitud)

Unidades soportadas:
    - 'rad': Radianes (float)
    - 'deg': Grados decimales (float)
    - 'hour': Horas decimales (float)
    - 'dms': Grados, Minutos, Segundos (tupla o array Nx3)
    - 'hms': Horas, Minutos, Segundos (tupla o array Nx3)
"""

import numpy as np
from typing import Tuple, Union, Any, Literal
from ..core import constants as k
from ..core import utils

# ==============================================================================
# Definiciones de Constantes y Tipos
# ==============================================================================

class Sistema:
    HORIZONTAL = 'horizontal'   # (Azimut, Distancia Cenital)
    HORARIO = 'horario'         # (Ángulo Horario, Declinación)
    ECUATORIAL = 'ecuatorial'   # (Ascensión Recta, Declinación)
    ECLIPTICO = 'ecliptico'     # (Longitud, Latitud)
    GALACTICO = 'galactico'     # (Longitud, Latitud)

class Unidad:
    RAD = 'rad'
    DEG = 'deg'     # Grados decimales
    HOUR = 'hour'   # Horas decimales
    DMS = 'dms'     # Tupla (g, m, s)
    HMS = 'hms'     # Tupla (h, m, s)

# ==============================================================================
# Función Maestra de Conversión
# ==============================================================================

def transformar(
    c1: Union[float, tuple, np.ndarray],
    c2: Union[float, tuple, np.ndarray],
    origen: str,
    destino: str,
    unidad_in: str = Unidad.RAD,
    unidad_out: str = Unidad.RAD,
    **kwargs
) -> Tuple[Any, Any]:
    """
    Convierte coordenadas de un sistema/unidad a otro sistema/unidad.

    Argumentos:
        c1, c2: Coordenadas de entrada (ej. Azimut, Altura o AR, Dec).
                Pueden ser floats, tuplas (g,m,s) o arrays de numpy.
        origen: Sistema de referencia de entrada (clase Sistema).
        destino: Sistema de referencia de salida (clase Sistema).
        unidad_in: Formato de las coordenadas de entrada (clase Unidad). Default: 'rad'.
        unidad_out: Formato deseado para la salida (clase Unidad). Default: 'rad'.
        **kwargs: Parámetros de contexto (phi, TS, epsilon). Deben estar en RADIANES
                  o especificar su unidad con sufijo (ej. phi_deg=40.0).
                  - phi: Latitud observador.
                  - TS: Tiempo Sidéreo Local.
                  - epsilon: Oblicuidad eclíptica (default J2000).

    Retorna:
        (res1, res2): Coordenadas transformadas en el formato 'unidad_out'.
    """
    
    # 1. Gestionar parámetros de contexto (phi, TS) a Radianes
    # Permite pasar phi_deg=40 en lugar de phi=0.698...
    ctx = _normalizar_contexto(kwargs)

    # 2. Estandarizar entrada a RADIANES (c1_rad, c2_rad)
    #    Si el sistema es HORIZONTAL, asumimos que c2 es ALTURA si unidad_in no es rad,
    #    pero el cálculo interno requiere DISTANCIA CENITAL (z).
    #    Haremos la conversión matemática después.
    val1_rad = _input_a_rad(c1, unidad_in, es_tiempo=True if origen in [Sistema.HORARIO, Sistema.ECUATORIAL] else False)
    val2_rad = _input_a_rad(c2, unidad_in, es_tiempo=False)

    # Caso especial Horizontal: Entrada suele ser Altura (h), fórmulas usan Distancia Cenital (z)
    # z = 90 - h
    if origen == Sistema.HORIZONTAL:
        # Asumimos que el usuario da (Azimut, Altura)
        val2_rad = np.pi/2 - val2_rad

    # 3. Motor de Transformación (Radianes -> Radianes)
    out1_rad, out2_rad = _nucleo_transformacion(val1_rad, val2_rad, origen, destino, ctx)

    # Caso especial Horizontal Salida: Convertir z de vuelta a Altura (h) si se desea
    # Normalmente en astronomía observacional se prefiere Altura.
    if destino == Sistema.HORIZONTAL:
        out2_rad = np.pi/2 - out2_rad

    # 4. Formatear salida
    es_tiempo_salida = True if destino in [Sistema.HORARIO, Sistema.ECUATORIAL] else False
    res1 = _rad_a_output(out1_rad, unidad_out, es_tiempo=es_tiempo_salida)
    res2 = _rad_a_output(out2_rad, unidad_out, es_tiempo=False)

    return res1, res2

# ==============================================================================
# Lógica Interna (Privada)
# ==============================================================================

def _nucleo_transformacion(c1, c2, origen, destino, ctx):
    """Motor Hub & Spoke en Radianes puro."""
    if origen == destino:
        return c1, c2

    # --- PASO 1: Origen -> HUB (Ecuatorial Absoluto: alpha, delta) ---
    alpha, delta = 0.0, 0.0

    if origen == Sistema.ECUATORIAL:
        alpha, delta = c1, c2
    elif origen == Sistema.HORARIO:
        _validar_ctx(ctx, 'TS', origen)
        alpha = utils.normalize_rad(ctx['TS'] - c1) # alpha = TS - H
        delta = c2
    elif origen == Sistema.HORIZONTAL:
        _validar_ctx(ctx, ['phi', 'TS'], origen)
        H, delta = _horizontal_to_horary(c1, c2, ctx['phi']) # c1=A, c2=z
        alpha = utils.normalize_rad(ctx['TS'] - H)
    elif origen == Sistema.ECLIPTICO:
        eps = ctx.get('epsilon', k.EPSILON_J2000)
        alpha, delta = _ecliptic_to_equatorial(c1, c2, eps)
    elif origen == Sistema.GALACTICO:
        alpha, delta = _galactic_to_equatorial(c1, c2)

    # --- PASO 2: HUB -> Destino ---
    if destino == Sistema.ECUATORIAL:
        return alpha, delta
    elif destino == Sistema.HORARIO:
        _validar_ctx(ctx, 'TS', destino)
        H = utils.normalize_rad(ctx['TS'] - alpha)
        return H, delta
    elif destino == Sistema.HORIZONTAL:
        _validar_ctx(ctx, ['phi', 'TS'], destino)
        H = utils.normalize_rad(ctx['TS'] - alpha)
        A, z = _horary_to_horizontal(H, delta, ctx['phi'])
        return A, z
    elif destino == Sistema.ECLIPTICO:
        eps = ctx.get('epsilon', k.EPSILON_J2000)
        return _equatorial_to_ecliptic(alpha, delta, eps)
    elif destino == Sistema.GALACTICO:
        return _equatorial_to_galactic(alpha, delta)
    
    raise ValueError(f"Sistema destino no soportado: {destino}")

# --- Fórmulas Matemáticas Vectoriales (Abad, Docobo, Elipe) ---

def _horizontal_to_horary(A, z, phi):
    """(Azimut, Zenital) -> (H, Delta). A desde el SUR."""
    sin_z, cos_z = np.sin(z), np.cos(z)
    sin_A, cos_A = np.sin(A), np.cos(A)
    sin_phi, cos_phi = np.sin(phi), np.cos(phi)

    sin_delta = -sin_z * cos_A * cos_phi + cos_z * sin_phi
    delta = np.arcsin(np.clip(sin_delta, -1, 1))
    
    y = sin_z * sin_A
    x = sin_z * cos_A * sin_phi + cos_z * cos_phi
    H = np.arctan2(y, x)
    return utils.normalize_rad(H), delta

def _horary_to_horizontal(H, delta, phi):
    """(H, Delta) -> (Azimut, Zenital). Retorna A desde el SUR."""
    sin_d, cos_d = np.sin(delta), np.cos(delta)
    sin_H, cos_H = np.sin(H), np.cos(H)
    sin_phi, cos_phi = np.sin(phi), np.cos(phi)

    cos_z = cos_d * cos_H * cos_phi + sin_d * sin_phi
    z = np.arccos(np.clip(cos_z, -1, 1))

    num = cos_d * sin_H
    den = cos_d * cos_H * sin_phi - sin_d * cos_phi
    A = np.arctan2(num, den)
    return utils.normalize_rad(A), z

def _equatorial_to_ecliptic(alpha, delta, eps):
    sin_d, cos_d = np.sin(delta), np.cos(delta)
    sin_a, cos_a = np.sin(alpha), np.cos(alpha)
    sin_e, cos_e = np.sin(eps), np.cos(eps)

    sin_b = -cos_d * sin_a * sin_e + sin_d * cos_e
    beta = np.arcsin(np.clip(sin_b, -1, 1))
    
    y = cos_d * sin_a * cos_e + sin_d * sin_e
    x = cos_d * cos_a
    lamb = np.arctan2(y, x)
    return utils.normalize_rad(lamb), beta

def _ecliptic_to_equatorial(lamb, beta, eps):
    sin_b, cos_b = np.sin(beta), np.cos(beta)
    sin_l, cos_l = np.sin(lamb), np.cos(lamb)
    sin_e, cos_e = np.sin(eps), np.cos(eps)

    sin_d = cos_b * sin_l * sin_e + sin_b * cos_e
    delta = np.arcsin(np.clip(sin_d, -1, 1))
    
    y = cos_b * sin_l * cos_e - sin_b * sin_e
    x = cos_b * cos_l
    alpha = np.arctan2(y, x)
    return utils.normalize_rad(alpha), delta

def _equatorial_to_galactic(alpha, delta):
    # J2000
    ap = np.radians(192.85948)
    dp = np.radians(27.12825)
    lnode = np.radians(32.93192)
    
    sin_d, cos_d = np.sin(delta), np.cos(delta)
    sin_dp, cos_dp = np.sin(dp), np.cos(dp)
    
    diff = alpha - ap
    sin_b = sin_d * sin_dp + cos_d * cos_dp * np.cos(diff)
    b = np.arcsin(np.clip(sin_b, -1, 1))
    
    y = cos_d * np.sin(diff)
    x = sin_d * cos_dp - cos_d * sin_dp * np.cos(diff)
    l = lnode - np.arctan2(y, x)
    return utils.normalize_rad(l), b

def _galactic_to_equatorial(l, b):
    # J2000
    ap = np.radians(192.85948)
    dp = np.radians(27.12825)
    lnode = np.radians(32.93192)
    
    sin_b, cos_b = np.sin(b), np.cos(b)
    sin_dp, cos_dp = np.sin(dp), np.cos(dp)
    
    diff_l = l - lnode
    sin_d = np.sin(b) * np.sin(dp) + np.cos(b) * np.cos(dp) * np.cos(diff_l) # Corrección signo
    # Nota: Usamos la simetría inversa directa
    # sin(d) = cos(b) cos(dp) sin(l-lnode)... no, la fórmula rigurosa es:
    y = np.cos(b) * np.sin(l - lnode)
    x = np.sin(b) * np.cos(dp) - np.cos(b) * np.sin(dp) * np.cos(l - lnode)
    
    sin_d = np.sin(b) * np.sin(dp) + np.cos(b) * np.cos(dp) * np.cos(l - lnode)
    delta = np.arcsin(np.clip(sin_d, -1, 1))
    
    alpha = np.arctan2(y, x) + ap
    return utils.normalize_rad(alpha), delta

# ==============================================================================
# Gestión de Unidades y Contexto
# ==============================================================================

def _normalizar_contexto(kwargs):
    """Convierte parámetros auxiliares (phi, TS) a radianes si vienen con sufijos."""
    ctx = kwargs.copy()
    
    # Latitud
    if 'phi_deg' in ctx:
        ctx['phi'] = np.radians(ctx.pop('phi_deg'))
    elif 'phi' in ctx:
        pass # Asumimos radianes
        
    # Tiempo Sidéreo
    if 'TS_h' in ctx: # TS en horas decimales
        ctx['TS'] = np.radians(ctx.pop('TS_h') * 15.0)
    elif 'TS_deg' in ctx:
        ctx['TS'] = np.radians(ctx.pop('TS_deg'))
        
    # Oblicuidad
    if 'epsilon_deg' in ctx:
        ctx['epsilon'] = np.radians(ctx.pop('epsilon_deg'))
        
    return ctx

def _input_a_rad(val, unidad, es_tiempo=False):
    """Convierte entrada genérica a radianes."""
    if unidad == Unidad.RAD:
        return val
    elif unidad == Unidad.DEG:
        return np.radians(val)
    elif unidad == Unidad.HOUR:
        return np.radians(val * 15.0)
    elif unidad == Unidad.DMS:
        # Se espera tupla (g, m, s) o array Nx3
        val = np.array(val)
        if val.ndim == 1 and val.shape[0] == 3: # Un solo ángulo
            return utils.to_rad(val[0], val[1], val[2])
        # Vectorizado pendiente para arrays grandes, aquí simple:
        return utils.to_rad(val[...,0], val[...,1], val[...,2])
    elif unidad == Unidad.HMS:
        val = np.array(val)
        if val.ndim == 1 and val.shape[0] == 3:
            return utils.hms_to_rad(val[0], val[1], val[2])
        return utils.hms_to_rad(val[...,0], val[...,1], val[...,2])
    else:
        raise ValueError(f"Unidad de entrada desconocida: {unidad}")

def _rad_a_output(val_rad, unidad, es_tiempo=False):
    """Convierte radianes al formato de salida deseado."""
    if unidad == Unidad.RAD:
        return val_rad
    elif unidad == Unidad.DEG:
        deg = np.degrees(val_rad)
        if not es_tiempo: # Normalizar latitud a [-90, 90] si fuera necesario? No, el cálculo ya lo da.
            # Normalizar longitud a [0, 360)
            pass
        return deg
    elif unidad == Unidad.HOUR:
        # Normalizar a [0, 24)
        return (np.degrees(val_rad) / 15.0) % 24.0
    elif unidad == Unidad.DMS:
        return utils.rad_to_dms(val_rad)
    elif unidad == Unidad.HMS:
        return utils.rad_to_hms(val_rad)
    else:
        raise ValueError(f"Unidad de salida desconocida: {unidad}")

def _validar_ctx(ctx, keys, sistema):
    if isinstance(keys, str): keys = [keys]
    for k in keys:
        if k not in ctx:
            raise ValueError(f"Falta parámetro '{k}' para el sistema {sistema}")