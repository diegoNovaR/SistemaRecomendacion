import pandas as pd

def cargar_majors_limpio(ruta):
    data = []

    with open(ruta, "r", encoding="utf-8") as f:
        next(f)  # saltar header

        for linea in f:
            linea = linea.strip()

            if not linea:
                continue

            partes = [p.strip() for p in linea.split(",")]

            # 🔹 Buscar si el último valor es número
            if partes[-1].isdigit():
                terms = int(partes[-1])
                majors = ",".join(partes[:-1])
            else:
                # 🔥 Caso raro: NO hay número válido
                # opción 1: descartar
                continue

                # opción 2 (si quisieras conservarlo):
                # terms = None
                # majors = ",".join(partes)

            data.append({
                "Majors": majors,
                "Terms in Attendance": terms
            })

    return pd.DataFrame(data)


def cargar_dataframes():
    names_df = pd.read_csv("names.csv")
    majors_df = cargar_majors_limpio("majors.csv")

    # Normalizar texto en names minus
    names_df["Name"] = names_df["Name"].str.lower().str.strip()
    names_df["Role"] = names_df["Role"].str.lower().str.strip()

    # Normalizar majors 
    majors_df["Majors"] = majors_df["Majors"].str.split(",")
    majors_df = majors_df.explode("Majors")
    majors_df["Majors"] = majors_df["Majors"].str.strip()

    return names_df, majors_df