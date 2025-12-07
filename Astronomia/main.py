"""
main.py
Punto de entrada principal del proyecto.

• Arquitectura basada en módulos (capítulos) extensibles.
• Cada capítulo debe implementar una función: get_menu_entry()
• El menú es generado dinámicamente a partir de los capítulos cargados.
"""

import sys


# ============================================================================
#   REGISTRO DE CAPÍTULOS
#   Cada capítulo debe exponer: get_menu_entry() → (id, título, función)
# ============================================================================

# Importa aquí los capítulos que tengas:
from cap1.menu import get_menu_entry as cap1_entry
# Cuando tengas más capítulos:
# from cap2.menu import get_menu_entry as cap2_entry
# from cap3.menu import get_menu_entry as cap3_entry
# ...


def cargar_capitulos():
    """
    Devuelve la lista de capítulos registrados.
    Cada entrada es una tupla: (id, texto_visible, funcion_menu)
    """
    capitulos = [
        cap1_entry(),
        # Agrega más capítulos simplemente añadiendo:
        # cap2_entry(),
        # cap3_entry(),
    ]
    return capitulos


# ============================================================================
#   MENÚ PRINCIPAL
# ============================================================================

def mostrar_menu_principal(capitulos):
    print("\n========================")
    print("  ASTRONOMÍA ESFÉRICA ")
    print("  Menú principal")
    print("========================\n")

    for idx, (_, titulo, _) in enumerate(capitulos, start=1):
        print(f"  {idx}. {titulo}")

    print("  0. SALIR\n")


def leer_opcion(max_opcion):
    while True:
        op = input("Seleccione una opción: ").strip()
        if op.isdigit():
            op = int(op)
            if 0 <= op <= max_opcion:
                return op
        print(f"Opción inválida (0–{max_opcion}). Intente nuevamente.\n")


# ============================================================================
#   LOOP PRINCIPAL
# ============================================================================

def main():
    capitulos = cargar_capitulos()

    while True:
        mostrar_menu_principal(capitulos)
        op = leer_opcion(len(capitulos))

        if op == 0:
            print("\nSaliendo del programa.\n")
            sys.exit(0)

        cap_id, cap_titulo, cap_func = capitulos[op - 1]
        print(f"\n>>> Ejecutando {cap_titulo}...\n")

        try:
            cap_func()
        except Exception as e:
            print("\n[ERROR] Ocurrió una excepción dentro del capítulo:")
            print(type(e).__name__, "-", e)
            print("\nRegresando al menú principal...\n")


if __name__ == "__main__":
    main()
