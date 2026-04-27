import matplotlib.pyplot as plt
def Boxplot(majors_df):
    top5 = majors_df["Majors"].value_counts().head(5).index
    subset = majors_df[majors_df["Majors"].isin(top5)]

    plt.figure()
    subset.boxplot(column="Terms in Attendance", by="Majors")

    plt.title("Duración por Major (Top 5)")
    plt.suptitle("")  # quita título automático feo
    plt.xlabel("Majors")
    plt.ylabel("Terms in Attendance")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
    return