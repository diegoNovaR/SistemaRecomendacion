
def distancia_euclidiana(puntA, puntB):

    coincidencias = 0
    suma = 0
    for llave in puntA:
        if llave in puntB and puntA[llave] is not None and puntB[llave] is not None:
            suma += (puntA[llave] - puntB[llave])**2
            coincidencias += 1
    
    if coincidencias == 0:
        return float('inf')
    return suma**0.5