
from correlacion_person import correlacion_person

def knn(user_id, all_users, k=2):
    distancias = []
    perfil_objetivo = all_users[user_id]

    # 1. Comparar contra todos
    # otroid es la llave del usuario y perfilOtro es el valor de las peliculas que valoro el user
    for otro_id, perfil_otro in all_users.items():
        if otro_id != user_id:#comparamos si es el mismo usuario
            
            #aqui deber[ia de cambiarse segun el metodo]
            similitud = correlacion_person(perfil_objetivo, perfil_otro)
            
            # Guardamos el ID y su puntaje
            distancias.append((otro_id, similitud))

    # 2. Ordenar de mayor a menor similitud (Pearson/Coseno)
    # Usamos una función lambda para decirle que ordene por el segundo valor (el puntaje)
    distancias.sort(key=lambda x: x[1], reverse=True)

    # 3. Retornar solo los K primeros
    return distancias[:k]