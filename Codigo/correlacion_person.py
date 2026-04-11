

def correlacion_person(puntA, puntB):
    valores_A = []
    valores_B = []
    for llave in puntA:
        if llave in puntB and puntB[llave] == puntB[llave] and puntA[llave] == puntA[llave]:
            valores_A.append(puntA[llave])
            valores_B.append(puntB[llave])
    
    n = len(valores_A) # cantidad de items
    if n < 3: # Umbral mínimo para que la correlación tenga sentido
        return 0.0

    prom_A = sum(valores_A) / n
    prom_B = sum(valores_B) / n

    suma_superior = 0
    suma_cuad_A = 0
    suma_cuad_B = 0

    for valA, valB in zip(valores_A, valores_B):
        
        diff_A = valA - prom_A
        diff_B = valB - prom_B
    
    
        suma_superior = suma_superior + diff_A * diff_B
        
        suma_cuad_A += diff_A ** 2
        suma_cuad_B += diff_B ** 2
    
    denominador = (suma_cuad_A * suma_cuad_B) ** 0.5
    
    if denominador == 0:
        return 0.0
        
    return suma_superior / denominador
