from carga_datos import cargar_dataframes
from barras import Barras
from histograma import Histograma
from boxplot import Boxplot

if __name__ == "__main__":
    names_df, majors_df = cargar_dataframes()

    print(len(names_df))

    print(len(majors_df))
    
    #print(majors_df.head(20))
    #print(majors_df.dtypes)

    # # Convertir a diccionarios
    # names_dict = names_df.to_dict(orient="records")
    # majors_dict = majors_df.to_dict(orient="records")

    # print("Names:")
    # print(names_dict)

    # print("\nMajors:")
    # print(majors_dict)
    #print(names_df.head(20))
    #print(names_df.dtypes)

    #print(names_df.info())
    #print(majors_df.info())

    #print(names_df['Role'].unique())
    #print(names_df['Role'].value_counts().to_frame())

    #print(majors_df['Majors'].unique())
    #print(majors_df['Majors'].value_counts().to_frame())

# 5 
    print(names_df.describe())
   
    #print(names_df["Role"].unique())

    #print(majors_df["Majors"].describe())

    print(majors_df["Majors"].value_counts().head(10))

#7 
    Barras(majors_df)
    Histograma(majors_df)
    Boxplot(majors_df)

