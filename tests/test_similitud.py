import ast
import pytest
from src.normalizacion import normalizar_arbol_funcion
from src.serializacion import serializar_pre_order
from src.comparacion import similitud_jaccard, UMBRAL_DUPLICADO

def pipeline(codigo_funcion: str):
    modulo = ast.parse(codigo_funcion)
    fn_def = modulo.body[0]
    norm = normalizar_arbol_funcion(fn_def)
    return serializar_pre_order(norm)

# --- CASOS POSITIVOS ---
def test_clon_renombrado_variables():
    # Función original que calcula promedio
    f1 = """
def promedio(lista_numeros):
    acumulador = 0
    for elemento in lista_numeros:
        acumulador = acumulador + elemento
    return acumulador / len(lista_numeros)
"""
    # Función clonada con variables renombradas y nombre cambiado
    f2 = """
def calcular_media(valores):
    total = 0
    for v in valores:
        total = total + v
    return total / len(valores)
"""
    tokens1 = pipeline(f1)
    tokens2 = pipeline(f2)
    score = similitud_jaccard(tokens1, tokens2)

    # Deben ser idénticos tras la normalización
    assert score == 1.0
    assert score >= UMBRAL_DUPLICADO

def test_clon_cambio_de_literales():
    f1 = """
def validar_edad(edad):
    if edad >= 18:
        return "Mayor de edad"
    return "Menor"
"""
    f2 = """
def check_limite(valor):
    if valor >= 65:
        return "Jubilado"
    return "Activo"
"""
    tokens1 = pipeline(f1)
    tokens2 = pipeline(f2)
    score = similitud_jaccard(tokens1, tokens2)

    assert score == 1.0
    assert score >= UMBRAL_DUPLICADO

# --- CASOS NEGATIVOS ---
def test_funciones_estructuralmente_disjuntas():
    # Algoritmo matemático iterativo
    f1 = """
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
"""
    # Lectura de archivos con manejo de excepciones
    f2 = """
def leer_log(ruta):
    try:
        with open(ruta) as f:
            return f.read()
    except FileNotFoundError:
        return None
"""
    tokens1 = pipeline(f1)
    tokens2 = pipeline(f2)
    score = similitud_jaccard(tokens1, tokens2)

    # Estructuras completamente distintas
    assert score < 0.25
    assert score < UMBRAL_DUPLICADO

# --- CASO CLON SEMÁNTICO (TIPO 4) ---
def test_clon_semantico_multiplicacion_vs_suma():
    # Función 1: Multiplicación directa mediante operador aritmético
    f1 = """
def multiplicar(a, b):
    return a * b
"""
    # Función 2: Mismo resultado computacional pero mediante sumas sucesivas (bucle)
    f2 = """
def multiplicar(a, b):
    resultado = 0
    for _ in range(b):
        resultado = resultado + a
    return resultado
"""
    tokens1 = pipeline(f1)
    tokens2 = pipeline(f2)
    score = similitud_jaccard(tokens1, tokens2)

    # Teóricamente es un clon semántico (Tipo 4): resuelven el mismo problema
    # matemático, pero sintácticamente el AST es muy diferente (operador vs bucle for).
    # Por ende, el análisis sintáctico NO debe marcarlo como duplicado estructural.
    assert score < UMBRAL_DUPLICADO

