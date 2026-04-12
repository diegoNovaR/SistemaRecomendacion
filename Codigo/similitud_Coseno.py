def similitud_coseno(puntA, puntB):
    producto_escalar = 0
    suma_A = 0
    suma_B = 0
    items_comunes = 0
    for llave in puntA:
        if llave in puntB and puntB[llave] == puntB[llave] and puntA[llave] == puntA[llave]:
            producto_escalar = producto_escalar + (puntA[llave] * puntB[llave])
            suma_A = suma_A + (puntA[llave]**2)
            suma_B = suma_B + (puntB[llave]**2)
            items_comunes +=1
    
    if items_comunes < 3:
        return 0.0

    mag_A = suma_A ** 0.5
    mag_B = suma_B ** 0.5
    
    if mag_A == 0 or mag_B == 0: # Protección contra división por cero
        return 0.0
    
    return producto_escalar/ (mag_A * mag_B)

    
        

