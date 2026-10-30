import argparse
import ast
import sys
from pathlib import Path
from extraccion import extraer_todas_las_funciones
from normalizacion import normalizar_arbol_funcion
from serializacion import serializar_pre_order
from comparacion import similitud_jaccard, UMBRAL_DUPLICADO

# Devuelve el nombre del archivo y el nombre de la función a partir de un string con formato 'archivo.py:nombre_funcion'.
def parsear_objetivo(objetivo: str):
    if ":" not in objetivo:
        raise ValueError("El objetivo debe tener el formato 'archivo.py:nombre_funcion'")
    archivo, nombre = objetivo.split(":", 1)
    return archivo.strip(), nombre.strip()

# Parsea un string de código Python y devuelve el nodo AST de la primera función encontrada.
def obtener_funcion_de_codigo(codigo: str):
    try:
        arbol = ast.parse(codigo)
    except SyntaxError as e:
        print(f"Error de sintaxis en el código ingresado: {e}")
        sys.exit(1)

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef):
            return nodo

    print("Error: No se encontró ninguna definición de función (def) en el código ingresado.")
    sys.exit(1)

def main():
    # Definimos los argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Detector de similitud de funciones vía AST")
    parser.add_argument("--dir", required=True, help="Ruta al directorio de archivos Python a analizar")
    parser.add_argument("--top", type=int, default=5, help="Cantidad de resultados similares a mostrar")
    parser.add_argument("--umbral", type=float, default=UMBRAL_DUPLICADO,
                        help=f"Umbral de similitud para marcar un clon (0.0 a 1.0). Por defecto: {UMBRAL_DUPLICADO}")

    # Grupo mutuamente excluyente: el usuario elige UNA de las dos formas de ingresar la función objetivo
    grupo_objetivo = parser.add_mutually_exclusive_group(required=True)
    grupo_objetivo.add_argument("--funcion",
                                help="Función objetivo en formato 'archivo.py:nombre_funcion'")
    grupo_objetivo.add_argument("--codigo",
                                help="Código fuente Python de la función objetivo (ej: \"def f(x): return x\")")

    args = parser.parse_args()

    # Validar umbral
    if not (0.0 <= args.umbral <= 1.0):
        print(f"Advertencia: --umbral debe ser un valor entre 0.0 y 1.0. Se usará el valor por defecto: {UMBRAL_DUPLICADO}")
        args.umbral = UMBRAL_DUPLICADO

    todas_las_funciones = extraer_todas_las_funciones(args.dir)

    # ── MODO 1: el usuario pasa --funcion archivo.py:nombre ──────────────────
    if args.funcion:
        archivo_obj, nombre_obj = parsear_objetivo(args.funcion)

        funcion_objetivo_nodo = None
        funcion_objetivo_ref  = None
        for f in todas_las_funciones:
            if Path(f.archivo).name == Path(archivo_obj).name and f.nombre == nombre_obj:
                funcion_objetivo_nodo = f.nodo_ast
                funcion_objetivo_ref  = f   # guardamos la referencia para excluirla del bucle
                break

        if funcion_objetivo_nodo is None:
            print(f"Error: No se encontró la función '{nombre_obj}' en '{archivo_obj}'")
            sys.exit(1)

        etiqueta_objetivo = f"{nombre_obj} ({archivo_obj})"

    # ── MODO 2: el usuario pasa --codigo "def f(x): ..." ─────────────────────
    else:
        funcion_objetivo_nodo = obtener_funcion_de_codigo(args.codigo)
        funcion_objetivo_ref  = None   # no pertenece a ningún archivo del directorio
        nombre_obj            = funcion_objetivo_nodo.name
        etiqueta_objetivo     = f"{nombre_obj} (código ingresado)"

    # Normalizar y serializar la función objetivo
    ast_norm_obj = normalizar_arbol_funcion(funcion_objetivo_nodo)
    tokens_obj   = serializar_pre_order(ast_norm_obj)

    # Comparar contra todas las funciones del directorio
    resultados = []
    for f in todas_las_funciones:
        # En modo --funcion: excluir la función contra sí misma
        if funcion_objetivo_ref and f.archivo == funcion_objetivo_ref.archivo and f.linea == funcion_objetivo_ref.linea:
            continue

        ast_norm_candidata = normalizar_arbol_funcion(f.nodo_ast)
        tokens_candidata   = serializar_pre_order(ast_norm_candidata)
        score              = similitud_jaccard(tokens_obj, tokens_candidata)

        resultados.append((f, score))

    # Ordenar por score decreciente
    resultados.sort(key=lambda x: x[1], reverse=True)

    print(f"\nBúsqueda de funciones similares para: {etiqueta_objetivo}")
    print(f"Umbral de clon establecido: {args.umbral:.2f}\n")
    print(f"{'Función':<25} {'Archivo':<25} {'Línea':<8} {'Similitud':<12} {'Candidata a Clon'}")
    print("-" * 80)

    for f, score in resultados[: args.top]:
        es_clon = "SÍ" if score >= args.umbral else "NO"
        print(f"{f.nombre:<25} {Path(f.archivo).name:<25} {f.linea:<8} {score:.4f}      {es_clon}")

if __name__ == "__main__":
    main()
