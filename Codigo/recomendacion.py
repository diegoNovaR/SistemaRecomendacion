def recomendacion(user_id, all_users, vecinos, min_vecinos, metrica):
    recomendaciones = {}
    perfil_objetivo = all_users[user_id]

    for vecino_id, valor_metrica in vecinos:
        
        if metrica in ['manhattan', 'euclidiana']:
            # Si la distancia es 0, el peso es 1 (máximo). 
            # Si la distancia es grande, el peso tiende a 0.
            peso = 1 / (1 + valor_metrica)
        else:
            # Para Pearson/Coseno el valor ya nos sirve como peso
            peso = valor_metrica

        perfil_vecino = all_users[vecino_id]
        
        for artista, nota in perfil_vecino.items():
            # 1. Verificar si el usuario objetivo no la ha visto (o es NaN)
            if artista not in perfil_objetivo or perfil_objetivo[artista] != perfil_objetivo[artista]:
                # 2. Verificar que la nota del vecino sea válida
                if nota == nota: 
                    
                    if artista not in recomendaciones:
                        # [SumaPonderada, SumaPesos, ContadorVecinos]
                        recomendaciones[artista] = [0, 0, 0]
                    
                    # Acumulamos datos
                    recomendaciones[artista][0] += nota * peso
                    recomendaciones[artista][1] += peso
                    # Incrementamos el contador de cuántos vecinos vieron esta peli
                    recomendaciones[artista][2] += 1

    # 3. Calcular el promedio final considerando la TOLERANCIA
    lista_final = []
    for artista, totales in recomendaciones.items():
        suma_ponderada, suma_pesos, conteo = totales
         
        # Solo se agrega si el número de vecinos que la vieron >= min_vecinos (al mínimo de vecinos que vieron la película)
        if suma_pesos > 0 and conteo >= min_vecinos:
            prediccion = suma_ponderada / suma_pesos
            lista_final.append((artista, prediccion))

    # 4. Ordenar
    lista_final.sort(key=lambda x: x[1], reverse=True)
    return lista_final