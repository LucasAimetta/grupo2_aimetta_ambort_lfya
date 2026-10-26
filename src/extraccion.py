import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass #Usamos dataclass y no diccionario para que sea más fácil de usar.
class FuncionExtraida:
    nombre: str          # Identificador original para reportar al usuario
    archivo: str         # Ruta del archivo fuente
    linea: int           # Número de línea donde inicia
    nodo_ast: ast.FunctionDef  # El subárbol AST de la función

#Recibe la ruta de un archivo y devuelve una lista de funciones extraídas de ese archivo en el formato (nombre, archivo, linea, nodo_ast).
def extraer_funciones_de_archivo(ruta_archivo: Path) -> List[FuncionExtraida]:
    funciones = []
    try:
        codigo = ruta_archivo.read_text(encoding="utf-8")
        # ast.parse() ejecuta el análisis léxico y sintáctico completo de Python
        arbol_completo = ast.parse(codigo, filename=str(ruta_archivo))
    except (SyntaxError, UnicodeDecodeError):
        # Si un archivo tiene errores de sintaxis, se ignora de forma segura
        return funciones

    # ast.walk() realiza un recorrido por todos los nodos del árbol. El recorrido es en BFS, nivel por nivel.
    for nodo in ast.walk(arbol_completo):
        #Filtra los nodos para identificar únicamente definiciones de funciones.
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funciones.append(
                FuncionExtraida(
                    nombre=nodo.name,
                    archivo=str(ruta_archivo),
                    linea=nodo.lineno,
                    nodo_ast=nodo
                )
            )
    return funciones
# Recibe la ruta de un directorio y devuelve una lista de todas las funciones extraídas de todos los archivos .py en ese directorio y sus subdirectorios.
def extraer_todas_las_funciones(directorio: str) -> List[FuncionExtraida]:
    todas = []
    base = Path(directorio)
    # Recorrido recursivo buscando todo archivo .py
    for archivo in base.rglob("*.py"):
        todas.extend(extraer_funciones_de_archivo(archivo))
    return todas
