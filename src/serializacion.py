import ast
from typing import List

# Transforma el árbol AST jerárquico en una lista lineal de tokens (1D)
# mediante un recorrido Pre-Order (Padre -> Hijos de izquierda a derecha),
# permitiendo comparar el código con algoritmos de secuencias o distancias.

def serializar_pre_order(nodo: ast.AST) -> List[str]:
    tokens = []

# Función recursiva que visita cada nodo en profundidad (DFS).
# Al estar anidada, comparte y acumula directamente en la lista 'tokens'.
    def recorrer(subnodo: ast.AST):
        # 1. Registrar la clase del nodo gramatical (ej: 'Assign', 'BinOp', 'Add')
        # ast.Name: Variables usadas en el cuerpo de la función (su nombre está en .id)
        # ast.arg: Parámetros definidos en la firma de la función (su nombre está en .arg)
        # ast.Constant: Literales homogéneos como números o textos (su valor está en .value, ej: 'LIT')
        nombre_tipo = type(subnodo).__name__
        tokens.append(nombre_tipo)

        # 2. Si el nodo contiene nuestros tokens normalizados, los anexamos
        if isinstance(subnodo, ast.Name):
            tokens.append(subnodo.id)
        elif isinstance(subnodo, ast.arg):
            tokens.append(subnodo.arg)
        elif isinstance(subnodo, ast.Constant):
            tokens.append(str(subnodo.value))

        # 3. Recorrer de forma recursiva los nodos hijos en orden pre-order
        # ast.iter_child_nodes itera únicamente sobre los subnodos sintácticos directos,
        # ignorando metadatos como números de línea (lineno) o columnas (col_offset).
        for hijo in ast.iter_child_nodes(subnodo):
            recorrer(hijo)

    recorrer(nodo)
    return tokens
