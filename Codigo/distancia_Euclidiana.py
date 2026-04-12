
def distancia_euclidiana(puntA, puntB):#usuarios

    coincidencias = 0
    suma = 0
    for llave in puntA:
        if llave in puntB and puntA[llave] == puntA[llave] and puntB[llave] == puntB[llave]:
            suma += (puntA[llave] - puntB[llave])**2
            coincidencias += 1
    
    if coincidencias < 3:
        return float('inf')
    return suma**0.5