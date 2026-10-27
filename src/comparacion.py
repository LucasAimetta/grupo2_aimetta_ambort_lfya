from typing import List, Set, Tuple

def generar_ngramas(tokens: List[str], n: int = 3) -> Set[Tuple[str, ...]]:
    # Si la función es más corta que n, tomamos toda la secuencia como único n-grama
    if len(tokens) < n:
        return {tuple(tokens)}
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}

def similitud_jaccard(tokens_a: List[str], tokens_b: List[str], n: int = 3) -> float:
    ngramas_a = generar_ngramas(tokens_a, n=n)
    ngramas_b = generar_ngramas(tokens_b, n=n)

    interseccion = ngramas_a.intersection(ngramas_b)
    union = ngramas_a.union(ngramas_b)
#Control de seguridad para evitar una división por cero
    if not union:
        return 0.0

    return len(interseccion) / len(union)

UMBRAL_DUPLICADO = 0.80
