from correlacion_person import correlacion_person
from distancia_Euclidiana import distancia_euclidiana
from similitud_Coseno import similitud_coseno
from distancia_Manhattan import distancia_manhattan

def knn(user_id, all_users, k=2, metrica ='pearson'):
    distancias = []
    perfil_objetivo = all_users[user_id]

    # 1. Comparar contra todos
    # otroid es la llave del usuario y perfilOtro es el valor de las peliculas que valoro el user
    for otro_id, perfil_otro in all_users.items():
        if otro_id != user_id:#comparamos si es el mismo usuario
            
            # 1. Selección del algoritmo
            if metrica == 'pearson':
                puntaje = correlacion_person(perfil_objetivo, perfil_otro)
            elif metrica == 'coseno':
                puntaje = similitud_coseno(perfil_objetivo, perfil_otro)
            elif metrica == 'manhattan':
                puntaje = distancia_manhattan(perfil_objetivo, perfil_otro)
            elif metrica == 'euclidiana':
                puntaje = distancia_euclidiana(perfil_objetivo, perfil_otro)
            else:
                raise ValueError("Métrica no reconocida")

            distancias.append((otro_id, puntaje))

    # 2. Lógica de ordenamiento diferenciada
    # Similitudes (Pearson/Coseno):  -> reverse=True
    # Distancias (Manhattan/Euclidiana):  -> reverse=False
    es_similitud = metrica in ['pearson', 'coseno']
    distancias.sort(key=lambda x: x[1], reverse=es_similitud)

    # 3. Retornar solo los K primeros
    return distancias[:k]