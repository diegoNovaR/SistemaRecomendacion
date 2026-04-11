def distancia_manhattan(puntA, puntB):
    total_distancia = 0
    items_comunes = 0

    for llave in puntA:
        if llave in puntB and puntB[llave] is not None and puntA[llave] is not None:
            total_distancia = total_distancia + abs(puntA[llave] - puntB[llave])
            items_comunes += 1

    if items_comunes < 3:#para que no se evalue en base a 2 datos 
        return float('inf')
    
    return total_distancia;
