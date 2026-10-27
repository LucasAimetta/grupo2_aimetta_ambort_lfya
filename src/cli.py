import argparse
import sys
from pathlib import Path
from src.extraccion import extraer_todas_las_funciones
from src.normalizacion import normalizar_arbol_funcion
from src.serializacion import serializar_pre_order
from src.comparacion import similitud_jaccard, UMBRAL_DUPLICADO

#Devuelve el nombre del archivo y el nombre de la función a partir de un string con formato 'archivo.py:nombre_funcion'.
def parsear_objetivo(objetivo: str):
    if ":" not in objetivo:
        raise ValueError("El objetivo debe tener el formato 'archivo.py:nombre_funcion'")
    archivo, nombre = objetivo.split(":", 1)
    return archivo.strip(), nombre.strip()

def main():
    #Definemos los argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Detector de similitud de funciones vía AST")
    parser.add_argument("--dir", required=True, help="Ruta al directorio de archivos Python")
    parser.add_argument("--funcion", required=True, help="Función objetivo en formato 'archivo.py:nombre_funcion'")
    parser.add_argument("--top", type=int, default=5, help="Cantidad de resultados similares a mostrar")
    args = parser.parse_args()

    archivo_obj, nombre_obj = parsear_objetivo(args.funcion)
    todas_las_funciones = extraer_todas_las_funciones(args.dir)

    # Localizar la función objetivo
    funcion_objetivo = None
    for f in todas_las_funciones:
        if Path(f.archivo).name == Path(archivo_obj).name and f.nombre == nombre_obj:
            funcion_objetivo = f
            break

    if not funcion_objetivo:
        print(f"Error: No se encontró la función '{nombre_obj}' en '{archivo_obj}'")
        sys.exit(1)

    # Procesar la función objetivo
    ast_norm_obj = normalizar_arbol_funcion(funcion_objetivo.nodo_ast)
    tokens_obj = serializar_pre_order(ast_norm_obj)

    resultados = []
    for f in todas_las_funciones:
        # Evitar comparar la función contra sí misma exactamente en la misma ubicación
        if f.archivo == funcion_objetivo.archivo and f.linea == funcion_objetivo.linea:
            continue

        ast_norm_candidata = normalizar_arbol_funcion(f.nodo_ast)
        tokens_candidata = serializar_pre_order(ast_norm_candidata)
        score = similitud_jaccard(tokens_obj, tokens_candidata)

        resultados.append((f, score))

    # Ordenar por score decreciente
    resultados.sort(key=lambda x: x[1], reverse=True)

    print(f"\nBúsqueda de funciones similares para: {nombre_obj} ({archivo_obj})")
    print(f"Umbral de clon establecido: {UMBRAL_DUPLICADO:.2f}\n")
    print(f"{'Función':<25} {'Archivo':<25} {'Línea':<8} {'Similitud':<12} {'Candidata a Clon'}")
    print("-" * 80)

    for f, score in resultados[: args.top]:
        es_clon = "SÍ" if score >= UMBRAL_DUPLICADO else "NO"
        print(f"{f.nombre:<25} {Path(f.archivo).name:<25} {f.linea:<8} {score:.4f}      {es_clon}")

if __name__ == "__main__":
    main()
