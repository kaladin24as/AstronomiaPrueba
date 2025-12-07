"""
cap1/menu.py
Menú del Capítulo 1: Coordenadas Astronómicas.

Este módulo es cargado dinámicamente por main.py.
Debe exponer una función pública:
    get_menu_entry() → (id, título, función_del_capítulo)
"""

import os
import cap1_coords  # módulo con las funciones de conversión


# ============================================================================
#   UTILIDADES LOCALES
# ============================================================================

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    input("\nPresione ENTER para continuar...")


# ============================================================================
#   FUNCIONES DEL CAPÍTULO
# ============================================================================

def menu_conversiones():
    """Submenú: Conversión entre formatos angulares."""
    limpiar()
    print("============================================")
    print("   Conversión de Ángulos y Coordenadas")
    print("============================================\n")

    nombre = input("Nombre del ángulo a ingresar (ej: Declinación, AR, etc.): ").strip()
    rad = cap1_coords.solicitar_angulo(nombre, -360, 360, es_tiempo=False)

    limpiar()
    print("============================================")
    print(f"      RESULTADOS PARA: {nombre}")
    print("============================================\n")
    cap1_coords.mostrar_resultado(nombre, rad)

    pausar()


def submenu_ejemplo_2():
    """
    Ejemplo de cómo añadir otro ejercicio del capítulo.
    Aquí puedes conectar cualquier futura función de cap1_coords.
    """
    limpiar()
    print("============================================")
    print("   EJERCICIO 2 (en construcción)")
    print("============================================\n")

    print("Aquí podrás añadir nuevos cálculos del Capítulo 1.")
    pausar()


# ============================================================================
#   MENÚ PRINCIPAL DEL CAPÍTULO
# ============================================================================

def ejecutar_menu_cap1():
    """Menú principal del Capítulo 1."""
    while True:
        limpiar()
        print("============================================")
        print("    CAPÍTULO 1 – COORDENADAS ASTRONÓMICAS")
        print("============================================\n")

        print("  1. Conversión de ángulos (rad, grados, DMS, HMS)")
        print("  2. Ejercicio 2 (placeholder)")
        print("  0. Volver al menú principal\n")

        op = input("Seleccione opción: ").strip()

        if op == "1":
            menu_conversiones()
        elif op == "2":
            submenu_ejemplo_2()
        elif op == "0":
            return  # ← vuelve al main
        else:
            print("Opción inválida.")
            pausar()


# ============================================================================
#   REGISTRO EN MAIN
# ============================================================================

def get_menu_entry():
    """
    Proporciona al menú principal la información del capítulo.
    Return:
        (id_cap, nombre_visible, funcion_a_ejecutar)
    """
    return ("cap1", "Capítulo 1 – Coordenadas Astronómicas", ejecutar_menu_cap1)
