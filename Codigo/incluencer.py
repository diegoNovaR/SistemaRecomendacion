#funcion para obtener items importantes, encontramos las pelis mas vstas
def items_populares(all_users, top_n):
    conteo = {}

    for user in all_users.values():
        for item, rating in user.items():
            if rating == rating:  # evitar NaN
                conteo[item] = conteo.get(item, 0) + 1

    # Ordenar por popularidad
    populares = sorted(conteo, key=conteo.get, reverse=True)

    return populares[:top_n]

#filtrar items que el usuario no miro
def items_no_vistos(user_id, all_users, items):
    # Solo considerar películas realmente vistas (rating válido)
    vistos = set(
        item for item, rating in all_users[user_id].items()
        if rating == rating  # filtra NaN
    )

    return [item for item in items if item not in vistos]

#crear user influecen 
def crear_influencer(user_id, all_users, nuevas_recomendaciones, peso_extra=1.0):
    influencer = {}
    usuario = all_users[user_id]

    # Copiar gustos del usuario objetivo
    for item, rating in usuario.items():
        if rating == rating:
            influencer[item] = rating

    # Agregar nuevas recomendaciones con rating alto
    for item in nuevas_recomendaciones:
        influencer[item] = 5 * peso_extra  # puedes variar influencia

    return influencer



