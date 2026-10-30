import ast
import copy

class NormalizadorAST(ast.NodeTransformer):
    # Inicializa el normalizador y crea la tabla de símbolos vacía.
    # Esta tabla guardará la correspondencia {'nombre_original': 'VARn'}
    # para que una misma variable reciba siempre el mismo token.
    def __init__(self):
        super().__init__()
        # Tabla de símbolos local para mantener la correspondencia de variables
        self.mapeo_variables = {}

    # Administra la tabla de símbolos. Si el nombre de la variable aparece por
    # primera vez, le asigna un identificador correlativo (VAR1, VAR2, ...) y lo
    # guarda. Si ya fue registrada, devuelve el identificador que ya tenía.
    def _obtener_token_variable(self, nombre_original: str) -> str:
        if nombre_original not in self.mapeo_variables:
            nuevo_token = f"VAR{len(self.mapeo_variables) + 1}"
            self.mapeo_variables[nombre_original] = nuevo_token
        return self.mapeo_variables[nombre_original]

    # Se ejecuta al encontrar la definición de una función ('def ...').
    # Anonimiza su nombre cambiándolo por 'FUNC_ANONIMA' para que el nombre
    # elegido por el programador no afecte la comparación estructural.
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        # El nombre de la función NO debe influir en la comparación
        node.name = "funcionNN"
        # Continuamos recorriendo los hijos del nodo
        self.generic_visit(node)
        return node

    # Se ejecuta sobre cada parámetro en los paréntesis de la función (ej: def f(x, y)).
    # Reemplaza el nombre de cada parámetro por su token canónico (VAR1, VAR2, etc.).
    def visit_arg(self, node: ast.arg) -> ast.AST:
        # Anonimiza los parámetros de la función (ej: def f(x, y) -> VAR1, VAR2)
        node.arg = self._obtener_token_variable(node.arg)
        self.generic_visit(node)
        return node

    # Se ejecuta cada vez que se usa o asigna una variable en el cuerpo de la función.
    # Reemplaza el identificador real ('node.id') por su token correspondiente en el AST.
    def visit_Name(self, node: ast.Name) -> ast.AST:
        # Anonimiza variables utilizadas en expresiones y asignaciones
        node.id = self._obtener_token_variable(node.id)
        self.generic_visit(node)
        return node

    # Se ejecuta al encontrar cualquier literal (números, strings, booleanos).
    # Reemplaza cualquier valor concreto por el token fijo 'LIT' para que
    # valores diferentes pero con idéntica lógica no alteren la similitud.
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        # En Python 3.8+, todos los números, strings y booleanos son ast.Constant
        node.value = "LIT"
        return node

# Función principal de entrada. Clona el AST original (mediante deepcopy)
# para no modificar el código fuente original en memoria, ejecuta el
# NormalizadorAST sobre la copia y retorna el árbol ya normalizado.
def normalizar_arbol_funcion(nodo_funcion: ast.FunctionDef) -> ast.FunctionDef:
    # Usamos deepcopy para no destruir el árbol original
    copia_arbol = copy.deepcopy(nodo_funcion)
    normalizador = NormalizadorAST()
    return normalizador.visit(copia_arbol)
