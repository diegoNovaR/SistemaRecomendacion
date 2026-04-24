from carga_datos import cargar_dataframes


if __name__ == "__main__":
    names_df, majors_df = cargar_dataframes()

    print(len(names_df))

    print(len(majors_df))
    
    print(majors_df.head(20))
    print(majors_df.dtypes)

    # # Convertir a diccionarios
    # names_dict = names_df.to_dict(orient="records")
    # majors_dict = majors_df.to_dict(orient="records")

    # print("Names:")
    # print(names_dict)

    # print("\nMajors:")
    # print(majors_dict)
    print(names_df.head(20))
    print(names_df.dtypes)