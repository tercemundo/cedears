import requests
import pandas as pd
from io import BytesIO

URL = "https://www.comafi.com.ar/Multimedios/otros/7279.xlsx?v=1432025"

def main():
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()

    df_raw = pd.read_excel(
        BytesIO(resp.content),
        sheet_name="LISTA TOTAL DE CEDEARS",
        header=None
    )

    # Buscar la fila donde aparece "Identificación Mercado"
    header_row = None
    for i in range(len(df_raw)):
        if str(df_raw.iloc[i, 2]).strip() == "Identificación Mercado":
            header_row = i
            break

    if header_row is None:
        raise RuntimeError("No encontré la fila de encabezados 'Identificación Mercado'")

    # Reconstruir DataFrame con encabezados correctos
    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = df_raw.iloc[header_row]

    # Columna de tickers
    codigos = (
        df["Identificación Mercado"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    print(f"Total códigos: {len(codigos)}")

    # Guardar uno por línea en cedears.txt
    codigos.to_csv("cedears.txt", index=False, header=False)

if __name__ == "__main__":
    main()
