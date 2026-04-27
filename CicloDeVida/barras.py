
import matplotlib.pyplot as plt

def Barras(majors_df):

    top_majors = majors_df["Majors"].value_counts().head(10)

    plt.figure()
    top_majors.plot(kind="bar")

    plt.title("Top 10 Majors")
    plt.xlabel("Majors")
    plt.ylabel("Cantidad de estudiantes")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
    return 