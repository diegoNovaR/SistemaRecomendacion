import matplotlib.pyplot as plt

def Histograma(majors_df):
    plt.figure()
    majors_df["Terms in Attendance"].plot(kind="hist", bins=10)

    plt.title("Distribución de Terms in Attendance")
    plt.xlabel("Número de ciclos")
    plt.ylabel("Frecuencia")

    plt.tight_layout()
    plt.show()
    return