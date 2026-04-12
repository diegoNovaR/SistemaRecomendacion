def recomendacion(user_id, all_users, vecinos):
    recomendaciones = {}
    perfil_objetivo = all_users[user_id]

    for vecino_id, valor_metrica in vecinos:
        peso = valor_metrica #1 obtener valor del peso

        # 2. Explorar los gustos del vecino
        perfil_vecino = all_users[vecino_id]#mediante la llave obtenemos datos del vecino
        for artista, nota in perfil_vecino.items():
            # Solo nos interesa si el usuario objetivo NO lo ha visto
            # Y si el vecino SÍ le puso una nota válida (no NaN)
            if artista not in perfil_objetivo or perfil_objetivo[artista] != perfil_objetivo[artista]:
                if nota == nota: # Validar que la nota del vecino no sea NaN
                    
                    if artista not in recomendaciones:#
                        recomendaciones[artista] = [0, 0]
                    
                    # Acumulamos: (nota * peso) y el peso por separado
                    recomendaciones[artista][0] += nota * peso
                    recomendaciones[artista][1] += peso

    # 3. Calcular el promedio final y limpiar resultados
    lista_final = []
    for artista, totales in recomendaciones.items():
        suma_ponderada, suma_pesos = totales
        if suma_pesos > 0:
            prediccion = suma_ponderada / suma_pesos
            lista_final.append((artista, prediccion))

    # 4. Ordenar de mayor a menor predicción
    lista_final.sort(key=lambda x: x[1], reverse=True)
    return lista_final